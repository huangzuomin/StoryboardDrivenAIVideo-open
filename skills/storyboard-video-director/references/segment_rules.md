# Segment Rules

## Segment Duration

Seedance2 Segment limit: 5-15 seconds.

Use these defaults:

- Simple concept: 1 Segment, 5-15 seconds.
- Normal short video: 2-4 Segments, 20-45 seconds.
- Strong action or strong narrative: 4-8 Segments, 45-60 seconds.
- Over 60 seconds: group by Sequence.
- Over 90 seconds: recommend chapter-level breakdown.

15 seconds is a maximum, not a target.

## Beat Density

Recommended density:

- 5 second Segment: 1-2 Beats.
- 8-10 second Segment: 2-3 Beats.
- 12-15 second Segment: 3-5 Beats.
- More than 5 Beats: split the Segment.

High-motion Segments should use fewer Beats and clearer start/end poses.

## Segment-Specific Storyboard Control

When the plan contains more than one Segment, each Segment must have an independent storyboard control prompt and, if images are generated, an independent storyboard image.

Required behavior:

- `S01` video generation should receive a storyboard image that contains only the Beats for `S01`.
- `S02` video generation should receive a storyboard image that contains only the Beats for `S02`.
- Do not ask a downstream video model to use one shared 8-panel or 12-panel overview board while verbally telling it to use only half of the panels.
- A full-project overview board may still be useful for human review, editing rhythm, and continuity checks, but it is not the direct control asset for Segment generation.

Reason:

Video agents tend to treat every visible panel in a reference image as relevant. If the board contains Beats outside the current Segment, the model may compress, repeat, skip, or hallucinate actions. Segment-specific storyboard images reduce ambiguity and make the handoff to platforms such as xyq safer.

## Motion Risk

High-risk actions:

- fast turn
- jump
- fall
- standing-to-floor or floor-to-standing transition
- intense running
- body collision
- complex dance
- strong camera motion
- rapid scene switching
- strong human-object interaction

For high-risk Segments:

- shorten duration
- reduce Beat count
- define opening and ending body states
- avoid stacking too many motion goals

## Segment Modes

### single_continuous_shot

Use for dance, body performance, psychological pressure, immersive movement, and emotional release.

Requirements:

- few cuts or no cuts
- camera movement does spatial work
- continuous action
- clear start and end posture

### coherent_multi_shot_sequence

Use for advertising, city promo, product display, news-like short films, and multi-angle spatial explanation.

Requirements:

- internal shot changes are allowed
- all shots serve one Segment function
- maintain identity, location, light, and continuity across Beats

### motivated_camera_changes

Use for disaster rescue, pursuit, investigation, action scenes, and documentary field pressure.

Requirements:

- camera changes are motivated by action, sound, eyeline, or spatial pressure
- avoid arbitrary cuts
- preserve movement direction

### match_cut_sequence

Use for emotional progression, product change, time passage, action rhythm, and music video language.

Requirements:

- connect Beats through action, composition, light, or posture
- each Beat must have a clear match relationship

### rhythm_performance_board

Use for sport-performance, dance, music-video, martial arts form, stage act, skating, parkour, jump rope, drumming, runway, or any movement where rhythm is the product.

Requirements:

- make rhythm visible through beat counts, timestamps, repeated motif shapes, or technique escalation
- preserve technique readability with full-body or clear contact-point shots
- use named actions, not generic athletic poses
- alternate fast motion snapshots with readable impact or hold moments
- end with a held payoff, hero pose, release, or final statement

### face_emotion_flow

Use for monologue, dialogue, restrained acting, singing close-up, inner conflict, or psychological shift.

Requirements:

- prioritize gaze, breath, mouth state, posture, and facial expression continuity
- use 4-panel horizontal flow when a storyboard is needed
- include emotion coordinates or a valence/arousal curve
- avoid forcing subtle acting into action-grid grammar

### body_driven_transformation

Use for ribbon, fan, fabric, magic, product assembly, costume change, or any transformation where visible body/action must trigger the changing shape.

Requirements:

- transformation is driven by body mechanics, not autonomous floating
- define transformation stages clearly
- show trigger actions such as step, pivot, spin, sweep, twist, jump, or landing
- use delayed follow-through and overlapping motion
- keep the final reveal alive with subtle continuing motion

## Panel Count

When unspecified, choose:

- 3 panels: very short concept, single action, preview board.
- 6 panels: simple complete scene.
- 9 panels: standard short video scene.
- 12 panels: strong action, strong narrative, performance, disaster, chase, dance.
- 16 panels: dense action, rhythm performance, or complex segment set; avoid as default for quiet scenes.
- More than 16 panels: split into multiple storyboard sheets.

Estimate:

```text
panel_count = segment_count * average_beats_per_segment
```

For multi-Segment output, apply that estimate per Segment sheet as well as the optional overview sheet.
