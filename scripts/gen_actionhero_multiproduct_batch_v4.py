#!/usr/bin/env python3
"""
gen_actionhero_multiproduct_batch_v4.py
Generates configs/actionhero-multiproduct-batch-v4.json

v4 changes vs v3:
- Uses content-match-map-v2.json (raw photography ONLY, no rendered ads)
- Same strategic headline-to-image matching as v3
- Same rotation rules (no image repeated > 2x per category)
- Output dir: actionhero-multiproduct-v4/
- 25 renders: belts×7, dredges×6, lures×6, planers×6
"""

import json
import os
import random

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CONTENT_MATCH_FILE = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/content-match-map-v2.json"
COPY_FILE          = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/category-copy-sets-v2.json"
OUT_CONFIG         = os.path.join(PROJECT_ROOT, "configs", "actionhero-multiproduct-batch-v4.json")
RENDERS_DIR        = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/actionhero-multiproduct-v4"

# Renders per category (total 25)
COUNTS = {"belts": 7, "dredges": 6, "lures": 6, "planers": 6}

# Copy keys in category-copy-sets-v2.json
COPY_KEYS = {
    "belts":   "belts",
    "dredges": "dredges_teasers",
    "lures":   "lures",
    "planers": "planers_bridles",
}

# Per-category badge copy pool
BADGE_COPY = {
    "belts":   ["FIGHTING BELTS", "OFFSHORE READY", "BLUE WATER GEAR", "FIGHT HARD"],
    "dredges": ["DREDGE SEASON", "TROLL SMARTER", "OFFSHORE SPREAD", "TOURNAMENT RIG"],
    "lures":   ["WAHOO SEASON", "OFFSHORE LURES", "TROLL READY", "MAHI COLORS"],
    "planers": ["PLANER KITS", "BRIDLE UP", "RIG IT RIGHT", "SPREAD WIDE"],
}

# ── Strategic image-to-headline matching sets ─────────────────────────────────
# Belts: fighting-action vs product-only
BELT_FIGHTING_FILENAMES = {
    "seamount-fish-fighting-belt-a.jpg",
    "seamount-fish-fighting-belt-b.jpg",
    "seamount-fish-fighting-belt-c.jpg",
    "fighting-fish-dusk-a.jpg",
    "fighting-fish-dusk-b.jpg",
    "fighting-fish-dusk-c.jpg",
}
BELT_PRODUCT_FILENAMES = {
    "fighting-belts-landscape.jpg",
}

# Dredges: daisy-chain/spread vs squid-dredge product
DREDGE_DAISY_FILENAMES = {
    "flying-fish-daisy-chain-a.jpg",
    "squid-daisy-chain-a.jpg",
    "squid-daisy-chain-c.jpg",
    "epic-fishing-flying-fish-daisy-chain-a.jpg",
}
DREDGE_SQUID_FILENAMES = {
    "phat-squid-dredge-a.jpg",
    "phat-squid-dredge-b.jpg",
    "phat-squid-dredge-c.jpg",
    "squid-flapz-dredge-a.jpg",
    "monster-squid-dredge-c.jpg",
}
DREDGE_SPREAD_FILENAMES = {
    "troll-pro-camera-a.jpg",
    "squid-daisy-chain-a.jpg",
    "squid-daisy-chain-c.jpg",
    "epic-fishing-flying-fish-daisy-chain-a.jpg",
}

# Lures: wahoo vs mahi vs general-trolling
LURE_WAHOO_FILENAMES = {
    "epic-axis-stainless-steel-wahoo-trolling-lure-a.jpg",
    "epic-axis-stainless-steel-wahoo-trolling-lure-b.jpg",
    "hawaiian-ono-wahoo-gyotaku-artwork-print-by-dwight-hwang-a.jpg",
}
LURE_MAHI_FILENAMES = {
    "mahi-madness-b.jpg",
}
LURE_TROLL_FILENAMES = {
    "rod-holders-lures-a.jpg",
    "rod-holders-lures-b.jpg",
    "rod-holders-lures-c.jpg",
    "sea-witch-heads-a.jpg",
    "uv-sea-witch-hair-a.jpg",
}

# Planers: bridle/clip vs lifestyle-running
PLANER_BRIDLE_FILENAMES = {
    "planer-bridle-a.jpg",
    "planer-bridle-b.jpg",
    "planer-bridle-c.jpg",
    "planer-bridle-kit-a.jpg",
    "planer-bridle-rigging-kit-a.jpg",
    "BridleClips noLogo.png",
    "fishing-bridle-leader-reel-a.jpg",
}
PLANER_RUNNING_FILENAMES = {
    "sportfisher-running-a.jpg",
    "sportfisher-running-b.jpg",
}

random.seed(42)  # reproducible


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_preferred_pool(cat, headline_lower, content_images):
    """
    Return a preferred sub-list of content_images based on headline keywords.
    Falls back to full pool if preferred sub-list is empty.
    """
    paths_by_filename = {os.path.basename(img["path"]): img["path"] for img in content_images}

    def fnames_to_paths(fname_set):
        return [paths_by_filename[fn] for fn in fname_set if fn in paths_by_filename]

    if cat == "belts":
        if "marlin" in headline_lower or "fight" in headline_lower or "wahoo" in headline_lower:
            preferred = fnames_to_paths(BELT_FIGHTING_FILENAMES)
        elif "belt" in headline_lower or "back" in headline_lower:
            # Product pool is small — expand to all fighting images as fallback
            product = fnames_to_paths(BELT_PRODUCT_FILENAMES)
            preferred = product if len(product) >= 2 else fnames_to_paths(BELT_FIGHTING_FILENAMES | BELT_PRODUCT_FILENAMES)
        else:
            preferred = [img["path"] for img in content_images]

    elif cat == "dredges":
        if "daisy chain" in headline_lower:
            preferred = fnames_to_paths(DREDGE_DAISY_FILENAMES)
        elif "squid" in headline_lower or "four" in headline_lower:
            preferred = fnames_to_paths(DREDGE_SQUID_FILENAMES)
        elif "spread" in headline_lower or "marlin" in headline_lower:
            preferred = fnames_to_paths(DREDGE_SPREAD_FILENAMES)
        else:
            preferred = [img["path"] for img in content_images]

    elif cat == "lures":
        if "wahoo" in headline_lower:
            preferred = fnames_to_paths(LURE_WAHOO_FILENAMES)
        elif "mahi" in headline_lower or "pink" in headline_lower:
            preferred = fnames_to_paths(LURE_MAHI_FILENAMES)
        elif "troll" in headline_lower or "skirt" in headline_lower or "tuna" in headline_lower:
            preferred = fnames_to_paths(LURE_TROLL_FILENAMES)
        else:
            preferred = [img["path"] for img in content_images]

    elif cat == "planers":
        if "bridle" in headline_lower or "live" in headline_lower or "sailfish" in headline_lower:
            preferred = fnames_to_paths(PLANER_BRIDLE_FILENAMES)
        elif "spread" in headline_lower or "planer" in headline_lower:
            # Mix bridle + running for spread/planer headlines
            preferred = fnames_to_paths(PLANER_BRIDLE_FILENAMES | PLANER_RUNNING_FILENAMES)
        else:
            preferred = [img["path"] for img in content_images]

    else:
        preferred = [img["path"] for img in content_images]

    # Fall back to full pool if preferred is empty
    return preferred if preferred else [img["path"] for img in content_images]


def build_bg_rotation(content_images, count, cat, headlines, max_repeats=2):
    """
    Build a list of `count` background paths for this category.
    For each render (n), match the headline to the best preferred pool,
    then pick from that pool respecting the max_repeats constraint.
    """
    all_paths = [img["path"] for img in content_images]
    usage = {}
    result = []

    for n in range(count):
        hl_lower = headlines[n % len(headlines)].lower()
        preferred = get_preferred_pool(cat, hl_lower, content_images)

        # Try preferred pool first (under max_repeats)
        candidates = [p for p in preferred if usage.get(p, 0) < max_repeats]
        if not candidates:
            # Try any from preferred (ignore max_repeats)
            candidates = list(preferred) if preferred else all_paths

        if not candidates:
            candidates = all_paths

        chosen = random.choice(candidates)
        result.append(chosen)
        usage[chosen] = usage.get(chosen, 0) + 1

    return result


def verify_content_images(content_map, cat_key):
    """Verify images exist on disk; return only those that do."""
    verified = []
    skipped = []
    for item in content_map.get(cat_key, []):
        if os.path.isfile(item["path"]):
            verified.append(item)
        else:
            skipped.append(item["path"])
    if skipped:
        print(f"  ⚠ Skipped missing images in [{cat_key}]:")
        for p in skipped:
            print(f"      MISSING: {p}")
    return verified, skipped


def main():
    copy_data   = load_json(COPY_FILE)
    content_map = load_json(CONTENT_MATCH_FILE)

    os.makedirs(RENDERS_DIR, exist_ok=True)

    renders = []
    all_skipped = []

    for cat in ["belts", "dredges", "lures", "planers"]:
        count    = COUNTS[cat]
        copy_cat = copy_data["categories"][COPY_KEYS[cat]]
        headlines = copy_cat["headlines"]
        ctas      = copy_cat["ctas"]
        badges    = BADGE_COPY[cat]

        # Verify images from content-match-map-v2
        content_images, skipped = verify_content_images(content_map, cat)
        all_skipped.extend(skipped)

        if not content_images:
            print(f"  ✗ No valid images for [{cat}] — skipping all {count} renders")
            continue

        print(f"  [{cat}] {len(content_images)} valid images → {count} renders")

        # Build rotation with headline-to-image matching
        bg_paths = build_bg_rotation(content_images, count, cat, headlines, max_repeats=2)

        for n in range(count):
            idx   = n + 1
            hl    = headlines[n % len(headlines)]
            cta   = ctas[n % len(ctas)]
            badge = badges[n % len(badges)]
            bg    = bg_paths[n]

            # Vary typography and layout deterministically
            hl_size  = random.choice([72, 74, 76, 78, 80, 82, 84])
            hl_y     = random.randint(800, 860)
            vignette = round(random.uniform(0.65, 0.90), 2)
            badge_x  = random.choice([780, 800, 810, 820])

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
                    "leftColor":      "4,14,28",
                    "midColor":       "4,14,28",
                    "rightColor":     "4,14,28",
                    "leftOpacity":    0.0,
                    "midOpacity":     0.08,
                    "rightOpacity":   0.0,
                    "vignetteBottom": vignette
                },
                "layout": {
                    "personality":      "editorial-left",
                    "leftX":            60,
                    "headlineY":        hl_y,
                    "subheadY":         2000,
                    "ctaX":             275,
                    "ctaRectX":         60,
                    "ctaRectY":         948,
                    "ctaWidth":         430,
                    "ctaHeight":        72,
                    "ctaRadius":        12,
                    "footerY":          2000,
                    "maxHeadlineChars": 18,
                    "panelX":           0,
                    "panelY":           0,
                    "panelWidth":       0,
                    "panelHeight":      0
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
        "preset":   "social-square",
        "template": "banner",
        "logoMode": "white-card-landscape",
        "logo": {
            "placement":  "corner-anchor",
            "corner":     "top-left",
            "width":      260,
            "height":     60,
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

    print(f"\n✓ Wrote {len(renders)} renders to {OUT_CONFIG}")
    if all_skipped:
        print(f"  ⚠ Total skipped (missing) images: {len(all_skipped)}")
    else:
        print(f"  ✓ No missing images skipped")

    print("\nRender manifest:")
    for r in renders:
        print(f"  {os.path.basename(r['output']):<40}  bg={os.path.basename(r['backgroundPath'])}")


if __name__ == "__main__":
    main()
