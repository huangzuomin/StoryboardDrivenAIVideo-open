#!/usr/bin/env python3
"""Create an environment reference prompt for a storyboard director pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OUTPUT_DIR = "11_reference_assets"
ENVIRONMENT_PROMPT = "environment_reference_prompt.txt"


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


def location_from_manifest(manifest: dict) -> str:
    constraints = manifest.get("user_hard_constraints", {})
    if isinstance(constraints, dict):
        location = str(constraints.get("location") or "").strip()
        if location:
            return location
    return "Primary environment from the Visual Bible and Beat Storyboard Plan."


def build_environment_prompt(manifest: dict, visual_bible: str, beat_plan: str) -> str:
    title = manifest.get("project_title", "Storyboard environment")
    location = location_from_manifest(manifest)
    aspect_ratio = manifest.get("aspect_ratio", "16:9")
    bible = compact(visual_bible, 1400)
    beats = compact(beat_plan, 1400)

    return f"""Create a clean environment reference sheet for downstream video generation.

Project:
{title}

Environment:
{location}

Purpose:
This is an environment and spatial-continuity reference, not a storyboard and not a final video frame. It controls geography, platforms, action lanes, water/ground surfaces, background props, lighting direction, weather/atmosphere, and repeated environmental anchors. It must not control character identity, action order, choreography, or final render style.

Required sheet layout:
- wide establishing view in {aspect_ratio}
- top-down or isometric spatial map showing action zones and camera-safe paths
- 3/4 view of the main performance/action area
- close callouts for repeated spatial anchors: platforms, stairs, banners, water edges, pillars, doors, railings, props, light sources
- lighting and atmosphere swatches
- foreground / midground / background separation
- scale cue without introducing extra main characters

Spatial lock:
- Preserve the same geography across shots and Segments.
- Keep action lanes open and readable for body movement, prop motion, cloth motion, and camera movement.
- Make recurring landmarks easy to re-identify from different angles.
- Keep water, platform edges, stairs, banners, and obstacles consistent in position and scale when present.
- The reference may include small labels/callouts for production use, but it must not include storyboard panel borders, shot numbers, arrows, motion trails, subtitles, logos, UI, or watermarks.

Visual Bible summary:
{bible}

Beat / action geography summary:
{beats}

Avoid:
storyboard panels, beat numbers, camera arrows, motion annotations, character sheets, isolated prop sheets, unrelated rooms, impossible geography, excessive decorative clutter, logos, subtitles, UI, watermarks.
""".strip() + "\n"


def update_manifest(package_dir: Path, manifest: dict, environment_path: Path) -> None:
    assets = manifest.setdefault("reference_assets", {})
    if isinstance(assets, dict):
        environment = assets.setdefault("environment_reference", {})
        if isinstance(environment, dict):
            if environment.get("status") not in {"generated", "user_supplied"}:
                environment["path"] = str(environment_path.relative_to(package_dir)).replace("\\", "/")
                environment["status"] = "prompt_only"
            environment.setdefault(
                "role",
                "controls geography, platforms, props, lighting, weather, spatial continuity, and action lanes",
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

    environment_path = output_dir / ENVIRONMENT_PROMPT
    environment_path.write_text(build_environment_prompt(manifest, visual_bible, beat_plan), encoding="utf-8")

    if not args.no_manifest_update:
        update_manifest(package_dir, manifest, environment_path)

    print(f"Wrote environment reference prompt: {environment_path}")
    if not args.no_manifest_update:
        print("Updated manifest reference_assets.environment_reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
