# PLAYBOOK — Variant Proof System

**Purpose:** Generate a labeled proof sheet showing every primitive × every structural variant rendered with real TackleRoom assets and benchmark-calibrated design. This is the single command that proves the engine works.

**Date:** 2026-03-29
**Status:** Working. 25/25 renders passing.

---

## Quick start

```bash
cd ~/Documents/projects/30\ Projects/TackleRoom/Media\ Renderer\ MVP/

# Generate all 25 variant proof renders + proof sheet
python3 scripts/gen_variant_proof.py

# Custom output directory
python3 scripts/gen_variant_proof.py --output-dir /path/to/output
```

**Default output:** `/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/variant-proof/`

---

## What it produces

| File | What |
|------|------|
| `proof-sheet.jpg` | Labeled contact sheet of all 25 renders |
| `manifest.json` | Scores + metadata for every render |
| `{primitive}-{variant}.jpg` | Individual render (1080×1080) |
| `{primitive}-{variant}.critic.json` | Critic scoring (5 dimensions) |
| `{primitive}-{variant}.layout.json` | Element geometry + safe zones |
| `{primitive}-{variant}.review.json` | Composition review |

---

## Primitive inventory (8 primitives, 25 variants)

| # | Primitive | Variants | Config key | Score range |
|---|-----------|----------|------------|-------------|
| 1 | comparisonPanel | standard, hero-right, compact, split-weight | `comparisonTable` | 87-92 |
| 2 | offerFrame | standard, hero-price, badge-first | `offerFrame` | 87 |
| 3 | benefitStack | standard, compact, card | `benefitStack` | 92-96 |
| 4 | testimonial | standard, quote-hero, attribution-forward | `testimonial` | 89-90 |
| 5 | splitReveal | standard, pain-heavy, solution-hero | `splitReveal` | 96 |
| 6 | authorityBar | standard, bold | `authorityBar` | 92-93 |
| 7 | actionHero | bottom-heavy, center-band, split-action, compact-strip | `actionHero` | 95 |
| 8 | proofHero | quote-dominant, review-dominant, balanced | `proofHero` | 80 |

### What variants change structurally

Variants are NOT copy/color swaps. They change the layout architecture:

- **comparisonPanel:** Column width ratio (42-50%), row height, text scale, gutter width
- **offerFrame:** Price element scale (1x-1.35x), element ordering, spacing rhythm
- **benefitStack:** Row spacing, icon/text scale
- **testimonial:** Quote/name emphasis weighting, gap rhythm
- **splitReveal:** Column divider position (42-55%)
- **authorityBar:** Text scale, bar opacity
- **actionHero:** Headline Y position (45-82% of canvas), CTA offset, badge position
- **proofHero:** Quote/review/product emphasis, region proportions

---

## Assets required

These must exist on disk for the proof generator to work:

### Hero photos (6)
```
/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/
├── IMG_8585.png
├── IMG_8700.png
├── IMG_9117.jpg
├── Dolphin_Fish_Hooked.jpg
├── IMG_9109.jpg
└── IMG_9098.jpg
```

### Logo
```
/home/tlewis/Dropbox/Tim/TackleRoom/Creative/camera-strikeframe/tier1-ready/logo-landscape-1200x300-v2.png
```

### Review screenshots (proofHero only)
```
/home/tlewis/Dropbox/Tim/TackleRoom/Creative/review-proof/tier2-polish/
├── Review08.png
├── Review11.png
└── Review03.png
```

---

## Design decisions (benchmark-calibrated)

These values come from studying 16 LMNT benchmark ads in `/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/01_sources/external_examples/adexamples-kb/`.

### Canvas layout
- **Preset:** social-square (1080×1080)
- **CTA:** Fixed at Y=920, 400×62px, orange fill `rgba(232,93,58,0.95)`
- **Headline:** Y=140, 56px, weight 900
- **Content zone:** Y=290 (headline bottom) to Y=900 (CTA top) = 610px
- **Personality:** centered-hero (no frosted panel)

### Overlay (benchmark-dark)
```
leftColor: 5,12,22    leftOpacity: 0.82
midColor:  5,12,22    midOpacity:  0.68
rightColor: 5,12,22   rightOpacity: 0.82
vignetteBottom: 0.35
```
LMNT uses near-black backgrounds. This overlay achieves that while preserving photo texture.

### Typography scale
| Element | Size | Weight | Why |
|---------|------|--------|-----|
| Headline | 56px | 900 | Benchmark fills 25-30% of canvas width |
| Subhead | 26px | 400 | Supporting, not competing |
| CTA | 24px | 700 | Legible at mobile size |
| Price (offerFrame) | 148px | 800 | Price IS the hero element |
| Quote (testimonial) | 52px | 500 italic | Quote IS the visual hero |
| Table body | 22px | 400/600 | Readable but not dominant |

### Logo
- Corner-anchor, top-left
- White-card-landscape mode
- 240×56px with 12px clearSpace

### What we learned from LMNT
1. **Canvas fill:** 90%+ occupied. Zero dead space. Every pixel has a job.
2. **Product as proof:** Product image sits IN the layout as visual anchor.
3. **Dark backgrounds:** #1a1a1a to #2d2d2d solid or heavily overlaid photos.
4. **One accent color:** Used only on badges/icons/highlights. Everything else is white-on-dark.
5. **Proof density:** Review cards show full text, avatar, name, verified badge.
6. **Typography dominance:** Headlines are MASSIVE. Quote text is the biggest element on testimonials.

---

## Critic scoring

Every render gets a `.critic.json` with 5 dimensions scored 0-100:

| Dimension | What it checks |
|-----------|---------------|
| Geometry | Safe zones, collisions, canvas occupancy |
| Hierarchy | Focal point dominance, size ratios, CTA presence |
| Readability | Mobile font sizes, tap targets, line count |
| Spacing | Gap enforcement, vertical fill (benchmark: 80%+) |
| Persuasion | CTA position, proof presence, clutter level |

**Stop recommendations:**
- `ship` (≥85): Ready for production
- `iterate` (65-84): Needs targeted fixes
- `escalate` (<65 with 3+ failures): Structural problem

---

## Known gaps (next work)

1. **Product images:** Every LMNT ad has the physical product visible. Our primitives are text-only. The renderer already supports `productImage` and `productComposite` — needs wiring into primitive configs.
2. **ProofHero CTA positioning:** Primitive renders its own CTA but safe-zone checker flags edge placement. Score stuck at 80.
3. **OfferFrame vertical gap:** Price block is ~290px in a 610px zone. Product image would fill the gap.
4. **ActionHero middle zone:** Hero photo carries the canvas visually, but on pure gradient backgrounds the middle is sparse. Production runs with real photos solve this.

---

## How to add a new primitive

1. Create `lib/primitives/{name}.js` with `id`, `configKey`, `variants`, `resolve()`, `build()`
2. Register in `lib/primitives/index.js`
3. Add inline builder skip in `render.js` (`if (!activePrimitiveIds.has('{name}'))`)
4. Add sample content and primitive entry in `gen_variant_proof.py`
5. Run `python3 scripts/gen_variant_proof.py` to verify
6. Run `npm test` to verify no regressions

---

## How to tune the critic

Edit `lib/critic/index.js`. Each dimension is a separate scorer function. To change thresholds:
- Safe-zone exemptions: `EDGE_EXEMPT` set
- Occupancy ceiling: `scoreGeometry` occ check
- Vertical fill threshold: `scoreSpacing` utilization check
- Mobile readability filter: `scoreReadability` realSmall filter

After changes, regenerate proof renders and compare scores.
