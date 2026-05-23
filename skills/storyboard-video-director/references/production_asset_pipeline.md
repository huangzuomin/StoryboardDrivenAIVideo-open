# Production Asset Pipeline

Use this reference when a user asks to design a short video, product clip, ad, AI-video-ready plan, visual storyboard, or production handoff. These requests are not prompt-writing tasks by default.

## Core Rule

Do not downgrade a storyboard-driven video request into a single downstream video prompt.

The default deliverable is a production workflow:

```text
director pack
-> reference asset plan
-> visual assets or explicit blocked asset tasks
-> visual asset QC
-> downstream video prompt / generation handoff
```

For ordinary product-lock requests, stopping after "the next step is to generate images" is still an under-delivery. If image generation is available, generate the required central assets in the same turn. If it is unavailable, say exactly that and preserve the prompt/task files as blocked work.

For ordinary high-motion storyboard requests, especially fan, sleeve, ribbon, weapon, dance, fight, parkour, chase, sport, or other rhythm/performance scenes, the real `storyboard_control` image is also a preflight asset. A 12-panel or 16-panel storyboard prompt is not the finished deliverable when the user asks for a storyboard plan to use before video generation.

## Prompt-Only Is Not Production-Ready

`validate_package.py` and `validate_manifest.py` only prove structure and schema. They do not prove that the pack is visually ready.

Never describe a pack as production-ready only because validators pass. Production readiness requires:

- real generated or user-supplied central assets, not only prompts
- strict asset QC for final handoff
- visual asset review
- downstream prompt built from registered assets

## Required Order For Product-Lock Tasks

For product, prop, appliance, vehicle, device, package, or recurring-object videos where the object must remain identical:

```text
1. product / prop reference asset
2. storyboard control image constrained by the product / prop asset
3. environment reference when space, surface, light, or object placement matters
4. style reference when finish, grade, or ad-vs-non-ad tone matters
5. clean keyframes when exact final frames matter
6. visual asset QC
7. downstream video prompt / generation handoff
```

The `prop_reference` must lock:

- silhouette
- scale
- material and color
- buttons, ports, slots, seams, spout, handle, label placement, or other fixed features
- allowed moving parts
- forbidden mutations

## Coffee-Machine Example

For a request like:

```text
Design a 15-second coffee machine clip. The machine must always look the same.
```

The correct workflow is:

```text
prop_reference coffee-machine sheet
-> storyboard_control sheet for morning kitchen, capsule insertion, coffee flow, steam, cup moved to window
-> environment_reference for kitchen/counter/window geography
-> style_reference for clean premium non-slogan look
-> visual asset QC
-> video_generation_prompt / 17_generation_handoff
```

Incorrect workflows:

- Write only a 15-second video prompt.
- Write storyboard/prop/environment prompts but never generate or register the visual assets when production readiness is expected.
- Run schema validation and call the pack done.
- Use the storyboard image as product identity reference.
- Use the prop sheet as storyboard control.

## Visual Asset Generation Expectations

If the user explicitly asks for a visual storyboard, production-ready handoff, generated assets, or says to proceed from planning into assets, generate or register the required visual assets.

For ordinary product-lock or recurring-object video requests, treat real visual assets as a preflight expectation even if the user says "design" rather than "generate images." At minimum, product/object lock requires:

- `prop_reference`: generated or user-supplied image
- `storyboard_control`: generated or user-supplied image

Prompt-only versions of those assets are valid only for an explicitly labeled `text-plan` response or as blocked image-generation tasks.

For ordinary high-motion storyboard requests, preflight requires:

- `storyboard_control`: generated or user-supplied image

Prompt-only storyboard control is valid only for an explicit text-plan or when image generation is truly unavailable/blocked.

Quality floor for generated product-lock assets:

- Do not satisfy `generated` status with low-detail icons, wireframes, placeholder diagrams, or layout sketches unless the pack is explicitly marked as a regression/mock asset test.
- A usable `prop_reference` should show product volume, material finish, scale, fixed features, allowed moving parts, and forbidden mutations clearly enough for a video model to preserve identity.
- A usable `storyboard_control` should honor the declared layout. If the manifest says `3x4_product_board`, the generated storyboard control must be a real 12-cell grid or the manifest/layout must be downgraded to the actual panel format.
- When the generated central assets are schematic but structurally useful, report `READY WITH RISKS` rather than production-ready, and record the quality gap in review notes.

Use the installed `imagegen` skill when the built-in `image_gen` tool is available:

```text
1. Generate prop_reference from the product/prop reference prompt.
2. Save or copy the accepted image under 11_reference_assets/.
3. Update manifest reference_assets.prop_reference to status=generated.
4. Generate storyboard_control from the Segment storyboard prompt, using the prop reference description as the identity lock.
5. Save or copy the accepted image under 11_generated_storyboards/.
6. Update manifest reference_assets.storyboard_control to status=generated.
7. Run validate_expected_delivery.py --profile preflight and visual asset review.
```

If image generation is unavailable, blocked, or not configured, state that blocker explicitly and leave concrete image task files in the correct asset directories. Do not imply the visual asset loop is complete.

Before the final answer for an ordinary short-video or product-clip request, run:

```text
python scripts/validate_expected_delivery.py <package_dir> --profile preflight
```

Use `--profile final` for production handoff. Use `--profile text-plan --explicit-text-only-request` only when the user literally asked for text-only planning, no generated assets, or only a prompt draft. If the check fails, do not use completion language such as "done", "ready", "handoff-ready", or "已设计好" until the missing images are generated/registered or the blocker is clearly reported.

## Minimum Done Definitions

Text-only planning done:

- director pack exists
- manifest validates
- asset prompts/tasks exist
- no claim of production readiness

Preflight done:

- video prompt exists
- QC reports exist
- product/object-lock central assets are real images
- prompt-only non-central assets are allowed only when called out as risks

Final handoff done:

- central assets are `generated` or `user_supplied`
- visual storyboard image exists when required
- strict asset QC passes
- visual asset review passes or records accepted risks
- `17_generation_handoff/` contains upload asset manifest and upload-ref prompt
