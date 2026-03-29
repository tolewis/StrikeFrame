#!/usr/bin/env python3
"""Run the ProofHero production lane end-to-end.

Flow
1. Generate a 25-variant ProofHero batch manifest
2. Render the batch
3. Run hard geometry analysis
4. Run required prototype QC before any human review sheet is built
5. Optionally run Popeye bulk/final review on the best survivors
6. Write a markdown + json shortlist for agents
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
OUTPUT_DIR = Path('/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe/proofhero-batch-v1')
ANALYSIS_PATH = OUTPUT_DIR / 'proofhero-batch-analysis.json'
SUMMARY_JSON = OUTPUT_DIR / 'proofhero-pipeline-summary.json'
SUMMARY_MD = OUTPUT_DIR / 'proofhero-pipeline-summary.md'
PASS_SHEET = OUTPUT_DIR / 'proofhero-pass-sheet.jpg'
FAIL_SHEET = OUTPUT_DIR / 'proofhero-fail-sheet.jpg'
QC_JSON = OUTPUT_DIR / 'proofhero-prototype-qc.json'
BULK_QC_JSON = OUTPUT_DIR / 'proofhero-bulk-qc.json'


def run(cmd, check=True, capture=False):
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture)
    if check and result.returncode != 0:
        if capture:
            raise RuntimeError(result.stderr or result.stdout or f'Command failed: {cmd}')
        raise RuntimeError(f'Command failed: {cmd}')
    return result


def load_json(path: Path):
    return json.loads(path.read_text())


def render_sheet(images, out_path, label_prefix):
    if not images:
        return None
    if not shutil.which('convert') or not shutil.which('montage'):
        return None
    staged = []
    stage_dir = OUTPUT_DIR / '.sheet-stage'
    stage_dir.mkdir(parents=True, exist_ok=True)
    for image in images:
        src = OUTPUT_DIR / f'{image}.jpg'
        if not src.exists():
            continue
        staged_path = stage_dir / f'{image}.jpg'
        run([
            'convert', str(src),
            '-gravity', 'north',
            '-background', '#111111',
            '-fill', 'white',
            '-splice', '0x60',
            '-pointsize', '28',
            '-annotate', '+0+10', f'{label_prefix} - {image}',
            str(staged_path)
        ])
        staged.append(str(staged_path))
    if not staged:
        return None
    cols = min(5, len(staged))
    rows = (len(staged) + cols - 1) // cols
    run(['montage', *staged, '-tile', f'{cols}x{rows}', '-geometry', '270x285+10+10', '-background', '#0f0f0f', str(out_path)])
    return out_path


def parse_failures(analysis: dict) -> set[str]:
    failed = set()
    for names in analysis.get('examples', {}).values():
        for name in names:
            failed.add(name.replace('.layout.json', ''))
    return failed


def review_image(image_path: Path, *, backend: str, model: str | None, purpose: str, persona: str, timeout: int) -> dict | None:
    cmd = [
        sys.executable, 'scripts/vision_review.py', str(image_path),
        '--channel', 'paid-social',
        '--persona', persona,
        '--benchmark-role', 'proofHero',
        '--ad-type', 'proof-led',
        '--description', 'ProofHero testimonial ad for TackleRoom fighting belts',
        '--backend', backend,
        '--purpose', purpose,
        '--timeout', str(timeout),
        '--write-report'
    ]
    if model:
        cmd.extend(['--model', model])
    result = run(cmd, check=False, capture=True)
    if result.returncode not in {0, 1, 2}:
        return {'status': 'error', 'error': (result.stderr or result.stdout).strip()}
    try:
        payload = json.loads(result.stdout.strip())
    except Exception:
        return {'status': 'error', 'error': 'vision review returned non-json', 'raw': result.stdout[:500]}
    if isinstance(payload, dict) and payload.get('error'):
        payload['status'] = 'error'
    return payload


def prototype_qc(names: list[str], args) -> tuple[list[dict], list[dict]]:
    rows = []
    approved = []
    for name in names:
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
        name = item['source_image'] if 'source_image' in item else item.get('image')
        image_name = Path(name).stem if name else item.get('image')
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
    for stale in [PASS_SHEET, FAIL_SHEET, QC_JSON, BULK_QC_JSON]:
        stale.unlink(missing_ok=True)

    run([sys.executable, 'scripts/gen_proofhero_batch.py'])
    run(['node', 'scripts/render.js', 'configs/proofhero-batch-v1.json'])
    run([sys.executable, 'scripts/analyze_proofhero_batch.py'])

    analysis = load_json(ANALYSIS_PATH)
    failed = parse_failures(analysis)
    all_images = [p.stem for p in sorted(OUTPUT_DIR.glob('proofhero-*.jpg'))]
    geometry_survivors = [name for name in all_images if name not in failed]

    prototype_rows, approved_reviews = prototype_qc(geometry_survivors, args)
    approved_names = [Path(r['source_image']).stem for r in approved_reviews]
    blocked_names = [row['image'] for row in prototype_rows if row['image'] not in approved_names]
    QC_JSON.write_text(json.dumps({
        'stage': 'prototype-human-review-gate',
        'backend': args.prototype_backend,
        'model': args.prototype_model,
        'geometry_survivors': geometry_survivors,
        'approved_for_human_review': approved_names,
        'blocked': blocked_names,
        'reviews': prototype_rows,
    }, indent=2))

    pass_sheet = render_sheet(approved_names[:10], PASS_SHEET, 'QC PASS')
    fail_sheet = render_sheet(sorted(set(failed) | set(blocked_names)), FAIL_SHEET, 'BLOCKED')

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
        'batch': 'proofhero-batch-v1',
        'render_count': len(all_images),
        'geometry_survivor_count': len(geometry_survivors),
        'prototype_qc_pass_count': len(approved_names),
        'prototype_qc_blocked_count': len(blocked_names),
        'failure_count': len(failed),
        'geometry_failures': sorted(failed),
        'prototype_qc_pass': approved_names,
        'prototype_qc_blocked': blocked_names,
        'analysis': analysis,
        'prototype_qc_json': str(QC_JSON),
        'bulk_review_enabled': args.bulk_review == 'on',
        'bulk_qc_json': str(BULK_QC_JSON) if bulk_reviews else None,
        'top_k': ranked[:args.bulk_top_k],
        'pass_sheet': str(pass_sheet) if pass_sheet else None,
        'fail_sheet': str(fail_sheet) if fail_sheet else None,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))

    md = []
    md.append('# ProofHero Pipeline Summary')
    md.append('')
    md.append(f'- Batch: `{summary["batch"]}`')
    md.append(f'- Renders: **{summary["render_count"]}**')
    md.append(f'- Geometry survivors: **{summary["geometry_survivor_count"]}**')
    md.append(f'- Prototype QC approved for human review: **{summary["prototype_qc_pass_count"]}**')
    md.append(f'- Prototype QC blocked: **{summary["prototype_qc_blocked_count"]}**')
    md.append(f'- Geometry failures: **{summary["failure_count"]}**')
    md.append('')
    if summary['geometry_failures']:
        md.append('## Geometry failures')
        for name in summary['geometry_failures']:
            md.append(f'- `{name}`')
        md.append('')
    if blocked_names:
        md.append('## Prototype QC blocked')
        for name in blocked_names:
            md.append(f'- `{name}`')
        md.append('')
    md.append('## Human-review-safe variants')
    md.append('- ' + (', '.join(f'`{name}`' for name in approved_names) if approved_names else 'None'))
    md.append('')
    md.append('## Top finalists')
    if ranked:
        for idx, item in enumerate(ranked[:args.bulk_top_k], start=1):
            name = item.get('image') or Path(item.get('source_image', 'unknown')).stem
            md.append(f"{idx}. `{name}` — overall {item.get('overall_score', 'n/a')} | verdict {item.get('verdict', 'n/a')} | backend {item.get('backend', 'n/a')}")
    else:
        md.append('- No variants cleared prototype QC.')
    md.append('')
    if summary['pass_sheet']:
        md.append(f'- QC pass sheet: `{summary["pass_sheet"]}`')
    if summary['fail_sheet']:
        md.append(f'- Blocked sheet: `{summary["fail_sheet"]}`')
    md.append(f'- Prototype QC JSON: `{summary["prototype_qc_json"]}`')
    if summary['bulk_qc_json']:
        md.append(f'- Bulk QC JSON: `{summary["bulk_qc_json"]}`')
    SUMMARY_MD.write_text('\n'.join(md) + '\n')

    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
