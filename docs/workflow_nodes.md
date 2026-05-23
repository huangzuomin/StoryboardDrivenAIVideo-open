# Workflow Nodes

This document describes the production workflow as open-source users should understand it.

## 1. Director Pack

The director pack is the source of truth. It contains the control strategy, visual bible, beat storyboard plan, segment plan, prompts, manifest, and review reports.

Core files:

- `00_control_strategy.md`
- `02_duration_segment_plan.md`
- `03_visual_bible.md`
- `04_beat_storyboard_plan.md`
- `10_generation_manifest.json`

## 2. Storyboard Control

The annotated storyboard is a control image, not a final video frame. It may include panel numbers, arrows, timing notes, colored guides, and borders.

Downstream prompts must explicitly say not to render these storyboard artifacts in the final video.

## 3. Reference Assets

The manifest separates asset roles:

- storyboard control
- character reference
- prop reference
- environment reference
- style reference
- clean keyframe reference

Final production handoff should not rely on `prompt_only` assets for central controls.

## 4. Preproduction Orchestrator

Use:

```bash
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <pack_dir> --phase final
```

Phase profiles:

- `iteration`: prepares prompts and tasks with non-strict checks.
- `preflight`: default review profile.
- `final`: strict asset gate, visual storyboard requirement, QC, and production handoff bundle.

## 5. QC

`storyboard-video-qc` checks structure, strategy, reference roles, prompt adherence, asset status, and high-motion control risks.

Strict mode blocks final handoff when central visual assets are only prompt placeholders.

## 6. Production Handoff

`17_generation_handoff/` is the final local handoff surface for a video platform or video agent.

It should contain:

- uploadable asset list
- upload-ref prompt
- readiness report

It should not contain local absolute paths in the upload prompt.
