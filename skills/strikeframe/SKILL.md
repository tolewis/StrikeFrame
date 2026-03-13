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
- product explainer cards (split-panel: product image + feature bullets)
- ad concept exploration
- repeatable creative generation from JSON

## Important rules
Examples are **references**, not defaults to copy blindly.

Do not overfit to sample layouts, sample photos, or sample CTA treatments. If every output looks like the examples, you are using the tool badly.

**Read `DESIGN.md` before building any config.** It contains the marketing design frameworks (visual balance, rule of thirds, horizon awareness, visual hierarchy, reading flow, contrast) that govern every layout decision. These are not optional.

## Working approach
1. **Read DESIGN.md** for the design principles that apply to this render
2. If using a background image, **analyze the image composition first** — identify subject position, horizon line, bright/dark regions, and negative space before choosing a layout personality
3. Choose a preset and a layout personality that fit the job **and** respect the image composition
4. Create or adapt a config — place elements according to visual balance, rule of thirds, and reading flow
5. If the brand exists, match the spirit and modernize it
6. Treat the CTA as a grouped component so the button and label move together
7. **Run QA/QC** instead of the renderer directly: `python3 scripts/qaqc.py configs/your-config.json`
   - Pre-render: auto-detects and fixes stat block alignment, column grid, divider placement
   - Renders via node automatically
   - Post-render: reads review.json, grades composition, attempts one correction pass if fixable
   - Outputs graded report with composition scores
   - Max 1 correction pass — no loops
8. Read the `.qaqc-report.json` for final grades and any remaining warnings
9. If issues remain after QA/QC, adjust config deliberately and rerun once intentionally

## Do not do this
- Do not reuse the same photo over and over
- Do not always put text on the left
- Do not always use the same card/panel treatment
- Do not assume a social post layout is also a good paid-ad layout
- Do not create auto-rerender loops

## Key capabilities
- presets: `social-square`, `social-portrait`, `landscape-banner`, `linkedin-landscape`
- layout personalities: `editorial-left`, `centered-hero`, `split-card`
- design frameworks (DESIGN.md)
- grouped CTA placement (`ctaGroup` for flexible anchoring)
- shape overlays (rectangles, ellipses with rgba fills)
- stat blocks and dividers
- multiple text layers with per-layer font, color, size, wrapping
- rectangular product image compositing (`productImage` — white bg, fit-contain)
- circle-masked product compositing (`productComposite` — bg removal)
- automatic white background removal (flood-fill or soft-mask)
- special character rendering: gold stars (`★` → `<tspan fill="#FFD700">`), green checkmarks (`✓` → `<tspan fill="#4CAF50">`)
- batch manifest rendering (defaults + per-render overrides)
- composition scoring (rule of thirds, visual hierarchy, reading order, edge margins, canvas utilization)
- automated alignment correction (stat block grid snapping, divider alignment)
- single-pass QA/QC with circuit breaker (max 1 correction pass)
- Python batch generators for data-driven ad production (`gen_tof_batch.py`, `gen_explainer_batch.py`)

## Config reference — productImage (explainer cards)
```json
{
  "productImage": {
    "path": "/path/to/product.jpg",
    "x": 20, "y": 580,
    "width": 400, "height": 460,
    "padding": 20
  }
}
```
Renders the product photo on a white background at the specified position. Use with `shapes` rectangles to create split-panel layouts (white product area + dark feature panel).

## Commands
```bash
# Direct render (no QA)
node scripts/render.js configs/sample-batch.json

# QA/QC pipeline (preferred — includes alignment fixes, composition grading)
python3 scripts/qaqc.py configs/sample-batch.json

# Generate TOF lifestyle ad batch (10 images × 5 variants = 50 ads)
python3 scripts/gen_tof_batch.py

# Generate product explainer card batch (top products × 3 variants)
python3 scripts/gen_explainer_batch.py
```
