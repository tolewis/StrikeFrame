# StrikeFrame Design Principles

Read this before building any config. These are standard marketing design frameworks — not suggestions, not nice-to-haves. Apply them every time.

## 1. Visual Balance

Every image has visual weight. A boat on the right side, a person on the left, a bright object in the corner — these pull the eye. Text is also visual weight.

**Rule:** Place text on the opposite side of the image's heaviest visual element. If the subject is right-heavy, text goes left. If the subject is centered, use centered-hero personality and frame text above or below.

**In StrikeFrame terms:**
- `editorial-left` personality works when the image subject sits right of center
- `centered-hero` works for symmetric backgrounds or abstract/gradient fills
- Never stack text on top of the subject — it fights for attention and loses

## 2. Rule of Thirds

Divide the canvas into a 3x3 grid. Key elements belong at intersections or along grid lines, not dead center and not crammed into edges.

**Grid intersections (on a 1080x1080 canvas):**
- Top-left: (360, 360)
- Top-right: (720, 360)
- Bottom-left: (360, 720)
- Bottom-right: (720, 720)

**In StrikeFrame terms:**
- Headlines land strongest near the top-third line (y ≈ 33% of height)
- CTAs land strongest near the bottom-third line (y ≈ 66% of height)
- Stat blocks and supporting text live in the middle third
- Don't center everything vertically — let the grid create natural breathing room
- `headlineY` at exactly 50% height is almost always wrong

## 3. Horizon Awareness

When a background image has a visible horizon (water, sky, landscape), the horizon creates a hard visual line that text must respect.

**Rules:**
- Never place text directly on the horizon — it becomes unreadable and creates visual tension
- Place headlines above the horizon or well below it
- Use overlay opacity to darken the text region if needed, but don't rely on overlay alone
- If the horizon is in the upper third, put text in the lower two-thirds (and vice versa)

**In StrikeFrame terms:**
- Adjust `headlineY`, `subheadY` to avoid the horizon band
- Use `overlay.leftOpacity` / `overlay.rightOpacity` to protect text legibility on the text side
- If the horizon cuts through the middle third, consider `split-card` personality to contain text in a panel

## 4. Visual Hierarchy

The eye reads in order of: size → contrast → color → position. Use this to control what gets read first.

**Hierarchy stack (strongest to weakest):**
1. Headline — largest, highest contrast, boldest weight
2. Hero stat or key number — large size, accent color
3. Subhead — medium size, softer color
4. Supporting text / body — smaller, lower opacity
5. Footer / attribution — smallest, lowest contrast

**In StrikeFrame terms:**
- `headlineSize` should be at least 1.5x `subheadSize`
- Accent colors (`#63b3ed`, brand highlights) draw the eye — use on ONE focal element, not everything
- Footer text should be `rgba(255,255,255,0.3–0.5)`, never full white
- `valueSize` in statBlocks should dominate their region; `labelSize` should be at least 3x smaller

## 5. Reading Flow

Western audiences read in F-pattern (left-to-right, top-to-bottom) or Z-pattern (top-left → top-right → bottom-left → bottom-right).

**Rules:**
- Primary message (headline) goes top-left or top-center
- Supporting info flows downward
- CTA goes at the end of the reading path — bottom-center or bottom-right
- Never put the CTA above the headline
- Footer is last — bottom edge, low contrast

**In StrikeFrame terms:**
- `headlineY` < `subheadY` < `ctaRectY` < `footerY` — always
- For `editorial-left`, reading flows down the left column — keep `leftX` consistent
- For stat-heavy layouts, top row = context, bottom row = hero numbers, body text below

## 6. Breathing Room

Crowded designs feel cheap. Generous spacing signals quality.

**Rules:**
- Minimum 60px margin from any canvas edge to text
- Minimum 24px between headline and subhead
- Minimum 32px between subhead and CTA
- Stat blocks need at least 80px horizontal separation between columns
- Dividers need at least 20px clearance from adjacent text on each side

**In StrikeFrame terms:**
- `leftX` should be ≥ 60 (80 is a good default)
- Don't fill every pixel — leave at least 20% of the canvas visually empty
- If a layout feels tight, remove an element before shrinking spacing

## 7. Contrast and Legibility

Text that can't be read is worse than no text.

**Rules:**
- White text needs a dark region behind it (overlay opacity ≥ 0.4, or dark gradient, or panel)
- Dark text needs a light region behind it
- Never place light text on a light background area, even if the opposite side is dark
- Small text (< 18px) needs higher contrast than large text
- Accent colors must have enough contrast against their background — neon on dark works, pastel on dark doesn't

**In StrikeFrame terms:**
- If using a photo background, set `overlay.leftOpacity` ≥ 0.5 on the text side
- For gradient-only backgrounds, ensure `gradientStart` and text color have high contrast
- `footerColor` and `labelColor` can be low-opacity but must still be readable at the output resolution
- Test: if you squint and can't read it, the contrast is too low

## 8. Composition with Background Images

When a background image is provided, the agent MUST analyze the image before placing elements.

**Analysis checklist:**
1. Where is the subject? (left, center, right, distributed)
2. Where is the horizon? (upper third, middle, lower third, none)
3. Where are the bright/dark regions? (text needs dark behind it)
4. What's the overall mood? (match theme colors to the image mood)
5. Is there natural negative space? (place text there first)

**Decision flow:**
- Subject right → `editorial-left`, text on left, overlay heavier on left
- Subject left → flip: increase `leftX`, or use right-aligned text
- Subject centered → `centered-hero` with overlay vignette, or `split-card` panel
- Busy image with no clear negative space → `split-card` with semi-opaque panel
- Clean gradient or abstract → any personality works, use rule of thirds for placement

## 9. Color Harmony

Colors should feel intentional, not random.

**Rules:**
- Pick one accent color per design (for CTAs, hero stats, highlights)
- Accent should contrast with both the background and the primary text color
- Supporting text uses desaturated or lower-opacity versions of the primary palette
- Gradient backgrounds: start and end colors should be analogous (close on the color wheel), not complementary
- Match warmth: warm photo → warm accent; cool photo → cool accent

## 10. Platform-Aware Sizing

Different platforms crop differently. Design for the safe zone.

**Safe zones:**
- **Social square (1080x1080):** Full bleed, but keep key content within 900x900 center
- **Social portrait (1080x1350):** Top and bottom 135px may be cropped in feeds — keep headlines in middle 60%
- **LinkedIn landscape (1200x627):** Very short — headlines must be compact, subhead max 1 line
- **Landscape banner (1600x900):** Wide format — use horizontal spread, don't stack everything vertically

**In StrikeFrame terms:**
- Adjust `maxHeadlineChars` and `maxSubheadChars` per preset
- Portrait presets need tighter copy — fewer words, not just smaller font
- LinkedIn: `headlineSize` can be smaller since the format is intimate; don't waste the width

## 11. Template-Specific Design Guidance

### Benefit Stack
- 3-4 benefit items is the sweet spot. 5+ feels crowded on 1080x1080.
- Icon color should contrast with background but not compete with headline. `#63b3ed` (soft blue) works on dark backgrounds.
- Keep benefit labels under 32 characters — they should scan in 1-2 seconds.
- Place the benefit stack in the middle third of the canvas, below the headline/subhead, above the CTA.
- `spacing: 90` works for 3-4 items on social-square. Reduce to 70 for 5 items or portrait formats.

### Testimonial
- The open-quote mark is a visual anchor — it signals "this is a quote" before the text is read. Use accent color, not white.
- Italic quote text reads as authentic and personal. Keep `quoteMaxChars` tight (26-28) for dramatic line breaks.
- Star rating row goes between quote and attribution — it bridges the emotional quote and the factual source.
- Attribution (name + role) should be significantly smaller than the quote text. The quote is the hero, not the person.
- On centered layouts, all elements center-align. On editorial-left, everything left-aligns from `leftX`.

### Problem-Solution (Split Reveal)
- The vertical divider creates visual tension — it's the structural core of this template.
- Left side (problem) should feel weaker: lower opacity, lighter weight, muted color.
- Right side (solution) should feel stronger: full white, bold weight, optionally accent-colored label.
- Keep items to 3-5 rows. More than 5 and the comparison becomes a list, not a reveal.
- The `startY` should be well below the headline/subhead — leave breathing room. Minimum 100px gap.

### Offer Frame
- Sale price must visually dominate — `salePriceSize` should be at least 2.5x `originalPriceSize`.
- Strikethrough on original price must be visible but subtle — the eye should jump past it to the sale price.
- Savings badge (green pill) goes immediately below sale price for instant gratification.
- Offer text (e.g., "FREE SHIPPING OVER $99") sits below the savings badge at lower opacity — supporting info, not hero.
- Price block typically sits in the center-vertical zone (y ≈ 50-60% of canvas).

### Comparison Table
- The highlight column background creates visual weight — it draws the eye to the winning side.
- Row separators should be very subtle (`rgba(255,255,255,0.06)`) — they guide the eye without creating visual noise.
- Column headers use brand accent for the highlight column, muted for the competitor/status quo column.
- Keep row text short — comparison cells should be scannable in under 2 seconds per row.
- Works best on dark gradient backgrounds without photos — the table IS the visual.

### Authority
- Serif headline font (Georgia) signals credibility, editorial quality, and authority.
- The authority bar (credibility badges) sits in the lower third — it's proof, not headline.
- Bar fill should be nearly transparent (`rgba(255,255,255,0.06)`) — it's a subtle structural element.
- Credibility items separated by bullet characters, all uppercase with letter-spacing for editorial feel.
- Best paired with `centered-hero` personality and a strong background photo.

### Contrarian
- The bold statement IS the design. Headline should be the largest element on the canvas (60px+, 800 weight).
- Subhead provides the "why" — it should be significantly smaller and lower contrast than the headline.
- Dark overlay should be heavy (0.7+) to ensure the text punches through any background.
- CTA should feel like the natural resolution of the provocative statement.
- No extra visual elements needed — icons, badges, and decorations dilute the bold simplicity.

### Listicle
- Number prefixes create automatic visual structure — they guide the eye down the page.
- Keep all items at the same font size and weight for consistency.
- Items should be left-aligned with consistent X position — use `editorial-left` personality.
- 5 items is ideal. 3 feels thin, 7+ feels overwhelming.
- Each item should be a single line or two at most — tighten copy aggressively.
