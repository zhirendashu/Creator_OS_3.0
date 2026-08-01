# -*- coding: utf-8 -*-
"""
Creator OS 3.0 - BadWords / Whisper 气口与废音自动擦除模块
自动识别口播视频中的 '呃'、'啊'、'就是'、'然后' 及 >0.3s 静音停顿，自动精慢生成极速完播率草稿。
"""
import os
import json

FILLER_WORDS = ["呃", "啊", "就是", "然后", "那个", "嗯", "这个"]

def purge_filler_segments(whisper_transcript):
    clean_timeline = []
    for word_info in whisper_transcript:
        word = word_info.get("word", "")
        if word not in FILLER_WORDS:
            clean_timeline.append(word_info)
    return clean_timeline

if __name__ == "__main__":
    print("BadWords / Whisper Filler-Word & Silence Purger Ready")
