# PRD - StrikeFrame v1.5.1 - Agent-Forward Design Engine

**Version:** v1.5.1  
**Baseline:** v0.5.1  
**Status:** PRD / proposed next major product direction  
**Date:** 2026-03-26

## Product
StrikeFrame

**Working descriptor:** agent-forward graphic design engine for high-conviction marketing creative, ad systems, and visual content production.

## Why this PRD exists
StrikeFrame v0.5.1 proved that local rendering works.

It can:
- generate useful first drafts
- automate repeatable creative production
- support JSON-driven local image generation
- produce shippable internal marketing assets faster than manual design workflows in many cases

But the current system still breaks down on the hardest and highest-value problem:

**building premium ad creative that can compete visually with strong advertisers.**

The issue is not only taste. It is mostly structural.

The current renderer is strong at generating starting points. It is weak at understanding and solving layout with precision.

That means the system can produce “composed” graphics, but not yet reliably produce **elite visual hierarchy, believable proof layouts, or premium paid-social design patterns** at the level needed for serious spend.

This PRD defines StrikeFrame’s next product direction: from a **configurable renderer** into an **agent-forward design engine**.

---

## Core product thesis
The future version of StrikeFrame should not behave like a thin rendering tool that places text and images on a canvas.

It should behave like a **design system with a layout solver, visual primitives, and a critic loop** that helps agents produce higher-quality outcomes with less blind iteration.

The main shift is:

**from:** "tell me where to place layers"  
**to:** "give me the ad pattern and visual goal, and I will solve the layout, render it, inspect it, and improve it"

---

## Product vision
StrikeFrame should become the best local, agent-native creative system for:
- paid social ad creative
- ecommerce promotional graphics
- proof / review-driven ad layouts
- product hero graphics
- comparison / problem-solution formats
- static UGC-inspired ad formats
- benchmark-informed, platform-aware creative generation

The system should let an agent say things like:
- "Make a proof ad like LMNT using TackleRoom assets"
- "Reduce clutter and increase proof"
- "Make the CTA stronger"
- "Rebuild this for 4:5"
- "Use the same layout architecture but swap the product category"

And the system should solve composition in a structured, measurable way.

---

## Problem statement
### Current problem
StrikeFrame can render many useful outputs, but it is still limited by several technical constraints that prevent high-end design execution.

The current weak points are:
- insufficient spatial certainty
- weak understanding of actual rendered element footprint
- limited typography control
- inadequate layout primitives for premium ad patterns
- too much dependence on manual coordinate tuning
- weak feedback loop between design intent and final rendered reality

This leads to recurring failure modes:
- too many elements on the canvas
- weak hierarchy
- visually pasted-on product areas
- review/proof layouts that feel assembled instead of designed
- typography that is technically valid but visually weak
- layouts that are “organized” but not persuasive
- repeated iteration without enough geometric truth to guide refinement

### Root cause
The current system does not fully understand:
- how large each element actually renders
- where its true bounding box lives
- how it interacts with nearby elements
- how much whitespace surrounds it
- how readable it is at actual mobile viewing size
- whether the layout has a true dominant focal point

In short:

**StrikeFrame lacks the layout intelligence and feedback instrumentation required to build premium creative reliably.**

---

## Product goal
Build StrikeFrame into an **agent-forward design engine** that can:
1. reason about layout schematically
2. compose using high-level design primitives instead of loose layers
3. render with strong geometry and typography control
4. inspect its own output with measurable feedback
5. iterate toward stronger results with less blind guessing

---

## Primary users
### 1. Agent operators
- Tim
- Katya
- Thor
- Captain Bill

These users need the system to produce real outputs, not just template demos.

### 2. Agent workflows
StrikeFrame must support other agent systems that need:
- a local graphics engine
- deterministic reruns
- benchmark-driven ad iteration
- scalable creative production
- reusable visual architectures across categories and brands

### 3. Internal use cases
- TackleRoom paid social creative
- TackleRoom proof / review ads
- product hero ads
- promotional graphics
- future content-image and sales-support graphics

---

## Success definition
StrikeFrame v1.5.1 succeeds when it can do all of the following reliably:

### Creative quality
- produce ad layouts that feel visually coherent, intentional, and premium
- support competitive paid-social patterns without “template stack” energy
- produce outputs that can plausibly sit beside stronger benchmark advertisers

### Layout reasoning
- know where elements are
- understand their dimensions
- measure spacing, collisions, balance, and safe zones
- reduce blind coordinate-tuning loops

### Agent usability
- let an agent specify the *pattern* and *goal*, not every pixel
- support structured iteration using feedback instead of ad hoc guesswork
- enable benchmark-based re-creation of strong creative architectures

### System quality
- remain local-first
- remain deterministic and scriptable
- keep JSON/config-driven reproducibility
- expose enough instrumentation for debugging and future automation

---

## Product principles
### 1. Pattern over decoration
Do not add more design elements to simulate progress.

The system should optimize for:
- focal point
- hierarchy
- clarity
- proof
- readability
- persuasion

Not decorative complexity.

### 2. Geometry before vibes
Visual quality must be informed by measurable layout truth.

The system should know:
- element boundaries
- whitespace
- overlap
- spacing
- alignment
- canvas occupancy
- mobile viewing impact

### 3. Primitive-first design
Instead of composing every ad from generic text/image layers, the system should offer high-level primitives that encode good design behavior.

Examples:
- `proofHero`
- `reviewCard`
- `quoteBlock`
- `productCluster`
- `offerStrip`
- `comparisonPanel`
- `problemSolution`
- `testimonialStack`

### 4. Agent-forward, not GUI-first
The design engine should be optimized for agent execution and reproducible workflows first.

A GUI can come later.

### 5. Critic loop required
Generation alone is not enough.

StrikeFrame should render, inspect, score, and revise.

---

## Required product capabilities
## A. Layout engine and geometry model
StrikeFrame needs a more formal layout model than manually placed coordinates.

### Required capabilities
- named layout regions
- anchors and constraints
- margin systems
- safe-zone systems
- alignment rules
- collision checks
- spacing rules
- hierarchy checks
- proportional scaling rules

### Why this matters
Agents currently operate with partial visibility into actual layout behavior. A stronger layout engine reduces iteration waste and improves output quality.

---

## B. Bounding-box awareness
Every visual element should expose real rendered geometry.

### For each element, the system should know:
- top-left
- top-right
- bottom-left
- bottom-right
- width / height
- center point
- occupied area
- distance to neighboring elements
- distance to edges / safe zones
- overlap state

### Why this matters
Without real geometry, the system is mostly guessing at layout. That is acceptable for first drafts and unacceptable for premium creative.

---

## C. Typography measurement and control
Typography is one of the biggest current bottlenecks.

### Required capabilities
- real text box measurement
- accurate line wrapping
- controlled line height
- font metric awareness
- strong headline/subhead/CTA hierarchy tools
- quote-specific typography controls
- better control over rag, rhythm, and text density

### Why this matters
Many current failures come from text that is technically placed but visually weak or incorrectly balanced.

---

## D. Design primitives
StrikeFrame should move away from relying on only low-level generic composition parts.

### Current low-level primitives
- text layers
- image layers
- badges
- shapes
- generic overlays

These should remain available, but they should not be the primary path for high-end layouts.

### Needed high-level primitives
- `proofHero`
- `reviewCard`
- `quoteBlock`
- `productCluster`
- `ctaStrip`
- `founderNote`
- `comparisonPanel`
- `offerFrame`
- `problemSolutionSplit`
- `proofStack`

### Why this matters
Agents should specify *intent and ad architecture*, not manually reconstruct elite design patterns from primitive scraps every time.

---

## E. Render-inspect-revise loop
StrikeFrame should support an internal visual critic workflow.

### Desired loop
1. compose layout
2. render output
3. extract geometry + metadata
4. inspect against QC rules
5. compare to desired pattern and benchmark
6. revise only failing dimensions
7. rerender

### QC dimensions
- focal point strength
- hierarchy
- readability at mobile size
- CTA visibility
- proof credibility
- spacing quality
- crowding / dead zones
- balance
- product integration
- brand fit
- benchmark plausibility

### Why this matters
The current workflow often produces too much blind brute-force iteration. The system must provide structured revision guidance.

---

## F. Reference-mode composition
The system should be able to use a benchmark ad architecture as a layout reference.

### Example
If told: “Make a proof ad like LMNT,” the system should represent that as:
- relative quote block size
- star emphasis
- review-card band placement
- product placement proportions
- CTA emphasis level
- whitespace rhythm
- proof density balance

### Why this matters
Agents need a way to reproduce *structural quality* without manually reverse engineering every layout.

---

## G. Asset semantics and suitability scoring
The system must know what kinds of images it is working with.

### Needed asset metadata
- cutout vs lifestyle vs screenshot vs review
- focal subject position
- negative space regions
- background complexity
- contrast quality
- proof suitability
- hero suitability
- product utility
- screenshot cleanliness

### Why this matters
A lot of design failures are really asset-role failures. The engine needs to choose the right asset for the right layout role.

---

## H. Debug / schematic mode
StrikeFrame needs a visual debugging mode for layout work.

### Debug overlays should optionally show:
- element bounding boxes
- region boundaries
- grid lines
- alignment lines
- safe zones
- whitespace map
- labels per element
- collision markers

### Why this matters
This lets agents and humans inspect layout as a schematic system rather than only as a finished image.

---

## Initial target template family
The first major template family to fully upgrade should be:

## `proofHero`
This is the clearest and most urgent benchmark pattern because it exposed the current system’s limits most clearly.

### It should support
- oversized quote block
- large rating / star treatment
- review-card band
- believable proof treatment
- product cluster integration
- optional CTA
- optional eyebrow / source label
- multiple proof density modes
- multiple product integration modes
- mobile-first readability

### Why start here
Because this is where the current renderer most clearly fails to compete with best-in-class ad structures.

---

## Out of scope for this PRD
Not part of the immediate v1.5.1 focus:
- full GUI editor
- complete Figma replacement
- video/motion design system
- broad multi-brand style governance layer
- enterprise DAM system
- collaborative review workflow UI

Those may matter later, but they are not required for the core agent-forward design engine.

---

## Risks
### 1. Building a more complex renderer without a stronger evaluation loop
This would create more knobs without solving output quality.

### 2. Over-investing in template count instead of template depth
The system needs fewer, stronger architectures first.

### 3. Confusing benchmark mimicry with good design
Reference-mode should capture structure and persuasive architecture, not shallow style copying.

### 4. Over-indexing on critics without fixing geometry
A critic loop is only as good as the layout truth it can observe.

---

## Proposed phased path
## Phase 1 - Foundation
- geometry model
- bounding boxes
- spacing and collision checks
- better text measurement
- debug overlay mode

## Phase 2 - First elite primitive
- build `proofHero`
- benchmark against strong proof ads
- support stronger quote / review / product composition

## Phase 3 - Critic loop
- render-inspect-score-revise
- structured QC outputs
- benchmark-aware revision logic

## Phase 4 - Expand architecture library
- product hero
- comparison
- problem/solution
- offer-led ad
- proof stack

---

## Deliverables this PRD implies
This PRD should lead to a deeper technical document set, including:
1. technical architecture spec
2. geometry / layout model spec
3. primitive interface spec
4. critic loop spec
5. asset semantics schema
6. debug overlay / instrumentation spec
7. phased implementation plan

---

## Summary
StrikeFrame v0.5.1 proved local rendering works.

StrikeFrame v1.5.1 should prove that agent-forward design can work at a much higher level.

The key leap is not “more templates.”
It is:
- better geometry
- better primitives
- better feedback
- better layout intelligence

That is how StrikeFrame becomes a real design engine instead of a renderer with growing ambition.
