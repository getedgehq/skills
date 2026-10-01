# Review: how Fede judges a post, a short video, a page

When he reviews, he answers in chat: the verdict first ("boring hook", "ship it", "too busy"), then the two or three fixes that matter, then a fixed version if it's short. Not a scorecard. Run `scripts/check_copy.py` on any copy first; its hard failures are non-negotiable.

## A post (LinkedIn first, X the same idea)

**The hook gate.** Read the first line alone. It passes only if all four hold:

1. 8 to 10 words.
2. Contains a digit.
3. A statement, not a question. Question openers measurably lose.
4. Opens a loop it doesn't close: a curiosity gap or a contrarian claim.

Then:

- **Copied, not invented.** The hook follows a shape that already worked (his own best posts or a measured public template). Name the donor when you hand him a draft. If you can't name one, you invented it.
- **Problem before product.** The first two lines are the reader's situation in their own words. The product name comes after. Swap in a competitor's name: if the post still reads the same, it says nothing.
- **Results, not features.** "Found 10 customers", not "advanced AI-powered prospecting".
- **Short.** Around 150 to 170 words. Line breaks, one beat per line, no essay prose.
- **Ends on the last real fact.** No tidy summary, no "what do you think?", no writerly closer.
- **Links the website, never a repo**, and is written for operators, not engineers.
- **Every fact has a source.** Names, numbers, dates match the source. An unsupported line gets cut, not softened.
- **Tag** the people and companies the post names.
- **Bans:** em or en dash, "excited to announce", "game changer", "revolutionary", "unlock", disclaimers ("visuals are AI-generated"), uncensored swearing (write "f*ck").

What he says: "boring. no number." / "this sounds super AI generated." / "where is this from?" / "love it, ship it."

## A short video

- **Hook before anything else.** Full-screen, first second. No logo intro, no slow build.
- **Real product, real logo.** No fake badges, no invented UI.
- **No slow zooms.** Little camera movement. Text never slides or drifts: it appears in place (type-on, count, clean swap).
- **One transition language** for the whole film. Simple over busy.
- **Captions on**, with names and brands spelled right even when the speaker or the transcript got them wrong. Spoken German gets German and English captions.
- **Cut the stumbles, the look-downs and repeated takes.** Never cut mid-sentence.
- **Story first** on talking heads: the spoken line carries it, music stays a quiet bed. Mute test: it still makes sense with sound off.
- **End card:** face, the Edge mark, one line, the URL. Nothing else.
- **Check it plays**: audio in sync, the right length, every beat from the storyboard actually in the render.

What he says: "too much going on." / "why is the text moving?" / "cut that look-down." / "hook is late."

## A landing page or skill page

- One clear line on top that a non-technical founder understands. No code stubs, no terminal jargon in marketing visuals.
- Optimistic and selling, still true. Every claim on the page has a source.
- Show the result (before/after, a real output), not a feature list.
- No all-caps monospace micro labels, no em dashes (check the HTML entities too), no generic gradient filler. The Claude orange is for the Claude mark only.
- Mobile first: check it at phone width.
- UI changes start as an image mockup, then code.

What he says: "what does it do in one line?" / "show me the output." / "this looks like every AI site."

## A launch

See `references/launch.md`. Quick test: is it out today, does the hook pass the gate, is there one clear destination, and do we know what we measure tomorrow?
