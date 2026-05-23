# Methodology

This skill is a storyboard-driven AI video compiler, not a generic prompt improver.

The key distinction:

- Normal AI video workflow: text description -> image -> video -> retry prompt.
- Storyboard-driven workflow: user need -> story energy -> duration and Segment plan -> Beat Storyboard -> annotated motion/camera/composition/light/emotion control -> clean keyframes -> Seedance2 Segment prompts -> editing plan and manifest.

The storyboard is not the final result. It is the control layer.

## Three-Layer Model

Use this hierarchy:

1. Story: the complete creative or narrative intent.
2. Segment: one Seedance2 generation unit, usually 5-15 seconds.
3. Beat: one visual rhythm point inside a Segment, usually represented by one storyboard panel.

One Beat is not necessarily one video. Multiple Beats can become one coherent Segment.

## Annotated vs Clean

Always separate the two image concepts:

- Annotated Storyboard: for review and control. It can include arrows, labels, colored annotation, shot notes, and panel IDs.
- Clean Keyframes: for generation reference. It must not include arrows, text, labels, panel borders, shot numbers, or annotation marks.

Do not feed annotated boards directly as final reference images unless the user explicitly wants annotation artifacts in the generated output.

## Prompt Compilation

Do not write Seedance2 prompts directly from the user's original text. Compile them from:

- Visual Bible
- Segment Plan
- Beat Storyboard Plan
- Clean Keyframe references
- Editing continuity plan

Every Seedance2 prompt should explain that reference frames are ordered visual beats within one coherent segment, not unrelated scenes.

## Practical Default

When the user gives a rough idea, infer what is missing:

- Missing duration: estimate from complexity.
- Missing style: select a fitting camera/visual language.
- Missing panel count: derive from Segment count and Beat density.
- Existing shot script: preserve the user's order and enrich it with motion, camera, light, and emotion.
