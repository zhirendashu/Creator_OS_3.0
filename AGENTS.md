# 🌲 植人大树 Creator OS 3.5 - AI 自动读取接管规则 (Auto-Boot Directives)

加载 Creator_OS_3.5，进入植人大树视频生产模式。

---

## 📌 自动加载核心技能 (Auto-Loaded Skills)
- **`jianying-auto-editor`**: 剪映草稿 4 级管道（意图识别→素材预检→草稿构建→导出交付）、`Screen` 滤色混合模式、`1.778x` 竖屏放大与 90° 横竖屏自动旋转、jy-draftc 解密支持。
- **`peak-design-tech-typography`**: **Creator OS 3.5 默认首选极简工业科技花字模板**（双行技术编排：`// SPEC XX : TITLE` + 中文卖点，4.8pt 纯白晶体小字 + 52% 半透明圆角炭黑胶囊底衬 + 柔和硬影，`Y = -0.68` 竖屏安全区，渐显/渐隐呼吸动效）。
- **`zhirendashu-video`**: 植人大树美学（昭和感 / 北野武克制 / DV 胶片颗粒 / 3D 呼吸感运镜 / 34.53s 完播率快节奏）。
- **`eagle-skill`**: Eagle 206K 素材库 API 控制 (`X:\私人素材库.library`)，自动调用 4K 胶片漏光、黄闪、VHS 故障与 `Film Sound 1~7` 真实快门音效。
- **`qu-ai-wei`**: 通用中文去 AI 腔第一层（51 类模式 + 语体矩阵）。
- **`zhirendashu-humanizer-v2`**: 植人大树专属语气注入第二层（摄影师第一视角、北野武克制、真实颗粒感）。
- **`japanese-editorial-style`**: 日系杂志与潮流媒体视觉设计（《POPEYE》《GINZA》《Casa BRUTUS》CAP 排版哲学、5 大风格体系、中英日双语字阶比例、留白网格系统与 35mm 胶片和纸肌理）。
- **`xiaohongshu-skills`**: 小红书爆款标题、发布正文、话题标签与高光封面选择器。

---

## 🎯 意图路由表 (Intent Router)

> AI 必须在收到任何用户请求后，**先匹配以下路由表**，再执行对应技能链。路由优先于一切。

| 用户意图信号 | 触发技能链 | 备注 |
|:---|:---|:---|
| 发送**产品名称**（如「Sony ZV-E10」「神牛 ML60」） | → 5 步 SOP 完整闭环 | 见下方 SOP |
| 「帮我写文案 / 口播 / 脚本」 | → `zhirendashu-video` → `qu-ai-wei` → `humanizer-v2` | 串联三层 |
| 「去 AI 味 / 改得自然 / humanize」 | → `qu-ai-wei` → `humanizer-v2` | 串联两层 |
| 「日系风格 / 杂志封面 / POPEYE / 排版」 | → `japanese-editorial-style` | 单层/合成 |
| 「帮我剪辑 / 做视频 / 出草稿」 | → `ffmpeg-video-editor` → `subtitle-generation` → `jianying-auto-editor` | 串联三层 |
| 「提取高光 / 找钩子 / 切短片」 | → `shorts-clipper` → `jianying-auto-editor` | 串联两层 |
| 「做字幕 / 加字幕 / SRT」 | → `subtitle-generation` → `jianying-auto-editor` | 串联两层 |
| 「搜素材 / 找漏光 / 找音效」 | → `eagle-skill` | 单层 |
| 「发小红书 / 写标题 / 写正文」 | → `xiaohongshu-skills` | 单层 |
| 「打分 / 分析视频」 | → `zhirendashu-video` | 单层 |

---

## 🔄 5 步闭环 SOP（产品视频生产标准流程）

当用户发送任意【产品名称】时，AI 必须严格按以下 **5 步闭环** 自动运转：

### 步骤一：联网真实检索
- 自动调用 `search_web` 检索该特定产品的真实参数、材质细节与客观口碑（杜绝虚构）。
- 提取：重量、材质、核心功能、差异化卖点、真实用户评价关键词。

### 步骤二：撰写摄影师口播文案
- 激活 `zhirendashu-video` 美学框架，确定拍摄调性。
- 激活 `qu-ai-wei` 进行通用 AI 腔清洁。
- 激活 `humanizer-v2`，生成 30s 左右、摄影师第一视角、诚实且去 AI 营销腔的口播文案。
- **⚠️ 人工检查点 A**：输出文案后暂停，等待用户确认或修改口播内容。

### 步骤三：生成分镜提词卡 & 建立工程目录
- 输出适合手机浏览的【音画对齐分镜提词卡】（每镜头注明：时长 / 拍摄动作 / 口播台词 / 高光提示）。
- 自动建立本地工程文件夹结构：
  ```
  F:\视频保存\{产品名}\
  ├── 01_素材\       # 原始录音 + 拍摄视频
  ├── 02_黄金高光\   # shorts_clipper 输出的高光片段
  ├── 03_草稿\       # 剪映工程文件
  └── 04_导出\       # 最终成品 MP4
  ```
- 执行命令：`python init_project_workspace.py --product "{产品名}"`

### 步骤四：素材识别与剪映草稿构建

> **执行顺序（严格按序）：**

1. **预检**：`python preflight_check.py`（确认工具链版本，写入 project_config.json）
2. **音频预处理**：
   ```python
   from ffmpeg_preprocessor import extract_audio_wav, remove_silence
   wav_path = extract_audio_wav("录音.mp3", "voice.wav")
   clean_mp4 = remove_silence("原始视频.MOV", "clean.mp4")
   ```
3. **字幕生成**：
   ```python
   from auto_subtitle import transcribe_to_srt
   srt_path = transcribe_to_srt("voice.wav", language="zh", device="cuda")
   ```
4. **Eagle 素材检索**：调用 Eagle API 获取漏光、VHS、Film Sound 实体路径并验证存在。
5. **草稿构建**：`python scan_draft_by_name.py` 确定目标草稿 → 调用 `auto_edit_engine.py` 构建完整草稿（Screen 滤色 + 3D 微呼吸 + 花字预设 + SFX 音效）。
6. **字幕注入**：
   ```python
   from auto_subtitle import inject_subtitles_to_draft
   inject_subtitles_to_draft(script, srt_path, track_name="subtitle", y_position=0.75)
   ```

- **⚠️ 人工检查点 B**：草稿生成后输出完整轨道清单，等待用户在剪映中预览确认。

### 步骤五：小红书爆款发布套件输出
- 自动输出 3 个小红书爆款标题（情绪 + 个人经历 + 摄影元素公式）。
- 自带话题标签正文（#摄影 #开箱 + 产品专属标签）。
- 高光封面建议（指定时间码 + 构图建议）。

---

## 🛠️ AI 默认剪辑与防错法则

1. **零废音法则**：严禁低俗电子合成音 (`whoosh`/`pop`/`snap`)，100% 使用 Eagle 真实快门与开箱摩擦音 (`Film Sound 1~7`, `Paper Shuffle`)。
2. **零遮挡法则**：所有 Overlay 光效与转场必须挂载 `Screen`（滤色）混合模式。
3. **零媒体丢失法则**：所有素材路径必须为实体绝对路径，使用前必须 `os.path.exists()` 验证。
4. **零硬编码模板字幕法则**：彻底禁止使用营销模板字幕。每次收到新产品，必须先调用 `search_web` 检索真实参数。
5. **零越级法则**：严禁跳过人工检查点（A/B）直接输出最终结果。用户确认是质量门控的核心节点。
6. **默认花字模板法则（Peak Design 极简工业科技风）**：所有产品卖点与核心功能标注，一律默认采用 Peak Design 极简工业科技小字（禁止土味大字与过度装饰；双行结构：大写无衬线技术标签 + 摄影师人话卖点，4.8pt 纯白字 + 52% 半透黑圆角底衬，严格锁定在 9:16 安全视线带 `Y = -0.68`，全案挂载 0.3s 渐显/渐隐呼吸动效）。

---

## ✍️ 文字处理分层规则

> **qu-ai-wei 和 humanizer-v2 是串联关系，不是并联替代关系。**

| 层级 | 技能 | 职责 | 适用场景 |
|:---:|:---|:---|:---|
| 第一层 | `qu-ai-wei` | 通用中文去 AI 腔清洁（51 类模式）| 任何中文文字处理场景 |
| 第二层 | `humanizer-v2` | 植人大树专属语气注入（摄影师声口 + 北野武克制）| 口播文案、小红书笔记、产品体验文字 |

**执行规则**：凡涉及植人大树内容创作的文字，必须先过第一层再过第二层。单纯的通用文字清洁只需第一层。

---

## 🛠️ 常见问题排查与避坑准则 (Troubleshooting Directives)

详见完整技术文档：[问题排查_剪映自动剪辑与关键帧.md](file:///C:/Users/trees/Documents/antigravity/dazzling-noether/%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5_%E5%89%AA%E6%98%A0%E8%87%AA%E5%8A%A8%E5%89%AA%E8%BE%91%E4%B8%8E%E5%85%B3%E9%94%AE%E5%B8%A7.md)

1. **剪映 11.2+ 加密草稿无损破解与双向加解密准则**：
   - 剪映 11.2+ 采用本地 DLL 加密。现已集成基于 `aoguai/pyJianYingDraft` 的 `JianyingDraftCryptoCodec`，直接调用剪映原生 `videoeditor.dll`。
   - 读取：`codec.decode(raw_encrypted_bytes)` 获得完整原生明文字典。
   - 写回：`write_json_object_with_codec(path, data, content_codec=codec)` 重新加密写回，实现已有加密草稿无损二次修改。
2. **极简柔和呼吸感与等比缩放准则（拒绝高频密集刺猬帧）**：
   - 严禁在单个切片中铺设几十个高频密集正弦帧点（会导致时间线上密密麻麻如刺猬且容易引起眩晕）。
   - 单切片采用【极简双点/三点】柔和运镜：
     - 短镜头（<1.5s）：仅设首帧（1.000）与尾帧（1.055），极简线性推进/拉出；
     - 长镜头（>2.0s）：仅设首帧（1.000）➔ 中点（1.035 微呼/吸）➔ 尾帧（1.055 慢收），保持 2~3 个帧点即可。
   - 等比缩放支持：在 `seg["common_keyframes"]` 中同时注入 `KFTypeScaleX` 与 `KFTypeScaleY`，两者数值完全一致，`seg["uniform_scale"] = {}` 保持原生，实现完美等比柔和呼吸。
3. **多切片关键帧物理源对齐准则**：
   - 剪映多切片视频的关键帧 `time_offset` 必须绝对对齐源素材起点：`time_offset = source_start_us + local_offset_us`。严禁直接传入片段内的相对 0，否则除首片段外后续所有切片关键帧均会失效。
4. **原生数据层级清洁准则**：
   - 关键帧直接在 `seg["common_keyframes"]` 挂载属性列表；
   - `seg["keyframe_refs"] = None`，全局 `keyframes.videos` 不需乱塞多余引用，防止右侧面板属性互斥屏蔽。

