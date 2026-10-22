#!/usr/bin/env python3
"""mkreel.py SPEC.json [--render]

Turns a reel spec (see references/spec-format.md) into a self-contained bundle at
$REEL_WORK/bundles/<name>/: the clip(s), transcript, kept segments, drafted captions,
inserts (stat cards + closer), the hook layer, both fonts and a job.sh that renders it.
The bundle runs on any machine with ffmpeg + Python 3 + Pillow: locally (--render) or
remotely (remote_render.sh <bundle>).

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
        return
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy(src, dest)


clip = resolve_clip(sp["clip"])
clip_name = "main" + clip.suffix
place(clip, R / clip_name)
for name, path in sp.get("clips", {}).items():
    c = resolve_clip(path); place(c, R / "clips" / f"{name}{c.suffix}")

transcript = Path(os.path.expanduser(sp.get("transcript") or W / "transcripts" / f"{clip.stem}.json"))
if not transcript.exists():
    sys.exit(f"no transcript at {transcript}: run transcribe.py first")
shutil.copy(transcript, R / "transcript.json")

segs = []
for s in sp["segments"]:
    if isinstance(s, dict):
        segs.append(s)
    else:
        seg = {"start": s[0], "end": s[1]}
        if len(s) > 2:
            seg["src"] = s[2]
        segs.append(seg)
json.dump(segs, open(R / "segments.json", "w"))
main_segs = [s for s in segs if not s.get("src")]


def ed(t):
    """source time on the main clip -> edited (cut) timeline"""
    acc = 0
    for s in segs:
        if not s.get("src") and s["start"] <= t <= s["end"]:
            return round(acc + t - s["start"], 2)
        acc += s["end"] - s["start"]
    raise ValueError(f"card time {t} is not inside a kept segment of the main clip")


# captions: a curated file wins; otherwise draft from the transcript
if sp.get("captions"):
    shutil.copy(os.path.expanduser(sp["captions"]), R / "caps.json")
else:
    if len(main_segs) != len(segs):
        print("NOTE: segments from other clips get no drafted captions; curate caps.json by hand")
    subprocess.run([sys.executable, str(HERE / "make_caps.py"), "draft", "--transcript", str(R / "transcript.json"),
                    "--segments", json.dumps(main_segs), "--out", str(R / "caps.json")], check=True, capture_output=True)
    caps = json.load(open(R / "caps.json"))
    for k, v in sp.get("cap_fix", {}).items():
        for c in caps:
            c["text"] = c["text"].replace(k, v)
    caps = [c for c in caps if c["text"].strip()]
    json.dump(caps, open(R / "caps.json", "w"), ensure_ascii=False, indent=1)
caps = json.load(open(R / "caps.json"))

ins = []
for c in sp.get("cards", []):
    img = Path(os.path.expanduser(c["image"])); shutil.copy(img, R / "cards" / img.name)
    ins.append({"image": f"cards/{img.name}", "start": ed(c["at"][0]), "end": ed(c["at"][1]), "pos": c.get("pos", "top"),
                "w": c.get("w", 600), "y": c.get("y", 360), "bare": c.get("bare", True)})
if sp.get("closer", True):  # handle closer on the last ~0.9 s + the end hold
    subprocess.run([sys.executable, str(HERE / "closer_png.py"), str(R / "closer.png")], check=True, capture_output=True)
    ins.append({"image": "closer.png", "prebuilt": True, "at_end": 0.9, "start": 0, "end": 0})
json.dump(ins, open(R / "inserts.json", "w"))

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

grade = rmconf.get("REEL_GRADE"); speed = rmconf.get("REEL_SPEED")
edited = sum(s["end"] - s["start"] for s in segs)
# hook stays up to 10 edited seconds, but always fades before the closer on a short reel
hook_dur = round(max(2.0, min(10.0, edited - 1.5)), 2)
hs_out = subprocess.run([sys.executable, str(HERE / "hook_png.py"), str(R / "hook.png"), sp["hook"], str(hs)] + extra,
                        check=True, capture_output=True, text=True).stdout
if "size" in hs_out:
    hs = int(hs_out.split("size")[1].split()[0])
job = f"""#!/usr/bin/env bash
# render bundle '{n}'. Needs ffmpeg, python3, Pillow. Output: out/reel_{n}.mp4
set -euo pipefail
cd "$(dirname "$0")"; B="$PWD"
SEG1=$(python3 precut.py "$B/{clip_name}" segments.json "$B/pre.mov")
SRC="$B/pre.mov" TRANSCRIPT="$B/transcript.json" SEGMENTS="$SEG1" \\
CAPTIONS_JSON="$B/caps.json" HOOK={shlex.quote(sp['hook'])} HOOK_SIZE={hs} HOOK_Y=285 HOOK_MARGIN=174 HOOK_DUR={hook_dur} \\
HOOK_FONT="$B/fonts/hook{hook_font.suffix}" CAPTION_FONT="$B/fonts/caption{Path(cap_font).suffix}" CAPTION_FONT_INDEX={cap_idx} \\
END_HOLD=0.6 CRF=20 SPEED={speed} INSERTS="$(cat inserts.json)" GRADE={shlex.quote(grade)} \\
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
