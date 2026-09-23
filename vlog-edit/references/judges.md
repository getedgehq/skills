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

## Voice over music

With a music bed, the voice stem must sit at least 10 dB over the ducked music under every kept
word, measured on the two stems as they meet in the mix. Negative control: the same cut with the
bed at `below_lu: 0` fails on five words. Speech is levelled (`speechnorm`) before the mix,
because two people on one phone mic are not equally loud and a bed that sits fine under the near
voice buries the far one.

## Speech

Whisper on one window per sentence (never the whole file: whole-file passes drop repeated phrases
and drift). Two numbers, kept apart so ASR doubt cannot pose as lost audio:

- **cut recall**: the voice track after cutting, before music, against the kept transcript (the
  ASR text or the `fix`ed text, whichever matches better). A clipped syllable shows up here.
  Fails under 85%; the missing words are listed. Words Whisper was never sure of on the source
  also land here, which is why the bar is not 95%.
- **mix recall** (information): the same windows on the final. On clean audio a gap means the mix
  buried something; on noisy multi-speaker audio it is mostly ASR variance, so the voice-over-music
  margin above is the pass/fail for the mix.

## Contact sheet

`renders/<name>.contact.jpg`, two frames per second. Look at it. The judges catch broken cuts;
they do not know whether a card says the right thing.
