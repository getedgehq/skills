import {interpolate, spring, Easing} from 'remotion';
import {FPS} from './constants';

export const s = (sec: number) => Math.round(sec * FPS);

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Soft, slightly-overshooting spring used for every pop-in in the video.
export const pop = (frame: number, delaySec = 0, cfg: {damping?: number; stiffness?: number; mass?: number} = {}) =>
  spring({frame: frame - s(delaySec), fps: FPS, config: {damping: 16, stiffness: 140, mass: 0.9, ...cfg}});

// Critically damped (no overshoot) — for camera moves and big layout shifts.
export const glide = (frame: number, delaySec = 0, durSec = 0.9) =>
  interpolate(frame, [s(delaySec), s(delaySec + durSec)], [0, 1], {...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1)});

export const lerp = (t: number, a: number, b: number) => a + (b - a) * t;

export const range = (frame: number, fromSec: number, toSec: number, a = 0, b = 1, ease = Easing.inOut(Easing.cubic)) =>
  interpolate(frame, [s(fromSec), s(toSec)], [a, b], {...clamp, easing: ease});

// Fade in at the start and out at the end of a scene of length `durSec`.
export const fadeEdges = (frame: number, durSec: number, inSec = 0.35, outSec = 0.35) =>
  Math.min(range(frame, 0, inSec, 0, 1), range(frame, durSec - outSec, durSec, 1, 0));

// Number of characters to show for a typewriter effect.
export const typed = (frame: number, text: string, startSec: number, cps = 32) =>
  Math.max(0, Math.min(text.length, Math.floor(((frame - s(startSec)) / FPS) * cps)));

export const countUp = (frame: number, from: number, to: number, startSec: number, durSec: number) =>
  Math.round(interpolate(frame, [s(startSec), s(startSec + durSec)], [from, to], {...clamp, easing: Easing.out(Easing.cubic)}));

// Blur + fade "whoosh" used between beats.
export const blurIn = (frame: number, delaySec = 0, durSec = 0.5, maxBlur = 24) => {
  const t = glide(frame, delaySec, durSec);
  return {opacity: t, filter: `blur(${(1 - t) * maxBlur}px)`};
};
export const blurOut = (frame: number, atSec: number, durSec = 0.4, maxBlur = 24) => {
  const t = range(frame, atSec, atSec + durSec, 0, 1, Easing.in(Easing.cubic));
  return {opacity: 1 - t, filter: `blur(${t * maxBlur}px)`};
};
