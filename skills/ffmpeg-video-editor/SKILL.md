---
name: ffmpeg-video-editor
description: FFmpeg 视频与音频自动化预处理 Skill。支持无损静音擦除 (Silence Removal)、16:9 画幅转 9:16 居中竖屏裁切、16kHz 单声道 WAV 音轨提取与关键帧抽样。
---

# 🎬 FFmpeg 视频/音频自动化预处理 Skill

本 Skill 为 Antigravity 提供本地音视频底层极速预处理能力，配合 Python 自动化工具链使用。

---

## 🛠️ 核心功能与调用方式

系统关联脚本路径: `C:\Users\trees\Documents\antigravity\dazzling-noether\ffmpeg_preprocessor.py`

### 1. 提取 16kHz WAV 音轨 (Whisper 极速识别)
```python
from ffmpeg_preprocessor import extract_audio_wav
wav_path = extract_audio_wav("input.mp4", "output.wav")
```

### 2. 无损静音擦除 (零废音法则)
```python
from ffmpeg_preprocessor import remove_silence
clean_mp4 = remove_silence("input.mp4", "output_nosilence.mp4", noise_db=-35.0, min_duration=0.4)
```

### 3. 画幅适配 (16:9 横屏转 9:16 竖屏居中)
```python
from ffmpeg_preprocessor import crop_to_vertical_916
vertical_mp4 = crop_to_vertical_916("input_horizontal.mp4", "output_916.mp4")
```

### 4. 关键帧极速抽样 (每秒 1 帧图片)
```python
from ffmpeg_preprocessor import sample_keyframes
frames = sample_keyframes("input.mp4", "output_frames_dir", fps=1.0)
```
