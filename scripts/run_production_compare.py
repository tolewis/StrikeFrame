#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VISION_SCRIPT = PROJECT_ROOT / 'scripts' / 'vision_review.py'
DEFAULT_SET = [
    PROJECT_ROOT / 'configs/waterfall/personal-all-platforms.json',
    PROJECT_ROOT / 'configs/waterfall/tackleroom-all-platforms.json',
    PROJECT_ROOT / 'configs/waterfall/contractor-ai-blog-heroes.json',
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def channel_for(name: str) -> tuple[str, str]:
    if '_x_' in name:
        return 'x', 'tim-operator'
    return 'generic', 'generic'


def score_image(image: Path, channel: str, persona: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(VISION_SCRIPT), str(image), '--channel', channel, '--persona', persona, '--timeout', '180'],
        capture_output=True, text=True, check=False,
    )
    payload = json.loads(proc.stdout)
    return {
        'verdict': payload.get('verdict'),
        'overall_score': payload.get('overall_score'),
        'rubric_total': payload.get('rubric_total'),
        'slop_risk': payload.get('slop_risk'),
    }


def main():
    ap = argparse.ArgumentParser(description='Hash-aware production compare for StrikeFrame validation set.')
    ap.add_argument('--workdir', required=True, help='Tmp workdir for rerenders and reports')
    ap.add_argument('--before-dir', required=True, help='Directory containing prior outputs to compare against')
    args = ap.parse_args()

    workdir = Path(args.workdir)
    before_dir = Path(args.before_dir)
    renders_dir = workdir / 'renders'
    reports_dir = workdir / 'reports'
    renders_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    assets = []
    tmp_cfgs = []
    for cfg in DEFAULT_SET:
        data = json.loads(cfg.read_text())
        for render in data['renders']:
            name = Path(render['output']).name
            render['output'] = str(renders_dir / name)
            assets.append(name)
        tmp_cfg = workdir / f'{cfg.stem}.json'
        tmp_cfg.write_text(json.dumps(data, indent=2) + '\n')
        tmp_cfgs.append(tmp_cfg)

    for cfg in tmp_cfgs:
        subprocess.run(['node', str(PROJECT_ROOT / 'scripts/render.js'), str(cfg)], cwd=PROJECT_ROOT, check=True)

    rows = []
    improved = regressed = unchanged = skipped = 0
    for name in assets:
        before = before_dir / name
        new = renders_dir / name
        channel, persona = channel_for(name)
        old_hash = sha256_file(before)
        new_hash = sha256_file(new)
        row = {
            'asset': name,
            'channel': channel,
            'old_hash': old_hash,
            'new_hash': new_hash,
            'byte_identical': old_hash == new_hash,
        }
        if old_hash == new_hash:
            row['old'] = row['new'] = None
            row['delta_overall'] = 0
            row['delta_rubric_total'] = 0
            row['status'] = 'skipped-identical'
            skipped += 1
            unchanged += 1
        else:
            old_score = score_image(before, channel, persona)
            new_score = score_image(new, channel, persona)
            row['old'] = old_score
            row['new'] = new_score
            row['delta_overall'] = round((new_score.get('overall_score') or 0) - (old_score.get('overall_score') or 0), 2)
            row['delta_rubric_total'] = (new_score.get('rubric_total') or 0) - (old_score.get('rubric_total') or 0)
            if row['delta_overall'] > 0 or row['delta_rubric_total'] > 0:
                row['status'] = 'improved'
                improved += 1
            elif row['delta_overall'] < 0 or row['delta_rubric_total'] < 0:
                row['status'] = 'regressed'
                regressed += 1
            else:
                row['status'] = 'unchanged'
                unchanged += 1
        rows.append(row)

    summary = {
        'workdir': str(workdir),
        'before_dir': str(before_dir),
        'assets': rows,
        'improved_count': improved,
        'regressed_count': regressed,
        'unchanged_count': unchanged,
        'skipped_identical_count': skipped,
    }
    out = reports_dir / 'production-compare.json'
    out.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'report': str(out), 'improved': improved, 'regressed': regressed, 'unchanged': unchanged, 'skipped_identical': skipped}, indent=2))


if __name__ == '__main__':
    main()
