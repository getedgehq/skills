# Remotion and remocn

Use this reference only when the selected implementation is Remotion.

## Project rules

- Keep one root composition with explicit width, height, fps, and duration.
- Derive animation from `useCurrentFrame()` and composition configuration.
- Use `spring()`, `interpolate()`, and maintained primitives deterministically.
- Load fonts and media before render; do not depend on a viewer's machine.
- Seed any intentional randomness.
- Give every scene its own bounded time range and verify boundary frames.

## Reach for remocn first

Remocn is the shadcn-style component library for Remotion. Install a maintained
component from its registry when it matches the intended behavior:

```bash
npx -y shadcn@latest add https://remocn.dev/r/<component>.json
```

Useful mappings:

| Need | Primitive |
| --- | --- |
| Product or code walkthrough | `glass-code-walk` |
| Typed terminal moment | `terminal-cursor-zoom` or `terminal-simulator` |
| Quiet headline entrance | `soft-blur-in` or `tracking-in` |
| Word-by-word statement | `per-word-crossfade` |
| Metric reveal | `rolling-number` |
| Before/after code | `code-diff-wipe` |
| Product device transition | `device-mockup-zoom` |
| Clean scene change | `frosted-glass-wipe` or `directional-wipe` |
| Evidence chart | `animated-bar-chart` or `animated-line-chart` |
| Ecosystem reveal | `logo-enter` |

Use these as behavior primitives, not as a visual identity. Their colors,
spacing, type, and framing must come from the captured product design system.

## When custom animation is justified

Build a custom primitive only when the storyboard depends on a product-specific
spatial idea, a captured UI interaction, or a transition that carries narrative
meaning and no maintained component can express it. Document why the custom
behavior exists and keep it reusable within the project.

## Render gate

- no missing frames or transparent flashes at cuts;
- no layout dependent on browser interaction;
- no clipped type at delivery dimensions;
- no non-deterministic output across repeated renders;
- audio duration and composition duration agree;
- the final MP4 plays from start to finish outside the development viewer.

