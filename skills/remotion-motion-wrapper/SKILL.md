---
name: remotion-motion-wrapper
description: Remotion / 动态对比卡与科技花字包装 Skill。支持生成 9:16 黑底高对比度参数对比卡片 MP4 Overlay，自动配合 Screen (滤色) 混合模式注入剪映草稿。
---

> [!WARNING]
> **⚠️ 已降级 (Deprecated)：本 Skill 需要 Node.js 运行时，维护成本高。推荐使用更轻量的替代方案：**
> ```python
> # 推荐替代方案：FFmpeg + Pillow 直接渲染黑底文字视频（无需 Node.js）
> from motion_wrapper import generate_parameter_card_video
> # generate_parameter_card_video() 内部已切换为 Pillow 渲染引擎
> # 如需此功能请直接调用 motion_wrapper.py
> ```
> 仅当需要复杂 React 动画时才考虑启用 Remotion。

# 🎨 Remotion / Motion 动态包装 Skill

本 Skill 为 Antigravity 提供动态科技时尚参数卡片与 Title 包装渲染能力，实现无遮挡极简浮窗效果。

---

## 🛠️ 核心功能与调用方式

系统关联脚本路径: `C:\Users\trees\Documents\antigravity\dazzling-noether\motion_wrapper.py`

### 1. 渲染参数对比卡动态视频
```python
from motion_wrapper import generate_parameter_card_video
card_mp4 = generate_parameter_card_video(
    title="POCKET4 实测参数",
    params=[
        ("材质细节", "航空级铝合金 + 磨砂硅胶"),
        ("画幅兼容", "9:16 竖屏 / 黄金高光防摔")
    ],
    output_mp4="param_card_overlay.mp4",
    duration_sec=3.0
)
```

### 2. 在剪映草稿中挂载 Screen 滤色模式 (黑底变透明)
```python
from auto_edit_engine import AutoEditEngine
engine.apply_screen_blend_if_overlay(segment, "param_card_overlay.mp4")
```
