"""
Antigravity 2.0 - 剪映自动剪辑生成器 (Jianying Auto-Draft Generator)
支持通过 CLI 参数或 JSON 配置，自动拼装视频、音频、文字字幕并导出为剪映工程草稿。
"""

import os
import sys
import argparse
import json
import pyJianYingDraft as pjy

# 默认草稿目录
DEFAULT_DRAFT_DIR = os.path.expanduser("~/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft")

def build_draft(draft_name: str, 
                videos: list = None, 
                audios: list = None, 
                texts: list = None, 
                srt_file: str = None,
                width: int = 1080, 
                height: int = 1920, 
                fps: int = 30,
                draft_dir: str = DEFAULT_DRAFT_DIR):
    """
    根据输入的素材列表生成剪映草稿
    """
    if not os.path.exists(draft_dir):
        os.makedirs(draft_dir, exist_ok=True)
        
    draft_folder = pjy.DraftFolder(draft_dir)
    script_proj = draft_folder.create_draft(draft_name, width=width, height=height, fps=fps, allow_replace=True)
    
    current_time_us = 0 # 记录时间线 (微秒)

    # 1. 处理视频素材
    if videos:
        script_proj.append_track(pjy.TrackSpec(pjy.TrackType.video, name="主视频轨"))
        for v in videos:
            path = v.get("path")
            if not os.path.exists(path):
                print(f"[!] 警告：未找到视频文件 {path}，跳过")
                continue
            material = pjy.VideoMaterial(path)
            duration = v.get("duration_us", material.duration) # 若未指定，则默认取视频原时长
            seg = pjy.VideoSegment(material, pjy.Timerange(current_time_us, duration))
            script_proj.add_segment(seg, track="主视频轨")
            current_time_us += duration

    # 2. 处理音频素材
    if audios:
        script_proj.append_track(pjy.TrackSpec(pjy.TrackType.audio, name="音频轨"))
        audio_time_us = 0
        for a in audios:
            path = a.get("path")
            if not os.path.exists(path):
                print(f"[!] 警告：未找到音频文件 {path}，跳过")
                continue
            material = pjy.AudioMaterial(path)
            duration = a.get("duration_us", material.duration)
            seg = pjy.AudioSegment(material, pjy.Timerange(audio_time_us, duration))
            script_proj.add_segment(seg, track="音频轨")
            audio_time_us += duration

    # 3. 处理 SRT 字幕文件导入
    if srt_file and os.path.exists(srt_file):
        script_proj.import_srt(srt_file, track_name="字幕轨")
    elif texts:
        # 手动文本/字幕列表
        script_proj.append_track(pjy.TrackSpec(pjy.TrackType.text, name="字幕轨"))
        for t in texts:
            content = t.get("text", "")
            start = t.get("start_us", 0)
            duration = t.get("duration_us", 3000000)
            seg = pjy.TextSegment(content, pjy.Timerange(start, duration))
            script_proj.add_segment(seg, track="字幕轨")

    # 4. 保存草稿
    script_proj.save()
    target_path = os.path.join(draft_dir, draft_name)
    print(f"[✓] 剪映草稿生成成功: {target_path}")
    return target_path

def main():
    parser = argparse.ArgumentParser(description="Antigravity 2.0 剪映草稿生成工具")
    parser.add_argument("--name", type=str, required=True, help="草稿项目名称")
    parser.add_argument("--config", type=str, help="配置文件 JSON 路径")
    parser.add_argument("--srt", type=str, help="SRT 字幕文件路径")
    parser.add_argument("--width", type=int, default=1080, help="视频帧宽度 (默认1080)")
    parser.add_argument("--height", type=int, default=1920, help="视频帧高度 (默认1920)")

    args = parser.parse_args()

    videos, audios, texts = [], [], []

    if args.config and os.path.exists(args.config):
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            videos = cfg.get("videos", [])
            audios = cfg.get("audios", [])
            texts = cfg.get("texts", [])

    build_draft(
        draft_name=args.name,
        videos=videos,
        audios=audios,
        texts=texts,
        srt_file=args.srt,
        width=args.width,
        height=args.height
    )

if __name__ == "__main__":
    main()
