// TypeRing: a 3D spinning ring of repeated type (the ref's chrome "GRAPHICS" ring).
// New code (no in-house equivalent); three.js on a <surface>. The word is set
// once by the browser's text rasteriser into a strip texture and wrapped on an
// open cylinder (front faces in ink, back faces in grey, the classic depth read).
// Chrome: MeshStandardMaterial, metalness 1, lit by three's RoomEnvironment
// (in-memory PMREM, no HDR fetch), so highlights sweep across the letters as the
// ring turns. troika-three-text was not needed: one strip texture is enough.
// The ring is an OBJECT: it enters with an overshoot spin and tilt, turns at a
// steady rate, then whips out. Deterministic in composition time.
import { useTicker, useResolution, type SceneNode } from "@compound/jsx";
import { createEffect, createSignal, onCleanup, onMount } from "solid-js";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { FONT, clamp, expoOut, expoIn, rng } from "./clock";

type Props = {
  id?: string; s: number; e: number; text: string;
  x?: number; y?: number; width?: number; height?: number;
  /** times the word repeats around the ring */
  repeat?: number;
  radius?: number; band?: number;
  /** degrees of tilt toward camera and of roll */
  tilt?: number; roll?: number;
  /** turns per second at cruise */
  spin?: number;
  chrome?: boolean;
  /** optional second, counter-rotating ring of smaller type */
  inner?: string;
  /** orbiting chrome debris chips around the ring (0 = none) */
  debris?: number;
  /** occlusion layering with a person matte: "back" = far arc + rear debris, "front" = near arc + front debris */
  layer?: "all" | "back" | "front";
  /** exit by lifting up and shrinking instead of flying through the lens (over a face) */
  exitLift?: boolean;
  /** opacity of the defocused back arc (default 0.3; raise it so the pass behind a head reads) */
  backOpacity?: number;
};

function strip(text: string, repeat: number, h: number, weight = 900, blur = 0) {
  const c = document.createElement("canvas");
  const ctx = c.getContext("2d")!;
  const font = `${weight} ${Math.round(h * 0.78)}px ${FONT}`;
  ctx.font = font;
  const unit = text + "   ";
  const uw = ctx.measureText(unit).width;
  c.width = Math.min(8192, Math.ceil(uw * repeat)); c.height = h;
  const k = c.width / (uw * repeat);
  ctx.font = font;
  ctx.setTransform(k, 0, 0, 1, 0, 0);
  ctx.fillStyle = "#fff"; ctx.textBaseline = "middle";
  if (blur > 0) ctx.filter = `blur(${blur}px)`;
  for (let i = 0; i < repeat; i++) ctx.fillText(unit, i * uw, h / 2 + h * 0.03);
  return c;
}

export function TypeRing(p: Props) {
  const { time, hold } = useTicker();
  const resolution = useResolution();
  const [ready, setReady] = createSignal(false);
  const W = p.width ?? 1080, H = p.height ?? 1080;
  let ref: SceneNode | undefined;

  onMount(() => {
    const el = ref!.element!;
    const renderer = new THREE.WebGLRenderer({ canvas: el, antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    const scene = new THREE.Scene();
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    const cam = new THREE.PerspectiveCamera(32, W / H, 1, 100);
    cam.position.set(0, 0, 11);
    const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(3, 6, 8); scene.add(key);
    // rim lights from behind and above: bright edges on the front letters as they turn
    const rimA = new THREE.DirectionalLight(0xffffff, 5); rimA.position.set(-6, 5, -7); scene.add(rimA);
    const rimB = new THREE.DirectionalLight(0xffffff, 3.5); rimB.position.set(7, -2, -5); scene.add(rimB);

    const rig = new THREE.Group(); scene.add(rig);
    const R = p.radius ?? 3.1, B = p.band ?? 0.95;
    const mk = (text: string, repeat: number, radius: number, band: number) => {
      const g = new THREE.Group();
      const geo = new THREE.CylinderGeometry(radius, radius, band, 256, 1, true);
      const tex = new THREE.CanvasTexture(strip(text, repeat, 256));
      tex.anisotropy = 8; tex.wrapS = THREE.RepeatWrapping;
      // map the strip so it reads left-to-right from the front
      const chrome = p.chrome ?? true;
      const front = new THREE.MeshStandardMaterial({ color: 0xfafafc, metalness: chrome ? 1 : 0, roughness: chrome ? 0.22 : 0.6, alphaMap: tex, transparent: true, side: THREE.FrontSide, depthWrite: false, envMapIntensity: 1.4 });
      // back half: a defocused copy of the strip at ~30%, so depth reads (front sharp, back soft)
      const texB = new THREE.CanvasTexture(strip(text, repeat, 256, 900, 7));
      texB.wrapS = THREE.RepeatWrapping;
      const back = new THREE.MeshBasicMaterial({ color: 0x8a8a92, alphaMap: texB, transparent: true, side: THREE.BackSide, depthWrite: false, opacity: p.backOpacity ?? 0.3 });
      const mb = new THREE.Mesh(geo, back); mb.renderOrder = 0;
      const mf = new THREE.Mesh(geo, front); mf.renderOrder = 1;
      const lay = p.layer ?? "all";
      mb.visible = lay !== "front"; mf.visible = lay !== "back";
      g.add(mb, mf);
      return { g, dispose: () => { geo.dispose(); tex.dispose(); texB.dispose(); front.dispose(); back.dispose(); } };
    };
    let outer: ReturnType<typeof mk> | null = null, inner: ReturnType<typeof mk> | null = null;
    const build = () => {
      outer = mk(p.text, p.repeat ?? 4, R, B);
      rig.add(outer.g);
      if (p.inner) { inner = mk(p.inner, 6, R * 0.62, B * 0.42); inner.g.position.y = -0.05; rig.add(inner.g); }
    };

    // debris: small chrome chips on their own orbits around the ring
    const ND = p.debris ?? 0;
    const dr = rng(23);
    const dGeo = new THREE.BoxGeometry(0.22, 0.07, 0.012);
    const dMat = new THREE.MeshStandardMaterial({ color: 0xfafafc, metalness: 1, roughness: 0.25, envMapIntensity: 1.5 });
    const debris = new THREE.InstancedMesh(dGeo, dMat, Math.max(1, ND));
    const dp = Array.from({ length: ND }, () => ({ r: R * (1.08 + dr() * 0.42), h: (dr() - 0.5) * B * 2.6, a0: dr() * Math.PI * 2, w: (0.7 + dr() * 0.9) * (dr() < 0.85 ? 1 : -1), s: 0.5 + dr() * 1.3, sp: dr() * 6 }));
    const dm = new THREE.Object3D();
    if (ND > 0) rig.add(debris);

    const fontReady = (document as any).fonts?.load ? (document as any).fonts.load(`900 100px ${FONT}`).catch(() => null) : Promise.resolve();
    hold(Promise.resolve(fontReady).then(() => { build(); setReady(true); }));

    createEffect(() => {
      if (!ready() || !outer) return;
      const k = resolution();
      renderer.setPixelRatio(1);
      renderer.setSize(W * k, H * k, false);
      const t = time() - p.s, life = p.e - p.s;
      const inK = expoOut(clamp(t / 0.9));
      const outK = expoIn(clamp((t - (life - 0.35)) / 0.35));
      const spin = (p.spin ?? 0.22) * Math.PI * 2;
      // entry: a fast spin that decelerates into cruise (object overshoot), exit: whip + fly past
      const ang = t * spin + (1 - inK) * -2.6 + outK * 3.2;
      outer!.g.rotation.y = ang;
      if (inner) inner.g.rotation.y = -ang * 1.35 + 0.6;
      const tilt = ((p.tilt ?? 14) * Math.PI) / 180, roll = ((p.roll ?? -9) * Math.PI) / 180;
      rig.rotation.x = tilt + (1 - inK) * 0.9 * (tilt < 0 ? -1 : 1);
      rig.rotation.z = roll * inK;
      const lay = p.layer ?? "all";
      for (let i = 0; i < ND; i++) {
        const d = dp[i], a = d.a0 + ang * d.w;
        const z = Math.sin(a) * d.r;
        const show = lay === "all" || (lay === "back" ? z < 0 : z >= 0);
        dm.position.set(Math.cos(a) * d.r, d.h, z);
        dm.rotation.set(t * d.sp, a, t * d.sp * 0.7);
        dm.scale.setScalar(show ? d.s * inK : 0);
        dm.updateMatrix();
        debris.setMatrixAt(i, dm.matrix);
      }
      debris.instanceMatrix.needsUpdate = true;
      const sc = 0.55 + 0.45 * inK + (p.exitLift ? -0.5 * outK : outK * 1.6);
      rig.scale.setScalar(sc);
      if (p.exitLift) rig.position.y = outK * 5; else rig.position.z = outK * 4;
      renderer.render(scene, cam);
    });
    onCleanup(() => { dGeo.dispose(); dMat.dispose(); outer?.dispose(); inner?.dispose(); pmrem.dispose(); renderer.dispose(); });
  });

  return <surface x={p.x ?? 0} y={p.y ?? 420} width={W} height={H} start={p.s} end={p.e} id={p.id ?? "ring"} ref={ref} />;
}
