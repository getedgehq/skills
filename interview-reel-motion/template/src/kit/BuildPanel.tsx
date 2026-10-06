// BuildPanel: UI panels that build in pieces (style guide D4 Prompt Bar, D7 Counter + Unit
// over a filling grid, D8 Bar Race). Ports of in-house pieces:
//  - ChatPrompt  <- catalogue "Ask, activate, send" + "Send, working, done"
//                   (mocks/component-catalogue.html #1, #4) with remocn type-into-input's
//                   human (non-linear) keystroke rhythm and placeholder hand-off.
//  - BarChart    <- remocn animated-bar-chart (bars built one by one) under the
//                   catalogue rule "an object may move, a label may not".
//  - TileGrid    <- remocn grid-fill (skeleton cells first, then filled cell by cell).
// Rules: TYPE NEVER MOVES (labels resolve in place with Soften). NO COUNT-UPS (every
// figure lands as its final value; only bars, tiles and markers travel).
import { useTicker } from "@compound/jsx";
import { For, Index } from "solid-js";
import { C, FONT, clamp, soften, softStyle, snappyOut, expoOut, backOut, cubicOut, rng } from "./clock";

const panelIn = (t: number, s: number, fade = true) => {
  // the panel is an object: it rises 28px and settles (catalogue "Rows landing")
  const k = cubicOut(clamp((t - s) / 0.42));
  return { transform: `translateY(${((1 - k) * 28).toFixed(2)}px)`, ...(fade ? { opacity: k.toFixed(3) } : {}) };
  // fade=false where children Soften: a fractional ancestor opacity over blurred text blanks the html rasterizer
};

/** A panel is a physical object: it rises and settles from a stronger 3D tilt into a slight resting tilt. */
const PAD = 48;
const plate = (t: number, s: number, fade = true) => {
  const k = cubicOut(clamp((t - s) / 0.55));
  const rx = 7 + (1 - k) * 16, ry = -5 - (1 - k) * 8;
  return {
    transform: `perspective(1800px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg) translateY(${((1 - k) * 40).toFixed(2)}px)`,
    "transform-origin": "50% 70%",
    ...(fade ? { opacity: k.toFixed(3) } : {}),
  };
};
const backing = `position:absolute;left:0;top:0;right:0;bottom:0;border-radius:40px;background:linear-gradient(180deg,#141417,#0E0E10);border:2px solid rgba(250,250,252,.10);box-shadow:0 50px 110px rgba(0,0,0,.65), 0 10px 30px rgba(0,0,0,.4);`;

/* ------------------------------------------------------------------ ChatPrompt */
type ChatProps = {
  id?: string; s: number; e: number; text: string;
  x?: number; y?: number; width?: number;
  placeholder?: string; size?: number;
  /** characters per second (catalogue: 24) */
  cps?: number;
};

export function ChatPrompt(p: ChatProps) {
  const { time } = useTicker();
  const W = p.width ?? 864, size = p.size ?? 96, cps = p.cps ?? 24;
  const H = Math.round(size * 1.35 * 2 + 150);
  // type-into-input rhythm: per-key intervals jitter +-45% around 1/cps, deterministic
  const r = rng(7);
  const at: number[] = [];
  let acc = 0.55;
  for (const ch of p.text) { acc += (1 / cps) * (0.55 + r() * 0.9) * (ch === " " ? 1.6 : 1); at.push(acc); }
  const doneAt = acc;
  const pressAt = doneAt + 0.35, workEnd = pressAt + 0.75;
  const t = () => time() - p.s;
  const k = () => at.filter((a) => a <= t()).length;
  const focus = () => clamp((t() - 0.35) / 0.16);
  const armed = () => k() >= p.text.length;
  const press = () => (t() > pressAt && t() < pressAt + 0.14 ? 1 : 0);
  const state = () => (t() < pressAt ? 0 : t() < workEnd ? 1 : 2);
  const caretOn = () => focus() > 0.5 && state() === 0 && (k() > 0 && k() < p.text.length ? true : (time() * 1.6) % 1 < 0.5);
  const btn = 76;
  return (
    <html x={(p.x ?? 108) - PAD} y={(p.y ?? 300) - PAD} width={W + 2 * PAD} height={H + 2 * PAD} start={p.s} end={p.e} id={p.id ?? "chat"}>
      <div style={{ position: "absolute", left: `${PAD}px`, top: `${PAD}px`, width: `${W}px`, height: `${H}px`, ...plate(time(), p.s, false) }}>
        <div
          style={{
            position: "absolute", inset: "0", "border-radius": "34px", background: C.cell,
            border: `2px solid ${focus() > 0.4 ? "rgba(250,250,252,.42)" : "rgba(250,250,252,.10)"}`,
            "box-shadow": `0 0 0 ${(focus() * 6).toFixed(2)}px rgba(250,250,252,.06), 0 30px 70px rgba(0,0,0,.5)`,
          }}
        />
        <div style={`position:absolute;left:38px;top:34px;width:${W - 76}px;font:500 ${size}px/${size * 1.35}px ${FONT};letter-spacing:-0.5px;color:${C.ink};`}>
          <span style={{ color: C.grey, display: k() === 0 ? "inline" : "none" }}>{p.placeholder ?? "Ask for anything"}</span>
          <span>{p.text.slice(0, k())}</span>
          <span style={{ display: "inline-block", width: "3px", height: `${size * 1.05}px`, "vertical-align": "-6px", "margin-left": "2px", background: C.ink, visibility: caretOn() ? "visible" : "hidden" }} />
        </div>
        {/* send control: inert -> armed -> pressed -> working sweep -> drawn check. It never moves. */}
        <div
          style={{
            position: "absolute", right: "26px", bottom: "24px", width: `${btn}px`, height: `${btn}px`, "border-radius": "22px",
            background: armed() ? C.ink : "#2A2A2E", display: "flex", "align-items": "center", "justify-content": "center",
            transform: `scale(${press() ? 0.9 : 1 + (state() === 2 ? (1 - clamp((t() - workEnd) / 0.3)) * 0.08 : 0)})`,
          }}
        >
          <svg width="38" height="38" viewBox="0 0 24 24" style={{ display: state() === 0 ? "block" : "none" }}>
            <path d="M12 19V5M5.5 11.5 12 5l6.5 6.5" fill="none" stroke={armed() ? C.ground : "#6A6A70"} stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg width="40" height="40" viewBox="0 0 24 24" style={{ display: state() === 1 ? "block" : "none" }}>
            <circle cx="12" cy="12" r="8.5" fill="none" stroke="rgba(9,9,11,.25)" stroke-width="2.4" />
            <path d="M12 3.5a8.5 8.5 0 0 1 8.5 8.5" fill="none" stroke={C.ground} stroke-width="2.4" stroke-linecap="round" transform={`rotate(${((t() - pressAt) * 420).toFixed(1)} 12 12)`} />
          </svg>
          <svg width="40" height="40" viewBox="0 0 24 24" style={{ display: state() === 2 ? "block" : "none" }}>
            <path d="M6 12.5l4 4 8-8.5" fill="none" stroke={C.ground} stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="20" stroke-dashoffset={(20 * (1 - cubicOut(clamp((t() - workEnd) / 0.3)))).toFixed(2)} />
          </svg>
        </div>
      </div>
    </html>
  );
}

/* ------------------------------------------------------------------ BarChart */
type Bar = { label: string; value: number; display?: string };
type BarProps = {
  id?: string; s: number; e: number; bars: Bar[];
  x?: number; y?: number; width?: number; height?: number;
  /** seconds between bars */
  every?: number;
  /** the closing pill, e.g. "35x views" */
  pill?: string;
  title?: string; sub?: string;
};

export function BarChart(p: BarProps) {
  const { time } = useTicker();
  const W = p.width ?? 864, H = p.height ?? 760, every = p.every ?? 0.32;
  const max = Math.max(...p.bars.map((b) => b.value));
  const n = p.bars.length, gap = 28, bw = (W - gap * (n - 1)) / n;
  const top = p.title ? 170 : 40, base = H - 70, span = base - top - 60;
  const t = () => time() - p.s;
  // 9 frames at 30 fps; the hero (last) bar rises with back-out over 11 frames
  const grow = (i: number) => clamp((t() - 0.12 - i * every) / (i === n - 1 ? 11 / 30 : 0.3));
  const pillAt = 0.12 + n * every + 0.35;
  return (
    <html x={(p.x ?? 108) - PAD} y={(p.y ?? 200) - PAD} width={W + 2 * PAD} height={H + 2 * PAD} start={p.s} end={p.e} id={p.id ?? "bars"}>
      <div style={{ position: "absolute", inset: "0", ...plate(time(), p.s, false) }}>
      <div style={backing} />
      <div style={`position:absolute;left:${PAD}px;top:${PAD}px;width:${W}px;height:${H}px;`}>
        <div style={{ position: "absolute", left: "0", top: "0", font: `800 68px ${FONT}`, "letter-spacing": "-1.6px", color: C.ink, ...softStyle(soften(t(), 0.25)) }}>{p.title ?? ""}</div>
        <div style={{ position: "absolute", left: "0", top: "80px", font: `700 68px ${FONT}`, "letter-spacing": "-1.6px", color: C.grey, ...softStyle(soften(t() - 0.08, 0.25)) }}>{p.sub ?? ""}</div>
        <div style={`position:absolute;left:0;top:${base}px;width:${W}px;height:2px;background:rgba(250,250,252,.14);`} />
        <Index each={p.bars}>
          {(b, i) => {
            const h = (b().value / max) * span;
            const last = i === n - 1;
            const g = () => grow(i);
            const hmin = Math.max(h, 40); // small bars keep a visible minimum
            const hh = () => hmin * (last ? backOut(g()) : snappyOut(g()));
            return (
              <>
                <div style={{ position: "absolute", left: `${i * (bw + gap)}px`, top: `${(base - hh()).toFixed(1)}px`, width: `${bw}px`, height: `${Math.max(0, hh()).toFixed(1)}px`, "border-radius": "14px 14px 4px 4px", background: last ? C.ink : "#2C2C31" }} />
                {/* value lands as its final figure, in its final place, once the bar arrives */}
                <div style={{ position: "absolute", left: `${i * (bw + gap)}px`, width: `${bw}px`, top: `${(base - hmin - 74).toFixed(1)}px`, "text-align": "center", font: `800 54px ${FONT}`, "letter-spacing": "-1px", color: last ? C.ink : C.grey, ...softStyle(soften(t() - 0.12 - i * every - 0.24, 0.2)) }}>{b().display ?? String(b().value)}</div>
                <div style={{ position: "absolute", left: `${i * (bw + gap)}px`, width: `${bw}px`, top: `${base + 16}px`, "text-align": "center", font: `700 40px ${FONT}`, color: C.grey, ...softStyle(soften(t() - 0.12 - i * every, 0.22)) }}>{b().label}</div>
              </>
            );
          }}
        </Index>
        <div style={{ position: "absolute", right: "0", top: `${top - 10}px`, display: p.pill ? "block" : "none" }}>
          <div style={{ padding: "16px 30px", "border-radius": "999px", background: C.ink, transform: `scale(${(0.5 + 0.5 * backOut(clamp((t() - pillAt) / 0.3))).toFixed(4)})`, display: t() > pillAt ? "block" : "none", "transform-origin": "100% 50%" }}>
            <span style={{ font: `900 44px ${FONT}`, "letter-spacing": "-1px", color: C.ground, ...softStyle(soften(t() - pillAt - 0.08, 0.2)) }}>{p.pill ?? ""}</span>
          </div>
        </div>
      </div>
      </div>
    </html>
  );
}

/* ------------------------------------------------------------------ TileGrid */
type GridProps = {
  id?: string; s: number; e: number;
  cols?: number; rows?: number;
  /** how many cells end filled (default all) */
  fill?: number;
  /** headline counter: final value, never counted up */
  value?: string; unit?: string;
  x?: number; y?: number; width?: number;
  /** seconds for the whole fill sweep */
  sweep?: number;
};

export function TileGrid(p: GridProps) {
  const { time } = useTicker();
  const cols = p.cols ?? 10, rows = p.rows ?? 10, total = cols * rows, fill = p.fill ?? total;
  const W = p.width ?? 864, gap = 10, cell = (W - gap * (cols - 1)) / cols;
  const head = p.value ? 220 : 0;
  const H = head + rows * cell + (rows - 1) * gap;
  const sweep = p.sweep ?? 1.1;
  const t = () => time() - p.s;
  // skeletons arrive on a diagonal wave, then fill in reading order (grid-fill)
  const cells = Array.from({ length: total }, (_, i) => ({ i, c: i % cols, r: Math.floor(i / cols) }));
  return (
    <html x={(p.x ?? 108) - PAD} y={(p.y ?? 200) - PAD} width={W + 2 * PAD} height={H + 2 * PAD} start={p.s} end={p.e} id={p.id ?? "grid"}>
      <div style={{ position: "absolute", inset: "0", ...plate(time(), p.s, false) }}>
      <div style={backing} />
      <div style={`position:absolute;left:${PAD}px;top:${PAD}px;width:${W}px;height:${H}px;`}>
        <div style={{ position: "absolute", left: "0", top: "0", display: p.value ? "flex" : "none", "align-items": "baseline", gap: "22px" }}>
          <span style={{ font: `800 150px/1 ${FONT}`, "letter-spacing": "-5px", color: C.ink, ...softStyle(soften(t() - 0.15, 0.3)) }}>{p.value ?? ""}</span>
          <span style={{ font: `800 84px ${FONT}`, "letter-spacing": "-2px", color: C.grey, ...softStyle(soften(t() - 0.3, 0.3)) }}>{p.unit ?? ""}</span>
        </div>
        <For each={cells}>
          {(q) => {
            const skel = () => expoOut(clamp((t() - (q.c + q.r) * 0.018) / 0.35));
            const on = () => q.i < fill && t() > 0.35 + (q.i / total) * sweep;
            const pop = () => clamp((t() - 0.35 - (q.i / total) * sweep) / 0.18);
            return (
              <div
                style={{
                  position: "absolute", left: `${(q.c * (cell + gap)).toFixed(1)}px`, top: `${(head + q.r * (cell + gap) + (1 - skel()) * 18).toFixed(1)}px`,
                  width: `${cell.toFixed(1)}px`, height: `${cell.toFixed(1)}px`, "border-radius": "10px",
                  background: on() ? `rgba(250,250,252,${(0.25 + 0.75 * pop()).toFixed(3)})` : `rgba(26,26,26,${skel().toFixed(3)})`,
                }}
              />
            );
          }}
        </For>
      </div>
      </div>
    </html>
  );
}
