# StrikeFrame

Version: **v0.5.1**

Local renderer for banners, social graphics, and simple product composites.

Status: **PROJECT COMPLETE (v0.5.1 scope)**

## What it does
- renders marketing graphics locally
- uses JSON config files
- supports reusable size presets
- supports design frameworks, typography, button styles, layout personalities, and grouped CTA placement
- supports shape overlays, multiple text layers, batch rendering, and single-pass QA/QC review
- avoids GUI-tool dependency for simple asset generation

## Core idea
StrikeFrame should feel like an inspiring default design system, not a blank utility.

But the examples in this repo are **references, not the lane markers**.
If agents overfit to the examples, all output will look the same. That is failure, not consistency.

## Design philosophy
- Use examples to understand what is possible
- Build new layouts intentionally for the job at hand
- Do not blindly reuse the same layout, same photo, same left-text stack, or same CTA treatment
- Treat buttons and button labels as one grouped component
- Prefer brand-aware adaptation over rigid template reuse

## Layout personalities
- `editorial-left`
- `centered-hero`
- `split-card`

## Featured examples

### TackleRoomSupply 2030
![tackleroomsupply-2030](./examples/featured/tackleroomsupply-2030.jpg)

### Contractor-AI 2030
![contractor-ai-2030](./examples/featured/contractor-ai-2030.jpg)

### Unhook Outdoors 2030
![unhookoutdoors-2030](./examples/featured/unhookoutdoors-2030.jpg)

### Editorial Premium
![editorial-premium](./examples/featured/editorial-premium.jpg)

## QA/QC review layer
StrikeFrame runs a **single-pass review after file creation**.

It does **not** auto-rerender in a loop. It renders once, inspects once, writes a review file, and reports `pass`, `warn`, or `fail`.

StrikeFrame now includes a calibrated second-stage Popeye critic for benchmarked review and evaluation:
- `python3 scripts/vision_review.py <image> --channel x --persona tim-operator ...`
- `python3 scripts/qaqc.py <config> --vision on --channel x --persona tim-operator`
- `python3 scripts/qaqc.py <config> --vision required --channel x --persona tim-operator`

Review output:
- `<asset>.review.json`
- `<asset>.vision-review.json`

Checks include:
- headline/subhead/CTA fit inside the intended primary region
- panel padding
- spacing between headline/subhead/CTA/footer
- text-layer canvas overflow

## Review process
Do not trust the first render blindly.

Before calling an asset done, check:
- headline stays inside the intended composition area
- text does not overflow card/panel treatments
- CTA remains readable and visually distinct
- hierarchy reads fast on mobile
- colors feel modern, not muddy or dated
- image + typography mood match the brand/use case
- if the first render looks off, adjust the config and rerun once intentionally

## Run
- `npm install`
- `npm run render`
- `npm run render:square`
- `npm run render:linkedin`
- `npm run render:product`
- `npm run qaqc`
- `npm run qaqc:vision`
- `npm run calibration:eval`

## ProofHero production lane
ProofHero is the first serious primitive-backed production lane.

Primary docs:
- `docs/PLAYBOOK - ProofHero Production Lane.md`
- `configs/proofhero-canonical-v1.json`
- `scripts/run_proofhero_pipeline.py`

Fast path:
- `python3 scripts/run_proofhero_pipeline.py --vision off`
- `python3 scripts/run_proofhero_pipeline.py --vision on --model qwen2.5vl:32b`

This lane is designed to:
- generate a controlled 25-variant batch
- hard-fail obviously broken outputs
- let an AI or operator shortlist the survivors
- polish and ship the strongest 1-5

## ActionHero production lane
ActionHero is the next batch-first lane after ProofHero.

Primary docs:
- `docs/PLAYBOOK - ActionHero Production Lane.md`
- `configs/meta-v2-action-hero-v4.json`
- `scripts/run_actionhero_pipeline.py`

Fast path:
- `python3 scripts/run_actionhero_pipeline.py`

This lane is designed to:
- generate a controlled 25-variant action-led batch
- package a labeled review sheet
- let AI or an operator shortlist the strongest 5-10
- polish and ship the best 1-5

## Test and config hygiene
- `npm test` — config validation + smoke tests
- `npm run validate:configs` — parse all config JSON and flag missing repo-local refs
- `npm run test:smoke` — render self-contained fixtures and run QA/QC on the batch sample

Validation rules:
- missing repo-local assets = fail
- missing external asset refs (Dropbox/library paths) = warning only
- smoke tests fail only on render crashes or `reviewStatus/final_status = fail`

## Asset contract
- Sample configs are the self-contained test surface and should stay runnable on a clean checkout after `npm install`.
- Many production configs intentionally reference external asset libraries under Dropbox and other local paths; those are real workflow dependencies, not bundled repo fixtures.
- If an asset library moves, fix the config paths or the shared defaults instead of pretending the repo is fully portable.
- Repo-native code/docs/contracts belong here; generated calibration renders and scratch review batches belong in `/mnt/raid/Data/tmp/openclaw-builds/katya/...` until deliberately promoted.
- Dropbox is for verified final creative deliverables, not implementation debris.
- Durable social-media calibration datasets belong in `/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/`; existing `AdExamples-kb` is a registered upstream seed corpus.
- Calibration manifest loader: `python3 scripts/load_calibration_manifest.py` reads the Dropbox-backed benchmark manifest used for StrikeFrame vision calibration.

More examples and experiments live in:
- `configs/frameworks/`
- `configs/styles/`
- `configs/proof/`
- `examples/`
- `skills/`

## Calibration eval
- `python3 scripts/run_calibration_eval.py --limit-good 5 --limit-bad 1`
- Writes durable run outputs to `/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/03_calibration/strikeframe-vision/runs/`

## Release status
- v0.5.1 closes the current StrikeFrame project scope.
- Local render/test/config lane is working.
- Popeye vision review is integrated, benchmarked against external paid-social seeds, and wired to the Dropbox-backed calibration dataset.
- Future improvements are backlog, not blockers for closing this version.
