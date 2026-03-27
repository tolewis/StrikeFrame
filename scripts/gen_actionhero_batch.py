#!/usr/bin/env python3
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
BASE = ROOT / 'configs' / 'meta-v2-action-hero-v4.json'
OUT = ROOT / 'configs' / 'actionhero-batch-v1.json'

HEADLINES = [
    'Wahoo Don\'t Wait\nFor Slow Gear',
    'Built To Run\nWhen Wahoo Are On',
    'Fast Gear For\nFast Fish',
    'Rig For Wahoo\nNot Wishful Thinking',
    'When The Bite\nTurns Violent, Go Ready'
]
CTA_TEXTS = [
    'SHOP WAHOO GEAR',
    'SHOP WAHOO LURES',
    'BUILD YOUR WAHOO SPREAD',
    'SHOP CABLE RIGS',
    'GET WAHOO READY'
]
BADGES = ['WAHOO SEASON', 'OFFSHORE READY', 'BUILT FOR SPEED', 'TOURNAMENT GEAR', 'CABLE RIGGED']
HEADLINE_SIZES = [72, 76, 78, 80, 84]
HEADLINE_YS = [780, 800, 820, 840, 860]
CTA_WIDTHS = [390, 420, 450, 480, 510]
CTA_YS = [930, 948, 966, 984, 1002]
VIGNETTES = [0.64, 0.72, 0.80, 0.88, 0.94]
MID_OPACITIES = [0.04, 0.08, 0.12, 0.16, 0.20]

base = json.loads(BASE.read_text())
defaults = deepcopy(base)
defaults['output'] = None
renders = []

for i in range(25):
    cfg = {}
    cfg['output'] = str(ROOT / 'output' / 'meta-v2' / 'actionhero-batch-v1' / f'actionhero-{i+1:02d}.jpg')
    cfg['text'] = deepcopy(defaults['text'])
    cfg['text']['headline'] = HEADLINES[i % len(HEADLINES)]
    cfg['text']['cta'] = CTA_TEXTS[(i // len(HEADLINES)) % len(CTA_TEXTS)]

    cfg['typography'] = deepcopy(defaults['typography'])
    cfg['typography']['headlineSize'] = HEADLINE_SIZES[i % len(HEADLINE_SIZES)]

    cfg['layout'] = deepcopy(defaults['layout'])
    cfg['layout']['headlineY'] = HEADLINE_YS[(i // len(CTA_TEXTS)) % len(HEADLINE_YS)]
    cfg['layout']['ctaWidth'] = CTA_WIDTHS[i % len(CTA_WIDTHS)]
    cfg['layout']['ctaRectY'] = CTA_YS[(i // len(HEADLINE_SIZES)) % len(CTA_YS)]
    cfg['layout']['ctaY'] = cfg['layout']['ctaRectY'] + 48
    cfg['layout']['ctaX'] = 60 + cfg['layout']['ctaWidth'] // 2

    cfg['overlay'] = deepcopy(defaults['overlay'])
    cfg['overlay']['vignetteBottom'] = VIGNETTES[(i // len(CTA_WIDTHS)) % len(VIGNETTES)]
    cfg['overlay']['midOpacity'] = MID_OPACITIES[i % len(MID_OPACITIES)]

    cfg['badges'] = deepcopy(defaults['badges'])
    cfg['badges'][0]['text'] = BADGES[i % len(BADGES)]
    cfg['badges'][0]['width'] = 200 + (i % 5) * 18
    cfg['badges'][0]['x'] = 1040 - cfg['badges'][0]['width']

    renders.append(cfg)

batch = {
    'defaults': defaults,
    'renders': renders,
}
OUT.write_text(json.dumps(batch, indent=2))
print(OUT)
