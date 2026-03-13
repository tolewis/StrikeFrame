#!/usr/bin/env python3
"""Generate product explainer card batch — top products × 3 variants."""
import csv, os, json, re

STOCK = "/home/tlewis/Dropbox/Tim/TackleRoom/Creative/Assets/AdobeStock"
OUT = "/mnt/raid/Data/tmp/ads/explainer"
BRIEF_DIR = "/mnt/raid/Data/tmp/tackleroom-product-pages/"

# Ocean backgrounds (cycle through TOF images)
OCEAN_BGS = [
    f"{STOCK}/AdobeStock_372953083.jpeg",
    f"{STOCK}/AdobeStock_133588506.jpeg",
    f"{STOCK}/AdobeStock_175678582.jpeg",
    f"{STOCK}/AdobeStock_219637627.jpeg",
    f"{STOCK}/AdobeStock_331722964.jpeg",
    f"{STOCK}/AdobeStock_284446852.jpeg",
    f"{STOCK}/AdobeStock_229283027.jpeg",
    f"{STOCK}/AdobeStock_337378282.jpeg",
    f"{STOCK}/AdobeStock_345435684.jpeg",
    f"{STOCK}/AdobeStock_991789270.jpeg",
]


def load_top_products(limit=50):
    """Load top products from analytics CSV."""
    products = []
    csv_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Analytics/top_products_last90d_2026-02-19_2306.csv"
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            products.append(row)
            if int(row["rank"]) >= limit:
                break
    return products


def load_content_specs():
    """Index content specs by product_id."""
    index = {}
    for f in os.listdir(BRIEF_DIR):
        if f.endswith("-content-spec.json"):
            try:
                d = json.load(open(os.path.join(BRIEF_DIR, f)))
                pid = d.get("product_id")
                if pid:
                    index[pid] = d
            except:
                pass
    return index


def find_product_images():
    """Collect all product images from known directories."""
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
    """Fuzzy match product title to image filename."""
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
    """Shorten product title for headline use."""
    title = re.sub(r"\s*\|.*$", "", title)
    title = re.sub(r"\s*by\s+\w+.*$", "", title, flags=re.I)
    title = re.sub(r"\s*-\s+\w+.*$", "", title)
    title = re.sub(r"\s*\|\s*\d+.*$", "", title)
    title = re.sub(r"\s*\d+\s*pack\s*", "", title, flags=re.I)
    return title.strip()


def extract_features(spec):
    """Extract feature titles from content spec metafields."""
    mf = spec.get("metafields", {})
    features = []
    for i in range(1, 4):
        t = mf.get(f"feature_{i}_title", "")
        if t:
            features.append(t)
    return features


def extract_feature_bodies(spec):
    """Extract short feature clauses from content spec."""
    mf = spec.get("metafields", {})
    bodies = []
    for i in range(1, 4):
        b = mf.get(f"feature_{i}_body", "")
        if b:
            # First clause before ", " or ". " or " and "
            clause = re.split(r'[,.]\s|\s+and\s+', b)[0].strip()
            if len(clause) > 50:
                clause = clause[:47].rsplit(" ", 1)[0] + "..."
            bodies.append(clause)
    return bodies


def extract_specs_from_body(spec):
    """Extract spec-like bullet points from body_html."""
    body = spec.get("body_html", "")
    items = re.findall(r"<li>(.*?)</li>", body, re.I)
    specs = [re.sub(r"<[^>]+>", "", item).strip() for item in items]
    return [s for s in specs if s and len(s) < 55][:4]


def build_render(product, spec, image_path, variant, bg_index):
    """Build a single explainer card render config."""
    handle = spec.get("product_handle", "product")
    bg = OCEAN_BGS[bg_index % len(OCEAN_BGS)]

    features = variant["features"]
    num_feats = min(len(features), 4)
    headline = variant["headline"]

    # Layout constants (1080x1080)
    SPLIT_Y = 580       # ocean bg top / content bottom split
    PRODUCT_W = 440      # white product area width
    PANEL_X = PRODUCT_W  # dark panel starts here
    PANEL_W = 1080 - PANEL_X  # 640px dark panel

    # Feature panel layout
    FEAT_SIZE = 20
    FEAT_STEP = 65
    FEAT_MAX_CHARS = 30

    feat_x = PANEL_X + 35
    header_y = SPLIT_Y + 35
    feat_start_y = SPLIT_Y + 80

    # Feature text layers
    feature_layers = []

    # Section header
    feature_layers.append({
        "content": variant.get("header", "FEATURES"),
        "x": feat_x,
        "y": header_y,
        "fontSize": 17,
        "fontWeight": 700,
        "color": "rgba(255,255,255,0.5)",
        "maxChars": 40,
    })

    for i, feat in enumerate(features[:4]):
        feature_layers.append({
            "content": f"✓ {feat}",
            "x": feat_x,
            "y": feat_start_y + i * FEAT_STEP,
            "fontSize": FEAT_SIZE,
            "fontWeight": 600,
            "color": "#ffffff",
            "maxChars": FEAT_MAX_CHARS,
        })

    # CTA position: after last feature + gap
    cta_y = feat_start_y + num_feats * FEAT_STEP + 15

    # Domain text at bottom of dark panel
    feature_layers.append({
        "content": "THETACKLEROOM.COM",
        "x": PANEL_X + PANEL_W // 2,
        "y": 1055,
        "fontSize": 12,
        "fontWeight": 600,
        "color": "rgba(255,255,255,0.25)",
        "maxChars": 40,
        "align": "center",
    })

    # CTA button — centered in dark panel with 60px side padding
    cta_w = PANEL_W - 120  # 520
    cta_rect_x = PANEL_X + 60  # 500

    return {
        "_comment": f"=== {handle} | Variant {variant['id']} ===",
        "output": f"{OUT}/{handle}-{variant['id']}.jpg",
        "backgroundPath": bg,
        "productImage": {
            "path": image_path,
            "x": 20,
            "y": SPLIT_Y + 20,
            "width": PRODUCT_W - 40,
            "height": 1080 - SPLIT_Y - 40,
            "padding": 20,
        },
        "text": {
            "headline": headline.upper(),
            "subhead": "",
            "cta": variant.get("cta", "SHOP NOW"),
            "footer": "",
        },
        "overlay": {
            "leftColor": "5,20,35", "midColor": "5,20,35", "rightColor": "5,20,35",
            "leftOpacity": 0.25, "midOpacity": 0.2, "rightOpacity": 0.25,
            "vignetteBottom": 0.3,
        },
        "typography": {
            "headlineFontFamily": "Montserrat, Arial, sans-serif",
            "bodyFontFamily": "Source Sans Pro, Arial, sans-serif",
            "headlineSize": 64,
            "subheadSize": 1,
            "headlineWeight": 800,
            "subheadWeight": 400,
            "ctaSize": 20,
            "ctaWeight": 700,
            "footerSize": 1,
            "footerTracking": 4,
        },
        "layout": {
            "personality": "centered-hero",
            "align": "center",
            "leftX": 540,
            "headlineY": 280,
            "subheadY": SPLIT_Y - 10,  # invisible but QA-safe position
            "maxHeadlineChars": 22,
            "maxSubheadChars": 1,
            "ctaWidth": cta_w,
            "ctaHeight": 50,
            "ctaGroup": {
                "relativeTo": "canvas",
                "anchorX": "left",
                "anchorY": "top",
                "offsetX": cta_rect_x,
                "offsetY": cta_y,
                "textAlign": "center",
            },
            "footerY": 1055,
        },
        "shapes": [
            # White product area (left bottom)
            {
                "type": "rectangle",
                "x": 0, "y": SPLIT_Y,
                "width": PRODUCT_W, "height": 1080 - SPLIT_Y,
                "fill": "rgba(255,255,255,0.95)",
            },
            # Dark feature panel (right bottom)
            {
                "type": "rectangle",
                "x": PANEL_X, "y": SPLIT_Y,
                "width": PANEL_W, "height": 1080 - SPLIT_Y,
                "fill": "rgba(30,30,30,0.92)",
            },
        ],
        "textLayers": feature_layers,
    }


def build_variants(product, spec):
    """Generate 3 variant configs for a product."""
    title = short_title(product["title"])
    features = extract_features(spec)
    bodies = extract_feature_bodies(spec)
    specs_list = extract_specs_from_body(spec)
    mf = spec.get("metafields", {})
    value_heading = mf.get("value_story_heading", "")

    # Pad features to at least 3
    while len(features) < 3:
        features.append("Premium Quality")
    while len(bodies) < 3:
        bodies.append("Built for serious anglers")
    # If no real specs, fall back to feature titles
    if not specs_list:
        specs_list = list(features)
    while len(specs_list) < 3:
        specs_list.append(f"By {product.get('vendor', 'Epic Fishing Co.')}")

    variants = []

    # Variant A: Feature Card — value story headline + feature titles
    variants.append({
        "id": "a",
        "headline": value_heading if value_heading else title,
        "header": "FEATURES",
        "features": features[:4],
        "cta": "SHOP NOW",
    })

    # Variant B: Problem-Solution — question headline + short benefit clauses
    variants.append({
        "id": "b",
        "headline": f"Why {title}?",
        "header": "WHY THIS ONE",
        "features": bodies[:4],
        "cta": "SHOP NOW",
    })

    # Variant C: Specs — product name headline + spec bullets
    variants.append({
        "id": "c",
        "headline": title,
        "header": "THE SPECS",
        "features": specs_list[:4],
        "cta": "GET IT NOW",
    })

    # Fix variant B CTA — use actual price
    price_min = mf.get("price_min", "")
    if not price_min:
        try:
            brief = json.load(open(os.path.join(BRIEF_DIR, spec["product_handle"] + "-research-brief.json")))
            price_min = brief.get("price_range", {}).get("min", "")
        except:
            pass
    if price_min:
        variants[1]["cta"] = f"FROM ${price_min}"

    return variants


def main():
    os.makedirs(OUT, exist_ok=True)

    products = load_top_products(50)
    specs_index = load_content_specs()
    all_images = find_product_images()

    config = {
        "defaults": {
            "preset": "social-square",
            "template": "banner",
            "theme": {
                "headlineColor": "#FFFFFF",
                "subheadColor": "#e4e4e7",
                "footerColor": "rgba(255,255,255,0.01)",
                "ctaTextColor": "#FFFFFF",
                "ctaFill": "rgba(232,93,58,0.92)",
                "ctaStroke": "rgba(255,160,120,0.35)",
            },
        },
        "renders": [],
    }

    matched_products = []
    for p in products:
        pid = int(p["product_id"])
        spec = specs_index.get(pid)
        if not spec:
            continue
        img = match_image(p["title"], all_images)
        if not img:
            continue

        variants = build_variants(p, spec)
        bg_idx = len(matched_products)

        for v in variants:
            config["renders"].append(build_render(p, spec, img, v, bg_idx))

        matched_products.append(p["title"])

    out_path = "/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/configs/meta-explainer.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Products matched: {len(matched_products)}")
    print(f"Renders generated: {len(config['renders'])} ({len(matched_products)} products × 3 variants)")
    print(f"Config: {out_path}")


if __name__ == "__main__":
    main()
