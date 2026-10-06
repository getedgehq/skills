import type { Rect } from "../kit/Framer";
export type Ease = "io" | "eo" | "lin" | "sin";
/** one picture piece of the cut list, in output (scene) seconds. rate 0.01 = a held frame */
export type Clip = { start: number; end: number; sin: number; rate: number; src?: string; note?: string };
export type Key = [number, string | Rect, number, Ease?];
export type Voice = { start: number; sin: number; sout: number; rate: number; src?: string; gain?: [number, number][] };
export type Sfx = [number, string, number, number, number];
export type Reel = {
  name: string;
  scene: { id: string; width: number; height: number; fill: string; duration: number; stage?: string };
  footage: string;
  card: { x: number; y: number; width: number; height: number; radius: number };
  clips: Clip[];
  splits: number[];
  blank: [number, number][];
  framings: Record<string, Rect>;
  keys: Key[];
  audio: {
    voice: Voice[];
    music?: { src: string; rate: number; volume: number; keys: [number, number][]; fadeOut?: number };
    sfx: Sfx[];
  };
  end: { fadeFrames: number };
  captionStyle: { x: number; width: number; height: number; size: number; weight: number; color: string; tracking: number; shadow: { blur: number; offsetY: number; opacity: number } };
};
export type Beat = {
  id: string; t0: number; t1: number; component: string;
  layer?: "overlay" | "panel";
  phrase?: string; meaning?: string;
  /** eased exit frames (6 to 8) and optional fade-in frames, for components wrapped by the engine */
  exit?: number; fadeIn?: number;
  props?: Record<string, any>;
};
export type Caption = { t0: number; t1: number; text: string; y: number; speaker?: string };
