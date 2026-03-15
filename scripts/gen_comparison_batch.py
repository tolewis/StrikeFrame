#!/usr/bin/env python3
"""Generate comparison table ad batch — 2-column TackleRoom vs status quo.
High conversion potential (LMNT, HexClad model).
1 variant per comparison (manual data)."""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_DARK, OCEAN_BACKGROUNDS,
)

OUT = "/mnt/raid/Data/tmp/ads/comparison"

# Manual comparison data — these require domain knowledge to be accurate.
COMPARISONS = [
    {
        "id": "planer-kits",
        "headline": "Stop Piecing It Together.",
        "subhead": "Complete planer kit vs buying parts separately.",
        "leftHeader": "PARTS SHOPPING",
        "rightHeader": "TACKLEROOM KIT",
        "rows": [
            {"left": "3-5 separate orders", "right": "Everything in one box"},
            {"left": "Hope parts are compatible", "right": "Pre-matched components"},
            {"left": "Missing hardware", "right": "All clips and swivels included"},
            {"left": "$120+ across vendors", "right": "One kit, one price"},
        ],
        "cta": "SHOP PLANER KITS",
    },
    {
        "id": "dredge-quality",
        "headline": "Not All Dredges Are Equal.",
        "subhead": "Tournament-grade vs discount dredges.",
        "leftHeader": "CHEAP DREDGE",
        "rightHeader": "TACKLEROOM",
        "rows": [
            {"left": "Fades after 3 trips", "right": "UV-reactive squid, season-rated"},
            {"left": "Tangles constantly", "right": "Pre-rigged, tangle-free"},
            {"left": "Looks dead in water", "right": "Realistic swimming action"},
            {"left": "No captain endorsement", "right": "Tournament-proven results"},
        ],
        "cta": "SHOP DREDGES",
    },
    {
        "id": "leader-material",
        "headline": "Your Leader Is The Weakest Link.",
        "subhead": "Tackle shop leader vs offshore-rated leader.",
        "leftHeader": "GENERIC LEADER",
        "rightHeader": "TACKLEROOM",
        "rows": [
            {"left": "Unknown abrasion rating", "right": "Tested to 500lb+"},
            {"left": "High memory, coils up", "right": "Low-memory fluorocarbon"},
            {"left": "Inconsistent diameter", "right": "Precision-spec'd per spool"},
            {"left": "No rigging guidance", "right": "Captain-tested recommendations"},
        ],
        "cta": "SHOP LINE & LEADER",
    },
    {
        "id": "daisy-chains",
        "headline": "Teasers That Actually Work.",
        "subhead": "Generic teasers vs TackleRoom daisy chains.",
        "leftHeader": "GENERIC TEASER",
        "rightHeader": "TACKLEROOM",
        "rows": [
            {"left": "Static, no action", "right": "Swimming action at speed"},
            {"left": "Wrong color patterns", "right": "Species-matched colors"},
            {"left": "Falls apart in current", "right": "400lb mono backbone"},
            {"left": "Cheap materials", "right": "Tournament-grade build"},
        ],
        "cta": "SHOP DAISY CHAINS",
    },
    {
        "id": "buying-experience",
        "headline": "Where You Buy Matters.",
        "subhead": "Big box retail vs specialist offshore tackle.",
        "leftHeader": "BIG BOX STORE",
        "rightHeader": "TACKLEROOM",
        "rows": [
            {"left": "Staff doesn't fish offshore", "right": "Built by offshore anglers"},
            {"left": "Generic product mix", "right": "Curated for saltwater"},
            {"left": "No rigging support", "right": "Captain-backed recommendations"},
            {"left": "Returns nightmare", "right": "Direct support, fast resolution"},
        ],
        "cta": "SHOP TACKLEROOM",
    },
    {
        "id": "fighting-belts",
        "headline": "Comfort Decides The Fight.",
        "subhead": "Standard belt vs tournament fighting belt.",
        "leftHeader": "STANDARD BELT",
        "rightHeader": "TACKLEROOM",
        "rows": [
            {"left": "Thin padding, bruised hips", "right": "Tournament-grade cushion"},
            {"left": "Slips under heavy load", "right": "Locked harness system"},
            {"left": "One size, poor fit", "right": "Fully adjustable"},
            {"left": "Breaks after one season", "right": "Built for years of use"},
        ],
        "cta": "SHOP FIGHTING BELTS",
    },
]


def build_render(comparison, bg_index):
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]

    return {
        "_comment": f"=== Comparison: {comparison['id']} ===",
        "output": f"{OUT}/{comparison['id']}.jpg",
        "backgroundPath": bg,
        "text": {
            "headline": comparison["headline"],
            "subhead": comparison.get("subhead", ""),
            "cta": comparison["cta"],
            "footer": BRAND["name"],
        },
        "overlay": OVERLAY_DARK,
        "typography": {
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 46,
            "subheadSize": 22,
            "headlineWeight": 800,
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
            "headlineY": 160,
            "subheadY": 280,
            "maxHeadlineChars": 24,
            "maxSubheadChars": 40,
            "ctaWidth": 320,
            "ctaHeight": 58,
            "ctaRectX": 380,
            "ctaRectY": 920,
            "ctaX": 540,
            "ctaY": 949,
            "footerY": 1050,
        },
        "comparisonTable": {
            "startX": 60,
            "startY": 350,
            "rowHeight": 65,
            "headerSize": 18,
            "bodySize": 20,
            "leftHeader": comparison["leftHeader"],
            "rightHeader": comparison["rightHeader"],
            "highlightCol": "right",
            "rows": comparison["rows"],
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

    for i, comp in enumerate(COMPARISONS):
        config["renders"].append(build_render(comp, i))

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-comparison.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Comparisons: {len(COMPARISONS)}")
    print(f"Renders generated: {len(config['renders'])}")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
