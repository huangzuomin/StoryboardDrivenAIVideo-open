# Reference Asset Workflow

Use this file before generating storyboard images or handing a project to a video-generation platform such as xyq-nest-skill.

## Asset Roles

Separate reference images by job. Do not make one image carry every responsibility.

| Role | Purpose | Typical Count | Notes |
| --- | --- | ---: | --- |
| `storyboard_control` | Controls beat order, camera layout, action path, panel rhythm, staging, and environment progression. | 1-3 | Usually an annotated storyboard sheet. It may contain arrows and labels. |
| `character_reference` | Controls subject identity, face/body design, costume, color, proportions, and expression style. | 1-6 per character | Use front, side, full-body, action pose, and expression references when available. |
| `prop_reference` | Controls product/prop/object identity, silhouette, scale, materials, fixed features, moving parts, and forbidden mutations. | 1-4 | Required for product-lock, appliance, vehicle, weapon, fan, package, device, or recurring-object consistency. |
| `environment_reference` | Controls room/location layout, architecture, props, materials, lighting logic, and geography. | 1-5 | Especially important for chase, rescue, product, or continuity-heavy scenes. |
| `style_reference` | Controls rendering style, line quality, color palette, texture, and finish. | 1-3 | Keep separate from storyboard when visual style must survive video generation. |
| `clean_keyframe_reference` | Controls final-video visual frame without annotation artifacts. | 1 per Beat or key moment | Must not contain arrows, panel labels, borders, subtitles, or notes. |

## Recommended Production Order

```text
character references / character sheet
-> prop/product references when a recurring object must stay consistent
-> environment references if needed
-> annotated storyboard control sheet
-> clean keyframes for generation
-> video generation handoff
```

For fast MVP work, the minimum acceptable handoff is:

```text
one storyboard_control per video Segment + final_video_prompt
```

For production-quality video, prefer:

```text
storyboard_control + character_reference(s) + prop_reference(s) + environment/style reference(s) + final_video_prompt
```

## Handoff Message Rules

When submitting to a downstream video agent, explicitly state each asset's role:

```text
Reference image 1 is the annotated storyboard control sheet for Segment S01. Use it only for S01 beat order, action path, camera staging, environment progression, and timing.
Reference image 2 is the annotated storyboard control sheet for Segment S02. Use it only for S02 beat order, action path, camera staging, environment progression, and timing.
Reference images 2-4 are character references for [character]. Use them for identity, proportions, costume/body design, and expression style.
Reference image 5 is the environment reference. Use it for room layout, props, lighting, and spatial continuity.
Reference image 6 is the style reference. Use it for line quality, color palette, and rendering finish.
```

Then provide the video generation request:

```text
Generate a [duration] video. Preserve each Segment's storyboard beat order and the character/environment/style references. Treat Segment storyboard images as control, not as final clean frame art unless explicitly requested.
```

## Asset Manifest

Use `13_xyq_video_handoff/asset_manifest.json` to track local files and uploaded asset IDs. Initialize it with `scripts/build_xyq_video_task.py <package_dir> --init-manifest`; the script will use `10_generation_manifest.json` `reference_assets` when available.

```json
{
  "assets": [
    {
      "label": "Reference image 1",
      "role": "storyboard_control",
      "path": "11_generated_storyboards/storyboard_sheet_v01.png",
      "asset_id": "optional_uploaded_asset_id",
      "purpose": "Controls beat order, action path, camera staging, and timing."
    },
    {
      "label": "Reference image 2",
      "role": "character_reference",
      "character": "cat",
      "path": "references/cat_front.png",
      "asset_id": "optional_uploaded_asset_id",
      "purpose": "Controls cat identity, fur pattern, body proportions, and expression style."
    }
  ]
}
```

## Common Mistakes

- Uploading only an annotated storyboard and expecting character identity to stay consistent.
- Writing only a downstream video prompt for a product-lock task instead of first creating or registering a product/prop reference.
- Treating prop/product prompt text as a finished production asset.
- For a multi-Segment video, uploading one shared overview storyboard and asking the video model to use only part of it.
- Using an annotated storyboard as a clean generation reference without accepting arrows and labels as visual artifacts.
- Forgetting to say which reference image controls which aspect.
- Mixing environment layout, character design, and style into one vague phrase.
- Letting a downstream agent invent timing when a final video prompt already exists.
