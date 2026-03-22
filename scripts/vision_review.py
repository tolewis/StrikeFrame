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


def clamp_score(value, default=0.0) -> float:
    try:
        v = float(value)
    except Exception:
        return float(default)
    if v < 0:
        return 0.0
    if v > 10:
        return 10.0
    return v


def normalize_bool(value, default=False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {'true','yes','1','pass','warn'}:
            return True
        if v in {'false','no','0','fail','reject','should reject','should_reject'}:
            return False
    return default


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
        'benchmark_role': args.benchmark_role or '',
        'ad_type': args.ad_type or '',
        'description': args.description or '',
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
    if 'scroll_stop_score' in data:
        total = compute_rubric_total(data)
        overall = round(total / 10, 1)
        channel_fit = clamp_score(data.get('platform_fit_score', 3) * 2)
        fit = clamp_score(data.get('content_value_score', 3) * 2)
        readability = clamp_score(data.get('readability_score', data.get('text_readability_score', 3)) * 2)
        brand = clamp_score(data.get('brand_authenticity_score', 3))
        slop = 'low' if brand >= 4 else 'medium' if brand >= 3 else 'high'
        data['overall_score'] = overall
        data['channel_fit_score'] = channel_fit
        data['copy_visual_fit_score'] = fit
        data['readability_score'] = readability
        data['slop_risk'] = slop
        if channel == 'paid-social':
            if total >= 85:
                verdict = 'pass'
            elif total >= 70:
                verdict = 'warn'
            elif total >= 60:
                verdict = 'fail'
            else:
                verdict = 'reject'
        else:
            if total >= 85:
                verdict = 'pass'
            elif total >= 72:
                verdict = 'warn'
            elif total >= 60:
                verdict = 'fail'
            else:
                verdict = 'reject'
    else:
        overall = clamp_score(data.get('overall_score', 0))
        fit = clamp_score(data.get('copy_visual_fit_score', overall))
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


def compute_rubric_total(parsed: dict) -> int:
    """Compute the weighted rubric total from dimension scores (0-100)."""
    weights = {
        'scroll_stop_score': 4,
        'composition_score': 3,
        'text_readability_score': 3,
        'color_contrast_score': 2,
        'image_quality_score': 2,
        'content_value_score': 2,
        'brand_authenticity_score': 2,
        'platform_fit_score': 2,
    }
    total = 0
    for field, weight in weights.items():
        score = parsed.get(field, 3)  # default 3 if missing
        if isinstance(score, (int, float)):
            total += min(5, max(1, int(score))) * weight
        else:
            total += 3 * weight
    return total


def build_report(args, parsed: dict, raw_response: str) -> dict:
    # Compute rubric total if dimension scores are present
    has_rubric = 'scroll_stop_score' in parsed
    rubric_total = compute_rubric_total(parsed) if has_rubric else None
    
    # Map rubric total to 0-10 scale for backward compatibility
    if rubric_total is not None:
        overall_from_rubric = round(rubric_total / 10, 1)
    else:
        overall_from_rubric = None
    
    report = {
        'version': CONTRACT_VERSION,
        'model': args.model,
        'host': args.host,
        'channel': args.channel,
        'persona': args.persona,
        'source_image': str(Path(args.image).resolve()),
        'source_config': args.source_config,
        'created_at': datetime.now(UTC).isoformat(),
        'overall_score': clamp_score(overall_from_rubric or parsed.get('overall_score', 0)),
        'channel_fit_score': clamp_score(parsed.get('channel_fit_score', parsed.get('platform_fit_score', parsed.get('overall_score', 0)))),
        'copy_visual_fit_score': clamp_score(parsed.get('copy_visual_fit_score', parsed.get('content_value_score', parsed.get('overall_score', 0)))),
        'readability_score': clamp_score(parsed.get('readability_score', parsed.get('overall_score', 0))),
        'slop_risk': normalize_label_score(parsed.get('slop_risk', 'high'), 'slop'),
        'verdict': parsed.get('verdict', 'reject'),
        'should_reject': normalize_bool(parsed.get('should_reject', parsed.get('verdict', 'reject') in {'fail','reject'}), True),
        'confidence': normalize_label_score(parsed.get('confidence', 'medium'), 'confidence'),
        'summary': str(parsed.get('summary', '')).strip(),
        'weakest_dimension': str(parsed.get('weakest_dimension', '')).strip(),
        'reasons': normalize_list(parsed.get('reasons', [])),
        'fixes': normalize_list(parsed.get('fixes', [])),
        'raw_response': raw_response,
    }
    
    # Add rubric dimension scores if present
    if has_rubric:
        report['rubric_total'] = rubric_total
        report['rubric_max'] = 100
        report['dimension_scores'] = {
            'scroll_stop': int(parsed.get('scroll_stop_score', 3)),
            'composition': int(parsed.get('composition_score', 3)),
            'readability': int(parsed.get('text_readability_score', parsed.get('readability_score', 3))),
            'color_contrast': int(parsed.get('color_contrast_score', 3)),
            'image_quality': int(parsed.get('image_quality_score', 3)),
            'content_value': int(parsed.get('content_value_score', 3)),
            'brand_authenticity': int(parsed.get('brand_authenticity_score', 3)),
            'platform_fit': int(parsed.get('platform_fit_score', 3)),
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
    ap.add_argument('--benchmark-role', default='')
    ap.add_argument('--ad-type', default='')
    ap.add_argument('--description', default='')
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
