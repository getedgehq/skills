# Editing grammar, and the broken cut behind each rule

Every rule here was learned from a render that a person watched and called broken, fixed, and
then encoded so the engine or a judge enforces it. Keep them; they are cheaper than re-learning.

## Story

- **Transcript first.** Choose the story from the words, then place visuals on words. A timeline
  built from seconds drifts off the speech the first time anything is trimmed.
- **The hook is the thumbnail.** Whatever is on the first frame is what people decide on. While
  the hook is up, nothing else is: a karaoke line under a headline doubles the reading on the
  frame that matters most.
- **One visual per sentence, at most.** "Way too much text" is the most common note. A figure,
  the few words that qualify it, and its source are already three things to read in two seconds.

## Cuts

- **A card is a cut.** A 0.1 s dissolve into a graphic shows the face and the card both
  half-visible for three frames; it reads as a render fault, not as polish.
- **Cut in the gaps.** A cut inside a syllable is felt even when it is not seen. All edges resolve
  to the midpoint of the pause between two words.
- **Never leave a sliver.** A card that ends 2 ms after a join shows one frame of the old shot and
  then cuts again: two cuts a frame apart. Edges snap onto joins, and nothing under 0.45 s
  survives between two cuts.
- **Cutaways slide under cards.** Inserts composite above b-roll, so a cutaway that overlaps the
  card by 0.06 s hides the real join under the card.

## Motion

- **A hold is not motion.** A graphic that finishes building at half time is a still for the rest
  of its beat, and a still held for a second reads as a frozen video. Reveals are spread across
  the whole beat and the whole card pushes in until the last frame.
- **Whole-pixel moves freeze.** Pasting a layer at an integer offset quantises a slow move into
  runs of identical frames. All motion goes through a sub-pixel affine resample.
- **The push scales with length.** The eye reads pixels per frame, so a four-second card needs a
  bigger total move than a two-second one or it creeps.
- **Text never slides; objects travel.** Type fades in place. Cards, map plates, list rows move.
- **Moves leave already moving.** An ease that starts at zero velocity dead-holds for the first
  part of the beat; the push profile opens at a third of cruise speed.

## Numbers and places

- **Every figure has a source on screen.** An unattributed number over footage of real people is
  a claim the video cannot back up.
- **Never count up.** A count-up scrubbed to any frame shows a number nobody counted. Figures
  fade in at their final value.
- **Only print what you can cite.** If you are not sure of a date, a month or a scope, leave it out
  of the copy rather than infer it.
- **A neighbourhood is a shape.** A pin on a city map does not say where a neighbourhood is; its
  boundary does.

## Captions

- One band on every shot, graphic or face, so the eye never hunts for the line.
- Caps, bold, spoken words full, upcoming words dim, the word that carries the line boxed in the
  accent. Navy on light cards, white with a soft shadow on footage.
- The finished line stays up through a breath instead of blinking out.
- Never strand the last word of a sentence alone on a line; it flashes.
- Trust the speaker over the ASR: fix misheard words rather than caption them.
- Captions are what was said, in the language it was said. A translation goes on its own smaller
  line underneath; it never replaces the spoken words.
- White on bright sky is invisible, shadow or not. Footage gets a soft dark ramp under the band.

## Look

- One saturated colour (the accent). Navy ink, white surfaces, a lavender ground, hairline
  borders, a soft navy shadow. Inter Display for everything.
- Graphics fill the frame. A small card floating over empty ground is what makes people ask for a
  face inset; a full-frame graphic does not need one.
