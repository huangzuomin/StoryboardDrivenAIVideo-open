#!/usr/bin/env python3
"""Diagnose storyboard director pack readiness and recommend the next actions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from control_strategy_requirements import infer_requirements

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
REAL_STATUSES = {"generated", "user_supplied"}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run(command: list[str]) -> Check:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return Check(Path(command[1]).name if len(command) > 1 else command[0], result.returncode == 0, output)


def asset_images(package_dir: Path, asset: dict) -> list[Path]:
    path_value = asset.get("path")
    if not path_value:
        return []
    path = package_dir / str(path_value)
    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.suffix.lower() in IMAGE_EXTS)
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
        return [path]
    return []


def asset_state(package_dir: Path, asset: dict | None) -> tuple[bool, str]:
    if not isinstance(asset, dict):
        return False, "missing asset object"
    status = asset.get("status", "missing")
    path = asset.get("path", "none")
    images = asset_images(package_dir, asset)
    ok = status in REAL_STATUSES and bool(images)
    if ok:
        return True, f"status={status}, path={path}, images={len(images)}"
    return False, f"status={status}, path={path}"


def text_contains_any(package_dir: Path, names: list[str], phrases: tuple[str, ...]) -> bool:
    text_parts: list[str] = []
    for name in names:
        path = package_dir / name
        if path.exists():
            text_parts.append(path.read_text(encoding="utf-8-sig", errors="replace").lower())
    text = "\n".join(text_parts)
    return any(phrase in text for phrase in phrases)


def semantic_asset_checks(package_dir: Path, manifest: dict, required_roles: set[str]) -> list[Check]:
    checks: list[Check] = []
    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict):
        return [Check("reference asset semantics", False, "manifest.reference_assets is missing or invalid")]

    for role in sorted(required_roles):
        ok, detail = asset_state(package_dir, assets.get(role))
        checks.append(Check(f"real asset: {role}", ok, detail))

    if "storyboard_control" in required_roles:
        has_camera_language = text_contains_any(
            package_dir,
            ["04_beat_storyboard_plan.md", "05_annotated_storyboard_prompt.txt", "00_control_strategy.md"],
            ("camera", "lens", "shot", "运镜", "镜头", "机位", "景别", "push", "track", "pan", "dolly"),
        )
        has_motion_language = text_contains_any(
            package_dir,
            ["04_beat_storyboard_plan.md", "05_annotated_storyboard_prompt.txt", "00_control_strategy.md"],
            ("action direction", "motion", "arrow", "movement", "动作方向", "运动方向", "节奏", "timing"),
        )
        checks.append(
            Check(
                "storyboard control semantics",
                has_camera_language and has_motion_language,
                "requires camera/lens language and motion/timing annotations in storyboard plan or prompt",
            )
        )

    if "prop_reference" in required_roles:
        has_lock_language = text_contains_any(
            package_dir,
            ["03_visual_bible.md", "00_control_strategy.md", "04_beat_storyboard_plan.md"],
            (
                "product lock",
                "object lock",
                "prop lock",
                "产品锁",
                "道具锁",
                "same throughout",
                "一直长得一样",
                "forbidden mutations",
                "禁止变形",
            ),
        )
        checks.append(
            Check(
                "product/prop lock semantics",
                has_lock_language,
                "requires explicit lock language for shape, scale, material, fixed features, and forbidden mutations",
            )
        )

    return checks


def recommended_actions(profile: str, checks: list[Check], required_roles: set[str]) -> list[str]:
    actions: list[str] = []
    failed_names = {check.name for check in checks if not check.ok}
    for role in sorted(required_roles):
        if f"real asset: {role}" in failed_names:
            actions.append(f"Generate or register a real raster image for reference_assets.{role}.")
    if "storyboard control semantics" in failed_names:
        actions.append("Patch the storyboard plan/prompt so the accepted control board includes camera, lens, movement direction, timing, and final hold controls.")
    if "product/prop lock semantics" in failed_names:
        actions.append("Patch the visual bible/control strategy with explicit product or prop lock details before rebuilding prompts.")
    if any(not check.ok and check.name.endswith(".py") for check in checks):
        actions.append("Fix structural validation failures before creating or claiming handoff artifacts.")
    if profile == "final":
        actions.append("Run preproduction_orchestrator.py <package_dir> --phase final --strict-assets after all required assets are real.")
    else:
        actions.append("Run preproduction_orchestrator.py <package_dir> --phase preflight after missing assets are resolved.")
    return actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument("--profile", choices=["iteration", "preflight", "final"], default="preflight")
    parser.add_argument("--visual-storyboard-required", action="store_true")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        print(f"Readiness diagnosis failed: missing manifest: {manifest_path}")
        return 1

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Readiness diagnosis failed: manifest is not valid JSON: {exc}")
        return 1

    requirements = infer_requirements(
        package_dir,
        manifest,
        visual_storyboard_required=args.visual_storyboard_required,
    )
    required_roles = set(requirements.required_assets)
    if args.profile == "final":
        required_roles.update(requirements.recommended_assets)

    checks = [
        run([sys.executable, str(SCRIPT_DIR / "validate_package.py"), str(package_dir)]),
        run(
            [
                sys.executable,
                str(SCRIPT_DIR / "validate_manifest.py"),
                str(manifest_path),
                "--strict-current-schema",
            ]
        ),
    ]
    expected_profile = "text-plan" if args.profile == "iteration" else args.profile
    expected = [
        sys.executable,
        str(SCRIPT_DIR / "validate_expected_delivery.py"),
        str(package_dir),
        "--profile",
        expected_profile,
    ]
    if args.profile == "iteration":
        expected.append("--explicit-text-only-request")
    if args.visual_storyboard_required:
        expected.append("--visual-storyboard-required")
    checks.append(run(expected))
    checks.extend(semantic_asset_checks(package_dir, manifest, required_roles))

    failed = [check for check in checks if not check.ok]
    verdict = "READY" if not failed else "FIX BEFORE HANDOFF"
    print(f"Readiness verdict: {verdict}")
    print(f"Profile: {args.profile}")
    print("Required real assets: " + (", ".join(sorted(required_roles)) or "none inferred"))
    if requirements.notes:
        print("Requirement notes:")
        for note in requirements.notes:
            print(f"- {note}")
    print("Checks:")
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        print(f"- {status}: {check.name}")
        if check.detail:
            for line in check.detail.splitlines()[:8]:
                print(f"  {line}")
    if failed:
        print("Recommended next actions:")
        for action in recommended_actions(args.profile, checks, required_roles):
            print(f"- {action}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
