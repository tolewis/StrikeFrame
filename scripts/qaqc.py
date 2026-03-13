#!/usr/bin/env python3
"""
StrikeFrame QA/QC — Pre-render validation, alignment correction, and grading.

Usage:
    python3 scripts/qaqc.py configs/my-config.json
    python3 scripts/qaqc.py configs/my-batch.json

Flow:
    1. Load config (handles batch manifests)
    2. Pre-render: detect and fix alignment issues in the config
    3. Render via node scripts/render.js
    4. Post-render: read review.json, grade composition
    5. If fixable issues found: correct config, re-render ONCE
    6. Output final grade report

Circuit breaker: max 1 correction pass. No loops.
"""

import json
import subprocess
import sys
import os
import copy
import tempfile
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RENDER_SCRIPT = PROJECT_ROOT / "scripts" / "render.js"

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return json.load(f)


def is_batch(cfg: dict) -> bool:
    return "renders" in cfg and isinstance(cfg["renders"], list)


def flatten_batch(cfg: dict) -> list[dict]:
    """Expand a batch manifest into individual render configs."""
    if not is_batch(cfg):
        return [cfg]
    defaults = cfg.get("defaults", {})
    out = []
    for item in cfg["renders"]:
        merged = deep_merge(copy.deepcopy(defaults), item)
        out.append(merged)
    return out


def deep_merge(base: dict, override: dict) -> dict:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


# ---------------------------------------------------------------------------
# Pre-render alignment checks
# ---------------------------------------------------------------------------

def check_alignment(cfg: dict) -> dict:
    """Analyze a single render config for alignment issues. Returns fixes dict."""
    fixes = {}
    stat_blocks = cfg.get("statBlocks", [])
    dividers = cfg.get("dividers", [])

    if len(stat_blocks) >= 2:
        fixes.update(fix_stat_block_alignment(stat_blocks))

    if dividers and stat_blocks:
        fixes.update(fix_divider_alignment(stat_blocks, dividers))

    return fixes


def fix_stat_block_alignment(blocks: list) -> dict:
    """Snap stat blocks to consistent row/column grid."""
    fixes = {"stat_block_fixes": []}

    # Group by Y proximity (within 40px = same row)
    rows = group_by_proximity([b["y"] for b in blocks], threshold=40)

    # Within each row, snap all blocks to the rounded average Y
    for row_indices in rows.values():
        if len(row_indices) < 2:
            continue
        ys = [blocks[i]["y"] for i in row_indices]
        avg_y = round(sum(ys) / len(ys))
        for i in row_indices:
            if blocks[i]["y"] != avg_y:
                fixes["stat_block_fixes"].append(
                    f"Block '{blocks[i].get('label',i)}' y: {blocks[i]['y']} -> {avg_y}"
                )
                blocks[i]["y"] = avg_y

    # Check column alignment across rows
    row_list = sorted(rows.keys())
    if len(row_list) >= 2:
        row_blocks = {}
        for row_y, indices in rows.items():
            sorted_indices = sorted(indices, key=lambda i: blocks[i]["x"])
            row_blocks[row_y] = sorted_indices

        # If rows have the same column count, compute ideal evenly-spaced grid
        col_counts = [len(v) for v in row_blocks.values()]
        if len(set(col_counts)) == 1:
            num_cols = col_counts[0]

            # Average X per column across all rows
            col_avgs = []
            col_all_indices = []
            for col_idx in range(num_cols):
                col_xs = []
                indices = []
                for row_y in row_list:
                    idx = row_blocks[row_y][col_idx]
                    col_xs.append(blocks[idx]["x"])
                    indices.append(idx)
                col_avgs.append(round(sum(col_xs) / len(col_xs)))
                col_all_indices.append(indices)

            # Compute ideal evenly-spaced grid from the averaged positions
            if num_cols >= 2:
                left = col_avgs[0]
                right = col_avgs[-1]
                step = (right - left) / (num_cols - 1)
                ideal_xs = [round(left + step * i) for i in range(num_cols)]
            else:
                ideal_xs = col_avgs

            # Snap all blocks to the ideal grid
            for col_idx in range(num_cols):
                target_x = ideal_xs[col_idx]
                for i in col_all_indices[col_idx]:
                    if blocks[i]["x"] != target_x:
                        fixes["stat_block_fixes"].append(
                            f"Block '{blocks[i].get('label',i)}' x: {blocks[i]['x']} -> {target_x}"
                        )
                        blocks[i]["x"] = target_x

    if not fixes["stat_block_fixes"]:
        del fixes["stat_block_fixes"]
    return fixes


def fix_divider_alignment(blocks: list, dividers: list) -> dict:
    """Snap dividers to sit between stat block columns."""
    fixes = {"divider_fixes": []}

    # Get unique X positions from stat blocks (columns)
    col_xs = sorted(set(b["x"] for b in blocks))
    if len(col_xs) < 2:
        return {}

    # Calculate midpoints between adjacent columns
    midpoints = []
    for i in range(len(col_xs) - 1):
        midpoints.append(round((col_xs[i] + col_xs[i + 1]) / 2))

    # Group dividers by Y proximity to find which row they belong to
    row_ys = sorted(set(b["y"] for b in blocks))
    for div in dividers:
        if div.get("type") == "vertical" or div.get("height", 0) > div.get("width", 1):
            # Find nearest midpoint for this divider's X
            if midpoints:
                nearest = min(midpoints, key=lambda m: abs(m - div["x"]))
                if abs(nearest - div["x"]) <= 60 and div["x"] != nearest:
                    fixes["divider_fixes"].append(
                        f"Divider at x={div['x']} -> {nearest}"
                    )
                    div["x"] = nearest

    if not fixes["divider_fixes"]:
        del fixes["divider_fixes"]
    return fixes


def group_by_proximity(values: list, threshold: int = 40) -> dict:
    """Group indices by value proximity. Returns {representative_value: [indices]}."""
    if not values:
        return {}
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    groups = {}
    current_group_val = indexed[0][1]
    current_group = [indexed[0][0]]

    for i in range(1, len(indexed)):
        if indexed[i][1] - current_group_val <= threshold:
            current_group.append(indexed[i][0])
        else:
            groups[current_group_val] = current_group
            current_group_val = indexed[i][1]
            current_group = [indexed[i][0]]
    groups[current_group_val] = current_group
    return groups


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render(config_path: str) -> list[dict]:
    """Run node render.js and return results."""
    result = subprocess.run(
        ["node", str(RENDER_SCRIPT), config_path],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        timeout=120
    )
    if result.returncode != 0:
        print(f"  RENDER ERROR: {result.stderr.strip()}", file=sys.stderr)
        return []
    try:
        data = json.loads(result.stdout)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        print(f"  PARSE ERROR: {result.stdout[:200]}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Post-render review
# ---------------------------------------------------------------------------

def read_review(review_path: str) -> dict | None:
    if not os.path.exists(review_path):
        return None
    with open(review_path) as f:
        return json.load(f)


def grade_review(review: dict) -> dict:
    """Grade a review into structured feedback."""
    grade = {
        "status": review.get("status", "unknown"),
        "composition_overall": review.get("composition", {}).get("overall", 0),
        "composition_scores": review.get("composition", {}),
        "failures": review.get("failures", []),
        "warnings": review.get("warnings", []),
        "fixable": [],
    }

    # Identify fixable issues (things we can correct in config)
    for check in review.get("checks", []):
        name = check.get("name", "")
        if not check.get("pass", True):
            if "margin" in name or "padding" in name:
                grade["fixable"].append({"check": name, "type": "spacing", "value": check.get("value")})
            elif "thirds" in name:
                grade["fixable"].append({"check": name, "type": "composition", "value": check.get("value")})
            elif "hierarchy" in name:
                grade["fixable"].append({"check": name, "type": "typography", "value": check.get("value")})
            elif "utilization" in name:
                grade["fixable"].append({"check": name, "type": "layout", "value": check.get("value")})

    return grade


def attempt_auto_fix(cfg: dict, grade: dict) -> tuple[dict, list[str]]:
    """Attempt to auto-fix issues identified in review. Returns (fixed_cfg, fix_descriptions)."""
    fixed = copy.deepcopy(cfg)
    descriptions = []

    for issue in grade.get("fixable", []):
        check = issue["check"]
        itype = issue["type"]

        if itype == "spacing" and "margin" in check:
            # Push text inward if too close to edge
            layout = fixed.get("layout", {})
            if layout.get("leftX", 80) < 60:
                old = layout["leftX"]
                layout["leftX"] = 80
                descriptions.append(f"leftX: {old} -> 80 (edge margin)")

        if itype == "typography" and "hierarchy" in check:
            typo = fixed.get("typography", {})
            hl = typo.get("headlineSize", 42)
            sh = typo.get("subheadSize", 22)
            if hl / max(sh, 1) < 1.4:
                new_sh = int(hl / 1.5)
                descriptions.append(f"subheadSize: {sh} -> {new_sh} (hierarchy ratio)")
                typo["subheadSize"] = new_sh

    return fixed, descriptions


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_report(results: list[dict]):
    """Print final graded report."""
    total = len(results)
    pass_count = sum(1 for r in results if r["final_status"] == "pass")
    warn_count = sum(1 for r in results if r["final_status"] == "warn")
    fail_count = sum(1 for r in results if r["final_status"] == "fail")
    avg_comp = round(sum(r["composition_overall"] for r in results) / max(total, 1))

    print("\n" + "=" * 60)
    print("STRIKEFRAME QA/QC REPORT")
    print("=" * 60)

    for r in results:
        status_icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}.get(r["final_status"], "????")
        comp = r["composition_overall"]
        print(f"\n  [{status_icon}] {os.path.basename(r['output'])}")
        print(f"         Composition: {comp}/100")
        if r.get("pre_fixes"):
            print(f"         Pre-render fixes: {len(r['pre_fixes'])}")
            for f in r["pre_fixes"]:
                print(f"           - {f}")
        if r.get("post_fixes"):
            print(f"         Post-render fixes: {len(r['post_fixes'])}")
            for f in r["post_fixes"]:
                print(f"           - {f}")
        if r.get("warnings"):
            for w in r["warnings"]:
                print(f"         ! {w}")
        if r.get("failures"):
            for f in r["failures"]:
                print(f"         X {f}")

    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {total}  |  PASS: {pass_count}  |  WARN: {warn_count}  |  FAIL: {fail_count}")
    print(f"  AVG COMPOSITION: {avg_comp}/100")
    print(f"{'=' * 60}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/qaqc.py <config.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    if not os.path.isabs(config_path):
        config_path = str(PROJECT_ROOT / config_path)

    raw = load_config(config_path)
    batch = is_batch(raw)
    configs = flatten_batch(raw)
    all_results = []

    print(f"StrikeFrame QA/QC — {len(configs)} render(s)")
    print("-" * 40)

    for idx, cfg in enumerate(configs):
        label = cfg.get("_comment", cfg.get("output", f"render-{idx+1}"))
        print(f"\n[{idx+1}/{len(configs)}] {label}")

        # --- Phase 1: Pre-render alignment ---
        pre_fixes = check_alignment(cfg)
        pre_fix_list = []
        for category, items in pre_fixes.items():
            if isinstance(items, list):
                pre_fix_list.extend(items)
        if pre_fix_list:
            print(f"  Pre-render: {len(pre_fix_list)} alignment fix(es) applied")
            # Write corrected config back into the batch
            if batch:
                raw["renders"][idx] = rebuild_overrides(raw.get("defaults", {}), cfg)

        # --- Phase 2: Render ---
        # Write potentially corrected config to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", dir=str(PROJECT_ROOT / "configs"),
            delete=False, prefix="qaqc-"
        ) as tmp:
            if batch:
                # For batch, write just this single render
                json.dump(cfg, tmp, indent=2)
            else:
                json.dump(cfg, tmp, indent=2)
            tmp_path = tmp.name

        try:
            results = render(tmp_path)
        finally:
            os.unlink(tmp_path)

        if not results:
            all_results.append({
                "output": cfg.get("output", "unknown"),
                "final_status": "fail",
                "composition_overall": 0,
                "pre_fixes": pre_fix_list,
                "post_fixes": [],
                "warnings": ["Render failed"],
                "failures": ["Render produced no output"],
            })
            continue

        result = results[0]
        review = read_review(result.get("reviewPath", ""))

        if not review:
            all_results.append({
                "output": result.get("output", "unknown"),
                "final_status": "warn",
                "composition_overall": 0,
                "pre_fixes": pre_fix_list,
                "post_fixes": [],
                "warnings": ["No review.json found"],
                "failures": [],
            })
            continue

        grade = grade_review(review)
        print(f"  Render 1: status={grade['status']}  composition={grade['composition_overall']}/100")

        # --- Phase 3: Post-render correction (ONE pass max) ---
        post_fix_list = []
        if grade["fixable"] and grade["status"] in ("warn", "fail"):
            fixed_cfg, post_fixes = attempt_auto_fix(cfg, grade)
            if post_fixes:
                post_fix_list = post_fixes
                print(f"  Correction pass: {len(post_fixes)} fix(es)")

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", dir=str(PROJECT_ROOT / "configs"),
                    delete=False, prefix="qaqc-fix-"
                ) as tmp2:
                    json.dump(fixed_cfg, tmp2, indent=2)
                    tmp2_path = tmp2.name

                try:
                    results2 = render(tmp2_path)
                finally:
                    os.unlink(tmp2_path)

                if results2:
                    result = results2[0]
                    review = read_review(result.get("reviewPath", ""))
                    if review:
                        grade = grade_review(review)
                        print(f"  Render 2: status={grade['status']}  composition={grade['composition_overall']}/100")
        else:
            print(f"  No fixable issues — skipping correction pass")

        all_results.append({
            "output": result.get("output", "unknown"),
            "final_status": grade["status"],
            "composition_overall": grade["composition_overall"],
            "composition_scores": grade.get("composition_scores", {}),
            "pre_fixes": pre_fix_list,
            "post_fixes": post_fix_list,
            "warnings": grade.get("warnings", []),
            "failures": grade.get("failures", []),
        })

    # --- Final Report ---
    print_report(all_results)

    # Write machine-readable report
    report_path = config_path.replace(".json", ".qaqc-report.json")
    with open(report_path, "w") as f:
        json.dump({"renders": all_results}, f, indent=2)
    print(f"Report saved: {report_path}")

    # Exit code: 0 = all pass, 1 = has warnings, 2 = has failures
    if any(r["final_status"] == "fail" for r in all_results):
        sys.exit(2)
    elif any(r["final_status"] == "warn" for r in all_results):
        sys.exit(1)
    sys.exit(0)


def rebuild_overrides(defaults: dict, merged: dict) -> dict:
    """Reconstruct override dict from merged config (best-effort for batch writeback)."""
    # For batch configs, we just return the merged config since we render individually
    return merged


if __name__ == "__main__":
    main()
