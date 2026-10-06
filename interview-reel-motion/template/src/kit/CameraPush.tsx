// CameraPush: a slow perspective push / tilt / pan on the footage layer.
// Port of remocn camera-stage (MIT, see THIRD_PARTY_NOTICES): a REAL camera with a perspective distance P, a KEYFRAMED
// path (between two equal keys the camera is exactly still, so a hold is a
// true hold), on-screen scale P / (P - z). Compound has no 3D transform for
// <video>, so the projection runs as a <shaderPaint> over the clip: each output
// pixel casts a ray through a pinhole camera and samples the footage plane,
// which can be pushed (z), panned (x, y) and tilted (rx, ry degrees).
// Driven by globals.time (the clip's playhead), so it is frame-accurate in exports.
import type { JSX } from "solid-js";

export type CamKey = { t: number; z?: number; x?: number; y?: number; rx?: number; ry?: number };

const WGSL = /* wgsl */ `
@group(1) @binding(0) var<uniform> kt: vec4f;
@group(1) @binding(1) var<uniform> kz: vec4f;
@group(1) @binding(2) var<uniform> kx: vec4f;
@group(1) @binding(3) var<uniform> ky: vec4f;
@group(1) @binding(4) var<uniform> krx: vec4f;
@group(1) @binding(5) var<uniform> kry: vec4f;
@group(1) @binding(6) var<uniform> cfg: vec4f;
@group(1) @binding(7) var<uniform> off: f32;

// inOut = cubic-bezier(0.7, 0, 0.3, 1) (compound-docs easings.md), Newton solve
fn bez(x: f32) -> f32 {
  let x1 = 0.7; let x2 = 0.3;
  let cx = 3.0 * x1; let bx = 3.0 * (x2 - x1) - cx; let ax = 1.0 - cx - bx;
  let cy = 0.0; let by = 3.0 * (1.0 - 0.0) - cy; let ay = 1.0 - cy - by;
  var t = x;
  for (var i = 0; i < 8; i++) {
    let sx = ((ax * t + bx) * t + cx) * t - x;
    let d = (3.0 * ax * t + 2.0 * bx) * t + cx;
    if (abs(d) < 1e-5) { break; }
    t = clamp(t - sx / d, 0.0, 1.0);
  }
  return ((ay * t + by) * t + cy) * t;
}
fn trk(k: vec4f, t: f32) -> f32 {
  let n = i32(cfg.y);
  if (t <= kt[0] || n < 2) { return k[0]; }
  for (var i = 1; i < 4; i++) {
    if (i >= n) { break; }
    if (t <= kt[i]) {
      let p = clamp((t - kt[i - 1]) / max(1e-4, kt[i] - kt[i - 1]), 0.0, 1.0);
      return mix(k[i - 1], k[i], bez(p));
    }
  }
  return k[n - 1];
}

@fragment
fn main(@location(0) uv: vec2f) -> @location(0) vec4f {
  let t = globals.time - off;
  let res = globals.resolution;
  let P = cfg.x;
  let A = cfg.zw * res;
  let z = trk(kz, t);
  let pan = vec2f(trk(kx, t), trk(ky, t));
  let ax = radians(trk(krx, t));
  let ay = radians(trk(kry, t));
  let cxr = cos(ax); let sxr = sin(ax); let cyr = cos(ay); let syr = sin(ay);
  // R = Ry * Rx (columns)
  let R = mat3x3f(
    vec3f(cyr, 0.0, -syr),
    vec3f(syr * sxr, cxr, cyr * sxr),
    vec3f(syr * cxr, -sxr, cyr * cxr)
  );
  let d = uv * res - A;
  let r = vec3f(d, P);
  let D = P - z;
  let C = vec3f(0.0, 0.0, D);
  let n = R * vec3f(0.0, 0.0, 1.0);
  let s = dot(n, C) / dot(n, r);
  let X = s * r;
  let q = transpose(R) * (X - C);
  let src = (A + q.xy + pan) / res;
  if (src.x < 0.0 || src.y < 0.0 || src.x > 1.0 || src.y > 1.0) { return vec4f(0.035, 0.035, 0.043, 1.0); }
  return sampleSource(src);
}
`;

type Props = {
  id?: string;
  src: string; start: number; end: number; sourceIn?: number; playbackRate?: number; muted?: boolean;
  x: number; y: number; width: number; height: number;
  /** keys in SCENE seconds; up to 4. z = push toward the lens (px), x/y pan (px), rx/ry tilt (deg) */
  keys: CamKey[];
  /** perspective distance in px (camera-stage default 1700) */
  persp?: number;
  /** the point the camera pushes into, 0..1 of the box (e.g. the face) */
  anchor?: [number, number];
  children?: JSX.Element;
};

export function CameraPush(p: Props) {
  const ks = p.keys.slice(0, 4);
  const pad = (f: (k: CamKey) => number) => { const a = ks.map(f); while (a.length < 4) a.push(a[a.length - 1]); return a; };
  const uniforms = {
    kt: pad((k) => k.t - p.start),
    kz: pad((k) => k.z ?? 0), kx: pad((k) => k.x ?? 0), ky: pad((k) => k.y ?? 0),
    krx: pad((k) => k.rx ?? 0), kry: pad((k) => k.ry ?? 0),
    off: (p.sourceIn ?? 0),
    cfg: [p.persp ?? 1700, ks.length, (p.anchor ?? [0.5, 0.4])[0], (p.anchor ?? [0.5, 0.4])[1]],
  };
  return (
    <video id={p.id ?? "push"} src={p.src} start={p.start} end={p.end} sourceIn={p.sourceIn ?? 0} playbackRate={p.playbackRate ?? 1} muted={p.muted ?? true} x={p.x} y={p.y} width={p.width} height={p.height}>
      <shaderPaint wgsl={WGSL} uniforms={uniforms} id="errfkr" />
      {p.children}
    </video>
  );
}

// ---- push companions (r4): a frame-space vignette, and a parallax OBJECT (a stat
// card) that drifts at a different rate than the footage push so depth reads.
import { useTicker } from "@compound/jsx";
import { C, FONT, clamp, inOut, soften, softStyle } from "./clock";

export function Vignette(p: { id?: string; s: number; e: number; strength?: number }) {
  const k = p.strength ?? 0.55;
  return (
    <html x={0} y={0} width={1080} height={1920} start={p.s} end={p.e} id={p.id ?? "vig"}>
      <div style={`width:1080px;height:1920px;background:radial-gradient(ellipse 78% 62% at 50% 46%, rgba(9,9,11,0) 55%, rgba(9,9,11,${k}) 100%);`} />
    </html>
  );
}

/** A card that slides and rotates at its own rate while the camera pushes. */
export function ParallaxCard(p: { id?: string; s: number; e: number; x: number; y: number; title: string; stat: string; drift?: number }) {
  const { time } = useTicker();
  const W = 420, H = 190, dur = p.e - p.s;
  const t = () => time() - p.s;
  const k = () => inOut(clamp(t() / dur));
  const enter = () => clamp(t() / 0.35);
  // the card travels ~2.4x the footage push: x drift + a little scale, an object not type
  const tx = () => (1 - enter()) * 160 - k() * (p.drift ?? 90);
  const sc = () => 0.92 + 0.16 * k();
  return (
    <html x={p.x - 60} y={p.y - 60} width={W + 200} height={H + 120} start={p.s} end={p.e} id={p.id ?? "plx"}>
      <div style={{ position: "absolute", left: "60px", top: "60px", width: `${W}px`, height: `${H}px`, "border-radius": "34px",
        background: "rgba(24,24,26,.82)", border: `1px solid ${C.line}`, "box-shadow": "0 30px 70px rgba(0,0,0,.5)",
        transform: `translateX(${tx().toFixed(2)}px) rotate(${(-4 + 3 * k()).toFixed(3)}deg) scale(${sc().toFixed(4)})`,
        display: "flex", "flex-direction": "column", "justify-content": "center", padding: "0 40px", "box-sizing": "border-box" }}>
        <div style={{ font: `600 34px ${FONT}`, color: C.grey, ...softStyle(soften(t(), 0.2)) }}>{p.title}</div>
        <div style={{ font: `900 76px ${FONT}`, color: C.ink, "letter-spacing": "-2px", ...softStyle(soften(t() - 0.05, 0.2)) }}>{p.stat}</div>
      </div>
    </html>
  );
}
