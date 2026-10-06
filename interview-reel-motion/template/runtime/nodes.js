// nodes.js: the few scene primitives the kit is built from, as plain DOM.
// Each node is { el, update(t) }: update sets every style from t alone (no state carried between seeks).
//   html   a W x H box at x, y, live on [s, e), whose inner HTML is a pure function of t
//   group  children under one opacity keyframe track (times in scene seconds, ease applied out of a key)
//   rect, img, text   static shapes live on [s, e)
(function () {
  const IRM = (window.IRM = window.IRM || {});
  const EPS = 1e-6;
  const live = (t, s, e) => t >= s - EPS && t < e - EPS;
  const mk = (style, tag = "div") => { const el = document.createElement(tag); el.setAttribute("style", style); return el; };
  const abspx = (x, y, w, h) => `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;`;

  function html(o) {
    // o: { id, x, y, w, h, s, e, tpl(t) -> string, clip }
    const el = mk(abspx(o.x, o.y, o.w, o.h) + (o.clip === false ? "" : "overflow:hidden;") + "display:none;");
    if (o.id) el.id = o.id;
    el.className = "irm-html";
    let last = null;
    return {
      el,
      update(t) {
        const on = live(t, o.s, o.e);
        el.style.display = on ? "block" : "none";
        if (!on) return;
        const h = o.tpl(t);
        if (h !== last) { el.innerHTML = h; last = h; }
      },
    };
  }
  function group(o) {
    // o: { id, e, keys: [[t, v, ease?]], children: node[] }
    const el = mk("position:absolute;left:0;top:0;width:1080px;height:1920px;display:none;");
    if (o.id) el.id = o.id;
    o.children.forEach((c) => el.appendChild(c.el));
    return {
      el,
      update(t) {
        const on = t < o.e - EPS;
        el.style.display = on ? "block" : "none";
        if (!on) return;
        el.style.opacity = (o.keys && o.keys.length ? IRM.kfTrack(o.keys, t) : 1).toFixed(4);
        o.children.forEach((c) => c.update(t));
      },
    };
  }
  function rect(o) {
    const el = mk(abspx(o.x, o.y, o.w, o.h) + `border-radius:${o.radius || 0}px;background:${o.fill};display:none;`);
    if (o.id) el.id = o.id;
    return { el, update(t) { const on = live(t, o.s, o.e); el.style.display = on ? "block" : "none"; if (on && o.keys) el.style.opacity = IRM.kfTrack(o.keys, t - o.s).toFixed(4); } };
  }
  function img(o) {
    const el = mk(abspx(o.x, o.y, o.w, o.h) + `border-radius:${o.radius || 0}px;object-fit:${o.fit || "cover"};display:none;`, "img");
    el.src = o.src; el.alt = ""; el.decoding = "sync";
    if (o.id) el.id = o.id;
    return { el, update(t) { const on = live(t, o.s, o.e); el.style.display = on ? "block" : "none"; } };
  }
  function text(o) {
    // native text line: box at x, y (top-left), text vertically centred; align left by default
    const sh = o.shadow ? `text-shadow:0 ${o.shadow.offsetY}px ${o.shadow.blur}px rgba(0,0,0,${o.shadow.opacity});` : "";
    const el = mk(abspx(o.x, o.y, o.w, o.h) + `display:none;align-items:center;justify-content:${o.align === "center" ? "center" : "flex-start"};text-align:${o.align || "left"};white-space:nowrap;font-family:${o.font || "Inter"};font-weight:${o.weight};font-size:${o.size}px;letter-spacing:${o.tracking}px;color:${o.color};line-height:1;${sh}`);
    el.textContent = o.text;
    if (o.id) el.id = o.id;
    return { el, update(t) { el.style.display = live(t, o.s, o.e) ? "flex" : "none"; } };
  }
  /** a node made of several nodes in paint order */
  function frag(nodes) {
    const el = mk("position:absolute;left:0;top:0;width:1080px;height:1920px;");
    nodes.forEach((n) => el.appendChild(n.el));
    return { el, update(t) { nodes.forEach((n) => n.update(t)); } };
  }
  IRM.nodes = { html, group, rect, img, text, frag, live, mk, abspx };
})();
