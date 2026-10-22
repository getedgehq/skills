#!/usr/bin/env python3
"""Transcribe clips with ElevenLabs Scribe (word timestamps, diarization, audio events).

  transcribe.py CLIP [CLIP ...]          one-shot
  transcribe.py --watch [DIR]            transcribe every new clip in DIR (default $REEL_WORK/clips),
                                         stop after --idle-min minutes with nothing new

Writes $REEL_WORK/transcripts/<clip stem>.json (the full Scribe response). Cached: an existing
transcript is never re-uploaded. Audio is extracted with PyAV (mono 16 kHz), so no ffmpeg
binary is needed on this step. Needs ELEVENLABS_API_KEY in the environment.

Scribe call adapted from video-use helpers/transcribe.py (MIT, see THIRD_PARTY_NOTICES.md).
"""
import argparse, json, os, sys, tempfile, time, wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
EXTS = {".mov", ".mp4", ".m4v"}


def extract_audio(video, dest):
    import av, numpy as np
    c = av.open(str(video)); a = c.streams.audio[0]
    rs = av.AudioResampler(format="s16", layout="mono", rate=16000); buf = []
    for f in c.decode(a):
        for r in rs.resample(f):
            buf.append(r.to_ndarray().reshape(-1))
    for r in rs.resample(None):
        buf.append(r.to_ndarray().reshape(-1))
    pcm = np.concatenate(buf).astype(np.int16)
    w = wave.open(str(dest), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(pcm.tobytes()); w.close()


def call_scribe(audio, key, language=None, num_speakers=None):
    import requests
    data = {"model_id": "scribe_v1", "diarize": "true", "tag_audio_events": "true",
            "timestamps_granularity": "word"}
    if language:
        data["language_code"] = language
    if num_speakers:
        data["num_speakers"] = str(num_speakers)
    with open(audio, "rb") as f:
        r = requests.post(SCRIBE_URL, headers={"xi-api-key": key},
                          files={"file": (audio.name, f, "audio/wav")}, data=data, timeout=1800)
    if r.status_code != 200:
        raise RuntimeError(f"Scribe returned {r.status_code}: {r.text[:300]}")
    return r.json()


def transcribe_one(video, out_dir, key, language=None, num_speakers=None):
    out = out_dir / f"{video.stem}.json"
    if out.exists():
        print(f"cached: {out.name}"); return out
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / f"{video.stem}.wav"
        extract_audio(video, wav)
        payload = call_scribe(wav, key, language, num_speakers)
    out.write_text(json.dumps(payload, indent=2))
    print(f"saved {out.name}: {len(payload.get('words', []))} words in {time.time() - t0:.1f}s")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*", type=Path)
    ap.add_argument("--watch", nargs="?", const="", default=None)
    ap.add_argument("--idle-min", type=float, default=60)
    ap.add_argument("--language", default=None)
    ap.add_argument("--num-speakers", type=int, default=None)
    a = ap.parse_args()
    key = os.environ.get("ELEVENLABS_API_KEY") or sys.exit("ELEVENLABS_API_KEY is not set")
    lang = a.language if a.language is not None else (rmconf.get("REEL_LANGUAGE") or None)
    out_dir = rmconf.work() / "transcripts"; out_dir.mkdir(parents=True, exist_ok=True)
    if a.watch is None:
        if not a.clips:
            ap.error("give clips or --watch")
        for v in a.clips:
            transcribe_one(v.resolve(), out_dir, key, lang, a.num_speakers)
        return
    src = Path(a.watch) if a.watch else rmconf.work() / "clips"
    last_new = time.time()
    while time.time() - last_new < a.idle_min * 60:
        did = False
        for v in sorted(src.iterdir()):
            if v.suffix.lower() in EXTS and not (out_dir / f"{v.stem}.json").exists():
                time.sleep(20)  # let a copy in progress finish
                try:
                    transcribe_one(v, out_dir, key, lang, a.num_speakers); did = True
                except Exception as e:
                    print(f"failed {v.name}: {e}")
        if did:
            last_new = time.time()
        else:
            time.sleep(15)
    print("watch: idle, stopping")


if __name__ == "__main__":
    main()
