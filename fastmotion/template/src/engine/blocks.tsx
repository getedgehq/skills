// Reusable, data-driven building blocks distilled from the launch video.
// Each block is a full-frame scene layer: give it content + timings (scene-local seconds),
// it handles layout, camera and motion using the shared engine (springs, Camera, blur).
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {FPS} from './constants';
import {C, shadowLg} from './theme';
import {countUp, glide, pop, range, s, typed} from './anim';
import {AgentRow, Bubble, Media, Pill, Stage, Tag, Title, UserBubble, Rich, plainLen} from './ui';
import {Camera, CamKey, Dust, MotionBlur} from './motion';

const sec = (f: number) => f / FPS;

// ---------------------------------------------------------------------------
// ChatThread: agent/user messages that type in sequence, with an optional camera.
//   messages: [{from: 'agent'|'user', text, at}]  (text supports **orange** + \n)
// ---------------------------------------------------------------------------
export type Msg = {from: 'agent' | 'user'; text: string; at: number; cps?: number};
export const ChatThread: React.FC<{messages: Msg[]; agentName?: string; userName?: string; userInitial?: string; size?: number; x?: number; y?: number; width?: number; camera?: CamKey[]; dust?: boolean}> = ({messages, agentName, userName, userInitial = 'U', size = 34, x = 420, y = 300, width = 1080, camera, dust}) => {
  const f = useCurrentFrame();
  const t = sec(f);
  // group consecutive agent messages under one avatar, like the original
  const groups: {from: Msg['from']; items: Msg[]}[] = [];
  messages.forEach((m) => {
    const g = groups[groups.length - 1];
    if (g && g.from === m.from && m.from === 'agent') g.items.push(m);
    else groups.push({from: m.from, items: [m]});
  });
  const body = (
    <div style={{position: 'absolute', left: x, top: y, width, display: 'flex', flexDirection: 'column', gap: size * 0.7}}>
      {groups.map((g, gi) =>
        t < g.items[0].at - 0.2 ? null : g.from === 'agent' ? (
          <AgentRow key={gi} size={size} name={gi === 0 ? agentName : undefined} initial={agentName ? agentName[0].toUpperCase() : ''}>
            {g.items.map((m, i) => (t >= m.at - 0.2 ? <Bubble key={i} text={m.text} start={m.at} cps={m.cps ?? 34} size={size} /> : null))}
          </AgentRow>
        ) : (
          <div key={gi} style={{alignSelf: 'flex-end'}}>
            <UserBubble text={g.items[0].text} start={g.items[0].at} size={size} name={userName} initial={userInitial} />
          </div>
        ),
      )}
    </div>
  );
  return (
    <Stage>
      {dust && <Dust swirl={0.6} cy={y + 200} />}
      {camera ? <Camera keys={camera}>{body}</Camera> : body}
    </Stage>
  );
};

// ---------------------------------------------------------------------------
// Carousel3D: cards on a curved strip; `steps` = [{at, focus}] moves focus with motion blur.
// ---------------------------------------------------------------------------
export type CarouselItem = {label?: string; sub?: string; caption?: string; src?: string | null; hue?: number; variant?: 'person' | 'scene' | 'product'};
export const Carousel3D: React.FC<{items: CarouselItem[]; steps: {at: number; focus: number}[]; cardW?: number; cardH?: number; gap?: number; cx?: number; cy?: number}> = ({items, steps, cardW = 470, cardH = 840, gap = 0.82, cx = 960, cy = 560}) => {
  const f = useCurrentFrame();
  const focusAt = (t: number) => {
    if (steps.length === 1) return steps[0].focus;
    return interpolate(t, steps.map((q) => q.at), steps.map((q) => q.focus), {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1)});
  };
  const fc = focusAt(sec(f));
  const vel = Math.abs(fc - focusAt(sec(f - 1))) * cardW * 0.5;
  const active = items[Math.round(fc)];
  return (
    <Stage>
      <MotionBlur bx={Math.min(40, vel)}>
        <AbsoluteFill style={{perspective: 1800}}>
          {items.map((it, i) => {
            const d = i - fc;
            const ad = Math.abs(d);
            if (ad > 3.2) return null;
            const sc = 1 - Math.min(1, ad) * 0.22;
            return (
              <div key={i} style={{position: 'absolute', left: cx + d * cardW * gap - (cardW * sc) / 2, top: cy - (cardH * sc) / 2, zIndex: 100 - Math.round(ad * 10), transform: `rotateY(${-d * 24}deg)`, transformOrigin: d < 0 ? 'right center' : 'left center', filter: ad > 0.6 ? `blur(${(ad - 0.6) * 3}px)` : undefined}}>
                <Media w={cardW * sc} h={cardH * sc} hue={it.hue ?? 25 + i * 40} seed={i} src={it.src} caption={it.caption} variant={it.variant} radius={22} />
              </div>
            );
          })}
        </AbsoluteFill>
      </MotionBlur>
      {active?.label && (
        <div style={{position: 'absolute', left: 0, right: 0, top: cy + cardH / 2 + 26, display: 'flex', justifyContent: 'center'}}>
          <Tag name={active.label} sub={active.sub} size={20} />
        </div>
      )}
    </Stage>
  );
};

// ---------------------------------------------------------------------------
// CardFan: a hero card spawns N cards that fan out (remixes, variants, creators).
// ---------------------------------------------------------------------------
export const CardFan: React.FC<{count?: number; at?: number; cardW?: number; cardH?: number; spread?: number; cx?: number; cy?: number; heroCaption?: string; hue?: number}> = ({count = 7, at = 0.4, cardW = 230, cardH = 400, spread = 175, cx = 960, cy = 600, heroCaption, hue = 25}) => {
  const f = useCurrentFrame();
  const open = glide(f, at, 0.55);
  const mid = (count - 1) / 2;
  return (
    <AbsoluteFill style={{perspective: 1600}}>
      {Array.from({length: count}, (_, i) => {
        const d = i - mid;
        const hero = Math.abs(d) < 0.01;
        const k = hero ? 1.25 : 1 - Math.abs(d) * 0.05;
        return (
          <div key={i} style={{position: 'absolute', left: cx + d * spread * open - (cardW * k) / 2, top: cy - (cardH * k) / 2 + Math.abs(d) * 10 * open, zIndex: hero ? 50 : 40 - Math.abs(d), transform: `rotateY(${-d * 9 * open}deg) rotateZ(${d * 1.5 * open}deg)`, opacity: hero ? 1 : open}}>
            <Media w={cardW * k} h={cardH * k} hue={hue + i * 23} seed={i + 3} caption={hero ? heroCaption : undefined} radius={18} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// StatBars: titled bar-pair chart (baseline grey vs result orange) that grows in.
// ---------------------------------------------------------------------------
export type Metric = {name: string; base: string; val: string; bh: number; vh: number; note?: string};
export const StatBars: React.FC<{metrics: Metric[]; at?: number; x?: number; y?: number; height?: number}> = ({metrics, at = 0.3, x = 900, y = 330, height = 380}) => {
  const f = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: x, top: y, display: 'flex', gap: 60, alignItems: 'flex-end', height}}>
      {metrics.map((m, i) => {
        const g = pop(f, at + i * 0.12, {damping: 18});
        return (
          <div key={m.name} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
            <div style={{display: 'flex', gap: 10, alignItems: 'flex-end', height: height - 70}}>
              {[{h: m.bh, v: m.base, c: 'linear-gradient(90deg,#E9E7E3,#D2CFCA)', fs: 16, col: C.mute}, {h: m.vh, v: m.val, c: `linear-gradient(90deg,#FF8A3D,${C.orange})`, fs: 34, col: C.ink}].map((b, j) => (
                <div key={j} style={{width: height * 0.15, height: (height - 110) * b.h * g, background: b.c, borderRadius: 6, position: 'relative', boxShadow: '6px 0 0 rgba(0,0,0,0.06)'}}>
                  <div style={{position: 'absolute', bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: 6, fontSize: b.fs, fontWeight: 700, color: b.col, opacity: g, whiteSpace: 'nowrap'}}>{b.v}</div>
                </div>
              ))}
            </div>
            <div style={{fontSize: height * 0.055, fontWeight: 600}}>{m.name}</div>
            {m.note && <div style={{fontSize: 14, color: C.green, marginTop: -8}}>{m.note}</div>}
          </div>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------
// TitleBeat: typed headline + optional subline, blur-in, used for section titles.
// ---------------------------------------------------------------------------
export const TitleBeat: React.FC<{text: string; sub?: string; at?: number; y?: number; size?: number; cps?: number}> = ({text, sub, at = 0, y = 130, size = 50, cps = 40}) => {
  const f = useCurrentFrame();
  const n = typed(f, text.replace(/\*\*/g, ''), at, cps);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, textAlign: 'center'}}>
      <Title size={size}><Rich text={text} n={n} /></Title>
      {sub && <div style={{fontSize: size * 0.45, color: C.ink2, marginTop: 8, opacity: range(f, at + plainLen(text) / cps, at + plainLen(text) / cps + 0.4)}}>{sub}</div>}
    </div>
  );
};

// ---------------------------------------------------------------------------
// CounterCard: big number that counts up (days running, views, revenue...).
// ---------------------------------------------------------------------------
export const CounterCard: React.FC<{from?: number; to: number; label: string; note?: string; at?: number; dur?: number; x?: number; y?: number; prefix?: string; suffix?: string}> = ({from = 0, to, label, note, at = 0.2, dur = 1.2, x = 1000, y = 340, prefix = '', suffix = ''}) => {
  const f = useCurrentFrame();
  const p = pop(f, at);
  return (
    <div style={{position: 'absolute', left: x, top: y, width: 460, padding: 34, borderRadius: 26, background: 'rgba(250,249,247,0.94)', boxShadow: shadowLg, opacity: p, transform: `translateY(${(1 - p) * 30}px)`}}>
      <div style={{fontSize: 120, fontWeight: 700, letterSpacing: '-0.05em', lineHeight: 1}}>{prefix}{countUp(f, from, to, at, dur).toLocaleString()}{suffix}</div>
      <div style={{fontSize: 22, color: C.mute, marginTop: 8}}>{label}</div>
      {note && <div style={{fontSize: 26, fontWeight: 500, marginTop: 22}}>{note}</div>}
    </div>
  );
};

export {Pill, Tag, s};
