#!/usr/bin/env python3
"""Build a xyq-nest-skill video handoff message from a director pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_HANDOFF_DIR = "13_xyq_video_handoff"
DEFAULT_ASSET_MANIFEST = "asset_manifest.json"
DEFAULT_HANDOFF_VIDEO_PROMPT = "../17_generation_handoff/video_prompt_for_upload.txt"
DEFAULT_DEPLOYMENT_VIDEO_PROMPT = "../17_generation_deployment/video_prompt_for_upload.txt"
LEGACY_VIDEO_PROMPT = "../12_video_generation_prompt/video_generation_prompt.txt"
DEFAULT_OUTPUT_MESSAGE = "xyq_video_task_message.txt"

VALID_ROLES = {
    "storyboard_control",
    "character_reference",
    "prop_reference",
    "environment_reference",
    "style_reference",
    "clean_keyframe_reference",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rel_or_abs(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path)


def default_video_prompt(package_dir: Path) -> str:
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        return ""
    try:
        manifest = load_json(manifest_path)
    except Exception:  # noqa: BLE001
        return ""

    segments = manifest.get("segments", [])
    lines = [
        f"Generate a {manifest.get('target_duration', 'video')} video from this director pack.",
        "Preserve the storyboard beat order, character identity, environment layout, and visual style from the supplied reference assets.",
        "Use the storyboard as control for action path, camera staging, timing, and continuity.",
    ]
    for segment in segments:
        seg_id = segment.get("segment_id", "Segment")
        duration = segment.get("duration", "")
        function = segment.get("function", "")
        beats = ", ".join(segment.get("reference_beats", []))
        if beats or function:
            lines.append(f"{seg_id} ({duration}): {function} Reference beats: {beats}.")
    return "\n".join(lines).strip()


def asset_line(asset: dict, index: int) -> str:
    label = asset.get("label") or f"Reference image {index}"
    role = asset.get("role", "")
    purpose = asset.get("purpose", "")
    character = asset.get("character", "")
    path = asset.get("path", "")
    asset_id = asset.get("asset_id", "")

    role_text = role.replace("_", " ") if role else "reference"
    parts = [f"{label} is a {role_text}."]
    if character:
        parts.append(f"Character: {character}.")
    if purpose:
        parts.append(purpose.rstrip(".") + ".")
    if asset_id:
        parts.append(f"Uploaded asset_id: {asset_id}.")
    elif path:
        parts.append(f"Local path before upload: {path}.")
    return " ".join(parts)


def iter_uploadable_asset_paths(path_text: str, package_dir: Path) -> list[str]:
    if not path_text:
        return [""]
    path = Path(path_text)
    if not path.is_absolute():
        path = package_dir / path
    if path.is_dir():
        return [
            rel_or_abs(candidate, package_dir)
            for candidate in sorted(path.iterdir())
            if candidate.is_file() and candidate.suffix.lower() in IMAGE_EXTENSIONS
        ]
    return [rel_or_abs(path, package_dir)]


def validate_assets(assets: list[dict]) -> list[str]:
    errors: list[str] = []
    if not assets:
        errors.append("asset manifest must include at least one asset")
    roles = {asset.get("role") for asset in assets}
    if "storyboard_control" not in roles:
        errors.append("asset manifest should include one storyboard_control asset")
    for index, asset in enumerate(assets, start=1):
        role = asset.get("role")
        if role not in VALID_ROLES:
            errors.append(f"asset {index}: invalid role {role!r}")
        if not asset.get("asset_id") and not asset.get("path"):
            errors.append(f"asset {index}: provide either asset_id or path")
    return errors


def write_manifest_template(package_dir: Path, manifest_path: Path) -> None:
    handoff_dir = package_dir / DEFAULT_HANDOFF_DIR
    handoff_dir.mkdir(parents=True, exist_ok=True)
    generation_manifest_path = package_dir / "10_generation_manifest.json"
    assets: list[dict] = []
    if generation_manifest_path.exists():
        try:
            generation_manifest = load_json(generation_manifest_path)
            reference_assets = generation_manifest.get("reference_assets", {})
        except Exception:  # noqa: BLE001
            reference_assets = {}
        if isinstance(reference_assets, dict):
            for role, asset in reference_assets.items():
                if not isinstance(asset, dict):
                    continue
                path = asset.get("path") or ""
                if asset.get("status") not in {"generated", "user_supplied"}:
                    continue
                expanded_paths = iter_uploadable_asset_paths(path, package_dir)
                for path_index, expanded_path in enumerate(expanded_paths, start=1):
                    label = role.replace("_", " ").title()
                    if len(expanded_paths) > 1:
                        label = f"{label} {path_index:02d}"
                    assets.append(
                        {
                            "label": label,
                            "role": role,
                            "path": expanded_path,
                            "asset_id": "",
                            "purpose": asset.get("role", ""),
                        }
                    )

    if not assets:
        assets = [
            {
                "label": "Reference image 1",
                "role": "storyboard_control",
                "path": "11_generated_storyboards/storyboard_sheet_v01.png",
                "asset_id": "",
                "purpose": "Controls beat order, action path, camera staging, environment progression, and timing.",
            },
            {
                "label": "Reference image 2",
                "role": "character_reference",
                "character": "main character",
                "path": "",
                "asset_id": "",
                "purpose": "Controls identity, proportions, costume/body design, and expression style.",
            },
        ]

    template = {"assets": assets}
    manifest_path.write_text(
        json.dumps(template, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--asset-manifest",
        default="",
        help="Asset manifest JSON. Defaults to 13_xyq_video_handoff/asset_manifest.json.",
    )
    parser.add_argument(
        "--video-prompt",
        default="",
        help="Final video prompt text. Defaults to 17_generation_handoff/video_prompt_for_upload.txt, then legacy 17_generation_deployment or 12_video_generation_prompt prompts, or manifest-derived fallback.",
    )
    parser.add_argument(
        "--init-manifest",
        action="store_true",
        help="Create a starter asset manifest and exit.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    handoff_dir = package_dir / DEFAULT_HANDOFF_DIR
    handoff_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = (
        Path(args.asset_manifest).expanduser().resolve()
        if args.asset_manifest
        else handoff_dir / DEFAULT_ASSET_MANIFEST
    )

    if args.init_manifest:
        write_manifest_template(package_dir, manifest_path)
        print(f"Created asset manifest template: {manifest_path}")
        return 0

    if not manifest_path.exists():
        print(f"ERROR: asset manifest does not exist: {manifest_path}")
        print("Run with --init-manifest to create a starter file.")
        return 1

    if args.video_prompt:
        video_prompt_path = Path(args.video_prompt).expanduser().resolve()
    else:
        handoff_prompt_path = handoff_dir / DEFAULT_HANDOFF_VIDEO_PROMPT
        deployment_prompt_path = handoff_dir / DEFAULT_DEPLOYMENT_VIDEO_PROMPT
        legacy_prompt_path = handoff_dir / LEGACY_VIDEO_PROMPT
        if handoff_prompt_path.exists():
            video_prompt_path = handoff_prompt_path
        elif deployment_prompt_path.exists():
            video_prompt_path = deployment_prompt_path
        else:
            video_prompt_path = legacy_prompt_path

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: asset manifest is not valid JSON: {exc}")
        return 1

    assets = manifest.get("assets", [])
    errors = validate_assets(assets)
    if errors:
        print("Asset manifest validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    video_prompt = (
        read_text(video_prompt_path)
        if video_prompt_path.exists()
        else default_video_prompt(package_dir)
    )
    if not video_prompt:
        print(f"ERROR: no video prompt found at {video_prompt_path} and no manifest fallback could be built")
        return 1

    lines = [
        "Generate the video using the following reference assets. Keep each reference role separate:",
        "",
    ]
    lines.extend(asset_line(asset, index) for index, asset in enumerate(assets, start=1))
    lines.extend(
        [
            "",
            "Generation request:",
            video_prompt,
            "",
            "Important constraints:",
            "- Storyboard control images are for beat order, action path, camera staging, composition, timing, and continuity.",
            "- Character references are for identity, proportions, costume/body design, expression style, and silhouette consistency.",
            "- Prop references are for object identity, scale, design details, handling logic, and prop-motion continuity.",
            "- Environment references are for spatial layout, props, materials, lighting, and geography continuity.",
            "- Style references are for line quality, color, rendering texture, and finish level.",
            "- Clean keyframe references are final-frame visual targets; do not render production annotations, panel borders, arrows, notes, numbers, or UI.",
            "- Do not treat annotated storyboard controls as clean keyframes unless the intended output is explicitly a hand-drawn storyboard-style video.",
            "- Preserve duration, aspect ratio, identity, environment, style, action causality, and final payoff.",
        ]
    )

    message = "\n".join(lines).strip() + "\n"
    output_path = handoff_dir / DEFAULT_OUTPUT_MESSAGE
    output_path.write_text(message, encoding="utf-8")

    print(f"Wrote xyq video task message: {output_path}")
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
