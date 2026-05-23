#!/usr/bin/env python3
"""Build a compact user-facing preview/delivery summary for a director pack."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from control_strategy_requirements import infer_requirements


REPORT_NAME = "16_user_preview_summary.md"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def first_image(path: Path) -> str | None:
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
        return str(path)
    if path.is_dir():
        for item in sorted(path.iterdir()):
            if item.suffix.lower() in IMAGE_EXTS:
                return str(item)
    return None


def asset_line(package_dir: Path, role: str, asset: dict) -> str:
    status = asset.get("status", "missing") if isinstance(asset, dict) else "missing"
    path_value = asset.get("path") if isinstance(asset, dict) else None
    if path_value:
        image = first_image(package_dir / str(path_value))
        if image:
            try:
                path_text = str(Path(image).relative_to(package_dir)).replace("\\", "/")
            except ValueError:
                path_text = image
            return f"- {role}: {status}, image={path_text}"
        return f"- {role}: {status}, path={path_value}"
    return f"- {role}: {status}"


def read_verdict(package_dir: Path) -> str:
    for name in ("15_preflight_qc.md", "15_visual_asset_review.md", "16_preproduction_orchestrator_report.md"):
        path = package_dir / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            if line.lower().startswith("- verdict:"):
                return line.split(":", 1)[1].strip()
    return "not run"


def build_summary(package_dir: Path, manifest: dict, *, phase: str) -> str:
    requirements = infer_requirements(package_dir, manifest)
    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict):
        assets = {}
    segments = manifest.get("segments", [])
    segment_count = len(segments) if isinstance(segments, list) else 0
    verdict = read_verdict(package_dir)

    lines = [
        "# User Preview Summary",
        "",
        f"- Project: {manifest.get('project_title') or package_dir.name}",
        f"- Duration: {manifest.get('target_duration') or 'not recorded'}",
        f"- Aspect ratio: {manifest.get('aspect_ratio') or '16:9'}",
        f"- Phase: {phase}",
        f"- Control strategy: {manifest.get('control_strategy') or 'not recorded'}",
        f"- Layout: {manifest.get('layout_pattern') or 'not recorded'}",
        f"- Segments: {segment_count}",
        f"- Current verdict: {verdict}",
        "",
        "## User-Facing One-Line Plan",
        "",
        (
            f"{manifest.get('project_title') or package_dir.name} - "
            f"{manifest.get('target_duration') or 'duration TBD'}, "
            f"{manifest.get('aspect_ratio') or '16:9'}, "
            f"{manifest.get('layout_pattern') or 'storyboard layout TBD'}, "
            f"strategy={manifest.get('control_strategy') or 'TBD'}."
        ),
        "",
        "## Required Visual Assets",
        "",
        f"- Required now: {', '.join(sorted(requirements.required_assets)) or 'none inferred'}",
        f"- Recommended for final: {', '.join(sorted(requirements.recommended_assets)) or 'none inferred'}",
        "",
        "## Asset Status",
        "",
    ]
    if assets:
        for role in sorted(assets):
            asset = assets.get(role, {})
            lines.append(asset_line(package_dir, role, asset if isinstance(asset, dict) else {}))
    else:
        lines.append("- No reference assets registered.")

    prompt_path = package_dir / "12_video_generation_prompt" / "video_generation_prompt_concise_seedance.txt"
    handoff_path = package_dir / "17_generation_handoff" / "video_prompt_for_upload.txt"
    lines.extend(
        [
            "",
            "## Handoff Files",
            "",
            f"- Concise video prompt: {'available' if prompt_path.exists() else 'missing'}",
            f"- Final upload prompt: {'available' if handoff_path.exists() else 'missing'}",
            "",
            "## User Reply Guidance",
            "",
            "- Show the project folder, main storyboard image, key reference asset images, and verdict.",
            "- Do not paste every internal prompt unless the user asks for prompt details.",
            "- If any required asset is prompt_only or missing, say the pack is not ready for generation yet.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument("--phase", default="preflight", help="Current phase label for the summary.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: missing manifest: {manifest_path}")
        return 1
    manifest = read_json(manifest_path)
    report_path = package_dir / REPORT_NAME
    report_path.write_text(build_summary(package_dir, manifest, phase=args.phase), encoding="utf-8")
    print(f"Wrote user preview summary: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

