# TECH SPEC - StrikeFrame v1.5.1 - Primitive Interface Specification

**Product:** StrikeFrame  
**Version:** v1.5.1  
**Type:** Technical specification  
**Date:** 2026-03-26  
**Status:** Draft

## Purpose
This document defines the interface model for StrikeFrame design primitives.

In v0.5.1, most composition is built from low-level parts:
- text layers
- image layers
- shapes
- badges
- overlays

That works for flexible draft generation, but it does not scale well to premium ad systems.

The goal of this spec is to define a primitive architecture where agents can request a visual pattern like:
- proof hero
- product hero
- comparison panel
- offer strip
- problem/solution layout

And StrikeFrame can solve the layout using a known internal contract rather than forcing the agent to rebuild the pattern manually from raw coordinates.

---

## Why primitives matter
The current renderer can place things.

It cannot yet reliably compose strong design patterns at a high level because it treats too many layout decisions as manual layer placement.

This creates three recurring problems:
1. too much config detail exposed to the agent
2. too much blind iteration
3. too little internal design intelligence

Primitives solve that by giving the system reusable design architectures with their own:
- inputs
- defaults
- internal layout logic
- geometry contract
- quality checks
- variant modes

---

## Primitive definition
A primitive is a high-level compositional unit that encapsulates a repeatable visual pattern.

A primitive is not just a grouped template.

A proper primitive must have:
1. semantic purpose
2. declared inputs
3. internal layout rules
4. output geometry contract
5. optional internal scoring hooks

### Example
`proofHero` is not just:
- quote text
- stars
- review image
- product image
- CTA

It is a named ad architecture with internal logic about:
- hierarchy
- spacing
- emphasis
- proof density
- product role
- CTA role

---

## Primitive design principles
### 1. Intent-first
The primitive should be named after the communication job it performs, not the low-level mechanics.

Good:
- `proofHero`
- `comparisonPanel`
- `offerStrip`
- `productCluster`

Weak:
- `textImageStack`
- `leftCopyWithBadge`
- `twoBoxLayout`

### 2. Strong defaults
A primitive should produce a reasonable default result with minimal input.

### 3. Controlled variation
Primitives should support modes and variants, but not arbitrary chaos.

### 4. Geometry export required
Every primitive must expose the final geometry of its sub-elements.

### 5. Critic-compatible
Primitives should expose enough metadata for targeted QC and revision.

---

## Primitive lifecycle
Each primitive should follow the same lifecycle.

### 1. Resolve inputs
Normalize and validate the config.

### 2. Assign roles
Map assets and copy to semantic roles.

### 3. Choose layout mode
Select the relevant internal pattern or variant.

### 4. Solve geometry
Compute regions, anchors, spacing, and element rectangles.

### 5. Render sub-elements
Build the text, image, shape, and CTA layers.

### 6. Export geometry contract
Expose layout results in a machine-readable structure.

### 7. Emit primitive-specific QC hooks
Expose quality and warning metadata.

---

## Common primitive interface
All primitives should support a shared top-level contract.

## Required fields
- `primitive`
- `id` (optional if single primitive)
- `variant` (optional)
- `inputs`
- `layout`
- `theme`
- `roles`
- `constraints`

### Example
```json
{
  "primitive": "proofHero",
  "variant": "review-dominant",
  "inputs": {
    "quote": "Forty minutes on a blue marlin and the belt never shifted.",
    "reviewImage": "/path/review.png",
    "productImage": "/path/product.png",
    "cta": "SHOP FIGHTING BELTS"
  },
  "layout": {
    "mode": "balanced",
    "safeZone": "default"
  },
  "theme": {
    "background": "charcoal",
    "accent": "gold"
  },
  "roles": {
    "proof": "reviewImage",
    "supportProduct": "productImage"
  },
  "constraints": {
    "ctaRequired": true,
    "productMaxAreaPercent": 0.22
  }
}
```

---

## Shared primitive output contract
Every primitive should emit:
- `elements`
- `regions`
- `warnings`
- `scores` (optional, if available)
- `debug`

### Required output fields
```json
{
  "primitive": "proofHero",
  "variant": "review-dominant",
  "elements": [],
  "regions": [],
  "warnings": [],
  "scores": {},
  "debug": {}
}
```

### Elements should include
- id
- type
- rect
- role
- zIndex
- visible
- source

---

## Primitive registry
StrikeFrame should maintain a primitive registry.

### Purpose
The registry should define:
- primitive ids
- supported variants
- required inputs
- optional inputs
- default values
- renderer implementation entry points
- QC hooks

### Example registry shape
```json
{
  "proofHero": {
    "variants": ["review-dominant", "quote-dominant", "cta-dominant"],
    "requiredInputs": ["quote", "reviewImage"],
    "optionalInputs": ["productImage", "cta", "eyebrow"],
    "implementation": "buildProofHero",
    "qcProfile": "proofHeroQC"
  }
}
```

---

## v1 primitive set
The first version of the primitive library should stay small and high quality.

## Priority 1 primitives
### 1. `proofHero`
**Use case:** Review/testimonial/proof-led ads

**Required inputs:**
- quote or proof headline
- review/proof asset

**Optional inputs:**
- product image
- CTA
- eyebrow label
- stars
- source label

**Sub-elements:**
- quote block
- quote mark
- stars block
- review card
- product cluster
- CTA
- eyebrow label

**Core design requirement:**
The layout must feel intentional, premium, and believable. It cannot read like assembled template parts.

---

### 2. `productHero`
**Use case:** Product-first conversion creative

**Required inputs:**
- product image
- headline

**Optional inputs:**
- subhead
- CTA
- price
- offer badge
- logo

**Sub-elements:**
- product hero block
- headline block
- support copy
- CTA
- pricing/offer treatment

**Core design requirement:**
Strong product focal point with high mobile legibility.

---

### 3. `comparisonPanel`
**Use case:** Us vs them, alternative pages, competitive contrast, benefit comparison

**Required inputs:**
- left label
- right label
- comparison rows

**Optional inputs:**
- headline
- CTA
- proof strip

**Sub-elements:**
- comparison frame
- row set
- label bar
- CTA
- headline/support

**Core design requirement:**
Fast scan, strong contrast, no clutter.

---

### 4. `problemSolution`
**Use case:** Educational ads, pain-agitation-solution, objection handling

**Required inputs:**
- problem statements
- solution statements

**Optional inputs:**
- image
- CTA
- proof

**Sub-elements:**
- problem column
- solution column
- divider
- CTA
- support media

---

### 5. `offerStrip`
**Use case:** Pricing, promotional, or limited-offer creative

**Required inputs:**
- offer text
- CTA

**Optional inputs:**
- original price
- sale price
- urgency text
- supporting product or proof

**Sub-elements:**
- price stack
- savings badge
- CTA strip
- urgency line

---

## Primitive internals
Each primitive should define its logic in five sections.

### 1. Role assignment
Map raw input fields to compositional roles.

Example for `proofHero`:
- `quote` -> `primary_claim`
- `reviewImage` -> `proof_asset`
- `productImage` -> `support_product`
- `cta` -> `action_block`

### 2. Region plan
Reserve regions for each major role.

Example:
- quote region
- stars region
- proof band
- support product region
- CTA region

### 3. Variant logic
Change the balance of the primitive based on a named mode.

Example `proofHero` variants:
- `quote-dominant`
- `review-dominant`
- `balanced`
- `product-support`

### 4. Constraint logic
Apply primitive-specific rules.

Example:
- review card must occupy 45-70% of center band width
- CTA cannot dominate the quote
- product must not compete with proof asset

### 5. Export contract
Emit geometry, warnings, and revision hooks.

---

## Primitive input validation
Each primitive should validate:
- required fields exist
- assets exist and are compatible
- text length fits expected use
- incompatible combinations are rejected early

### Example validation rules for `proofHero`
- reject if no quote and no review image
- warn if quote exceeds recommended length threshold
- warn if review screenshot aspect ratio is poor for proof band
- warn if product image complexity is too high for support role

---

## Variant model
Variants must be explicit rather than accidental.

### Why this matters
Without named variants, the system ends up simulating variants through piles of coordinates. That is fragile.

### Variant example
```json
{
  "primitive": "proofHero",
  "variant": "quote-dominant"
}
```

### Variant responsibilities
A variant may change:
- region proportions
- allowed proof size
- CTA prominence
- product prominence
- typography scale
- spacing rhythm

---

## Theme interface
Primitives must support theme inputs without turning them into open-ended design chaos.

### Theme should allow
- background tone family
- accent color family
- CTA color system
- text palette
- proof card frame style
- logo mode

### Theme should not require
- manual restyling of every sub-element

The primitive should decide how to apply theme consistently.

---

## Asset role interface
Primitives should not just accept images. They should accept role-aware assets.

### Example
```json
{
  "inputs": {
    "proofAsset": {
      "path": "/path/review.png",
      "kind": "review_screenshot",
      "credibility": "high"
    },
    "productAsset": {
      "path": "/path/product.png",
      "kind": "cutout",
      "intendedRole": "support"
    }
  }
}
```

This creates better internal decision making later.

---

## QC hooks by primitive
Each primitive should publish primitive-specific checks.

## Example: `proofHero` QC hooks
- quote dominance score
- proof visibility score
- review card believability score
- CTA support-vs-domination score
- product integration score
- clutter score

## Example: `productHero` QC hooks
- hero focal point score
- price badge balance score
- CTA contrast score
- product isolation score

These should complement, not replace, the shared geometry review.

---

## Primitive debug interface
Each primitive should support optional debug output.

### Debug outputs
- region overlay
- element labels
- bounding boxes
- anchor markers
- occupancy map
- sub-element ids

### Why this matters
The primitive is only trustworthy if it can be inspected visually and structurally.

---

## Backward compatibility
The primitive system should coexist with the existing low-level config model.

### Transitional approach
- legacy configs still work
- primitives may internally produce text/image/shapes layers
- geometry export can begin immediately
- new premium layouts should prefer primitive mode

### Example
Old:
```json
{
  "textLayers": [...],
  "imageLayers": [...]
}
```

New:
```json
{
  "primitive": "proofHero",
  "inputs": {...}
}
```

---

## Implementation recommendations
## Phase 1
- define primitive registry
- build primitive normalization layer
- implement shared primitive output contract

## Phase 2
- fully implement `proofHero`
- add region and element export
- add primitive-specific QC hooks

## Phase 3
- implement `productHero`
- implement `comparisonPanel`
- add variant support and theme contracts

## Phase 4
- add primitive critic guidance
- connect primitive output to revision loop

---

## Open questions
1. Should each primitive live in its own module, or should the first version remain inside one renderer file?
2. Should primitive outputs be rendered directly, or compiled into normalized low-level layers before render?
3. How should primitive variant selection be encoded: explicit in config only, or optionally inferred by the agent layer?
4. Should primitive QC be numeric, symbolic, or both?
5. Which primitive should be the first benchmark-complete gold standard after `proofHero`?

---

## Summary
StrikeFrame needs a primitive interface layer so agents can request design intent rather than manually rebuild layouts from raw parts.

This spec defines:
- what a primitive is
- how it should be structured
- how it should validate inputs
- how it should export geometry
- how it should expose quality hooks
- how it should coexist with the existing renderer

This is the layer that turns StrikeFrame from a renderer into a design system the agents can actually drive.
