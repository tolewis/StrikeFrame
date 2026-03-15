#!/usr/bin/env python3
"""Generate benefit-stack ad batch — product hero + 3-4 icon/benefit rows.
Most common ad format in the competitive dataset (Grundens, AFTCO, LMNT model).
2 variants per product: benefit-led angle + specs angle."""
import csv, os, json, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from tackleroom_defaults import (
    BRAND, THEME_DEFAULT, OVERLAY_EDITORIAL, OVERLAY_OCEAN,
    OCEAN_BACKGROUNDS, guess_icon, category_for_title,
    CATEGORY_VOICE, wrap_text, est_text_width,
)

OUT = "/mnt/raid/Data/tmp/ads/benefit-stack"
BRIEF_DIR = "/mnt/raid/Data/tmp/tackleroom-product-pages/"


def load_top_products(limit=30):
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


def find_product_images():
    img_dirs = [
        "/home/tlewis/Dropbox/Tim/TackleRoom/Creative/Products/",
        "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/assets/product-photos/",
        "/home/tlewis/Dropbox/Tim/TackleRoom/Creative/Assets/ProductImages/",
    ]
    for sub in ["Bridle", "LipGripper", "VerticalHook"]:
        p = f"/home/tlewis/Dropbox/Tim/TackleRoom/Creative/Assets/{sub}/"
        if os.path.isdir(p):
            img_dirs.append(p)
    images = []
    for d in img_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and os.path.isfile(os.path.join(d, f)):
                images.append((f.lower(), os.path.join(d, f)))
    return images


def match_image(title, images):
    title_lower = title.lower()
    skip = {"the", "by", "with", "and", "or", "for", "a", "an", "co", "co.", "epic",
            "fishing", "pack", "lb", "oz", "inch", "100", "25", "10"}
    words = [w.strip("|(,)") for w in re.split(r"[\s|]+", title_lower) if len(w) > 2 and w not in skip]
    best_score = 0
    best_match = None
    for fname, fpath in images:
        score = sum(1 for w in words if w in fname)
        if score > best_score:
            best_score = score
            best_match = fpath
    return best_match if best_score >= 2 else None


def short_title(title):
    title = re.sub(r"\s*\|.*$", "", title)
    title = re.sub(r"\s*by\s+\w+.*$", "", title, flags=re.I)
    title = re.sub(r"\s*-\s+\w+.*$", "", title)
    return title.strip()


def extract_features(spec):
    mf = spec.get("metafields", {})
    features = []
    for i in range(1, 4):
        t = mf.get(f"feature_{i}_title", "")
        if t:
            features.append(t)
    return features


def extract_feature_bodies(spec):
    mf = spec.get("metafields", {})
    bodies = []
    for i in range(1, 4):
        b = mf.get(f"feature_{i}_body", "")
        if not b:
            continue
        b = re.sub(r'<[^>]+>', '', b).strip()
        sentences = re.split(r'[.?!]\s+', b)
        for sent in sentences[:4]:
            sent = sent.strip().rstrip('.!?')
            if 12 <= len(sent) <= 48:
                bodies.append(sent)
                break
    return bodies


def extract_specs(spec):
    body = spec.get("body_html", "")
    items = re.findall(r"<li>(.*?)</li>", body, re.I)
    specs = []
    for item in items:
        s = re.sub(r"<[^>]+>", "", item).strip()
        if s and len(s) <= 48:
            specs.append(s)
    return specs[:4]


def build_benefit_items(features, title):
    """Convert feature strings to benefit-stack items with auto-mapped icons."""
    items = []
    for feat in features[:4]:
        items.append({
            "icon": guess_icon(feat),
            "label": feat,
        })
    # Pad to at least 3
    fallback = ["Premium Build Quality", "Built for Saltwater", "Trusted by Anglers"]
    while len(items) < 3:
        idx = len(items)
        items.append({
            "icon": "check",
            "label": fallback[idx] if idx < len(fallback) else fallback[-1],
        })
    return items


def build_render(product, spec, image_path, variant, bg_index):
    handle = spec.get("product_handle", "product")
    bg = OCEAN_BACKGROUNDS[bg_index % len(OCEAN_BACKGROUNDS)]
    title = variant["headline"]
    category = category_for_title(product["title"])
    voice = CATEGORY_VOICE.get(category, CATEGORY_VOICE["kits"])

    # Dynamic CTA width
    cta_text = variant.get("cta", "SHOP NOW")
    cta_size = 24
    cta_width = max(280, est_text_width(cta_text, cta_size) + 80)

    return {
        "_comment": f"=== {handle} | Variant {variant['id']} | benefit-stack ===",
        "output": f"{OUT}/{handle}-bs-{variant['id']}.jpg",
        "backgroundPath": bg,
        "backgroundPosition": "attention",
        "text": {
            "headline": title.upper(),
            "subhead": variant.get("subhead", ""),
            "cta": cta_text,
            "footer": BRAND["name"],
        },
        "overlay": OVERLAY_EDITORIAL,
        "typography": {
            "headlineFontFamily": BRAND["headline_font"],
            "bodyFontFamily": BRAND["body_font"],
            "headlineSize": 54,
            "subheadSize": 26,
            "headlineWeight": 800,
            "subheadWeight": 400,
            "ctaSize": cta_size,
            "ctaWeight": 700,
            "footerSize": 14,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "editorial-left",
            "align": "left",
            "leftX": 80,
            "headlineY": 180,
            "subheadY": 340,
            "maxHeadlineChars": 20,
            "maxSubheadChars": 34,
            "ctaWidth": cta_width,
            "ctaHeight": 58,
            "ctaRectX": 80,
            "ctaRectY": 920,
            "ctaX": 80 + cta_width // 2,
            "ctaY": 920 + 29,
            "footerY": 1050,
        },
        "benefitStack": {
            "startX": 80,
            "startY": 500,
            "spacing": 95,
            "iconSize": 36,
            "iconColor": "rgba(232,93,58,0.9)",
            "textSize": 26,
            "textColor": "#ffffff",
            "textMaxChars": 30,
            "items": variant["items"],
        },
    }


def build_variants(product, spec):
    title = short_title(product["title"])
    features = extract_features(spec)
    bodies = extract_feature_bodies(spec)
    specs_list = extract_specs(spec)
    mf = spec.get("metafields", {})
    value_heading = mf.get("value_story_heading", "")

    benefit_items = build_benefit_items(features, title)
    spec_items = build_benefit_items(specs_list if specs_list else features, title)

    # Variant A: Benefit-led — outcome-focused headline + feature benefits
    variants = [{
        "id": "a",
        "headline": value_heading if value_heading else title,
        "subhead": "Everything you need. Nothing you don't.",
        "cta": "SHOP NOW",
        "items": benefit_items,
    }]

    # Variant B: Specs-led — product name + spec bullets
    variants.append({
        "id": "b",
        "headline": title,
        "subhead": "The specs that matter.",
        "cta": "SEE FULL SPECS",
        "items": spec_items,
    })

    return variants


def main():
    os.makedirs(OUT, exist_ok=True)
    products = load_top_products(30)
    specs_index = load_content_specs()
    all_images = find_product_images()

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
        img = match_image(p["title"], all_images)
        if not img:
            continue

        variants = build_variants(p, spec)
        bg_idx = len(matched)
        for v in variants:
            config["renders"].append(build_render(p, spec, img, v, bg_idx))
        matched.append(p["title"])

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-benefit-stack.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Products matched: {len(matched)}")
    print(f"Renders generated: {len(config['renders'])} ({len(matched)} products x 2 variants)")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
