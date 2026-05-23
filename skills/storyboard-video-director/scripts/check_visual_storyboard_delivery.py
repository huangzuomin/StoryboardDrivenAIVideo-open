#!/usr/bin/env python3
"""Fail if a requested visual storyboard has not been delivered as an image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    storyboard_dir = package_dir / "11_generated_storyboards"
    images = []
    if storyboard_dir.is_dir():
        images = sorted(
            path
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp")
            for path in storyboard_dir.glob(pattern)
        )

    if not images:
        print(
            "Visual storyboard delivery check failed: no storyboard image found under "
            f"{storyboard_dir}. Generate or copy the accepted storyboard image there "
            "before final response, or state the image-generation blocker explicitly."
        )
        return 1

    manifest_path = package_dir / "10_generation_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            print(f"Visual storyboard delivery check failed: manifest is not valid JSON: {exc}")
            return 1

        segments = manifest.get("segments", []) if isinstance(manifest, dict) else []
        if isinstance(segments, list) and len(segments) > 1:
            missing_segments: list[str] = []
            found_segments: list[tuple[str, Path]] = []
            for segment in segments:
                if not isinstance(segment, dict):
                    continue
                seg_id = str(segment.get("segment_id") or "").strip()
                if not seg_id:
                    continue
                candidates = sorted(
                    path
                    for pattern in (f"storyboard_{seg_id}_*.png", f"storyboard_{seg_id}_*.jpg", f"storyboard_{seg_id}_*.jpeg", f"storyboard_{seg_id}_*.webp")
                    for path in storyboard_dir.glob(pattern)
                )
                if candidates:
                    found_segments.append((seg_id, candidates[0]))
                else:
                    missing_segments.append(seg_id)
            if missing_segments:
                print(
                    "Visual storyboard delivery check failed: multi-Segment pack is missing "
                    "Segment-specific storyboard image(s)."
                )
                for seg_id in missing_segments:
                    print(f"- missing 11_generated_storyboards/storyboard_{seg_id}_<variant>.png")
                print("A shared overview storyboard is not sufficient for direct multi-Segment video control.")
                return 1
            if found_segments:
                print("Segment-specific storyboard images found:")
                for seg_id, path in found_segments:
                    print(f"- {seg_id}: {path}")

    print("Visual storyboard delivery check passed:")
    for path in images:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
