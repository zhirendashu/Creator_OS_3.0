# -*- coding: utf-8 -*-
"""
植人大树 Creator OS 3.0 - 剪映 3 文件自动化强刷与工程修复脚本
"""
import os
import json
import time

def repair_draft(draft_path, real_media_dir=r"F:\植人大树\最近項目"):
    timelines_dir = os.path.join(draft_path, "Timelines")
    if not os.path.exists(timelines_dir):
        return False
    subfolders = [os.path.join(timelines_dir, d) for d in os.listdir(timelines_dir) if os.path.isdir(os.path.join(timelines_dir, d))]
    if not subfolders:
        return False
    
    tmpl_p = os.path.join(subfolders[0], "template.json")
    timeline_draft = os.path.join(subfolders[0], "draft_content.json")
    root_draft = os.path.join(draft_path, "draft_content.json")

    with open(tmpl_p, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Physical path repair
    for v in data.get("materials", {}).get("videos", []):
        m_name = v.get("material_name", "")
        if "IMG_" in m_name:
            rp = os.path.join(real_media_dir, m_name)
            if os.path.exists(rp):
                v["path"] = rp.replace("\\", "/")

    # Invalidate memory cache
    data["update_time"] = int(time.time() * 1000000)
    json_output = json.dumps(data, ensure_ascii=False, indent=2)

    with open(tmpl_p, "w", encoding="utf-8") as f:
        f.write(json_output)
    with open(timeline_draft, "w", encoding="utf-8") as f:
        f.write(json_output)
    with open(root_draft, "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"🎉 Creator OS 3.0 Jianying Sync Finished: {draft_path}")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        repair_draft(sys.argv[1])
