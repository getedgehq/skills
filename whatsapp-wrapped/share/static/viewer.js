/* Story viewer for encrypted share links. Decrypts in the browser with the key from the #fragment, validates the
 * payload against schema-v1.json, then renders with DOM text nodes only (no innerHTML). Nothing here sends the key
 * or the statistics anywhere: the only requests are same-origin GETs for the ciphertext and the schema, and an
 * optional abuse report that carries only a reason. */
"use strict";

var MONTH_RE = /^(20[0-9]{2}|2100)-(0[1-9]|1[0-2])$/;
var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
var WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

/* ------------------------------------------------------------------ validation (mirrors share_schema.py) */
function isInt(x) { return typeof x === "number" && Number.isInteger(x); }
function plainObject(o) { return o !== null && typeof o === "object" && !Array.isArray(o); }
function sameKeys(o, keys) {
  if (!plainObject(o)) return false;
  var k = Object.keys(o).sort(), w = keys.slice().sort();
  if (k.length !== w.length) return false;
  for (var i = 0; i < k.length; i++) if (k[i] !== w[i]) return false;
  return true;
}
function checkField(schema, kind, v) {
  var p = kind.split(":");
  if (p[0] === "int") return isInt(v) && v >= +p[1] && v <= +p[2];
  if (kind === "month") return typeof v === "string" && MONTH_RE.test(v);
  if (kind === "archetype") return schema.archetypes.indexOf(v) >= 0;
  if (kind === "hist24") return Array.isArray(v) && v.length === 24 && v.every(function (x) { return isInt(x) && x >= 0 && x <= 100; });
  if (p[0] === "emojilist") {
    if (!Array.isArray(v) || v.length < +p[1] || v.length > +p[2]) return false;
    var seen = {};
    return v.every(function (it) {
      var ok = Array.isArray(it) && it.length === 2 && schema.emoji.indexOf(it[0]) >= 0 && !seen[it[0]] &&
        isInt(it[1]) && it[1] >= 1 && it[1] <= 100000000;
      if (ok) seen[it[0]] = 1;
      return ok;
    });
  }
  return false;
}
function validate(schema, p) {
  if (!sameKeys(p, ["v", "kind", "from", "to", "cards"])) return "payload keys";
  if (p.v !== schema.version) return "version";
  if (schema.kinds.indexOf(p.kind) < 0) return "kind";
  if (!checkField(schema, "month", p.from) || !checkField(schema, "month", p.to) || p.from > p.to) return "period";
  if (!Array.isArray(p.cards) || p.cards.length < schema.min_cards || p.cards.length > schema.max_cards) return "card count";
  var last = -1, types = [];
  for (var i = 0; i < p.cards.length; i++) {
    var c = p.cards[i];
    if (!plainObject(c) || !Object.prototype.hasOwnProperty.call(schema.cards, c.t)) return "card type";
    var spec = schema.cards[c.t];
    if (!sameKeys(c, Object.keys(spec).concat(["t"]))) return "card keys";
    var pos = schema.card_order.indexOf(c.t);
    if (pos <= last) return "card order";
    last = pos;
    for (var f in spec) if (!checkField(schema, spec[f], c[f])) return "field " + c.t + "." + f;
    types.push(c.t);
  }
  for (var r = 0; r < schema.required_cards.length; r++) if (types.indexOf(schema.required_cards[r]) < 0) return "required card";
  if (new TextEncoder().encode(JSON.stringify(p)).length > schema.max_plain_bytes) return "size";
  return null;
}

/* ------------------------------------------------------------------ crypto */
function b64uToBytes(s) {
  if (!/^[A-Za-z0-9_-]+$/.test(s)) throw new Error("bad base64url");
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  var bin = atob(s), out = new Uint8Array(bin.length);
  for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
async function decrypt(keyB64, ivB64, ctB64, aad) {
  var raw = b64uToBytes(keyB64);
  if (raw.length !== 32) throw new Error("key length");
  var key = await crypto.subtle.importKey("raw", raw, { name: "AES-GCM" }, false, ["decrypt"]);
  var plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64uToBytes(ivB64), additionalData: new TextEncoder().encode(aad) },
    key, b64uToBytes(ctB64));
  return JSON.parse(new TextDecoder().decode(plain));
}

/* ------------------------------------------------------------------ copy */
var ARCH = {
  night_owls: ["Night owls.", "Night owl.", "Most alive after midnight."],
  early_birds: ["Early birds.", "Early bird.", "Up and texting before 9am."],
  voice_note_crew: ["The voice note crew.", "Voice note royalty.", "Why type when you can talk?"],
  emoji_storm: ["Emoji storm.", "Emoji artist.", "Words optional. Emojis mandatory."],
  weekend_crew: ["Weekend crew.", "Weekend texter.", "Quiet all week, loud on Saturday."],
  streak_keepers: ["Streak keepers.", "Streak keeper.", "Not a day goes by without a message."],
  rapid_fire: ["Rapid fire.", "Rapid fire.", "More than 50 messages on an average day."],
  slow_burners: ["Slow burners.", "Slow burner.", "Few messages, every one counts."],
  evening_people: ["Evening people.", "Evening person.", "Most alive after dinner."]
};
function fmt(n) { return n.toLocaleString("en-US"); }
function month(m) { var p = m.split("-"); return MONTHS[+p[1] - 1] + " " + p[0]; }
function hour(h) { return h === 0 ? "midnight" : h === 12 ? "noon" : (h % 12) + (h < 12 ? "am" : "pm"); }
function plural(n, one, many) { return fmt(n) + " " + (n === 1 ? one : many); }

/* ------------------------------------------------------------------ DOM helpers */
function el(tag, cls, text) {
  var e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined && text !== null) e.textContent = String(text);
  return e;
}
function add(parent) { for (var i = 1; i < arguments.length; i++) if (arguments[i]) parent.appendChild(arguments[i]); return parent; }
function archSvg() {
  var ns = "http://www.w3.org/2000/svg", s = document.createElementNS(ns, "svg"), p = document.createElementNS(ns, "path");
  s.setAttribute("viewBox", "0 0 64 40"); s.setAttribute("aria-hidden", "true");
  p.setAttribute("fill", "currentColor"); p.setAttribute("d", "M0 40V36C0 16.1 14.3 0 32 0s32 16.1 32 36v4z");
  s.appendChild(p);
  return s;
}

/* ------------------------------------------------------------------ frames */
function buildFrames(p, ctx) {
  var solo = p.kind !== "group", frames = [];
  var period = month(p.from) === month(p.to) ? month(p.from) : month(p.from) + " to " + month(p.to);
  p.cards.forEach(function (c) {
    var f;
    if (c.t === "messages") {
      f = el("section", "frame frame-cover t-paper");
      var line = p.kind === "group" ? "messages between " + c.people + " people, across " + plural(c.span_days, "day", "days") + "."
        : p.kind === "duo" ? "messages I sent in one chat, across " + plural(c.span_days, "day", "days") + "."
        : "messages I sent across " + plural(c.chats, "chat", "chats") + " in " + plural(c.span_days, "day", "days") + ".";
      add(f, el("p", "kicker", ctx.name), el("p", "kicker", period), el("p", "big", fmt(c.n)), el("p", "line", line),
        el("div", "grow"));
      var img = el("img", "meadow"); img.src = ctx.base + "/static/meadow.webp"; img.alt = "";
      f.appendChild(img);
      f.dataset.dark = "";
    } else if (c.t === "peak") {
      f = el("section", "frame t-deep");
      var h = el("div", "hist"); h.setAttribute("aria-hidden", "true");
      c.hist.forEach(function (v, i) { var b = el("b", i === c.hour ? "peak" : ""); b.style.height = Math.max(2, v) + "%"; h.appendChild(b); });
      var ax = el("div", "axis"); ["midnight", "6am", "noon", "6pm", "11pm"].forEach(function (t) { ax.appendChild(el("span", "", t)); });
      add(f, el("p", "kicker", solo ? "When I text" : "When this chat comes alive"), el("p", "big", hour(c.hour)),
        el("p", "line", "is peak hour. " + WEEKDAYS[c.weekday] + "s are the busiest."), h, ax, el("div", "grow"));
      f.dataset.dark = "1";
    } else if (c.t === "streak") {
      f = el("section", "frame t-paper");
      var m = p.cards[0], st = el("div", "stats");
      add(st, stat(fmt(m.active_days), "days with messages"), stat(fmt(m.per_day), "messages on an average day"),
        stat(month(c.busiest_month), "busiest month, " + plural(c.busiest_n, "message", "messages"), true));
      add(f, el("p", "kicker", "Longest streak"), el("p", "big", fmt(c.days)), el("p", "line", c.days === 1 ? "day in a row." : "days in a row."),
        el("p", "sub", solo ? "Not a single day without a message." : "Nobody let the chat go quiet."), st, el("div", "grow"));
    } else if (c.t === "emojis") {
      f = el("section", "frame t-green");
      var row = el("div", "emoji-row");
      c.top.slice(1).forEach(function (it) { var d = el("div"); add(d, el("span", "", it[0]), el("small", "", fmt(it[1]))); row.appendChild(d); });
      add(f, el("p", "kicker", solo ? "My emojis" : "The chat in emojis"), el("p", "headline", "The official emoji"),
        el("div", "emoji-big", c.top[0][0]), el("p", "line", "used " + plural(c.top[0][1], "time", "times") + "."),
        c.top.length > 1 ? row : null, el("div", "grow"));
      f.dataset.dark = "1";
    } else if (c.t === "media") {
      f = el("section", "frame t-deep");
      var g = el("div", "stats");
      add(g, c.photos ? stat(fmt(c.photos), "photos, videos and other media") : null, c.stickers ? stat(fmt(c.stickers), "stickers and GIFs") : null);
      add(f, el("p", "kicker", "Voice notes and media"), el("p", "big", fmt(c.voice)),
        el("p", "line", c.voice === 1 ? "voice note." : "voice notes. Podcast when?"), g, el("div", "grow"));
      f.dataset.dark = "1";
    } else if (c.t === "archetype") {
      f = el("section", "frame t-paper");
      var a = ARCH[c.id];
      add(f, el("p", "kicker", solo ? "Texting personality" : "Chat personality"), el("p", "headline big mid", solo ? a[1] : a[0]),
        el("p", "line", a[2]), el("div", "grow"));
    }
    if (f) frames.push(f);
  });
  frames.push(finalFrame(ctx));
  return frames;
}
function stat(n, label, wide) { var d = el("div", "stat" + (wide ? " wide" : "")); add(d, el("span", "n", n), el("span", "l", label)); return d; }
function finalFrame(ctx) {
  var f = el("section", "frame frame-final t-paper");
  var cta = el("a", "cta", "Make yours"); cta.href = ctx.cta; cta.rel = "noreferrer noopener";
  var again = el("button", "ghost", "Watch again"); again.type = "button"; again.dataset.action = "restart";
  var ctas = add(el("div", "ctas"), cta, again);
  var img = el("img", "meadow"); img.src = ctx.base + "/static/meadow.webp"; img.alt = "";
  add(f, el("p", "kicker", ctx.name), el("h1", "headline", "Can your group beat this?"),
    el("p", "sub", "Turn your own chat export into a story like this one. It runs on your device."), ctas, el("div", "grow"), img);
  return f;
}
function footer(ctx, onReport) {
  var d = el("div", "foot");
  add(d, archSvg(), el("span", "", "made with Edge"), el("span", "sp"));
  var r = el("button", "linkbtn", "Report"); r.type = "button"; r.addEventListener("click", function (e) { e.stopPropagation(); onReport(); });
  d.appendChild(r);
  return d;
}

/* ------------------------------------------------------------------ story player */
function Player(story, frames, ctx) {
  var i = 0, DUR = 6000, self = this, prog = el("div", "progress"), segs = [];
  frames.forEach(function (f) {
    f.appendChild(footer(ctx, function () { self.report(); }));
    story.appendChild(f);
    var s = el("div", "seg"), fill = el("i"); s.appendChild(fill); prog.appendChild(s); segs.push(s);
    fill.addEventListener("animationend", function () { if (segs.indexOf(s) === i) self.go(i + 1); });
  });
  story.appendChild(prog);
  var prev = el("button", "tap prev"), next = el("button", "tap next");
  prev.type = next.type = "button"; prev.setAttribute("aria-label", "Previous"); next.setAttribute("aria-label", "Next");
  story.appendChild(prev); story.appendChild(next);
  var navL = el("button", "nav l", "‹"), navR = el("button", "nav r", "›");
  navL.type = navR.type = "button"; navL.setAttribute("aria-label", "Previous"); navR.setAttribute("aria-label", "Next");
  story.parentNode.appendChild(navL); story.parentNode.appendChild(navR);

  this.go = function (n) {
    if (n < 0 || n >= frames.length) return;
    i = n;
    frames.forEach(function (f, k) { f.classList.toggle("on", k === i); });
    segs.forEach(function (s, k) {
      s.classList.remove("run"); s.classList.toggle("done", k < i);
      if (k === i) { void s.offsetWidth; s.classList.add(i === frames.length - 1 ? "done" : "run"); }
    });
    story.classList.toggle("dark", frames[i].dataset.dark === "1");
    story.classList.toggle("last", i === frames.length - 1);
    navL.disabled = i === 0; navR.disabled = i === frames.length - 1;
  };
  this.report = function () { story.classList.add("paused"); reportSheet(story, ctx, function () { story.classList.remove("paused"); }); };
  story.style.setProperty("--dur", DUR + "ms");
  var swiped = false;
  prev.addEventListener("click", function () { if (swiped) { swiped = false; return; } self.go(i - 1); });
  next.addEventListener("click", function () { if (swiped) { swiped = false; return; } self.go(i + 1); });
  navL.addEventListener("click", function () { self.go(i - 1); });
  navR.addEventListener("click", function () { self.go(i + 1); });
  story.addEventListener("click", function (e) { if (e.target.dataset && e.target.dataset.action === "restart") self.go(0); });
  var holdT = null;
  story.addEventListener("pointerdown", function () { holdT = setTimeout(function () { story.classList.add("paused"); }, 180); });
  ["pointerup", "pointercancel", "pointerleave"].forEach(function (ev) {
    story.addEventListener(ev, function () { clearTimeout(holdT); if (!story.querySelector(".sheet")) story.classList.remove("paused"); });
  });
  var sx = null;
  story.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
  story.addEventListener("touchend", function (e) {
    if (sx === null) return;
    var dx = e.changedTouches[0].clientX - sx; sx = null;
    if (Math.abs(dx) > 60) { swiped = true; setTimeout(function () { swiped = false; }, 400); self.go(i + (dx < 0 ? 1 : -1)); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); self.go(i + 1); }
    if (e.key === "ArrowLeft") self.go(i - 1);
  });
  document.addEventListener("visibilitychange", function () { story.classList.toggle("paused", document.hidden); });
  this.go(0);
}

function reportSheet(story, ctx, done) {
  if (story.querySelector(".sheet")) return;
  var s = el("div", "sheet"); s.setAttribute("role", "dialog"); s.setAttribute("aria-label", "Report this story");
  var opts = el("div", "opts");
  var reasons = [["spam", "Spam"], ["harmful", "Hateful or harmful"], ["personal_info", "Shares someone's private information"], ["other", "Something else"]];
  function close() { s.remove(); done(); }
  reasons.forEach(function (r) {
    var b = el("button", "", r[1]); b.type = "button";
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      fetch(ctx.base + "/api/report/" + ctx.id, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: r[0] }), credentials: "omit", referrerPolicy: "no-referrer", cache: "no-store" })
        .catch(function () {});
      opts.replaceChildren(el("p", "", "Thanks. The report reached the team; the link stays up until it is reviewed."));
      setTimeout(close, 2200);
    });
    opts.appendChild(b);
  });
  var c = el("button", "cancel", "Cancel"); c.type = "button"; c.addEventListener("click", function (e) { e.stopPropagation(); close(); });
  add(s, el("h2", "", "Report this story"), el("p", "", "Only the reason is sent. The story itself stays encrypted."), opts, c);
  s.addEventListener("click", function (e) { e.stopPropagation(); });
  s.addEventListener("pointerdown", function (e) { e.stopPropagation(); });
  story.appendChild(s);
}

function message(story, ctx, title, sub) {
  story.replaceChildren();
  var f = el("section", "frame on msg t-paper");
  var cta = el("a", "cta", "Make yours"); cta.href = ctx.cta; cta.rel = "noreferrer noopener";
  add(f, el("p", "kicker", ctx.name), el("h1", "headline", title), el("p", "sub", sub), add(el("div", "ctas"), cta));
  story.appendChild(f);
}

async function main() {
  var b = document.body, story = document.querySelector(".story");
  var ctx = { base: b.dataset.base, id: b.dataset.id, name: b.dataset.name, cta: b.dataset.cta };
  var m = /(?:^#|&)k=([A-Za-z0-9_-]{43})(?:&|$)/.exec(location.hash);
  if (!m) return message(story, ctx, "This link is missing its key.", "The key is the part after # in the link. Ask the sender to copy the whole link.");
  var res, data, schema;
  try {
    var opts = { cache: "no-store", credentials: "omit", referrerPolicy: "no-referrer" };
    var r = await Promise.all([fetch(ctx.base + "/api/shares/" + ctx.id, opts), fetch(ctx.base + "/static/schema-v1.json", opts)]);
    res = r[0];
    if (res.status === 410 || res.status === 404) return message(story, ctx, "This story has expired or was deleted.", "Links last up to 30 days. Ask the sender for a new one, or make your own.");
    if (!res.ok || !r[1].ok) throw new Error("load");
    data = await res.json(); schema = await r[1].json();
  } catch (e) {
    return message(story, ctx, "The story did not load.", "Check your connection and open the link again.");
  }
  var payload;
  try {
    if (data.v !== schema.version) throw new Error("version");
    payload = await decrypt(m[1], data.iv, data.ct, schema.aad);
  } catch (e) {
    return message(story, ctx, "This link's key does not fit.", "Part of the link may be missing. Ask the sender to copy the whole link.");
  }
  var err = validate(schema, payload);
  if (err) return message(story, ctx, "This story could not be shown.", "Its contents did not pass the safety check, so nothing was displayed.");
  story.replaceChildren();
  new Player(story, buildFrames(payload, ctx), ctx);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { validate: validate, checkField: checkField };
} else if (typeof document !== "undefined") {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", main); else main();
}
