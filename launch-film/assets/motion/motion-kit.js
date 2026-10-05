// launch-film motion kit (v1.1.0). Depth field, story camera, rack focus, event flares and rings,
// iris scene change, kinetic type and odometers for a one-stage HTML film on a 1920x1080 stage.
//
// Every frame is a pure function of the master clock: call kit.apply(t) from the timeline's
// onUpdate (and once at t = 0). Every property the kit touches is written on every call, because
// cloud render workers seek out of order. No randomness at runtime: fields use a seeded generator.
// ASCII only on purpose: some checkers inline this file into the page.
//
//   const kit = MotionKit.create({ stage: "#stage", accent: "#154CFF", paper: "#F6F8FF", images, fields,
//     camera, rack, flares, irises, glyphs, odometers });
//   tl.eventCallback("onUpdate", () => kit.apply(tl.time()));
//   kit.apply(0);
//   kit.events()  // every motion event as [{t, kind, label}], for the SFX table and the beat plan
//
// See references/motion-kit.md for every option and the rules that keep it readable.
"use strict";
(() => {
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v)),
    smooth = (n) => { n = clamp(n); return n * n * (3 - 2 * n); },
    expo = (n) => { n = clamp(n); return n === 1 ? 1 : 1 - Math.pow(2, -10 * n); },
    mix = (a, b, p) => a + (b - a) * p,
    // closed-form damped spring: seek-safe, no state between frames
    spring = (t, k = 150, c = 20) => {
      if (t <= 0) return 0;
      const w = Math.sqrt(k), z = c / (2 * w), wd = w * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
    },
    rnd = (seed) => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646,
    EASE = { smooth, expo, linear: clamp };

  const W = 1920, H = 1080, SPAN = 3600;

  function rgb(c) {
    if (Array.isArray(c)) return c;
    const h = String(c).replace("#", "");
    const n = parseInt(h.length === 3 ? h.split("").map((x) => x + x).join("") : h, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a.toFixed(3)})`;
  const el = (x, root = document) => (typeof x === "string" ? root.querySelector(x) : x);

  // ---- camera ----------------------------------------------------------------------------------
  // keys: [{t, x, y, z, rx, ry, e}] in master seconds. e is the ease INTO that key:
  // "smooth", "expo" (a move that lands fast, then rests) or "spring" (a fly-in that settles).
  const K0 = { x: 0, y: 0, z: 0, rx: 0, ry: 0 };
  function camAt(keys, t) {
    if (!keys || !keys.length) return K0;
    const k = (i) => ({ ...K0, ...keys[i] });
    if (t <= keys[0].t) return k(0);
    for (let i = 1; i < keys.length; i++) {
      const a = k(i - 1), b = k(i);
      if (t < b.t) {
        const u = (t - a.t) / (b.t - a.t);
        const p = b.e === "spring" ? spring(t - a.t, 120, 19) : (EASE[b.e] || smooth)(u);
        const o = {};
        for (const n of ["x", "y", "z", "rx", "ry"]) o[n] = mix(a[n], b[n], p);
        return o;
      }
    }
    return k(keys.length - 1);
  }
  const camCSS = (c, P) =>
    `perspective(${P}px) translate3d(${-c.x}px, ${-c.y}px, ${c.z}px) rotateX(${c.rx}deg) rotateY(${c.ry}deg)`;

  // ---- depth field -----------------------------------------------------------------------------
  // Cards are crops of the user's own UI. They sit in 3D around the frame centre, blur by distance
  // from the focus depth, haze with depth, drift toward the lens and fade out before they reach
  // the content plane, so no card ever crosses the text.
  function buildField(world, f, images) {
    const r = rnd(f.seed || 7), cards = [];
    for (let i = 0; i < (f.n || 16); i++) {
      const kind = f.kinds[i % f.kinds.length], img = images[kind];
      if (!img) throw new Error(`motion-kit: unknown image "${kind}"`);
      const [src, w0, h0] = img;
      const d = document.createElement("div");
      d.className = "mk-card";
      const w = mix(f.minW || 300, f.maxW || 520, r());
      d.style.width = `${w}px`;
      d.style.height = `${(w * h0) / w0}px`;
      d.style.backgroundImage = `url("${src}")`;
      world.appendChild(d);
      const a = r() * Math.PI * 2, rad = mix(0.45, 1.2, r()) * (f.spread || 1);
      cards.push({ el: d, w, h: (w * h0) / w0, x: Math.cos(a) * 1100 * rad, y: Math.sin(a) * 640 * rad,
        z: mix(f.zFront ?? -600, f.zBack ?? -3800, r()), vx: mix(-14, 14, r()), vy: mix(-9, 9, r()),
        rot: mix(-12, 12, r()), ph: r() * 6.28 });
    }
    return cards;
  }
  function drawField(st, t, c, P) {
    const f = st.f, [t0, t1] = f.window || [-1e9, 1e9];
    let op = t < t0 || t >= t1 ? 0 : (f.fadeIn ? smooth((t - t0) / f.fadeIn) : 1) * (f.fadeOut ? 1 - smooth((t - (t1 - f.fadeOut)) / f.fadeOut) : 1);
    // rush: a dolly through the field as a scene exit, [{t, dur, dist}]
    let rush = 0;
    for (const r of f.rush || []) rush += r.dist * smooth((t - r.t) / r.dur);
    const tt = t - t0 + (f.phase || 1.5);
    const travel = (f.drift ?? 300) * 2.0 * tt + rush;
    for (const k of st.cards) {
      let z = k.z + travel - (f.start || 0) * (1 - expo((tt - 0.4) / 1.6));
      z = ((((z + 600) % SPAN) + SPAN) % SPAN) - SPAN + 400; // [-3200, 400)
      const x = k.x + k.vx * tt, y = k.y + k.vy * tt + Math.sin(tt * 0.6 + k.ph) * 14,
        depth = -z - c.z, near = z + c.z;
      const blur = (f.minBlur ?? 2) + clamp(Math.abs(depth - (f.focus ?? 1200)) / 130, 0, 14) + (near > -120 ? 10 : 0);
      const fadeFar = clamp((3400 + z) / 700), fadeNear = 1 - clamp((near + 520) / 420);
      const o = op * (f.op ?? 0.9) * fadeFar * fadeNear * (1 - (f.haze ?? 0.25) * clamp(-z / 3400));
      k.el.style.opacity = o.toFixed(3);
      k.el.style.filter = `blur(${blur.toFixed(1)}px)`;
      k.el.style.transform = `translate3d(${(x - k.w / 2).toFixed(1)}px, ${(y - k.h / 2).toFixed(1)}px, ${z.toFixed(1)}px) rotateY(${(k.rot * 0.6).toFixed(2)}deg) rotateZ(${(k.rot * 0.15).toFixed(2)}deg)`;
    }
    st.world.style.transform = `translate(${W / 2}px, ${H / 2}px) ${camCSS(c, P)}`;
    st.host.style.visibility = op > 0 ? "inherit" : "hidden";
  }

  // ---- kinetic type ----------------------------------------------------------------------------
  // Glyphs land from depth on a spring with blur and settle to plain text (transform "none"), so
  // the text is still while it is read. Odometers roll digit columns and land on the real value;
  // they never show an intermediate number that is not part of a count-up.
  function glyphSetup(node) {
    if (node.__mkg) return node.__mkg;
    const text = node.textContent;
    node.innerHTML = [...text].map((ch) => (ch === " " ? " " : `<span class="mk-gl">${ch}</span>`)).join("");
    node.style.perspective = "900px";
    return (node.__mkg = [...node.querySelectorAll(".mk-gl")]);
  }
  function drawGlyphs(gl, t, o) {
    const stagger = o.stagger ?? 0.016, from = o.from ?? 320;
    gl.forEach((g, i) => {
      const tt = t - i * stagger, s = spring(tt, 260, 30), e = clamp(tt / 0.12);
      const settled = tt > 0.9;
      g.style.opacity = e.toFixed(3);
      g.style.transform = settled ? "none" : `translate3d(0, ${((1 - s) * 0.3).toFixed(3)}em, ${(-from * (1 - s)).toFixed(1)}px) rotateX(${(-40 * (1 - s)).toFixed(2)}deg)`;
      g.style.filter = settled ? "none" : `blur(${Math.min(12, Math.abs(1 - s) * 12).toFixed(2)}px)`;
    });
  }
  const ROLL = 2;
  function odoSetup(node, text) {
    if (node.__odo === text) return;
    node.__odo = text;
    node.innerHTML = [...text].map((ch) => /\d/.test(ch)
      ? `<span class="mk-odo"><span>${[...Array(10 * ROLL + 10).keys()].map((k) => `<span>${k % 10}</span>`).join("")}</span></span>`
      : `<span>${ch}</span>`).join("");
    node.__cols = [...node.querySelectorAll(".mk-odo > span")];
    node.__digits = [...text].filter((ch) => /\d/.test(ch)).map(Number);
  }
  function drawOdometer(node, p) {
    node.__cols.forEach((col, i) => {
      // later digits land later and spin further, like a real counter
      const q = clamp((p - i * 0.08) / (1 - i * 0.08));
      const target = 10 * ROLL + node.__digits[i];
      const pos = target * (1 - Math.pow(1 - q, 3)), speed = 3 * Math.pow(1 - q, 2) * target;
      col.style.transform = q >= 1 ? `translateY(${-target}em)` : `translateY(${-pos}em)`;
      col.style.filter = q >= 1 ? "none" : `blur(${Math.min(12, speed * 0.55).toFixed(2)}px)`;
      col.style.opacity = (0.3 + 0.7 * Math.pow(clamp((q - 0.7) / 0.3), 2)).toFixed(3);
    });
    node.style.opacity = p > 0 ? 1 : 0;
  }

  // ---- create ----------------------------------------------------------------------------------
  function create(o) {
    const stage = el(o.stage || "#stage");
    if (!stage) throw new Error("motion-kit: stage not found");
    const P = o.perspective || 1700, accent = rgb(o.accent || "#154CFF"), paper = rgb(o.paper || "#F6F8FF");
    const images = o.images || {};

    const css = document.createElement("style");
    css.textContent = `
      .mk-field{position:absolute;left:0;top:0;width:${W}px;height:${H}px;overflow:hidden;pointer-events:none}
      .mk-world{position:absolute;left:0;top:0;width:0;height:0;transform-style:preserve-3d}
      .mk-card{position:absolute;left:0;top:0;border-radius:${o.radius ?? 14}px;background-size:cover;background-position:center;
        box-shadow:0 30px 60px rgba(20,30,70,.22),0 0 0 1px rgba(255,255,255,.55);will-change:transform,filter,opacity}
      .mk-veil{position:absolute;inset:0;pointer-events:none}
      .mk-fx{position:absolute;left:0;top:0;width:${W}px;height:${H}px;pointer-events:none;z-index:${o.fxZ ?? 40}}
      .mk-fx .mk-fl{position:absolute;left:0;top:0;border-radius:50%;opacity:0}
      .mk-rim{position:absolute;left:0;top:0;width:${W}px;height:${H}px;pointer-events:none;opacity:0;z-index:${(o.fxZ ?? 40) + 1}}
      .mk-gl{display:inline-block;will-change:transform,filter,opacity}
      .mk-odo{display:inline-block;height:1em;line-height:1em;overflow:hidden;vertical-align:-0.12em}
      .mk-odo>span,.mk-odo>span>span{display:block;height:1em}
    `;
    document.head.appendChild(css);

    // fields: {host (parent selector), before (sibling selector), veil: [[x, y, rx, ry, alpha]], cam: "main" | "none"}
    const fields = (o.fields || []).map((f) => {
      const parent = el(f.host || stage), host = document.createElement("div"), world = document.createElement("div");
      host.className = "mk-field"; world.className = "mk-world";
      if (f.z != null) host.style.zIndex = f.z;
      host.appendChild(world);
      parent.insertBefore(host, f.before ? el(f.before) : parent.firstChild);
      // veils keep text on calm ground: paper-coloured ellipses over the field, under the content
      if (f.veil) {
        const v = document.createElement("div");
        v.className = "mk-veil";
        v.style.background = f.veil.map(([x, y, rx, ry, a = 0.9]) =>
          `radial-gradient(ellipse ${rx}px ${ry}px at ${x}px ${y}px, ${rgba(paper, a)} 0, ${rgba(paper, a * 0.8)} 45%, ${rgba(paper, 0)} 100%)`).join(",");
        host.appendChild(v);
      }
      return { f, host, world, cards: buildField(world, f, images) };
    });

    // camera: the content plane (one or more elements) moved as one plane
    const cam = o.camera || { keys: [] };
    const camTargets = (cam.targets || []).map((s) => el(s)).filter(Boolean);

    // rack focus: [{t, dur, sharp, soft: [...], blur}] - the sharp element is crisp, the soft ones blurred
    const rack = (o.rack || []).map((r) => ({ ...r, sharpEl: el(r.sharp), softEls: (r.soft || []).map((s) => el(s)) }));
    const rackEls = [...new Set(rack.flatMap((r) => [r.sharpEl, ...r.softEls]).filter(Boolean))];

    const fx = document.createElement("div");
    fx.className = "mk-fx";
    stage.appendChild(fx);
    const rim = document.createElement("div");
    rim.className = "mk-rim";
    stage.appendChild(rim);

    // flares: [{t, at: selector or [x, y], tint}] - a glow plus a shock ring from the event point
    const flares = (o.flares || []).map((f) => {
      const g = document.createElement("div"), r = document.createElement("div");
      g.className = r.className = "mk-fl";
      fx.appendChild(g); fx.appendChild(r);
      return { ...f, tint: rgb(f.tint || accent), g, r };
    });
    const point = (at) => {
      if (Array.isArray(at)) return at;
      const sr = stage.getBoundingClientRect(), b = el(at).getBoundingClientRect(), s = sr.width / W || 1;
      return [(b.left - sr.left + b.width / 2) / s, (b.top - sr.top + b.height / 2) / s];
    };

    // irises: [{t, dur, from, incoming: [...], outgoing: [...], tint}] - the next scene opens as a disc
    // from the event point with a lit leading edge; the outgoing scene blurs and scales out
    const irises = (o.irises || []).map((i) => ({ dur: 0.4, ...i, tint: rgb(i.tint || accent),
      inEls: (i.incoming || []).map((s) => el(s)), outEls: (i.outgoing || []).map((s) => el(s)) }));

    const managed = [...new Set([...camTargets, ...rackEls, ...irises.flatMap((i) => i.outEls)])].filter(Boolean);

    const glyphs = (o.glyphs || []).map((g) => ({ ...g, node: el(g.el) }));
    glyphs.forEach((g) => { g.gl = glyphSetup(g.node); });
    const odos = (o.odometers || []).map((d) => ({ dur: 0.9, ...d, node: el(d.el) }));
    odos.forEach((d) => {
      if (!/^[\d.,%+\-x$ ]+$/.test(d.text)) throw new Error(`motion-kit: odometer text must be a real value, got "${d.text}"`);
      odoSetup(d.node, d.text);
    });

    function apply(t) {
      const c = camAt(cam.keys, t), cc = camCSS(c, P);
      // reset everything the kit blurs or scales, then write this frame's values
      for (const e of managed) { e.style.filter = ""; e.style.scale = ""; }
      for (const e of camTargets) {
        e.style.transformOrigin = cam.origin || `${W / 2}px ${H / 2}px`;
        e.style.transform = cc;
      }
      for (const st of fields) drawField(st, t, st.f.cam === "none" ? K0 : c, P);

      // rack focus: interpolate each element's blur between consecutive rack keys
      for (const e of rackEls) {
        let b = 0;
        for (let i = 0; i < rack.length; i++) {
          const r = rack[i];
          if (t < r.t) break;
          const p = smooth((t - r.t) / (r.dur || 0.35));
          const now = r.sharpEl === e ? 0 : r.softEls.includes(e) ? (r.blur ?? 5) : null;
          if (now != null) b = mix(b, now, p);
        }
        e.style.filter = b > 0.05 ? `blur(${b.toFixed(2)}px)` : "";
      }

      // irises
      rim.style.opacity = 0;
      for (const i of irises) for (const e of i.inEls) e.style.webkitMaskImage = e.style.maskImage = "none";
      for (const i of irises) {
        const p = clamp((t - i.t) / i.dur);
        if (t < i.t || p >= 1) continue;
        const [ex, ey] = point(i.from);
        const R = Math.hypot(Math.max(ex, W - ex), Math.max(ey, H - ey)) + 160, r = Math.pow(p, 1.25) * R;
        const m = `radial-gradient(circle at ${ex}px ${ey}px, #000 ${r}px, transparent ${r + 70}px)`;
        for (const e of i.inEls) e.style.webkitMaskImage = e.style.maskImage = m;
        for (const e of i.outEls) {
          e.style.filter = `blur(${(p * 10).toFixed(2)}px)`;
          e.style.scale = (1 + 0.1 * p).toFixed(4);
        }
        const a = Math.sin(p * Math.PI) * clamp((r - 60) / 500), tn = i.tint;
        rim.style.opacity = 1;
        rim.style.background = `radial-gradient(circle at ${ex}px ${ey}px, transparent ${Math.max(0, r - 46)}px, ${rgba(tn, 0.28 * a)} ${Math.max(0, r - 12)}px, rgba(255,255,255,${(0.95 * a).toFixed(3)}) ${r + 4}px, ${rgba(tn, 0.4 * a)} ${r + 18}px, transparent ${r + 70}px)`;
      }

      // flares and rings (they track the element, so they follow the camera)
      for (const f of flares) {
        const u = t - f.t, { g, r } = f;
        if (u < -0.05 || u > 0.9) { g.style.opacity = r.style.opacity = 0; continue; }
        const [x, y] = point(f.at), tn = f.tint;
        const gi = clamp(u / 0.08) * (1 - smooth((u - 0.08) / 0.6)), gs = 120 + 160 * expo(u / 0.5);
        g.style.width = g.style.height = `${gs * 2}px`;
        g.style.transform = `translate(${(x - gs).toFixed(1)}px, ${(y - gs).toFixed(1)}px)`;
        // white is capped at 0.4: a flare warms the point, it never whites out the frame (0 flashes)
        g.style.background = `radial-gradient(circle, rgba(255,255,255,${(0.4 * gi).toFixed(3)}) 0, ${rgba(tn, 0.22 * gi)} 35%, ${rgba(tn, 0)} 70%)`;
        g.style.opacity = 1;
        const rr = 30 + 230 * expo(u / 0.7);
        r.style.width = r.style.height = `${rr * 2}px`;
        r.style.transform = `translate(${(x - rr).toFixed(1)}px, ${(y - rr).toFixed(1)}px)`;
        r.style.border = `${Math.max(1, 6 * (1 - u)).toFixed(1)}px solid ${rgba(tn, 1)}`;
        r.style.opacity = (clamp(u / 0.05) * (1 - smooth(u / 0.75)) * 0.75).toFixed(3);
      }

      for (const g of glyphs) drawGlyphs(g.gl, t - g.t, g);
      for (const d of odos) drawOdometer(d.node, t < d.t ? 0 : Math.max(1e-4, clamp((t - d.t) / d.dur)));
    }

    // every motion event, for the per-event SFX table and the beat plan of the digestibility audit
    function events() {
      const ev = [];
      (cam.keys || []).forEach((k, i) => {
        if (!i) return;
        const a = cam.keys[i - 1], moved = ["x", "y", "z", "rx", "ry"].some((n) => Math.abs((k[n] || 0) - (a[n] || 0)) > 1);
        if (moved) ev.push({ t: a.t, kind: k.e === "expo" ? "push" : k.e === "spring" ? "fly-in" : "drift", label: k.label || "" });
      });
      for (const f of fields) for (const r of f.f.rush || []) ev.push({ t: r.t, kind: "dolly", label: "" });
      for (const r of rack) ev.push({ t: r.t, kind: "rack", label: r.sharp || "" });
      for (const f of flares) ev.push({ t: f.t, kind: "flare", label: typeof f.at === "string" ? f.at : "" });
      for (const i of irises) ev.push({ t: i.t, kind: "iris", label: "" });
      for (const g of glyphs) ev.push({ t: g.t, kind: "glyphs", label: g.el });
      for (const d of odos) ev.push({ t: d.t, kind: "odometer", label: d.text }, { t: d.t + d.dur, kind: "odometer-land", label: d.text });
      return ev.sort((a, b) => a.t - b.t).map((e) => ({ ...e, t: +e.t.toFixed(3) }));
    }

    return { apply, events, camAt: (t) => camAt(cam.keys, t) };
  }

  window.MotionKit = { create, spring, smooth, expo, beat: (bpm) => (b) => +((b * 60) / bpm).toFixed(4) };
})();
