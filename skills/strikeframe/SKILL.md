---
name: strikeframe
description: Generate local marketing images, banners, social graphics, and simple product composites with StrikeFrame. Use when an agent needs configurable JSON-driven creative rendering with presets, typography, grouped CTA placement, shape overlays, multiple text layers, or single-pass post-render QA/QC review.
---

# StrikeFrame

Use StrikeFrame when you need to generate marketing graphics locally without depending on a GUI design tool.

## Use it for
- banner graphics
- social images
- waterfall hero images
- simple product/lifestyle composites
- ad concept exploration
- repeatable creative generation from JSON

## Important rule
Examples are **references**, not defaults to copy blindly.

Do not overfit to sample layouts, sample photos, or sample CTA treatments. If every output looks like the examples, you are using the tool badly.

## Working approach
1. Choose a preset and a layout personality that fit the job
2. Create or adapt a config instead of reusing a sample unchanged
3. If the brand exists, match the spirit and modernize it
4. Treat the CTA as a grouped component so the button and label move together
5. Run the renderer once
6. Read the generated `.review.json`
7. If review fails or the design is weak, adjust config deliberately and rerun once intentionally

## Do not do this
- Do not reuse the same photo over and over
- Do not always put text on the left
- Do not always use the same card/panel treatment
- Do not assume a social post layout is also a good paid-ad layout
- Do not create auto-rerender loops

## Key capabilities
- presets
- design frameworks
- grouped CTA placement
- shape overlays
- multiple text layers
- batch manifest rendering
- single-pass QA/QC review

## Typical command
```bash
npm install
node scripts/render.js configs/sample-batch.json
```
