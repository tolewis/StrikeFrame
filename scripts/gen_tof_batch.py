#!/usr/bin/env python3
"""Generate TOF (top of funnel) ad batch config — 10 images × 5 copy variants = 50 ads."""
import json, math

STOCK = "/home/tlewis/Dropbox/Tim/TackleRoom/Creative/Assets/AdobeStock"
OUT = "/mnt/raid/Data/tmp/ads/tof"

# 5 copy variants — each element has one job:
#   headline = emotional hook
#   subhead  = one supporting sentence (value prop or emotion)
#   cta      = stat or offer (the reason to click)
VARIANTS = [
    {"id": "a",
     "headline": "This Is The Life.",
     "subhead": "Offshore gear for the ones who live it.",
     "cta": "200+ PRODUCTS IN STOCK"},
    {"id": "b",
     "headline": "The Ocean Doesn't Negotiate.",
     "subhead": "Neither does our gear.",
     "cta": "FREE SHIPPING OVER $69"},
    {"id": "c",
     "headline": "Rigged Right. Every Time.",
     "subhead": "Tested by the anglers who sell it.",
     "cta": "★★★★★  RATED 4.8 BY ANGLERS"},
    {"id": "d",
     "headline": "Built For Days Like This.",
     "subhead": "No middlemen. No markup. Just gear.",
     "cta": "DIRECT-TO-ANGLER PRICING"},
    {"id": "e",
     "headline": "You Don't Outwork The Ocean.",
     "subhead": "You out-gear it.",
     "cta": "JOIN 12,000+ ANGLERS"},
]

# Per-image config: composition-aware layout decisions
IMAGES = [
    {
        "id": "372953083", "name": "sportfisher-running",
        "personality": "editorial-left",
        "headlineY": 280, "subheadY": 470, "leftX": 80,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 90, "subheadSize": 58,
        "overlay": {"leftColor": "8,30,50", "midColor": "8,30,50", "rightColor": "8,30,50",
                     "leftOpacity": 0.55, "midOpacity": 0.35, "rightOpacity": 0.15, "vignetteBottom": 0.35},
        "note": "Boat right, open sky/water left. Text on left above horizon."
    },
    {
        "id": "133588506", "name": "underwater-mahi-sunlight",
        "personality": "centered-hero", "align": "center",
        "headlineY": 200, "subheadY": 610, "leftX": 540,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 96, "subheadSize": 60,
        "overlay": {"leftColor": "0,20,40", "midColor": "0,20,40", "rightColor": "0,20,40",
                     "leftOpacity": 0.25, "midOpacity": 0.2, "rightOpacity": 0.25, "vignetteBottom": 0.45},
        "note": "Mahi bottom-center, bright sky above. Headline in bright zone, subhead in dark water below."
    },
    {
        "id": "175678582", "name": "reel-sunset-silhouette",
        "personality": "centered-hero", "align": "center",
        "headlineY": 210, "subheadY": 600, "leftX": 540,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 96, "subheadSize": 60,
        "overlay": {"leftColor": "10,20,30", "midColor": "10,20,30", "rightColor": "10,20,30",
                     "leftOpacity": 0.35, "midOpacity": 0.25, "rightOpacity": 0.35, "vignetteBottom": 0.5},
        "note": "Reel center-left, dramatic sunset sky. Headline in sky, subhead in dark water."
    },
    {
        "id": "219637627", "name": "aerial-sharks-boat",
        "personality": "editorial-left",
        "headlineY": 260, "subheadY": 450, "leftX": 80,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 90, "subheadSize": 58,
        "overlay": {"leftColor": "0,30,40", "midColor": "0,30,40", "rightColor": "0,30,40",
                     "leftOpacity": 0.45, "midOpacity": 0.25, "rightOpacity": 0.1, "vignetteBottom": 0.2},
        "note": "Boat right, sharks center, turquoise water left. Clean text space left."
    },
    {
        "id": "331722964", "name": "fighting-fish-dusk",
        "personality": "editorial-left",
        "headlineY": 240, "subheadY": 430, "leftX": 80,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 90, "subheadSize": 58,
        "overlay": {"leftColor": "8,20,40", "midColor": "8,20,40", "rightColor": "8,20,40",
                     "leftOpacity": 0.5, "midOpacity": 0.3, "rightOpacity": 0.15, "vignetteBottom": 0.35},
        "note": "Man fighting fish on right side of boat, dusk sky. Text on left."
    },
    {
        "id": "284446852", "name": "underwater-mahi-deep",
        "personality": "editorial-left",
        "headlineY": 280, "subheadY": 470, "leftX": 80,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 90, "subheadSize": 58,
        "overlay": {"leftColor": "0,10,30", "midColor": "0,10,30", "rightColor": "0,10,30",
                     "leftOpacity": 0.35, "midOpacity": 0.2, "rightOpacity": 0.1, "vignetteBottom": 0.3},
        "note": "Mahi center-right in deep blue. Dark blue space on left for text."
    },
    {
        "id": "229283027", "name": "reel-golden-sunset",
        "personality": "centered-hero", "align": "center",
        "headlineY": 230, "subheadY": 600, "leftX": 540,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 96, "subheadSize": 60,
        "overlay": {"leftColor": "20,10,0", "midColor": "20,10,0", "rightColor": "20,10,0",
                     "leftOpacity": 0.3, "midOpacity": 0.2, "rightOpacity": 0.3, "vignetteBottom": 0.45},
        "note": "Reel handle silhouette center, warm golden sky. Text above and below."
    },
    {
        "id": "337378282", "name": "rod-holders-lures",
        "personality": "editorial-left",
        "headlineY": 260, "subheadY": 450, "leftX": 80,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 90, "subheadSize": 58,
        "overlay": {"leftColor": "10,15,25", "midColor": "10,15,25", "rightColor": "10,15,25",
                     "leftOpacity": 0.55, "midOpacity": 0.35, "rightOpacity": 0.15, "vignetteBottom": 0.35},
        "note": "Rods/reels/lures right side, sky+ocean visible left. Text on left."
    },
    {
        "id": "345435684", "name": "sportfisher-jetty",
        "personality": "centered-hero", "align": "center",
        "headlineY": 200, "subheadY": 600, "leftX": 540,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 96, "subheadSize": 60,
        "overlay": {"leftColor": "5,25,40", "midColor": "5,25,40", "rightColor": "5,25,40",
                     "leftOpacity": 0.35, "midOpacity": 0.25, "rightOpacity": 0.35, "vignetteBottom": 0.4},
        "note": "Boat center-left running past jetty. Big sky above, water below. Text top + bottom."
    },
    {
        "id": "991789270", "name": "fisherman-rough-seas",
        "personality": "centered-hero", "align": "center",
        "headlineY": 200, "subheadY": 610, "leftX": 540,
        "maxHeadlineChars": 14, "maxSubheadChars": 24,
        "headlineSize": 96, "subheadSize": 60,
        "overlay": {"leftColor": "10,15,20", "midColor": "10,15,20", "rightColor": "10,15,20",
                     "leftOpacity": 0.4, "midOpacity": 0.3, "rightOpacity": 0.35, "vignetteBottom": 0.45},
        "note": "Fisherman left hauling nets in rough seas. Gritty/tough. Text centered above + below."
    },
]


def wrap_text(text, max_chars):
    """Mirror render.js wrapText logic."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        nxt = f"{current} {word}" if current else word
        if len(nxt) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = nxt
    if current:
        lines.append(current)
    return lines


def est_text_width(text, font_size):
    """Estimate pixel width of text. ~0.58 average char width ratio for sans-serif."""
    return round(len(text) * font_size * 0.58)


def build_render(img, variant):
    is_left = img["personality"] == "editorial-left"
    align = "left" if is_left else "center"

    # Dynamic subhead placement: push down if headline wraps to 3+ lines
    headline_lines = wrap_text(variant["headline"], img["maxHeadlineChars"])
    headline_step = 88  # render.js social-square headlineStep
    headline_bottom = img["headlineY"] + (len(headline_lines) - 1) * headline_step + round(img["headlineSize"] * 0.3)
    subhead_y = max(img["subheadY"], headline_bottom + 30)

    subhead_size = img["subheadSize"]
    subhead_step = round(subhead_size * 1.25)
    subhead_lines = wrap_text(variant["subhead"], img["maxSubheadChars"])
    num_lines = len(subhead_lines)

    # Dynamic CTA placement: subhead bottom + 50px breathing room
    subhead_bottom = subhead_y + (num_lines - 1) * subhead_step + round(subhead_size * 0.3)
    cta_y = subhead_bottom + 50

    # CTA button: sized to fit text with 80px horizontal padding
    cta_height = 90
    cta_size = 44
    cta_text_px = est_text_width(variant["cta"], cta_size) + 80

    if is_left:
        cta_rect_x = img["leftX"]
        cta_width = max(620, cta_text_px)
    else:
        cta_width = max(810, cta_text_px)
        cta_rect_x = round((1080 - cta_width) / 2)

    return {
        "_comment": f"=== {img['name']} | Variant {variant['id'].upper()} ===",
        "output": f"{OUT}/{img['name']}-{variant['id']}.jpg",
        "backgroundPath": f"{STOCK}/AdobeStock_{img['id']}.jpeg",
        "text": {
            "headline": variant["headline"],
            "subhead": variant["subhead"],
            "cta": variant["cta"],
            "footer": "THETACKLEROOM.COM"
        },
        "overlay": img["overlay"],
        "typography": {
            "headlineFontFamily": "Montserrat, Arial, sans-serif",
            "bodyFontFamily": "Source Sans Pro, Arial, sans-serif",
            "headlineSize": img["headlineSize"],
            "subheadSize": subhead_size,
            "headlineWeight": 800,
            "subheadWeight": 400,
            "subheadLineHeight": subhead_step,
            "ctaSize": cta_size,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4
        },
        "layout": {
            "personality": img["personality"],
            "align": align,
            "leftX": img["leftX"],
            "headlineY": img["headlineY"],
            "subheadY": subhead_y,
            "maxHeadlineChars": img["maxHeadlineChars"],
            "maxSubheadChars": img["maxSubheadChars"],
            "ctaRectX": cta_rect_x,
            "ctaRectY": cta_y,
            "ctaX": cta_rect_x + cta_width // 2,
            "ctaY": cta_y + cta_height // 2,
            "ctaWidth": cta_width,
            "ctaHeight": cta_height,
            "footerY": 1040
        }
    }


def main():
    config = {
        "defaults": {
            "preset": "social-square",
            "template": "banner",
            "theme": {
                "headlineColor": "#FFFFFF",
                "subheadColor": "#e4e4e7",
                "footerColor": "rgba(255,255,255,0.35)",
                "ctaTextColor": "#FFFFFF",
                "ctaFill": "rgba(232,93,58,0.92)",
                "ctaStroke": "rgba(255,160,120,0.35)"
            }
        },
        "renders": []
    }

    for img in IMAGES:
        for variant in VARIANTS:
            config["renders"].append(build_render(img, variant))

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-tof-50.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    # Print button width summary
    print(f"Generated {len(config['renders'])} renders -> {out_path}")
    for v in VARIANTS:
        w = est_text_width(v["cta"], 44) + 80
        print(f"  Variant {v['id']}: \"{v['cta']}\" -> est {w}px")


if __name__ == "__main__":
    main()
