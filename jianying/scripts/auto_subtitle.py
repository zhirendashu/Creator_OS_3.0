"""
🚀 auto_subtitle.py — 口播自动字幕 + 花字注入
================================================
植人大树 Creator OS 3.0 — 自动字幕模块

功能：
  1. 从视频/音频文件中提取中文字幕（faster-whisper / WhisperX）
  2. 生成 SRT 字幕文件
  3. 直接注入剪映草稿字幕轨，支持昆丁花字样式（关键词橙色加粗）

依赖安装：
  pip install faster-whisper

用法：
  from auto_subtitle import transcribe_to_srt, inject_subtitles_to_draft
  
  srt_path = transcribe_to_srt("voiceover.mp4", language="zh")
  inject_subtitles_to_draft(script, srt_path, track_name="subtitle")
"""

from __future__ import annotations
import os
import re

from config import SFX_DIR  # 借用 SFX_DIR 获取项目根路径

# 花字关键词 → 样式映射（昆丁橙红色 + 加粗）
KEYWORD_STYLES: dict[str, dict] = {
    "开箱": {"color": (1.0, 0.55, 0.0), "bold": True},
    "拆包": {"color": (1.0, 0.55, 0.0), "bold": True},
    "实测": {"color": (1.0, 0.55, 0.0), "bold": True},
    "质感": {"color": (1.0, 0.55, 0.0), "bold": True},
    "推荐": {"color": (1.0, 0.55, 0.0), "bold": True},
    "4K":  {"color": (0.3, 0.8, 1.0),  "bold": True},   # 技术词蓝色
    "胶片": {"color": (0.9, 0.8, 0.2), "bold": False},   # 胶片感黄色
}


def transcribe_to_srt(
    video_path: str,
    output_srt: str = None,
    language: str = "zh",
    model_size: str = "large-v3-turbo",
    device: str = "cuda",
    compute_type: str = "float16",
) -> str:
    """
    使用 faster-whisper 将视频/音频转录为 SRT 字幕文件。

    :param video_path:    视频或音频文件路径
    :param output_srt:    输出 SRT 路径（默认与视频同目录同名）
    :param language:      语言代码（"zh" 中文，"en" 英文）
    :param model_size:    Whisper 模型大小（推荐 large-v3-turbo）
    :param device:        "cuda"（GPU）或 "cpu"
    :param compute_type:  "float16"（GPU）或 "int8"（CPU）
    :return: SRT 文件路径
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError(
            "请先安装 faster-whisper：\n"
            "  pip install faster-whisper\n"
            "（GPU 用户还需要安装 CUDA 工具包）"
        )

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"文件不存在：{video_path}")

    if output_srt is None:
        base = os.path.splitext(video_path)[0]
        output_srt = f"{base}.srt"

    print(f"🎙️ 正在识别字幕：{os.path.basename(video_path)}")
    print(f"  模型：{model_size}，语言：{language}，设备：{device}")

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(video_path, language=language)

    lines: list[str] = []
    for i, seg in enumerate(segments, 1):
        start = _format_srt_time(seg.start)
        end   = _format_srt_time(seg.end)
        text  = seg.text.strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")

    srt_content = "\n".join(lines)
    with open(output_srt, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"  ✅ 字幕已生成：{output_srt}（{len(lines)} 条）")
    return output_srt


def parse_srt(srt_path: str) -> list[dict]:
    """
    解析 SRT 字幕文件，返回 [{"index", "start_us", "end_us", "text"}, ...] 列表。
    时间单位：微秒（µs）
    """
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT 文件不存在：{srt_path}")

    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(\d+)\n"                              # 序号
        r"(\d{2}:\d{2}:\d{2},\d{3})"           # 开始时间
        r" --> "
        r"(\d{2}:\d{2}:\d{2},\d{3})\n"         # 结束时间
        r"(.*?)(?=\n\n|\Z)",                    # 字幕文本
        re.DOTALL
    )

    segments = []
    for m in pattern.finditer(content):
        idx, start_str, end_str, text = m.groups()
        segments.append({
            "index":    int(idx),
            "start_us": _srt_time_to_us(start_str),
            "end_us":   _srt_time_to_us(end_str),
            "text":     text.strip().replace("\n", " "),
        })

    return segments


def inject_subtitles_to_draft(
    script,
    srt_path: str,
    track_name: str = "subtitle",
    font_size: float = 7.0,      # 9:16竖屏安全字号（剪映内置单位，7=约等于72sp）
    y_position: float = 0.75,    # 保留参数，实际使用 transform_y=-0.8
) -> int:
    """
    将 SRT 字幕注入到剪映草稿脚本的字幕轨道中。

    :param script:      pyJianYingDraft ScriptFile 对象
    :param srt_path:    SRT 文件路径
    :param track_name:  字幕轨道名称
    :param font_size:   字幕字体大小
    :param y_position:  竖向位置（0.0~1.0，0.75 = 下部 1/4 处）
    :return: 注入的字幕条数
    """
    import pyJianYingDraft as draft
    from pyJianYingDraft import TextSegment, TextStyle, TextBorder, TextShadow, Timerange

    segments = parse_srt(srt_path)
    if not segments:
        print("  ⚠️ SRT 文件为空，跳过字幕注入")
        return 0

    # 昆丁花字基础样式（9:16竖屏适配）
    base_style = TextStyle(
        size=font_size,
        color=(1.0, 1.0, 1.0),   # 白色主体
        bold=False,
        align=1,                  # 居中对齐（0=左 1=中 2=右）
        letter_spacing=0,
        auto_wrapping=True,       # 允许自动换行，防止溢出
        max_line_width=0.88,      # 最大行宽占屏宽 88%，留安全边距
    )
    border = TextBorder(color=(0.0, 0.0, 0.0), width=0.08, alpha=0.95)
    shadow = TextShadow(color=(0.0, 0.0, 0.0), alpha=0.6, diffuse=0.5, distance=4.0, angle=-45.0)

    count = 0
    for seg in segments:
        dur = seg["end_us"] - seg["start_us"]
        if dur <= 0:
            continue

        text_str = seg["text"]
        current_style = base_style

        # 检测关键词施加高光花字样式（昆丁橙/科技蓝/胶片黄）
        for kw, kw_cfg in KEYWORD_STYLES.items():
            if kw in text_str:
                current_style = TextStyle(
                    size=font_size * 1.05,   # 关键词字号微幅放大，不破坏行宽
                    color=kw_cfg.get("color", (1.0, 0.55, 0.0)),
                    bold=kw_cfg.get("bold", True),
                    align=1,
                    letter_spacing=0,
                    auto_wrapping=True,
                    max_line_width=0.88,
                )
                print(f"  ✨ [PresetTypography] 字幕 '{text_str[:12]}...' 已匹配高光关键词 [{kw}]")
                break

        text_seg = TextSegment(
            text_str,
            Timerange(seg["start_us"], dur),
            style=current_style,
            border=border,
            shadow=shadow,
        )
        
        # 9:16 竖屏安全区：transform_y 单位=半个画布高，-0.8 贴近底部字幕区
        # 参考：剪映官方导入字幕默认取 -0.8
        text_seg.clip_settings.transform_y = -0.8
        
        script.add_segment(text_seg, track=track_name)
        count += 1

    print(f"  ✅ 已注入 {count} 条字幕 → 轨道 [{track_name}] (应用昆丁花字排版)")
    return count


# ──────────────────────────────────────────────
# 内部工具函数
# ──────────────────────────────────────────────

def _format_srt_time(seconds: float) -> str:
    """秒 → SRT 时间格式（HH:MM:SS,mmm）"""
    ms  = int((seconds % 1) * 1000)
    sec = int(seconds) % 60
    mn  = int(seconds) // 60 % 60
    hr  = int(seconds) // 3600
    return f"{hr:02d}:{mn:02d}:{sec:02d},{ms:03d}"


def _srt_time_to_us(time_str: str) -> int:
    """SRT 时间格式 → 微秒"""
    h, m, rest = time_str.split(":")
    s, ms = rest.split(",")
    total_sec = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return int(total_sec * 1_000_000)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法：python auto_subtitle.py <视频路径>")
        print("示例：python auto_subtitle.py F:\\植人大树\\最近項目\\IMG_4485.MOV")
        sys.exit(1)

    video = sys.argv[1]
    srt   = transcribe_to_srt(video, language="zh", device="cpu", compute_type="int8")
    parsed = parse_srt(srt)
    print(f"\n前 5 条字幕预览：")
    for s in parsed[:5]:
        print(f"  [{s['start_us']//1_000_000:.2f}s] {s['text']}")
