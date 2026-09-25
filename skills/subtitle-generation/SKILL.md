---
name: subtitle-generation
description: 自动转写与字幕处理 Skill。支持语音识别 (Whisper ASR)、SRT 时间轴精确解析、昆丁橙红/科技蓝花字绑定与 9:16 竖屏安全区自动排版。
---

# 🎙 Subtitle-Generation 自动字幕与花字 Skill v2.0

本 Skill 为 Antigravity 提供从语音/视频识别字幕并自动注入剪映草稿的完整处理能力。

---

## 🛠️ 核心功能与调用方式

系统关联脚本路径: `C:\Users\trees\Documents\antigravity\dazzling-noether\auto_subtitle.py`

---

### 1. 语音转写 SRT 文件

```python
from auto_subtitle import transcribe_to_srt

# 基本用法
srt_path = transcribe_to_srt(
    input_path="voiceover.mp4",  # 支持 .mp4 .mov .wav .mp3 .m4a
    language="zh",               # zh=中文, en=英文, ja=日文
    device="cuda",               # cuda 或 cpu，GPU 速度约3倍
    model_size="large-v3"        # tiny/base/small/medium/large-v3
)
# 输出: voiceover.srt
```

#### 推荐参数配置（中文口播最佳）

```python
srt_path = transcribe_to_srt(
    input_path="voiceover.wav",
    language="zh",
    device="cuda",
    model_size="large-v3",    # 中文必须用 large-v3，识别精度最高
    beam_size=5,              # 识别宽度，默认 5
    word_timestamps=True,     # 开启单词时间戳，字幕更精确
    vad_filter=True           # 过滤无效语音段
)
```

#### SRT 输出示例

```
1
00:00:01,240 --> 00:00:03,680
拿到手第一感觉，比照片重。

2
00:00:03,720 --> 00:00:06,100
这个榫口的阻尼感
有点上头。

3
00:00:06,200 --> 00:00:09,450
胶片颗粒装饭时也很对味。
```

---

### 2. 字幕注入剪映草稿并绑定昆丁花字预设

```python
from auto_subtitle import inject_subtitles_to_draft

# 自动匹配高光词并施加昆丁橙红加粗样式
count = inject_subtitles_to_draft(
    script=jianying_script,           # pyJianYingDraft Script 对象
    srt_path="transcript.srt",
    track_name="subtitle",
    y_position=-0.68,                  # 底部安全区，避开小红书 UI
    preset="05_clean_subtitle"         # 默认高对比口播字幕样式
)
print(f"共注入 {count} 条字幕")
```

#### 高光关键词匹配与昆丁橙红样式

当字幕中出现以下关键词时，自动切换为「昆丁橙红加粗」样式：

```python
HIGHLIGHT_KEYWORDS = [
    # 开箱类
    "折叠", "开箱", "实测", "评测", "拆包",
    # 质感类
    "质感", "手感", "阻尼", "胶片", "胶卷",
    # 技术类
    "4K", "6K", "RAW", "LOG", "全画幅", "光圈",
    # 行为类
    "推荐", "值得", "评分", "聊聊",
    # 情绪类
    "对味", "上头", "排吧", "真的"
]
```

---

### 3. Whisper → SRT → 剪映草稿完整链路示例

```python
"""
完整自动字幕流水线：从视频文件到剪映草稿
"""
from ffmpeg_preprocessor import extract_audio_wav
from auto_subtitle import transcribe_to_srt, inject_subtitles_to_draft
import pyJianYingDraft as pjd

# 步骤 1：提取音频（优化 Whisper 识别速度）
wav_path = extract_audio_wav(
    input_path="F:/植人大树/最近项目/录音.mp3",
    output_path="voice_16k.wav"
)

# 步骤 2：语音识别
print("🎙️ 正在识别语音...")
srt_path = transcribe_to_srt(wav_path, language="zh", device="cuda")
print(f"✅ 字幕已生成: {srt_path}")

# 步骤 3：构建剪映草稿基础结构
script = pjd.Script_file(1080, 1920)  # 9:16 竖屏

# 步骤 4：注入字幕并绑定框架
count = inject_subtitles_to_draft(
    script=script,
    srt_path=srt_path,
    track_name="subtitle",
    y_position=-0.68,
    preset="05_clean_subtitle"
)
print(f"📝 共注入 {count} 条字幕")

# 步骤 5：导出草稿
script.dump(r"C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\我的项目")
print("🎉 草稿已导出，请在剪映中打开预览")
```

---

### 4. 9:16 竖屏安全区布局规范

```
屏幕高度: 1920px
│
├── 顶部状态栏避开区（Y > 0.80）── 禁止放置任何内容
├── 大标题 / Hook 区（Y: 0.55 ~ 0.70）
├── 剪辑主画面区
├── 字幕安全区（Y: -0.60 ~ -0.72）── 口播字幕标准位置
└── 平台 UI 遮挡区（Y < -0.75）── 禁止放置内容
```

| 内容类型 | transform_y 范围 | 字号范围 | 备注 |
|:---|:---:|:---:|:---|
| 大标题 / Hook | 0.55 ~ 0.70 | 80~120pt | 单行上限 7~8 字 |
| 剪辑内容说明 | 0.30 ~ 0.45 | 50~60pt | 可多行 |
| 口播字幕 | -0.60 ~ -0.72 | 40~50pt | 单行上限 14~16 字 |

---

### 5. 字幕轨预设匹配表

| SRT 内容类型 | 推荐预设 | 颜色 | 适用场景 |
|:---|:---|:---|:---|
| 默认口播字幕 | `05_clean_subtitle` | 白字黑边 | 通篇解说 |
| 开场 Hook / 大标题 | `01_pulp_amber` | 暖金橙 + 血红 | 激烈开场 |
| 数码/技术审评 | `02_tech_silver` | 纯银 + 科技蓝 | 相机评测 |
| 高端商品展示 | `03_champagne_gold` | 香槟金 | 开箱产品 |
| 潮牌味道/豪华 | `04_cyber_neon` | 霓虹玫红 + 暗夜紫 | 潮品联名 |
