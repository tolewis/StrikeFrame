"""Shared TackleRoom brand constants for all StrikeFrame batch generators."""

BRAND = {
    "name": "THETACKLEROOM.COM",
    "accent": "rgba(232,93,58,0.92)",
    "accent_stroke": "rgba(255,160,120,0.35)",
    "headline_font": "Montserrat, Arial, sans-serif",
    "body_font": "Source Sans Pro, Arial, sans-serif",
    "serif_font": "Georgia, 'Times New Roman', serif",
    "headline_color": "#FFFFFF",
    "subhead_color": "#e4e4e7",
    "footer_color": "rgba(255,255,255,0.35)",
    "cta_text_color": "#FFFFFF",
    "dark_panel": "rgba(30,30,30,0.92)",
    "light_panel": "rgba(255,255,255,0.95)",
}

THEME_DEFAULT = {
    "headlineColor": BRAND["headline_color"],
    "subheadColor": BRAND["subhead_color"],
    "footerColor": BRAND["footer_color"],
    "ctaTextColor": BRAND["cta_text_color"],
    "ctaFill": BRAND["accent"],
    "ctaStroke": BRAND["accent_stroke"],
    "gradientStart": "#0b2a40",
    "gradientEnd": "#1f6b8f",
}

BADGES = {
    "captains_pick": {"text": "CAPTAIN'S PICK", "fill": "rgba(232,93,58,0.92)", "textColor": "#ffffff"},
    "best_seller": {"text": "BEST SELLER", "fill": "rgba(232,93,58,0.92)", "textColor": "#ffffff"},
    "complete_kit": {"text": "COMPLETE KIT", "fill": "rgba(40,120,80,0.9)", "textColor": "#ffffff"},
    "new": {"text": "NEW", "fill": "rgba(59,130,246,0.9)", "textColor": "#ffffff"},
    "tournament_proven": {"text": "TOURNAMENT PROVEN", "fill": "rgba(232,93,58,0.92)", "textColor": "#ffffff"},
    "free_shipping": {"text": "FREE SHIPPING OVER $99", "fill": "rgba(255,255,255,0.16)", "textColor": "#ffffff"},
}

ICON_MAP = {
    "durability": "shield",
    "saltwater": "wave",
    "offshore": "anchor",
    "precision": "target",
    "performance": "gear",
    "verified": "check",
    "species": "fish",
    "speed": "arrow",
    "quality": "shield",
    "strength": "shield",
    "tested": "check",
    "complete": "check",
    "ready": "check",
    "tournament": "target",
    "deep": "anchor",
    "trolling": "wave",
    "rigging": "gear",
    "leader": "arrow",
}

PROOF_TYPES = {
    "captain": "Captain-verified",
    "tournament": "Tournament-tested",
    "reorder": "High reorder rate",
    "specs": "Full specs verified",
    "kit_complete": "Complete system, nothing missing",
}

CATEGORY_VOICE = {
    "planers": {"tone": "technical-practical", "proof_style": "kit_complete", "icon_default": "gear"},
    "dredges": {"tone": "performance-outcome", "proof_style": "captain", "icon_default": "anchor"},
    "daisy_chains": {"tone": "performance-outcome", "proof_style": "captain", "icon_default": "fish"},
    "lures": {"tone": "confidence-trust", "proof_style": "reorder", "icon_default": "fish"},
    "line_leader": {"tone": "technical-precision", "proof_style": "specs", "icon_default": "arrow"},
    "leads": {"tone": "technical-precision", "proof_style": "specs", "icon_default": "anchor"},
    "belts": {"tone": "comfort-endurance", "proof_style": "captain", "icon_default": "shield"},
    "kits": {"tone": "convenience-complete", "proof_style": "kit_complete", "icon_default": "check"},
    "camera": {"tone": "insight-advantage", "proof_style": "captain", "icon_default": "target"},
}

OVERLAY_OCEAN = {
    "leftColor": "5,20,35", "midColor": "5,20,35", "rightColor": "5,20,35",
    "leftOpacity": 0.25, "midOpacity": 0.2, "rightOpacity": 0.25,
    "vignetteBottom": 0.3,
}

OVERLAY_DARK = {
    "leftColor": "10,10,10", "midColor": "10,10,10", "rightColor": "10,10,10",
    "leftOpacity": 0.7, "midOpacity": 0.7, "rightOpacity": 0.7,
    "vignetteBottom": 0.2,
}

OVERLAY_EDITORIAL = {
    "leftColor": "8,30,50", "midColor": "8,30,50", "rightColor": "8,30,50",
    "leftOpacity": 0.55, "midOpacity": 0.35, "rightOpacity": 0.15,
    "vignetteBottom": 0.35,
}

STOCK_DIR = "/home/tlewis/Dropbox/Tim/TackleRoom/Creative/Assets/AdobeStock"

OCEAN_BACKGROUNDS = [
    f"{STOCK_DIR}/AdobeStock_372953083.jpeg",
    f"{STOCK_DIR}/AdobeStock_133588506.jpeg",
    f"{STOCK_DIR}/AdobeStock_175678582.jpeg",
    f"{STOCK_DIR}/AdobeStock_219637627.jpeg",
    f"{STOCK_DIR}/AdobeStock_331722964.jpeg",
    f"{STOCK_DIR}/AdobeStock_284446852.jpeg",
    f"{STOCK_DIR}/AdobeStock_229283027.jpeg",
    f"{STOCK_DIR}/AdobeStock_337378282.jpeg",
    f"{STOCK_DIR}/AdobeStock_345435684.jpeg",
    f"{STOCK_DIR}/AdobeStock_991789270.jpeg",
]


def guess_icon(feature_text):
    """Map a feature string to an icon glyph using keyword matching."""
    text = feature_text.lower()
    for keyword, icon in ICON_MAP.items():
        if keyword in text:
            return icon
    return "check"


def category_for_title(title):
    """Guess product category from title keywords."""
    t = title.lower()
    if "planer" in t or "bridle" in t:
        return "planers"
    if "dredge" in t:
        return "dredges"
    if "daisy" in t or "chain" in t or "teaser" in t or "squid" in t:
        return "daisy_chains"
    if "lure" in t or "bait" in t:
        return "lures"
    if "leader" in t or "line" in t or "braid" in t or "mono" in t or "hollow" in t:
        return "line_leader"
    if "lead" in t or "sinker" in t or "weight" in t:
        return "leads"
    if "belt" in t or "harness" in t:
        return "belts"
    if "kit" in t or "bundle" in t or "package" in t or "combo" in t:
        return "kits"
    if "camera" in t or "strike" in t:
        return "camera"
    return "kits"


def wrap_text(text, max_chars):
    """Mirror render.js wrapText logic."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        nxt = f"{current} {word}" if current else word
        if len(nxt) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = nxt
    if current:
        lines.append(current)
    return lines


def est_text_width(text, font_size):
    """Estimate pixel width of text. ~0.58 average char width ratio for sans-serif."""
    return round(len(text) * font_size * 0.58)
