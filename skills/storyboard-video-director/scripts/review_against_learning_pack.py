#!/usr/bin/env python3
"""Review a director pack against the aimikoda learning pack patterns."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path


DEFAULT_OUTPUT_PREFIX = "storyboard_skill_iteration_suggestions"
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "this",
    "that",
    "use",
    "uses",
    "using",
    "video",
    "storyboard",
    "panel",
    "panels",
    "reference",
    "references",
    "controls",
    "prompt",
    "segment",
    "beat",
    "beats",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def maybe_read(path: Path) -> str:
    return read_text(path) if path.exists() else ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def tokenize(text: str) -> Counter[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,}", text.lower())
    return Counter(word for word in words if word not in STOPWORDS)


def split_case_studies(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+)$", text, flags=re.MULTILINE))
    cases: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        cases.append((title, text[start:end].strip()))
    return cases


def score(query: Counter[str], candidate: Counter[str]) -> int:
    return sum(min(count, candidate.get(word, 0)) for word, count in query.items())


def collect_pack_text(package_dir: Path) -> str:
    filenames = [
        "00_control_strategy.md",
        "00_project_brief.md",
        "02_duration_segment_plan.md",
        "03_visual_bible.md",
        "04_beat_storyboard_plan.md",
        "05_annotated_storyboard_prompt.txt",
        "09_editing_plan.md",
        "10_generation_manifest.json",
        "14_review_summary.md",
    ]
    parts = [maybe_read(package_dir / name) for name in filenames]
    prompt_dir = package_dir / "12_video_generation_prompt"
    if prompt_dir.is_dir():
        parts.extend(maybe_read(path) for path in sorted(prompt_dir.glob("*.txt")))
    manifest_path = package_dir / "10_generation_manifest.json"
    if manifest_path.exists():
        try:
            manifest = load_json(manifest_path)
        except Exception:  # noqa: BLE001
            manifest = {}
        layout = str(manifest.get("layout_pattern", "")).lower()
        strategy = str(manifest.get("control_strategy", "")).lower()
        joined_segments = " ".join(
            " ".join(
                str(segment.get(key, ""))
                for key in ("function", "control_mode", "execution_mode", "mode")
            )
            for segment in manifest.get("segments", [])
            if isinstance(segment, dict)
        ).lower()
        heuristic_terms: list[str] = []
        if "16_panel_action_sheet" in layout or "sword" in joined_segments or "martial" in joined_segments:
            heuristic_terms.extend(["16-panel Anime Swordsman Action martial arts choreography"] * 4)
        if "jump" in joined_segments or "rope" in joined_segments:
            heuristic_terms.extend(["Jump Rope Choreography Cinematic Anime rhythm performance"] * 4)
        if "product" in layout or "product" in strategy:
            heuristic_terms.extend(["Luxury Skincare Storyboard Animation product continuity"] * 4)
        if "trailer" in layout or "disaster" in joined_segments or "invasion" in joined_segments:
            heuristic_terms.extend(["Cloud Skateboard Rescue Storyboard adventure rescue danger"] * 2)
        if "transformation" in strategy or "rebirth" in joined_segments or "forest" in joined_segments:
            heuristic_terms.extend(["Forest Rebirth environment transformation"] * 4)
        parts.extend(heuristic_terms)
    return "\n\n".join(part for part in parts if part)


def closest_cases(learning_pack: Path, pack_text: str) -> list[tuple[str, int]]:
    case_path = learning_pack / "01_case_studies.md"
    if not case_path.exists():
        return []
    cases = split_case_studies(read_text(case_path))
    query = tokenize(pack_text)
    ranked = []
    for title, body in cases:
        ranked.append((title, score(query, tokenize(title + "\n" + body))))
    return sorted(ranked, key=lambda item: item[1], reverse=True)


def manifest_checks(package_dir: Path) -> tuple[dict, list[str], list[str]]:
    manifest_path = package_dir / "10_generation_manifest.json"
    if not manifest_path.exists():
        return {}, ["missing manifest"], []
    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        return {}, [f"manifest is not valid JSON: {exc}"], []

    issues: list[str] = []
    strengths: list[str] = []
    if manifest.get("control_strategy"):
        strengths.append(f"control_strategy recorded: {manifest.get('control_strategy')}")
    else:
        issues.append("control_strategy missing")
    if manifest.get("layout_pattern"):
        strengths.append(f"layout_pattern recorded: {manifest.get('layout_pattern')}")
    else:
        issues.append("layout_pattern missing")

    if isinstance(manifest.get("reference_assets"), dict):
        strengths.append("reference_assets present in manifest")
        missing_roles = [
            role
            for role, asset in manifest["reference_assets"].items()
            if isinstance(asset, dict) and asset.get("status") == "missing"
        ]
        if missing_roles:
            issues.append("missing reference asset statuses: " + ", ".join(missing_roles))
    else:
        issues.append("reference_assets missing from manifest")

    if isinstance(manifest.get("user_hard_constraints"), dict):
        strengths.append("user_hard_constraints present in manifest")
    else:
        issues.append("user_hard_constraints missing from manifest")

    for segment in manifest.get("segments", []):
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("segment_id", "Segment")
        if not segment.get("control_mode"):
            issues.append(f"{seg_id}: control_mode missing")
        if not segment.get("execution_mode"):
            issues.append(f"{seg_id}: execution_mode missing")
        if len(segment.get("reference_beats", [])) > 5:
            layout = str(manifest.get("layout_pattern", ""))
            control = str(segment.get("control_mode") or segment.get("mode") or "")
            if "16_panel" in layout or "12_panel" in layout or "rhythm" in control:
                strengths.append(f"{seg_id}: dense reference beats look intentional for {layout or control}")
            else:
                issues.append(f"{seg_id}: more than 5 reference beats without dense-layout signal")
    return manifest, issues, strengths


def prompt_checks(package_dir: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    strengths: list[str] = []
    prompt_dir = package_dir / "12_video_generation_prompt"
    concise = prompt_dir / "video_generation_prompt_concise_seedance.txt"
    full = prompt_dir / "video_generation_prompt_full.txt"
    if concise.exists():
        text = read_text(concise).lower()
        strengths.append("concise Seedance prompt exists")
        for phrase in (
            "ordered cinematic beat",
            "do not skip, merge, reorder, or reinterpret",
            "do not render storyboard",
        ):
            if phrase not in text:
                issues.append(f"concise prompt missing adherence phrase: {phrase}")
    else:
        issues.append("concise Seedance prompt missing")
    if full.exists():
        strengths.append("full review prompt exists")
    else:
        issues.append("full review prompt missing")
    return issues, strengths


def storyboard_image_checks(package_dir: Path) -> tuple[list[str], list[str]]:
    story_dir = package_dir / "11_generated_storyboards"
    if not story_dir.is_dir():
        return ["11_generated_storyboards missing"], []
    images = sorted(story_dir.glob("*.png"))
    notes = sorted(story_dir.glob("*_review.md"))
    issues = []
    strengths = []
    if images:
        strengths.append(f"storyboard images present: {len(images)}")
    else:
        issues.append("no storyboard images generated")
    if notes:
        strengths.append(f"storyboard review notes present: {len(notes)}")
    else:
        issues.append("storyboard image review notes missing")
    return issues, strengths


def slugify(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "_".join(words[:5]) or "review"


def build_report(
    *,
    package_dir: Path,
    learning_pack: Path,
    ranked_cases: list[tuple[str, int]],
    manifest: dict,
    issues: list[str],
    strengths: list[str],
    user_correction: str,
    process_issue: str,
    skill_update_target: str,
    regression_test: str,
) -> str:
    top_case = ranked_cases[0][0] if ranked_cases else "unknown"
    top_three = ranked_cases[:3]
    lines = [
        f"# storyboard-video-director skill 复盘建议：{package_dir.name}",
        "",
        f"日期：{date.today().isoformat()}",
        "",
        "## 背景",
        "",
        f"- 学习资源包：`{learning_pack}`",
        f"- 当前复盘对象：`{package_dir}`",
        f"- 最接近原始案例：`{top_case}`",
        "",
        "## Top 3 相似案例",
        "",
    ]
    for title, case_score in top_three:
        lines.append(f"- `{title}`，score={case_score}")

    lines.extend(
        [
            "",
            "## Pack 概览",
            "",
            f"- project_title: {manifest.get('project_title', 'not recorded')}",
            f"- target_duration: {manifest.get('target_duration', 'not recorded')}",
            f"- aspect_ratio: {manifest.get('aspect_ratio', 'not recorded')}",
            f"- control_strategy: {manifest.get('control_strategy', 'not recorded')}",
            f"- layout_pattern: {manifest.get('layout_pattern', 'not recorded')}",
            "",
            "## 已满足项",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in strengths or ["none recorded"])
    lines.extend(["", "## 待迭代问题", ""])
    lines.extend(f"- {item}" for item in issues or ["none detected"])
    lines.extend(
        [
            "",
            "## 建议",
            "",
            "- 若 manifest 仍是旧 schema，先运行 `scripts/upgrade_manifest_schema.py <package_dir> --write`。",
            "- 若缺少 concise prompt，运行 `scripts/build_video_generation_prompt.py <package_dir> --mode concise_seedance`。",
            "- 若缺少 review status/summary，运行 `scripts/build_review_summary.py <package_dir>`。",
            "- 若缺少视觉故事板但用户请求可视化故事板，运行 `scripts/build_storyboard_image_task.py <package_dir>` 并生成图片。",
            "",
            "## User Correction Signals",
            "",
            "User correction:",
            f"- {user_correction or 'none recorded in this automated review'}",
            "",
            "Process issue:",
            f"- {process_issue or 'fill manually if this review was triggered by a user correction'}",
            "",
            "Skill update target:",
            f"- {skill_update_target or 'fill manually if a new workflow or script change is required'}",
            "",
            "Regression test:",
            f"- {regression_test or 'add a plain-language input to `docs/storyboard_skill_reproduction_test_cases.md` if this issue can recur'}",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--learning-pack",
        default="docs/aimikoda_storyboard_learning_pack",
        help="Learning pack directory with 01_case_studies.md.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs",
        help="Directory for the generated review markdown.",
    )
    parser.add_argument("--output", default="", help="Explicit output markdown path.")
    parser.add_argument("--user-correction", default="", help="User correction to record.")
    parser.add_argument("--process-issue", default="", help="Process issue revealed by the correction.")
    parser.add_argument("--skill-update-target", default="", help="Skill files or workflow areas to update.")
    parser.add_argument("--regression-test", default="", help="Plain-language regression test to add or run.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    learning_pack = Path(args.learning_pack).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    pack_text = collect_pack_text(package_dir)
    ranked_cases = closest_cases(learning_pack, pack_text)
    manifest, manifest_issues, manifest_strengths = manifest_checks(package_dir)
    prompt_issues, prompt_strengths = prompt_checks(package_dir)
    image_issues, image_strengths = storyboard_image_checks(package_dir)

    issues = manifest_issues + prompt_issues + image_issues
    strengths = manifest_strengths + prompt_strengths + image_strengths
    report = build_report(
        package_dir=package_dir,
        learning_pack=learning_pack,
        ranked_cases=ranked_cases,
        manifest=manifest,
        issues=issues,
        strengths=strengths,
        user_correction=args.user_correction.strip(),
        process_issue=args.process_issue.strip(),
        skill_update_target=args.skill_update_target.strip(),
        regression_test=args.regression_test.strip(),
    )

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        case_slug = slugify(ranked_cases[0][0] if ranked_cases else package_dir.name)
        output_path = output_dir / f"{DEFAULT_OUTPUT_PREFIX}_{date.today().isoformat()}_{case_slug}.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote learning-pack review: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
