# Storyboard Driven AI Video

Storyboard Driven AI Video 是一组用于 **故事板驱动 AI 视频生产** 的 Codex skills 和本地脚本。

它的核心不是“直接写一个视频 prompt”，而是先把创意拆成可控的导演包：控制策略、分镜节奏、可视化故事板、角色/道具/环境/风格/干净关键帧参考资产、质检报告，以及最终给视频模型或视频 agent 使用的生产 handoff。

English summary: see [README.en.md](README.en.md).

## 它解决什么问题

AI 视频生成很容易出现这些问题：

- 故事板只变成一张图，没有被当作镜头顺序和动作控制。
- 角色、道具、环境、风格、关键帧参考混在一起，导致模型误解。
- 下游 prompt 太长、太散，或者把本地路径、标注箭头、面板边框带进最终视频。
- 进入昂贵生成前没有严格质检。

这个项目把流程拆成明确节点：先导演规划，再资产闭环，再严格 QC，最后生成可上传的生产 handoff。

## 包含内容

- `storyboard-video-director`：把普通语言视频想法整理成 storyboard-first director pack。
- `storyboard-video-qc`：在视频生成前做生产质检。
- `preproduction_orchestrator.py`：一键跑预生产链路。
- `17_generation_handoff/`：最终给视频平台或视频 agent 使用的上传资产清单和 prompt。
- `examples/fan_kata_minimal/`：可公开的最小回归样例。
- `scripts/run_regression.py`：一键 smoke test。

## 工作流

```mermaid
flowchart LR
  A["用户视频想法"] --> B["导演包 director pack"]
  B --> C["故事板和参考资产"]
  C --> D["预生产 orchestrator"]
  D --> E["strict QC"]
  E --> F["17_generation_handoff"]
  F --> G["视频平台或视频 agent"]
```

## 快速开始

核心脚本只依赖 Python 标准库。`Pillow` 是可选依赖，只用于增强图片尺寸检查。

```powershell
python -m py_compile (Get-ChildItem skills\storyboard-video-director\scripts,skills\storyboard-video-qc\scripts -Filter *.py | ForEach-Object FullName)
python scripts\run_regression.py
```

从普通用户 brief 创建一个第一版导演包：

```powershell
python skills\storyboard-video-director\scripts\create_pack_from_brief.py --brief "我想做一个 12 秒的奇幻短片，一个普通女孩在旧图书馆里翻开一本书，纸页飞起来绕着她转，她的外套和书页一起变成发光的斗篷。变化要像是她的动作带出来的，不是突然魔法乱闪。最后她站定，斗篷慢慢落稳。"
```

然后跑预生产链路：

```powershell
python skills\storyboard-video-director\scripts\preproduction_orchestrator.py production_packs\library_luminous_cloak --phase preflight --visual-storyboard-required
```

`16_user_preview_summary.md` 会生成一个面向用户的紧凑交付摘要，适合作为聊天回复和人工审稿入口。

对公开样例跑 final 生产链路：

```powershell
python skills\storyboard-video-director\scripts\preproduction_orchestrator.py examples\fan_kata_minimal --phase final
```

预期输出：

- `examples/fan_kata_minimal/16_preproduction_orchestrator_report.md`
- `examples/fan_kata_minimal/17_generation_handoff/asset_manifest.json`
- `examples/fan_kata_minimal/17_generation_handoff/video_prompt_for_upload.txt`
- `examples/fan_kata_minimal/17_generation_handoff/handoff_readiness_report.md`

## 安装到 Codex

本仓库里的 skill 副本和 Codex 已安装副本是分开的。要让 Codex 使用当前仓库版本，可以复制：

```powershell
Copy-Item skills\storyboard-video-director $env:USERPROFILE\.codex\skills\storyboard-video-director -Recurse -Force
Copy-Item skills\storyboard-video-qc $env:USERPROFILE\.codex\skills\storyboard-video-qc -Recurse -Force
```

以后改了仓库里的 skill，需要重新复制到 Codex skills 目录。

## 生产 Handoff

当一个 director pack 准备进入真实或昂贵的视频生成时，使用 final phase：

```powershell
python skills\storyboard-video-director\scripts\preproduction_orchestrator.py <pack_dir> --phase final
```

`--phase final` 会自动启用：

- strict asset QC
- 可视化故事板检查
- final asset gate
- visual asset review
- preflight QC
- `17_generation_handoff/` 生产交付包生成

`17_generation_handoff/` 包含：

- `asset_manifest.json`：上传图片文件和 `@upload_ref` 的映射。
- `video_prompt_for_upload.txt`：使用上传引用的最终视频 prompt，不包含本机绝对路径。
- `handoff_readiness_report.md`：是否可进入生成的 readiness 报告。

## 参考资产角色

- `storyboard_control`：控制镜头顺序、动作路径、节奏、镜头、构图。
- `character_reference`：控制角色身份、服装、比例、脸、身体语言。
- `prop_reference`：控制道具轮廓、尺度、材质、运动部件、禁止变形。
- `environment_reference`：控制空间地理、地标、光线、连续性。
- `style_reference`：控制渲染完成度、线条、色彩、镜头质感。
- `clean_keyframe_reference`：控制干净最终画面，不应包含箭头、编号、边框、文字或 UI。

## 仓库发布边界

默认 `.gitignore` 会排除私有学习包、生成包、本地输出和实验目录。公开示例应放在 `examples/` 下，并避免包含不可再分发的图片或视频资产。

正式公开发布前，请参考：

- [docs/publication_manifest.md](docs/publication_manifest.md)
- [docs/open_source_release_checklist.md](docs/open_source_release_checklist.md)

## 版本管理

当前起始版本：

```text
0.1.0-alpha
```

每个 skill 都有独立版本文件：

- `skills/storyboard-video-director/VERSION`
- `skills/storyboard-video-qc/VERSION`

`VERSION` 文件和 director pack 的 `10_generation_manifest.json` 会共同记录版本。`SKILL.md` frontmatter 遵循 Codex skill 规范，不放版本字段。检查版本一致性：

```powershell
python scripts\check_skill_versions.py --package-dir examples\fan_kata_minimal
```

## 当前状态

适合 alpha/beta 阶段使用。核心工作流已经可以脚本化测试，但真实的故事板图像生成、角色资产生成和最终视频生成仍依赖外部图像/视频模型工具。
