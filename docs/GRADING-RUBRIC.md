# Static Content Quality Grading Rubric

*Research-backed scoring framework for automated image/creative QA/QC via vision model.*
*Sources: MrBeast Production Handbook (thumbnail/CTR science), Attention Insight visual hierarchy research, Nielsen/Faraday eye-tracking studies, Meta/Facebook ad benchmarks (WordStream, Focus Digital), Ramotion design hierarchy principles, OpusClip text readability data, JMU visual quality criteria.*

---

## Scoring System

**Total: 100 points across 8 dimensions. Minimum passing: 72/100.**
**Tim/X threshold: 85/100 minimum.**

Each dimension scored 1-5:
- **1** = Failing (fundamental problems that kill performance)
- **2** = Below standard (noticeable issues, will hurt CTR/engagement)
- **3** = Acceptable (meets baseline, no major issues)
- **4** = Good (professional quality, competitive with paid creative)
- **5** = Excellent (best-in-class, scroll-stopping, would outperform benchmarks)

Weight multiplied per dimension to produce 0-100 total.

---

## Dimension 1: Scroll-Stop Power (×4 = 20 pts max)

*"CTR is what dictates what we do. If 100M people see our thumbnail and 10M click, that's 10% CTR." — MrBeast*
*"Bold, high-contrast image with a real person's face (ideally making eye contact), layered with a short emotional hook" — SocialInsider 2025*
*"Colour contrast creates focus points and makes thumbnails easier to process" — LowKeyJude (733 MrBeast videos analyzed)*
*"The first 1.7 seconds of exposure determine whether a user stops scrolling" — Meta internal research*

| Score | Criteria |
|-------|----------|
| 5 | Immediately grabs attention. Strong focal point. High contrast between subject and background. Would stop the scroll in a busy feed. Face or product dominates with clear emotional or curiosity trigger. |
| 4 | Good attention-grab. Clear focal point. Competitive with professional paid creative. |
| 3 | Acceptable. Has a subject and some contrast but doesn't demand attention. Would blend into a feed. |
| 2 | Weak visual impact. Low contrast, no clear focal point. Easy to scroll past. |
| 1 | Invisible in a feed. No contrast, no subject, looks like noise or generic stock. |

**Vision model checks:**
- Is there a clear dominant focal point?
- Is there high contrast between the primary subject and background?
- Does the image have a single clear "thing to look at"?
- Would this image stop you from scrolling?
- Is there a face visible? (faces increase CTR — MrBeast, SocialInsider)

---

## Dimension 2: Visual Composition & Layout (×3 = 15 pts max)

*"Visual hierarchy tells the viewer what to look at first, second, and third" — UseVisuals*
*"Embrace whitespace: avoid clutter to make key elements pop, improving focus and CTR" — Attention Insight*
*"Faraday (2000) eye tracking: variables that influence attention include size, color, position, and isolation" — The Arts Journal*
*Rule of thirds, golden ratio, Z-pattern/F-pattern reading flow — established design principles*

| Score | Criteria |
|-------|----------|
| 5 | Clear visual hierarchy: eye knows where to go first, second, third. Clean layout with intentional whitespace. Rule of thirds or deliberate symmetry. No clutter. Background supports rather than competes with subject. |
| 4 | Good hierarchy with minor issues. Layout is clean and organized. Subject is well-positioned. |
| 3 | Acceptable layout. Elements are present but hierarchy isn't immediately obvious. Some clutter or competing elements. |
| 2 | Cluttered or confusing layout. No clear reading path. Elements compete for attention. |
| 1 | No visual organization. Chaotic or empty. Elements randomly placed. |

**Vision model checks:**
- Is there a clear visual hierarchy (what do you see first, second, third)?
- Is there adequate whitespace/breathing room?
- Is the layout clean and organized?
- Does the background support the subject or compete with it?

---

## Dimension 3: Typography & Text Readability (×3 = 15 pts max)

*"Large bold headlines paired with smaller supporting text guide the eye naturally" — Attention Insight*
*"White text on black = 21:1 contrast ratio (gold standard). WCAG AA minimum: 4.5:1" — OpusClip + W3C*
*"Instagram requires 20% larger fonts than YouTube for readability" — OpusClip*
*"Me like simple. 50M people need to understand it instantly." — MrBeast*

| Score | Criteria |
|-------|----------|
| 5 | Headline instantly readable at thumbnail size. High contrast text (≥4.5:1 ratio). Clear size hierarchy (headline > subhead > body). No text clipped by edges. Font choice is clean and professional. Message understood in under 2 seconds. |
| 4 | Text readable and well-contrasted. Minor hierarchy issues. Message is clear. |
| 3 | Text present and readable with effort. Some contrast or size issues. Message takes a moment to parse. |
| 2 | Text hard to read. Low contrast, too small, or competing with background imagery. |
| 1 | Text unreadable, missing, or completely lost against the background. |

**Vision model checks:**
- Can you read the headline immediately?
- Is there clear text size hierarchy (big headline, smaller supporting text)?
- Is the text-to-background contrast high enough to read at a glance?
- Is the text within safe zones (not at extreme edges)?
- Could someone understand the message in under 2 seconds? (MrBeast simplicity test)

---

## Dimension 4: Color & Contrast (×2 = 10 pts max)

*"Contrasting colors create focus points and make thumbnails easier to process" — LowKeyJude (MrBeast analysis)*
*"Color and contrast help specific elements stand out or recede" — Ramotion*
*"Meta rewards engaging and relevant ads with lower CPCs" — Ad quality relevance score*

| Score | Criteria |
|-------|----------|
| 5 | Intentional color palette. Strong contrast between key elements. Colors evoke the right mood for the content type. Brand-consistent. No clashing or muddy colors. |
| 4 | Good use of color. Adequate contrast. Mostly brand-consistent. |
| 3 | Acceptable colors. Nothing offensive but not strategic. Generic palette. |
| 2 | Poor color choices. Muddy, low-contrast, or clashing colors that hurt readability. |
| 1 | Terrible color execution. Colors fight each other, no contrast, or so dark/bright that content is lost. |

**Vision model checks:**
- Is there intentional contrast between primary and secondary elements?
- Do the colors support readability or fight against it?
- Is the overall palette appropriate for the content type (professional, energetic, etc.)?

---

## Dimension 5: Image Quality & Production Value (×2 = 10 pts max)

*"Better lighting reduces drop-off" — MrBeast (tested correlation)*
*JMU Educational Video Rubric: lighting and image quality as independent scored criteria*
*"Ad quality and relevance score: Meta rewards engaging and relevant ads with lower CPCs" — Facebook benchmarks*

| Score | Criteria |
|-------|----------|
| 5 | Sharp, high-resolution, no artifacts. Professional product photography or well-executed composite. No visible compression, aliasing, or stretching. Clean edges on all elements. |
| 4 | Good quality with minor issues. Slight compression or scaling artifacts that don't distract. |
| 3 | Acceptable quality. Some visible artifacts or soft areas. Clearly not a stock photo but not polished. |
| 2 | Noticeable quality issues. Blurry, pixelated, or stretched elements. Visible compression. |
| 1 | Severely degraded. Heavy pixelation, major artifacts, stretched/distorted, or clearly broken. |

**Vision model checks:**
- Is the image sharp and high-resolution?
- Are there visible compression artifacts, blurriness, or stretching?
- Are edges clean (no aliasing or jagged borders on text/shapes)?
- Does it look professional or amateurish?

---

## Dimension 6: Content Value & Message Clarity (×2 = 10 pts max)

*"144% more likely to add to cart after seeing product content" — Invesp*
*"Credibility, expertise, authenticity influence purchasing behavior" — Frontiers 2025*
*"Creativity over production value. Make the best YOUTUBE content, not the best-produced." — MrBeast*
*"Hook format with escalating stakes" — MrBeast retention architecture*

| Score | Criteria |
|-------|----------|
| 5 | Message is instantly clear. Product/benefit is obvious. One clear takeaway. A non-expert understands it in under 2 seconds. Feels authentic, not generic template. |
| 4 | Clear message with minor ambiguity. Product/benefit visible. Feels purposeful. |
| 3 | Message is present but takes effort to parse. Product somewhat visible. Generic feel. |
| 2 | Unclear what the image is selling or saying. Vague or confusing message. |
| 1 | No discernible message or value. Random imagery with no commercial purpose. |

**Vision model checks:**
- Is there a clear product or benefit being communicated?
- Can you understand what's being sold/promoted in under 2 seconds?
- Does it feel authentic and credible, or like generic AI/template output?
- Is there a clear CTA or next action implied?

---

## Dimension 7: Brand Consistency & Authenticity (×2 = 10 pts max)

*"Slop risk" — StrikeFrame existing review contract criterion*
*"Reject generic AI/template slop. Reject visuals that do not earn the copy." — StrikeFrame QA prompt*
*"Leave a good impression with your last video. That impression carries into CTR on the next one." — MrBeast*

| Score | Criteria |
|-------|----------|
| 5 | Unmistakably on-brand. Consistent with the brand's visual language. Feels like a real company made this, not a template. No slop or generic AI artifacts. Would build trust. |
| 4 | Mostly on-brand. Consistent visual language with minor deviations. Professional feel. |
| 3 | Generic but not off-brand. Could be any company's creative. Template feel but acceptable. |
| 2 | Off-brand or slop-adjacent. Feels auto-generated. Decorative elements that don't mean anything. |
| 1 | Obvious AI slop, generic template, or actively damages brand perception. |

**Vision model checks:**
- Does this look like a real brand created it or like a template?
- Are there decorative elements (fake dashboards, abstract UI, meaningless icons) that don't serve the message?
- Is the visual style consistent with what you'd expect from this brand?
- Does it feel authentic or generated?

---

## Dimension 8: Platform Optimization (×2 = 10 pts max)

*Safe zone standards: inner 80% for text, platform UI zones top/bottom*
*"Images with faces get 38% more likes on Instagram" — Georgia Tech study*
*Meta ad specs: 1080×1080 (feed), 1080×1920 (stories/reels), text <20% of image area*

| Score | Criteria |
|-------|----------|
| 5 | Correct dimensions for target platform. Nothing in platform UI zones. Text within safe area. Would work as a thumbnail. Optimized for the platform's feed behavior. |
| 4 | Correct dimensions. Minor content near edges but not critical. |
| 3 | Correct dimensions but no safe-zone consideration. |
| 2 | Wrong dimensions or significant content hidden by platform UI. |
| 1 | Wrong dimensions, wrong ratio, or completely unoptimized. |

**Automated checks:**
- Resolution matches target platform (1080×1080, 1080×1350, 1080×1920)
- File size within platform limits
- Text-to-image ratio (Meta: <20% text for optimal delivery)
- Important content within safe zones

---

## Score Interpretation

| Total Score | Rating | Action |
|-------------|--------|--------|
| 90-100 | Excellent | Ship it. |
| 85-89 | Good | Ship for most channels. Tim/X: review flagged items. |
| 72-84 | Passing | Review flagged items. Fix if easy, otherwise usable for lower-stakes channels. |
| 60-71 | Below Standard | Needs iteration. Fix lowest-scoring dimensions. |
| <60 | Failing | Major rework or reject. Do not publish. |

**Tim/X override:** Minimum 85/100 + slop_risk=low + brand_score≥4. Otherwise downgrade to fail.

---

## Integration with StrikeFrame

### Where This Fits

```
Config → render.js → image.jpg → qaqc.py (layout checks) → vision_review.py (content quality grading) → report
```

The grading rubric replaces the simple "is this slop?" prompt in `vision_review.py` with dimension-specific scoring. The existing review contract fields map to rubric dimensions:

| Existing Field | → Rubric Dimension |
|---------------|-------------------|
| `overall_score` | Total weighted score (0-100 mapped to 0-10) |
| `readability_score` | Dimension 3: Typography & Text Readability |
| `copy_visual_fit_score` | Dimension 6: Content Value & Message Clarity |
| `channel_fit_score` | Dimension 8: Platform Optimization |
| `slop_risk` | Dimension 7: Brand Consistency & Authenticity |

### New Fields Added
- `scroll_stop_score` — Dimension 1
- `composition_score` — Dimension 2
- `color_contrast_score` — Dimension 4
- `image_quality_score` — Dimension 5
- `dimension_scores` — full breakdown object with all 8 scores

### Prompt Changes
The prompt in `prompts/vision-review-generic.txt` needs to be replaced with a rubric-aware prompt that scores each dimension and returns structured results.

---

*Sources cited inline. Rubric structure adapted from the video-edit quality grading framework with static content-specific adaptations.*
