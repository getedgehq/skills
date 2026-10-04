# Example films

Three 16.9-second launch films for Edge skills were made with this skill using the one-stage path in `references/one-stage-film.md`. They are authored demonstrations: the prompt, the "picked" chip and the outputs on screen are written for the film, not recordings of a live run. People and companies on screen are fictional.

| film | made in | final render | QA |
| --- | --- | --- | --- |
| fede-voice v4 ("AI kept making me sound like this.") | Claude Code, Claude Opus 5.5, one session of about an hour on 2026-10-03 that also made client-comms | HyperFrames on AWS Lambda, $0.0212 | 1920x1080, 30 fps, 507 frames, -16.1 LUFS, -1.8 dBTP, `hyperframes check` 0 errors, 0 flashes |
| client-comms v4 ("why does it take me 5 prompts to write this every time?") | same session | HyperFrames on AWS Lambda, $0.0220 | 1920x1080, 30 fps, 507 frames, -16.2 LUFS, -1.4 dBTP, 0 errors, 0 flashes |
| inbound-triage v4 ("127 unread. which ones need me?") | Claude Code, Claude Opus 5.5, one session of about 20 minutes on 2026-10-03, reusing the system above | HyperFrames on AWS Lambda, $0.0186, the only render | 1920x1080, 30 fps, 507 frames, -16.2 LUFS, -1.4 dBTP, 0 errors, 0 flashes |

What the agent did in those sessions: read this skill, built each film as one live HTML stage with one GSAP timeline, wrote and mastered an original 128 BPM score per film with the bundled synth recipe and sound effects, rendered on Lambda, checked the stills, fixed what it saw and rendered again. Three earlier renders of the first two films were discarded because emoji and ✕ rendered as empty boxes on Lambda (about $0.07 together); that trap is now in the reference.

What a person did: wrote the brief, approved the story and copy from an earlier storyboard round, and asked for cleaner transitions after watching the previous version. Nobody edited the films in a video editor.
