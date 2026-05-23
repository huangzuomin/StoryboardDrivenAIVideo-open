#!/usr/bin/env python3
"""Create a storyboard-video-director production pack skeleton."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


WORKFLOW_VERSION = "0.1.0-alpha"
SKILL_VERSIONS = {
    "storyboard-video-director": WORKFLOW_VERSION,
    "storyboard-video-qc": WORKFLOW_VERSION,
}


FILES = {
    "00_control_strategy.md": "# Control Strategy\n\n",
    "00_project_brief.md": "# Project Brief\n\n",
    "01_method_summary.md": "# Method Summary\n\n",
    "02_duration_segment_plan.md": "# Duration and Segment Plan\n\n",
    "03_visual_bible.md": "# Visual Bible\n\n",
    "04_beat_storyboard_plan.md": "# Beat Storyboard Plan\n\n",
    "05_annotated_storyboard_prompt.txt": "",
    "08_segment_beat_mapping.json": '{\n  "segments": []\n}\n',
    "09_editing_plan.md": "# Editing Plan\n\n",
    "14_review_status.md": (
        "# Review Status\n\n"
        "- Text director pack: incomplete\n"
        "- Package validation: not run\n"
        "- Overview storyboard image: missing\n"
        "- Segment storyboard images: missing\n"
        "- Final video prompt: missing\n"
        "- Concise video prompt: missing\n"
        "- Known inconsistencies: none recorded\n"
        "- Recommended next action: complete the director pack and run validation\n"
    ),
    "14_review_summary.md": "# Review Summary\n\n",
    "10_generation_manifest.json": json.dumps(
        {
            "project_title": "",
            "workflow_version": WORKFLOW_VERSION,
            "skill_versions": SKILL_VERSIONS,
            "target_duration": "",
            "aspect_ratio": "16:9",
            "storyboard_type": "beat_storyboard",
            "control_strategy": "",
            "layout_pattern": "",
            "video_model": "seedance2",
            "seedance2_segment_limit": "15s",
            "user_hard_constraints": {
                "target_duration": "",
                "subject_identity": "",
                "location": "",
                "required_final_payoff": "",
                "visual_style": "",
                "explicit_exclusions": [],
            },
            "reference_assets": {
                "storyboard_control": {
                    "path": None,
                    "status": "missing",
                    "role": "controls beat order, camera staging, action path, timing, composition, and emotional progression",
                },
                "character_reference": {
                    "path": None,
                    "status": "missing",
                    "role": "controls identity, costume, proportions, face, and body language",
                },
                "environment_reference": {
                    "path": None,
                    "status": "missing",
                    "role": "controls geography, props, lighting, weather, and spatial continuity",
                },
                "style_reference": {
                    "path": None,
                    "status": "missing",
                    "role": "controls render finish, texture, palette, lens language, and style",
                },
                "clean_keyframe_reference": {
                    "path": "06_clean_keyframe_prompts/",
                    "status": "prompt_only",
                    "role": "controls clean final-frame look without annotations",
                },
            },
            "visual_bible": "03_visual_bible.md",
            "segments": [],
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
}


DIRS = [
    "05_segment_storyboard_prompts",
    "06_clean_keyframe_prompts",
    "07_seedance2_segment_prompts",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Directory to create or update.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing placeholder files.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    package_dir.mkdir(parents=True, exist_ok=True)

    for dirname in DIRS:
        (package_dir / dirname).mkdir(exist_ok=True)

    for name, content in FILES.items():
        path = package_dir / name
        if path.exists() and not args.force:
            continue
        path.write_text(content, encoding="utf-8")

    print(f"Created storyboard director pack skeleton: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
