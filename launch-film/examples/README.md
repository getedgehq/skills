# Example films

Three 16.9-second launch films for Edge skills were made with this skill using the one-stage path in `references/one-stage-film.md`. They are authored demonstrations: the prompt, the "picked" chip and the outputs on screen are written for the film, not recordings of a live run. People and companies on screen are fictional.

| film | made in | final render | QA |
| --- | --- | --- | --- |
| fede-voice v4 ("AI kept making me sound like this.") | Claude Code, Claude Opus 5.5, one session of about an hour on 2026-10-03 that also made client-comms | HyperFrames on AWS Lambda, $0.0212 | 1920x1080, 30 fps, 507 frames, -16.1 LUFS, -1.8 dBTP, `hyperframes check` 0 errors, 0 flashes |
| client-comms v4 ("why does it take me 5 prompts to write this every time?") | same session | HyperFrames on AWS Lambda, $0.0220 | 1920x1080, 30 fps, 507 frames, -16.2 LUFS, -1.4 dBTP, 0 errors, 0 flashes |
| inbound-triage v4 ("127 unread. which ones need me?") | Claude Code, Claude Opus 5.5, one session of about 20 minutes on 2026-10-03, reusing the system above | HyperFrames on AWS Lambda, $0.0186, the only render | 1920x1080, 30 fps, 507 frames, -16.2 LUFS, -1.4 dBTP, 0 errors, 0 flashes |

What the agent did in those sessions: read this skill, built each film as one live HTML stage with one GSAP timeline, wrote and mastered an original 128 BPM score per film with the bundled synth recipe and sound effects, rendered on Lambda, checked the stills, fixed what it saw and rendered again. Three earlier renders of the first two films were discarded because emoji and ✕ rendered as empty boxes on Lambda (about $0.07 together); that trap is now in the reference.

What a person did: wrote the brief, approved the story and copy from an earlier storyboard round, and asked for cleaner transitions after watching the previous version. Nobody edited the films in a video editor.

## Motion passes (v1.1.0)

Two existing films were given the motion layer that is now `assets/motion/motion-kit.js` (see `references/motion-kit.md`). Every beat, cut, caption, number, logo and end card was kept; only motion, light and per-event sound were added. Both were made in Claude Code with Claude Opus 5.5 on 2026-10-05 and rendered with HyperFrames on AWS Lambda. Pace is measured with `scripts/pace.py`.

| film | pass | pace before (mean / p50 / static) | pace after | flashes | other QA | renders |
| --- | --- | --- | --- | --- | --- | --- |
| Edge launch film, 67.7 s | v16 to v17: depth field of real Edge UI crops on every scene, per-scene camera keyed to story cues, iris with a lit rim from each click, send and Play, flare and ring on clicks, glyph springs on two statement lines, odometers on real percentages, 50 per-event sounds | 1.60 / 0.07 / 65.8 % | 2.25 / 0.95 / 23.1 % (pilot window 2.15 / 0.99) | 0 | 2031 frames at 30 fps, -16.0 LUFS, -5.7 dBTP; film gate 10 of 11 (the one fail is an OCR false positive on one blurred iris frame); digestibility 86.3 (A), v16 87.2 on the same plan | 9 Lambda renders including 4 beat pilots, $1.81 |
| inbound-triage skill film, 16.9 s | v5 to v6: three depth fields of the film's own inbox rows, skill card and result, camera on the board plane (pull-back, glide, kick on the stamp, pan, push, rest while read), flares on 4 events, iris from the flip point, glyph springs on the line and end headline, 27 per-event sounds | 0.57 / 0.03 / 89.1 % | 2.53 / 1.56 / 1.6 % (pilot window 2.60 / 1.34), no second under 0.92 | 0 | 507 frames, -16.3 LUFS, -1.7 dBTP; film gate 11 of 11; digestibility 59.1 (D), unchanged from v5 because every beat is under its read time (copy and length were locked) | 3 Lambda renders (one 7 s pilot, two full), $0.25 |

What the agent did: wrote the kit as a pure function of the master clock, built the depth fields from crops of the film's own earlier render, keyed the camera to the existing cue table, piloted one window, tuned pace from local seek frames (the local estimate matched Lambda within 0.01), rendered, ran the gate and the digestibility audit, fixed contrast and action-safe findings (shallower pushes, darker muted grey) and rendered again. What a person did: asked for more movement, at the pace of a reference film we had measured, and kept the copy and length locked. Neither film got a blind outside review.
