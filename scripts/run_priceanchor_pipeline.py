#!/usr/bin/env python3
"""Run the PriceAnchor production lane.

Flow
1. Generate a 25-variant PriceAnchor batch manifest
2. Render the batch
3. Build a labeled contact sheet for AI/human shortlist review
4. Write a summary for agent handoff
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
OUTPUT_DIR = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/priceanchor-batch-v1')
SUMMARY_JSON = OUTPUT_DIR / 'priceanchor-pipeline-summary.json'
SUMMARY_MD = OUTPUT_DIR / 'priceanchor-pipeline-summary.md'
SHEET = OUTPUT_DIR / 'priceanchor-review-sheet.jpg'


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or f'Command failed: {cmd}')
    return result


def load_batch(path: Path):
    return json.loads(path.read_text())


def render_sheet(ids):
    if not ids or not shutil.which('convert') or not shutil.which('montage'):
        print('ImageMagick not found — skipping contact sheet.')
        return None
    stage_dir = OUTPUT_DIR / '.sheet-stage'
    stage_dir.mkdir(parents=True, exist_ok=True)
    staged = []
    for name in ids:
        src = OUTPUT_DIR / f'{name}.jpg'
        if not src.exists():
            continue
        staged_path = stage_dir / f'{name}.jpg'
        subprocess.run([
            'convert', str(src),
            '-gravity', 'north',
            '-background', '#111111',
            '-fill', 'white',
            '-splice', '0x60',
            '-pointsize', '28',
            '-annotate', '+0+10', name,
            str(staged_path)
        ], check=True)
        staged.append(str(staged_path))
    if not staged:
        return None
    cols = 5
    rows = (len(staged) + cols - 1) // cols
    subprocess.run(
        ['montage', *staged,
         '-tile', f'{cols}x{rows}',
         '-geometry', '270x285+10+10',
         '-background', '#0f0f0f',
         str(SHEET)],
        check=True
    )
    return SHEET


def main():
    argparse.ArgumentParser(description='Run PriceAnchor production lane.').parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print('Step 1 — generating batch manifest...')
    run([sys.executable, 'scripts/gen_priceanchor_batch.py'])

    print('Step 2 — rendering batch...')
    run(['node', 'scripts/render.js', 'configs/priceanchor-batch-v1.json'])

    batch = load_batch(ROOT / 'configs' / 'priceanchor-batch-v1.json')
    ids = [Path(item['output']).stem for item in batch['renders']]
    rendered = [i for i in ids if (OUTPUT_DIR / f'{i}.jpg').exists()]

    print(f'Step 3 — building contact sheet ({len(rendered)} tiles)...')
    render_sheet(rendered)

    summary = {
        'batch': 'priceanchor-batch-v1',
        'render_count': len(rendered),
        'expected_count': len(ids),
        'variants': rendered,
        'review_sheet': str(SHEET) if SHEET.exists() else None,
        'categories': {
            'dredges': [v for v in rendered if v.startswith('dredge-')],
            'belts': [v for v in rendered if v.startswith('belt-')],
            'lures': [v for v in rendered if v.startswith('lure-')],
            'planers': [v for v in rendered if v.startswith('planer-')],
        },
        'notes': [
            'PriceAnchor lane anchors on prominent price text (fontSize 148, fontWeight 900).',
            'Each render uses a hero image matched by category from hero-classification.json.',
            'Use the review sheet with AI or operator judgment to pick the strongest 5-10 variants per category.',
            'Finalist selection should prioritize price legibility, image-text contrast, and CTA clarity.',
        ]
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))

    md_lines = [
        '# PriceAnchor Pipeline Summary',
        '',
        f'- Batch: `{summary["batch"]}`',
        f'- Renders: **{summary["render_count"]}** / {summary["expected_count"]} expected',
    ]
    if summary['review_sheet']:
        md_lines.append(f'- Review sheet: `{summary["review_sheet"]}`')
    else:
        md_lines.append('- Review sheet: not generated')
    md_lines += [
        '',
        '## Category Breakdown',
    ]
    for cat, variants in summary['categories'].items():
        md_lines.append(f'- **{cat}** ({len(variants)}): ' + ', '.join(f'`{v}`' for v in variants))
    md_lines += [
        '',
        '## Notes',
    ]
    for note in summary['notes']:
        md_lines.append(f'- {note}')
    SUMMARY_MD.write_text('\n'.join(md_lines) + '\n')

    print('\nStep 4 — done.')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
