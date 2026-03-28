#!/usr/bin/env python3
"""
gen_actionhero_multiproduct_batch.py
Generates configs/actionhero-multiproduct-batch-v1.json
25 renders across 4 categories: belts, dredges, lures, planers (6-7 each)
Uses background/lifestyle images (square or landscape), varies copy/sizing/vignette.
"""

import json
import os
import random

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
COPY_FILE    = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/category-copy-sets.json"
INVENTORY    = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/product-bg-inventory.json"
OUT_CONFIG   = os.path.join(PROJECT_ROOT, "configs", "actionhero-multiproduct-batch-v1.json")
RENDERS_DIR  = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/actionhero-multiproduct-v1"

# ── Category mapping ──────────────────────────────────────────────────────────
# Maps our 4 target categories -> copy-sets key + inventory image categories to pull from
CATEGORIES = {
    "belts":   {"copy_key": "belts",            "img_cats": ["belt"]},
    "dredges": {"copy_key": "dredges_teasers",  "img_cats": ["dredge"]},
    "lures":   {"copy_key": "lures",            "img_cats": ["lure"]},
    "planers": {"copy_key": "planers_bridles",  "img_cats": ["planer"]},
}

# Per-category badge copy pool
BADGE_COPY = {
    "belts":   ["FIGHTING BELTS", "OFFSHORE READY", "BLUE WATER GEAR", "FIGHT HARD"],
    "dredges": ["DREDGE SEASON", "TROLL SMARTER", "OFFSHORE SPREAD", "TOURNAMENT RIG"],
    "lures":   ["WAHOO SEASON", "OFFSHORE LURES", "TROLL READY", "MAHI COLORS"],
    "planers": ["PLANER KITS", "BRIDLE UP", "RIG IT RIGHT", "SPREAD WIDE"],
}

# Renders per category (total 25)
COUNTS = {"belts": 7, "dredges": 6, "lures": 6, "planers": 6}

random.seed(42)  # reproducible


def load_json(path):
    with open(path) as f:
        return json.load(f)


def filter_backgrounds(inventory_images, img_cats):
    """Return square/landscape images from specified inventory categories."""
    return [
        img for img in inventory_images
        if img["category"] in img_cats
        and img["orientation"] in ("square", "landscape")
    ]


def build_bg_rotation(images, count, max_repeats=2):
    """
    Build a list of `count` background paths, rotating through the pool.
    No single image appears more than max_repeats times.
    Falls back to unconstrained if pool is too small.
    """
    if not images:
        raise ValueError("No background images found")

    pool = list(images)
    random.shuffle(pool)
    usage = {}
    result = []

    for _ in range(count):
        # Prefer images under max_repeats limit
        candidates = [img for img in pool if usage.get(img["path"], 0) < max_repeats]
        if not candidates:
            # Reset usage and try again
            usage = {}
            candidates = pool

        chosen = random.choice(candidates)
        result.append(chosen["path"])
        usage[chosen["path"]] = usage.get(chosen["path"], 0) + 1

    return result


def main():
    copy_data = load_json(COPY_FILE)
    inv_data  = load_json(INVENTORY)
    all_images = inv_data["images"]

    renders = []

    for cat, cfg in CATEGORIES.items():
        count     = COUNTS[cat]
        copy_cat  = copy_data["categories"][cfg["copy_key"]]
        headlines = copy_cat["headlines"]
        ctas      = copy_cat["ctas"]
        badges    = BADGE_COPY[cat]

        # Pull category-specific backgrounds
        cat_images = filter_backgrounds(all_images, cfg["img_cats"])

        # Fall back to generic background/lifestyle images if category pool is small
        if len(cat_images) < 3:
            generic = filter_backgrounds(all_images, ["background", "lifestyle"])
            cat_images = cat_images + generic

        bg_paths = build_bg_rotation(cat_images, count, max_repeats=2)

        for n in range(count):
            idx   = n + 1
            hl    = headlines[n % len(headlines)]
            cta   = ctas[n % len(ctas)]
            badge = badges[n % len(badges)]
            bg    = bg_paths[n]

            # Vary parameters deterministically but with spread
            hl_size   = random.choice([72, 74, 76, 78, 80, 82, 84])
            hl_y      = random.randint(800, 860)
            vignette  = round(random.uniform(0.65, 0.90), 2)
            badge_x   = random.choice([780, 800, 810, 820])

            output = f"{RENDERS_DIR}/actionhero-{cat}-{idx:02d}.jpg"

            render = {
                "backgroundPath":     bg,
                "backgroundPosition": "center",
                "output":             output,
                "text": {
                    "headline": hl,
                    "subhead":  "",
                    "cta":      cta,
                    "footer":   ""
                },
                "overlay": {
                    "leftColor":    "4,14,28",
                    "midColor":     "4,14,28",
                    "rightColor":   "4,14,28",
                    "leftOpacity":  0.0,
                    "midOpacity":   0.08,
                    "rightOpacity": 0.0,
                    "vignetteBottom": vignette
                },
                "layout": {
                    "personality":     "editorial-left",
                    "leftX":          60,
                    "headlineY":      hl_y,
                    "subheadY":       2000,
                    "ctaX":           275,
                    "ctaRectX":       60,
                    "ctaRectY":       948,
                    "ctaWidth":       430,
                    "ctaHeight":      72,
                    "ctaRadius":      12,
                    "footerY":        2000,
                    "maxHeadlineChars": 18,
                    "panelX":         0,
                    "panelY":         0,
                    "panelWidth":     0,
                    "panelHeight":    0
                },
                "typography": {
                    "headlineSize": hl_size
                },
                "badges": [
                    {
                        "text":      badge,
                        "x":         badge_x,
                        "y":         40,
                        "fill":      "rgba(232,93,58,0.92)",
                        "textColor": "#FFFFFF",
                        "fontSize":  20,
                        "width":     230,
                        "height":    42,
                        "radius":    8
                    }
                ]
            }

            renders.append(render)

    # ── Shared defaults (merged over each render by render.js) ─────────────────
    defaults = {
        "preset":    "social-square",
        "template":  "banner",
        "logoMode":  "white-card-landscape",
        "logo": {
            "placement": "corner-anchor",
            "corner":    "top-left",
            "width":     260,
            "height":    60,
            "clearSpace": 15
        },
        "theme": {
            "headlineColor":   "#FFFFFF",
            "subheadColor":    "rgba(0,0,0,0)",
            "footerColor":     "rgba(0,0,0,0)",
            "ctaTextColor":    "#FFFFFF",
            "ctaFill":         "rgba(232,93,58,0.98)",
            "ctaStroke":       "rgba(255,255,255,0.24)",
            "textPanelFill":   "rgba(0,0,0,0)",
            "textPanelStroke": "rgba(0,0,0,0)"
        },
        "typography": {
            "headlineFontFamily": "Montserrat, Arial, sans-serif",
            "headlineSize":       78,
            "headlineWeight":     800,
            "bodyFontFamily":     "Source Sans 3, Arial, sans-serif",
            "ctaSize":            30,
            "ctaWeight":          800
        },
        "review": {
            "enforcePanelFit": False
        }
    }

    batch = {
        "defaults": defaults,
        "renders":  renders
    }

    os.makedirs(os.path.dirname(OUT_CONFIG), exist_ok=True)
    with open(OUT_CONFIG, "w") as f:
        json.dump(batch, f, indent=2)

    print(f"✓ Wrote {len(renders)} renders to {OUT_CONFIG}")
    for r in renders:
        cat_label = os.path.basename(r["output"]).replace("actionhero-", "").rsplit("-", 1)[0]
        print(f"  {os.path.basename(r['output'])}  bg={os.path.basename(r['backgroundPath'])}")


if __name__ == "__main__":
    main()
