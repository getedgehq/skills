import React, {useId} from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {FPS} from './constants';

// ---------------------------------------------------------------------------
// Directional motion blur. Chrome supports SVG filters on HTML, and an
// anisotropic feGaussianBlur ("x y") gives a real streak in the direction of travel.
// ---------------------------------------------------------------------------
export const MotionBlur: React.FC<{bx: number; by?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({bx, by = 0, children, style}) => {
  const id = useId().replace(/:/g, '');
  const ax = Math.abs(bx), ay = Math.abs(by);
  if (ax < 0.3 && ay < 0.3) return <AbsoluteFill style={style}>{children}</AbsoluteFill>;
  return (
    <AbsoluteFill style={style}>
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <filter id={`mb${id}`} x="-20%" y="-20%" width="140%" height="140%" colorInterpolationFilters="sRGB">
          <feGaussianBlur stdDeviation={`${ax} ${ay}`} />
        </filter>
      </svg>
      <AbsoluteFill style={{filter: `url(#mb${id})`}}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Camera: keyframed pan / zoom / tilt over scene-local seconds. Velocity drives
// motion blur automatically, which is what makes whips and push-ins feel filmed.
// ---------------------------------------------------------------------------
export type CamKey = {t: number; x?: number; y?: number; z?: number; rx?: number; ry?: number; rz?: number; blur?: number};
const ease = Easing.bezier(0.65, 0, 0.35, 1);

const sample = (keys: CamKey[], sec: number) => {
  const prop = (k: keyof CamKey, def: number) => {
    const ks = keys.filter((q) => q[k] !== undefined);
    if (ks.length === 0) return def;
    if (ks.length === 1) return ks[0][k] as number;
    return interpolate(sec, ks.map((q) => q.t), ks.map((q) => q[k] as number), {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  };
  return {x: prop('x', 0), y: prop('y', 0), z: prop('z', 1), rx: prop('rx', 0), ry: prop('ry', 0), rz: prop('rz', 0), blur: prop('blur', 0)};
};

export const useCamera = (keys: CamKey[]) => {
  const f = useCurrentFrame();
  const now = sample(keys, f / FPS);
  const prev = sample(keys, (f - 1) / FPS);
  // px per frame → blur strength (shutter ≈ 180°)
  const vx = (now.x - prev.x) * 0.5, vy = (now.y - prev.y) * 0.5;
  const vz = Math.abs(now.z - prev.z) * 400;
  return {...now, vx, vy, vz};
};

export const Camera: React.FC<{keys: CamKey[]; origin?: string; perspective?: number; children: React.ReactNode; maxBlur?: number}> = ({keys, origin = '50% 50%', perspective = 1600, children, maxBlur = 40}) => {
  const c = useCamera(keys);
  const bx = Math.min(maxBlur, Math.abs(c.vx) + c.vz * 0.3);
  const by = Math.min(maxBlur, Math.abs(c.vy) + c.vz * 0.3);
  return (
    <AbsoluteFill style={{perspective, overflow: 'hidden'}}>
      <MotionBlur bx={bx} by={by}>
        <AbsoluteFill style={{transformOrigin: origin, transform: `translate(${-c.x}px, ${-c.y}px) scale(${c.z}) rotateX(${c.rx}deg) rotateY(${c.ry}deg) rotateZ(${c.rz}deg)`, transformStyle: 'preserve-3d', filter: c.blur ? `blur(${c.blur}px)` : undefined}}>
          {children}
        </AbsoluteFill>
      </MotionBlur>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Depth of field: wrap a layer with its depth; blur grows with distance from focus.
// ---------------------------------------------------------------------------
export const Depth: React.FC<{z: number; focus?: number; k?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({z, focus = 0, k = 9, children, style}) => {
  const b = Math.abs(z - focus) * k;
  return <div style={{filter: b > 0.2 ? `blur(${b}px)` : undefined, ...style}}>{children}</div>;
};

// ---------------------------------------------------------------------------
// Dust: soft orange particles drifting / swirling (used behind chat + transitions).
// ---------------------------------------------------------------------------
export const Dust: React.FC<{count?: number; color?: string; swirl?: number; cx?: number; cy?: number; radius?: number; opacity?: number; seed?: number}> = ({count = 90, color = '255,120,50', swirl = 0, cx = 960, cy = 540, radius = 520, opacity = 1, seed = 1}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity}}>
      {Array.from({length: count}, (_, i) => {
        const r0 = ((i * 9301 + seed * 49297) % 233280) / 233280;
        const r1 = ((i * 4933 + seed * 1777) % 1000) / 1000;
        const a = r0 * Math.PI * 2 + (f / FPS) * (0.15 + swirl * (1.2 - r1));
        const rad = radius * (0.25 + r1 * 0.85) * (1 - swirl * 0.25);
        const x = cx + Math.cos(a) * rad * 1.6;
        const y = cy + Math.sin(a) * rad * 0.7 + Math.sin(f / 40 + i) * 6;
        const sz = 1.5 + r1 * 3;
        const len = 1 + swirl * 10 * r1;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: sz * len, height: sz, borderRadius: sz, background: `rgba(${color},${0.25 + r0 * 0.45})`, transform: `rotate(${(a * 180) / Math.PI + 90}deg)`}} />;
      })}
    </AbsoluteFill>
  );
};
