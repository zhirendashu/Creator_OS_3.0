"""
🎬 optimize_final_draft.py — 针对「9月8日-副本-副本」终案深度精修
===================================================================
1. 【视听 Hook 与音效密度增强】：
   - 在 8.50s (提到"只有27克") 注入 Eagle Film Sound 3 真实轻质快门音
   - 在 18.35s (提到"侧面是控制按钮") 注入 Eagle Camera Shutter 机械按键声
   - 在 45.80s - 49.47s (结尾 The End 复古贴纸留白区) 垫入 MECH VHS 真实胶片机械底噪，完美消除静音尴尬
2. 【长镜头关键帧对称校准】：
   - 消除 Clip 2 和 Clip 6 中 ScaleX / ScaleY 存在的微小非对称插值，回归纯净等比呼吸
3. 【剪映 11.4 格式原生写回与双目录同步】
"""

import json
import uuid
import shutil
import time
from pathlib import Path
from pyJianYingDraft import JianyingDraftCryptoCodec, DraftCryptoConfig
from pyJianYingDraft.draft_codec import write_json_object_with_codec

JY_INSTALL_DIR = r"C:\Users\trees\AppData\Local\JianyingPro\Apps\11.4.1.14443"
DRAFT_DIR = Path(r"F:\trees\Documents\JianyingPro Drafts\9月8日-副本-副本")
TIMELINE_ID = "2B9525A2-5D8B-4131-B87E-6359E530440E"
TIMELINE_DIR = DRAFT_DIR / "Timelines" / TIMELINE_ID
DRAFT_JSON = TIMELINE_DIR / "draft_content.json"
BAK_JSON = DRAFT_JSON.with_suffix(".json.opt_bak")

# Eagle 真实音效路径
SFX_27G_PATH = r"X:/私人素材库.library/images/M3AG45SEHHI20.info/Film Sound 3.wav"
SFX_BUTTON_PATH = r"X:/私人素材库.library/images/MINMOANSV99HJ.info/Camera Shutter.wav"
SFX_TAPE_ROOM_PATH = r"X:/私人素材库.library/images/LOXVLN9YUGQ1A.info/MECH_VHS Player_Tapehead error_02.wav"

def load_draft() -> dict:
    codec = JianyingDraftCryptoCodec(DraftCryptoConfig(
        jy_install_dir=JY_INSTALL_DIR, isolated=True,
        validate_roundtrip=False, backup=False
    ))
    if not BAK_JSON.exists():
        shutil.copy2(DRAFT_JSON, BAK_JSON)
        print(f"[backup] 已备份原始终案: {BAK_JSON.name}")
    else:
        print(f"[backup] 备份已存在: {BAK_JSON.name}")
        
    raw = DRAFT_JSON.read_bytes()
    if raw[:1] == b"{":
        return json.loads(raw.decode("utf-8"))
    return codec.decode(raw)

def save_and_sync(data: dict):
    codec = JianyingDraftCryptoCodec(DraftCryptoConfig(
        jy_install_dir=JY_INSTALL_DIR, isolated=True,
        validate_roundtrip=True, backup=False
    ))
    data["update_time"] = int(time.time() * 1_000_000)
    
    print(f"[save] 加密写回: {DRAFT_JSON}")
    write_json_object_with_codec(DRAFT_JSON, data, content_codec=codec, indent=None)
    
    sync_targets = [
        TIMELINE_DIR / "template-2.tmp",
        DRAFT_DIR / "draft_content.json",
        DRAFT_DIR / "template-2.tmp"
    ]
    for dst in sync_targets:
        shutil.copy2(DRAFT_JSON, dst)
        print(f"[sync] 镜像同步 -> {dst.name}")
        
    for bdir in [DRAFT_DIR / ".backup", TIMELINE_DIR / ".backup"]:
        if bdir.exists():
            shutil.rmtree(bdir, ignore_errors=True)
            print(f"[clean] 清除缓存: {bdir}")

    appdata_dst = Path(r"C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\9月8日-副本-副本")
    if appdata_dst.parent.exists():
        if appdata_dst.exists():
            shutil.rmtree(appdata_dst, ignore_errors=True)
        shutil.copytree(DRAFT_DIR, appdata_dst)
        print(f"[sync] 同步至剪映系统主目录: {appdata_dst}")

def add_audio_asset(draft_data: dict, audio_name: str, audio_path: str, duration_us: int) -> str:
    mat_id = str(uuid.uuid4()).upper()
    audio_obj = {
        "id": mat_id,
        "name": audio_name,
        "path": audio_path.replace("\\", "/"),
        "duration": duration_us,
        "type": "sound",
        "category_name": "我的音效",
        "source_platform": 0,
        "app_id": 1775
    }
    draft_data.setdefault("materials", {}).setdefault("audios", []).append(audio_obj)
    return mat_id

def create_audio_segment(mat_id: str, target_start_us: int, target_duration_us: int, volume: float = 0.5) -> dict:
    seg_id = str(uuid.uuid4()).upper()
    return {
        "id": seg_id,
        "material_id": mat_id,
        "source_timerange": {"start": 0, "duration": target_duration_us},
        "target_timerange": {"start": target_start_us, "duration": target_duration_us},
        "render_timerange": {},
        "extra_material_refs": [],
        "volume": volume,
        "enable_lut": False,
        "enable_adjust": False,
        "enable_hsl": False,
        "track_render_index": 8,
        "responsive_layout": {},
        "enable_adjust_mask": False,
        "source": "segmentsourcenormal"
    }

def main():
    print("=" * 65)
    print("🌲 植人大树 Creator OS 3.0 — 终案精修与音画时髦化注入")
    print("=" * 65)
    
    draft = load_draft()
    
    # ── 1. 视听 Hook 与音效密度增强 ─────────────────────────────
    print("\n🎧 [1/3] 正在注入高品味物理音效...")
    t8 = draft["tracks"][8] # 音效专用轨
    
    # (A) 8.5s - 只有27克 (Film Sound 3 快门音)
    id_27g = add_audio_asset(draft, "Film Sound 3 (27g特写)", SFX_27G_PATH, 1_088_549)
    seg_27g = create_audio_segment(id_27g, target_start_us=8_500_000, target_duration_us=1_088_549, volume=0.55)
    t8["segments"].append(seg_27g)
    print("  ✨ 已在 8.50s 注入 [Film Sound 3] 快门声 (对齐 '重量只有27克')")
    
    # (B) 18.35s - 侧面是控制按钮 (Camera Shutter 机械段落微动)
    id_btn = add_audio_asset(draft, "Camera Shutter (控制按键)", SFX_BUTTON_PATH, 1_125_000)
    seg_btn = create_audio_segment(id_btn, target_start_us=18_350_000, target_duration_us=900_000, volume=0.50)
    t8["segments"].append(seg_btn)
    print("  ✨ 已在 18.35s 注入 [Camera Shutter] 机械声 (对齐 '侧面是控制按钮')")
    
    # (C) 45.8s - 49.47s 结尾留白彩蛋 (MECH VHS 胶片放映机质感底噪)
    end_dur_us = int((49.47 - 45.80) * 1_000_000) # 3.67s
    id_tape = add_audio_asset(draft, "MECH VHS Room Sound (留白彩蛋)", SFX_TAPE_ROOM_PATH, 94_703_010)
    seg_tape = create_audio_segment(id_tape, target_start_us=45_800_000, target_duration_us=end_dur_us, volume=0.35)
    t8["segments"].append(seg_tape)
    print("  ✨ 已在 45.80s - 49.47s 注入 [MECH VHS 机械底噪] 解决尾部静音断层")
    
    # 按时间戳排序音效段
    t8["segments"].sort(key=lambda s: s["target_timerange"]["start"])
    
    # ── 2. 长镜头关键帧对称校准 (消除微小畸变) ────────────────────
    print("\n🎥 [2/3] 正在校准长镜头 Scale 关键帧对称性...")
    t0 = draft["tracks"][0]
    
    # 校准 Clip 2 (10.8s: 1.18s -> 11.98s, src=8499999)
    # 设为首(1.000) -> 中(1.035) -> 尾(1.055) 完美平滑
    seg2 = t0["segments"][2]
    s2_start = seg2["source_timerange"]["start"]
    s2_dur = seg2["target_timerange"]["duration"]
    p2 = [
        (s2_start, 1.000),
        (s2_start + s2_dur // 2, 1.035),
        (s2_start + s2_dur, 1.055)
    ]
    seg2["common_keyframes"] = [
        {
            "id": str(uuid.uuid4()).upper(), "material_id": "", "property_type": "KFTypeScaleX",
            "keyframe_list": [{"id": str(uuid.uuid4()).upper(), "time_offset": t, "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [v]} for t, v in p2]
        },
        {
            "id": str(uuid.uuid4()).upper(), "material_id": "", "property_type": "KFTypeScaleY",
            "keyframe_list": [{"id": str(uuid.uuid4()).upper(), "time_offset": t, "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [v]} for t, v in p2]
        }
    ]
    print("  ✨ Clip [02] 10.80s 已校准为绝对等比呼吸 (1.000 ➔ 1.035 ➔ 1.055)")
    
    # 校准 Clip 6 (12.62s: 30.08s -> 42.70s, src=34400000)
    # 设为首(1.000) -> 中(1.035) -> 尾(1.055)
    seg6 = t0["segments"][6]
    s6_start = seg6["source_timerange"]["start"]
    s6_dur = seg6["target_timerange"]["duration"]
    p6 = [
        (s6_start, 1.000),
        (s6_start + s6_dur // 2, 1.035),
        (s6_start + s6_dur, 1.055)
    ]
    seg6["common_keyframes"] = [
        {
            "id": str(uuid.uuid4()).upper(), "material_id": "", "property_type": "KFTypeScaleX",
            "keyframe_list": [{"id": str(uuid.uuid4()).upper(), "time_offset": t, "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [v]} for t, v in p6]
        },
        {
            "id": str(uuid.uuid4()).upper(), "material_id": "", "property_type": "KFTypeScaleY",
            "keyframe_list": [{"id": str(uuid.uuid4()).upper(), "time_offset": t, "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [v]} for t, v in p6]
        }
    ]
    print("  ✨ Clip [06] 12.62s 已校准为绝对等比呼吸 (1.000 ➔ 1.035 ➔ 1.055)")
    
    # ── 3. 保存与同步 ─────────────────────────────────────────────
    print("\n💾 [3/3] 正在执行无损重加密与镜像同步...")
    save_and_sync(draft)
    
    print("\n" + "=" * 65)
    print("🎉 优化注入完成！请在剪映中打开《9月8日-副本-副本》预览听感与画质：")
    print("   1. 8.5s & 18.3s 已增添摄影器材的真实机械触感音；")
    print("   2. 结尾 The End 贴纸已拥有复古放映机氛围底噪；")
    print("   3. 长镜头缩放已实现绝对对称等比呼吸。")
    print("=" * 65)

if __name__ == "__main__":
    main()
