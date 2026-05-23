#!/usr/bin/env python3
"""Create a first-pass storyboard director pack from a plain-language brief."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from control_strategy_requirements import infer_requirements


def slugify(text: str) -> str:
    ascii_text = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    if ascii_text:
        return ascii_text[:60].strip("_")
    return "storyboard_project"


def infer_duration(brief: str) -> str:
    match = re.search(r"(\d+)\s*(?:秒|s|sec|second|seconds)", brief, re.IGNORECASE)
    return f"{match.group(1)}s" if match else ""


def infer_strategy_and_layout(brief: str) -> tuple[str, str]:
    lower = brief.lower()
    if any(token in lower for token in ("咖啡机", "product", "产品", "一直长得一样", "一致")):
        return "product_lock_hybrid", "3x4_product_board"
    if any(token in lower for token in ("表情", "克制", "强装", "眼神", "inner", "emotion")):
        return "face_emotion_flow_hybrid", "4_panel_horizontal_face_emotion_flow"
    if any(token in lower for token in ("救援", "水", "路线", "空间", "rope", "rescue", "flood")):
        return "storyboard_heavy_object_lock_hybrid", "two_segment_route_action_boards"
    if any(token in lower for token in ("变成", "变化", "斗篷", "transformation", "become", "turns into")):
        return "body_driven_transformation", "6_panel_transformation_strip"
    if any(token in lower for token in ("扇", "袖", "舞", "kata", "dance", "fan", "sleeve")):
        return "rhythm_performance_board_hybrid", "12_panel_rhythm_sheet"
    return "storyboard_heavy", "beat_storyboard"


def infer_title(brief: str) -> str:
    cleaned = re.sub(r"\s+", " ", brief.strip())
    if len(cleaned) <= 28:
        return cleaned
    if "图书馆" in cleaned and "斗篷" in cleaned:
        return "Library Luminous Cloak"
    if "咖啡机" in cleaned:
        return "Coffee Machine Morning"
    if "救援" in cleaned:
        return "City Rescue"
    return cleaned[:28].strip(" ，。,.;")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def seed_pack(package_dir: Path, brief: str) -> None:
    manifest_path = package_dir / "10_generation_manifest.json"
    manifest = read_json(manifest_path)
    title = infer_title(brief)
    duration = infer_duration(brief)
    strategy, layout = infer_strategy_and_layout(brief)

    manifest["project_title"] = title
    manifest["target_duration"] = duration
    manifest["control_strategy"] = strategy
    manifest["layout_pattern"] = layout
    constraints = manifest.setdefault("user_hard_constraints", {})
    constraints["target_duration"] = duration
    constraints["subject_identity"] = brief
    constraints["required_final_payoff"] = "Preserve the user's final payoff exactly."
    constraints["visual_style"] = "professional cinematic preproduction, controllable visual planning"
    constraints["explicit_exclusions"] = ["random reinterpretation", "unmotivated effects", "skipped payoff"]
    manifest["segments"] = [
        {
            "segment_id": "S01",
            "duration": duration or "TBD",
            "control_mode": strategy,
            "execution_mode": "single_continuous_or_motivated_camera_flow",
            "function": "complete user-requested story arc",
            "reference_beats": [],
            "prompt_file": "07_seedance2_segment_prompts/S01.txt",
            "storyboard_prompt_file": "05_segment_storyboard_prompts/S01_storyboard_prompt.txt",
            "transition_out": "hold on the required final payoff",
        }
    ]
    write_json(manifest_path, manifest)

    requirements = infer_requirements(package_dir, manifest, visual_storyboard_required=True)
    (package_dir / "00_project_brief.md").write_text(
        "\n".join(
            [
                "# Project Brief",
                "",
                f"- Project title: {title}",
                f"- User input: {brief}",
                f"- Target duration: {duration or 'not specified'}",
                f"- Initial control strategy: {strategy}",
                f"- Initial layout pattern: {layout}",
                "",
                "## Required Visual Assets",
                "",
                f"- Required now: {', '.join(sorted(requirements.required_assets)) or 'none inferred'}",
                f"- Recommended for final: {', '.join(sorted(requirements.recommended_assets)) or 'none inferred'}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (package_dir / "00_control_strategy.md").write_text(
        "\n".join(
            [
                "# Control Strategy",
                "",
                f"Primary strategy: `{strategy}`.",
                "",
                f"Layout pattern: `{layout}`.",
                "",
                "Reference priority: storyboard controls order/staging/timing; character controls identity; environment controls geography; style controls finish; clean keyframes control final clean look.",
                "",
                "Adherence booster: do not skip, merge, reorder, or reinterpret storyboard panels.",
                "",
                "This file is a first-pass scaffold from a plain-language brief and should be expanded before final handoff.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True, help="Plain-language user video brief.")
    parser.add_argument("--out-root", default="production_packs", help="Root folder for generated packs.")
    parser.add_argument("--slug", default="", help="Optional output slug.")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold placeholders.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[2]
    slug = args.slug or slugify(infer_title(args.brief))
    package_dir = (repo_root / args.out_root / slug).resolve()

    scaffold = script_dir / "scaffold_package.py"
    command = [sys.executable, str(scaffold), str(package_dir)]
    if args.force:
        command.append("--force")
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode

    seed_pack(package_dir, args.brief)

    preview = script_dir / "build_user_preview_summary.py"
    subprocess.run([sys.executable, str(preview), str(package_dir), "--phase", "iteration"], check=False)
    print(f"Created first-pass director pack: {package_dir}")
    print(f"Next: expand storyboard/assets, then run preproduction_orchestrator.py {package_dir} --phase preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

