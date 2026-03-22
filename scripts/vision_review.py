#!/usr/bin/env python3
import argparse
import base64
import json
import re
import sys
from datetime import datetime, UTC
from pathlib import Path
from urllib import request, error

try:
    from review_prompts import load_prompt
except ModuleNotFoundError:
    from scripts.review_prompts import load_prompt

DEFAULT_HOST = 'http://192.168.0.160:11434'
DEFAULT_MODEL = 'minicpm-v:latest'
CONTRACT_VERSION = '1.0'


def normalize_label_score(value, kind: str) -> str:
    if isinstance(value, (int, float)):
        if kind == "slop":
            if value >= 7:
                return "high"
            if value >= 4:
                return "medium"
            return "low"
        if kind == "confidence":
            if value >= 0.8:
                return "high"
            if value >= 0.5:
                return "medium"
            return "low"
    value = str(value).lower().strip()
    return value or ("high" if kind == "slop" else "medium")


def normalize_list(items) -> list[str]:
    out = []
    if not isinstance(items, list):
        return out
    for item in items:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            name = item.get("name") or item.get("label") or item.get("text") or item.get("field")
            value = item.get("value")
            reason = item.get("reason")
            if name and reason and value is not None:
                out.append(f"{name}: {value} — {reason}")
            elif name and value is not None:
                out.append(f"{name}: {value}")
            elif name and reason:
                out.append(f"{name} — {reason}")
            elif name:
                out.append(str(name))
            elif reason:
                out.append(str(reason))
            else:
                out.append(json.dumps(item, ensure_ascii=False))
        else:
            out.append(str(item))
    return out


def build_user_prompt(args) -> str:
    rubric = load_prompt(args.channel)
    context = {
        'channel': args.channel,
        'persona': args.persona,
        'headline': args.headline or '',
        'subhead': args.subhead or '',
        'cta': args.cta or '',
        'footer': args.footer or '',
        'source_config': args.source_config or '',
    }
    return rubric + '\n\nReview context:\n' + json.dumps(context, indent=2)


def call_ollama(host: str, model: str, prompt: str, image_path: Path, timeout: int) -> str:
    payload = {
        'model': model,
        'stream': False,
        'format': 'json',
        'options': {'temperature': 0.1},
        'messages': [
            {
                'role': 'user',
                'content': prompt,
                'images': [base64.b64encode(image_path.read_bytes()).decode('ascii')],
            }
        ],
    }
    req = request.Request(
        host.rstrip('/') + '/api/chat',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
    )
    with request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    return data['message']['content']


def extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r'\{.*\}', text, re.S)
    if not match:
        raise ValueError('model response did not contain JSON')
    return json.loads(match.group(0))


def normalize_verdict(data: dict, channel: str, persona: str) -> dict:
    overall = float(data.get('overall_score', 0))
    fit = float(data.get('copy_visual_fit_score', overall))
    slop = normalize_label_score(data.get('slop_risk', 'high'), 'slop')

    verdict = str(data.get('verdict', '')).lower().strip()
    if verdict not in {'pass', 'warn', 'fail', 'reject'}:
        if overall >= 9.0:
            verdict = 'pass'
        elif overall >= 7.5:
            verdict = 'warn'
        elif overall >= 5.0:
            verdict = 'fail'
        else:
            verdict = 'reject'

    if channel == 'x' and persona == 'tim-operator':
        if overall < 9.0 or fit < 9.0 or slop != 'low':
            if overall < 5.0 or slop == 'high':
                verdict = 'reject'
            elif overall < 8.5 or fit < 8.5:
                verdict = 'fail'
            else:
                verdict = 'warn'

    data['verdict'] = verdict
    data['should_reject'] = verdict in {'fail', 'reject'}
    return data


def build_report(args, parsed: dict, raw_response: str) -> dict:
    report = {
        'version': CONTRACT_VERSION,
        'model': args.model,
        'host': args.host,
        'channel': args.channel,
        'persona': args.persona,
        'source_image': str(Path(args.image).resolve()),
        'source_config': args.source_config,
        'created_at': datetime.now(UTC).isoformat(),
        'overall_score': float(parsed.get('overall_score', 0)),
        'channel_fit_score': float(parsed.get('channel_fit_score', parsed.get('overall_score', 0))),
        'copy_visual_fit_score': float(parsed.get('copy_visual_fit_score', parsed.get('overall_score', 0))),
        'readability_score': float(parsed.get('readability_score', parsed.get('overall_score', 0))),
        'slop_risk': normalize_label_score(parsed.get('slop_risk', 'high'), 'slop'),
        'verdict': parsed.get('verdict', 'reject'),
        'should_reject': bool(parsed.get('should_reject', True)),
        'confidence': normalize_label_score(parsed.get('confidence', 'medium'), 'confidence'),
        'summary': parsed.get('summary', ''),
        'reasons': normalize_list(parsed.get('reasons', [])),
        'fixes': normalize_list(parsed.get('fixes', [])),
        'raw_response': raw_response,
    }
    return report


def report_path_for(image_path: Path) -> Path:
    return image_path.with_name(image_path.name + '.vision-review.json')


def main():
    ap = argparse.ArgumentParser(description='Run multimodal creative review on a rendered StrikeFrame asset.')
    ap.add_argument('image')
    ap.add_argument('--host', default=DEFAULT_HOST)
    ap.add_argument('--model', default=DEFAULT_MODEL)
    ap.add_argument('--channel', default='generic')
    ap.add_argument('--persona', default='generic')
    ap.add_argument('--headline', default='')
    ap.add_argument('--subhead', default='')
    ap.add_argument('--cta', default='')
    ap.add_argument('--footer', default='')
    ap.add_argument('--source-config', default='')
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--write-report', action='store_true')
    args = ap.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f'Image not found: {image_path}', file=sys.stderr)
        sys.exit(2)

    try:
        raw_response = call_ollama(args.host, args.model, build_user_prompt(args), image_path, args.timeout)
        parsed = extract_json(raw_response)
        parsed = normalize_verdict(parsed, args.channel.lower(), args.persona.lower())
        report = build_report(args, parsed, raw_response)
    except error.URLError as e:
        print(json.dumps({'status': 'error', 'error': f'ollama unreachable: {e}'}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))
        sys.exit(2)

    if args.write_report:
        out = report_path_for(image_path)
        out.write_text(json.dumps(report, indent=2) + '\n')
        report['report_path'] = str(out)

    print(json.dumps(report, indent=2))
    if report['verdict'] == 'pass':
        sys.exit(0)
    if report['verdict'] == 'warn':
        sys.exit(1)
    sys.exit(2)


if __name__ == '__main__':
    main()
