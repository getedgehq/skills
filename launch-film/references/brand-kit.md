# Brand kit

Lock the brand before the first frame. A film that drifts between logo versions, greys or type weights reads as cheap even when the motion is good.

## What a kit needs

Put these in the project's `assets/brand/` (the starter copies the bundled example there):

- the logo or lockup as SVG, exactly as the owner supplied it;
- `tokens.json`: ink, muted text, line, paper, soft background and one signal colour, plus the card radius;
- the type family and weights, installed locally (no font files go into the skill);
- at most one accent treatment (a pixel type, a mono label, a highlight colour) used once per shot.

Ask for the user's kit if it is not in the brief or the repository. Never regenerate a logo with an image model, never type a wordmark as text, and never invent a mascot.

## Rules that hold for any kit

- One signal colour carries selection and the call to action. Everything else stays neutral.
- Cards are thin and quiet: light border, small radius, nearly invisible shadow.
- Real third-party logos or portraits appear only where the real product, creator or output appears, and only with the right to use them.
- Do not default to green, neon gradients, dark glossy SaaS layouts, terminal walls, fake metrics or oversized black buttons unless the kit itself says so.

## The bundled example: Edge

The files in `assets/brand/` are Edge's own kit, included so the starter renders out of the box. They are an example, not a licence to use Edge's marks as your brand.

- Lockup: `edge-lockup.svg` (the Scout avatar plus the pixel `Edge` word). Scout states: `scout/scout-{neutral,search,found,celebrate,curious}.svg`.
- Colours (`tokens.json`): ink `#12141B`, muted `#747D8D`, cobalt `#154CFF`, line `#DDE5F1`, paper `#FFFFFF`, soft `#F5F8FF`, card radius 9 px.
- Type: Inter, headlines around weight 650 with tight tracking and line height near 1.04. One 5×7 pixel-type accent per shot, drawn as SVG rectangles, not a font.
- Scout is a small flat pixel guide that moves through the scene, never a 3D mascot.
- White and pale sky dominate. Cobalt only marks the selected skill, the route and the destination.
