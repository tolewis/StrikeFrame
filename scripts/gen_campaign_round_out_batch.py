#!/usr/bin/env python3
"""
Campaign Roundout Batch Generator — 24 high-quality ads across 5 categories + retarget.

Uses all 8 new StrikeFrame template types to diversify creative formats beyond
the existing lifestyle hero and explainer card inventory.

Content sourced from:
- Thesis bank (06_tackleroom_ad_thesis_bank.md)
- Hook matrix (07_category_hook_matrix.md)
- Saltwater-kb facts
- Batch 3 testimonial data
"""

import json
import os
import sys
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, BADGES, OVERLAY_OCEAN, OVERLAY_DARK,
    OVERLAY_EDITORIAL, STOCK_DIR, OCEAN_BACKGROUNDS,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = "/mnt/raid/Data/tmp/ads/campaign-roundout"

# Extended background pool — 24 unique images, no repeats
ALL_BACKGROUNDS = sorted([
    str(p) for p in Path(STOCK_DIR).glob("*.jpeg")
])

# Hand-picked backgrounds by mood for each ad
# Fight/action shots, ocean scenes, boat scenes, underwater, etc.
BG = {
    # Belts
    "belts_benefit":    f"{STOCK_DIR}/AdobeStock_331722964.jpeg",
    "belts_testimonial": f"{STOCK_DIR}/AdobeStock_284446852.jpeg",
    "belts_contrarian": f"{STOCK_DIR}/AdobeStock_229283027.jpeg",
    "belts_comparison": None,  # gradient, no photo
    # Lead
    "lead_benefit":     f"{STOCK_DIR}/AdobeStock_175678582.jpeg",
    "lead_listicle":    f"{STOCK_DIR}/AdobeStock_219637627.jpeg",
    "lead_offer":       f"{STOCK_DIR}/AdobeStock_337378282.jpeg",
    "lead_authority":   f"{STOCK_DIR}/AdobeStock_345435684.jpeg",
    # Dredges
    "dredge_testimonial": f"{STOCK_DIR}/AdobeStock_133588506.jpeg",
    "dredge_comparison": None,  # gradient
    "dredge_benefit":   f"{STOCK_DIR}/AdobeStock_372953083.jpeg",
    "dredge_problem":   f"{STOCK_DIR}/AdobeStock_991789270.jpeg",
    "dredge_offer":     f"{STOCK_DIR}/AdobeStock_175678638.jpeg",
    # Planers
    "planer_problem":   None,  # gradient
    "planer_benefit":   f"{STOCK_DIR}/AdobeStock_194759350.jpeg",
    "planer_comparison": None,  # gradient
    "planer_contrarian": f"{STOCK_DIR}/AdobeStock_167858576.jpeg",
    # Lures
    "lure_benefit":     f"{STOCK_DIR}/AdobeStock_180645942.jpeg",
    "lure_testimonial": f"{STOCK_DIR}/AdobeStock_195400385.jpeg",
    "lure_listicle":    f"{STOCK_DIR}/AdobeStock_186432960.jpeg",
    "lure_authority":   f"{STOCK_DIR}/AdobeStock_183199836.jpeg",
    # Retarget
    "retarget_offer":   f"{STOCK_DIR}/AdobeStock_134773205.jpeg",
    "retarget_testimonial": f"{STOCK_DIR}/AdobeStock_139875840.jpeg",
    "retarget_benefit": f"{STOCK_DIR}/AdobeStock_144669694.jpeg",
}

# ── Shared defaults ──────────────────────────────────────────────────────────

DEFAULTS = {
    "preset": "social-square",
    "template": "banner",
    "theme": THEME_DEFAULT,
    "typography": {
        "headlineFontFamily": BRAND["headline_font"],
        "bodyFontFamily": BRAND["body_font"],
        "headlineWeight": 800,
        "subheadWeight": 400,
        "ctaWeight": 700,
        "footerSize": 14,
        "footerTracking": 4,
    },
}


def out(category, name):
    return f"{OUTPUT_DIR}/{category}/{name}.jpg"


def base_layout(personality="centered-hero", max_hl_chars=20, max_sh_chars=34, cta_y=920):
    """Build common layout dict."""
    is_centered = personality == "centered-hero"
    cta_w = 560 if is_centered else 360
    return {
        "personality": personality,
        "align": "center" if is_centered else "left",
        "leftX": 540 if is_centered else 80,
        "headlineY": 140,
        "subheadY": 380,
        "maxHeadlineChars": max_hl_chars,
        "maxSubheadChars": max_sh_chars,
        "ctaWidth": cta_w,
        "ctaHeight": 62,
        "ctaRectX": (1080 - cta_w) // 2 if is_centered else 80,
        "ctaRectY": cta_y,
        "ctaRadius": 20,
        "footerY": 1040,
    }


# ── Ad definitions ───────────────────────────────────────────────────────────

def build_renders():
    renders = []

    # ═══════════════════════════════════════════════════════════════════════
    # 1. FIGHTING BELTS (4 ads)
    # ═══════════════════════════════════════════════════════════════════════

    # Belt 1: Benefit Stack — comfort/endurance features
    renders.append({
        "_comment": "BELTS | benefit-stack | Built For The Fight",
        "_category": "belts", "_template": "benefit-stack", "_thesis": "new",
        "output": out("belts", "belts-benefit-stack-fight"),
        "backgroundPath": BG["belts_benefit"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "Built For The Fight, Not The Photo",
            "subhead": "Comfort that lasts longer than the fish.",
            "cta": "SHOP FIGHTING BELTS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 58, "subheadSize": 24},
        "layout": base_layout("editorial-left", cta_y=900),
        "benefitStack": {
            "startX": 80, "startY": 500, "spacing": 110,
            "iconSize": 36, "iconColor": "#63b3ed",
            "textSize": 28, "textColor": "#ffffff", "textMaxChars": 32,
            "items": [
                {"icon": "shield", "label": "Wide padded lumbar support"},
                {"icon": "gear", "label": "Gimbal pin locks rod in position"},
                {"icon": "check", "label": "Adjustable harness attachment points"},
                {"icon": "anchor", "label": "Rated for 40+ minute fights"},
            ],
        },
    })

    # Belt 2: Testimonial — captain proof on marlin fight
    renders.append({
        "_comment": "BELTS | testimonial | Captain Marlin Quote",
        "_category": "belts", "_template": "testimonial", "_thesis": "T11",
        "output": out("belts", "belts-testimonial-captain"),
        "backgroundPath": BG["belts_testimonial"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "What Captains Trust",
            "subhead": "",
            "cta": "SHOP FIGHTING BELTS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 44, "subheadSize": 22},
        "layout": {**base_layout("centered-hero", cta_y=900), "headlineY": 200},
        "testimonial": {
            "quote": "Forty minutes on a blue marlin and the belt was the only thing that wasn't sore the next day.",
            "stars": 5, "starSize": 32,
            "name": "Capt. Rick Stanczyk",
            "role": "Bud N' Mary's Marina, Islamorada",
            "quoteSize": 32, "quoteMaxChars": 26,
            "nameSize": 22, "startY": 330,
        },
    })

    # Belt 3: Contrarian — cheap belt costs fish
    renders.append({
        "_comment": "BELTS | contrarian | $30 Belt Costs $200 Fish",
        "_category": "belts", "_template": "contrarian", "_thesis": "T22",
        "output": out("belts", "belts-contrarian-cheap"),
        "backgroundPath": BG["belts_contrarian"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "A $30 Belt Costs You A $200 Fish.",
            "subhead": "Lose your footing once and the yellowfin wins. The belt is where you don't cut corners.",
            "cta": "SHOP QUALITY BELTS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 62, "subheadSize": 24},
        "layout": base_layout("centered-hero", max_hl_chars=18, max_sh_chars=32, cta_y=800),
    })

    # Belt 4: Comparison — cheap vs quality belt
    renders.append({
        "_comment": "BELTS | comparison | Cheap vs Quality Belt",
        "_category": "belts", "_template": "comparison", "_thesis": "T20",
        "output": out("belts", "belts-comparison-quality"),
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "Why Your Belt Matters",
            "subhead": "The difference shows at minute 20.",
            "cta": "SHOP FIGHTING BELTS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 56, "subheadSize": 22},
        "layout": base_layout("centered-hero", cta_y=900),
        "comparisonTable": {
            "startX": 80, "startY": 460, "colWidth": 440, "rowHeight": 60,
            "headerSize": 22, "bodySize": 20,
            "highlightCol": "right",
            "leftHeader": "Generic Belt",
            "rightHeader": "TackleRoom",
            "rows": [
                {"left": "Thin foam padding", "right": "Wide lumbar support"},
                {"left": "Plastic gimbal", "right": "Stainless gimbal pin"},
                {"left": "Fixed size", "right": "Adjustable harness points"},
                {"left": "20-minute comfort", "right": "Built for the full fight"},
                {"left": "Replace every season", "right": "Buy once, fish forever"},
            ],
        },
    })

    # ═══════════════════════════════════════════════════════════════════════
    # 2. LEAD / TROLLING WEIGHTS (4 ads)
    # ═══════════════════════════════════════════════════════════════════════

    # Lead 1: Benefit Stack — weight kit coverage
    renders.append({
        "_comment": "LEAD | benefit-stack | Three Sizes Cover 90%",
        "_category": "lead", "_template": "benefit-stack", "_thesis": "T9",
        "output": out("lead", "lead-benefit-stack-kit"),
        "backgroundPath": BG["lead_benefit"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "Three Sizes Cover 90% Of Trips",
            "subhead": "Stop guessing which weight to pack.",
            "cta": "SHOP WEIGHT KITS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 56, "subheadSize": 24},
        "layout": base_layout("editorial-left", cta_y=900),
        "benefitStack": {
            "startX": 80, "startY": 500, "spacing": 110,
            "iconSize": 36, "iconColor": "#63b3ed",
            "textSize": 28, "textColor": "#ffffff", "textMaxChars": 34,
            "items": [
                {"icon": "anchor", "label": "8oz for shallow trolling under 4kts"},
                {"icon": "wave", "label": "16oz for standard offshore depth"},
                {"icon": "target", "label": "24oz for deep drops and current"},
                {"icon": "check", "label": "Hand-poured, flash-free finish"},
            ],
        },
    })

    # Lead 2: Listicle — rigging mistakes
    renders.append({
        "_comment": "LEAD | listicle | 5 Rigging Mistakes",
        "_category": "lead", "_template": "listicle", "_thesis": "new",
        "output": out("lead", "lead-listicle-mistakes"),
        "backgroundPath": BG["lead_listicle"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "5 Rigging Mistakes That Cost You Fish",
            "subhead": "Most happen before you leave the dock.",
            "cta": "SHOP TROLLING WEIGHTS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 54, "subheadSize": 22},
        "layout": base_layout("editorial-left", max_hl_chars=22, cta_y=920),
        "textLayers": [
            {"content": "1. Wrong weight for your trolling speed", "x": 80, "y": 480, "fontSize": 28, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
            {"content": "2. Flash lines that spook gamefish", "x": 80, "y": 556, "fontSize": 28, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
            {"content": "3. Machine-poured seams that catch weed", "x": 80, "y": 632, "fontSize": 28, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
            {"content": "4. Only carrying one size on the boat", "x": 80, "y": 708, "fontSize": 28, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
            {"content": "5. Running out of weights mid-season", "x": 80, "y": 784, "fontSize": 28, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
        ],
    })

    # Lead 3: Offer — deep drop weight kit pricing
    renders.append({
        "_comment": "LEAD | offer | Weight Kit Pricing",
        "_category": "lead", "_template": "offer", "_thesis": "T9",
        "output": out("lead", "lead-offer-kit"),
        "backgroundPath": BG["lead_offer"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "Deep Drop Weights",
            "subhead": "Hand-poured. Flash-free. Tournament-legal.",
            "cta": "SHOP WEIGHTS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 58, "subheadSize": 24},
        "layout": {**base_layout("centered-hero", cta_y=880), "headlineY": 240},
        "offerFrame": {
            "originalPrice": "$18.99",
            "salePrice": "$12.99",
            "savings": "BEST SELLER",
            "offerText": "FREE SHIPPING OVER $69",
            "salePriceSize": 72, "originalPriceSize": 28,
            "priceY": 580,
        },
        "badges": [{
            "text": "HAND POURED",
            "x": 430, "y": 120,
            "fill": BRAND["accent"], "textColor": "#ffffff", "fontSize": 16,
        }],
    })

    # Lead 4: Authority — hand-poured specs
    renders.append({
        "_comment": "LEAD | authority | Hand-Poured Tournament-Legal",
        "_category": "lead", "_template": "authority", "_thesis": "T8",
        "output": out("lead", "lead-authority-handpoured"),
        "backgroundPath": BG["lead_authority"],
        "overlay": {**OVERLAY_EDITORIAL, "leftOpacity": 0.6, "midOpacity": 0.4},
        "text": {
            "headline": "Hand-Poured. Flash-Free. Tournament-Legal.",
            "subhead": "Every weight inspected by hand. No flash lines, no seams, no weed catchers.",
            "cta": "SHOP TROLLING WEIGHTS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {
            **DEFAULTS["typography"],
            "headlineFontFamily": BRAND["serif_font"],
            "headlineSize": 58, "subheadSize": 22,
            "headlineWeight": 700,
        },
        "layout": {
            **base_layout("centered-hero", max_hl_chars=20, max_sh_chars=34, cta_y=880),
            "headlineY": 160,
            "subheadY": 420,
        },
        "authorityBar": {
            "barY": 700, "barHeight": 40, "textSize": 13,
            "textColor": "rgba(255,255,255,0.5)",
            "barFill": "rgba(255,255,255,0.06)",
            "publications": ["HAND INSPECTED", "FLASH-FREE", "TOURNAMENT LEGAL", "MADE IN USA"],
        },
    })

    # ═══════════════════════════════════════════════════════════════════════
    # 3. DREDGES (5 ads)
    # ═══════════════════════════════════════════════════════════════════════

    # Dredge 1: Testimonial — captain on raising fish
    renders.append({
        "_comment": "DREDGES | testimonial | Captain Raising Fish",
        "_category": "dredges", "_template": "testimonial", "_thesis": "T5",
        "output": out("dredges", "dredge-testimonial-captain"),
        "backgroundPath": BG["dredge_testimonial"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "Ask Any Captain",
            "subhead": "",
            "cta": "SHOP DREDGE SYSTEMS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 44, "subheadSize": 22},
        "layout": {**base_layout("centered-hero", cta_y=900), "headlineY": 200},
        "testimonial": {
            "quote": "If you aren't pulling dredges you aren't competing. They raise fish better than anything else in the spread.",
            "stars": 5, "starSize": 32,
            "name": "Capt. Wheeler",
            "role": "Tournament Circuit, South Florida",
            "quoteSize": 32, "quoteMaxChars": 26,
            "nameSize": 22, "startY": 330,
        },
    })

    # Dredge 2: Comparison — with vs without dredge
    renders.append({
        "_comment": "DREDGES | comparison | With vs Without Dredge",
        "_category": "dredges", "_template": "comparison", "_thesis": "T4",
        "output": out("dredges", "dredge-comparison-spread"),
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "The Spread Matters",
            "subhead": "Dredges raise fish. Empty water doesn't.",
            "cta": "UPGRADE YOUR SPREAD",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 56, "subheadSize": 22},
        "layout": {**base_layout("centered-hero", cta_y=900), "headlineY": 240},
        "comparisonTable": {
            "startX": 80, "startY": 460, "colWidth": 440, "rowHeight": 60,
            "headerSize": 22, "bodySize": 20,
            "highlightCol": "right",
            "leftHeader": "Without Dredge",
            "rightHeader": "With Dredge",
            "rows": [
                {"left": "Flat spread, no depth", "right": "3D bait school at depth"},
                {"left": "Fish ignore surface lures", "right": "Fish rise into strike zone"},
                {"left": "Random hookup pattern", "right": "90% hookup rate on teasers"},
                {"left": "Hope for the best", "right": "Tournament-proven results"},
            ],
        },
    })

    # Dredge 3: Benefit Stack — system specs
    renders.append({
        "_comment": "DREDGES | benefit-stack | Heavy Bar UV Squid",
        "_category": "dredges", "_template": "benefit-stack", "_thesis": "T6",
        "output": out("dredges", "dredge-benefit-stack-specs"),
        "backgroundPath": BG["dredge_benefit"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "Heavy Bar. UV Squid. 400lb Mono.",
            "subhead": "Built for current, not calm water.",
            "cta": "SEE THE FULL BUILD",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 54, "subheadSize": 24},
        "layout": base_layout("editorial-left", max_hl_chars=22, cta_y=900),
        "benefitStack": {
            "startX": 80, "startY": 500, "spacing": 110,
            "iconSize": 36, "iconColor": "#63b3ed",
            "textSize": 28, "textColor": "#ffffff", "textMaxChars": 34,
            "items": [
                {"icon": "anchor", "label": "38\" heavy bar handles Gulf Stream"},
                {"icon": "wave", "label": "UV-enhanced squid visible at depth"},
                {"icon": "shield", "label": "400lb mono won't fail on billfish"},
                {"icon": "check", "label": "Mesh bag included, ready to fish"},
            ],
        },
    })

    # Dredge 4: Problem-Solution — spread missing key element
    renders.append({
        "_comment": "DREDGES | problem-solution | Spread Missing Key Element",
        "_category": "dredges", "_template": "problem-solution", "_thesis": "T4",
        "output": out("dredges", "dredge-problem-solution-spread"),
        "backgroundPath": BG["dredge_problem"],
        "overlay": {**OVERLAY_DARK, "leftOpacity": 0.8, "midOpacity": 0.8, "rightOpacity": 0.8},
        "text": {
            "headline": "Your Spread Is Missing One Thing",
            "subhead": "Fish don't eat what they can't see.",
            "cta": "ADD A DREDGE",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 54, "subheadSize": 24},
        "layout": base_layout("centered-hero", max_hl_chars=22, cta_y=880),
        "splitReveal": {
            "dividerX": 540, "startY": 500, "rowHeight": 70, "textSize": 22,
            "problemLabel": "WITHOUT DREDGE",
            "solutionLabel": "WITH DREDGE",
            "items": [
                {"left": "Surface-only spread", "right": "Bait school at depth"},
                {"left": "Fish stay down", "right": "Fish rise to strike zone"},
                {"left": "Random hookups", "right": "Consistent teaser bites"},
                {"left": "Dead-looking water", "right": "Life behind the boat"},
            ],
        },
    })

    # Dredge 5: Offer — complete dredge system
    renders.append({
        "_comment": "DREDGES | offer | Complete System Pricing",
        "_category": "dredges", "_template": "offer", "_thesis": "T16",
        "output": out("dredges", "dredge-offer-system"),
        "backgroundPath": BG["dredge_offer"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "Complete Dredge System",
            "subhead": "Bar, squid, mono, bag. Nothing else to buy.",
            "cta": "SHOP DREDGE KITS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 58, "subheadSize": 22},
        "layout": base_layout("centered-hero", cta_y=880),
        "offerFrame": {
            "originalPrice": "$529.99",
            "salePrice": "$429.99",
            "savings": "SAVE $100",
            "offerText": "FREE SHIPPING",
            "salePriceSize": 72, "originalPriceSize": 28,
            "priceY": 580,
        },
        "badges": [{
            "text": "TOURNAMENT GRADE",
            "x": 80, "y": 50,
            "fill": BRAND["accent"], "textColor": "#ffffff", "fontSize": 16,
        }],
    })

    # ═══════════════════════════════════════════════════════════════════════
    # 4. PLANERS (4 ads)
    # ═══════════════════════════════════════════════════════════════════════

    # Planer 1: Problem-Solution — missing parts
    renders.append({
        "_comment": "PLANERS | problem-solution | Stop Guessing Setup",
        "_category": "planers", "_template": "problem-solution", "_thesis": "T1",
        "output": out("planers", "planer-problem-solution-setup"),
        "overlay": {**OVERLAY_DARK, "leftOpacity": 0.8, "midOpacity": 0.8, "rightOpacity": 0.8},
        "text": {
            "headline": "Stop Guessing Your Planer Setup",
            "subhead": "One kit. Zero missing parts.",
            "cta": "SHOP COMPLETE KITS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 54, "subheadSize": 24},
        "layout": base_layout("centered-hero", max_hl_chars=22, cta_y=880),
        "splitReveal": {
            "dividerX": 540, "startY": 500, "rowHeight": 70, "textSize": 22,
            "problemLabel": "THE PROBLEM",
            "solutionLabel": "THE FIX",
            "items": [
                {"left": "Incomplete kits online", "right": "Every piece included"},
                {"left": "Wrong bridle for your planer", "right": "Matched to your model"},
                {"left": "Hardware fails at speed", "right": "500lb rated clips & snaps"},
                {"left": "3 orders to rig 1 planer", "right": "One order. Done."},
            ],
        },
    })

    # Planer 2: Benefit Stack — complete kit contents
    renders.append({
        "_comment": "PLANERS | benefit-stack | One Kit Zero Missing Parts",
        "_category": "planers", "_template": "benefit-stack", "_thesis": "T3",
        "output": out("planers", "planer-benefit-stack-kit"),
        "backgroundPath": BG["planer_benefit"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "One Kit. Zero Missing Parts.",
            "subhead": "Fish today, not next week.",
            "cta": "SHOP PLANER KITS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 58, "subheadSize": 24},
        "layout": base_layout("editorial-left", cta_y=900),
        "benefitStack": {
            "startX": 80, "startY": 500, "spacing": 110,
            "iconSize": 36, "iconColor": "#63b3ed",
            "textSize": 28, "textColor": "#ffffff", "textMaxChars": 34,
            "items": [
                {"icon": "check", "label": "Planer, bridle, and hardware matched"},
                {"icon": "shield", "label": "500lb rated clips and snaps"},
                {"icon": "gear", "label": "Runs clean at trolling speed"},
                {"icon": "wave", "label": "Dives 20-30ft then releases on strike"},
            ],
        },
    })

    # Planer 3: Comparison — planer vs downrigger
    renders.append({
        "_comment": "PLANERS | comparison | Planer vs Downrigger",
        "_category": "planers", "_template": "comparison", "_thesis": "T19",
        "output": out("planers", "planer-comparison-downrigger"),
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "Planer vs Downrigger",
            "subhead": "Same depth. Very different price.",
            "cta": "SHOP PLANERS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 56, "subheadSize": 22},
        "layout": {**base_layout("centered-hero", cta_y=900), "headlineY": 240},
        "comparisonTable": {
            "startX": 80, "startY": 460, "colWidth": 440, "rowHeight": 60,
            "headerSize": 22, "bodySize": 20,
            "highlightCol": "right",
            "leftHeader": "Downrigger",
            "rightHeader": "Planer Kit",
            "rows": [
                {"left": "$800+ installed", "right": "Under $40 complete"},
                {"left": "Permanent mount needed", "right": "Clips to any line"},
                {"left": "Mechanical maintenance", "right": "Zero maintenance"},
                {"left": "One depth at a time", "right": "Run multiple depths"},
                {"left": "Releases on strike", "right": "Releases on strike"},
            ],
        },
    })

    # Planer 4: Contrarian — your setup is probably wrong
    renders.append({
        "_comment": "PLANERS | contrarian | Setup Is Probably Wrong",
        "_category": "planers", "_template": "contrarian", "_thesis": "T1",
        "output": out("planers", "planer-contrarian-wrong"),
        "backgroundPath": BG["planer_contrarian"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "Your Planer Setup Is Probably Wrong.",
            "subhead": "Wrong bridle size means wrong depth, wrong action, wrong results.",
            "cta": "FIX YOUR SETUP",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 62, "subheadSize": 24},
        "layout": base_layout("centered-hero", max_hl_chars=18, max_sh_chars=30, cta_y=800),
    })

    # ═══════════════════════════════════════════════════════════════════════
    # 5. LURES / SPREAD COMPONENTS (4 ads)
    # ═══════════════════════════════════════════════════════════════════════

    # Lure 1: Benefit Stack — cleaner spread
    renders.append({
        "_comment": "LURES | benefit-stack | Build A Cleaner Spread",
        "_category": "lures", "_template": "benefit-stack", "_thesis": "T12",
        "output": out("lures", "lure-benefit-stack-spread"),
        "backgroundPath": BG["lure_benefit"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "Build A Cleaner Spread In Half The Time",
            "subhead": "Matched lures that work together.",
            "cta": "BUILD YOUR SPREAD",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 54, "subheadSize": 24},
        "layout": base_layout("editorial-left", max_hl_chars=22, cta_y=900),
        "benefitStack": {
            "startX": 80, "startY": 500, "spacing": 110,
            "iconSize": 36, "iconColor": "#63b3ed",
            "textSize": 28, "textColor": "#ffffff", "textMaxChars": 34,
            "items": [
                {"icon": "fish", "label": "Lures matched by spread position"},
                {"icon": "target", "label": "Species-specific color patterns"},
                {"icon": "gear", "label": "Pre-rigged, ready to deploy"},
                {"icon": "check", "label": "Reordered by charter crews"},
            ],
        },
    })

    # Lure 2: Testimonial — crew reorder proof
    renders.append({
        "_comment": "LURES | testimonial | Crew Reorder Proof",
        "_category": "lures", "_template": "testimonial", "_thesis": "T11",
        "output": out("lures", "lure-testimonial-reorder"),
        "backgroundPath": BG["lure_testimonial"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "What Crews Keep Rigged",
            "subhead": "",
            "cta": "SHOP CONFIDENCE LURES",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 44, "subheadSize": 22},
        "layout": base_layout("centered-hero", cta_y=900),
        "testimonial": {
            "quote": "We keep three of these rigged and ready. When something works you don't mess with it.",
            "stars": 5, "starSize": 32,
            "name": "Tournament Mate",
            "role": "South Florida Circuit",
            "quoteSize": 32, "quoteMaxChars": 26,
            "nameSize": 22, "startY": 260,
        },
    })

    # Lure 3: Listicle — signs spread is wrong
    renders.append({
        "_comment": "LURES | listicle | 4 Signs Your Spread Is Wrong",
        "_category": "lures", "_template": "listicle", "_thesis": "T10",
        "output": out("lures", "lure-listicle-spread-signs"),
        "backgroundPath": BG["lure_listicle"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "4 Signs Your Spread Is Working Against You",
            "subhead": "Fix these before your next trip.",
            "cta": "SHOP TESTED LURE SETUPS",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 52, "subheadSize": 22},
        "layout": base_layout("editorial-left", max_hl_chars=22, cta_y=900),
        "textLayers": [
            {"content": "1. Same color in every position — fish see one meal, not a school", "x": 80, "y": 500, "fontSize": 26, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
            {"content": "2. Lures tangle at speed — bad combo, not bad luck", "x": 80, "y": 610, "fontSize": 26, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
            {"content": "3. No teaser in front — fish need a reason to look", "x": 80, "y": 720, "fontSize": 26, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
            {"content": "4. Rigging every trip — buy pre-rigged, fish more", "x": 80, "y": 830, "fontSize": 26, "fontWeight": 600, "color": "#ffffff", "maxChars": 36},
        ],
    })

    # Lure 4: Authority — captains choice
    renders.append({
        "_comment": "LURES | authority | Rigged By Captains",
        "_category": "lures", "_template": "authority", "_thesis": "T11",
        "output": out("lures", "lure-authority-captains"),
        "backgroundPath": BG["lure_authority"],
        "overlay": {**OVERLAY_EDITORIAL, "leftOpacity": 0.6, "midOpacity": 0.4},
        "text": {
            "headline": "Rigged By Captains. Reordered By Crews.",
            "subhead": "The lures serious offshore teams keep buying. Not because of marketing. Because they work.",
            "cta": "SHOP PROVEN LURES",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {
            **DEFAULTS["typography"],
            "headlineFontFamily": BRAND["serif_font"],
            "headlineSize": 58, "subheadSize": 22,
            "headlineWeight": 700,
        },
        "layout": {
            **base_layout("centered-hero", max_hl_chars=20, max_sh_chars=34, cta_y=880),
            "headlineY": 220,
            "subheadY": 460,
        },
        "authorityBar": {
            "barY": 700, "barHeight": 40, "textSize": 13,
            "textColor": "rgba(255,255,255,0.5)",
            "barFill": "rgba(255,255,255,0.06)",
            "publications": ["CHARTER TESTED", "TOURNAMENT PROVEN", "CAPTAIN SELECTED", "REORDER RATE: HIGH"],
        },
    })

    # ═══════════════════════════════════════════════════════════════════════
    # 6. RETARGET (3 ads — cross-category warm audience)
    # ═══════════════════════════════════════════════════════════════════════

    # Retarget 1: Offer — free shipping threshold
    renders.append({
        "_comment": "RETARGET | offer | Free Shipping Over $69",
        "_category": "retarget", "_template": "offer", "_thesis": "T18",
        "output": out("retarget", "retarget-offer-shipping"),
        "backgroundPath": BG["retarget_offer"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "You Were Looking At Something",
            "subhead": "Come back and we'll ship it free.",
            "cta": "FINISH YOUR ORDER",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 58, "subheadSize": 24},
        "layout": base_layout("centered-hero", cta_y=860),
        "offerFrame": {
            "salePrice": "FREE SHIPPING",
            "savings": "ORDERS OVER $69",
            "offerText": "Premium offshore tackle. No surprises at checkout.",
            "salePriceSize": 56, "originalPriceSize": 24,
            "priceY": 560,
        },
    })

    # Retarget 2: Testimonial — best customer quote
    renders.append({
        "_comment": "RETARGET | testimonial | Best Customer Quote",
        "_category": "retarget", "_template": "testimonial", "_thesis": "T11",
        "output": out("retarget", "retarget-testimonial-trust"),
        "backgroundPath": BG["retarget_testimonial"],
        "overlay": OVERLAY_DARK,
        "text": {
            "headline": "Why Anglers Come Back",
            "subhead": "",
            "cta": "SHOP THETACKLEROOM.COM",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 44, "subheadSize": 22},
        "layout": base_layout("centered-hero", cta_y=900),
        "testimonial": {
            "quote": "Best tackle shop online. Everything is what they say it is. Ships fast. Will order again.",
            "stars": 5, "starSize": 32,
            "name": "Verified Buyer",
            "role": "Repeat Customer",
            "quoteSize": 34, "quoteMaxChars": 26,
            "nameSize": 22, "startY": 260,
        },
    })

    # Retarget 3: Benefit Stack — simple & durable
    renders.append({
        "_comment": "RETARGET | benefit-stack | Simple Enough To Run",
        "_category": "retarget", "_template": "benefit-stack", "_thesis": "T21",
        "output": out("retarget", "retarget-benefit-stack-trust"),
        "backgroundPath": BG["retarget_benefit"],
        "overlay": OVERLAY_EDITORIAL,
        "text": {
            "headline": "Simple Enough To Run. Durable Enough To Trust.",
            "subhead": "Offshore tackle that works the first time.",
            "cta": "SHOP NOW",
            "footer": "THETACKLEROOM.COM",
        },
        "typography": {**DEFAULTS["typography"], "headlineSize": 52, "subheadSize": 24},
        "layout": base_layout("editorial-left", max_hl_chars=22, cta_y=900),
        "benefitStack": {
            "startX": 80, "startY": 500, "spacing": 110,
            "iconSize": 36, "iconColor": "#63b3ed",
            "textSize": 28, "textColor": "#ffffff", "textMaxChars": 34,
            "items": [
                {"icon": "shield", "label": "Tournament-grade hardware"},
                {"icon": "check", "label": "Complete kits, nothing missing"},
                {"icon": "wave", "label": "Tested offshore, not in a warehouse"},
                {"icon": "arrow", "label": "Free shipping over $69"},
            ],
        },
    })

    return renders


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for cat in ["belts", "lead", "dredges", "planers", "lures", "retarget"]:
        os.makedirs(f"{OUTPUT_DIR}/{cat}", exist_ok=True)

    renders = build_renders()
    batch = {
        "defaults": DEFAULTS,
        "renders": renders,
    }

    config_path = PROJECT_ROOT / "configs" / "campaign-roundout.json"
    with open(config_path, "w") as f:
        json.dump(batch, f, indent=2)

    print(f"Generated {len(renders)} ad configs → {config_path}")
    print(f"Output dir: {OUTPUT_DIR}")
    print("\nBreakdown:")
    from collections import Counter
    cats = Counter(r["_category"] for r in renders)
    templates = Counter(r["_template"] for r in renders)
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count} ads")
    print(f"\nTemplates used: {len(templates)}")
    for tmpl, count in sorted(templates.items()):
        print(f"  {tmpl}: {count}")


if __name__ == "__main__":
    main()
