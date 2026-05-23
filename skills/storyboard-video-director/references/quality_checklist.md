# Quality Checklist

Before finalizing a director pack, verify:

- Professional inference is explicit when the user prompt is sparse.
- The strongest genre interpretation has been chosen, not merely the most literal one.
- Subject identity is specific enough to be memorable when the genre benefits from a named performer, team, product, place, or role.
- A motif system exists when the subject has a dominant moving shape, prop, environment force, or visual rhythm.
- Story energy is explicit and drives the Segment choices.
- Pacing diagnosis is explicit and drives total duration, Beat duration, Segment count, and panel count.
- Duration is not mechanically derived from panel count or model maximum length.
- Panel count is appropriate for the genre; rhythm showcases and technical performance boards are not under-paneled.
- Visual Bible is stable enough to keep identity, space, style, and light consistent.
- Every Segment is 5-15 seconds.
- Any video over 15 seconds is split into multiple Segments.
- Multi-Segment videos have one Segment-specific storyboard prompt and one Segment-specific storyboard control image per generated Segment.
- Every Segment has 2-5 Beats unless there is a deliberate exception.
- High-motion Segments have reduced Beat density and clear start/end poses.
- Every Beat can be drawn as a visual keyframe.
- Every Beat includes motion, pressure, change, or a decision.
- Annotated Storyboard prompt includes the colored annotation system.
- Annotated Storyboard prompt avoids logos, dense text, photo realism, and extra characters. Timestamps or beat counts appear only when the board mode explicitly needs them.
- Clean Keyframe prompts contain no arrows, annotations, panel labels, borders, shot numbers, subtitles, or logos.
- Seedance2 prompts are per Segment, not per Beat.
- Seedance2 prompts state that reference frames are ordered visual beats, not unrelated scenes.
- Editing plan explains action, light, sound, and rhythm continuity between Segments.
- Manifest is valid JSON and traces prompt files and keyframe prompt files.
- Output pack can be re-run, inspected, and adjusted without reconstructing the whole creative intent.
- Validator pass is not treated as production readiness.
- Product-lock or recurring-object tasks create or register a real `prop_reference` before final handoff.
- Downstream video prompts are built after asset roles are defined, not before the storyboard/reference asset plan.

Storyboard excellence checks:

- Does the board have a clear title, identity, or concept hook?
- Does every panel add new visual information?
- Is there a visible rhythm curve: anticipation, launch, escalation, pause or impact, peak, payoff?
- Is the subject-specific motif present and escalating?
- Are camera angles varied and intentional rather than randomly assorted?
- Are technique names or action phrases specific to the subject?
- Does the final panel feel like a payoff, statement, reveal, or held emotional release?
- Are expressive annotations useful, sparse, and energetic?
- Would the board still feel professional if the user had provided only a five-word idea?
- If the board is for video control, is the visual spectacle still readable enough for generation?

Post-generation storyboard adherence checks:

- Does the final video follow the storyboard panel order?
- Are panels skipped, merged, reordered, or reinterpreted?
- Does each storyboard beat appear as a readable motion snapshot when the prompt requested compressed beats?
- Does the character identity, costume/body design, and silhouette remain stable?
- Does the camera follow the intended framing progression and screen direction?
- Does action progression preserve cause and effect?
- Are annotations, arrows, panel numbers, labels, borders, timing marks, sketch overlays, UI, subtitles, or watermarks absent from the final video?
- Did the model add extra characters, extra action, or unrelated scene changes?
- Does the final pose, reveal, product shot, or emotional state match the planned payoff?
- If adherence failed, was the likely cause soft-hint behavior, overloaded panels, unclear layout, weak reference priority, or an overlong downstream prompt?

Common failure modes:

- Writing only a beautiful visual prompt instead of a controllable Segment plan.
- Treating a normal short-video design request as prompt writing instead of storyboard-first production workflow.
- Running validators and calling the pack complete without visual assets or visual asset QC.
- Building the downstream video prompt before product/storyboard/environment/style assets are planned or registered.
- Following a sparse user prompt too literally and producing a generic board.
- Using generic actions where the subject requires technique vocabulary.
- Treating a dominant prop or movement path as a small accessory instead of the visual motif.
- Treating each storyboard panel as a separate video.
- Feeding annotated storyboard images as clean generation references.
- Feeding one shared multi-Segment storyboard image as the only control reference for multiple video generations.
- Using too many Beats in one Segment.
- Allowing style drift between Visual Bible, keyframes, and video prompts.
- Omitting transition logic between Segments.
- Assuming storyboards are hard constraints instead of soft hints for current video models.
- Sending an overlong downstream prompt that buries the storyboard control contract.
- Using a storyboard layout that does not fit the scene type, such as action-grid grammar for a subtle dialogue scene.
