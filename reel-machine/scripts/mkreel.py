#!/usr/bin/env python3
"""mkreel.py SPEC.json [--render]

Turns a reel spec (see references/spec-format.md) into a self-contained bundle at
$REEL_WORK/bundles/<name>/: the clip(s), transcript, kept segments, drafted captions,
inserts (stat cards, full-screen cutaways, closer or CTA), the hook layer, both fonts and a
job.sh that renders it. The bundle runs on any machine with ffmpeg + Python 3 + Pillow:
locally (--render) or remotely (remote_render.sh <bundle>). After the render, run
finish.sh on the bundle (voice EQ, jump cuts, pace gate, face check).

Two spec forms:
  single clip   "clip": "<stem>", "segments": [[a, b], ...]
  multi clip    "clips": ["<stem>", "<stem>"], "segments": [[clip_index, a, b], ...]
In the multi-clip form the clips' transcripts are laid end to end, so captions, cards, cuts
and the ending rule work across clips; "at" times are [clip_index, a, b].

Prints the drafted captions with their edited times, so you can curate caps.json in the
bundle (and run make_caps.py check on it) before rendering.
"""
import json, os, shlex, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rmconf

spec_path = Path(sys.argv[1]); render = "--render" in sys.argv[2:]
sp = json.load(open(spec_path)); n = sp["name"]
W = rmconf.work()
R = W / "bundles" / n
for sub in ("cards", "sig", "clips", "fonts", "out"):
    (R / sub).mkdir(parents=True, exist_ok=True)
SPEED = float(rmconf.get("REEL_SPEED"))


def resolve_clip(c):
    p = Path(os.path.expanduser(c))
    if p.exists():
        return p
    for ext in (".mov", ".MOV", ".mp4"):
        q = W / "clips" / f"{c}{ext}"
        if q.exists():
            return q
    sys.exit(f"clip not found: {c}")


def place(src, dest):
    """hard link when possible (no extra disk), else copy"""
    if dest.exists():
        dest.unlink()
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy(src, dest)


def duration(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip())


def transcript_for(clip, given=None):
    t = Path(os.path.expanduser(given or W / "transcripts" / f"{clip.stem}.json"))
    if not t.exists():
        sys.exit(f"no transcript at {t}: run transcribe.py first")
    return t


# --- timeline. tl[i] = {"c": [start, end] on the caption timeline or None, "seg": segment for precut.py} ---
multi = isinstance(sp.get("clips"), list)
if multi:
    clips = [resolve_clip(c) for c in sp["clips"]]
    place(clips[0], R / ("main" + clips[0].suffix)); clip_name = "main" + clips[0].suffix
    for i, c in enumerate(clips[1:], 1):
        place(c, R / "clips" / f"c{i}{c.suffix}")
    dur = [duration(c) for c in clips]
    off = [sum(dur[:i]) for i in range(len(clips))]
    tr = sp.get("transcripts") or [None] * len(clips)
    words = []
    for i, c in enumerate(clips):  # transcripts laid end to end: one caption timeline across clips
        for w in json.load(open(transcript_for(c, tr[i])))["words"]:
            w = dict(w)
            if "start" in w:
                w["start"] = round(w["start"] + off[i], 3); w["end"] = round(w["end"] + off[i], 3)
            words.append(w)
    json.dump({"words": words, "text": "".join(w.get("text", "") for w in words)}, open(R / "transcript.json", "w"))
    C = lambda ci, t: round(off[ci] + t, 3)
    tl = []
    for ci, a, b in sp["segments"]:
        seg = {"start": a, "end": b}
        if ci:
            seg["src"] = f"c{ci}"
        tl.append({"c": [C(ci, a), C(ci, b)], "seg": seg})
    last_ci = sp["segments"][-1][0]
    clip_end = off[last_ci] + dur[last_ci]
    at = lambda x: [C(x[0], x[1]), C(x[0], x[2])]
else:
    clip = resolve_clip(sp["clip"])
    clip_name = "main" + clip.suffix
    place(clip, R / clip_name)
    for name, path in (sp.get("clips") or {}).items():
        c = resolve_clip(path); place(c, R / "clips" / f"{name}{c.suffix}")
    shutil.copy(transcript_for(clip, sp.get("transcript")), R / "transcript.json")
    tl = []
    for s in sp["segments"]:
        seg = dict(s) if isinstance(s, dict) else {"start": s[0], "end": s[1], **({"src": s[2]} if len(s) > 2 else {})}
        tl.append({"c": None if seg.get("src") else [seg["start"], seg["end"]], "seg": seg})
    clip_end = duration(clip)
    at = lambda x: list(x)

# --- ending rule: the last segment ends on the last whole word; footage runs on under the closer ---
END = None
if sp.get("ending", True) and tl[-1]["c"]:
    W_ = [w for w in json.load(open(R / "transcript.json"))["words"] if w.get("type") == "word"]
    a, b = tl[-1]["c"]
    inside = [w for w in W_ if w["start"] >= a - 0.05 and w["end"] <= b + 0.15]
    if inside:
        last = inside[-1]
        if last["text"].rstrip()[-1:] not in ".?!":
            print("WARNING ending: the last word is not a sentence end:", last["text"])
        nxt = [w["start"] for w in W_ if w["start"] > last["end"] + 0.01]
        nstart = nxt[0] if nxt else 1e9
        ve = max(last["end"] + 0.15, min(last["end"] + float(sp.get("tail_max", 1.15)), nstart - 0.08, clip_end - 0.05))
        delta = round(ve, 2) - b
        tl[-1]["c"][1] = round(ve, 2); tl[-1]["seg"]["end"] = round(tl[-1]["seg"]["end"] + delta, 3)
        END = {"speech": last["end"], "tail": ve - last["end"]}
        print(f"ending: last word {last['text']!r} @ {last['end']:.2f}, next word @ {nstart:.2f}, tail {END['tail']:.2f}s")

segs = [t["seg"] for t in tl]
json.dump(segs, open(R / "segments.json", "w"))
cap_segs = [{"start": t["c"][0], "end": t["c"][1]} for t in tl if t["c"]]


def ed(t):
    """caption-timeline time -> edited (cut) timeline"""
    acc = 0
    for x in tl:
        if x["c"] and x["c"][0] <= t <= x["c"][1]:
            return round(acc + t - x["c"][0], 2)
        acc += x["seg"]["end"] - x["seg"]["start"]
    raise ValueError(f"time {t} is not inside a kept segment")


# --- captions: a curated file wins; otherwise draft from the transcript ---
if sp.get("captions"):
    shutil.copy(os.path.expanduser(sp["captions"]), R / "caps.json")
else:
    if len(cap_segs) != len(segs):
        print("NOTE: segments from other clips get no drafted captions; use the multi-clip form or curate caps.json")
    subprocess.run([sys.executable, str(HERE / "make_caps.py"), "draft", "--transcript", str(R / "transcript.json"),
                    "--segments", json.dumps(cap_segs), "--out", str(R / "caps.json")], check=True, capture_output=True)
    caps = json.load(open(R / "caps.json"))
    for k, v in sp.get("cap_fix", {}).items():
        for c in caps:
            c["text"] = c["text"].replace(k, v)
    caps = [c for c in caps if c["text"].strip()]
    json.dump(caps, open(R / "caps.json", "w"), ensure_ascii=False, indent=1)
caps = json.load(open(R / "caps.json"))

# --- inserts: stat cards, full-screen cutaways, closer or CTA ---
ins, credits = [], []
for c in sp.get("cards", []):
    img = Path(os.path.expanduser(c["image"])); shutil.copy(img, R / "cards" / img.name)
    t0, t1 = at(c["at"])
    ins.append({"image": f"cards/{img.name}", "start": ed(t0), "end": ed(t1), "pos": c.get("pos", "top"),
                "w": c.get("w", 600), "y": c.get("y", 360), "bare": c.get("bare", True)})
for k, c in enumerate(sp.get("cuts", [])):
    img = Path(os.path.expanduser(c["image"]))
    if c.get("title"):  # build the 1080x1920 cutaway card from a photo + title
        dest = R / "cards" / f"cut{k}_{img.stem}.png"
        subprocess.run([sys.executable, str(HERE / "cutaway.py"), str(dest), str(img), c["title"], c.get("subtitle", "")],
                       check=True, capture_output=True)
    else:
        dest = R / "cards" / img.name; shutil.copy(img, dest)
    t0, t1 = at(c["at"])
    ins.append({"image": f"cards/{dest.name}", "prebuilt": True, "hard": True, "start": ed(t0), "end": ed(t1)})
    if c.get("credit"):
        credits.append(c["credit"])
tail = round(min(1.15, END["tail"]), 2) if END else 0.9
if sp.get("cta"):  # product reel: logo + call to action at the end instead of the handle closer
    cta = sp["cta"]; cmd = [sys.executable, str(HERE / "cta_png.py"), str(R / "closer.png"), cta["text"]]
    if cta.get("logo"):
        cmd += ["--logo", os.path.expanduser(cta["logo"])]
    subprocess.run(cmd, check=True, capture_output=True)
    ins.append({"image": "closer.png", "prebuilt": True, "at_end": float(cta.get("at_end", max(tail, 1.5))), "start": 0, "end": 0})
elif sp.get("closer", True):  # handle closer on the last ~0.9 s + the end hold
    subprocess.run([sys.executable, str(HERE / "closer_png.py"), str(R / "closer.png")], check=True, capture_output=True)
    ins.append({"image": "closer.png", "prebuilt": True, "at_end": tail, "start": 0, "end": 0})
json.dump(ins, open(R / "inserts.json", "w"))
if credits:
    (R / "credits.txt").write_text("Photos: " + "; ".join(dict.fromkeys(credits)) + "\n")
    print("CREDITS (add to the post caption, or pass --credits to schedule_reel.py):", (R / "credits.txt").read_text().strip())

corner = ""
if sp.get("corner_logo"):
    lg = Path(os.path.expanduser(sp["corner_logo"])); shutil.copy(lg, R / "sig" / lg.name)
    corner = f'CORNER_LOGO="$B/sig/{lg.name}" '

hs = subprocess.run([sys.executable, str(HERE / "fit_hook.py"), sp["hook"]], capture_output=True, text=True).stdout
hs = int(hs.split("HOOK_SIZE=")[1].split()[0]) if "HOOK_SIZE=" in hs else 72
extra = []
for w, img in sp.get("inline", {}).items():
    extra += ["--after", f"{w}={os.path.expanduser(img)}"]
if sp.get("strip"):
    extra += ["--strip", os.path.expanduser(sp["strip"])]

hook_font = Path(rmconf.hook_font()); cap_font, cap_idx = rmconf.caption_font()
shutil.copy(hook_font, R / "fonts" / ("hook" + hook_font.suffix))
shutil.copy(cap_font, R / "fonts" / ("caption" + Path(cap_font).suffix))
for f in ("precut.py", "build_reel.py"):
    shutil.copy(HERE / f, R / f)

grade = rmconf.get("REEL_GRADE")
edited = sum(s["end"] - s["start"] for s in segs)
# hook stays up to 10 edited seconds, but always fades before the closer on a short reel
hook_dur = float(sp.get("hook_dur", round(max(2.0, min(10.0, edited - 1.5)), 2)))
hs_out = subprocess.run([sys.executable, str(HERE / "hook_png.py"), str(R / "hook.png"), sp["hook"], str(hs)] + extra,
                        check=True, capture_output=True, text=True).stdout
if "size" in hs_out:
    hs = int(hs_out.split("size")[1].split()[0])
endenv = (f"END_HOLD={max(0.0, round(1.0 - END['tail'] / SPEED, 2))} AUD_FADE=0.25 AUD_END={ed(END['speech'] + 0.12)}"
          if END else "END_HOLD=0.6")
job = f"""#!/usr/bin/env bash
# render bundle '{n}'. Needs ffmpeg, python3, Pillow. Output: out/reel_{n}.mp4
set -euo pipefail
cd "$(dirname "$0")"; B="$PWD"
SEG1=$(python3 precut.py "$B/{clip_name}" segments.json "$B/pre.mov")
SRC="$B/pre.mov" TRANSCRIPT="$B/transcript.json" SEGMENTS="$SEG1" \\
CAPTIONS_JSON="$B/caps.json" HOOK={shlex.quote(sp['hook'])} HOOK_SIZE={hs} HOOK_Y=285 HOOK_MARGIN=174 HOOK_DUR={hook_dur} \\
HOOK_FONT="$B/fonts/hook{hook_font.suffix}" CAPTION_FONT="$B/fonts/caption{Path(cap_font).suffix}" CAPTION_FONT_INDEX={cap_idx} \\
CAP_SIZE={rmconf.get('REEL_CAP_SIZE')} CAP_BOTTOM={rmconf.get('REEL_CAP_BOTTOM')} {corner}\\
{endenv} CRF=20 SPEED={SPEED} INSERTS="$(cat inserts.json)" GRADE={shlex.quote(grade)} \\
HOOK_PNG="$B/hook.png" REEL_ROOT="$B/out" OUT=reel_{n} python3 build_reel.py > out/build.log 2>&1 || {{ tail -20 out/build.log; exit 1; }}
cp out/data/final/reel_{n}.mp4 out/ && rm -f pre.mov && tail -1 out/build.log
"""
(R / "job.sh").write_text(job); os.chmod(R / "job.sh", 0o755)

print(R, "| caps", len(caps), "| inserts", len(ins), "| hook size", hs)
for c in caps:
    print("  %.2f-%.2f %s" % (c["start"], c["end"], c["text"]))
if render:
    subprocess.run(["bash", str(R / "job.sh")], check=True)
    dest = W / "renders" / f"reel_{n}.mp4"
    shutil.copy(R / "out" / f"reel_{n}.mp4", dest); print("render:", dest)
    print(f"next: bash {HERE / 'finish.sh'} {R}")
