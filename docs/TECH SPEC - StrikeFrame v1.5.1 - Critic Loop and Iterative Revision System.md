# TECH SPEC - StrikeFrame v1.5.1 - Critic Loop and Iterative Revision System

**Product:** StrikeFrame  
**Version:** v1.5.1  
**Type:** Technical specification  
**Date:** 2026-03-26  
**Status:** Draft

## Purpose
This document defines the critic loop system for StrikeFrame.

The critic loop is the mechanism that turns StrikeFrame from a one-pass renderer into an agent-forward design engine capable of iterative improvement.

Today StrikeFrame can:
- render
- run a review pass
- mark outputs as pass / warn / fail

That is useful, but not enough.

The next system needs to support:
1. render
2. inspect
3. diagnose
4. revise
5. rerender
6. compare
7. stop when the layout meets target quality or no longer improves meaningfully

---

## Why a critic loop is necessary
Without a critic loop, the agent is forced into blind iteration.

That means the workflow becomes:
- guess
- render
- look
- guess again

This is too slow and too unreliable for premium layouts.

A critic loop gives the system a structured way to ask:
- what is wrong?
- where is it wrong?
- which element is causing the issue?
- what revision should happen next?
- did the revision improve the result?

---

## Core product objective
The critic loop should make it possible for StrikeFrame to improve layouts intentionally rather than randomly.

It should reduce waste from brute-force iteration and increase the quality ceiling of agent-generated creative.

---

## Critic loop architecture
The critic loop should have seven stages.

## Stage 1 - Compose
Build the layout using primitives, geometry model, and theme inputs.

## Stage 2 - Render
Generate the asset.

## Stage 3 - Observe
Collect post-render facts.

## Stage 4 - Critique
Score and diagnose the layout.

## Stage 5 - Propose revisions
Generate targeted layout changes.

## Stage 6 - Apply revisions
Update config or primitive state.

## Stage 7 - Compare and decide
Measure improvement and choose whether to continue.

---

## Observation layer
The critic loop requires a strong observation layer.

## Required observation inputs
### 1. Geometry sidecar
From the layout model:
- canvas
- regions
- element rectangles
- text block measurements
- spacing metrics
- overlaps
- occupancy

### 2. Render artifact
The actual output image.

### 3. Primitive metadata
- primitive type
- variant
- role assignments
- asset roles
- theme mode

### 4. Optional benchmark context
- reference ad structure
- expected hierarchy pattern
- target template family

This observation layer is what makes critique grounded rather than speculative.

---

## Critic dimensions
The critic loop should assess layouts across several categories.

## A. Geometry and layout quality
- collisions
- edge violations
- spacing problems
- tangent problems
- canvas imbalance
- occupancy problems
- safe-zone violations

## B. Hierarchy quality
- dominant focal point exists
- primary claim is clearly dominant
- supporting proof is visible but secondary
- CTA is strong but not accidentally dominant unless intended
- logo does not compete with selling element

## C. Readability quality
- quote/headline readable at mobile size
- stars readable
- CTA readable
- proof screenshot readable enough to feel credible
- no tiny secondary text pretending to matter

## D. Persuasion quality
- proof feels believable
- product feels integrated, not pasted on
- layout communicates one main idea
- clutter is low enough to support fast feed comprehension

## E. Benchmark plausibility
- would this plausibly sit beside stronger advertisers?
- does it resemble a known high-performing architecture structurally?
- does it feel like a real ad, not a rendered draft?

---

## Critic output contract
The critic should produce structured output, not only narrative comments.

### Required fields
- `status`
- `overallScore`
- `categoryScores`
- `failures`
- `warnings`
- `diagnosis`
- `revisionTargets`
- `stopRecommendation`

### Example
```json
{
  "status": "warn",
  "overallScore": 6.8,
  "categoryScores": {
    "hierarchy": 6.5,
    "spacing": 7.1,
    "readability": 7.6,
    "proof": 5.9,
    "productIntegration": 5.3,
    "benchmarkPlausibility": 6.2
  },
  "failures": [
    "Review card lacks believable proof treatment",
    "Product cluster appears visually pasted on"
  ],
  "warnings": [
    "CTA may be slightly too quiet for this variant"
  ],
  "diagnosis": "The proof band is structurally correct but visually weak, and the product cluster is not integrated into the composition.",
  "revisionTargets": [
    "review_card",
    "product_cluster"
  ],
  "stopRecommendation": "iterate"
}
```

---

## Critic categories in detail
## 1. Hard-fail checks
These should immediately block approval.

Examples:
- text outside canvas
- CTA outside safe zone
- element collisions that break legibility
- unreadable headline at mobile size
- logo blocking core content

## 2. Structural quality checks
These assess whether the layout architecture is coherent.

Examples:
- no dominant focal point
- primary proof element too small
- supporting element accidentally dominates
- no clear whitespace separation between major blocks

## 3. Persuasion checks
These assess whether the ad is doing real communication work.

Examples:
- proof asset does not feel credible
- CTA style is disconnected from concept
- product role is decorative instead of persuasive
- clutter dilutes the core claim

## 4. Benchmark checks
These assess closeness to a known target pattern.

Examples:
- quote block too small vs reference
- proof band too low on canvas
- product cluster too large for support role
- CTA prominence inconsistent with target family

---

## Revision model
The critic loop should produce revision actions, not only commentary.

### Revision actions should be scoped
Good:
- increase quote size by 8%
- reduce product area by 12%
- move review card upward 20 px
- widen CTA by 48 px
- switch product role from support-large to support-small
- change proof variant to review-dominant

Weak:
- make it better
- improve design
- reduce clutter

---

## Revision action types
### 1. Geometry adjustments
- resize
- move
- align
- rebalance
- add gap
- reduce gap

### 2. Primitive variant changes
- switch variant
- reduce proof density
- increase quote dominance
- demote CTA emphasis

### 3. Asset role changes
- swap proof asset
- swap product role
- use cutout instead of photo
- replace screenshot candidate

### 4. Typography changes
- change size
- change line height
- change wrap width
- change weight
- change style mode

### 5. Theme changes
- increase contrast
- brighten CTA
- darken background
- reduce accent overload

---

## Revision targeting strategy
Not every element should be revised on every loop.

The critic should identify only the highest-leverage revision targets.

### Priority order
1. hard failures
2. dominant focal point issues
3. proof credibility issues
4. readability failures
5. clutter and spacing issues
6. benchmark polish issues

This reduces unnecessary layout churn.

---

## Iteration budget
The critic loop should be bounded.

### Why
Unlimited iteration can waste compute while producing no meaningful improvement.

### Proposed controls
- `maxIterations`
- `maxNoImprovementRounds`
- `targetScore`
- `minimumDeltaToContinue`

### Example
```json
{
  "criticLoop": {
    "maxIterations": 8,
    "targetScore": 8.8,
    "minimumDeltaToContinue": 0.2,
    "maxNoImprovementRounds": 2
  }
}
```

---

## Compare step
After each iteration, the critic should compare the new render to the previous one.

### Compare fields
- previous overall score
- current overall score
- changed categories
- regression categories
- net decision

### Example decision logic
- if score improves and no regressions exceed threshold -> continue if target not met
- if score is flat for two rounds -> stop
- if score regresses in hierarchy or readability -> revert last change

---

## Stop conditions
The loop should stop when one of these is true:
1. target score reached
2. no meaningful improvement remains
3. hard constraints cannot be solved with current assets
4. iteration budget exhausted
5. benchmark gap is asset-limited, not layout-limited

---

## Human escalation conditions
The critic loop should know when to stop and ask for better ingredients.

Examples:
- proof asset too weak to support the intended layout
- product image unusable for support role
- quote too long for this pattern without rewriting
- brand asset missing required logo variant
- layout benchmark cannot be reached with current primitive capabilities

This prevents fake confidence and wasted iterations.

---

## Benchmark-aware mode
The critic loop should optionally run in benchmark mode.

### Inputs
- reference architecture
- target pattern
- hierarchy expectations
- relative role sizes

### Example
For LMNT-style proof hero:
- quote must dominate upper band
- stars must be oversized and immediate
- proof band must feel credible and central
- product must support, not dominate
- CTA may be present but should not disrupt proof structure

### Benchmark output
The critic should report:
- structural similarity
- role emphasis mismatch
- spacing mismatch
- over-complexity delta

---

## Critic implementation modes
## Mode 1 - Rule-based critic
Uses geometry, spacing, safe zones, occupancy, and simple heuristics.

### Strengths
- deterministic
- cheap
- transparent

### Weaknesses
- limited aesthetic sensitivity

## Mode 2 - Hybrid critic
Uses rule-based checks plus reference-aware scoring and design heuristics.

### Strengths
- more useful for premium layout iteration

## Mode 3 - Vision-assisted critic
Uses rendered output plus external or internal multimodal review.

### Strengths
- can catch higher-level visual problems

### Weaknesses
- more variable
- should not replace geometry-based facts

### Recommendation
Use hybrid critic as the default. Vision should be additive, not foundational.

---

## Critic data outputs
Each iteration should emit:
- `<asset>.review.json`
- `<asset>.layout.json`
- `<asset>.critic.json`
- optional `<asset>.debug.png`

### `critic.json` should include
- round number
- input summary
- score summary
- diagnosis
- applied changes
- comparison to prior round
- stop decision

---

## Example iteration trace
### Round 1
- issue: quote too small, proof band too low, product too large
- action: enlarge quote, lift proof, shrink product

### Round 2
- issue: quote improved, CTA now too quiet
- action: widen CTA, increase contrast slightly

### Round 3
- issue: proof still looks weak due to asset quality
- action: swap proof asset candidate

### Round 4
- issue: score flat, benchmark plausibility capped by proof asset
- stop and escalate asset limitation

This is the kind of revision trace agents need.

---

## Primitive-specific critics
Each primitive should have a dedicated critic profile.

### Example `proofHeroQC`
Checks should include:
- quote dominance
- stars immediacy
- proof card credibility
- product support role balance
- CTA subordination or emphasis depending on variant
- clutter score
- benchmark plausibility

### Example `productHeroQC`
Checks should include:
- product focal point
- price/offer visibility
- CTA contrast
- product isolation quality
- text support density

---

## Observability requirements
The critic loop should be inspectable by humans.

### Human-friendly outputs
- concise scorecard
- top 3 failures
- top 3 recommended revisions
- before/after comparison summary

### Machine-friendly outputs
- structured JSON
- stable field names
- primitive-aware diagnosis labels

---

## Risk controls
### 1. Do not let the critic optimize for score hacks
A layout can become technically “better” while becoming visually dead.

### 2. Do not let the critic over-iterate weak assets
Know when asset quality is the real bottleneck.

### 3. Do not rely on vision-only scoring
Vision is useful but should be grounded by geometry and design contracts.

### 4. Do not let the loop mutate too many variables at once
Changes should be scoped and explainable.

---

## Implementation priorities
## Priority 1
- critic output schema
- iteration state model
- compare-and-decide logic
- primitive-specific revision targets

## Priority 2
- benchmark mode
- hybrid scoring model
- stop conditions and escalation logic

## Priority 3
- vision-assisted pass
- revision ranking improvements
- multi-round trace tooling

---

## Open questions
1. Should revision actions mutate raw config, primitive inputs, or both?
2. Should the critic be able to rewrite copy, or only layout and styling parameters in the first version?
3. What score threshold should correspond to “human review required” vs “safe to ship internally”?
4. Should benchmark mode be explicit in config, or inferred from the primitive family and task brief?
5. How should critic traces be surfaced in agent workflows by default?

---

## Summary
The critic loop is what converts StrikeFrame from a renderer into an iterative design engine.

This spec defines:
- the observation layer
- the critic outputs
- the revision action model
- the compare step
- stop conditions
- benchmark-aware review
- primitive-specific QC

With this system in place, agents can stop brute-forcing layout guesses and start improving outputs through structured revision.
