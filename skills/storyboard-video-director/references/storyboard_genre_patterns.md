# Storyboard Genre Patterns

Use this file when selecting panel count, camera grammar, motion rhythm, annotation priorities, and failure-mode guards by genre.

Sources distilled: StudioBinder storyboard/commercial/action guidance, previsualization references, dance-film references including Maya Deren's camera-choreography model, comedy storyboarding/editing references, film noir lighting notes, advertising animatic guidance, music-video storyboard guidance, PSA guidance, and recent AI video consistency research.

## General Previz Baseline

Treat storyboard panels as camera-facing shot units, not script paragraphs. Each panel should specify:

- shot size
- angle
- lens or depth if useful
- camera movement
- subject blocking
- action arrows
- timing or transition
- continuity/VFX note when needed
- sound, music, vocal, or impact cue when rhythm matters

## Layout Patterns

Choose layout intentionally. Panel count and grid shape communicate different control priorities.

| Layout | Best For | Control Priority | Failure Guard |
| --- | --- | --- | --- |
| `3x3_action_grid` | short action, fight beats, chase gags, athletic moves | clear geography, screen direction, tight camera direction | avoid overloading each panel with too many actions |
| `4_panel_horizontal_flow` | dialogue, character moments, inner emotional shift | gaze, expression, breath, posture, relationship progression | avoid forcing subtle acting into action grammar |
| `4x3_trailer_grid` | trailers, disaster, invasion, horror reveal, large-scale escalation | opening danger, reveal, escalation, peak, aftermath | avoid disconnected spectacle panels |
| `quiet_discovery_reveal_flow` | quiet discovery, child adventure, small robot/creature reveal, mystery object | clue, decision, approach, reveal, recognition, careful contact | avoid under-specifying object identity or emotional payoff |
| `3x4_product_board` | skincare, product use, beauty, fashion, tactile ads | product continuity, hand interaction, macro detail, final packshot | avoid product scale or label drift |
| `12_panel_rhythm_sheet` | dance, singing, sport phrase, music-video beat | fast snapshots, beat logic, technique progression | avoid full-length action per panel |
| `16_panel_action_sheet` | sakuga action, martial arts, dense technique showcase | choreography flow, motion escalation, in-between permission | avoid unreadable chaos and random camera invention |
| `transformation_strip_or_grid` | ribbon, fabric, magic, product assembly, costume change | transformation stages, trigger actions, final reveal | avoid static center pose or autonomous prop movement |

Prompt cue:

```text
Use a [layout_pattern] because this scene is controlled primarily by [action geography / emotional flow / product continuity / transformation stages / rhythm escalation].
```

Layout adherence rule:

When a pack declares a numeric grid layout, the generated storyboard control should visibly match that grid. For example, `3x4_product_board` means 12 visible cells, not merely 5 large panels with unused whitespace. If the creative plan truly has 5 Beats, fill the remaining cells with repeated continuity locks, macro inserts, hold frames, or "same product" verification views; otherwise change the manifest to a non-numeric 5-beat board description.

## Fan / Weapon-Prop Kata

Panel tendency: 12 panels for a compact readable kata; 16 panels when the appeal depends on fast snapshots, technique escalation, multiple prop/fabric paths, or a controlled final stop.

Control priority:

- rhythm-performance control for timing, pauses, acceleration, and final payoff
- body-driven transformation for fan, blade, sleeve, ribbon, cloak, or fabric path logic
- object lock / character reference when the weapon, fan, costume, hair, or sleeve volume must remain stable

Camera grammar:

- wide readability before impact frames
- low-angle hero frames for burst or extension
- orbit or spinning follow camera only when it clarifies rotation
- overhead panels for circular path geometry
- insert close-ups for fan ribs, grip, blade reveal, foot plant, or tactile timing
- locked final frame when the ending must feel steady

Motion rhythm:

- hook -> controlled anticipation -> first burst -> spin/level change -> signature reveal or path crossing -> suspension -> peak combo -> landing/recovery -> final statement
- for a steady ending, decelerate over the final 2-3 panels instead of ending in unresolved forward motion

Annotation priorities:

- body path / weight transfer
- fan, weapon, sleeve, or fabric path
- camera path
- timing pause or acceleration
- impact, pressure wave, debris, bell/banner/water reaction

Failure guards:

- avoid pretty dance poses without martial intent
- avoid autonomous floating props unless the prompt asks for magic autonomy
- avoid over-polished concept art when the board is meant for video control
- avoid effects that hide body line, fan silhouette, grip, or footwork
- avoid continuing motion after a requested stable final hold

## Contemporary Dance

Panel tendency: 8-20 panels for a full phrase; 12 panels is a strong default for intense performance.

Camera grammar:

- full-body wide shots to preserve choreography
- low/side angles for weight and extension
- overhead for floorwork and body geometry
- occasional close-ups for face, hand, torso, breath, or vocal strain
- camera behaves like a partner, not a spectator

Motion rhythm:

- breath-led phrases
- sustained hold -> acceleration -> release
- floorwork -> rise -> collapse
- match cuts across gesture or body line

Environment progression:

- keep environment minimal unless location transformation matters
- use smoke, fabric, harsh light beams, wet floor reflections, negative space

Annotation priorities:

- body orientation
- floor path
- weight shift
- camera-dancer distance
- voice/emotion marks
- edit points on gesture

Failure guards:

- avoid cropped limbs unless close-up is intentional
- avoid static standing poses
- avoid music-video overcutting that hides choreography
- avoid camera motion fighting body motion

Prompt cue:

```text
Every panel must contain visible body momentum: floor slide, crawl transition, hair whip, balance shift, collapse, rebound, or sculptural pose under pressure.
```

## Chase Comedy

Panel tendency: 12 panels for a compact 15-30 second gag; 12-30 for longer escalation.

Camera grammar:

- wide readable staging for geography
- lateral tracking for screen direction
- whip pans and snap zooms for surprise
- low-angle tracking for speed
- locked-off frames for punchlines
- overhead shots to clarify obstacle layout

Motion rhythm:

- setup -> acceleration -> near-miss -> escalation -> reversal -> pause -> payoff -> final tag
- repeated pattern with escalating absurdity

Environment progression:

- ordinary room becomes obstacle course
- mess/destruction must progress panel by panel
- preserve geography: entrances, exits, hiding place, obstacle positions

Annotation priorities:

- chase direction
- entrances/exits
- obstacle positions
- exact punchline frame
- reaction beat
- debris/flying object paths

Failure guards:

- avoid geography collapse and teleporting characters
- avoid revealing the gag too early
- avoid excessive motion blur that hides action
- avoid generic action tone; keep comedic timing

Prompt cue:

```text
Each panel escalates the chase and the room damage: scatter, skid, rip, topple, smash, collapse, freeze, final tiny victory.
```

## Disaster Rescue

Panel tendency: 8-15 panels for a short rescue beat; 20-50 for a major sequence.

Camera grammar:

- establishing scale shots
- handheld urgency
- POV inserts
- overhead geography
- close-ups for human stakes
- VFX plates for fire, water, debris, smoke

Motion rhythm:

- chaos burst -> assessment -> decision -> controlled action -> complication -> extraction
- countdown logic when danger escalates

Environment progression:

- safe zone -> hazard boundary -> trapped/victim location -> extraction route
- cause-effect continuity for debris, flood, fire, smoke, collapse

Annotation priorities:

- hazard map
- rescuer/victim positions
- safety equipment
- light/signal direction
- debris/fire/water behavior
- VFX layer notes

Failure guards:

- avoid physics violations
- avoid unreadable rescue plan
- avoid spectacle overpowering the human objective
- avoid inconsistent injuries or unsafe behavior shown as solution

## Investigation / Noir

Panel tendency: 10-25 panels per scene; fewer panels can work when composition is dense.

Camera grammar:

- low-key lighting
- hard shadows
- silhouettes
- venetian-blind patterns
- mirrors/reflections
- foreground obstruction
- slow pushes
- Dutch angle only for instability

Motion rhythm:

- slow discovery
- clue insert -> reaction -> concealment -> reversal
- pressure builds through framing and light, not speed

Environment progression:

- exterior rain/street -> interior office/bar/warehouse
- space feels more constricted as truth narrows

Annotation priorities:

- light source direction
- shadow shape
- clue placement
- gaze lines
- prop continuity
- moral/psychological framing

Failure guards:

- avoid generic dark detective cliche
- avoid muddy illegible blacks
- avoid unreadable clue text
- avoid noir style without investigative causality

## Product Commercial

Panel tendency: 6-12 panels for 15-30 seconds; 10-18 for 60 seconds.

Camera grammar:

- hook shot
- problem/use-case shot
- hero product
- macro detail
- product-in-hand
- transformation/result
- packshot or CTA

Motion rhythm:

- crisp and efficient
- every shot sells one claim
- music/VO timing often matters

Environment progression:

- lifestyle problem space -> clean product world -> branded end frame

Annotation priorities:

- brand/product accuracy
- label orientation
- material finish
- hand interaction
- benefit text
- legal/supers/CTA frame

Failure guards:

- avoid wrong logo or unreadable label
- avoid invented features
- avoid product scale changes
- avoid hand deformation

## Music Video

Panel tendency: 20-60 key panels for a full song; not every cut needs a panel.

Camera grammar:

- performance master
- stylized close-ups
- rhythmic camera moves
- choreographed transitions
- surreal inserts
- repeated visual motifs

Motion rhythm:

- song-structure driven
- verse restraint -> pre-chorus build -> chorus release -> bridge rupture

Environment progression:

- performance world
- narrative world
- abstract motif world
- chorus returns to recognizable visual anchor

Annotation priorities:

- timestamp
- lyric cue without quoting long lyrics
- beat hit
- performance/narrative layer
- transition type
- wardrobe/look continuity

Failure guards:

- avoid performer identity drift
- avoid visuals detached from song sections
- avoid inconsistent wardrobe
- avoid overbusy camera

## Rhythm Performance / Sport Performance

Use for movement whose appeal depends on visible rhythm and technical escalation: jump rope, skating, parkour, gymnastics, martial arts forms, boxing footwork, drumming, runway, street dance, stage acts, and sport-performance music videos.

Panel tendency:

- 12 panels for a compact readable phrase.
- 16 panels for a dense 10-20 second showcase.
- 16-24 panels when the subject has many named techniques or a full music phrase.
- Do not default to 6-8 panels unless the user asks for a minimal board.

Camera grammar:

- title strip with performer name, track/energy cue, and optional BPM.
- full-body wide and low shots for technique readability.
- top-down or bird's-eye shots for graphic paths, footwork, rope circles, floor patterns, or formation geometry.
- low-angle push-ins for power beats.
- close inserts for percussion points: feet, hands, prop strike, grip, breath, sweat, dust.
- orbit, whip pan, fisheye, ultra-wide, or 360-degree notes at peak energy.
- final hero wide, god shot, or locked-off held pose for payoff.

Motion rhythm:

- anticipation -> first beat -> acceleration -> signature trick -> suspended pause -> combo escalation -> speed ramp -> impact/release -> final held statement.
- use timestamps, beat counts, BPM, or music-section labels when the board is music-led.
- alternate continuous motion panels with one or two readable impact/hold panels.

Motif system:

- identify the dominant moving shape: rope arc, wheel circle, footwork grid, baton trail, glove line, drumstick slash, fabric wave.
- repeat it as a graphic pattern across panels.
- escalate it from simple path to complex figure: line -> circle -> spiral -> infinity loop -> energy ring -> final emblem.
- make the motif drive composition, camera path, and editing rhythm.

Annotation priorities:

- timestamp or beat count.
- named technique/action phrase.
- subject path and prop path.
- camera direction and lens note.
- impact/percussion point.
- short expressive director note.
- final statement or emotional tag.

Failure guards:

- avoid generic athletic poses without named technique.
- avoid cropping limbs during technique readability beats.
- avoid treating the prop as a small accessory when it should define the rhythm.
- avoid flat tempo; build toward a peak and a held payoff.
- avoid dense readable text; use short handwritten notes only.
- avoid making the board a poster instead of a sequence.

Prompt cue:

```text
Make rhythm visible. The repeated moving motif must organize most panels: it begins as a simple beat line, escalates into complex graphic paths, peaks as a full-frame energy structure, and resolves into the final held pose.
```

Example jump-rope technique escalation:

```text
ready stance -> first side swing -> fast alternating steps -> double-under -> cross and figure-eight -> close foot percussion -> orbiting flow state -> suspended air pause -> triple-under combo -> fisheye lean into beat -> speed ramp -> ground-break impact -> hero build -> ultra-wide 360 energy ring -> god-shot final statement
```

15s / 12-16 panel compression:

- P01-P02: 0.0-2.0s, immediate setup and launch.
- P03-P06: 2.0-6.0s, technique vocabulary and rhythm establishment.
- P07-P10: 6.0-10.0s, fast motion snapshots and escalation.
- P11-P14: 10.0-13.5s, peak combo, impact, or visual maximum.
- P15-P16: 13.5-15.0s, slow-motion catch and final held pose.

These panels are compressed action snapshots, not full-length actions. Do not extend a user-requested 15-second video to 30 seconds just because the board has 12 or 16 panels.

## Trailer / Invasion / Disaster Escalation

Use `4x3_trailer_grid` when the request contains trailer, teaser, invasion, disaster, city collapse, horror reveal, large-scale escalation, or a final suspense hook.

Default panel map:

- P01-P02: immediate danger hook.
- P03-P04: scale and information expansion.
- P05-P07: protagonist route and main reveal.
- P08-P10: escalation, complication, or near capture.
- P11: peak, false safety, or moment of irreversible danger.
- P12: aftermath, unresolved reveal, or final held suspense.

Do not compress these topics into a 6-panel synopsis unless the user explicitly asks for a minimal board.

## Quiet Discovery / Object Reveal

Use `quiet_discovery_reveal_flow` for a short scene where a subject discovers a mysterious object, small robot, pet-like creature, artifact, or quiet supernatural clue.

Default panel map:

- P01: establish place and subject isolation.
- P02: clue appears and subject notices.
- P03: subject chooses to approach or interacts with an obstruction.
- P04: object or creature reveal.
- P05: mutual recognition, eye contact, or threat-softening beat.
- P06: careful contact or final held payoff.
- P07 optional: aftermath glow, emotional tag, or unresolved signal.

Pair this layout with `emotion_lite` and `object_lock` when the payoff depends on expression and a recurring small object.

## Public Service Promo

Panel tendency: 6-15 panels for 15-60 seconds.

Camera grammar:

- clear human scenario
- simple symbolic image
- testimonial or dramatized consequence
- direct CTA frame

Motion rhythm:

- problem -> empathy -> fact/consequence -> action
- clarity over flourish

Environment progression:

- everyday setting -> consequence/solution setting

Annotation priorities:

- message hierarchy
- audience
- statistic/source note
- readable CTA
- inclusive casting
- safe behavior

Failure guards:

- avoid unreadable text
- avoid melodrama or ad gloss
- avoid unclear action
- avoid stereotypes

## AI Video Failure Guards

Current image/video models often struggle with:

- temporal consistency
- character identity over many panels
- coherent physics
- long-range control
- exact camera precision
- text rendering
- multi-shot continuity

Therefore, storyboard and video prompts should explicitly preserve:

- character identity
- costume/body design
- environment layout
- screen direction
- cause-effect progression
- start and end pose for each high-motion segment
