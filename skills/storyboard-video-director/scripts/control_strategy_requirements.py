#!/usr/bin/env python3
"""Infer strategy-specific asset and QC requirements for storyboard packs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StrategyRequirements:
    strategies: set[str] = field(default_factory=set)
    required_assets: set[str] = field(default_factory=set)
    recommended_assets: set[str] = field(default_factory=set)
    semantic_checks: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def manifest_text(manifest: dict) -> str:
    parts: list[str] = []
    for key in ("project_title", "control_strategy", "layout_pattern", "storyboard_type", "target_duration"):
        value = manifest.get(key)
        if value:
            parts.append(str(value))
    constraints = manifest.get("user_hard_constraints")
    if constraints:
        parts.append(json.dumps(constraints, ensure_ascii=False))
    for segment in manifest.get("segments", []):
        if isinstance(segment, dict):
            parts.append(json.dumps(segment, ensure_ascii=False))
    return "\n".join(parts).lower()


def package_text(package_dir: Path, manifest: dict) -> str:
    files = [
        "00_control_strategy.md",
        "02_duration_segment_plan.md",
        "03_visual_bible.md",
        "04_beat_storyboard_plan.md",
        "05_annotated_storyboard_prompt.txt",
    ]
    return "\n".join([manifest_text(manifest), *[read_text(package_dir / name).lower() for name in files]])


def has_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def infer_requirements(package_dir: Path, manifest: dict, *, visual_storyboard_required: bool = False) -> StrategyRequirements:
    text = package_text(package_dir, manifest)
    req = StrategyRequirements()

    if visual_storyboard_required or has_any(
        text,
        (
            "storyboard",
            "visual storyboard",
            "故事板",
            "分镜",
            "生成视频前",
            "video generation",
        ),
    ):
        req.required_assets.add("storyboard_control")
        req.semantic_checks.add("storyboard_order")

    if has_any(
        text,
        (
            "product_lock",
            "object_lock",
            "product lock",
            "object lock",
            "same throughout",
            "look the same",
            "一直长得一样",
            "一致性",
            "产品锁",
            "道具锁",
        ),
    ):
        req.strategies.add("product_lock")
        req.required_assets.update({"prop_reference", "storyboard_control"})
        req.recommended_assets.add("clean_keyframe_reference")
        req.semantic_checks.update({"product_identity_lock", "clean_keyframe"})
        req.notes.append("Product/object-lock requires a real prop/product reference before storyboard/video handoff.")

    face_mode = has_any(text, ("face_emotion_flow", "face/emotion", "micro-expression", "micro expression"))
    face_story = has_any(text, ("inner conflict", "forced calm", "眼神", "表情", "强装")) and has_any(
        text,
        ("face", "eyes", "mouth", "jaw", "micro", "emotion", "脸", "眼", "嘴", "表情"),
    )
    if face_mode or face_story:
        req.strategies.add("face_emotion_flow")
        req.required_assets.update({"storyboard_control", "character_reference"})
        req.recommended_assets.add("clean_keyframe_reference")
        req.semantic_checks.update({"face_readability", "emotion_progression", "clean_keyframe"})
        req.notes.append("Face/emotion flow needs close-enough face states or an expression sheet, not only a body-position board.")

    if has_any(
        text,
        (
            "rhythm_performance_board",
            "body_driven_transformation",
            "storyboard_heavy",
            "12_panel",
            "16_panel",
            "rhythm",
            "fan",
            "sleeve",
            "rope",
            "rescue",
            "chase",
            "kata",
            "扇",
            "袖",
            "救援",
        ),
    ):
        req.strategies.add("high_motion")
        req.required_assets.add("storyboard_control")
        req.recommended_assets.update({"prop_reference", "clean_keyframe_reference"})
        req.semantic_checks.update({"body_driven_motion", "movement_qualities", "final_payoff"})
        req.notes.append("High-motion packs need body mechanics, movement qualities, and final payoff protection.")

    spatial_route = has_any(text, ("rescue", "flood", "safe zone", "victim", "救援", "水街道", "安全区"))
    spatial_route = spatial_route or (
        has_any(text, ("route", "路线", "geography"))
        and has_any(text, ("hazard", "return path", "victim", "safe zone", "障碍", "返回"))
    )
    if spatial_route:
        req.strategies.add("spatial_route_action")
        req.required_assets.update({"storyboard_control", "environment_reference"})
        req.recommended_assets.update({"prop_reference", "clean_keyframe_reference"})
        req.semantic_checks.update({"spatial_route", "body_driven_motion", "prop_continuity"})
        req.notes.append("Spatial rescue/route scenes need both a route map and action mechanics.")

    if has_any(
        text,
        (
            "transformation",
            "mid-change",
            "变化",
            "变成",
            "转化",
        ),
    ):
        req.strategies.add("body_driven_transformation")
        req.required_assets.add("storyboard_control")
        req.recommended_assets.update({"character_reference", "clean_keyframe_reference"})
        req.semantic_checks.update({"transformation_stages", "body_driven_motion", "final_payoff"})
        req.notes.append("Body-driven transformation needs before/trigger/mid-change/payoff key states.")

    return req
