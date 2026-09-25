---
name: shorts-clipper
description: 长视频切短片与黄金高光提取 Skill。分析音视频 Transcript 逐字稿，提取黄金前 3 秒钩子段落与高光台词区间，自动归档至工程 `01_黄金高光` 目录。
---

# ✂️ Shorts 黄金高光自动切片 Skill v2.0

本 Skill 为 Antigravity 提供短视频黄金高光提词与自动切片的智能提取能力。

---

## 🛠️ 核心功能与调用方式

系统关联脚本路径: `C:\Users\trees\Documents\antigravity\dazzling-noether\shorts_clipper.py`

---

### 1. 黄金前 3 秒 Hook 强度评分算法

```python
from shorts_clipper import analyze_transcript_highlights

highlights = analyze_transcript_highlights(parsed_srt_segments)
# 返回: List[HighlightSegment]
# 每个 HighlightSegment 包含:
#   .start_time (float)      # 片段开始时间秒
#   .end_time (float)        # 片段结束时间秒
#   .text (str)              # 片段口播内容
#   .hook_score (float)      # 0~100 钩子强度分
#   .highlight_score (float) # 0~100 高光价值分
```

#### Hook 强度打分定义

| 维度 | 权重 | 高分辨别特征 |
|:---|:---:|:---|
| 情绪张力 | 30% | 包含强情绪动词：什么、为什么、没想到、吸引、加满 |
| 信息密度 | 25% | 单句中出现 2+ 个实体名词（品牌/型号/参数/类型） |
| 语速节奏 | 20% | 每秒 4~6 字，节奏有张弛感 |
| 问题结构 | 15% | 包含反问句或悬念语气 |
| 高光关键词 | 10% | 包含高光词库关键词 |

```python
HOOK_HIGH_SCORE_SIGNALS = {
    # 情绪动词（+20~30 分）
    "什么": 20, "为什么": 20, "没想到": 25, "意外": 25,
    "弹到": 20, "没想过": 25, "这个": 15,
    # 情绪形容（+15~25 分）
    "吸引": 15, "难以置信": 20, "剩饰": 20,
    "老实": 15, "真的": 15, "有点": 15,
    # 反差模式（+25 分）
    "不是...而是": 25, "但是": 15, "却": 15,
}
```

---

### 2. 自动切出高光片段并建库归档

```python
from shorts_clipper import prepare_project_golden_directory

# 自动提取前 3 大黄金高光片段，创建并归档至 02_黄金高光 目录
golden_dir = prepare_project_golden_directory(
    project_dir="F:/视频保存/产品名/",
    video_path="F:/视频保存/产品名/01_素材/原始视频.MOV",
    srt_segments=highlights,
    top_n=3,               # 提取前 3 个高光片段
    extend_seconds=1.0     # 干婐头尾各延伸 1 秒
)
print(f"黄金高光已归档至: {golden_dir}")
# 输出目录结构:
# F:/视频保存/产品名/02_黄金高光/
# │
# ├── highlight_01_score94.mp4  (高光片段 + 分数命名)
# ├── highlight_02_score87.mp4
# ├── highlight_03_score79.mp4
# └── highlights_report.json    (完整打分报告)
```

---

### 3. 黄金前 3 秒钩子判断标准

**构成强勁钩子的必要元素（必须同时满足 3 项以上）：**

1. **强视觉冲击** — 镜头具有强运动感或引尼层次局部
2. **情绪语言直接** — 就是说了出不需要铺垫
3. **信息审查** — 听了这句话不指望下一秒的人会续播看
4. **声音张力** — 语速有变化或音调升起
5. **不完整感** — 这句话不是一个完整句子，观众需要等下一句

**自动判断：**

```python
def is_strong_hook(segment, hook_score_threshold=70):
    """
    判断一个片段是否与强钉子开场
    hook_score >= 70 判定为强钩子★
    hook_score 60~69 判定为中等钩子，可用但建议编辑
    hook_score < 60  判定为弱钩子，不建议作为开场
    """
    return segment.hook_score >= hook_score_threshold
```

---

### 4. 完整工作流示例

```python
from ffmpeg_preprocessor import extract_audio_wav
from auto_subtitle import transcribe_to_srt
from shorts_clipper import analyze_transcript_highlights, prepare_project_golden_directory

video_path = "F:/植人大树/最近项目/IMG_1234.MOV"
project_dir = "F:/视频保存/Sony_ZVE10/"

# Step 1: 提取音频
wav = extract_audio_wav(video_path, "temp_audio.wav")

# Step 2: 识别语音
srt_path = transcribe_to_srt(wav, language="zh", device="cuda")

# Step 3: 分析高光
with open(srt_path) as f:
    segments = parse_srt(f.read())  # 解析 SRT

highlights = analyze_transcript_highlights(segments)

# Step 4: 建库归档
golden_dir = prepare_project_golden_directory(
    project_dir=project_dir,
    video_path=video_path,
    srt_segments=highlights,
    top_n=3
)

# Step 5: 输出建议
for i, seg in enumerate(highlights[:3], 1):
    print(f"黄金高光 {i}: {seg.start_time:.1f}s ~ {seg.end_time:.1f}s")
    print(f"  Hook分: {seg.hook_score:.0f} | 口播: {seg.text[:20]}...")
    print(f"  剪辑建议: 用于 {'Shorts 开场' if i==1 else 'B-Roll 内容'}")
```

---

### 5. 黄金高光归档 SOP

1. 运行分析后，默认将 Top 3 高光片段切割并归档至 `02_黄金高光/`
2. 高光运事序号按分数命名（`highlight_01_score94.mp4`）
3. 最高分片段优先考虑作为 **Shorts 顶集 / 开场 3 秒钩子**
4. 所有片段同时保存 `.json` 打分报告供人工审阅
