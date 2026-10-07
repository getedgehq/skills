/* Tracked deck links: runs inside the deck frame (injected by the server, never part of the deck file).
 * Reads its config from the shell page (window.parent.DECK_TRACK). Without it, it does nothing, and
 * every failure is swallowed: tracking must never break the deck.
 *
 * Slides:  Reveal.js decks use Reveal's events. Any other deck: elements matching [data-slide],
 *          section.slide, .slide, or top-level <section>s, first non-empty wins; the slide with the most
 *          visible area is the current one. No slide markup: the whole page is one slide "page".
 * Title:   data-title, else the first h1/h2/h3, else empty.
 * Active time (Falco's rule): a second counts only when the tab is visible, the window has focus and
 *          there was input or a slide change in the last 60 s. Counted per slide and in total; sent every
 *          10 s, on hide and on close. Counters survive a reload in the same tab; the server only raises values.
 */
(function () {
  try {
    var cfg = null;
    try { cfg = window.parent !== window ? window.parent.DECK_TRACK : null; } catch (e) {}
    if (!cfg || !cfg.viewId || !cfg.sessionId) return;
    var IDLE_MS = 60000, SEND_MS = 10000;
    var memoKey = 'decklinks-progress-' + cfg.token;
    var state = { seconds: 0, slides: {}, interacted: false, maxIndex: 0 };
    try {
      var saved = JSON.parse(sessionStorage.getItem(memoKey) || 'null');
      if (saved && typeof saved === 'object') state = { seconds: saved.seconds || 0, slides: saved.slides || {}, interacted: !!saved.interacted, maxIndex: saved.maxIndex || 0 };
    } catch (e) {}
    function remember() { try { sessionStorage.setItem(memoKey, JSON.stringify(state)); } catch (e) {} }

    var reveal = window.Reveal && typeof window.Reveal.on === 'function' ? window.Reveal : null;
    var els = [];
    if (reveal) {
      els = Array.prototype.slice.call(document.querySelectorAll('.reveal .slides > section'));
    } else {
      var sels = ['[data-slide]', 'section.slide', '.slide', 'body > section', 'main > section'];
      for (var k = 0; k < sels.length && !els.length; k++) els = Array.prototype.slice.call(document.querySelectorAll(sels[k]));
    }
    function slideKey(el, idx) {
      var id = el && (el.getAttribute('data-slide-id') || el.id);
      return id && /^[A-Za-z0-9_-]{1,64}$/.test(id) ? id : (els.length ? 'slide-' + (idx + 1) : 'page');
    }
    function titleOf(el) {
      if (!el) return document.title || '';
      var t = el.getAttribute('data-title');
      if (!t) { var h = el.querySelector('h1,h2,h3'); t = h ? h.textContent : ''; }
      return String(t || '').replace(/\s+/g, ' ').trim().slice(0, 200);
    }
    var outline = els.length ? els.map(function (el, i) { return { i: i, id: slideKey(el, i), title: titleOf(el) }; })
      : [{ i: 0, id: 'page', title: titleOf(null) }];

    var cur = null, lastActive = Date.now();
    function enter(idx) {
      var key = outline[idx] ? outline[idx].id : 'page';
      if (key === cur) return;
      var s = state.slides[key] || (state.slides[key] = { s: 0, v: 0, i: idx });
      s.v += 1; s.i = idx; cur = key;
      if (idx > state.maxIndex) state.maxIndex = idx;
      lastActive = Date.now();
      remember();
    }
    function mostVisible() {
      var best = 0, bestArea = -1, vh = window.innerHeight, vw = window.innerWidth;
      for (var i = 0; i < els.length; i++) {
        var r = els[i].getBoundingClientRect();
        var h = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
        var w = Math.max(0, Math.min(r.right, vw) - Math.max(r.left, 0));
        if (h * w > bestArea) { bestArea = h * w; best = i; }
      }
      return best;
    }
    function act() { state.interacted = true; lastActive = Date.now(); }
    function topHasFocus() { try { return window.parent.document.hasFocus(); } catch (e) { return document.hasFocus(); } }

    var ax = -1, ay = -1, lastTop = window.scrollY || 0;
    window.addEventListener('pointermove', function (e) {
      if (ax < 0 || Math.abs(e.clientX - ax) + Math.abs(e.clientY - ay) >= 24) { ax = e.clientX; ay = e.clientY; act(); }
    }, { passive: true });
    ['keydown', 'pointerdown', 'touchstart', 'wheel'].forEach(function (t) { window.addEventListener(t, act, { passive: true }); });
    document.addEventListener('scroll', function () {
      var y = window.scrollY || 0;
      if (Math.abs(y - lastTop) >= 40) { lastTop = y; act(); }
      if (!reveal && els.length) enter(mostVisible());
    }, { passive: true, capture: true });

    setInterval(function () {
      if (!reveal && els.length) enter(mostVisible());
      if (cur && document.visibilityState === 'visible' && topHasFocus() && Date.now() - lastActive < IDLE_MS) {
        state.seconds += 1;
        state.slides[cur].s += 1;
        remember();
      }
    }, 1000);

    var lastSent = '', lastSentAt = 0, outlineSent = false;
    function send(final) {
      var payload = { viewId: cfg.viewId, sessionId: cfg.sessionId, seconds: state.seconds, slides: state.slides,
        maxIndex: state.maxIndex, interacted: state.interacted, final: !!final };
      var fp = JSON.stringify(payload).replace(/"final":(true|false)/, '');
      var keepalive = document.visibilityState === 'visible' && Date.now() - lastSentAt > 30000;
      if (!final && outlineSent && fp === lastSent && !keepalive) return;
      if (!outlineSent) { payload.deck = outline; outlineSent = true; }
      lastSent = fp; lastSentAt = Date.now();
      var body = JSON.stringify(payload), url = cfg.api + '/beat', ok = false;
      try { ok = navigator.sendBeacon && navigator.sendBeacon(url, new Blob([body], { type: 'application/json' })); } catch (e) {}
      if (!ok) { try { fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: body, keepalive: true }).catch(function () {}); } catch (e) {} }
    }

    function start() {
      if (reveal) {
        enter(reveal.getIndices().h || 0);
        reveal.on('slidechanged', function () { send(); enter(reveal.getIndices().h || 0); });
      } else {
        enter(els.length ? mostVisible() : 0);
      }
      send();
      setInterval(function () { send(); }, SEND_MS);
      document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') send(true); });
      window.addEventListener('pagehide', function () { send(true); });
    }
    if (!reveal || (reveal.isReady && reveal.isReady())) start(); else reveal.on('ready', start);
  } catch (e) { /* never break the deck */ }
})();
