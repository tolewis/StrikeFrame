#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

from load_calibration_manifest import load_manifest, DEFAULT_MANIFEST

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VISION_SCRIPT = PROJECT_ROOT / 'scripts' / 'vision_review.py'
VERDICT_ORDER = {'pass': 3, 'warn': 2, 'fail': 1, 'reject': 0}


def eval_entry(entry: dict, kind: str, args) -> dict:
    image_path = entry.get('linked_path') or entry.get('path') or entry.get('source_path')
    channel = entry.get('channel', args.channel if kind == 'good' else 'x')
    persona = entry.get('persona', args.persona if kind == 'good' else 'tim-operator')
    if kind == 'good' and (not channel or channel == 'generic'):
        channel = 'paid-social'

    cmd = [
        sys.executable,
        str(VISION_SCRIPT),
        image_path,
        '--host', args.host,
        '--model', args.model,
        '--channel', channel,
        '--persona', persona,
        '--headline', entry.get('headline', ''),
        '--subhead', entry.get('subhead', ''),
        '--cta', entry.get('cta', ''),
        '--footer', entry.get('footer', ''),
        '--source-config', entry.get('source_config', ''),
        '--benchmark-role', entry.get('benchmark_role', ''),
        '--ad-type', entry.get('ad_type', ''),
        '--description', entry.get('description', ''),
        '--timeout', str(args.timeout),
    ]

    payload = {'status': 'error', 'error': 'no attempts run'}
    proc = None
    attempts = []

    for attempt in range(args.retries + 1):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        attempts.append({'attempt': attempt + 1, 'returncode': proc.returncode})

        if proc.stdout.strip():
            try:
                payload = json.loads(proc.stdout)
            except Exception:
                payload = {'status': 'error', 'error': 'invalid json', 'raw': proc.stdout[-1000:]}
        else:
            payload = {'status': 'error', 'error': proc.stderr.strip() or 'no stdout'}

        timed_out = isinstance(payload, dict) and payload.get('status') == 'error' and 'timed out' in str(payload.get('error', '')).lower()
        if not timed_out:
            break

    result = {
        'id': entry.get('id') or Path(image_path).stem,
        'kind': kind,
        'image_path': image_path,
        'channel': channel,
        'persona': persona,
        'exit_code': proc.returncode if proc else 2,
        'review': payload,
        'attempts': attempts,
    }

    verdict = payload.get('verdict') if isinstance(payload, dict) else None
    if kind == 'good':
        result['expected'] = 'pass_or_warn'
        result['meets_expectation'] = verdict in {'pass', 'warn'}
    else:
        expected_max = entry.get('expected_verdict_max', 'fail')
        result['expected'] = f'max_{expected_max}'
        result['meets_expectation'] = VERDICT_ORDER.get(verdict, -1) <= VERDICT_ORDER.get(expected_max, 1)
    return result


def flatten_sources(manifest: dict):
    goods = []
    bads = []
    for src in manifest.get('good_sources', []):
        goods.extend(src.get('entries', []))
    for src in manifest.get('bad_sources', []):
        bads.extend(src.get('entries', []))
    return goods, bads


def main():
    import argparse
    ap = argparse.ArgumentParser(description='Run StrikeFrame calibration evaluation against Dropbox manifest.')
    ap.add_argument('--host', default='http://192.168.0.160:11434')
    ap.add_argument('--model', default='minicpm-v:latest')
    ap.add_argument('--channel', default='generic')
    ap.add_argument('--persona', default='generic')
    ap.add_argument('--limit-good', type=int, default=5)
    ap.add_argument('--limit-bad', type=int, default=5)
    ap.add_argument('--timeout', type=int, default=180)
    ap.add_argument('--retries', type=int, default=1)
    args = ap.parse_args()

    manifest = load_manifest(DEFAULT_MANIFEST)
    goods, bads = flatten_sources(manifest)
    goods = goods[:args.limit_good]
    bads = bads[:args.limit_bad]

    results = []
    for entry in goods:
        results.append(eval_entry(entry, 'good', args))
    for entry in bads:
        results.append(eval_entry(entry, 'bad', args))

    summary = {
        'manifest_path': str(DEFAULT_MANIFEST),
        'generated_at': datetime.now(UTC).isoformat(),
        'model': args.model,
        'host': args.host,
        'good_evaluated': sum(1 for r in results if r['kind'] == 'good'),
        'bad_evaluated': sum(1 for r in results if r['kind'] == 'bad'),
        'met_expectation': sum(1 for r in results if r.get('meets_expectation')),
        'failed_expectation': sum(1 for r in results if not r.get('meets_expectation')),
        'results': results,
    }

    run_dir = Path(manifest['run_output_dir'])
    run_dir.mkdir(parents=True, exist_ok=True)
    run_path = run_dir / f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    run_path.write_text(json.dumps(summary, indent=2) + '\n')
    summary['run_path'] = str(run_path)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
