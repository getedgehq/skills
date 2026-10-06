// engine.js: builds a whole interview short from three data files, as one HyperFrames composition.
//   reel.json      cut list (clips), framing boxes and keys, audio, end fade, caption style
//   beats.json     time + phrase -> component + props (the beat map)
//   captions.json  phrase captions (2 to 5 words, one speaker each) with their y
// Layers, bottom to top: scene fill, panels, A-roll (Framer), overlay beats, captions, end fade.
// The page has one clock: render(t) sets every pixel from scene time t. HyperFrames drives it through
// hf-seek (and the player's renderSeek); a #t=<seconds> hash seeks a plain headless capture.
(function () {
  const IRM = window.IRM;
  const D = window.IRM_DATA;
  const { clamp, easeInOut } = IRM;
  const N = IRM.nodes, K = IRM.kit, R = IRM.rules;
  const r = D.reel, END = r.scene.duration, QA = D.qa || "";
  const FPS = R.FPS;
  IRM.asset = (p) => (/^(https?:|data:|assets\/)/.test(p) ? p : "assets/" + p);

  /* ------------------------------------------------------------------ cut list -> pieces */
  function pieces() {
    const out = [];
    const inBlank = (t) => r.blank.some(([a, b]) => t >= a - 1e-6 && t < b - 1e-6);
    r.clips.forEach((c, ci) => {
      const cuts = [c.start, ...r.splits.filter((b) => b > c.start + 1e-6 && b < c.end - 1e-6), c.end].sort((a, b) => a - b);
      for (let i = 0; i < cuts.length - 1; i++) {
        const a = cuts[i], b = cuts[i + 1];
        if (inBlank(a)) continue;
        out.push({ start: a, end: b, sin: c.sin + (a - c.start) * c.rate, rate: c.rate, src: c.src ?? r.footage, key: `v${ci}_${i}` });
      }
    });
    return out;
  }
  function keysFor(p) {
    const Kk = r.keys;
    let a = 0, b = Kk.length - 1;
    Kk.forEach((k, i) => { if (k[0] <= p.start + 1e-6) a = i; });
    for (let i = Kk.length - 1; i >= 0; i--) if (Kk[i][0] >= p.end - 1e-6) b = i;
    if (b < a) b = a;
    const box = (x) => (typeof x === "string" ? r.framings[x] : x);
    const ks = Kk.slice(a, b + 1).map((k) => ({ t: k[0], box: box(k[1]), m: k[2], ease: k[3] ?? "io" }));
    if (ks.length > 5) throw new Error(`framing keys > 5 for ${p.key}: add a split`);
    return ks;
  }
  IRM.pieces = pieces; IRM.keysFor = keysFor;

  /* ------------------------------------------------------------------ Framer: keyed box + card morph */
  // Each key is a framing box (where the full source frame sits, in frame px) plus a card amount m:
  // 0 = full frame, 1 = the face card (rounded rect, radius grows with m). Box and mask ease together,
  // so a punch-in is a push and full <-> split is a morph. Here: a CSS transform on the frame image and
  // a clip-path inset(... round r) on the layer (the WGSL shader of the Compound version, same maths).
  const bezIO = IRM.bezier(0.7, 0, 0.3, 1);
  const ez = (p, e) => (e === "sin" ? 0.5 - 0.5 * Math.cos(Math.PI * p) : e === "lin" ? p : e === "eo" ? (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p)) : bezIO(p));
  const mix = (a, b, k) => a + (b - a) * k;
  const mix4 = (a, b, k) => [0, 1, 2, 3].map((i) => mix(a[i], b[i], k));
  function framing(keys, t) {
    const n = keys.length;
    let box = keys[0].box, m = keys[0].m ?? 0;
    if (n > 1 && t > keys[0].t) {
      box = keys[n - 1].box; m = keys[n - 1].m ?? 0;
      for (let i = 1; i < n; i++) {
        if (t <= keys[i].t) {
          const p = clamp((t - keys[i - 1].t) / Math.max(1e-4, keys[i].t - keys[i - 1].t));
          const k = ez(p, keys[i].ease);
          box = mix4(keys[i - 1].box, keys[i].box, k); m = mix(keys[i - 1].m ?? 0, keys[i].m ?? 0, k);
          break;
        }
      }
    }
    return { box, m };
  }
  const P = pieces().map((p) => ({ ...p, keys: keysFor(p) }));
  const card = [r.card.x, r.card.y, r.card.width, r.card.height];
  const stackIdx = (p, t) => { const st = D.stacks[p.src]; const f = Math.floor((p.sin + (t - p.start) * p.rate) * st.fps + (D.reel.framePhase ?? 1e-3)); return Math.max(st.first, Math.min(st.last, f)); };
  /** the A-roll state at t: active piece, framing box, card mask rect and radius, source frame */
  function arollAt(t) {
    const p = P.find((q) => t >= q.start - 1e-6 && t < q.end - 1e-6);
    if (!p) return null;
    const { box, m } = framing(p.keys, t);
    const Rr = mix4([0, 0, R.W, R.H], card, m);
    return { p, box, m, R: Rr, rad: r.card.radius * m, idx: stackIdx(p, t), st: D.stacks[p.src] };
  }
  IRM.arollAt = arollAt;
  /** the frame stacks: one <img> per source frame the cut needs (built here, not in markup, so a compiler that
   *  rewrites the page cannot drop them); a frame is shown by toggling display, never by seeking a <video> */
  const stackEls = {};
  function stackEl(kind) {
    if (stackEls[kind]) return stackEls[kind];
    const el = N.mk(`position:absolute;left:0;top:0;width:${R.W}px;height:${R.H}px;background:${kind === "aroll" ? "#09090B" : "transparent"};display:none;`);
    el.id = `${kind}-stack`;
    for (const src in D.stacks) {
      const st = D.stacks[src];
      const frames = kind === "aroll" ? st.frames : (D.matte || {})[st.key] || [];
      for (const f of frames) {
        const im = document.createElement("img");
        im.alt = ""; im.decoding = "sync"; im.width = st.w; im.height = st.h; im.dataset.k = `${st.key}/${f}`;
        im.setAttribute("style", "position:absolute;left:0;top:0;transform-origin:0 0;display:none;max-width:none;");
        im.src = kind === "aroll" ? `stacks/${st.key}/${f}.${D.ext}` : `stacks/matte/${st.key}/${f}.apng`;
        el.appendChild(im);
      }
    }
    stackEls[kind] = el;
    return el;
  }
  const imgsLoaded = (el) => Promise.all([...el.querySelectorAll("img")].map((im) => (im.complete && im.naturalWidth ? null : new Promise((res) => { im.addEventListener("load", res, { once: true }); im.addEventListener("error", res, { once: true }); }))));
  /** a footage layer (A-roll, or a matte copy for occlusion) that follows the Framer */
  function framerNode(kind) {
    const el = stackEl(kind);
    const imgs = new Map();
    el.querySelectorAll("img").forEach((im) => imgs.set(im.dataset.k, im));
    let shown = null;
    return {
      el,
      update(t) {
        const a = arollAt(t);
        if (!a) { el.style.display = "none"; return; }
        el.style.display = "block";
        const [x, y, w, h] = a.R;
        el.style.clipPath = `inset(${y.toFixed(2)}px ${(R.W - x - w).toFixed(2)}px ${(R.H - y - h).toFixed(2)}px ${x.toFixed(2)}px round ${a.rad.toFixed(2)}px)`;
        const im = imgs.get(`${a.st.key}/${a.idx}`);
        if (shown && shown !== im) shown.style.display = "none";
        if (im) {
          im.style.display = "block";
          im.style.transform = `translate(${a.box[0].toFixed(3)}px, ${a.box[1].toFixed(3)}px) scale(${(a.box[2] / a.st.w).toFixed(6)}, ${(a.box[3] / a.st.h).toFixed(6)})`;
        }
        shown = im || null;
      },
    };
  }

  /* ------------------------------------------------------------------ registry */
  const EXITF = R.EXIT_FRAMES;
  /** group pinned to the scene clock: opacity eases in over din frames and out over d frames */
  function Out(id, s, e, din, d, children) {
    const keys = [];
    if (din) keys.push([s, 0, easeInOut]);
    keys.push([din ? s + din / FPS : s, 1]);
    keys.push([e - (d ?? EXITF) / FPS, 1, easeInOut]);
    keys.push([e, 0]);
    return N.group({ id, e: END, keys, children });
  }
  const threeNodes = [];
  function threeNode(kind, p) {
    const W = p.width ?? 1080, H = p.height ?? (kind === "TypeRing" ? 1080 : 900);
    const el = N.mk(N.abspx(p.x ?? 0, p.y ?? (kind === "TypeRing" ? 420 : 500), W, H) + "display:none;", "canvas");
    el.width = W; el.height = H;
    const node = { el, impl: null, kind, p, update(t) { const on = N.live(t, p.s, p.e); el.style.display = on ? "block" : "none"; if (on && node.impl) node.impl.update(t); } };
    threeNodes.push(node);
    return node;
  }
  const cards = (list) => list.map((c) => (c.kind === "video" ? K.videoCard(c.title, c.sub, c.src && IRM.asset(c.src)) : c.kind === "phone" ? K.phoneCard(c.title, c.sub, c.src && IRM.asset(c.src)) : c.kind === "stat" ? K.statCard(c.title, c.sub) : K.imageCard(IRM.asset(c.src))));
  const Pp = (b) => b.props ?? {};
  const OWN = {
    Cover: (b, s, e) => K.Cover({ id: b.id, s, e, ...Pp(b) }),
    LowerThird: (b, s, e) => K.LowerThird({ id: b.id, s, e, ...Pp(b) }),
    Headline: (b, s, e) => K.Headline({ id: b.id, s, e, ...Pp(b) }),
    CompareCards: (b, s, e) => K.CompareCards({ id: b.id, s, e, ...Pp(b) }),
    BlockMeter: (b, s, e) => K.BlockMeter({ id: b.id, s, e, ...Pp(b) }),
    EndCard: (b, s, e) => K.EndCard({ id: b.id, s, e, ...Pp(b) }),
    StickerStack: (b, s, e) => K.StickerStack({ id: b.id, s, e, ...Pp(b) }),
    BrandChip: (b, s, e) => K.BrandChip({ id: b.id, s, e, ...Pp(b) }),
    /** native text line (attribution, labels): no wrapper, it ends with the reel's fade */
    Text: (b, s, e) => { const p = Pp(b); return N.text({ id: b.id, x: p.x, y: p.y, w: p.width, h: p.height ?? 70, s, e, text: p.text, font: p.font ?? "Inter", weight: p.weight ?? 700, size: p.size ?? 44, tracking: p.tracking ?? -0.6, color: p.color ?? "#A0A0A5" }); },
  };
  const WRAPPED = {
    Sticker: (b, s, e) => K.Sticker({ id: `${b.id}c`, s, e, ...Pp(b) }),
    KineticWord: (b) => K.KineticWord({ id: `${b.id}c`, ...Pp(b) }),
    ChatPrompt: (b, s, e) => K.ChatPrompt({ id: `${b.id}c`, s, e, ...Pp(b) }),
    BarChart: (b, s, e) => K.BarChart({ id: `${b.id}c`, s, e, ...Pp(b) }),
    TileGrid: (b, s, e) => K.TileGrid({ id: `${b.id}c`, s, e, ...Pp(b) }),
    CounterBar: (b, s, e) => K.CounterBar({ id: `${b.id}c`, s, e, ...Pp(b) }),
    TypeRing: (b, s, e) => threeNode("TypeRing", { id: `${b.id}c`, s, e, ...Pp(b) }),
    OrbitCards: (b, s, e) => { const p = Pp(b); return K.OrbitCards({ id: `${b.id}c`, s, e, ...p, cards: cards(p.cards ?? []) }); },
    Arrow: (b, s, e) => K.Arrow({ id: `${b.id}c`, s, e, ...Pp(b) }),
    Plate: (b, s, e) => { const p = Pp(b); return N.rect({ id: `${b.id}c`, x: p.x, y: p.y, w: p.width, h: p.height, radius: p.radius ?? 28, fill: p.fill ?? "rgba(9,9,11,0.93)", s, e }); },
    Image: (b, s, e) => { const p = Pp(b); return N.img({ id: `${b.id}c`, src: IRM.asset(p.src), x: p.x, y: p.y, w: p.width, h: p.height, radius: p.radius ?? 0, s, e }); },
    /** the signature full-frame moment, once per reel: ground + ParticleText */
    Takeover: (b, s, e) => {
      const p = Pp(b);
      return N.frag([
        N.rect({ id: `${b.id}g`, x: 0, y: 0, w: 1080, h: 1920, fill: p.ground ?? "#09090B", s, e }),
        threeNode("ParticleText", { id: `${b.id}c`, s, e, text: p.text, size: p.size ?? 180, y: p.y ?? 510, height: p.height ?? 900, resolve: p.resolve ?? 0.55, dissolve: p.dissolve ?? 0.12, ...(p.extra ?? {}) }),
      ]);
    },
    ParticleText: (b, s, e) => threeNode("ParticleText", { id: `${b.id}c`, s, e, ...Pp(b) }),
    /** occlusion: the person matte (RGBA frames from scripts/matte_rvm.py) over the back layers, same framing as the A-roll */
    Matte: (b, s, e) => { const n = framerNode("matte"); return { el: n.el, update(t) { if (N.live(t, s, e)) n.update(t); else n.el.style.display = "none"; } }; },
  };
  function renderBeat(b) {
    const own = OWN[b.component];
    if (own) return own(b, b.t0, b.t1);
    const w = WRAPPED[b.component];
    if (!w) throw new Error(`unknown beat component ${b.component} (${b.id})`);
    return Out(b.id, b.t0, b.t1, b.fadeIn, b.exit, [w(b, b.t0, b.t1)]);
  }

  /* ------------------------------------------------------------------ assemble */
  // The scene is built from data, so it can be rebuilt: a HyperFrames runtime may re-mount the composition root
  // from the original markup after page scripts ran (the Lambda renderer does), which drops script-built nodes.
  // render() checks the marker and re-assembles into whatever #reel-layers is live, then draws the frame.
  let stage = null, nodes = [];
  function assemble() {
    stage = document.getElementById("reel-layers");
    if (!stage) return false;
    nodes = []; threeNodes.length = 0;
    stage.textContent = "";
    const add = (n) => { stage.appendChild(n.el); nodes.push(n); };
    const fill = N.mk(`position:absolute;inset:0;background:${QA === "gfx" ? "#FF00FF" : r.scene.fill};`);
    fill.dataset.irm = "1";
    stage.appendChild(fill);
    const panels = D.beats.filter((b) => b.layer === "panel"), overlay = D.beats.filter((b) => b.layer !== "panel");
    if (QA === "") panels.forEach((b) => add(renderBeat(b)));
    if (QA !== "gfx") add(framerNode("aroll"));
    if (QA !== "foot") overlay.forEach((b) => add(renderBeat(b)));
    const cs = r.captionStyle;
    if (QA !== "foot") D.captions.forEach((c, i) => add(N.text({ id: `cap${i}`, x: cs.x, y: c.y - cs.height / 2, w: cs.width, h: cs.height, s: c.t0, e: c.t1, text: c.text, align: "center", weight: cs.weight, size: cs.size, tracking: cs.tracking, color: cs.color, shadow: cs.shadow })));
    const fade = r.end.fadeFrames / FPS, fs = R.snap(END - fade);
    add(N.rect({ id: "endfade", x: 0, y: 0, w: R.W, h: R.H, fill: "#000000", s: fs, e: END + 1, keys: [[0, 0, easeInOut], [fade, 1]] }));
    if (window.__irmReady) for (const n of threeNodes) n.impl = IRM.three[n.kind](n.p, n.el);
    return true;
  }
  const live = () => stage && stage.isConnected && stage === document.getElementById("reel-layers") && stage.firstChild && stage.firstChild.dataset && stage.firstChild.dataset.irm === "1";

  /* ------------------------------------------------------------------ clock */
  let cur = 0;
  function render(t) {
    cur = Math.max(0, Math.min(END - 1e-6, +t || 0));
    if (!live() && !assemble()) return;
    for (const n of nodes) n.update(cur);
  }
  IRM.render = render;
  window.seek = render;
  // readiness: fonts, then the three.js pieces (they rasterise type at build time)
  let threeOk;
  const threeLoaded = new Promise((res) => (threeOk = res));
  IRM.threeLoaded = () => threeOk();
  const weights = [500, 600, 700, 800, 900];
  const fontsReady = Promise.all(weights.map((w) => document.fonts.load(`${w} 40px Inter`))).then(() => document.fonts.ready).catch(() => null);
  const needsThree = D.beats.some((b) => ["TypeRing", "ParticleText", "Takeover"].includes(b.component));
  const stacksReady = Promise.all([imgsLoaded(stackEl("aroll")), imgsLoaded(stackEl("matte"))]);
  IRM.ready = Promise.all([fontsReady, stacksReady, needsThree ? threeLoaded : Promise.resolve()]).then(() => {
    if (!live()) assemble();
    for (const n of threeNodes) n.impl = IRM.three[n.kind](n.p, n.el);
    render(cur);
    window.__irmReady = true;
  });
  window.__hf = window.__hf || {};
  window.__hf.buildReady = Object.assign(window.__hf.buildReady || {}, { irm: IRM.ready });
  window.addEventListener("hf-seek", (ev) => {
    const d = ev.detail || {};
    render(d.time);
    if (!window.__irmReady && typeof d.waitUntil === "function") d.waitUntil(IRM.ready.then(() => render(d.time)));
  });
  // the player's own seek (Lambda capture path): wrap renderSeek so every captured frame is rendered first
  const bridge = () => {
    const pl = window.__player;
    if (!pl || typeof pl.renderSeek !== "function") return false;
    if (pl.__irmBridge) return true;
    const f = pl.renderSeek.bind(pl);
    pl.renderSeek = (t, o) => { const out = f(t, o); render(t); return out; };
    pl.__irmBridge = true;
    return true;
  };
  if (!bridge()) { const iv = setInterval(() => { if (bridge()) clearInterval(iv); }, 25); }
  // keep the scene mounted if the runtime swaps the root after load (re-render the current frame)
  setInterval(() => { if (!live()) render(cur); }, 50);
  const m = /[#&?]t=([0-9.]+)/.exec(location.hash + location.search);
  render(m ? parseFloat(m[1]) : 0);
  IRM.ready.then(() => render(m ? parseFloat(m[1]) : cur));
})();
