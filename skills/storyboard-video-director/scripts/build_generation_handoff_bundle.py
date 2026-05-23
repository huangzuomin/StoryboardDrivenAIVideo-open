#!/usr/bin/env python3
"""Build a production-ready video generation handoff bundle from a finalized director pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OUTPUT_DIR = "17_generation_handoff"
ASSET_MANIFEST = "asset_manifest.json"
UPLOAD_PROMPT = "video_prompt_for_upload.txt"
READINESS_REPORT = "handoff_readiness_report.md"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


ROLE_ORDER = [
    "storyboard_control",
    "character_reference",
    "prop_reference",
    "environment_reference",
    "style_reference",
    "clean_keyframe_reference",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def maybe_read(path: Path) -> str:
    return read_text(path) if path.exists() else ""


def short_block(text: str, limit: int = 1800) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def rel(package_dir: Path, path: Path) -> str:
    return str(path.resolve().relative_to(package_dir.resolve())).replace("\\", "/")


def image_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(item for item in path.iterdir() if item.suffix.lower() in IMAGE_EXTS)
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
        return [path]
    return []


def role_sort_key(item: dict) -> tuple[int, str]:
    role = item.get("role", "")
    try:
        index = ROLE_ORDER.index(role)
    except ValueError:
        index = len(ROLE_ORDER)
    return index, item.get("upload_ref", "")


def clean_upload_ref(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or "asset"


def collect_assets(package_dir: Path, manifest: dict) -> tuple[list[dict], list[str]]:
    assets = manifest.get("reference_assets", {})
    errors: list[str] = []
    output: list[dict] = []
    if not isinstance(assets, dict):
        return [], ["manifest.reference_assets is missing or invalid"]

    for role, asset in assets.items():
        if not isinstance(asset, dict):
            errors.append(f"{role}: invalid asset object")
            continue
        status = asset.get("status")
        if status == "not_needed":
            continue
        if status not in {"generated", "user_supplied"}:
            errors.append(f"{role}: status must be generated/user_supplied/not_needed for handoff, got {status!r}")
            continue
        path_value = asset.get("path")
        if not path_value:
            errors.append(f"{role}: missing path")
            continue
        path = package_dir / str(path_value)
        files = image_files(path)
        if not files:
            errors.append(f"{role}: no supported image files at {path_value}")
            continue
        base_ref = clean_upload_ref(role)
        for index, file_path in enumerate(files, start=1):
            suffix = f"_{index:02d}" if len(files) > 1 else ""
            upload_ref = f"@{base_ref}{suffix}"
            output.append(
                {
                    "upload_ref": upload_ref,
                    "role": role,
                    "local_path": rel(package_dir, file_path),
                    "status": status,
                    "purpose": asset.get("role", ""),
                    "include_in_upload": True,
                    "notes": "Upload this image; do not upload adjacent task .txt files." if role == "clean_keyframe_reference" else "",
                }
            )

    output.sort(key=role_sort_key)
    return output, errors


def segment_lines(manifest: dict) -> list[str]:
    lines: list[str] = []
    for segment in manifest.get("segments", []):
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("segment_id", "Segment")
        duration = segment.get("duration", "")
        function = segment.get("function", "")
        beats = ", ".join(segment.get("reference_beats", []))
        lines.append(f"- {seg_id} ({duration}): {function} Beats: {beats}.")
    return lines


def build_upload_prompt(manifest: dict, assets: list[dict], *, visual_bible: str, beat_plan: str) -> str:
    duration = manifest.get("target_duration", "video")
    aspect_ratio = manifest.get("aspect_ratio", "16:9")
    title = manifest.get("project_title", "Storyboard-driven video")
    lines = [
        "INTENT:",
        f"Generate a {duration} {aspect_ratio} video for: {title}. Preserve the planned story, performance objective, and final payoff.",
        "",
        "ATTACHED REFERENCES:",
    ]
    for asset in assets:
        lines.append(
            f"- {asset['upload_ref']} = {asset['role']}. Use only for this role: {asset.get('purpose') or 'reference control'}"
        )
    lines.extend(
        [
            "",
            "BEATS:",
            *(segment_lines(manifest) or ["- Follow the approved ordered storyboard beats."]),
            "",
            "CAMERA AND STORYBOARD CONTROL DETAIL:",
            short_block(beat_plan or "Follow the approved Beat Storyboard Plan for ordered shots, camera movement, action direction, timing, composition, and final hold."),
            "",
            "VISUAL CONTINUITY DETAIL:",
            short_block(visual_bible or "Follow the approved Visual Bible for identity, product/prop lock, environment, lighting, style, and avoid list."),
            "",
            "EXECUTION:",
            "Use storyboard_control only for choreography, timing, camera, staging, panel order, and motion planning.",
            "Use character_reference only for identity, proportions, face, hair, costume, and body language.",
            "Use prop_reference only for prop silhouette, scale, material, moving parts, allowed motion, and forbidden mutations.",
            "Use environment_reference only for geography, platforms, props, lighting, weather, and spatial continuity.",
            "Use style_reference only for render finish, line quality, texture density, color grade, lighting treatment, lens tone, and completion level.",
            "Use clean_keyframe_reference only as clean final-frame/keyframe look references.",
            "Expand motion naturally between storyboard beats with body weight, prop physics, cloth and hair response, camera inertia, and environmental motion.",
            "",
            "ADHERENCE:",
            "Treat every storyboard panel as an ordered cinematic beat, not as one page image.",
            "Do not skip, merge, reorder, or reinterpret panels.",
            "",
            "AVOID:",
            "Do not render storyboard artifacts, colored annotations, arrows, motion lines, handwritten notes, labels, panel numbers, borders, timing marks, sketch overlays, text, UI, logos, subtitles, or watermarks.",
            "Do not change identity, costume/body design, prop design, location, lighting logic, visual style, screen direction, final pose, or payoff.",
            "Do not add extra characters, unrelated action, unrelated cuts, random camera drift, broken physics, severe deformation, or extra limbs.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def validate_upload_prompt(prompt: str) -> list[str]:
    errors: list[str] = []
    if re.search(r"[A-Za-z]:\\", prompt):
        errors.append("upload prompt contains a Windows absolute path")
    if "missing reference" in prompt.lower():
        errors.append("upload prompt mentions missing references")
    required = [
        "ATTACHED REFERENCES:",
        "Do not skip, merge, reorder, or reinterpret panels.",
        "Do not render storyboard artifacts",
    ]
    for phrase in required:
        if phrase not in prompt:
            errors.append(f"upload prompt missing phrase: {phrase}")
    return errors


def write_bundle(package_dir: Path, manifest: dict, assets: list[dict], errors: list[str]) -> Path:
    output_dir = package_dir / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    upload_prompt = build_upload_prompt(
        manifest,
        assets,
        visual_bible=maybe_read(package_dir / "03_visual_bible.md"),
        beat_plan=maybe_read(package_dir / "04_beat_storyboard_plan.md"),
    )
    prompt_errors = validate_upload_prompt(upload_prompt)
    all_errors = [*errors, *prompt_errors]
    verdict = "READY" if not all_errors else "FIX BEFORE HANDOFF"

    (output_dir / ASSET_MANIFEST).write_text(
        json.dumps({"assets": assets}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / UPLOAD_PROMPT).write_text(upload_prompt, encoding="utf-8")

    lines = [
        "# Generation Handoff Readiness",
        "",
        f"- Verdict: {verdict}",
        f"- Project: {manifest.get('project_title', 'not recorded')}",
        f"- Asset count: {len(assets)}",
        "",
        "## Upload Assets",
        "",
    ]
    if assets:
        for asset in assets:
            lines.append(f"- {asset['upload_ref']} [{asset['role']}]: {asset['local_path']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Blockers", ""])
    if all_errors:
        lines.extend(f"- {error}" for error in all_errors)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            f"- {OUTPUT_DIR}/{ASSET_MANIFEST}",
            f"- {OUTPUT_DIR}/{UPLOAD_PROMPT}",
            f"- {OUTPUT_DIR}/{READINESS_REPORT}",
        ]
    )

    report_path = output_dir / READINESS_REPORT
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
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

    assets, errors = collect_assets(package_dir, manifest)
    report_path = write_bundle(package_dir, manifest, assets, errors)
    report = read_text(report_path)
    verdict = "READY" if "- Verdict: READY" in report else "FIX BEFORE HANDOFF"
    print(f"Generation handoff readiness: {verdict}")
    print(f"Wrote report: {report_path}")
    return 0 if verdict == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
