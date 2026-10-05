# Pace and digestibility

Two measures decide whether the motion pass worked: pace (does the film move?) and digestibility (can a viewer read what it hands them?). They are independent. Motion raises pace; only fewer words or more time raise digestibility.

## The pace metric

`scripts/pace.py` decodes the film with PyAV, converts every frame to grey 320x180 and takes the mean absolute difference between consecutive frames (0 to 255).

```bash
python scripts/pace.py film.mp4                  # whole film
python scripts/pace.py film.mp4 1.0 8.0          # a pilot window
python scripts/pace.py film.mp4 --json pace.json
```

It reports `mean_motion`, the median frame difference `p50`, `p90`, `static_pct` (frames that differ by less than 0.4, which look frozen), `cuts` (difference over 28), `flashes` (frame X differs by more than 20 from both neighbours while they agree within 6) and `per_second`.

Read it like this:
- **p50 is the tell.** A film whose median frame is frozen (p50 under about 0.1) feels static however big its moves are. A film where something always drifts sits at 0.6 to 1.6.
- **Mean 2.2 to 3.7 is the working range** for a 15 to 70 second launch film. A pilot over about 6 means the camera never rests.
- **No second under about 0.9 outside the end card** is a good target for a short film.
- **Flashes must be 0.**
- **Cuts** are fine when they are planned (an iris between a light and a dark world registers as 2 to 4 cut frames).

A third-party reference launch film we studied (16 s) measured mean 3.1 to 3.2, p50 0.57 to 0.63, about 43 % static. It gets its mean from long fly-throughs between short captions.

## Our measured results

All numbers are from our own films, measured with this script at 30 fps.

| film | pass | mean | p50 | static | flashes |
| --- | --- | --- | --- | --- | --- |
| Edge launch film (67.7 s) | before: flat, v16 | 1.60 | 0.07 | 65.8 % | 0 |
| | pilot window | 2.15 | 0.99 | | 0 |
| | after: motion kit, v17 | **2.25** | **0.95** | **23.1 %** | **0** |
| inbound-triage skill film (16.9 s) | before: v4 | 0.21 | 0.00 | 91.9 % | 0 |
| | before: v5 (new hook) | 0.57 | 0.03 | 89.1 % | 0 |
| | pilot window, 1 to 8 s | 2.60 | 1.34 | 8.1 % | 0 |
| | after: motion kit, v6 | **2.53** | **1.56** | **1.6 %** | **0** |
| customer story film (40.6 s) | before: v15 | 2.24 | 0.38 | 50.9 % | 0 |
| | pilot 1 (camera never rests) | 7.04 | 3.63 | | |
| | pilot after the rest rule | 6.04 | 2.25 | | |
| | after: dark world + camera, v16 | **3.67** | **0.96** | **22.3 %** | **0** (one in render 1, fixed) |

What these passes taught:
- The kit took the triage film from a frozen median (0.03) to 1.56 and from 89 % to 1.6 % static, and every second moves (lowest 0.92, a reading rest).
- The Edge film's mean stopped at 2.25, short of the 3.0 aimed for, because five beats are long reads or typing where the camera rests by rule. Getting higher would have meant moving text or cutting copy. Accept that rather than break the read rule.
- The first pilot of the customer story was twice the reference mean because every move kept going. Landing each move in 0.65 s or less and then holding brought it down without losing the peaks.
- The local seek estimate matched the cloud render within 0.01 (2.61 vs 2.60), so tune pace locally before paying for renders.

## The read-time rule

A beat needs at least

```
max(1.0 s, 0.45 s + 0.30 s per word read + 0.12 s per extra reveal)
```

with muted secondary text (labels, greyed history, table cells) at about 0.12 s per word, and words carried over from the previous beat at half weight. During that time the camera rests and the text does not move. If a beat is short, cut words before adding time: every 0.3 s short is one word too many.

## Copy density, not motion, drives digestibility

We score digestibility from the beat plan (read time 30 %, events per 2 s 20 %, layout 15 %, competing text 15 %, concurrent elements 5 %, churn 15 %; A from 85). The audit tool is not bundled; the rule above is the part that matters most. Three passes show the same thing:

| film | change | pace p50 | digestibility |
| --- | --- | --- | --- |
| inbound-triage v5 to v6 | motion kit added, copy and length locked | 0.03 to 1.56 | **59.1 (D) to 59.1 (D)** |
| Edge launch v16 to v17 | motion kit added, copy locked | 0.07 to 0.95 | 87.2 (A) to 86.3 (A), same plan |
| customer story v16 | words cut (19 to 16 beats, one card from 18 to 9 words, toasts and footnotes removed), slams held longer, same length and motion | about the same | **50.5 (F) to 99.5 (A)** |

In the triage film every one of the 8 beats was under its read time, 10.4 s short in total, so the read score was 0 whatever the motion did. Motion lifted every measure it can reach (pace, layout, churn) and left the grade where the copy put it. Cutting words moved the customer story from F to A without touching the motion.

So: settle the copy against the read-time rule first, then add motion. If the copy and length are locked and the beats are short, say so in the delivery note; motion will not fix it.
