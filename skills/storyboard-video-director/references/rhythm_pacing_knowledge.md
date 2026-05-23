# Rhythm And Pacing Knowledge

Use this file before choosing duration, Segment count, Beat density, or storyboard panel count.

## Core Idea

Pacing is the audience's felt speed of story information. Rhythm is the pattern of emphasis, release, repetition, acceleration, pause, and payoff inside that speed.

Do not derive duration mechanically from panel count. First decide the scene's genre energy, then decide how long the audience needs to understand each action or emotion.

## Editing Principles To Apply

### 1. Emotion And Story Before Shot Math

Walter Murch's editing hierarchy is a useful planning lens: the strongest cut serves emotion and story before technical continuity. In storyboard planning, this means:

- do not add seconds just because a panel exists
- do not add panels unless they change emotion, story information, spatial clarity, or comic timing
- a pause is justified when the audience needs anticipation, realization, dread, embarrassment, or payoff
- an action beat is justified when it changes momentum, danger, distance, or cause-effect

Prompt check:

```text
What should the audience feel at this Beat, and does the duration support that feeling?
```

### 2. Internal Rhythm Versus External Rhythm

Internal rhythm comes from movement inside the shot: running speed, body recoil, falling objects, gaze, breath, dialogue, or music.

External rhythm comes from shot length and cuts: rapid cuts, long takes, repeated shot patterns, acceleration, deceleration, and held punchlines.

Use both:

- fast internal motion can still need a slightly longer wide shot if geography must read
- low internal motion can feel fast if cuts are short and information changes quickly
- comedy often needs a fast action burst plus a held reaction

### 3. Cut Rate Should Match Scene Energy

Shot length should be chosen from genre and story energy:

| Scene energy | Typical felt rhythm | Beat duration tendency | Notes |
| --- | --- | ---: | --- |
| quiet observation | slow, spacious | 4-8s per Beat | Use when environment or mood is the product. |
| emotional realization | slow-to-medium | 3-6s per Beat | Include reaction time and eye-trace. |
| product / explainer | medium, clear | 2-4s per Beat | Each Beat sells one claim or step. |
| chase comedy | fast with held punchlines | 1-3s per action Beat; 2-4s for setup/payoff | Alternate burst, near-miss, escalation, reaction. |
| action / rescue | fast but readable | 1.5-4s per Beat | Preserve geography and cause-effect. |
| montage / transformation | very fast pattern | 0.5-2s per micro-Beat | Use repetition and rhythmic match cuts. |
| dance / performance | phrase-based | 3-8s per phrase | Preserve full-body motion unless close-up is intentional. |

These are planning defaults, not hard laws. Stretch or compress based on clarity and emotion.

### 4. Acceleration Curves

Most energetic scenes should not run at one flat tempo. Use a curve:

- `setup`: just long enough to understand geography and desire
- `launch`: first burst of speed
- `complication`: faster or denser action
- `peak`: shortest, most intense beats
- `pause`: reaction or realization
- `payoff`: held long enough to land

For chase comedy:

```text
setup -> burst -> near-miss -> escalation -> chain reaction -> panic peak -> sudden stop -> held punchline
```

### 5. Information Density

If a Beat contains multiple pieces of information, either lengthen it or split it.

High-density Beat examples:

- character changes direction while camera also changes angle
- three objects fall and the hero reacts
- geography, danger, and emotion all need to read

Low-density Beat examples:

- one clear launch
- one insert
- one reaction blink
- one final held pose

Do not put too much information into a 1-second Beat unless the audience only needs the impression, not the details.

### 6. Readability Gates

Before assigning duration, ask:

- Does the viewer know where the subject starts?
- Does the viewer know where the subject is going?
- Does the viewer see what changed?
- Does the viewer understand cause and effect?
- Does the viewer get the reaction or emotion?

If any answer is no, add a setup panel, a wider shot, a reaction beat, or a slightly longer duration. Do not simply add more chaotic action.

### 7. Comedy Timing

Comedy needs contrast:

- quick action burst
- clean impact
- small delay
- reaction
- topper or final tag

For slapstick, do not make every Beat the same length. A typical gag rhythm:

```text
1.5s setup
1s launch
1s near-miss
1.5s impact
1s chain reaction
1s panic
2s realization
2-3s final held punchline
```

The exact values change by story, but the pattern matters: speed creates surprise; the hold lets the joke land.

### 8. Action Geography

Fast cutting does not mean unclear cutting. For chases and action:

- establish the route before speed
- preserve screen direction unless reversal is the point
- cut on motion or impact
- use wide shots when obstacle layout matters
- use close-ups for reaction, danger, or payoff
- return to geography after a chaotic burst

If the board cannot explain the route, the video model will likely drift.

### 9. Sound As Rhythm

Even when no final audio is generated, plan sound rhythm:

- footsteps, skids, impacts, object clatter
- breath, silence, held reaction
- music beat, non-lyrical stings, sudden dropouts

Sound cues help define when cuts should happen and where the audience should feel impact.

## Workflow Insert

Before writing `02_duration_segment_plan.md`, create a short pacing diagnosis:

```text
Pacing diagnosis:
- Genre energy:
- Audience felt speed:
- Target total duration:
- Average Beat duration:
- Fastest Beat:
- Slowest Beat:
- Required pauses:
- Segment split reason:
```

Then choose Segment count and Beat count.

## Duration Planning Heuristics

1. Estimate story beats by function, not by desired runtime.
2. Assign each Beat a rough duration based on energy.
3. Sum durations.
4. If total exceeds 15 seconds, split into Segment-specific boards.
5. If a high-energy scene feels slow, reduce Beat count or compress durations before adding Segments.
6. If a scene feels unclear, widen shots or split information, but keep the rhythm curve intentional.

## Panel Count Heuristics

Choose panel count from story density and genre craft, not from runtime alone.

- 6-8 panels: simple product, single reveal, one clear event, or low-complexity emotional moment.
- 8-12 panels: short action beat, simple dance phrase, compact rescue, short comedy setup/payoff.
- 12-16 panels: performance showcase, sport trick sequence, martial arts form, rhythm-led movement, music-video phrase, or technical escalation.
- 16-24 panels: highly technical movement, full music phrase, dense choreographic escalation, complex chase geography, or multi-stage transformation.

For rhythm-led performance, a 10-20 second board may still need 12-16 panels because each panel marks a technique, beat hit, camera escalation, or motif transformation. The board is a rhythm map, not only a shot-count estimate.

Sparse user prompts should not force sparse storyboards. If the subject implies expertise, infer the professional beat structure and choose enough panels to show the escalation.

## Example: Cat Chases Mouse In A Room

Naive plan:

```text
8 panels, 20 seconds = 2.5 seconds per panel.
```

Problem:

For a cat chasing a mouse, that can feel slow unless the style is deliberately slow-motion or lush animation. The story energy is chase comedy, so most action Beats should be 1-2 seconds, with longer holds only for setup and final punchline.

Better rhythm:

```text
P01 setup: 1.5-2s
P02 launch: 1-1.5s
P03 near-miss: 1-1.5s
P04 sofa impact: 1.5-2s
P05 chain reaction: 1.5-2s
P06 peak chaos: 1.5-2s
P07 wall-hole skid: 1.5-2s
P08 held punchline: 2-3s
Total: about 12-16s
```

If using Seedance2:

- A 12-15 second single Segment may work if the model can handle the action density.
- Two shorter Segment-specific boards may work better if control matters:
  - S01: 6-8s, P01-P04
  - S02: 6-8s, P05-P08
- Do not stretch to 20 seconds unless the user asks for a slower, more detailed animated short.

## Red Flags

- Every Beat has the same duration.
- A chase, rescue, fight, or slapstick gag is paced like a dialogue scene.
- Segment duration is chosen only because the model allows 15 seconds.
- More panels are added to solve rhythm instead of clarifying action.
- A final punchline has no hold.
- A complex action Beat has no geography setup.
- A multi-Segment video uses one shared storyboard image as the only downstream control reference.

