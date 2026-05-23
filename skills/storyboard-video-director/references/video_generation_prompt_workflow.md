# Video Generation Prompt Workflow

Use this after a director pack and, ideally, an annotated storyboard image exist. This stage creates the final video-generation prompt before handing off to any specific platform.

## Purpose

The video prompt binds three things:

- storyboard control: beat order, action path, camera staging, timing, transitions
- visual continuity: character identity, environment layout, style, lighting
- model execution: duration, aspect ratio, shot continuity, motion constraints, negative constraints

## Inputs

Required:

- `03_visual_bible.md`
- `04_beat_storyboard_plan.md`
- `10_generation_manifest.json`
- `07_seedance2_segment_prompts/Sxx.txt` when available

Optional:

- `11_generated_storyboards/storyboard_sheet_v01.png`
- `11_generated_storyboards/storyboard_Sxx_v01.png` per Segment for multi-Segment packs
- character reference images
- environment reference images
- style reference images
- user-approved extra video direction

## Output

Write:

```text
12_video_generation_prompt/
  video_generation_prompt.txt                  # default selected output
  video_generation_prompt_full.txt             # full review/archival version
  video_generation_prompt_concise_seedance.txt # compact downstream control contract
```

## Rules

- State whether the video is one continuous Segment or multiple stitched Segments.
- Explicitly preserve storyboard beat order.
- For multi-Segment projects, reference the Segment-specific storyboard image for each Segment. Do not use a shared overview board as the only downstream control image.
- Treat annotated storyboard images as control references, not clean final-frame references, unless the user wants hand-drawn storyboard style in the video.
- Mention character references separately from storyboard references when available.
- Mention environment/style references separately when available.
- Prefer `10_generation_manifest.json` `reference_assets` as the source of truth for reference role, path, and status.
- Preserve Segment `control_mode` and `execution_mode` separately when both exist.
- Include duration and aspect ratio.
- Include screen direction and continuity constraints for action.
- Include negative constraints for identity drift, random cuts, added characters, text, logos, and uncontrolled style changes.
- Choose prompt mode by handoff context:
  - `full`: use for human review, platform-neutral archival, or complex multi-Segment handoff.
- `concise_seedance`: use when the storyboard already carries visual detail and the downstream model benefits from a short control contract.
  - Do not include `missing reference` lines in model-facing prompts. Missing assets are a QC/reporting issue, not instructions for the video model.

## Concise Seedance Mode

This mode should foreground the control contract and avoid burying the key instruction inside a long director pack.

Structure:

```text
INTENT:
[story/performance objective]

STYLE:
[rendering and camera tone]

WORLD:
[location and atmosphere]

REFERENCES:
Use @[storyboard ref] as the choreography, timing, camera, and motion-planning reference.
Use @[storyboard ref] as the exact sequential visual keyframe reference.
Treat every storyboard panel as an ordered cinematic beat, not as one page image.
Use @[character ref] as strict identity reference.
Use @[environment/style ref] only for geography, light, texture, and finish.

EXECUTION:
Follow panel order, timing, action, camera, framing, and emotional progression exactly.
Expand natural in-between motion.
Use annotations internally for staging only.

AVOID:
[storyboard artifacts, identity drift, added action, text, UI, random cuts]
```

Use this mode especially for Seedance-style storyboard-to-video requests.

## Template

```text
Generate a [duration] [aspect ratio] video.

Reference assets:
- Storyboard control image(s): for a single Segment, use one storyboard control image; for multiple Segments, use one Segment-specific storyboard image per Segment for beat order, action path, camera staging, timing, and environment progression.
- Character reference images: use for identity, proportions, costume/body design, and expression style.
- Environment reference images: use for layout, props, lighting, and geography.
- Style reference images: use for rendering finish, line quality, color, and texture.

Continuity:
Preserve the same subject identity, environment layout, visual style, and lighting logic across the full video.

Storyboard execution:
[Beat or Segment progression]

Camera:
[camera language]

Motion:
[subject/object motion, momentum, impact, reaction]

Environment:
[environment progression]

End state:
[final frame/state]

Avoid:
random scene changes, changing identity, changing costume/body design, changing location, unrelated cuts, added characters, added text, logos, subtitles, style drift, uncontrolled camera changes, broken physics, severe deformation.
```

When an annotated storyboard is used as a control image, explicitly suppress storyboard artifacts in the model-facing prompt:

```text
Do not render storyboard artifacts, colored annotations, arrows, motion lines, handwritten notes, labels, panel numbers, borders, timing marks, sketch overlays, text, UI, logos, subtitles, or watermarks.
```
