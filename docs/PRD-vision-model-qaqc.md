# PRD — Vision Model QA/QC for StrikeFrame

**Product:** StrikeFrame  
**Status:** SHIPPED IN v0.5.0 SCOPE  
**Date:** 2026-03-22  
**Author:** Katya  
**Driver:** Tim rejected a live X asset that built-in StrikeFrame QA scored as `93/pass`, while Popeye multimodal review scored it `3/10 reject`.


## Outcome
This PRD is now shipped for the v0.5.0 project scope at the level required to close StrikeFrame cleanly:
- vision review script exists
- paid-social / generic / X prompt variants exist
- Dropbox-backed calibration dataset exists
- benchmark manifest loader exists
- calibration eval runner exists
- external good seeds and internal bad diagnostics are registered

Remaining work is iterative calibration improvement, not a blocker to call the project shipped.

## 1. Problem
StrikeFrame currently has a geometry-first QA/QC layer.

It is good at checking:
- overflow
- spacing
- hierarchy ratios
- canvas utilization
- region bounds

It is bad at checking:
- generic template/slop feel
- whether the visual actually supports the copy
- whether the asset feels credible for Tim/X
- whether the composition creates stop-scroll value
- whether the image reads like a real operator receipt versus fake-smart decoration

Current failure mode:
- asset passes local QA
- agent treats it as done
- Tim sees it and correctly calls it unusable

That is unacceptable.

## 2. Goal
Add a **vision-model review stage** to StrikeFrame so rendered assets are critiqued by a multimodal model on Popeye before being treated as acceptable.

This stage must be:
- critical by default
- deterministic enough to use in workflows
- structured enough to produce actionable fixes
- strict enough that mediocre assets fail

For Tim/X and high-judgment social work, the bar should be **9/10 or better** before the asset is considered passable without explicit human override.

## 3. Users
- **Katya** — reliable rejection of fake-smart assets
- **Thor** — machine-readable critique and next-step guidance
- **Tim** — should stop seeing obvious StrikeFrame/template slop presented as done

## 4. Non-goals
## 4A. Benchmark policy
The vision reviewer must be calibrated against **external, highly qualified social-media evidence** for what strong paid/social creative looks like.

Do **not** use internal Tim content, legacy StrikeFrame outputs, or our own published posts as the gold standard for great creative. Those are useful as negative cases, edge cases, or regression fixtures — not as proof of excellence.

Primary benchmark sources should come from external knowledge and competitive intelligence, especially:
- `30 Projects/Master Social Media/`
- `30 Projects/TackleRoom/Competitive Ad Intelligence/`
- `30 Projects/TackleRoom/Integrations/Meta Ads API/2026-03-10 - Paid Ads Skill Adoption and Thesis Framework.md`
- Dropbox dataset home: `/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/`
- Existing seed corpus: `/home/tlewis/Dropbox/Tim/Datasets/AdExamples-kb`

Implication:
- **good fixtures** should be sourced from external, qualified examples and research
- **bad fixtures** may include internal misses like the rejected StrikeFrame/X asset

Not in scope for v1:
- automatic infinite rerender loops
- full autonomous creative direction with no human review
- replacing existing layout/overflow checks
- cloud-image-model dependency as primary path

This is an additional critic layer, not a replacement for structural checks.

## 5. Product requirements
### 5.1 Review stages
StrikeFrame QA/QC should become a multi-stage gate:
1. pre-render structural checks
2. render
3. post-render deterministic checks
4. vision-model critique
5. final disposition (`pass` / `warn` / `fail` / `reject-for-channel`)

### 5.2 Required review dimensions
The vision reviewer must explicitly score and comment on:
- overall quality
- readability at feed size
- layout/composition quality
- text hierarchy clarity
- copy-to-visual alignment
- stop-scroll value
- generic template / AI slop risk
- proof/receipt credibility
- channel fit (especially X)
- brand/persona fit (Tim operator voice vs generic business aesthetic)

### 5.3 Strictness
Default reviewer personality should be skeptical and critical, biased toward rejection unless the image earns approval.

### 5.4 Thresholds
Default thresholds:
- **9.0+** = pass
- **7.5–8.9** = warn / needs revision
- **<7.5** = fail
- **<5.0** = reject outright

For `channel = x` and `persona = tim-operator`, require:
- overall >= 9.0
- copy-to-visual alignment >= 9.0
- slop-risk <= low

### 5.5 Output contract
Vision review must emit structured JSON with at least:
- `model`
- `overall_score`
- `channel_fit_score`
- `copy_visual_fit_score`
- `slop_risk`
- `verdict`
- `should_reject`
- `reasons[]`
- `fixes[]`
- `confidence`

File shape:
- `<asset>.vision-review.json`

### 5.6 Human-readable receipt
CLI should print a short summary like:
- `VISION FAIL (3.0/10): generic template slop, weak copy-visual fit, disconnected decorative elements`

## 6. Integration design
### 6.1 Model host
Primary host: **Popeye**

Initial supported local models:
- `minicpm-v:latest` for primary critique
- optional fallback: `llava:7b`

### 6.2 Invocation path
Preferred implementation:
- new Python module/script inside StrikeFrame, e.g. `scripts/vision_review.py`
- called by `scripts/qaqc.py` after render + deterministic review
- talks to Popeye over HTTP/Ollama API

### 6.3 Input bundle to the model
The reviewer should receive:
- rendered image
- headline
- subhead
- CTA
- footer
- channel target (`x`, `linkedin`, etc.)
- optional persona/brand hints
- optional source config path

Without the text intent, the model can only judge aesthetics, not truthfulness of the composition.

### 6.4 Prompt strategy
Use a fixed reviewer prompt with:
- explicit anti-slop stance
- examples of what to reject
- examples of what counts as real proof/receipt energy
- instruction to prefer false negatives over false positives

Need prompt variants by use case:
- X social
- paid social
- LinkedIn
- generic brand creative

## 7. UX / CLI requirements
### 7.1 Commands
Support:
- `python3 scripts/qaqc.py <config>` → includes vision stage when configured
- `python3 scripts/vision_review.py <image> --channel x --headline ...`
- `npm run qaqc` should reflect the multi-stage gate once implemented

### 7.2 Config flags
Need config or CLI switches for:
- `--vision on|off|required`
- `--vision-model minicpm-v:latest`
- `--channel x`
- `--persona tim-operator`
- `--min-score 9`

### 7.3 Failure behavior
If Popeye is unavailable:
- do **not** silently pass
- return degraded state clearly
- for high-judgment channels, treat missing vision review as **incomplete**, not success

## 8. Repo organization requirements
The current repo is workable but still loose. Vision review work should land in a cleaner structure:
- `scripts/vision_review.py` — model call + response parser
- `scripts/review_prompts.py` or `prompts/` — reviewer prompts and channel variants
- `docs/PRD-vision-model-qaqc.md` — this doc
- `docs/review-contract.md` — JSON schema / status model
- `fixtures/` or `test-fixtures/` — known good/bad assets for regression testing
- `tests/` — regression checks for parser and threshold logic

Do not bury critical review logic in one monolithic `qaqc.py` blob forever.

## 9. Acceptance criteria
The feature is not done until all are true:
1. StrikeFrame can produce a machine-readable vision review JSON for a rendered asset.
2. `qaqc.py` can fail a render based on vision-review threshold, not just geometry.
3. A known-bad asset like `2026-03-16_plumbing-comes-first.jpg` fails the vision gate.
4. At least 5 known-good and 5 known-bad fixtures are stored and used as regression cases.
5. Missing Popeye/model availability results in explicit degraded/incomplete status.
6. CLI output makes it obvious whether failure was structural, aesthetic, or both.
7. Tim/X profile can enforce a stricter threshold than generic rendering.

## 10. Risks
### 10.1 Model inconsistency
Multimodal local models are not perfectly consistent.
Mitigation:
- use structured prompts
- keep scoring rubric stable
- regression-test against fixed fixtures

### 10.2 Overcorrection / false negatives
A harsh reviewer may reject some decent assets.
Mitigation:
- acceptable early; false positives are more expensive right now
- allow explicit human override later, but do not lower the default bar

### 10.3 Latency
Vision review adds runtime.
Mitigation:
- acceptable for high-judgment creative workflows
- keep structural checks fast and local first

### 10.4 Monolith creep
Dumping this into `qaqc.py` will create a maintenance swamp.
Mitigation:
- split model I/O, prompts, contracts, and tests into separate files from the start

## 11. Rollout plan
### Phase 1 — Design and contracts
- finalize PRD
- define JSON contract
- define prompt variants
- identify fixture set

### Phase 2 — Minimal working integration
- build `vision_review.py`
- call Popeye model
- save `.vision-review.json`
- wire `qaqc.py` to surface result without blocking

### Phase 3 — Hard gate
- enforce thresholds
- fail bad assets
- add channel/persona-specific strictness

### Phase 4 — Guided revision loop
- convert critic output into actionable render suggestions
- allow one bounded rerender pass for fixable issues
- no autonomous infinite loops

## 12. Immediate next tasks
1. Create review JSON contract doc
2. Build fixture set from **external qualified good examples** plus known-bad internal failures
3. Implement `scripts/vision_review.py` against Popeye `minicpm-v:latest`
4. Wire non-blocking output into `qaqc.py`
5. Add hard-gate mode for X / Tim persona once fixture calibration is done

## 13. Bottom line
StrikeFrame's current QA is good at asking:
- "did the text fit?"

It is bad at asking:
- "should this image exist?"

The Popeye vision-review layer exists to answer the second question.
