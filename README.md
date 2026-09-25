# 🌲 植人大树 Creator OS 3.0

## 七大核心子系统

1. **Creator Brain**：内容策略与创作者人格数据库 (`./prompts/`, `./presets/`)
2. **Jianying AI**：剪映 11.2+ 原生 DLL 加密无损破解 (`JianyingDraftCryptoCodec`)、极简柔和等比呼吸感关键帧注入 (`./jianying/scripts/breath_inject_clean.py`)、3 文件强刷与草稿生成 (`./jianying/`)
3. **Eagle AI**：Eagle 206K 素材库智能检索与 API 控制 (`./eagle/`)
4. **Humanizer**：人格化文字与摄影师视角 (`./skills/zhirendashu-humanizer-v2/`)
5. **Video Lab**：视频分析、B-Roll 检索与调色辅助 (`./tools/`, `./skills/`)
6. **Publishing**：小红书 / B站 发布全链路系统 (`./prompts/xiaohongshu.md`, `./skills/xiaohongshu-skills/`)
7. **Editorial Visual Design**：日系杂志与潮流媒体视觉设计 (`./skills/japanese-editorial-style/`)，沉淀《POPEYE》《GINZA》《Casa BRUTUS》CAP 排版哲学、5 大风格体系、中英日双语字阶比例、留白网格系统与 35mm 胶片/和纸肌理。

---

## 🛠️ 2026 核心底层工程突破 (Core Breakthroughs)
- **剪映 11.2+ 加密草稿无损解密修改**：通过 `JianyingDraftCryptoCodec` 原生调用 `videoeditor.dll`，彻底攻克设备级 AES 加密，告别只能新建空白草稿的限制，实现已有工程原地读取、无损修改与加密写回。
- **极简柔和等比呼吸感规范**：单切片仅设 2~3 个帧点（首尾/中），彻底终结密集刺猬帧；ScaleX/Y 同步驱动，完美兼容剪映原生等比缩放。详见：`./jianying/问题排查_剪映自动剪辑与关键帧.md`。

---

## 📖 核心技术手册与项目全录 (Master Compendium)
- 👉 **底层工程与剪辑技术总览**：[CREATOR_OS_MASTER_COMPENDIUM.md](./CREATOR_OS_MASTER_COMPENDIUM.md)
  （包含所有实操项目清单、加解密演进、关键帧踩坑史、4大集成Skill与防崩溃速查表）
- 👉 **自媒体·时髦有趣实操指南**：[TRENDY_CONTENT_PLAYBOOK.md](./TRENDY_CONTENT_PLAYBOOK.md)
  （涵盖毒舌/松弛人设公式、5大高点击反差标题、短句留白排版、前3秒反向Hook与神评论引导）

---

## 🚀 Codex / Antigravity 工作指令

开启 AI 助手后输入：
> **"加载 Creator_OS_3.0，进入植人大树视频生产模式：读取 jianying-auto-editor、zhirendashu-video、eagle-skill、zhirendashu-humanizer-v2、japanese-editorial-style。"**
