// clock.js: one clock for the whole kit. Every value is a pure function of composition time t
// (seconds), so a HyperFrames seek, a #t= capture and the final render land on the same pixels.
// Easings are the kit's six cubic beziers plus backOut (objects only, never type).
(function () {
  const IRM = (window.IRM = window.IRM || {});
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  function bezier(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = (t) => ((ax * t + bx) * t + cx) * t;
    const sy = (t) => ((ay * t + by) * t + cy) * t;
    const dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
    return (x) => {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      let t = x;
      for (let i = 0; i < 8; i++) {
        const d = dx(t);
        if (Math.abs(d) < 1e-6) break;
        t -= (sx(t) - x) / d;
      }
      let lo = 0, hi = 1;
      if (Math.abs(sx(t) - x) > 1e-4) {
        t = x;
        for (let i = 0; i < 30; i++) { const v = sx(t); if (v < x) lo = t; else hi = t; t = (lo + hi) / 2; }
      }
      return sy(clamp(t));
    };
  }
  const snappyOut = bezier(0, 0.6, 0.4, 1);
  const expoOut = bezier(0, 1, 0, 1);
  const snappyIn = bezier(0.6, 0, 1, 0.4);
  const expoIn = bezier(1, 0, 1, 0);
  const outIn = bezier(0, 0.7, 1, 0.3);
  const inOut = bezier(0.7, 0, 0.3, 1);
  const backOut = bezier(0.34, 1.56, 0.64, 1);
  /** the keyframe "easeInOut" of the Compound engine (group and fade tracks) */
  const easeInOut = bezier(0.42, 0, 0.58, 1);
  const cubicOut = (n) => 1 - Math.pow(1 - clamp(n), 3);
  const tw = (t, t0, dur, from, to, ease = snappyOut) => from + (to - from) * ease(clamp((t - t0) / dur));
  const prog = (t, t0, dur, ease = snappyOut) => ease(clamp((t - t0) / dur));
  /** Soften: blur + opacity resolve to sharp, hold, optional resolve out. Position is never touched. */
  function soften(p, inD = 0.27, outStart = Infinity, outD = 0, blurIn = 13, blurOut = 9) {
    if (p < 0) return { o: 0, b: blurIn };
    if (p < inD) { const a = cubicOut(p / inD); return { o: a, b: blurIn * (1 - a) }; }
    if (p < outStart) return { o: 1, b: 0 };
    if (outD <= 0) return { o: 0, b: 0 };
    if (p < outStart + outD) { const c = cubicOut((p - outStart) / outD); return { o: 1 - c, b: blurOut * c }; }
    return { o: 0, b: blurOut };
  }
  const softStyle = (e) => `opacity:${e.o.toFixed(3)};filter:${e.b > 0.05 ? `blur(${e.b.toFixed(2)}px)` : "none"};`;
  /** deterministic PRNG (mulberry32) */
  function rng(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  /** keyed value track: [{t, v, ease}] with the ease applied INTO each key; equal keys hold exactly still */
  function track(keys, t) {
    if (t <= keys[0].t) return keys[0].v;
    for (let i = 1; i < keys.length; i++) {
      const a = keys[i - 1], b = keys[i];
      if (t <= b.t) return a.v + (b.v - a.v) * (b.ease || inOut)(clamp((t - a.t) / (b.t - a.t)));
    }
    return keys[keys.length - 1].v;
  }
  /** keyframe track with the ease applied OUT of each key (Compound keyframeTrack semantics) */
  function kfTrack(keys, t) {
    if (!keys.length) return 1;
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const a = keys[i - 1], b = keys[i];
      if (t <= b[0]) { const p = clamp((t - a[0]) / Math.max(1e-9, b[0] - a[0])); return a[1] + (b[1] - a[1]) * (a[2] || ((x) => x))(p); }
    }
    return keys[keys.length - 1][1];
  }
  const C = { ground: "#09090B", ink: "#FAFAFC", grey: "#A0A0A5", cell: "#18181A", cell2: "#1A1A1A", line: "rgba(250,250,252,0.10)" };
  const FONT = "Inter";
  const css = (o) => Object.entries(o).filter(([, v]) => v !== undefined && v !== null && v !== "").map(([k, v]) => `${k}:${v}`).join(";") + ";";
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  /** motion.ts variant (Overlays): Newton only, no bisection fallback; kept separate so the overlays match 1:1 */
  function bezierM(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = (t) => ((ax * t + bx) * t + cx) * t;
    const sy = (t) => ((ay * t + by) * t + cy) * t;
    const dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
    return (x) => {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      let t = x;
      for (let i = 0; i < 8; i++) { const d = dx(t); if (Math.abs(d) < 1e-6) break; t -= (sx(t) - x) / d; }
      return sy(Math.min(1, Math.max(0, t)));
    };
  }
  const M = { snappyOut: bezierM(0, 0.6, 0.4, 1), expoOut: bezierM(0, 1, 0, 1), inOut: bezierM(0.7, 0, 0.3, 1), snappyIn: bezierM(0.6, 0, 1, 0.4), backOut: bezierM(0.34, 1.56, 0.64, 1) };
  M.tw = (t, t0, dur, from, to, ease = M.snappyOut) => from + (to - from) * ease(clamp((t - t0) / dur));
  IRM.M = M;
  Object.assign(IRM, { clamp, bezier, snappyOut, expoOut, snappyIn, expoIn, outIn, inOut, backOut, easeInOut, cubicOut, tw, prog, soften, softStyle, rng, track, kfTrack, C, FONT, css, esc });
})();
