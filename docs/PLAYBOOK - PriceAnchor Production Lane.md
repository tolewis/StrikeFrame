# PLAYBOOK - PriceAnchor Production Lane

**Product:** StrikeFrame  
**Lane:** `priceAnchor`  
**Status:** Batch-first production lane  
**Updated:** 2026-03-28

## Purpose
PriceAnchor is a paid social lane that leads with price.

Use it when the ad should win on:
- clear price dominance (large, bold price = the hero element)
- deal / value framing
- specific product + price combination
- SAVE badge urgency
- conversion-focused ad copy with direct CTA

This lane is batch-first.
You do not need 25 perfect ads.
You need 25 strong shots on goal, then shortlist the best 5-10 and ship the best 1-5.

---

## Use PriceAnchor for
- promotional price drops
- bundle pricing
- seasonal sale pushes
- direct-response paid social ads
- categories where price + product detail beats a review-first proof

Examples:
- dredge system price points ($289-$699)
- fighting belt bundle pricing ($89-$249)
- wahoo lure kit deals ($49-$149)
- planer bridle kit pricing ($39-$89)

---

## Core files
- `configs/priceanchor-canonical-v4.json` — base config (8.6/10 quality)
- `scripts/gen_priceanchor_batch.py` — batch generator (25 renders, 4 categories)
- `scripts/run_priceanchor_pipeline.py` — full pipeline runner
- `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-batch-v1/` — output artifacts
- `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-copy-sets-v1.json` — copy (headlines, prices, badges, CTAs)
- `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/hero-classification.json` — approved hero image pool

---

## How to run
```bash
cd "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP"
python3 scripts/run_priceanchor_pipeline.py
```

This will:
1. Generate the 25-variant PriceAnchor batch manifest
2. Render the full batch via `render.js`
3. Build a labeled contact sheet (5-column grid)
4. Write summary artifacts for agent handoff and finalist review

---

## Category breakdown
| Category | Count | Slug | Hero images used |
|---|---|---|---|
| Dredge Systems | 7 | `dredge-{n}` | dredges + offshore |
| Fighting Belt Kits | 6 | `belt-{n}` | belts + fight scenes |
| Wahoo Lure Kits | 6 | `lure-{n}` | lures + mahi action |
| Planer Bridle Kits | 6 | `planer-{n}` | planers + offshore |

**Total: 25 renders**

---

## Design spec (PriceAnchor canonical)
| Element | Spec |
|---|---|
| Price textLayer | fontSize 148, fontWeight 900, white, drop shadow |
| Headline | 2-line, fontSize 36, fontWeight 700, 80% white, letterSpacing 2 |
| Description | 1 line, fontSize 28, fontWeight 600, 90% white |
| SAVE badge | fill rgba(232,93,58,0.96), fontWeight 800, fontSize 22, radius 8 |
| CTA button | fill rgba(232,93,58,0.82), fontSize 26, fontWeight 700 |
| Logo | corner-anchor, top-left, 260×60, clearSpace 15, white-card-landscape |
| Overlay | vignette bottom 0.72–0.96, midOpacity 0.12–0.22 |

---

## Current variation dimensions
The v1 PriceAnchor batch varies:
- headline copy (5 per category, rotating)
- price point (5 price points per category)
- badge copy (5 badges per category)
- CTA copy (3 CTAs per category)
- description line (category-specific gear detail)
- hero background image (rotated from approved hero pool)
- overlay vignette strength
- overlay mid opacity
- CTA button width

That is enough variation to identify which price points, copy hooks, and images perform best.

---

## Output artifacts
After a run, look for:
- `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-batch-v1/dredge-01.jpg` … `planer-06.jpg`
- `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-batch-v1/priceanchor-review-sheet.jpg`
- `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-batch-v1/priceanchor-pipeline-summary.json`
- `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-batch-v1/priceanchor-pipeline-summary.md`

---

## Image matching rules (critical)
**Only use verified hero images from `hero-classification.json`.**

Category → image mapping:
- `dredge_systems` → images tagged `dredges` (offshore trolling scenes)
- `fighting_belt_kits` → images tagged `belts` (fight scenes, bent rods)
- `wahoo_lure_kits` → images tagged `lures` (mahi action, strike shots)
- `planer_bridle_kits` → images tagged `planers` + `dredges` (offshore context)

Do not use:
- White-background product cutouts
- Non-hero images from the `not_hero` list
- StrikeFrame-rendered ads as backgrounds (baked-in text = corrupted render)

---

## Review model
Do not over-trust automated scoring for this lane.
The price readability, contrast, and visual hierarchy are what matter most.

### Code handles
- batch generation
- render execution
- contact sheet packaging

### AI or operator handles
- verifying price legibility at a glance
- checking image-text contrast on each tile
- identifying which price points and copy combos feel most compelling
- shortlisting the best 5-10 for polish and ship

---

## Success criteria
PriceAnchor is usable when another agent can:
- run the 25-variant batch from one command
- review the labeled contact sheet
- shortlist finalists by price, copy, and image match
- polish and ship the best outputs without oral history

That is enough to call the lane real.

---

## Key rules learned (2026-03-28)
1. **Price is the hero.** fontSize 148 + fontWeight 900 + white + drop shadow. Do not downsize.
2. **Description line = gear detail.** One specific line (lb test, arm count, included items). Not generic marketing.
3. **Badge + headline + price + desc + CTA must all fit without overlap.** Check the review sheet for collision.
4. **Vignette is required.** Without it, white text on bright water becomes unreadable.
5. **Category-image matching matters.** Belt headlines over belt/fight images. Dredge prices over offshore trolling shots.

---

## Next expansions
After PriceAnchor is stable, likely next lanes are:
- `priceAnchor v2` — extended price range, new copy hooks, additional hero images
- `offerStack` — multi-deal layout with stacked price tiers
- `seasonalDrop` — time-limited price anchor with countdown framing

Use the same pattern every time:
- canonical config
- copy sets JSON
- hero-classified image pool
- batch generator
- review sheet
- shortlist
- polish
- ship
