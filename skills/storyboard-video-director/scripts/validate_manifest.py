#!/usr/bin/env python3
"""Validate the generation manifest for a storyboard director pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_TOP_LEVEL = {
    "project_title",
    "workflow_version",
    "skill_versions",
    "target_duration",
    "aspect_ratio",
    "storyboard_type",
    "video_model",
    "seedance2_segment_limit",
    "segments",
}

REQUIRED_SEGMENT_KEYS = {
    "segment_id",
    "duration",
    "function",
    "reference_beats",
    "clean_keyframes",
    "prompt_file",
    "transition_out",
}

VALID_ASPECT_RATIOS = {"16:9", "9:16", "1:1", "4:5"}

VALID_CONTROL_MODES = {
    "storyboard_heavy",
    "face_emotion_flow",
    "rhythm_performance_board",
    "body_driven_transformation",
    "product_lock",
    "object_lock",
    "hybrid",
    "emotion_lite",
}

VALID_EXECUTION_MODES = {
    "single_continuous_shot",
    "coherent_multi_shot_sequence",
    "motivated_camera_changes",
    "match_cut_sequence",
}

VALID_REFERENCE_STATUSES = {
    "missing",
    "generated",
    "user_supplied",
    "prompt_only",
    "not_needed",
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

REQUIRED_REFERENCE_ASSETS = {
    "storyboard_control",
    "character_reference",
    "prop_reference",
    "environment_reference",
    "style_reference",
    "clean_keyframe_reference",
}


def parse_seconds(value: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*s", str(value).lower())
    if not match:
        return None
    return float(match.group(1))


def supported_images(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.suffix.lower() in IMAGE_EXTS)
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
        return [path]
    return []


def asset_is_real_image(package_dir: Path, asset: dict) -> bool:
    if asset.get("status") not in {"generated", "user_supplied"}:
        return False
    path_value = asset.get("path")
    if not path_value:
        return False
    path = package_dir / str(path_value)
    if not path.exists():
        return False
    return bool(supported_images(path))


def manifest_modes(data: dict) -> set[str]:
    modes: set[str] = set()
    if data.get("control_strategy"):
        modes.add(str(data.get("control_strategy", "")).lower())
    for segment in data.get("segments", []):
        if not isinstance(segment, dict):
            continue
        for key in ("control_mode", "execution_mode", "mode"):
            value = segment.get(key)
            if value:
                modes.add(str(value).lower())
    return modes


def allows_dense_reference_beats(data: dict, segment: dict) -> bool:
    layout = str(data.get("layout_pattern", "")).lower()
    control_mode = str(segment.get("control_mode") or segment.get("mode") or "").lower()
    dense_layout = any(
        token in layout
        for token in (
            "12_panel_rhythm_sheet",
            "16_panel_action_sheet",
            "rhythm",
            "action_sheet",
        )
    )
    dense_control = control_mode in {
        "rhythm_performance_board",
        "body_driven_transformation",
    }
    seconds = parse_seconds(segment.get("duration", "")) or 0
    return seconds <= 15 and (dense_layout or dense_control)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", help="Path to 10_generation_manifest.json")
    parser.add_argument(
        "--strict-current-schema",
        action="store_true",
        help="Require current-schema fields such as reference_assets and user_hard_constraints.",
    )
    parser.add_argument(
        "--allow-prompt-only-product-lock",
        action="store_true",
        help="Allow product/object-lock prompt-only central assets for explicitly text-only planning drafts.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest).expanduser().resolve()
    package_dir = manifest_path.parent
    errors: list[str] = []

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: manifest is not valid JSON: {exc}")
        return 1

    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        errors.append(f"missing top-level keys: {', '.join(sorted(missing))}")

    if data.get("aspect_ratio") not in VALID_ASPECT_RATIOS:
        errors.append(
            "aspect_ratio must be one of: " + ", ".join(sorted(VALID_ASPECT_RATIOS))
        )
    if data.get("storyboard_type") != "beat_storyboard":
        errors.append("storyboard_type must be beat_storyboard")
    if data.get("video_model") != "seedance2":
        errors.append("video_model must be seedance2")

    segments = data.get("segments", [])
    if not isinstance(segments, list):
        errors.append("segments must be a list")
        segments = []

    reference_assets = data.get("reference_assets", {})
    if args.strict_current_schema and not reference_assets:
        errors.append("reference_assets is required in strict current-schema mode")
    if reference_assets:
        if not isinstance(reference_assets, dict):
            errors.append("reference_assets must be an object")
        else:
            missing_assets = REQUIRED_REFERENCE_ASSETS - reference_assets.keys()
            if missing_assets:
                errors.append(
                    "reference_assets missing roles: "
                    + ", ".join(sorted(missing_assets))
                )
            for role, asset in reference_assets.items():
                if not isinstance(asset, dict):
                    errors.append(f"reference_assets.{role} must be an object")
                    continue
                status = asset.get("status")
                if status not in VALID_REFERENCE_STATUSES:
                    errors.append(
                        f"reference_assets.{role}.status must be one of: "
                        + ", ".join(sorted(VALID_REFERENCE_STATUSES))
                    )
                if not asset.get("role"):
                    errors.append(f"reference_assets.{role}.role is required")
                path_value = asset.get("path")
                if status in {"generated", "user_supplied", "prompt_only"} and path_value:
                    path = package_dir / str(path_value)
                    if not path.exists():
                        errors.append(f"reference_assets.{role}.path does not exist: {path_value}")

    if args.strict_current_schema and "user_hard_constraints" not in data:
        errors.append("user_hard_constraints is required in strict current-schema mode")
    if args.strict_current_schema:
        workflow_version = str(data.get("workflow_version", "")).strip()
        if not workflow_version:
            errors.append("workflow_version is required in strict current-schema mode")
        skill_versions = data.get("skill_versions")
        if not isinstance(skill_versions, dict):
            errors.append("skill_versions is required in strict current-schema mode")
        else:
            for skill_name in ("storyboard-video-director", "storyboard-video-qc"):
                if not str(skill_versions.get(skill_name, "")).strip():
                    errors.append(f"skill_versions.{skill_name} is required in strict current-schema mode")

        modes = manifest_modes(data)
        product_lock = any(mode in {"product_lock", "object_lock"} for mode in modes)
        if product_lock and isinstance(reference_assets, dict):
            required_real_roles = ("prop_reference", "storyboard_control")
            for role in required_real_roles:
                asset = reference_assets.get(role, {})
                if (
                    not args.allow_prompt_only_product_lock
                    and (not isinstance(asset, dict) or not asset_is_real_image(package_dir, asset))
                ):
                    status = asset.get("status", "missing") if isinstance(asset, dict) else "invalid"
                    path_value = asset.get("path", "none") if isinstance(asset, dict) else "none"
                    errors.append(
                        "product/object-lock strict delivery requires real generated or "
                        f"user-supplied image asset for reference_assets.{role}; "
                        f"got status={status}, path={path_value}"
                    )

    for index, segment in enumerate(segments, start=1):
        if not isinstance(segment, dict):
            errors.append(f"segment {index} must be an object")
            continue

        seg_id = segment.get("segment_id", f"segment {index}")
        missing_segment = REQUIRED_SEGMENT_KEYS - segment.keys()
        if missing_segment:
            errors.append(f"{seg_id}: missing keys: {', '.join(sorted(missing_segment))}")

        seconds = parse_seconds(segment.get("duration", ""))
        if seconds is None:
            errors.append(f"{seg_id}: duration must include seconds, e.g. 12s")
        elif seconds > 15:
            errors.append(f"{seg_id}: duration exceeds Seedance2 15s limit")
        elif seconds < 5:
            errors.append(f"{seg_id}: duration is below recommended 5s minimum")

        legacy_mode = segment.get("mode")
        control_mode = segment.get("control_mode")
        execution_mode = segment.get("execution_mode")
        if args.strict_current_schema:
            if not control_mode:
                errors.append(f"{seg_id}: control_mode is required in strict current-schema mode")
            if not execution_mode:
                errors.append(f"{seg_id}: execution_mode is required in strict current-schema mode")
        if legacy_mode and not control_mode and not execution_mode:
            if legacy_mode in VALID_EXECUTION_MODES:
                execution_mode = legacy_mode
            elif legacy_mode in VALID_CONTROL_MODES:
                control_mode = legacy_mode

        if control_mode and control_mode not in VALID_CONTROL_MODES:
            errors.append(f"{seg_id}: invalid control_mode {control_mode!r}")
        if execution_mode and execution_mode not in VALID_EXECUTION_MODES:
            errors.append(f"{seg_id}: invalid execution_mode {execution_mode!r}")
        if not control_mode and not execution_mode:
            errors.append(
                f"{seg_id}: provide control_mode and/or execution_mode, or a valid legacy mode"
            )

        reference_beats = segment.get("reference_beats", [])
        if not isinstance(reference_beats, list) or not reference_beats:
            errors.append(f"{seg_id}: reference_beats must be a non-empty list")
        elif len(reference_beats) > 5 and not allows_dense_reference_beats(data, segment):
            errors.append(f"{seg_id}: more than 5 reference beats; split the segment")
        elif len(reference_beats) > 16:
            errors.append(f"{seg_id}: more than 16 reference beats; split the segment")

        for file_key in ("prompt_file",):
            file_value = segment.get(file_key)
            if file_value and not (package_dir / file_value).exists():
                errors.append(f"{seg_id}: {file_key} does not exist: {file_value}")

        clean_keyframes = segment.get("clean_keyframes", [])
        if isinstance(clean_keyframes, list):
            for file_value in clean_keyframes:
                if not (package_dir / file_value).exists():
                    errors.append(f"{seg_id}: clean keyframe file does not exist: {file_value}")

    if errors:
        print("Manifest validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Manifest validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
