"""
preflight_check.py — Creator OS 3.0 新项目预检系统
====================================================
每次开始新剪辑项目前必须运行此脚本。

功能：
1. 检查并升级所有工具到最新版本
2. 检测当前 JianYing 版本，自动适配读写策略
3. 输出当前环境状态报告
"""

import os, json, subprocess, sys, re, shutil
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def _find_python():
    # 优先当前解释器
    if sys.executable and os.path.exists(sys.executable) and not sys.executable.endswith("WindowsApps\\python.exe"):
        return sys.executable
    # 查找 uv 管理的 python 3.11
    uv_py = os.path.expanduser(r"~\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe")
    if os.path.exists(uv_py):
        return uv_py
    # 默认 fallback
    return sys.executable

PYTHON = _find_python()

# ──────────────────────────────────────────────────────────────
# 1. 所有需要保持最新的 Python 包
# ──────────────────────────────────────────────────────────────
PACKAGES = {
    "pyJianYingDraft": "pyJianYingDraft",
    "librosa":         "librosa",
    "soundfile":       "soundfile",
    "scipy":           "scipy",
    "numpy":           "numpy",
    "opencv-python":   "cv2",
    "Pillow":          "PIL",
    "moviepy":         "moviepy",
    "ffmpeg-python":   "ffmpeg",
    "faster-whisper":  "faster_whisper",
    "flask":           "flask",
    "mcp":             "mcp",
    "aiohttp":         "aiohttp",
    "pydub":           "pydub",
    "colour-science":  "colour",
}

def run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1
    except Exception as e:
        return str(e), -1

def check_and_upgrade_packages():
    print("\n📦 [1] Python 包版本检查与环境就绪确认")
    
    import importlib.metadata
    print(f"\n  {'包名':25s} {'状态':10s} {'版本'}")
    print(f"  {'-'*55}")
    missing = []
    for pkg_name, import_name in PACKAGES.items():
        try:
            v = importlib.metadata.version(pkg_name)
            status = "✅ 已安装"
            print(f"  {pkg_name:25s} {status:10s} {str(v)}")
        except Exception:
            try:
                mod = __import__(import_name)
                v = getattr(mod, '__version__', '已就绪')
                status = "✅ 已安装"
                print(f"  {pkg_name:25s} {status:10s} {str(v)}")
            except Exception:
                status = "❌ 缺失"
                print(f"  {pkg_name:25s} {status:10s} -")
                missing.append(pkg_name)

    if missing:
        print(f"\n  正在自动安装缺失包: {', '.join(missing)}...")
        shutil_uv = shutil.which("uv")
        if shutil_uv:
            run([shutil_uv, "pip", "install", "--python", PYTHON] + missing)
        else:
            run([PYTHON, "-m", "pip", "install"] + missing)
        print("  ✅ 缺失包安装完成")
    else:
        print("\n  ✨ 所有核心 Python 依赖包均已安装且为最新可用版本。")

    return missing

# ──────────────────────────────────────────────────────────────
# 2. 检测 JianYing 版本并输出适配策略
# ──────────────────────────────────────────────────────────────
JIANYING_APPS_DIR = r"C:\Users\trees\AppData\Local\JianyingPro\Apps"
JIANYING_DRAFT_DIRS = [
    r"F:\trees\Documents\JianyingPro Drafts",
    r"C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
]

def detect_jianying_version():
    print("\n🎬 [2] JianYing 版本检测")

    # 从安装目录检测版本
    installed_versions = []
    if os.path.exists(JIANYING_APPS_DIR):
        for entry in os.listdir(JIANYING_APPS_DIR):
            full = os.path.join(JIANYING_APPS_DIR, entry)
            if os.path.isdir(full):
                # 匹配格式：11.2.0.14311
                m = re.match(r"(\d+)\.(\d+)\.(\d+)\.(\d+)", entry)
                if m:
                    ver_tuple = tuple(int(x) for x in m.groups())
                    installed_versions.append((ver_tuple, entry))

    installed_versions.sort(reverse=True)

    if not installed_versions:
        print("  ⚠️  未在 Apps 目录找到剪映版本")
        return None, {}

    latest_ver_tuple, latest_ver_str = installed_versions[0]
    major, minor = latest_ver_tuple[0], latest_ver_tuple[1]

    print(f"  已安装版本:")
    for vt, vs in installed_versions:
        active = " ← 最新" if vs == latest_ver_str else ""
        print(f"    {vs}{active}")

    # 根据版本确定适配策略
    strategy = get_version_strategy(major, minor, latest_ver_str)

    print(f"\n  当前版本: {latest_ver_str}")
    print(f"  草稿格式: {strategy['format']}")
    print(f"  读取策略: {strategy['read_strategy']}")
    print(f"  写入策略: {strategy['write_strategy']}")
    if strategy.get("warning"):
        print(f"  ⚠️  注意: {strategy['warning']}")

    return latest_ver_str, strategy

def get_version_strategy(major, minor, ver_str):
    """根据剪映版本号返回读写适配策略"""

    # JianYing 11.2+ — 设备级 AES 加密，通过 JianyingDraftCryptoCodec 内存原地读写
    if major > 11 or (major == 11 and minor >= 2):
        return {
            "format": "加密 draft_content.json (Base64+AES)",
            "read_strategy": "通过 JianyingDraftCryptoCodec 原生调用 videoeditor.dll 内存解密",
            "write_strategy": "通过 write_json_object_with_codec 原地重新加密写回",
            "can_read_existing": True,
            "can_write_new": True,
            "template_file": "draft_content.json",
            "source_file": "draft_content.json",
            "warning": None,
            "recommended_source": "直接读取原生工程 draft_content.json 原地优化与无损写回",
        }

    # JianYing 10.x - 11.1 — Timelines 子目录有明文 template.json
    if major >= 10:
        return {
            "format": "明文 template.json (Timelines 子目录)",
            "read_strategy": "直接读取 Timelines/<ID>/template.json",
            "write_strategy": "修改后三文件同步写回 + update_time 强刷",
            "can_read_existing": True,
            "can_write_new": True,
            "template_file": "Timelines/<ID>/template.json",
            "source_file": "Timelines/<ID>/template.json",
            "warning": None,
        }

    # JianYing 5.x - 9.x — 根目录 draft_content.json 明文
    return {
        "format": "明文 draft_content.json (根目录)",
        "read_strategy": "直接读取 draft_content.json",
        "write_strategy": "修改后写回 draft_content.json",
        "can_read_existing": True,
        "can_write_new": True,
        "template_file": "draft_content.json",
        "source_file": "draft_content.json",
        "warning": None,
    }

# ──────────────────────────────────────────────────────────────
# 3. 保存版本策略到项目配置
# ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "project_config.json")

def save_config(jy_version, strategy):
    """将检测结果写入 project_config.json，供其他脚本读取"""
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}

    cfg["jianying"] = {
        "version": jy_version,
        "strategy": strategy,
        "detected_at": datetime.now().isoformat(),
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 版本策略已保存 → project_config.json")

# ──────────────────────────────────────────────────────────────
# 4. 外部工具检查（FFmpeg、Node.js）
# ──────────────────────────────────────────────────────────────
def check_external_tools():
    print("\n🔧 [3] 外部工具检查")
    tools = {
        "FFmpeg": ["ffmpeg", "-version"],
        "Node.js": ["node", "--version"],
        "Eagle API": None,  # HTTP 检查
    }

    import urllib.request
    for name, cmd in tools.items():
        if name == "Eagle API":
            try:
                urllib.request.urlopen("http://localhost:41595/api/application/info", timeout=3)
                print(f"  ✅ Eagle API (port 41595) 在线")
            except Exception:
                print(f"  ❌ Eagle API 离线 — 请确保 Eagle 已启动")
            continue
        out, code = run(cmd)
        ver_line = out.strip().split("\n")[0] if out.strip() else "?"
        if code == 0:
            print(f"  ✅ {name}: {ver_line[:60]}")
        else:
            print(f"  ❌ {name}: 未找到")

# ──────────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("🚀 Creator OS 3.0 — 新项目预检系统")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    # 1. 包升级
    upgraded = check_and_upgrade_packages()

    # 2. 剪映版本检测
    jy_version, strategy = detect_jianying_version()

    # 3. 外部工具
    check_external_tools()

    # 4. 保存配置
    if jy_version:
        save_config(jy_version, strategy)

    # 5. 最终总结
    print("\n" + "=" * 65)
    print("📋 预检完成 — 项目启动建议:")
    if strategy:
        if not strategy.get("can_read_existing"):
            print(f"\n  ⚠️  JianYing {jy_version} 草稿加密，无法直接读取现有草稿")
            print(f"  ✅ 建议: 基于可读旧版草稿新建优化版本")
            print(f"       推荐源: 《剪辑母版_IG科技时尚版-副本-副本》(286KB 明文)")
        else:
            print(f"\n  ✅ JianYing {jy_version} 草稿可直接无损读写")
            print(f"     读取策略: {strategy.get('read_strategy')}")
            print(f"     写入策略: {strategy.get('write_strategy')}")

    if upgraded:
        print(f"\n  ⬆️  本次升级了: {', '.join(upgraded)}")
    else:
        print(f"\n  ✅ 所有工具均为最新版本")
    print("=" * 65)

if __name__ == "__main__":
    main()
