// One clock for the whole kit, ported from the approved Edge motion catalogue
// (~/Projects/edge-video-factory/mocks/motion-catalogue.html, runtime "clock" block):
// every unit is a pure function of composition time t (seconds), so scrubbing,
// capture and export all land on the same pixels. Easings are the six from
// compound-docs/guides/motion/easings.md.

export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));

function bezier(x1: number, y1: number, x2: number, y2: number) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = (t: number) => ((ax * t + bx) * t + cx) * t;
  const sy = (t: number) => ((ay * t + by) * t + cy) * t;
  const dx = (t: number) => (3 * ax * t + 2 * bx) * t + cx;
  return (x: number) => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 8; i++) {
      const d = dx(t);
      if (Math.abs(d) < 1e-6) break;
      t -= (sx(t) - x) / d;
    }
    // bisection fallback for flat-slope curves (expoOut)
    let lo = 0, hi = 1;
    if (Math.abs(sx(t) - x) > 1e-4) {
      t = x;
      for (let i = 0; i < 30; i++) { const v = sx(t); if (v < x) lo = t; else hi = t; t = (lo + hi) / 2; }
    }
    return sy(clamp(t));
  };
}
export type Ease = (x: number) => number;
export const snappyOut = bezier(0, 0.6, 0.4, 1);
export const expoOut = bezier(0, 1, 0, 1);
export const snappyIn = bezier(0.6, 0, 1, 0.4);
export const expoIn = bezier(1, 0, 1, 0);
export const outIn = bezier(0, 0.7, 1, 0.3);
export const inOut = bezier(0.7, 0, 0.3, 1);
/** Overshoot for OBJECTS only (cards, pills, bars). Never on type. */
export const backOut = bezier(0.34, 1.56, 0.64, 1);
export const cubicOut: Ease = (n) => 1 - Math.pow(1 - clamp(n), 3); // catalogue `ease`

/** Tween value: starts at t0, lasts dur seconds. */
export const tw = (t: number, t0: number, dur: number, from: number, to: number, ease: Ease = snappyOut) =>
  from + (to - from) * ease(clamp((t - t0) / dur));

/** Progress 0..1 of a window. */
export const prog = (t: number, t0: number, dur: number, ease: Ease = snappyOut) => ease(clamp((t - t0) / dur));

/**
 * The catalogue's Soften envelope: blur+opacity resolve to sharp, hold, then
 * (optionally) resolve out. Position is never touched: TYPE NEVER MOVES.
 * p = local time; inD = in duration; outStart/outD = exit (outD 0 = hard off).
 */
export function soften(p: number, inD = 0.27, outStart = Infinity, outD = 0, blurIn = 13, blurOut = 9) {
  if (p < 0) return { o: 0, b: blurIn };
  if (p < inD) { const a = cubicOut(p / inD); return { o: a, b: blurIn * (1 - a) }; }
  if (p < outStart) return { o: 1, b: 0 };
  if (outD <= 0) return { o: 0, b: 0 }; // hard off
  if (p < outStart + outD) { const c = cubicOut((p - outStart) / outD); return { o: 1 - c, b: blurOut * c }; }
  return { o: 0, b: blurOut };
}
export const softStyle = (e: { o: number; b: number }) => ({ opacity: e.o.toFixed(3), filter: e.b > 0.05 ? `blur(${e.b.toFixed(2)}px)` : "none" });

/** Deterministic PRNG (mulberry32) so particle fields are identical in every mount. */
export function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Keyframed value track (camera-stage semantics): between two equal keys the value is EXACTLY still. */
export type Key = { t: number; v: number; ease?: Ease };
export function track(keys: Key[], t: number) {
  if (t <= keys[0].t) return keys[0].v;
  for (let i = 1; i < keys.length; i++) {
    const a = keys[i - 1], b = keys[i];
    if (t <= b.t) return a.v + (b.v - a.v) * (b.ease ?? inOut)(clamp((t - a.t) / (b.t - a.t)));
  }
  return keys[keys.length - 1].v;
}

/** Monochrome palette from the style guide's GRAPHIC LANGUAGE. */
export const C = { ground: "#09090B", ink: "#FAFAFC", grey: "#A0A0A5", cell: "#18181A", cell2: "#1A1A1A", line: "rgba(250,250,252,0.10)" };
export const FONT = "Inter";
