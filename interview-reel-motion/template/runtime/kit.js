// kit.js: the interview-reel components as HyperFrames-ready DOM nodes.
// Ported 1:1 from the Compound kit (KineticWord, BuildPanel, CounterBar, OrbitCards, CameraPush, Overlays).
// Rules carried over: TYPE NEVER MOVES (glyphs only Soften in place), objects may travel and overshoot,
// NO COUNT-UPS (every figure lands final), monochrome #09090B / #FAFAFC / #A0A0A5, logos are plain <img>.
// Every component returns a node { el, update(t) } whose look is a pure function of scene time t.
(function () {
  const IRM = window.IRM;
  const { clamp, soften, softStyle, snappyOut, expoOut, expoIn, inOut, backOut, cubicOut, rng, easeInOut, C, FONT, css, esc, M } = IRM;
  const N = IRM.nodes;
  const R = IRM.rules;
  const W = 1080, H = 1920;
  const EXIT = () => R.EXIT_FRAMES / R.FPS;
  const glyphs = (s) => [...String(s)].map((c) => (c === " " ? " " : esc(c)));

  /* ============================================================ KineticWord + Sticker */
  function KineticWord(p) {
    const Wd = p.width ?? 1000, Hd = p.height ?? 140, size = p.size ?? 84;
    const s = Math.min(...p.words.map((w) => w.t0)), e = Math.max(...p.words.map((w) => w.t1));
    const per = p.per ?? "char", st = p.stagger ?? 0.028, inD = p.inDur ?? 0.24, bl = p.blur ?? 13;
    const shadow = p.overFace ? "0 2px 8px rgba(0,0,0,.45), 0 0 30px rgba(0,0,0,.35)" : "none";
    return N.html({
      id: p.id ?? "kw", x: p.x ?? 40, y: p.y ?? 1400, w: Wd, h: Hd, s, e,
      tpl: (t) => {
        let out = `<div style="position:relative;width:${Wd}px;height:${Hd}px;">`;
        for (const w of p.words) {
          if (!(t >= w.t0 - 0.001 && t < w.t1)) continue;
          const chars = per === "char" ? glyphs(w.text) : [esc(w.text)];
          const plate = p.plate ? `display:flex;padding:${size * 0.06}px ${size * 0.22}px ${size * 0.1}px;border-radius:${size * 0.24}px;background:rgba(9,9,11,.58);box-shadow:0 24px 70px rgba(0,0,0,.4);` : "display:flex;";
          out += `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:${p.weight ?? 700} ${size}px ${FONT};letter-spacing:${-size * 0.02}px;color:${p.color ?? C.ink};text-shadow:${shadow};white-space:pre;"><div style="${plate}">`;
          chars.forEach((ch, i) => { out += `<span style="display:inline-block;${softStyle(soften(t - w.t0 - i * st, inD, Infinity, 0, bl))}">${ch}</span>`; });
          out += `</div></div>`;
        }
        return out + `</div>`;
      },
    });
  }

  function Sticker(p) {
    const Wd = p.width ?? 640, Hd = p.height ?? 190, size = p.size ?? 88;
    const box = Wd + 80, boxH = Hd + 120;
    const chars = glyphs(p.text);
    return N.html({
      id: p.id ?? "stk", x: p.x - 40, y: p.y - 40, w: box, h: boxH, s: p.s, e: p.e,
      tpl: (t) => {
        const k = clamp((t - p.s) / 0.4), pop = clamp(k / 0.6);
        const pillScale = k < 0.6 ? 0.6 + 0.43 * snappyOut(k / 0.6) : 1.03 - 0.03 * inOut((k - 0.6) / 0.4);
        let out = `<div style="position:relative;width:${box}px;height:${boxH}px;">`;
        out += `<div style="position:absolute;left:40px;top:40px;width:${Wd}px;height:${Hd}px;border-radius:${Hd * 0.22}px;background:${p.fill ?? "#FFFFFF"};box-shadow:${p.shadow ?? "0 30px 60px rgba(0,0,0,.5), 0 8px 18px rgba(0,0,0,.3)"};transform:translateY(${((1 - snappyOut(pop)) * -60).toFixed(2)}px) rotate(${p.rot ?? -7}deg) scale(${pillScale.toFixed(4)});opacity:${clamp(pop * 3).toFixed(3)};"></div>`;
        out += `<div style="position:absolute;left:40px;top:40px;width:${Wd}px;height:${Hd}px;display:flex;align-items:center;justify-content:center;transform:rotate(${p.rot ?? -7}deg);font:900 ${size}px ${FONT};letter-spacing:${-size * 0.03}px;color:${p.ink ?? "#0A0A0A"};">`;
        chars.forEach((ch, i) => { out += `<span style="display:inline-block;${softStyle(soften(t - p.s - 0.1 - i * 0.022, 0.2, Infinity, 0, 9))}">${ch}</span>`; });
        return out + `</div></div>`;
      },
    });
  }

  /* ============================================================ BuildPanel */
  const PAD = 48;
  const plate = (t, s, fade = true) => {
    const k = cubicOut(clamp((t - s) / 0.55));
    const rx = 7 + (1 - k) * 16, ry = -5 - (1 - k) * 8;
    return `transform:perspective(1800px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg) translateY(${((1 - k) * 40).toFixed(2)}px);transform-origin:50% 70%;` + (fade ? `opacity:${k.toFixed(3)};` : "");
  };
  const backing = `position:absolute;left:0;top:0;right:0;bottom:0;border-radius:40px;background:linear-gradient(180deg,#141417,#0E0E10);border:2px solid rgba(250,250,252,.10);box-shadow:0 50px 110px rgba(0,0,0,.65), 0 10px 30px rgba(0,0,0,.4);`;

  function ChatPrompt(p) {
    const Wd = p.width ?? 864, size = p.size ?? 96, cps = p.cps ?? 24;
    const Hd = Math.round(size * 1.35 * 2 + 150);
    const r = rng(7);
    const at = [];
    let acc = 0.55;
    for (const ch of p.text) { acc += (1 / cps) * (0.55 + r() * 0.9) * (ch === " " ? 1.6 : 1); at.push(acc); }
    const doneAt = acc, pressAt = doneAt + 0.35, workEnd = pressAt + 0.75, btn = 76;
    return N.html({
      id: p.id ?? "chat", x: (p.x ?? 108) - PAD, y: (p.y ?? 300) - PAD, w: Wd + 2 * PAD, h: Hd + 2 * PAD, s: p.s, e: p.e,
      tpl: (time) => {
        const t = time - p.s;
        const k = at.filter((a) => a <= t).length;
        const focus = clamp((t - 0.35) / 0.16);
        const armed = k >= [...p.text].length;
        const press = t > pressAt && t < pressAt + 0.14 ? 1 : 0;
        const state = t < pressAt ? 0 : t < workEnd ? 1 : 2;
        const caretOn = focus > 0.5 && state === 0 && (k > 0 && k < [...p.text].length ? true : (time * 1.6) % 1 < 0.5);
        const txt = [...p.text].slice(0, k).join("");
        return `<div style="position:absolute;left:${PAD}px;top:${PAD}px;width:${Wd}px;height:${Hd}px;${plate(time, p.s, false)}">`
          + `<div style="position:absolute;inset:0;border-radius:34px;background:${C.cell};border:2px solid ${focus > 0.4 ? "rgba(250,250,252,.42)" : "rgba(250,250,252,.10)"};box-shadow:0 0 0 ${(focus * 6).toFixed(2)}px rgba(250,250,252,.06), 0 30px 70px rgba(0,0,0,.5);"></div>`
          + `<div style="position:absolute;left:38px;top:34px;width:${Wd - 76}px;font:500 ${size}px/${size * 1.35}px ${FONT};letter-spacing:-0.5px;color:${C.ink};">`
          + `<span style="color:${C.grey};display:${k === 0 ? "inline" : "none"};">${esc(p.placeholder ?? "Ask for anything")}</span>`
          + `<span>${esc(txt)}</span>`
          + `<span style="display:inline-block;width:3px;height:${size * 1.05}px;vertical-align:-6px;margin-left:2px;background:${C.ink};visibility:${caretOn ? "visible" : "hidden"};"></span></div>`
          + `<div style="position:absolute;right:26px;bottom:24px;width:${btn}px;height:${btn}px;border-radius:22px;background:${armed ? C.ink : "#2A2A2E"};display:flex;align-items:center;justify-content:center;transform:scale(${press ? 0.9 : 1 + (state === 2 ? (1 - clamp((t - workEnd) / 0.3)) * 0.08 : 0)});">`
          + `<svg width="38" height="38" viewBox="0 0 24 24" style="display:${state === 0 ? "block" : "none"};"><path d="M12 19V5M5.5 11.5 12 5l6.5 6.5" fill="none" stroke="${armed ? C.ground : "#6A6A70"}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`
          + `<svg width="40" height="40" viewBox="0 0 24 24" style="display:${state === 1 ? "block" : "none"};"><circle cx="12" cy="12" r="8.5" fill="none" stroke="rgba(9,9,11,.25)" stroke-width="2.4"/><path d="M12 3.5a8.5 8.5 0 0 1 8.5 8.5" fill="none" stroke="${C.ground}" stroke-width="2.4" stroke-linecap="round" transform="rotate(${((t - pressAt) * 420).toFixed(1)} 12 12)"/></svg>`
          + `<svg width="40" height="40" viewBox="0 0 24 24" style="display:${state === 2 ? "block" : "none"};"><path d="M6 12.5l4 4 8-8.5" fill="none" stroke="${C.ground}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="20" stroke-dashoffset="${(20 * (1 - cubicOut(clamp((t - workEnd) / 0.3)))).toFixed(2)}"/></svg>`
          + `</div></div>`;
      },
    });
  }

  function BarChart(p) {
    const Wd = p.width ?? 864, Hd = p.height ?? 760, every = p.every ?? 0.32;
    const max = Math.max(...p.bars.map((b) => b.value));
    const n = p.bars.length, gap = 28, bw = (Wd - gap * (n - 1)) / n;
    const top = p.title ? 170 : 40, base = Hd - 70, span = base - top - 60;
    const pillAt = 0.12 + n * every + 0.35;
    return N.html({
      id: p.id ?? "bars", x: (p.x ?? 108) - PAD, y: (p.y ?? 200) - PAD, w: Wd + 2 * PAD, h: Hd + 2 * PAD, s: p.s, e: p.e,
      tpl: (time) => {
        const t = time - p.s;
        const grow = (i) => clamp((t - 0.12 - i * every) / (i === n - 1 ? 11 / 30 : 0.3));
        let out = `<div style="position:absolute;inset:0;${plate(time, p.s, false)}"><div style="${backing}"></div><div style="position:absolute;left:${PAD}px;top:${PAD}px;width:${Wd}px;height:${Hd}px;">`;
        out += `<div style="position:absolute;left:0;top:0;font:800 68px ${FONT};letter-spacing:-1.6px;color:${C.ink};${softStyle(soften(t, 0.25))}">${esc(p.title ?? "")}</div>`;
        out += `<div style="position:absolute;left:0;top:80px;font:700 68px ${FONT};letter-spacing:-1.6px;color:${C.grey};${softStyle(soften(t - 0.08, 0.25))}">${esc(p.sub ?? "")}</div>`;
        out += `<div style="position:absolute;left:0;top:${base}px;width:${Wd}px;height:2px;background:rgba(250,250,252,.14);"></div>`;
        p.bars.forEach((b, i) => {
          const h = (b.value / max) * span, last = i === n - 1, g = grow(i), hmin = Math.max(h, 40);
          const hh = hmin * (last ? backOut(g) : snappyOut(g));
          out += `<div style="position:absolute;left:${i * (bw + gap)}px;top:${(base - hh).toFixed(1)}px;width:${bw}px;height:${Math.max(0, hh).toFixed(1)}px;border-radius:14px 14px 4px 4px;background:${last ? C.ink : "#2C2C31"};"></div>`;
          out += `<div style="position:absolute;left:${i * (bw + gap)}px;width:${bw}px;top:${(base - hmin - 74).toFixed(1)}px;text-align:center;font:800 54px ${FONT};letter-spacing:-1px;color:${last ? C.ink : C.grey};${softStyle(soften(t - 0.12 - i * every - 0.24, 0.2))}">${esc(b.display ?? String(b.value))}</div>`;
          out += `<div style="position:absolute;left:${i * (bw + gap)}px;width:${bw}px;top:${base + 16}px;text-align:center;font:700 40px ${FONT};color:${C.grey};${softStyle(soften(t - 0.12 - i * every, 0.22))}">${esc(b.label)}</div>`;
        });
        out += `<div style="position:absolute;right:0;top:${top - 10}px;display:${p.pill ? "block" : "none"};"><div style="padding:16px 30px;border-radius:999px;background:${C.ink};transform:scale(${(0.5 + 0.5 * backOut(clamp((t - pillAt) / 0.3))).toFixed(4)});display:${t > pillAt ? "block" : "none"};transform-origin:100% 50%;"><span style="font:900 44px ${FONT};letter-spacing:-1px;color:${C.ground};${softStyle(soften(t - pillAt - 0.08, 0.2))}">${esc(p.pill ?? "")}</span></div></div>`;
        return out + `</div></div>`;
      },
    });
  }

  function TileGrid(p) {
    const cols = p.cols ?? 10, rows = p.rows ?? 10, total = cols * rows, fill = p.fill ?? total;
    const Wd = p.width ?? 864, gap = 10, cell = (Wd - gap * (cols - 1)) / cols;
    const head = p.value ? 220 : 0, Hd = head + rows * cell + (rows - 1) * gap, sweep = p.sweep ?? 1.1;
    return N.html({
      id: p.id ?? "grid", x: (p.x ?? 108) - PAD, y: (p.y ?? 200) - PAD, w: Wd + 2 * PAD, h: Hd + 2 * PAD, s: p.s, e: p.e,
      tpl: (time) => {
        const t = time - p.s;
        let out = `<div style="position:absolute;inset:0;${plate(time, p.s, false)}"><div style="${backing}"></div><div style="position:absolute;left:${PAD}px;top:${PAD}px;width:${Wd}px;height:${Hd}px;">`;
        out += `<div style="position:absolute;left:0;top:0;display:${p.value ? "flex" : "none"};align-items:baseline;gap:22px;"><span style="font:800 150px/1 ${FONT};letter-spacing:-5px;color:${C.ink};${softStyle(soften(t - 0.15, 0.3))}">${esc(p.value ?? "")}</span><span style="font:800 84px ${FONT};letter-spacing:-2px;color:${C.grey};${softStyle(soften(t - 0.3, 0.3))}">${esc(p.unit ?? "")}</span></div>`;
        for (let i = 0; i < total; i++) {
          const c = i % cols, r = Math.floor(i / cols);
          const skel = expoOut(clamp((t - (c + r) * 0.018) / 0.35));
          const on = i < fill && t > 0.35 + (i / total) * sweep;
          const pop = clamp((t - 0.35 - (i / total) * sweep) / 0.18);
          out += `<div style="position:absolute;left:${(c * (cell + gap)).toFixed(1)}px;top:${(head + r * (cell + gap) + (1 - skel) * 18).toFixed(1)}px;width:${cell.toFixed(1)}px;height:${cell.toFixed(1)}px;border-radius:10px;background:${on ? `rgba(250,250,252,${(0.25 + 0.75 * pop).toFixed(3)})` : `rgba(26,26,26,${skel.toFixed(3)})`};"></div>`;
        }
        return out + `</div></div>`;
      },
    });
  }

  /* ============================================================ CounterBar */
  function CounterBar(p) {
    const Wd = p.width ?? 940, travel = p.travel ?? 1.15, k = p.k ?? 1, barY = Math.round(240 * k), barH = Math.round(80 * k);
    let crossT = Infinity;
    for (let i = 0; i <= 300; i++) {
      const tt = 0.35 + (i / 300) * travel;
      if (p.progress * inOut(clamp((tt - 0.35) / travel)) >= p.goal) { crossT = tt; break; }
    }
    const value = String(p.value).split(/(,)/).map((part) => (part === "," ? `<span style="letter-spacing:0;margin:0 0.07em 0 0.03em;font-variant-numeric:normal;">,</span>` : esc(part))).join("");
    return N.html({
      id: p.id ?? "ctr", x: p.x ?? 70, y: p.y ?? 300, w: Wd, h: 470, s: p.s, e: p.e,
      tpl: (time) => {
        const t = time - p.s;
        const fill = p.progress * inOut(clamp((t - 0.35) / travel));
        const hit = t >= crossT;
        const flash = hit ? Math.exp(-(t - crossT) / 0.22) : 0;
        const sweep = hit ? clamp((t - crossT) / 0.55) : 0;
        return `<div style="position:absolute;inset:0;">`
          + `<div style="position:absolute;left:0;top:0;display:flex;align-items:baseline;gap:20px;"><span style="font:800 ${Math.round(150 * k)}px/1 ${FONT};letter-spacing:${(-5 * k).toFixed(1)}px;color:${C.ink};font-variant-numeric:tabular-nums;">${value}</span><span style="font:800 ${Math.round(84 * k)}px ${FONT};letter-spacing:-2px;color:${C.grey};">${esc(p.unit ?? "")}</span></div>`
          + `<div style="position:absolute;left:0;top:${barY}px;width:${Wd}px;height:${barH}px;border-radius:${barH / 2}px;background:${C.cell};"></div>`
          + `<div style="position:absolute;left:0;top:${barY}px;width:${(Wd * fill).toFixed(1)}px;height:${barH}px;border-radius:${barH / 2}px;background:${hit ? C.ink : "#B9B9BF"};box-shadow:${hit ? `0 0 ${(50 * flash).toFixed(1)}px rgba(250,250,252,${(0.55 * flash).toFixed(3)})` : "none"};"></div>`
          + `<div style="position:absolute;top:${barY}px;height:${barH}px;width:220px;left:${(Wd * fill * sweep - 220).toFixed(1)}px;border-radius:${barH / 2}px;background:linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.95), rgba(255,255,255,0));display:${sweep > 0 && sweep < 1 ? "block" : "none"};"></div>`
          + `<div style="position:absolute;left:${Wd * p.goal - 7}px;top:${barY - Math.round(34 * k)}px;width:14px;height:${barH + Math.round(68 * k)}px;border-radius:7px;background:${hit ? C.ink : C.grey};box-shadow:${hit ? `0 0 ${(70 * flash).toFixed(1)}px ${(18 * flash).toFixed(1)}px rgba(250,250,252,${(0.9 * flash).toFixed(3)})` : "none"};transform:scale(${hit ? (1 + 0.45 * Math.sin(Math.PI * clamp((t - crossT) / 0.32))).toFixed(3) : "1"});"></div>`
          + `<div style="position:absolute;left:${Math.max(0, Wd * p.goal - 200)}px;width:400px;top:${barY + barH + Math.round(44 * k)}px;text-align:${Wd * p.goal < 200 ? "left" : "center"};white-space:nowrap;font:900 ${Math.round(68 * k)}px ${FONT};letter-spacing:1.5px;color:${hit ? C.ink : C.grey};${softStyle(soften(t - 0.2, 0.3))}">${esc(p.goalLabel ?? "GOAL")}</div>`
          + `</div>`;
      },
    });
  }

  /* ============================================================ OrbitCards (CSS 3D, as in the original) */
  const face = (w, h, r = 22) => `width:${w}px;height:${h}px;border-radius:${r}px;background:linear-gradient(160deg,#34343A,#1C1C20);border:2px solid rgba(250,250,252,.32);box-shadow:0 30px 70px rgba(0,0,0,.55);position:relative;font-family:${FONT};`;
  const videoCard = (title, views, img) => ({ w: 360, h: 260, html: `<div style="${face(360, 260)}">` + (img ? `<img src="${esc(img)}" style="position:absolute;left:0;top:0;width:360px;height:196px;object-fit:cover;object-position:50% 30%;border-radius:20px 20px 0 0;">` : `<div style="position:absolute;left:0;top:0;width:360px;height:196px;border-radius:20px 20px 0 0;background:linear-gradient(135deg,#6A6A72,#26262B);"></div>`) + `<div style="position:absolute;left:158px;top:76px;width:0;height:0;border-left:30px solid rgba(250,250,252,.95);border-top:18px solid transparent;border-bottom:18px solid transparent;"></div><div style="position:absolute;right:12px;top:162px;padding:3px 8px;border-radius:6px;background:rgba(0,0,0,.6);color:#FAFAFC;font:600 15px Inter;">0:42</div><div style="position:absolute;left:16px;top:206px;color:#FAFAFC;font:700 19px Inter;letter-spacing:-0.3px;">${esc(title)}</div><div style="position:absolute;left:16px;top:232px;color:#A0A0A5;font:500 15px Inter;">${esc(views)}</div></div>` });
  const phoneCard = (handle, stat, img) => ({ w: 210, h: 374, html: `<div style="${face(210, 374, 30)}background:#16161A;">` + (img ? `<img src="${esc(img)}" style="position:absolute;left:4px;top:4px;width:202px;height:366px;object-fit:cover;border-radius:26px;">` : `<div style="position:absolute;left:4px;top:4px;width:202px;height:366px;border-radius:26px;background:linear-gradient(160deg,#7A7A82,#2A2A30);"></div>`) + `<div style="position:absolute;left:14px;top:18px;color:#FAFAFC;font:700 17px Inter;text-shadow:0 1px 6px rgba(0,0,0,.6);">${esc(handle)}</div><div style="position:absolute;left:14px;bottom:16px;padding:6px 12px;border-radius:999px;background:rgba(250,250,252,.94);color:#0A0A0A;font:800 17px Inter;">▶ ${esc(stat)}</div></div>` });
  const statCard = (num, unit) => ({ w: 300, h: 170, html: `<div style="${face(300, 170)}"><div style="position:absolute;left:22px;top:22px;color:#FAFAFC;font:800 64px Inter;letter-spacing:-2px;line-height:1;">${esc(num)}</div><div style="position:absolute;left:24px;top:106px;color:#A0A0A5;font:600 20px Inter;">${esc(unit)}</div></div>` });
  const imageCard = (src, w = 320, h = 220) => ({ w, h, html: `<div style="${face(w, h)}"><img src="${esc(src)}" style="width:${w}px;height:${h}px;object-fit:cover;border-radius:22px;"></div>` });

  function OrbitCards(p) {
    const Wd = p.width ?? 1080, Hd = p.height ?? 1920;
    const P = p.persp ?? 1400, rx = p.rx ?? 400, rz = p.rz ?? 420, tilt = ((p.tilt ?? 16) * Math.PI) / 180;
    const speed = p.speed ?? 0.85, every = p.every ?? 0.2, focusZ = p.focusZ ?? 260, bpp = p.blurPerPx ?? 0.016, maxBlur = p.maxBlur ?? 12;
    const n = p.cards.length, cs = p.cardScale ?? 1.5, exitDur = 0.42;
    const pose = (i, time) => {
      const t = time - p.s;
      const a = (i / n) * Math.PI * 2 + t * speed + 0.35;
      const tl = tilt + 0.05 * Math.sin(t * 0.8);
      let x = rx * Math.sin(a), z = rz * Math.cos(a), y = Math.cos(a) * rz * Math.sin(tl) + Math.sin(a) * rz * 0.06 * Math.sin(t * 0.6);
      const k = clamp((t - i * every) / 0.7), arr = expoOut(k);
      x = x * (0.55 + 0.45 * arr); y = y + (1 - arr) * (p.arriveDy ?? 260); z = z - (1 - arr) * 2200;
      const ry = Math.sin(a) * 24 + (1 - arr) * 50, rxDeg = (1 - arr) * 24 + 16;
      const ex = expoIn(clamp((time - (p.e - exitDur)) / exitDur));
      if (p.exitLift) y -= ex * 1300; else z += ex * 1700;
      const lay = p.layer ?? "all";
      let g = 1;
      if (p.noGo && p.noGo.length) {
        const row = p.noGo[Math.min(p.noGo.length - 1, Math.max(0, Math.round(t * 30)))];
        const [top, bot, left, right, hl, hr] = row;
        const c = p.cards[i], sc = P / (P - z), hw = ((c.w * cs) / 2) * 1.12, hh = ((c.h * cs) / 2) * 1.12;
        const X0 = p.cx + (x - hw) * sc, X1 = p.cx + (x + hw) * sc, Y0 = p.cy + (y - hh) * sc, Y1 = p.cy + (y + hh) * sc;
        const hidden = z < 0 && X0 >= hl + 10 && X1 <= hr - 10;
        // the drop shadow (0 30px 70px) and the depth blur reach past the card: keep them out of the face box too
        const bl = Math.min(maxBlur, Math.abs(z - focusZ) * bpp), padX = (70 * cs + 2 * bl) * sc, padB = (100 * cs + 2 * bl) * sc;
        if (!hidden && X1 + padX > left && X0 - padX < right && Y1 + padB > top && Y0 < bot) { const cyS = p.cy + y * sc; g = cyS >= top ? 0 : clamp((top - cyS) / (hh * sc + padB)); }
      }
      const seen = k > 0 && z < P - 80 && g >= 0.3 && (lay === "all" || (lay === "back" ? z < 0 : z >= 0));
      const blur = Math.min(maxBlur, Math.abs(z - focusZ) * bpp) + ex * 10;
      const dim = clamp(0.35 + 0.65 * ((z + rz) / (2 * rz)), 0.2, 1);
      return { x, y, z, ry, rxDeg, blur, dim: dim * (0.4 + 0.6 * g), seen, g };
    };
    return N.html({
      id: p.id ?? "orbit", x: 0, y: 0, w: Wd, h: Hd, s: p.s, e: p.e,
      tpl: (time) => {
        let out = `<div style="position:absolute;inset:0;perspective:${P}px;perspective-origin:${p.cx}px ${p.cy}px;">`;
        p.cards.forEach((c, i) => {
          const q = pose(i, time);
          out += `<div style="position:absolute;left:${p.cx - (c.w * cs) / 2}px;top:${p.cy - (c.h * cs) / 2}px;width:${c.w * cs}px;height:${c.h * cs}px;transform:translate3d(${q.x.toFixed(1)}px, ${q.y.toFixed(1)}px, ${q.z.toFixed(1)}px) rotateY(${q.ry.toFixed(2)}deg) rotateX(${q.rxDeg.toFixed(2)}deg) scale(${q.g.toFixed(4)});filter:blur(${q.blur.toFixed(2)}px) brightness(${q.dim.toFixed(3)});display:${q.seen ? "block" : "none"};z-index:${Math.round(q.z + 5000)};"><div style="zoom:${cs};">${c.html}</div></div>`;
        });
        return out + `</div>`;
      },
    });
  }

  /* ============================================================ CameraPush (CSS 3D, replaces the WGSL ray cast) */
  // A real pinhole camera over a flat footage plane: perspective P, push z, pan x/y, tilt rx/ry, keyed and eased
  // with inOut; between two equal keys the camera is exactly still. The footage is any node (usually a stack).
  function CameraPush(p, footage) {
    const ks = p.keys.slice(0, 4);
    const k = (f) => ks.map((q) => ({ t: q.t, v: f(q) ?? 0 }));
    const T = { z: k((q) => q.z), x: k((q) => q.x), y: k((q) => q.y), rx: k((q) => q.rx), ry: k((q) => q.ry) };
    const A = p.anchor ?? [0.5, 0.4];
    const outer = N.mk(N.abspx(p.x, p.y, p.width, p.height) + `overflow:hidden;background:#09090B;perspective:${p.persp ?? 1700}px;perspective-origin:${A[0] * 100}% ${A[1] * 100}%;display:none;`);
    const inner = N.mk(`position:absolute;inset:0;transform-origin:${A[0] * 100}% ${A[1] * 100}%;`);
    inner.appendChild(footage.el); outer.appendChild(inner);
    return {
      el: outer,
      update(t) {
        const on = N.live(t, p.start, p.end);
        outer.style.display = on ? "block" : "none";
        if (!on) return;
        const v = (tr) => IRM.track(tr, t);
        inner.style.transform = `translate3d(${-v(T.x)}px, ${-v(T.y)}px, ${v(T.z)}px) rotateX(${v(T.rx)}deg) rotateY(${v(T.ry)}deg)`;
        footage.update(t);
      },
    };
  }
  function Vignette(p) {
    const k = p.strength ?? 0.55;
    return N.html({ id: p.id ?? "vig", x: 0, y: 0, w: W, h: H, s: p.s, e: p.e, tpl: () => `<div style="width:1080px;height:1920px;background:radial-gradient(ellipse 78% 62% at 50% 46%, rgba(9,9,11,0) 55%, rgba(9,9,11,${k}) 100%);"></div>` });
  }
  function ParallaxCard(p) {
    const Wd = 420, Hd = 190, dur = p.e - p.s;
    return N.html({
      id: p.id ?? "plx", x: p.x - 60, y: p.y - 60, w: Wd + 200, h: Hd + 120, s: p.s, e: p.e,
      tpl: (time) => {
        const t = time - p.s, k = inOut(clamp(t / dur)), enter = clamp(t / 0.35);
        const tx = (1 - enter) * 160 - k * (p.drift ?? 90), sc = 0.92 + 0.16 * k;
        return `<div style="position:absolute;left:60px;top:60px;width:${Wd}px;height:${Hd}px;border-radius:34px;background:rgba(24,24,26,.82);border:1px solid ${C.line};box-shadow:0 30px 70px rgba(0,0,0,.5);transform:translateX(${tx.toFixed(2)}px) rotate(${(-4 + 3 * k).toFixed(3)}deg) scale(${sc.toFixed(4)});display:flex;flex-direction:column;justify-content:center;padding:0 40px;box-sizing:border-box;"><div style="font:600 34px ${FONT};color:${C.grey};${softStyle(soften(t, 0.2))}">${esc(p.title)}</div><div style="font:900 76px ${FONT};color:${C.ink};letter-spacing:-2px;${softStyle(soften(t - 0.05, 0.2))}">${esc(p.stat)}</div></div>`;
      },
    });
  }

  /* ============================================================ Overlays */
  const K = { bg: "#09090B", cell: "#18181A", line: "#2A2A2E", white: "#FAFAFC", grey: "#A0A0A5", ink: "#0A0A0A" };
  const SANS = "Inter, sans-serif"; // only resolvable faces: distributed renders fail closed on unknown font names
  const abs = (x, y, extra = {}) => css({ position: "absolute", left: `${x}px`, top: `${y}px`, ...extra });
  const popO = (t, t0, origin = "left center") => ({ opacity: t < t0 ? 0 : 1, transform: `scale(${t < t0 ? 0.88 : M.tw(t, t0, 0.24, 0.88, 1, M.backOut)})`, "transform-origin": origin });
  const Num = (text) => String(text).split(/(?<=\d),(?=\d)/).map((s, i) => (i === 0 ? esc(s) : `<span style="letter-spacing:0;margin:0 0.06em 0 0.02em;">,</span>${esc(s)}`)).join("");
  const exitKeys = (e) => [[e - EXIT(), 1, easeInOut], [e, 0]];

  /** full-frame html layer pinned to the scene clock, eased out over its last EXIT frames */
  function Frame(o, tpl) {
    const id = o.id ?? "ovl";
    const h = N.html({ id: `${id}frame`, x: 0, y: 0, w: W, h: H, s: o.s, e: o.e, tpl: (t) => `<div style="position:relative;width:${W}px;height:${H}px;background:${o.ground ? K.bg : "transparent"};overflow:hidden;font-family:${SANS};color:${K.white};">${tpl(t)}</div>` });
    return N.group({ id: `${id}grp`, e: o.e, keys: exitKeys(o.e), children: [h] });
  }

  function PopSticker(t, d) {
    const on = t >= d.t0 && (d.t1 === undefined || t < d.t1);
    const z = d.size ?? 72;
    const ex = d.t1 === undefined ? 0 : M.inOut(clamp((t - (d.t1 - EXIT())) / EXIT()));
    const pos = d.rel ? { position: "relative" } : { position: "absolute", left: `${d.x}px`, top: `${d.y}px` };
    const st = css({
      ...pos, display: on ? "block" : "none", opacity: 1 - ex, background: "#FFFFFF", color: K.ink,
      "border-radius": `${Math.round(z * 0.3)}px`, padding: `${Math.round(z * 0.16)}px ${Math.round(z * 0.36)}px`,
      "font-size": `${z}px`, "line-height": "1.02", "font-weight": 800, "letter-spacing": `${-z * 0.02}px`, "white-space": "nowrap",
      "box-shadow": "0 14px 40px rgba(0,0,0,0.35)",
      transform: `rotate(${d.rot ?? -7}deg) scale(${(t < d.t0 ? 0.6 : M.tw(t, d.t0, 0.26, 0.6, 1, M.backOut)) * (1 - 0.12 * ex)})`,
      "transform-origin": "center",
    });
    return `<div style="${st}">${d.lines ? d.lines.map((l) => `<div>${esc(l)}</div>`).join("") : esc(d.text)}</div>`;
  }

  function StickerStack(p) {
    return Frame(p, (t) => p.items.map((d) => d.center
      ? `<div style="${abs(0, d.y, { width: `${p.safeWidth ?? 930}px`, display: "flex", "justify-content": "center" })}">${PopSticker(t, { t0: d.t0, t1: d.t1, x: 0, y: 0, text: d.text ?? (d.lines ?? [""])[0], lines: d.lines && d.lines.length > 1 ? d.lines : undefined, rot: d.rot, size: d.size, rel: true })}</div>`
      : PopSticker(t, { t0: d.t0, t1: d.t1, x: d.x ?? 0, y: d.y, text: d.text ?? "", lines: d.lines, rot: d.rot, size: d.size })).join(""));
  }

  const chipBox = (c) => ({ display: "flex", "align-items": "center", gap: `${c.gap}px`, background: c.bg, border: c.border, "border-radius": `${c.radius}px`, padding: c.pad, "white-space": "nowrap", ...(c.shadow ? { "box-shadow": c.shadow } : {}) });
  const chipInner = (c) => `<div style="width:${c.logoSize}px;height:${c.logoSize}px;"></div><span style="font-size:${c.size}px;font-weight:800;letter-spacing:-1px;color:${K.white};white-space:nowrap;">${esc(c.label)}</span>`;
  const logoXY = (c) => { const parts = c.pad.split(" "); return [c.x + parseFloat(parts[parts.length - 1]), c.y + parseFloat(parts[0])]; };
  /** the logo is a plain <img> layered over the chip's spacer, easing out with it */
  function ChipLogo(o, c, id) {
    if (!c.logo) return null;
    const [x, y] = logoXY(c);
    const im = N.img({ id: `${id}lgi`, src: IRM.asset(c.logo), x, y, w: c.logoSize, h: c.logoSize, radius: c.logoRadius ?? 10, s: o.s, e: o.e });
    return N.group({ id: `${id}lg`, e: o.e, keys: [[o.s, 1], [o.e - EXIT(), 1, easeInOut], [o.e, 0]], children: [im] });
  }
  const COVER_CHIP = { logoSize: 64, size: 44, pad: "8px 22px 8px 8px", gap: 14, bg: "rgba(250,250,252,0.12)", border: "1px solid rgba(250,250,252,0.25)", radius: 20 };
  const CARD_CHIP = { logoSize: 72, size: 50, pad: "10px 24px 10px 10px", gap: 16, bg: "rgba(9,9,11,0.9)", border: "1px solid #2A2A2E", radius: 20, shadow: "0 14px 40px rgba(0,0,0,0.35)" };

  function BrandChip(p) {
    const c = { ...(p.variant === "card" ? CARD_CHIP : COVER_CHIP), logo: p.logo, label: p.label, x: p.x, y: p.y };
    const id = p.id ?? "chip";
    return N.frag([Frame({ ...p, id }, () => `<div style="${abs(c.x, c.y)}"><div style="${css(chipBox(c))}">${chipInner(c)}</div></div>`), ChipLogo(p, c, id)].filter(Boolean));
  }

  function Cover(p) {
    const id = p.id ?? "cover";
    const x = p.x ?? 56, y = p.y ?? 400, z1 = p.size ?? 110, z2 = p.size2 ?? 88;
    const c = p.chip ? { ...COVER_CHIP, logo: p.chip.logo, label: p.chip.label, x: 60, y: y - 110 } : null;
    const fr = Frame({ ...p, id }, () =>
      `<div style="position:absolute;left:0;top:${p.scrimTop ?? 222}px;width:928px;height:${p.scrimHeight ?? 403}px;background:linear-gradient(180deg, rgba(9,9,11,0) 0%, rgba(9,9,11,0.85) 14%, rgba(9,9,11,0.82) 55%, rgba(9,9,11,0) 100%);-webkit-mask-image:linear-gradient(90deg, #000 70%, transparent 100%);mask-image:linear-gradient(90deg, #000 70%, transparent 100%);"></div>`
      + (c ? `<div style="${abs(c.x, c.y, chipBox(c))}">${chipInner(c)}</div>` : "")
      + `<div style="${abs(x, y, { "font-size": `${z1}px`, "line-height": "1.02", "font-weight": 900, "letter-spacing": `${(-z1 * 4.5) / 110}px`, color: K.white, "white-space": "nowrap", "text-shadow": "0 4px 24px rgba(0,0,0,.5)" })}"><div>${Num(p.lines[0])}</div>`
      + (p.lines[1] ? `<div style="font-size:${z2}px;margin-top:14px;letter-spacing:${(-z2 * 3.5) / 88}px;">${Num(p.lines[1])}</div>` : "") + `</div>`);
    return N.frag([fr, c ? ChipLogo(p, c, id) : null].filter(Boolean));
  }

  function LowerThird(p) {
    const id = p.id ?? "lt";
    const c = p.chip ? { ...CARD_CHIP, logo: p.chip.logo, label: p.chip.label, x: p.chip.x, y: p.chip.y } : null;
    const fr = Frame({ ...p, id }, (t) => {
      const x = M.tw(t, p.s, 0.35, -80, 0, M.expoOut);
      return `<div style="${abs(p.x ?? 50, p.y ?? 240, { width: "740px", height: "230px", background: "rgba(9,9,11,0.9)", border: `1px solid ${K.line}`, "border-radius": "28px", transform: `translateX(${x}px)` })}">`
        + `<div style="${abs(40, 22, { "font-size": "104px", "line-height": "1.05", "font-weight": 800, "letter-spacing": "-3px", color: K.white })}">${esc(p.name)}</div>`
        + `<div style="${abs(42, 146, { "font-size": "48px", "line-height": "1.1", "font-weight": 700, "letter-spacing": "-0.8px", color: K.grey, "white-space": "nowrap", ...popO(t, p.s) })}">${esc(p.role)}</div></div>`
        + (c ? `<div style="${abs(c.x, c.y, { display: t >= p.s ? "block" : "none" })}"><div style="${css(chipBox(c))}">${chipInner(c)}</div></div>` : "");
    });
    return N.frag([fr, c ? ChipLogo(p, { ...c, x: c.x + 1, y: c.y + 1 }, id) : null].filter(Boolean));
  }

  function Headline(p) {
    const z = p.size ?? 128;
    return Frame(p, (t) => `<div style="${abs(p.x ?? 60, p.y ?? 250, { "font-size": `${z}px`, "line-height": "1.02", "font-weight": 800, "letter-spacing": `${p.tracking ?? -5}px`, color: p.color ?? K.white, ...popO(t, p.s) })}">${p.lines.map((l) => `<div>${esc(l)}</div>`).join("")}</div>`);
  }

  function CompareCards(p) {
    return Frame({ ...p, ground: p.ground ?? true }, (t) => {
      const fly = t < p.inAt ? 0 : M.tw(t, p.inAt, 0.4, 0, 1, M.expoOut);
      const slide = t < p.rightAt ? 0 : M.tw(t, p.rightAt, 0.35, 0, 1, M.expoOut);
      return `<div style="${abs(60, 240, { "font-size": "76px", "line-height": "1", "font-weight": 800, "letter-spacing": "-3px", color: K.white, ...popO(t, p.inAt) })}">${esc(p.title)}</div>`
        + `<div style="${abs(62, 330, { "font-size": "50px", "line-height": "1.05", "font-weight": 700, "letter-spacing": "-1.5px", color: K.grey, ...popO(t, p.subAt) })}">${esc(p.sub)}</div>`
        + `<div style="${abs(60, 440, { width: "400px", height: "480px", perspective: "1200px" })}"><div style="${css({ position: "absolute", inset: "0", background: K.cell, border: `2px solid ${K.line}`, "border-radius": "30px", opacity: t < p.inAt ? 0 : 1, transform: `translateX(${(1 - fly) * -260}px) rotateY(${(1 - fly) * 40}deg) scale(${0.85 + 0.15 * fly})` })}">`
        + `<svg width="160" height="160" style="${abs(120, 50)}"><circle cx="80" cy="80" r="78" fill="#2A2A2E"/><circle cx="80" cy="64" r="26" fill="${K.grey}"/><path d="M 34 132 Q 80 84 126 132" fill="${K.grey}"/></svg>`
        + `<div style="${abs(60, 250, { width: "280px", height: "26px", "border-radius": "13px", background: K.grey })}"></div>`
        + `<div style="${abs(90, 296, { width: "220px", height: "20px", "border-radius": "10px", background: "#3A3A3E" })}"></div>`
        + `<div style="${abs(50, 370, { background: "#FFFFFF", color: K.ink, "border-radius": "20px", padding: "8px 24px", "font-size": "50px", "font-weight": 800, "white-space": "nowrap", ...popO(t, p.leftAt, "center") })}">${esc(p.leftLabel)}</div></div></div>`
        + `<div style="${abs(500, 440, { width: "400px", height: "480px", border: `4px dashed ${K.grey}`, "border-radius": "30px", "box-sizing": "border-box", opacity: t < p.rightAt ? 0 : 1, transform: `translateX(${(1 - slide) * 300}px)` })}"><div style="${abs(0, 200, { width: "392px", "text-align": "center", "font-size": "56px", "font-weight": 800, "letter-spacing": "1px", color: K.white, ...popO(t, p.rightLabelAt, "center") })}">${esc(p.rightLabel)}</div></div>`;
    });
  }

  function BlockMeter(p) {
    const Nn = p.n ?? 7, D = p.dark ?? 3, BW = 110, BG = 10, X = 70, Y = 450, BH = 250;
    const bx = (i) => X + i * (BW + BG);
    const at = (i) => (i < D ? p.darkAt + i * 0.05 : p.lightAt + (i - D) * 0.05);
    return Frame({ ...p, ground: p.ground ?? true }, (t) => {
      const mpos = t < p.sweep[0] ? -1 : M.tw(t, p.sweep[0], p.sweep[1] - p.sweep[0], 0, Nn - 1, M.inOut);
      let out = `<div style="${abs(60, 240, { "font-size": "140px", "line-height": "1", "font-weight": 800, "letter-spacing": "-6px", color: K.white, ...popO(t, p.titleAt) })}">${esc(p.title)}</div>`;
      for (let i = 0; i < Nn; i++) {
        const f = t >= at(i);
        const bg = !f ? "transparent" : i < D ? "#2A2A2E" : K.white;
        const bd = !f ? K.line : i < D ? "#4A4A4F" : K.white;
        out += `<div style="${abs(bx(i), Y, { width: `${BW}px`, height: `${BH}px`, "border-radius": "18px", background: bg, border: `4px solid ${bd}`, "box-sizing": "border-box", opacity: t < p.gridAt ? 0 : 1, transform: `scale(${f ? M.tw(t, at(i), 0.2, 1.08, 1, M.backOut) : 1})` })}"></div>`;
      }
      out += `<div style="${abs(bx(0) + Math.max(0, mpos) * (BW + BG) + BW / 2 - 5, Y - 30, { width: "10px", height: `${BH + 60}px`, background: K.white, "border-radius": "5px", border: `3px solid ${K.bg}`, opacity: mpos < 0 ? 0 : 1 })}"></div>`;
      out += `<div style="${abs(bx(0), Y + BH + 24, { "font-size": "56px", "font-weight": 800, "letter-spacing": "-1px", color: K.grey, ...popO(t, p.leftLabelAt) })}">${esc(p.leftLabel)}</div>`;
      out += `<div style="${abs(bx(D) + 30, Y + BH + 24, { "font-size": "56px", "font-weight": 800, "letter-spacing": "-1px", color: K.white, ...popO(t, p.rightLabelAt) })}">${esc(p.rightLabel)}</div>`;
      return out;
    });
  }

  function EndCard(p) {
    return Frame(p, (t) => `<div style="${abs(p.x ?? 40, p.y ?? 250, { width: "880px", height: "250px", background: "rgba(9,9,11,0.92)", border: `1px solid ${K.line}`, "border-radius": "30px", ...popO(t, p.s, "center top") })}"><div style="${abs(40, 40, { "font-size": `${p.size ?? 84}px`, "line-height": "1", "font-weight": 800, "letter-spacing": "-3px", color: K.white, "white-space": "nowrap" })}">${esc(p.title)}</div></div>`);
  }

  function Arrow(p) {
    const w = p.width ?? 170, h = p.height ?? 90;
    return N.html({ id: p.id ?? "arrow", x: p.x, y: p.y, w, h, s: p.s, e: p.e, tpl: () => `<svg width="${w}" height="${h}" viewBox="0 0 170 90" style="filter:drop-shadow(0 6px 14px rgba(0,0,0,.5));${p.flip ? "transform:scaleX(-1);" : ""}"><path d="M 12 50 Q 70 30 140 40" fill="none" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round"/><path d="M 118 18 L 146 40 L 116 62" fill="none" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></svg>` });
  }

  IRM.kit = { KineticWord, Sticker, ChatPrompt, BarChart, TileGrid, CounterBar, OrbitCards, videoCard, phoneCard, statCard, imageCard, CameraPush, Vignette, ParallaxCard, Frame, PopSticker, StickerStack, BrandChip, Cover, LowerThird, Headline, CompareCards, BlockMeter, EndCard, Arrow, Num, K };
})();
