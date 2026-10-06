// Beat component registry: beats.json names a component and its props; this maps the name to the kit.
// "own" components carry their own eased exit; every other component is wrapped in Out (EXIT_FRAMES by default).
import type { JSX } from "solid-js";
import type { Beat } from "./types";
import { EXIT_FRAMES, FPS } from "./rules";
import { Sticker, KineticWord } from "../kit/KineticWord";
import { ChatPrompt, BarChart, TileGrid } from "../kit/BuildPanel";
import { CounterBar } from "../kit/CounterBar";
import { ParticleText } from "../kit/ParticleText";
import { TypeRing } from "../kit/TypeRing";
import { OrbitCards, videoCard, phoneCard, statCard, imageCard } from "../kit/OrbitCards";
import { Cover, LowerThird, Headline, CompareCards, BlockMeter, EndCard, StickerStack, BrandChip, Arrow } from "../kit/Overlays";

/** group pinned to the scene clock whose opacity eases in over `din` frames and out over `d` frames */
export function Out(p: { id: string; s: number; e: number; end: number; din?: number; d?: number; children: JSX.Element }) {
  return (
    <group id={p.id} start={0} end={p.end}>
      {p.children}
      <keyframeTrack property="opacity" id={`${p.id}k`}>
        {p.din ? <keyframe time={p.s} value={0} easing="easeInOut" id={`${p.id}k0`} /> : null}
        <keyframe time={p.din ? p.s + p.din / FPS : p.s} value={1} id={`${p.id}k1`} />
        <keyframe time={p.e - (p.d ?? EXIT_FRAMES) / FPS} value={1} easing="easeInOut" id={`${p.id}k2`} />
        <keyframe time={p.e} value={0} id={`${p.id}k3`} />
      </keyframeTrack>
    </group>
  );
}

const cards = (list: any[]) => list.map((c) => (c.kind === "video" ? videoCard(c.title, c.sub) : c.kind === "phone" ? phoneCard(c.title, c.sub) : c.kind === "stat" ? statCard(c.title, c.sub) : imageCard(c.src)));

type R = (b: Beat, s: number, e: number) => JSX.Element;
const P = (b: Beat) => b.props ?? {};
/** components that ease themselves out */
export const OWN: Record<string, R> = {
  Cover: (b, s, e) => <Cover id={b.id} s={s} e={e} {...(P(b) as any)} />,
  LowerThird: (b, s, e) => <LowerThird id={b.id} s={s} e={e} {...(P(b) as any)} />,
  Headline: (b, s, e) => <Headline id={b.id} s={s} e={e} {...(P(b) as any)} />,
  CompareCards: (b, s, e) => <CompareCards id={b.id} s={s} e={e} {...(P(b) as any)} />,
  BlockMeter: (b, s, e) => <BlockMeter id={b.id} s={s} e={e} {...(P(b) as any)} />,
  EndCard: (b, s, e) => <EndCard id={b.id} s={s} e={e} {...(P(b) as any)} />,
  StickerStack: (b, s, e) => <StickerStack id={b.id} s={s} e={e} {...(P(b) as any)} />,
  BrandChip: (b, s, e) => <BrandChip id={b.id} s={s} e={e} {...(P(b) as any)} />,
  /** native text line (attribution, labels): no wrapper, it ends with the reel's fade */
  Text: (b, s, e) => {
    const p = P(b);
    return <text id={b.id} x={p.x} y={p.y} width={p.width} height={p.height ?? 70} start={s} end={e} fontFamily={p.font ?? "Inter"} fontWeight={p.weight ?? 700} fontSize={p.size ?? 44} letterSpacing={p.tracking ?? -0.6} textBaseline="middle" color={p.color ?? "#A0A0A5"}>{p.text}</text>;
  },
};
/** components wrapped in Out by the engine */
export const WRAPPED: Record<string, R> = {
  Sticker: (b, s, e) => <Sticker id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
  KineticWord: (b, s, e) => <KineticWord id={`${b.id}c`} {...(P(b) as any)} />,
  ChatPrompt: (b, s, e) => <ChatPrompt id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
  BarChart: (b, s, e) => <BarChart id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
  TileGrid: (b, s, e) => <TileGrid id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
  CounterBar: (b, s, e) => <CounterBar id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
  TypeRing: (b, s, e) => <TypeRing id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
  OrbitCards: (b, s, e) => { const p = P(b); return <OrbitCards id={`${b.id}c`} s={s} e={e} {...(p as any)} cards={cards(p.cards ?? [])} />; },
  Arrow: (b, s, e) => <Arrow id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
  /** a dark plate behind a figure */
  Plate: (b, s, e) => { const p = P(b); return <rect id={`${b.id}c`} x={p.x} y={p.y} width={p.width} height={p.height} cornerRadius={p.radius ?? 28} fill={p.fill ?? "rgba(9,9,11,0.93)"} start={s} end={e} />; },
  Image: (b, s, e) => { const p = P(b); return <image id={`${b.id}c`} src={p.src} x={p.x} y={p.y} width={p.width} height={p.height} cornerRadius={p.radius ?? 0} start={s} end={e} />; },
  /** the signature full-frame moment, once per reel: ground + ParticleText (wrap with fadeIn and exit of 6) */
  Takeover: (b, s, e) => {
    const p = P(b);
    return (
      <>
        <rect id={`${b.id}g`} x={0} y={0} width={1080} height={1920} fill={p.ground ?? "#09090B"} start={s} end={e} />
        <ParticleText id={`${b.id}c`} s={s} e={e} text={p.text} size={p.size ?? 180} y={p.y ?? 510} height={p.height ?? 900} resolve={p.resolve ?? 0.55} dissolve={p.dissolve ?? 0.12} {...(p.extra ?? {})} />
      </>
    );
  },
  ParticleText: (b, s, e) => <ParticleText id={`${b.id}c`} s={s} e={e} {...(P(b) as any)} />,
};

export function renderBeat(b: Beat, end: number): JSX.Element {
  const own = OWN[b.component];
  if (own) return own(b, b.t0, b.t1);
  const w = WRAPPED[b.component];
  if (!w) throw new Error(`unknown beat component ${b.component} (${b.id})`);
  return <Out id={b.id} s={b.t0} e={b.t1} end={end} din={b.fadeIn} d={b.exit}>{w(b, b.t0, b.t1)}</Out>;
}
