#!/usr/bin/env python3
"""Check repo, installed Codex skill, and pack manifest version consistency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTALLED_ROOT = Path.home() / ".codex" / "skills"
SKILLS = ("storyboard-video-director", "storyboard-video-qc")


def read_version_file(skill_dir: Path) -> str:
    path = skill_dir / "VERSION"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig").strip()


def load_manifest(package_dir: Path) -> dict:
    path = package_dir / "10_generation_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed-root", default=str(DEFAULT_INSTALLED_ROOT), help="Codex installed skills root.")
    parser.add_argument("--package-dir", default="", help="Optional director pack to check manifest versions.")
    parser.add_argument("--no-installed", action="store_true", help="Skip installed skill checks.")
    args = parser.parse_args()

    installed_root = Path(args.installed_root).expanduser()
    errors: list[str] = []
    repo_versions: dict[str, str] = {}

    for skill in SKILLS:
        repo_dir = ROOT / "skills" / skill
        version_file = read_version_file(repo_dir)
        repo_versions[skill] = version_file
        if not version_file:
            errors.append(f"{skill}: missing VERSION")

        if not args.no_installed:
            installed_dir = installed_root / skill
            installed_version = read_version_file(installed_dir)
            if not installed_dir.exists():
                errors.append(f"{skill}: installed skill missing at {installed_dir}")
            elif version_file and installed_version != version_file:
                errors.append(f"{skill}: installed VERSION {installed_version or 'missing'} != repo VERSION {version_file}")

    if args.package_dir:
        package_dir = Path(args.package_dir).expanduser().resolve()
        try:
            manifest = load_manifest(package_dir)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"manifest could not be loaded: {exc}")
            manifest = {}
        if not manifest:
            errors.append(f"missing manifest in package: {package_dir}")
        else:
            workflow_version = str(manifest.get("workflow_version", "")).strip()
            director_version = repo_versions.get("storyboard-video-director", "")
            if workflow_version and director_version and workflow_version != director_version:
                errors.append(f"manifest workflow_version {workflow_version} != director VERSION {director_version}")
            skill_versions = manifest.get("skill_versions")
            if not isinstance(skill_versions, dict):
                errors.append("manifest skill_versions is missing or invalid")
            else:
                for skill, version in repo_versions.items():
                    manifest_version = str(skill_versions.get(skill, "")).strip()
                    if manifest_version != version:
                        errors.append(f"manifest skill_versions.{skill} {manifest_version or 'missing'} != repo VERSION {version}")

    if errors:
        print("Skill version check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Skill version check passed.")
    for skill, version in repo_versions.items():
        print(f"- {skill}: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
