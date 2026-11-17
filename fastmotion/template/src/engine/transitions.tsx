import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {FPS} from './constants';
import {MotionBlur} from './motion';

// Engine-level scene transitions, declared per scene in timeline.ts.
//   whipL / whipR / whipU / whipD : fast pan with directional motion blur
//   blur  : defocus + fade          zoom : push through (scale up + blur)
//   fade  : plain opacity           (omitted) : scene handles its own edges
export type Tx = 'whipL' | 'whipR' | 'whipU' | 'whipD' | 'blur' | 'zoom' | 'fade';

const dirs: Record<string, [number, number]> = {whipL: [-1, 0], whipR: [1, 0], whipU: [0, -1], whipD: [0, 1]};

// p: 0 = fully on screen, 1 = fully gone. `out` flips which side it travels to.
const look = (tx: Tx, p: number, out: boolean) => {
  if (p <= 0) return {style: {}, bx: 0, by: 0};
  if (tx in dirs) {
    const [dx, dy] = dirs[tx];
    const sgn = out ? 1 : -1; // enter comes from the opposite side
    const d = Easing.in(Easing.cubic)(p);
    return {style: {transform: `translate(${dx * sgn * d * 1400}px, ${dy * sgn * d * 900}px)`, opacity: 1 - Math.max(0, p - 0.6) * 2.5}, bx: Math.abs(dx) * p * 60, by: Math.abs(dy) * p * 60};
  }
  if (tx === 'zoom') return {style: {transform: `scale(${out ? 1 + p * 1.5 : 1 - p * 0.3})`, opacity: 1 - p, filter: `blur(${p * 24}px)`}, bx: 0, by: 0};
  if (tx === 'blur') return {style: {opacity: 1 - p, filter: `blur(${p * 26}px)`, transform: `scale(${1 + (out ? 0.04 : -0.04) * p})`}, bx: 0, by: 0};
  return {style: {opacity: 1 - p}, bx: 0, by: 0};
};

export const Transition: React.FC<{dur: number; enter?: Tx; exit?: Tx; inSec?: number; outSec?: number; children: React.ReactNode}> = ({dur, enter, exit, inSec = 0.3, outSec = 0.3, children}) => {
  const f = useCurrentFrame();
  const sec = f / FPS;
  const pin = enter ? interpolate(sec, [0, inSec], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const pout = exit ? interpolate(sec, [dur - outSec, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const a = enter ? look(enter, pin, false) : look('fade', 0, false);
  const b = exit ? look(exit, pout, true) : look('fade', 0, true);
  return (
    <AbsoluteFill style={a.style}>
      <AbsoluteFill style={b.style}>
        <MotionBlur bx={a.bx + b.bx} by={a.by + b.by}>{children}</MotionBlur>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
