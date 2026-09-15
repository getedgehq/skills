// Scroll-scrubbed background video. No dependencies.
//
// Markup:
//   <video id="bg" muted playsinline preload="auto"
//          data-desktop="hero-desktop.mp4" data-mobile="hero-mobile.mp4"
//          data-poster-desktop="poster.jpg" data-poster-mobile="poster-mobile.jpg"></video>
// CSS:
//   #bg { position: fixed; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -1; }
//   body.video-ready .needs-video { opacity: 1; }

(function () {
  const video = document.getElementById("bg");
  if (!video) return;

  const mobile = window.matchMedia("(max-width: 768px)").matches;
  video.poster = video.dataset[mobile ? "posterMobile" : "posterDesktop"];

  // Reduced motion: poster only, no scrub.
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.body.classList.add("video-ready");
    return;
  }

  video.src = video.dataset[mobile ? "mobile" : "desktop"];
  video.muted = true;
  video.playsInline = true;

  const EASE = 0.12;       // fraction of the remaining distance covered per frame
  const EPSILON = 1 / 60;  // seconds; below this the scrub is settled
  let target = 0;
  let current = 0;
  let running = false;

  function progress() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    return max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
  }

  function tick() {
    if (!video.duration) { running = false; return; }
    target = progress() * (video.duration - 0.05);
    const delta = target - current;
    if (Math.abs(delta) < EPSILON) { running = false; return; }
    current += delta * EASE;
    // Never queue seeks: skip this frame while the last one is still decoding.
    if (!video.seeking) video.currentTime = current;
    requestAnimationFrame(tick);
  }

  function wake() {
    if (!running) { running = true; requestAnimationFrame(tick); }
  }

  // iOS Safari may not paint seeks until the element has played once.
  let primed = false;
  function prime() {
    if (primed) return;
    primed = true;
    const p = video.play();
    if (p && p.then) p.then(() => video.pause()).catch(() => {});
  }

  function ready() {
    document.body.classList.add("video-ready");
    wake();
  }

  video.addEventListener("loadedmetadata", wake);
  video.addEventListener("canplay", ready, { once: true });
  setTimeout(() => document.body.classList.add("video-ready"), 2500);

  window.addEventListener("scroll", () => { prime(); wake(); }, { passive: true });
  window.addEventListener("touchstart", prime, { passive: true, once: true });
  window.addEventListener("resize", wake);
})();
