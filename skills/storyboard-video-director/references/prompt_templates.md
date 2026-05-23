# Prompt Templates

## Annotated Storyboard Prompt

Use this as the base structure:

```text
Create a 16:9 storyboard sheet with [N] cinematic panels.

Style:
black-and-white rough pencil storyboard, fast previsualization drawing, coarse graphite lines, strong readable silhouettes, minimal background detail, not photorealistic, not polished comic art.

Subject and world:
[inherit Visual Bible summary]

Panel sequence:
P01: [Beat summary, shot size, action, camera, emotion]
P02: [...]

Annotation system:
red arrows = subject movement
blue arrows = camera movement
green marks = framing / composition / visual focus
orange marks = lighting / signal / danger / environmental force
purple marks = emotion / voice / narrative pressure
black text = panel ID, shot size, very short shot note

Requirements:
every panel must show motion, pressure, change, or decision.
keep panel labels readable.
show camera direction and subject movement clearly.
no timestamps, no logos, no subtitles, no photo realism, no extra characters, no dense readable text.
```

## High-Action Annotated Storyboard Prompt

Use this for chase, dance, disaster, fight, slapstick, rescue, or any board where motion quality is the product. Before writing, consult:

- `cinematic_storyboard_language.md`
- `motion_action_vocabulary.md`
- `storyboard_genre_patterns.md`

```text
Create a 16:9 annotated storyboard sheet with [N] cinematic panels.

The actual storyboard drawings must be black and white only: rough pencil lines, fast gesture drawing energy, lightweight construction, strong silhouettes, readable staging, unfinished professional previs style.

Subject and world:
[inherit Visual Bible summary, including role of any character/environment/style reference images]

Genre grammar:
[genre-specific rhythm, e.g. chase comedy setup -> escalation -> reversal -> payoff, or contemporary dance breath -> acceleration -> collapse -> release]

Motion rule:
Every panel must contain visible motion, impact, transition, or decision. Avoid static standing poses. Each panel must show direction, momentum, and consequence.

Panel sequence:
P01: [shot size], [angle], [lens note], [composition], [subject action with force and direction], [camera movement], [environment progression], [emotion/sound note]
P02: [...]

Camera language:
Use professional shot notes such as wide shot, low-angle tracking, overhead geography, aggressive close-up, whip pan, handheld push-in, orbit, long lens compression, wide-angle distortion, rack focus, or locked-off punchline frame where appropriate.

Environment progression:
[state how the space changes panel by panel: smoke, debris, broken furniture, wet floor reflection, evidence accumulation, hazard spread, product assembly, etc.]

Annotation system:
red arrows = subject/body/object movement
blue arrows = camera movement
green marks = framing / composition / visual focus
orange marks = lighting / danger / signal / impact direction
purple marks = emotional / vocal / sound / punchline emphasis
black text = panel ID, lens note, short shot note

Requirements:
- preserve character design, costume/body design, environment layout, and style from reference assets.
- keep labels and marks readable but sparse.
- include one clear camera note or lens note per panel.
- include one motion/consequence note per panel.
- keep screen direction consistent unless a reversal is intentional.
- no timestamps, no logos, no subtitles, no photorealism, no polished comic art, no dense readable text.
```

## Premium Hand-Drawn Action Storyboard Prompt

Use this when the user wants a visually impressive storyboard sheet, a high-motion performance board, or a sparse prompt that should be upgraded into a professional director-level board. It is especially useful for `rhythm_performance_board`.

```text
Create a 16:9 premium hand-drawn action storyboard sheet with [N] panels arranged in a clean readable grid.

Title strip:
[PROJECT / PERFORMER NAME] - [SUBJECT] STORYBOARD
[optional track / energy cue]    [optional BPM]    [short theme line]

Style:
professional hand-drawn production storyboard sheet, expressive pencil and ink, rough but masterful gesture drawing, dynamic action-animation energy, cinematic camera notes, handwritten director annotations, strong speed lines, impact marks, dust, light bursts, readable silhouettes, controlled panel grid, not polished comic cover art, not photoreal final frames.

Professional inference:
[strongest genre interpretation]
[subject-specific technique vocabulary]
[named subject identity and signature silhouette]
[dominant motif system]
[rhythm engine: BPM / timestamps / beat counts / breath pattern / edit pulse]
[final emotional payoff]

Subject and world:
[inherit Visual Bible summary]

Motif system:
Dominant moving shape: [rope arc / footwork grid / orbit line / prop trail / fabric wave / other]
Repeated graphic pattern: [how it appears across panels]
Escalation: [simple path -> complex figure -> full-frame energy structure]
Final transformation: [how the motif resolves in the final panel]

Panel sequence:
P01 [timestamp or beat count]: [shot size], [angle], [lens], [technique/action phrase], [subject action with direction and momentum], [motif appearance], [camera movement], [impact or sound cue], [short handwritten director note]
P02 [...]

Expressive annotation layer:
Use a few short handwritten director notes tied to rhythm, emotion, impact, or camera intent, such as "LET'S GO", "AIR PAUSE", "BEAT LOCKED", "ACCELERATE >> MAX", "EVERYTHING BUILDS TO THIS", or a localized equivalent. Keep phrases sparse and large enough to read.

Annotation system:
red arrows = subject/body/prop movement
blue arrows = camera movement
green marks = framing / composition / visual focus
orange marks = lighting / impact / environmental force
purple marks = rhythm / sound / emotion / beat hit
black text = panel ID, timestamp/beat, lens note, short shot note

Requirements:
- every panel must add new visual information.
- show a clear rhythm curve from anticipation to final payoff.
- make the dominant motif visible in most panels.
- include named techniques or specific action phrases, not generic movement.
- vary camera angles intentionally across the board.
- keep labels and notes readable but sparse.
- no logos, no subtitles, no dense text, no unrelated characters, no final-video photorealism, no poster composition.
```

## Rough Action Planning Board Prompt

Use this when the storyboard image will be used as direct video-control reference for high-motion action, fan kata, weapon forms, martial arts, chase, sport, or dense choreography. This mode prioritizes timing, staging, and motion readability over illustration quality.

```text
Create a 16:9 rough cinematic action-planning storyboard sheet with [N] panels arranged in a clean readable grid.

Style:
rough sakuga planning thumbnails, key animation board, first-pass animation previs, loose pencil and ink, visible construction lines, broken strokes, simplified masses, semi-mannequin characters, low-to-medium detail, strong silhouettes, clear body lines, clear prop arcs, clear camera notes. Prioritize timing, staging, and motion readability over beauty.

Do not make polished concept art, poster art, finished comic art, detailed clothing folds, material rendering, decorative linework, or photoreal final frames.

Planning layers:
- body path and weight transfer
- prop / weapon / fan / fabric path
- cloth or hair follow-through
- camera path
- timing pauses, acceleration, impact, and final payoff

Subject and world:
[inherit Visual Bible summary]

Motion system:
[body-driven prop logic, Laban movement qualities, emotion/arousal curve, motif progression]

Panel sequence:
P01: [shot size], [camera angle/lens], [one clear action beat], [body path], [prop/cloth path], [camera path], [timing note], [purpose note]
P02: [...]

Annotation system:
Use sparse, functional, hand-drawn annotation marks. Keep them readable but do not cover face direction, body line, or prop silhouette.
[project color key]

Requirements:
- one clear action beat per panel.
- preserve spatial continuity and screen direction.
- show anticipation, burst, follow-through, and recovery.
- make body-driven prop logic visible.
- keep notes short and functional.
- no dialogue, subtitles, logos, watermarks, decorative UI, dense text, or polished illustration finish.
```

## Rhythm Performance Storyboard Add-On

```text
Use rhythm-performance grammar: anticipation -> first beat -> acceleration -> signature trick -> suspended pause -> combo escalation -> speed ramp -> impact/release -> final held statement.
Include a title strip, performer identity, optional track/BPM, and per-panel timestamps or beat counts.
The repeated movement motif must become the board's visual rhythm system.
Every panel should name a technique/action phrase and show how the body, prop, floor, light, or camera hits the beat.
Use short expressive director notes rather than dense explanatory text.
```

## 4x3 Trailer Grid Prompt Add-On

Use for invasion, disaster, horror reveal, large-scale promo, or any short trailer-like sequence.

```text
Use a 4x3 trailer grid with 12 sequential panels.
Each panel is an independent image and also a sequential keyframe in one continuous flow.
Maintain strong visual and narrative consistency across all panels.

Sequence structure:
P01-P02: in medias res, immediate danger, partial visibility.
P03-P04: situation begins to reveal, scale emerging.
P05-P07: main reveal and key story beat.
P08-P10: escalation, conflict intensifies.
P11: peak moment.
P12: aftermath, unresolved state, or final haunting image.

Requirements:
- one continuous unfolding event, no disconnected ideas.
- maintain spatial logic, no teleporting.
- mix close, mid, and wide shots.
- make the threat or story force escalate panel by panel.
```

## 4-Panel Face / Emotion Flow Prompt Add-On

Use for dialogue, monologue, restrained acting, singing close-up, or inner conflict where facial continuity matters more than action geography.

```text
Use a 4-panel horizontal emotional flow.
The panels should read left to right as one subtle acting progression.

Panel structure:
P01: social mask / neutral surface.
P02: first emotional leak through eyes, breath, or posture.
P03: conflict breaks through; expression and body tension become visible.
P04: decision, concealment, release, or quiet emotional turn.

Each panel must include gaze direction, mouth/breath state, posture change, camera distance, and emotion coordinate.
Use face and body acting, not large action.
Keep text minimal or absent.
```

## Body-Driven Transformation Prompt Add-On

Use when ribbons, fans, fabric, magic, costume, product parts, or abstract shapes transform through movement.

```text
Performance logic:
The subject is not a static center pose. The body actively drives the transformation choreography.
Every transformation must be triggered by visible full-body actions: stepping, pivoting, spinning, arching, sweeping arms, twisting torso, rising, leaping, landing, or turning through profile.
The transformed material reacts to shoulders, wrists, hips, spine, hair, costume, and footwork with delayed follow-through and overlapping motion.

Transformation logic:
[form 1] -> [form 2] -> [form 3] -> [storm/peak] -> [final reveal].
Each form is constructed from the same material and quickly transforms into the next without settling into long static holds.

Pacing:
continuous escalation, no calm posing, no mannequin-like floating, no scene where only the prop moves while the body remains frozen.
The final reveal remains alive and active with subtle continuing motion.
```

## Concise Seedance-Style Video Prompt

Use when sending a compact downstream prompt to a video model after the storyboard pack already exists.

```text
INTENT:
[one concise paragraph describing the story arc or performance objective]

STYLE:
[visual style, rendering finish, camera tone]

WORLD:
[location, atmosphere, lighting logic, important environment behavior]

REFERENCES:
Use @[storyboard ref] as the exact sequential visual keyframe reference for the video.
Treat every panel as an independent cinematic shot, not as a single image.
Follow the storyboard shot by shot, preserving panel order, timing, action, camera, framing, and emotion progression.
Use @[character ref] as the strict identity reference.
Use @[environment/style ref] only for geography, lighting, texture, and finish.

EXECUTION:
Expand motion naturally between panels with body weight, prop physics, cloth/hair response, camera inertia, and environmental motion.
Use annotations, arrows, and movement guides internally for staging and animation logic only.

AVOID:
Do not render storyboard artifacts, colored annotations, arrows, motion lines, handwritten notes, labels, panel numbers, borders, timing marks, sketch overlays, text, UI, logos, subtitles, or watermarks.
Do not skip, merge, reorder, or reinterpret panels.
Do not add extra action beyond the storyboard.
```

## Chase Comedy Storyboard Prompt Add-On

```text
Use chase-comedy grammar: setup, acceleration, near-miss, escalation, reversal, pause, payoff, final tag.
Make the room geography readable. Escalate environment damage panel by panel: scatter, skid, rip, topple, smash, collapse, freeze, tiny victory.
Use wide readable staging, low-angle tracking, whip pans, overhead obstacle layout, locked-off punchline frames, reaction close-ups.
Avoid teleporting characters, unclear exits, excessive motion blur, generic action tone, and missed reaction beats.
```

## Contemporary Dance Storyboard Prompt Add-On

```text
Use dance-film grammar: the camera behaves like a partner. Preserve full-body choreography except for intentional close-ups of face, hands, torso, breath, or vocal strain.
Every panel must show body momentum: floor slide, crawl transition, hair whip, balance shift, collapse, rebound, suspension, slash, glide, press, or release.
Use negative space, harsh light beams, wet floor reflections, smoke, fabric motion, overhead floorwork, side silhouettes, low angles, orbit movement, handheld whip pans.
Avoid cropped limbs, static standing poses, overcutting, and camera motion that hides choreography.
```

## Clean Keyframe Prompt

Use one file per Beat:

```text
[Shot size] cinematic video keyframe of [subject] in [location].

Visual Bible continuity:
[identity, costume, lighting, camera texture, environment]

Beat action:
[the single core visual moment for this Beat]

Composition:
[framing, subject position, depth, environment relationship]

Mood:
[emotion and pressure]

Avoid:
arrows, annotation marks, text, panel labels, storyboard borders, shot numbers, subtitles, logos, extra characters, changed costume, changed identity, changed location, over-stylized illustration.
```

## Seedance2 Segment Prompt

Use one file per Segment:

```text
Generate one coherent [duration]-second Seedance2 video segment.

Use the provided reference frames as sequential visual beats:
- P01 = opening composition / starting pose: [...]
- P02 = middle action beat: [...]
- P03 = ending pose / transition target: [...]

Do not treat these reference frames as separate unrelated scenes.
They are time-ordered beats within one continuous segment.

Preserve the same subject identity, costume, location, lighting logic, visual style, and emotional continuity.

Segment ID:
[Sxx]

Segment mode:
[single_continuous_shot / coherent_multi_shot_sequence / motivated_camera_changes / match_cut_sequence]

Beat progression:
0-[x]s: [...]
[x]-[y]s: [...]
[y]-[duration]s: [...]

Camera:
[camera movement and shot logic]

Motion:
[subject action path and body/object movement]

Environment:
[lighting, haze, weather, crowd, props, signals, or spatial pressure]

Audio / vocal:
[if relevant, describe non-lyrical sound, voice, breath, music energy, or silence]

Opening state:
 [...]

End state:
 [...]

Transition to next Segment:
 [...]

Avoid:
random scene changes, changing identity, changing costume, changing location, changing lighting logic, unrelated cuts, added characters, added text, logos, subtitles, style drift, uncontrolled camera changes, extra limbs, severe deformation, treating the reference frames as unrelated images.
```
