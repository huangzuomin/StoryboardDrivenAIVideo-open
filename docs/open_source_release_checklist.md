# Open Source Release Checklist

Use this checklist before publishing the repository publicly.

## Required

- [ ] `README.md` explains purpose, quick start, workflow, and handoff output.
- [ ] `LICENSE` is present and approved for release.
- [ ] `.gitignore` excludes private learning packs, generated packs, and local outputs.
- [ ] `scripts/run_regression.py` passes.
- [ ] `scripts/check_skill_versions.py --package-dir examples/fan_kata_minimal` passes after syncing installed skills, or passes with `--no-installed` for release archive checks.
- [ ] Public examples contain only redistributable or placeholder assets.
- [ ] No API keys, upload IDs, private file paths, or generated platform secrets are committed.
- [ ] `storyboard-video-director` and `storyboard-video-qc` scripts compile.

## Recommended

- [ ] Add real screenshots only when their source is redistributable.
- [ ] Tag the first public release as `v0.1.0-alpha`.
- [ ] Keep private case-study learning packs outside the public repo.
- [ ] Document any external image/video generation tools as optional integrations.

## Current Public Smoke Test

```powershell
python scripts\run_regression.py
```

Expected result:

```text
Regression passed.
- examples\fan_kata_minimal
```
