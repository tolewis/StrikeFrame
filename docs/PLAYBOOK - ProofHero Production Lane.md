# PLAYBOOK - ProofHero Production Lane

**Product:** StrikeFrame  
**Primitive:** `proofHero`  
**Status:** Shippable production lane for agent-assisted iteration  
**Updated:** 2026-03-27

## Purpose
This playbook lets another agent pick up StrikeFrame and produce ProofHero ads without reverse-engineering the repo.

Success is not "make 25 perfect ads."
Success is:
- generate a controlled 25-variant batch
- hard-fail obviously broken outputs
- review the survivors
- pick the best 5-10
- polish and ship the strongest 1-5

That is the production model.

---

## What ProofHero is for
Use `proofHero` when the ad should lead with:
- testimonial language
- a review screenshot or proof card
- strong credibility signals
- product as supporting evidence, not the hero

This is the right primitive for:
- fighting belts
- tackle products with strong customer feedback
- durability / trust / long-fight / charter-captain style proof-led ads

Do not use ProofHero when the ad needs:
- product-as-hero action imagery first
- a price-led or offer-led layout
- feature-stack education
- comparison-table structure

Those should become other primitives such as `actionHero`, `priceAnchor`, or `comparisonPanel`.

---

## Core files
### Primitive
- `lib/primitives/proofHero.js`

### Canonical configs
- `configs/proofhero-canonical-v1.json`
- `configs/proofhero-canonical-v2.json`
- `configs/proofhero-canonical-v3.json`
- `configs/proofhero-base-v1.json`

### Batch generation and analysis
- `scripts/gen_proofhero_batch.py`
- `scripts/analyze_proofhero_batch.py`
- `scripts/run_proofhero_pipeline.py`

### Batch outputs
- `output/meta-v2/proofhero-batch-v1/`

---

## Current contract
ProofHero currently expects a config shaped like this:

```json
{
  "proofHero": {
    "content": {
      "quote": "When the fish is bigger than you, this is what you want on.",
      "cta": "SHOP FIGHTING BELTS"
    },
    "assets": {
      "reviewPath": "/absolute/path/to/review.png",
      "productPath": "/absolute/path/to/product.jpg"
    },
    "quoteSize": 68,
    "maxQuoteLines": 3,
    "maxQuoteWidth": 760,
    "reviewHeight": 222,
    "productWidth": 250,
    "productHeight": 228
  }
}
```

Important behavior:
- quote should stay at 3 lines or fewer
- widening the quote block is preferred over ugly over-wrapping
- stars sit below the quote
- review card sits below the stars
- product is supporting, not dominant
- CTA must stay inside the safe zone

---

## How to run the lane
### Fast path - generate, render, analyze
```bash
cd "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP"
python3 scripts/run_proofhero_pipeline.py --vision off
```

This will:
1. generate `configs/proofhero-batch-v1.json`
2. render the 25-image batch
3. analyze hard geometry failures
4. write summary artifacts
5. build survivor/failure contact sheets when ImageMagick is available

### With vision review on survivors
```bash
cd "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP"
python3 scripts/run_proofhero_pipeline.py --vision on --model qwen2.5vl:32b
```

Use this when the Popeye/Ollama vision endpoint is reachable.

---

## Output artifacts
After a pipeline run, look for:
- `output/meta-v2/proofhero-batch-v1/proofhero-01.jpg` ... `proofhero-25.jpg`
- `output/meta-v2/proofhero-batch-v1/*.layout.json`
- `output/meta-v2/proofhero-batch-v1/proofhero-batch-analysis.json`
- `output/meta-v2/proofhero-batch-v1/proofhero-pipeline-summary.json`
- `output/meta-v2/proofhero-batch-v1/proofhero-pipeline-summary.md`
- `output/meta-v2/proofhero-batch-v1/proofhero-pass-sheet.jpg`
- `output/meta-v2/proofhero-batch-v1/proofhero-fail-sheet.jpg`

These are the minimum artifacts an agent should use to decide what ships.

---

## How to judge success
### Good enough to move on
ProofHero is considered shipped enough when an agent can:
- run the batch without manual renderer surgery
- get a healthy pool of survivors
- discard broken outputs fast
- review the survivors with AI or human taste
- pick finalists worth polish or launch use

### Not required
Do **not** block shipment on these:
- making all 25 perfect
- eliminating every weird corner case immediately
- building a heavy coded ranking system before the lane is useful

We care about production leverage, not perfection theater.

---

## Recommended operating loop
1. update inputs or variation ranges
2. run the batch
3. read `proofhero-batch-analysis.json`
4. ignore obvious failures
5. use vision review or an LLM to shortlist the survivors
6. polish the best 1-5
7. ship

This primitive is now meant to be used in batches, not as a one-shot renderer.

---

## Variation dimensions to adjust
These are the safest high-value knobs:
- `quoteSize`
- `maxQuoteWidth`
- `reviewHeight`
- `productWidth`
- `productHeight`
- CTA width
- quote copy set
- review asset set
- product image set

Do not immediately open up dozens of new knobs. Controlled variation beats chaos.

---

## Review split: code vs AI
### Code should handle
- batch generation
- render execution
- layout sidecars
- hard geometry checks
- contact sheets
- artifact packaging

### AI should handle
- ranking survivors
- explaining why finalists are better
- identifying which few are worth polish
- final judgment when several options are close

That split keeps code deterministic and uses LLM taste where it actually helps.

---

## Agent handoff checklist
Before saying ProofHero is usable by another agent, verify:
- [ ] `proofHero` primitive exists and renders from current config contract
- [ ] canonical config exists
- [ ] batch generator exists
- [ ] analysis script exists
- [ ] pipeline runner exists
- [ ] summary artifacts are written to output
- [ ] playbook explains how to run and judge the lane

If all of that is true, another agent should be able to pick up the tool and make ProofHero batches without a long oral history transfer.

---

## What comes after ProofHero
Once this lane is stable enough, the next primitive should be:
- `actionHero`

Use the same pattern:
- canonical config
- batch generator
- hard-fail checks
- survivor review
- shortlist and polish
