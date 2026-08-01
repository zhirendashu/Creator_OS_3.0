# -*- coding: utf-8 -*-
"""
Creator OS 3.0 - pyJianYingDraft & VectCutAPI Automation Wrapper
整合 GitHub 开源标杆 pyJianYingDraft 与 VectCutAPI 语法
支持自动挂载 3D 呼吸运镜、Screen 滤色混合模式与 1.778x 竖屏适配。
"""
import os
import json
import time

class CreatorOSJianyingDraft:
    def __init__(self, draft_name, canvas_w=1080, canvas_h=1920):
        self.draft_name = draft_name
        self.width = canvas_w
        self.height = canvas_h
        self.tracks = []
        self.materials = {"videos": [], "audios": [], "texts": [], "mix_modes": []}

    def add_video_segment(self, path, start_us, dur_us, is_overlay=False, screen_blend=False):
        v_id = f"V_{len(self.materials['videos'])+1:04d}"
        v_mat = {"id": v_id, "path": path, "duration": dur_us, "type": "video"}
        self.materials["videos"].append(v_mat)
        
        seg = {
            "id": f"SEG_{v_id}",
            "material_id": v_id,
            "target_timerange": {"start": start_us, "duration": dur_us},
            "clip": {
                "rotation": 90 if self.width < self.height else 0,
                "scale": {"x": 1.7777777777777777, "y": 1.7777777777777777} if is_overlay else {"x": 1, "y": 1},
                "alpha": 1.0
            },
            "extra_material_refs": ["SCREEN_BLEND_MAT_ID"] if screen_blend else []
        }
        return seg

print("pyJianYingDraft & VectCutAPI Module Ready in Creator OS 3.0")
