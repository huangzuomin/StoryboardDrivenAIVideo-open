# aimikoda Case Patterns

This file distills public storyboard-to-video case patterns into reusable production guidance. Use it for pattern inspiration, not as a verbatim source library.

## 1. Define Visuals First

Pattern:

```text
Define visuals first with an image/storyboard model, then use the video model to execute motion.
```

Use when:

- text-to-video randomness is high
- camera sequence matters
- the user needs repeatable control

Skill implication:

The pack should make control assets explicit before writing final video prompts.

## 2. Storyboard as Shot Sequence

Pattern:

```text
Use the provided image as a visual shot-sequence reference.
Read panels left to right, top to bottom as chronological keyframes.
Do not show grid, panels, borders, or text in the final video.
Smoothly connect each panel into one coherent sequence.
```

Use when:

- a single storyboard sheet controls a short video
- the main risk is panel-order confusion

## 3. Simple Video Prompt Contract

Pattern:

```text
INTENT / STYLE / WORLD / REFERENCES / VISUAL APPROACH
```

Use when:

- the storyboard already contains most visual detail
- downstream model performance improves with concise instruction

Skill implication:

Do not always send the full director pack as the final generation prompt. Preserve a concise downstream prompt mode.

## 4. Multi-Reference Identity Lock

Pattern:

```text
Storyboard controls sequence.
Character sheet controls identity.
Environment controls geography.
Style reference controls finish.
```

Use when:

- character consistency matters
- multiple characters have contrasting identity
- storyboard drawings are too rough to carry final design

## 5. 4x3 Trailer Grid

Pattern:

```text
Panels 1-2: immediate danger / partial visibility.
Panels 3-4: situation reveal / scale emerging.
Panels 5-7: main reveal / key beat.
Panels 8-10: escalation.
Panel 11: peak moment.
Panel 12: aftermath or unresolved state.
```

Use for:

- trailers
- disaster
- invasion
- horror reveal
- high-scale promo

## 6. 12-Beat Compressed Performance

Pattern:

```text
Compress the full 12-beat sequence into 15 seconds.
Each beat appears clearly as a fast motion snapshot, not a full-length action.
Use urgent rhythm, quick cuts, match cuts, and whip transitions.
No pauses until the final beat.
```

Use for:

- dance
- singing performance
- sport phrase
- short music-video phrase

## 7. 16-Panel Action Escalation

Pattern:

```text
Use the 16-panel storyboard as the direct sequential visual keyframe reference.
Preserve choreography flow, framing logic, and motion escalation.
Add in-between animation, cloth physics, prop recoil, footwork detail, camera inertia, and particles while staying faithful to the sequence.
```

Use for:

- martial arts
- sword action
- parkour
- stylized sport
- dense technique showcases

## 8. Director Language Two-Step

Pattern:

1. Generate abstract cinematic language from a named influence or mood.
2. Apply that language to a new storyboard grid without copying copyrighted scenes or characters.

Use when:

- the user asks for a director-inspired tone
- the board needs coherent lens/light/movement language

Safety:

Describe abstract qualities such as contrast, camera distance, pacing, blocking, or light behavior. Do not reproduce living artists' exact style as a direct imitation.

## 9. Body-Driven Prop Transformation

Pattern:

```text
The character is not a static center pose.
Every transformation is triggered by visible body action.
Prop forms evolve through clear stages and never settle for long.
Final reveal remains alive, with subtle motion continuing through the pose.
```

Use for:

- ribbon
- fan
- fabric
- magic transformation
- costume reveal
- product assembly

## 10. Soft-Hint Reality

Current models may treat storyboards as soft hints rather than hard constraints.

Therefore:

- add adherence boosters when fidelity matters
- keep storyboard labels sparse and clear
- separate reference roles
- evaluate output after generation
- do not promise exact compliance

