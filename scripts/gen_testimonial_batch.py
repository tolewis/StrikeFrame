#!/usr/bin/env python3
"""Generate testimonial ad batch — captain/customer quotes + star ratings.
Social proof is the #1 trust builder for offshore skeptics (Dr. Squatch, Googan model).
2 variants per review: centered quote card + editorial-left photo card."""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_DARK, OVERLAY_OCEAN,
    OCEAN_BACKGROUNDS,
)

OUT = "/mnt/raid/Data/tmp/ads/testimonial"

# Curated captain and customer quotes from Batch 3 manifest + product data.
# In production, load from a reviews CSV or Shopify export.
REVIEWS = [
    {
        "quote": "If you aren't pulling dredges you aren't competing.",
        "stars": 5,
        "name": "Capt. Wheeler",
        "role": "Tournament Captain, Islamorada",
        "category": "dredges",
    },
    {
        "quote": "90% hookup rate with teasers running. Without them, you're leaving fish in the water.",
        "stars": 5,
        "name": "Capt. Cameron",
        "role": "Charter Captain, Florida Keys",
        "category": "daisy_chains",
    },
    {
        "quote": "This dredge changed our tournament results completely. The realism is unmatched.",
        "stars": 5,
        "name": "Capt. Rosher",
        "role": "24-marlin tournament record holder",
        "category": "dredges",
    },
    {
        "quote": "Complete kit, every piece matched. Saved me two hours of rigging time.",
        "stars": 5,
        "name": "Jake M.",
        "role": "Center Console Owner, Gulf Coast",
        "category": "planers",
    },
    {
        "quote": "The bridle kit is perfect. No guesswork, no missing hardware, just clip and fish.",
        "stars": 5,
        "name": "David R.",
        "role": "Weekend Tournament Angler",
        "category": "planers",
    },
    {
        "quote": "Best daisy chain I've run. Flying fish pattern raised blues three trips in a row.",
        "stars": 5,
        "name": "Capt. Santos",
        "role": "Charter Captain, Outer Banks",
        "category": "daisy_chains",
    },
    {
        "quote": "Ran this spread at the Bahamas Championship. 36 billfish released. Enough said.",
        "stars": 5,
        "name": "Capt. Torres",
        "role": "Bahamas Championship Winner",
        "category": "lures",
    },
    {
        "quote": "I've ordered from TackleRoom three times now. The leader material is exactly what I need.",
        "stars": 5,
        "name": "Mike K.",
        "role": "Offshore Angler, Virginia Beach",
        "category": "line_leader",
    },
    {
        "quote": "716lb blue marlin from a 42ft center console. This gear handles anything.",
        "stars": 5,
        "name": "Capt. Williams",
        "role": "Sport Fishing Captain",
        "category": "lures",
    },
    {
        "quote": "The Phat Squid dredge pulls fish up from 200 feet. Nothing else compares.",
        "stars": 5,
        "name": "Capt. Rivera",
        "role": "Tournament Captain, Miami",
        "category": "dredges",
    },
    {
        "quote": "Finally a fighting belt that doesn't bruise your hips after a 40-minute tuna fight.",
        "stars": 5,
        "name": "Chris L.",
        "role": "Big Game Angler",
        "category": "belts",
    },
    {
        "quote": "Compact enough for my center console but effective enough for tournament fishing.",
        "stars": 5,
        "name": "Tom H.",
        "role": "Center Console Owner, Destin FL",
        "category": "dredges",
    },
]


def build_render_centered(review, bg_index):
    """Centered quote card — big quote, stars, attribution centered on dark background."""
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]
    slug = review["name"].lower().replace(" ", "-").replace(".", "")

    return {
        "_comment": f"=== Testimonial: {review['name']} | centered ===",
        "output": f"{OUT}/{slug}-centered.jpg",
        "backgroundPath": bg,
        "text": {
            "headline": "",
            "subhead": "",
            "cta": "SHOP NOW",
            "footer": BRAND["name"],
        },
        "overlay": OVERLAY_DARK,
        "typography": {
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 1,
            "subheadSize": 1,
            "ctaSize": 22,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "centered-hero",
            "align": "center",
            "leftX": 540,
            "headlineY": 60,
            "subheadY": 80,
            "maxHeadlineChars": 1,
            "maxSubheadChars": 1,
            "ctaWidth": 280,
            "ctaHeight": 58,
            "ctaRectX": 400,
            "ctaRectY": 920,
            "ctaX": 540,
            "ctaY": 949,
            "footerY": 1050,
        },
        "testimonial": {
            "quote": review["quote"],
            "stars": review["stars"],
            "starSize": 32,
            "name": review["name"],
            "role": review["role"],
            "quoteSize": 36,
            "quoteMaxChars": 26,
            "nameSize": 24,
            "startY": 280,
            "quoteColor": "#ffffff",
            "attributionColor": "rgba(255,255,255,0.6)",
        },
    }


def build_render_editorial(review, bg_index):
    """Editorial-left quote card — quote on left side with lifestyle background."""
    bg = OCEAN_BACKGROUNDS[(bg_index + 3) % len(OCEAN_BACKGROUNDS)]
    slug = review["name"].lower().replace(" ", "-").replace(".", "")

    return {
        "_comment": f"=== Testimonial: {review['name']} | editorial ===",
        "output": f"{OUT}/{slug}-editorial.jpg",
        "backgroundPath": bg,
        "text": {
            "headline": "",
            "subhead": "",
            "cta": "SHOP NOW",
            "footer": BRAND["name"],
        },
        "overlay": {
            "leftColor": "8,20,35", "midColor": "8,20,35", "rightColor": "8,20,35",
            "leftOpacity": 0.7, "midOpacity": 0.45, "rightOpacity": 0.15,
            "vignetteBottom": 0.3,
        },
        "typography": {
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 1,
            "subheadSize": 1,
            "ctaSize": 22,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "editorial-left",
            "align": "left",
            "leftX": 80,
            "headlineY": 60,
            "subheadY": 80,
            "maxHeadlineChars": 1,
            "maxSubheadChars": 1,
            "ctaWidth": 260,
            "ctaHeight": 58,
            "ctaRectX": 80,
            "ctaRectY": 920,
            "ctaX": 210,
            "ctaY": 949,
            "footerY": 1050,
        },
        "testimonial": {
            "quote": review["quote"],
            "stars": review["stars"],
            "starSize": 28,
            "name": review["name"],
            "role": review["role"],
            "quoteSize": 32,
            "quoteMaxChars": 22,
            "nameSize": 22,
            "startY": 280,
            "quoteColor": "#ffffff",
            "attributionColor": "rgba(255,255,255,0.6)",
        },
    }


def main():
    os.makedirs(OUT, exist_ok=True)

    config = {
        "defaults": {
            "preset": "social-square",
            "template": "banner",
            "theme": THEME_DEFAULT,
        },
        "renders": [],
    }

    for i, review in enumerate(REVIEWS):
        config["renders"].append(build_render_centered(review, i))
        config["renders"].append(build_render_editorial(review, i))

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-testimonial.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Reviews: {len(REVIEWS)}")
    print(f"Renders generated: {len(config['renders'])} ({len(REVIEWS)} reviews x 2 variants)")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
