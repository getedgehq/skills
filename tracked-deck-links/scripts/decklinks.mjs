#!/usr/bin/env node
// Command line for the tracked deck links server (app/server.mjs). Zero dependencies, Node 22.13+.
//
//   decklinks.mjs doctor [--port N]                 check Node, SQLite, port, PDF tools
//   decklinks.mjs init [--port N] [--public-origin URL] [--prefix /path] [--title TEXT] [--ntfy-topic T]
//   decklinks.mjs start | stop | status             run the server in the background (local use and tests)
//   decklinks.mjs publish <deck.html|deck-dir|deck.pdf> [--deck NAME] [--version V]
//   decklinks.mjs mint <recipient> [--deck NAME] [--note TEXT]
//   decklinks.mjs revoke <token|url> | unrevoke <token|url>
//   decklinks.mjs links
//   decklinks.mjs report [recipient-substring] [--json]
//
// State lives in $DECKLINKS_HOME (default ./decklinks-data): config.json, admin-password (600),
// signing-key (600), tracker.db, decks/. The admin password is never printed or put on argv.
process.removeAllListeners('warning'); // node:sqlite prints an ExperimentalWarning on import
import fs from 'node:fs';
import path from 'node:path';
import net from 'node:net';
import crypto from 'node:crypto';
import { execFileSync, spawn } from 'node:child_process';

const HOME = path.resolve(process.env.DECKLINKS_HOME || './decklinks-data');
const NAME_RE = /^[A-Za-z0-9._-]{1,40}$/;

function die(msg) { console.error(`error: ${msg}`); process.exit(1); }
function parse(argv) {
  const pos = []; const opt = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      if (i + 1 < argv.length && !argv[i + 1].startsWith('--')) opt[k] = argv[++i]; else opt[k] = true;
    } else pos.push(a);
  }
  return { pos, opt };
}
function config() {
  try { return JSON.parse(fs.readFileSync(path.join(HOME, 'config.json'), 'utf8')); }
  catch { die(`no ${path.join(HOME, 'config.json')}; run "decklinks.mjs init" first (or set DECKLINKS_HOME)`); }
}
function have(cmd) { try { execFileSync('sh', ['-c', `command -v ${cmd}`], { stdio: 'ignore' }); return true; } catch { return false; } }
function portFree(port, host = '127.0.0.1') {
  return new Promise((resolve) => {
    const s = net.createServer();
    s.once('error', () => resolve(false));
    s.listen(port, host, () => s.close(() => resolve(true)));
  });
}

// ---------- doctor ----------
async function doctor(opt) {
  let ok = true;
  const [maj, min] = process.versions.node.split('.').map(Number);
  const nodeOk = maj > 23 || (maj === 23 && min >= 4) || (maj === 22 && min >= 13);
  console.log(`${nodeOk ? 'ok  ' : 'FAIL'} node ${process.versions.node} (need 22.13+ for built-in SQLite without flags)`);
  ok &&= nodeOk;
  try { await import('node:sqlite'); console.log('ok   node:sqlite loads'); } catch (e) { ok = false; console.log(`FAIL node:sqlite: ${e.message}`); }
  let port = opt.port ? Number(opt.port) : null;
  if (!port) { try { port = JSON.parse(fs.readFileSync(path.join(HOME, 'config.json'), 'utf8')).port; } catch { port = 8787; } }
  const free = await portFree(port);
  console.log(`${free ? 'ok  ' : 'FAIL'} port ${port} ${free ? 'is free' : 'is in use: pick another with --port, or stop what holds it'}`);
  ok &&= free;
  console.log(`${have('pdftoppm') ? 'ok  ' : 'warn'} pdftoppm ${have('pdftoppm') ? 'found' : 'missing: only needed to publish PDF decks (apt install poppler-utils / brew install poppler)'}`);
  console.log(ok ? 'doctor: ready' : 'doctor: fix the FAIL lines first');
  process.exit(ok ? 0 : 1);
}

// ---------- init ----------
function init(opt) {
  fs.mkdirSync(HOME, { recursive: true, mode: 0o700 });
  const file = path.join(HOME, 'config.json');
  let cfg = {};
  try { cfg = JSON.parse(fs.readFileSync(file, 'utf8')); } catch {}
  const port = Number(opt.port || cfg.port || 8787);
  if (!Number.isInteger(port) || port < 1 || port > 65535) die('bad --port');
  cfg = {
    port,
    host: opt.host || cfg.host || '127.0.0.1',
    prefix: (opt.prefix ?? cfg.prefix ?? '').replace(/\/+$/, ''),
    publicOrigin: (opt['public-origin'] || cfg.publicOrigin || `http://localhost:${port}`).replace(/\/+$/, ''),
    shellTitle: opt.title || cfg.shellTitle || 'Shared document',
    ...(opt['ntfy-topic'] || cfg.ntfyTopic ? { ntfyTopic: opt['ntfy-topic'] || cfg.ntfyTopic } : {}),
    ...(cfg.ntfyServer ? { ntfyServer: cfg.ntfyServer } : {}),
  };
  if (cfg.prefix && !/^\/[A-Za-z0-9/_-]+$/.test(cfg.prefix)) die('bad --prefix (use e.g. /deck)');
  fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + '\n');
  const pw = path.join(HOME, 'admin-password');
  if (!fs.existsSync(pw)) {
    fs.writeFileSync(pw, crypto.randomBytes(18).toString('base64url') + '\n', { mode: 0o600 });
    console.log(`admin password created in ${pw} (mode 600, not printed)`);
  } else console.log(`admin password kept: ${pw}`);
  console.log(`config: ${file}`);
  console.log(JSON.stringify(cfg, null, 2));
}

// ---------- start / stop / status (background server for local use; production uses systemd) ----------
const PID_FILE = () => path.join(HOME, 'server.pid');
function runningPid() {
  let pid; try { pid = Number(fs.readFileSync(PID_FILE(), 'utf8').trim()); } catch { return null; }
  if (!pid) return null;
  try { process.kill(pid, 0); } catch { return null; }
  try { if (!fs.readFileSync(`/proc/${pid}/cmdline`, 'utf8').includes('server.mjs')) return null; } catch {}
  return pid;
}
const localBase = (cfg) => `http://${!cfg.host || cfg.host === '0.0.0.0' || cfg.host === '::' ? '127.0.0.1' : cfg.host}:${cfg.port}${cfg.prefix || ''}`;
async function health(cfg) {
  try { const r = await fetch(`${localBase(cfg)}/healthz`); return r.ok ? await r.json() : null; } catch { return null; }
}
async function start() {
  const cfg = config();
  const pid = runningPid();
  if (pid) return console.log(`already running (pid ${pid}) on ${localBase(cfg)}`);
  if (!(await portFree(cfg.port))) die(`port ${cfg.port} is in use by another program; run init --port <free port>`);
  const log = fs.openSync(path.join(HOME, 'server.log'), 'a');
  const server = new URL('../app/server.mjs', import.meta.url).pathname;
  const child = spawn(process.execPath, ['--disable-warning=ExperimentalWarning', server], {
    detached: true, stdio: ['ignore', log, log], env: { ...process.env, DECKLINKS_HOME: HOME },
  });
  child.unref();
  fs.writeFileSync(PID_FILE(), `${child.pid}\n`);
  for (let i = 0; i < 50; i++) {
    await new Promise((r) => setTimeout(r, 100));
    const h = await health(cfg);
    if (h) return console.log(`started (pid ${child.pid}) on ${localBase(cfg)} · public links use ${cfg.publicOrigin}${cfg.prefix || ''} · log ${path.join(HOME, 'server.log')}`);
  }
  die(`server did not answer within 5 s; see ${path.join(HOME, 'server.log')}`);
}
async function stop() {
  const cfg = config();
  const pid = runningPid();
  if (!pid) return console.log('not running (no live pid in server.pid)');
  process.kill(pid, 'SIGTERM');
  for (let i = 0; i < 50 && !(await portFree(cfg.port)); i++) await new Promise((r) => setTimeout(r, 100));
  try { fs.unlinkSync(PID_FILE()); } catch {}
  console.log(`stopped (pid ${pid}); port ${cfg.port} ${(await portFree(cfg.port)) ? 'is free' : 'is STILL in use'}`);
}
async function status() {
  const cfg = config();
  const pid = runningPid(); const h = await health(cfg);
  console.log(`${h ? 'up' : 'DOWN'} · ${localBase(cfg)} · pid ${pid || '-'} · decks ${h ? JSON.stringify(h.decks) : '-'}`);
  process.exit(h ? 0 : 1);
}

// ---------- publish ----------
function versionName() { return 'v' + new Date().toISOString().replace(/[-:]/g, '').replace('T', '-').slice(0, 15); }
function copyTree(src, dst) {
  let n = 0;
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    if (e.name.startsWith('.') || e.name === 'node_modules' || /\.(log|sh|md|py)$/i.test(e.name)) continue;
    const s = path.join(src, e.name); const d = path.join(dst, e.name);
    if (e.isDirectory()) { fs.mkdirSync(d, { recursive: true }); n += copyTree(s, d); }
    else if (e.isFile()) { fs.copyFileSync(s, d); n++; }
  }
  return n;
}
const escHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function pdfToDeck(pdf, out) {
  if (!have('pdftoppm')) die('pdftoppm not found: install poppler-utils (apt) or poppler (brew) to publish a PDF');
  fs.mkdirSync(path.join(out, 'pages'), { recursive: true });
  execFileSync('pdftoppm', ['-r', '110', '-png', pdf, path.join(out, 'pages', 'page')], { stdio: 'inherit' });
  const pages = fs.readdirSync(path.join(out, 'pages')).filter((f) => f.endsWith('.png')).sort();
  if (!pages.length) die('pdftoppm produced no pages');
  const titles = pages.map((_, i) => {
    if (!have('pdftotext')) return '';
    try {
      const t = execFileSync('pdftotext', ['-f', String(i + 1), '-l', String(i + 1), pdf, '-'], { encoding: 'utf8' });
      return (t.split('\n').map((l) => l.trim()).find((l) => l.length > 1) || '').slice(0, 120);
    } catch { return ''; }
  });
  const base = path.basename(pdf).replace(/\.pdf$/i, '');
  const sections = pages.map((f, i) => `<section class="slide" data-title="${escHtml(titles[i] || `Page ${i + 1}`)}"><img src="pages/${f}" alt="Page ${i + 1}"></section>`).join('\n');
  fs.writeFileSync(path.join(out, 'index.html'), `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>${escHtml(base)}</title>
<style>html{scroll-snap-type:y proximity;background:#1b1d22}body{margin:0}
.slide{min-height:100vh;display:flex;align-items:center;justify-content:center;scroll-snap-align:start;padding:2vh 0;box-sizing:border-box}
.slide img{max-width:100vw;max-height:96vh;box-shadow:0 2px 18px rgba(0,0,0,.4);background:#fff}</style></head>
<body>
${sections}
</body></html>
`);
  return pages.length;
}
function publish(pos, opt) {
  const cfg = config(); void cfg;
  const src = pos[0] ? path.resolve(pos[0]) : die('publish needs a path: deck.html, a folder with index.html, or deck.pdf');
  const deck = opt.deck || 'deck';
  const version = opt.version || versionName();
  if (!NAME_RE.test(deck)) die('bad --deck (letters, digits, . _ - ; max 40)');
  if (!NAME_RE.test(version)) die('bad --version (letters, digits, . _ - ; max 40)');
  if (!fs.existsSync(src)) die(`${src} does not exist`);
  const root = path.join(HOME, 'decks', deck);
  const dst = path.join(root, version);
  if (fs.existsSync(dst)) die(`${deck}/${version} already exists; pass a new --version`);
  fs.mkdirSync(dst, { recursive: true });
  let files; let kind;
  const st = fs.statSync(src);
  if (st.isDirectory()) {
    if (!fs.existsSync(path.join(src, 'index.html'))) die(`${src}/index.html missing`);
    files = copyTree(src, dst); kind = 'folder';
  } else if (/\.html?$/i.test(src)) {
    fs.copyFileSync(src, path.join(dst, 'index.html')); files = 1; kind = 'single HTML file';
  } else if (/\.pdf$/i.test(src)) {
    const n = pdfToDeck(src, dst); files = n + 1; kind = `PDF, ${n} pages`;
  } else die('unsupported input: use .html, .pdf, or a folder with index.html');
  const html = fs.readFileSync(path.join(dst, 'index.html'), 'utf8');
  const sections = (html.match(/<section\b/gi) || []).length;
  const abs = (html.match(/\b(?:src|href)="\/(?!\/)[^"]*"/gi) || []).slice(0, 3);
  const tmp = path.join(root, '.current.tmp');
  try { fs.unlinkSync(tmp); } catch {}
  fs.symlinkSync(version, tmp);
  fs.renameSync(tmp, path.join(root, 'current'));
  console.log(`published ${kind} as ${deck}/${version} (${files} files, ${sections} <section> elements)`);
  console.log(`current ${deck} -> ${fs.readlinkSync(path.join(root, 'current'))}; every existing link for "${deck}" now serves this version`);
  if (abs.length) console.log(`warning: root-absolute references will not resolve inside the deck folder: ${abs.join(' ')} (make them relative)`);
  if (!/<script[^>]+reveal/i.test(html) && !/data-slide|class="[^"]*\bslide\b|<section\b/i.test(html)) {
    console.log('note: no slide markup found; the whole page counts as one slide. Wrap slides in <section> for per-slide stats.');
  }
}

// ---------- API ----------
function apiBase(cfg) {
  if (process.env.DECKLINKS_API) return process.env.DECKLINKS_API.replace(/\/+$/, '');
  const host = !cfg.host || cfg.host === '0.0.0.0' || cfg.host === '::' ? '127.0.0.1' : cfg.host;
  return `http://${host}:${cfg.port}${cfg.prefix || ''}/api/admin`;
}
async function api(method, body) {
  const cfg = config();
  let pw;
  try { pw = fs.readFileSync(process.env.ADMIN_PASSWORD_FILE || path.join(HOME, 'admin-password'), 'utf8').trim(); }
  catch { die('admin password file missing; run init'); }
  let r;
  try {
    r = await fetch(apiBase(cfg), { method, headers: { 'Content-Type': 'application/json', 'x-admin-password': pw }, body: body ? JSON.stringify(body) : undefined });
  } catch (e) { die(`server not reachable at ${apiBase(cfg)} (${e.cause?.code || e.message}); is app/server.mjs running?`); }
  const d = await r.json().catch(() => ({}));
  if (!r.ok) die(d.error || `HTTP ${r.status}`);
  return d;
}
const tokenOf = (s) => String(s || '').replace(/\/+$/, '').split('/').pop().toLowerCase();

async function mint(pos, opt) {
  const recipient = pos.join(' ').trim() || die('mint needs a recipient name');
  const d = await api('POST', { recipient, deck: opt.deck || 'deck', note: typeof opt.note === 'string' ? opt.note : undefined });
  console.log(`${d.link.recipient} -> ${d.link.url}`);
}
async function setRevoked(pos, revoked) {
  const id = tokenOf(pos[0]) || die('needs a token or link URL');
  await api('PATCH', { id, revoked });
  console.log(`${id} ${revoked ? 'revoked: the link now returns 404 and is no longer counted' : 'reactivated'}`);
}
async function links() {
  const d = await api('GET');
  if (!d.links.length) return console.log('no links yet');
  for (const l of d.links) console.log(`${l.revoked ? 'REVOKED ' : ''}${l.recipient} · ${l.deck} · ${l.url} · ${l.status}`);
}

// ---------- report in plain words ----------
const dur = (s) => (!s ? '0s' : s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, '0')}s`);
const when = (iso) => (iso ? new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' }) : '-');
const STATUS = {
  read: 'READ: opened in a browser, with real input and at least 10 active seconds',
  opened: 'OPENED: the deck loaded in a browser, but no real reading yet (under 10 active seconds or no input)',
  'preview only': 'PREVIEW ONLY: the link was fetched (chat app unfurl, mail scanner), nobody opened the deck',
  'not opened': 'NOT OPENED: nobody has fetched the link yet',
  revoked: 'REVOKED: the link no longer works',
};
function plain(l) {
  const out = [];
  out.push(`${l.recipient}${l.note ? ` (${l.note})` : ''} · deck "${l.deck}" · ${l.url}`);
  out.push(`  Status: ${STATUS[l.status] || l.status}.`);
  if (l.sessions) {
    out.push(`  First opened ${when(l.first_open)}, last seen ${when(l.last_seen)}.`);
    out.push(`  Active time ${dur(l.total_seconds)} over ${l.sessions} visit${l.sessions > 1 ? 's' : ''}` +
      `${l.opens > l.sessions ? ` (${l.opens} page loads incl. reloads)` : ''}; ${l.slides_seen}${l.deck_size ? ` of ${l.deck_size}` : ''} slides seen.`);
    out.push(`  Devices: ${l.devices} (${l.device_labels.join('; ')}).${l.devices > 1 ? ' Opened on a second device.' : ''}`);
  }
  out.push(`  Link previews (not counted as opens): ${l.previews}${l.preview_agents.length ? ` · ${l.preview_agents.join(' | ')}` : ''}.`);
  if (l.own_views) out.push(`  Your own views (excluded): ${l.own_views}.`);
  if (l.slides.length) {
    out.push('  Per slide (all visits):');
    const seen = new Map(l.slides.map((s) => [s.slide_id, s]));
    const rows = l.deck_outline.length ? l.deck_outline : l.slides.map((s) => ({ i: s.slide_index, id: s.slide_id, title: s.title }));
    for (const r of rows) {
      const s = seen.get(r.id);
      const label = `${String(r.i + 1).padStart(2)}. ${(r.title || r.id).slice(0, 48)}`;
      out.push(`    ${label.padEnd(54)} ${s && s.visits ? `${dur(s.seconds).padStart(7)}  ${s.visits} visit${s.visits > 1 ? 's' : ''}` : '   not seen'}`);
    }
  }
  if (l.views.length) {
    out.push('  Visits (one per browser tab):');
    for (const v of l.views) {
      out.push(`    ${when(v.opened_at)} · ${v.device}${v.device_id ? ` [device ${v.device_id}]` : ''} · ${v.kind} · ${dur(v.seconds)} active · ${v.slides_seen} slides` +
        `${v.opens > 1 ? ` · ${v.opens} loads` : ''}${v.is_owner ? ' · you' : ''}${v.is_bot ? ' · bot' : ''}`);
    }
  }
  return out.join('\n');
}
async function report(pos, opt) {
  const d = await api('GET');
  const f = pos.join(' ').toLowerCase();
  const ls = d.links.filter((l) => !f || l.recipient.toLowerCase().includes(f) || l.id === f);
  if (opt.json) return console.log(JSON.stringify({ decks: d.decks, links: ls }, null, 2));
  console.log(`Live decks: ${Object.entries(d.decks).map(([n, v]) => `${n} (${v})`).join(', ') || 'none'} · ${ls.length} link${ls.length === 1 ? '' : 's'}\n`);
  console.log(ls.map(plain).join('\n\n') || 'no links');
}

// ---------- main ----------
const [cmd, ...rest] = process.argv.slice(2);
const { pos, opt } = parse(rest);
const cmds = {
  doctor: () => doctor(opt), init: () => init(opt), start, stop, status, publish: () => publish(pos, opt), mint: () => mint(pos, opt),
  revoke: () => setRevoked(pos, true), unrevoke: () => setRevoked(pos, false), links, report: () => report(pos, opt),
};
if (!cmds[cmd]) {
  console.log(fs.readFileSync(new URL(import.meta.url), 'utf8').split('\n').slice(1, 12).map((l) => l.replace(/^\/\/ ?/, '')).join('\n'));
  process.exit(cmd ? 1 : 0);
}
await cmds[cmd]();
