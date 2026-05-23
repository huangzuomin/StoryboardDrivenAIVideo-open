# Performance Control Systems

Use this file when a video depends on facial acting, singing, dance, martial arts, sport technique, prop choreography, transformation, or inner emotional state.

## Control Choice

Do not force every scene into the same storyboard format.

Use storyboard-heavy control when the scene depends on:

- spatial staging
- action order
- camera continuity
- group blocking
- prop paths
- transformation stages
- product use sequence

Use face/emotion-heavy control when the scene depends on:

- inner conflict
- restrained dialogue
- monologue
- micro-expression
- singing close-up
- eye-line and breath rhythm
- subtle psychological shift

Use hybrid control when facial acting and spatial action both matter.

## Emotion Model

Use a simple valence/arousal curve when emotion must change across the video.

Template:

```text
Emotion model:
Valence: [negative/neutral/positive curve]
Arousal: [low/medium/high curve]
Dominant shift: [what changes emotionally and when]
Visible signals: [breath, gaze, jaw, shoulders, hand tension, posture, pace]
```

Examples:

```text
Valence: guarded uncertainty -> focused resolve -> fierce release
Arousal: low stillness -> sharp burst peaks -> sustained high -> composed finish
```

## FACS Lite

Use FACS only when facial expression or singing mouth shape matters. Keep it short.

Common lightweight cues:

- `AU1+AU4`: inner brow raise plus brow tension, worried focus.
- `AU5`: upper eyelid raise, intensity or alarm.
- `AU12`: smile pull, warmth or controlled confidence.
- `AU14`: dimpler, restrained skepticism or pressure.
- `AU25`: lips parted, speaking or singing mouth.
- `AU26`: jaw drop, open release.
- `AU43`: eye closure or exhausted blink.

Template:

```text
FACS:
[AU codes] = [plain-language expression function].
Use these as subtle acting targets, not exaggerated masks.
```

Avoid long FACS lists. If the prompt becomes unreadable, describe the expression in plain language.

## Emotion Lite

Use this when the scene needs readable emotional progression but not full face/emotion-heavy control: discovery, wonder, fear-to-trust, reunion, quiet realization, child/creature bonding, or a small final emotional payoff.

Template:

```text
Emotion Lite:
- gaze:
- brows:
- mouth/breath:
- shoulders/posture:
- hand tension:
- transition:
```

Example:

```text
Emotion Lite:
- guarded gaze, shoulders hunched, object held close
- eyes widen slightly, breath pauses, body leans but does not retreat
- fear softens into surprise, hand opens
- tiny cautious smile, fingertips relaxed, shared stillness
```

Use full FACS only when facial acting is the primary control surface. Use IPA only for singing, chanting, dialogue, or mouth timing.

## IPA and Mouth Timing

Use IPA only when singing, chanting, or a precise spoken phrase matters. Keep text short and avoid long lyrics.

Template:

```text
Vocal / mouth timing:
Continuous live singing throughout, with visible breath, mouth movement, throat tension, and body strain.
IPA cue, once:
/short phonetic phrase/
```

Rules:

- Do not quote long lyrics.
- Use one short phrase or non-lyrical syllables.
- Tie mouth shapes to breath and body effort.
- If lyrics are not important, describe vocal energy instead of IPA.

## Laban Movement

Use Laban effort qualities to define body texture, not just action names.

Useful qualities:

- `Glide`: smooth, sustained, direct, light.
- `Float`: airy, indirect, sustained, light.
- `Slash`: fast, strong, indirect, explosive.
- `Dab`: fast, light, direct, accented.
- `Punch`: fast, strong, direct, percussive.
- `Press`: sustained, strong, direct, heavy.
- `Wring`: sustained, strong, indirect, twisting.
- `Flick`: fast, light, indirect, quick release.
- `Bound`: controlled, contained, precise.
- `Free Flow`: continuous, open, uncontrolled release.

Template:

```text
Laban movement:
[quality] -> [quality] -> [quality], with [Bound/Free Flow] control changes.
```

## Body-Driven Prop Logic

Use this when props or visual effects are central: ribbon, fan, rope, bat, sword, fabric, smoke, magic, product assembly, costume transformation.

Principle:

The prop must be visibly driven by body action. It should not animate independently unless the story explicitly calls for magical autonomy.

Template:

```text
Performance logic:
The character is not a static center pose. The body actively drives the prop choreography.
Every prop transformation is triggered by visible full-body actions: [steps, pivots, spins, torso twist, arm sweep, jump, landing].
The prop reacts to shoulders, wrists, hips, spine, hair, costume, and footwork with delayed follow-through and overlapping motion.
```

Prop progression template:

```text
Prop logic:
[simple shape] -> [larger shape] -> [complex pattern] -> [storm/peak] -> [final emblem/reveal].
Each form transforms quickly into the next without settling into long static holds.
```

Avoid:

- only the prop moves while the character freezes
- static center posing
- unmotivated floating
- long calm holds in a fast transformation sequence
- prop paths that ignore body mechanics

## Fan / Sleeve / Weapon Kata Control

Use this for fan kata, sleeve martial dance, sword forms, ribbon forms, staff/bat/sport-performance forms, and any action where the prop path is the visible rhythm system.

Required controls:

- Emotion model: calm control -> focused intensity -> explosive release -> composed finish, adjusted to the user's story.
- Laban qualities: start with `Glide` or `Bound` control, escalate through `Slash`, `Flick`, `Punch`, `Spin`/rotation language, then return to `Bound` or a held statement when the ending must be stable.
- Body path: foot plant, step, slide, pivot, jump, landing, or breath recovery must be visible.
- Prop path: fan/blade/ribbon/sleeve path must be visually attached to wrist, shoulder, torso, hip, or footwork.
- Timing: include at least one anticipation pause, one acceleration burst, one peak path, and one recovery or held payoff.

Avoid:

- generic dance wording without technique intent
- prop trails that hide the grip, fan silhouette, or body line
- static center posing while the prop performs alone
- uncontrolled effects that make the path unreadable

## Object / Product / Creature Lock

Use this when a recurring object, product, robot, pet, artifact, creature, prop, or hero item must stay visually consistent across panels and video generation.

Template:

```text
Object Lock:
- scale:
- silhouette:
- material:
- moving parts:
- light source:
- fixed features:
- allowed motion:
- forbidden mutations:
```

Example small robot lock:

```text
Robot Lock:
- palm-sized only
- round head, small body, tiny arms, tread feet
- weathered white ceramic-metal shell
- one cyan chest core fixed at center chest
- two small dot eyes
- friendly, fragile, non-weaponized
- cannot become giant, humanoid mecha, monster, drone swarm, weapon, or branded device
```

Product-lock and object-lock references should be written into the Visual Bible, manifest reference roles, clean keyframe prompts, and final video prompt avoid list.

## Face/Emotion Flow Layout

Use a 4-panel horizontal flow for restrained acting or dialogue:

```text
Panel 1: neutral mask / social surface
Panel 2: first emotional leak
Panel 3: conflict breaks through
Panel 4: decision, concealment, or release
```

Each panel should include:

- gaze target
- facial action
- breath or mouth state
- posture change
- emotion coordinate
- camera distance

## Adherence Boosters

When fidelity matters, add:

```text
Follow the exact panel order.
Do not skip, merge, reorder, or reinterpret panels.
Use annotations, arrows, and movement guides internally for staging and animation logic only.
Do not render storyboard artifacts in the final video.
No extra action beyond the storyboard.
Treat each panel as a fast motion snapshot, not as a full-length action.
```
