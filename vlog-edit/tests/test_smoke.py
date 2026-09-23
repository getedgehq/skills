#!/usr/bin/env python3
"""End-to-end smoke test on synthetic media: render, then every judge except speech must pass.

Needs ffmpeg and the fonts from `vlog.py setup`. No network, no Whisper: the transcript is written
by hand, so the test exercises the cut, the cards, the captions, the hook, the outro, the mix and
the judges, not the ASR.

    python3 tests/test_smoke.py
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VLOG = os.path.join(HERE, "..", "scripts", "vlog.py")
FFMPEG = os.environ.get("VLOG_EDIT_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def main():
    d = tempfile.mkdtemp(prefix="vlog-edit-smoke-")
    clip = os.path.join(d, "clip.mp4")
    subprocess.run([FFMPEG, "-y", "-v", "error",
                    "-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=30:duration=12",
                    "-f", "lavfi", "-i", "sine=frequency=220:duration=12",
                    "-af", "volume=0.25", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-shortest", clip], check=True)
    text = ("this is a synthetic test of the vlog editor and it has "
            "numbers in it like forty two percent of the time").split()
    words, t = [], 0.3
    for k, w in enumerate(text):
        words.append({"i": k, "w": w, "s": round(t, 3), "e": round(t + 0.24, 3)})
        t += 0.30 + (0.9 if k == 10 else 0.0)
    os.makedirs(os.path.join(d, "vlog-work"))
    json.dump(words, open(os.path.join(d, "vlog-work", "words.a.json"), "w"))
    edit = {
        "name": "smoke", "clips": {"a": "clip.mp4"},
        "keep": [{"clip": "a", "from": 0, "to": len(text) - 1}],
        "hook": {"text": "a synthetic hook", "hold": 1.2},
        "captions": {"keys": ["numbers"]},
        "cards": [
            {"kind": "prompt", "at": 4, "until": 8, "app": "Assistant", "text": "Edit my vlog."},
            {"kind": "stat", "at": 12, "until": 18, "title": "Share of the time", "value": "42%",
             "unit": "of the time", "total": 100, "part": 42, "accent": True,
             "source": "Synthetic test data"},
        ],
        "outro": {"text": "the end", "dur": 1.0},
    }
    ep = os.path.join(d, "EDIT.json")
    json.dump(edit, open(ep, "w"))
    subprocess.run([sys.executable, VLOG, "render", ep, "--jobs", "2"], check=True)
    r = subprocess.run([sys.executable, VLOG, "qa", ep, "--no-speech"])
    rep = json.load(open(os.path.join(d, "renders", "smoke.qa.json")))
    assert r.returncode == 0, f"qa failed: {rep['fails']}"
    assert os.path.isfile(os.path.join(d, "renders", "smoke.contact.jpg"))
    print(f"smoke OK ({d})")
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
