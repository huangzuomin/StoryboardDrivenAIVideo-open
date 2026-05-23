#!/usr/bin/env python3
"""Run the public storyboard-video workflow regression suite."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTOR_SCRIPTS = ROOT / "skills" / "storyboard-video-director" / "scripts"
QC_SCRIPTS = ROOT / "skills" / "storyboard-video-qc" / "scripts"
PUBLIC_FIXTURES = [ROOT / "examples" / "fan_kata_minimal"]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode, output


def py_files() -> list[str]:
    files = sorted(DIRECTOR_SCRIPTS.glob("*.py")) + sorted(QC_SCRIPTS.glob("*.py"))
    files.append(Path(__file__).resolve())
    return [str(path) for path in files]


def assert_no_windows_absolute_paths(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing expected file: {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8-sig")
    if re.search(r"[A-Za-z]:\\", text):
        return [f"Windows absolute path leaked into {path.relative_to(ROOT)}"]
    return []


def run_fixture(package_dir: Path) -> list[str]:
    errors: list[str] = []
    code, output = run(
        [
            sys.executable,
            str(DIRECTOR_SCRIPTS / "preproduction_orchestrator.py"),
            str(package_dir),
            "--phase",
            "final",
        ]
    )
    if code != 0:
        errors.append(f"{package_dir.relative_to(ROOT)} final orchestrator failed:\n{output}")
        return errors

    handoff_dir = package_dir / "17_generation_handoff"
    expected = [
        handoff_dir / "asset_manifest.json",
        handoff_dir / "video_prompt_for_upload.txt",
        handoff_dir / "handoff_readiness_report.md",
    ]
    for path in expected:
        if not path.exists():
            errors.append(f"missing expected handoff output: {path.relative_to(ROOT)}")

    errors.extend(assert_no_windows_absolute_paths(handoff_dir / "video_prompt_for_upload.txt"))
    report = handoff_dir / "handoff_readiness_report.md"
    if report.exists() and "- Verdict: READY" not in report.read_text(encoding="utf-8-sig"):
        errors.append(f"handoff report is not READY: {report.relative_to(ROOT)}")
    return errors


def run_product_lock_negative_fixture() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="storyboard-product-lock-") as tmp:
        package_dir = Path(tmp)
        prompt_dir = package_dir / "15_reference_asset_prompts"
        storyboard_dir = package_dir / "05_segment_storyboard_prompts"
        segment_dir = package_dir / "07_seedance2_segment_prompts"
        keyframe_dir = package_dir / "06_clean_keyframe_prompts"
        for directory in (prompt_dir, storyboard_dir, segment_dir, keyframe_dir):
            directory.mkdir(parents=True, exist_ok=True)
        (prompt_dir / "prop.txt").write_text("prompt-only product reference\n", encoding="utf-8")
        (storyboard_dir / "S01_storyboard_prompt.txt").write_text("prompt-only storyboard\n", encoding="utf-8")
        (segment_dir / "S01.txt").write_text("video prompt\n", encoding="utf-8")
        (keyframe_dir / "P01.txt").write_text("keyframe prompt\n", encoding="utf-8")
        manifest = {
            "project_title": "Product Lock Negative Fixture",
            "workflow_version": "0.1.0-alpha",
            "skill_versions": {
                "storyboard-video-director": "0.1.0-alpha",
                "storyboard-video-qc": "0.1.0-alpha",
            },
            "target_duration": "15s",
            "aspect_ratio": "16:9",
            "storyboard_type": "beat_storyboard",
            "video_model": "seedance2",
            "seedance2_segment_limit": "5-15s",
            "layout_pattern": "3x4_product_board",
            "user_hard_constraints": ["product must look the same throughout"],
            "reference_assets": {
                "storyboard_control": {
                    "role": "controls shot order",
                    "path": "05_segment_storyboard_prompts/S01_storyboard_prompt.txt",
                    "status": "prompt_only",
                },
                "character_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "prop_reference": {
                    "role": "locks product identity",
                    "path": "15_reference_asset_prompts/prop.txt",
                    "status": "prompt_only",
                },
                "environment_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "style_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "clean_keyframe_reference": {
                    "role": "prompt-only keyframes",
                    "path": "06_clean_keyframe_prompts",
                    "status": "prompt_only",
                },
            },
            "segments": [
                {
                    "segment_id": "S01",
                    "duration": "15s",
                    "function": "product sequence",
                    "control_mode": "product_lock",
                    "execution_mode": "single_continuous_shot",
                    "reference_beats": ["P01"],
                    "clean_keyframes": ["06_clean_keyframe_prompts/P01.txt"],
                    "prompt_file": "07_seedance2_segment_prompts/S01.txt",
                    "transition_out": "hold",
                }
            ],
        }
        (package_dir / "10_generation_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        code, output = run(
            [
                sys.executable,
                str(DIRECTOR_SCRIPTS / "validate_expected_delivery.py"),
                str(package_dir),
                "--profile",
                "preflight",
            ]
        )
        if code == 0:
            errors.append(
                "product-lock prompt-only expected delivery fixture unexpectedly passed:\n"
                + output
            )

        code, output = run(
            [
                sys.executable,
                str(DIRECTOR_SCRIPTS / "validate_manifest.py"),
                str(package_dir / "10_generation_manifest.json"),
                "--strict-current-schema",
            ]
        )
        if code == 0:
            errors.append(
                "product-lock prompt-only strict manifest fixture unexpectedly passed:\n"
                + output
            )

        code, output = run(
            [
                sys.executable,
                str(DIRECTOR_SCRIPTS / "validate_expected_delivery.py"),
                str(package_dir),
                "--profile",
                "text-plan",
            ]
        )
        if code == 0:
            errors.append(
                "product-lock prompt-only text-plan fixture unexpectedly passed without explicit user text-only flag:\n"
                + output
            )

        code, output = run(
            [
                sys.executable,
                str(DIRECTOR_SCRIPTS / "validate_expected_delivery.py"),
                str(package_dir),
                "--profile",
                "text-plan",
                "--explicit-text-only-request",
            ]
        )
        if code != 0:
            errors.append(
                "product-lock explicit text-only fixture should pass but failed:\n"
                + output
            )
    return errors


def run_high_motion_storyboard_negative_fixture() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="storyboard-high-motion-") as tmp:
        package_dir = Path(tmp)
        storyboard_dir = package_dir / "05_segment_storyboard_prompts"
        segment_dir = package_dir / "07_seedance2_segment_prompts"
        keyframe_dir = package_dir / "06_clean_keyframe_prompts"
        for directory in (storyboard_dir, segment_dir, keyframe_dir):
            directory.mkdir(parents=True, exist_ok=True)
        (storyboard_dir / "S01_storyboard_prompt.txt").write_text("prompt-only 16 panel fan storyboard\n", encoding="utf-8")
        (segment_dir / "S01.txt").write_text("video prompt\n", encoding="utf-8")
        (keyframe_dir / "P01.txt").write_text("keyframe prompt\n", encoding="utf-8")
        manifest = {
            "project_title": "High Motion Storyboard Negative Fixture",
            "workflow_version": "0.1.0-alpha",
            "skill_versions": {
                "storyboard-video-director": "0.1.0-alpha",
                "storyboard-video-qc": "0.1.0-alpha",
            },
            "target_duration": "15s",
            "aspect_ratio": "16:9",
            "storyboard_type": "beat_storyboard",
            "control_strategy": "hybrid",
            "layout_pattern": "16_panel_action_sheet",
            "video_model": "seedance2",
            "seedance2_segment_limit": "5-15s",
            "user_hard_constraints": {
                "subject_identity": "gufeng fan and sleeve heroine",
                "required_final_payoff": "steady final hold",
                "visual_style": "storyboard plan before video generation",
            },
            "reference_assets": {
                "storyboard_control": {
                    "role": "controls fan path and sleeve burst",
                    "path": "05_segment_storyboard_prompts/S01_storyboard_prompt.txt",
                    "status": "prompt_only",
                },
                "character_reference": {"role": "prompt-only character", "path": None, "status": "not_needed"},
                "prop_reference": {"role": "prompt-only fan", "path": None, "status": "not_needed"},
                "environment_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "style_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "clean_keyframe_reference": {
                    "role": "prompt-only keyframes",
                    "path": "06_clean_keyframe_prompts",
                    "status": "prompt_only",
                },
            },
            "segments": [
                {
                    "segment_id": "S01",
                    "duration": "15s",
                    "function": "fan sleeve burst storyboard",
                    "control_mode": "rhythm_performance_board",
                    "execution_mode": "single_continuous_shot",
                    "reference_beats": ["P01"],
                    "clean_keyframes": ["06_clean_keyframe_prompts/P01.txt"],
                    "prompt_file": "07_seedance2_segment_prompts/S01.txt",
                    "transition_out": "hold",
                }
            ],
        }
        (package_dir / "10_generation_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        code, output = run(
            [
                sys.executable,
                str(DIRECTOR_SCRIPTS / "validate_expected_delivery.py"),
                str(package_dir),
                "--profile",
                "preflight",
            ]
        )
        if code == 0:
            errors.append(
                "high-motion prompt-only storyboard expected delivery fixture unexpectedly passed:\n"
                + output
            )
    return errors


def run_svg_storyboard_negative_fixture() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="storyboard-svg-only-") as tmp:
        package_dir = Path(tmp)
        storyboard_dir = package_dir / "11_generated_storyboards"
        segment_dir = package_dir / "07_seedance2_segment_prompts"
        keyframe_dir = package_dir / "06_clean_keyframe_prompts"
        for directory in (storyboard_dir, segment_dir, keyframe_dir):
            directory.mkdir(parents=True, exist_ok=True)
        (storyboard_dir / "storyboard_sheet_v01.svg").write_text(
            "<svg xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"100\" height=\"100\"/></svg>\n",
            encoding="utf-8",
        )
        (segment_dir / "S01.txt").write_text("video prompt\n", encoding="utf-8")
        (keyframe_dir / "P01.txt").write_text("keyframe prompt\n", encoding="utf-8")
        manifest = {
            "project_title": "SVG Storyboard Negative Fixture",
            "workflow_version": "0.1.0-alpha",
            "skill_versions": {
                "storyboard-video-director": "0.1.0-alpha",
                "storyboard-video-qc": "0.1.0-alpha",
            },
            "target_duration": "12s",
            "aspect_ratio": "16:9",
            "storyboard_type": "beat_storyboard",
            "control_strategy": "body_driven_transformation",
            "layout_pattern": "6_panel_transformation_strip",
            "video_model": "seedance2",
            "seedance2_segment_limit": "5-15s",
            "user_hard_constraints": {
                "subject_identity": "girl transforms pages into cloak",
                "required_final_payoff": "cloak settles steady",
                "visual_style": "visual storyboard before video generation",
            },
            "reference_assets": {
                "storyboard_control": {
                    "role": "controls transformation action",
                    "path": "11_generated_storyboards/storyboard_sheet_v01.svg",
                    "status": "generated",
                },
                "character_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "prop_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "environment_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "style_reference": {"role": "not needed", "path": None, "status": "not_needed"},
                "clean_keyframe_reference": {
                    "role": "prompt-only keyframes",
                    "path": "06_clean_keyframe_prompts",
                    "status": "prompt_only",
                },
            },
            "segments": [
                {
                    "segment_id": "S01",
                    "duration": "12s",
                    "function": "transformation",
                    "control_mode": "body_driven_transformation",
                    "execution_mode": "single_continuous_shot",
                    "reference_beats": ["P01"],
                    "clean_keyframes": ["06_clean_keyframe_prompts/P01.txt"],
                    "prompt_file": "07_seedance2_segment_prompts/S01.txt",
                    "transition_out": "hold",
                }
            ],
        }
        (package_dir / "10_generation_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        code, output = run(
            [
                sys.executable,
                str(DIRECTOR_SCRIPTS / "validate_expected_delivery.py"),
                str(package_dir),
                "--profile",
                "preflight",
                "--visual-storyboard-required",
            ]
        )
        if code == 0:
            errors.append("SVG-only storyboard expected delivery fixture unexpectedly passed:\n" + output)

        code, output = run(
            [
                sys.executable,
                str(QC_SCRIPTS / "preflight_qc.py"),
                str(package_dir),
                "--strict-assets",
            ]
        )
        if code == 0:
            errors.append("SVG-only storyboard QC fixture unexpectedly passed:\n" + output)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-compile", action="store_true", help="Skip Python compilation.")
    args = parser.parse_args()

    errors: list[str] = []
    if not args.skip_compile:
        code, output = run([sys.executable, "-m", "py_compile", *py_files()])
        if code != 0:
            errors.append(f"py_compile failed:\n{output}")

    code, output = run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_skill_versions.py"),
            "--no-installed",
            "--package-dir",
            str(ROOT / "examples" / "fan_kata_minimal"),
        ]
    )
    if code != 0:
        errors.append(f"skill version check failed:\n{output}")

    for fixture in PUBLIC_FIXTURES:
        errors.extend(run_fixture(fixture))
    errors.extend(run_product_lock_negative_fixture())
    errors.extend(run_high_motion_storyboard_negative_fixture())
    errors.extend(run_svg_storyboard_negative_fixture())

    if errors:
        print("Regression failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Regression passed.")
    for fixture in PUBLIC_FIXTURES:
        print(f"- {fixture.relative_to(ROOT)}")
    print("- product-lock prompt-only negative fixture")
    print("- high-motion storyboard prompt-only negative fixture")
    print("- SVG-only storyboard negative fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
