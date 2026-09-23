#!/usr/bin/env python3
"""Fourth QA gate: judge the CUT, not the pixels.

Black-frame, loudness and transcript checks all pass a cut that flashes, ghosts or freezes,
because none of them looks at a transition. This judge does.

This gate decodes every frame at 270x480 grey and judges the shape of the frame-to-frame difference:

  GHOST     a transition spread over 2+ frames. A hard cut is ONE large difference. Two or more in a
            row means both pictures were on screen at once, which reads as a render fault.
  FLASH     two cuts less than `--min-shot` apart. Between two graphics that is a sliver of the
            underlying face; the eye catches it and the cut feels broken.
  FROZEN    a still frame held on screen.
  CREEP     a shot animating so slowly the eye cannot tell it from a still. A hold is not motion:
            a card that is supposed to be pushing and is not is worse than no card.
  OFFBEAT   a cut that lands in the middle of a spoken word. Cuts belong in the gaps, or exactly on
            a word's onset.
  STROBE    consecutive large differences, i.e. a shot shorter than three frames.

Usage:
    judge_cut.py <media> [--plan <plan.json>] [--json <out.json>]
                 [--cut 22] [--ghost 8] [--min-shot 0.40] [--hold 2.5] [--hold-run 0.40]
Exit 1 on any finding.
"""
import argparse, json, os, subprocess, sys, re

import numpy as np

import shutil
FFMPEG = os.environ.get("VLOG_EDIT_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("VLOG_EDIT_FFPROBE") or shutil.which("ffprobe") or "ffprobe"
GW, GH = 270, 480


def probe_fps(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=r_frame_rate", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True).stdout.strip()
    num, den = out.split("/")
    return float(num) / float(den)


def frames(path):
    p = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-vf", f"scale={GW}:{GH},format=gray",
         "-f", "rawvideo", "-"],
        capture_output=True, check=True)
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    n = buf.size // (GW * GH)
    return buf[: n * GW * GH].reshape(n, GH, GW).astype(np.int16)


def is_blend(f, i, j):
    """True when the frames between i and j are a mix of frame i and frame j.

    That is what a dissolve IS: both pictures on screen at once. A clean cut followed by ordinary
    camera shake also produces several large differences in a row, but its in-between frames look
    like the NEW shot, not like a mix, so it is not flagged.
    """
    a, b = f[i].astype(np.float32), f[j].astype(np.float32)
    ab = a - b
    den = float((ab * ab).sum())
    if den < 1e-6:
        return False
    span = float(np.abs(ab).mean())
    for m in range(i + 1, j):
        x = f[m].astype(np.float32) - b
        alpha = float((x * ab).sum()) / den
        resid = float(np.abs(x - alpha * ab).mean())
        if not (0.12 < alpha < 0.88) or resid > 0.35 * span:
            return False
    return True


def word_spans(plan):
    """(start, end) of every spoken word on the final timeline, from the render plan."""
    return sorted((w["s"], w["e"]) for w in json.load(open(plan))["words"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("--plan")
    ap.add_argument("--json")
    ap.add_argument("--cut", type=float, default=22.0)
    ap.add_argument("--ghost", type=float, default=8.0)
    ap.add_argument("--min-shot", type=float, default=0.40)
    ap.add_argument("--hold", type=float, default=0.80)
    ap.add_argument("--hold-run", type=float, default=0.40)
    ap.add_argument("--creep", type=float, default=3.00)
    ap.add_argument("--creep-run", type=float, default=0.80)
    ap.add_argument("--ignore-before", type=float, default=0.0,
                    help="seconds of head to skip (title card animation)")
    ap.add_argument("--ignore-after", type=float, default=0.0,
                    help="seconds of tail to skip, measured from the end (outro)")
    a = ap.parse_args()

    fps = probe_fps(a.media)
    f = frames(a.media)
    n = len(f)
    if n < 4:
        print(f"FAIL  only {n} frames decoded", file=sys.stderr)
        return 1
    t = lambda i: i / fps
    dur = n / fps

    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))      # d[i] = change INTO frame i+1
    lum = f.mean(axis=(1, 2))

    # A whole-frame average is the wrong ruler for a graphic. A card is mostly flat colour, so a
    # push that is plainly visible on screen averages out to almost nothing, while walking b-roll
    # scores high everywhere. Measure instead how much the EDGES moved: the mean change over the
    # pixels that carry structure, which is what the eye actually tracks.
    gx = np.abs(np.diff(f, axis=2))[:, :-1, :]
    gy = np.abs(np.diff(f, axis=1))[:, :, :-1]
    grad = np.maximum(gx, gy)
    diffc = np.abs(np.diff(f, axis=0))[:, :-1, :-1]
    de = np.empty(len(f) - 1)
    for i in range(len(de)):
        mask = np.maximum(grad[i], grad[i + 1]) > 12
        de[i] = diffc[i][mask].mean() if mask.any() else 0.0
    lo, hi = a.ignore_before, dur - a.ignore_after
    live = lambda i: lo <= t(i + 1) <= hi

    findings = []

    # --- transitions -------------------------------------------------------------------------
    # A transition is not "a lot of change": walking b-roll changes a lot every frame. It is change
    # that stands out against how much this part of the film is moving anyway. Score each frame
    # against the median difference in a +/-0.5s window around it, ignoring its own neighbourhood.
    half, skip = int(round(0.5 * fps)), 3
    bg = np.empty_like(d)
    for i in range(len(d)):
        w = np.concatenate([d[max(0, i - half):max(0, i - skip)], d[i + skip + 1:i + half + 1]])
        bg[i] = np.median(w) if w.size else d[i]
    z = d / np.maximum(bg, 0.6)
    trans = (z > 4.0) & (d > a.ghost)

    # One flagged frame is a hard cut. Two or more in a row means both pictures were on screen at
    # once, and a monotone luma ramp across the run is the fingerprint of a cross-dissolve.
    cuts = []
    i = 0
    while i < len(trans):
        if not trans[i]:
            i += 1
            continue
        j = i
        while j < len(trans) and trans[j]:
            j += 1
        peak = float(d[i:j].max())
        if j - i >= 2 and is_blend(f, i, j):
            seq = lum[i:j + 1]
            ramp = bool(np.all(np.diff(seq) > 0) or np.all(np.diff(seq) < 0))
            if live(i):
                findings.append({
                    "kind": "GHOST", "at": round(t(i + 1), 2), "frames": int(j - i),
                    "peak": round(peak, 1), "lumaRamp": ramp,
                    "detail": f"transition spread over {j-i} frames at {t(i+1):.2f}s "
                              f"({(j-i)/fps:.2f}s, luma {seq[0]:.0f}->{seq[-1]:.0f}"
                              f"{', monotone ramp' if ramp else ''}); both pictures visible at once",
                })
        cuts.append((i + (j - i) // 2, peak))
        i = j

    # --- shots too short to read ------------------------------------------------------------
    for (i0, p0), (i1, p1) in zip(cuts, cuts[1:]):
        gap = (i1 - i0) / fps
        if gap < a.min_shot and live(i0):
            findings.append({
                "kind": "FLASH", "at": round(t(i0 + 1), 2), "dur": round(gap, 3),
                "detail": f"shot of {gap:.2f}s between cuts at {t(i0+1):.2f}s and {t(i1+1):.2f}s; "
                          f"under {a.min_shot:.2f}s it reads as a glitch, not a shot",
            })
        if i1 - i0 <= 2 and live(i0):
            findings.append({
                "kind": "STROBE", "at": round(t(i0 + 1), 2),
                "detail": f"two cuts {i1-i0} frames apart at {t(i0+1):.2f}s",
            })

    # --- dead holds --------------------------------------------------------------------------
    # Two grades. FROZEN is a still frame held on screen. CREEP is a shot that is technically
    # animating but so slowly the eye cannot tell it apart from a still: a hold is not motion.
    for kind, thresh, run_s in (("FROZEN", a.hold, a.hold_run), ("CREEP", a.creep, a.creep_run)):
        run_min = max(2, int(round(run_s * fps)))
        still = de < thresh
        i = 0
        while i < len(still):
            if not still[i]:
                i += 1
                continue
            j = i
            while j < len(still) and still[j]:
                j += 1
            if j - i >= run_min and live(i) and live(j - 1):
                if kind == "CREEP" and any(x["kind"] == "FROZEN" and
                                           abs(x["at"] - t(i + 1)) < 0.2 for x in findings):
                    i = j
                    continue
                findings.append({
                    "kind": kind, "at": round(t(i + 1), 2), "dur": round((j - i) / fps, 2),
                    "peak": round(float(de[i:j].max()), 2),
                    "detail": f"{(j-i)/fps:.2f}s from {t(i+1):.2f}s with no frame moving its edges "
                              f"more than {de[i:j].max():.2f} (limit {thresh}); "
                              + ("nothing on screen is moving" if kind == "FROZEN"
                                 else "the shot creeps rather than moves"),
                })
            i = j

    # --- cuts against the speech -------------------------------------------------------------
    if a.plan:
        spans = word_spans(a.plan)
        for i, peak in cuts:
            ct = t(i + 1)
            if not live(i):
                continue
            inside = next(((s, e) for s, e in spans if s + 0.06 < ct < e - 0.06), None)
            if inside:
                findings.append({
                    "kind": "OFFBEAT", "at": round(ct, 2),
                    "detail": f"cut at {ct:.2f}s lands inside the word spanning "
                              f"{inside[0]:.2f}-{inside[1]:.2f}s",
                })

    order = {"GHOST": 0, "STROBE": 1, "FLASH": 2, "FROZEN": 3, "CREEP": 4, "OFFBEAT": 5}
    findings.sort(key=lambda x: (order[x["kind"]], x["at"]))

    report = {
        "media": a.media, "fps": round(fps, 3), "frames": n, "duration": round(dur, 2),
        "cuts": [round(t(i + 1), 2) for i, _ in cuts],
        "maxDiff": round(float(d.max()), 2), "medianDiff": round(float(np.median(d)), 2),
        "edgeMotion": {f"{t(i+1):.2f}": round(float(de[i]), 2) for i in range(0, len(de), 5)},
        "findings": findings, "pass": not findings,
    }
    if a.json:
        open(a.json, "w").write(json.dumps(report, indent=2))

    print(f"{a.media}  {n} frames @ {fps:.2f}fps  {dur:.2f}s")
    print(f"cuts: {', '.join(f'{c:.2f}' for c in report['cuts']) or 'none'}")
    for x in findings:
        print(f"  {x['kind']:8s} {x['detail']}")
    print("PASS" if report["pass"] else f"FAIL  {len(findings)} finding(s)")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
