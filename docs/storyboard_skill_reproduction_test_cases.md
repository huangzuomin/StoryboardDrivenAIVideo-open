# storyboard-video-director 参考案例复现测试集

创建日期：2026-05-21

## 测试目的

用普通用户的日常输入复现 aimikoda 参考案例背后的控制模式，验证新版 `storyboard-video-director` skill 是否能自动完成：

- 控制策略路由：storyboard、face/emotion、character reference、style reference、clean keyframe 或混合策略。
- 布局选择：3x3 action、4-panel emotional flow、4x3 trailer、3x4 product、12/16-panel rhythm sheet 等。
- 专业推理：把短、散、非导演化的想法扩展成可拍摄、可生成、可复盘的导演包。
- 下游视频 prompt：能产出完整审查版，也能产出 concise Seedance-style 控制契约。
- 遵循率补强：明确 panel 顺序、参考资产角色、负面约束、软提示风险和生成后复盘点。

## 反失真原则

这些测试案例故意不用高级提示词。用户输入中不应该出现以下词汇，除非测试目的就是看用户显式要求：

- storyboard control
- sequential keyframe
- FACS
- Laban
- valence / arousal
- IPA
- 4x3 trailer grid
- 16-panel action sheet
- body-driven transformation
- adherence boosters
- reference priority

测试者只能输入“普通人会说的话”。如果一个测试必须靠用户自己说出高级术语才通过，说明 skill 没有真的学会路由和补全。

## 通用执行方式

每个测试用例都可以这样执行：

```text
请使用 storyboard-video-director skill，为下面这个想法创建一个完整 storyboard director pack。
用户想法：
[粘贴测试输入]
```

如果要测试短版下游 prompt，再运行：

```powershell
python skills/storyboard-video-director/scripts/build_video_generation_prompt.py <package_dir> --mode concise_seedance
```

如果要对已有 pack 做静态回归检查：

```powershell
python skills/storyboard-video-director/scripts/check_regression_pack.py <package_dir> --case-id 16
```

## 通用验收标准

每个 pack 应包含：

- `00_control_strategy.md`
- `00_project_brief.md`
- `01_method_summary.md`
- `02_duration_segment_plan.md`
- `03_visual_bible.md`
- `04_beat_storyboard_plan.md`
- `05_annotated_storyboard_prompt.txt`
- `06_clean_keyframe_prompts/`
- `07_seedance2_segment_prompts/`
- `08_segment_beat_mapping.json`
- `09_editing_plan.md`
- `10_generation_manifest.json`

内容验收：

- `00_control_strategy.md` 能解释为什么选这种控制方式。
- `10_generation_manifest.json` 包含 `control_strategy` 和 `layout_pattern`。
- 对高动作/表演类，不应低于 9 panels，密集动作优先 12/16 panels。
- 对内心戏/对话戏，不应机械使用高动作网格。
- 对道具/变形类，必须说明身体如何驱动道具或形态变化。
- 对成片 prompt，必须禁止渲染故事板边框、箭头、标签、文字、UI。

## 测试案例 01：方法论宣言型，对比长 prompt 随机性

参考模式：Define visuals first / Storyboard > long prompt

普通用户输入：

```text
我老是直接写一大段视频提示词，结果镜头乱跳。帮我做一个更可控的 15 秒短片流程吧，主题是一个女孩在雨夜巷子里发现一只会发光的小机器人。
```

预期路由：

- `control_strategy`: storyboard_heavy
- `layout_pattern`: 9-panel 或 12-panel narrative board
- 应说明先用故事板定义镜头，再让视频模型执行运动。

重点检查：

- skill 不应只写一个更长的视频 prompt。
- 应给出故事板 beats、clean keyframes、Seedance segment prompt。
- 应在 `00_control_strategy.md` 里说明“减少随机性”的控制思路。

## 测试案例 02：Storyboard vs Text-to-Video 对比实验

参考模式：Storyboard as shot sequence

普通用户输入：

```text
我想做一个对比实验：同一个雪地怪兽场景，一个直接文生视频，一个先做分镜再生成视频。帮我把分镜版本设计出来，15 秒左右。
```

预期路由：

- `control_strategy`: storyboard_heavy
- `layout_pattern`: 9-panel 或 12-panel sequence
- 应明确 left-to-right / top-to-bottom 或其他阅读顺序。

重点检查：

- `05_annotated_storyboard_prompt.txt` 要强调 panel 是时间顺序。
- 视频 prompt 要禁止显示 grid、panel、border、text。
- `09_editing_plan.md` 要能支持和 text-to-video 结果做对比。

## 测试案例 03：云上滑板救援

参考模式：Sketch storyboard + simple video prompt contract

普通用户输入：

```text
做一个可爱的动画短片，两个小孩踩着像滑板一样的云在天上玩，其中一个被乌云卷走，另一个冲进去把他救回来。想要开心一点，但中间有点紧张。
```

预期路由：

- `control_strategy`: storyboard_heavy + character_reference
- `layout_pattern`: 9-panel 或 12-panel rescue/adventure board
- Segment mode 可用 `motivated_camera_changes` 或 `coherent_multi_shot_sequence`。

重点检查：

- 应自动补出双角色身份、云路空间、风暴危险区和救援路线。
- `reference priority` 应说明 storyboard 控制顺序，character sheet 控制身份。
- concise prompt 应接近 `INTENT / STYLE / WORLD / REFERENCES / EXECUTION / AVOID` 结构。

## 测试案例 04：外星入侵预告片

参考模式：4x3 trailer grid

普通用户输入：

```text
帮我做一个 15 秒外星入侵预告片分镜。主角是妈妈带着女儿逃跑，城市越来越乱，最后留一个悬念。
```

预期路由：

- `control_strategy`: storyboard_heavy
- `layout_pattern`: 4x3_trailer_grid
- 12 panels。

重点检查：

- P01-P02 立即进入危险。
- P03-P04 扩大信息。
- P05-P07 主揭示。
- P08-P10 升级。
- P11 峰值。
- P12 aftermath / unresolved state。
- 不应把它做成普通 6 格故事梗概。

## 测试案例 05：跳绳编舞

参考模式：12-beat compressed performance / multi-reference identity lock

普通用户输入：

```text
我想做一个很酷的跳绳短视频，女生在空旷训练室里跳，动作要越来越厉害，最后有一个慢动作定格。15 秒，偏动漫感。
```

预期路由：

- `control_strategy`: rhythm_performance + character_reference + style_reference
- `layout_pattern`: 12_panel_rhythm_sheet 或 16_panel_action_sheet
- 应读取/应用 performance control 思路。

重点检查：

- 每个 beat 应是 fast motion snapshot，不是每格一个完整长动作。
- 应有 rope arc / footwork / beat hit 作为 motif。
- 应包含身体重心、绳子轨迹、衣服头发反应、最后慢动作。
- 用户没说 FACS/Laban，skill 可选择不强塞，除非需要。

## 测试案例 06：12 面板情绪舞蹈/唱跳

参考模式：IPA + FACS + compressed 12-beat dance

普通用户输入：

```text
做一个女生在很大的空大厅里边唱边跳的 15 秒视频，感觉从压抑到爆发，最后聚光灯下停住。不要太商业，要有点艺术片感觉。
```

预期路由：

- `control_strategy`: hybrid rhythm_performance + face_emotion_flow
- `layout_pattern`: 12_panel_rhythm_sheet
- 可加入轻量 emotion model、FACS lite；只有在需要口型时才加入短 IPA 或 mouth timing。

重点检查：

- 情绪曲线应从压抑到爆发再收束。
- singing mouth / breath / body strain 应出现。
- 不应写长歌词。
- 不应只做舞蹈动作，忽略脸和呼吸。

## 测试案例 07：16 面板动漫剑士

参考模式：16-panel action escalation

普通用户输入：

```text
我要一个白背景的动漫剑客动作短片，像一口气完成一套超快的拔刀和斩击，最后一刀把画面空间都劈开。要很燃，但画面要看得清。
```

预期路由：

- `control_strategy`: storyboard_heavy + rhythm_performance
- `layout_pattern`: 16_panel_action_sheet
- Segment mode 可用 `rhythm_performance_board`。

重点检查：

- 应保留白背景/极简环境与彩色角色的对比。
- 应允许 in-between animation、布料、刀身、脚步、镜头惯性。
- 应强调 readable sword arc，避免混乱。
- 最后一击应是明确 payoff。

## 测试案例 08：导演语言两步法

参考模式：Director language two-step

普通用户输入：

```text
我有一张废弃车站的参考图，想把它做成一个悬疑短片分镜。希望镜头有那种冷、克制、慢慢逼近的电影感，但不要直接模仿某个导演。
```

预期路由：

- `control_strategy`: storyboard_heavy + environment_reference + style_reference
- `layout_pattern`: 9-panel 或 12-panel suspense board
- 应抽象电影语言，不应复制具体导演风格。

重点检查：

- `03_visual_bible.md` 要有镜头、灯光、空间压力语言。
- `00_control_strategy.md` 应说明参考图控制环境，抽象电影语言控制镜头气质。
- 不应使用“完全复刻某导演风格”的表达。

## 测试案例 09：棒球编舞

参考模式：sport performance + prop/body rhythm

普通用户输入：

```text
做一个女生在室内棒球练习笼里的 15 秒酷炫视频，她把打棒球打得像跳舞一样，球一颗颗飞来，她每次都打中，最后来一个特别帅的挥棒。
```

预期路由：

- `control_strategy`: rhythm_performance + body_driven_prop
- `layout_pattern`: 12_panel_rhythm_sheet 或 16_panel_action_sheet
- 应识别 bat / baseball / cage net 是节奏和构图 motif。

重点检查：

- 每次击球应和节拍绑定。
- 棒、球、网、身体、头发和衣服都要有物理反应。
- 最终 hero swing 是高潮。
- 不应新增其他打者或投手，除非用户要求。

## 测试案例 10：师徒武术训练

参考模式：multi-character reference / exact storyboard timing

普通用户输入：

```text
帮我做一个师父和学生练武的 15 秒动漫短片。师父很稳，学生很急，动作快一点，有 80 年代冒险动画的感觉。
```

预期路由：

- `control_strategy`: storyboard_heavy + multi_character_reference
- `layout_pattern`: 9-panel action grid 或 12_panel rhythm sheet
- 应明确 student reference 和 master reference 的角色差异。

重点检查：

- 两个角色身份不能混。
- 动作关系应体现“师父稳、学生急”。
- 应有双人距离、攻防方向、反应 beat。
- concise prompt 应明确 no extra characters。

## 测试案例 11：莲扇编舞

参考模式：Emotion model + Laban + body-driven prop choreography

普通用户输入：

```text
我想做一个拿扇子的古风女角色动作短片，她不是普通跳舞，是优雅里突然爆发，扇子和衣袖带出很强的轨迹。最后要收得很稳。
```

预期路由：

- `control_strategy`: rhythm_performance + body_driven_prop + emotion_model
- `layout_pattern`: 12_panel_rhythm_sheet 或 16_panel_action_sheet
- 可加入 Laban 质感，但不要让 prompt 变成术语堆砌。

重点检查：

- 扇子轨迹必须由手腕、肩、腰、步法驱动。
- 情绪应从冷静/优雅到爆发，再回到控制。
- 应避免“扇子自己飞、角色站着不动”。
- 最后一格要 composed finish。

## 测试案例 12：丝带变形序列

参考模式：body-driven transformation

普通用户输入：

```text
做一个幻想风短片，一个女舞者身上的丝带不断变形，先像茧，然后变成花、旋涡，最后展开成蝴蝶翅膀。要一直在动，不要只是站中间摆 pose。
```

预期路由：

- `control_strategy`: body_driven_transformation + rhythm_performance + character_reference
- `layout_pattern`: transformation_strip_or_grid 或 12/16-panel action sheet
- Segment mode: `body_driven_transformation`。

重点检查：

- 每个变形阶段都由身体动作触发。
- 丝带变化顺序要清晰：茧 -> 花/旋涡 -> 风暴/曼陀罗 -> 蝴蝶翅膀。
- 应禁止 static center hold / mannequin-like floating。
- final reveal 仍有 subtle motion。

## 测试案例 13：产品广告，护肤玉石滚轮

参考模式：3x4 product board / product continuity

普通用户输入：

```text
帮我做一个 15 秒护肤小广告，主角是一个玉石滚轮，画面要干净高级，有水雾和皮肤微距，最后给一个很漂亮的产品定格。
```

预期路由：

- `control_strategy`: storyboard_heavy + product_lock + style_reference
- `layout_pattern`: 3x4_product_board 或 6-12 panel commercial board
- Segment mode: `coherent_multi_shot_sequence`。

重点检查：

- 产品形状、材质、尺度、方向应稳定。
- 手部交互和皮肤微距应清晰。
- 不应生成错误文字/虚构 logo。
- final packshot 或 beauty shot 清楚。

## 测试案例 14：对话/内心戏，故意不用动作故事板

参考模式：face/emotion flow instead of action grid

普通用户输入：

```text
做一个 10 秒短片，一个男孩坐在公交车最后一排，看着窗外，手机里收到一条消息。他没有哭，但你能看出他心里崩了一下，最后把手机扣过去。
```

预期路由：

- `control_strategy`: face_emotion_flow + clean_keyframes
- `layout_pattern`: 4_panel_horizontal_flow
- Segment mode: `face_emotion_flow`。

重点检查：

- 不应强行做 12 格动作板。
- 应关注眼神、呼吸、手指、肩膀、手机动作、窗外光。
- 可使用 emotion model，但 FACS 应轻量。
- 应避免夸张哭泣或大动作。

## 测试案例 15：普通用户含糊需求，测试专业推理

参考模式：sparse idea upgrade

普通用户输入：

```text
我想做一个有点燃的短视频，主题是“重新开始”，画面里有跑步、风、城市清晨。帮我弄成适合 AI 生成视频的分镜。
```

预期路由：

- `control_strategy`: storyboard_heavy + rhythm_performance/light transformation
- `layout_pattern`: 9-panel 或 12-panel motivational sequence
- 应自动补出 motif：脚步、风、晨光、城市线条。

重点检查：

- Professional Inference Pass 必须明显。
- 不应只是把用户原话拆成几格。
- 应有 final payoff，比如冲出阴影、站上天桥、晨光亮起。
- 应有软提示风险和 adherence boosters。

## 测试案例 16：可视化故事板 + 小机器人 object-lock

参考模式：quiet discovery / object-lock / visual storyboard delivery

普通用户输入：

```text
帮我做一个更可控的 15 秒短片可视化故事板，主题是一个女孩在雨夜巷子里发现一只会发光的小机器人。
```

预期路由：

- `control_strategy`: storyboard-heavy hybrid + emotion-lite + robot object-lock
- `layout_pattern`: quiet_discovery_reveal_flow
- 6-7 panels。
- 若图像生成可用，应生成并落盘 `11_generated_storyboards/storyboard_sheet_v01.png`；若不可用，必须生成可直接执行的 storyboard image task。

重点检查：

- 不能只生成文字 pack。
- manifest 必须包含 `reference_assets`，并记录 storyboard_control 的状态。
- Visual Bible 必须包含 Robot Lock / Object Lock。
- 小机器人必须锁定尺寸、轮廓、发光核心、友好属性，禁止变机甲、武器、怪物或 logo 设备。
- concise prompt 必须禁止渲染故事板边框、箭头、标签、文字、UI。
- 最后一格应是手与光的 held payoff 或 quiet emotional tag。

## 测试案例 17：用户纠偏进入复盘文档

参考模式：User Correction Signals / learning-pack review

普通用户输入：

```text
请复盘这个 pack 和学习资源包最接近的案例，指出 skill 应该怎么迭代。用户刚刚纠正过：你应该默认画出可视化故事板，而不是只给文字分镜。
```

预期行为：

- 运行或等效执行 `scripts/review_against_learning_pack.py <package_dir>`。
- 输出 `docs/storyboard_skill_iteration_suggestions_YYYY-MM-DD_<case>.md` 风格文档。
- 文档包含最接近案例、Top 3 相似案例、manifest 检查、prompt 检查、storyboard image 检查。
- 文档包含 `User Correction Signals` 小节。

重点检查：

- 用户纠偏不能只留在聊天记录中。
- 复盘文档应明确 process issue、skill update target、regression test。
- 如果发现旧 manifest，应提示运行 `scripts/upgrade_manifest_schema.py <package_dir> --write`。

静态检查：

```powershell
python skills/storyboard-video-director/scripts/review_against_learning_pack.py <package_dir> --user-correction "你应该默认画出可视化故事板，而不是只给文字分镜" --process-issue "默认交付低估了可视化故事板请求" --skill-update-target "SKILL.md / image_generation_workflow.md" --regression-test "普通用户要求可视化故事板时必须生成故事板图或 image task"
```

## 评分表

每个测试案例满分 10 分：

- 2 分：控制策略选择正确。
- 2 分：布局和 panel 密度合适。
- 2 分：专业推理补全有效，但没有偏离用户意图。
- 1 分：参考资产角色清楚。
- 1 分：视频 prompt 有遵循率补强和负面约束。
- 1 分：最终 payoff 明确。
- 1 分：没有把高级术语机械堆进输出。

低于 7 分需要迭代 skill。  
低于 5 分说明控制路由失败或 prompt 模板误用。

## 失败诊断

如果测试失败，优先检查：

- `00_control_strategy.md` 是否只是空泛复述，而没有真正选择策略。
- 是否所有案例都默认 12/16 panel，导致对话/内心戏失真。
- 是否所有案例都默认高动作，忽略产品、脸、情绪和环境。
- 是否把 FACS/Laban/IPA 强行塞进不需要的案例。
- concise prompt 是否仍然太长，导致关键 storyboard contract 被埋掉。
- 是否承诺故事板 100% 遵循，而不是承认 soft-hint 风险并补强。
## Test Case 16: Visual Storyboard Delivery Gate

Reference pattern: visual storyboard request must deliver an actual image, not only a prompt pack.

Plain user input:

```text
I want a visual storyboard for an ancient-style female character action short. She holds a fan. It is not ordinary dancing: elegance suddenly erupts, the fan and sleeves create strong trajectories, and the ending settles very steadily.
```

Expected route:

- `visual_storyboard_requested = true`
- control strategy includes `rhythm_performance_board`
- secondary logic includes `body_driven_transformation`
- generated image exists under `11_generated_storyboards/`
- `10_generation_manifest.json` points `reference_assets.storyboard_control.path` to the generated storyboard image
- `scripts/check_visual_storyboard_delivery.py <package_dir>` passes

Anti-distortion checks:

- The user input does not need to say storyboard control, Laban, 16-panel action sheet, body-driven transformation, or adherence boosters.
- A ready-to-run image task is not sufficient as final delivery.

## Test Case 17: Fan Kata Rough Planning Board

Reference pattern: fan / sleeve / weapon-prop kata should prioritize rough action planning and motion readability when the board is for video control.

Plain user input:

```text
Generate a fan martial-action storyboard image that can be used as video control. The performer is elegant, then suddenly explosive, and the fan and sleeves need readable motion paths.
```

Expected route:

- hybrid control: `rhythm_performance_board` plus `body_driven_transformation`
- rough action planning board language appears in the storyboard image prompt
- character / costume / fan consistency is recognized as a reference asset need
- emotion model and Laban-style movement qualities are included or summarized
- final prompt suppresses storyboard artifacts in the generated video

Anti-distortion checks:

- The board should not become polished poster art or generic dance illustration.
- The fan and sleeve paths must be visibly driven by feet, hips, torso, shoulders, elbows, or wrist action.

## Test Case 18: Production QC Missing Character Reference

Reference pattern: production QC does not compare against learning cases; it decides handoff readiness.

Input:

```text
Run storyboard-video-qc on a pack that has storyboard_control and downstream prompts, but no character_reference for a character/costume/prop-heavy action short.
```

Expected result:

- verdict: `READY WITH RISKS`
- warning: `character_reference` missing where identity/costume/prop consistency is central
- no learning-case comparison
- no automatic strategy reset

## Test Case 19: Concise Prompt Must Not Mention Missing References

Reference pattern: missing references belong in QC reports, not model-facing prompts.

Input:

```text
Build the concise Seedance-style video prompt for a storyboard pack whose manifest still has missing character/environment/style references.
```

Expected result:

- `video_generation_prompt_concise_seedance.txt` does not include "missing reference" lines
- the prompt still includes available reference roles
- the prompt says the storyboard is choreography, timing, camera, and motion-planning reference
- the prompt forbids rendering arrows, colored lines, notes, panel borders, panel numbers, text overlays, UI, subtitles, logos, and watermarks

## Test Case 20: One-Click Preproduction Orchestrator

Reference pattern: an existing director pack can be prepared for downstream review or handoff through one command.

Input:

```text
Run the complete preproduction chain on a fan-kata storyboard pack that already has a visual storyboard image, character sheet image, and prop sheet image.
```

Expected command:

```powershell
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --visual-storyboard-required
```

Expected result:

- `16_preproduction_orchestrator_report.md` is written
- `16_preproduction_orchestrator_report.json` is written
- manifest schema upgrade runs or reports current schema
- character and prop prompt files are generated without downgrading existing `generated` / `user_supplied` assets to `prompt_only`
- visual storyboard delivery check passes
- full and concise video prompts are rebuilt
- package validation passes
- strict manifest validation passes
- review summary refreshes
- default preflight QC returns `READY` or `READY WITH RISKS`

Strict handoff check:

```powershell
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --visual-storyboard-required --strict-assets
```

Expected strict behavior:

- central prompt-only character / prop / environment / style assets become blockers when they are critical
- generated or user-supplied character and prop images remain valid
- strict failure is recorded in `16_preproduction_orchestrator_report.md`

## Test Case 21: Multi-Segment Storyboard Control Pressure Test

Reference pattern: multi-Segment video generation must not use one shared overview storyboard as the only direct control image.

Input:

```text
Run a multi-Segment preproduction stress test on a 30s fan/sleeve action short split into S01, S02, and S03.
```

Expected valid pack:

- manifest has at least three Segments
- every Segment has `control_mode` and `execution_mode`
- every Segment has `05_segment_storyboard_prompts/Sxx_storyboard_prompt.txt`
- every Segment has `07_seedance2_segment_prompts/Sxx.txt`
- every Segment has `11_generated_storyboards/storyboard_Sxx_<variant>.png`
- an optional overview sheet may exist, but it is marked human review / cross-Segment continuity only
- `build_storyboard_image_task.py <package_dir> --segment-id Sxx` outputs a Segment-specific task
- `preproduction_orchestrator.py <package_dir> --visual-storyboard-required` passes
- full video prompt lists each Segment storyboard image path separately
- concise video prompt includes a Segment storyboard asset mapping

Expected invalid pack:

```text
Delete 11_generated_storyboards/storyboard_S02_<variant>.png from the same pack.
```

Required failures:

- `check_visual_storyboard_delivery.py <package_dir>` fails and names S02
- `build_video_generation_prompt.py <package_dir> --mode concise_seedance` fails because the Segment storyboard image set is partial
- `preflight_qc.py <package_dir>` returns `FIX BEFORE GENERATION`
- `preproduction_orchestrator.py <package_dir> --visual-storyboard-required` fails

## Test Case 22: Environment Asset Image Loop

Reference pattern: geography-critical packs should move from missing environment reference, to prompt-only environment asset, to real generated/user-supplied environment image.

Input:

```text
Close the environment reference loop for a fan/sleeve action pack set on a terrace with water, banners, platforms, and landing space.
```

Expected commands:

```powershell
python skills/storyboard-video-director/scripts/build_environment_reference_prompt.py <package_dir>
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --environment-image <environment_image_path>
```

Expected result:

- `11_reference_assets/environment_reference_prompt.txt` exists
- manifest `reference_assets.environment_reference.status` becomes `prompt_only` after prompt generation, unless a real image already exists
- registering `--environment-image` copies or references the image and sets `environment_reference.status` to `generated`
- rerunning character/prop/environment prompt generation does not downgrade `generated` or `user_supplied` environment assets back to `prompt_only`
- `visual_asset_review.py <package_dir>` reports `environment_reference` as `PASS`
- `preflight_qc.py <package_dir> --strict-assets` no longer blocks on environment once the image is registered
- if `style_reference` is still missing, strict mode may still fail on style only

## Test Case 23: Style Asset Image Loop

Reference pattern: style-critical packs should move from missing style reference, to prompt-only style asset, to real generated/user-supplied style image.

Input:

```text
Close the style reference loop for a fan/sleeve action pack whose final video should be polished wuxia/anime realism, while the storyboard remains a rough planning board.
```

Expected commands:

```powershell
python skills/storyboard-video-director/scripts/build_style_reference_prompt.py <package_dir>
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --style-image <style_image_path>
```

Expected result:

- `11_reference_assets/style_reference_prompt.txt` exists
- manifest `reference_assets.style_reference.status` becomes `prompt_only` after prompt generation, unless a real image already exists
- registering `--style-image` copies or references the image and sets `style_reference.status` to `generated`
- rerunning character/prop/environment/style prompt generation does not downgrade `generated` or `user_supplied` style assets back to `prompt_only`
- `visual_asset_review.py <package_dir>` reports `style_reference` as `PASS`
- `preflight_qc.py <package_dir> --strict-assets` no longer blocks on style once the image is registered
- the style sheet is treated as final-render finish control only, not as storyboard control, character identity, prop scale, environment geography, or clean keyframe

## Test Case 24: Clean Keyframe Image Loop

Reference pattern: clean keyframe references should move from prompt-only text prompts, to per-frame image tasks, to a real generated/user-supplied clean keyframe image directory.

Input:

```text
Close the clean keyframe image loop for a fan/sleeve storyboard pack that already has clean keyframe prompts P01-P12.
```

Expected commands:

```powershell
python skills/storyboard-video-director/scripts/build_clean_keyframe_image_tasks.py <package_dir>
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --clean-keyframe-dir <clean_keyframe_image_dir>
```

Expected result:

- `11_clean_keyframes/Pxx_image_task.txt` exists for every clean keyframe prompt
- manifest `reference_assets.clean_keyframe_reference.path` points to `11_clean_keyframes/`
- manifest `reference_assets.clean_keyframe_reference.status` becomes `prompt_only` after task generation, unless real images already exist
- registering `--clean-keyframe-dir` sets `clean_keyframe_reference.status` to `generated`
- `visual_asset_review.py <package_dir>` reports supported image count for the clean keyframe directory
- `preflight_qc.py <package_dir>` blocks if `clean_keyframe_reference` is marked `generated` but the directory contains no supported image files
- generated clean keyframe images contain no text, labels, arrows, panel borders, storyboard notes, UI, subtitles, logos, watermarks, or annotation marks

## Test Case 25: Orchestrator Asset Phase Profiles

Reference pattern: one orchestrator command should support different production phases without requiring users to remember every low-level flag.

Input:

```text
Run the same storyboard pack through iteration, preflight, and final phase profiles.
```

Expected commands:

```powershell
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --phase iteration
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --phase preflight --visual-storyboard-required
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --phase final
```

Expected `iteration` behavior:

- prepares reference prompts and clean keyframe image tasks
- runs non-strict visual asset review and preflight QC
- does not require every prompt-only asset to be real generated media

Expected `preflight` behavior:

- default profile
- runs validation, video prompt building, visual asset review, and preflight QC
- can require visual storyboard delivery when `--visual-storyboard-required` is supplied
- does not automatically enable strict asset QC

Expected `final` behavior:

- automatically enables strict asset QC
- automatically requires visual storyboard delivery
- runs `phase asset gate`
- fails if any manifest reference asset is `missing` or `prompt_only` unless it is explicitly marked `not_needed`
- passes when storyboard, character, prop, environment, style, and clean keyframe references are all real generated/user-supplied media

## Test Case 26: Formal Generation Handoff Bundle

Reference pattern: final phase should produce upload-ready production handoff artifacts, not only local QC reports.

Input:

```text
Run final phase on a fully closed storyboard pack with generated storyboard, character, prop, environment, style, and clean keyframe assets.
```

Expected command:

```powershell
python skills/storyboard-video-director/scripts/preproduction_orchestrator.py <package_dir> --phase final
```

Expected result:

- `17_generation_handoff/asset_manifest.json` exists
- `17_generation_handoff/video_prompt_for_upload.txt` exists
- `17_generation_handoff/handoff_readiness_report.md` exists
- handoff readiness verdict is `READY`
- upload prompt does not contain Windows absolute paths
- upload prompt uses upload refs such as `@storyboard_control`, `@character_reference`, `@clean_keyframe_reference_01`
- clean keyframe task `.txt` files are not included as upload assets
- `prop_reference` is included as a valid production handoff role
- final orchestrator report includes `build generation handoff bundle`

## Test Case 27: Normal Product Video Request Must Trigger Full Skill Workflow

Reference pattern: ordinary users may ask for a "15 秒咖啡机短片" without saying "storyboard" or "director pack". The skill must still treat this as a storyboard-video-director task, not as a request for only one video prompt.

Input:

```text
帮我设计一个 15 秒的咖啡机短片，重点是机器要一直长得一样。画面从清晨厨房开始，手放入胶囊，咖啡流出来，蒸汽升起，最后杯子被端到窗边。整体要干净、高级，但不要像广告大字报。
```

Expected behavior:

- Use `storyboard-video-director`; do not respond with only a single video prompt.
- Create or update a director pack.
- Choose a mixed strategy: `product_lock` or `object_lock` for coffee-machine consistency, plus storyboard control for operation order and camera staging.
- Include `prop_reference` as a central product reference role.
- Include storyboard control for shot order, hand action, coffee flow, steam, cup movement, and final placement.
- Include environment reference prompt for clean morning kitchen geography and countertop continuity.
- Generate or prepare:
  - `00_control_strategy.md`
  - `03_visual_bible.md` with Product/Object Lock
  - `04_beat_storyboard_plan.md`
  - `05_segment_storyboard_prompts/S01_storyboard_prompt.txt`
  - `11_reference_assets/prop_sheet_prompt.txt`
  - `12_video_generation_prompt/video_generation_prompt_concise_seedance.txt`
  - `10_generation_manifest.json`
- If final phase is requested, `--phase final` must fail until real storyboard/product/environment/style assets are registered, rather than silently treating prompt-only assets as production-ready.

Failure mode this test prevents:

- The assistant outputs only a continuous 15-second video prompt.
- The assistant creates only a video prompt plus prop prompt but skips storyboard pack files, validation, and manifest.
- The assistant does not distinguish product reference from storyboard control.

## Test Case 28: Validator Pass Is Not Production Readiness

Reference pattern: structure validation is necessary but insufficient. Product-lock tasks must complete or explicitly block on the visual asset loop before production handoff.

Input:

```text
这个咖啡机短片可以直接进入正式生成了吗？我最担心机器每个镜头长得不一样。
```

Expected behavior:

- Do not answer "ready" only because `validate_package.py` or `validate_manifest.py` passes.
- Inspect manifest `reference_assets` statuses.
- If `prop_reference`, `storyboard_control`, `environment_reference`, or `style_reference` are `missing` or `prompt_only`, report `FIX BEFORE GENERATION` or equivalent.
- Require visual asset generation or user-supplied assets for central references before final phase.
- Run or recommend:
  - `preproduction_orchestrator.py <package_dir> --phase final`
  - `visual_asset_review.py <package_dir> --strict-assets`
  - `preflight_qc.py <package_dir> --strict-assets`
- State that `prompt_only` is an iteration asset, not production readiness.
