#!/usr/bin/env python3
import json
from pathlib import Path

DEFAULT_MANIFEST = Path('/home/tlewis/Dropbox/Tim/Datasets/social-media-kb/03_calibration/strikeframe-vision/benchmark-manifest.json')


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict:
    return json.loads(path.read_text())


def main():
    manifest = load_manifest()
    good = manifest.get('good_sources', [])
    bad = manifest.get('bad_sources', [])
    print(json.dumps({
        'manifest_path': str(DEFAULT_MANIFEST),
        'good_sources': good,
        'bad_sources': bad,
        'good_count': len(good),
        'bad_count': len(bad),
    }, indent=2))


if __name__ == '__main__':
    main()
