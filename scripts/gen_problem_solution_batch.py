#!/usr/bin/env python3
"""Generate problem-solution ad batch — bold problem headline + solution reveal.
Directly maps to 6 thesis bank entries (Mystery Tackle Box, Native model).
3 headline variants per thesis."""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_DARK, OCEAN_BACKGROUNDS,
)

OUT = "/mnt/raid/Data/tmp/ads/problem-solution"

# Problem/solution theses from the thesis bank + hook matrix.
# Each entry: problem statement, solution items, CTA, landing direction.
THESES = [
    {
        "id": "planers",
        "headlines": [
            "Most Planer Setups Fail Before They Hit The Water.",
            "The Wrong Bridle Size Will Cost You Fish.",
            "Stop Guessing Your Planer Setup.",
        ],
        "items": [
            {"left": "Missing hardware", "right": "Every piece included"},
            {"left": "Wrong bridle size", "right": "Matched to your planer"},
            {"left": "Incomplete kits", "right": "Ready to run, day one"},
        ],
        "cta": "SHOP PLANER KITS",
    },
    {
        "id": "dredges",
        "headlines": [
            "A Dead Spread Won't Pull Fish Up.",
            "Your Dredge Should Look Alive, Not Like A Mop.",
            "No Teasers? No Tournament Fish.",
        ],
        "items": [
            {"left": "Lifeless squid imitations", "right": "UV-reactive realistic squid"},
            {"left": "Tangled rigging", "right": "Pre-rigged, ready to deploy"},
            {"left": "Too heavy for center consoles", "right": "Compact enough for any boat"},
        ],
        "cta": "SHOP DREDGES",
    },
    {
        "id": "line-leader",
        "headlines": [
            "Bad Leader Material Costs More Than Fish.",
            "If Your Wind-On Fails, Everything Behind It Is Gone.",
            "That 80lb Leader Won't Hold A Serious Fish.",
        ],
        "items": [
            {"left": "Weak crimps", "right": "500lb rated hardware"},
            {"left": "Memory-heavy mono", "right": "Low-memory fluorocarbon"},
            {"left": "Guessing what works", "right": "Captain-tested specs"},
        ],
        "cta": "SHOP LINE & LEADER",
    },
    {
        "id": "lures",
        "headlines": [
            "90% Of Tackle Shop Lures Won't Catch Tournament Fish.",
            "Your Spread Looks Nothing Like Bait.",
            "Random Lures Don't Build Confidence.",
        ],
        "items": [
            {"left": "Generic lure sets", "right": "Species-matched spreads"},
            {"left": "No pattern logic", "right": "Tested color combinations"},
            {"left": "One-size-fits-all", "right": "Sized by target species"},
        ],
        "cta": "SHOP LURES",
    },
    {
        "id": "kits",
        "headlines": [
            "Ordering Parts One At A Time Is A Trap.",
            "You Shouldn't Need 6 Orders To Build One Rig.",
            "Incomplete Gear Orders Waste Time And Money.",
        ],
        "items": [
            {"left": "Multiple vendors", "right": "Everything in one order"},
            {"left": "Compatibility questions", "right": "Pre-matched components"},
            {"left": "Missing one piece", "right": "Complete system, nothing extra"},
        ],
        "cta": "SHOP COMPLETE KITS",
    },
    {
        "id": "belts",
        "headlines": [
            "A 40-Minute Tuna Fight Will Bruise Your Hips.",
            "Cheap Belts Break Anglers Before Fish.",
            "Your Back Shouldn't Hurt More Than The Fish.",
        ],
        "items": [
            {"left": "Thin padding", "right": "Tournament-grade cushion"},
            {"left": "Belt slips under load", "right": "Locked harness system"},
            {"left": "One-size discomfort", "right": "Adjustable fit for hours"},
        ],
        "cta": "SHOP FIGHTING BELTS",
    },
]


def build_render(thesis, headline_idx, bg_index):
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]
    headline = thesis["headlines"][headline_idx]
    slug = f"{thesis['id']}-v{headline_idx + 1}"

    return {
        "_comment": f"=== Problem-Solution: {thesis['id']} | v{headline_idx + 1} ===",
        "output": f"{OUT}/{slug}.jpg",
        "backgroundPath": bg,
        "text": {
            "headline": headline,
            "subhead": "",
            "cta": thesis["cta"],
            "footer": BRAND["name"],
        },
        "overlay": OVERLAY_DARK,
        "typography": {
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 48,
            "subheadSize": 1,
            "headlineWeight": 800,
            "ctaSize": 22,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "centered-hero",
            "align": "center",
            "leftX": 540,
            "headlineY": 180,
            "subheadY": 200,
            "maxHeadlineChars": 24,
            "maxSubheadChars": 1,
            "ctaWidth": 320,
            "ctaHeight": 58,
            "ctaRectX": 380,
            "ctaRectY": 920,
            "ctaX": 540,
            "ctaY": 949,
            "footerY": 1050,
        },
        "splitReveal": {
            "dividerX": 540,
            "startY": 420,
            "rowHeight": 70,
            "textSize": 22,
            "labelSize": 14,
            "problemLabel": "THE PROBLEM",
            "solutionLabel": "THE FIX",
            "leftColor": "rgba(255,255,255,0.45)",
            "rightColor": "#ffffff",
            "accentColor": "rgba(232,93,58,0.9)",
            "items": thesis["items"],
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

    for i, thesis in enumerate(THESES):
        for v in range(3):
            config["renders"].append(build_render(thesis, v, i * 3 + v))

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-problem-solution.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Theses: {len(THESES)}")
    print(f"Renders generated: {len(config['renders'])} ({len(THESES)} theses x 3 variants)")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
