// KineticWord: one-word captions and sticker stamps.
// Port of the approved catalogue "Soften" / "Soften, per character" reveals
// (edge-video-factory mocks/motion-catalogue.html #1, #2). TYPE NEVER MOVES:
// each glyph resolves from blur+transparent to sharp in its final position
// (28 ms per-glyph offset), holds, then goes hard off. The only thing allowed to
// travel or overshoot is an OBJECT (the sticker's pill), never the type on it.
import { useTicker } from "@compound/jsx";
import { For, Index } from "solid-js";
import { C, FONT, soften, softStyle, backOut, clamp, cubicOut, snappyOut, inOut } from "./clock";

export type Word = { t0: number; t1: number; text: string };

type CapProps = {
  id?: string;
  words: Word[];
  x?: number; y?: number; width?: number; height?: number;
  size?: number; weight?: number; color?: string;
  /** "char" offsets each glyph by `stagger` s; "word" resolves the word as one unit */
  per?: "char" | "word";
  stagger?: number; inDur?: number; blur?: number;
  /** soft legibility shadow for type over footage (no scrim, no darkening) */
  overFace?: boolean;
  /** a soft dark plate behind each word (an object; the glyphs on it still only Soften) */
  plate?: boolean;
};

/** One-word captions. Mount once per caption track; words switch hard on their own t1. */
export function KineticWord(p: CapProps) {
  const { time } = useTicker();
  const W = p.width ?? 1000, H = p.height ?? 140, size = p.size ?? 84;
  const s = Math.min(...p.words.map((w) => w.t0)), e = Math.max(...p.words.map((w) => w.t1));
  const per = p.per ?? "char", st = p.stagger ?? 0.028, inD = p.inDur ?? 0.24, bl = p.blur ?? 13;
  const shadow = p.overFace ? "0 2px 8px rgba(0,0,0,.45), 0 0 30px rgba(0,0,0,.35)" : "none";
  return (
    <html x={p.x ?? 40} y={p.y ?? 1400} width={W} height={H} start={s} end={e} id={p.id ?? "kw"}>
      <div style={`position:relative;width:${W}px;height:${H}px;`}>
        <For each={p.words}>
          {(w) => {
            const chars = per === "char" ? [...w.text].map((c) => (c === " " ? "\u00A0" : c)) : [w.text];
            const live = () => time() >= w.t0 - 0.001 && time() < w.t1;
            return (
              <div
                style={{
                  position: "absolute", inset: "0", display: live() ? "flex" : "none",
                  "align-items": "center", "justify-content": "center",
                  font: `${p.weight ?? 700} ${size}px ${FONT}`, "letter-spacing": `${-size * 0.02}px`,
                  color: p.color ?? C.ink, "text-shadow": shadow, "white-space": "pre",
                }}
              >
                <div style={p.plate ? `display:flex;padding:${size * 0.06}px ${size * 0.22}px ${size * 0.1}px;border-radius:${size * 0.24}px;background:rgba(9,9,11,.58);box-shadow:0 24px 70px rgba(0,0,0,.4);` : "display:flex;"}>
                  <Index each={chars}>
                    {(ch, i) => (
                      <span style={{ display: "inline-block", ...softStyle(soften(time() - w.t0 - i * st, inD, Infinity, 0, bl)) }}>{ch()}</span>
                    )}
                  </Index>
                </div>
              </div>
            );
          }}
        </For>
      </div>
    </html>
  );
}

type StickerProps = {
  id?: string;
  s: number; e: number; text: string;
  x: number; y: number; width?: number; height?: number;
  rot?: number; size?: number;
  /** pill colours: style guide D5 is white #FFFFFF with #0A0A0A heavy type */
  fill?: string; ink?: string;
  /** pill shadow override (CSS box-shadow) for tight safe zones */
  shadow?: string;
};

/**
 * Sticker stamp (style guide D5). The pill is an object: it pops in with
 * overshoot, then holds. The word on it resolves in place (Soften), it does
 * not scale with the pill. Hard off at e.
 */
export function Sticker(p: StickerProps) {
  const { time } = useTicker();
  const W = p.width ?? 640, H = p.height ?? 190, size = p.size ?? 88;
  const box = W + 80, boxH = H + 120;
  // pill (object only): drops in and overshoots to exactly 103% scale, then settles to 100%
  const k = () => clamp((time() - p.s) / 0.4);
  const pop = () => clamp(k() / 0.6);
  const pillScale = () => (k() < 0.6 ? 0.6 + 0.43 * snappyOut(k() / 0.6) : 1.03 - 0.03 * inOut((k() - 0.6) / 0.4));
  const chars = [...p.text].map((c) => (c === " " ? "\u00A0" : c));
  return (
    <html x={p.x - 40} y={p.y - 40} width={box} height={boxH} start={p.s} end={p.e} id={p.id ?? "stk"}>
      <div style={`position:relative;width:${box}px;height:${boxH}px;`}>
        <div
          style={{
            position: "absolute", left: "40px", top: "40px", width: `${W}px`, height: `${H}px`,
            "border-radius": `${H * 0.22}px`, background: p.fill ?? "#FFFFFF",
            "box-shadow": p.shadow ?? "0 30px 60px rgba(0,0,0,.5), 0 8px 18px rgba(0,0,0,.3)",
            transform: `translateY(${((1 - snappyOut(pop())) * -60).toFixed(2)}px) rotate(${p.rot ?? -7}deg) scale(${pillScale().toFixed(4)})`,
            opacity: clamp(pop() * 3).toFixed(3),
          }}
        />
        <div
          style={{
            position: "absolute", left: "40px", top: "40px", width: `${W}px`, height: `${H}px`,
            display: "flex", "align-items": "center", "justify-content": "center",
            transform: `rotate(${p.rot ?? -7}deg)`,
            font: `900 ${size}px ${FONT}`, "letter-spacing": `${-size * 0.03}px`, color: p.ink ?? "#0A0A0A",
          }}
        >
          <Index each={chars}>
            {(ch, i) => <span style={{ display: "inline-block", ...softStyle(soften(time() - p.s - 0.1 - i * 0.022, 0.2, Infinity, 0, 9)) }}>{ch()}</span>}
          </Index>
        </div>
      </div>
    </html>
  );
}

export { cubicOut };
