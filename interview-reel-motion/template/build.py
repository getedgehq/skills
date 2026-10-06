#!/usr/bin/env python3
"""Build the HyperFrames project for an interview reel from reel.json, beats.json and captions.json.

  python3 build.py --data examples/proof --assets assets [--qa gfx|foot] [--out .] [--reuse]

What it does (all pre-passes; the render itself is `npx hyperframes render` or `hyperframes lambda render`):
  1. cuts the clips into pieces (same rule as the engine) and lists the source frame every output frame shows
  2. extracts exactly those frames as JPEG stacks (stacks/<key>/<n>.jpe) with ffmpeg; the page swaps them
     per frame, so the render never depends on <video> seeking (HyperFrames Lambda does not wait for seeks)
  3. mixes the audio (voice cut list with dB gain keys, music bed with dB keys and fade out, sfx) into
     assets/mix.wav with ffmpeg + numpy, and places it as one <audio> at the composition root
  4. writes index.html: the data inline, the stacks, the runtime scripts, fonts
The speed ramp stays a pre-rendered clip (tools/ramp.py); the matte and face boxes are pre-pass scripts too.
"""
import argparse, json, math, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FPS = 30
FFMPEG = os.environ.get("IRM_FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("IRM_FFPROBE", "ffprobe")
SR = 48000
# Frame stacks use the .jpe extension on purpose: the HyperFrames bundler inlines every .jpg/.png under 2 MB
# as a base64 data URL, which for a thousand frames overflows the bundle string. .jpe stays a served file.
EXT = "jpe"
# voice/music playbackRate: "shift" resamples (pitch follows the rate, as the Compound engine and r15 do);
# "keep" time-stretches with atempo
PITCH = os.environ.get("IRM_PITCH", "shift")


def load(d):
    d = Path(d)
    return (json.loads((d / n).read_text()) for n in ("reel.json", "beats.json", "captions.json"))


def pieces(r):
    out = []
    in_blank = lambda t: any(a - 1e-6 <= t < b - 1e-6 for a, b in r["blank"])
    for ci, c in enumerate(r["clips"]):
        cuts = sorted([c["start"], *[b for b in r["splits"] if c["start"] + 1e-6 < b < c["end"] - 1e-6], c["end"]])
        for i in range(len(cuts) - 1):
            a, b = cuts[i], cuts[i + 1]
            if in_blank(a):
                continue
            out.append(dict(start=a, end=b, sin=c["sin"] + (a - c["start"]) * c["rate"], rate=c["rate"], src=c.get("src", r["footage"]), key=f"v{ci}_{i}"))
    return out


def probe(path):
    j = json.loads(subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:stream_side_data=rotation", "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout)
    s = j["streams"][0]
    w, h = s["width"], s["height"]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = s["r_frame_rate"].split("/")
    return w, h, float(num) / float(den)


def frame_lists(r, P, n_frames, assets):
    """source frames each output frame needs, per source file"""
    need, meta = {}, {}
    ph = float(r.get("framePhase", 1e-3))  # added before flooring; must match runtime/engine.js
    for p in P:
        src = p["src"]
        if src not in meta:
            w, h, fps = probe(assets / src)
            meta[src] = dict(key=f"s{len(meta)}", w=w, h=h, fps=fps)
        fps = meta[src]["fps"]
        for f in range(n_frames):
            t = f / FPS
            if p["start"] - 1e-6 <= t < p["end"] - 1e-6:
                need.setdefault(src, set()).add(math.floor((p["sin"] + (t - p["start"]) * p["rate"]) * fps + ph))
    for src, s in need.items():
        meta[src]["first"], meta[src]["last"] = min(s), max(s)
    return need, meta


def extract(src_path, frames, outdir, w, h, quality):
    """decode the source once up to the last needed frame and keep only the needed ones (exact frame index)"""
    import numpy as np
    from PIL import Image
    outdir.mkdir(parents=True, exist_ok=True)
    todo = sorted(f for f in frames if not (outdir / f"{f}.{EXT}").exists())
    if not todo:
        return 0
    last = todo[-1]
    cmd = [FFMPEG, "-nostdin", "-v", "error", "-i", str(src_path), "-frames:v", str(last + 1), "-vsync", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    want, n, size = set(todo), 0, w * h * 3
    while n <= last:
        buf = pr.stdout.read(size)
        if len(buf) < size:
            break
        if n in want:
            Image.fromarray(np.frombuffer(buf, np.uint8).reshape(h, w, 3)).save(outdir / f"{n}.{EXT}", format="JPEG", quality=quality, subsampling=0)
        n += 1
    pr.stdout.close(); pr.wait()
    missing = [f for f in todo if not (outdir / f"{f}.{EXT}").exists()]
    if missing:
        sys.exit(f"stack {outdir}: {len(missing)} frames missing (source shorter than the cut list?)")
    return len(todo)


# ------------------------------------------------------------------ audio
def decode(path, rate=1.0):
    """decode to float32 stereo at SR so that one output second covers `rate` source seconds.
    PITCH=shift (default): plain resample, pitch follows the rate (matches the Compound engine's mix);
    PITCH=keep: time-stretch with atempo."""
    import numpy as np
    if rate == 1 or PITCH == "shift":
        sr_in = int(round(SR / rate))
        af = []
    else:
        sr_in = SR
        af = ["-af", f"atempo={rate}"]
    raw = subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-i", str(path), "-vn", *af, "-ac", "2", "-ar", str(sr_in), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def db_track(keys, tt):
    """dB keyframes [[time, dB], ...] linearly interpolated, held before the first and after the last key"""
    import numpy as np
    ks = sorted(keys)
    return np.interp(tt, [k[0] for k in ks], [k[1] for k in ks])


def mix_audio(r, assets, out_wav, dur):
    import numpy as np
    n = int(round(dur * SR))
    mix = np.zeros((n, 2), np.float32)
    cache = {}

    def src(path, rate):
        k = (path, rate)
        if k not in cache:
            cache[k] = decode(assets / path, rate)
        return cache[k]

    def place(buf, start, gain):
        a = int(round(start * SR))
        b = min(n, a + len(buf))
        if b > a:
            mix[a:b] += buf[: b - a] * gain[: b - a, None]

    a = r["audio"]
    for v in a["voice"]:
        rate = v.get("rate", 1)
        x = src(v.get("src", r["footage"]), rate)  # sample i of x is source time i * rate / SR
        i0, i1 = int(round(v["sin"] * SR / rate)), int(round(v["sout"] * SR / rate))
        seg = x[i0:i1]
        tsrc = v["sin"] + np.arange(len(seg)) * rate / SR
        g = 10 ** (db_track(v["gain"], tsrc) / 20) if v.get("gain") else np.ones(len(seg))
        place(seg, v["start"], g.astype(np.float32))
    m = a.get("music")
    if m:
        rate = m.get("rate", 1)
        x = src(m["src"], rate)
        seg = x[: n]
        tsrc = np.arange(len(seg)) / SR * rate  # music keys are in source seconds: t_src = t_scene * rate
        db = db_track(m["keys"], tsrc) if m.get("keys") else np.full(len(seg), m.get("volume", 0))
        g = 10 ** (db / 20)
        fo = m.get("fadeOut", 0.7)
        tt = np.arange(len(seg)) / SR
        g = g * np.clip((dur - tt) / fo, 0, 1) if fo else g
        place(seg, 0, g.astype(np.float32))
    for t0, path, sin, sout, db in a.get("sfx", []):
        x = src(path, 1)
        seg = x[int(round(sin * SR)): int(round(sout * SR))]
        place(seg, t0, np.full(len(seg), 10 ** (db / 20), np.float32))
    pk = float(np.abs(mix).max()) if n else 0  # reported; samples over full scale are clipped like the editor's mix
    pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes()
    import wave
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)
    return pk


# ------------------------------------------------------------------ page
SCRIPTS = ["clock.js", "rules.js", "nodes.js", "kit.js", "engine.js"]
THREE_COMPONENTS = {"TypeRing", "ParticleText", "Takeover"}


def page(r, beats, caps, stacks_meta, need, qa, title, matte=None):
    dur = r["scene"]["duration"]
    data = dict(reel=r, beats=beats, captions=caps, qa=qa, stacks={src: {**{k: m[k] for k in ("key", "w", "h", "fps", "first", "last")}, "frames": sorted(need[src])} for src, m in stacks_meta.items() if src in need}, ext=EXT, matte=matte or {})
    # Inter 4 (variable wght + opsz, OFL), subset to Latin plus the few symbols the kit sets (check mark, play, arrows)
    faces = '@font-face{font-family:"Inter";font-style:normal;font-weight:100 900;font-display:block;src:url("fonts/InterVariable.woff2") format("woff2");}'
    uses_three = any(b["component"] in THREE_COMPONENTS for b in beats)
    three = ""
    if uses_three:
        three = ('<script type="importmap">{"imports":{"three":"./vendor/three.module.min.js","three/addons/":"./vendor/"}}</script>\n'
                 '<script type="module" src="runtime/three-kit.js"></script>')
    # the classic runtime is inlined: the distributed (Lambda) compiler did not execute one of the external
    # classic scripts in testing, and inline code runs identically in preview, local render and Lambda
    def inline(name):
        code = (HERE / "runtime" / name).read_text()
        assert "</script" not in code.lower()
        return f"<script>\n/* runtime/{name} */\n{code}\n</script>"
    scripts = "\n".join(inline(s) for s in SCRIPTS)
    W, H = r["scene"]["width"], r["scene"]["height"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<style>
{faces}
*{{box-sizing:border-box}} html,body{{margin:0;padding:0;background:#09090B;overflow:hidden}}
#reel{{position:relative;width:{W}px;height:{H}px;overflow:hidden;font-family:Inter,sans-serif;color:#FAFAFC}}
#reel-layers{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;overflow:hidden}}
.irm-html, .irm-html *{{font-family:Inter,sans-serif}}
</style></head><body>
<div id="reel" data-composition-id="reel" data-start="0" data-width="{W}" data-height="{H}" data-duration="{dur:.6f}" data-fps="{FPS}" data-no-timeline>
<audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{dur:.6f}" data-track-index="10" data-volume="1"></audio>
<div id="reel-layers"></div>

</div>
<script>window.IRM_DATA = {json.dumps(data, separators=(",", ":"))};</script>
{scripts}
{three}
</body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="folder with reel.json, beats.json, captions.json")
    ap.add_argument("--assets", default="assets", help="asset root the json paths are relative to")
    ap.add_argument("--out", default=".", help="HyperFrames project dir (gets index.html, stacks/, assets/)")
    ap.add_argument("--qa", default="", choices=["", "gfx", "foot"], help="gfx: graphics on magenta, no footage; foot: footage only")
    ap.add_argument("--quality", type=int, default=92, help="JPEG quality of the frame stacks")
    ap.add_argument("--reuse", action="store_true", help="keep existing stacks and mix")
    ap.add_argument("--matte", default=None, help="folder of RGBA person-matte PNGs from scripts/matte_rvm.py, as <stack key>/<frame>.png")
    a = ap.parse_args()
    r, beats, caps = load(a.data)
    assets, out = Path(a.assets).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    dur = r["scene"]["duration"]
    n_frames = int(round(dur * FPS))
    P = pieces(r)
    need, meta = frame_lists(r, P, n_frames, assets)
    total = 0
    for src, s in need.items():
        total += extract(assets / src, s, out / "stacks" / meta[src]["key"], meta[src]["w"], meta[src]["h"], a.quality)
    print(f"stacks: {sum(len(s) for s in need.values())} frames ({total} new) from {len(need)} sources")
    (out / "assets").mkdir(exist_ok=True)
    if not (a.reuse and (out / "assets/mix.wav").exists()):
        pk = mix_audio(r, assets, out / "assets/mix.wav", dur)
        print(f"mix: assets/mix.wav peak {pk:.3f}")
    # logos and stills referenced by beats are plain <img>: copy them next to the page
    for b in beats:
        p = b.get("props", {}) or {}
        refs = [p.get("src"), (p.get("chip") or {}).get("logo"), p.get("logo")] + [c.get("src") for c in p.get("cards", []) if isinstance(c, dict)]
        for ref in filter(None, refs):
            dst = out / "assets" / ref
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                shutil.copyfile(assets / ref, dst)
    for d in ("runtime", "vendor", "fonts"):
        if (HERE / d).resolve() != (out / d).resolve():
            shutil.copytree(HERE / d, out / d, dirs_exist_ok=True)
    matte = {}
    if a.matte:
        # .apng (a static PNG is a valid APNG) keeps the bundler from inlining hundreds of PNGs as data URLs
        for src, s in need.items():
            k = meta[src]["key"]
            for f in sorted(s):
                png = Path(a.matte) / k / f"{f}.png"
                if png.exists():
                    dst = out / "stacks" / "matte" / k / f"{f}.apng"
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(png, dst)
                    matte.setdefault(k, []).append(f)
        print(f"matte: {sum(len(v) for v in matte.values())} frames")
    (out / "index.html").write_text(page(r, beats, caps, meta, need, a.qa, r.get("name", "reel"), matte))
    print(f"index.html: {n_frames} frames, {dur:.3f} s, qa={a.qa or 'final'}")


if __name__ == "__main__":
    main()
