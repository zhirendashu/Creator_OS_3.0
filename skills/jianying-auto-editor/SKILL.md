---
name: jianying-auto-editor
description: 剪映（JianYing Pro）自动剪辑与花字预设技能。支持自动合成视频、音频、ASMR音效轨、3D微旋转运镜与5大昆丁/科技时尚风文字预设模板。
---

# 剪映（JianYing Pro）自动剪辑与预设 Skill

本 Skill 为 Antigravity 2.0 提供操作"剪映专业版"（JianYing Pro）自动生成与管理草稿工程的核心能力。

---

## 核心配置与路径信息

- **系统 Python 环境**: Python 3.11 (`C:\Users\trees\AppData\Local\Programs\Python\Python311\python.exe`)
- **核心依赖库**: `pyJianYingDraft` (已安装)
- **剪映草稿存储目录**:
  - 系统默认: `C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\`
  - 工作区文档: `F:\trees\Documents\JianyingPro Drafts\`
- **Eagle 素材库**: `X:\私人素材库.library` (API port: 41595)

---

## 🚨 AI 剪辑操作强制规范（每次操作前必须遵守）

### 规范 -1 — 剪辑需求四级分层执行架构（4-STAGE PIPELINE）⭐ 核心交互总纲
> **面对自然语言剪辑指令时，必须按以下 4 级步骤逐步推进，严禁越级或盲目修改代码。**

1. **阶段 1：意图识别层（Intent Recognition & Parsing）**
   - 提取目标时长、剪辑节奏（快切/慢镜头/卡点）、标题预设（如 `01_pulp_amber`）、BGM/音效需求（如 `Film Sound 1~7`）、Overlay 光效与目标画幅（如 9:16 竖屏）。
2. **阶段 2：素材匹配与预处理层（Asset Pre-flight & Validation）**
   - 运行 `python preflight_check.py` 确认系统工具链与剪映版本策略。
   - 调用 Eagle API（`http://localhost:41595/api/item/list?keyword=...`）检索真实的漏光、VHS、快门音效等实体路径。
   - 使用 `ffprobe` 检测素材宽高比，预计算 `scale_x/scale_y` 填满目标画布。
3. **阶段 3：草稿构建与属性注入层（Draft Assembly & Property Injection）**
   - 执行 `python scan_draft_by_name.py` 扫描并锁定最新的明文工程。
   - 使用 `pyJianYingDraft` 构建或优化草稿，严格执行 `Screen` 滤色模式、音效截断（≤1.2s）、3D 微旋转与花字预设注入。
   - 强刷同步 `template.json` / `draft_content.json` 3 文件并清理 `.backup` 缓存。
4. **阶段 4：导出触发与工程交付层（Export & Delivery）**
   - 如果用户环境支持 GUI 自动化（如剪映 v5.9），唤醒自动化导出脚本。
   - 打印完整剪辑清单（轨道数、素材路径、音效数），并交由用户进行工程预览或一键导出。

---

### 规范 0 — 新项目预检（PRE-FLIGHT CHECK）⭐ 每个新项目第一步
> **每次开始新剪辑项目时，必须先运行预检脚本，确认工具最新、版本已适配。**

```powershell
# 每次新项目必须第一步运行
python preflight_check.py
```

**预检内容（自动执行）：**
1. **工具版本升级** — 检测所有 Python 包是否为最新版，不是则自动 `pip install --upgrade`
   - 检测包：`pyJianYingDraft` / `librosa` / `soundfile` / `scipy` / `numpy` / `opencv-python` / `Pillow` / `moviepy` / `ffmpeg-python` / `faster-whisper` / `flask` / `mcp` / `aiohttp` / `pydub` / `colour-science`
2. **JianYing 版本检测** — 读取 `C:\Users\trees\AppData\Local\JianyingPro\Apps\` 目录，识别已安装版本
3. **外部工具检测** — 确认 FFmpeg / Node.js / Eagle API (port 41595) 均在线
4. **写入 `project_config.json`** — 将版本策略持久化，供后续脚本读取

---

### 规范 0.5 — JianYing 版本适配策略（VERSION ADAPTIVE STRATEGY）
> **根据检测到的 JianYing 版本，自动切换读写草稿的策略。**

| 版本范围 | 草稿格式 | 读取文件 | 可直接读取 |
|:---|:---|:---|:---|
| 5.x – 9.x | 明文 JSON | `draft_content.json`（根目录） | ✅ 是 |
| 10.x – 11.1 | 明文 JSON | `Timelines/<ID>/template.json` | ✅ 是 |
| **11.2+** | **Base64+AES 加密** | `draft_content.json`（加密，不可读）| **❌ 否** |

**JianYing 11.2+ 强制工作流：**
- ❌ 不得尝试解密现有草稿（设备级 AES，无法从外部解密）
- ✅ 必须从**可读的旧版草稿**（如遗留的明文 template.json）新建优化版
- ✅ 或请用户在剪映内「复制草稿」后让剪映做一次修改保存，看是否生成明文文件
- ✅ 所有新生成的草稿通过 `pyJianYingDraft` 从零构建（生成明文 template.json）

```python
# 每次操作前读取版本策略
import json
with open('project_config.json') as f:
    cfg = json.load(f)
strategy = cfg['jianying']['strategy']
can_read = strategy['can_read_existing']   # False for 11.2+
```

---

### 规范 0.6 — jy-draftc 解密工具（11.2+ 强制工作流补丁）
> **剪映 11.2+ 版本加密草稿的唯一可靠修改方案：先解密、修改、再回加密。**

#### 安装 jy-draftc
```powershell
pip install jy-draftc
# 或从源码安装（获取最新版）
# git clone https://github.com/jy-draftc/jy-draftc && cd jy-draftc && pip install -e .
```

#### 解密 → 修改 → 回加密 完整流程
```python
import subprocess, json, shutil, time
from pathlib import Path

def decrypt_and_patch_draft(encrypted_json_path: str, patch_fn):
    """
    对剪映 11.2+ 加密草稿执行：解密 → 修改 → 回加密
    patch_fn: 接受 dict，返回修改后的 dict
    """
    p = Path(encrypted_json_path)
    backup_path = p.with_suffix('.bak_before_patch')
    shutil.copy2(p, backup_path)  # 备份原文件
    print(f"[jy-draftc] 备份已保存: {backup_path}")

    # 1. 解密为明文 JSON
    decrypted_path = p.with_suffix('.decrypted.json')
    subprocess.run(['jy-draftc', 'decrypt', str(p), '--output', str(decrypted_path)], check=True)

    # 2. 读取并修改
    with open(decrypted_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    patched_data = patch_fn(data)
    with open(decrypted_path, 'w', encoding='utf-8') as f:
        json.dump(patched_data, f, ensure_ascii=False, indent=2)

    # 3. 回加密覆盖原文件
    subprocess.run(['jy-draftc', 'encrypt', str(decrypted_path), '--output', str(p)], check=True)
    decrypted_path.unlink()  # 清理临时解密文件
    print(f"[jy-draftc] 草稿已修改并重新加密: {p}")
    return str(p)

# 使用示例：修改草稿更新时间戳
def patch_timestamp(data: dict) -> dict:
    data['update_time'] = int(time.time() * 1_000_000)
    return data

decrypt_and_patch_draft(
    r"C:\Users\trees\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\我的草稿\draft_content.json",
    patch_fn=patch_timestamp
)
```

#### 模板克隆方案（推荐，最稳健）
> 对于复杂的花字/特效草稿，「模板克隆」比解密修改更安全：

```python
import shutil, os

def clone_template_draft(template_dir: str, new_name: str, target_base_dir: str) -> str:
    """克隆一个已有的剪映草稿作为新项目起点"""
    target_dir = os.path.join(target_base_dir, new_name)
    shutil.copytree(template_dir, target_dir)
    print(f"[模板克隆] 新草稿已创建: {target_dir}")
    return target_dir
```

#### 版本策略决策树（2026 突破版）
```
检测到剪映版本
│
├── 5.x ~ 9.x   → 直接读写 draft_content.json（根目录）
├── 10.x ~ 11.1 → 直接读写 Timelines/<ID>/template.json
└── 11.2+ (如 11.4) →
    ├── ⭐ 推荐 (最高级无损加解密): 使用 JianyingDraftCryptoCodec 直接内存加解密已有加密草稿
    │     - 读取: codec.decode(raw_bytes) -> dict
    │     - 写回: write_json_object_with_codec(path, dict, content_codec=codec)
    ├── 模板克隆方案: 复制已有明文模板草稿
    └── 从零构建: pyJianYingDraft.DraftFolder.create_draft()
```

#### 极简柔和等比呼吸感关键帧规范（防眩晕、防刺猬密帧）
1. **关键帧密度控制**：单镜头仅放置 **2 ~ 3 个帧点**（首帧、[中点微吸/呼]、尾帧），完全依靠底层平滑过渡，杜绝几十个密集高频震颤点。
2. **等比缩放规范**：
   - 在 `seg["common_keyframes"]` 中同时挂载 `KFTypeScaleX` 与 `KFTypeScaleY`；
   - 保证 X 与 Y 两个轴的各时间点数值完全一致（如 `1.000 ➔ 1.055`）；
   - `seg["uniform_scale"] = {}` 保持原生字典，实现前台无冲突的等比平滑呼吸。
3. **物理源绝对对齐**：
   - 每个切片内部帧的 `time_offset = source_start_us + local_offset`，防止后续切片由于时间越界死值。
```

---

### 规范 1 — 扫描优先法则（SCAN FIRST）
> **每次修改草稿前，必须先扫描磁盘上草稿的最新状态。**

- 读取 `Timelines/<SubID>/template.json`（选最新时间戳 + 最大文件尺寸 + 可解析明文 JSON 的版本）
- 对比所有候选文件的大小和修改时间，优先最新
- 加密文件（header 非 `{` 开头）跳过，不强行覆盖
- **绝对禁止** 基于上一次扫描结果直接操作，每轮对话必须重新扫描

```python
# 每次操作的第一步
python scan_draft_by_name.py  # 自动找最新可读 JSON 并打印轨道/片段全览
```

### 规范 2 — 重大修改新建草稿（NEW DRAFT FOR MAJOR CHANGES）
> **结构性修改（增删片段、重排音轨）必须新建草稿，原版保持只读。**

- 命名规则：`原始草稿名 + _AI优化版_MMDD`
- 使用 `pyJianYingDraft.DraftFolder.create_draft()` 生成干净工程
- 原始草稿目录禁止删除或重命名

### 规范 3 — Eagle 素材库优先（EAGLE FIRST）
> **转场、叠加、音效素材优先从 Eagle 库搜索真实文件。**

- 调用 `http://localhost:41595/api/item/list?keyword=<关键词>` 搜索
- 有效关键词：`漏光` / `VHS` / `Flash` / `Film` / `Overlay` / `胶片` / `Film Sound 1~7`
- 有效标签（Eagle库中已确认）：`视频特效` / `动态叠加` / `后期剪辑` / `材质纹理` / `做旧模板`
- 获得路径后**必须用 `os.path.exists()` 验证**再使用
- 音频文件扩展名白名单: `.wav .mp3 .m4a .aac .flac`（排除 `.zip .rar`）

### 规范 4 — 素材尺寸分析（DIMENSION ANALYSIS）
> **使用转场/叠加素材前，必须用 `ffprobe` 检测分辨率和宽高比。**

```python
ffprobe -v quiet -print_format json -show_streams -show_format <path>
```

- 竖屏目标画布：`1080x1920`（9:16）
- 横屏素材（如 3840x2160）在竖屏草稿中需设置：
  - `scale_x = scale_y = 1920 / 2160 ≈ 0.889`（填满竖屏高度）
  - 或在剪映中手动旋转 90° + 放大 `1.778x`
- 音效文件检测实际播放时长，超过目标时长须截断 `source_timerange.duration`

### 规范 5 — 叠加混合模式（BLEND MODE = SCREEN）
> **所有光效/转场叠加素材必须使用滤色（Screen）混合模式，防止遮挡主视频。**

| 素材类型 | 混合模式 | 最大时长 |
|:---|:---|:---|
| 胶片漏光 / 白闪 / 黄闪 | `screen`（滤色） | 0.5 ~ 1.5s |
| VHS噪波 / 胶片颗粒 | `screen`（滤色） | 1.0 ~ 2.0s |
| Film Strip / 胶片条 | `screen`（滤色） | 0.5 ~ 1.5s |
| Camera Overlay | `screen`（滤色） | 贯穿片段但 opacity ≤ 0.6 |
| LUT 调色 | `normal`（正常，仅滤镜轨） | 全程 |

- 叠加段不得使用 `normal` 模式且 opacity=1.0 贯穿主视频
- `source_timerange` 必须截断至 ≤ 素材切点实际长度

### 规范 6 — 音效时长截断（SFX TRIM RULE）
> **Eagle Film Sound 音效文件有完整播放时长（1~13s），使用时必须精确截断。**

```
eagle_cut_sfx 切点音效：source_timerange.duration ≤ 1_200_000 us (1.2s)
eagle_text_sfx 文字音效：source_timerange.duration ≤ 800_000 us (0.8s)
BGM 轨：保持原长，仅控制 volume ≤ 0.35
同时重叠音效轨 ≤ 2 条（防止吵闹堆叠）
```

### 规范 7 — 针对文字超界与重叠的 3 大修正自我检查 (TEXT OVERFLOW & OVERLAP SELF-CHECK)
> **生成或修改任何花字、标题、口播字幕前，必须执行以下 3 大自查与修正，杜绝文字出界与重叠打架。**

#### 1. 修正 1：单行字数上限与自动换行（X 轴防出界）
- **自查问题**：文本未折行，单行文字数过长，导致左右两端超出 1080px 安全画布。
- **强制规则**：
  - **大标题 / Hook 预设**（字号 80 ~ 120pt）：单行上限 **7 ~ 8 字**。超过 8 字强制插入 `\n` 换行居中显示。
  - **口播字幕 / 辅助解说**（字号 40 ~ 50pt）：单行上限 **14 ~ 16 字**。超过 16 字强制按中点标点断句插入 `\n` 换行。
  - **安全画布边距**：左右两侧必须留出 `margin_x ≥ 80px` 安全缓冲，禁止字符挤压在屏边缘。

#### 2. 修正 2：纵向坐标隔离与时间轴避让（Y 轴 & 时间防重叠）
- **自查问题**：主标题、副标题与字幕在相同 Y 坐标堆叠（上下遮挡），或相邻文本片段时间戳交叉（前后闪烁重叠）。
- **强制规则**：
  - **空间纵向 Y 轴分层隔离**：
    - 主标题 / Hook 区：`transform_y` 锁定在 **`0.55 ~ 0.70`**（中上/顶部区域）。
    - 副标题 / 辅助标注：`transform_y` 锁定在 **`0.30 ~ 0.45`**（中部区域）。
    - 口播字幕 / 底部解说：`transform_y` 锁定在 **`-0.60 ~ -0.72`**（底部安全区，避开平台底部 UI 遮挡）。
  - **时间轴顺序硬隔离 (Time Range Gap)**：
    - 同一轨道内相邻文本片段，下一个片段的 `start_time` 必须 `≥` 前一个片段的 `start_time + duration`。
    - 片段间需预留 **`≥ 50,000 us (0.05s)`** 时间缓冲区间，严禁时间戳重叠。

#### 3. 修正 3：动态字号自适应与平台 UI 遮挡避让（Dynamic Scaling & Safety Zone）
- **自查问题**：不同字数应用统一花字预设时拉伸变形，或文字落在抖音/小红书底部评论点赞点赞 UI 遮挡区。
- **强制规则**：
  - **动态缩放系数**：若单段文本字数 `L > 10` 字，字号缩放比例按 `scale_x = scale_y = min(1.0, 10.0 / L)` 自动等比向下微调，防止大字打满画面。
  - **UI 遮挡避让黑区**：顶部避开系统状态栏（`Y > 0.8`），底部避开小红书/抖音评论点赞面板（`Y < -0.75`）及右侧侧边栏互动区（`X > 0.75`）。

---

## 6 大内置文本/标题变体预设 (Text Preset Matrix)

> ⭐️ **Creator OS 3.5 默认首选：`06_peak_design_tech`（Peak Design 极简工业科技小字）**

| 变体编码 | 预设名称 | 适用场景 | 颜色与排版规范 (Face + Background + Shadow) |
| :--- | :--- | :--- | :--- |
| `06_peak_design_tech` ⭐ | **Peak Design 极简工业科技小字 (默认)** | 核心卖点卡片、工业设计细节、摄影数码参数解读 | **4.8pt 纯白晶体字** + **52% 半透黑圆角胶囊底衬** + 柔和硬影，双行结构（`// SPEC XX : TITLE` + 中文卖点），9:16 安全区 `Y = -0.68`，渐显/渐隐呼吸动效 |
| `01_pulp_amber` | **昆丁复古橙红** | 视频大片头、强视觉开场 Hook | 暖金橙色 `#FF8C00` + 纯血红硬影 `#D31400` |
| `02_tech_silver` | **极简科技纯银** | 高端数码展示、苹果冷光风 | 纯银晶白 `#F2F4F8` + 科技发光蓝 `#0066FF` |
| `03_champagne_gold` | **奢华香槟金** | 质感配件、限定版标语、品牌LOGO | 香槟软金 `#F3E5AB` + 沉稳炭黑 `#1A1A1A` |
| `04_cyber_neon` | **潮酷霓虹粉紫** | 潮牌联名、IG 潮流短视频、Night Mode | 霓虹玫红 `#FF007F` + 暗夜紫蓝 `#1A0826` |
| `05_clean_subtitle` | **高对比口播字幕**| 通篇解说、细节文字标注、快速阅读 | 纯白 `#FFFFFF` + 纯黑高对比硬边 `#000000` |

---

## 常用预设母版工程
* `《剪辑母版_IG科技时尚版》` (包含 3D 运镜与 ASMR 音效轨)

---

## ⚠️ 核心避坑（Default Troubleshooting Rules）

1. **模板占位符 → 媒体丢失**:
   - 修改脚本必须遍历 `materials.videos`，检查 `path` 字段非占位符，并按 `material_name` 重新映射真实绝对路径。

2. **三文件同步写回**:
   - `Timelines/<SubID>/template.json`
   - `Timelines/<SubID>/draft_content.json`
   - `draft_content.json`（草稿根目录）

3. **版本时间戳强刷**:
   - `data["update_time"] = int(time.time() * 1_000_000)`

4. **备份勿清除（.backup 目录）**:
   - 剪映高版本会在打开草稿时从 `.backup` 自动还原；若要让修改生效，须在写入后清除 `.backup` 目录，或改为新建草稿。

5. **加密 draft_content.json**:
   - 剪映高版本的根目录 `draft_content.json` 和部分 `.bak` 文件为加密格式（header 非 JSON），无法直接解析；始终优先操作 `Timelines/<SubID>/template.json`（通常为明文）。

6. **零硬编码模板字幕法则**:
   - 彻底禁止使用代码预设/营销模板字幕（如 `⚡ //` 或旧产品描述）。每次收到新产品，必须先调用网络搜索工具（`search_web`）检索该特定产品的真实参数与特点，结合真实观察生成客观字幕。

7. **多切片关键帧物理源对齐法则 (Source-Aligned Time Offsets)**:
   - 剪映对分割后的视频切片，其关键帧 `time_offset` 必须相对于源媒体物理起点：`time_offset = source_start_us + local_offset_us`。严禁传入切片内部相对 0，否则后续所有片段动画都会因“播放时关键帧已过期”而失效。

8. **属性互斥防崩溃法则 (Scale Property Mutex)**:
   - `uniform_scale` 与 `scale_x/scale_y` 严格互斥，严禁在同一片段内混写，否则剪映必报「草稿内容已损坏」。统一使用 `KP.scale_x` + `KP.scale_y` 组合。

9. **IG 复合呼吸防眩晕法则 (IG Natural Breathing)**:
   - 避免机械式的高频震颤重复。单镜头控制在 2.0s ~ 3.2s，按 8 大镜头类型（`fast_hook`, `hook_opening`, `detail_macro`, `cinematic_pan`, `unboxing_action`, `overview`, `ending`）交替推拉，配合 `-0.8° ~ +0.6°` 3D 微倾斜与 Y 轴 4% 安全区偏移。

