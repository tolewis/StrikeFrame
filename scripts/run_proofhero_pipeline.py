#!/usr/bin/env python3
"""Run the ProofHero production lane end-to-end.

Flow
1. Generate a 25-variant ProofHero batch manifest
2. Render the batch
3. Run hard geometry analysis
4. Build pass/fail contact sheets
5. Optionally run vision review on survivors
6. Write a markdown + json shortlist for agents
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
OUTPUT_DIR = ROOT / 'output' / 'meta-v2' / 'proofhero-batch-v1'
ANALYSIS_PATH = OUTPUT_DIR / 'proofhero-batch-analysis.json'
SUMMARY_JSON = OUTPUT_DIR / 'proofhero-pipeline-summary.json'
SUMMARY_MD = OUTPUT_DIR / 'proofhero-pipeline-summary.md'
PASS_SHEET = OUTPUT_DIR / 'proofhero-pass-sheet.jpg'
FAIL_SHEET = OUTPUT_DIR / 'proofhero-fail-sheet.jpg'


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


def review_image(image_path: Path, args) -> dict | None:
    cmd = [
        sys.executable, 'scripts/vision_review.py', str(image_path),
        '--channel', 'paid-social',
        '--persona', args.persona,
        '--benchmark-role', 'proofHero',
        '--ad-type', 'proof-led',
        '--description', 'ProofHero testimonial ad for TackleRoom fighting belts',
        '--model', args.model,
        '--timeout', str(args.timeout),
        '--write-report'
    ]
    result = run(cmd, check=False, capture=True)
    if result.returncode != 0:
        return {'status': 'error', 'error': (result.stderr or result.stdout).strip()}
    try:
        return json.loads(result.stdout.strip())
    except Exception:
        return {'status': 'error', 'error': 'vision review returned non-json', 'raw': result.stdout[:500]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vision', choices=['on', 'off'], default='off')
    ap.add_argument('--persona', default='tim-operator')
    ap.add_argument('--model', default='qwen2.5vl:32b')
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--top-k', type=int, default=5)
    args = ap.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run([sys.executable, 'scripts/gen_proofhero_batch.py'])
    run(['node', 'scripts/render.js', 'configs/proofhero-batch-v1.json'])
    run([sys.executable, 'scripts/analyze_proofhero_batch.py'])

    analysis = load_json(ANALYSIS_PATH)
    failed = parse_failures(analysis)
    all_images = [p.stem for p in sorted(OUTPUT_DIR.glob('proofhero-*.jpg'))]
    survivors = [name for name in all_images if name not in failed]

    render_sheet(survivors[:10], PASS_SHEET, 'SURVIVOR')
    render_sheet(sorted(failed), FAIL_SHEET, 'FAIL')

    reviews = []
    if args.vision == 'on':
        for name in survivors:
            review = review_image(OUTPUT_DIR / f'{name}.jpg', args)
            review = review or {'status': 'error', 'error': 'unknown'}
            review['image'] = name
            reviews.append(review)

    ranked = []
    if reviews:
        scored = [r for r in reviews if isinstance(r, dict) and r.get('status') != 'error']
        ranked = sorted(scored, key=lambda r: (r.get('overall_score', 0), r.get('channel_fit_score', 0)), reverse=True)

    summary = {
        'batch': 'proofhero-batch-v1',
        'render_count': len(all_images),
        'survivor_count': len(survivors),
        'failure_count': len(failed),
        'failures': sorted(failed),
        'survivors': survivors,
        'analysis': analysis,
        'vision_enabled': args.vision == 'on',
        'top_k': ranked[:args.top_k],
        'pass_sheet': str(PASS_SHEET) if PASS_SHEET.exists() else None,
        'fail_sheet': str(FAIL_SHEET) if FAIL_SHEET.exists() else None,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))

    md = []
    md.append('# ProofHero Pipeline Summary')
    md.append('')
    md.append(f'- Batch: `{summary["batch"]}`')
    md.append(f'- Renders: **{summary["render_count"]}**')
    md.append(f'- Survivors: **{summary["survivor_count"]}**')
    md.append(f'- Failures: **{summary["failure_count"]}**')
    md.append('')
    if summary['failures']:
        md.append('## Failed variants')
        for name in summary['failures']:
            md.append(f'- `{name}`')
        md.append('')
    md.append('## Survivor variants')
    md.append('- ' + ', '.join(f'`{name}`' for name in survivors))
    md.append('')
    if ranked:
        md.append('## Top finalists')
        for idx, item in enumerate(ranked[:args.top_k], start=1):
            md.append(f"{idx}. `{item['image']}` — overall {item.get('overall_score', 'n/a')} | verdict {item.get('verdict', 'n/a')}")
        md.append('')
    else:
        md.append('## Top finalists')
        md.append('- Vision ranking not run or unavailable. Use the survivor sheet + LLM review to choose finalists.')
        md.append('')
    if summary['pass_sheet']:
        md.append(f'- Survivor sheet: `{summary["pass_sheet"]}`')
    if summary['fail_sheet']:
        md.append(f'- Failure sheet: `{summary["fail_sheet"]}`')
    SUMMARY_MD.write_text('\n'.join(md) + '\n')

    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
