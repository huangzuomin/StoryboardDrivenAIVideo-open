#!/usr/bin/env python3
"""Run the storyboard-to-video preproduction chain for a director pack."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR_FOR_IMPORT = Path(__file__).resolve().parent
if str(SCRIPT_DIR_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR_FOR_IMPORT))

from control_strategy_requirements import infer_requirements


REPORT_NAME = "16_preproduction_orchestrator_report.md"
JSON_REPORT_NAME = "16_preproduction_orchestrator_report.json"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
PHASES = ("iteration", "preflight", "final")


@dataclass
class StepResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    required: bool = True

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def rel(package_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(package_dir.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_step(name: str, command: list[str], *, required: bool = True) -> StepResult:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    return StepResult(
        name=name,
        command=command,
        returncode=result.returncode,
        stdout=(result.stdout or "").strip(),
        stderr=(result.stderr or "").strip(),
        required=required,
    )


def first_existing_storyboard(package_dir: Path) -> Path | None:
    storyboard_dir = package_dir / "11_generated_storyboards"
    if not storyboard_dir.is_dir():
        return None
    images = sorted(path for path in storyboard_dir.iterdir() if path.suffix.lower() in IMAGE_EXTS)
    if not images:
        return None
    preferred = [path for path in images if "sheet" in path.stem or "overview" in path.stem]
    return preferred[0] if preferred else images[0]


def manifest_asset_path(package_dir: Path, role: str) -> Path | None:
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = read_json(manifest_path)
    except Exception:  # noqa: BLE001
        return None
    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict):
        return None
    asset = assets.get(role, {})
    if not isinstance(asset, dict):
        return None
    path_value = asset.get("path")
    if not path_value:
        return None
    path = package_dir / str(path_value)
    return path if path.exists() else None


def copy_or_reference_asset(package_dir: Path, source: str, dest_dir: str, stem: str) -> str:
    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"asset image does not exist: {source_path}")
    if source_path.suffix.lower() not in IMAGE_EXTS:
        raise ValueError(f"asset image must use one of {sorted(IMAGE_EXTS)}: {source_path}")

    try:
        source_path.relative_to(package_dir.resolve())
        return rel(package_dir, source_path)
    except ValueError:
        target_dir = package_dir / dest_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{stem}{source_path.suffix.lower()}"
        if source_path.resolve() != target.resolve():
            shutil.copy2(source_path, target)
        return rel(package_dir, target)


def copy_or_reference_image_dir(package_dir: Path, source: str, dest_dir: str) -> str:
    source_dir = Path(source).expanduser().resolve()
    if not source_dir.is_dir():
        raise FileNotFoundError(f"asset image directory does not exist: {source_dir}")
    images = sorted(path for path in source_dir.iterdir() if path.suffix.lower() in IMAGE_EXTS)
    if not images:
        raise FileNotFoundError(f"asset image directory has no supported images: {source_dir}")

    try:
        source_dir.relative_to(package_dir.resolve())
        path_value = rel(package_dir, source_dir)
    except ValueError:
        target_dir = package_dir / dest_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        for image in images:
            shutil.copy2(image, target_dir / image.name)
        path_value = rel(package_dir, target_dir)
    return path_value.rstrip("/") + "/"


def register_asset_images(package_dir: Path, args: argparse.Namespace) -> list[str]:
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        return []
    manifest = read_json(manifest_path)
    assets = manifest.setdefault("reference_assets", {})
    if not isinstance(assets, dict):
        manifest["reference_assets"] = {}
        assets = manifest["reference_assets"]

    registrations = {
        "storyboard_control": (
            args.storyboard_image,
            "11_generated_storyboards",
            "storyboard_sheet_v01",
            "controls beat order, camera staging, action path, timing, composition, and emotional progression",
        ),
        "character_reference": (
            args.character_image,
            "11_reference_assets",
            "character_sheet_v01",
            "controls identity, costume, proportions, face, hair, and body language",
        ),
        "prop_reference": (
            args.prop_image,
            "11_reference_assets",
            "prop_sheet_v01",
            "controls central prop silhouette, scale, materials, moving parts, allowed motion, and forbidden mutations",
        ),
        "environment_reference": (
            args.environment_image,
            "11_reference_assets",
            "environment_reference_v01",
            "controls geography, props, lighting, weather, and spatial continuity",
        ),
        "style_reference": (
            args.style_image,
            "11_reference_assets",
            "style_reference_v01",
            "controls render finish, texture, palette, lens language, and style",
        ),
    }

    notes: list[str] = []
    for role, (source, dest_dir, stem, default_role) in registrations.items():
        if not source:
            continue
        path_value = copy_or_reference_asset(package_dir, source, dest_dir, stem)
        asset = assets.setdefault(role, {})
        if not isinstance(asset, dict):
            asset = {}
            assets[role] = asset
        asset["path"] = path_value
        asset["status"] = "generated"
        asset.setdefault("role", default_role)
        notes.append(f"{role}: {path_value}")

    if notes:
        write_json(manifest_path, manifest)
    return notes


def register_clean_keyframe_dir(package_dir: Path, args: argparse.Namespace) -> list[str]:
    source = getattr(args, "clean_keyframe_dir", "")
    if not source:
        return []
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        return []
    manifest = read_json(manifest_path)
    assets = manifest.setdefault("reference_assets", {})
    if not isinstance(assets, dict):
        manifest["reference_assets"] = {}
        assets = manifest["reference_assets"]

    path_value = copy_or_reference_image_dir(package_dir, source, "11_clean_keyframes")
    clean = assets.setdefault("clean_keyframe_reference", {})
    if not isinstance(clean, dict):
        clean = {}
        assets["clean_keyframe_reference"] = clean
    clean["path"] = path_value
    clean["status"] = "generated"
    clean.setdefault(
        "role",
        "controls clean final-frame/keyframe look without annotations, text, arrows, borders, or UI",
    )
    write_json(manifest_path, manifest)
    return [f"clean_keyframe_reference: {path_value}"]


def supported_images(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.suffix.lower() in IMAGE_EXTS)
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
        return [path]
    return []


def asset_is_real(package_dir: Path, asset: dict) -> bool:
    if asset.get("status") not in {"generated", "user_supplied"}:
        return False
    path_value = asset.get("path")
    if not path_value:
        return False
    path = package_dir / str(path_value)
    if not path.exists():
        return False
    if path.is_dir():
        return bool(supported_images(path))
    return path.suffix.lower() in IMAGE_EXTS


def phase_asset_gate(package_dir: Path, phase: str) -> StepResult:
    if phase != "final":
        return StepResult("phase asset gate", [], 0, f"Phase {phase}: final asset gate not required.", "", False)

    manifest_path = package_dir / "10_generation_manifest.json"
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        return StepResult("phase asset gate", [], 1, "", f"Manifest could not be loaded: {exc}", True)

    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict) or not assets:
        return StepResult("phase asset gate", [], 1, "", "manifest.reference_assets is missing or invalid.", True)

    missing: list[str] = []
    skipped: list[str] = []
    passed: list[str] = []
    for role, asset in assets.items():
        if not isinstance(asset, dict):
            missing.append(f"{role}: invalid asset object")
            continue
        if asset.get("status") == "not_needed":
            skipped.append(role)
            continue
        if asset_is_real(package_dir, asset):
            passed.append(role)
        else:
            status = asset.get("status", "missing")
            path = asset.get("path") or "none"
            missing.append(f"{role}: status={status}, path={path}")

    if missing:
        stdout = "Final phase requires real generated/user-supplied assets for every manifest reference role that is not marked not_needed."
        stderr = "\n".join(missing)
        return StepResult("phase asset gate", [], 1, stdout, stderr, True)

    lines = ["Final phase asset gate passed."]
    if passed:
        lines.append("Real assets: " + ", ".join(passed))
    if skipped:
        lines.append("Marked not_needed: " + ", ".join(skipped))
    return StepResult("phase asset gate", [], 0, "\n".join(lines), "", True)


def write_report(
    package_dir: Path,
    steps: list[StepResult],
    asset_notes: list[str],
    prompt_mode: str,
    phase: str,
    strict_assets: bool,
) -> Path:
    failed_required = [step for step in steps if step.required and not step.ok]
    verdict = "PASS" if not failed_required else "FAIL"
    manifest: dict = {}
    try:
        manifest = read_json(package_dir / "10_generation_manifest.json")
    except Exception:  # noqa: BLE001
        manifest = {}
    requirements = infer_requirements(package_dir, manifest) if manifest else None

    lines = [
        "# Preproduction Orchestrator Report",
        "",
        f"- Verdict: {verdict}",
        f"- Phase: {phase}",
        f"- Prompt mode: {prompt_mode}",
        f"- Strict asset QC: {'enabled' if strict_assets else 'disabled'}",
        "",
        "## Registered Assets",
        "",
    ]
    if asset_notes:
        lines.extend(f"- {note}" for note in asset_notes)
    else:
        lines.append("- None registered in this run")

    if requirements is not None:
        lines.extend(
            [
                "",
                "## Inferred Asset Requirements",
                "",
                f"- Strategies: {', '.join(sorted(requirements.strategies)) or 'none'}",
                f"- Required real assets: {', '.join(sorted(requirements.required_assets)) or 'none'}",
                f"- Recommended assets: {', '.join(sorted(requirements.recommended_assets)) or 'none'}",
                f"- Semantic checks: {', '.join(sorted(requirements.semantic_checks)) or 'none'}",
            ]
        )
        if requirements.notes:
            lines.extend(["", "Notes:", *[f"- {note}" for note in requirements.notes]])

    if failed_required:
        lines.extend(
            [
                "",
                "## Repair Guidance",
                "",
                "- If an inferred required asset is prompt_only or missing, generate/register the image asset and rerun this orchestrator.",
                "- If preflight QC fails on motion/emotion/spatial semantics, patch 03_visual_bible.md and 04_beat_storyboard_plan.md before rebuilding prompts.",
                "- If clean_keyframe_reference is prompt_only during final phase, generate clean images with no text, labels, arrows, borders, panel numbers, or UI.",
            ]
        )

    lines.extend(["", "## Steps", ""])
    for step in steps:
        status = "PASS" if step.ok else "FAIL"
        requirement = "required" if step.required else "optional"
        lines.extend(
            [
                f"### {step.name}",
                "",
                f"- Status: {status}",
                f"- Requirement: {requirement}",
                f"- Command: `{' '.join(step.command)}`",
            ]
        )
        output = "\n".join(part for part in (step.stdout, step.stderr) if part)
        if output:
            lines.extend(["", "```text", output, "```"])
        lines.append("")

    report_path = package_dir / REPORT_NAME
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    json_path = package_dir / JSON_REPORT_NAME
    json_path.write_text(
        json.dumps(
            {
                "verdict": verdict,
                "prompt_mode": prompt_mode,
                "phase": phase,
                "strict_assets": strict_assets,
                "registered_assets": asset_notes,
                "inferred_requirements": {
                    "strategies": sorted(requirements.strategies) if requirements else [],
                    "required_assets": sorted(requirements.required_assets) if requirements else [],
                    "recommended_assets": sorted(requirements.recommended_assets) if requirements else [],
                    "semantic_checks": sorted(requirements.semantic_checks) if requirements else [],
                    "notes": requirements.notes if requirements else [],
                },
                "steps": [
                    {
                        "name": step.name,
                        "command": step.command,
                        "returncode": step.returncode,
                        "required": step.required,
                        "stdout": step.stdout,
                        "stderr": step.stderr,
                    }
                    for step in steps
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--phase",
        choices=PHASES,
        default="preflight",
        help="Asset workflow profile: iteration, preflight, or final.",
    )
    parser.add_argument("--mode", choices=["full", "concise_seedance"], default="concise_seedance")
    parser.add_argument("--strict-assets", action="store_true", help="Run final-handoff strict asset QC.")
    parser.add_argument(
        "--visual-storyboard-required",
        action="store_true",
        help="Fail if no visible storyboard image exists under 11_generated_storyboards/.",
    )
    parser.add_argument("--storyboard-image", default="", help="Register a generated storyboard control image.")
    parser.add_argument("--character-image", default="", help="Register a generated character reference image.")
    parser.add_argument("--prop-image", default="", help="Register a generated prop reference image.")
    parser.add_argument("--environment-image", default="", help="Register a generated environment reference image.")
    parser.add_argument("--style-image", default="", help="Register a generated style reference image.")
    parser.add_argument("--clean-keyframe-dir", default="", help="Register a directory of generated clean keyframe images.")
    parser.add_argument("--skip-reference-prompts", action="store_true", help="Do not create prompt-only character/prop sheets.")
    parser.add_argument("--skip-review-summary", action="store_true", help="Do not refresh 14_review_status.md / 14_review_summary.md.")
    parser.add_argument("--extra-direction", default="", help="Extra direction to append to the video-generation prompt.")
    parser.add_argument(
        "--explicit-text-only-request",
        action="store_true",
        help="Allow iteration/text-plan checks only when the user explicitly asked for text-only planning.",
    )
    args = parser.parse_args()
    if args.phase == "final":
        args.strict_assets = True
        args.visual_storyboard_required = True

    package_dir = Path(args.package_dir).expanduser().resolve()
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[2]
    qc_script = repo_root / "skills" / "storyboard-video-qc" / "scripts" / "preflight_qc.py"
    visual_asset_review_script = repo_root / "skills" / "storyboard-video-qc" / "scripts" / "visual_asset_review.py"

    if not package_dir.exists():
        print(f"ERROR: package does not exist: {package_dir}")
        return 1
    if not (package_dir / "10_generation_manifest.json").exists():
        print(f"ERROR: missing manifest: {package_dir / '10_generation_manifest.json'}")
        return 1

    steps: list[StepResult] = []
    asset_notes: list[str] = []

    upgrade_script = script_dir / "upgrade_manifest_schema.py"
    if upgrade_script.exists():
        steps.append(
            run_step(
                "upgrade manifest schema",
                [sys.executable, str(upgrade_script), str(package_dir), "--write"],
            )
        )

    if not args.skip_reference_prompts:
        steps.append(
            run_step(
                "build character and prop reference prompts",
                [sys.executable, str(script_dir / "build_character_reference_prompt.py"), str(package_dir)],
            )
        )
        environment_prompt_script = script_dir / "build_environment_reference_prompt.py"
        if environment_prompt_script.exists():
            steps.append(
                run_step(
                    "build environment reference prompt",
                    [sys.executable, str(environment_prompt_script), str(package_dir)],
                )
            )
        style_prompt_script = script_dir / "build_style_reference_prompt.py"
        if style_prompt_script.exists():
            steps.append(
                run_step(
                    "build style reference prompt",
                    [sys.executable, str(style_prompt_script), str(package_dir)],
                )
            )
        clean_keyframe_script = script_dir / "build_clean_keyframe_image_tasks.py"
        if clean_keyframe_script.exists():
            steps.append(
                run_step(
                    "build clean keyframe image tasks",
                    [sys.executable, str(clean_keyframe_script), str(package_dir)],
                )
            )

    try:
        asset_notes = register_asset_images(package_dir, args)
        asset_notes.extend(register_clean_keyframe_dir(package_dir, args))
    except Exception as exc:  # noqa: BLE001
        failed = StepResult("register asset images", [], 1, "", str(exc), True)
        steps.append(failed)
        report_path = write_report(package_dir, steps, asset_notes, args.mode, args.phase, args.strict_assets)
        print("Preproduction verdict: FAIL")
        print(f"Wrote report: {report_path}")
        print(str(exc))
        return 1
    if asset_notes:
        steps.append(StepResult("register asset images", [], 0, "\n".join(asset_notes), "", True))

    phase_gate = phase_asset_gate(package_dir, args.phase)
    if args.phase == "final" or not phase_gate.ok:
        steps.append(phase_gate)

    storyboard_image = first_existing_storyboard(package_dir) or manifest_asset_path(package_dir, "storyboard_control")
    if args.visual_storyboard_required:
        steps.append(
            run_step(
                "check visual storyboard delivery",
                [sys.executable, str(script_dir / "check_visual_storyboard_delivery.py"), str(package_dir)],
            )
        )

    video_command = [
        sys.executable,
        str(script_dir / "build_video_generation_prompt.py"),
        str(package_dir),
        "--mode",
        args.mode,
    ]
    if storyboard_image:
        video_command.extend(["--storyboard-image", str(storyboard_image)])
    if args.extra_direction:
        video_command.extend(["--extra-direction", args.extra_direction])
    steps.append(run_step("build video generation prompt", video_command))

    steps.append(run_step("validate package", [sys.executable, str(script_dir / "validate_package.py"), str(package_dir)]))
    steps.append(
        run_step(
            "validate manifest schema",
            [
                sys.executable,
                str(script_dir / "validate_manifest.py"),
                str(package_dir / "10_generation_manifest.json"),
                "--strict-current-schema",
            ],
        )
    )

    if not args.skip_review_summary:
        steps.append(
            run_step(
                "build review summary",
                [sys.executable, str(script_dir / "build_review_summary.py"), str(package_dir)],
                required=False,
            )
        )

    user_preview_script = script_dir / "build_user_preview_summary.py"
    if user_preview_script.exists():
        steps.append(
            run_step(
                "build user preview summary",
                [sys.executable, str(user_preview_script), str(package_dir), "--phase", args.phase],
                required=False,
            )
        )

    if visual_asset_review_script.exists():
        visual_review_command = [sys.executable, str(visual_asset_review_script), str(package_dir)]
        if args.strict_assets:
            visual_review_command.append("--strict-assets")
        steps.append(run_step("visual asset review", visual_review_command))

    qc_command = [sys.executable, str(qc_script), str(package_dir)]
    if args.strict_assets:
        qc_command.append("--strict-assets")
    steps.append(run_step("preflight QC", qc_command))

    handoff_bundle_script = script_dir / "build_generation_handoff_bundle.py"
    legacy_deployment_bundle_script = script_dir / "build_generation_deployment_bundle.py"
    bundle_script = handoff_bundle_script if handoff_bundle_script.exists() else legacy_deployment_bundle_script
    if args.phase == "final" and bundle_script.exists():
        steps.append(
            run_step(
                "build generation handoff bundle",
                [sys.executable, str(bundle_script), str(package_dir)],
            )
        )

    expected_delivery_script = script_dir / "validate_expected_delivery.py"
    if expected_delivery_script.exists():
        expected_profile = "text-plan" if args.phase == "iteration" else args.phase
        expected_command = [
            sys.executable,
            str(expected_delivery_script),
            str(package_dir),
            "--profile",
            expected_profile,
        ]
        if args.visual_storyboard_required:
            expected_command.append("--visual-storyboard-required")
        if args.explicit_text_only_request:
            expected_command.append("--explicit-text-only-request")
        steps.append(run_step("validate expected delivery", expected_command))

    readiness_script = script_dir / "diagnose_pack_readiness.py"
    if readiness_script.exists():
        readiness_command = [
            sys.executable,
            str(readiness_script),
            str(package_dir),
            "--profile",
            args.phase,
        ]
        if args.visual_storyboard_required:
            readiness_command.append("--visual-storyboard-required")
        steps.append(run_step("diagnose pack readiness", readiness_command))

    report_path = write_report(package_dir, steps, asset_notes, args.mode, args.phase, args.strict_assets)
    failed_required = [step for step in steps if step.required and not step.ok]
    verdict = "FAIL" if failed_required else "PASS"
    print(f"Preproduction verdict: {verdict}")
    print(f"Wrote report: {report_path}")
    print(f"Wrote JSON report: {package_dir / JSON_REPORT_NAME}")
    for step in steps:
        status = "PASS" if step.ok else "FAIL"
        print(f"- {status}: {step.name}")
    return 1 if failed_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
