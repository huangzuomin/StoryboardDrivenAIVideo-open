#!/usr/bin/env python3
"""Production preflight QC for storyboard-video director packs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DIRECTOR_SCRIPT_DIR = Path(__file__).resolve().parents[2] / "storyboard-video-director" / "scripts"
if str(DIRECTOR_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(DIRECTOR_SCRIPT_DIR))

from control_strategy_requirements import infer_requirements


REPORT_NAME = "15_preflight_qc.md"

REQUIRED_PACK_FILES = [
    "00_control_strategy.md",
    "02_duration_segment_plan.md",
    "03_visual_bible.md",
    "04_beat_storyboard_plan.md",
    "05_annotated_storyboard_prompt.txt",
    "08_segment_beat_mapping.json",
    "09_editing_plan.md",
    "10_generation_manifest.json",
]

PROMPT_ARTIFACT_FORBIDS = [
    "do not render storyboard",
    "arrows",
    "panel numbers",
    "borders",
    "subtitles",
    "watermarks",
]

ORDERED_BEAT_PHRASES = [
    "ordered cinematic beat",
    "do not skip, merge, reorder, or reinterpret",
]

HIGH_MOTION_MODES = {
    "rhythm_performance_board",
    "body_driven_transformation",
    "storyboard_heavy",
}


@dataclass
class Finding:
    severity: str
    area: str
    message: str
    fix: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def maybe_read(path: Path) -> str:
    return read_text(path) if path.exists() else ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rel(package_dir: Path, path: Path) -> str:
    try:
        return str(path.relative_to(package_dir)).replace("\\", "/")
    except ValueError:
        return str(path)


def run_director_validation(package_dir: Path) -> tuple[bool, str]:
    candidates = [
        Path(__file__).resolve().parents[2] / "storyboard-video-director" / "scripts" / "validate_package.py",
        Path.cwd() / "skills" / "storyboard-video-director" / "scripts" / "validate_package.py",
        Path.home() / ".codex" / "skills" / "storyboard-video-director" / "scripts" / "validate_package.py",
    ]
    script = next((path for path in candidates if path.exists()), None)
    if script is None:
        return False, "validate_package.py not found; skipped structural validation."
    result = subprocess.run(
        [sys.executable, str(script), str(package_dir)],
        text=True,
        capture_output=True,
        check=False,
    )
    output = (result.stdout or result.stderr).strip()
    return result.returncode == 0, output


def discover_images(package_dir: Path) -> list[Path]:
    image_dir = package_dir / "11_generated_storyboards"
    if not image_dir.is_dir():
        return []
    images: list[Path] = []
    for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        images.extend(image_dir.glob(pattern))
    return sorted(images)


def prompt_files(package_dir: Path) -> list[Path]:
    prompt_dir = package_dir / "12_video_generation_prompt"
    files: list[Path] = []
    if prompt_dir.is_dir():
        files.extend(sorted(prompt_dir.glob("*.txt")))
    segment_dir = package_dir / "07_seedance2_segment_prompts"
    if segment_dir.is_dir():
        files.extend(sorted(segment_dir.glob("*.txt")))
    return files


def asset_path_exists(package_dir: Path, asset: dict) -> bool:
    path_value = asset.get("path")
    if not path_value:
        return False
    return (package_dir / str(path_value)).exists()


def asset_is_real(asset: dict) -> bool:
    return asset.get("status") in {"generated", "user_supplied"} and bool(asset.get("path"))


def asset_is_not_needed(asset: object) -> bool:
    return isinstance(asset, dict) and asset.get("status") == "not_needed"


def supported_images(path: Path) -> list[Path]:
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.suffix.lower() in exts)
    if path.is_file() and path.suffix.lower() in exts:
        return [path]
    return []


def schematic_files(path: Path) -> list[Path]:
    exts = {".svg"}
    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.suffix.lower() in exts)
    if path.is_file() and path.suffix.lower() in exts:
        return [path]
    return []


def modes_from_manifest(manifest: dict) -> set[str]:
    modes: set[str] = set()
    for segment in manifest.get("segments", []):
        if not isinstance(segment, dict):
            continue
        for key in ("control_mode", "execution_mode", "mode"):
            value = segment.get(key)
            if value:
                modes.update(str(value).split())
    strategy = manifest.get("control_strategy")
    if strategy:
        modes.update(str(strategy).split())
    return {mode.strip().lower() for mode in modes if mode.strip()}


def strict_asset_severity(strict_assets: bool) -> str:
    return "blocker" if strict_assets else "warning"


def collect_findings(
    package_dir: Path,
    manifest: dict,
    validation_ok: bool,
    validation_output: str,
    *,
    strict_assets: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []

    for filename in REQUIRED_PACK_FILES:
        path = package_dir / filename
        if not path.exists() or path.stat().st_size == 0:
            findings.append(
                Finding(
                    "blocker",
                    "manifest/files",
                    f"Required pack file is missing or empty: {filename}",
                    f"Regenerate or fill {filename}.",
                )
            )

    if not validation_ok:
        severity = "blocker" if "failed" in validation_output.lower() or "error" in validation_output.lower() else "warning"
        findings.append(
            Finding(
                severity,
                "manifest/files",
                "Director package validation did not pass cleanly.",
                "Run storyboard-video-director validation and fix reported structural issues.",
            )
        )

    if not manifest:
        findings.append(
            Finding(
                "blocker",
                "manifest",
                "Manifest is missing or invalid.",
                "Fix 10_generation_manifest.json before video generation.",
            )
        )
        return findings

    segments = manifest.get("segments", [])
    if not isinstance(segments, list) or not segments:
        findings.append(
            Finding("blocker", "manifest", "Manifest has no Segments.", "Add at least one Segment with beats and prompt files.")
        )

    requirements = infer_requirements(package_dir, manifest)
    layout = str(manifest.get("layout_pattern", "")).lower()
    modes = modes_from_manifest(manifest)
    high_motion = (
        "high_motion" in requirements.strategies
        or bool(modes & HIGH_MOTION_MODES)
        or any(token in layout for token in ("12_panel", "16_panel", "action", "rhythm"))
    )

    control_strategy_text = maybe_read(package_dir / "00_control_strategy.md").lower()
    if high_motion and "do not skip, merge, reorder, or reinterpret" not in control_strategy_text:
        findings.append(
            Finding(
                "warning",
                "control strategy",
                "High-motion pack lacks a strong panel-order adherence booster in 00_control_strategy.md.",
                "Add an adherence sentence forbidding skipped, merged, reordered, or reinterpreted panels.",
            )
        )

    visual_bible = maybe_read(package_dir / "03_visual_bible.md").lower()
    beat_plan = maybe_read(package_dir / "04_beat_storyboard_plan.md").lower()
    combined_motion_text = f"{visual_bible}\n{beat_plan}\n{control_strategy_text}"
    if high_motion and not any(term in combined_motion_text for term in ("body-driven", "body driven", "driven by", "laban", "prop logic")):
        findings.append(
            Finding(
                "blocker",
                "motion control",
                "High-motion/action pack does not clearly describe body-driven motion or movement qualities.",
                "Add body-driven prop/action logic and movement qualities to 03_visual_bible.md and 04_beat_storyboard_plan.md.",
            )
        )
    if high_motion and not any(term in combined_motion_text for term in ("final payoff", "held", "steady", "controlled stop", "final pose")):
        findings.append(
            Finding(
                "warning",
                "motion control",
                "Final payoff is not clearly protected.",
                "Add a final held pose/payoff check in 00_control_strategy.md and final Beats.",
            )
        )

    if "face_readability" in requirements.semantic_checks and not any(
        term in combined_motion_text
        for term in (
            "close-up",
            "close up",
            "close-medium",
            "expression sheet",
            "micro-expression",
            "jaw",
            "eyes",
            "eyelid",
            "mouth corner",
            "facs",
            "眼神",
            "下颌",
            "嘴角",
            "特写",
        )
    ):
        findings.append(
            Finding(
                "blocker",
                "emotion control",
                "Face/emotion-flow pack does not describe readable facial performance states.",
                "Add close-up or expression-sheet controls for eyes, jaw, mouth corners, breath, and public-mask recovery.",
            )
        )

    if "emotion_progression" in requirements.semantic_checks and not any(
        term in combined_motion_text
        for term in ("emotion model", "arousal", "forced calm", "near tears", "mask", "break", "情绪", "强装", "崩", "克制")
    ):
        findings.append(
            Finding(
                "warning",
                "emotion control",
                "Emotion progression is not explicitly modeled.",
                "Add an emotion model showing the transition from starting mask to peak leak to final recovered mask.",
            )
        )

    if "spatial_route" in requirements.semantic_checks and not all(
        term in combined_motion_text for term in ("safe", "route", "victim")
    ):
        findings.append(
            Finding(
                "blocker",
                "spatial control",
                "Spatial route action lacks explicit safe zone, route, and victim-position language.",
                "Lock the start zone, route path, hazard positions, victim location, and return path in storyboard/environment assets.",
            )
        )

    if "prop_continuity" in requirements.semantic_checks and "rope" in combined_motion_text and not any(
        term in combined_motion_text
        for term in ("taut", "attached", "anchor", "carabiner", "tension", "slack", "绷紧", "固定")
    ):
        findings.append(
            Finding(
                "blocker",
                "prop continuity",
                "Rope/prop continuity lacks attachment and tension logic.",
                "Describe anchor point, attachment point, taut/slack states, and how the rope leads the viewer through each beat.",
            )
        )

    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict) or not assets:
        findings.append(
            Finding("blocker", "reference assets", "Manifest lacks reference_assets roles.", "Upgrade/fix manifest reference_assets.")
        )
    else:
        for role in sorted(requirements.required_assets):
            asset = assets.get(role, {})
            if asset_is_not_needed(asset):
                findings.append(
                    Finding(
                        "blocker",
                        "reference assets",
                        f"{role} is marked not_needed but the inferred strategy requires it.",
                        f"Generate/register {role} or revise the control strategy if it truly is not needed.",
                    )
                )
            elif not isinstance(asset, dict) or not asset_is_real(asset):
                status = asset.get("status", "missing") if isinstance(asset, dict) else "missing"
                severity = "blocker" if strict_assets or role in {"storyboard_control", "prop_reference"} else "warning"
                findings.append(
                    Finding(
                        severity,
                        "reference assets",
                        f"Inferred strategy requires a real {role}; current status is {status}.",
                        f"Generate or attach {role} image and update 10_generation_manifest.json.",
                    )
                )

        storyboard = assets.get("storyboard_control", {})
        if not isinstance(storyboard, dict) or storyboard.get("status") == "missing":
            findings.append(
                Finding(
                    "blocker",
                    "reference assets",
                    "storyboard_control is missing.",
                    "Generate or attach a storyboard control image/prompt before video generation.",
                )
            )
        elif storyboard.get("path") and not asset_path_exists(package_dir, storyboard):
            findings.append(
                Finding(
                    "blocker",
                    "reference assets",
                    "storyboard_control path does not exist.",
                    "Fix reference_assets.storyboard_control.path in 10_generation_manifest.json.",
                )
            )
        elif isinstance(storyboard, dict) and storyboard.get("path"):
            storyboard_path = package_dir / str(storyboard.get("path"))
            if storyboard_path.exists() and schematic_files(storyboard_path) and not supported_images(storyboard_path):
                findings.append(
                    Finding(
                        "blocker",
                        "storyboard image",
                        "storyboard_control is SVG/schematic-only, not a raster image2/image-generation storyboard.",
                        "Generate a PNG/JPG/WebP storyboard_control image with image2/image generation and register SVG maps as schematic/route references only.",
                    )
                )

        character = assets.get("character_reference", {})
        character_missing = not isinstance(character, dict) or character.get("status") == "missing"
        identity_central = any(term in combined_motion_text for term in ("costume", "face", "hair", "fan", "sleeve", "character", "identity"))
        if asset_is_not_needed(character):
            pass
        elif character_missing and identity_central:
            findings.append(
                Finding(
                    strict_asset_severity(strict_assets),
                    "reference assets",
                    "character_reference is missing even though identity/costume/prop consistency is central.",
                    "Generate or attach a character sheet before final handoff if identity drift is unacceptable.",
                )
            )
        elif strict_assets and identity_central and isinstance(character, dict) and not asset_is_real(character):
            findings.append(
                Finding(
                    "blocker",
                    "reference assets",
                    "strict asset QC requires a generated or user-supplied character_reference for this identity/costume-heavy pack.",
                    "Generate or attach a character sheet image and update reference_assets.character_reference.",
                )
            )

        prop_central = any(term in combined_motion_text for term in ("fan", "sleeve", "fabric", "ribbon", "rope", "bat", "sword", "prop", "object lock"))
        prop = assets.get("prop_reference", {})
        if prop_central:
            if not isinstance(prop, dict) or prop.get("status") == "missing":
                findings.append(
                    Finding(
                        strict_asset_severity(strict_assets),
                        "reference assets",
                        "prop_reference is missing even though a central prop/fabric path drives the video.",
                        "Generate or attach a prop sheet before final handoff if prop drift is unacceptable.",
                    )
                )
            elif prop.get("status") == "prompt_only":
                findings.append(
                    Finding(
                        "blocker" if strict_assets else "info",
                        "reference assets",
                        "prop_reference is prompt_only for a prop-heavy pack.",
                        "Generate a prop sheet image when prop silhouette, scale, or moving parts must stay stable.",
                    )
                )
            elif prop.get("path") and not asset_path_exists(package_dir, prop):
                findings.append(
                    Finding(
                        "blocker",
                        "reference assets",
                        "prop_reference path does not exist.",
                        "Fix reference_assets.prop_reference.path in 10_generation_manifest.json.",
                    )
                )

        environment_critical = any(term in combined_motion_text for term in ("chase", "rescue", "geography", "route", "map", "spatial", "terrace", "courtyard", "water", "platform", "stairs"))
        style_critical = any(term in combined_motion_text for term in ("product", "brand", "style reference", "style-critical", "visual style", "gufeng", "wuxia", "anime", "rough planning"))
        for role in ("environment_reference", "style_reference"):
            asset = assets.get(role, {})
            if not isinstance(asset, dict) or asset.get("status") == "missing":
                critical = (role == "environment_reference" and environment_critical) or (role == "style_reference" and style_critical)
                findings.append(
                    Finding(
                        "blocker" if strict_assets and critical else "info",
                        "reference assets",
                        f"{role} is missing.",
                        f"Accept as a risk or add a {role} when geography/style fidelity matters.",
                    )
                )
            elif strict_assets and not asset_is_real(asset):
                critical = (role == "environment_reference" and environment_critical) or (role == "style_reference" and style_critical)
                if critical:
                    findings.append(
                        Finding(
                            "blocker",
                            "reference assets",
                            f"strict asset QC requires a generated or user-supplied {role}.",
                            f"Generate or attach a {role} image and update manifest.",
                        )
                    )

        clean = assets.get("clean_keyframe_reference", {})
        if isinstance(clean, dict) and clean.get("status") in {"generated", "user_supplied"}:
            path_value = clean.get("path")
            path = package_dir / str(path_value) if path_value else package_dir / "__missing__"
            if not path.exists() or not supported_images(path):
                findings.append(
                    Finding(
                        "blocker",
                        "reference assets",
                        "clean_keyframe_reference is marked generated/user_supplied but contains no supported image files.",
                        "Generate or attach clean keyframe images under the registered clean keyframe path.",
                    )
                )

    images = discover_images(package_dir)
    storyboard_status = assets.get("storyboard_control", {}).get("status") if isinstance(assets, dict) else ""
    if storyboard_status == "generated" and not images:
        findings.append(
            Finding(
                "blocker",
                "storyboard image",
                "Manifest says storyboard_control is generated but no image exists under 11_generated_storyboards.",
                "Copy the accepted storyboard image into 11_generated_storyboards/ and update review summary.",
            )
        )
    segments = manifest.get("segments", [])
    if isinstance(segments, list) and len(segments) > 1:
        image_dir = package_dir / "11_generated_storyboards"
        missing_segment_images: list[str] = []
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            seg_id = str(segment.get("segment_id") or "").strip()
            if not seg_id:
                continue
            candidates = []
            if image_dir.is_dir():
                for pattern in (
                    f"storyboard_{seg_id}_*.png",
                    f"storyboard_{seg_id}_*.jpg",
                    f"storyboard_{seg_id}_*.jpeg",
                    f"storyboard_{seg_id}_*.webp",
                ):
                    candidates.extend(image_dir.glob(pattern))
            if not candidates:
                missing_segment_images.append(seg_id)
        if missing_segment_images:
            findings.append(
                Finding(
                    "blocker",
                    "storyboard image",
                    "Multi-Segment pack is missing Segment-specific storyboard image(s): "
                    + ", ".join(missing_segment_images),
                    "Generate 11_generated_storyboards/storyboard_Sxx_<variant>.png for every Segment. A shared overview sheet is not enough for direct video control.",
                )
            )

    prompts = prompt_files(package_dir)
    if not prompts:
        findings.append(
            Finding("blocker", "prompt contract", "No downstream video prompt files found.", "Build final/concise video prompts before handoff.")
        )
    else:
        prompt_text = "\n".join(maybe_read(path).lower() for path in prompts)
        model_facing_prompts = [
            path
            for path in prompts
            if path.name in {"video_generation_prompt.txt", "video_generation_prompt_concise_seedance.txt"}
            or path.parent.name == "07_seedance2_segment_prompts"
        ]
        model_facing_text = "\n".join(maybe_read(path).lower() for path in model_facing_prompts)
        if "missing reference" in model_facing_text or "as missing reference" in model_facing_text:
            findings.append(
                Finding(
                    "warning",
                    "prompt contract",
                    "Model-facing prompt mentions missing references.",
                    "Remove missing-reference lines from concise/selected handoff prompts; keep missing asset status in QC reports only.",
                )
            )
        for phrase in ORDERED_BEAT_PHRASES:
            if phrase not in prompt_text:
                findings.append(
                    Finding(
                        "blocker",
                        "prompt contract",
                        f"Downstream prompts do not include required ordered-panel contract: {phrase}",
                        "Add the phrase to final/concise prompts.",
                    )
                )
        for phrase in PROMPT_ARTIFACT_FORBIDS:
            if phrase not in prompt_text:
                findings.append(
                    Finding(
                        "warning",
                        "prompt contract",
                        f"Downstream prompts may not suppress storyboard artifact: {phrase}",
                        "Add explicit avoid language for storyboard artifacts.",
                    )
                )

        concise = package_dir / "12_video_generation_prompt" / "video_generation_prompt_concise_seedance.txt"
        if not concise.exists() or concise.stat().st_size == 0:
            findings.append(
                Finding(
                    "warning",
                    "prompt contract",
                    "Concise Seedance-style prompt is missing.",
                    "Generate or hand-write a shorter prompt contract for model-facing handoff.",
                )
            )

    mapping_path = package_dir / "08_segment_beat_mapping.json"
    if mapping_path.exists() and manifest.get("segments"):
        try:
            mapping = load_json(mapping_path)
            mapping_ids = {str(seg.get("segment_id")) for seg in mapping.get("segments", []) if isinstance(seg, dict)}
            manifest_ids = {str(seg.get("segment_id")) for seg in manifest.get("segments", []) if isinstance(seg, dict)}
            if mapping_ids and manifest_ids and mapping_ids != manifest_ids:
                findings.append(
                    Finding(
                        "blocker",
                        "manifest/files",
                        "Segment IDs differ between manifest and 08_segment_beat_mapping.json.",
                        "Align Segment IDs and beat lists.",
                    )
                )
        except Exception as exc:  # noqa: BLE001
            findings.append(
                Finding("blocker", "manifest/files", f"08_segment_beat_mapping.json is invalid JSON: {exc}", "Fix JSON syntax.")
            )

    return findings


def choose_verdict(findings: list[Finding], manifest: dict) -> str:
    if any(f.severity == "blocker" for f in findings):
        # Strategy reset is reserved for explicit mismatches rather than missing files.
        strategy_mismatch = any(
            f.area == "control strategy" and "mismatch" in f.message.lower()
            for f in findings
        )
        return "STRATEGY RESET" if strategy_mismatch else "FIX BEFORE GENERATION"
    if any(f.severity == "warning" for f in findings):
        return "READY WITH RISKS"
    return "READY"


def severity_rank(severity: str) -> int:
    return {"blocker": 0, "warning": 1, "info": 2}.get(severity, 3)


def write_report(
    package_dir: Path,
    manifest: dict,
    findings: list[Finding],
    validation_output: str,
    *,
    strict_assets: bool = False,
) -> Path:
    verdict = choose_verdict(findings, manifest)
    sorted_findings = sorted(findings, key=lambda item: (severity_rank(item.severity), item.area, item.message))

    blockers = [f for f in sorted_findings if f.severity == "blocker"]
    warnings = [f for f in sorted_findings if f.severity == "warning"]
    infos = [f for f in sorted_findings if f.severity == "info"]

    lines = [
        "# Storyboard Video Preflight QC",
        "",
        f"- Verdict: {verdict}",
        f"- Project: {manifest.get('project_title', 'not recorded') if manifest else 'not recorded'}",
        f"- Target duration: {manifest.get('target_duration', 'not recorded') if manifest else 'not recorded'}",
        f"- Layout: {manifest.get('layout_pattern', 'not recorded') if manifest else 'not recorded'}",
        f"- Control strategy: {manifest.get('control_strategy', 'not recorded') if manifest else 'not recorded'}",
        f"- Strict asset QC: {'enabled' if strict_assets else 'disabled'}",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(
        f"- [{f.area}] {f.message} Fix: {f.fix}" for f in blockers
    )
    if not blockers:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    lines.extend(
        f"- [{f.area}] {f.message} Fix: {f.fix}" for f in warnings
    )
    if not warnings:
        lines.append("- None")

    lines.extend(["", "## Notes", ""])
    lines.extend(
        f"- [{f.area}] {f.message} Action: {f.fix}" for f in infos
    )
    if not infos:
        lines.append("- None")

    prompt_dir = package_dir / "12_video_generation_prompt"
    concise = prompt_dir / "video_generation_prompt_concise_seedance.txt"
    lines.extend(
        [
            "",
            "## Handoff Recommendation",
            "",
        ]
    )
    if verdict == "READY":
        lines.append("- Proceed to video generation. Prefer the concise prompt when visual references carry the details.")
    elif verdict == "READY WITH RISKS":
        lines.append("- Proceed only if the listed warnings are acceptable. Prefer fixing missing identity/style references for expensive generations.")
    elif verdict == "FIX BEFORE GENERATION":
        lines.append("- Do not submit to video generation until blockers are fixed.")
    else:
        lines.append("- Revisit control strategy/layout before generating video.")
    if concise.exists():
        lines.append(f"- Concise prompt available: {rel(package_dir, concise)}")

    if validation_output:
        lines.extend(["", "## Structural Validation", "", "```text", validation_output, "```"])

    report_path = package_dir / REPORT_NAME
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary instead of text.")
    parser.add_argument(
        "--strict-assets",
        action="store_true",
        help="Require generated or user-supplied real reference assets for central identity, prop, environment, or style controls.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    manifest_path = package_dir / "10_generation_manifest.json"
    manifest: dict = {}
    manifest_error = ""
    if manifest_path.exists():
        try:
            manifest = load_json(manifest_path)
        except Exception as exc:  # noqa: BLE001
            manifest_error = str(exc)
    else:
        manifest_error = f"missing {manifest_path}"

    validation_ok, validation_output = run_director_validation(package_dir)
    findings: list[Finding] = []
    if manifest_error:
        findings.append(Finding("blocker", "manifest", f"Manifest could not be loaded: {manifest_error}", "Fix manifest JSON."))
    findings.extend(
        collect_findings(
            package_dir,
            manifest,
            validation_ok,
            validation_output,
            strict_assets=args.strict_assets,
        )
    )
    report_path = write_report(package_dir, manifest, findings, validation_output, strict_assets=args.strict_assets)
    verdict = choose_verdict(findings, manifest)

    if args.json:
        print(
            json.dumps(
                {
                    "verdict": verdict,
                    "strict_assets": args.strict_assets,
                    "report_path": str(report_path),
                    "findings": [finding.__dict__ for finding in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Preflight verdict: {verdict}")
        print(f"Wrote report: {report_path}")
        for finding in sorted(findings, key=lambda item: (severity_rank(item.severity), item.area, item.message)):
            print(f"- {finding.severity.upper()} [{finding.area}] {finding.message}")

    return 1 if verdict in {"FIX BEFORE GENERATION", "STRATEGY RESET"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
