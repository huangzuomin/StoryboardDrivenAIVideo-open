# User-Facing Handoff Template

Use this when replying to ordinary users after creating or updating a storyboard-video director pack.

The user usually does not need every internal prompt, schema field, or validation log. Keep the chat response clean and production-oriented, while leaving detailed evidence in files.

## Default Reply Shape

```text
已生成/更新导演包：
<absolute package path>

核心方案：
- 时长 / 画幅：
- 控制策略：
- 故事板布局：
- 必需资产：
- 当前状态：

可查看的主要交付：
- 主故事板图：
- 角色/道具/环境/风格资产：
- 下游视频 prompt：
- 质检报告：

状态判断：
READY / READY WITH RISKS / FIX BEFORE GENERATION
一句话说明原因。
```

## What To Show

- Show the project folder.
- Show or link the main storyboard image when it exists.
- Show or link key reference asset images when they exist.
- Mention the concise downstream video prompt path.
- Mention the QC verdict.
- Mention missing real assets plainly when the pack is not ready.

## What Not To Dump By Default

- Do not paste the full manifest.
- Do not paste every prompt file.
- Do not list every generated internal file unless the user asks.
- Do not claim production readiness from schema validation alone.
- Do not say "next step is generate images" when the user asked for visual storyboard/assets and image generation is available.

## Status Language

- `READY`: real required assets exist, prompt contract is present, and preflight QC has no blockers.
- `READY WITH RISKS`: handoff can be tested, but specific visual or asset gaps remain.
- `FIX BEFORE GENERATION`: do not submit to video generation until blockers are fixed.
- `TEXT PLAN ONLY`: only valid when the user explicitly asked for text-only planning.

## Preview Summary

When available, read `16_user_preview_summary.md` first. It is the compact user-facing index for the pack and should guide the final answer.

