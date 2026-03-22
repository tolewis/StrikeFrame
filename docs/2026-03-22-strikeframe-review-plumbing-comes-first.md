# StrikeFrame Review — 2026-03-22

## Asset under review
- Config: `configs/waterfall/2026-03-16_x-best5-strikeframe.json`
- Render target: `output/waterfall/2026-03-16_plumbing-comes-first.jpg`
- Prompt/copy payload:
  - Headline: `Plumbing comes first`
  - Subhead: `GA + Ads + Shopify before lunch. Then 50 articles went live.`
  - CTA: `SYSTEMS`
  - Footer: `@TOLEWIS · CONTENT OPS`

## Reproduction result on current StrikeFrame
- Current renderer still reproduces the same underlying concept cleanly.
- Built-in review output: `pass`
- Built-in composition score: `93/100`
- Review file: `output/waterfall/2026-03-16_plumbing-comes-first.review.json`

## Reality check
This asset is still bad for X.

### Why it fails despite the built-in pass
1. **The visual does not earn the copy.**
   - The copy is about operational plumbing, systems work, and infrastructure.
   - The image presents a generic flowchart/card abstraction that does not feel like a real receipt.
   - It reads as "AI generated business graphic" instead of a lived operator artifact.

2. **The right side is decorative, not informative.**
   - The pipeline boxes, arrows, and chips look like fake-competent dashboard furniture.
   - They don't convey anything concrete enough to justify the message.

3. **It looks like StrikeFrame made it.**
   - This is the exact anti-goal for Tim/X.
   - The image has template smell: blue gradient, generic cards, vague systems motif, no actual proof object.

4. **Current QA is grading geometry, not persuasion.**
   - The built-in review correctly checks spacing, hierarchy, and bounds.
   - It completely misses brand fit, operator credibility, copy-to-visual truth, and stop-scroll value.

## External vision-model review (Popeye)
Model used: `minicpm-v:latest`

### Score
- **3/10**
- **Verdict: rejected**

### Key reasons returned by Popeye
- subpar layout quality
- weak feed-size readability and hierarchy
- visual does not support the copy effectively
- generic AI / cookie-cutter template feel
- awkward disconnected elements (`PIPELINE`, boxes, chips)

## Final judgment
- **Reject for X**
- Do not post assets like this again just because geometry checks passed.
- The current internal QA/QC layer is useful for layout sanity, but it is not sufficient for social creative acceptance.

## Immediate product implication
StrikeFrame needs a second-stage **vision critic** that can fail images for:
- generic template/slop feel
- weak copy-to-visual alignment
- poor stop-scroll value
- lack of concrete proof/receipt feeling
- brand/voice mismatch

That work is captured in:
- `docs/PRD-vision-model-qaqc.md`
