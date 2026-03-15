#!/usr/bin/env python3
"""Generate authority/advertorial ad batch — serif headlines + credibility bars.
Tournament results and captain endorsements (LMNT, Dr. Squatch model)."""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_DARK, OCEAN_BACKGROUNDS,
)

OUT = "/mnt/raid/Data/tmp/ads/authority"

# Authority-style ads with credibility markers
ADS = [
    {
        "id": "tournament-results",
        "headline": "36 Billfish Released At The Bahamas Championship.",
        "subhead": "The gear behind the numbers.",
        "publications": ["BAHAMAS CHAMPIONSHIP", "FLORIDA KEYS", "TOURNAMENT PROVEN"],
        "cta": "SHOP THE GEAR",
    },
    {
        "id": "captain-trust",
        "headline": "What Charter Captains Actually Run.",
        "subhead": "Not what they get paid to say. What they buy with their own money.",
        "publications": ["ISLAMORADA CHARTERS", "GULF COAST CAPTAINS", "OUTER BANKS CREWS"],
        "cta": "SEE CAPTAIN'S PICKS",
    },
    {
        "id": "marlin-record",
        "headline": "716lb Blue Marlin. 42ft Center Console.",
        "subhead": "The same tackle is in our shop right now.",
        "publications": ["VERIFIED CATCH", "CENTER CONSOLE RECORD", "OFFSHORE PROVEN"],
        "cta": "SHOP NOW",
    },
    {
        "id": "hookup-rate",
        "headline": "90% Hookup Rate With Teasers Running.",
        "subhead": "Without them, you're leaving fish in the water.",
        "publications": ["CAPT. CAMERON", "FLORIDA KEYS CHARTERS", "FIELD TESTED"],
        "cta": "SHOP TEASERS",
    },
    {
        "id": "reorder-rate",
        "headline": "Our Most Reordered Products Tell The Real Story.",
        "subhead": "When captains come back for a second order, you know it works.",
        "publications": ["HIGH REORDER RATE", "CAPTAIN VERIFIED", "DIRECT TO ANGLER"],
        "cta": "SEE BEST SELLERS",
    },
    {
        "id": "offshore-specialist",
        "headline": "Built By Offshore Anglers. For Offshore Anglers.",
        "subhead": "Every product tested on the water before it ships.",
        "publications": ["SPECIALIST TACKLE", "TESTED OFFSHORE", "ANGLER OWNED"],
        "cta": "SHOP TACKLEROOM",
    },
]


def build_render(ad, bg_index):
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]

    return {
        "_comment": f"=== Authority: {ad['id']} ===",
        "output": f"{OUT}/{ad['id']}.jpg",
        "backgroundPath": bg,
        "text": {
            "headline": ad["headline"],
            "subhead": ad["subhead"],
            "cta": ad["cta"],
            "footer": BRAND["name"],
        },
        "overlay": OVERLAY_DARK,
        "typography": {
            "headlineFontFamily": BRAND["serif_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 50,
            "subheadSize": 24,
            "headlineWeight": 700,
            "subheadWeight": 400,
            "ctaSize": 22,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "centered-hero",
            "align": "center",
            "leftX": 540,
            "headlineY": 260,
            "subheadY": 520,
            "maxHeadlineChars": 26,
            "maxSubheadChars": 38,
            "ctaWidth": 320,
            "ctaHeight": 58,
            "ctaRectX": 380,
            "ctaRectY": 800,
            "ctaX": 540,
            "ctaY": 829,
            "footerY": 1050,
        },
        "authorityBar": {
            "publications": ad["publications"],
            "barY": 120,
            "barHeight": 44,
            "barFill": "rgba(255,255,255,0.06)",
            "textSize": 12,
            "textColor": "rgba(255,255,255,0.45)",
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

    for i, ad in enumerate(ADS):
        config["renders"].append(build_render(ad, i))

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-authority.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Ads: {len(ADS)}")
    print(f"Renders generated: {len(config['renders'])}")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
