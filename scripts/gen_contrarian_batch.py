#!/usr/bin/env python3
"""Generate contrarian hook ad batch — bold statement + product reveal.
Experimental, low volume (LMNT, Black Rifle Coffee model)."""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_DARK, OCEAN_BACKGROUNDS,
)

OUT = "/mnt/raid/Data/tmp/ads/contrarian"

# Bold contrarian statements that challenge fishing conventional wisdom.
ADS = [
    {
        "id": "planer-setup-wrong",
        "headline": "Your Planer Setup Is Probably Wrong.",
        "subhead": "One missing piece and you're trolling dead bait at the wrong depth.",
        "cta": "FIX YOUR SETUP",
    },
    {
        "id": "tackle-shop-advice",
        "headline": "Stop Trusting Tackle Shop Advice.",
        "subhead": "The kid behind the counter has never fought a tuna. Our captains have.",
        "cta": "SHOP CAPTAIN'S PICKS",
    },
    {
        "id": "spread-wont-raise",
        "headline": "That Spread Won't Raise Fish.",
        "subhead": "Dead squid imitations don't trigger strikes. Realistic ones do.",
        "cta": "UPGRADE YOUR SPREAD",
    },
    {
        "id": "cheap-dredge",
        "headline": "A Cheap Dredge Costs More Than An Expensive One.",
        "subhead": "Lost fish, lost trips, lost confidence. Buy it once. Buy it right.",
        "cta": "SHOP DREDGES",
    },
    {
        "id": "six-orders",
        "headline": "You Don't Need 6 Orders To Build One Rig.",
        "subhead": "Everything matched. Everything included. One order.",
        "cta": "SHOP COMPLETE KITS",
    },
    {
        "id": "not-serious",
        "headline": "If You're Not Running Teasers, You're Not Serious.",
        "subhead": "Every tournament boat in the Gulf runs a dredge. Not some. Every one.",
        "cta": "SHOP TEASERS",
    },
]


def build_render(ad, bg_index):
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]

    return {
        "_comment": f"=== Contrarian: {ad['id']} ===",
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
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 60,
            "subheadSize": 26,
            "headlineWeight": 800,
            "subheadWeight": 400,
            "ctaSize": 24,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "centered-hero",
            "align": "center",
            "leftX": 540,
            "headlineY": 300,
            "subheadY": 580,
            "maxHeadlineChars": 18,
            "maxSubheadChars": 32,
            "ctaWidth": 340,
            "ctaHeight": 64,
            "ctaRectX": 370,
            "ctaRectY": 780,
            "ctaX": 540,
            "ctaY": 812,
            "footerY": 1050,
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

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-contrarian.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Ads: {len(ADS)}")
    print(f"Renders generated: {len(config['renders'])}")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
