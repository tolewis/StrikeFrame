#!/usr/bin/env python3
"""Generate a 25-variant PriceAnchor batch config.

Categories:
  dredges × 7
  belts   × 6
  lures   × 6
  planers × 6

Images: ONLY hero images from hero-classification.json (matched by category).
Each render has: headline (2-line), price textLayer, description line, SAVE badge, CTA.
"""

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
TMP_ROOT = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-batch-v1')
BASE = ROOT / 'configs' / 'priceanchor-canonical-v4.json'
COPY_SETS = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-copy-sets-v1.json')
HERO_CLASS = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/hero-classification.json')
OUT = ROOT / 'configs' / 'priceanchor-batch-v1.json'

# ---------------------------------------------------------------------------
# Load source data
# ---------------------------------------------------------------------------
base = json.loads(BASE.read_text())
copy_sets = json.loads(COPY_SETS.read_text())['categories']
hero_data = json.loads(HERO_CLASS.read_text())['hero']

# Build hero image pools by category
# Mapping from copy-set key to hero category tags
CATEGORY_IMAGE_MAP = {
    'dredge_systems': ['dredges'],
    'fighting_belt_kits': ['belts'],
    'wahoo_lure_kits': ['lures'],
    'planer_bridle_kits': ['planers', 'dredges'],  # planers share offshore images
}

hero_pools = {}
for cat_key, tags in CATEGORY_IMAGE_MAP.items():
    pool = [h['path'] for h in hero_data if h['category'] in tags]
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for p in pool:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    hero_pools[cat_key] = deduped

# Description lines per category (specific gear detail, 1 line each)
DESCRIPTIONS = {
    'dredge_systems': [
        '130-squid spread. 400lb mono. Built for billfish.',
        '8-arm spreader. 80-squid teaser. Heavy-duty swivels.',
        '6-arm rig, 60-squid spread. Ready to deploy.',
        'Double-bar dredge, 100 squids. Tournament-proven.',
        '400lb mono. Stainless spreader bar. Blue-water ready.',
        'Full offshore teaser. Squid & bird combo included.',
        '10-arm dredge, 120 squids. Rigged and ready.',
    ],
    'fighting_belt_kits': [
        'Padded gimbal bucket. 60°-gimbal insert. Full harness ready.',
        'Kidney belt, gimbal, and shoulder harness kit.',
        'Stand-up pad, adjustable harness, heavy-duty buckle.',
        'Deluxe fighting belt with integrated rod holder.',
        'Full stand-up kit. Fits 30-50W reels. Ships complete.',
        'Neoprene belt, stainless gimbal. Big-game proven.',
    ],
    'wahoo_lure_kits': [
        'High-speed heads, 12\"-14\". Wire-rigged and ready.',
        '6 colors: pink, blue, white, purple, green, black.',
        'Pre-rigged #9 Mustad hooks, 200lb Malin wire.',
        '18"-24" trolling lures. Wahoo-proven patterns.',
        '6 wire-rigged runners. 12-24 kts tested.',
        '400lb wire leaders. Speed-tested at 15+ kts.',
    ],
    'planer_bridle_kits': [
        'Hand-tied bridles. #2 and #4 planer included.',
        'Stainless bridle clips. Fits #2, #3, #4 planers.',
        'Complete bridle set. 30-50lb mono. Kink-resistant.',
        'Pre-tied bridles. Planers, clips, and leader included.',
        'Mono bridle loops, swivel snap, 4-size planer kit.',
        'Ready-tied bridles. 20-50lb leader. Clip-and-go.',
    ],
}

# Slight overlay/vignette variation for visual diversity
VIGNETTES = [0.72, 0.80, 0.88, 0.92, 0.96, 0.84, 0.76]
MID_OPACITIES = [0.16, 0.20, 0.14, 0.18, 0.12, 0.22, 0.16]

# ---------------------------------------------------------------------------
# Build per-category renders
# ---------------------------------------------------------------------------
TMP_ROOT.mkdir(parents=True, exist_ok=True)

PLAN = [
    ('dredge_systems', 7, 'dredge'),
    ('fighting_belt_kits', 6, 'belt'),
    ('wahoo_lure_kits', 6, 'lure'),
    ('planer_bridle_kits', 6, 'planer'),
]

renders = []

for cat_key, count, slug in PLAN:
    cs = copy_sets[cat_key]
    headlines = cs['headlines']
    prices = cs['price_points']
    badges = cs['badges']
    ctas = cs['ctas']
    descs = DESCRIPTIONS[cat_key]
    images = hero_pools[cat_key]

    for n in range(count):
        idx = n  # primary index within this category
        hl = headlines[n % len(headlines)]
        price = prices[n % len(prices)]
        badge = badges[n % len(badges)]
        cta = ctas[n % len(ctas)]
        desc = descs[n % len(descs)]
        bg = images[n % len(images)]
        vignette = VIGNETTES[n % len(VIGNETTES)]
        mid_op = MID_OPACITIES[n % len(MID_OPACITIES)]

        # Compose headline: line1 + newline + line2
        headline_text = f'{hl["line1"]}\n{hl["line2"]}'

        cfg = {}
        cfg['backgroundPath'] = bg
        cfg['backgroundPosition'] = 'center'
        cfg['output'] = str(TMP_ROOT / f'{slug}-{len(renders)+1:02d}.jpg')
        cfg['logoMode'] = 'white-card-landscape'
        cfg['logo'] = {
            'placement': 'corner-anchor',
            'corner': 'top-left',
            'width': 260,
            'height': 60,
            'clearSpace': 15
        }
        cfg['text'] = {
            'headline': '',
            'subhead': '',
            'cta': cta['text'],
            'footer': ''
        }
        cfg['overlay'] = {
            'leftColor': '4,14,28',
            'midColor': '4,14,28',
            'rightColor': '4,14,28',
            'leftOpacity': 0.0,
            'midOpacity': mid_op,
            'rightOpacity': 0.0,
            'vignetteBottom': vignette
        }
        cfg['theme'] = deepcopy(base['theme'])
        cfg['typography'] = deepcopy(base['typography'])
        cfg['layout'] = deepcopy(base['layout'])
        cfg['review'] = {'enforcePanelFit': False}

        # CTA layout
        cfg['layout']['ctaRectX'] = 60
        cfg['layout']['ctaRectY'] = 965
        cfg['layout']['ctaWidth'] = 340 + (n % 4) * 20
        cfg['layout']['ctaHeight'] = 56
        cfg['layout']['ctaRadius'] = 12
        cfg['layout']['ctaX'] = 60 + cfg['layout']['ctaWidth'] // 2
        cfg['layout']['ctaY'] = 965 + 36  # vertically centered in CTA rect

        # Text layers: headline, price, description
        cfg['textLayers'] = [
            {
                'content': headline_text,
                'x': 60,
                'y': 600,
                'fontSize': 36,
                'fontFamily': 'Montserrat, Arial, sans-serif',
                'fontWeight': 700,
                'color': 'rgba(255,255,255,0.80)',
                'letterSpacing': 2
            },
            {
                'content': f'${price}',
                'x': 60,
                'y': 745,
                'fontSize': 148,
                'fontFamily': 'Montserrat, Arial, sans-serif',
                'fontWeight': 900,
                'color': '#FFFFFF',
                'shadow': {
                    'dx': 0,
                    'dy': 4,
                    'color': 'rgba(0,0,0,0.55)'
                }
            },
            {
                'content': desc,
                'x': 60,
                'y': 880,
                'fontSize': 28,
                'fontFamily': 'Montserrat, Arial, sans-serif',
                'fontWeight': 600,
                'color': 'rgba(255,255,255,0.90)'
            }
        ]

        # SAVE badge
        badge_text = badge['text']
        badge_width = 130 + len(badge_text) * 6
        cfg['badges'] = [
            {
                'text': badge_text,
                'x': 60,
                'y': 540,
                'fill': 'rgba(232,93,58,0.96)',
                'textColor': '#FFFFFF',
                'fontSize': 22,
                'width': badge_width,
                'height': 46,
                'radius': 8,
                'fontFamily': 'Montserrat, Arial, sans-serif',
                'fontWeight': 800
            }
        ]

        renders.append(cfg)

# ---------------------------------------------------------------------------
# Build defaults from canonical base
# ---------------------------------------------------------------------------
defaults = deepcopy(base)
defaults['output'] = None

batch = {
    'defaults': defaults,
    'renders': renders,
}
OUT.write_text(json.dumps(batch, indent=2))
print(f'Written {len(renders)} renders → {OUT}')
