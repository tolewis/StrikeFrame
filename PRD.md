# PRD — StrikeFrame

**Version:** v0.5.0  
**Status:** PROJECT COMPLETE  
**Date:** 2026-03-22

## Product
StrikeFrame

**Internal descriptor:** local media renderer for banners, waterfall graphics, and product/lifestyle composites

## Purpose
Create local, automatable marketing graphics without Canva or external design-app dependency.

## Problem
The content system can write posts, select images, and schedule content, but it lacked a reliable local path for generating actual banner-style graphics and product/lifestyle composites.

That gap caused:
- dependence on manual design tools
- inconsistent visual output
- friction for agents trying to ship full waterfall assets
- no repeatable API-free path for graphics generation

## Users
- Katya — orchestration and creative routing
- Thor — execution of content + asset generation tasks
- Captain Bill — future TackleRoom promo/support asset generation when visual production is required

## MVP scope
### Included
- Local Node.js renderer
- `sharp`-based composition
- JSON config input
- Preset export sizes
- Banner template
- Product-composite template scaffold
- Typography system controls
- Button style controls
- Layout personalities
- Brand-aware framework presets (TackleRoomSupply, Contractor-AI, Unhook Outdoors examples)
- Sample outputs generated from saved stock images
- Agent skill for reuse (`media-renderer`)
- Popeye vision-review integration with external benchmark calibration
- Dropbox-backed social-media calibration dataset + manifest loader
- Calibration eval runner for good/bad benchmark regression checks
- Waterfall system integration docs

### Not included
- Rich typography engine
- batch manifest rendering
- focal-point smart crop logic
- GUI editor
- full ad-creative system with product cutout pipeline

## Presets
- `landscape-banner` — 1600x900
- `social-square` — 1080x1080
- `social-portrait` — 1080x1350
- `linkedin-landscape` — 1200x627

## Templates
- `banner`
- `product-composite`

## Inputs
- background image path
- optional product image path
- preset
- template
- output path
- headline
- subhead
- CTA
- footer

## Outputs
- local JPG render in `output/`
- deterministic rerun command
- skill-driven workflow other agents can call

## Success criteria
- Agent can generate a usable banner locally without Canva
- Agent can rerun graphics creation from JSON config
- Waterfall system knows when to route to the renderer
- Thor and Captain Bill have memory breadcrumbs pointing to this capability

## Shipped proof
- `output/sample-banner.jpg`
- `output/sample-product-composite.jpg`
- `docs/GRADING-RUBRIC.md`
- `scripts/vision_review.py`
- `scripts/run_calibration_eval.py`
- Dropbox calibration manifest at `/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/03_calibration/strikeframe-vision/benchmark-manifest.json`
- Visible GitHub README examples for 4 featured directions:
  - TackleRoomSupply 2030
  - Contractor-AI 2030
  - Unhook Outdoors 2030
  - Editorial Premium
- Repo live: `https://github.com/tolewis/StrikeFrame`

## Integration points
- `skills/media-renderer/`
- `skills/social-content/`
- `31 Content Waterfall System/Media Renderer Integration.md`
- `31 Content Waterfall System/Image Selection Framework.md`

## Future backlog (not blockers for v0.5.0 closeout)
1. Real product PNG/cutout flow
2. Theme tokens and font system
3. Batch rendering from content manifests
4. Platform-safe crop and focal-point controls
5. Ad-creative template set for Meta
