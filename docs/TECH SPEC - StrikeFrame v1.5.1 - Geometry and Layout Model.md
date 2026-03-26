# TECH SPEC - StrikeFrame v1.5.1 - Geometry and Layout Model

**Product:** StrikeFrame  
**Version:** v1.5.1  
**Type:** Technical specification  
**Date:** 2026-03-26  
**Status:** Draft

## Purpose
This document defines the geometry, spatial reasoning, and layout model required for StrikeFrame to evolve from a config-driven renderer into an agent-forward design engine.

This spec exists because the current system can render many useful marketing graphics, but it still lacks the spatial certainty needed to create premium ad layouts consistently.

The goal of this document is to define a model where StrikeFrame can:
- know where every element lives on the canvas
- know how much space every element actually occupies
- reason about alignment, spacing, overlap, balance, and safe zones
- expose enough geometry to support a critic loop and iterative improvement

---

## Problem summary
The current renderer mostly composes from configured positions and estimated text dimensions.

That is good enough for:
- simple banners
- product composites
- repeatable first drafts
- structured internal marketing graphics

It is not enough for:
- premium paid social layouts
- proof-heavy ad structures
- benchmark-matching visual architecture
- iterative design correction based on actual rendered outcomes

### Current limitations
1. Element geometry is only partially known.
2. Text footprint is estimated more than measured.
3. Layout is mostly coordinate-driven rather than constraint-driven.
4. There is no shared geometry contract across all primitives.
5. The renderer has limited visibility into whitespace, balance, and focal hierarchy.
6. Agents cannot reliably reason from top-left / top-right / bottom-left / bottom-right schematic relationships.

---

## Design goals
The geometry and layout model must satisfy six goals:

### 1. Deterministic
The same input config and assets should produce the same layout result.

### 2. Inspectable
Every meaningful rendered element should expose its geometry in a machine-readable form.

### 3. Constraint-aware
Layouts should be solvable using regions, anchors, spacing rules, and safe zones, not only raw coordinates.

### 4. Primitive-friendly
High-level design primitives must be able to express their spatial logic using the same geometry model.

### 5. Critic-compatible
The model must provide enough information to support automated critique and revision.

### 6. Agent-usable
Agents must be able to reason about the layout through concepts like region, dominance, stack order, gap, margin, and collision rather than manually tuning dozens of coordinates blindly.

---

## Conceptual model
StrikeFrame layout should be modeled in four layers:

### Layer 1 - Canvas
The total render area.

### Layer 2 - Regions
Named zones that define intended use areas.

### Layer 3 - Elements
Concrete text, image, shape, proof, product, CTA, logo, or primitive outputs.

### Layer 4 - Constraints
Rules that govern how elements can be placed relative to canvas, regions, and each other.

This creates a hierarchy:

`Canvas -> Regions -> Elements -> Constraints -> Render -> Geometry Export`

---

## Core data model
## 1. Canvas model
The canvas is the root coordinate system.

### Required fields
- `width`
- `height`
- `aspectRatio`
- `safeZone`
- `bleed` (optional)
- `grid` (optional debug/useful authoring aid)

### Example
```json
{
  "canvas": {
    "width": 1080,
    "height": 1080,
    "aspectRatio": 1.0,
    "safeZone": { "top": 40, "right": 40, "bottom": 40, "left": 40 }
  }
}
```

### Notes
- Safe zones should be first-class and not implied.
- Safe zones should support platform-specific overrides later.

---

## 2. Rectangle model
All layout geometry should normalize to the same rectangle structure.

### Required fields
- `x`
- `y`
- `width`
- `height`

### Derived values
- `left`
- `top`
- `right`
- `bottom`
- `centerX`
- `centerY`
- `area`

### Example
```json
{
  "rect": {
    "x": 120,
    "y": 84,
    "width": 540,
    "height": 180
  }
}
```

### Rules
- All regions and elements must be convertible into this rect model.
- Debug overlays and critics should consume the same model.

---

## 3. Region model
A region defines a named intended-use area within the canvas.

### Examples
- `top_band`
- `proof_band`
- `hero_region`
- `product_anchor_region`
- `cta_zone`
- `logo_safe_zone`
- `copy_column`

### Required fields
- `id`
- `rect`
- `role`
- `priority`
- `padding`
- `allowOverflow`

### Optional fields
- `anchorPreference`
- `maxOccupancy`
- `minOccupancy`
- `alignmentMode`
- `debugColor`

### Example
```json
{
  "regions": [
    {
      "id": "quote_region",
      "role": "headline_like_proof",
      "priority": 1,
      "rect": { "x": 80, "y": 60, "width": 700, "height": 260 },
      "padding": { "top": 16, "right": 16, "bottom": 16, "left": 16 },
      "allowOverflow": false
    }
  ]
}
```

### Why regions matter
Regions let the agent think in layout roles rather than raw coordinates.

Instead of saying:
- place quote at x 120 y 90

The agent can say:
- quote owns the quote region
- stars sit below quote region with fixed gap
- review card occupies center proof band

---

## 4. Element model
Every rendered component should resolve into one or more elements.

### Element types
- `text`
- `image`
- `shape`
- `logo`
- `cta`
- `review_card`
- `product_cluster`
- `primitive`

### Required fields
- `id`
- `type`
- `rect`
- `zIndex`
- `regionId` (optional but strongly preferred)
- `source` (config path or primitive origin)
- `visible`

### Derived fields
- `occupancyPercent`
- `distanceToCanvasEdges`
- `distanceToNeighboringElements`
- `overlapWith`
- `anchorPoint`
- `visualWeightScore` (future)

### Example
```json
{
  "elements": [
    {
      "id": "proof_quote",
      "type": "text",
      "regionId": "quote_region",
      "rect": { "x": 110, "y": 84, "width": 612, "height": 168 },
      "zIndex": 30,
      "source": "proofHero.quote",
      "visible": true
    }
  ]
}
```

---

## 5. Anchor model
Every element should support normalized anchor behavior.

### Supported anchors
- `top-left`
- `top-center`
- `top-right`
- `center-left`
- `center`
- `center-right`
- `bottom-left`
- `bottom-center`
- `bottom-right`

### Why anchors matter
This is the exact spatial language needed for agent-forward design.

Many layout instructions are naturally expressed as:
- review card centered in proof band
- product anchored bottom-right
- CTA anchored bottom-left safe zone
- logo anchored top-left safe zone

### Anchor resolution
Anchor placement should resolve to a real rect using:
- base region rect
- element dimensions
- padding
- offset
- collision adjustments if needed

---

## 6. Gap model
Spacing between elements should be explicit and measurable.

### Gap types
- vertical gap
- horizontal gap
- edge gap
- region padding gap
- baseline gap (text-related)

### Required support
- min gap checks
- ideal gap targets
- max gap warnings

### Example use cases
- stars must be 16-36 px below the quote block
- CTA must be at least 24 px below review band
- product cluster must maintain 20 px from right safe zone

---

## Constraint model
The layout engine should support three categories of constraints.

## 1. Hard constraints
Must never be violated.

Examples:
- element must remain inside canvas
- CTA must remain inside safe zone
- no element can overflow a locked region
- logo cannot collide with quote block

## 2. Soft constraints
Can be violated temporarily but should trigger warnings or optimization.

Examples:
- ideal gap between quote and stars is 24 px
- review card should occupy 55-70% of center band width
- product cluster should not exceed 24% of canvas area

## 3. Preference constraints
Used for ranking candidate layouts.

Examples:
- prefer larger quote dominance
- prefer lower clutter score
- prefer CTA left alignment in proofHero layouts

---

## Layout solving modes
StrikeFrame should support multiple solving modes.

### 1. Absolute mode
Raw coordinates. Maintains backward compatibility.

### 2. Anchored mode
Element placed by anchor, size, and offset.

### 3. Region-bound mode
Element placed within a named region and solved against padding and occupancy rules.

### 4. Primitive-solved mode
A design primitive internally resolves its own sub-layout and exports final geometry.

The long-term default for premium creative should be:
- primitive-solved + region-aware + critic-reviewed

---

## Text geometry model
Text needs a dedicated geometry model, not generic rectangle assumptions.

## Required text geometry outputs
- line count
- line height
- max line width
- total text block height
- bounding box
- baseline positions
- font family
- font size
- font weight
- wrap rule used

### Why this matters
Many current layout problems come from text boxes being estimated instead of measured.

### Text layout object example
```json
{
  "textLayout": {
    "content": "Forty minutes on a blue marlin and the belt never shifted.",
    "fontFamily": "Georgia",
    "fontSize": 68,
    "fontWeight": 700,
    "lineHeight": 74,
    "maxChars": 15,
    "lines": [
      "Forty minutes on",
      "a blue marlin and",
      "the belt never",
      "shifted."
    ],
    "rect": { "x": 110, "y": 96, "width": 602, "height": 296 }
  }
}
```

---

## Image geometry model
Images should expose more than width and height.

## Needed fields
- source dimensions
- rendered dimensions
- fit mode
- crop mode
- focal point
- subject box (future)
- negative space region (future)
- complexity score (future)

### Why this matters
A lifestyle image and a review screenshot should not be treated like generic interchangeable rectangles.

---

## Primitive geometry contracts
Every high-level primitive must export a geometry contract.

### Example: `proofHero`
Sub-elements may include:
- quote block
- quote mark
- stars
- review card
- product cluster
- CTA
- eyebrow label

Each one should export:
- final rect
- parent primitive id
- region relationship
- layering
- visibility state

### Example output
```json
{
  "primitive": "proofHero",
  "elements": [
    { "id": "proof_quote", "type": "text", "rect": { "x": 108, "y": 84, "width": 620, "height": 250 } },
    { "id": "proof_stars", "type": "text", "rect": { "x": 222, "y": 316, "width": 370, "height": 84 } },
    { "id": "proof_review_card", "type": "image", "rect": { "x": 104, "y": 404, "width": 760, "height": 210 } },
    { "id": "proof_product_cluster", "type": "image", "rect": { "x": 646, "y": 650, "width": 238, "height": 220 } },
    { "id": "proof_cta", "type": "cta", "rect": { "x": 112, "y": 930, "width": 340, "height": 72 } }
  ]
}
```

---

## Geometry export requirements
Every render should optionally emit a geometry sidecar.

### Proposed file
`<asset>.layout.json`

### Contents
- canvas
- regions
- elements
- text layouts
- constraint results
- warnings
- occupancy metrics
- overlaps
- spacing metrics

### Why this matters
This sidecar is the foundation for:
- debugging
- automatic critique
- agent revision loops
- benchmark comparisons

---

## Occupancy and density metrics
The engine should calculate useful spatial metrics.

### Per element
- area
- occupancy % of canvas
- occupancy % of assigned region

### Per layout
- top-half occupancy
- bottom-half occupancy
- left/right balance
- whitespace ratio
- dead zone regions
- cluster density score

### Why this matters
A layout can be technically valid and still feel unbalanced, sparse, or overcrowded.

---

## Collision and overlap model
Collisions should be measured, not inferred loosely.

### Required checks
- element vs canvas overflow
- element vs region overflow
- element vs element overlap
- invalid tangents
- too-tight spacing

### Tangent examples
- CTA almost touching review card
- product corner kissing the review band
- stars nearly colliding with quote descender area

These are subtle but often make designs feel amateur.

---

## Safe-zone model
Safe zones should be universal and overridable.

### Types
- global canvas safe zone
- platform safe zone
- primitive safe zone
- reserved logo zone

### Example
```json
{
  "safeZones": {
    "global": { "top": 40, "right": 40, "bottom": 40, "left": 40 },
    "logo": { "top": 32, "right": 32, "bottom": null, "left": 32 },
    "cta": { "bottom": 48, "left": 48 }
  }
}
```

---

## Layout evaluation hooks
The geometry model must expose fields that critics can score.

### Example critic hooks
- `dominantElementId`
- `dominantElementOccupancy`
- `minReadableTextHeight`
- `ctaContrastStatus`
- `reviewCardBelievabilityCandidate`
- `proofDensityScore`
- `balanceScore`
- `crowdingScore`

These do not have to be perfect on day one, but the geometry model should make them possible.

---

## Backward compatibility
The new layout model must not break existing config files immediately.

### Strategy
- keep raw coordinate support
- add geometry export without requiring new config syntax
- let new primitives use the richer model first
- progressively migrate old templates

This preserves shipped utility while enabling stronger future behavior.

---

## Implementation priorities
## Priority 1
- canonical rect model
- element geometry export
- text layout export
- region model
- safe zones

## Priority 2
- anchor resolution
- gap measurement
- collision checks
- layout sidecar output

## Priority 3
- primitive geometry contracts
- occupancy metrics
- debug overlay mode
- critic-facing hooks

---

## Suggested file outputs
For every render, support:
- `<asset>.review.json` - existing QA/QC review
- `<asset>.layout.json` - geometry export
- `<asset>.debug.png` - optional visual overlay for schematic debugging

---

## Open questions
1. Should region definitions live in templates, presets, or both?
2. Should geometry be exported for all primitives by default or only in debug mode?
3. Should the first implementation use measured Sharp/font metrics only, or should it add a richer typography engine later?
4. How should balance and whitespace scoring be approximated in the first critic pass?
5. Should primitive layout contracts be versioned separately from renderer version?

---

## Summary
StrikeFrame cannot become a serious agent-forward design engine without a stronger geometry and layout model.

This spec defines the foundation:
- canvas
- regions
- elements
- constraints
- geometry export
- occupancy
- spacing
- collision
- primitive contracts

This is the technical backbone that makes all later design primitives and critic loops credible.
