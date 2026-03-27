#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter,defaultdict

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP/output/meta-v2/proofhero-batch-v1')
canvas_area = 1080*1080
issues = Counter()
examples = defaultdict(list)

for layout_path in sorted(ROOT.glob('*.layout.json')):
    data = json.loads(layout_path.read_text())
    elems = {e['id']: e['rect'] for e in data.get('elements', [])}
    quote = elems.get('proofHero.quote')
    stars = elems.get('proofHero.stars')
    review = elems.get('proofHero.review')
    product = elems.get('proofHero.product')
    cta = elems.get('proofHero.cta')
    if not all([quote, stars, review, product, cta]):
        issues['missing_elements'] += 1
        examples['missing_elements'].append(layout_path.name)
        continue
    quote_lines_est = round(quote['height'] / 74)
    if quote_lines_est > 3:
        issues['quote_over_3_lines'] += 1; examples['quote_over_3_lines'].append(layout_path.name)
    if quote['width'] < 650:
        issues['quote_too_narrow'] += 1; examples['quote_too_narrow'].append(layout_path.name)
    if stars['top'] - quote['bottom'] < 8:
        issues['quote_stars_too_tight'] += 1; examples['quote_stars_too_tight'].append(layout_path.name)
    if review['top'] - stars['bottom'] < 24:
        issues['stars_review_too_tight'] += 1; examples['stars_review_too_tight'].append(layout_path.name)
    if cta['top'] - review['bottom'] < 140:
        issues['review_cta_too_tight'] += 1; examples['review_cta_too_tight'].append(layout_path.name)
    if product['left'] < review['right'] - 120 and product['top'] < review['bottom'] + 40:
        issues['product_crowds_review'] += 1; examples['product_crowds_review'].append(layout_path.name)
    if product['area'] / canvas_area > 0.06:
        issues['product_too_large'] += 1; examples['product_too_large'].append(layout_path.name)
    safe = data.get('constraintPolicy', {}).get('geometry', {}).get('minSafeZone', 40)
    if cta['bottom'] > (1080 - safe) or cta['left'] < safe:
        issues['cta_safe_zone_violation'] += 1; examples['cta_safe_zone_violation'].append(layout_path.name)

summary = {
    'count': len(list(ROOT.glob('*.layout.json'))),
    'issues': issues,
    'examples': {k:v[:5] for k,v in examples.items()}
}
print(json.dumps(summary, indent=2, default=lambda x: dict(x)))
(Path(ROOT) / 'proofhero-batch-analysis.json').write_text(json.dumps(summary, indent=2, default=lambda x: dict(x)))
