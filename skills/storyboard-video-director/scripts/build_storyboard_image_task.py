#!/usr/bin/env python3
"""Build a Codex images2 task for annotated storyboard generation."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_FILES = {
    "prompt": "05_annotated_storyboard_prompt.txt",
    "visual_bible": "03_visual_bible.md",
    "beat_plan": "04_beat_storyboard_plan.md",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--variant",
        default="v01",
        help="Storyboard image variant label, e.g. v01 or v02.",
    )
    parser.add_argument(
        "--segment-id",
        default="",
        help="Build a Segment-specific storyboard image task, e.g. S01.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    segment_id = args.segment_id.strip()

    required = dict(REQUIRED_FILES)
    if segment_id:
        required["prompt"] = f"05_segment_storyboard_prompts/{segment_id}_storyboard_prompt.txt"

    missing = [filename for filename in required.values() if not (package_dir / filename).exists()]
    if missing:
        print("ERROR: missing required files:")
        for filename in missing:
            print(f"- {filename}")
        return 1

    output_dir = package_dir / "11_generated_storyboards"
    output_name = (
        f"storyboard_{segment_id}_{args.variant}.png"
        if segment_id
        else f"storyboard_sheet_{args.variant}.png"
    )

    prompt = read(package_dir / required["prompt"])
    visual_bible = read(package_dir / required["visual_bible"])
    beat_plan = read(package_dir / required["beat_plan"])

    scope = (
        f"Segment-specific storyboard sheet for {segment_id}"
        if segment_id
        else "Full-project overview storyboard sheet"
    )
    scope_requirement = (
        f"This image must contain only the Beats assigned to {segment_id}; do not include previous or future Segment panels."
        if segment_id
        else "This image may show the full project overview for director review; do not use it as the sole video-control asset for multi-Segment generation."
    )

    task = f"""Generate one annotated storyboard sheet image from this director pack.

Output target:
- Save the image as: {output_dir / output_name}
- Aspect ratio: 16:9
- Image type: {scope}, not clean keyframes and not final video frames.
- After saving, update 10_generation_manifest.json reference_assets.storyboard_control.path/status when this image is the accepted storyboard control asset.
- Write or update 14_review_status.md with storyboard image status.

Hard requirements:
- Preserve the panel count, panel labels, and Beat order from the prompt.
- {scope_requirement}
- Use the colored annotation system exactly: red subject movement, blue camera movement, green composition, orange light/signal/danger, purple emotion/narrative pressure.
- Keep labels and annotations readable but sparse.
- Preserve timestamps, beat counts, title strips, and short expressive director notes only when the storyboard prompt explicitly asks for them.
- Avoid logos, subtitles, dense readable text, extra characters, photorealism, polished comic art, poster layout, unrelated props, and any timestamps not requested by the storyboard prompt.
- Write a review note beside the image that states panel count observed, beat order check, text/label density, human overview suitability, direct video-control suitability, contamination risk, and recommended next version.

Annotated storyboard prompt:
{prompt}

Visual Bible continuity:
{visual_bible}

Beat plan:
{beat_plan}
"""

    print(task)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
