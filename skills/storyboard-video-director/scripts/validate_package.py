#!/usr/bin/env python3
"""Validate a storyboard-video-director production pack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = [
    "00_control_strategy.md",
    "00_project_brief.md",
    "01_method_summary.md",
    "02_duration_segment_plan.md",
    "03_visual_bible.md",
    "04_beat_storyboard_plan.md",
    "05_annotated_storyboard_prompt.txt",
    "08_segment_beat_mapping.json",
    "09_editing_plan.md",
    "10_generation_manifest.json",
]

REQUIRED_DIRS = [
    "05_segment_storyboard_prompts",
    "06_clean_keyframe_prompts",
    "07_seedance2_segment_prompts",
]

ANNOTATED_REQUIRED_TERMS = [
    "storyboard",
    "panel",
    "red",
    "blue",
    "green",
    "orange",
    "purple",
]

CLEAN_FORBIDDEN_TERMS = [
    "arrow",
    "arrows",
    "annotation",
    "annotations",
    "panel label",
    "shot number",
    "storyboard border",
    "subtitle",
    "logo",
]

SEGMENT_REQUIRED_PHRASE = "do not treat these reference frames as separate unrelated scenes"

MOJIBAKE_MARKERS = ["锟", "閿", "閺", "閸", "娑", "鈧"]


def read_lower(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").lower()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def positive_prompt_text(content: str) -> str:
    for marker in ("avoid:", "negative prompt:", "do not include:"):
        if marker in content:
            return content.split(marker, 1)[0]
    return content


def segment_ids_from_mapping(path: Path) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return set()
    segments = data.get("segments", []) if isinstance(data, dict) else []
    return {
        str(segment.get("segment_id"))
        for segment in segments
        if isinstance(segment, dict) and segment.get("segment_id")
    }


def mode_for_segment(segment: dict) -> str:
    return (
        str(segment.get("control_mode") or "")
        + " "
        + str(segment.get("execution_mode") or "")
        + " "
        + str(segment.get("mode") or "")
    ).strip().lower()


def contains_mojibake(text: str) -> bool:
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    errors: list[str] = []

    if not package_dir.exists():
        print(f"ERROR: package does not exist: {package_dir}")
        return 1

    for filename in REQUIRED_FILES:
        path = package_dir / filename
        if not path.exists():
            errors.append(f"missing file: {filename}")
        elif filename.endswith((".md", ".txt")) and contains_mojibake(read_text(path)):
            errors.append(f"{filename}: possible mojibake detected")

    for dirname in REQUIRED_DIRS:
        if not (package_dir / dirname).is_dir():
            errors.append(f"missing directory: {dirname}")

    annotated_path = package_dir / "05_annotated_storyboard_prompt.txt"
    if annotated_path.exists():
        annotated = read_lower(annotated_path)
        for term in ANNOTATED_REQUIRED_TERMS:
            if term not in annotated:
                errors.append(f"annotated storyboard prompt missing term: {term}")

    clean_dir = package_dir / "06_clean_keyframe_prompts"
    if clean_dir.is_dir():
        clean_files = sorted(clean_dir.glob("*.txt"))
        if not clean_files:
            errors.append("no clean keyframe prompt files found")
        for path in clean_files:
            content = read_lower(path)
            if contains_mojibake(read_text(path)):
                errors.append(f"{path.name}: possible mojibake detected")
            positive_content = positive_prompt_text(content)
            for term in CLEAN_FORBIDDEN_TERMS:
                if term in positive_content:
                    errors.append(f"{path.name}: clean prompt describes forbidden artifact: {term}")

    segment_dir = package_dir / "07_seedance2_segment_prompts"
    if segment_dir.is_dir():
        segment_files = sorted(segment_dir.glob("*.txt"))
        if not segment_files:
            errors.append("no Seedance2 segment prompt files found")
        for path in segment_files:
            content = read_lower(path)
            if contains_mojibake(read_text(path)):
                errors.append(f"{path.name}: possible mojibake detected")
            if SEGMENT_REQUIRED_PHRASE not in content:
                errors.append(f"{path.name}: missing ordered-reference-frame continuity phrase")

    manifest_path = package_dir / "10_generation_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            manifest = {}
            errors.append(f"manifest is not valid JSON: {exc}")

        segments = manifest.get("segments", []) if isinstance(manifest, dict) else []
        manifest_segment_ids = {
            str(segment.get("segment_id"))
            for segment in segments
            if isinstance(segment, dict) and segment.get("segment_id")
        }
        mapping_ids = segment_ids_from_mapping(package_dir / "08_segment_beat_mapping.json")
        if mapping_ids and manifest_segment_ids and mapping_ids != manifest_segment_ids:
            errors.append(
                "Segment IDs differ between manifest and 08_segment_beat_mapping.json: "
                f"manifest={sorted(manifest_segment_ids)}, mapping={sorted(mapping_ids)}"
            )

        segment_files = sorted((package_dir / "07_seedance2_segment_prompts").glob("*.txt"))
        segment_file_ids = {path.stem for path in segment_files}
        if manifest_segment_ids and segment_file_ids and segment_file_ids != manifest_segment_ids:
            errors.append(
                "Seedance2 prompt files differ from manifest segments: "
                f"manifest={sorted(manifest_segment_ids)}, prompt_files={sorted(segment_file_ids)}"
            )

        control_strategy_text = (
            read_lower(package_dir / "00_control_strategy.md")
            if (package_dir / "00_control_strategy.md").exists()
            else ""
        )
        duration_plan_text = (
            read_lower(package_dir / "02_duration_segment_plan.md")
            if (package_dir / "02_duration_segment_plan.md").exists()
            else ""
        )
        for segment in segments if isinstance(segments, list) else []:
            if not isinstance(segment, dict):
                continue
            seg_id = str(segment.get("segment_id", "")).lower()
            if not seg_id:
                continue
            if len(manifest_segment_ids) > 1 and control_strategy_text and seg_id not in control_strategy_text:
                errors.append(f"{seg_id.upper()}: missing from 00_control_strategy.md")
            if duration_plan_text and seg_id not in duration_plan_text:
                errors.append(f"{seg_id.upper()}: missing from 02_duration_segment_plan.md")
            mode_text = mode_for_segment(segment)
            if mode_text:
                for mode in mode_text.split():
                    if mode and mode not in duration_plan_text:
                        errors.append(f"{seg_id.upper()}: mode {mode!r} missing from duration plan")

        video_prompt_dir = package_dir / "12_video_generation_prompt"
        if video_prompt_dir.is_dir():
            prompt_files = list(video_prompt_dir.glob("*.txt"))
            combined_prompt = "\n".join(read_text(path) for path in prompt_files)
            if contains_mojibake(combined_prompt):
                errors.append("12_video_generation_prompt: possible mojibake detected")
            aspect_ratio = str(manifest.get("aspect_ratio", ""))
            target_duration = str(manifest.get("target_duration", ""))
            if aspect_ratio and aspect_ratio not in combined_prompt:
                errors.append("12_video_generation_prompt: manifest aspect_ratio missing from prompts")
            if target_duration and target_duration not in combined_prompt:
                errors.append("12_video_generation_prompt: manifest target_duration missing from prompts")
            required_adherence = [
                "ordered cinematic beat",
                "do not skip, merge, reorder, or reinterpret",
                "do not render storyboard",
            ]
            prompt_lower = combined_prompt.lower()
            for phrase in required_adherence:
                if phrase not in prompt_lower:
                    errors.append(f"12_video_generation_prompt: missing adherence phrase: {phrase}")

        if isinstance(segments, list) and len(segments) > 1:
            segment_prompt_dir = package_dir / "05_segment_storyboard_prompts"
            for segment in segments:
                if not isinstance(segment, dict):
                    continue
                seg_id = segment.get("segment_id")
                if not seg_id:
                    continue
                prompt_path = segment_prompt_dir / f"{seg_id}_storyboard_prompt.txt"
                if not prompt_path.exists():
                    errors.append(
                        f"{seg_id}: missing Segment-specific storyboard prompt: "
                        f"05_segment_storyboard_prompts/{seg_id}_storyboard_prompt.txt"
                    )

        script_dir = Path(__file__).resolve().parent
        result = subprocess.run(
            [sys.executable, str(script_dir / "validate_manifest.py"), str(manifest_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            errors.append(result.stdout.strip() or result.stderr.strip())

    if errors:
        print("Package validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
