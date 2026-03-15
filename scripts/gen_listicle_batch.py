#!/usr/bin/env python3
"""Generate listicle/spec transparency ad batch — numbered benefits or spec grids.
Overlaps with explainer but uses numbered list format (Magic Spoon, MudWtr model).
Uses textLayers with numbered prefixes."""
import csv, os, json, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_DARK, OCEAN_BACKGROUNDS,
    category_for_title,
)

OUT = "/mnt/raid/Data/tmp/ads/listicle"
BRIEF_DIR = "/mnt/raid/Data/tmp/tackleroom-product-pages/"


def load_top_products(limit=20):
    csv_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Analytics/top_products_last90d_2026-02-19_2306.csv"
    products = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            products.append(row)
            if int(row["rank"]) >= limit:
                break
    return products


def load_content_specs():
    index = {}
    for f in os.listdir(BRIEF_DIR):
        if f.endswith("-content-spec.json"):
            try:
                d = json.load(open(os.path.join(BRIEF_DIR, f)))
                pid = d.get("product_id")
                if pid:
                    index[pid] = d
            except Exception:
                pass
    return index


def short_title(title):
    title = re.sub(r"\s*\|.*$", "", title)
    title = re.sub(r"\s*by\s+\w+.*$", "", title, flags=re.I)
    return title.strip()


def extract_features(spec):
    mf = spec.get("metafields", {})
    features = []
    for i in range(1, 4):
        t = mf.get(f"feature_{i}_title", "")
        if t:
            features.append(t)
    return features


def extract_specs(spec):
    body = spec.get("body_html", "")
    items = re.findall(r"<li>(.*?)</li>", body, re.I)
    specs = []
    for item in items:
        s = re.sub(r"<[^>]+>", "", item).strip()
        if s and len(s) <= 48:
            specs.append(s)
    return specs[:5]


def build_render(product, spec, variant, bg_index):
    handle = spec.get("product_handle", "product")
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]
    title = short_title(product["title"])
    items = variant["items"]

    # Build numbered text layers
    text_layers = []
    start_y = 420
    spacing = 80

    # Section header
    text_layers.append({
        "content": variant.get("header", "THE SPECS"),
        "x": 540,
        "y": start_y - 50,
        "fontSize": 16,
        "fontWeight": 700,
        "color": "rgba(255,255,255,0.4)",
        "maxChars": 30,
        "align": "center",
    })

    for i, item in enumerate(items[:5]):
        text_layers.append({
            "content": f"{i + 1}.  {item}",
            "x": 540,
            "y": start_y + i * spacing,
            "fontSize": 28,
            "fontWeight": 600,
            "color": "#ffffff",
            "maxChars": 32,
            "align": "center",
        })

    # Domain footer
    text_layers.append({
        "content": BRAND["name"],
        "x": 540,
        "y": 1050,
        "fontSize": 14,
        "fontWeight": 600,
        "color": "rgba(255,255,255,0.3)",
        "maxChars": 40,
        "align": "center",
    })

    return {
        "_comment": f"=== {handle} | Variant {variant['id']} | listicle ===",
        "output": f"{OUT}/{handle}-list-{variant['id']}.jpg",
        "backgroundPath": bg,
        "text": {
            "headline": title.upper(),
            "subhead": "",
            "cta": variant.get("cta", "SHOP NOW"),
            "footer": "",
        },
        "overlay": OVERLAY_DARK,
        "typography": {
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 52,
            "subheadSize": 1,
            "headlineWeight": 800,
            "ctaSize": 22,
            "ctaWeight": 700,
            "footerSize": 1,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "centered-hero",
            "align": "center",
            "leftX": 540,
            "headlineY": 220,
            "subheadY": 240,
            "maxHeadlineChars": 22,
            "maxSubheadChars": 1,
            "ctaWidth": 280,
            "ctaHeight": 58,
            "ctaRectX": 400,
            "ctaRectY": start_y + len(items[:5]) * spacing + 20,
            "ctaX": 540,
            "ctaY": start_y + len(items[:5]) * spacing + 49,
            "footerY": 1060,
        },
        "textLayers": text_layers,
    }


def build_variants(product, spec):
    title = short_title(product["title"])
    features = extract_features(spec)
    specs_list = extract_specs(spec)

    fallback = ["Premium build quality", "Built for saltwater", "Trusted by tournament anglers"]
    while len(features) < 3:
        features.append(fallback[len(features)] if len(features) < len(fallback) else fallback[-1])
    if not specs_list:
        specs_list = list(features)

    variants = []

    # Variant A: Feature listicle
    variants.append({
        "id": "a",
        "header": "WHY THIS ONE",
        "items": features[:5],
        "cta": "SHOP NOW",
    })

    # Variant B: Spec transparency
    variants.append({
        "id": "b",
        "header": "EVERYTHING IN IT",
        "items": specs_list[:5],
        "cta": "SEE FULL SPECS",
    })

    return variants


def main():
    os.makedirs(OUT, exist_ok=True)
    products = load_top_products(20)
    specs_index = load_content_specs()

    config = {
        "defaults": {
            "preset": "social-square",
            "template": "banner",
            "theme": THEME_DEFAULT,
        },
        "renders": [],
    }

    matched = []
    for p in products:
        pid = int(p["product_id"])
        spec = specs_index.get(pid)
        if not spec:
            continue

        variants = build_variants(p, spec)
        bg_idx = len(matched)
        for v in variants:
            config["renders"].append(build_render(p, spec, v, bg_idx))
        matched.append(p["title"])

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-listicle.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Products matched: {len(matched)}")
    print(f"Renders generated: {len(config['renders'])} ({len(matched)} products x 2 variants)")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
