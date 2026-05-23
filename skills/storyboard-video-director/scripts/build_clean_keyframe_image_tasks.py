#!/usr/bin/env python3
"""Create clean keyframe image-generation tasks for a director pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TASK_DIR = "11_clean_keyframes"
TASK_SUFFIX = "_image_task.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def clean_keyframe_prompt_paths(package_dir: Path, manifest: dict) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    for segment in manifest.get("segments", []):
        if not isinstance(segment, dict):
            continue
        for path_value in segment.get("clean_keyframes", []):
            path = package_dir / str(path_value)
            key = str(path)
            if path.exists() and key not in seen:
                paths.append(path)
                seen.add(key)
    if paths:
        return paths
    prompt_dir = package_dir / "06_clean_keyframe_prompts"
    if prompt_dir.is_dir():
        return sorted(prompt_dir.glob("*.txt"))
    return []


def build_task(package_dir: Path, prompt_path: Path, output_dir: Path) -> str:
    beat_id = prompt_path.stem
    prompt = read_text(prompt_path)
    output_path = output_dir / f"{beat_id}_v01.png"
    return f"""Generate one clean keyframe image for downstream video generation.

Output target:
- Save the image as: {output_path}
- Use the prompt below as the visual content source.
- This image is a clean final-frame/keyframe reference, not a storyboard.

Hard requirements:
- No text, labels, subtitles, logos, UI, watermarks, panel borders, frame grid, arrows, colored annotation marks, motion guides, shot numbers, timing notes, or production callouts.
- Preserve character identity, costume, prop scale, environment geography, lighting logic, and final render style from the director pack references.
- Keep the image usable as a direct video reference frame.
- Do not add extra characters or unrelated props.

Clean keyframe prompt source:
{prompt}
""".strip() + "\n"


def update_manifest(package_dir: Path, manifest: dict, output_dir: Path) -> None:
    assets = manifest.setdefault("reference_assets", {})
    if isinstance(assets, dict):
        clean = assets.setdefault("clean_keyframe_reference", {})
        if isinstance(clean, dict):
            if clean.get("status") not in {"generated", "user_supplied"}:
                clean["path"] = str(output_dir.relative_to(package_dir)).replace("\\", "/") + "/"
                clean["status"] = "prompt_only"
            clean.setdefault(
                "role",
                "controls clean final-frame/keyframe look without annotations, text, arrows, borders, or UI",
            )
    write_json(package_dir / "10_generation_manifest.json", manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument("--no-manifest-update", action="store_true")
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

    prompt_paths = clean_keyframe_prompt_paths(package_dir, manifest)
    if not prompt_paths:
        print("ERROR: no clean keyframe prompts found.")
        return 1

    output_dir = package_dir / TASK_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for prompt_path in prompt_paths:
        task_path = output_dir / f"{prompt_path.stem}{TASK_SUFFIX}"
        task_path.write_text(build_task(package_dir, prompt_path, output_dir), encoding="utf-8")
        written.append(task_path)

    if not args.no_manifest_update:
        update_manifest(package_dir, manifest, output_dir)

    print(f"Wrote {len(written)} clean keyframe image task(s):")
    for path in written:
        print(f"- {path}")
    if not args.no_manifest_update:
        print("Updated manifest reference_assets.clean_keyframe_reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
