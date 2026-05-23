#!/usr/bin/env python3
"""Upgrade legacy storyboard director manifests to the current schema."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path


EXECUTION_MODES = {
    "single_continuous_shot",
    "coherent_multi_shot_sequence",
    "motivated_camera_changes",
    "match_cut_sequence",
}

CONTROL_MODES = {
    "storyboard_heavy",
    "face_emotion_flow",
    "rhythm_performance_board",
    "body_driven_transformation",
    "product_lock",
    "object_lock",
    "hybrid",
    "emotion_lite",
}

WORKFLOW_VERSION = "0.1.0-alpha"
SKILL_VERSIONS = {
    "storyboard-video-director": WORKFLOW_VERSION,
    "storyboard-video-qc": WORKFLOW_VERSION,
}


DEFAULT_REFERENCE_ASSETS = {
    "storyboard_control": {
        "path": None,
        "status": "missing",
        "role": "controls beat order, camera staging, action path, timing, composition, and emotional progression",
    },
    "character_reference": {
        "path": None,
        "status": "missing",
        "role": "controls identity, costume, proportions, face, and body language",
    },
    "environment_reference": {
        "path": None,
        "status": "missing",
        "role": "controls geography, props, lighting, weather, and spatial continuity",
    },
    "style_reference": {
        "path": None,
        "status": "missing",
        "role": "controls render finish, texture, palette, lens language, and style",
    },
    "clean_keyframe_reference": {
        "path": "06_clean_keyframe_prompts/",
        "status": "prompt_only",
        "role": "controls clean final-frame look without annotations",
    },
}


DEFAULT_USER_HARD_CONSTRAINTS = {
    "target_duration": "",
    "subject_identity": "",
    "location": "",
    "required_final_payoff": "",
    "visual_style": "",
    "explicit_exclusions": [],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path, base: Path) -> str:
    return str(path.relative_to(base)).replace("\\", "/")


def infer_control_strategy(manifest: dict) -> str:
    existing = str(manifest.get("control_strategy", "")).strip()
    if existing:
        return existing
    layout = str(manifest.get("layout_pattern", "")).lower()
    if "rhythm" in layout or "action_sheet" in layout:
        return "rhythm_performance_board"
    if "product" in layout:
        return "product_lock"
    if "trailer" in layout or "action" in layout:
        return "storyboard_heavy"
    return "storyboard_heavy"


def infer_layout_pattern(manifest: dict) -> str:
    existing = str(manifest.get("layout_pattern", "")).strip()
    if existing:
        return existing
    strategy = str(manifest.get("control_strategy", "")).lower()
    segments = [segment for segment in manifest.get("segments", []) if isinstance(segment, dict)]
    max_beats = max((len(segment.get("reference_beats", [])) for segment in segments), default=0)
    joined = " ".join(
        " ".join(str(segment.get(key, "")) for key in ("function", "control_mode", "mode"))
        for segment in segments
    ).lower()
    if "face_emotion" in strategy or "message" in joined or "dialogue" in joined:
        return "4_panel_horizontal_flow"
    if "product" in strategy:
        return "3x4_product_board"
    if "trailer" in joined or "disaster" in joined or "invasion" in joined:
        return "4x3_trailer_grid"
    if max_beats >= 13:
        return "16_panel_action_sheet"
    if max_beats >= 9 or "rhythm" in strategy:
        return "12_panel_rhythm_sheet"
    if max_beats >= 6:
        return "3x3_action_grid"
    return "6_panel_sequence"


def infer_control_mode(manifest: dict, segment: dict) -> str:
    existing = str(segment.get("control_mode", "")).strip()
    if existing:
        return existing
    legacy = str(segment.get("mode", "")).strip()
    if legacy in CONTROL_MODES:
        return legacy
    layout = str(manifest.get("layout_pattern", "")).lower()
    strategy = str(manifest.get("control_strategy", "")).lower()
    if "face" in layout or "emotion" in layout or "face_emotion" in strategy:
        return "face_emotion_flow"
    if "rhythm" in layout or "action_sheet" in layout:
        return "rhythm_performance_board"
    if "product" in layout:
        return "product_lock"
    if "transformation" in layout:
        return "body_driven_transformation"
    return "storyboard_heavy"


def infer_execution_mode(segment: dict) -> str:
    existing = str(segment.get("execution_mode", "")).strip()
    if existing:
        return existing
    legacy = str(segment.get("mode", "")).strip()
    if legacy in EXECUTION_MODES:
        return legacy
    control = str(segment.get("control_mode", "")).strip()
    if control == "face_emotion_flow":
        return "single_continuous_shot"
    return "coherent_multi_shot_sequence"


def discover_storyboard_path(package_dir: Path) -> tuple[str | None, str]:
    storyboard_dir = package_dir / "11_generated_storyboards"
    if not storyboard_dir.is_dir():
        return None, "missing"
    candidates = sorted(storyboard_dir.glob("*.png"))
    if not candidates:
        return None, "missing"
    preferred = [
        path
        for path in candidates
        if "control" in path.stem or "sheet" in path.stem or "overview" in path.stem
    ]
    chosen = (preferred or candidates)[0]
    return rel(chosen, package_dir), "generated"


def merge_reference_assets(package_dir: Path, manifest: dict) -> dict:
    output = deepcopy(DEFAULT_REFERENCE_ASSETS)
    existing = manifest.get("reference_assets", {})
    if isinstance(existing, dict):
        for key, value in existing.items():
            if isinstance(value, dict):
                output.setdefault(key, {}).update(value)
    storyboard_path, storyboard_status = discover_storyboard_path(package_dir)
    if storyboard_path and output["storyboard_control"].get("status") == "missing":
        output["storyboard_control"]["path"] = storyboard_path
        output["storyboard_control"]["status"] = storyboard_status
    clean_dir = package_dir / "06_clean_keyframe_prompts"
    if clean_dir.is_dir() and output["clean_keyframe_reference"].get("status") == "missing":
        output["clean_keyframe_reference"]["status"] = "prompt_only"
        output["clean_keyframe_reference"]["path"] = "06_clean_keyframe_prompts/"
    return output


def merge_user_constraints(manifest: dict) -> dict:
    output = deepcopy(DEFAULT_USER_HARD_CONSTRAINTS)
    existing = manifest.get("user_hard_constraints", {})
    if isinstance(existing, dict):
        output.update(existing)
    if not output.get("target_duration"):
        output["target_duration"] = manifest.get("target_duration", "")
    return output


def upgrade_manifest(package_dir: Path, manifest: dict) -> tuple[dict, list[str]]:
    upgraded = deepcopy(manifest)
    changes: list[str] = []

    for key, default in (
        ("project_title", ""),
        ("workflow_version", WORKFLOW_VERSION),
        ("skill_versions", deepcopy(SKILL_VERSIONS)),
        ("target_duration", ""),
        ("aspect_ratio", "16:9"),
        ("storyboard_type", "beat_storyboard"),
        ("video_model", "seedance2"),
        ("seedance2_segment_limit", "15s"),
        ("visual_bible", "03_visual_bible.md"),
    ):
        if key not in upgraded:
            upgraded[key] = default
            changes.append(f"added top-level {key}")
        elif key == "skill_versions" and isinstance(upgraded.get(key), dict):
            for skill_name, version in SKILL_VERSIONS.items():
                if skill_name not in upgraded[key]:
                    upgraded[key][skill_name] = version
                    changes.append(f"added skill_versions.{skill_name}")

    inferred_strategy = infer_control_strategy(upgraded)
    if upgraded.get("control_strategy") != inferred_strategy:
        upgraded["control_strategy"] = inferred_strategy
        changes.append("filled control_strategy")

    inferred_layout = infer_layout_pattern(upgraded)
    if upgraded.get("layout_pattern") != inferred_layout:
        upgraded["layout_pattern"] = inferred_layout
        changes.append("filled layout_pattern")

    upgraded["user_hard_constraints"] = merge_user_constraints(upgraded)
    if "user_hard_constraints" not in manifest:
        changes.append("added user_hard_constraints")

    upgraded["reference_assets"] = merge_reference_assets(package_dir, upgraded)
    if "reference_assets" not in manifest:
        changes.append("added reference_assets")

    segments = upgraded.get("segments", [])
    if isinstance(segments, list):
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            control_mode = infer_control_mode(upgraded, segment)
            execution_mode = infer_execution_mode({**segment, "control_mode": control_mode})
            if segment.get("control_mode") != control_mode:
                segment["control_mode"] = control_mode
                changes.append(f"{segment.get('segment_id', 'segment')}: filled control_mode")
            if segment.get("execution_mode") != execution_mode:
                segment["execution_mode"] = execution_mode
                changes.append(f"{segment.get('segment_id', 'segment')}: filled execution_mode")
            if "storyboard_prompt_file" not in segment:
                segment_prompt = package_dir / "05_segment_storyboard_prompts" / f"{segment.get('segment_id', '')}_storyboard_prompt.txt"
                if segment_prompt.exists():
                    segment["storyboard_prompt_file"] = rel(segment_prompt, package_dir)
                    changes.append(f"{segment.get('segment_id', 'segment')}: added storyboard_prompt_file")

    return upgraded, changes


def write_support_files(package_dir: Path, manifest: dict, changes: list[str]) -> None:
    control_path = package_dir / "00_control_strategy.md"
    if not control_path.exists():
        segments = manifest.get("segments", [])
        segment_lines = []
        if isinstance(segments, list):
            for segment in segments:
                if not isinstance(segment, dict):
                    continue
                segment_lines.append(
                    "- {segment_id}: control={control_mode}, execution={execution_mode}, duration={duration}".format(
                        segment_id=segment.get("segment_id", "Segment"),
                        control_mode=segment.get("control_mode") or segment.get("mode") or "not recorded",
                        execution_mode=segment.get("execution_mode") or "not recorded",
                        duration=segment.get("duration", "not recorded"),
                    )
                )
        content = [
            "# Control Strategy",
            "",
            f"- Primary control strategy: {manifest.get('control_strategy', 'storyboard_heavy')}",
            f"- Layout pattern: {manifest.get('layout_pattern', 'not recorded')}",
            "- Reference priority: storyboard controls beat order, camera staging, action path, timing, and composition; character/environment/style references control identity, geography, and finish when supplied.",
            "- Soft-hint risk: current video models may prioritize cinematic appeal over exact storyboard adherence.",
            "- Adherence boosters: follow ordered storyboard beats; do not skip, merge, reorder, or reinterpret panels; do not render storyboard artifacts.",
            "",
            "## Segments",
            "",
            *(segment_lines or ["- No segments recorded."]),
            "",
            "## Migration Note",
            "",
            "This file was generated by `scripts/upgrade_manifest_schema.py --write` for a legacy pack. Review and refine before production handoff.",
        ]
        control_path.write_text("\n".join(content).strip() + "\n", encoding="utf-8")
        changes.append("created 00_control_strategy.md")

    for filename, title in (
        ("14_review_status.md", "Review Status"),
        ("14_review_summary.md", "Review Summary"),
    ):
        path = package_dir / filename
        if not path.exists():
            path.write_text(f"# {title}\n\nGenerated placeholder during manifest schema upgrade.\n", encoding="utf-8")
            changes.append(f"created {filename}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument("--write", action="store_true", help="Write upgraded manifest in place.")
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

    upgraded, changes = upgrade_manifest(package_dir, manifest)
    if not changes:
        print("Manifest already matches the current schema.")
        return 0

    print("Planned manifest schema upgrades:")
    for change in changes:
        print(f"- {change}")

    if args.write:
        write_json(manifest_path, upgraded)
        write_support_files(package_dir, upgraded, changes)
        print(f"Wrote upgraded manifest: {manifest_path}")
    else:
        print("Dry run only. Re-run with --write to update the manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
