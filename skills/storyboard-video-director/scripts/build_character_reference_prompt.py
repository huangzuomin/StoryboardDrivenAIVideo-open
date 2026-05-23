#!/usr/bin/env python3
"""Create character and central-prop reference prompts for a director pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OUTPUT_DIR = "11_reference_assets"
CHARACTER_PROMPT = "character_sheet_prompt.txt"
PROP_PROMPT = "prop_sheet_prompt.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def maybe_read(path: Path) -> str:
    return read_text(path) if path.exists() else ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compact(text: str, limit: int = 1600) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def likely_central_prop(text: str) -> str:
    lowered = text.lower()
    prop_source = lowered
    # Avoid treating forbidden-mutation phrases as positive prop requirements.
    prop_source = re.sub(r"cannot[^.\n;]*sword", "", prop_source)
    prop_source = re.sub(r"forbidden[^.\n;]*sword", "", prop_source)
    candidates = [
        ("fan", ("fan", "folding fan", "war fan")),
        ("sword", ("sword", "katana")),
        ("sleeves / fabric", ("sleeve", "fabric", "ribbon", "cloth")),
        ("rope", ("rope", "jump rope")),
        ("bat", ("bat", "baseball")),
    ]
    found = [label for label, terms in candidates if any(term in prop_source for term in terms)]
    return ", ".join(found)


def build_character_prompt(manifest: dict, visual_bible: str, beat_plan: str) -> str:
    title = manifest.get("project_title", "Storyboard character")
    constraints = manifest.get("user_hard_constraints", {})
    subject = ""
    style = ""
    if isinstance(constraints, dict):
        subject = str(constraints.get("subject_identity") or "")
        style = str(constraints.get("visual_style") or "")

    bible = compact(visual_bible)
    prop = likely_central_prop(f"{visual_bible}\n{beat_plan}\n{subject}\n{style}")
    prop_line = f"Central prop(s): {prop}." if prop else "Central prop(s): use the Visual Bible if any prop is specified."

    return f"""Create a clean character reference sheet for downstream video generation.

Project:
{title}

Subject:
{subject or "Main performer / subject from the storyboard pack."}

Purpose:
This is an identity reference, not a storyboard. It controls face, hair, body proportions, costume layers, silhouette, color palette, and recurring props. It must not include storyboard arrows, panel borders, shot numbers, action annotations, UI, subtitles, or logos.

Required sheet layout:
- full-body front view
- full-body back view
- left and right profile views
- 3-5 head/face expression close-ups if facial identity matters
- costume detail callouts: collar, sleeves, waist/sash, hem, footwear, hair ornament
- neutral standing pose plus one small pose showing how the costume volume moves
- simple color palette swatches
- prop callout if relevant

Identity lock:
- Preserve the same face, hairstyle, hair accessories, body proportions, costume silhouette, costume layers, and palette across all views.
- Keep the design usable for video generation: readable shapes, no excessive tiny ornaments, no contradictory outfits.
- {prop_line}

Visual Bible summary:
{bible}

Avoid:
storyboard panels, arrows, colored annotations, motion trails, cinematic camera notes, multiple unrelated outfits, redesigning the character between views, extra characters, logos, subtitles, UI, watermarks.
""".strip() + "\n"


def build_prop_prompt(manifest: dict, visual_bible: str, beat_plan: str) -> str:
    title = manifest.get("project_title", "Storyboard prop")
    prop = likely_central_prop(f"{visual_bible}\n{beat_plan}")
    prop_name = prop or "central recurring prop"
    return f"""Create a clean prop reference sheet for downstream video generation.

Project:
{title}

Prop:
{prop_name}

Purpose:
This sheet controls the prop silhouette, scale, material, moving parts, allowed motion, and forbidden mutations. It is not a storyboard.

Required sheet layout:
- closed / neutral state
- open / active state
- side view and top view when useful
- hand-held scale reference
- material and color swatches
- moving-part notes
- allowed motion notes
- forbidden mutation notes

Source behavior from storyboard:
{compact(beat_plan, 1200)}

Avoid:
storyboard arrows, panel borders, action sequence panels, extra redesigned prop variants, floating autonomous prop motion unless explicitly required, logos, UI, subtitles, watermarks.
""".strip() + "\n"


def update_manifest(package_dir: Path, manifest: dict, character_path: Path, prop_path: Path | None) -> None:
    assets = manifest.setdefault("reference_assets", {})
    if isinstance(assets, dict):
        character = assets.setdefault("character_reference", {})
        if isinstance(character, dict):
            if character.get("status") not in {"generated", "user_supplied"}:
                character["path"] = str(character_path.relative_to(package_dir)).replace("\\", "/")
                character["status"] = "prompt_only"
            character.setdefault(
                "role",
                "controls identity, costume, proportions, face, hair, recurring props, and body language",
            )
        if prop_path is not None:
            prop = assets.setdefault("prop_reference", {})
            if isinstance(prop, dict):
                if prop.get("status") not in {"generated", "user_supplied"}:
                    prop["path"] = str(prop_path.relative_to(package_dir)).replace("\\", "/")
                    prop["status"] = "prompt_only"
                prop.setdefault(
                    "role",
                    "controls central prop silhouette, scale, materials, moving parts, allowed motion, and forbidden mutations",
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

    character_path = output_dir / CHARACTER_PROMPT
    prop_path = output_dir / PROP_PROMPT
    character_path.write_text(build_character_prompt(manifest, visual_bible, beat_plan), encoding="utf-8")
    prop_path.write_text(build_prop_prompt(manifest, visual_bible, beat_plan), encoding="utf-8")

    if not args.no_manifest_update:
        update_manifest(package_dir, manifest, character_path, prop_path)

    print(f"Wrote character sheet prompt: {character_path}")
    print(f"Wrote prop sheet prompt: {prop_path}")
    if not args.no_manifest_update:
        print("Updated manifest reference_assets.character_reference and reference_assets.prop_reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
