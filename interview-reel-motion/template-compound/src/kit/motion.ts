// Small deterministic motion helpers (no external deps): cubic-bezier easings and tweens.
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
    t = Math.min(1, Math.max(0, t));
    return sy(t);
  };
}
export const snappyOut = bezier(0, 0.6, 0.4, 1);
export const expoOut = bezier(0, 1, 0, 1);
export const inOut = bezier(0.7, 0, 0.3, 1);
export const snappyIn = bezier(0.6, 0, 1, 0.4);
export const backOut = bezier(0.34, 1.56, 0.64, 1);

export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));

/** value of a tween that starts at t0 and lasts dur seconds */
export function tw(t: number, t0: number, dur: number, from: number, to: number, ease = snappyOut) {
  const p = clamp((t - t0) / dur);
  return from + (to - from) * ease(p);
}

export const fmt = (n: number) => Math.round(n).toLocaleString("en-US");
