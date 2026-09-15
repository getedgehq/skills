---
name: reference-first-design
description: >-
  Before designing or building any visual page, collect references, turn them
  into a written design brief with explicit decisions (type, color, layout,
  motion, imagery) and anti-references, get it confirmed, and only then build.
  Use when the user asks for a landing page, website, hero section, redesign or
  "make it look premium", especially when they give no visual direction, or
  share screenshots, Pinterest boards, Dribbble shots or sites they like.
---

# Reference-first design

Asked for "a premium landing page", a model averages every landing page it has
seen: centered headline, gradient blob, three cards, a purple button. The fix
designers use is the same one that works for agents: decide what it should look
like from real references before writing code, and write the decisions down so
they can be checked.

Inspired by the workflow Viktor Oddy (motionsites.ai) demonstrates publicly,
which starts every site from a saved reference image. The process here is
written from scratch.

## 1. Collect references per dimension, not per page

A single "site I like" mixes decisions you want with ones you do not. Collect
two or three references for each dimension separately:

| Dimension | What to look at |
| --- | --- |
| Type | Headline face, weight, size relative to the screen, line length |
| Color | Background, text, one accent. Count the colors actually used |
| Layout | Grid, where the headline sits, how much is empty |
| Imagery | Photo, render, illustration, video; crop; light |
| Motion | What moves, how fast, what triggers it (load, scroll, hover) |
| Density | Words per screen, number of sections |

Sources: what the user shares first. If they share nothing, ask for two sites
or images they like and one they dislike. If they cannot, name three concrete
directions (for example "editorial print", "technical product", "quiet
hospitality") with a real, well-known example of each, and let them pick.

When references are images, look at them. Describe what you see in each, in
one or two lines, before you use them. Do not guess from filenames.

## 2. Strip text from image references

A reference with its own headline pulls the model toward copying that headline
and layout. When a reference image will be used as a generation input (for
example as the first frame of a hero video), remove its text, logos and UI
first with an image-editing model or by cropping. Keep only the scene.

## 3. Write the brief

Write `DESIGN.md` in the project from `templates/DESIGN.md`. Every line is a
decision, not an adjective:

- Bad: "Modern, clean typography."
- Good: "Headline: serif, 96px desktop / 44px mobile, weight 400, max 12
  words, left-aligned in the top-left third."

Include:

- **Anti-references:** the two or three things this page must not look like,
  named concretely ("no gradient blobs", "no three icon cards in a row", "no
  dark overlay on the hero").
- **One signature move:** the single thing someone will remember (a
  scroll-scrubbed video, an oversized number, a hand-drawn line). One, not
  four.
- **Copy constraints:** real words from the brief, never lorem ipsum. Headline
  word limit.

Show the brief to the user and wait for a yes or corrections before building,
unless they said to go ahead without review.

## 4. Build against the brief

- Keep `DESIGN.md` open while building; when a choice is not covered, add it to
  the brief rather than improvising silently.
- After the first full render, take a screenshot at desktop and at 390px wide,
  and compare each decision in the brief against it, line by line. Fix
  mismatches before showing it.

## Do not

- Do not copy a reference's assets, copy, logo or exact layout. References set
  direction; the page is original.
- Do not use an image you do not have rights to in a published site.
- Do not describe the result with words from the brief ("premium", "clean")
  as proof it worked. Show the screenshots.
