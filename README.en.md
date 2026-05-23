# Storyboard Driven AI Video

Storyboard Driven AI Video is a pair of Codex skills for building and checking storyboard-first AI video preproduction packs.

The project focuses on control before generation: plan the video as a director pack, create or register visual reference assets, run production QC, then hand off a clean upload prompt and asset manifest to a downstream video model or agent.

Default documentation is in Chinese: [README.md](README.md).

## What It Includes

- `storyboard-video-director`: turns a plain-language video idea into a structured director pack.
- `storyboard-video-qc`: reviews a pack before expensive video generation.
- Production handoff builder: creates upload-ready references and a prompt under `17_generation_handoff/`.
- Regression utilities and public fixture packs for checking the workflow without private assets.

## Quick Start

```powershell
python -m py_compile (Get-ChildItem skills\storyboard-video-director\scripts,skills\storyboard-video-qc\scripts -Filter *.py | ForEach-Object FullName)
python scripts\run_regression.py
```

Run the final preproduction chain against the public fixture:

```powershell
python skills\storyboard-video-director\scripts\preproduction_orchestrator.py examples\fan_kata_minimal --phase final
```

Expected final outputs:

- `examples/fan_kata_minimal/16_preproduction_orchestrator_report.md`
- `examples/fan_kata_minimal/17_generation_handoff/asset_manifest.json`
- `examples/fan_kata_minimal/17_generation_handoff/video_prompt_for_upload.txt`
- `examples/fan_kata_minimal/17_generation_handoff/handoff_readiness_report.md`

## Installing the Skills in Codex

```powershell
Copy-Item skills\storyboard-video-director $env:USERPROFILE\.codex\skills\storyboard-video-director -Recurse -Force
Copy-Item skills\storyboard-video-qc $env:USERPROFILE\.codex\skills\storyboard-video-qc -Recurse -Force
```

The repository copy and the installed Codex copy are separate. Re-copy after local edits when you want Codex to use the updated version.

## Production Handoff

Use `--phase final` when a pack is ready for expensive generation:

```powershell
python skills\storyboard-video-director\scripts\preproduction_orchestrator.py <pack_dir> --phase final
```

The handoff folder contains only platform-facing material:

- `asset_manifest.json`: local upload files mapped to stable `@upload_ref` handles.
- `video_prompt_for_upload.txt`: prompt written against upload refs, not local absolute paths.
- `handoff_readiness_report.md`: pass/fail summary for generation readiness.

## Versioning

The initial release line starts at:

```text
0.1.0-alpha
```

Check repo, installed skill, and pack manifest versions:

```powershell
python scripts\check_skill_versions.py --package-dir examples\fan_kata_minimal
```

## Status

The project is suitable for alpha/beta use. The core workflow is script-testable, but actual storyboard/image/video generation still depends on external model tools.
