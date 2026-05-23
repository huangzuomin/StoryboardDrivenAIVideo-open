# Output Contract

Create a production pack with this structure. Directory comments describe where files live; the delivery profile table below defines what is actually required for a user-facing response.

```text
project/
  00_control_strategy.md
  00_project_brief.md
  01_method_summary.md
  02_duration_segment_plan.md
  03_visual_bible.md
  04_beat_storyboard_plan.md
  05_annotated_storyboard_prompt.txt
  05_segment_storyboard_prompts/
    S01_storyboard_prompt.txt
    S02_storyboard_prompt.txt
  06_clean_keyframe_prompts/
    P01.txt
    P02.txt
  07_seedance2_segment_prompts/
    S01.txt
    S02.txt
  08_segment_beat_mapping.json
  09_editing_plan.md
  10_generation_manifest.json
  14_review_status.md
  14_review_summary.md
  11_generated_storyboards/
    storyboard_sheet_v01.png          # optional full-project overview; raster only for accepted storyboard_control
    storyboard_S01_v01.png
    storyboard_S02_v01.png
    storyboard_sheet_v01_review.md
  12_video_generation_prompt/
    video_generation_prompt.txt
    video_generation_prompt_zh.txt
  13_xyq_video_handoff/              # optional before/after xyq video generation
    asset_manifest.json
    xyq_video_task_message.txt
    submit_result.json
    downloaded_results/
  17_generation_handoff/
    asset_manifest.json
    video_prompt_for_upload.txt
    handoff_readiness_report.md
```

## 00_control_strategy.md

Include:

- primary control strategy
- secondary controls
- why this strategy fits the scene
- storyboard layout pattern when applicable
- reference priority
- soft-hint risk
- adherence boosters
- post-generation checks

This file answers why the pack uses storyboard, face/emotion coordinates, character sheets, environment maps, style references, clean keyframes, or a hybrid.

## 10_generation_manifest.json Version Fields

Current packs must include:

```json
{
  "workflow_version": "0.1.0-alpha",
  "skill_versions": {
    "storyboard-video-director": "0.1.0-alpha",
    "storyboard-video-qc": "0.1.0-alpha"
  }
}
```

## Delivery Profiles

Use these profiles as the done definition. Do not describe a pack as done, ready, or handoff-ready unless the current profile's required files and checks are satisfied.

| Profile | Use when | Required outputs | Required checks |
| --- | --- | --- | --- |
| `iteration` | The user explicitly asks for text-only planning, rough drafting, or no generated assets. | Core director files `00` through `10`, `14_review_status.md`, `14_review_summary.md`, prompt/task files for missing assets, and a clear text-plan-only status. | `validate_package.py`, `validate_manifest.py --strict-current-schema --allow-prompt-only-product-lock` only when product/object lock is text-only by request, and `validate_expected_delivery.py --profile text-plan --explicit-text-only-request`. |
| `preflight` | Ordinary requests to design a short video, product clip, AI-video-ready plan, or visual storyboard. | All iteration outputs plus `12_video_generation_prompt/video_generation_prompt.txt`, `video_generation_prompt_full.txt`, `video_generation_prompt_concise_seedance.txt`, required real image assets inferred by strategy, `15_preflight_qc.md` when QC is available, and `16_user_preview_summary.md` when the orchestrator is used. Product/object-lock requires real `prop_reference` and `storyboard_control`. Visual-storyboard requests require a real raster storyboard image. | `validate_package.py`, `validate_manifest.py --strict-current-schema`, `validate_expected_delivery.py --profile preflight`, visual storyboard check when required, and preflight QC. |
| `final` | The user asks for production handoff, upload-ready package, expensive generation, or final video-agent handoff. | All preflight outputs plus real generated/user-supplied images for every non-`not_needed` manifest asset, strict visual asset review, `17_generation_handoff/asset_manifest.json`, `17_generation_handoff/video_prompt_for_upload.txt`, and `17_generation_handoff/handoff_readiness_report.md`. | `preproduction_orchestrator.py --phase final --strict-assets`, final asset gate, visual asset review, preflight QC, and generation handoff bundle readiness. |

If a required image asset cannot be generated or registered, leave concrete task files and report the true blocker. Do not silently downgrade an ordinary request to `iteration`.

Use `scripts/check_skill_versions.py --package-dir <package_dir>` from the repository root to compare repo skill versions, installed Codex skill versions, and pack manifest versions.

## 00_project_brief.md

Include:

- project title
- user input
- interpreted story type
- main subject
- location
- core story energy
- target duration
- visual style
- video model
- assumptions made
- user hard constraints
- professional inference summary when user input is sparse
- strongest genre interpretation
- dominant motif system
- final payoff statement

## 01_method_summary.md

Briefly state the selected control strategy from `00_control_strategy.md`. Explain that annotated storyboards are for review/control, clean keyframes are for generation look, and Seedance2 prompts are per Segment.

## 02_duration_segment_plan.md

Include a Segment table with:

- pacing diagnosis
- Segment ID
- duration
- mode
- function
- opening state
- ending state
- reference Beats
- transition out
- motion risk

The pacing diagnosis must state genre energy, audience felt speed, target duration, average Beat duration, fastest Beat, slowest Beat, required pauses, and Segment split reason.

## 03_visual_bible.md

Include:

- main subject
- costume/body language
- location
- visual style
- lighting logic
- camera language
- motif system
- environment elements
- annotation system
- avoid list

When a product, creature, robot, pet, artifact, prop, or recurring object must remain consistent, include an `Object Lock`, `Product Lock`, or `Creature Lock` block with scale, silhouette, material, fixed features, allowed motion, and forbidden mutations.

## 04_beat_storyboard_plan.md

For each Beat include:

- Beat ID
- Segment ID
- beat role
- timestamp or beat count when rhythm-led
- technique/action phrase when action-led
- shot size
- frame description
- subject action
- camera movement
- composition
- environment change
- motif progression when relevant
- emotion function
- expressive director note when useful
- clean keyframe prompt summary

## 05_annotated_storyboard_prompt.txt

One complete prompt for generating an n-panel annotated storyboard overview sheet. It must include the required annotation color system.

Accepted `storyboard_control` images must be raster images (`.png`, `.jpg`, `.jpeg`, `.webp`) generated by image2/image generation or supplied by the user. SVG/programmatic boards may be kept as auxiliary schematic or route-map references, but they do not satisfy preflight/final storyboard control by themselves.

For multi-Segment projects, this overview sheet is for human review only unless the final video is generated as a single Segment. Do not use a shared overview sheet as the only direct storyboard control reference for multiple downstream video generations.

## 05_segment_storyboard_prompts/

Required for multi-Segment projects.

One annotated storyboard prompt per Segment. Use names like `S01_storyboard_prompt.txt`.

Each Segment prompt must:

- include only the Beats that belong to that Segment
- preserve the same Visual Bible and local Segment continuity
- include the colored annotation system
- state the Segment ID, duration, opening state, ending state, and transition to the next Segment
- avoid showing future or previous Segment Beats in the same control image

For single-Segment projects this directory is optional.

## 06_clean_keyframe_prompts/

One `.txt` file per Beat. Use names like `P01.txt`.

Each prompt must be a clean video keyframe prompt with no annotation artifacts.

## 07_seedance2_segment_prompts/

One `.txt` file per Segment. Use names like `S01.txt`.

Each prompt must describe how ordered reference Beats become one coherent Segment.

## 08_segment_beat_mapping.json

Valid JSON mapping Segments to Beats:

```json
{
  "segments": [
    {
      "segment_id": "S01",
      "duration": "12s",
      "mode": "single_continuous_shot",
      "beats": ["P01", "P02", "P03"]
    }
  ]
}
```

## 09_editing_plan.md

Describe:

- final Segment order
- transitions
- action continuity
- lighting continuity
- sound or vocal continuity
- rhythm suggestions
- long-shot preservation notes

## 10_generation_manifest.json

Valid JSON:

```json
{
  "project_title": "string",
  "target_duration": "string",
  "aspect_ratio": "16:9",
  "storyboard_type": "beat_storyboard",
  "control_strategy": "storyboard_heavy",
  "layout_pattern": "3x3_action_grid",
  "video_model": "seedance2",
  "seedance2_segment_limit": "15s",
  "user_hard_constraints": {
    "target_duration": "string",
    "subject_identity": "string",
    "location": "string",
    "required_final_payoff": "string",
    "visual_style": "string",
    "explicit_exclusions": []
  },
  "reference_assets": {
    "storyboard_control": {
      "path": null,
      "status": "missing",
      "role": "controls beat order, camera staging, action path, timing, composition, and emotional progression"
    },
    "character_reference": {
      "path": null,
      "status": "missing",
      "role": "controls identity, costume, proportions, face, and body language"
    },
    "environment_reference": {
      "path": null,
      "status": "missing",
      "role": "controls geography, props, lighting, weather, and spatial continuity"
    },
    "style_reference": {
      "path": null,
      "status": "missing",
      "role": "controls render finish, texture, palette, lens language, and style"
    },
    "clean_keyframe_reference": {
      "path": "06_clean_keyframe_prompts/",
      "status": "prompt_only",
      "role": "controls clean final-frame look without annotations"
    }
  },
  "visual_bible": "03_visual_bible.md",
  "segments": [
    {
      "segment_id": "S01",
      "duration": "12s",
      "control_mode": "rhythm_performance_board",
      "execution_mode": "single_continuous_shot",
      "function": "string",
      "reference_beats": ["P01", "P02"],
      "clean_keyframes": ["06_clean_keyframe_prompts/P01.txt"],
      "prompt_file": "07_seedance2_segment_prompts/S01.txt",
      "transition_out": "string"
    }
  ]
}
```

## 11_generated_storyboards/ Optional

Create this directory only when the user asks to generate storyboard images.

Use names like:

```text
11_generated_storyboards/
  storyboard_sheet_v01.png              # optional full-project overview
  storyboard_sheet_v01_review.md
  storyboard_S01_v01.png                # required when S01 is generated as its own video Segment
  storyboard_S01_v01_review.md
  storyboard_S02_v01.png
  storyboard_S02_v01_review.md
```

For multi-Segment projects, every generated video Segment should have a matching Segment-specific storyboard control image. A shared overview image can be kept for human review, but should not be the sole storyboard reference in `13_xyq_video_handoff/asset_manifest.json`.

The review note should state:

- source prompt file
- generation date
- whether the sheet appears to contain the requested panel count
- visible continuity risks
- whether another version is recommended

## 12_video_generation_prompt/ Optional

Create this directory after the director pack and storyboard image prompt are ready, and before handing off to a specific video platform.

Use:

```text
12_video_generation_prompt/
  video_generation_prompt.txt
  video_generation_prompt_full.txt
  video_generation_prompt_concise_seedance.txt
  video_generation_prompt_zh.txt
```

## 17_generation_handoff/

Created during final preproduction by `scripts/build_generation_handoff_bundle.py`.

This folder is the public production handoff surface:

- `asset_manifest.json`: uploadable image files mapped to `@upload_ref` handles.
- `video_prompt_for_upload.txt`: downstream prompt written against upload refs, not local absolute paths.
- `handoff_readiness_report.md`: readiness verdict and blockers.

Older internal builds may contain `17_generation_deployment/`; new packs should use `17_generation_handoff/`.

Legacy packs can be upgraded with:

```text
scripts/upgrade_manifest_schema.py <package_dir>
scripts/upgrade_manifest_schema.py <package_dir> --write
```

Use strict validation for newly generated packs:

```text
scripts/validate_manifest.py <package_dir>/10_generation_manifest.json --strict-current-schema
```

The prompt should include:

- duration and aspect ratio
- storyboard control instructions
- optional generated storyboard image path
- character, environment, and style reference roles if known
- Beat or Segment progression
- camera, motion, environment, end state, and avoid list

Generate it with:

```text
scripts/build_video_generation_prompt.py <package_dir>
scripts/build_video_generation_prompt.py <package_dir> --mode concise_seedance
```

## 13_xyq_video_handoff/ Optional

Create this directory only when the user asks to generate video, use xyq, use 小云雀, or prepare a video-agent handoff.

Use:

```text
13_xyq_video_handoff/
  asset_manifest.json
  xyq_video_task_message.txt
  submit_result.json
  downloaded_results/
```

`asset_manifest.json` tracks local paths and uploaded asset IDs:

```json
{
  "assets": [
    {
      "label": "Reference image 1",
      "role": "storyboard_control",
      "path": "11_generated_storyboards/storyboard_sheet_v01.png",
      "asset_id": "optional_uploaded_asset_id",
      "purpose": "Controls beat order, action path, camera staging, environment progression, and timing."
    },
    {
      "label": "Reference image 2",
      "role": "character_reference",
      "character": "main character",
      "path": "references/character_front.png",
      "asset_id": "optional_uploaded_asset_id",
      "purpose": "Controls identity, proportions, costume/body design, and expression style."
    }
  ]
}
```

Valid roles:

- `storyboard_control`
- `character_reference`
- `prop_reference`
- `environment_reference`
- `style_reference`
- `clean_keyframe_reference`

## 14_review_status.md

Required for production packs after this iteration.

Track:

- text director pack status
- package validation status
- overview storyboard image status
- Segment storyboard image status
- final video prompt status
- concise video prompt status
- known inconsistencies
- recommended next action

Generate or refresh it with:

```text
scripts/build_review_summary.py <package_dir>
```

## 14_review_summary.md

Use this as a one-file review entry point. Include:

- user hard constraints
- selected closest learning pattern if known
- control strategy
- layout and panel count
- reference asset status
- emotion, action, object-lock, or prop-control modules used
- downstream prompt status
- known adherence risks
- recommended fixes before video generation

Generate or refresh it with:

```text
scripts/build_review_summary.py <package_dir>
```

## Learning-Pack Review

When reviewing a pack against the included learning resources, use:

```text
scripts/review_against_learning_pack.py <package_dir>
scripts/review_against_learning_pack.py <package_dir> --learning-pack docs/aimikoda_storyboard_learning_pack
scripts/review_against_learning_pack.py <package_dir> --user-correction "用户指出应默认画出可视化故事板" --process-issue "默认交付低估视觉故事板期望" --skill-update-target "SKILL.md / image_generation_workflow.md" --regression-test "普通可视化故事板请求必须生成图或 image task"
```

The script writes a structured review markdown under `docs/` by default, including closest case, top similar cases, manifest checks, prompt checks, storyboard image checks, suggested fixes, and a `User Correction Signals` section.

## Static Regression Check

Use this after generating a pack for one of the reproduction test cases:

```text
scripts/check_regression_pack.py <package_dir>
scripts/check_regression_pack.py <package_dir> --case-id 16
scripts/check_regression_pack.py <package_dir> --expect quiet_discovery_reveal_flow --expect "object lock"
```

This is a static pack check, not a substitute for visual review or generated-video review.

Use the reviewed `12_video_generation_prompt/video_generation_prompt.txt` as the final video request. `xyq_video_task_message.txt` is generated by `scripts/build_xyq_video_task.py` and should be the message submitted to xyq-nest-skill after asset IDs are filled in.
