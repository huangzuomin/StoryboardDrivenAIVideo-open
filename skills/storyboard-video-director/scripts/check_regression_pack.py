#!/usr/bin/env python3
"""Run static regression assertions against a storyboard director pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def maybe_read(path: Path) -> str:
    return read_text(path) if path.exists() else ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def pack_text(package_dir: Path) -> str:
    names = [
        "00_control_strategy.md",
        "00_project_brief.md",
        "02_duration_segment_plan.md",
        "03_visual_bible.md",
        "04_beat_storyboard_plan.md",
        "05_annotated_storyboard_prompt.txt",
        "09_editing_plan.md",
        "14_review_summary.md",
    ]
    parts = [maybe_read(package_dir / name) for name in names]
    prompt_dir = package_dir / "12_video_generation_prompt"
    if prompt_dir.is_dir():
        parts.extend(maybe_read(path) for path in sorted(prompt_dir.glob("*.txt")))
    return "\n\n".join(part for part in parts if part).lower()


def expected_terms_for_case(case_id: str) -> list[str]:
    normalized = case_id.strip().lower()
    cases = {
        "04": ["4x3_trailer_grid", "12", "suspense"],
        "05": ["rhythm", "rope", "15s", "slow"],
        "14": ["face_emotion_flow", "4_panel_horizontal_flow", "phone"],
        "16": ["quiet_discovery_reveal_flow", "object lock", "robot", "emotion lite"],
    }
    return cases.get(normalized, [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--case-id",
        default="",
        help="Optional reproduction test case id, e.g. 04, 05, 14, 16.",
    )
    parser.add_argument(
        "--expect",
        action="append",
        default=[],
        help="Additional required text or /regex/ pattern. Can be repeated.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    manifest_path = package_dir / "10_generation_manifest.json"
    errors: list[str] = []
    passes: list[str] = []

    if not manifest_path.exists():
        print(f"ERROR: missing manifest: {manifest_path}")
        return 1
    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: manifest is not valid JSON: {exc}")
        return 1

    text = pack_text(package_dir)

    required_files = [
        "00_control_strategy.md",
        "00_project_brief.md",
        "02_duration_segment_plan.md",
        "03_visual_bible.md",
        "04_beat_storyboard_plan.md",
        "05_annotated_storyboard_prompt.txt",
        "08_segment_beat_mapping.json",
        "09_editing_plan.md",
        "10_generation_manifest.json",
    ]
    for name in required_files:
        if (package_dir / name).exists():
            passes.append(f"file exists: {name}")
        else:
            errors.append(f"missing file: {name}")

    for key in ("control_strategy", "layout_pattern", "reference_assets", "user_hard_constraints"):
        if manifest.get(key):
            passes.append(f"manifest has {key}")
        else:
            errors.append(f"manifest missing {key}")

    for segment in manifest.get("segments", []):
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("segment_id", "Segment")
        for key in ("control_mode", "execution_mode"):
            if segment.get(key):
                passes.append(f"{seg_id} has {key}")
            else:
                errors.append(f"{seg_id} missing {key}")

    prompt_text = maybe_read(package_dir / "12_video_generation_prompt" / "video_generation_prompt_concise_seedance.txt").lower()
    for phrase in (
        "ordered cinematic beat",
        "do not skip, merge, reorder, or reinterpret",
        "do not render storyboard",
    ):
        if phrase in prompt_text:
            passes.append(f"concise prompt has adherence phrase: {phrase}")
        else:
            errors.append(f"concise prompt missing adherence phrase: {phrase}")

    expectations = expected_terms_for_case(args.case_id) + args.expect
    for expected in expectations:
        if expected.startswith("/") and expected.endswith("/") and len(expected) > 2:
            pattern = expected[1:-1]
            if re.search(pattern, text):
                passes.append(f"matched regex: {pattern}")
            else:
                errors.append(f"missing regex: {pattern}")
        elif expected.lower() in text or expected.lower() in json.dumps(manifest, ensure_ascii=False).lower():
            passes.append(f"found expected term: {expected}")
        else:
            errors.append(f"missing expected term: {expected}")

    if passes:
        print("Regression checks passed:")
        for item in passes:
            print(f"- {item}")

    if errors:
        print("Regression checks failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("All regression checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
