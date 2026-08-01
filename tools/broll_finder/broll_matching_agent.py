# -*- coding: utf-8 -*-
"""
Creator OS 3.0 - FireRed-OpenStoryline B-Roll 智能匹配模块
语义化分析口播文本，自动检索 Eagle 206K 素材库 (eagle_material_index.json) 匹配 B-Roll 特写镜头。
"""
import os
import json

def search_broll_for_script(keywords, index_file):
    if not os.path.exists(index_file):
        return []
    with open(index_file, "r", encoding="utf-8") as f:
        idx_data = json.load(f).get("data", {})
    
    videos = idx_data.get("video_overlays", []) + idx_data.get("textures_images", [])
    results = []
    for item in videos:
        name = item.get("name", "").lower()
        tags = " ".join(item.get("tags", [])).lower()
        if any(k.lower() in name or k.lower() in tags for k in keywords):
            results.append(item)
    return results

if __name__ == "__main__":
    print("FireRed-OpenStoryline B-Roll Finder Ready")
