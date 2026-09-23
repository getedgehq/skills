#!/usr/bin/env python3
"""vlog-edit: turn raw selfie footage into a captioned 9:16 short, then judge the result.

    python3 vlog.py setup                          fetch the Inter Display fonts once
    python3 vlog.py transcribe EDIT.json           word timings for every clip, numbered
    python3 vlog.py render EDIT.json               cut, cards, captions, hook, outro, mix
    python3 vlog.py qa EDIT.json                   four judges on the render; exit 1 on a finding

Everything is keyed to WORDS, never to hand-typed seconds. A card, a cutaway and a caption all start
and end in the gap between two words, which is what keeps every cut off a syllable.
See ../references/edit-json.md for the EDIT.json contract.
"""
import argparse, difflib, json, math, os, re, shutil, subprocess, sys, tempfile, zipfile
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FFMPEG = os.environ.get("VLOG_EDIT_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("VLOG_EDIT_FFPROBE") or shutil.which("ffprobe") or "ffprobe"
FPS = 30
W, H = 1080, 1920
HOOK_FADE = 0.35
MIN_SHOT = 0.45      # anything shorter between two cuts reads as a glitch, not a shot
LINE_HOLD = 0.70     # a finished caption line stays up through a breath instead of blinking out
INTER_URL = "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip"


def die(msg):
    print(f"vlog-edit: {msg}", file=sys.stderr)
    sys.exit(2)


def run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die(f"{what} failed (exit {r.returncode}):\n{r.stderr[-1500:]}")
    return r


def probe(path):
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
             "-of", "json", path], f"ffprobe {path}")
    return json.loads(r.stdout)


def duration(path):
    return float(probe(path)["format"]["duration"])


# ---------------------------------------------------------------------------------------------
# setup
# ---------------------------------------------------------------------------------------------

def cmd_setup(_a):
    import look
    os.makedirs(look.FONT_DIR, exist_ok=True)
    want = ["Medium", "SemiBold", "Bold", "ExtraBold"]
    if all(os.path.isfile(os.path.join(look.FONT_DIR, f"InterDisplay-{w}.ttf")) for w in want):
        print(f"fonts already in {look.FONT_DIR}")
        return
    import urllib.request
    print(f"downloading Inter 4.1 (SIL Open Font License) from {INTER_URL}")
    body = urllib.request.urlopen(INTER_URL, timeout=120).read()
    z = zipfile.ZipFile(BytesIO(body))
    got = 0
    for name in z.namelist():
        base = os.path.basename(name)
        if base.startswith("InterDisplay-") and base.endswith(".ttf") and base[13:-4] in want:
            open(os.path.join(look.FONT_DIR, base), "wb").write(z.read(name))
            got += 1
        if base == "LICENSE.txt":
            open(os.path.join(look.FONT_DIR, "OFL-LICENSE.txt"), "wb").write(z.read(name))
    if got < len(want):
        die(f"the Inter zip carried {got} of {len(want)} Inter Display weights; layout would be wrong.")
    print(f"fonts ready in {look.FONT_DIR}")


# ---------------------------------------------------------------------------------------------
# EDIT.json
# ---------------------------------------------------------------------------------------------

def load_edit(path):
    e = json.load(open(path))
    base = os.path.dirname(os.path.abspath(path))
    e["_base"] = base
    e["_work"] = os.path.join(base, e.get("work", "vlog-work"))
    os.makedirs(e["_work"], exist_ok=True)
    clips = e.get("clips") or {}
    if not clips:
        die("EDIT.json needs `clips`: {id: path}.")
    e["clips"] = {k: (v if os.path.isabs(v) else os.path.join(base, v)) for k, v in clips.items()}
    for k, v in e["clips"].items():
        if not os.path.isfile(v):
            die(f"clip {k!r}: no file at {v}")
    e["_default_clip"] = next(iter(e["clips"]))
    return e


def words_path(e, cid):
    return os.path.join(e["_work"], f"words.{cid}.json")


def load_words(e, cid):
    """The clip's words with the EDIT.json `fix` corrections applied.

    Trust the speaker over the ASR. `fix` maps "clip:3" or "clip:3-5" to the words actually said;
    the corrected words share the original span. Ids stay stable ("3", "3.1", ...) so every other
    reference in EDIT.json keeps pointing at the same moment.
    """
    p = words_path(e, cid)
    if not os.path.isfile(p):
        die(f"no transcript for clip {cid!r}. Run `vlog.py transcribe` first.")
    ws = [{**w, "id": str(w["i"])} for w in json.load(open(p))]
    for key, text in (e.get("fix") or {}).items():
        c, rng = key.split(":", 1) if ":" in key else (e["_default_clip"], key)
        if c != cid:
            continue
        a, b = (int(x) for x in rng.split("-")) if "-" in rng else (int(rng), int(rng))
        pos = [k for k, w in enumerate(ws) if w["i"] in range(a, b + 1)]
        if len(pos) != b - a + 1:
            die(f"fix {key!r}: words {a}-{b} are not all in clip {cid}.")
        s0, e0 = ws[pos[0]]["s"], ws[pos[-1]]["e"]
        new = text.split()
        if not new:
            die(f"fix {key!r}: give the words actually said.")
        step = (e0 - s0) / len(new)
        raw = " ".join(ws[k].get("raw", ws[k]["w"]) for k in pos)
        repl = [{"i": a, "id": str(a) if k == 0 else f"{a}.{k}", "w": t, "raw": raw if k == 0 else "",
                 "s": round(s0 + k * step, 3), "e": round(s0 + (k + 1) * step, 3)}
                for k, t in enumerate(new)]
        ws = ws[:pos[0]] + repl + ws[pos[-1] + 1:]
    return ws


def ref(e, r):
    """A word reference: 14 (default clip) or "b:14"."""
    if isinstance(r, int):
        return e["_default_clip"], r
    if isinstance(r, str) and ":" in r:
        c, n = r.split(":", 1)
        return c, int(n)
    if isinstance(r, str) and r.isdigit():
        return e["_default_clip"], int(r)
    die(f"bad word reference {r!r}; use 14 or \"clip:14\".")


# ---------------------------------------------------------------------------------------------
# transcribe
# ---------------------------------------------------------------------------------------------

def speech_regions(path):
    """Where someone is actually talking, in seconds, from the Silero VAD bundled with
    faster-whisper. A loudness threshold cannot do this on street footage: traffic is as loud as
    the voice."""
    from faster_whisper.audio import decode_audio
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    audio = decode_audio(path, sampling_rate=16000)
    ts = get_speech_timestamps(audio, VadOptions(min_silence_duration_ms=160, speech_pad_ms=40))
    return [(t["start"] / 16000.0, t["end"] / 16000.0) for t in ts]


def refine(words, regions):
    """Pull every word's edges in to the speech region it mostly sits in.

    Whisper's word timestamps close every pause: the word before a breath simply runs until the
    next word starts, so "but" can span two seconds. Cut on that and the cut lands inside a
    "word", and no pause is ever found to tighten.
    """
    out = []
    for w in words:
        s, e = w["s"], w["e"]
        best, ov = None, 0.0
        for a, b in regions:
            o = min(e, b) - max(s, a)
            if o > ov:
                best, ov = (a, b), o
        if best:
            s2, e2 = max(s, best[0]), min(e, best[1])
            if e2 - s2 >= 0.06:
                s, e = s2, e2
        out.append({**w, "s": round(s, 3), "e": round(e, 3), "s0": w["s"], "e0": w["e"]})
    return out


def cmd_transcribe(a):
    e = load_edit(a.edit)
    from faster_whisper import WhisperModel
    model = None
    for cid, path in e["clips"].items():
        out = words_path(e, cid)
        if os.path.isfile(out) and not a.force:
            words = json.load(open(out))
        else:
            if model is None:
                model = WhisperModel(a.model, device="cpu", compute_type="int8")
            segs, _ = model.transcribe(path, word_timestamps=True, language=e.get("language"),
                                       vad_filter=False,
                                       initial_prompt=e.get("vocabulary") or None)
            words = []
            for s in segs:
                for w in s.words or []:
                    t = w.word.strip()
                    if t:
                        words.append({"i": len(words), "w": t, "s": round(w.start, 3),
                                      "e": round(w.end, 3)})
            words = refine(words, speech_regions(path))
            json.dump(words, open(out, "w"), indent=0)
        if words and "s0" not in words[0]:
            words = refine(words, speech_regions(path))
            json.dump(words, open(out, "w"), indent=0)
        print(f"\n== clip {cid} ({os.path.basename(path)}), {len(words)} words")
        line = []
        for w in words:
            nxt = words[w["i"] + 1]["s"] if w["i"] + 1 < len(words) else w["e"]
            pause = f" |{nxt - w['e']:.1f}s|" if nxt - w["e"] >= 0.3 else ""
            line.append(f"{w['i']}:{w['w']}{pause}")
            if w["w"][-1:] in ".?!" or len(line) >= 12:
                print(f"  [{words[w['i'] - len(line) + 1]['s']:7.2f}s] " + " ".join(line))
                line = []
        if line:
            print(f"  [{words[-len(line)]['s']:7.2f}s] " + " ".join(line))


# ---------------------------------------------------------------------------------------------
# timeline: keep ranges -> cut list -> word times on the output clock
# ---------------------------------------------------------------------------------------------

def build_timeline(e):
    tighten = float(e.get("tighten", 0.35))
    lead, tail = 0.10, 0.18
    cuts, out_words, t = [], [], 0.0
    for kr in e.get("keep") or []:
        cid = kr.get("clip", e["_default_clip"])
        allw = load_words(e, cid)
        f0, t0 = int(kr["from"]), int(kr["to"])
        sel = [k for k, w in enumerate(allw) if f0 <= w["i"] <= t0]
        if not sel:
            die(f"keep {cid}:{f0}-{t0} selects no words of clip {cid}.")
        ws, f, to = allw, sel[0], sel[-1]
        lo = ws[f]["s"] - lead
        if f > 0:
            lo = max(lo, (ws[f - 1]["e"] + ws[f]["s"]) / 2)
        spans, cur = [], [max(0.0, lo), None]
        for k in range(f, to):
            gap = ws[k + 1]["s"] - ws[k]["e"]
            if gap > tighten:
                cur[1] = ws[k]["e"] + tighten / 2
                spans.append(cur)
                cur = [ws[k + 1]["s"] - tighten / 2, None]
        hi = ws[to]["e"] + tail
        if to + 1 < len(ws):
            hi = min(hi, (ws[to]["e"] + ws[to + 1]["s"]) / 2)
        cur[1] = hi
        spans.append(cur)
        for a0, b0 in spans:
            nf = max(1, round((b0 - a0) * FPS))
            d = nf / FPS
            cuts.append({"clip": cid, "a": round(a0, 3), "dur": round(d, 4), "frames": nf,
                         "out": round(t, 4)})
            for k in range(f, to + 1):
                w = ws[k]
                if a0 - 1e-6 <= w["s"] < a0 + d:
                    out_words.append({"ref": f"{cid}:{w['id']}", "w": w["w"],
                                      "raw": w.get("raw", w["w"]),
                                      "s": round(t + w["s"] - a0, 3),
                                      "e": round(min(t + d, t + w["e"] - a0), 3)})
            t += d
    if not cuts:
        die("EDIT.json `keep` is empty: nothing to cut.")
    return cuts, out_words, round(t, 4)


def gap_times(out_words):
    """For each kept word: the gap boundary before it and after it, on the output clock."""
    idx = {w["ref"]: k for k, w in enumerate(out_words)}
    before, after = [], []
    for k, w in enumerate(out_words):
        before.append(0.0 if k == 0 else (out_words[k - 1]["e"] + w["s"]) / 2)
        after.append(w["e"] if k == len(out_words) - 1 else (w["e"] + out_words[k + 1]["s"]) / 2)
    return idx, before, after


def snap(t, joins):
    """Land an edge on a frame, and on a join in the footage when one is within 4 frames.

    A card that ends two milliseconds after a join shows one frame of the old shot and then cuts
    again: two cuts a frame apart, which reads as a glitch. Snapped, both happen on one frame.
    """
    t = round(t * FPS) / FPS
    near = [j for j in joins if abs(j - t) <= 4 / FPS]
    return round(min(near, key=lambda j: abs(j - t)), 4) if near else round(t, 4)


def span(e, item, idx, before, after, total, what, joins=()):
    for key in ("at", "until"):
        if key not in item:
            die(f"{what} needs `at` and `until` word references.")
    ca, na = ref(e, item["at"])
    cu, nu = ref(e, item["until"])
    ka, ku = idx.get(f"{ca}:{na}"), idx.get(f"{cu}:{nu}")
    if ka is None or ku is None:
        die(f"{what}: word {item['at']} or {item['until']} is not inside a `keep` range.")
    s, t = snap(before[ka], joins), snap(after[ku], joins)
    if ku == len(before) - 1:
        t = total
    if t - s < 0.6:
        die(f"{what}: {t - s:.2f}s is too short to read; widen `until`.")
    return s, t


# ---------------------------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------------------------

def frame_for(args):
    kind, spec, i, n, out = args
    import look
    look.CARDS[kind](i, n, spec).convert("RGB").save(out, compress_level=1)
    return out


def render_card(e, k, c, dur, jobs):
    import look
    kind = c.get("kind")
    if kind not in look.CARDS:
        die(f"card {k}: `kind` must be one of {sorted(look.CARDS)}, got {kind!r}.")
    if kind == "stat" and c.get("value") is not None and not c.get("source"):
        die(f"card {k}: a stat needs `source`. A figure on screen without where it came from is a "
            f"claim the video cannot back up.")
    d = os.path.join(e["_work"], f"card{k}")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    n = max(3, round(dur * FPS))
    spec = dict(c)
    if spec.get("geojson") and not os.path.isabs(spec["geojson"]):
        spec["geojson"] = os.path.join(e["_base"], spec["geojson"])
    if kind == "map":
        # Fetch every plate here, once, before the frame workers start: tile servers want light,
        # serial use, and the workers then read the plates from the disk cache.
        pts = look.load_shape(spec)
        lat = sum(p[0] for p in pts) / len(pts)
        lon = sum(p[1] for p in pts) / len(pts)
        vw = look.MAP_BOX[2] - look.MAP_BOX[0] - 2 * look.MAP_PAD
        vh = look.MAP_BOX[3] - look.MAP_BOX[1] - 2 * look.MAP_PAD
        z0, z1 = look.map_zooms(spec, pts, vw, vh)
        for z in range(int(math.floor(z0)), int(math.floor(z1)) + 2):
            look.styled_plate(lat, lon, z)
    tasks = [(kind, spec, i, n - 1, os.path.join(d, f"{i + 1:04d}.png")) for i in range(n)]
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        list(ex.map(frame_for, tasks, chunksize=4))
    mov = os.path.join(e["_work"], f"card{k}.mov")
    run([FFMPEG, "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(d, "%04d.png"),
         "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", mov], f"encode card {k}")
    return mov


def framing(cx):
    cx = min(1.0, max(0.0, float(cx)))
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:(iw-{W})*{cx}:(ih-{H})/2,setsar=1,fps={FPS}")


def render_base(e, cuts):
    """The spoken cut: every kept span framed to 9:16, joined, audio with 12ms join fades."""
    work = e["_work"]
    crops = e.get("crop") or {}
    args, fc, cat = [FFMPEG, "-y", "-v", "error"], [], []
    for k, c in enumerate(cuts):
        args += ["-ss", f"{c['a']:.3f}", "-t", f"{c['dur'] + 0.2:.3f}", "-i", e["clips"][c["clip"]]]
        d = c["frames"] / FPS
        fc.append(f"[{k}:v]{framing(crops.get(c['clip'], 0.5))},trim=end_frame={c['frames']},"
                  f"setpts=PTS-STARTPTS,format=yuv420p[v{k}]")
        fc.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=mono,apad,"
                  f"atrim=duration={d:.4f},asetpts=N/SR/TB,afade=t=in:d=0.012,"
                  f"afade=t=out:st={max(0, d - 0.012):.4f}:d=0.012[a{k}]")
        cat.append(f"[v{k}][a{k}]")
    fc.append("".join(cat) + f"concat=n={len(cuts)}:v=1:a=1[v][a]")
    base, voice = os.path.join(work, "base.mp4"), os.path.join(work, "voice.wav")
    run(args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "libx264", "-crf", "16",
                "-preset", "medium", "-an", base, "-map", "[a]", "-c:a", "pcm_s16le", voice],
        "cut the spoken timeline")
    return base, voice


def render_broll(e, k, b, dur):
    cid = b.get("clip")
    if cid not in e["clips"]:
        die(f"broll {k}: clip {cid!r} is not in `clips`.")
    o = os.path.join(e["_work"], f"broll{k}.mp4")
    nf = max(1, round(dur * FPS))
    run([FFMPEG, "-y", "-v", "error", "-ss", f"{float(b.get('from_s', 0)):.3f}", "-t",
         f"{dur + 0.3:.3f}", "-i", e["clips"][cid], "-vf",
         f"{framing(b.get('crop', 0.5))},trim=end_frame={nf},setpts=PTS-STARTPTS,format=yuv420p",
         "-an", "-c:v", "libx264", "-crf", "16", o], f"cut broll {k}")
    return o


def caption_lines(out_words, start_after):
    lines, cur = [], []
    for k, w in enumerate(out_words):
        cur.append(w)
        nxt = out_words[k + 1] if k + 1 < len(out_words) else None
        chars = sum(len(x["w"]) + 1 for x in cur)
        # Never strand the last word of a sentence on a line of its own: it flashes for a
        # fraction of a second. A line may run to five words to take it.
        tail_word = (nxt is not None and nxt["w"][-1:] in ".?!" and w["w"][-1:] not in ".,?!;:"
                     and nxt["s"] - w["e"] <= 0.35 and len(cur) < 5)
        brk = (nxt is None or ((len(cur) >= 4 or chars > 20) and not tail_word)
               or w["w"][-1:] in ".,?!;:" or nxt["s"] - w["e"] > 0.35)
        if brk:
            lines.append(cur)
            cur = []
    out = []
    for n, ln in enumerate(lines):
        nxt_start = lines[n + 1][0]["s"] if n + 1 < len(lines) else ln[-1]["e"] + LINE_HOLD
        end = min(ln[-1]["e"] + LINE_HOLD, nxt_start)
        states = []
        for j, w in enumerate(ln):
            s = w["s"]
            t = ln[j + 1]["s"] if j + 1 < len(ln) else end
            if t <= start_after:
                continue
            states.append({"active": j, "s": round(max(s, start_after), 3), "e": round(t, 3)})
        if states:
            out.append({"words": [w["w"] for w in ln], "states": states,
                        "end": states[-1]["e"]})
    return out


def render_captions(e, lines, light, total, keys):
    import look
    from PIL import Image
    d = os.path.join(e["_work"], "captions")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    blank = os.path.join(d, "_blank.png")
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    made = {}
    n = round(total * FPS)
    for f in range(n):
        t = (f + 0.5) / FPS
        src = blank
        for ln in lines:
            st = next((s for s in ln["states"] if s["s"] <= t < s["e"]), None)
            if st:
                lt = any(a <= t < b for a, b in light)
                key = (tuple(ln["words"]), st["active"], lt)
                if key not in made:
                    p = os.path.join(d, f"_s{len(made):04d}.png")
                    look.caption(ln["words"], st["active"], lt, keys).save(p)
                    made[key] = p
                src = made[key]
                break
        os.link(src, os.path.join(d, f"{f + 1:04d}.png"))
    mov = os.path.join(e["_work"], "captions.mov")
    run([FFMPEG, "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(d, "%04d.png"),
         "-c:v", "qtrle", "-pix_fmt", "argb", mov], "encode captions")
    return mov


def loudness(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None), (float(p.group(1)) if p else None)


def master_audio(e, voice, total, outro_dur):
    """Voice (+ optional ducked music), padded to the full length, levelled to the target."""
    work = e["_work"]
    target = float(e.get("loudness", -14.0))
    pre = os.path.join(work, "premaster.wav")
    m = e.get("music")
    if m:
        mp = m["path"] if os.path.isabs(m["path"]) else os.path.join(e["_base"], m["path"])
        below = float(m.get("below_lu", 12))
        run([FFMPEG, "-y", "-v", "error", "-i", voice, "-stream_loop", "-1", "-i", mp,
             "-filter_complex",
             f"[0:a]highpass=f=80,apad=whole_dur={total:.3f},asplit[v][sc];"
             f"[1:a]aformat=sample_rates=48000:channel_layouts=mono,volume=-{below + 8}dB,"
             f"atrim=duration={total:.3f},afade=t=in:d=1.2,afade=t=out:st={max(0, total - 1.5):.3f}:d=1.5[m];"
             f"[m][sc]sidechaincompress=threshold=0.08:ratio=5:attack=12:release=380[md];"
             f"[v][md]amix=inputs=2:duration=first:normalize=0,atrim=duration={total:.3f}[o]",
             "-map", "[o]", "-ac", "1", "-c:a", "pcm_s16le", pre], "mix music")
    else:
        run([FFMPEG, "-y", "-v", "error", "-i", voice, "-af",
             f"highpass=f=80,apad=whole_dur={total:.3f},atrim=duration={total:.3f}",
             "-c:a", "pcm_s16le", pre], "pad voice")
    gain = 0.0
    out = os.path.join(work, "master.wav")
    for _ in range(3):
        run([FFMPEG, "-y", "-v", "error", "-i", pre, "-af",
             f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.84:attack=5:release=80:"
             f"level=disabled,aresample=48000", "-ac", "2", "-c:a", "pcm_s16le", out], "master")
        i, _p = loudness(out)
        if i is None or abs(i - target) <= 0.3:
            break
        gain += (target - i) * 1.2
    return out


def cmd_render(a):
    e = load_edit(a.edit)
    import look
    for w in ("Medium", "SemiBold", "Bold", "ExtraBold"):
        look.font(w, 20)
    cuts, out_words, total = build_timeline(e)
    idx, before, after = gap_times(out_words)
    joins = [c["out"] for c in cuts[1:]]
    print(f"cut: {len(cuts)} spans, {len(out_words)} words, {total:.2f}s spoken")

    cards = []
    for k, c in enumerate(e.get("cards") or []):
        s, t = span(e, c, idx, before, after, total, f"card {k}", joins)
        cards.append({**c, "start": s, "end": t})
    cards.sort(key=lambda c: c["start"])
    # A card that starts a breath after a join leaves a sliver of face between two cuts, and one
    # that ends just before a join does the same on the way out. Stretch the card over the sliver.
    for c in cards:
        for j in joins:
            if c["start"] - MIN_SHOT < j < c["start"]:
                c["start"] = j
            if c["end"] < j < c["end"] + MIN_SHOT:
                c["end"] = j
    for x, y in zip(cards, cards[1:]):
        if 0 < y["start"] - x["end"] < MIN_SHOT:
            x["end"] = y["start"]
    for x, y in zip(cards, cards[1:]):
        if y["start"] < x["end"] - 0.01:
            die(f"cards overlap: {x['kind']} ends {x['end']:.2f}s, {y['kind']} starts {y['start']:.2f}s.")
    brolls = []
    for k, b in enumerate(e.get("broll") or []):
        s, t = span(e, b, idx, before, after, total, f"broll {k}", joins)
        # A cutaway next to a card slides 0.06s under it on that side. Cards composite on top,
        # so the real join hides under the card and no sliver of the face flashes between them.
        for c in cards:
            if abs(c["start"] - t) < 0.15:
                t = c["start"] + 0.06
            if abs(c["end"] - s) < 0.15:
                s = c["end"] - 0.06
        brolls.append({**b, "start": round(s, 4), "end": round(min(t, total), 4)})

    hook = e.get("hook") or {}
    hook_end = float(hook.get("hold", 1.8)) + HOOK_FADE if hook.get("text") else 0.0
    keys = set(k.lower() for k in (e.get("captions") or {}).get("keys", []))
    lines = caption_lines(out_words, hook_end)
    light = [[c["start"], c["end"]] for c in cards]

    base, voice = render_base(e, cuts)
    card_movs = [render_card(e, k, c, c["end"] - c["start"], a.jobs) for k, c in enumerate(cards)]
    broll_mp4 = [render_broll(e, k, b, b["end"] - b["start"]) for k, b in enumerate(brolls)]
    cap_mov = render_captions(e, lines, light, total, keys)

    work = e["_work"]
    inputs, fc, pre = ["-i", base], [f"[0:v]setpts=PTS-STARTPTS[s0]"], "s0"
    n = 1
    for k, (b, p) in enumerate(zip(brolls, broll_mp4)):
        inputs += ["-i", p]
        fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{b['start']:.3f}/TB[b{k}];"
                  f"[{pre}][b{k}]overlay=eof_action=pass:enable='between(t,{b['start']:.3f},{b['end']:.3f})'[sb{k}]")
        pre, n = f"sb{k}", n + 1
    for k, (c, p) in enumerate(zip(cards, card_movs)):
        inputs += ["-i", p]
        fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{c['start']:.3f}/TB[c{k}];"
                  f"[{pre}][c{k}]overlay=eof_action=pass:enable='between(t,{c['start']:.3f},{c['end']:.3f})'[sc{k}]")
        pre, n = f"sc{k}", n + 1
    if hook.get("text"):
        hp = os.path.join(work, "hook.png")
        look.hook(hook["text"], hook.get("kicker", "")).save(hp)
        inputs += ["-loop", "1", "-t", f"{hook_end:.3f}", "-i", hp]
        hold = hook_end - HOOK_FADE
        fc.append(f"[{n}:v]format=rgba,fade=t=out:st={hold:.3f}:d={HOOK_FADE}:alpha=1[hk];"
                  f"[{pre}][hk]overlay=eof_action=pass[sh]")
        pre, n = "sh", n + 1
    inputs += ["-i", cap_mov]
    fc.append(f"[{n}:v]format=rgba[cp];[{pre}][cp]overlay=eof_action=pass,format=yuv420p[vout]")
    body = os.path.join(work, "body.mp4")
    run([FFMPEG, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]",
         "-t", f"{total:.4f}", "-c:v", "libx264", "-crf", "17", "-preset", "medium", body],
        "compose")

    outro = e.get("outro") or {}
    outro_dur = float(outro.get("dur", 0)) if outro else 0.0
    parts = [body]
    if outro_dur > 0:
        from PIL import Image
        still = os.path.join(work, "last.png")
        run([FFMPEG, "-y", "-v", "error", "-sseof", "-0.2", "-i", base, "-update", "1", still],
            "grab the last frame")
        im = Image.open(still).convert("RGB")
        od = os.path.join(work, "outro")
        shutil.rmtree(od, ignore_errors=True)
        os.makedirs(od)
        nf = round(outro_dur * FPS)
        for i in range(nf):
            look.outro_frame(im, i, nf - 1, outro.get("text", "")).convert("RGB").save(
                os.path.join(od, f"{i + 1:04d}.png"), compress_level=1)
        om = os.path.join(work, "outro.mp4")
        run([FFMPEG, "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(od, "%04d.png"),
             "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", om], "encode outro")
        parts.append(om)
    full = total + outro_dur
    master = master_audio(e, voice, full, outro_dur)

    out_dir = os.path.join(e["_base"], e.get("out", "renders"))
    os.makedirs(out_dir, exist_ok=True)
    name = e.get("name", "vlog")
    final = os.path.join(out_dir, f"{name}.mp4")
    ins = []
    for p in parts:
        ins += ["-i", p]
    vcat = "".join(f"[{k}:v]" for k in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[v]"
    run([FFMPEG, "-y", "-v", "error", *ins, "-i", master, "-filter_complex", vcat,
         "-map", "[v]", "-map", f"{len(parts)}:a", "-c:v", "libx264", "-crf", "17",
         "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", "-t", f"{full:.4f}", final], "mux")

    plan = {"name": name, "final": final, "duration": round(full, 3), "spoken": total,
            "hook_end": hook_end, "outro": outro_dur, "cuts": cuts,
            "words": [{"w": w["w"], "raw": w["raw"], "s": w["s"], "e": w["e"]} for w in out_words],
            "cards": [{k: v for k, v in c.items()} for c in cards],
            "broll": brolls, "captions": lines}
    pp = os.path.join(out_dir, f"{name}.plan.json")
    json.dump(plan, open(pp, "w"), indent=1)
    print(f"rendered {final} ({full:.2f}s); plan {pp}")


# ---------------------------------------------------------------------------------------------
# qa
# ---------------------------------------------------------------------------------------------

def norm(t):
    return re.findall(r"[a-z0-9]+", t.lower().replace("\u2019", "'"))


def cmd_qa(a):
    e = load_edit(a.edit)
    out_dir = os.path.join(e["_base"], e.get("out", "renders"))
    name = e.get("name", "vlog")
    final, pp = os.path.join(out_dir, f"{name}.mp4"), os.path.join(out_dir, f"{name}.plan.json")
    if not (os.path.isfile(final) and os.path.isfile(pp)):
        die("nothing rendered yet: run `vlog.py render` first.")
    plan = json.load(open(pp))
    report, fails = {"media": final}, []

    # 1. streams and length
    info = probe(final)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v or (v["width"], v["height"]) != (W, H):
        fails.append(f"video stream is not {W}x{H}")
    if not au:
        fails.append("no audio stream")
    dur = float(info["format"]["duration"])
    if abs(dur - plan["duration"]) > 0.1:
        fails.append(f"length {dur:.2f}s, plan says {plan['duration']:.2f}s")
    report["duration"] = dur

    # 2. black frames
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", final, "-vf", "blackdetect=d=0.25:pix_th=0.08",
                        "-an", "-f", "null", "-"], capture_output=True, text=True)
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)
    if blacks:
        fails.append(f"black frames: {blacks}")

    # 3. loudness
    i, p = loudness(final)
    target = float(e.get("loudness", -14.0))
    report["loudness"] = {"integrated": i, "peak": p}
    if i is None or abs(i - target) > 1.0:
        fails.append(f"integrated loudness {i} LUFS, target {target}")
    if p is not None and p > -0.5:
        fails.append(f"peak {p} dBFS is at the ceiling")

    # 4. the cut judge
    jc = os.path.join(out_dir, f"{name}.cut.json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "judge_cut.py"), final, "--plan", pp,
                        "--json", jc, "--ignore-before", "0.5",
                        "--ignore-after", f"{plan['outro'] + 0.2:.2f}"], capture_output=True, text=True)
    print(r.stdout.strip())
    cut = json.load(open(jc))
    report["cut"] = {"cuts": cut["cuts"], "findings": cut["findings"]}
    fails += [f"cut {x['kind']}: {x['detail']}" for x in cut["findings"]]

    # 5. every kept word is still audible
    if not a.no_speech:
        from faster_whisper import WhisperModel
        m = WhisperModel(a.model, device="cpu", compute_type="int8")
        heard = norm(" ".join(s.text for s in m.transcribe(final, vad_filter=False,
                                                           language=e.get("language"))[0]))
        # Compare against what the ASR heard at transcription, not the `fix`ed caption text: the
        # question is whether the cut and the mix lost audio, not whether Whisper can spell.
        want = norm(" ".join(w.get("raw", w["w"]) for w in plan["words"]))
        sm = difflib.SequenceMatcher(a=want, b=heard, autojunk=False)
        got, missing = 0, []
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op == "equal":
                got += a2 - a1
            elif op == "replace" and difflib.SequenceMatcher(
                    None, "".join(want[a1:a2]), "".join(heard[b1:b2])).ratio() >= 0.6:
                got += a2 - a1          # heard, just spelled differently ("claude" / "cloud")
            elif op in ("replace", "delete"):
                missing.append(" ".join(want[a1:a2]))
        recall = got / max(1, len(want))
        report["speech"] = {"recall": round(recall, 3), "expected": len(want), "missing": missing,
                            "heard": " ".join(heard)}
        if recall < 0.95:
            fails.append(f"speech recall {recall:.2f}: not heard in the render: {missing}")

    # contact sheet, to LOOK at
    sheet = os.path.join(out_dir, f"{name}.contact.jpg")
    cols = 8
    rows = max(1, math.ceil(dur * 2 / cols))
    run([FFMPEG, "-y", "-v", "error", "-i", final, "-vf",
         f"fps=2,scale=216:384,tile={cols}x{rows}", "-frames:v", "1", "-q:v", "3", sheet],
        "contact sheet")
    report["contact_sheet"] = sheet
    report["fails"] = fails
    report["pass"] = not fails
    json.dump(report, open(os.path.join(out_dir, f"{name}.qa.json"), "w"), indent=1)
    for f in fails:
        print(f"  FAIL {f}")
    print(("PASS" if not fails else f"FAIL {len(fails)}") + f"  report {name}.qa.json, look at {sheet}")
    sys.exit(0 if not fails else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    t = sub.add_parser("transcribe")
    t.add_argument("edit")
    t.add_argument("--model", default=os.environ.get("VLOG_EDIT_WHISPER", "medium"))
    t.add_argument("--force", action="store_true")
    r = sub.add_parser("render")
    r.add_argument("edit")
    r.add_argument("--jobs", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 1)))
    q = sub.add_parser("qa")
    q.add_argument("edit")
    q.add_argument("--model", default=os.environ.get("VLOG_EDIT_WHISPER", "medium"))
    q.add_argument("--no-speech", action="store_true", help="skip the transcript check")
    a = ap.parse_args()
    {"setup": cmd_setup, "transcribe": cmd_transcribe, "render": cmd_render, "qa": cmd_qa}[a.cmd](a)


if __name__ == "__main__":
    main()
