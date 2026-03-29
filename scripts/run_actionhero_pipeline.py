#!/usr/bin/env python3
"""Run the ActionHero production lane.

Flow
1. Generate a 25-variant ActionHero batch manifest
2. Render the batch
3. Run required prototype QC before building any human review sheet
4. Optionally run bulk/final Popeye review on the best survivors
5. Write a summary for agent handoff
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
OUTPUT_DIR = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/actionhero-batch-v1')
SUMMARY_JSON = OUTPUT_DIR / 'actionhero-pipeline-summary.json'
SUMMARY_MD = OUTPUT_DIR / 'actionhero-pipeline-summary.md'
SHEET = OUTPUT_DIR / 'actionhero-review-sheet.jpg'
BLOCKED_SHEET = OUTPUT_DIR / 'actionhero-blocked-sheet.jpg'
QC_JSON = OUTPUT_DIR / 'actionhero-prototype-qc.json'
BULK_QC_JSON = OUTPUT_DIR / 'actionhero-bulk-qc.json'


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or f'Command failed: {cmd}')
    return result


def load_batch(path: Path):
    return json.loads(path.read_text())


def render_sheet(ids, out_path, label='QC PASS'):
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
            '-annotate', '+0+10', f'{label} - {name}',
            str(staged_path)
        ], check=True)
        staged.append(str(staged_path))
    if not staged:
        return None
    cols = 4
    rows = (len(staged) + cols - 1) // cols
    subprocess.run(['montage', *staged, '-tile', f'{cols}x{rows}', '-geometry', '270x285+10+10', '-background', '#0f0f0f', str(out_path)], check=True)
    return out_path


def review_image(image_path: Path, *, backend: str, model: str | None, purpose: str, persona: str, timeout: int) -> dict | None:
    cmd = [
        sys.executable, 'scripts/vision_review.py', str(image_path),
        '--channel', 'paid-social',
        '--persona', persona,
        '--benchmark-role', 'actionHero',
        '--ad-type', 'action-led',
        '--description', 'ActionHero product and outcome ad for TackleRoom',
        '--backend', backend,
        '--purpose', purpose,
        '--timeout', str(timeout),
        '--write-report'
    ]
    if model:
        cmd.extend(['--model', model])
    result = run(cmd, check=False)
    if result.returncode not in {0, 1, 2}:
        return {'status': 'error', 'error': (result.stderr or result.stdout).strip()}
    try:
        payload = json.loads(result.stdout.strip())
    except Exception:
        return {'status': 'error', 'error': 'vision review returned non-json', 'raw': result.stdout[:500]}
    if isinstance(payload, dict) and payload.get('error'):
        payload['status'] = 'error'
    return payload


def prototype_qc(ids: list[str], args) -> tuple[list[dict], list[dict]]:
    rows = []
    approved = []
    for name in ids:
        review = review_image(
            OUTPUT_DIR / f'{name}.jpg',
            backend=args.prototype_backend,
            model=args.prototype_model,
            purpose='human-review',
            persona=args.persona,
            timeout=args.timeout,
        ) or {'status': 'error', 'error': 'unknown'}
        row = {
            'image': name,
            'verdict': review.get('verdict', 'error'),
            'overall_score': review.get('overall_score'),
            'backend': review.get('backend'),
            'model': review.get('model'),
            'report_path': review.get('report_path'),
            'summary': review.get('summary'),
            'error': review.get('error'),
        }
        rows.append(row)
        if review.get('verdict') == 'pass' and not review.get('error'):
            approved.append(review)
    rows.sort(key=lambda r: ((r.get('overall_score') or 0), r['image']), reverse=True)
    approved.sort(key=lambda r: ((r.get('overall_score') or 0), (r.get('channel_fit_score') or 0)), reverse=True)
    return rows, approved


def bulk_qc(reviews: list[dict], args) -> list[dict]:
    finalists = []
    for item in reviews[:args.bulk_top_k]:
        image_name = Path(item.get('source_image', '')).stem or item.get('image')
        review = review_image(
            OUTPUT_DIR / f'{image_name}.jpg',
            backend=args.bulk_backend,
            model=args.bulk_model,
            purpose='bulk',
            persona=args.persona,
            timeout=args.bulk_timeout,
        ) or {'status': 'error', 'error': 'unknown'}
        review['image'] = image_name
        finalists.append(review)
    finalists.sort(key=lambda r: ((r.get('overall_score') or 0), (r.get('channel_fit_score') or 0)), reverse=True)
    return finalists


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--persona', default='tim-operator')
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--prototype-backend', choices=['auto', 'openai', 'ollama'], default='auto')
    ap.add_argument('--prototype-model', default=None)
    ap.add_argument('--bulk-review', choices=['on', 'off'], default='off')
    ap.add_argument('--bulk-backend', choices=['auto', 'openai', 'ollama'], default='ollama')
    ap.add_argument('--bulk-model', default='qwen2.5vl:32b')
    ap.add_argument('--bulk-timeout', type=int, default=180)
    ap.add_argument('--bulk-top-k', type=int, default=5)
    args = ap.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in [SHEET, BLOCKED_SHEET, QC_JSON, BULK_QC_JSON]:
        stale.unlink(missing_ok=True)

    run([sys.executable, 'scripts/gen_actionhero_batch.py'])
    run(['node', 'scripts/render.js', 'configs/actionhero-batch-v1.json'])

    batch = load_batch(ROOT / 'configs' / 'actionhero-batch-v1.json')
    ids = [Path(item['output']).stem for item in batch['renders']]

    prototype_rows, approved_reviews = prototype_qc(ids, args)
    approved_ids = [Path(r['source_image']).stem for r in approved_reviews]
    blocked_ids = [row['image'] for row in prototype_rows if row['image'] not in approved_ids]
    QC_JSON.write_text(json.dumps({
        'stage': 'prototype-human-review-gate',
        'backend': args.prototype_backend,
        'model': args.prototype_model,
        'approved_for_human_review': approved_ids,
        'blocked': blocked_ids,
        'reviews': prototype_rows,
    }, indent=2))

    review_sheet = render_sheet(approved_ids, SHEET, 'QC PASS')
    blocked_sheet = render_sheet(blocked_ids, BLOCKED_SHEET, 'BLOCKED')

    bulk_reviews = []
    if args.bulk_review == 'on' and approved_reviews:
        bulk_reviews = bulk_qc(approved_reviews, args)
        BULK_QC_JSON.write_text(json.dumps({
            'stage': 'bulk-final-review',
            'backend': args.bulk_backend,
            'model': args.bulk_model,
            'top_k': args.bulk_top_k,
            'reviews': bulk_reviews,
        }, indent=2))

    ranked = bulk_reviews if bulk_reviews else approved_reviews

    summary = {
        'batch': 'actionhero-batch-v1',
        'render_count': len(ids),
        'prototype_qc_pass_count': len(approved_ids),
        'prototype_qc_blocked_count': len(blocked_ids),
        'prototype_qc_pass': approved_ids,
        'prototype_qc_blocked': blocked_ids,
        'review_sheet': str(review_sheet) if review_sheet else None,
        'blocked_sheet': str(blocked_sheet) if blocked_sheet else None,
        'prototype_qc_json': str(QC_JSON),
        'bulk_review_enabled': args.bulk_review == 'on',
        'bulk_qc_json': str(BULK_QC_JSON) if bulk_reviews else None,
        'top_k': ranked[:args.bulk_top_k],
        'notes': [
            'Human review sheet now contains only variants that passed prototype vision QC.',
            'Cloud reviewer is preferred for prototype iteration; Popeye is available for bulk/final review.',
            'Legacy review.json is still banner-centric and should not be treated as the final creative judge for this lane.'
        ]
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))

    md = [
        '# ActionHero Pipeline Summary',
        '',
        f'- Batch: `{summary["batch"]}`',
        f'- Renders: **{summary["render_count"]}**',
        f'- Prototype QC approved for human review: **{summary["prototype_qc_pass_count"]}**',
        f'- Prototype QC blocked: **{summary["prototype_qc_blocked_count"]}**',
        f'- Review sheet: `{summary["review_sheet"]}`' if summary['review_sheet'] else '- Review sheet not generated',
        f'- Blocked sheet: `{summary["blocked_sheet"]}`' if summary['blocked_sheet'] else '- Blocked sheet not generated',
        '',
        '## Human-review-safe variants',
        '- ' + (', '.join(f'`{v}`' for v in approved_ids) if approved_ids else 'None'),
        '',
        '## Blocked variants',
        '- ' + (', '.join(f'`{v}`' for v in blocked_ids) if blocked_ids else 'None'),
        '',
        '## Top variants',
    ]
    if ranked:
        for idx, item in enumerate(ranked[:args.bulk_top_k], start=1):
            name = item.get('image') or Path(item.get('source_image', 'unknown')).stem
            md.append(f"{idx}. `{name}` — overall {item.get('overall_score', 'n/a')} | verdict {item.get('verdict', 'n/a')} | backend {item.get('backend', 'n/a')}")
    else:
        md.append('- No variants cleared prototype QC.')
    md.extend(['', '## Notes'])
    for note in summary['notes']:
        md.append(f'- {note}')
    SUMMARY_MD.write_text('\n'.join(md) + '\n')

    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
