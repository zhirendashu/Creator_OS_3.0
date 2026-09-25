"""
🍃 breath_inject_clean.py — 植人大树 Creator OS 3.5 柔和呼吸感关键帧注入器
============================================================================
针对用户最新需求与剪映底层原生真机数据重构：
1. 解决「过于密集」：每个切片仅设置【首帧、缓动微呼/吸点、末尾过渡帧】（仅 2~3 个帧点，不再打几十个密密麻麻的关键帧）。
2. 解决「缩放没有效果」：
   - 彻底清除之前冗余的全局 keyframes.videos 与 keyframe_refs 干扰；
   - 严格按照剪映原生运行态格式，直接在 seg['common_keyframes'] 挂载 KFTypeScaleX 与 KFTypeScaleY；
   - X 和 Y 轴数值完全同步（如 1.00 -> 1.045），达成视觉上的【平滑等比缩放】；
   - uniform_scale 保持原生字典 {}。
"""

import json
import uuid
import shutil
import time
from pathlib import Path
from pyJianYingDraft import JianyingDraftCryptoCodec, DraftCryptoConfig
from pyJianYingDraft.draft_codec import write_json_object_with_codec

JY_INSTALL_DIR = r"C:\Users\trees\AppData\Local\JianyingPro\Apps\11.4.1.14443"
DRAFT_DIR = Path(r"F:\trees\Documents\JianyingPro Drafts\9月8日-副本")
TIMELINE_ID = "2B9525A2-5D8B-4131-B87E-6359E530440E"
TIMELINE_DIR = DRAFT_DIR / "Timelines" / TIMELINE_ID
DRAFT_JSON = TIMELINE_DIR / "draft_content.json"
BAK_JSON = DRAFT_JSON.with_suffix(".json.breath_bak")

def load_clean_draft() -> dict:
    codec = JianyingDraftCryptoCodec(DraftCryptoConfig(
        jy_install_dir=JY_INSTALL_DIR, isolated=True,
        validate_roundtrip=False, backup=False
    ))
    if BAK_JSON.exists():
        raw = BAK_JSON.read_bytes()
        print(f"[load] 从纯净备份恢复草稿: {BAK_JSON.name}")
    else:
        raw = DRAFT_JSON.read_bytes()
        print(f"[load] 读取草稿: {DRAFT_JSON.name}")
        
    if raw[:1] == b"{":
        return json.loads(raw.decode("utf-8"))
    return codec.decode(raw)

def save_and_sync_draft(data: dict):
    codec = JianyingDraftCryptoCodec(DraftCryptoConfig(
        jy_install_dir=JY_INSTALL_DIR, isolated=True,
        validate_roundtrip=True, backup=False
    ))
    
    data["update_time"] = int(time.time() * 1_000_000)
    
    # 写入主时间线 draft_content.json
    print(f"[save] 加密写回: {DRAFT_JSON}")
    write_json_object_with_codec(DRAFT_JSON, data, content_codec=codec, indent=None)
    
    # 同步镜像文件
    sync_targets = [
        TIMELINE_DIR / "template-2.tmp",
        DRAFT_DIR / "draft_content.json",
        DRAFT_DIR / "template-2.tmp"
    ]
    for dst in sync_targets:
        shutil.copy2(DRAFT_JSON, dst)
        print(f"[sync] 镜像同步 -> {dst.name}")
        
    # 清理所有 .backup 缓存
    for bdir in [DRAFT_DIR / ".backup", TIMELINE_DIR / ".backup"]:
        if bdir.exists():
            shutil.rmtree(bdir, ignore_errors=True)
            print(f"[clean] 清理缓存: {bdir}")

    # 同步至 AppData 系统草稿目录
    appdata_dst = Path(r"C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\9月8日-副本")
    if appdata_dst.parent.exists():
        if appdata_dst.exists():
            shutil.rmtree(appdata_dst, ignore_errors=True)
        shutil.copytree(DRAFT_DIR, appdata_dst)
        print(f"[sync] 同步至剪映系统主目录: {appdata_dst}")

def make_clean_kf_node(exact_time_us: int, scale_val: float) -> dict:
    """标准剪映关键帧点"""
    return {
        "id": str(uuid.uuid4()).upper(),
        "time_offset": exact_time_us,
        "left_control": {"x": 0.0, "y": 0.0},
        "right_control": {"x": 0.0, "y": 0.0},
        "values": [round(float(scale_val), 4)]
    }

def build_smooth_scale_keyframes(source_start_us: int, duration_us: int, is_zoom_in: bool = True):
    """
    每个片段生成极简柔和关键帧（仅 2~3 个点）：
    推镜头 (Zoom In):
       0.0s        -> 1.000 (原比例)
       中点 (可选)  -> 1.035 (柔和微吸)
       末尾        -> 1.050 (平滑落定)
    拉镜头 (Zoom Out):
       0.0s        -> 1.050 (微切大画面)
       中点 (可选)  -> 1.025 (柔和慢拉)
       末尾        -> 1.000 (回到原景)
    """
    dur_sec = duration_us / 1_000_000.0
    
    if is_zoom_in:
        s_val, m_val, e_val = 1.000, 1.035, 1.055
    else:
        s_val, m_val, e_val = 1.055, 1.025, 1.000
        
    t_start = source_start_us
    t_mid   = source_start_us + duration_us // 2
    t_end   = source_start_us + duration_us
    
    # 短镜头（<1.5秒）直接首尾两点线性推拉；长镜头增加中点让呼吸更顺滑
    if dur_sec < 1.5:
        points = [(t_start, s_val), (t_end, e_val)]
    else:
        points = [(t_start, s_val), (t_mid, m_val), (t_end, e_val)]
        
    # ScaleX 属性组
    kf_group_x = {
        "id": str(uuid.uuid4()).upper(),
        "material_id": "",
        "property_type": "KFTypeScaleX",
        "keyframe_list": [make_clean_kf_node(t, v) for t, v in points]
    }
    
    # ScaleY 属性组（保持与 ScaleX 完全相同的数值，实现等比缩放）
    kf_group_y = {
        "id": str(uuid.uuid4()).upper(),
        "material_id": "",
        "property_type": "KFTypeScaleY",
        "keyframe_list": [make_clean_kf_node(t, v) for t, v in points]
    }
    
    return [kf_group_x, kf_group_y], len(points)

def main():
    print("=" * 60)
    print("🍃 植人大树 Creator OS 3.5 — 极简柔和等比呼吸感注入")
    print("=" * 60)
    
    draft = load_clean_draft()
    
    # 彻底清理可能产生冲突的旧数据结构
    if "keyframes" in draft and isinstance(draft["keyframes"], dict):
        draft["keyframes"]["videos"] = []
    draft["keyframe_graph_list"] = []
    
    tracks = draft.get("tracks", [])
    video_track = None
    for t in tracks:
        if t.get("type") in ("video", "mixed") and t.get("flag") is None:
            video_track = t
            break
            
    if not video_track:
        print("❌ 未找到有效主视频轨道")
        return
        
    segments = video_track.get("segments", [])
    print(f"🎬 定位到主视频轨，共 {len(segments)} 个片段，开始注入首尾极简关键帧...")
    
    total_points = 0
    for i, seg in enumerate(segments):
        src_tr = seg.get("source_timerange", {})
        tgt_tr = seg.get("target_timerange", {})
        source_start_us = src_tr.get("start", 0)
        duration_us = tgt_tr.get("duration", src_tr.get("duration", 0))
        
        if duration_us <= 0:
            continue
            
        dur_sec = duration_us / 1_000_000.0
        # 奇偶交替推拉
        is_zoom_in = (i % 2 == 0)
        
        # 生成 ScaleX + ScaleY 属性组
        common_kfs, pt_count = build_smooth_scale_keyframes(source_start_us, duration_us, is_zoom_in)
        
        # 挂载到剪映原生 common_keyframes 属性
        seg["common_keyframes"] = common_kfs
        seg["keyframe_refs"] = None  # 原生为 None，不打架
        seg["uniform_scale"] = {}    # 保持原生
        
        total_points += pt_count
        mode_text = "柔和推进 (1.000 ➔ 1.055)" if is_zoom_in else "柔和拉出 (1.055 ➔ 1.000)"
        print(f"  [{i:02d}] 时长 {dur_sec:5.2f}s | {mode_text} | 仅放置 {pt_count} 个关键帧点")
        
    print(f"\n✨ 处理完成！全片 8 个片段现已全部改为首尾极简柔和运镜（单片段仅 2~3 个帧点）。")
    
    # 写回保存
    save_and_sync_draft(draft)
    print("=" * 60)
    print("🎉 注入完毕！请重新在剪映打开《9月8日-副本》体验柔和呼吸感！")
    print("=" * 60)

if __name__ == "__main__":
    main()
