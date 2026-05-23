# Contributing

Thanks for improving Storyboard Driven AI Video.

## Development Loop

Run the public regression before submitting changes:

```powershell
python scripts\run_regression.py
```

Also compile the skill scripts after editing Python:

```powershell
python -m py_compile (Get-ChildItem skills\storyboard-video-director\scripts,skills\storyboard-video-qc\scripts -Filter *.py | ForEach-Object FullName)
```

## What To Keep Out Of Pull Requests

- private learning packs
- generated videos
- non-redistributable source images
- local production packs
- API keys, upload ids, or platform credentials

Use `examples/` for small redistributable fixtures.

## Skill Design Principles

- Keep storyboard control, character reference, prop reference, environment reference, style reference, and clean keyframe reference separate.
- Prefer plain-language regression prompts over expert prompt imitation.
- Treat prompt-only assets as iteration artifacts, not final production assets.
- Preserve user intent while allowing professional storyboard inference.
