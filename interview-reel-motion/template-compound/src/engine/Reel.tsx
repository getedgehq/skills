// Reel: builds a whole interview short from three data files.
//   reel.json      cut list (clips), framing boxes and keys, audio (voice, music, sfx), end fade, caption style
//   beats.json     time + phrase -> component + props (the beat map)
//   captions.json  phrase captions (2 to 5 words, one speaker each) with their y
// Layers, bottom to top: panels (on the scene ground), A-roll (Framer pieces), overlay beats, captions, end fade.
import { For } from "solid-js";
import type { Reel as ReelSpec, Beat, Caption, Clip } from "./types";
import { Framer, type FKey, type Rect } from "../kit/Framer";
import { renderBeat } from "./registry";
import { QA_MODE } from "./qa";
import { FPS, snap } from "./rules";

type Piece = { start: number; end: number; sin: number; rate: number; src: string; key: string };

/** cut every clip at the split times (so each piece needs at most 5 framing keys) and drop blank spans */
export function pieces(r: ReelSpec): Piece[] {
  const out: Piece[] = [];
  const inBlank = (t: number) => r.blank.some(([a, b]) => t >= a - 1e-6 && t < b - 1e-6);
  r.clips.forEach((c: Clip, ci) => {
    const cuts = [c.start, ...r.splits.filter((b) => b > c.start + 1e-6 && b < c.end - 1e-6), c.end].sort((a, b) => a - b);
    for (let i = 0; i < cuts.length - 1; i++) {
      const a = cuts[i], b = cuts[i + 1];
      if (inBlank(a)) continue;
      out.push({ start: a, end: b, sin: c.sin + (a - c.start) * c.rate, rate: c.rate, src: c.src ?? r.footage, key: `v${ci}_${i}` });
    }
  });
  return out;
}

/** the framing keys that cover a piece: the last key at or before its start through the first at or after its end */
export function keysFor(r: ReelSpec, p: Piece): FKey[] {
  const K = r.keys;
  let a = 0, b = K.length - 1;
  K.forEach((k, i) => { if (k[0] <= p.start + 1e-6) a = i; });
  for (let i = K.length - 1; i >= 0; i--) if (K[i][0] >= p.end - 1e-6) b = i;
  if (b < a) b = a;
  const box = (x: string | Rect): Rect => (typeof x === "string" ? r.framings[x] : x);
  const ks = K.slice(a, b + 1).map((k) => ({ t: k[0], box: box(k[1]), m: k[2], ease: k[3] ?? "io" }));
  if (ks.length > 5) throw new Error(`framing keys > 5 for ${p.key}: add a split (WGSL allows 5 keys per piece)`);
  return ks;
}

export function Reel(props: { reel: ReelSpec; beats: Beat[]; captions: Caption[] }) {
  const r = props.reel, END = r.scene.duration;
  const P = pieces(r);
  const panels = props.beats.filter((b) => b.layer === "panel");
  const overlay = props.beats.filter((b) => b.layer !== "panel");
  const cs = r.captionStyle;
  const fade = r.end.fadeFrames / FPS;
  return (
    <stage background={r.scene.stage ?? "#161616"} camera={[0.4, 0, 0, 0.4, 200, 40]} id="reelstage">
      <scene name={r.name} id={r.scene.id} width={r.scene.width} height={r.scene.height} fill={QA_MODE === "gfx" ? "#FF00FF" : r.scene.fill} active>
        {QA_MODE === "" ? (
          <sequence name="Panels" id="panels">
            <For each={panels}>{(b) => renderBeat(b, END)}</For>
          </sequence>
        ) : null}

        {QA_MODE !== "gfx" ? (
          <sequence name="A-roll" id="aroll">
            <For each={P}>
              {(p) => <Framer id={p.key} src={p.src} start={p.start} end={p.end} sourceIn={p.sin} playbackRate={p.rate} keys={keysFor(r, p)} card={[r.card.x, r.card.y, r.card.width, r.card.height]} radius={r.card.radius} />}
            </For>
          </sequence>
        ) : null}

        {QA_MODE !== "foot" ? (
          <sequence name="Overlay" id="overlay">
            <For each={overlay}>{(b) => renderBeat(b, END)}</For>
          </sequence>
        ) : null}

        <sequence name="Voice" id="voice">
          <For each={r.audio.voice}>
            {(v, i) => (
              <audio id={`vo${i()}`} src={v.src ?? r.footage} start={v.start} sourceIn={v.sin} sourceOut={v.sout} playbackRate={v.rate}>
                <keyframeTrack property="volume" id={`vo${i()}k`}>
                  <For each={v.gain ?? []}>{(g, j) => <keyframe time={g[0]} value={g[1]} id={`vo${i()}k${j()}`} />}</For>
                </keyframeTrack>
              </audio>
            )}
          </For>
        </sequence>

        {r.audio.music ? (
          <audio id="music" src={r.audio.music.src} start={0} end={END} playbackRate={r.audio.music.rate} volume={r.audio.music.volume}>
            <keyframeTrack property="volume" id="musick">
              <For each={r.audio.music.keys}>{(m, j) => <keyframe time={m[0]} value={m[1]} id={`musick${j()}`} />}</For>
            </keyframeTrack>
            <animation type="gain" phase="out" duration={r.audio.music.fadeOut ?? 0.7} id="musicfade" />
          </audio>
        ) : null}

        <sequence name="SFX" id="sfx">
          <For each={r.audio.sfx}>{(x, i) => <audio id={`sfx${i()}`} src={x[1]} start={x[0]} sourceIn={x[2]} sourceOut={x[3]} volume={x[4]} />}</For>
        </sequence>

        {QA_MODE !== "foot" ? (
          <sequence name="Captions" id="captions">
            <For each={props.captions}>
              {(c, i) => (
                <text id={`cap${i()}`} x={cs.x} y={c.y - cs.height / 2} width={cs.width} height={cs.height} start={c.t0} end={c.t1} fontFamily="Inter" fontWeight={cs.weight} fontSize={cs.size} letterSpacing={cs.tracking} textAlign="center" textBaseline="middle" color={cs.color}>
                  {c.text}
                  <shadow color="#000000" blur={cs.shadow.blur} offsetY={cs.shadow.offsetY} opacity={cs.shadow.opacity} id={`cap${i()}s`} />
                </text>
              )}
            </For>
          </sequence>
        ) : null}

        <rect id="endfade" x={0} y={0} width={r.scene.width} height={r.scene.height} fill="#000000" start={snap(END - fade)} end={END}>
          <keyframeTrack property="opacity" id="endfadek">
            <keyframe time={0} value={0} easing="easeInOut" id="endfade0" />
            <keyframe time={fade} value={1} id="endfade1" />
          </keyframeTrack>
        </rect>
      </scene>
    </stage>
  );
}
