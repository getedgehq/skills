# The judges

`vlog.py qa` runs four checks and exits 1 if any fails. They exist because black-frame, loudness
and transcript checks all pass a cut that flashes, ghosts or freezes.

## Cut judge (`scripts/judge_cut.py`)

Decodes every frame at 270x480 grey.

- **Transitions.** `d[i]` is the mean absolute change into frame i+1. A frame is a transition when
  `d > 8` and it is more than 4x the median change in the surrounding ±0.5 s (its own ±3 frames
  excluded). Walking footage changes a lot every frame; a transition is change that stands out
  against how much this part of the film is moving anyway.
- **GHOST.** Two or more transition frames in a row whose in-between frames are a *blend* of the
  frame before and the frame after (least-squares mix weight between 0.12 and 0.88, residual under
  35% of the difference). That is what a dissolve is. A clean cut followed by camera shake also
  gives several large differences in a row, but its in-between frames look like the new shot, so
  it is not flagged.
- **FLASH / STROBE.** Two cuts less than 0.40 s apart / within two frames.
- **FROZEN / CREEP.** Measured on edges, not the whole frame: the mean change over pixels whose
  gradient exceeds 12. A card is mostly flat colour, so a visible push averages to ~1 on the whole
  frame while street footage scores 30. On edges: card 6-8, map push 11-18, footage 25-37,
  imperceptible under 2.5. FROZEN is under 0.8 for 0.4 s; CREEP is under 3.0 for 0.8 s.
- **OFFBEAT.** A cut more than 60 ms inside a spoken word (word spans from the plan).

Calibration record, from a real series of cuts: the judge flags all ten known defects in a cut
that shipped dissolves and 0.2 s slivers (six GHOST, three FLASH, one FROZEN), and passes the
fixed version and both demos. Re-run that pair whenever the judge changes; a judge that stops
catching the bad cut is worse than none.

## Picture

Size 1080x1920, an audio stream, length within 0.1 s of the plan, no black run over 0.25 s.

## Loudness

EBU R128 integrated loudness within 1 LU of the target (default -14 LUFS), peak below -0.5 dBFS.

## Speech

Whisper on the final file vs the kept words as the ASR originally heard them (so a `fix` does not
count as a loss). Replacements that are close in spelling ("claude" / "cloud") count as heard;
deletions and unrelated replacements do not. Fails under 95% recall and lists what went missing.

## Contact sheet

`renders/<name>.contact.jpg`, two frames per second. Look at it. The judges catch broken cuts;
they do not know whether a card says the right thing.
