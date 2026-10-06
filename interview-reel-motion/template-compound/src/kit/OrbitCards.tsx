// OrbitCards: 3 to 5 dark cards orbiting in 3D perspective around a face region
// (style guide D1 "Proof Orbit"). Ported from an in-house card field
// (CSS perspective, translate3d per card, depth blur + depth dimming, a fast
// dolly through the lens as the exit) and remocn device-cluster's one-after-
// another arrivals (a new front card about every 0.5 s). Depth-of-field follows
// remocn camera-stage: blur = |z - focusZ| * blurPerPx, capped.
// Cards are OBJECTS, so they travel; the type printed on them never animates.
import { useTicker } from "@compound/jsx";
import { For, type JSX } from "solid-js";
import { C, FONT, clamp, expoOut, expoIn, snappyOut } from "./clock";

export type Card = { w: number; h: number; render: () => JSX.Element };

type Props = {
  id?: string;
  s: number; e: number;
  cards: Card[];
  /** orbit centre in scene px (usually just above the face) */
  cx: number; cy: number;
  /** orbit radii: rx across the frame, rz in depth */
  rx?: number; rz?: number;
  /** degrees the orbit plane is tilted toward camera (0 = edge on) */
  tilt?: number;
  /** radians per second */
  speed?: number;
  /** seconds between card arrivals */
  every?: number;
  persp?: number; focusZ?: number; blurPerPx?: number; maxBlur?: number;
  width?: number; height?: number;
  /** card size multiplier (CSS zoom on the card face, not a transform) */
  cardScale?: number;
  /**
   * Occlusion layering with a person matte: render the orbit twice, "back" (cards
   * behind the ring centre, z < 0) under a matted copy of the footage and "front" over it.
   */
  layer?: "all" | "back" | "front";
  /**
   * Face no-go zone, one row per 30 fps frame from `s`: [top, bottom, left, right, headL, headR].
   * A card whose projected box would enter it shrinks (and dims) until it clears, and is
   * hidden below 30% size. Back cards fully inside the head span are exempt: the matte hides them.
   */
  noGo?: number[][];
  /** arrival offset in px (positive = cards rise from below, negative = drop from above) */
  arriveDy?: number;
  /** exit by lifting out of frame instead of flying past the lens (keeps the face clear) */
  exitLift?: boolean;
};

export function OrbitCards(p: Props) {
  const { time } = useTicker();
  const W = p.width ?? 1080, H = p.height ?? 1920;
  const P = p.persp ?? 1400, rx = p.rx ?? 400, rz = p.rz ?? 420, tilt = ((p.tilt ?? 16) * Math.PI) / 180;
  const speed = p.speed ?? 0.85, every = p.every ?? 0.2, focusZ = p.focusZ ?? 260, bpp = p.blurPerPx ?? 0.016, maxBlur = p.maxBlur ?? 12;
  const n = p.cards.length, cs = p.cardScale ?? 1.5;
  const exitDur = 0.42;

  const pose = (i: number) => {
    const t = time() - p.s;
    // each card lands on its slot of the ring, then the whole ring turns
    const a = (i / n) * Math.PI * 2 + t * speed + 0.35;
    // slow yaw/tilt sway of the whole ring plane, so the orbit has parallax even mid-hold
    const tl = tilt + 0.05 * Math.sin(t * 0.8);
    let x = rx * Math.sin(a), z = rz * Math.cos(a), y = Math.cos(a) * rz * Math.sin(tl) + Math.sin(a) * rz * 0.06 * Math.sin(t * 0.6);
    // arrival: from deep behind and below, tilting in (device-cluster order)
    const k = clamp((t - i * every) / 0.7);
    const arr = expoOut(k);
    x = x * (0.55 + 0.45 * arr);
    y = y + (1 - arr) * (p.arriveDy ?? 260);
    z = z - (1 - arr) * 2200;
    const ry = Math.sin(a) * 24 + (1 - arr) * 50;
    const rxDeg = (1 - arr) * 24 + 16;
    // exit: the camera dollies forward through the field (in-house card field)
    const ex = expoIn(clamp((time() - (p.e - exitDur)) / exitDur));
    if (p.exitLift) y -= ex * 1300; else z += ex * 1700;
    const lay = p.layer ?? "all";
    let g = 1;
    if (p.noGo && p.noGo.length) {
      const row = p.noGo[Math.min(p.noGo.length - 1, Math.max(0, Math.round(t * 30)))];
      const [top, bot, left, right, hl, hr] = row;
      const c = p.cards[i], s = P / (P - z), hw = (c.w * cs) / 2 * 1.12, hh = (c.h * cs) / 2 * 1.12;
      const X0 = p.cx + (x - hw) * s, X1 = p.cx + (x + hw) * s, Y0 = p.cy + (y - hh) * s, Y1 = p.cy + (y + hh) * s;
      const hidden = z < 0 && X0 >= hl + 10 && X1 <= hr - 10;
      if (!hidden && X1 > left && X0 < right && Y1 > top && Y0 < bot) {
        // shrink about the card centre until its bottom edge clears the zone top
        const cyS = p.cy + y * s;
        g = cyS >= top ? 0 : clamp((top - cyS) / (hh * s));
      }
    }
    const seen = k > 0 && z < P - 80 && g >= 0.3 && (lay === "all" || (lay === "back" ? z < 0 : z >= 0));
    const blur = Math.min(maxBlur, Math.abs(z - focusZ) * bpp) + ex * 10;
    const dim = clamp(0.35 + 0.65 * ((z + rz) / (2 * rz)), 0.2, 1);
    return { x, y, z, ry, rxDeg, blur, dim: dim * (0.4 + 0.6 * g), seen, g, op: clamp(k * 4) };
  };

  return (
    <html x={0} y={0} width={W} height={H} start={p.s} end={p.e} id={p.id ?? "orbit"}>
      <div style={{ position: "absolute", inset: "0", perspective: `${P}px`, "perspective-origin": `${p.cx}px ${p.cy}px` }}>
        <For each={p.cards.map((c, i) => ({ c, i }))}>
          {({ c, i }) => {
            const q = () => pose(i);
            return (
              <div
                style={{
                  position: "absolute", left: `${p.cx - (c.w * cs) / 2}px`, top: `${p.cy - (c.h * cs) / 2}px`, width: `${c.w * cs}px`, height: `${c.h * cs}px`,
                  transform: `translate3d(${q().x.toFixed(1)}px, ${q().y.toFixed(1)}px, ${q().z.toFixed(1)}px) rotateY(${q().ry.toFixed(2)}deg) rotateX(${q().rxDeg.toFixed(2)}deg) scale(${q().g.toFixed(4)})`,
                  filter: `blur(${q().blur.toFixed(2)}px) brightness(${q().dim.toFixed(3)})`,
                  display: q().seen ? "block" : "none",
                  "z-index": String(Math.round(q().z + 5000)),
                }}
              >
                <div style={{ zoom: String(cs) }}>{c.render()}</div>
              </div>
            );
          }}
        </For>
      </div>
    </html>
  );
}

/* ---------- card faces: real stills in a monochrome frame ---------- */
const face = (w: number, h: number, r = 22) =>
  `width:${w}px;height:${h}px;border-radius:${r}px;background:linear-gradient(160deg,#34343A,#1C1C20);border:2px solid rgba(250,250,252,.32);box-shadow:0 30px 70px rgba(0,0,0,.55);position:relative;font-family:${FONT};`;

/** A video card: a real still (16:9 crop), play glyph, duration chip, title and views. */
export const videoCard = (title: string, views: string, img?: string): Card => ({
  w: 360, h: 260,
  render: () => (
    <div style={face(360, 260)}>
      {img ? (
        <img src={img} style="position:absolute;left:0;top:0;width:360px;height:196px;object-fit:cover;object-position:50% 30%;border-radius:20px 20px 0 0;" />
      ) : (
        <div style="position:absolute;left:0;top:0;width:360px;height:196px;border-radius:20px 20px 0 0;background:linear-gradient(135deg,#6A6A72,#26262B);" />
      )}
      <div style="position:absolute;left:158px;top:76px;width:0;height:0;border-left:30px solid rgba(250,250,252,.95);border-top:18px solid transparent;border-bottom:18px solid transparent;" />
      <div style="position:absolute;right:12px;top:162px;padding:3px 8px;border-radius:6px;background:rgba(0,0,0,.6);color:#FAFAFC;font:600 15px Inter;">0:42</div>
      <div style="position:absolute;left:16px;top:206px;color:#FAFAFC;font:700 19px Inter;letter-spacing:-0.3px;">{title}</div>
      <div style="position:absolute;left:16px;top:232px;color:#A0A0A5;font:500 15px Inter;">{views}</div>
    </div>
  ),
});

/** A phone card: a 9:16 short (real still, full bleed) with a views pill, the ref's card. */
export const phoneCard = (handle: string, stat: string, img?: string): Card => ({
  w: 210, h: 374,
  render: () => (
    <div style={face(210, 374, 30) + "background:#16161A;"}>
      {img ? (
        <img src={img} style="position:absolute;left:4px;top:4px;width:202px;height:366px;object-fit:cover;border-radius:26px;" />
      ) : (
        <div style="position:absolute;left:4px;top:4px;width:202px;height:366px;border-radius:26px;background:linear-gradient(160deg,#7A7A82,#2A2A30);" />
      )}
      <div style="position:absolute;left:14px;top:18px;color:#FAFAFC;font:700 17px Inter;text-shadow:0 1px 6px rgba(0,0,0,.6);">{handle}</div>
      <div style="position:absolute;left:14px;bottom:16px;padding:6px 12px;border-radius:999px;background:rgba(250,250,252,.94);color:#0A0A0A;font:800 17px Inter;">{"\u25B6 " + stat}</div>
    </div>
  ),
});

/** A stat card: big number, grey unit. */
export const statCard = (num: string, unit: string): Card => ({
  w: 300, h: 170,
  render: () => (
    <div style={face(300, 170)}>
      <div style="position:absolute;left:22px;top:22px;color:#FAFAFC;font:800 64px Inter;letter-spacing:-2px;line-height:1;">{num}</div>
      <div style="position:absolute;left:24px;top:106px;color:#A0A0A5;font:600 20px Inter;">{unit}</div>
    </div>
  ),
});

/** An image card from the asset library (any still). */
export const imageCard = (src: string, w = 320, h = 220): Card => ({
  w, h,
  render: () => (
    <div style={face(w, h)}>
      <img src={src} style={`width:${w}px;height:${h}px;object-fit:cover;border-radius:22px;`} />
    </div>
  ),
});

export { snappyOut };
