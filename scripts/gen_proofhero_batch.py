#!/usr/bin/env python3
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
TMP_ROOT = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/proofhero-batch-v1')
BASE = ROOT / 'configs' / 'proofhero-canonical-v1.json'
OUT = ROOT / 'configs' / 'proofhero-batch-v1.json'

QUOTES = [
    'When the fish is bigger than you, this is what you want on.',
    'Forty minutes on a blue marlin and the belt never shifted.',
    'Charter captains put these on the rail every morning.',
    'Built for the long fight, not the first five minutes.',
    'If the gimbal moves, everything else gets harder.'
]

REVIEWS = [
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/review-proof/tier2-polish/Review08.png',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/review-proof/tier2-polish/Review11.png',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/review-proof/tier2-polish/RReview05.1.png'
]

PRODUCTS = [
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/belts/tier4-marginal/media-renderer-assets__product-photos__seamount-belt-person.jpg',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/belts/tier1-ready/media-renderer-assets__product-photos__seamount-gimbal.jpg'
]

QUOTE_SIZES = [62, 64, 66, 68, 70]
QUOTE_WIDTHS = [720, 760, 800, 840, 880]
PRODUCT_WIDTHS = [180, 200, 220, 240, 260]
REVIEW_HEIGHTS = [180, 195, 210, 225, 240]

# Structural layout variants — cycle through for real layout diversity
LAYOUT_VARIANTS = ['quote-dominant', 'review-dominant', 'balanced']

base = json.loads(BASE.read_text())
defaults = deepcopy(base)
defaults['output'] = None
renders = []

TMP_ROOT.mkdir(parents=True, exist_ok=True)

for i in range(25):
    cfg = {}
    cfg['output'] = str(TMP_ROOT / f'proofhero-{i+1:02d}.jpg')
    cfg['proofHero'] = deepcopy(defaults['proofHero'])
    cfg['proofHero']['content']['quote'] = QUOTES[i % len(QUOTES)]
    cfg['proofHero']['assets']['reviewPath'] = REVIEWS[i % len(REVIEWS)]
    cfg['proofHero']['assets']['productPath'] = PRODUCTS[(i // len(REVIEWS)) % len(PRODUCTS)]
    cfg['proofHero']['quoteSize'] = QUOTE_SIZES[i % len(QUOTE_SIZES)]
    cfg['proofHero']['maxQuoteWidth'] = QUOTE_WIDTHS[(i // len(QUOTE_SIZES)) % len(QUOTE_WIDTHS)]
    cfg['proofHero']['reviewHeight'] = REVIEW_HEIGHTS[i % len(REVIEW_HEIGHTS)]
    cfg['proofHero']['productWidth'] = PRODUCT_WIDTHS[(i // len(REVIEW_HEIGHTS)) % len(PRODUCT_WIDTHS)]
    cfg['proofHero']['productHeight'] = cfg['proofHero']['productWidth']
    cfg['proofHero']['productY'] = 720 if cfg['proofHero']['reviewHeight'] <= 210 else 740
    cfg['proofHero'].setdefault('cta', {})
    cfg['proofHero']['cta']['width'] = 400 if i % 2 == 0 else 430
    # Structural variant — cycle through layout modes for diversity
    cfg['proofHero']['variant'] = LAYOUT_VARIANTS[i % len(LAYOUT_VARIANTS)]
    renders.append(cfg)

batch = {
    'defaults': defaults,
    'renders': renders
}
OUT.write_text(json.dumps(batch, indent=2))
print(OUT)
