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

## Compatibility

Older internal builds used `17_generation_deployment/`. New public-facing workflow uses `17_generation_handoff/`.
