---
name: storyboard-video-qc
description: Production preflight quality control for storyboard-video director packs before video generation. Use when the user asks to review, audit, QC, preflight, approve, or decide whether a storyboard pack is ready for video generation, handoff, Seedance, xyq, Veo, or other downstream video tools. This skill does not compare against learning cases unless explicitly asked.
---

# Storyboard Video QC

## Purpose

Use this skill as a production gate for storyboard-to-video packs. It answers:

- Can this pack enter video generation now?
- What must be fixed before handoff?
- Which risks are acceptable, and which are likely to break generation?

Do not run learning-case comparison by default. This is not an iteration/research reviewer. It is a production preflight reviewer.

## Verdicts

Use one of these verdicts:

- `READY`: pack is structurally valid, references and prompt contract are strong enough for handoff.
- `READY WITH RISKS`: handoff is possible, but known risks should be acknowledged.
- `FIX BEFORE GENERATION`: likely generation failure or preventable drift; fix files/assets first.
- `STRATEGY RESET`: control strategy/layout is mismatched to the project, so patching prompts is not enough.

## Workflow

1. Identify the pack directory.
2. Run:

```bash
python skills/storyboard-video-qc/scripts/preflight_qc.py <package_dir>
```

If running from an installed skill path, use that skill's `scripts/preflight_qc.py`.

For final production handoff or expensive generations, run strict asset QC:

```bash
python skills/storyboard-video-qc/scripts/preflight_qc.py <package_dir> --strict-assets
```

For visual reference asset review, run:

```bash
python skills/storyboard-video-qc/scripts/visual_asset_review.py <package_dir>
```

Use `--strict-assets` when the review is part of final handoff readiness.

3. Read the generated `15_preflight_qc.md`.
4. Give the user the verdict first, then the smallest useful fix list.

## Review Focus

Check these areas:

- Control strategy: manifest, `00_control_strategy.md`, Segment control modes, and execution modes agree.
- Layout fit: panel count and layout suit the motion/emotion/product problem.
- Reference roles: storyboard control, character reference, environment reference, style reference, clean keyframes are not confused.
- Storyboard image safety: annotated boards exist when needed and will not contaminate the final video.
- Motion/emotion control: high-motion packs include action progression, body-driven prop logic, adherence boosters, and final payoff; face-driven packs include emotion flow.
- Downstream prompt contract: prompt says panels are ordered cinematic beats, forbids rendering storyboard artifacts, and forbids skipping/merging/reordering.
- Manifest integrity: paths exist, Segment-to-Beat mapping is coherent, prompt files exist.
- Visual asset roles: storyboard control may include annotations; character/prop/environment/style references should not be confused with clean keyframes or storyboard control.
- Strategy-specific asset quality: product-lock, face/emotion, high-motion, transformation, and spatial route/rescue packs have different required assets and semantic checks.

## Production Rules

- Missing `storyboard_control` is usually `FIX BEFORE GENERATION`.
- Missing strategy-required assets is `FIX BEFORE GENERATION` under strict assets, and at least `READY WITH RISKS` otherwise.
- Missing `character_reference` is `READY WITH RISKS` for simple subjects, but `FIX BEFORE GENERATION` when identity/costume/prop consistency is central.
- Missing `environment_reference` or `style_reference` is usually a risk, not a blocker, unless the pack depends on precise geography or brand/style fidelity.
- Annotated storyboard images are valid control references but must be paired with prompts that suppress arrows, borders, labels, notes, and UI artifacts in final video.
- A concise downstream prompt is preferred when visual references already carry detail.
- Do not ask to regenerate or rewrite the pack unless the control strategy or layout is wrong.

## Strategy-Specific QC

- `product_lock` / `object_lock`: require real `prop_reference` and `storyboard_control`; check product/object identity lock and forbidden mutations.
- `face_emotion_flow`: require readable character/expression control; check close-up or expression-sheet language for eyes, jaw, mouth corners, breath, and final mask.
- `rhythm_performance_board` / high-motion action: require storyboard control; check body-driven motion, prop logic, movement qualities, timing snapshots, and final payoff.
- `spatial_route_action` / rescue/chase/route: require storyboard control and environment reference; check route clarity, start/end positions, hazard locations, return path, and prop/rope continuity.
- `body_driven_transformation`: require staged transformation control; check before/trigger/mid-change/payoff and that transformation is action-driven.

## Strict Asset QC

Use `--strict-assets` when the user is about to spend generation credits, submit to a video platform, or wants final production readiness rather than iterative review.

Strict mode requires real generated or user-supplied assets for central controls:

- identity/costume-heavy pack -> `character_reference` must be `generated` or `user_supplied`
- prop/fabric-heavy pack -> `prop_reference` must be `generated` or `user_supplied`
- geography-critical pack -> `environment_reference` must be `generated` or `user_supplied`
- style/brand-critical pack -> `style_reference` must be `generated` or `user_supplied`

Prompt-only assets are useful during iteration but are not final-production assets in strict mode.

Environment asset loop:

- `build_environment_reference_prompt.py <package_dir>` creates `11_reference_assets/environment_reference_prompt.txt` and marks `environment_reference` as `prompt_only` unless a real generated/user-supplied environment image already exists.
- `preproduction_orchestrator.py <package_dir> --environment-image <path>` registers a real environment image and marks it `generated`.
- In strict mode, geography-critical packs fail until `environment_reference` is a real generated or user-supplied image.

Style asset loop:

- `build_style_reference_prompt.py <package_dir>` creates `11_reference_assets/style_reference_prompt.txt` and marks `style_reference` as `prompt_only` unless a real generated/user-supplied style image already exists.
- `preproduction_orchestrator.py <package_dir> --style-image <path>` registers a real style image and marks it `generated`.
- In strict mode, style-critical packs fail until `style_reference` is a real generated or user-supplied image.

Clean keyframe image loop:

- `build_clean_keyframe_image_tasks.py <package_dir>` creates one task file per `06_clean_keyframe_prompts/Pxx.txt` under `11_clean_keyframes/` and marks `clean_keyframe_reference` as `prompt_only` unless real clean keyframe images already exist.
- `preproduction_orchestrator.py <package_dir> --clean-keyframe-dir <dir>` registers a directory of generated clean keyframe images and marks `clean_keyframe_reference` as `generated`.
- Generated clean keyframes must contain no text, labels, arrows, panel borders, storyboard notes, UI, subtitles, logos, watermarks, or annotation marks.
- A generated/user-supplied clean keyframe directory with no supported image files is a blocker.

## Visual Asset Review

Use `visual_asset_review.py` when the user asks for visual asset review, asset QA, reference QA, or a check of generated storyboard / character / prop / environment / style images.

The review should verify:

- storyboard_control: panel order, camera movement, action path, timing, and payoff are readable; arrows, borders, notes, and colored guides are allowed only because this is a control board.
- character_reference: identity, proportions, costume, hair, expression range, silhouette, and palette are stable; any labels are acceptable only for reference use, not clean keyframes.
- prop_reference: closed/open states, scale, material, grip, allowed motion, and forbidden mutations are clear.
- environment_reference: geography, platforms, props, lighting, and spatial continuity are available when action depends on the space.
- style_reference: finish, line quality, color, lens tone, and completion level are available when style fidelity matters.
- clean_keyframe_reference: no text, panel borders, arrows, notes, UI, subtitles, labels, or annotations.

## Output Shape

Keep final user-facing output concise:

```text
Verdict: READY WITH RISKS

Main blockers:
- ...

Recommended fixes:
- file: action

Generated report:
- <path>/15_preflight_qc.md
```
