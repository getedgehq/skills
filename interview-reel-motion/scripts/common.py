"""Shared helpers for the QA scripts: ffmpeg location, frame readers, run grouping. Standard library + numpy."""
import os, shutil, subprocess, json
import numpy as np

FFMPEG = os.environ.get("IRM_FFMPEG") or shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
FFPROBE = os.environ.get("IRM_FFPROBE") or shutil.which("ffprobe") or "/usr/bin/ffprobe"
FPS = 30


def probe(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames:format=duration", "-of", "json", path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out); s = j["streams"][0]; n, d = s["r_frame_rate"].split("/")
    return dict(w=int(s["width"]), h=int(s["height"]), fps=float(n) / float(d), frames=int(s.get("nb_frames") or 0), duration=float(j["format"]["duration"]))


def frames(path, w=None, h=None, fmt="rgb24", start=None, duration=None):
    """yield (index, HxWxC uint8) frames, optionally scaled"""
    info = probe(path); W, H = w or info["w"], h or info["h"]; ch = {"rgb24": 3, "gray": 1}[fmt]
    cmd = [FFMPEG, "-nostdin", "-v", "error"]
    if start is not None: cmd += ["-ss", str(start)]
    cmd += ["-i", path]
    if duration is not None: cmd += ["-t", str(duration)]
    if (W, H) != (info["w"], info["h"]): cmd += ["-vf", f"scale={W}:{H}"]
    cmd += ["-f", "rawvideo", "-pix_fmt", fmt, "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE); n = W * H * ch; i = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield i, np.frombuffer(b, np.uint8).reshape(H, W, ch) if ch > 1 else np.frombuffer(b, np.uint8).reshape(H, W)
        i += 1
    p.wait()


def runs(rows, gap=0.05):
    """group (t, value) rows into [t0, t1, max value] runs"""
    out = []
    for t, v in rows:
        if out and t - out[-1][1] < gap: out[-1][1] = t; out[-1][2] = max(out[-1][2], v)
        else: out.append([t, t, v])
    return out


def spans(arg):
    """'26.8-27.9,41.8-42.2' -> [(26.8, 27.9), (41.8, 42.2)]"""
    return [tuple(float(x) for x in s.split("-")) for s in arg.split(",") if s] if arg else []
