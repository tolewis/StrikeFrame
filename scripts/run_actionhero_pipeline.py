#!/usr/bin/env python3
"""Run the ActionHero production lane.

Flow
1. Generate a 25-variant ActionHero batch manifest
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
OUTPUT_DIR = ROOT / 'output' / 'meta-v2' / 'actionhero-batch-v1'
SUMMARY_JSON = OUTPUT_DIR / 'actionhero-pipeline-summary.json'
SUMMARY_MD = OUTPUT_DIR / 'actionhero-pipeline-summary.md'
SHEET = OUTPUT_DIR / 'actionhero-review-sheet.jpg'


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or f'Command failed: {cmd}')
    return result


def load_batch(path: Path):
    return json.loads(path.read_text())


def render_sheet(ids):
    if not ids or not shutil.which('convert') or not shutil.which('montage'):
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
    cols = 4
    rows = (len(staged) + cols - 1) // cols
    subprocess.run(['montage', *staged, '-tile', f'{cols}x{rows}', '-geometry', '270x285+10+10', '-background', '#0f0f0f', str(SHEET)], check=True)
    return SHEET


def main():
    argparse.ArgumentParser().parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run([sys.executable, 'scripts/gen_actionhero_batch.py'])
    run(['node', 'scripts/render.js', 'configs/actionhero-batch-v1.json'])

    batch = load_batch(ROOT / 'configs' / 'actionhero-batch-v1.json')
    ids = [Path(item['output']).stem for item in batch['renders']]
    render_sheet(ids)

    summary = {
        'batch': 'actionhero-batch-v1',
        'render_count': len(ids),
        'variants': ids,
        'review_sheet': str(SHEET) if SHEET.exists() else None,
        'notes': [
            'ActionHero relies on batch review and finalist selection rather than coded rank ordering.',
            'Legacy review.json is still banner-centric and should not be treated as the final creative judge for this lane.',
            'Use the review sheet with AI or operator judgment to pick the strongest 5-10 variants.'
        ]
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))

    md = [
        '# ActionHero Pipeline Summary',
        '',
        f'- Batch: `{summary["batch"]}`',
        f'- Renders: **{summary["render_count"]}**',
        f'- Review sheet: `{summary["review_sheet"]}`' if summary['review_sheet'] else '- Review sheet not generated',
        '',
        '## Variants',
        '- ' + ', '.join(f'`{v}`' for v in ids),
        '',
        '## Notes',
    ]
    for note in summary['notes']:
        md.append(f'- {note}')
    SUMMARY_MD.write_text('\n'.join(md) + '\n')

    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
