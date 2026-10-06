// Framer (r12): one footage layer whose framing is a keyed, eased path. Each key is a
// framing box (where the full source frame sits, in frame px) plus a card amount m: 0 = full
// frame, 1 = the face card (rounded rect, radius grows with m). Between keys the box and the
// mask ease together, so punch-ins become pushes and full <-> split becomes a morph, never a swap.
// Keys are in SCENE seconds; the shader recovers scene time from the source playhead
// (scene t = start + (source t - sourceIn) / rate), so a freeze (rate 0.01) holds its framing.
import type { JSX } from "solid-js";

export type Rect = [number, number, number, number];
export type FKey = { t: number; box: Rect; m?: number; ease?: "io" | "eo" | "lin" | "sin" };

const WGSL = /* wgsl */ `
@group(1) @binding(0) var<uniform> ta: vec4f; // key times 0..3
@group(1) @binding(1) var<uniform> tb: vec4f; // key time 4, key count, radius, card amount of key 4
@group(1) @binding(2) var<uniform> ma: vec4f; // card amount of keys 0..3
@group(1) @binding(3) var<uniform> ea: vec4f; // easing into keys 1..4
@group(1) @binding(4) var<uniform> b0: vec4f;
@group(1) @binding(5) var<uniform> b1: vec4f;
@group(1) @binding(6) var<uniform> b2: vec4f;
@group(1) @binding(7) var<uniform> b3: vec4f;
@group(1) @binding(8) var<uniform> b4: vec4f;
@group(1) @binding(9) var<uniform> cfg: vec4f; // scene start, rate, sourceIn
@group(1) @binding(10) var<uniform> card: vec4f;

fn kt(i: i32) -> f32 { if (i < 4) { return ta[i]; } return tb.x; }
fn km(i: i32) -> f32 { if (i < 4) { return ma[i]; } return tb.w; }
fn ke(i: i32) -> f32 { return ea[clamp(i - 1, 0, 3)]; }
fn kb(i: i32) -> vec4f {
  if (i == 0) { return b0; } if (i == 1) { return b1; } if (i == 2) { return b2; }
  if (i == 3) { return b3; } return b4;
}
// 0: inOut cubic-bezier(0.7,0,0.3,1) (the kit push), 1: expoOut, 2: linear
fn bez(x: f32) -> f32 {
  let x1 = 0.7; let x2 = 0.3;
  let cx = 3.0 * x1; let bx = 3.0 * (x2 - x1) - cx; let ax = 1.0 - cx - bx;
  let by = 3.0; let ay = 1.0 - by;
  var t = x;
  for (var i = 0; i < 8; i++) {
    let sx = ((ax * t + bx) * t + cx) * t - x;
    let d = (3.0 * ax * t + 2.0 * bx) * t + cx;
    if (abs(d) < 1e-5) { break; }
    t = clamp(t - sx / d, 0.0, 1.0);
  }
  return (ay * t + by) * t * t;
}
fn ez(p: f32, e: f32) -> f32 {
  if (e > 2.5) { return 0.5 - 0.5 * cos(3.14159265 * p); }
  if (e > 1.5) { return p; }
  if (e > 0.5) { if (p >= 1.0) { return 1.0; } return 1.0 - pow(2.0, -10.0 * p); }
  return bez(p);
}
fn rr(p: vec2f, c: vec2f, h: vec2f, r: f32) -> f32 {
  let q = abs(p - c) - h + vec2f(r);
  return length(max(q, vec2f(0.0))) + min(max(q.x, q.y), 0.0) - r;
}

@fragment
fn main(@location(0) uv: vec2f) -> @location(0) vec4f {
  let t = cfg.x + (globals.time - cfg.z) / cfg.y;
  let n = i32(tb.y);
  var box = kb(0); var m = km(0);
  if (n > 1 && t > kt(0)) {
    box = kb(n - 1); m = km(n - 1);
    for (var i = 1; i < 5; i++) {
      if (i >= n) { break; }
      if (t <= kt(i)) {
        let p = clamp((t - kt(i - 1)) / max(1e-4, kt(i) - kt(i - 1)), 0.0, 1.0);
        let k = ez(p, ke(i));
        box = mix(kb(i - 1), kb(i), k);
        m = mix(km(i - 1), km(i), k);
        break;
      }
    }
  }
  let P = uv * globals.resolution;
  let R = mix(vec4f(0.0, 0.0, globals.resolution), card, m);
  let d = rr(P, R.xy + R.zw * 0.5, R.zw * 0.5, tb.z * m);
  let a = clamp(0.5 - d, 0.0, 1.0);
  if (a <= 0.0) { return vec4f(0.0); }
  let src = (P - box.xy) / box.zw;
  var c = vec4f(0.035, 0.035, 0.043, 1.0);
  if (src.x >= 0.0 && src.y >= 0.0 && src.x <= 1.0 && src.y <= 1.0) { c = sampleSource(src); }
  // cfg.w > 0: the whole layer fades out over 4 frames from scene time cfg.w (freeze dissolve)
  var o = 1.0;
  if (cfg.w > 0.0) { let q = clamp((t - cfg.w) / (4.0 / 30.0), 0.0, 1.0); o = 1.0 - (0.5 - 0.5 * cos(3.14159265 * q)); }
  return vec4f(c.rgb * a * o, a * o);
}
`;

const EZ = { io: 0, eo: 1, lin: 2, sin: 3 } as const;

type Props = {
  id: string; src: string; start: number; end: number; sourceIn: number; playbackRate: number;
  keys: FKey[]; fadeOut?: number; card: Rect; radius: number; children?: JSX.Element;
};

export function Framer(p: Props) {
  const ks = p.keys.slice(0, 5);
  const at = (i: number) => ks[Math.min(i, ks.length - 1)];
  const uniforms = {
    ta: [0, 1, 2, 3].map((i) => at(i).t), tb: [at(4).t, ks.length, p.radius, at(4).m ?? 0],
    ma: [0, 1, 2, 3].map((i) => at(i).m ?? 0), ea: [1, 2, 3, 4].map((i) => EZ[at(i).ease ?? "io"]),
    b0: at(0).box, b1: at(1).box, b2: at(2).box, b3: at(3).box, b4: at(4).box,
    cfg: [p.start, p.playbackRate, p.sourceIn, p.fadeOut ?? 0], card: p.card,
  };
  return (
    <video id={p.id} src={p.src} start={p.start} end={p.end} sourceIn={p.sourceIn} playbackRate={p.playbackRate} muted x={0} y={0} width={1080} height={1920} objectFit="fill">
      <shaderPaint wgsl={WGSL} uniforms={uniforms} id={`${p.id}sh`} />
      {p.children}
    </video>
  );
}
