#!/usr/bin/env python3
"""
gen_actionhero_multiproduct_batch_v6.py
Generates configs/actionhero-multiproduct-batch-v6.json

v6 — hero-classified images with semantic headline pairing:
- Source: hero-classification.json (ONLY hero images, no not_hero)
- Semantic pairing: headline-image-pairs.json drives best_images per headline
- Image selection: use best_images from semantic pair, filtered to hero list only
- 25 renders: belts×7, dredges×6, lures×6, planers×6
- Dredges only has 2 hero images (IMG_9109.jpg, IMG_9098.jpg) — rotate+repeat OK
- No image repeated > 3× per category (relaxed from 2×)
- Logo: corner-anchor, top-left, width 260, height 60, clearSpace 15
- Template: banner, editorial-left only
- NO white-bg product shots (all excluded from hero list)
- Verifies all hero image paths exist on disk before rendering
- Output dir: actionhero-multiproduct-v6/
"""

import json
import os
import random

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

HERO_CLASS_FILE     = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/hero-classification.json"
HEADLINE_PAIRS_FILE = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/headline-image-pairs.json"
COPY_FILE           = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/category-copy-sets-v2.json"
OUT_CONFIG          = os.path.join(PROJECT_ROOT, "configs", "actionhero-multiproduct-batch-v6.json")
RENDERS_DIR         = "/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/actionhero-multiproduct-v6"

# Renders per category (total 25)
COUNTS = {"belts": 7, "dredges": 6, "lures": 6, "planers": 6}

# Copy keys in category-copy-sets-v2.json
COPY_KEYS = {
    "belts":   "belts",
    "dredges": "dredges_teasers",
    "lures":   "lures",
    "planers": "planers_bridles",
}

# Headline-pairing keys in headline-image-pairs.json
PAIR_KEYS = {
    "belts":   "belts",
    "dredges": "dredges",
    "lures":   "lures",
    "planers": "planers",
}

# Per-category badge copy pool
BADGE_COPY = {
    "belts":   ["FIGHTING BELTS", "OFFSHORE READY", "BLUE WATER GEAR", "FIGHT HARD"],
    "dredges": ["DREDGE SEASON", "TROLL SMARTER", "OFFSHORE SPREAD", "TOURNAMENT RIG"],
    "lures":   ["WAHOO SEASON", "OFFSHORE LURES", "TROLL READY", "MAHI COLORS"],
    "planers": ["PLANER KITS", "BRIDLE UP", "RIG IT RIGHT", "SPREAD WIDE"],
}

random.seed(42)  # reproducible


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_hero_index(hero_list):
    """
    Build per-category lookup structures from hero-classification.json hero list.
    Returns:
      hero_by_cat:      {cat: [{"path":..., "filename":...}, ...]}
      hero_filenames:   {cat: set(filenames)}
      hero_path_by_fn:  {filename: path}  (unique by filename across all cats)
    """
    hero_by_cat     = {}
    hero_filenames  = {}
    hero_path_by_fn = {}

    for item in hero_list:
        cat = item["category"]
        fn  = item["filename"]
        path = item["path"]

        hero_by_cat.setdefault(cat, [])
        hero_filenames.setdefault(cat, set())

        # Avoid duplicates within a category (same file listed twice)
        if fn not in hero_filenames[cat]:
            hero_by_cat[cat].append({"path": path, "filename": fn})
            hero_filenames[cat].add(fn)

        # Global filename→path map (last write wins, but filenames are unique)
        hero_path_by_fn[fn] = path

    return hero_by_cat, hero_filenames, hero_path_by_fn


def verify_hero_images(hero_by_cat):
    """
    Verify all hero images exist on disk.
    Prints a report and returns only verified items per category.
    """
    verified = {}
    all_ok = True
    for cat, items in hero_by_cat.items():
        ok = []
        for item in items:
            if os.path.isfile(item["path"]):
                ok.append(item)
            else:
                print(f"  ✗ MISSING hero image [{cat}]: {item['path']}")
                all_ok = False
        verified[cat] = ok
    if all_ok:
        print("  ✓ All hero images verified on disk")
    return verified


def build_headline_to_image_map(pairs_data, pair_key, hero_path_by_fn, hero_filenames_cat):
    """
    For a given category's pairs list, build a headline→[hero_paths] map.
    Only include best_images filenames that exist in the hero set for this category.
    """
    hl_to_paths = {}
    for entry in pairs_data.get(pair_key, []):
        hl = entry["headline"]
        hero_paths = []
        for fn in entry.get("best_images", []):
            if fn in hero_filenames_cat and fn in hero_path_by_fn:
                hero_paths.append(hero_path_by_fn[fn])
        hl_to_paths[hl] = hero_paths
    return hl_to_paths


def pick_image(headline, hl_to_paths, all_hero_paths, usage, max_repeats=3):
    """
    Pick best image for a headline following v6 semantic rules:
    1. Try headline's semantic best_images (hero-filtered) under max_repeats
    2. Fall back to any semantic best_images (ignore max_repeats)
    3. Fall back to full hero pool under max_repeats
    4. Fall back to full hero pool (ignore max_repeats — for tiny pools like dredges)
    """
    semantic = hl_to_paths.get(headline, [])

    # Stage 1: semantic, under limit
    candidates = [p for p in semantic if usage.get(p, 0) < max_repeats]
    if candidates:
        return random.choice(candidates)

    # Stage 2: semantic, ignore limit
    if semantic:
        return random.choice(semantic)

    # Stage 3: full hero pool, under limit
    candidates = [p for p in all_hero_paths if usage.get(p, 0) < max_repeats]
    if candidates:
        return random.choice(candidates)

    # Stage 4: full hero pool, ignore limit (tiny pool fallback)
    return random.choice(all_hero_paths)


def main():
    print("Loading data files...")
    hero_data   = load_json(HERO_CLASS_FILE)
    pairs_data  = load_json(HEADLINE_PAIRS_FILE)
    copy_data   = load_json(COPY_FILE)

    print(f"  Hero images: {len(hero_data['hero'])} hero, {len(hero_data['not_hero'])} not_hero")
    print("  Using ONLY hero list — not_hero excluded")

    # Build hero index
    hero_by_cat, hero_filenames, hero_path_by_fn = build_hero_index(hero_data["hero"])

    for cat, items in hero_by_cat.items():
        fns = [i["filename"] for i in items]
        print(f"  [{cat}] {len(items)} hero images: {fns}")

    # Verify all exist on disk
    print("\nVerifying hero image paths on disk...")
    hero_by_cat = verify_hero_images(hero_by_cat)

    os.makedirs(RENDERS_DIR, exist_ok=True)

    renders = []

    for cat in ["belts", "dredges", "lures", "planers"]:
        count     = COUNTS[cat]
        copy_cat  = copy_data["categories"][COPY_KEYS[cat]]
        headlines = copy_cat["headlines"]
        ctas      = copy_cat["ctas"]
        badges    = BADGE_COPY[cat]

        hero_items     = hero_by_cat.get(cat, [])
        all_hero_paths = [item["path"] for item in hero_items]

        if not all_hero_paths:
            print(f"  ✗ No hero images for [{cat}] — skipping all {count} renders")
            continue

        # Build semantic headline→hero_path map for this category
        pair_key = PAIR_KEYS[cat]
        hl_to_paths = build_headline_to_image_map(
            pairs_data, pair_key,
            hero_path_by_fn,
            hero_filenames.get(cat, set())
        )

        # Log semantic matches
        print(f"\n  [{cat}] semantic matches:")
        for hl, paths in hl_to_paths.items():
            fns = [os.path.basename(p) for p in paths]
            print(f"    '{hl[:40]}' → {fns if fns else '[no hero match, will use pool]'}")

        usage = {}  # track per-path usage within this category
        print(f"\n  [{cat}] {len(all_hero_paths)} hero images → {count} renders")

        for n in range(count):
            idx   = n + 1
            hl    = headlines[n % len(headlines)]
            cta   = ctas[n % len(ctas)]
            badge = badges[n % len(badges)]

            # Semantic image pick
            bg = pick_image(hl, hl_to_paths, all_hero_paths, usage, max_repeats=3)
            usage[bg] = usage.get(bg, 0) + 1

            # Typography variation (deterministic via seed)
            hl_size  = random.choice([72, 74, 76, 78, 80, 82, 84])
            hl_y     = random.randint(800, 860)
            badge_x  = random.choice([780, 800, 810, 820])

            # Vignette — all hero images are action/lifestyle, no white bg
            vignette = round(random.uniform(0.65, 0.90), 2)

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
            print(f"    {os.path.basename(output):<45}  hl='{hl[:30]}'  bg={os.path.basename(bg)}  vignette={vignette}")

    # ── Shared defaults ─────────────────────────────────────────────────────────
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

    # Usage summary per category
    print("\nImage usage summary (v6 hero-only):")
    for cat in ["belts", "dredges", "lures", "planers"]:
        cat_renders = [r for r in renders if f"-{cat}-" in r["output"]]
        from collections import Counter
        counts = Counter(os.path.basename(r["backgroundPath"]) for r in cat_renders)
        print(f"  [{cat}] {dict(counts)}")


if __name__ == "__main__":
    main()
