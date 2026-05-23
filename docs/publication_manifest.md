# Publication Manifest

This repository has two surfaces:

## Public Surface

Recommended for an open-source release:

- `README.md`
- `README.en.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `.gitignore`
- `.gitattributes`
- `requirements.txt`
- `skills/storyboard-video-director/`
- `skills/storyboard-video-qc/`
- `scripts/run_regression.py`
- `scripts/check_skill_versions.py`
- `examples/fan_kata_minimal/`
- `docs/workflow_nodes.md`
- `docs/production_handoff.md`
- `docs/qc_policy.md`
- `docs/open_source_release_checklist.md`
- `docs/publication_manifest.md`
- `docs/normal_user_prompt_regression_prompts.md`
- `skills/storyboard-video-director/references/production_asset_pipeline.md`
- `docs/storyboard_skill_reproduction_test_cases.md`

## Internal / Excluded Surface

Do not include in a first public release unless reviewed and sanitized:

- private learning packs
- generated production packs
- ad hoc output folders
- case-study research notes with local paths
- generated videos or images whose license is unclear
- platform upload IDs, API keys, or model-provider credentials

## Release Recommendation

Publish a clean release branch or repository containing only the public surface above. Keep internal case-study learning material private or move it into a separate sanitized documentation package.

Use `README.md` as the default Chinese landing page. Keep `README.en.md` as a compact English entry point.
