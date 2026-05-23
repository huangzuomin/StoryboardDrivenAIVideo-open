#!/usr/bin/env python3
"""Check the public release surface for common open-source hygiene issues."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = [
    "README.md",
    "README.en.md",
    "LICENSE",
    "CONTRIBUTING.md",
    ".gitignore",
    ".gitattributes",
    "requirements.txt",
    "skills/storyboard-video-director",
    "skills/storyboard-video-qc",
    "scripts",
    "examples",
    "docs/workflow_nodes.md",
    "docs/production_handoff.md",
    "docs/qc_policy.md",
    "docs/open_source_release_checklist.md",
    "docs/publication_manifest.md",
    "docs/versioning.md",
    "docs/normal_user_prompt_regression_prompts.md",
    "docs/storyboard_skill_reproduction_test_cases.md",
]

TEXT_EXTS = {".md", ".txt", ".json", ".py", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".gitignore", ".gitattributes"}
GENERATED_EXAMPLE_PARTS = {
    "12_video_generation_prompt",
    "13_xyq_video_handoff",
    "17_generation_handoff",
    "17_generation_deployment",
}
SECRET_PATTERNS = [
    re.compile(r"(^|[\s'\"`(])([A-Za-z]:\\)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?key|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{12,}"),
]


def public_files() -> list[Path]:
    files: list[Path] = []
    for item in PUBLIC_PATHS:
        path = ROOT / item
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for candidate in path.rglob("*"):
                parts = set(candidate.relative_to(ROOT).parts)
                if parts & GENERATED_EXAMPLE_PARTS:
                    continue
                if candidate.name.startswith("15_") or candidate.name.startswith("16_"):
                    continue
                if candidate.name.endswith("_image_task.txt"):
                    continue
                if candidate.is_file():
                    files.append(candidate)
    return sorted(set(files))


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTS or path.name in {".gitignore", ".gitattributes"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-placeholder-images", action="store_true", help="Allow text placeholder .png files in examples.")
    args = parser.parse_args()

    errors: list[str] = []
    required = [
        "README.md",
        "README.en.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "requirements.txt",
        "scripts/run_regression.py",
        "scripts/check_skill_versions.py",
        "docs/versioning.md",
    ]
    for item in required:
        if not (ROOT / item).exists():
            errors.append(f"missing required public file: {item}")

    for path in public_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            if not args.allow_placeholder_images and rel.startswith("examples/"):
                errors.append(f"example image needs license/source review or placeholder allowance: {rel}")
            continue
        if not is_text_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            errors.append(f"non-utf8 text file: {rel}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible local path or secret in public file: {rel}")
                break

    if errors:
        print("Open-source readiness check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Open-source readiness check passed for the configured public surface.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
