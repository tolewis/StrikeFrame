# PLAYBOOK - ActionHero Production Lane

**Product:** StrikeFrame  
**Lane:** `actionHero`  
**Status:** Batch-first production lane  
**Updated:** 2026-03-27

## Purpose
ActionHero is the next lane after ProofHero.

Use it when the ad should win on:
- action image first
- strong hook first
- clear CTA
- product/category urgency
- premium paid-social feel without overbuilding the layout

This lane is intentionally batch-first.
You do not need 25 perfect ads.
You need 25 strong shots on goal, then shortlist the best 5-10 and ship the best 1-5.

---

## Use ActionHero for
- seasonal category pushes
- species-driven action ads
- urgency and speed language
- products where action/outcome beats review-first proof

Examples:
- wahoo gear
- offshore trolling spreads
- aggressive-bite seasonal collections

---

## Core files
- `configs/meta-v2-action-hero-v4.json`
- `scripts/gen_actionhero_batch.py`
- `scripts/run_actionhero_pipeline.py`
- `output/meta-v2/actionhero-batch-v1/`

---

## How to run
```bash
cd "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP"
python3 scripts/run_actionhero_pipeline.py
```

This will:
1. generate a controlled 25-variant ActionHero batch
2. render the full batch
3. build a labeled contact sheet
4. write summary artifacts for agent handoff and finalist review

---

## Current variation dimensions
The v1 ActionHero batch varies:
- headline copy
- CTA copy
- headline size
- headline Y position
- CTA width
- CTA Y position
- overlay vignette strength
- overlay mid opacity
- badge copy and width

That is enough to get a real spread without turning the lane into chaos.

---

## Output artifacts
After a run, look for:
- `output/meta-v2/actionhero-batch-v1/actionhero-01.jpg` ... `actionhero-25.jpg`
- `output/meta-v2/actionhero-batch-v1/actionhero-review-sheet.jpg`
- `output/meta-v2/actionhero-batch-v1/actionhero-pipeline-summary.json`
- `output/meta-v2/actionhero-batch-v1/actionhero-pipeline-summary.md`

---

## Review model
For this lane, do not over-trust the legacy `review.json` banner checks.
They are still biased toward old headline/subhead/CTA assumptions.

Use this split:

### Code handles
- batch generation
- render execution
- packaging outputs for review

### AI or operator handles
- picking finalists
- identifying the strongest hooks
- calling out which variants feel most premium and shippable
- deciding which few deserve final polish

---

## Success criteria
ActionHero is usable when another agent can:
- run the 25-variant batch from one command
- review the labeled sheet
- shortlist finalists without oral history
- polish and ship the best outputs

That is enough to call the lane real.

---

## Next expansions
After ActionHero is stable, likely next lanes are:
- `priceAnchor`
- `proofCard`

Use the same pattern every time:
- canonical config
- batch generator
- review sheet
- shortlist
- polish
- ship
