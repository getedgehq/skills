#!/usr/bin/env python3
"""Build one reel from a source clip: 9:16 base (optional grade), wind high-pass +
-14 LUFS audio, verbatim captions (short chunks, filler trimmed, no periods,
drop-shadow only), a bold top-center hook, global speed-up (default 1.1x),
inserts (stat cards, closer), Instagram-ready HQ export. Derived from video-use (MIT, see THIRD_PARTY_NOTICES.md).

Fonts: HOOK_FONT (variable font, Bold instance used), CAPTION_FONT + CAPTION_FONT_INDEX.

Cut model:
  SEGMENTS = JSON list of {"start","end"} in ORIGINAL seconds -> the KEPT parts,
             concatenated with clean audio splices. If unset, uses START/END.
Inserts (b-roll), times in ORIGINAL seconds, mapped onto the cut timeline:
  INSERTS  = JSON list of {"image","start","end","pos"?,"w"?}
             pos = "center" (default) | "topright"; w = width px.
  (legacy single insert: INSERT / INSERT_START / INSERT_END)

Other env: SRC TRANSCRIPT HOOK OUT HOOK_SIZE HOOK_Y HOOK_MARGIN
  LOGO_INLINE LOGO_INLINE_SCALE LOGO_INLINE_DY LOGO_INLINE_GAP
  LOGO LOGO_W LOGO_Y  END_FADE
"""
import json, os, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = os.environ["SRC"]
TRANSCRIPT = os.environ["TRANSCRIPT"]
HOOK = os.environ["HOOK"]
OUT = os.environ["OUT"]
HOOK_SIZE = int(os.environ.get("HOOK_SIZE", "112"))
HOOK_MARGIN = int(os.environ.get("HOOK_MARGIN", "130"))
LOGO_INLINE = os.environ.get("LOGO_INLINE", "")
LOGO_INLINE_SCALE = float(os.environ.get("LOGO_INLINE_SCALE", "1.05"))
LOGO_INLINE_DY = int(os.environ.get("LOGO_INLINE_DY", "0"))
LOGO_INLINE_GAP = float(os.environ.get("LOGO_INLINE_GAP", "0.16"))
LOGO = os.environ.get("LOGO", "")
LOGO_W = int(os.environ.get("LOGO_W", "380"))
LOGO_Y = int(os.environ.get("LOGO_Y", "560"))
# Optional small persistent corner logo (e.g. bottom-left, above the IG name/UI).
CORNER_LOGO = os.environ.get("CORNER_LOGO", "")
CORNER_LOGO_W = int(os.environ.get("CORNER_LOGO_W", "95"))
CORNER_X = os.environ.get("CORNER_X", "48")
CORNER_Y = os.environ.get("CORNER_Y", "1460")
END_FADE = float(os.environ.get("END_FADE", "0"))
# Freeze-frame hold at the very end (seconds, after speed): clones the last
# composited frame + pads silence, so the reel gets a beat to land instead of
# cutting on the final word.
END_HOLD = float(os.environ.get("END_HOLD", "0"))
# Optional subtle grade applied to the base (before overlays). Off by default.
GRADE = os.environ.get("GRADE", "")
SPEED = float(os.environ.get("SPEED", "1.1"))
# headline on-screen time (EDITED seconds, before speed; 5 -> ~4.5s at 1.1x)
HOOK_DUR = float(os.environ.get("HOOK_DUR", "5"))
W, H = 1080, 1920

# --- kept segments (original seconds) ---
if os.environ.get("SEGMENTS"):
    SEGS = [(float(s["start"]), float(s["end"])) for s in json.loads(os.environ["SEGMENTS"])]
else:
    SEGS = [(float(os.environ["START"]), float(os.environ["END"]))]
SEGS = sorted(SEGS, key=lambda s: s[0])
DUR = sum(e - s for s, e in SEGS)  # edited duration (before speed)


def to_edited(t):
    """Map an ORIGINAL time to the concatenated/cut timeline."""
    cum = 0.0
    for s, e in SEGS:
        if t < s:
            return cum
        if t <= e:
            return cum + (t - s)
        cum += e - s
    return cum


# outputs land under REEL_ROOT (default: current dir, i.e. the video-use repo root)
ROOT = Path(os.environ.get("REEL_ROOT", "."))
WORK = ROOT / "data/edit/reels" / OUT
CAPS = WORK / "caps"
CAPS.mkdir(parents=True, exist_ok=True)
(ROOT / "data/final").mkdir(parents=True, exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"cmd failed: {' '.join(str(c) for c in cmd[:6])}...\n{r.stderr[-1800:]}")


# 1) base 9:16: trim each kept segment, scale/crop, concat, optional grade.
vparts = [f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,"
          f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v{i}]"
          for i, (s, e) in enumerate(SEGS)]
cc = "vcc" if GRADE else "vout"
vfilters = vparts + ["".join(f"[v{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=0[{cc}]"]
if GRADE:
    vfilters.append(f"[vcc]{GRADE}[vout]")
base = WORK / "base.mp4"
run(["ffmpeg", "-y", "-i", SRC, "-filter_complex", ";".join(vfilters),
     "-map", "[vout]", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-an", str(base)])

# 2) audio: trim each segment with a 12ms edge fade (kills splice clicks), concat,
#    then wind high-pass + loudnorm -14 LUFS over the whole.
aparts = []
for i, (s, e) in enumerate(SEGS):
    d = e - s
    aparts.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:st=0:d=0.012,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[a{i}]")
acat = "".join(f"[a{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=0:a=1[ac]"
# optional de-breath: gate quiet inter-word breaths + light FFT denoise
afl = ["highpass=f=100:poles=2", "highpass=f=100:poles=2"]
if os.environ.get("DEBREATH"):
    afl += ["agate=threshold=0.05:range=0.3:ratio=2:attack=8:release=180", "afftdn=nr=10:nf=-30"]
afl.append("loudnorm=I=-14:TP=-1:LRA=11")
apost = "[ac]" + ",".join(afl) + "[aout]"
audio = WORK / "audio.wav"
if os.environ.get("AUDIO_OVERRIDE"):
    audio = Path(os.environ["AUDIO_OVERRIDE"])  # use a pre-cleaned/isolated track as-is
else:
    run(["ffmpeg", "-y", "-i", SRC, "-filter_complex", ";".join(aparts + [acat, apost]),
         "-map", "[aout]", "-ac", "2", "-ar", "48000", str(audio)])

# 3) captions: kept words only, times mapped to the cut timeline; break on
#    sentence end / pause / 3-word cap / segment boundary.
FILLER = {"ähm", "äh", "ähm,", "äh,", "em", "uh", "um", "uh,", "um,", "hm", "ähmm"}
allw = [w for w in json.load(open(TRANSCRIPT)).get("words", []) if w.get("type") == "word"]


def seg_of(t):
    for idx, (s, e) in enumerate(SEGS):
        if s - 0.001 <= t < e:
            return idx
    return None


capwords = []
for w in allw:
    si = seg_of(w["start"])
    if si is None:
        continue
    raw = w["text"].strip()
    if raw.lower() in FILLER:
        continue
    capwords.append((raw, to_edited(w["start"]), to_edited(min(w["end"], SEGS[si][1])), si))

caps, cur = [], []


def flush():
    global cur
    if not cur:
        return
    text = re.sub(r"\s+", " ", " ".join(t for t, _, _, _ in cur).replace(".", "").strip())
    if text:
        caps.append({"text": text, "start": round(cur[0][1], 2), "end": round(cur[-1][2], 2)})
    cur = []


for i, (raw, es, ee, si) in enumerate(capwords):
    cur.append((raw, es, ee, si))
    nxt = capwords[i + 1] if i + 1 < len(capwords) else None
    gap = (nxt[1] - ee) if nxt else 999
    seg_break = (nxt is None) or (nxt[3] != si)
    if raw.endswith((".", "!", "?")) or gap > 0.35 or len(cur) >= 3 or seg_break:
        flush()
flush()

# Curated caption override: JSON list of {text,start,end} in EDITED seconds
# (cleaned text + parentheticals). Replaces the auto-generated captions.
if os.environ.get("CAPTIONS_JSON"):
    caps = json.load(open(os.environ["CAPTIONS_JSON"]))

# render caption PNGs (drop shadow only, Helvetica Neue Bold 44, wide margins)
CAP_FONT = os.environ["CAPTION_FONT"]
CAP_IDX = int(os.environ.get("CAPTION_FONT_INDEX", "0"))
cf = ImageFont.truetype(CAP_FONT, 44, index=CAP_IDX)
try:
    cf.set_variation_by_name("Bold")
except Exception:
    pass
asc, desc = cf.getmetrics()
clh = asc + desc + 8
# optional smaller second-language subtitle rendered UNDER the caption (per-cap "en")
EN_SIZE = int(os.environ.get("EN_SIZE", "30"))
cf_en = ImageFont.truetype(CAP_FONT, EN_SIZE, index=CAP_IDX)
try:
    cf_en.set_variation_by_name("Bold")
except Exception:
    pass
easc, edesc = cf_en.getmetrics()
clh_en = easc + edesc + 4
d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))


def wrapc(t, mw, font=cf):
    out, c = [], ""
    for wd in t.split():
        s = (c + " " + wd).strip()
        if d0.textlength(s, font=font) <= mw:
            c = s
        else:
            if c:
                out.append(c)
            c = wd
    if c:
        out.append(c)
    return out


meta = []
for idx, c in enumerate(caps):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd, sd = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    lines = wrapc(c["text"], W - 260)
    en_lines = wrapc(c["en"], W - 300, cf_en) if c.get("en") else []
    y = H - int(os.environ.get("CAP_BOTTOM", "330")) - clh * len(lines)
    placed = []
    for ln in lines:
        x = (W - dd.textlength(ln, font=cf)) / 2
        placed.append((x, y, ln, cf, (255, 255, 255, 255)))
        sd.text((x, y), ln, font=cf, fill=(0, 0, 0, 230))
        y += clh
    if en_lines:  # smaller, slightly dimmer translation line(s) just below
        y += 8
        for ln in en_lines:
            x = (W - dd.textlength(ln, font=cf_en)) / 2
            placed.append((x, y, ln, cf_en, (225, 225, 225, 255)))
            sd.text((x, y), ln, font=cf_en, fill=(0, 0, 0, 220))
            y += clh_en
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    img.alpha_composite(sh, (0, 0))
    for x, y, ln, fnt, col in placed:
        dd.text((x, y), ln, font=fnt, fill=col)
    fp = CAPS / f"c_{idx:03d}.png"
    img.save(fp)
    meta.append([str(fp), c["start"], c["end"]])

blank = CAPS / "_blank.png"
Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
lines = ["ffconcat version 1.0"]
t = 0.0
END_PAD = 0.15
for i, (png, s, e) in enumerate(meta):
    s = max(s, t)
    nxt = meta[i + 1][1] if i + 1 < len(meta) else DUR
    e = min(e + END_PAD, nxt)
    if e <= s:
        continue
    if s > t + 1e-3:
        lines += [f"file '{os.path.abspath(blank)}'", f"duration {s - t:.3f}"]
    lines += [f"file '{os.path.abspath(png)}'", f"duration {max(0.033, e - s):.3f}"]
    t = e
if t < DUR:
    lines += [f"file '{os.path.abspath(blank)}'", f"duration {DUR - t:.3f}"]
lines.append(f"file '{os.path.abspath(blank)}'")
(CAPS / "track.ffconcat").write_text("\n".join(lines))
captrack = WORK / "caption_track.mov"
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(CAPS / "track.ffconcat"),
     "-vf", "fps=30,format=rgba", "-c:v", "qtrle", "-t", f"{DUR:.2f}", str(captrack)])

# 4) hook PNG (Funnel Display, mixed case, top scrim, top-center; optional inline logo)
FONT = os.environ["HOOK_FONT"]
hf = ImageFont.truetype(FONT, HOOK_SIZE)
try:
    hf.set_variation_by_name("Bold")
except Exception:
    pass
himg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(himg)
px = himg.load()
bott = int(H * 0.50)
for yy in range(0, bott):
    a = int(200 * ((bott - yy) / bott) ** 1.3)
    for xx in range(W):
        px[xx, yy] = (6, 6, 6, a)
hd0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
if "\n" in HOOK:
    hlines = [ln.strip() for ln in HOOK.split("\n") if ln.strip()]
else:
    hlines, c = [], ""
    for wd in HOOK.split():
        s = (c + " " + wd).strip()
        if hd0.textlength(s, font=hf) <= W - HOOK_MARGIN:
            c = s
        else:
            if c:
                hlines.append(c)
            c = wd
    if c:
        hlines.append(c)
asc2 = hf.getmetrics()[0]
inline = None
gap = 0
if LOGO_INLINE:
    lhh = int(HOOK_SIZE * LOGO_INLINE_SCALE)
    lg = Image.open(LOGO_INLINE).convert("RGBA")
    inline = lg.resize((max(1, int(lg.width * lhh / lg.height)), lhh), Image.LANCZOS)
    gap = int(HOOK_SIZE * LOGO_INLINE_GAP)
y = int(os.environ.get("HOOK_Y", str(int(H * 0.13))))
for i, ln in enumerate(hlines):
    tw = hd.textlength(ln, font=hf)
    if inline is not None and i == len(hlines) - 1:
        total = tw + gap + inline.width
        x = (W - total) / 2
        hd.text((x, y), ln, font=hf, fill=(255, 255, 255, 255))
        ly = int(y + asc2 * 0.52 - inline.height / 2 + LOGO_INLINE_DY)
        himg.alpha_composite(inline, (int(x + tw + gap), ly))
    else:
        hd.text(((W - tw) / 2, y), ln, font=hf, fill=(255, 255, 255, 255))
    y += int(HOOK_SIZE * 1.0)
hookpng = WORK / "hook.png"
himg.save(hookpng)
if os.environ.get("HOOK_PNG"):
    hookpng = Path(os.environ["HOOK_PNG"])  # pre-rendered hook (e.g. justified block layout)

# --- b-roll inserts: build a 1080x1920 PNG per insert (photo + soft shadow) ---
if os.environ.get("INSERTS"):
    INSERTS = json.loads(os.environ["INSERTS"])
elif os.environ.get("INSERT"):
    INSERTS = [{"image": os.environ["INSERT"], "start": float(os.environ.get("INSERT_START", "0")),
                "end": float(os.environ.get("INSERT_END", "0")), "prebuilt": True}]
else:
    INSERTS = []


def build_insert_png(spec, path):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if spec.get("prebuilt"):
        return spec["image"]  # already a 1080x1920 overlay
    im = Image.open(spec["image"]).convert("RGBA")
    pos = spec.get("pos", "center")
    w = int(spec.get("w", 460 if pos == "topright" else 940))
    im = im.resize((w, max(1, int(im.height * w / im.width))), Image.LANCZOS)
    if pos == "topright":
        x, y0 = W - w - 45, int(spec.get("y", 300))
    elif pos == "top":
        x, y0 = (W - w) // 2, int(spec.get("y", 210))  # sit high, above the face
    else:
        x, y0 = (W - w) // 2, (H - im.height) // 2
    if spec.get("bare"):  # transparent sticker: no plate, no box shadow
        canvas.alpha_composite(im, (x, y0)); canvas.save(path); return path
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 170)), (x, y0 + 12))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    if pos in ("topright", "top"):
        b = Image.new("RGBA", (im.width + 10, im.height + 10), (255, 255, 255, 255))
        b.alpha_composite(im, (5, 5))
        canvas.alpha_composite(b, (x - 5, y0 - 5))
    else:
        canvas.alpha_composite(im, (x, y0))
    canvas.save(path)
    return path


# 5) compose: base + hook(0-5s) [+ logo] [+ inserts] + caption track (LAST) + 1.1x + HQ
final_dur = DUR / SPEED
AUD_FADE = 0.12
afade_st = max(0.0, final_dur - AUD_FADE)
out = str(ROOT / "data/final" / f"{OUT}.mp4")
inputs = ["-i", str(base), "-i", str(audio), "-i", str(captrack),
          "-loop", "1", "-t", f"{HOOK_DUR + 1}", "-i", str(hookpng)]
nidx = 4
apad = f",apad=pad_dur={END_HOLD}" if END_HOLD > 0 else ""
fc = [
    f"[1:a]atempo={SPEED},afade=t=out:st={afade_st:.2f}:d={AUD_FADE}{apad}[aout]",
    f"[3:v]setpts=PTS-STARTPTS,fade=t=out:st={HOOK_DUR - 0.4}:d=0.4:alpha=1[hook]",
]
# video b-roll cutaways FIRST (under hook/inserts/captions): full-frame video
# over the base while the voice runs on. VIDEO_INSERTS = JSON list of
# {"src","from","dur","at"} - "from" in SOURCE seconds of the b-roll clip,
# "at"/"dur" on the EDITED (pre-speed) timeline. Hard cuts.
last = "0:v"
VIDEO_INSERTS = json.loads(os.environ.get("VIDEO_INSERTS", "[]"))
vid_idx0 = nidx + (1 if LOGO else 0) + len(INSERTS)
for k, spec in enumerate(VIDEO_INSERTS):
    f0, bdur, at = float(spec["from"]), float(spec["dur"]), float(spec["at"])
    fc.append(f"[{vid_idx0 + k}:v]trim=start={f0}:end={f0 + bdur},setpts=PTS-STARTPTS+{at}/TB,"
              f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[vb{k}]")
    fc.append(f"[{last}][vb{k}]overlay=0:0:enable='between(t,{at},{at + bdur})'[vv{k}]")
    last = f"vv{k}"
fc.append(f"[{last}][hook]overlay=0:0:enable='between(t,0,{HOOK_DUR})'[vh]")
last = "vh"
if LOGO:
    inputs += ["-loop", "1", "-t", "6", "-i", LOGO]
    fc.append(f"[{nidx}:v]setpts=PTS-STARTPTS,scale={LOGO_W}:-2,fade=t=out:st=4.6:d=0.4:alpha=1[logo]")
    fc.append(f"[{last}][logo]overlay=(W-w)/2:{LOGO_Y}:enable='between(t,0,5)'[vl]")
    last = "vl"
    nidx += 1
for k, spec in enumerate(INSERTS):
    ins_png = build_insert_png(spec, WORK / f"insert_{k}.png")
    if spec.get("at_end"):  # closer: last N edited seconds, stays on through the END_HOLD freeze
        e0, e1 = max(0.0, DUR - float(spec["at_end"])), DUR + 1
    else:
        e0 = to_edited(float(spec["start"]))
        e1 = to_edited(float(spec["end"]))
    inputs += ["-loop", "1", "-t", f"{DUR + 1}", "-i", str(ins_png)]
    fout = "" if spec.get("at_end") else f",fade=t=out:st={max(e0, e1 - 0.3):.2f}:d=0.3:alpha=1"
    fc.append(f"[{nidx}:v]setpts=PTS-STARTPTS,"
              f"fade=t=in:st={e0:.2f}:d=0.3:alpha=1{fout}[ins{k}]")
    fc.append(f"[{last}][ins{k}]overlay=0:0:enable='between(t,{e0:.2f},{e1:.2f})'[vi{k}]")
    last = f"vi{k}"
    nidx += 1
for spec in VIDEO_INSERTS:  # inputs appended here; overlay chain built above (under hook)
    inputs += ["-i", spec["src"]]
    nidx += 1
if CORNER_LOGO:
    inputs += ["-loop", "1", "-t", f"{DUR}", "-i", CORNER_LOGO]
    if os.environ.get("CORNER_HOOK"):  # only during the headline (0-5s), then gone
        fc.append(f"[{nidx}:v]setpts=PTS-STARTPTS,scale={CORNER_LOGO_W}:-2,fade=t=out:st=4.6:d=0.4:alpha=1[clogo]")
        fc.append(f"[{last}][clogo]overlay={CORNER_X}:{CORNER_Y}:enable='between(t,0,5)'[vcl]")
    else:
        fc.append(f"[{nidx}:v]setpts=PTS-STARTPTS,scale={CORNER_LOGO_W}:-2[clogo]")
        # CORNER_WINDOWS = JSON list of [start,end] (EDITED secs): logo only inside
        # these windows (e.g. only while at one place). Default: permanent.
        if os.environ.get("CORNER_WINDOWS"):
            wins = json.loads(os.environ["CORNER_WINDOWS"])
            en = "+".join(f"between(t,{a},{b})" for a, b in wins)
            fc.append(f"[{last}][clogo]overlay={CORNER_X}:{CORNER_Y}:enable='{en}'[vcl]")
        else:
            fc.append(f"[{last}][clogo]overlay={CORNER_X}:{CORNER_Y}[vcl]")
    last = "vcl"
    nidx += 1
fc.append(f"[{last}][2:v]overlay=0:0[vc]")
vend = f"setpts=PTS/{SPEED}"
if END_HOLD > 0:
    vend += f",tpad=stop_mode=clone:stop_duration={END_HOLD}"
END_CARD = os.environ.get("END_CARD", "")
if END_CARD and END_HOLD > 0:
    # full-frame end card (e.g. URL on white) hard-cut in for the END_HOLD seconds
    inputs += ["-loop", "1", "-framerate", "30", "-t", f"{END_HOLD}", "-i", END_CARD]
    fc.append(f"[vc]setpts=PTS/{SPEED},fps=30,format=yuv420p,setsar=1[vm]")
    fc.append(f"[{nidx}:v]scale={W}:{H},fps=30,format=yuv420p,setsar=1[ec]")
    fc.append("[vm][ec]concat=n=2:v=1:a=0[vout]")
    nidx += 1
elif END_FADE > 0:
    fc.append(f"[vc]{vend},fade=t=out:st={max(0, final_dur + END_HOLD - END_FADE):.2f}:d={END_FADE}[vout]")
else:
    fc.append(f"[vc]{vend}[vout]")
# LEAD_FRAME=<output secs>: prepend that composited frame as frame 0 (1/30s), so
# anything that previews the first frame (Finder, WhatsApp, Buffer) shows it.
if os.environ.get("LEAD_FRAME"):
    lt = float(os.environ["LEAD_FRAME"])
    fc[-1] = fc[-1].replace("[vout]", "[vpre]")
    fc.append("[vpre]fps=30,split[vp1][vp2]")
    fi = int(round(lt * 30))  # pick by frame index (time-based trim can miss the frame)
    fc.append(f"[vp2]trim=start_frame={fi}:end_frame={fi + 1},setpts=PTS-STARTPTS[lf]")
    fc.append("[lf][vp1]concat=n=2:v=1:a=0[vout]")
    fc = [f.replace("[aout]", "[apre]") if f.endswith("[aout]") else f for f in fc]
    fc.append("[apre]adelay=33:all=1[aout]")
# optional CRF export (e.g. CRF=17) instead of the default ~10 Mbps ABR
rate = (["-crf", os.environ["CRF"], "-maxrate", "24M", "-bufsize", "40M"] if os.environ.get("CRF")
        else ["-b:v", "10M", "-maxrate", "12M", "-bufsize", "20M"])
run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
     "-c:v", "libx264", "-preset", "medium", *rate,
     "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-r", "30",
     "-g", "60", "-keyint_min", "60", "-sc_threshold", "0",
     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
     "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart",
     # cap the length: looped overlay inputs (hook, inserts) would otherwise stretch a short reel
     "-t", f"{final_dur + END_HOLD + (1 / 30 if os.environ.get('LEAD_FRAME') else 0):.3f}", out])
print(f"OK {out} | {len(SEGS)} seg(s) | {len(caps)} caps | {len(INSERTS)} insert(s) | "
      f"{DUR:.1f}s -> {final_dur:.1f}s reel | hook '{HOOK[:40]}'")
