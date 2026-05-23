# Production Handoff

The production handoff is the boundary between storyboard planning and downstream video generation.

## Output Folder

`17_generation_handoff/`

## Files

`asset_manifest.json`

Maps each uploadable file to a stable reference handle:

```json
{
  "upload_ref": "@storyboard_control",
  "role": "storyboard_control",
  "local_path": "11_generated_storyboards/storyboard_sheet_v01.png",
  "include_in_upload": true
}
```

`video_prompt_for_upload.txt`

Uses upload refs, not local absolute paths. This prompt is meant to be pasted into or submitted to a video platform after the files have been uploaded.

`handoff_readiness_report.md`

Summarizes whether handoff is ready and lists blockers.

## Rules

- Upload images, not task text files.
- Expand directory assets such as clean keyframes into individual image refs.
- Keep reference roles separate.
- Never use annotated storyboard controls as clean keyframes.
- Do not send prompt-only reference assets into final production unless the target platform explicitly supports text-only references for that role.

## Downstream Video Tools

The handoff is model/tool agnostic. It can be used with an agent such as XYQ / Xiao Yun Que, a web tool such as Jimeng, or any Seedance2-style video generator that accepts prompt text plus reference images.

Recommended order:

1. Confirm `handoff_readiness_report.md` says `READY`.
2. Upload each image listed in `asset_manifest.json`.
3. Preserve each image's role when configuring references in the downstream tool.
4. Paste `video_prompt_for_upload.txt` as the main generation prompt.
5. Keep the duration, aspect ratio, Segment order, and final payoff from the director pack.

Do not collapse all references into one generic reference bucket when the target tool allows role separation. If the target tool has limited reference slots, prioritize:

1. `storyboard_control`
2. `character_reference` or `prop_reference`, depending on whether identity or product/object consistency is the central risk
3. `environment_reference`
4. `style_reference`
5. `clean_keyframe_reference`

## XYQ / Xiao Yun Que Agent

For an XYQ-style agent workflow, use the dedicated task builder:

```powershell
python skills\storyboard-video-director\scripts\build_xyq_video_task.py <pack_dir> --init-manifest
```

This creates:

```text
13_xyq_video_handoff/asset_manifest.json
```

Upload the listed images to the agent/platform, fill the returned `asset_id` values back into that file, then run:

```powershell
python skills\storyboard-video-director\scripts\build_xyq_video_task.py <pack_dir>
```

The script writes:

```text
13_xyq_video_handoff/xyq_video_task_message.txt
```

Send that message to the agent with the uploaded assets attached or referenced.

## Jimeng / Seedance2-Style Web Tools

For web tools that do not use persistent `asset_id` values:

1. Upload the files listed in `17_generation_handoff/asset_manifest.json`.
2. Paste `17_generation_handoff/video_prompt_for_upload.txt`.
3. If the UI asks for reference type, map each image according to its `role`.
4. If the UI provides only one or two reference slots, use `storyboard_control` first, then the identity-critical reference (`character_reference` or `prop_reference`).

Final video output should not include storyboard artifacts such as panel borders, arrows, labels, handwritten notes, timing marks, UI, or watermarks. Those artifacts are control instructions, not visual content.

## Compatibility

Older internal builds used `17_generation_deployment/`. New public-facing workflow uses `17_generation_handoff/`.
