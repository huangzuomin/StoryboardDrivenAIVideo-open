#!/usr/bin/env python3
"""Create a style reference prompt for a storyboard director pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OUTPUT_DIR = "11_reference_assets"
STYLE_PROMPT = "style_reference_prompt.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def maybe_read(path: Path) -> str:
    return read_text(path) if path.exists() else ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compact(text: str, limit: int = 1800) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def style_from_manifest(manifest: dict) -> str:
    constraints = manifest.get("user_hard_constraints", {})
    if isinstance(constraints, dict):
        style = str(constraints.get("visual_style") or "").strip()
        if style:
            return style
    return "Final rendering style from the Visual Bible."


def build_style_prompt(manifest: dict, visual_bible: str, beat_plan: str) -> str:
    title = manifest.get("project_title", "Storyboard style")
    style = style_from_manifest(manifest)
    aspect_ratio = manifest.get("aspect_ratio", "16:9")
    bible = compact(visual_bible, 1500)
    beats = compact(beat_plan, 1000)

    return f"""Create a clean style reference sheet for downstream video generation.

Project:
{title}

Style target:
{style}

Purpose:
This is a final-render style reference, not a storyboard, not a character sheet, not a prop sheet, and not an environment map. It controls visual finish, line quality, color grading, lighting treatment, texture density, lens feel, motion blur taste, atmosphere, and completion level for the final video. It must not control action order, choreography, character identity, prop scale, or spatial geography.

Required sheet layout:
- one hero frame-style sample in {aspect_ratio} showing the intended final-video finish
- 3-5 small crop samples: face/skin rendering, fabric/sleeve rendering, fan material rendering, stone/water rendering, atmosphere/light bloom
- palette strip with dominant, secondary, accent, shadow, and highlight colors
- line / edge treatment sample
- texture density sample: skin, silk, bamboo/wood, stone, water/mist
- lens and lighting notes as small production callouts
- one "do not use this" mini swatch area showing forbidden finish drift if useful

Style lock:
- The final video should use this reference for rendering finish only.
- Keep the storyboard control board separate from final style. Storyboard arrows, panel borders, notes, rough construction lines, and colored annotation marks must not appear in final video.
- Keep character identity and costume controlled by character_reference, not this style sheet.
- Keep prop shape and scale controlled by prop_reference, not this style sheet.
- Keep geography controlled by environment_reference, not this style sheet.
- The sheet may include small production labels/callouts, but it must not be used as a clean keyframe.

Visual Bible summary:
{bible}

Beat tone summary:
{beats}

Avoid:
storyboard panels, motion arrows, action timing marks, character turnaround layout, prop-only sheet layout, environment map layout, logos, subtitles, UI, watermarks, unreadable clutter, style drift toward unrelated genres, changing the character design, changing prop design, changing environment geography.
""".strip() + "\n"


def update_manifest(package_dir: Path, manifest: dict, style_path: Path) -> None:
    assets = manifest.setdefault("reference_assets", {})
    if isinstance(assets, dict):
        style = assets.setdefault("style_reference", {})
        if isinstance(style, dict):
            if style.get("status") not in {"generated", "user_supplied"}:
                style["path"] = str(style_path.relative_to(package_dir)).replace("\\", "/")
                style["status"] = "prompt_only"
            style.setdefault(
                "role",
                "controls render finish, line quality, texture density, color grade, lighting treatment, lens tone, and completion level",
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

    visual_bible = maybe_read(package_dir / "03_visual_bible.md")
    beat_plan = maybe_read(package_dir / "04_beat_storyboard_plan.md")
    output_dir = package_dir / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    style_path = output_dir / STYLE_PROMPT
    style_path.write_text(build_style_prompt(manifest, visual_bible, beat_plan), encoding="utf-8")

    if not args.no_manifest_update:
        update_manifest(package_dir, manifest, style_path)

    print(f"Wrote style reference prompt: {style_path}")
    if not args.no_manifest_update:
        print("Updated manifest reference_assets.style_reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
