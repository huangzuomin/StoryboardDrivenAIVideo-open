# Image Generation Workflow

## Raster Storyboard Requirement

For preflight/final delivery, accepted `storyboard_control` assets must be raster images (`.png`, `.jpg`, `.jpeg`, `.webp`) generated through image2/image generation or supplied by the user.

Do not use programmatic SVG diagrams as the only storyboard control image. SVG maps can be useful as route maps, product schematics, or debug previews, but they must be registered as auxiliary schematic/route references and paired with a raster storyboard control image.

When the user asks for a visual storyboard/storyboard sheet/visual storyboard, visible image output is mandatory. A ready-to-run image task is an intermediate artifact, not the final deliverable.

Use this after a valid director pack exists and the user explicitly asks to generate an annotated storyboard image, asks for a visual storyboard/storyboard sheet, asks to proceed from prompt pack to visible storyboard output, or when product/object-lock consistency makes real visual assets required for preflight.

For product/object-lock preflight, image generation is not optional when the built-in `image_gen` tool is available. Generate the prop/product reference first, then the storyboard control image.

## Inputs

Required:

- `05_annotated_storyboard_prompt.txt`
- `05_segment_storyboard_prompts/Sxx_storyboard_prompt.txt` for multi-Segment packs
- `03_visual_bible.md`
- `04_beat_storyboard_plan.md`

Optional:

- `02_duration_segment_plan.md`
- user-provided style references

## Procedure

1. Validate the pack first with `scripts/validate_package.py <package_dir>`.
2. For product/object-lock packs, generate or register the prop/product reference image first from the prop reference prompt under `15_reference_asset_prompts/` or `11_reference_assets/`.
   - Use the `imagegen` skill and built-in `image_gen` tool by default when available.
   - Save or copy the accepted result under `11_reference_assets/`.
   - Update `10_generation_manifest.json` `reference_assets.prop_reference.path` and `status=generated`.
3. Build the image-agent task with `scripts/build_storyboard_image_task.py <package_dir>`.
   - For a single-Segment pack, this creates one storyboard sheet task.
   - For a multi-Segment pack, use `--segment-id Sxx` and run it once per Segment.
4. Send the resulting task text to the image generator. Use the `imagegen` skill and built-in `image_gen` tool by default when available.
5. Request one 16:9 annotated storyboard sheet image per Segment unless the user asks for variants.
6. Save image outputs under `11_generated_storyboards/`.
   - If the image generation tool saves to a default/generated-images directory, copy the accepted image into `11_generated_storyboards/` and keep the original file.
7. Write a short review note beside the image.
8. Update `10_generation_manifest.json` `reference_assets.storyboard_control.path` and `status` when a storyboard control image is generated.
9. Update `14_review_status.md` with overview and Segment storyboard image status.
10. Run `scripts/check_visual_storyboard_delivery.py <package_dir>` before final response.
11. Run `scripts/validate_expected_delivery.py <package_dir> --profile preflight` before final response for ordinary product/object-lock requests.

## Image Generator Task Requirements

The task must instruct the image generator to:

- generate a single annotated storyboard sheet, not final video frames
- preserve the requested panel count and Beat order for that Segment
- use panel labels only for the annotated storyboard
- use colored annotation marks: red, blue, green, orange, purple
- when the board mode is `rhythm_performance_board` or premium action, preserve the title strip, timestamps or beat counts, motif escalation, technique names, and sparse expressive director notes
- when using the premium hand-drawn action style, keep the drawing rough, masterful, directional, and energetic rather than polished poster art
- avoid logos, subtitles, photo realism, extra characters, dense readable text, and any timestamps not explicitly requested by the storyboard mode
- keep the sheet readable at 16:9

## Review Note

Write `storyboard_sheet_v01_review.md` with:

```markdown
# Storyboard Image Review

- Source prompt: 05_annotated_storyboard_prompt.txt
- Output: storyboard_sheet_v01.png
- Panel count check: pass/fail/uncertain
- Beat order check: pass/fail/uncertain
- Visual Bible continuity: pass/fail/uncertain
- Annotation readability: pass/fail/uncertain
- Recommended next step: accept / regenerate with adjustment
- Can be used as human overview: yes/no/uncertain
- Can be used as direct video control: yes/no/uncertain
- Contamination risk: none/low/medium/high
```

Human overview vs direct video control:

- A human overview board may include title strips, timestamps, sparse labels, arrows, and notes for review.
- A direct video-control board should avoid dense notes, timecodes, large titles, UI-like text, and decorative labels that a video model may render into the final shot.
- If the overview board has medium or high contamination risk, recommend a cleaner `storyboard_control_clean_v01.png` pass before video generation.

## Regeneration Guidance

Regenerate when:

- panel count is wrong
- Beat order is scrambled
- a multi-Segment project uses only one shared overview storyboard as direct video control
- annotations are missing or dominate the drawing
- a clean keyframe style is produced instead of a storyboard sheet
- the image becomes photorealistic, polished comic art, or a poster
- subject identity, costume, location, or lighting logic drifts from the Visual Bible

For a second attempt, keep the same Beat sequence and add a short correction paragraph at the top of the image task. Do not rewrite the entire director pack unless the pack itself is wrong.
