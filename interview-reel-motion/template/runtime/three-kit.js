// three-kit.js: the WebGL pieces of the kit, three.js on a <canvas>, driven only by scene time.
//   ParticleText  a seeded particle swarm forms a word; the crisp word Softens in place; the swarm dissolves
//   TypeRing      a chrome ring of repeated type turning in 3D (optional occlusion layer for a person matte)
// Ported 1:1 from the Compound kit. Each factory returns { update(t) } bound to a canvas the engine owns.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/RoomEnvironment.js";

const IRM = window.IRM;
const { C, FONT, clamp, rng, expoOut, expoIn, snappyIn, inOut, cubicOut } = IRM;

function ParticleText(p, canvas) {
  const W = p.width ?? 1080, H = p.height ?? 900;
  const N = p.count ?? 7000, size = p.size ?? 230, form = p.form ?? 0.08, res = p.resolve ?? 0.8, dis = p.dissolve ?? 0.6;
  const tgt = new Float32Array(N * 2), orb = new Float32Array(N * 4), del = new Float32Array(N), scat = new Float32Array(N * 3);
  let face, glowC;
  const sample = () => {
    const txt = document.createElement("canvas");
    txt.width = W; txt.height = H;
    const tc = txt.getContext("2d", { willReadFrequently: true });
    tc.fillStyle = "#fff"; tc.textAlign = "center"; tc.textBaseline = "middle";
    tc.font = `${p.weight ?? 800} ${size}px ${FONT}`;
    tc.letterSpacing = `${-size * 0.03}px`;
    tc.fillText(p.text, W / 2, H / 2);
    const data = tc.getImageData(0, 0, W, H).data;
    const pts = [];
    for (let yy = 0; yy < H; yy += 3) for (let xx = 0; xx < W; xx += 3) if (data[(yy * W + xx) * 4 + 3] > 140) pts.push(xx, yy);
    const r = rng(11);
    const M = pts.length / 2;
    for (let i = 0; i < N; i++) {
      const j = Math.floor(r() * M);
      tgt[i * 2] = pts[j * 2] + (r() - 0.5) * 2; tgt[i * 2 + 1] = pts[j * 2 + 1] + (r() - 0.5) * 2;
      orb[i * 4] = 90 + Math.pow(r(), 0.7) * 430;
      orb[i * 4 + 1] = r() * Math.PI * 2;
      orb[i * 4 + 2] = (0.8 + r() * 1.6) * (r() < 0.5 ? -1 : 1);
      orb[i * 4 + 3] = (r() - 0.5) * 900;
      del[i] = (tgt[i * 2] / W) * 0.12 + r() * 0.06;
      const a = r() * Math.PI * 2, b = (r() - 0.5) * Math.PI;
      const sp = 260 + r() * 700;
      scat[i * 3] = Math.cos(a) * Math.cos(b) * sp; scat[i * 3 + 1] = Math.sin(b) * sp; scat[i * 3 + 2] = Math.sin(a) * Math.cos(b) * sp + 300;
    }
    const font = `${p.weight ?? 800} ${size}px ${FONT}`, ls = `${-size * 0.03}px`, depth = Math.round(size * 0.09);
    face = document.createElement("canvas"); face.width = W; face.height = H;
    const fc = face.getContext("2d");
    fc.font = font; fc.letterSpacing = ls; fc.textAlign = "center"; fc.textBaseline = "middle";
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
    glowC = document.createElement("canvas"); glowC.width = W; glowC.height = H;
    const gc = glowC.getContext("2d");
    gc.font = font; gc.letterSpacing = ls; gc.textAlign = "center"; gc.textBaseline = "middle";
    gc.filter = `blur(${Math.round(size * 0.14)}px)`; gc.fillStyle = "#fff"; gc.fillText(p.text, W / 2, H / 2);
    gc.filter = `blur(${Math.round(size * 0.05)}px)`; gc.fillText(p.text, W / 2, H / 2);
  };

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  const scene = new THREE.Scene();
  const fov = 40, camZ = H / 2 / Math.tan((fov * Math.PI) / 360);
  const cam = new THREE.PerspectiveCamera(fov, W / H, 1, 6000);
  cam.position.set(0, 0, camZ);
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(N * 3);
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const dot = document.createElement("canvas"); dot.width = dot.height = 32;
  const dc = dot.getContext("2d");
  const g = dc.createRadialGradient(16, 16, 0, 16, 16, 16);
  g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.45, "rgba(255,255,255,.85)"); g.addColorStop(1, "rgba(255,255,255,0)");
  dc.fillStyle = g; dc.fillRect(0, 0, 32, 32);
  const mat = new THREE.PointsMaterial({ size: 9, blending: THREE.AdditiveBlending, map: new THREE.CanvasTexture(dot), transparent: true, depthWrite: false, color: new THREE.Color(p.color ?? C.ink), sizeAttenuation: true });
  scene.add(new THREE.Points(geo, mat));
  const NT = Math.ceil(N / 2);
  const trail = new Float32Array(NT * 6), tCol = new Float32Array(NT * 6);
  for (let q = 0; q < NT; q++) tCol.set([0, 0, 0, 1, 1, 1], q * 6);
  const tGeo = new THREE.BufferGeometry();
  tGeo.setAttribute("position", new THREE.BufferAttribute(trail, 3));
  tGeo.setAttribute("color", new THREE.BufferAttribute(tCol, 3));
  const tMat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.9 });
  scene.add(new THREE.LineSegments(tGeo, tMat));
  const wordTex = new THREE.CanvasTexture(document.createElement("canvas"));
  wordTex.colorSpace = THREE.SRGBColorSpace;
  const wordMat = new THREE.MeshBasicMaterial({ map: wordTex, transparent: true, opacity: 0, depthWrite: false });
  const word = new THREE.Mesh(new THREE.PlaneGeometry(W, H), wordMat);
  const scr = document.createElement("canvas"); scr.width = 256; scr.height = 256;
  const sc2 = scr.getContext("2d");
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
  scene.add(glow); scene.add(word);
  sample();
  wordTex.image = face; wordTex.needsUpdate = true;
  glowTex.image = glowC; glowTex.needsUpdate = true;
  const blurCanvas = document.createElement("canvas"); blurCanvas.width = W; blurCanvas.height = H;
  const bc = blurCanvas.getContext("2d");
  const blurTex = new THREE.CanvasTexture(blurCanvas);
  let lastBlur = -1;

  return {
    update(time) {
      const t = time - p.s, life = p.e - p.s;
      const dOut = clamp((t - (life - dis)) / dis);
      const P3 = (i, tt, o, j) => {
        const R = orb[i * 4], ph = orb[i * 4 + 1], w = orb[i * 4 + 2], zz = orb[i * 4 + 3];
        const residue = i % 12 === 0;
        const a = ph + tt * w;
        const conv = 1 + 1.6 * (1 - expoOut(clamp((tt + 0.25) / 0.7)));
        const br = (1 + 0.12 * Math.sin(tt * 3 + ph * 2)) * conv * (residue ? 1.25 : 1);
        const sx = Math.cos(a) * R * br, sy = Math.sin(a) * R * 0.55 * br + Math.sin(a * 2 + ph) * 60, sz = zz + Math.sin(a) * 200;
        const tx = tgt[i * 2] - W / 2, ty = H / 2 - tgt[i * 2 + 1];
        const f = residue ? 0 : expoOut(clamp((tt - form - del[i]) / 0.55));
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
      for (let i = 0, q = 0; i < N; i += 2, q++) {
        P3(i, t - 0.05, trail, q * 6);
        trail[q * 6 + 3] = pos[i * 3]; trail[q * 6 + 4] = pos[i * 3 + 1]; trail[q * 6 + 5] = pos[i * 3 + 2];
      }
      tGeo.attributes.position.needsUpdate = true;
      tMat.opacity = 0.9 * (1 - clamp((t - res) / 0.3)) + 0.6 * Math.sin(Math.PI * dOut);
      cam.position.z = camZ * (1 - 0.07 * inOut(clamp((t - res) / Math.max(0.1, life - dis - res))));
      geo.attributes.position.needsUpdate = true;
      mat.opacity = (1 - 0.55 * clamp((t - res) / 0.35)) * (1 - inOut(dOut) * 0.85);
      const wv = cubicOut(clamp((t - res) / 0.3));
      const wOut = cubicOut(clamp((t - (life - dis)) / (dis * 0.5)));
      const b = Math.round(((1 - wv) * 12 + wOut * 8) * 2) / 2;
      if (b !== lastBlur) {
        lastBlur = b;
        if (b <= 0) wordMat.map = wordTex;
        else { bc.clearRect(0, 0, W, H); bc.filter = `blur(${b}px)`; bc.drawImage(face, 0, 0); bc.filter = "none"; blurTex.needsUpdate = true; wordMat.map = blurTex; }
        wordMat.needsUpdate = true;
      }
      wordMat.opacity = wv * (1 - wOut);
      glowMat.opacity = clamp((t - res + 0.15) / 0.25) * (1 - 0.6 * clamp((t - res - 0.25) / 0.5)) * (1 - wOut) * 0.85;
      scrimMat.opacity = clamp(t / 0.4) * (1 - inOut(dOut));
      renderer.render(scene, cam);
    },
  };
}

function strip(text, repeat, h, weight = 900, blur = 0) {
  const c = document.createElement("canvas");
  const ctx = c.getContext("2d");
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

function TypeRing(p, canvas) {
  const W = p.width ?? 1080, H = p.height ?? 1080;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const cam = new THREE.PerspectiveCamera(32, W / H, 1, 100);
  cam.position.set(0, 0, 11);
  const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(3, 6, 8); scene.add(key);
  const rimA = new THREE.DirectionalLight(0xffffff, 5); rimA.position.set(-6, 5, -7); scene.add(rimA);
  const rimB = new THREE.DirectionalLight(0xffffff, 3.5); rimB.position.set(7, -2, -5); scene.add(rimB);
  const rig = new THREE.Group(); scene.add(rig);
  const R = p.radius ?? 3.1, B = p.band ?? 0.95;
  const lay = p.layer ?? "all";
  const mk = (text, repeat, radius, band) => {
    const g = new THREE.Group();
    const geo = new THREE.CylinderGeometry(radius, radius, band, 256, 1, true);
    const tex = new THREE.CanvasTexture(strip(text, repeat, 256));
    tex.anisotropy = 8; tex.wrapS = THREE.RepeatWrapping;
    const chrome = p.chrome ?? true;
    const front = new THREE.MeshStandardMaterial({ color: 0xfafafc, metalness: chrome ? 1 : 0, roughness: chrome ? 0.22 : 0.6, alphaMap: tex, transparent: true, side: THREE.FrontSide, depthWrite: false, envMapIntensity: 1.4 });
    const texB = new THREE.CanvasTexture(strip(text, repeat, 256, 900, 7));
    texB.wrapS = THREE.RepeatWrapping;
    const back = new THREE.MeshBasicMaterial({ color: 0x8a8a92, alphaMap: texB, transparent: true, side: THREE.BackSide, depthWrite: false, opacity: p.backOpacity ?? 0.3 });
    const mb = new THREE.Mesh(geo, back); mb.renderOrder = 0;
    const mf = new THREE.Mesh(geo, front); mf.renderOrder = 1;
    mb.visible = lay !== "front"; mf.visible = lay !== "back";
    g.add(mb, mf);
    return { g };
  };
  const outer = mk(p.text, p.repeat ?? 4, R, B);
  rig.add(outer.g);
  let inner = null;
  if (p.inner) { inner = mk(p.inner, 6, R * 0.62, B * 0.42); inner.g.position.y = -0.05; rig.add(inner.g); }
  const ND = p.debris ?? 0;
  const dr = rng(23);
  const dGeo = new THREE.BoxGeometry(0.22, 0.07, 0.012);
  const dMat = new THREE.MeshStandardMaterial({ color: 0xfafafc, metalness: 1, roughness: 0.25, envMapIntensity: 1.5 });
  const debris = new THREE.InstancedMesh(dGeo, dMat, Math.max(1, ND));
  const dp = Array.from({ length: ND }, () => ({ r: R * (1.08 + dr() * 0.42), h: (dr() - 0.5) * B * 2.6, a0: dr() * Math.PI * 2, w: (0.7 + dr() * 0.9) * (dr() < 0.85 ? 1 : -1), s: 0.5 + dr() * 1.3, sp: dr() * 6 }));
  const dm = new THREE.Object3D();
  if (ND > 0) rig.add(debris);
  return {
    update(time) {
      const t = time - p.s, life = p.e - p.s;
      const inK = expoOut(clamp(t / 0.9));
      const outK = expoIn(clamp((t - (life - 0.35)) / 0.35));
      const spin = (p.spin ?? 0.22) * Math.PI * 2;
      const ang = t * spin + (1 - inK) * -2.6 + outK * 3.2;
      outer.g.rotation.y = ang;
      if (inner) inner.g.rotation.y = -ang * 1.35 + 0.6;
      const tilt = ((p.tilt ?? 14) * Math.PI) / 180, roll = ((p.roll ?? -9) * Math.PI) / 180;
      rig.rotation.x = tilt + (1 - inK) * 0.9 * (tilt < 0 ? -1 : 1);
      rig.rotation.z = roll * inK;
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
    },
  };
}

IRM.three = { ParticleText, TypeRing };
IRM.threeLoaded();
