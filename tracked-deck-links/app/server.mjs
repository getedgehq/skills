// Tracked deck links: one personal link per recipient, served behind a shell-only page.
// Design by Falco Schneider (Next.js + Supabase original), ported to one zero-dependency
// Node process with built-in SQLite.
//
// What counts as what:
//   preview  a server GET of /d/<token>. The response is an empty shell with no deck content,
//            so link unfurls (WhatsApp, Slack, iMessage, mail scanners) never see the deck and
//            never count as an open.
//   opened   the shell's JavaScript ran in a browser and called /api/open. Only then does the
//            deck load, in a frame, from a short-lived signed URL.
//   read     opened + real input (pointer, key, touch, scroll) + at least 10 active seconds.
// One row per browser tab session; a reload in the same tab bumps `opens`. Beats only move values up.
// Per slide: active seconds and visits, slide titles per deck version.
//
// Config: DECKLINKS_HOME/config.json (written by `decklinks.mjs init`), env vars override it.
// Admin password: DECKLINKS_HOME/admin-password (mode 600) or ADMIN_PASSWORD_FILE. Never env/argv.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const HOME = path.resolve(process.env.DECKLINKS_HOME || './decklinks-data');
let fileCfg = {};
try { fileCfg = JSON.parse(fs.readFileSync(path.join(HOME, 'config.json'), 'utf8')); } catch {}
const cfg = (envName, key, dflt) => process.env[envName] ?? fileCfg[key] ?? dflt;

const PORT = Number(cfg('PORT', 'port', 8787));
const HOST = cfg('HOST', 'host', '127.0.0.1');
const PREFIX = String(cfg('PREFIX', 'prefix', '')).replace(/\/+$/, '');
const PUBLIC_ORIGIN = String(cfg('PUBLIC_ORIGIN', 'publicOrigin', `http://localhost:${PORT}`)).replace(/\/+$/, '');
const SHELL_TITLE = String(cfg('SHELL_TITLE', 'shellTitle', 'Shared document'));
const NTFY_SERVER = cfg('NTFY_SERVER', 'ntfyServer', 'https://ntfy.sh');
const NTFY_TOPIC = cfg('NTFY_TOPIC', 'ntfyTopic', '');
const DECK_ROOT = path.join(HOME, 'decks');
const DB_PATH = path.join(HOME, 'tracker.db');
const SIGNED_URL_SECONDS = 6 * 3600;
const IDLE_SWEEP_MS = 30_000;

function readSecretFile(file) { try { return fs.readFileSync(file, 'utf8').trim(); } catch { return ''; } }
const ADMIN_PASSWORD = readSecretFile(process.env.ADMIN_PASSWORD_FILE || path.join(HOME, 'admin-password'));
if (!ADMIN_PASSWORD) console.error('WARNING: no admin password file, /api/admin disabled (run decklinks.mjs init)');
let SIGNING_KEY = readSecretFile(path.join(HOME, 'signing-key'));
if (!SIGNING_KEY) {
  SIGNING_KEY = crypto.randomBytes(32).toString('hex');
  fs.mkdirSync(HOME, { recursive: true });
  fs.writeFileSync(path.join(HOME, 'signing-key'), SIGNING_KEY + '\n', { mode: 0o600 });
}
fs.mkdirSync(DECK_ROOT, { recursive: true });

// ---------- database ----------
const db = new DatabaseSync(DB_PATH);
db.exec(`
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA busy_timeout=3000;
CREATE TABLE IF NOT EXISTS links (
  id TEXT PRIMARY KEY, deck TEXT NOT NULL DEFAULT 'deck', recipient TEXT NOT NULL, note TEXT,
  created_at TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, archived_at TEXT
);
CREATE TABLE IF NOT EXISTS hits (            -- server GETs of a link: unfurls, scanners, and the first step of every real open
  id INTEGER PRIMARY KEY AUTOINCREMENT, link_id TEXT NOT NULL REFERENCES links(id) ON DELETE CASCADE,
  at TEXT NOT NULL, user_agent TEXT, ip TEXT, referrer TEXT, is_bot INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS views (           -- one per browser tab session that ran JS
  id INTEGER PRIMARY KEY AUTOINCREMENT, link_id TEXT NOT NULL REFERENCES links(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL, device_id TEXT, deck_version TEXT,
  opened_at TEXT NOT NULL, last_seen_at TEXT NOT NULL, closed_at TEXT,
  seconds INTEGER NOT NULL DEFAULT 0, max_index INTEGER NOT NULL DEFAULT 0,
  kind TEXT NOT NULL DEFAULT 'opened', interacted INTEGER NOT NULL DEFAULT 0,
  is_bot INTEGER NOT NULL DEFAULT 0, is_owner INTEGER NOT NULL DEFAULT 0, opens INTEGER NOT NULL DEFAULT 1,
  user_agent TEXT, ip TEXT, referrer TEXT,
  summary_sent_at TEXT, summary_seconds INTEGER NOT NULL DEFAULT 0,
  UNIQUE(link_id, session_id)
);
CREATE TABLE IF NOT EXISTS slide_stats (
  view_id INTEGER NOT NULL REFERENCES views(id) ON DELETE CASCADE,
  slide_id TEXT NOT NULL, slide_index INTEGER NOT NULL DEFAULT 0,
  seconds INTEGER NOT NULL DEFAULT 0, visits INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (view_id, slide_id)
);
CREATE TABLE IF NOT EXISTS deck_slides (
  deck_version TEXT NOT NULL, slide_index INTEGER NOT NULL, slide_id TEXT NOT NULL, title TEXT,
  PRIMARY KEY (deck_version, slide_index)
);
CREATE INDEX IF NOT EXISTS views_link_idx ON views(link_id, opened_at DESC);
CREATE INDEX IF NOT EXISTS hits_link_idx ON hits(link_id);
`);

const now = () => new Date().toISOString();
const q = (sql) => db.prepare(sql);
const S = {
  getLink: q('SELECT * FROM links WHERE id=?'),
  insLink: q('INSERT INTO links (id, deck, recipient, note, created_at) VALUES (?,?,?,?,?)'),
  listLinks: q('SELECT * FROM links WHERE archived_at IS NULL ORDER BY created_at DESC'),
  setRevoked: q('UPDATE links SET revoked=? WHERE id=?'),
  archive: q('UPDATE links SET archived_at=? WHERE id=? AND revoked=1'),
  insHit: q('INSERT INTO hits (link_id, at, user_agent, ip, referrer, is_bot) VALUES (?,?,?,?,?,?)'),
  hitsFor: q('SELECT * FROM hits WHERE link_id=? ORDER BY at DESC LIMIT 200'),
  viewBySession: q('SELECT * FROM views WHERE link_id=? AND session_id=?'),
  viewById: q('SELECT * FROM views WHERE id=?'),
  insView: q(`INSERT INTO views (link_id, session_id, device_id, deck_version, opened_at, last_seen_at, is_bot, is_owner,
              user_agent, ip, referrer) VALUES (?,?,?,?,?,?,?,?,?,?,?) RETURNING id`),
  reopen: q('UPDATE views SET opens=opens+1, closed_at=NULL, last_seen_at=?, is_owner=MAX(is_owner,?), deck_version=COALESCE(?, deck_version) WHERE id=?'),
  beat: q(`UPDATE views SET seconds=MAX(seconds,?), max_index=MAX(max_index,?), interacted=MAX(interacted,?),
           kind=?, last_seen_at=?, closed_at=? WHERE id=?`),
  upSlide: q(`INSERT INTO slide_stats (view_id, slide_id, slide_index, seconds, visits) VALUES (?,?,?,?,?)
              ON CONFLICT(view_id, slide_id) DO UPDATE SET seconds=MAX(seconds,excluded.seconds),
              visits=MAX(visits,excluded.visits), slide_index=excluded.slide_index`),
  upDeckSlide: q(`INSERT INTO deck_slides (deck_version, slide_index, slide_id, title) VALUES (?,?,?,?)
                  ON CONFLICT(deck_version, slide_index) DO UPDATE SET slide_id=excluded.slide_id, title=excluded.title`),
  viewsFor: q('SELECT * FROM views WHERE link_id=? ORDER BY opened_at DESC'),
  slidesFor: q('SELECT * FROM slide_stats WHERE view_id=?'),
  deckSlides: q('SELECT * FROM deck_slides WHERE deck_version=? ORDER BY slide_index'),
  humanDevices: q('SELECT DISTINCT device_id FROM views WHERE link_id=? AND is_owner=0 AND is_bot=0'),
  stale: q(`SELECT * FROM views WHERE is_owner=0 AND is_bot=0 AND last_seen_at > ?
            AND ((closed_at IS NOT NULL AND closed_at < ?) OR last_seen_at < ?)`),
  markSummarized: q('UPDATE views SET summary_sent_at=?, summary_seconds=? WHERE id=?'),
};

// ---------- helpers ----------
const ALPHABET = 'abcdefghjkmnpqrstuvwxyz23456789';
const newToken = (n = 10) => Array.from(crypto.randomBytes(n), (b) => ALPHABET[b % ALPHABET.length]).join('');
const TOKEN_RE = /^[a-z0-9]{6,40}$/;
const ID_RE = /^[A-Za-z0-9-]{8,64}$/;
const SLIDE_RE = /^[A-Za-z0-9_-]{1,64}$/;
const NAME_RE = /^[A-Za-z0-9._-]{1,40}$/;   // deck names and versions

// Known unfurlers, crawlers and script clients. The list need not be complete: only a browser that
// runs the shell's JavaScript can open the deck. It only labels preview rows.
const BOT_RE = new RegExp([
  'bot\\b', 'crawler', 'spider', 'preview', 'fetcher', 'scanner', 'facebookexternalhit', 'whatsapp', 'slackbot',
  'slack-imgproxy', 'telegrambot', 'linkedinbot', 'twitterbot', 'discordbot', 'skypeuripreview', 'microsoftpreview',
  'applebot', 'googlebot', 'bingbot', 'yandex', 'embedly', 'iframely', 'bitlybot', 'redditbot', 'vkshare',
  'w3c_validator', 'curl/', 'wget/', 'python-requests', 'python-urllib', 'go-http-client', 'java/', 'okhttp',
  'axios/', 'node-fetch', 'headlesschrome', 'phantomjs',
].join('|'), 'i');
const isBot = (ua) => !ua || BOT_RE.test(ua);

function device(ua) {
  const s = String(ua || '');
  const type = /iPad|Tablet/.test(s) ? 'Tablet' : /iPhone|Android.*Mobile|Mobile/.test(s) ? 'Phone' : 'Desktop';
  const os = /iPhone|iPad|iOS/.test(s) ? 'iOS' : /Android/.test(s) ? 'Android' : /Mac OS X|Macintosh/.test(s) ? 'macOS'
    : /Windows/.test(s) ? 'Windows' : /Linux/.test(s) ? 'Linux' : 'Other';
  const br = /Edg\//.test(s) ? 'Edge' : /OPR\//.test(s) ? 'Opera' : /Firefox\/|FxiOS/.test(s) ? 'Firefox'
    : /Chrome\/|CriOS/.test(s) ? 'Chrome' : /Safari\//.test(s) ? 'Safari' : 'Other';
  return `${type} · ${os} · ${br}`;
}

const ipOf = (req) => String(req.headers['x-real-ip'] || req.socket.remoteAddress || '').slice(0, 64);
const fmt = (s) => (s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, '0')}s`);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function send(res, status, body, headers = {}) {
  const isObj = body !== null && typeof body === 'object' && !Buffer.isBuffer(body);
  res.writeHead(status, {
    'Cache-Control': 'no-store',
    'X-Robots-Tag': 'noindex, nofollow',
    'X-Content-Type-Options': 'nosniff',
    ...(isObj ? { 'Content-Type': 'application/json' } : {}),
    ...headers,
  });
  res.end(isObj ? JSON.stringify(body) : body);
}

function readBody(req, limit = 64 * 1024) {
  return new Promise((resolve) => {
    let size = 0; const chunks = [];
    req.on('data', (c) => { size += c.length; if (size > limit) { req.destroy(); resolve(null); } else chunks.push(c); });
    req.on('end', () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8') || 'null')); } catch { resolve(null); }
    });
    req.on('error', () => resolve(null));
  });
}

async function notify(title, body, tags = ['eyes'], priority = 3) {
  if (!NTFY_TOPIC) return;
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 2000);
  try {
    await fetch(NTFY_SERVER, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: ctl.signal,
      body: JSON.stringify({ topic: NTFY_TOPIC, title, message: body, tags, priority, click: `${PUBLIC_ORIGIN}${PREFIX}/admin` }),
    });
  } catch (e) { console.error('ntfy failed:', e.message); } finally { clearTimeout(t); }
}

// ---------- decks ----------
// DECK_ROOT/<deck>/<version>/ holds index.html + assets; DECK_ROOT/<deck>/current is a symlink to the live
// version. Resolved per request, so a republish takes effect for every existing link on its next open.
function currentVersion(deck) {
  if (!NAME_RE.test(deck || '')) return null;
  try { return path.basename(fs.realpathSync(path.join(DECK_ROOT, deck, 'current'))); } catch { return null; }
}
// The name pushes use for a published deck: the <title> of that version's index.html (a PDF publish
// writes the file name there), else the deck name. Pushes go to the owner only, never to an unfurl.
const deckNames = new Map();
function deckName(deck, version) {
  const key = `${deck}/${version}`;
  if (!deckNames.has(key)) {
    let name = '';
    try {
      const m = fs.readFileSync(path.join(DECK_ROOT, deck, version, 'index.html'), 'utf8').match(/<title[^>]*>([^<]*)<\/title>/i);
      if (m) name = m[1].replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/\s+/g, ' ').trim().slice(0, 80);
    } catch {}
    deckNames.set(key, name || deck);
  }
  return deckNames.get(key);
}
function listDecks() {
  let names = [];
  try { names = fs.readdirSync(DECK_ROOT).filter((n) => NAME_RE.test(n)); } catch {}
  return Object.fromEntries(names.map((n) => [n, currentVersion(n)]));
}

function sign(deck, version, exp) {
  return crypto.createHmac('sha256', SIGNING_KEY).update(`${deck}/${version}/${exp}`).digest('base64url');
}
function signedKey(deck, version) {
  const exp = Math.floor(Date.now() / 1000) + SIGNED_URL_SECONDS;
  return `${exp}.${sign(deck, version, exp)}`;
}
function keyValid(deck, version, k) {
  const m = /^(\d{10})\.([A-Za-z0-9_-]{43})$/.exec(k || '');
  if (!m || Number(m[1]) < Date.now() / 1000) return false;
  const a = Buffer.from(m[2]); const b = Buffer.from(sign(deck, version, m[1]));
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
function cookieOf(req, name) {
  for (const part of String(req.headers.cookie || '').split(/;\s*/)) {
    const i = part.indexOf('=');
    if (i > 0 && part.slice(0, i) === name) return part.slice(i + 1);
  }
  return '';
}

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
  '.avif': 'image/avif', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.mp4': 'video/mp4', '.webm': 'video/webm', '.mp3': 'audio/mpeg',
  '.m4a': 'audio/mp4', '.pdf': 'application/pdf', '.txt': 'text/plain; charset=utf-8',
};

// GET /v/<deck>/<version>/<file>. index.html needs a signed key (?k=, minted by /api/open) and drops it into
// a cookie scoped to this deck version, so the deck's relative assets load without carrying the key.
// Without a live link nobody gets a key, so the deck itself is never publicly reachable.
function serveDeckFile(req, res, deck, version, rel, url) {
  if (!NAME_RE.test(deck) || !NAME_RE.test(version)) return send(res, 404, 'Not found');
  const dir = path.join(DECK_ROOT, deck, version);
  const file = path.normalize(path.join(dir, decodeURIComponent(rel || 'index.html')));
  if (!file.startsWith(dir + path.sep)) return send(res, 404, 'Not found');
  const cookieName = `dk_${deck.replace(/[^A-Za-z0-9_]/g, '_')}`;
  const qk = url.searchParams.get('k');
  const viaQuery = keyValid(deck, version, qk);
  if (!viaQuery && !keyValid(deck, version, cookieOf(req, cookieName))) {
    return send(res, 403, 'This link has expired. Open your personal link again.', { 'Content-Type': 'text/plain; charset=utf-8' });
  }
  let st; try { st = fs.statSync(file); } catch { return send(res, 404, 'Not found'); }
  if (!st.isFile()) return send(res, 404, 'Not found');
  const ext = path.extname(file).toLowerCase();
  const headers = { 'Content-Type': TYPES[ext] || 'application/octet-stream', 'Cache-Control': 'private, no-store', 'X-Robots-Tag': 'noindex, nofollow' };
  if (viaQuery) {
    const maxAge = Math.max(0, Number(qk.split('.')[0]) - Math.floor(Date.now() / 1000));
    headers['Set-Cookie'] = `${cookieName}=${qk}; Path=${PREFIX}/v/${deck}/${version}/; Max-Age=${maxAge}; HttpOnly; SameSite=Lax`
      + (PUBLIC_ORIGIN.startsWith('https:') ? '; Secure' : '');
  }
  if (ext === '.html' || ext === '.htm') {
    const tag = `<meta name="deck-version" content="${esc(deck)}/${esc(version)}">`;
    const script = `<script src="${PREFIX}/track.js" defer></script>`;
    let html = fs.readFileSync(file, 'utf8');
    html = /<head[^>]*>/i.test(html) ? html.replace(/<head[^>]*>/i, (h) => h + tag) : tag + html;
    html = /<\/body>/i.test(html) ? html.replace(/<\/body>(?![\s\S]*<\/body>)/i, script + '</body>') : html + script;
    headers['Referrer-Policy'] = 'no-referrer';
    res.writeHead(200, headers); return res.end(html);
  }
  res.writeHead(200, { ...headers, 'Content-Length': st.size });
  fs.createReadStream(file).pipe(res);
}

// The shell: no deck content, no deck title. A link unfurl sees only SHELL_TITLE.
function shellHtml() {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>${esc(SHELL_TITLE)}</title>
<style>html,body{margin:0;height:100%;background:#0f1115;color:#c9ced8;font:15px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
#msg{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;padding:24px;text-align:center}
iframe{position:fixed;inset:0;width:100%;height:100%;border:0;background:#fff}</style></head>
<body><div id="msg">Loading…</div><noscript><p style="padding:24px">This document needs JavaScript.</p></noscript>
<script>
(function () {
  var P = ${JSON.stringify(PREFIX)};
  var m = location.pathname.match(/\\/d\\/([a-z0-9]{6,40})\\/?$/i);
  var msg = document.getElementById('msg');
  if (!m) { msg.textContent = 'This link is not valid.'; return; }
  var token = m[1].toLowerCase();
  function rid() { var b = new Uint8Array(16); crypto.getRandomValues(b); return Array.prototype.map.call(b, function (x) { return ('0' + x.toString(16)).slice(-2); }).join(''); }
  function stored(box, key) { try { var v = box.getItem(key); if (!v) { v = rid(); box.setItem(key, v); } return v; } catch (e) { return rid(); } }
  var owner = false; try { owner = localStorage.getItem('decklinks-owner') === '1'; } catch (e) {}
  var sessionId = stored(window.sessionStorage, 'decklinks-session-' + token);
  var deviceId = stored(window.localStorage, 'decklinks-device');
  fetch(P + '/api/open', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: token, sessionId: sessionId, deviceId: deviceId, owner: owner }) })
    .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
    .then(function (x) {
      if (!x.ok || !x.d.src) { msg.textContent = (x.d && x.d.error) || 'This link is not available right now.'; return; }
      window.DECK_TRACK = { api: P + '/api', token: token, viewId: x.d.viewId, sessionId: sessionId };
      var f = document.createElement('iframe');
      f.src = x.d.src; f.title = document.title; f.allow = 'fullscreen; autoplay';
      f.addEventListener('load', function () { msg.remove(); try { f.contentWindow.focus(); } catch (e) {} });
      document.body.appendChild(f);
    })
    .catch(function () { msg.textContent = 'No connection. Please try again later.'; });
})();
</script></body></html>`;
}
const SHELL_CSP = "default-src 'self'; script-src 'unsafe-inline' 'self'; style-src 'unsafe-inline'; frame-src 'self'; connect-src 'self'; img-src 'self' data:";

// ---------- admin auth (header, timing-safe) + brute-force brake ----------
const fails = new Map();
function authorised(req) {
  if (!ADMIN_PASSWORD) return false;
  const ip = ipOf(req); const f = fails.get(ip);
  if (f && f.n >= 10 && Date.now() - f.at < 15 * 60_000) return 'locked';
  const given = req.headers['x-admin-password'];
  const a = Buffer.from(typeof given === 'string' ? given : '');
  const b = Buffer.from(ADMIN_PASSWORD);
  const ok = a.length === b.length && crypto.timingSafeEqual(a, b);
  if (!ok) fails.set(ip, { n: (f && Date.now() - f.at < 15 * 60_000 ? f.n : 0) + 1, at: Date.now() });
  else fails.delete(ip);
  return ok;
}

function linkReport(link) {
  const views = S.viewsFor.all(link.id);
  const hits = S.hitsFor.all(link.id);
  const human = views.filter((v) => !v.is_bot && !v.is_owner);
  const own = views.filter((v) => v.is_owner);
  const status = link.revoked ? 'revoked' : human.some((v) => v.kind === 'read') ? 'read'
    : human.length ? 'opened' : hits.length && !own.length ? 'preview only' : 'not opened';

  const slides = new Map();
  const versions = new Set();
  const sessions = views.map((v) => {
    const ss = S.slidesFor.all(v.id);
    if (!v.is_bot && !v.is_owner) {
      if (v.deck_version) versions.add(v.deck_version);
      for (const s of ss) {
        const cur = slides.get(s.slide_id) || { slide_id: s.slide_id, slide_index: s.slide_index, seconds: 0, visits: 0, sessions: 0 };
        cur.seconds += s.seconds; cur.visits += s.visits; cur.sessions += 1; cur.slide_index = s.slide_index;
        slides.set(s.slide_id, cur);
      }
    }
    return {
      id: v.id, opened_at: v.opened_at, last_seen_at: v.last_seen_at, closed_at: v.closed_at, seconds: v.seconds,
      kind: v.kind, opens: v.opens, is_owner: !!v.is_owner, is_bot: !!v.is_bot, device: device(v.user_agent),
      device_id: v.device_id ? v.device_id.slice(0, 6) : null, ip: v.ip, deck_version: v.deck_version,
      slides_seen: ss.filter((s) => s.visits > 0).length,
      slides: ss.sort((a, b) => a.slide_index - b.slide_index).map((s) => ({ id: s.slide_id, i: s.slide_index, s: s.seconds, v: s.visits })),
    };
  });
  const cur = currentVersion(link.deck);
  const latestVersion = [...versions].sort().pop() || (cur ? `${link.deck}/${cur}` : '');
  const deckRows = S.deckSlides.all(latestVersion);
  const titles = new Map(deckRows.map((d) => [d.slide_id, d.title]));
  const humanOpens = human.reduce((n, v) => n + v.opens, 0);
  return {
    ...link, revoked: !!link.revoked, path: `${PREFIX}/d/${link.id}`, url: `${PUBLIC_ORIGIN}${PREFIX}/d/${link.id}`, status,
    first_open: human.map((v) => v.opened_at).sort()[0] || null,
    last_seen: human.length ? human.map((v) => v.last_seen_at).sort().pop() : null,
    sessions: human.length,
    opens: humanOpens,
    revisits: Math.max(0, humanOpens - 1),
    devices: new Set(human.map((v) => v.device_id).filter(Boolean)).size,
    device_labels: [...new Set(human.map((v) => device(v.user_agent)))],
    total_seconds: human.reduce((n, v) => n + v.seconds, 0),
    slides_seen: [...slides.values()].filter((s) => s.visits > 0).length, deck_size: deckRows.length,
    deck_versions: [...versions],
    // Every real open starts with a server GET of the shell, so previews = bot GETs + browser-looking GETs
    // that never ran the shell's JS (mail scanners with browser UAs, JS blocked).
    previews: hits.filter((h) => h.is_bot).length + Math.max(0, hits.filter((h) => !h.is_bot).length - views.reduce((n, v) => n + v.opens, 0)),
    bot_previews: hits.filter((h) => h.is_bot).length, page_loads: hits.length,
    preview_agents: [...new Set(hits.filter((h) => h.is_bot).map((h) => (h.user_agent || '(no user agent)').slice(0, 60)))].slice(0, 5),
    own_views: own.length,
    slides: [...slides.values()].sort((a, b) => a.slide_index - b.slide_index)
      .map((s) => ({ ...s, title: titles.get(s.slide_id) || null })),
    deck_outline: deckRows.map((d) => ({ i: d.slide_index, id: d.slide_id, title: d.title })),
    views: sessions.slice(0, 40),
  };
}

// ---------- API handlers ----------
async function apiOpen(req, res) {
  const b = await readBody(req);
  if (!b || typeof b.token !== 'string' || !TOKEN_RE.test(b.token) || !ID_RE.test(b.sessionId || '') || !ID_RE.test(b.deviceId || '')) {
    return send(res, 400, { error: 'bad request' });
  }
  const link = S.getLink.get(b.token);
  if (!link || link.revoked) return send(res, 410, { error: 'This link is no longer active.' });
  const version = currentVersion(link.deck);
  if (!version) return send(res, 503, { error: 'This document is not available right now.' });
  const deckVersion = `${link.deck}/${version}`;
  const ua = String(req.headers['user-agent'] || '').slice(0, 400);
  const owner = b.owner === true ? 1 : 0;
  const bot = isBot(ua) ? 1 : 0;
  const t = now();
  const src = `${PREFIX}/v/${link.deck}/${version}/index.html?k=${signedKey(link.deck, version)}`;

  const existing = S.viewBySession.get(link.id, b.sessionId);
  if (existing) {
    S.reopen.run(t, owner, deckVersion, existing.id);
    return send(res, 200, { viewId: existing.id, src });
  }
  const before = new Set(S.humanDevices.all(link.id).map((r) => r.device_id));
  const { id } = S.insView.get(link.id, b.sessionId, b.deviceId, deckVersion, t, t, bot, owner, ua, ipOf(req),
    String(req.headers.referer || '').slice(0, 300));
  if (!owner && !bot) {
    const n = S.viewsFor.all(link.id).filter((v) => !v.is_owner && !v.is_bot).length;
    const newDevice = before.size > 0 && !before.has(b.deviceId);
    notify(`${link.recipient} opened ${deckName(link.deck, version)}`,
      [n <= 1 ? 'first time' : `visit #${n}`, device(ua), newDevice ? 'Opened on a second device' : ''].filter(Boolean).join(' · '),
      [newDevice ? 'warning' : 'eyes'], newDevice ? 4 : 3);
  }
  return send(res, 200, { viewId: id, src });
}

async function apiBeat(req, res) {
  const b = await readBody(req);
  if (!b || !Number.isInteger(b.viewId) || typeof b.sessionId !== 'string' || typeof b.seconds !== 'number') {
    return send(res, 400, { error: 'bad request' });
  }
  const row = S.viewById.get(b.viewId);
  if (!row || row.session_id !== b.sessionId) return send(res, 403, { error: 'forbidden' });
  const seconds = Math.min(Math.max(Math.round(b.seconds), 0), 6 * 3600);
  const interacted = row.interacted || b.interacted === true ? 1 : 0;
  const maxSeconds = Math.max(row.seconds, seconds);
  const kind = interacted && maxSeconds >= 10 ? 'read' : row.kind === 'read' ? 'read' : 'opened';
  const maxIndex = Number.isInteger(b.maxIndex) ? Math.min(Math.max(b.maxIndex, 0), 500) : 0;
  const t = now();
  db.exec('BEGIN');
  try {
    S.beat.run(seconds, maxIndex, interacted, kind, t, b.final === true ? t : null, row.id);
    if (row.deck_version && Array.isArray(b.deck) && b.deck.length <= 300) {
      for (const d of b.deck) {
        if (d && Number.isInteger(d.i) && SLIDE_RE.test(d.id || '')) S.upDeckSlide.run(row.deck_version, d.i, d.id, String(d.title || '').slice(0, 200));
      }
    }
    if (b.slides && typeof b.slides === 'object') {
      for (const [sid, v] of Object.entries(b.slides).slice(0, 300)) {
        if (!SLIDE_RE.test(sid) || !v || typeof v !== 'object') continue;
        const s = Math.min(Math.max(Math.round(Number(v.s) || 0), 0), 6 * 3600);
        const n = Math.min(Math.max(Math.round(Number(v.v) || 0), 0), 10000);
        const i = Math.min(Math.max(Math.round(Number(v.i) || 0), 0), 500);
        S.upSlide.run(row.id, sid, i, s, n);
      }
    }
    db.exec('COMMIT');
  } catch (e) { db.exec('ROLLBACK'); throw e; }
  res.writeHead(204, { 'Cache-Control': 'no-store' }); res.end();
}

async function apiAdmin(req, res) {
  const auth = authorised(req);
  if (auth === 'locked') return send(res, 429, { error: 'Too many attempts. Try again in 15 minutes.' });
  if (!auth) return send(res, 401, { error: 'Wrong password.' });
  if (req.method === 'GET') {
    return send(res, 200, { decks: listDecks(), links: S.listLinks.all().map(linkReport) });
  }
  const b = (await readBody(req)) || {};
  if (req.method === 'POST') {
    const recipient = typeof b.recipient === 'string' ? b.recipient.trim().slice(0, 120) : '';
    if (!recipient) return send(res, 400, { error: 'recipient required' });
    const deck = typeof b.deck === 'string' && b.deck ? b.deck : 'deck';
    if (!NAME_RE.test(deck)) return send(res, 400, { error: 'bad deck name' });
    if (!currentVersion(deck)) return send(res, 400, { error: `no published deck named "${deck}" (publish it first)` });
    const note = typeof b.note === 'string' && b.note.trim() ? b.note.trim().slice(0, 500) : null;
    const id = newToken();
    S.insLink.run(id, deck, recipient, note, now());
    return send(res, 200, { link: linkReport(S.getLink.get(id)) });
  }
  if (req.method === 'PATCH') {
    if (typeof b.id !== 'string' || !S.getLink.get(b.id)) return send(res, 404, { error: 'unknown link' });
    if (b.archive === true) { S.archive.run(now(), b.id); return send(res, 200, { ok: true }); }
    if (typeof b.revoked !== 'boolean') return send(res, 400, { error: 'revoked required' });
    S.setRevoked.run(b.revoked ? 1 : 0, b.id);
    return send(res, 200, { ok: true });
  }
  return send(res, 405, { error: 'method' });
}

// ---------- sweep: summary push when a visit has ended ----------
function sweep() {
  const ago = (ms) => new Date(Date.now() - ms).toISOString();
  for (const v of S.stale.all(ago(6 * 3600_000), ago(15_000), ago(120_000))) {
    if (v.seconds < 3) continue;
    if (v.summary_sent_at && v.seconds < (v.summary_seconds || 0) + 3) continue;
    const link = S.getLink.get(v.link_id); if (!link) continue;
    S.markSummarized.run(now(), v.seconds, v.id);
    const seen = S.slidesFor.all(v.id).filter((s) => s.visits > 0);
    const top = seen.sort((a, b) => b.seconds - a.seconds).slice(0, 2).map((s) => `${s.slide_id} ${fmt(s.seconds)}`).join(', ');
    const [vDeck, vVersion] = String(v.deck_version || '').split('/');
    notify(`${link.recipient} left ${vDeck && vVersion ? deckName(vDeck, vVersion) : deckName(link.deck, currentVersion(link.deck))}`,
      [`${fmt(v.seconds)} active`, `${seen.length} slides`, top ? `most: ${top}` : '', device(v.user_agent)].filter(Boolean).join(' · '),
      ['hourglass_flowing_sand']);
  }
}
setInterval(() => { try { sweep(); } catch (e) { console.error('sweep failed:', e.message); } }, IDLE_SWEEP_MS).unref();

// ---------- router ----------
const ADMIN_HTML = fs.readFileSync(path.join(HERE, 'admin.html'), 'utf8');
const TRACK_JS = fs.readFileSync(path.join(HERE, 'track.js'), 'utf8');

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://x');
    let p = url.pathname;
    if (PREFIX) { if (!p.startsWith(PREFIX + '/') && p !== PREFIX) return send(res, 404, 'Not found'); p = p.slice(PREFIX.length) || '/'; }

    if (p === '/healthz') return send(res, 200, { ok: true, decks: listDecks() });

    const m = p.match(/^\/d\/([^/]+)\/?$/);
    if (m && (req.method === 'GET' || req.method === 'HEAD')) {
      const token = m[1].toLowerCase();
      const link = TOKEN_RE.test(token) ? S.getLink.get(token) : null;
      // Unknown or revoked token: plain 404, nothing logged.
      if (!link || link.revoked) return send(res, 404, 'Not found', { 'Content-Type': 'text/plain; charset=utf-8' });
      const ua = String(req.headers['user-agent'] || '').slice(0, 400);
      try { S.insHit.run(link.id, now(), ua, ipOf(req), String(req.headers.referer || '').slice(0, 300), isBot(ua) ? 1 : 0); }
      catch (e) { console.error('hit not stored:', e.message); }
      return send(res, 200, shellHtml(), { 'Content-Type': 'text/html; charset=utf-8', 'Referrer-Policy': 'no-referrer', 'Content-Security-Policy': SHELL_CSP });
    }
    const v = p.match(/^\/v\/([^/]+)\/([^/]+)\/(.*)$/);
    if (v && (req.method === 'GET' || req.method === 'HEAD')) return serveDeckFile(req, res, v[1], v[2], v[3], url);
    if (p === '/track.js') return send(res, 200, TRACK_JS, { 'Content-Type': 'text/javascript; charset=utf-8' });
    if (p === '/api/open' && req.method === 'POST') return await apiOpen(req, res);
    if (p === '/api/beat' && req.method === 'POST') return await apiBeat(req, res);
    if (p === '/api/admin') return await apiAdmin(req, res);
    if (p === '/admin' || p === '/admin/') {
      return send(res, 200, ADMIN_HTML, {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Security-Policy': "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'",
      });
    }
    return send(res, 404, 'Not found', { 'Content-Type': 'text/plain' });
  } catch (e) {
    console.error('request failed:', e);
    if (!res.headersSent) send(res, 500, { error: 'server error' });
  }
});
server.on('error', (e) => { console.error(`cannot listen on ${HOST}:${PORT}: ${e.message}`); process.exit(1); });
server.listen(PORT, HOST, () => console.log(`tracked-deck-links on http://${HOST}:${PORT}${PREFIX} · public ${PUBLIC_ORIGIN}${PREFIX} · decks ${JSON.stringify(listDecks())} · push ${NTFY_TOPIC ? 'on' : 'off'}`));
