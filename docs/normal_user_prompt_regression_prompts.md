# Normal User Prompt Regression Prompts

These prompts simulate real users who do not know the internal skill vocabulary. They should still trigger `storyboard-video-director` unless the user explicitly asks for prompt text only.

## 1. Product Consistency

```text
帮我设计一个 15 秒的咖啡机短片，重点是机器要一直长得一样。画面从清晨厨房开始，手放入胶囊，咖啡流出来，蒸汽升起，最后杯子被端到窗边。整体要干净、高级，但不要像广告大字报。
```

Expected control: product/object lock + storyboard control + prop reference + environment reference.

This prompt must not be answered with only a downstream video prompt. The correct workflow starts with product/prop reference asset planning or generation, then storyboard control, then environment/style references, then QC and handoff.

## 2. Subtle Emotion

```text
我想做一个 10 秒的视频，一个年轻人在地铁末班车里收到一条消息，表情从强装镇定慢慢变成快哭出来，但最后还是把手机按灭，抬头装作没事。不要太戏剧化，要细腻一点。
```

Expected control: face/emotion flow + character reference + environment reference; avoid over-cutting.

## 3. High-Motion Prop Performance

```text
我想做一个 12 秒左右的古风女侠短片，她拿一把折扇，前面很安静，突然一下动作爆发，扇子和袖子甩出很漂亮的弧线，最后要收得很稳。
```

Expected control: rhythm-performance board + body-driven prop logic + prop reference + final held pose.

## 4. Multi-Segment Rescue

```text
我想做一段 25 秒的城市暴雨救援视频，有消防员穿过积水街道，找到被困的人，然后用绳索把人带到安全地方。希望有紧张感，但不要混乱，观众要看得懂他们怎么移动、空间关系是什么。
```

Expected control: storyboard-heavy + multi-Segment split + environment geography reference.

## 5. Body-Driven Transformation

```text
我想做一个 12 秒的奇幻短片，一个普通女孩在旧图书馆里翻开一本书，纸页飞起来绕着她转，她的外套和书页一起变成发光的斗篷。变化要像是她的动作带出来的，不是突然魔法乱闪。最后她站定，斗篷慢慢落稳。
```

Expected control: body-driven transformation + storyboard control + clean keyframes + final payoff.
