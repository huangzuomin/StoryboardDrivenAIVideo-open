#!/usr/bin/env python3
"""Write review status and summary files for a storyboard director pack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


STATUS_FILE = "14_review_status.md"
SUMMARY_FILE = "14_review_summary.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def exists_nonempty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def run_validation(package_dir: Path) -> tuple[str, str]:
    script_dir = Path(__file__).resolve().parent
    result = subprocess.run(
        [sys.executable, str(script_dir / "validate_package.py"), str(package_dir)],
        text=True,
        capture_output=True,
        check=False,
    )
    status = "passed" if result.returncode == 0 else "failed"
    details = (result.stdout or result.stderr).strip()
    return status, details


def discover_storyboards(package_dir: Path) -> tuple[list[Path], list[Path]]:
    storyboard_dir = package_dir / "11_generated_storyboards"
    if not storyboard_dir.is_dir():
        return [], []
    images = sorted(storyboard_dir.glob("*.png"))
    overview = [path for path in images if "sheet" in path.stem or "overview" in path.stem]
    segment = [path for path in images if path not in overview]
    return overview, segment


def prompt_status(package_dir: Path) -> tuple[str, str]:
    prompt_dir = package_dir / "12_video_generation_prompt"
    full = prompt_dir / "video_generation_prompt_full.txt"
    concise = prompt_dir / "video_generation_prompt_concise_seedance.txt"
    selected = prompt_dir / "video_generation_prompt.txt"
    final_status = "generated" if exists_nonempty(selected) or exists_nonempty(full) else "missing"
    concise_status = "generated" if exists_nonempty(concise) else "missing"
    return final_status, concise_status


def asset_status_lines(manifest: dict) -> list[str]:
    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict) or not assets:
        return ["- reference_assets: missing from manifest"]
    lines = []
    for name, asset in assets.items():
        if not isinstance(asset, dict):
            lines.append(f"- {name}: invalid")
            continue
        status = asset.get("status", "missing")
        path = asset.get("path") or "none"
        role = asset.get("role", "")
        lines.append(f"- {name}: {status}, path={path}, role={role}")
    return lines


def schema_recommendations(manifest: dict) -> list[str]:
    recommendations: list[str] = []
    if "reference_assets" not in manifest:
        recommendations.append("- Run `scripts/upgrade_manifest_schema.py <package_dir> --write` to add reference_assets.")
    if "user_hard_constraints" not in manifest:
        recommendations.append("- Run `scripts/upgrade_manifest_schema.py <package_dir> --write` to add user_hard_constraints.")
    for segment in manifest.get("segments", []):
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("segment_id", "Segment")
        if "control_mode" not in segment or "execution_mode" not in segment:
            recommendations.append(
                f"- Run `scripts/upgrade_manifest_schema.py <package_dir> --write` to split {seg_id} mode into control_mode/execution_mode."
            )
            break
    return recommendations or ["- Manifest appears to use the current schema."]


def user_constraints_lines(manifest: dict) -> list[str]:
    constraints = manifest.get("user_hard_constraints", {})
    if not isinstance(constraints, dict) or not constraints:
        return ["- user_hard_constraints: missing from manifest"]
    lines = []
    for key, value in constraints.items():
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value) or "none"
        lines.append(f"- {key}: {value or 'not recorded'}")
    return lines


def segment_lines(manifest: dict) -> list[str]:
    segments = manifest.get("segments", [])
    if not isinstance(segments, list) or not segments:
        return ["- segments: none recorded"]
    lines = []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("segment_id", "Segment")
        duration = segment.get("duration", "")
        control_mode = segment.get("control_mode") or segment.get("mode") or ""
        execution_mode = segment.get("execution_mode") or ""
        beats = ", ".join(segment.get("reference_beats", []))
        lines.append(
            f"- {seg_id}: {duration}, control={control_mode or 'not recorded'}, "
            f"execution={execution_mode or 'not recorded'}, beats={beats or 'none'}"
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Do not run validate_package.py before writing review files.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: missing manifest: {manifest_path}")
        return 1

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: manifest is not valid JSON: {exc}")
        return 1

    validation_status = "not run"
    validation_details = ""
    if not args.skip_validation:
        validation_status, validation_details = run_validation(package_dir)

    overview_images, segment_images = discover_storyboards(package_dir)
    final_prompt_status, concise_prompt_status = prompt_status(package_dir)

    text_pack_files = [
        "00_control_strategy.md",
        "00_project_brief.md",
        "02_duration_segment_plan.md",
        "03_visual_bible.md",
        "04_beat_storyboard_plan.md",
        "05_annotated_storyboard_prompt.txt",
        "10_generation_manifest.json",
    ]
    text_pack_complete = all(exists_nonempty(package_dir / name) for name in text_pack_files)

    status_lines = [
        "# Review Status",
        "",
        f"- Text director pack: {'complete' if text_pack_complete else 'incomplete'}",
        f"- Package validation: {validation_status}",
        f"- Overview storyboard image: {'generated' if overview_images else 'missing'}",
        f"- Segment storyboard images: {'generated' if segment_images else 'missing'}",
        f"- Final video prompt: {final_prompt_status}",
        f"- Concise video prompt: {concise_prompt_status}",
        f"- Known inconsistencies: {'see validation details' if validation_status == 'failed' else 'none detected'}",
        "- Recommended next action: "
        + (
            "fix validation issues before handoff"
            if validation_status == "failed"
            else "review visual assets and proceed to video handoff when ready"
        ),
    ]
    if validation_details:
        status_lines.extend(["", "## Validation Details", "", "```text", validation_details, "```"])

    summary_lines = [
        "# Review Summary",
        "",
        f"- Project title: {manifest.get('project_title', 'not recorded')}",
        f"- Target duration: {manifest.get('target_duration', 'not recorded')}",
        f"- Aspect ratio: {manifest.get('aspect_ratio', 'not recorded')}",
        f"- Control strategy: {manifest.get('control_strategy', 'not recorded')}",
        f"- Layout pattern: {manifest.get('layout_pattern', 'not recorded')}",
        "",
        "## User Hard Constraints",
        "",
        *user_constraints_lines(manifest),
        "",
        "## Segments",
        "",
        *segment_lines(manifest),
        "",
        "## Reference Asset Status",
        "",
        *asset_status_lines(manifest),
        "",
        "## Schema Status",
        "",
        *schema_recommendations(manifest),
        "",
        "## Downstream Prompt Status",
        "",
        f"- final video prompt: {final_prompt_status}",
        f"- concise Seedance prompt: {concise_prompt_status}",
        "",
        "## Storyboard Image Status",
        "",
        f"- overview images: {', '.join(str(path.relative_to(package_dir)) for path in overview_images) or 'missing'}",
        f"- segment images: {', '.join(str(path.relative_to(package_dir)) for path in segment_images) or 'missing'}",
        "",
        "## Known Adherence Risks",
        "",
        "- Storyboard control remains a soft hint for current video models.",
        "- Annotated storyboard images may contaminate final video if borders, arrows, labels, or dense notes are rendered.",
        "- Multi-Segment projects need Segment-specific storyboard control images for safest handoff.",
        "",
        "## Recommended Fixes Before Video Generation",
        "",
        "- Run package validation and resolve any failures.",
        "- Confirm reference asset roles and statuses in manifest.",
        "- Use concise prompt for model-facing handoff when visual references already carry detail.",
    ]

    (package_dir / STATUS_FILE).write_text("\n".join(status_lines).strip() + "\n", encoding="utf-8")
    (package_dir / SUMMARY_FILE).write_text("\n".join(summary_lines).strip() + "\n", encoding="utf-8")

    print(f"Wrote review status: {package_dir / STATUS_FILE}")
    print(f"Wrote review summary: {package_dir / SUMMARY_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
