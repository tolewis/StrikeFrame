#!/usr/bin/env python3
"""Generate a 25-variant ComparisonPanel batch config.

Structure: 5 copy sets × 5 renders each = 25 total.
For each copy set, vary the background from the hero image list.
Hero images are cycled across all 25 renders so all 6 images appear.

v2: Cycles through primitive variant modes (standard, hero-right,
compact, split-weight) for structural layout diversity across renders.
"""

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
TMP_ROOT = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/comparisonpanel-batch-v1')
BASE = ROOT / 'configs' / 'comparisonpanel-canonical-v3.json'
COPY_SETS = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/comparisonpanel-copy-sets-v1.json')
HERO_CLASS = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/hero-classification.json')
OUT = ROOT / 'configs' / 'comparisonpanel-batch-v1.json'

# ---------------------------------------------------------------------------
# Load source data
# ---------------------------------------------------------------------------
base = json.loads(BASE.read_text())
copy_sets = json.loads(COPY_SETS.read_text())['sets']
hero_data = json.loads(HERO_CLASS.read_text())['hero']

# Deduplicate hero images preserving order
seen = set()
HERO_IMAGES = []
for h in hero_data:
    if h['path'] not in seen:
        seen.add(h['path'])
        HERO_IMAGES.append(h['path'])

# 6 unique hero images available — cycle across 25 renders
# Each copy set gets 5 background images (indices 0-4, shifted by set index)
# This spreads all 6 images across the 25 renders

print(f'Hero images available: {len(HERO_IMAGES)}')
print(f'Copy sets: {len(copy_sets)}')

# ---------------------------------------------------------------------------
# Overlay variation for visual diversity across 5 renders per set
# ---------------------------------------------------------------------------
OVERLAY_VARIANTS = [
    {'leftOpacity': 0.82, 'midOpacity': 0.50, 'rightOpacity': 0.82, 'vignetteBottom': 0.20},
    {'leftOpacity': 0.78, 'midOpacity': 0.44, 'rightOpacity': 0.80, 'vignetteBottom': 0.22},
    {'leftOpacity': 0.85, 'midOpacity': 0.55, 'rightOpacity': 0.85, 'vignetteBottom': 0.18},
    {'leftOpacity': 0.80, 'midOpacity': 0.48, 'rightOpacity': 0.82, 'vignetteBottom': 0.24},
    {'leftOpacity': 0.76, 'midOpacity': 0.52, 'rightOpacity': 0.78, 'vignetteBottom': 0.20},
]

# Structural layout variants — cycle through for real layout diversity
LAYOUT_VARIANTS = ['standard', 'hero-right', 'compact', 'split-weight']

# ---------------------------------------------------------------------------
# Load canonical render as template
# ---------------------------------------------------------------------------
TMP_ROOT.mkdir(parents=True, exist_ok=True)

canonical_render = deepcopy(base['renders'][0])
base_defaults = deepcopy(base['defaults'])

renders = []

for set_idx, cs in enumerate(copy_sets):
    for n in range(5):
        # Global render index: 0-24
        global_idx = set_idx * 5 + n

        # Cycle hero images across all 25 renders
        bg = HERO_IMAGES[global_idx % len(HERO_IMAGES)]

        overlay_v = OVERLAY_VARIANTS[n]

        cfg = {}

        # Background
        cfg['backgroundPath'] = bg
        cfg['backgroundPosition'] = 'attention'

        # Output path: comparisonpanel-{set}-{n:02d}.jpg  (set is 1-indexed)
        cfg['output'] = str(TMP_ROOT / f'comparisonpanel-{set_idx+1:02d}-{n+1:02d}.jpg')

        # Logo: corner-anchor, top-left, width 260, height 60, clearSpace 15
        cfg['logoPath'] = canonical_render['logoPath']
        cfg['logoMode'] = canonical_render['logoMode']
        cfg['logo'] = {
            'enabled': True,
            'placement': 'corner-anchor',
            'corner': 'top-left',
            'width': 260,
            'height': 60,
            'clearSpace': 15,
            'x': 32,
            'y': 32,
            'opacity': 0.95,
        }

        # Text
        cfg['text'] = {
            'headline': cs['headline'],
            'subhead': '',
            'cta': cs['cta'],
            'footer': '',
        }

        # Overlay
        cfg['overlay'] = {
            'leftColor': '5,18,30',
            'midColor': '5,18,30',
            'rightColor': '5,18,30',
            'leftOpacity': overlay_v['leftOpacity'],
            'midOpacity': overlay_v['midOpacity'],
            'rightOpacity': overlay_v['rightOpacity'],
            'vignetteBottom': overlay_v['vignetteBottom'],
        }

        # Typography from canonical
        cfg['typography'] = deepcopy(canonical_render['typography'])

        # Layout from canonical
        cfg['layout'] = deepcopy(canonical_render['layout'])
        cfg['layout']['personality'] = 'centered-hero'

        # Comparison table — carry rows and headers from copy set
        cfg['comparisonTable'] = deepcopy(canonical_render['comparisonTable'])
        cfg['comparisonTable']['leftHeader'] = cs['leftHeader']
        cfg['comparisonTable']['rightHeader'] = cs['rightHeader']
        cfg['comparisonTable']['rows'] = deepcopy(cs['rows'])
        # Required: leftTextColor on all renders
        cfg['comparisonTable']['leftTextColor'] = 'rgba(255,255,255,0.82)'
        # Structural variant — cycle through layout modes for diversity
        cfg['comparisonTable']['variant'] = LAYOUT_VARIANTS[global_idx % len(LAYOUT_VARIANTS)]

        renders.append(cfg)

# ---------------------------------------------------------------------------
# Write batch config
# ---------------------------------------------------------------------------
batch = {
    'defaults': deepcopy(base_defaults),
    'renders': renders,
}

OUT.write_text(json.dumps(batch, indent=2))
print(f'Written {len(renders)} renders → {OUT}')

# Print image distribution summary
print('\nBackground image distribution across 25 renders:')
img_counts = {}
for r in renders:
    key = Path(r['backgroundPath']).name
    img_counts[key] = img_counts.get(key, 0) + 1
for img, count in sorted(img_counts.items()):
    print(f'  {img}: {count}x')
