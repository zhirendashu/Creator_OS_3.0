---
name: jianying-auto-editor
description: 剪映（JianYing Pro）自动剪辑与花字预设技能。支持自动合成视频、音频、ASMR音效轨、3D微旋转运镜与5大昆丁/科技时尚风文字预设模板。
---

# 剪映（JianYing Pro）自动剪辑与预设 Skill

本 Skill 为 Antigravity 2.0 提供操作“剪映专业版”（JianYing Pro）自动生成与管理草稿工程的核心能力。

---

## 核心配置与路径信息

- **系统 Python 环境**: Python 3.11 (`C:\Users\trees\AppData\Local\Programs\Python\Python311\python.exe`)
- **核心依赖库**: `pyJianYingDraft` (已安装)
- **剪映草稿存储目录**: 
  - 系统默认: `C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\`
  - 工作区文档: `F:\trees\Documents\JianyingPro Drafts\`

---

## 5 大内置文本/标题变体预设 (Text Preset Matrix)

本 Skill 内置了 5 种专门契合“开箱+产品介绍+IG发布+科技时尚+昆丁美学”的调色与字效变体：

| 变体编码 | 预设名称 | 适用场景 | 颜色搭配 (Face + Shadow/Border) |
| :--- | :--- | :--- | :--- |
| `01_pulp_amber` | **昆丁复古橙红** | 视频大片头、强视觉开场 Hook | 暖金橙色 `#FF8C00` + 纯血红硬影 `#D31400` |
| `02_tech_silver` | **极简科技纯银** | 高端数码展示、苹果冷光风 | 纯银晶白 `#F2F4F8` + 科技发光蓝 `#0066FF` |
| `03_champagne_gold` | **奢华香槟金** | 质感配件、限定版标语、品牌LOGO | 香槟软金 `#F3E5AB` + 沉稳炭黑 `#1A1A1A` |
| `04_cyber_neon` | **潮酷霓虹粉紫** | 潮牌联名、IG 潮流短视频、Night Mode | 霓虹玫红 `#FF007F` + 暗夜紫蓝 `#1A0826` |
| `05_clean_subtitle` | **高对比口播字幕**| 通篇解说、细节文字标注、快速阅读 | 纯白 `#FFFFFF` + 纯黑高对比硬边 `#000000` |

---

## 常用预设母版工程
可以直接在剪映客户端中打开以下母版工程，右键保存文字为剪映【我的预设】：
* `《昆丁与科技时尚文本预设大全》` (包含上述 5 大变体的中英文示例)
* `《剪辑母版_IG科技时尚版》` (包含 3D 运镜与 ASMR 音效轨)

---

## ⚠️ 核心避坑与默认自动排查规则 (Default Troubleshooting Rules)

1. **模板占位符导致的“媒体丢失/灰色不可用” (Template Placeholder Pitfall)**:
   - **现象**: 剪映打开修改后的草稿时，视频切片显示灰色无预览，提示素材丢失。
   - **成因**: 母版/模板草稿在导出时，其 `materials.videos` 的 `path` 字段会被替换为 `##_material_placeholder_...##` 或相对路径 `materials/video/...`。
   - **默认排查**: 任何针对草稿的修改脚本，必须在写入前自动遍历 `materials.videos`，检查并按 `material_name` 重新关联映射为真实的物理绝对路径（如 `F:/植人大树/最近項目/IMG_xxxx.MOV`）。

2. **三文件同步写回 (Sync Write Rule)**:
   - 修改 JSON 时，必须同步写回以下三个文件：
     - `Timelines/<Subfolder>/template.json`
     - `Timelines/<Subfolder>/draft_content.json`
     - `draft_content.json` (草稿根目录)

3. **版本时间戳强刷**:
   - 每次写回必须跟进更新 `update_time = int(time.time() * 1000000)`，强制剪映刷新内存缓存。

