#!/usr/bin/env python3
"""Validate that a director pack matches the expected user-facing delivery level."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from control_strategy_requirements import infer_requirements


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SCHEMATIC_EXTS = {".svg"}
REAL_STATUSES = {"generated", "user_supplied"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def supported_images(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.suffix.lower() in IMAGE_EXTS)
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
        return [path]
    return []


def has_schematic_file(path: Path) -> bool:
    if path.is_dir():
        return any(item.suffix.lower() in SCHEMATIC_EXTS for item in path.iterdir())
    return path.is_file() and path.suffix.lower() in SCHEMATIC_EXTS


def asset_is_real_image(package_dir: Path, asset: dict) -> bool:
    if asset.get("status") not in REAL_STATUSES:
        return False
    path_value = asset.get("path")
    if not path_value:
        return False
    path = package_dir / str(path_value)
    if not path.exists():
        return False
    return bool(supported_images(path))


def required_file_gaps(package_dir: Path, profile: str) -> list[str]:
    gaps: list[str] = []
    if profile in {"preflight", "final"}:
        for path_value in (
            "12_video_generation_prompt/video_generation_prompt.txt",
            "12_video_generation_prompt/video_generation_prompt_full.txt",
            "12_video_generation_prompt/video_generation_prompt_concise_seedance.txt",
            "12_video_generation_prompt/video_generation_prompt_zh.txt",
        ):
            if not (package_dir / path_value).is_file():
                gaps.append(f"required prompt file missing: {path_value}")
    if profile == "final":
        for path_value in (
            "17_generation_handoff/asset_manifest.json",
            "17_generation_handoff/video_prompt_for_upload.txt",
            "17_generation_handoff/handoff_readiness_report.md",
        ):
            if not (package_dir / path_value).is_file():
                gaps.append(f"required final handoff file missing: {path_value}")
    return gaps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--profile",
        choices=["text-plan", "preflight", "final"],
        default="preflight",
        help="Expected delivery level for the current user-facing response.",
    )
    parser.add_argument(
        "--explicit-text-only-request",
        action="store_true",
        help="Allow text-plan gaps only when the user explicitly asked for text-only planning and no generated assets.",
    )
    parser.add_argument(
        "--visual-storyboard-required",
        action="store_true",
        help="Require a real storyboard image even when product/object lock is absent.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        print(f"Expected delivery check failed: missing manifest: {manifest_path}")
        return 1

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Expected delivery check failed: manifest is not valid JSON: {exc}")
        return 1

    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict):
        print("Expected delivery check failed: manifest.reference_assets is missing or invalid.")
        return 1

    requirements = infer_requirements(package_dir, manifest, visual_storyboard_required=args.visual_storyboard_required)
    required_set = set(requirements.required_assets)
    if args.profile == "final":
        required_set.update(requirements.recommended_assets)
    required_roles = sorted(required_set)
    missing: list[str] = []
    schematic_only: list[str] = []
    for role in required_roles:
        asset = assets.get(role, {})
        if not isinstance(asset, dict) or not asset_is_real_image(package_dir, asset):
            status = asset.get("status", "missing") if isinstance(asset, dict) else "invalid"
            path_value = asset.get("path", "none") if isinstance(asset, dict) else "none"
            if isinstance(asset, dict) and path_value != "none" and has_schematic_file(package_dir / str(path_value)):
                schematic_only.append(f"{role}: status={status}, path={path_value}")
            else:
                missing.append(f"{role}: status={status}, path={path_value}")

    if schematic_only:
        missing.extend(
            f"{item} (SVG/schematic assets do not satisfy required real storyboard/reference images)"
            for item in schematic_only
        )
    missing.extend(required_file_gaps(package_dir, args.profile))

    if missing:
        if args.profile == "text-plan":
            if not args.explicit_text_only_request:
                print(
                    "Expected delivery check failed: text-plan profile cannot be used "
                    "unless the user explicitly asked for text-only planning and no generated assets."
                )
                for item in missing:
                    print(f"- {item}")
                print("Use --profile preflight for ordinary short-video/product-clip requests.")
                return 1
            print("Expected delivery check passed with explicit text-plan gaps:")
            for item in missing:
                print(f"- missing real asset: {item}")
            print("Final response must say this is text planning only, not visual asset handoff.")
            return 0
        print("Expected delivery check failed: required real visual asset(s) are missing.")
        for item in missing:
            print(f"- {item}")
        print(
            "Generate/register the asset(s) or explicitly report image generation as blocked. "
            "Do not say the pack is complete or ready for production handoff."
        )
        return 1

    print("Expected delivery check passed.")
    if required_roles:
        print("Required real assets: " + ", ".join(required_roles))
    else:
        print("No mandatory real visual assets inferred for this profile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
