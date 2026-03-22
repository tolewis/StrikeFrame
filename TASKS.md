# TASKS

## Done
- Initialized minimal Node project
- Installed renderer dependency (`sharp`)
- Built local banner renderer
- Added JSON-driven render path
- Added platform presets
- Added product-composite template scaffold
- Added design frameworks and layout personalities
- Added shape overlays
- Added multiple text layers
- Added batch manifest rendering
- Added post-render QA/QC review layer
- Added white background removal (flood-fill + soft-mask)
- Added rectangular product image compositing (explainer cards)
- Added gold star (★) and green checkmark (✓) SVG coloring
- Built TOF lifestyle ad batch generator (10 images × 5 variants = 50 ads)
- Built product explainer card batch generator (21 products × 3 variants = 63 cards)
- Added QA/QC pipeline script (pre-render alignment + render + post-render grading)
- Added DESIGN.md with 10 marketing design principles
- Updated SKILL.md with full capability reference
- Produced 50 TOF lifestyle ads — pushed to Dropbox 2026-03-12
- Produced 63 product explainer cards (100% pass QA) — pushed to Dropbox 2026-03-12

## Next
- Build calibration ingestion/eval tooling against `/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/03_calibration/strikeframe-vision/benchmark-manifest.json`
- Stand up Dropbox-backed social-media calibration dataset under `/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/` and absorb `AdExamples-kb` deliberately
- Build Popeye vision-model QA/QC layer with channel/persona thresholds (`docs/PRD-vision-model-qaqc.md`)
- Create fixture set for creative regression testing using external qualified good examples and internal bad/diagnostic misses
- Split monolithic review responsibilities out of `scripts/qaqc.py` before vision integration lands
- Add focal-point crop controls
- Add font tokens / brand theme tokens
- Improve text sharpness and spacing logic
- Expand product image matching (only 21/50 top products matched)
- Add 1080×1350 portrait variant for explainer cards
