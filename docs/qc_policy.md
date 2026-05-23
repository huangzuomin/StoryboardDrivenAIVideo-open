# QC Policy

QC exists to prevent expensive video generations from failing for avoidable reasons.

## Verdicts

- `READY`: suitable for handoff.
- `READY WITH RISKS`: generation can proceed, but visible risks remain.
- `FIX BEFORE GENERATION`: fix blockers before handoff.
- `STRATEGY RESET`: the chosen control strategy or layout is wrong enough that patching prompts is not enough.

## Strict Asset Mode

Use strict mode for final generation or paid/limited model runs.

Strict mode requires generated or user-supplied media for central controls. `prompt_only` assets are allowed during iteration but should not pass final handoff when the asset role is central to the project.

## High-Motion Projects

High-motion projects need:

- clear action progression
- body-driven prop logic
- panel-order adherence boosters
- final held pose or payoff
- reference assets for identity and recurring props

## Manual Visual Review

The automated visual asset review checks file presence, roles, status, and basic image readability. A human or vision-capable reviewer should still inspect whether the image content actually matches the role.
