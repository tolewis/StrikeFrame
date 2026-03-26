# TECH SPEC - StrikeFrame v1.5.1 - Design Intent and Constraint Model

**Product:** StrikeFrame  
**Version:** v1.5.1  
**Type:** Technical specification  
**Date:** 2026-03-26  
**Status:** Draft

## Purpose
This document defines the layer above primitives: the authoring model that lets an agent describe **what the creative is trying to do** before StrikeFrame decides how to compose it.

This exists to prevent StrikeFrame from becoming a one-proof engine or a pile of hardcoded layout assumptions.

The long-term top-level unit of the system should not be:
- raw coordinates
- text layers
- image layers
- even primitives alone

It should be:
- **design intent**
- **constraints / policy**
- **assets + capabilities**
- **benchmark profile**
- **channel / placement context**

Primitives are compiled building blocks underneath that layer.

---

## Why this matters
If the system is authored directly through primitive details, it will drift toward hardcoded assumptions like:
- headline always top-left
- proof always center band
- CTA always bottom-left
- product always bottom-right

That is useful for one ad family and dangerous for a production engine.

The design-intent layer keeps the system flexible by letting agents specify:
- goal
- emphasis
- proof style
- product prominence
- CTA aggressiveness
- diversity goals
- benchmark family
- channel constraints

without manually encoding the layout each time.

---

## Top-level model
A future StrikeFrame render request should support a structure like:

```json
{
  "designIntent": {},
  "constraintPolicy": {},
  "benchmarkProfile": {},
  "inputs": {},
  "theme": {},
  "primitive": "proofHero"
}
```

The `primitive` can still be explicit, but over time StrikeFrame should also be able to choose or narrow the primitive family from intent.

---

## Design Intent model
`designIntent` describes the communication job.

## Required fields
- `goal`
- `channel`
- `audience`
- `offerType`
- `proofType`
- `productRole`
- `optimizationTarget`

## Optional fields
- `emphasis`
- `tone`
- `variantStrategy`
- `diversityTarget`
- `riskTolerance`
- `brandProfile`
- `placement`
- `notes`

### Example
```json
{
  "designIntent": {
    "goal": "convert",
    "channel": "paid-social",
    "placement": "feed",
    "audience": "saltwater anglers",
    "offerType": "proof-led",
    "proofType": "review-screenshot",
    "productRole": "supporting",
    "optimizationTarget": "thumb-stop + credibility + click",
    "emphasis": "proof-over-product",
    "tone": "confident",
    "diversityTarget": "high"
  }
}
```

---

## Intent fields in detail
### `goal`
The business objective.

Examples:
- `convert`
- `educate`
- `announce`
- `retarget`
- `compare`
- `collect-lead`

### `channel`
Primary delivery context.

Examples:
- `paid-social`
- `display`
- `email`
- `organic-social`
- `landing-page`

### `offerType`
Communication architecture.

Examples:
- `proof-led`
- `product-led`
- `offer-led`
- `problem-solution`
- `comparison`

### `proofType`
Preferred evidence mode.

Examples:
- `review-screenshot`
- `quote-only`
- `ugc-still`
- `testimonial-card`
- `spec-comparison`

### `productRole`
How much visual priority the product should get.

Examples:
- `hero`
- `supporting`
- `secondary`
- `none`

### `optimizationTarget`
Primary success direction.

Examples:
- `scroll-stop`
- `credibility`
- `click-through`
- `clarity`
- `high-contrast readability`

### `emphasis`
Relative weighting between message components.

Examples:
- `proof-over-product`
- `product-over-proof`
- `cta-forward`
- `education-first`

### `diversityTarget`
Used to avoid repetitive output.

Examples:
- `low`
- `medium`
- `high`

This should influence how aggressively the engine varies architecture, spacing rhythm, and visual balance across batches.

---

## Constraint Policy model
`constraintPolicy` describes the rules the system must obey.

These are separate from intent.

Intent says what the ad should do.
Constraint policy says what the ad is allowed to do.

## Constraint categories
### 1. Geometry constraints
- min safe zones
- max occupancy
- no overflow
- spacing floors
- overlap rules

### 2. Semantic constraints
- proof must be visible
- CTA must exist
- product cannot dominate in proof-led mode
- logo must stay subordinate

### 3. Brand constraints
- approved logo modes
- forbidden badge styles
- typography limits
- approved background families

### 4. Compliance / policy constraints
- required disclaimer
- no unsupported claims
- testimonial handling rules
- platform policy restrictions

### 5. Diversity constraints
- avoid repeating identical structure too often
- vary proof treatment across batch
- vary quote/product balance within allowed range

### Example
```json
{
  "constraintPolicy": {
    "geometry": {
      "minSafeZone": 40,
      "allowOverflow": false,
      "minHeadlineSizeMobile": 44
    },
    "semantic": {
      "proofRequired": true,
      "ctaRequired": true,
      "maxProductProminence": 0.25
    },
    "brand": {
      "logoModesAllowed": ["white-card-landscape", "transparent-full"],
      "forbidShadedLogos": true
    },
    "diversity": {
      "avoidDuplicateLayoutWithinBatch": true,
      "targetStructureVariance": "medium"
    }
  }
}
```

---

## Asset capability model
Inputs should not just be files. They should declare what each asset can support.

### Example
```json
{
  "inputs": {
    "proofAsset": {
      "path": "/path/review.png",
      "kind": "review-screenshot",
      "credibility": "high",
      "textDensity": "medium",
      "supportsProofBand": true
    },
    "productAsset": {
      "path": "/path/product.png",
      "kind": "cutout",
      "supportsHeroRole": true,
      "supportsSupportingRole": true,
      "backgroundComplexity": "low"
    }
  }
}
```

This helps the engine choose a layout the assets can actually support.

---

## Benchmark Profile model
Benchmark work should be encoded as architecture constraints, not visual similarity targets.

### A benchmark profile may specify
- quote dominance range
- proof band position
- CTA relative prominence
- product-to-proof ratio
- whitespace rhythm
- text density limits

### Example
```json
{
  "benchmarkProfile": {
    "family": "proof-hero-premium",
    "reference": "LMNT-like structural profile",
    "constraints": {
      "quoteDominance": "high",
      "proofBandVerticalPosition": "middle",
      "ctaProminence": "supporting",
      "productRole": "secondary"
    }
  }
}
```

---

## Variant Strategy model
Variation should become a platform concept, not an accidental byproduct of config edits.

### Controlled axes
- proof density
- product prominence
- CTA aggressiveness
- hierarchy style
- spacing rhythm
- benchmark family
- emotional tone
- claim compactness

### Example
```json
{
  "designIntent": {
    "variantStrategy": {
      "proofDensity": "medium-high",
      "productProminence": "low",
      "ctaAggressiveness": "medium",
      "hierarchyStyle": "quote-dominant"
    }
  }
}
```

---

## Semantic scene graph
The system should produce a semantic scene graph separate from raw layout geometry.

### Why
Agents need to reason in semantic roles, not only rectangles.

### Proposed output
`<asset>.design.json`

### Example contents
- primary claim
- proof asset
- CTA
- logo
- product support element
- badge
- disclaimers
- their relationships and intended weights

### Relationship examples
- `proof_asset supports primary_claim`
- `cta follows proof`
- `logo is subordinate to primary_claim`
- `product reinforces proof`

This is the bridge between design intent and geometry.

---

## Provenance / lineage
Every output should carry lineage.

### Why
This is essential for trust, debugging, and future learning.

### Provenance should record
- design intent used
- constraint policy applied
- primitive selected
- benchmark profile selected
- asset roles assigned
- critic findings
- revision actions applied
- any constraint waivers

### Proposed output
`<asset>.lineage.json`

---

## Failure taxonomy
The design-intent layer should connect directly to known failure classes.

### Examples
- `proof_underpowered`
- `product_too_dominant`
- `cta_buried`
- `quote_too_long`
- `review_asset_not_credible`
- `logo_competes_with_claim`
- `batch_diversity_too_low`

Each failure should map to allowed remediation actions.

---

## Migration model
Legacy configs should not directly define the future authoring model.

### Strategy
- keep legacy configs valid
- translate them into canonical internal structures when possible
- store legacy-only assumptions in adapters
- do not let legacy fields dictate the future top-level contract

---

## What becomes first-class in v1.5.1 direction
These concepts should now be treated as core platform objects:
1. `designIntent`
2. `constraintPolicy`
3. `benchmarkProfile`
4. `assetCapabilities`
5. `semanticSceneGraph`
6. `lineage`
7. `failureTaxonomy`

These are more important long-term than adding many new primitives.

---

## Immediate implementation guidance
### Near-term
- add `designIntent` and `constraintPolicy` to config normalization
- keep them pass-through at first
- start using them in primitive selection and critic targeting

### Medium-term
- generate `.design.json` and `.lineage.json`
- connect intent to primitive variant selection
- connect constraints to hard/soft critic checks

### Longer-term
- let agents author through intent-first configs
- let StrikeFrame choose and tune primitives underneath

---

## Summary
If StrikeFrame is going to become a real production engine for diverse, high-quality ads, it cannot stop at geometry + primitives.

It needs a first-class layer for:
- design intent
- constraints
- benchmark profiles
- semantic roles
- provenance

That is what prevents the system from becoming a hardcoded one-proof machine and pushes it toward a real agent-forward design compiler.
