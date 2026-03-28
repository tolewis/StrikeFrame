#!/usr/bin/env python3
"""
gen_actionhero_multiproduct_batch_v2.py
Generates configs/actionhero-multiproduct-batch-v2.json

Changes from v1:
- Uses category-copy-sets-v2.json (improved copy)
- Planers: ONLY use background/lifestyle images - no planer product cutouts
- Lures: prefer square background images with ocean/boat/action content
- Output dir: actionhero-multiproduct-v2/
"""

import json
import os
import random

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
COPY_FILE    = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/category-copy-sets-v2.json"
INVENTORY    = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/product-bg-inventory.json"
OUT_CONFIG   = os.path.join(PROJECT_ROOT, "configs", "actionhero-multiproduct-batch-v2.json")
RENDERS_DIR  = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/actionhero-multiproduct-v2"

# ── Category mapping ──────────────────────────────────────────────────────────
# v2 changes:
#   planers -> img_cats: ["background", "lifestyle"]  (no planer product cutouts)
#   lures   -> img_cats: ["lure", "background"]       (with background preference for ocean/action)
CATEGORIES = {
    "belts":   {"copy_key": "belts",            "img_cats": ["belt"]},
    "dredges": {"copy_key": "dredges_teasers",  "img_cats": ["dredge"]},
    "lures":   {"copy_key": "lures",            "img_cats": ["lure", "background"]},
    "planers": {"copy_key": "planers_bridles",  "img_cats": ["background", "lifestyle"]},
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

# Filenames to prefer for lures (ocean/boat/action content, square orientation)
LURE_PREFERRED_BG_FILENAMES = {
    "aerial-sharks-boat-a.jpg",
    "aerial-sharks-boat-b.jpg",
    "aerial-sharks-boat-c.jpg",
    "aerial-sharks-boat-d.jpg",
    "aerial-sharks-boat-e.jpg",
    "fighting-fish-dusk-a.jpg",
    "fighting-fish-dusk-b.jpg",
    "fighting-fish-dusk-c.jpg",
    "fighting-fish-dusk-d.jpg",
    "fighting-fish-dusk-e.jpg",
    "fisherman-rough-seas-b.jpg",
    "fisherman-rough-seas-c.jpg",
    "fisherman-rough-seas-d.jpg",
    "mahi-madness-a.jpg",
    "mahi-madness-c.jpg",
    "sportfisher-running-a.jpg",
    "sportfisher-running-b.jpg",
    "sportfisher-running-c.jpg",
    "sportfisher-running-d.jpg",
    "sportfisher-running-e.jpg",
    "sportfisher-jetty-a.jpg",
    "sportfisher-jetty-b.jpg",
    "sportfisher-jetty-c.jpg",
    "sportfisher-jetty-d.jpg",
    "sportfisher-jetty-e.jpg",
    "underwater-mahi-deep-a.jpg",
    "underwater-mahi-deep-b.jpg",
    "underwater-mahi-deep-c.jpg",
    "underwater-mahi-deep-d.jpg",
    "underwater-mahi-deep-e.jpg",
    "underwater-mahi-sunlight-b.jpg",
    "underwater-mahi-sunlight-c.jpg",
    "underwater-mahi-sunlight-d.jpg",
    "underwater-mahi-sunlight-e.jpg",
    "troll-pro-camera-a.jpg",
    "troll-pro-camera-b.jpg",
    "troll-pro-camera-c.jpg",
    "rod-holders-lures-a.jpg",
    "rod-holders-lures-b.jpg",
    "rod-holders-lures-c.jpg",
    "rod-holders-lures-d.jpg",
    "rod-holders-lures-e.jpg",
}

# Filenames to exclude from planer pool (logos, retargeting graphics, non-scene images)
PLANER_BG_EXCLUDE = {
    "logo-landscape-1200x300-v2.png",
    "logo-landscape-1200x300.png",
    "logo-square-1200x1200-v2.png",
    "logo-square-1200x1200.png",
    "retarget-benefit-stack-trust.jpg",
    "retarget-testimonial-trust.jpg",
    "TR-logo-2024-diamond_large.png",
    "TackleRoom 1.1.png",
    "tackle room-logo-2024-diamond.png",
    "tackleroom logo shaded 2048.png",
    "tackleroom logo shaded.jpg",
    "tackleroom logo.png",
    "epic logo 1.png",
    "epic logo with outline.png",
    "GoodCompany2.jpg",
}

random.seed(42)  # reproducible


def load_json(path):
    with open(path) as f:
        return json.load(f)


def filter_backgrounds(inventory_images, img_cats, orientation_filter=None, exclude_filenames=None):
    """Return images from specified inventory categories, optionally filtered by orientation."""
    exclude = exclude_filenames or set()
    results = [
        img for img in inventory_images
        if img["category"] in img_cats
        and img["filename"] not in exclude
    ]
    if orientation_filter:
        results = [img for img in results if img["orientation"] in orientation_filter]
    else:
        results = [img for img in results if img["orientation"] in ("square", "landscape")]
    return results


def filter_lure_preferred(images):
    """Split lure images into preferred-background pool and fallback pool."""
    preferred = [img for img in images
                 if img["category"] == "background"
                 and img["orientation"] == "square"
                 and img["filename"] in LURE_PREFERRED_BG_FILENAMES]
    other = [img for img in images if img not in preferred]
    return preferred, other


def build_bg_rotation(images, count, max_repeats=2, preferred=None):
    """
    Build a list of `count` background paths, rotating through the pool.
    If `preferred` list is provided, use those first before falling back to `images`.
    No single image appears more than max_repeats times.
    Falls back to unconstrained if pool is too small.
    """
    if not images:
        raise ValueError("No background images found")

    # Build combined pool: preferred first, then rest
    if preferred:
        pool = list(preferred) + [img for img in images if img not in preferred]
    else:
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

        # --- Image selection strategy per category ---

        if cat == "planers":
            # ONLY background or lifestyle - no planer product cutouts
            cat_images = filter_backgrounds(
                all_images,
                ["background", "lifestyle"],
                orientation_filter=["square"],
                exclude_filenames=PLANER_BG_EXCLUDE
            )
            preferred_pool = None

        elif cat == "lures":
            # Pull lure product shots + background imagery
            cat_images = filter_backgrounds(all_images, cfg["img_cats"])
            # Build preferred pool: square background images with ocean/boat/action
            preferred_pool, _ = filter_lure_preferred(cat_images)
            if len(preferred_pool) < 3:
                preferred_pool = None  # not enough to matter

        else:
            cat_images = filter_backgrounds(all_images, cfg["img_cats"])
            preferred_pool = None

        # Fall back to generic background/lifestyle images if pool is too small
        if len(cat_images) < 3:
            generic = filter_backgrounds(all_images, ["background", "lifestyle"],
                                         exclude_filenames=PLANER_BG_EXCLUDE)
            cat_images = cat_images + generic

        bg_paths = build_bg_rotation(cat_images, count, max_repeats=2,
                                      preferred=preferred_pool)

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
        print(f"  {os.path.basename(r['output'])}  bg={os.path.basename(r['backgroundPath'])}")


if __name__ == "__main__":
    main()
