#!/usr/bin/env python3
"""Run the ComparisonPanel production lane.

Flow
1. Generate a 25-variant ComparisonPanel batch manifest
2. Render the batch
3. Build a labeled contact sheet (5x5, 216x216 tiles, dark bg) for review
4. Write a summary for agent handoff
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
OUTPUT_DIR = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/comparisonpanel-batch-v1')
SUMMARY_JSON = OUTPUT_DIR / 'comparisonpanel-pipeline-summary.json'
SUMMARY_MD = OUTPUT_DIR / 'comparisonpanel-pipeline-summary.md'
SHEET = OUTPUT_DIR / 'comparisonpanel-review-sheet.jpg'


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or f'Command failed: {cmd}')
    return result


def load_batch(path: Path):
    return json.loads(path.read_text())


def render_sheet(ids):
    """Build a 5x5 contact sheet at 216x216 per tile, dark background."""
    if not ids:
        print('No renders found — skipping contact sheet.')
        return None
    if not shutil.which('convert') or not shutil.which('montage'):
        print('ImageMagick not found — skipping contact sheet.')
        return None

    stage_dir = OUTPUT_DIR / '.sheet-stage'
    stage_dir.mkdir(parents=True, exist_ok=True)
    staged = []

    for name in ids:
        src = OUTPUT_DIR / f'{name}.jpg'
        if not src.exists():
            print(f'  Missing: {name}.jpg — skipped from sheet.')
            continue
        staged_path = stage_dir / f'{name}.jpg'
        # Label each tile with its stem name
        subprocess.run([
            'convert', str(src),
            '-resize', '216x216^',
            '-gravity', 'center',
            '-extent', '216x216',
            '-gravity', 'south',
            '-background', '#111111',
            '-fill', 'white',
            '-splice', '0x30',
            '-pointsize', '14',
            '-annotate', '+0+8', name,
            str(staged_path)
        ], check=True)
        staged.append(str(staged_path))

    if not staged:
        print('No staged tiles — skipping contact sheet.')
        return None

    # 5x5 grid
    cols = 5
    rows = (len(staged) + cols - 1) // cols
    subprocess.run(
        ['montage', *staged,
         '-tile', f'{cols}x{rows}',
         '-geometry', '216x246+6+6',
         '-background', '#0f0f0f',
         str(SHEET)],
        check=True
    )
    shutil.rmtree(stage_dir, ignore_errors=True)
    return SHEET


def main():
    argparse.ArgumentParser(description='Run ComparisonPanel production lane.').parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print('Step 1 — generating batch manifest...')
    run([sys.executable, 'scripts/gen_comparisonpanel_batch.py'])

    print('Step 2 — rendering batch...')
    run(['node', 'scripts/render.js', 'configs/comparisonpanel-batch-v1.json'])

    batch = load_batch(ROOT / 'configs' / 'comparisonpanel-batch-v1.json')
    ids = [Path(item['output']).stem for item in batch['renders']]
    rendered = [i for i in ids if (OUTPUT_DIR / f'{i}.jpg').exists()]

    print(f'Step 3 — building contact sheet ({len(rendered)} tiles, 5x5, 216px)...')
    render_sheet(rendered)

    # Categorise by copy set (set 1–5)
    set_breakdown = {}
    for v in rendered:
        # stem: comparisonpanel-{set}-{n}
        parts = v.split('-')
        if len(parts) >= 3:
            set_key = f'set-{parts[1]}'
            set_breakdown.setdefault(set_key, []).append(v)

    summary = {
        'batch': 'comparisonpanel-batch-v1',
        'render_count': len(rendered),
        'expected_count': len(ids),
        'variants': rendered,
        'review_sheet': str(SHEET) if SHEET.exists() else None,
        'sets': set_breakdown,
        'notes': [
            'ComparisonPanel lane: 5 copy sets × 5 backgrounds = 25 renders.',
            'Template: banner | personality: centered-hero.',
            'All renders use hero images from hero-classification.json.',
            'comparisonTable.leftTextColor fixed at rgba(255,255,255,0.82) on all renders.',
            'Logo: corner-anchor top-left, 260×60px, clearSpace 15.',
            'Use the contact sheet to shortlist top 5-8 creatives for paid media.',
        ]
    }

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))

    md_lines = [
        '# ComparisonPanel Pipeline Summary',
        '',
        f'- Batch: `{summary["batch"]}`',
        f'- Renders: **{summary["render_count"]}** / {summary["expected_count"]} expected',
    ]
    if summary['review_sheet']:
        md_lines.append(f'- Review sheet: `{summary["review_sheet"]}`')
    else:
        md_lines.append('- Review sheet: not generated')
    md_lines += ['', '## Copy Set Breakdown']
    for s, variants in sorted(summary['sets'].items()):
        md_lines.append(f'- **{s}** ({len(variants)}): ' + ', '.join(f'`{v}`' for v in variants))
    md_lines += ['', '## Notes']
    for note in summary['notes']:
        md_lines.append(f'- {note}')

    SUMMARY_MD.write_text('\n'.join(md_lines) + '\n')

    print('\nStep 4 — done.')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
