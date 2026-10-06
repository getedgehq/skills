// The house rules as defaults. Components and the QA scripts read these numbers; change them here only.
export const FPS = 30;
export const W = 1080, H = 1920;
/** frame 0 is the cover: everything important sits inside the 3:4 grid crop (feed grids crop 9:16 to 3:4) */
export const COVER_SAFE = { y0: 260, y1: 1660 };
/** during playback no graphic in the top 220, bottom 420 or right 150 px (platform UI) */
export const SAFE = { top: 220, bottom: 420, right: 150 };
export const SAFE_BOX = { x0: 0, y0: SAFE.top, x1: W - SAFE.right, y1: H - SAFE.bottom };
/** graphics never leave in one frame: an eased exit of 6 to 8 frames (7 by default) */
export const EXIT_FRAMES = 7;
/** captions are whole phrases of 2 to 5 words; never split across speakers or idioms */
export const CAPTION_WORDS = { min: 2, max: 5 };
/** a text element must be complete on screen for at least max(0.7 s, 0.25 s per word), or it is dropped */
export const minShow = (words: number) => Math.max(0.7, 0.25 * words);
/** a caption stays up until its phrase ends plus this much where room allows */
export const CAPTION_TAIL = 0.2;
/** the end: hold a good frame with a slow eased push, then fade to black over this many frames (10 to 15) */
export const END_FADE_FRAMES = 12;
/** frame snapping */
export const snap = (t: number) => Math.round(t * FPS) / FPS;
export const f = (n: number) => n / FPS;
