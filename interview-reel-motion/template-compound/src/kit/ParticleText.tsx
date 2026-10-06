// ParticleText: a particle swarm that forms a word, the word resolves in place,
// then the swarm dissolves. New code (no in-house equivalent); built on three.js
// THREE.Points on a <surface>. Text is sampled to target points with the
// browser's own 2D text rasteriser (getImageData), the standard three.js recipe.
// Particles are OBJECTS, so they travel; the crisp word never moves: it Softens
// in at exactly the position the particles resolved to (same raster, same canvas).
// Deterministic: a seeded PRNG decides everything; positions are pure functions
// of composition time.
import { useTicker, useResolution, type SceneNode } from "@compound/jsx";
import { createEffect, createSignal, onCleanup, onMount } from "solid-js";
import * as THREE from "three";
import { C, FONT, clamp, rng, expoOut, snappyIn, inOut, cubicOut } from "./clock";

type Props = {
  id?: string; s: number; e: number; text: string;
  x?: number; y?: number; width?: number; height?: number;
  /** font size of the resolved word in px */
  size?: number; weight?: number;
  count?: number;
  /** timeline (seconds from s): swarm until form, form until resolve, dissolve from e - dissolve */
  form?: number; resolve?: number; dissolve?: number;
  color?: string;
  /** soft dark field behind the word, for use over footage */
  scrim?: boolean;
};

export function ParticleText(p: Props) {
  const { time, hold } = useTicker();
  const [ready, setReady] = createSignal(false);
  const resolution = useResolution();
  const W = p.width ?? 1080, H = p.height ?? 900;
  const N = p.count ?? 7000, size = p.size ?? 230, form = p.form ?? 0.08, res = p.resolve ?? 0.8, dis = p.dissolve ?? 0.6;
  let ref: SceneNode | undefined;

  let txt!: HTMLCanvasElement, face!: HTMLCanvasElement, glowC!: HTMLCanvasElement;
  const tgt = new Float32Array(N * 2), orb = new Float32Array(N * 4), del = new Float32Array(N), scat = new Float32Array(N * 3);
  const sample = () => {
  // --- sample the word (also kept as the crisp texture) ---
  txt = document.createElement("canvas");
  txt.width = W; txt.height = H;
  const tc = txt.getContext("2d", { willReadFrequently: true })!;
  tc.fillStyle = "#fff"; tc.textAlign = "center"; tc.textBaseline = "middle";
  tc.font = `${p.weight ?? 800} ${size}px ${FONT}`;
  (tc as any).letterSpacing = `${-size * 0.03}px`;
  tc.fillText(p.text, W / 2, H / 2);
  const data = tc.getImageData(0, 0, W, H).data;
  const pts: number[] = [];
  for (let yy = 0; yy < H; yy += 3) for (let xx = 0; xx < W; xx += 3) if (data[(yy * W + xx) * 4 + 3] > 140) pts.push(xx, yy);
  const r = rng(11);
  // per particle: target, swarm orbit params, delay
  const M = pts.length / 2;
  for (let i = 0; i < N; i++) {
    const j = Math.floor(r() * M);
    tgt[i * 2] = pts[j * 2] + (r() - 0.5) * 2; tgt[i * 2 + 1] = pts[j * 2 + 1] + (r() - 0.5) * 2;
    orb[i * 4] = 90 + Math.pow(r(), 0.7) * 430; // radius
    orb[i * 4 + 1] = r() * Math.PI * 2; // phase
    orb[i * 4 + 2] = (0.8 + r() * 1.6) * (r() < 0.5 ? -1 : 1); // angular speed
    orb[i * 4 + 3] = (r() - 0.5) * 900; // z depth
    del[i] = (tgt[i * 2] / W) * 0.12 + r() * 0.06; // left-to-right resolve, a little loose
    const a = r() * Math.PI * 2, b = (r() - 0.5) * Math.PI;
    const sp = 260 + r() * 700;
    scat[i * 3] = Math.cos(a) * Math.cos(b) * sp; scat[i * 3 + 1] = Math.sin(b) * sp; scat[i * 3 + 2] = Math.sin(a) * Math.cos(b) * sp + 300;
  }
  // the resolved word: extruded (stacked offset layers) with a bevel gradient face and a top-edge highlight
  const font = `${p.weight ?? 800} ${size}px ${FONT}`, ls = `${-size * 0.03}px`, depth = Math.round(size * 0.09);
  face = document.createElement("canvas"); face.width = W; face.height = H;
  const fc = face.getContext("2d")!;
  fc.font = font; (fc as any).letterSpacing = ls; fc.textAlign = "center"; fc.textBaseline = "middle";
  for (let k = depth; k >= 1; k--) {
    const v = Math.round(52 + (1 - k / depth) * 60);
    fc.fillStyle = `rgb(${v},${v},${v + 4})`;
    fc.fillText(p.text, W / 2 + k * 0.45, H / 2 + k * 0.9);
  }
  const gr = fc.createLinearGradient(0, H / 2 - size * 0.4, 0, H / 2 + size * 0.4);
  gr.addColorStop(0, "#FFFFFF"); gr.addColorStop(0.55, "#E4E4E8"); gr.addColorStop(1, "#A9A9B0");
  fc.fillStyle = gr; fc.fillText(p.text, W / 2, H / 2);
  fc.save(); fc.globalCompositeOperation = "source-atop"; fc.strokeStyle = "rgba(255,255,255,.95)"; fc.lineWidth = 3;
  fc.strokeText(p.text, W / 2, H / 2 - 1.5); fc.restore();
  // bloom source: the word, heavily blurred
  glowC = document.createElement("canvas"); glowC.width = W; glowC.height = H;
  const gc = glowC.getContext("2d")!;
  gc.font = font; (gc as any).letterSpacing = ls; gc.textAlign = "center"; gc.textBaseline = "middle";
  gc.filter = `blur(${Math.round(size * 0.14)}px)`; gc.fillStyle = "#fff"; gc.fillText(p.text, W / 2, H / 2);
  gc.filter = `blur(${Math.round(size * 0.05)}px)`; gc.fillText(p.text, W / 2, H / 2);

  };

  onMount(() => {
    const el = ref!.element!;
    const renderer = new THREE.WebGLRenderer({ canvas: el, antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setClearColor(0x000000, 0);
    const scene = new THREE.Scene();
    const fov = 40;
    const camZ = H / 2 / Math.tan((fov * Math.PI) / 360);
    const cam = new THREE.PerspectiveCamera(fov, W / H, 1, 6000);
    cam.position.set(0, 0, camZ);
    // pixel space: (px, py) -> (px - W/2, H/2 - py, 0) lands exactly on the canvas pixel
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(N * 3);
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const dot = document.createElement("canvas"); dot.width = dot.height = 32;
    const dc = dot.getContext("2d")!;
    const g = dc.createRadialGradient(16, 16, 0, 16, 16, 16);
    g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.45, "rgba(255,255,255,.85)"); g.addColorStop(1, "rgba(255,255,255,0)");
    dc.fillStyle = g; dc.fillRect(0, 0, 32, 32);
    const mat = new THREE.PointsMaterial({ size: 9, blending: THREE.AdditiveBlending, map: new THREE.CanvasTexture(dot), transparent: true, depthWrite: false, color: new THREE.Color(p.color ?? C.ink), sizeAttenuation: true });
    const points = new THREE.Points(geo, mat);
    scene.add(points);
    const NT = Math.ceil(N / 2);
    const trail = new Float32Array(NT * 6), tCol = new Float32Array(NT * 6);
    for (let q = 0; q < NT; q++) { tCol.set([0, 0, 0, 1, 1, 1], q * 6); }
    const tGeo = new THREE.BufferGeometry();
    tGeo.setAttribute("position", new THREE.BufferAttribute(trail, 3));
    tGeo.setAttribute("color", new THREE.BufferAttribute(tCol, 3));
    const tMat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.9 });
    scene.add(new THREE.LineSegments(tGeo, tMat));
    // crisp word plane, same raster the particles were sampled from
    const fontReady = (document as any).fonts?.load ? (document as any).fonts.load(`${p.weight ?? 800} ${size}px ${FONT}`).catch(() => null) : Promise.resolve();
    const wordTex = new THREE.CanvasTexture(document.createElement("canvas"));
    wordTex.colorSpace = THREE.SRGBColorSpace;
    const wordMat = new THREE.MeshBasicMaterial({ map: wordTex, transparent: true, opacity: 0, depthWrite: false });
    const word = new THREE.Mesh(new THREE.PlaneGeometry(W, H), wordMat);
    // scrim (over footage only): a soft dark field behind the word so it reads on any picture
    const scr = document.createElement("canvas"); scr.width = 256; scr.height = 256;
    const sc2 = scr.getContext("2d")!;
    const rg = sc2.createRadialGradient(128, 128, 0, 128, 128, 128);
    rg.addColorStop(0, "rgba(9,9,11,.78)"); rg.addColorStop(0.55, "rgba(9,9,11,.5)"); rg.addColorStop(1, "rgba(9,9,11,0)");
    sc2.fillStyle = rg; sc2.fillRect(0, 0, 256, 256);
    const scrimMat = new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(scr), transparent: true, opacity: 0, depthWrite: false, depthTest: false });
    const scrim = new THREE.Mesh(new THREE.PlaneGeometry(W * 1.1, H * 0.95), scrimMat);
    scrim.renderOrder = -2; scrim.position.z = -400; scrim.scale.setScalar((camZ + 400) / camZ);
    if (p.scrim) scene.add(scrim);
    const glowTex = new THREE.CanvasTexture(document.createElement("canvas"));
    const glowMat = new THREE.MeshBasicMaterial({ map: glowTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
    const glow = new THREE.Mesh(new THREE.PlaneGeometry(W, H), glowMat);
    glow.renderOrder = 2; word.renderOrder = 1;
    scene.add(glow);
    scene.add(word);
    hold(Promise.resolve(fontReady).then(() => { sample(); wordTex.image = face; wordTex.needsUpdate = true; glowTex.image = glowC; glowTex.needsUpdate = true; setReady(true); }));
    const blurCanvas = document.createElement("canvas"); blurCanvas.width = W; blurCanvas.height = H;
    const bc = blurCanvas.getContext("2d")!;
    const blurTex = new THREE.CanvasTexture(blurCanvas);
    let lastBlur = -1;

    createEffect(() => {
      if (!ready()) return;
      const k = resolution();
      renderer.setPixelRatio(1);
      renderer.setSize(W * k, H * k, false);
      const t = time() - p.s, life = p.e - p.s;
      const dOut = clamp((t - (life - dis)) / dis);
      // position of particle i at local time tt (pure function: also used for the trail tails)
      const P3 = (i: number, tt: number, o: Float32Array, j: number) => {
        const R = orb[i * 4], ph = orb[i * 4 + 1], w = orb[i * 4 + 2], zz = orb[i * 4 + 3];
        const residue = i % 12 === 0; // ~8% never join the word: a sparse drift so the frame is never empty
        // swarm: already in motion on frame 1, a turning cloud collapsing in from off frame
        const a = ph + tt * w;
        const conv = 1 + 1.6 * (1 - expoOut(clamp((tt + 0.25) / 0.7)));
        const br = (1 + 0.12 * Math.sin(tt * 3 + ph * 2)) * conv * (residue ? 1.25 : 1);
        const sx = Math.cos(a) * R * br, sy = Math.sin(a) * R * 0.55 * br + Math.sin(a * 2 + ph) * 60, sz = zz + Math.sin(a) * 200;
        const tx = tgt[i * 2] - W / 2, ty = H / 2 - tgt[i * 2 + 1];
        const f = residue ? 0 : expoOut(clamp((tt - form - del[i]) / 0.55));
        // spiral in: the offset from the target rotates while it shrinks, so every path is a curve
        const dx = sx - tx, dy = sy - ty, sw = (1 - f) * 2.4 * Math.sign(w), cs = Math.cos(sw), sn = Math.sin(sw);
        let x = tx + (dx * cs - dy * sn) * (1 - f), y = ty + (dx * sn + dy * cs) * (1 - f), z = sz * (1 - f);
        const dOutL = clamp((tt - (life - dis)) / dis);
        const hold = clamp((tt - res) / 0.3) * (1 - dOutL);
        x += hold * Math.sin(tt * 5 + ph * 7) * 1.2; y += hold * Math.cos(tt * 4 + ph * 5) * 1.2;
        const dd = snappyIn(dOutL);
        x += scat[i * 3] * dd; y += scat[i * 3 + 1] * dd; z += scat[i * 3 + 2] * dd;
        o[j] = x; o[j + 1] = y; o[j + 2] = z;
      };
      for (let i = 0; i < N; i++) P3(i, t, pos, i * 3);
      // streaks: every 2nd particle draws a line from where it was 50 ms ago (tail dark, head bright, additive)
      for (let i = 0, q = 0; i < N; i += 2, q++) {
        P3(i, t - 0.05, trail, q * 6);
        trail[q * 6 + 3] = pos[i * 3]; trail[q * 6 + 4] = pos[i * 3 + 1]; trail[q * 6 + 5] = pos[i * 3 + 2];
      }
      tGeo.attributes.position.needsUpdate = true;
      tMat.opacity = 0.9 * (1 - clamp((t - res) / 0.3)) + 0.6 * Math.sin(Math.PI * dOut);
      // slow dolly-in on the resolved word (a camera move, the word itself stays put in its plane)
      cam.position.z = camZ * (1 - 0.07 * inOut(clamp((t - res) / Math.max(0.1, life - dis - res))));
      geo.attributes.position.needsUpdate = true;
      mat.opacity = (1 - 0.55 * clamp((t - res) / 0.35)) * (1 - inOut(dOut) * 0.85);
      // the crisp word: Soften in place (blur -> sharp), hard-ish out as the swarm leaves
      const wv = cubicOut(clamp((t - res) / 0.3));
      const wOut = cubicOut(clamp((t - (life - dis)) / (dis * 0.5)));
      const blur = (1 - wv) * 12 + wOut * 8;
      const b = Math.round(blur * 2) / 2;
      if (b !== lastBlur) {
        lastBlur = b;
        if (b <= 0) { wordMat.map = wordTex; } else {
          bc.clearRect(0, 0, W, H); bc.filter = `blur(${b}px)`; bc.drawImage(face, 0, 0); bc.filter = "none";
          blurTex.needsUpdate = true; wordMat.map = blurTex;
        }
        wordMat.needsUpdate = true;
      }
      wordMat.opacity = wv * (1 - wOut);
      // bloom flares as the word resolves, then settles to a soft halo
      glowMat.opacity = clamp((t - res + 0.15) / 0.25) * (1 - 0.6 * clamp((t - res - 0.25) / 0.5)) * (1 - wOut) * 0.85;
      scrimMat.opacity = clamp(t / 0.4) * (1 - inOut(dOut));
      renderer.render(scene, cam);
    });
    onCleanup(() => { tGeo.dispose(); tMat.dispose(); geo.dispose(); mat.dispose(); wordMat.dispose(); wordTex.dispose(); blurTex.dispose(); renderer.dispose(); });
  });

  return <surface x={p.x ?? 0} y={p.y ?? 500} width={W} height={H} start={p.s} end={p.e} id={p.id ?? "ptxt"} ref={ref} />;
}
