#!/usr/bin/env python3
"""
Generate variant proof renders for all StrikeFrame primitives.

For each primitive × each variant, renders a sample image using
representative content. Outputs to a proof directory with labeled
filenames: {primitive}-{variant}.jpg

Then assembles a labeled contact sheet (proof-sheet.jpg).

Usage:
    python3 scripts/gen_variant_proof.py [--output-dir DIR]
"""

import json
import os
import sys
import subprocess
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RENDER_JS = os.path.join(SCRIPT_DIR, 'render.js')

# --- Sample content for each primitive ---

# -----------------------------------------------------------------------
# Content zone: headline bottom (~280px) to CTA top (920px) = 640px
# Each primitive's content should be vertically centered in this zone.
# ZONE_TOP and ZONE_BOTTOM define the available area.
# -----------------------------------------------------------------------
ZONE_TOP = 290   # just below 2-line headline
ZONE_BOTTOM = 900 # just above CTA
ZONE_HEIGHT = ZONE_BOTTOM - ZONE_TOP  # 610px

# -----------------------------------------------------------------------
# Real TackleRoom assets
# -----------------------------------------------------------------------
HERO_IMAGES = [
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/IMG_8585.png',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/IMG_8700.png',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/IMG_9117.jpg',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/Dolphin_Fish_Hooked.jpg',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/IMG_9109.jpg',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/IMG_9098.jpg',
]

LOGO_PATH = '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/camera-strikeframe/tier1-ready/logo-landscape-1200x300-v2.png'

REVIEW_IMAGES = [
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/review-proof/tier2-polish/Review08.png',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/review-proof/tier2-polish/Review11.png',
    '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/review-proof/tier2-polish/Review03.png',
]


def _center_start(content_height):
    """Return startY that centers content_height in the zone."""
    return ZONE_TOP + (ZONE_HEIGHT - content_height) // 2


# ComparisonPanel: headers(50) + 5 rows × 100px = 550px content
_cp_content_h = 50 + 5 * 100
COMPARISON_PANEL_CONTENT = {
    'comparisonTable': {
        'startX': 72,
        'startY': _center_start(_cp_content_h),
        'colWidth': 440,
        'rowHeight': 100,
        'headerSize': 22,
        'bodySize': 20,
        'highlightCol': 'right',
        'leftHeader': 'GENERIC SHOP',
        'rightHeader': 'THE TACKLE ROOM',
        'rows': [
            {'left': 'Generic Freshwater Stock', 'right': 'Offshore-Only Inventory'},
            {'left': 'Ask Google for Tips', 'right': 'Captain-Tested Advice'},
            {'left': '1-2 Week Shipping', 'right': 'Ships Same Day'},
            {'left': 'Hit or Miss 80lb+ Gear', 'right': 'Full Heavy Tackle'},
            {'left': 'No One to Call', 'right': 'Live Expert on the Line'},
        ]
    }
}

# OfferFrame: orig(32) + gap(16) + sale(96) + badge(32) + gap(18) + offer(20) ≈ 220px
_of_content_h = 220
_of_center = ZONE_TOP + (ZONE_HEIGHT - _of_content_h) // 2
OFFER_FRAME_CONTENT = {
    'offerFrame': {
        'originalPrice': '$289.99',
        'salePrice': '$224.99',
        'savings': 'SAVE 22%',
        'offerText': 'FREE SHIPPING OVER $99',
        'salePriceSize': 96,
        'originalPriceSize': 32,
        'priceY': _of_center + 140  # sale price baseline
    }
}

# BenefitStack: 4 items × 130px spacing = 390px content
_bs_content_h = 4 * 130
BENEFIT_STACK_CONTENT = {
    'benefitStack': {
        'startX': 80,
        'startY': _center_start(_bs_content_h),
        'spacing': 130,
        'iconSize': 40,
        'textSize': 30,
        'items': [
            {'icon': 'shield', 'label': '500lb rated hardware'},
            {'icon': 'wave', 'label': 'Built for offshore current'},
            {'icon': 'check', 'label': 'Complete kit, nothing missing'},
            {'icon': 'anchor', 'label': 'Captain-verified gear'}
        ]
    }
}

# Testimonial: quote mark(80) + quote(~150) + gap(40) + stars(36) + gap(24) + name(22) + role(18) ≈ 370px
_tm_content_h = 370
TESTIMONIAL_CONTENT = {
    'testimonial': {
        'quote': 'This dredge changed our tournament results completely.',
        'stars': 5,
        'starSize': 40,
        'name': 'Capt. Mike Henderson',
        'role': 'Blue Water Charters, Islamorada',
        'quoteSize': 42,
        'quoteMaxChars': 24,
        'startY': _center_start(_tm_content_h)
    }
}

# SplitReveal: labels(30) + 4 rows × 120px = 510px
_sr_content_h = 30 + 4 * 120
SPLIT_REVEAL_CONTENT = {
    'splitReveal': {
        'startY': _center_start(_sr_content_h),
        'rowHeight': 120,
        'textSize': 24,
        'problemLabel': 'THE PROBLEM',
        'solutionLabel': 'THE FIX',
        'items': [
            {'left': 'Incomplete planer kits', 'right': 'Every piece included'},
            {'left': 'Wrong bridle size', 'right': 'Matched to your planer'},
            {'left': 'Cheap snap swivels', 'right': '500lb ball bearings'},
            {'left': 'No rigging guidance', 'right': 'Captain setup guide'}
        ]
    }
}

# AuthorityBar: sits just above CTA
AUTHORITY_BAR_CONTENT = {
    'authorityBar': {
        'barY': ZONE_BOTTOM - 50,
        'barHeight': 44,
        'textSize': 14,
        'publications': ['TOURNAMENT TESTED', 'CAPTAIN VERIFIED', 'OFFSHORE PROVEN']
    }
}

ACTION_HERO_CONTENT = {
    'actionHero': {}  # variant injected below
}

# ProofHero: quote(~180) + stars(72) + gaps ≈ 350px — push down into zone
_ph_quote_start = _center_start(350) - 40  # offset for quote mark
PROOF_HERO_CONTENT = {
    'proofHero': {
        'quote': 'Best offshore tackle supplier I have found. Period.',
        'quoteSize': 58,
        'quoteMaxChars': 22,
        'quoteY': _ph_quote_start + 100,
        'maxQuoteLines': 3,
        'starsText': '★★★★★',
        'starsSize': 72,
        'assets': {
            'reviewPath': REVIEW_IMAGES[0],
        },
        'reviewWidth': 700,
        'reviewHeight': 200,
        'cta': {
            'text': 'SHOP OFFSHORE TACKLE',
            'width': 420,
            'height': 64,
            'y': ZONE_BOTTOM - 20,
            'x': 110,
            'fill': 'rgba(232,93,58,0.95)',
            'textColor': '#ffffff'
        }
    }
}

# --- Primitive definitions with their variants ---

PRIMITIVES = {
    'comparisonPanel': {
        'configKey': 'comparisonTable',
        'content': COMPARISON_PANEL_CONTENT,
        'variants': ['standard', 'hero-right', 'compact', 'split-weight'],
        'headline': 'WHY SERIOUS ANGLERS\nCHOOSE THE TACKLE ROOM',
        'cta': 'SHOP NOW →'
    },
    'offerFrame': {
        'configKey': 'offerFrame',
        'content': OFFER_FRAME_CONTENT,
        'variants': ['standard', 'hero-price', 'badge-first'],
        'headline': 'COMPLETE DREDGE\nSPREAD SYSTEM',
        'cta': 'SAVE NOW →'
    },
    'benefitStack': {
        'configKey': 'benefitStack',
        'content': BENEFIT_STACK_CONTENT,
        'variants': ['standard', 'compact', 'card'],
        'headline': 'TOURNAMENT-GRADE\nDREDGE SYSTEMS',
        'cta': 'BUILD YOUR SPREAD →'
    },
    'testimonial': {
        'configKey': 'testimonial',
        'content': TESTIMONIAL_CONTENT,
        'variants': ['standard', 'quote-hero', 'attribution-forward'],
        'headline': 'WHAT CAPTAINS SAY',
        'cta': 'READ MORE REVIEWS →'
    },
    'splitReveal': {
        'configKey': 'splitReveal',
        'content': SPLIT_REVEAL_CONTENT,
        'variants': ['standard', 'pain-heavy', 'solution-hero'],
        'headline': 'PLANER BRIDLE KITS\nDONE RIGHT',
        'cta': 'SEE COMPLETE KITS →'
    },
    'authorityBar': {
        'configKey': 'authorityBar',
        'content': AUTHORITY_BAR_CONTENT,
        'variants': ['standard', 'bold'],
        'headline': 'OFFSHORE TACKLE\nYOU CAN TRUST',
        'cta': 'SHOP ALL GEAR →'
    },
    'actionHero': {
        'configKey': 'actionHero',
        'content': ACTION_HERO_CONTENT,
        'variants': ['bottom-heavy', 'center-band', 'split-action', 'compact-strip'],
        'headline': 'WAHOO DON\'T WAIT\nFOR SLOW GEAR',
        'cta': 'SHOP WAHOO GEAR →',
        'subhead': 'High-speed trolling lures, wire rigs, and\ncable leaders built for 40+ knot strikes.',
        'subheadY': ZONE_TOP + ZONE_HEIGHT // 3,  # upper third of content zone
        'badge': {'text': 'WAHOO SEASON', 'x': 340, 'y': 60, 'fill': 'rgba(232,93,58,0.92)', 'textColor': '#ffffff', 'fontSize': 16, 'width': 200, 'height': 38}
    },
    'proofHero': {
        'configKey': 'proofHero',
        'content': PROOF_HERO_CONTENT,
        'variants': ['quote-dominant', 'review-dominant', 'balanced'],
        'headline': '',
        'cta': '',
        'no_base_cta': True  # proofHero renders its own CTA
    }
}

def build_config(primitive_name, variant_name, output_path):
    """Build a complete render config for one primitive variant."""
    prim = PRIMITIVES[primitive_name]
    content = json.loads(json.dumps(prim['content']))  # deep copy

    # Inject variant into content
    config_key = prim['configKey']
    if config_key in content:
        content[config_key]['variant'] = variant_name

    # CTA position: close to bottom but not stranded
    cta_y = 920
    cta_text = prim['cta']

    # proofHero renders its own CTA — suppress the base renderer CTA
    if prim.get('no_base_cta'):
        cta_text = ''
        cta_y = 1200  # push off-canvas

    subhead = prim.get('subhead', '')
    badges = [prim['badge']] if prim.get('badge') else None

    # Cycle through hero images based on variant index for visual variety
    all_variants = prim['variants']
    variant_idx = all_variants.index(variant_name) if variant_name in all_variants else 0
    bg_image = HERO_IMAGES[variant_idx % len(HERO_IMAGES)]

    config = {
        'preset': 'social-square',
        'template': 'banner',
        'backgroundPath': bg_image,
        'backgroundPosition': 'center',
        'logoMode': 'white-card-landscape',
        'logo': {
            'placement': 'corner-anchor',
            'corner': 'top-left',
            'width': 240,
            'height': 56,
            'clearSpace': 12,
            'x': 28,
            'y': 28
        },
        'text': {
            'headline': prim['headline'],
            'subhead': subhead,
            'cta': cta_text,
            'footer': ''
        },
        'theme': {
            # Solid orange CTA — not translucent gray
            'ctaFill': 'rgba(232,93,58,0.95)',
            'ctaStroke': 'none',
            'ctaTextColor': '#ffffff',
            # No panel for these proofs
            'textPanelFill': 'none',
            'textPanelStroke': 'none'
        },
        'typography': {
            'headlineFontFamily': 'Montserrat, Arial, sans-serif',
            'bodyFontFamily': 'Source Sans Pro, Arial, sans-serif',
            'headlineSize': 48,
            'headlineWeight': 800,
            'subheadSize': 24 if subhead else 1,
            'ctaSize': 22,
            'footerSize': 1
        },
        'layout': {
            'personality': 'centered-hero',
            'minHeadlineCtaGap': 40,
            'ctaRectY': cta_y,
            'ctaY': cta_y + 28,
            'ctaWidth': 380,
            'ctaHeight': 56,
            'ctaRadius': 12,
            'headlineY': 130,
            'subheadY': prim.get('subheadY', 310)
        },
        'overlay': {
            # Darker overlay for text readability on real photos
            'leftColor': '5,18,30',
            'midColor': '5,18,30',
            'rightColor': '5,18,30',
            'leftOpacity': 0.72,
            'midOpacity': 0.58,
            'rightOpacity': 0.72,
            'vignetteBottom': 0.25
        },
        'output': output_path,
        **content
    }

    if badges:
        config['badges'] = badges

    return config


def main():
    parser = argparse.ArgumentParser(description='Generate variant proof renders')
    parser.add_argument('--output-dir', default=os.path.join(
        '/mnt/raid/Data/tmp/openclaw-builds/captain-bill/strikeframe', 'variant-proof'))
    args = parser.parse_args()

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Write all configs as a batch
    renders = []
    manifest = []

    for prim_name, prim_def in PRIMITIVES.items():
        for variant in prim_def['variants']:
            filename = f'{prim_name}-{variant}.jpg'
            output_path = os.path.join(output_dir, filename)
            config = build_config(prim_name, variant, output_path)
            renders.append(config)
            manifest.append({
                'primitive': prim_name,
                'variant': variant,
                'output': output_path,
                'critic': output_path.replace('.jpg', '.critic.json')
            })

    # Write batch config
    batch_path = os.path.join(output_dir, 'variant-proof-batch.json')
    # Render individually since each config is self-contained
    results = []
    for i, config in enumerate(renders):
        entry = manifest[i]
        config_path = os.path.join(output_dir, f'_tmp_{entry["primitive"]}-{entry["variant"]}.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        result = subprocess.run(
            ['node', RENDER_JS, config_path],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        if result.returncode != 0:
            print(f'  FAIL: {entry["primitive"]}-{entry["variant"]}: {result.stderr.strip()}')
            entry['status'] = 'fail'
            entry['error'] = result.stderr.strip()
        else:
            try:
                render_data = json.loads(result.stdout)
                if isinstance(render_data, list):
                    render_data = render_data[0]
                entry['criticScore'] = render_data.get('criticScore', 0)
                entry['criticStatus'] = render_data.get('criticStatus', 'unknown')
                entry['status'] = 'ok'
                print(f'  OK: {entry["primitive"]}-{entry["variant"]} — critic {entry["criticScore"]}/100 ({entry["criticStatus"]})')
            except json.JSONDecodeError:
                entry['status'] = 'ok'
                entry['criticScore'] = 0
                print(f'  OK: {entry["primitive"]}-{entry["variant"]} (no critic data)')

        # Clean up temp config
        os.remove(config_path)
        results.append(entry)

    # Write manifest
    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Summary
    ok = sum(1 for r in results if r['status'] == 'ok')
    fail = sum(1 for r in results if r['status'] == 'fail')
    print(f'\n{ok}/{len(results)} renders succeeded, {fail} failed')
    print(f'Output: {output_dir}')
    print(f'Manifest: {manifest_path}')

    # Build proof sheet
    build_proof_sheet(results, output_dir)

    return 0 if fail == 0 else 1


def build_proof_sheet(results, output_dir):
    """Assemble a labeled contact sheet using ImageMagick montage."""
    # Check if montage is available
    check = subprocess.run(['which', 'montage'], capture_output=True)
    if check.returncode != 0:
        print('WARNING: ImageMagick montage not found — skipping proof sheet')
        return

    ok_results = [r for r in results if r['status'] == 'ok' and os.path.exists(r['output'])]
    if not ok_results:
        print('No successful renders to assemble')
        return

    # Group by primitive
    by_primitive = {}
    for r in ok_results:
        by_primitive.setdefault(r['primitive'], []).append(r)

    # Build one row per primitive — labeled tiles
    labeled_tiles = []
    for prim_name, prim_results in by_primitive.items():
        for r in prim_results:
            score = r.get('criticScore', '?')
            status = r.get('criticStatus', '?')
            label = f'{prim_name}\\n{r["variant"]}\\n{score}/100 ({status})'

            # Create labeled tile
            labeled_path = r['output'].replace('.jpg', '-labeled.jpg')
            subprocess.run([
                'convert', r['output'],
                '-gravity', 'South',
                '-background', '#111111',
                '-fill', '#ffffff',
                '-font', 'DejaVu-Sans',
                '-pointsize', '24',
                '-splice', '0x80',
                '-annotate', '+0+10', label,
                '-resize', '400x480',
                labeled_path
            ], capture_output=True)
            if os.path.exists(labeled_path):
                labeled_tiles.append(labeled_path)
            else:
                labeled_tiles.append(r['output'])

    if not labeled_tiles:
        return

    # Montage — max 5 columns
    proof_path = os.path.join(output_dir, 'proof-sheet.jpg')
    cols = min(5, max(len(v) for v in by_primitive.values()))
    subprocess.run([
        'montage',
        *labeled_tiles,
        '-tile', f'{cols}x',
        '-geometry', '400x480+4+4',
        '-background', '#1a1a1a',
        proof_path
    ], capture_output=True)

    if os.path.exists(proof_path):
        print(f'Proof sheet: {proof_path}')
    else:
        print('WARNING: Proof sheet assembly failed')

    # Clean up labeled tiles
    for t in labeled_tiles:
        if t.endswith('-labeled.jpg') and os.path.exists(t):
            os.remove(t)


if __name__ == '__main__':
    sys.exit(main())
