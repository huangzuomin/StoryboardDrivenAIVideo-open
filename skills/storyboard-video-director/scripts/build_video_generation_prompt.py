#!/usr/bin/env python3
"""Build a final video-generation prompt from a storyboard director pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OUTPUT_DIR = "12_video_generation_prompt"
OUTPUT_FILE = "video_generation_prompt.txt"
FULL_OUTPUT_FILE = "video_generation_prompt_full.txt"
CONCISE_OUTPUT_FILE = "video_generation_prompt_concise_seedance.txt"
ZH_OUTPUT_FILE = "video_generation_prompt_zh.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def maybe_read(path: Path) -> str:
    return read_text(path) if path.exists() else ""


def collect_segment_prompts(package_dir: Path) -> list[tuple[str, str]]:
    segment_dir = package_dir / "07_seedance2_segment_prompts"
    if not segment_dir.is_dir():
        return []
    return [(path.stem, read_text(path)) for path in sorted(segment_dir.glob("*.txt"))]


def build_progression(manifest: dict) -> str:
    lines: list[str] = []
    for segment in manifest.get("segments", []):
        seg_id = segment.get("segment_id", "Segment")
        duration = segment.get("duration", "")
        control_mode = segment.get("control_mode", "")
        execution_mode = segment.get("execution_mode", "")
        legacy_mode = segment.get("mode", "")
        mode_parts = []
        if control_mode:
            mode_parts.append(f"control: {control_mode}")
        if execution_mode:
            mode_parts.append(f"execution: {execution_mode}")
        if not mode_parts and legacy_mode:
            mode_parts.append(legacy_mode)
        mode = "; ".join(mode_parts)
        function = segment.get("function", "")
        beats = ", ".join(segment.get("reference_beats", []))
        transition = segment.get("transition_out", "")
        line = f"- {seg_id} ({duration}, {mode}): {function}"
        if beats:
            line += f" Reference beats: {beats}."
        if transition:
            line += f" Transition out: {transition}."
        lines.append(line)
    return "\n".join(lines)


def short_block(text: str, limit: int = 700) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def format_reference_assets(manifest: dict) -> list[str]:
    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict) or not assets:
        return [
            "- Storyboard control: use the Beat Storyboard Plan for beat order, action path, camera staging, timing, composition, and environment progression.",
            "- Character references, if supplied later, control identity, proportions, costume/body design, and expression style.",
            "- Environment references, if supplied later, control layout, props, lighting, and geography.",
            "- Style references, if supplied later, control rendering finish, texture, line quality, and color palette.",
        ]

    lines: list[str] = []
    for asset_name, asset in assets.items():
        if not isinstance(asset, dict):
            continue
        label = asset_name.replace("_", " ")
        status = asset.get("status", "missing")
        path = asset.get("path")
        role = asset.get("role", "")
        path_text = f" Path: {path}." if path else ""
        lines.append(f"- {label} ({status}).{path_text} Role: {role}")
    return lines


def compact_reference_roles(manifest: dict) -> list[str]:
    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict) or not assets:
        return [
            "Use character references only for identity, proportions, costume/body design, and expression style.",
            "Use environment and style references only for geography, lighting, texture, color, and finish.",
        ]

    lines: list[str] = []
    for asset_name, asset in assets.items():
        if not isinstance(asset, dict):
            continue
        label = asset_name.replace("_", " ")
        status = asset.get("status", "missing")
        path = asset.get("path")
        role = asset.get("role", "")
        if status == "missing":
            continue
        path_text = f" at {path}" if path else ""
        lines.append(f"Use {label}{path_text} only for this role: {role}")
    return lines


def manifest_storyboard_ref(manifest: dict) -> str:
    assets = manifest.get("reference_assets", {})
    if not isinstance(assets, dict):
        return ""
    storyboard = assets.get("storyboard_control", {})
    if not isinstance(storyboard, dict):
        return ""
    if storyboard.get("status") in {"generated", "user_supplied", "prompt_only"} and storyboard.get("path"):
        return str(storyboard["path"])
    return ""


def concise_style_line(visual_bible: str) -> str:
    text = " ".join(visual_bible.split())
    if not text:
        return "Use the approved visual bible for rendering style, lighting, camera tone, and texture."
    # Keep concise handoff model-facing. Avoid dumping full markdown sections.
    text = re.sub(r"#|\*|`", "", text)
    return short_block(text, 360)


def concise_world_line(manifest: dict, beat_plan: str) -> str:
    constraints = manifest.get("user_hard_constraints", {})
    if isinstance(constraints, dict):
        location = constraints.get("location")
        visual_style = constraints.get("visual_style")
        if location or visual_style:
            return short_block(" ".join(str(item) for item in (location, visual_style) if item), 300)
    return short_block(beat_plan or "Use the approved Beat Storyboard Plan for environment progression and scene continuity.", 300)


def manifest_schema_note(manifest: dict) -> str:
    if "reference_assets" in manifest and "user_hard_constraints" in manifest:
        return "Manifest schema: current, with explicit reference asset roles and user hard constraints."
    return "Manifest schema: legacy or partial; verify reference roles and user hard constraints before final handoff."


def discover_segment_storyboards(package_dir: Path, manifest: dict) -> list[tuple[str, str]]:
    output: list[tuple[str, str]] = []
    story_dir = package_dir / "11_generated_storyboards"
    for segment in manifest.get("segments", []):
        if not isinstance(segment, dict):
            continue
        seg_id = segment.get("segment_id", "")
        if not seg_id:
            continue
        candidates = sorted(story_dir.glob(f"storyboard_{seg_id}_*.png"))
        if candidates:
            output.append((seg_id, str(candidates[0])))
    return output


def missing_segment_storyboard_ids(package_dir: Path, manifest: dict) -> list[str]:
    story_dir = package_dir / "11_generated_storyboards"
    missing: list[str] = []
    segments = manifest.get("segments", [])
    if not isinstance(segments, list) or len(segments) <= 1:
        return missing
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        seg_id = str(segment.get("segment_id") or "").strip()
        if not seg_id:
            continue
        candidates = []
        if story_dir.is_dir():
            for pattern in (
                f"storyboard_{seg_id}_*.png",
                f"storyboard_{seg_id}_*.jpg",
                f"storyboard_{seg_id}_*.jpeg",
                f"storyboard_{seg_id}_*.webp",
            ):
                candidates.extend(story_dir.glob(pattern))
        if not candidates:
            missing.append(seg_id)
    return missing


def build_full_prompt(
    *,
    manifest: dict,
    visual_bible: str,
    beat_plan: str,
    segment_prompts: list[tuple[str, str]],
    storyboard_image: str,
    segment_storyboards: list[tuple[str, str]],
    extra_direction: str,
) -> str:
    duration = manifest.get("target_duration", "")
    aspect_ratio = manifest.get("aspect_ratio", "16:9")
    project_title = manifest.get("project_title", "Storyboard-driven video")
    progression = build_progression(manifest)

    lines = [
        f"Generate a {duration} {aspect_ratio} video for: {project_title}.",
        "",
        "Reference assets:",
    ]
    if segment_storyboards:
        for seg_id, path in segment_storyboards:
            lines.append(
                f"- {seg_id} storyboard control image: {path}. Use it only for {seg_id} beat order, action path, camera staging, timing, composition, and environment progression."
            )
        if storyboard_image:
            lines.append(
                f"- Full-project overview storyboard image: {storyboard_image}. Use it for human review and cross-Segment continuity only, not as the sole direct control image for any individual Segment."
            )
    elif storyboard_image:
        lines.append(
            f"- Storyboard control image: {storyboard_image}. Use it for beat order, action path, camera staging, timing, composition, and environment progression."
        )
    else:
        lines.extend(format_reference_assets(manifest))
    if storyboard_image or segment_storyboards:
        lines.extend(
            line
            for line in format_reference_assets(manifest)
            if "storyboard control" not in line.lower()
        )
    lines.extend(
        [
            "",
            "Continuity:",
            "Preserve the same subject identity, costume/body design, environment layout, lighting logic, visual style, and emotional continuity across the full video.",
            "Treat annotated storyboard images as control references, not clean final-frame references, unless the requested final style is explicitly a hand-drawn storyboard animation.",
            "",
            "Storyboard execution:",
            progression or "Follow the Beat Storyboard Plan in order.",
        ]
    )

    if segment_prompts:
        lines.append("")
        lines.append("Segment prompt source material:")
        for seg_id, prompt in segment_prompts:
            lines.append(f"\n[{seg_id}]\n{prompt}")

    if visual_bible:
        lines.extend(["", "Visual Bible continuity:", visual_bible])

    if beat_plan:
        lines.extend(["", "Beat Storyboard Plan:", beat_plan])

    if extra_direction:
        lines.extend(["", "User-approved additional direction:", extra_direction.strip()])

    lines.extend(
        [
            "",
            "Global avoid list:",
            "random scene changes, changing identity, changing costume/body design, changing location, changing lighting logic, unrelated cuts, added characters, added text, logos, subtitles, style drift, uncontrolled camera changes, broken physics, severe deformation, extra limbs, treating ordered storyboard beats as unrelated scenes.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def build_concise_seedance_prompt(
    *,
    manifest: dict,
    visual_bible: str,
    beat_plan: str,
    storyboard_image: str,
    segment_storyboards: list[tuple[str, str]],
    extra_direction: str,
) -> str:
    duration = manifest.get("target_duration", "")
    aspect_ratio = manifest.get("aspect_ratio", "16:9")
    project_title = manifest.get("project_title", "Storyboard-driven video")
    control_strategy = manifest.get("control_strategy", "")
    layout_pattern = manifest.get("layout_pattern", "")
    progression = build_progression(manifest)

    storyboard_ref = "@[storyboard ref]"
    if segment_storyboards:
        storyboard_ref = ", ".join(f"@[{seg_id} storyboard ref]" for seg_id, _ in segment_storyboards)
    elif storyboard_image:
        storyboard_ref = storyboard_image
    else:
        storyboard_ref = manifest_storyboard_ref(manifest) or storyboard_ref

    lines = [
        "INTENT:",
        f"Create a {duration} {aspect_ratio} storyboard-driven video for: {project_title}. Preserve the planned story, performance objective, and final payoff.",
        "",
        "STYLE:",
        concise_style_line(visual_bible),
        "",
        "WORLD:",
        concise_world_line(manifest, beat_plan),
        "",
        "BEATS:",
        short_block(progression or "Follow the approved ordered storyboard beats.", 500),
        "",
        "REFERENCES:",
        f"Use {storyboard_ref} as the choreography, timing, camera, and motion-planning reference for the video.",
        f"Use {storyboard_ref} as the exact sequential visual keyframe reference for the video.",
        "Treat every storyboard panel as an ordered cinematic beat, not as one page image.",
        "Follow the storyboard shot by shot, preserving panel order, timing, action, camera, framing, and emotional progression.",
    ]
    reference_lines = compact_reference_roles(manifest)
    if reference_lines:
        lines.extend(reference_lines)
    if segment_storyboards:
        lines.append("Segment storyboard asset mapping:")
        for seg_id, path in segment_storyboards:
            lines.append(f"Attach @{seg_id} storyboard ref from {path}; use it only for {seg_id}.")
    lines.extend([
        "",
        "EXECUTION:",
        "Expand motion naturally between panels with body weight, prop physics, cloth and hair response, camera inertia, and environmental motion.",
        "Use annotations, arrows, and movement guides internally for staging and animation logic only.",
        "",
        "ADHERENCE:",
        "Do not skip, merge, reorder, or reinterpret panels.",
        "Treat compressed beats as fast motion snapshots, not full-length actions, when the storyboard uses dense 12/16-beat performance logic.",
    ])

    if control_strategy or layout_pattern:
        lines.extend(
            [
                "",
                "CONTROL NOTES:",
                manifest_schema_note(manifest),
                f"Control strategy: {control_strategy or 'storyboard-driven hybrid'}.",
                f"Layout pattern: {layout_pattern or 'use the approved storyboard layout'}.",
            ]
        )

    if extra_direction:
        lines.extend(["", "EXTRA DIRECTION:", extra_direction.strip()])

    lines.extend(
        [
            "",
            "AVOID:",
            "Do not render storyboard artifacts, colored annotations, arrows, motion lines, handwritten notes, labels, panel numbers, borders, timing marks, sketch overlays, text, UI, logos, subtitles, or watermarks.",
            "Do not change identity, costume/body design, location, lighting logic, visual style, screen direction, final pose, or payoff.",
            "Do not add extra characters, extra action beyond the storyboard, unrelated cuts, random camera drift, broken physics, severe deformation, or extra limbs.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def build_zh_prompt(
    *,
    manifest: dict,
    visual_bible: str,
    beat_plan: str,
    storyboard_image: str,
    segment_storyboards: list[tuple[str, str]],
    extra_direction: str,
) -> str:
    duration = manifest.get("target_duration", "")
    aspect_ratio = manifest.get("aspect_ratio", "16:9")
    project_title = manifest.get("project_title", "故事板驱动视频")
    progression = build_progression(manifest)

    storyboard_ref = "已登记的 storyboard_control"
    if segment_storyboards:
        storyboard_ref = "、".join(f"{seg_id} 分段故事板控制图 {path}" for seg_id, path in segment_storyboards)
    elif storyboard_image:
        storyboard_ref = storyboard_image
    else:
        storyboard_ref = manifest_storyboard_ref(manifest) or storyboard_ref

    lines = [
        "意图:",
        f"生成一条 {duration}、{aspect_ratio} 的故事板驱动视频：{project_title}。保持既定故事目标、表演目标和最终收束。",
        "",
        "参考资产使用规则:",
        f"- 使用 {storyboard_ref} 控制动作顺序、镜头调度、运镜、构图、节奏和最终定格。",
    ]
    for line in compact_reference_roles(manifest):
        lines.append("- " + line)
    lines.extend(
        [
            "",
            "分镜执行:",
            short_block(progression or "严格按已批准的 Beat 顺序执行。", 800),
            "",
            "视觉连续性:",
            short_block(visual_bible or "遵循视觉圣经中的主体身份、场景、光线、材质、镜头语言和风格。", 1000),
            "",
            "Beat 细节:",
            short_block(beat_plan or "按 Beat Storyboard Plan 展开每个镜头动作。", 1400),
            "",
            "执行要求:",
            "把每个故事板格子当作有顺序的电影 Beat，不要当成一张拼贴图。镜头之间自然补足动作、重心、道具物理、布料/毛发反应、环境运动和相机惯性。",
            "故事板中的箭头、标注、面板编号和控制文字只用于内部调度，最终视频不能渲染出来。",
            "",
            "禁止:",
            "禁止跳过、合并、重排或重新解释分镜。禁止出现故事板边框、彩色标注、箭头、运动线、手写注释、标签、面板编号、时间标记、字幕、UI、logo、水印。禁止改变主体身份、服装/身体设计、道具设计、场景、光线逻辑、视觉风格、运动方向和最终收束。",
        ]
    )
    if extra_direction:
        lines.extend(["", "额外方向:", extra_direction.strip()])
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", help="Storyboard director pack directory.")
    parser.add_argument(
        "--storyboard-image",
        default="",
        help="Optional generated storyboard image path to reference in the prompt.",
    )
    parser.add_argument(
        "--extra-direction",
        default="",
        help="Optional user-approved additional direction to append.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output prompt path. Defaults to 12_video_generation_prompt/video_generation_prompt.txt.",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "concise_seedance"],
        default="full",
        help="Prompt mode to write to video_generation_prompt.txt.",
    )
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
    segment_prompts = collect_segment_prompts(package_dir)
    storyboard_image = args.storyboard_image.strip()
    segment_storyboards = discover_segment_storyboards(package_dir, manifest)
    missing_segment_storyboards = missing_segment_storyboard_ids(package_dir, manifest)
    if segment_storyboards and missing_segment_storyboards:
        print(
            "ERROR: partial multi-Segment storyboard image set. Missing Segment-specific storyboard image(s): "
            + ", ".join(missing_segment_storyboards)
        )
        print("Generate storyboard_Sxx_<variant>.png for every Segment, or remove partial Segment storyboard images.")
        return 1

    full_prompt = build_full_prompt(
        manifest=manifest,
        visual_bible=visual_bible,
        beat_plan=beat_plan,
        segment_prompts=segment_prompts,
        storyboard_image=storyboard_image,
        segment_storyboards=segment_storyboards,
        extra_direction=args.extra_direction,
    )
    concise_prompt = build_concise_seedance_prompt(
        manifest=manifest,
        visual_bible=visual_bible,
        beat_plan=beat_plan,
        storyboard_image=storyboard_image,
        segment_storyboards=segment_storyboards,
        extra_direction=args.extra_direction,
    )
    zh_prompt = build_zh_prompt(
        manifest=manifest,
        visual_bible=visual_bible,
        beat_plan=beat_plan,
        storyboard_image=storyboard_image,
        segment_storyboards=segment_storyboards,
        extra_direction=args.extra_direction,
    )
    selected_prompt = concise_prompt if args.mode == "concise_seedance" else full_prompt

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else package_dir / OUTPUT_DIR / OUTPUT_FILE
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(selected_prompt, encoding="utf-8")

    prompt_dir = output_path.parent
    (prompt_dir / FULL_OUTPUT_FILE).write_text(full_prompt, encoding="utf-8")
    (prompt_dir / CONCISE_OUTPUT_FILE).write_text(concise_prompt, encoding="utf-8")
    (prompt_dir / ZH_OUTPUT_FILE).write_text(zh_prompt, encoding="utf-8")

    print(f"Wrote video generation prompt ({args.mode}): {output_path}")
    print(f"Wrote full prompt: {prompt_dir / FULL_OUTPUT_FILE}")
    print(f"Wrote concise Seedance prompt: {prompt_dir / CONCISE_OUTPUT_FILE}")
    print(f"Wrote Chinese prompt: {prompt_dir / ZH_OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
