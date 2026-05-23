# Versioning

The skills use semantic versioning.

Current initial version:

```text
0.1.0-alpha
```

## Version Locations

Each skill records its version in two places:

- `skills/<skill-name>/VERSION`
- `skills/<skill-name>/SKILL.md` frontmatter `version`

Director packs record the workflow version in:

- `10_generation_manifest.json.workflow_version`
- `10_generation_manifest.json.skill_versions`

## Compatibility Rules

- `PATCH`: bug fixes, wording updates, and validator fixes that do not change pack structure.
- `MINOR`: new scripts, checks, asset roles, or optional fields that remain backwards compatible.
- `MAJOR`: pack structure, manifest schema, default folder, or required command changes that need migration.

## Checks

Check repo and installed Codex skill versions:

```powershell
python scripts\check_skill_versions.py
```

Check a pack manifest too:

```powershell
python scripts\check_skill_versions.py --package-dir examples\fan_kata_minimal
```

For release archives where the installed Codex skill is irrelevant:

```powershell
python scripts\check_skill_versions.py --no-installed --package-dir examples\fan_kata_minimal
```

## Release Flow

1. Update code, docs, and examples.
2. Update `VERSION`, `SKILL.md` frontmatter, and `CHANGELOG.md`.
3. Run regression and version checks.
4. Sync installed Codex skills if testing in Codex.
5. Tag the release, for example `v0.1.0-alpha`.
