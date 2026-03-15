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
- automated alignment correction (stat block grid snapping, divider alignment, template-specific overflow checks)
- single-pass QA/QC with circuit breaker (max 1 correction pass)
- SVG icon glyphs: shield, check, wave, anchor, gear, arrow, target, fish
- Python batch generators for data-driven ad production (10 generators covering all template types)

## Ad template types (10 total)

| Template | Generator | Config Key(s) | Description |
|----------|-----------|---------------|-------------|
| lifestyle | `gen_tof_batch.py` | (base config) | Lifestyle identity hero — background photo + headline/subhead/CTA |
| explainer | `gen_explainer_batch.py` | `productImage`, `shapes`, `textLayers` | Product image + feature bullets in split-panel layout |
| benefit-stack | `gen_benefit_stack_batch.py` | `benefitStack` | Product hero + 3-4 icon/benefit rows |
| testimonial | `gen_testimonial_batch.py` | `testimonial` | Quote card with stars, attribution, open-quote marks |
| problem-solution | `gen_problem_solution_batch.py` | `splitReveal` | Split layout with PROBLEM/SOLUTION columns and divider |
| offer | `gen_offer_batch.py` | `offerFrame`, `badges` | Price callout with strikethrough, savings badge, offer text |
| comparison | `gen_comparison_batch.py` | `comparisonTable` | Two-column comparison table with highlight column |
| listicle | `gen_listicle_batch.py` | `textLayers` | Numbered benefit/spec lists |
| authority | `gen_authority_batch.py` | `authorityBar` | Serif headline + credibility bar with publication badges |
| contrarian | `gen_contrarian_batch.py` | (base config) | Bold contrarian statement + product reveal |

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

## Config reference — benefitStack
```json
{
  "benefitStack": {
    "startX": 80, "startY": 580, "spacing": 90,
    "iconSize": 36, "iconColor": "#63b3ed",
    "textSize": 28, "textColor": "#ffffff", "textMaxChars": 32,
    "items": [
      { "icon": "shield", "label": "500lb rated hardware" },
      { "icon": "wave", "label": "Built for offshore current" },
      { "icon": "check", "label": "Complete kit, nothing missing" }
    ]
  }
}
```
Icon glyph types: `shield`, `check`, `wave`, `anchor`, `gear`, `arrow`, `target`, `fish`.

## Config reference — testimonial
```json
{
  "testimonial": {
    "quote": "This dredge changed our tournament results.",
    "stars": 5, "starSize": 32,
    "name": "Capt. Mike Henderson",
    "role": "Blue Water Charters, Islamorada",
    "quoteSize": 36, "quoteMaxChars": 28,
    "nameSize": 22, "startY": 300
  }
}
```

## Config reference — splitReveal (problem-solution)
```json
{
  "splitReveal": {
    "dividerX": 540, "startY": 400, "rowHeight": 70,
    "textSize": 22,
    "problemLabel": "THE PROBLEM", "solutionLabel": "THE FIX",
    "items": [
      { "left": "Incomplete planer kits", "right": "Every piece included" },
      { "left": "Wrong bridle size", "right": "Matched to your planer" }
    ]
  }
}
```

## Config reference — offerFrame
```json
{
  "offerFrame": {
    "originalPrice": "$289.99",
    "salePrice": "$224.99",
    "savings": "SAVE 22%",
    "offerText": "FREE SHIPPING OVER $99",
    "salePriceSize": 72,
    "originalPriceSize": 28,
    "priceY": 580
  }
}
```

## Config reference — comparisonTable
```json
{
  "comparisonTable": {
    "startX": 80, "startY": 360,
    "colWidth": 440, "rowHeight": 65,
    "headerSize": 22, "bodySize": 20,
    "highlightCol": "right",
    "leftHeader": "Status Quo", "rightHeader": "TackleRoom",
    "rows": [
      { "left": "3-4 separate orders", "right": "One complete order" },
      { "left": "Mismatched hardware", "right": "Matched 500lb rated" }
    ]
  }
}
```

## Config reference — authorityBar
```json
{
  "authorityBar": {
    "barY": 680, "barHeight": 40,
    "textSize": 13,
    "textColor": "rgba(255,255,255,0.5)",
    "barFill": "rgba(255,255,255,0.06)",
    "publications": ["TOURNAMENT TESTED", "CAPTAIN VERIFIED", "OFFSHORE PROVEN"]
  }
}
```

## Config reference — badges
```json
{
  "badges": [
    {
      "text": "COMPLETE KIT",
      "x": 420, "y": 120,
      "fill": "rgba(40,120,80,0.9)",
      "textColor": "#ffffff",
      "fontSize": 16
    }
  ]
}
```

## Commands
```bash
# Direct render (no QA)
node scripts/render.js configs/sample-batch.json

# QA/QC pipeline (preferred — includes alignment fixes, composition grading)
python3 scripts/qaqc.py configs/sample-batch.json

# Generate all ad batches
python3 scripts/gen_tof_batch.py            # Lifestyle hero ads
python3 scripts/gen_explainer_batch.py       # Product explainer cards
python3 scripts/gen_benefit_stack_batch.py   # Benefit stack ads
python3 scripts/gen_testimonial_batch.py     # Testimonial/social proof cards
python3 scripts/gen_problem_solution_batch.py # Problem-solution reveals
python3 scripts/gen_offer_batch.py           # Offer/price frame ads
python3 scripts/gen_listicle_batch.py        # Numbered benefit lists
python3 scripts/gen_comparison_batch.py      # Comparison table ads
python3 scripts/gen_authority_batch.py       # Authority/credibility ads
python3 scripts/gen_contrarian_batch.py      # Contrarian hook ads
```

## TackleRoom batch generation
All generators import `scripts/tackleroom_defaults.py` which centralizes brand constants (colors, fonts, badges, icon map, category voice, overlay presets).

### Content sources for ad copy

Generators should pull from the full content ecosystem, not just one source:

| Source | Path | What it provides |
|--------|------|------------------|
| Thesis bank | `Competitive Ad Intelligence/06_tackleroom_ad_thesis_bank.md` | 23 actionable theses with hook direction, proof point, CTA, destination, asset concept |
| Hook matrix | `Competitive Ad Intelligence/07_category_hook_matrix.md` | Quick hook/CTA/destination lookup by category (planers, dredges, lures, line/leader, kits) |
| Pattern playbook | `Competitive Ad Intelligence/04_tackleroom_ad_pattern_playbook.md` | 7 reusable ad types mapped to TackleRoom categories with competitor examples |
| Saltwater KB articles | `Dropbox/Tim/Datasets/saltwater-kb/02_clean_md/` | ~7,800 canonical articles (species, gear, technique, tournaments). Searchable via `qmd search "query" --collection saltwater-kb` |
| Fact-checked claims | `Dropbox/Tim/Datasets/saltwater-kb/03_claims/claims_jsonl_reviewed/reviewed_all.jsonl` | 49,115 verified claims with species/region/category tags — embed real facts in copy |
| Truth cards | `Dropbox/Tim/Datasets/saltwater-kb/03_claims/truth_cards/` | ~1,800 species/attribute consensus cards (bait, technique, appearance, achievement) |
| Competitor ads | `Competitive Ad Intelligence/exports/competitor_ads_latest.csv` | 73 active Meta ads with hooks, body copy, angles, landing URLs — reference for tone/structure |
| Customer voice | Thesis 19–23 in thesis bank | Reddit/forum-sourced overlays: "enough not overkill," "buy once not twice," "simple & durable" |

### Content generation workflow
1. Pick category → hook matrix lookup for hooks, proof angles, CTAs
2. Select thesis for strategic direction + proof structure
3. Pull real facts from saltwater-kb (via qmd or claims JSONL) to ground the copy
4. Reference competitor ad patterns for tone calibration
5. Never use generic marketing language — every claim should trace back to a source
