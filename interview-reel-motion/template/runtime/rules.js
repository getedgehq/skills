// rules.js: the house rules as defaults. Components, the engine and the QA scripts read these numbers;
// change them here only. Same values as the Compound engine's rules.ts.
(function () {
  const IRM = (window.IRM = window.IRM || {});
  const FPS = 30;
  const W = 1080, H = 1920;
  const SAFE = { top: 220, bottom: 420, right: 150 };
  IRM.rules = {
    FPS, W, H,
    /** frame 0 is the cover: everything important sits inside the 3:4 grid crop */
    COVER_SAFE: { y0: 260, y1: 1660 },
    /** during playback no graphic in the top 220, bottom 420 or right 150 px (platform UI) */
    SAFE,
    SAFE_BOX: { x0: 0, y0: SAFE.top, x1: W - SAFE.right, y1: H - SAFE.bottom },
    /** graphics never leave in one frame: an eased exit of 6 to 8 frames (7 by default) */
    EXIT_FRAMES: 7,
    /** captions are whole phrases of 2 to 5 words; never split across speakers or idioms */
    CAPTION_WORDS: { min: 2, max: 5 },
    /** a text element must be complete on screen for at least max(0.7 s, 0.25 s per word), or it is dropped */
    minShow: (words) => Math.max(0.7, 0.25 * words),
    CAPTION_TAIL: 0.2,
    /** the end: hold a good frame with a slow eased push, then fade to black over this many frames (10 to 15) */
    END_FADE_FRAMES: 12,
    snap: (t) => Math.round(t * FPS) / FPS,
    f: (n) => n / FPS,
  };
})();
