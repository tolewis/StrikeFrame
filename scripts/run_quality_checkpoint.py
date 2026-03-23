#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path('/home/tlewis/Documents/projects/30 Projects/TackleRoom/Media Renderer MVP')
VISION_SCRIPT = PROJECT_ROOT / 'scripts' / 'vision_review.py'
RENDER_SCRIPT = PROJECT_ROOT / 'scripts' / 'render.js'

CHANNEL_HINTS = [
    ('_linkedin_', 'linkedin'),
    ('_x_', 'x'),
    ('_ig_', 'instagram'),
    ('blog_hero_', 'generic'),
    ('_blog_', 'generic'),
]


def deep_merge(a, b):
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def flatten_configs(config_path: Path):
    payload = json.loads(config_path.read_text())
    if isinstance(payload, dict) and isinstance(payload.get('renders'), list):
        defaults = payload.get('defaults', {})
        configs = []
        for render in payload['renders']:
            merged = deep_merge(defaults, render)
            configs.append(merged)
        return configs
    return [payload]


def infer_channel(output_name: str) -> str:
    lowered = output_name.lower()
    for needle, channel in CHANNEL_HINTS:
        if needle in lowered:
            return channel
    return 'generic'


def run(cmd, cwd=PROJECT_ROOT, check=True):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(map(str, cmd))}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc


def render_config(cfg: dict, candidate_dir: Path) -> Path:
    output_name = Path(cfg['output']).name
    cfg = copy.deepcopy(cfg)
    cfg['output'] = str(candidate_dir / output_name)
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, dir=str(PROJECT_ROOT / 'configs')) as tmp:
        json.dump(cfg, tmp, indent=2)
        tmp_path = Path(tmp.name)
    try:
        run(['node', str(RENDER_SCRIPT), str(tmp_path)])
    finally:
        tmp_path.unlink(missing_ok=True)
    return candidate_dir / output_name


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def vision_review(image_path: Path, cfg: dict) -> dict:
    channel = infer_channel(Path(cfg['output']).name)
    cmd = [
        sys.executable,
        str(VISION_SCRIPT),
        str(image_path),
        '--channel', channel,
        '--persona', 'tim-operator',
        '--headline', cfg.get('text', {}).get('headline', ''),
        '--subhead', cfg.get('text', {}).get('subhead', ''),
        '--cta', cfg.get('text', {}).get('cta', ''),
        '--footer', cfg.get('text', {}).get('footer', ''),
    ]
    proc = run(cmd, check=False)
    if not proc.stdout.strip():
        raise RuntimeError(f'vision review produced no stdout for {image_path}: {proc.stderr}')
    payload = json.loads(proc.stdout)
    payload['exit_code'] = proc.returncode
    return payload


def summarize_review(payload: dict) -> dict:
    return {
        'overall_score': payload.get('overall_score'),
        'rubric_total': payload.get('rubric_total'),
        'verdict': payload.get('verdict'),
        'slop_risk': payload.get('slop_risk'),
    }


def main():
    ap = argparse.ArgumentParser(description='Render a candidate checkpoint and compare Popeye vision scores to a baseline directory.')
    ap.add_argument('--baseline-dir', required=True)
    ap.add_argument('--candidate-dir', required=True)
    ap.add_argument('configs', nargs='+')
    args = ap.parse_args()

    baseline_dir = Path(args.baseline_dir)
    candidate_dir = Path(args.candidate_dir)
    candidate_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    all_configs = []
    for raw in args.configs:
        all_configs.extend(flatten_configs(Path(raw)))

    for cfg in all_configs:
        output_name = Path(cfg['output']).name
        baseline_image = baseline_dir / output_name
        if not baseline_image.exists():
            raise FileNotFoundError(f'Baseline image missing: {baseline_image}')
        candidate_image = render_config(cfg, candidate_dir)
        baseline_md5 = file_md5(baseline_image)
        candidate_md5 = file_md5(candidate_image)
        base_review = vision_review(baseline_image, cfg)
        if baseline_md5 == candidate_md5:
            cand_review = base_review
        else:
            cand_review = vision_review(candidate_image, cfg)
        rows.append({
            'asset': output_name,
            'channel': infer_channel(output_name),
            'baseline_md5': baseline_md5,
            'candidate_md5': candidate_md5,
            'image_changed': baseline_md5 != candidate_md5,
            'baseline': summarize_review(base_review),
            'candidate': summarize_review(cand_review),
            'delta_overall': round((cand_review.get('overall_score') or 0) - (base_review.get('overall_score') or 0), 2),
            'delta_rubric_total': (cand_review.get('rubric_total') or 0) - (base_review.get('rubric_total') or 0),
        })

    summary = {
        'asset_count': len(rows),
        'improved': sum(1 for r in rows if r['delta_rubric_total'] > 0),
        'regressed': sum(1 for r in rows if r['delta_rubric_total'] < 0),
        'unchanged': sum(1 for r in rows if r['delta_rubric_total'] == 0),
        'avg_delta_overall': round(sum(r['delta_overall'] for r in rows) / max(len(rows), 1), 3),
        'avg_delta_rubric_total': round(sum(r['delta_rubric_total'] for r in rows) / max(len(rows), 1), 3),
    }
    payload = {
        'baseline_dir': str(baseline_dir),
        'candidate_dir': str(candidate_dir),
        'summary': summary,
        'assets': rows,
    }
    out_path = candidate_dir / 'compare.json'
    out_path.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
