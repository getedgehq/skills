// Overlays: the interview-reel graphic layer, generalised from a shipped reel.
// Monochrome: #FAFAFC and #A0A0A5 type on #09090B, white stickers with #0A0A0A type. Brand logos are images.
// Every value is a pure function of the scene clock (useTicker().time()); all times are scene seconds.
// Each component here owns its exit: a group whose opacity eases out over the last EXIT frames.
import { useTicker } from "@compound/jsx";
import { For, type JSX } from "solid-js";
import { tw, inOut, backOut, expoOut, clamp } from "./motion";
import { EXIT_FRAMES, FPS } from "../engine/rules";

export const K = { bg: "#09090B", cell: "#18181A", line: "#2A2A2E", white: "#FAFAFC", grey: "#A0A0A5", ink: "#0A0A0A" };
const SANS = "Inter, -apple-system, 'Helvetica Neue', sans-serif";
const W = 1080, H = 1920;
export type Span = { s: number; e: number; id?: string };

const useT = () => useTicker().time;
export const abs = (x: number, y: number, extra: JSX.CSSProperties = {}): JSX.CSSProperties => ({ position: "absolute", left: `${x}px`, top: `${y}px`, ...extra });
/** objects pop with overshoot (0.88 -> 1.04 -> 1); type inside them never moves on its own */
export const pop = (t: number, t0: number, origin = "left center"): JSX.CSSProperties => ({
  opacity: t < t0 ? 0 : 1,
  transform: `scale(${t < t0 ? 0.88 : tw(t, t0, 0.24, 0.88, 1, backOut)})`,
  "transform-origin": origin,
});
/** digit groups keep a normal comma gap under tight tracking ("27,000", never "27/000") */
export function Num(p: { text: string }) {
  const parts = p.text.split(/(?<=\d),(?=\d)/);
  return <>{parts.map((s, i) => (i === 0 ? s : <><span style="letter-spacing:0;margin:0 0.06em 0 0.02em;">,</span>{s}</>))}</>;
}

/** full-frame html layer pinned to the scene clock, eased out over its last EXIT frames */
export function Frame(props: { s: number; e: number; ground?: boolean; id?: string; children?: JSX.Element }) {
  const id = props.id ?? "ovl";
  return (
    <group id={`${id}grp`} start={0} end={props.e}>
      <html x={0} y={0} width={W} height={H} start={props.s} end={props.e} id={`${id}frame`}>
        <div style={{ position: "relative", width: `${W}px`, height: `${H}px`, background: props.ground ? K.bg : "transparent", overflow: "hidden", "font-family": SANS, color: K.white }}>
          {props.children}
        </div>
      </html>
      <keyframeTrack property="opacity" id={`${id}xk`}>
        <keyframe time={props.e - EXIT_FRAMES / FPS} value={1} easing="easeInOut" id={`${id}xk0`} />
        <keyframe time={props.e} value={0} id={`${id}xk1`} />
      </keyframeTrack>
    </group>
  );
}

/** white pill, heavy black type, tilted, overshoot pop; with t1 it eases off over its last EXIT frames */
export function PopSticker(props: { t: () => number; t0: number; t1?: number; x: number; y: number; text: string; rot?: number; size?: number; lines?: string[]; rel?: boolean }) {
  const on = () => props.t() >= props.t0 && (props.t1 === undefined || props.t() < props.t1);
  const z = props.size ?? 72;
  const ex = () => (props.t1 === undefined ? 0 : inOut(clamp((props.t() - (props.t1 - EXIT_FRAMES / FPS)) / (EXIT_FRAMES / FPS))));
  return (
    <div
      style={{
        ...(props.rel ? { position: "relative" } : abs(props.x, props.y)),
        display: on() ? "block" : "none",
        opacity: 1 - ex(),
        background: "#FFFFFF",
        color: K.ink,
        "border-radius": `${Math.round(z * 0.3)}px`,
        padding: `${Math.round(z * 0.16)}px ${Math.round(z * 0.36)}px`,
        "font-size": `${z}px`,
        "line-height": "1.02",
        "font-weight": 800,
        "letter-spacing": `${-z * 0.02}px`,
        "white-space": "nowrap",
        "box-shadow": "0 14px 40px rgba(0,0,0,0.35)",
        transform: `rotate(${props.rot ?? -7}deg) scale(${(props.t() < props.t0 ? 0.6 : tw(props.t(), props.t0, 0.26, 0.6, 1, backOut)) * (1 - 0.12 * ex())})`,
        "transform-origin": "center",
      }}
    >
      {props.lines ? props.lines.map((l) => <div>{l}</div>) : props.text}
    </div>
  );
}

/** a timed run of pop stickers. center: each sticker is centred in the safe width (x 0..930) at its y */
export type StickerItem = { t0: number; t1?: number; text?: string; lines?: string[]; x?: number; y: number; rot?: number; size?: number; center?: boolean };
export function StickerStack(p: Span & { items: StickerItem[]; safeWidth?: number }) {
  const t = useT();
  return (
    <Frame s={p.s} e={p.e} id={p.id}>
      <For each={p.items}>
        {(d) =>
          d.center ? (
            <div style={abs(0, d.y, { width: `${p.safeWidth ?? 930}px`, display: "flex", "justify-content": "center" })}>
              <PopSticker t={t} t0={d.t0} t1={d.t1} x={0} y={0} text={d.text ?? (d.lines ?? [""])[0]} lines={d.lines && d.lines.length > 1 ? d.lines : undefined} rot={d.rot} size={d.size} rel />
            </div>
          ) : (
            <PopSticker t={t} t0={d.t0} t1={d.t1} x={d.x ?? 0} y={d.y} text={d.text ?? ""} lines={d.lines} rot={d.rot} size={d.size} />
          )
        }
      </For>
    </Frame>
  );
}

/** a logo + label chip. The logo is a native <image> layered on the html spacer (html cannot hold <img>) */
export type Chip = { logo?: string; label: string; x: number; y: number; logoSize: number; size: number; pad: string; gap: number; bg: string; border: string; radius: number; shadow?: string; logoRadius?: number };
function chipBox(c: Chip): JSX.CSSProperties {
  return { display: "flex", "align-items": "center", gap: `${c.gap}px`, background: c.bg, border: c.border, "border-radius": `${c.radius}px`, padding: c.pad, "white-space": "nowrap", ...(c.shadow ? { "box-shadow": c.shadow } : {}) };
}
function ChipHtml(c: Chip) {
  return (
    <div style={chipBox(c)}>
      <div style={`width:${c.logoSize}px;height:${c.logoSize}px;`} />
      <span style={{ "font-size": `${c.size}px`, "font-weight": 800, "letter-spacing": "-1px", color: K.white, "white-space": "nowrap" }}>{c.label}</span>
    </div>
  );
}
/** logo position: chip x/y + left padding + border (1 px) */
const logoXY = (c: Chip): [number, number] => {
  const padL = parseFloat(c.pad.split(" ").slice(-1)[0]), padT = parseFloat(c.pad.split(" ")[0]);
  return [c.x + padL, c.y + padT];
};
/** native logo layer that eases out with the chip */
function ChipLogo(p: Span & { c: Chip; id: string }) {
  if (!p.c.logo) return null;
  const [x, y] = logoXY(p.c);
  return (
    <group id={`${p.id}lg`} start={0} end={p.e}>
      <image id={`${p.id}lgi`} src={p.c.logo} x={x} y={y} width={p.c.logoSize} height={p.c.logoSize} cornerRadius={p.c.logoRadius ?? 10} start={p.s} end={p.e} />
      <keyframeTrack property="opacity" id={`${p.id}lgk`}>
        <keyframe time={p.s} value={1} id={`${p.id}lgk1`} />
        <keyframe time={p.e - EXIT_FRAMES / FPS} value={1} easing="easeInOut" id={`${p.id}lgk2`} />
        <keyframe time={p.e} value={0} id={`${p.id}lgk3`} />
      </keyframeTrack>
    </group>
  );
}
const COVER_CHIP = { logoSize: 64, size: 44, pad: "8px 22px 8px 8px", gap: 14, bg: "rgba(250,250,252,0.12)", border: "1px solid rgba(250,250,252,0.25)", radius: 20 };
const CARD_CHIP = { logoSize: 72, size: 50, pad: "10px 24px 10px 10px", gap: 16, bg: "rgba(9,9,11,0.9)", border: "1px solid #2A2A2E", radius: 20, shadow: "0 14px 40px rgba(0,0,0,0.35)" };

/** BrandChip: any logo + label, standalone */
export function BrandChip(p: Span & { logo?: string; label: string; x: number; y: number; variant?: "cover" | "card" }) {
  const c: Chip = { ...(p.variant === "card" ? CARD_CHIP : COVER_CHIP), logo: p.logo, label: p.label, x: p.x, y: p.y };
  const id = p.id ?? "chip";
  return (
    <>
      <Frame s={p.s} e={p.e} id={id}>
        <div style={abs(c.x, c.y)}>{ChipHtml(c)}</div>
      </Frame>
      <ChipLogo s={p.s} e={p.e} c={c} id={id} />
    </>
  );
}

/** Cover: frame 0 is the grid thumbnail. Soft scrim, brand chip, a hook of one or two lines, all inside the 3:4 crop */
export function Cover(p: Span & { chip?: { logo?: string; label: string }; lines: string[]; x?: number; y?: number; size?: number; size2?: number; scrimTop?: number; scrimHeight?: number }) {
  const id = p.id ?? "cover";
  const x = p.x ?? 56, y = p.y ?? 400, z1 = p.size ?? 110, z2 = p.size2 ?? 88;
  const c: Chip | null = p.chip ? { ...COVER_CHIP, logo: p.chip.logo, label: p.chip.label, x: 60, y: y - 110 } : null;
  return (
    <>
      <Frame s={p.s} e={p.e} id={id}>
        <div style={{ position: "absolute", left: "0", top: `${p.scrimTop ?? 222}px`, width: "928px", height: `${p.scrimHeight ?? 403}px`, background: "linear-gradient(180deg, rgba(9,9,11,0) 0%, rgba(9,9,11,0.85) 14%, rgba(9,9,11,0.82) 55%, rgba(9,9,11,0) 100%)", "-webkit-mask-image": "linear-gradient(90deg, #000 70%, transparent 100%)", "mask-image": "linear-gradient(90deg, #000 70%, transparent 100%)" }} />
        {c ? <div style={abs(c.x, c.y, chipBox(c))}><div style={`width:${c.logoSize}px;height:${c.logoSize}px;`} /><span style={{ "font-size": `${c.size}px`, "font-weight": 800, "letter-spacing": "-1px", color: K.white, "white-space": "nowrap" }}>{c.label}</span></div> : null}
        <div style={abs(x, y, { "font-size": `${z1}px`, "line-height": "1.02", "font-weight": 900, "letter-spacing": `${-z1 * 4.5 / 110}px`, color: K.white, "white-space": "nowrap", "text-shadow": "0 4px 24px rgba(0,0,0,.5)" })}>
          <div><Num text={p.lines[0]} /></div>
          {p.lines[1] ? <div style={{ "font-size": `${z2}px`, "margin-top": "14px", "letter-spacing": `${-z2 * 3.5 / 88}px` }}><Num text={p.lines[1]} /></div> : null}
        </div>
      </Frame>
      {c ? <ChipLogo s={p.s} e={p.e} c={{ ...c, x: c.x, y: c.y }} id={id} /> : null}
    </>
  );
}

/** LowerThird: name + role card that slides in, with an optional brand chip under its right edge */
export function LowerThird(p: Span & { name: string; role: string; x?: number; y?: number; chip?: { logo?: string; label: string; x: number; y: number } }) {
  const t = useT();
  const id = p.id ?? "lt";
  const x = () => tw(t(), p.s, 0.35, -80, 0, expoOut);
  const c: Chip | null = p.chip ? { ...CARD_CHIP, logo: p.chip.logo, label: p.chip.label, x: p.chip.x, y: p.chip.y } : null;
  return (
    <>
      <Frame s={p.s} e={p.e} id={id}>
        <div style={abs(p.x ?? 50, p.y ?? 240, { width: "740px", height: "230px", background: "rgba(9,9,11,0.9)", border: `1px solid ${K.line}`, "border-radius": "28px", transform: `translateX(${x()}px)` })}>
          <div style={abs(40, 22, { "font-size": "104px", "line-height": "1.05", "font-weight": 800, "letter-spacing": "-3px", color: K.white })}>{p.name}</div>
          <div style={abs(42, 146, { "font-size": "48px", "line-height": "1.1", "font-weight": 700, "letter-spacing": "-0.8px", color: K.grey, "white-space": "nowrap", ...pop(t(), p.s) })}>{p.role}</div>
        </div>
        {c ? <div style={abs(c.x, c.y, { display: t() >= p.s ? "block" : "none" })}>{ChipHtml(c)}</div> : null}
      </Frame>
      {c ? <ChipLogo s={p.s} e={p.e} c={{ ...c, x: c.x + 1, y: c.y + 1 }} id={id} /> : null}
    </>
  );
}

/** Headline: one resolved statement, one or more lines, popped as a block */
export function Headline(p: Span & { lines: string[]; x?: number; y?: number; size?: number; color?: string; tracking?: number }) {
  const t = useT();
  const z = p.size ?? 128;
  return (
    <Frame s={p.s} e={p.e} id={p.id}>
      <div style={abs(p.x ?? 60, p.y ?? 250, { "font-size": `${z}px`, "line-height": "1.02", "font-weight": 800, "letter-spacing": `${p.tracking ?? -5}px`, color: p.color ?? K.white, ...pop(t(), p.s) })}>
        <For each={p.lines}>{(l) => <div>{l}</div>}</For>
      </div>
    </Frame>
  );
}

/** CompareCards: "made for X" vs "nothing for Y". A filled profile card flies in, an empty dashed twin slides in */
export function CompareCards(p: Span & { title: string; sub: string; leftLabel: string; rightLabel: string; inAt: number; leftAt: number; rightAt: number; rightLabelAt: number; subAt: number; ground?: boolean }) {
  const t = useT();
  const fly = () => (t() < p.inAt ? 0 : tw(t(), p.inAt, 0.4, 0, 1, expoOut));
  const slide = () => (t() < p.rightAt ? 0 : tw(t(), p.rightAt, 0.35, 0, 1, expoOut));
  return (
    <Frame s={p.s} e={p.e} ground={p.ground ?? true} id={p.id}>
      <div style={abs(60, 240, { "font-size": "76px", "line-height": "1", "font-weight": 800, "letter-spacing": "-3px", color: K.white, ...pop(t(), p.inAt) })}>{p.title}</div>
      <div style={abs(62, 330, { "font-size": "50px", "line-height": "1.05", "font-weight": 700, "letter-spacing": "-1.5px", color: K.grey, ...pop(t(), p.subAt) })}>{p.sub}</div>
      <div style={abs(60, 440, { width: "400px", height: "480px", perspective: "1200px" })}>
        <div style={{ position: "absolute", inset: "0", background: K.cell, border: `2px solid ${K.line}`, "border-radius": "30px", opacity: t() < p.inAt ? 0 : 1, transform: `translateX(${(1 - fly()) * -260}px) rotateY(${(1 - fly()) * 40}deg) scale(${0.85 + 0.15 * fly()})` }}>
          <svg width="160" height="160" style={abs(120, 50)}>
            <circle cx="80" cy="80" r="78" fill="#2A2A2E" />
            <circle cx="80" cy="64" r="26" fill={K.grey} />
            <path d="M 34 132 Q 80 84 126 132" fill={K.grey} />
          </svg>
          <div style={abs(60, 250, { width: "280px", height: "26px", "border-radius": "13px", background: K.grey })} />
          <div style={abs(90, 296, { width: "220px", height: "20px", "border-radius": "10px", background: "#3A3A3E" })} />
          <div style={abs(50, 370, { background: "#FFFFFF", color: K.ink, "border-radius": "20px", padding: "8px 24px", "font-size": "50px", "font-weight": 800, "white-space": "nowrap", ...pop(t(), p.leftAt, "center") })}>{p.leftLabel}</div>
        </div>
      </div>
      <div style={abs(500, 440, { width: "400px", height: "480px", border: `4px dashed ${K.grey}`, "border-radius": "30px", "box-sizing": "border-box", opacity: t() < p.rightAt ? 0 : 1, transform: `translateX(${(1 - slide()) * 300}px)` })}>
        <div style={abs(0, 200, { width: "392px", "text-align": "center", "font-size": "56px", "font-weight": 800, "letter-spacing": "1px", color: K.white, ...pop(t(), p.rightLabelAt, "center") })}>{p.rightLabel}</div>
      </div>
    </Frame>
  );
}

/** BlockMeter: a headline over a row of day blocks; the first `dark` fill grey, the rest white, then a marker sweeps */
export function BlockMeter(p: Span & { title: string; n?: number; dark?: number; leftLabel: string; rightLabel: string; gridAt: number; titleAt: number; darkAt: number; leftLabelAt: number; lightAt: number; rightLabelAt: number; sweep: [number, number]; ground?: boolean }) {
  const t = useT();
  const N = p.n ?? 7, D = p.dark ?? 3, BW = 110, BG = 10, X = 70, Y = 450, BH = 250;
  const bx = (i: number) => X + i * (BW + BG);
  const at = (i: number) => (i < D ? p.darkAt + i * 0.05 : p.lightAt + (i - D) * 0.05);
  const filled = (i: number) => t() >= at(i);
  const mpos = () => (t() < p.sweep[0] ? -1 : tw(t(), p.sweep[0], p.sweep[1] - p.sweep[0], 0, N - 1, inOut));
  return (
    <Frame s={p.s} e={p.e} ground={p.ground ?? true} id={p.id}>
      <div style={abs(60, 240, { "font-size": "140px", "line-height": "1", "font-weight": 800, "letter-spacing": "-6px", color: K.white, ...pop(t(), p.titleAt) })}>{p.title}</div>
      <For each={Array.from({ length: N }, (_, i) => i)}>
        {(i) => {
          const st = () => {
            const f = filled(i);
            const bg = !f ? "transparent" : i < D ? "#2A2A2E" : K.white;
            const bd = !f ? K.line : i < D ? "#4A4A4F" : K.white;
            return abs(bx(i), Y, { width: `${BW}px`, height: `${BH}px`, "border-radius": "18px", background: bg, border: `4px solid ${bd}`, "box-sizing": "border-box", opacity: t() < p.gridAt ? 0 : 1, transform: `scale(${f ? tw(t(), at(i), 0.2, 1.08, 1, backOut) : 1})` });
          };
          return <div style={st()} />;
        }}
      </For>
      <div style={abs(bx(0) + Math.max(0, mpos()) * (BW + BG) + BW / 2 - 5, Y - 30, { width: "10px", height: `${BH + 60}px`, background: K.white, "border-radius": "5px", border: `3px solid ${K.bg}`, opacity: mpos() < 0 ? 0 : 1 })} />
      <div style={abs(bx(0), Y + BH + 24, { "font-size": "56px", "font-weight": 800, "letter-spacing": "-1px", color: K.grey, ...pop(t(), p.leftLabelAt) })}>{p.leftLabel}</div>
      <div style={abs(bx(D) + 30, Y + BH + 24, { "font-size": "56px", "font-weight": 800, "letter-spacing": "-1px", color: K.white, ...pop(t(), p.rightLabelAt) })}>{p.rightLabel}</div>
    </Frame>
  );
}

/** EndCard: the closing line on a dark card in the top band (pair with a native Text attribution line) */
export function EndCard(p: Span & { title: string; x?: number; y?: number; size?: number }) {
  const t = useT();
  return (
    <Frame s={p.s} e={p.e} id={p.id}>
      <div style={abs(p.x ?? 40, p.y ?? 250, { width: "880px", height: "250px", background: "rgba(9,9,11,0.92)", border: `1px solid ${K.line}`, "border-radius": "30px", ...pop(t(), p.s, "center top") })}>
        <div style={abs(40, 40, { "font-size": `${p.size ?? 84}px`, "line-height": "1", "font-weight": 800, "letter-spacing": "-3px", color: K.white, "white-space": "nowrap" })}>{p.title}</div>
      </div>
    </Frame>
  );
}

/** Arrow: a hand-drawn white arrow (object, may travel); drawn in a 170x90 box and scaled to width x height */
export function Arrow(p: Span & { x: number; y: number; width?: number; height?: number; flip?: boolean }) {
  const w = p.width ?? 170, h = p.height ?? 90;
  return (
    <html id={p.id ?? "arrow"} x={p.x} y={p.y} width={w} height={h} start={p.s} end={p.e}>
      <svg width={w} height={h} viewBox="0 0 170 90" style={`filter:drop-shadow(0 6px 14px rgba(0,0,0,.5));${p.flip ? "transform:scaleX(-1);" : ""}`}>
        <path d="M 12 50 Q 70 30 140 40" fill="none" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round" />
        <path d="M 118 18 L 146 40 L 116 62" fill="none" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </html>
  );
}
