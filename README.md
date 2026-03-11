# StrikeFrame

Version: **v0.3.1**

Local renderer for banners, social graphics, and simple product composites.

## What it does
- renders marketing graphics locally
- uses JSON config files
- supports reusable size presets
- supports design frameworks, typography, button styles, and layout personalities
- avoids GUI-tool dependency for simple asset generation

## Core idea
StrikeFrame should feel like an inspiring default design system, not a blank utility.

The LLM should usually be able to make a strong first-pass decision on:
- font direction
- color palette
- CTA treatment
- spacing and hierarchy
- layout personality

without demanding a full marketing brief every time.

## Brand-aware default
If a brand/site already exists, take a quick look at it and match the spirit — then modernize it.

Current example brand directions in the repo:
- **TackleRoomSupply 2030**
- **Contractor-AI 2030**
- **Unhook Outdoors 2030**
- **Editorial Premium**

## Layout personalities
- `editorial-left`
- `centered-hero`
- `split-card`

## Featured examples

### TackleRoomSupply 2030
![tackleroomsupply-2030](./examples/featured/tackleroomsupply-2030.jpg)

### Contractor-AI 2030
![contractor-ai-2030](./examples/featured/contractor-ai-2030.jpg)

### Unhook Outdoors 2030
![unhookoutdoors-2030](./examples/featured/unhookoutdoors-2030.jpg)

### Editorial Premium
![editorial-premium](./examples/featured/editorial-premium.jpg)

## Review process
Do not trust the first render blindly.

Before calling an asset done, check:
- headline stays inside the intended composition area
- text does not overflow card/panel treatments
- CTA remains readable and visually distinct
- hierarchy reads fast on mobile
- colors feel modern, not muddy or dated
- image + typography mood match the brand/use case
- if the first render looks off, adjust the config and rerun

Current built-in guardrail:
- split-card layouts now auto-expand the panel height when needed so the CTA/text block does not hang outside the card

## Run
- `npm install`
- `npm run generate:banner`
- `npm run generate:product`

## Example configs
- `node scripts/render.js configs/sample-batch.json`
- `node scripts/render.js configs/frameworks/tackleroomsupply-2030.json`
- `node scripts/render.js configs/frameworks/contractor-ai-2030.json`
- `node scripts/render.js configs/frameworks/unhookoutdoors-2030.json`
- `node scripts/render.js configs/frameworks/editorial-premium.json`

More examples and experiments live in:
- `configs/frameworks/`
- `configs/styles/`
- `examples/`

## New in this phase
- shape overlays (`ellipse`, `rectangle`)
- multiple text layers
- batch manifest rendering via `sample-batch.json`

## Configurable systems
### Typography
- headline font family
- body font family
- font weights
- type scale

### Buttons
- fill color
- stroke color
- text color
- width/placement

### Layout
- alignment
- hierarchy spacing
- card/panel treatment
- centered vs left-led composition

### Theme
- gradient background
- overlay colors
- text colors
- badge/product plate styling

## Notes
- Works with a real background image if `backgroundPath` is provided in config
- Falls back to a generated gradient background if no source image is provided
- Current product-composite flow is still early; real product cutouts are the next important upgrade
