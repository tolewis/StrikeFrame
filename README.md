# StrikeFrame

Version: **v0.2.0**

Local renderer for banners, social graphics, and simple product composites.

## What it does
- renders marketing graphics locally
- uses JSON config files
- supports reusable size presets
- avoids GUI-tool dependency for simple asset generation

## Presets
- `landscape-banner`
- `social-square`
- `social-portrait`
- `linkedin-landscape`

## Templates
- `banner`
- `product-composite`

## Run
- `npm install`
- `npm run generate:banner`
- `npm run generate:product`

## Notes
- Works with a real background image if `backgroundPath` is provided in config
- Falls back to a generated gradient background if no source image is provided
