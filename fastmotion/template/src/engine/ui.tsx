import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {C, font, mono, shadow, shadowLg} from './theme';
import {pop, typed} from './anim';

type Style = React.CSSProperties;

// Warm grey stage with soft orange glow, used by every UI scene.
export const Stage: React.FC<{children?: React.ReactNode; glow?: string; glow2?: string; glowX?: number; glowY?: number; glowScale?: number}> = ({children, glow = 'rgba(255,128,48,0.42)', glow2, glowX = 50, glowY = 55, glowScale = 1}) => (
  <AbsoluteFill style={{background: `radial-gradient(120% 90% at 50% 40%, ${C.bgHi}, ${C.bg})`, fontFamily: font, color: C.ink, overflow: 'hidden'}}>
    <div style={{position: 'absolute', left: `${glowX}%`, top: `${glowY}%`, width: 1300 * glowScale, height: 620 * glowScale, transform: 'translate(-50%,-50%)', background: `radial-gradient(closest-side, ${glow}, transparent)`, filter: 'blur(40px)'}} />
    {glow2 && <div style={{position: 'absolute', left: '22%', top: '35%', width: 800, height: 600, transform: 'translate(-50%,-50%)', background: `radial-gradient(closest-side, ${glow2}, transparent)`, filter: 'blur(50px)'}} />}
    {children}
    <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, pointerEvents: 'none', opacity: 0.07, mixBlendMode: 'multiply'}}>
      <filter id="stagegrain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4" /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="100%" height="100%" filter="url(#stagegrain)" />
    </svg>
  </AbsoluteFill>
);

export const Abs: React.FC<{x: number; y: number; children?: React.ReactNode; style?: Style; center?: boolean}> = ({x, y, children, style, center}) => (
  <div style={{position: 'absolute', left: x, top: y, transform: center ? 'translate(-50%,-50%)' : undefined, ...style}}>{children}</div>
);

export const Card: React.FC<{children?: React.ReactNode; style?: Style; lg?: boolean}> = ({children, style, lg}) => (
  <div style={{background: C.card, borderRadius: 22, boxShadow: lg ? shadowLg : shadow, border: '1px solid rgba(255,255,255,0.7)', ...style}}>{children}</div>
);

// Renders text where **word** becomes orange. Supports \n line breaks. `n` = chars visible.
export const Rich: React.FC<{text: string; n?: number; accent?: string}> = ({text, n, accent = C.orange}) => {
  const parts: {t: string; b: boolean}[] = [];
  text.split(/(\*\*[^*]+\*\*)/).forEach((p) => {
    if (!p) return;
    const b = p.startsWith('**');
    parts.push({t: b ? p.slice(2, -2) : p, b});
  });
  let left = n ?? Infinity;
  return (
    <>
      {parts.map((p, i) => {
        const shown = p.t.slice(0, Math.max(0, left));
        left -= p.t.length;
        return shown ? (
          <span key={i} style={p.b ? {color: accent, fontWeight: 600} : undefined}>
            {shown.split('\n').map((l, j) => (j ? [<br key={j} />, l] : l))}
          </span>
        ) : null;
      })}
    </>
  );
};
export const plainLen = (text: string) => text.replace(/\*\*/g, '').length;

// Glassy chat bubble. Types its text from `start` (sec, scene-local). Width grows with text.
// Glassy chat bubble. It opens at its final width (like the original) and the text types
// into it from `start` (sec, scene-local). `reserve={false}` shrink-wraps the typed text instead.
export const Bubble: React.FC<{text: string; start?: number; cps?: number; size?: number; style?: Style; typing?: boolean; minW?: number; reserve?: boolean}> = ({text, start = 0, cps = 34, size = 30, style, typing = true, minW = 0, reserve = true}) => {
  const f = useCurrentFrame();
  const n = typing ? typed(f, text.replace(/\*\*/g, ''), start, cps) : Infinity;
  const p = pop(f, start - 0.15);
  const pad = `${size * 0.5}px ${size * 0.75}px`;
  return (
    <div
      style={{
        position: 'relative', display: 'inline-block', padding: pad, borderRadius: size * 0.75, fontSize: size, fontWeight: 500, letterSpacing: '-0.02em', lineHeight: 1.25,
        background: 'linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(250,248,245,0.92) 55%, rgba(241,238,234,0.9) 100%)',
        boxShadow: `${shadow}, inset 0 1px 0 rgba(255,255,255,0.9), inset 0 -1px 0 rgba(0,0,0,0.04)`, border: '1px solid rgba(255,255,255,0.85)', whiteSpace: 'pre',
        minWidth: minW, minHeight: size * 2.25, opacity: p, transform: `translateY(${(1 - p) * 20}px) scale(${0.96 + 0.04 * p})`, transformOrigin: 'left center', ...style,
      }}
    >
      {reserve ? (
        <>
          <span style={{visibility: 'hidden'}}><Rich text={text} /></span>
          <span style={{position: 'absolute', left: 0, top: 0, padding: pad}}><Rich text={text} n={n} /></span>
        </>
      ) : (
        <Rich text={text} n={n} />
      )}
    </div>
  );
};

export const UserBubble: React.FC<{text: string; start?: number; size?: number; name?: string; initial?: string}> = ({text, start = 0, size = 30, name, initial = 'U'}) => {
  const f = useCurrentFrame();
  const p = pop(f, start);
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-end', opacity: Math.min(1, p * 1.5), transform: `scale(${0.7 + 0.3 * p})`, transformOrigin: 'right center'}}>
      {name && <div style={{fontSize: size * 0.45, color: C.mute, marginRight: size * 1.8, marginBottom: 4}}>{name}</div>}
      <div style={{display: 'flex', alignItems: 'center', gap: size * 0.35}}>
        <div style={{background: `linear-gradient(180deg, #FF8A3D, ${C.orange})`, color: '#fff', fontWeight: 600, fontSize: size, padding: `${size * 0.42}px ${size * 0.75}px`, borderRadius: 999, boxShadow: '0 16px 30px -12px rgba(255,106,26,0.7)', whiteSpace: 'nowrap'}}>{text}</div>
        <div style={{width: size * 1.1, height: size * 1.1, borderRadius: '50%', background: '#3A3937', color: '#fff', fontSize: size * 0.5, fontWeight: 600, display: 'grid', placeItems: 'center'}}>{initial}</div>
      </div>
    </div>
  );
};

// Agent row: avatar + optional name label above the bubbles.
export const AgentRow: React.FC<{children: React.ReactNode; size?: number; name?: string; initial?: string; style?: Style}> = ({children, size = 30, name, initial, style}) => (
  <div style={{display: 'flex', gap: size * 0.5, alignItems: 'flex-start', ...style}}>
    <AgentAvatar size={size * 1.5} initial={initial ?? (name ? name[0].toUpperCase() : '')} style={{marginTop: size * 0.45}} />
    <div style={{display: 'flex', flexDirection: 'column', gap: size * 0.45, alignItems: 'flex-start'}}>
      {name && <div style={{fontSize: size * 0.48, color: C.mute, marginLeft: 8, marginBottom: -size * 0.25}}>{name}</div>}
      {children}
    </div>
  </div>
);

export const Pill: React.FC<{children: React.ReactNode; style?: Style; dot?: string}> = ({children, style, dot}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: 10, background: 'rgba(255,255,255,0.95)', borderRadius: 999, padding: '10px 20px', fontSize: 22, fontWeight: 600, boxShadow: shadow, whiteSpace: 'nowrap', ...style}}>
    {dot && <span style={{width: 10, height: 10, borderRadius: '50%', background: dot}} />}
    {children}
  </div>
);

// "● Brand  Competitor ad" style caption.
export const Tag: React.FC<{name: string; sub?: string; size?: number; style?: Style; dot?: string}> = ({name, sub, size = 18, style, dot = C.orange}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: size * 0.45, fontSize: size, fontWeight: 600, color: C.ink, whiteSpace: 'nowrap', background: 'rgba(255,255,255,0.75)', padding: `${size * 0.25}px ${size * 0.6}px`, borderRadius: 999, ...style}}>
    <span style={{width: size * 0.45, height: size * 0.45, borderRadius: '50%', background: dot}} />
    {name}
    {sub && <span style={{color: C.mute, fontWeight: 400}}>{sub}</span>}
  </div>
);

// Media slot: shows a real image/video if `src` is given, otherwise a stylised placeholder
// (gradient + soft silhouette + optional caption) so the composition still reads.
// Media slot: shows a real image/video if `src` is given, otherwise a photo-like
// stand-in (room backdrop, generic person, key light, vignette, grain) with roughly the
// tonal weight of real footage, so layout and pacing read correctly before assets exist.
// variant: 'person' (default UGC framing) | 'scene' (no person) | 'product' (pack shot).
const rnd = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
export const Media: React.FC<{src?: string | null; w: number; h: number; hue?: number; radius?: number; caption?: string; style?: Style; seed?: number; dark?: boolean; variant?: 'person' | 'scene' | 'product'; children?: React.ReactNode}> = ({src, w, h, hue = 25, radius = 18, caption, style, seed = 0, dark, variant = 'person', children}) => {
  const isVid = src && /\.(mp4|webm|mov)$/i.test(src);
  const r = (k: number) => rnd(seed * 13 + k + hue * 0.37);
  // backdrop: wall + floor/desk band, lit from one side
  const wallL = dark ? 18 + r(1) * 10 : 46 + r(1) * 22;
  const wallH = hue + (r(2) - 0.5) * 30;
  const lightX = 20 + r(3) * 60;
  const skin = ['#E8C3A8', '#D7A584', '#B98563', '#8D5B3E', '#F0D2BC'][Math.floor(r(4) * 5)];
  const hair = ['#2A1D16', '#5A3A22', '#C9A06A', '#1A1412', '#8A5A35', '#E2C48E'][Math.floor(r(5) * 6)];
  const cloth = [`hsl(${hue},20%,22%)`, '#1E1F24', '#E9E6E1', `hsl(${hue + 180},25%,35%)`, '#6B6F78', '#2F3A2E'][Math.floor(r(6) * 6)];
  const px = 50 + (r(7) - 0.5) * 18; // subject x %
  const headW = 34 + r(8) * 8; // % of width
  const headTop = 22 + r(9) * 10; // % of height
  const portrait = h > w * 1.05;
  return (
    <div style={{width: w, height: h, borderRadius: radius, overflow: 'hidden', position: 'relative', boxShadow: shadowLg, flex: 'none', background: `hsl(${wallH},14%,${wallL}%)`, ...style}}>
      {src ? (
        isVid ? <OffthreadVideo src={staticFile(src)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} /> : <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      ) : (
        <div style={{position: 'absolute', inset: 0}}>
          {/* key light on the wall */}
          <div style={{position: 'absolute', inset: 0, background: `radial-gradient(70% 60% at ${lightX}% 28%, hsla(${wallH + 10},40%,${Math.min(92, wallL + 30)}%,0.75), transparent 70%)`}} />
          {/* window / shelf / doorway detail */}
          <div style={{position: 'absolute', left: `${r(10) * 60}%`, top: `${8 + r(11) * 14}%`, width: `${18 + r(12) * 22}%`, height: `${22 + r(13) * 20}%`, borderRadius: 4, background: r(14) > 0.5 ? `hsla(${wallH + 20},30%,${Math.min(95, wallL + 35)}%,0.55)` : `hsla(${wallH},15%,${wallL * 0.55}%,0.55)`, filter: 'blur(2px)'}} />
          {/* floor / desk band */}
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: `${portrait ? 26 : 32}%`, background: `linear-gradient(hsl(${wallH + 15},18%,${wallL * 0.62}%), hsl(${wallH + 15},18%,${wallL * 0.4}%))`}} />
          {variant === 'person' && (
            <>
              {/* torso */}
              <div style={{position: 'absolute', left: `${px}%`, bottom: '-4%', width: `${headW * 2.5}%`, height: `${100 - headTop - headW * (w / h) * 1.05}%`, transform: 'translateX(-50%)', borderRadius: '46% 46% 6% 6% / 30% 30% 4% 4%', background: `linear-gradient(100deg, ${cloth}, color-mix(in srgb, ${cloth} 70%, #000))`}} />
              {/* neck */}
              <div style={{position: 'absolute', left: `${px}%`, top: `${headTop + headW * (w / h) * 0.95}%`, width: `${headW * 0.42}%`, height: `${headW * (w / h) * 0.3}%`, transform: 'translateX(-50%)', background: `color-mix(in srgb, ${skin} 82%, #000)`}} />
              {/* hair back */}
              <div style={{position: 'absolute', left: `${px}%`, top: `${headTop - headW * (w / h) * 0.08}%`, width: `${headW * 1.18}%`, height: `${headW * (w / h) * (r(15) > 0.5 ? 1.75 : 1.05)}%`, transform: 'translateX(-50%)', borderRadius: '48% 48% 40% 40%', background: hair}} />
              {/* face */}
              <div style={{position: 'absolute', left: `${px}%`, top: `${headTop}%`, width: `${headW}%`, height: `${headW * (w / h) * 1.22}%`, transform: 'translateX(-50%)', borderRadius: '46% 46% 44% 44% / 40% 40% 58% 58%', background: `radial-gradient(80% 70% at ${lightX < 50 ? 35 : 65}% 35%, ${skin}, color-mix(in srgb, ${skin} 70%, #000))`}} />
              {/* fringe */}
              <div style={{position: 'absolute', left: `${px}%`, top: `${headTop - headW * (w / h) * 0.04}%`, width: `${headW * 1.02}%`, height: `${headW * (w / h) * 0.26}%`, transform: 'translateX(-50%)', borderRadius: '50% 50% 18% 40% / 80% 80% 20% 30%', background: `linear-gradient(${hair} 70%, transparent)`}} />
            </>
          )}
          {variant === 'product' && (
            <div style={{position: 'absolute', left: '50%', bottom: '18%', width: '42%', height: '52%', transform: 'translateX(-50%)', borderRadius: '10% 10% 6% 6%', background: `linear-gradient(90deg, hsl(${hue},45%,${dark ? 22 : 32}%), hsl(${hue},40%,${dark ? 34 : 48}%) 40%, hsl(${hue},45%,${dark ? 18 : 26}%))`, boxShadow: '0 20px 30px rgba(0,0,0,0.35)'}} />
          )}
          {/* vignette + grain */}
          <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(120% 90% at 50% 40%, transparent 55%, rgba(0,0,0,0.38))'}} />
          <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, opacity: 0.16, mixBlendMode: 'overlay'}}>
            <filter id={`grain${seed}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed={seed} /></filter>
            <rect width="100%" height="100%" filter={`url(#grain${seed})`} />
          </svg>
        </div>
      )}
      {caption && (
        <div style={{position: 'absolute', left: '8%', right: '8%', top: '52%', textAlign: 'center', color: '#fff', fontSize: Math.max(11, w * 0.06), fontWeight: 600, textShadow: '0 1px 3px rgba(0,0,0,0.6)'}}>{caption}</div>
      )}
      {children}
    </div>
  );
};

// Agent avatar: a glossy orange orb with the agent's initial.
export const AgentAvatar: React.FC<{size?: number; initial?: string; style?: React.CSSProperties}> = ({size = 60, initial = '', style}) => (
  <div style={{width: size, height: size, borderRadius: '50%', flex: 'none', position: 'relative', display: 'grid', placeItems: 'center',
    background: `radial-gradient(70% 70% at 32% 28%, #FFB27A, ${C.orange} 55%, #C9480A)`,
    boxShadow: `0 ${size * 0.12}px ${size * 0.22}px -${size * 0.06}px rgba(255,106,26,0.55), inset 0 ${size * 0.04}px ${size * 0.06}px rgba(255,255,255,0.55)`,
    color: '#fff', fontWeight: 700, fontSize: size * 0.44, ...style}}>
    <div style={{position: 'absolute', left: '18%', top: '12%', width: '38%', height: '22%', borderRadius: '50%', background: 'rgba(255,255,255,0.45)', filter: `blur(${size * 0.03}px)`, transform: 'rotate(-24deg)'}} />
    <span style={{position: 'relative'}}>{initial}</span>
  </div>
);

export const Cursor: React.FC<{x: number; y: number; scale?: number}> = ({x, y, scale = 1}) => (
  <svg width={40 * scale} height={52 * scale} viewBox="0 0 40 52" style={{position: 'absolute', left: x, top: y, filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.35))'}}>
    <path d="M3 2 L3 42 L13 33 L20 49 L27 46 L20 30 L34 30Z" fill="#111" stroke="#fff" strokeWidth="3" strokeLinejoin="round" />
  </svg>
);

// Instagram-style phone mock with a profile grid.
export const Phone: React.FC<{w?: number; name?: string; posts?: string; followers?: string; following?: string; bio?: string[]; hue?: number; style?: Style}> = ({w = 240, name = 'your.brand', posts = '3', followers = '12.4K', following = '318', bio = [], hue = 25, style}) => {
  const k = w / 240;
  return (
    <div style={{width: w, height: w * 2.05, borderRadius: 38 * k, border: `${5 * k}px solid #2B2A29`, background: '#fff', boxShadow: shadowLg, overflow: 'hidden', position: 'relative', fontSize: 9 * k, color: '#111', ...style}}>
      <div style={{display: 'flex', justifyContent: 'space-between', padding: `${12 * k}px ${16 * k}px 0`, fontWeight: 600, fontSize: 9 * k}}><span>9:41</span><span>▮▮ ◔</span></div>
      <div style={{padding: `${8 * k}px ${12 * k}px`, fontWeight: 700, fontSize: 11 * k}}>{name} ⌄</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 12 * k, padding: `0 ${12 * k}px`}}>
        <div style={{width: 46 * k, height: 46 * k, borderRadius: '50%', background: `linear-gradient(135deg,hsl(${hue},55%,80%),hsl(${hue},40%,55%))`}} />
        {[[posts, 'posts'], [followers, 'followers'], [following, 'following']].map(([a, b]) => (
          <div key={b} style={{textAlign: 'center', fontSize: 8 * k}}><b style={{fontSize: 11 * k}}>{a}</b><br />{b}</div>
        ))}
      </div>
      <div style={{padding: `${6 * k}px ${12 * k}px`, lineHeight: 1.35}}>{bio.map((b) => <div key={b}>{b}</div>)}</div>
      <div style={{display: 'flex', gap: 5 * k, padding: `0 ${12 * k}px`}}>
        {['Edit profile', 'Share profile'].map((t) => <div key={t} style={{flex: 1, background: '#EFEFEF', borderRadius: 6 * k, textAlign: 'center', padding: 4 * k, fontWeight: 600}}>{t}</div>)}
      </div>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 2 * k, marginTop: 30 * k}}>
        {[0, 1, 2].map((i) => <div key={i} style={{aspectRatio: '3/4', background: `linear-gradient(160deg,hsl(${hue + i * 40},35%,78%),hsl(${hue + i * 40},25%,45%))`}} />)}
      </div>
      <div style={{position: 'absolute', bottom: 10 * k, left: 0, right: 0, display: 'flex', justifyContent: 'space-around', fontSize: 13 * k, color: '#333'}}>⌂ ⌕ ⊕ ▷ ●</div>
    </div>
  );
};

export const Title: React.FC<{children: React.ReactNode; size?: number; style?: Style}> = ({children, size = 44, style}) => (
  <div style={{fontSize: size, fontWeight: 600, letterSpacing: '-0.025em', textAlign: 'center', whiteSpace: 'nowrap', ...style}}>{children}</div>
);

export const Mono: React.FC<{children: React.ReactNode; style?: Style}> = ({children, style}) => <span style={{fontFamily: mono, ...style}}>{children}</span>;
