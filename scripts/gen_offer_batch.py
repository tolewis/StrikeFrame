#!/usr/bin/env python3
"""Generate offer/price frame ad batch — product + price callout + savings badge.
Revenue-direct format (HexClad, Ridge, YETI model).
2 variants per product: offer/kit framing + price emphasis."""
import csv, os, json, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_EDITORIAL, OCEAN_BACKGROUNDS,
    category_for_title, est_text_width,
)

OUT = "/mnt/raid/Data/tmp/ads/offer"
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


def build_render(product, spec, variant, bg_index):
    handle = spec.get("product_handle", "product")
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]
    mf = spec.get("metafields", {})
    price_min = mf.get("price_min", "")

    # Try to get price from research brief
    if not price_min:
        try:
            brief = json.load(open(os.path.join(BRIEF_DIR, handle + "-research-brief.json")))
            price_min = brief.get("price_range", {}).get("min", "")
        except Exception:
            pass

    price_str = f"${price_min}" if price_min else ""
    title = short_title(product["title"])
    category = category_for_title(product["title"])

    # Badge based on category
    badge_map = {
        "kits": "COMPLETE KIT",
        "planers": "COMPLETE KIT",
        "dredges": "CAPTAIN'S PICK",
        "daisy_chains": "TOURNAMENT PROVEN",
        "lures": "BEST SELLER",
        "belts": "CAPTAIN'S PICK",
    }
    badge_text = badge_map.get(category, "BEST SELLER")

    return {
        "_comment": f"=== {handle} | Variant {variant['id']} | offer ===",
        "output": f"{OUT}/{handle}-offer-{variant['id']}.jpg",
        "backgroundPath": bg,
        "text": {
            "headline": variant["headline"],
            "subhead": variant.get("subhead", ""),
            "cta": variant["cta"],
            "footer": BRAND["name"],
        },
        "overlay": OVERLAY_EDITORIAL,
        "typography": {
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 52,
            "subheadSize": 24,
            "headlineWeight": 800,
            "subheadWeight": 400,
            "ctaSize": 22,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "editorial-left",
            "align": "left",
            "leftX": 80,
            "headlineY": 180,
            "subheadY": 350,
            "maxHeadlineChars": 18,
            "maxSubheadChars": 30,
            "ctaWidth": 280,
            "ctaHeight": 58,
            "ctaRectX": 80,
            "ctaRectY": 920,
            "ctaX": 220,
            "ctaY": 949,
            "footerY": 1050,
        },
        "offerFrame": variant.get("offerFrame"),
        "badges": [{
            "text": badge_text,
            "x": 80,
            "y": 100,
            "fill": "rgba(232,93,58,0.92)",
            "textColor": "#ffffff",
            "fontSize": 14,
        }] if variant["id"] == "a" else None,
    }


def build_variants(product, spec):
    title = short_title(product["title"])
    mf = spec.get("metafields", {})
    price_min = mf.get("price_min", "")
    if not price_min:
        try:
            handle = spec.get("product_handle", "")
            brief = json.load(open(os.path.join(BRIEF_DIR, handle + "-research-brief.json")))
            price_min = brief.get("price_range", {}).get("min", "")
        except Exception:
            pass

    price_str = f"${price_min}" if price_min else "$49.99"

    # Variant A: Offer/kit framing
    variants = [{
        "id": "a",
        "headline": title,
        "subhead": "Everything in one order. Free shipping over $99.",
        "cta": "SHOP NOW",
        "offerFrame": {
            "salePrice": price_str,
            "salePriceSize": 64,
            "offerText": "FREE SHIPPING OVER $99",
            "priceY": 620,
        },
    }]

    # Variant B: Price emphasis with from-price anchor
    variants.append({
        "id": "b",
        "headline": title,
        "subhead": "Direct-to-angler pricing. No middlemen.",
        "cta": f"FROM {price_str}",
        "offerFrame": {
            "salePrice": price_str,
            "salePriceSize": 72,
            "savings": "DIRECT PRICING",
            "priceY": 600,
        },
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

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-offer.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Products matched: {len(matched)}")
    print(f"Renders generated: {len(config['renders'])} ({len(matched)} products x 2 variants)")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
