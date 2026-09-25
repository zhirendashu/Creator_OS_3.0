"""
scan_draft_by_name.py — 规范第1条：按草稿名称扫描最新状态
"""
import os, json, subprocess, sys, argparse
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

parser = argparse.ArgumentParser(description="扫描草稿")
parser.add_argument("--name", "-n", default="9月2日-副本", help="草稿名称关键词")
args, _ = parser.parse_known_args()

TARGET = args.name

DRAFT_ROOTS = [
    r"F:\trees\Documents\JianyingPro Drafts",
    r"C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
]

def ffprobe_info(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", path],
            capture_output=True, text=True, timeout=8
        )
        d = json.loads(r.stdout)
        for s in d.get("streams", []):
            if s.get("codec_type") == "video":
                w, h = s.get("width", 0), s.get("height", 0)
                return {
                    "type": "video", "width": w, "height": h,
                    "duration": float(d.get("format", {}).get("duration", 0)),
                    "codec": s.get("codec_name", "?"),
                    "is_vertical": h > w,
                    "ratio": f"{w}x{h}",
                }
        return {"type": "audio", "duration": float(d.get("format", {}).get("duration", 0))}
    except Exception:
        return {}

def find_best_json(draft_dir):
    """找最新、最大、可解析的 JSON"""
    tl_dir = os.path.join(draft_dir, "Timelines")
    if not os.path.exists(tl_dir):
        return None, None
    candidates = []
    for sub in os.listdir(tl_dir):
        sub_path = os.path.join(tl_dir, sub)
        if not os.path.isdir(sub_path):
            continue
        for fname in ["template.json", "draft_content.json"]:
            fp = os.path.join(sub_path, fname)
            if os.path.exists(fp):
                candidates.append((os.path.getmtime(fp), os.path.getsize(fp), fp, sub_path))
    candidates.sort(reverse=True)
    for _, size, fp, subdir in candidates:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"  ✅ [{size//1024}KB | {datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%H:%M:%S')}] {os.path.relpath(fp, draft_dir)}")
            return data, subdir
        except Exception:
            print(f"  ⚠️  加密跳过: {os.path.relpath(fp, draft_dir)} [{size//1024}KB]")
    return None, None

print("="*65)
print(f"🔍 Creator OS 3.0 — 规范扫描")
print(f"   目标草稿: 《{TARGET}》")
print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*65)

data = subdir = draft_dir = None
for root in DRAFT_ROOTS:
    candidate = os.path.join(root, TARGET)
    if os.path.isdir(candidate):
        print(f"\n📁 {candidate}")
        data, subdir = find_best_json(candidate)
        if data:
            draft_dir = candidate
            break

if not data:
    print("❌ 无可解析 JSON")
    exit(1)

tracks = data.get("tracks", [])
mats   = data.get("materials", {})
kfs    = mats.get("keyframes", [])
vids   = {v["id"]: v for v in mats.get("videos", [])}
auds   = {a["id"]: a for a in mats.get("audios", [])}
texts  = {t["id"]: t for t in mats.get("texts", [])}

print(f"\n📊 基本信息:")
print(f"   时长: {data.get('duration',0)/1e6:.3f}s  |  画布: {data.get('canvas_config')}  |  关键帧: {len(kfs)} 个")

print(f"\n📋 轨道:")
for t in tracks:
    print(f"   [{t.get('type'):6s}] '{t.get('name','(无名)')}': {len(t.get('segments',[]))} segs")

print(f"\n🎥 主视频轨 (main_video):")
for t in tracks:
    if t.get("type") == "video" and t.get("name") == "main_video":
        segs = t.get("segments", [])
        print(f"   共 {len(segs)} 个片段:")
        for i, s in enumerate(segs):
            mat = vids.get(s.get("material_id"), {})
            tgt = s.get("target_timerange", {})
            src = s.get("source_timerange", {})
            refs = len(s.get("extra_material_refs", []))
            path = mat.get("path", "?")
            ok = "✅" if os.path.exists(path) else "❌"
            print(f"   [{i:02d}] {mat.get('material_name','?'):22s} | {tgt.get('start',0)/1e6:.2f}s +{tgt.get('duration',0)/1e6:.2f}s | src@{src.get('start',0)/1e6:.2f}s | refs={refs} {ok}")

print(f"\n🎞️  FX 覆盖轨 (含尺寸分析):")
for t in tracks:
    if t.get("type") == "video" and t.get("name") != "main_video":
        print(f"   轨: '{t.get('name')}'")
        for s in t.get("segments", []):
            mat = vids.get(s.get("material_id"), {})
            tgt = s.get("target_timerange", {})
            path = mat.get("path", "?")
            blend = mat.get("blend_mode", "(未设置)")
            info = ffprobe_info(path) if os.path.exists(path) else {}
            ratio   = info.get("ratio", "?")
            is_v    = "竖屏✅" if info.get("is_vertical") else f"横屏⚠️需缩放"
            dur     = info.get("duration", 0)
            print(f"   - {mat.get('material_name','?'):32s} | {ratio} {is_v} | dur={dur:.1f}s | blend={blend} | tgt@{tgt.get('start',0)/1e6:.2f}s +{tgt.get('duration',0)/1e6:.2f}s")

print(f"\n🔊 音频轨:")
for t in tracks:
    if t.get("type") == "audio":
        print(f"   轨: '{t.get('name')}'")
        for s in t.get("segments", []):
            mat = auds.get(s.get("material_id"), {})
            tgt = s.get("target_timerange", {})
            src = s.get("source_timerange", {})
            tgt_dur = tgt.get("duration", 0)/1e6
            flag = "🔴过长" if tgt_dur > 3 else "🟡偏长" if tgt_dur > 1.5 else "🟢"
            print(f"   {flag} {mat.get('name','?'):24s} vol={s.get('volume',1.0):.2f} | @{tgt.get('start',0)/1e6:.2f}s +{tgt_dur:.2f}s | src_dur={src.get('duration',0)/1e6:.2f}s")

print(f"\n✍️  文字:")
for t in tracks:
    if t.get("type") == "text":
        for s in t.get("segments", []):
            mat = texts.get(s.get("material_id"), {})
            tgt = s.get("target_timerange", {})
            try:
                txt = json.loads(mat.get("content","{}")).get("text","?")
            except:
                txt = "?"
            print(f"   @{tgt.get('start',0)/1e6:.2f}s +{tgt.get('duration',0)/1e6:.2f}s  '{txt.replace(chr(10),' ')[:30]}'")

print(f"\n{'='*65}")
print(f"✅ 扫描完成  — {sum(len(t.get('segments',[])) for t in tracks)} 个总片段")
print(f"   subdir: {subdir}")
print(f"{'='*65}")
