// CounterBar: a figure plus a progress bar crossing a goal tick.
// Port of remocn stat-payoff / number-wheel layout and the catalogue "Fill and
// read out" meter, under the NO COUNT-UPS rule: the number lands as its
// FINAL value (Soften, per glyph, tabular figures, in place) and only the bar
// and the goal marker move. When the bar crosses the goal tick, the tick and its
// label flip state (grey to ink); the marker pops as an object.
import { useTicker } from "@compound/jsx";
import { C, FONT, clamp, soften, softStyle, inOut } from "./clock";

type Props = {
  id?: string; s: number; e: number;
  value: string; unit?: string;
  /** bar end position and goal position, 0..1 of the track */
  progress: number; goal: number;
  goalLabel?: string;
  x?: number; y?: number; width?: number;
  /** seconds the bar takes to travel */
  travel?: number;
  /** layout scale (type, bar and label); 1 = original */
  k?: number;
};

export function CounterBar(p: Props) {
  const { time } = useTicker();
  const W = p.width ?? 940, travel = p.travel ?? 1.15, k = p.k ?? 1, barY = Math.round(240 * k), barH = Math.round(80 * k);
  const t = () => time() - p.s;
  const fill = () => p.progress * inOut(clamp((t() - 0.35) / travel));
  // the moment the fill passes the goal (solve inOut by sampling: deterministic, cheap)
  let crossT = Infinity;
  for (let i = 0; i <= 300; i++) {
    const tt = 0.35 + (i / 300) * travel;
    if (p.progress * inOut(clamp((tt - 0.35) / travel)) >= p.goal) { crossT = tt; break; }
  }
  const hit = () => t() >= crossT;
  // flash decays over ~0.6 s; the sweep runs 0.55 s from the crossing
  const flash = () => (hit() ? Math.exp(-(t() - crossT) / 0.22) : 0);
  const sweep = () => (hit() ? clamp((t() - crossT) / 0.55) : 0);
  
  const chars = [...p.value];
  return (
    <html x={p.x ?? 70} y={p.y ?? 300} width={W} height={470} start={p.s} end={p.e} id={p.id ?? "ctr"}>
      <div style="position:absolute;inset:0;">
        <div style="position:absolute;left:0;top:0;display:flex;align-items:baseline;gap:20px;">
          <span style={`font:800 ${Math.round(150 * k)}px/1 ${FONT};letter-spacing:${(-5 * k).toFixed(1)}px;color:${C.ink};font-variant-numeric:tabular-nums;`}>
            {/* lands final on frame one: no ghost glyphs. The comma gets its own normal spacing: under the tight
                tracking it tucked into the 7 and read as "27/000". */}
            {p.value.split(/(,)/).map((part) => (part === "," ? <span style="letter-spacing:0;margin:0 0.07em 0 0.03em;font-variant-numeric:normal;">,</span> : part))}
          </span>
          <span style={{ font: `800 ${Math.round(84 * k)}px ${FONT}`, "letter-spacing": "-2px", color: C.grey }}>{p.unit ?? ""}</span>
        </div>
        {/* track, fill (object, travels), goal tick (object, pops on contact) */}
        <div style={`position:absolute;left:0;top:${barY}px;width:${W}px;height:${barH}px;border-radius:${barH / 2}px;background:${C.cell};`} />
        <div style={{ position: "absolute", left: "0", top: `${barY}px`, width: `${(W * fill()).toFixed(1)}px`, height: `${barH}px`, "border-radius": `${barH / 2}px`, background: hit() ? C.ink : "#B9B9BF", "box-shadow": hit() ? `0 0 ${(50 * flash()).toFixed(1)}px rgba(250,250,252,${(0.55 * flash()).toFixed(3)})` : "none" }} />
        {/* the goal-crossing event: a light sweep runs along the fill once */}
        <div style={{ position: "absolute", top: `${barY}px`, height: `${barH}px`, width: "220px", left: `${(W * fill() * sweep() - 220).toFixed(1)}px`, "border-radius": `${barH / 2}px`, background: "linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.95), rgba(255,255,255,0))", display: sweep() > 0 && sweep() < 1 ? "block" : "none" }} />
        <div
          style={{
            position: "absolute", left: `${W * p.goal - 7}px`, top: `${barY - Math.round(34 * k)}px`, width: "14px", height: `${barH + Math.round(68 * k)}px`, "border-radius": "7px",
            background: hit() ? C.ink : C.grey, "box-shadow": hit() ? `0 0 ${(70 * flash()).toFixed(1)}px ${(18 * flash()).toFixed(1)}px rgba(250,250,252,${(0.9 * flash()).toFixed(3)})` : "none", transform: `scale(${hit() ? (1 + 0.45 * Math.sin(Math.PI * clamp((t() - crossT) / 0.32))).toFixed(3) : "1"})`,
          }}
        />
        <div style={{ position: "absolute", left: `${Math.max(0, W * p.goal - 200)}px`, width: "400px", top: `${barY + barH + Math.round(44 * k)}px`, "text-align": W * p.goal < 200 ? "left" : "center", "white-space": "nowrap", font: `900 ${Math.round(68 * k)}px ${FONT}`, "letter-spacing": "1.5px", color: hit() ? C.ink : C.grey, ...softStyle(soften(t() - 0.2, 0.3)) }}>
          {p.goalLabel ?? "GOAL"}
        </div>
      </div>
    </html>
  );
}
