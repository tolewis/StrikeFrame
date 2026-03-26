# IMPLEMENTATION PLAN - StrikeFrame v1.5.1 - Phased Roadmap

**Product:** StrikeFrame  
**Version:** v1.5.1  
**Type:** Implementation plan  
**Date:** 2026-03-26  
**Status:** Draft

## Purpose
This document turns the v1.5.1 PRD and technical specs into a phased execution roadmap.

It is designed to answer:
- what gets built first
- what dependencies exist
- what success looks like in each phase
- how to keep the system shippable while upgrading it

This plan assumes StrikeFrame currently exists as a functioning v0.5.1 renderer and should evolve incrementally without losing the value of the current repo.

---

## Product objective
Build StrikeFrame from a local configurable renderer into an **agent-forward design engine** with:
- geometry awareness
- higher-level design primitives
- structured critic loop
- benchmark-aware iteration
- stronger ad layout quality

---

## Guiding delivery rules
### 1. Foundation before flourish
Do not build many new templates before geometry, measurement, and layout visibility are in place.

### 2. One flagship primitive first
Get one pattern truly strong before expanding the library.

### 3. Keep backward compatibility
Existing configs and production use should continue to work while the new system is layered in.

### 4. Instrument before optimizing
If the system cannot explain layout truth, it cannot improve layout truth reliably.

### 5. Measure against real benchmarks
Every premium primitive should be judged against real winning ad structures, not internal optimism.

---

## Roadmap overview
## Phase 0 - Stabilize current state
## Phase 1 - Minimum viable geometry core
## Phase 2 - Design intent and constraint layer
## Phase 3 - Primitive framework
## Phase 4 - ProofHero as flagship primitive
## Phase 5 - Critic loop MVP
## Phase 6 - Benchmark profile system
## Phase 7 - Additional primitive families
## Phase 8 - Production hardening

---

## Phase 0 - Stabilize current state
### Goal
Preserve the useful parts of current StrikeFrame while preparing for structural upgrades.

### Outcomes
- repo current on GitHub
- current renderer state committed
- new PRD and first technical docs in repo
- no ambiguity about project root or version baseline

### Tasks
- confirm project root and git remote
- commit current renderer changes that matter
- store v1.5.1 PRD in repo docs
- write technical follow-on specs

### Exit criteria
- v1.5.1 documents exist in repo
- current state is version-controlled
- roadmap can proceed from a clean baseline

### Status
Complete enough to proceed.

---

## Phase 1 - Minimum viable geometry core
### Goal
Make StrikeFrame spatially inspectable enough to build one strong flagship primitive without turning geometry into a science project.

### Why this comes first
Without geometry truth, every later design primitive or critic loop will be partially blind. But the first implementation should stay tightly scoped to what ProofHero actually needs.

### Deliverables
1. canonical rect model
2. text measurement output
3. element bounding boxes
4. safe-zone model
5. geometry export sidecar (`.layout.json`)
6. simple spacing and overflow checks

### Core engineering tasks
- define a shared rect utility layer
- normalize current layout outputs into geometry objects
- export text block geometry instead of only rough checks
- export element rects for images, CTAs, badges, logos, shapes, text, and primitive sub-elements
- add safe-zone checks as first-class logic
- keep diagnostics/debug overlay out of the critical path unless needed for active implementation

### Dependencies
- none beyond current renderer

### Risks
- too much effort spent on perfect geometry before practical usefulness
- exporting geometry without making it actionable

### Success criteria
- every meaningful element exposes its final rect
- layout JSON can be generated alongside every render
- the debug overlay can visually confirm geometry output
- spacing and overlap checks become more reliable than the current estimation-only approach

### Suggested milestone output
- one demo render with `.layout.json`
- one sample QC trace using geometry data

---

## Phase 2 - Design intent and constraint layer
### Goal
Introduce the authoring layer above primitives so StrikeFrame does not become a hardcoded one-proof engine.

### Deliverables
1. `designIntent` config contract
2. `constraintPolicy` config contract
3. initial asset capability metadata fields
4. benchmark profile placeholder contract

### Core engineering tasks
- define the intent schema used by agents
- define hard vs soft constraint buckets
- add pass-through support in config normalization
- connect intent fields to primitive selection and revision targeting over time

### Success criteria
- intent and constraint objects can be declared without breaking legacy configs
- one primitive can consume at least part of the intent model

---

## Phase 3 - Primitive framework
### Goal
Create the architectural layer for named design primitives.

### Deliverables
1. primitive registry
2. primitive normalization layer
3. primitive output contract
4. primitive debug contract
5. primitive QC hook interface

### Core engineering tasks
- define `primitive` config entry path
- support primitive-specific `inputs`, `variant`, `theme`, and `constraints`
- map primitive internals into exported geometry
- keep low-level config compatibility intact
- decide whether primitives render directly or compile into low-level layers before final render

### Dependencies
- Phase 1 minimum viable geometry core strongly preferred
- Phase 2 design intent and constraint layer preferred

### Risks
- building primitives before the geometry/export model is stable
- letting primitive interfaces become too open-ended and hard to maintain

### Success criteria
- at least one primitive can be declared cleanly in config
- primitive outputs are inspectable
- primitive internals are not encoded as ad hoc text/image layer piles in the calling config

### Suggested milestone output
- primitive registry file or module
- one working primitive interface
- one legacy config and one primitive config rendered side by side

---

## Phase 4 - ProofHero as flagship primitive
### Goal
Build one genuinely strong benchmark-oriented primitive without hardcoding the whole system around one proof style.

### Why ProofHero first
This pattern exposed the system’s current design ceiling more clearly than any other.

It is also one of the most commercially valuable formats for TackleRoom and future paid-social use.

### Deliverables
1. `proofHero` primitive implementation
2. one canonical flagship mode first, with a narrow optional second mode only if earned by real use
3. proof-specific QC hooks
4. support for proof asset + product asset role separation
5. proof-specific geometry export

### Core engineering tasks
- implement `proofHero` internals as a first-class primitive
- create strong quote block controls
- create review-card framing logic
- create product cluster logic
- create CTA treatment logic that does not dominate accidentally
- tune region ratios and spacing rules against benchmark examples

### Dependencies
- Phase 1 minimum viable geometry core
- Phase 2 design intent and constraint layer
- Phase 3 primitive framework

### Risks
- trying to solve every ad type through `proofHero`
- overfitting to one benchmark ad visually rather than structurally

### Success criteria
- the primitive can produce multiple coherent proof layouts without manual coordinate surgery
- outputs are clearly stronger than current generic assembled proof attempts
- agents can request the pattern using intent rather than dozens of raw placements

### Suggested milestone output
- benchmark board comparing:
  - old proof attempts
  - first primitive version
  - improved primitive version
- at least one internal “this is now in the right family” result

---

## Phase 5 - Critic loop MVP
### Goal
Enable render-inspect-revise cycles with structured feedback.

### Deliverables
1. critic output schema
2. compare-and-decide logic
3. primitive-specific revision targeting
4. iteration budget controls
5. stop conditions

### Core engineering tasks
- create `critic.json` output format
- connect critic inputs to geometry export and render artifact
- implement a simple first-pass critic focused on hard fails, hierarchy, readability, CTA visibility, and proof visibility
- generate revision suggestions at element or primitive role level
- build compare logic only after the first-pass critic is trustworthy

### Dependencies
- geometry export
- at least one primitive with real internal structure

### Risks
- overcomplicated scoring too early
- excessive iteration without measurable gains
- revision actions too vague to be useful

### Success criteria
- the system can critique a render and produce targeted revision recommendations
- the system can compare current vs prior iterations meaningfully
- the system can stop intelligently when improvement stalls

### Suggested milestone output
- 3-5 round iteration trace on a proofHero ad
- before/after summary with structured score changes

---

## Phase 6 - Benchmark profile system
### Goal
Teach StrikeFrame to reason relative to strong reference architectures without turning benchmark work into fuzzy similarity scoring.

### Deliverables
1. benchmark profile format
2. reference-mode constraints
3. architecture-level comparison outputs
4. benchmark-informed revision heuristics

### Core engineering tasks
- define benchmark profile schema
- encode known winning structures as layout role expectations
- add benchmark profile schema and profile selection rules
- compare candidate layout role proportions against target architecture
- avoid visual resemblance scoring as a first-class requirement

### Dependencies
- critic loop MVP
- proofHero primitive

### Risks
- confusing style mimicry with structural learning
- overfitting to one advertiser’s surface aesthetic

### Success criteria
- the system can explain how a layout differs from a target reference structure
- revisions become more focused when benchmark mode is enabled

### Suggested milestone output
- one benchmark profile for proofHero
- one benchmark comparison report

---

## Phase 7 - Additional primitive families
### Goal
Extend the system beyond proofHero after the foundation is proven.

### Candidate next primitives
1. `productHero`
2. `comparisonPanel`
3. `problemSolution`
4. `offerStrip`

### Delivery rule
Only expand after proofHero is genuinely credible.

### Dependencies
- proofHero success
- critic loop operating reasonably

### Risks
- adding breadth too early
- reintroducing weak generic template behavior under new names

### Success criteria
- new primitives are architecturally strong and not just alternate coordinate presets

---

## Phase 8 - Production hardening
### Goal
Make the upgraded system dependable for repeated real-world use.

### Deliverables
1. documented primitive library
2. regression samples
3. benchmark regression checks
4. improved repo docs
5. stable output contracts
6. safer production workflow for iteration mode

### Core engineering tasks
- add regression tests for geometry export
- create gold samples for flagship primitives
- define acceptable score thresholds by use case
- improve documentation for agents and future contributors
- stabilize config versioning if needed

### Success criteria
- StrikeFrame can be upgraded without silently breaking flagship layouts
- agent-facing workflows are understandable and repeatable

---

## Technical work packages
These are the concrete engineering work packages implied by the roadmap.

## WP-1 Geometry utilities
- rect helpers
- spacing helpers
- overlap helpers
- occupancy helpers

## WP-2 Layout export
- `.layout.json`
- debug overlay mode
- region serialization

## WP-3 Primitive runtime
- registry
- config normalization
- primitive execution path
- primitive output contract

## WP-4 ProofHero implementation
- quote module
- proof card module
- product cluster module
- CTA module
- variant system

## WP-5 Critic runtime
- critic schema
- rule-based checks
- hybrid checks
- compare logic
- iteration state

## WP-6 Benchmark profiles
- benchmark schema
- reference profiles
- benchmark comparison logic

## WP-7 Production docs and tests
- docs
- regression fixtures
- quality thresholds

---

## Sequencing recommendation
The fastest path to real value is:

1. minimum viable geometry core  
2. design intent + constraint layer  
3. primitive runtime  
4. proofHero primitive  
5. critic MVP  
6. benchmark profile system  
7. expand primitive library

Do not swap steps 4 and 5 unless the critic can meaningfully operate on primitive output.

---

## Suggested repo doc order
After the PRD and initial tech specs, the docs folder should clearly express the system stack:

1. PRD - product vision
2. Geometry and Layout Model
3. Design Intent and Constraint Model
4. Primitive Interface Specification
5. Critic Loop and Iterative Revision System
6. Phased Roadmap

This should become the canonical v1.5.1 document chain.

---

## What should be prototyped first
If implementation starts immediately, the first prototyping sprint should focus on:

### Sprint A
- layout sidecar output
- debug overlay render
- text geometry export
- basic region model

### Sprint B
- primitive registry
- proofHero primitive shell
- first geometry-aware proofHero output

### Sprint C
- critic output schema
- first rule-based revision loop
- proofHero iteration test

That is the shortest path to visible product improvement.

---

## What not to do next
Avoid these traps:

### 1. Do not add 10 more ad templates first
That increases surface area without fixing the root limitation.

### 2. Do not rely on pure brute-force iteration
Without geometry truth and critic logic, brute force mostly burns time.

### 3. Do not defer debug outputs
If the system cannot show its own layout skeleton, debugging will stay slow.

### 4. Do not let the critic become a vague essay generator
It must produce targeted revisions.

---

## Resourcing view
This roadmap is realistically a multi-phase engineering/design systems effort, not a one-file tweak.

### High-leverage components
- geometry foundation
- proofHero primitive
- critic MVP

Those three will determine whether StrikeFrame becomes a real agent-forward design engine or remains a useful but limited renderer.

---

## Done definition for v1.5.1 direction
The v1.5.1 direction is materially successful when:
- a flagship primitive exists and feels structurally strong
- the system exports layout geometry
- the system can critique and revise in a controlled loop
- output quality improves through instrumented iteration rather than blind brute force
- agents can request design patterns semantically

---

## Summary
This roadmap translates the v1.5.1 product direction into a build sequence.

The order matters.

If StrikeFrame builds geometry first, primitives second, and critics third, it has a real shot at becoming the agent-forward design engine Tim wants.

If it skips that order, it will keep generating smarter drafts without solving the deeper layout problem.
