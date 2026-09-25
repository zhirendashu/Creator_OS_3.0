# 🌲 植人大树 Creator OS 3.0 — 综合技术手册与项目实战经验全录 (Master Compendium)

> **版本定位**：Creator OS 3.0 / 3.5 自动化核心技术总结  
> **归档目的**：汇总自系统上线以来所有实战工程项目、底层崩溃原因、架构演进史、终极解决代码与关键备忘，作为未来全系统重构与统一整理的总依据。

---

## 📑 目录索引

1. [实操验证项目清单 (Projects Audited)](#1-实操验证项目清单-projects-audited)
2. [剪映版本加解密演进与 11.2+ 破解方案 (Draft Decryption Engine)](#2-剪映版本加解密演进与-112-破解方案-draft-decryption-engine)
3. [运镜与呼吸关键帧注入踩坑与成熟方案 (Breathing Motion Evolution)](#3-运镜与呼吸关键帧注入踩坑与成熟方案-breathing-motion-evolution)
4. [四大切片与辅助 Skill 管线集成 (Integrated Core Skills)](#4-四大切片与辅助-skill-管线集成-integrated-core-skills)
5. [Eagle 素材库与音效规范 (Eagle DAM & Sound Asset Pipeline)](#5-eagle-素材库与音效规范-eagle-dam--sound-asset-pipeline)
6. [草稿损坏与数据冲突防崩溃手册 (Crash Prevention & Schema Traps)](#6-草稿损坏与数据冲突防崩溃手册-crash-prevention--schema-traps)
7. [未来统一整理演进备忘 (Future Roadmap Notes)](#7-未来统一整理演进备忘-future-roadmap-notes)

---

## 1. 实操验证项目清单 (Projects Audited)

截至目前，已在以下具体产品与草稿工程中完成端到端落地检验：

| 工程 / 项目名称 | 涉及素材 / 场景 | 主要解决的问题与验证内容 | 对应沉淀脚本 |
|:---|:---|:---|:---|
| **《9月8日-副本》** | 曼比利 f-mini 铝合金机灵小开箱 | 11.4 最新版 DLL 加密草稿无损解密、去除刺猬高频密帧、改为首尾极简柔和等比缩放呼吸感 | `breath_inject_clean.py` |
| **《9月2日-副本》** | DJI Osmo Pocket 4 拍摄素材全片注入 | 多切片时间轴跨片段相位连续、正弦长周期呼吸波形注入 | `inject_breath_to_replica.py` |
| **《8月17日》** | Pk4 桌面多功能支架拆包 | 单长镜头（30s）内按亮相、特写、高光、收尾分段加权推拉呼吸曲线 | `inject_breath_keyframes.py` |
| **《35.4_AI全片段呼吸生效版》** | 35.4 定焦镜头开箱快切碎剪（1.2s一刀） | 首次攻克多切片「仅首片段生效，后续全部死值」问题，确立物理源对齐准则 | `build_source_aligned_draft.py` |
| **《斯丹德_DJI片头精剪版》** | 斯丹德配件开箱与 DJI 联名片头 | Eagle 真实漏光、Film Sound 1~7 真实快门音效与昆丁花字模板注入 | `build_enhanced_draft.py` |
| **《CCD模拟器_千禧年复古风》** | 复古数码相机胶片质感模拟 | DV 胶片噪波、VHS 故障叠加、自动配音与昆丁/复古调色 LUT 挂载 | `build_ccd_draft.py` |
| **《剪辑母版_IG科技时尚版》** | 通用标准产品开箱模版 | 3D 微倾斜（±0.8°）运镜与 IG Reels 4% Y 轴安全区避让、ASMR 开箱音轨 | `keyframe_utils.py` |

---

## 2. 剪映版本加解密演进与 11.2+ 破解方案 (Draft Decryption Engine)

### 2.1 格式演进历史
- **剪映 5.x ~ 9.x**：根目录 `draft_content.json` 为纯文本明文 JSON。
- **剪映 10.x ~ 11.1**：多时间线架构，主数据存放在 `Timelines/<ID>/template.json` 或 `draft_content.json`，依然为明文 JSON。
- **剪映 11.2 ~ 11.4+（当前最新版）**：全面推行**设备级 AES-128-CBC + Base64 强加密**。落地文件特征为以 `I5Bi`、`JHhe` 或 `H453Q` 等 Base64 乱码开头，外部直接解析会抛出 JSON 解析异常；直接新建或覆盖会被客户端校验为「草稿已损坏」。

### 2.2 终极破解解决方案：DLL 内存双向加解密
无需编译复杂的 C++ 工具或依赖第三方外部可执行程序，利用 Python 挂接剪映自身的 `videoeditor.dll`（由 `aoguai/pyJianYingDraft` 0.3 high-version fork 提供驱动）：

```python
from pyJianYingDraft import JianyingDraftCryptoCodec, DraftCryptoConfig
from pyJianYingDraft.draft_codec import write_json_object_with_codec

# 绑定本机安装的剪映主程序目录
JY_INSTALL_DIR = r"C:\Users\trees\AppData\Local\JianyingPro\Apps\11.4.1.14443"
codec = JianyingDraftCryptoCodec(DraftCryptoConfig(
    jy_install_dir=JY_INSTALL_DIR,
    isolated=True,
    validate_roundtrip=False,
    backup=False
))

# 1. 内存直接解密
raw_bytes = open("draft_content.json", "rb").read()
draft_dict = codec.decode(raw_bytes)  # 解出标准原生 JSON 字典

# 2. 对 draft_dict 进行业务注入 (如关键帧、花字、字幕) ...

# 3. 内存加密安全写回
write_json_object_with_codec("draft_content.json", draft_dict, content_codec=codec, indent=None)
```

### 2.3 必须同步的三文件体系与缓存清除
写回已有加密草稿时，必须**同时镜像同步**以下文件并清理缓存：
1. `Timelines/<SubID>/draft_content.json`（主数据）
2. `Timelines/<SubID>/template-2.tmp`（剪映临时还原锚点）
3. 草稿根目录 `draft_content.json`
4. **必须彻底删除 `.backup/` 文件夹**（否则剪映启动时会检测到未完成的修改并强行从旧备份还原，导致注入失效）。

---

## 3. 运镜与呼吸关键帧注入踩坑与成熟方案 (Breathing Motion Evolution)

### 3.1 踩坑史与演进阶段

| 演进阶段 | 实施方案 | 遇到的致命问题 / 现象 | 结论与修正 |
|:---|:---|:---|:---|
| **第一代：相对时间打帧** | 片段内部以 `local_t = 0 ~ duration` 打点 | 仅第 1 个片段生效，从第 2 片段起缩放全部锁死在固定数值 | **确定多切片物理源对齐准则**：剪映要求时间戳是 `source_start_us + local_offset` |
| **第二代：高频正弦采样点** | 每 0.35s 计算一个正弦采样点 | 时间线上密密麻麻如刺猬，画面高频晃动引起眩晕，且右侧面板无法正常交互 | **确立极简柔和原则**：拒绝刺猬帧，单片段只保留 2~3 个帧点，交由剪映原生贝塞尔插值 |
| **第三代：全局引用打架** | 往 `keyframes.videos` 和 `keyframe_refs` 乱塞节点 | 面板滑块空心、缩放无实际动态效果，或等比缩放互斥屏蔽 | **确立原生清洁准则**：直接在 `seg["common_keyframes"]` 挂载，`keyframe_refs` 置 None |

### 3.2 最终成熟方案：极简柔和等比呼吸感规范 (Golden Standard)

1. **等比缩放无缝支持**：
   - 同时向 `KFTypeScaleX` 与 `KFTypeScaleY` 注入相同的数值与时间轴；
   - `seg["uniform_scale"] = {}`（保留原生空字典），在剪映前台开启「等比缩放」时画面依然能平滑推拉。
2. **极简双点 / 三点点位布局**：
   - **短镜头（< 1.5s）**：
     - 起点：`1.000`
     - 终点：`1.055`（推）或 `1.000`（拉）
   - **长镜头（> 2.0s）**：
     - 起点：`1.000`（原比例）
     - 中点：`1.035`（微呼吸峰值，柔和起伏）
     - 终点：`1.055`（平滑收止）
3. **推拉交替节奏**：
   - 奇数片段推（Zoom In: `1.000 ➔ 1.055`）；
   - 偶数片段拉（Zoom Out: `1.055 ➔ 1.000`）；
   - 视觉上呈现摄影师呼吸感的自然张弛。

---

## 4. 四大切片与辅助 Skill 管线集成 (Integrated Core Skills)

在 `dazzling-noether` 中已完成全量集成的 4 大核心模块：

### 4.1 FFmpeg 预处理 (`ffmpeg_preprocessor.py`)
- **音轨提取**：`extract_audio_wav(input, output)`，提取 16kHz PCM 单声道 WAV，Whisper 识别效率最高。
- **静音无损擦除**：`remove_silence(input, output)`，基于 `silencedetect=noise=-30dB:d=0.5` 自动剔除口播空白与卡顿废话。
- **9:16 居中竖屏裁切**：`crop_to_vertical_916(input, output)`，自动将 16:9 横屏转为 1080x1920。

### 4.2 智能动态字幕 (`auto_subtitle.py`)
- **高光关键词感知**：自动匹配 `["开箱", "拆包", "实测", "质感", "4K", "胶片", "推荐", "铝合金"]`。
- **排版安全区**：字幕锁定在 `transform_y = -0.60 ~ -0.72`，严格避开抖音/小红书底部标题区与点赞面板。
- **单行字数控制**：单行上限 14~16 字，超长按标点自动换行；标题花字单行上限 7~8 字。

### 4.3 黄金高光切片 (`shorts_clipper.py`)
- 分析音视频转写文本，根据语气助词、高光情绪词与信息密度，自动筛选提取前 3 秒黄金钩子（Hook）及高光片段。
- 自动归档至工程目录 `02_黄金高光/`，为快切片头提供弹药。

### 4.4 科技动态卡片 Overlay (`motion_wrapper.py`)
- 自动生成 9:16 黑底高对比度参数对比卡片 MP4。
- 配合剪映 `Screen`（滤色）混合模式，自动将黑底过滤为透明，无缝贴合在产品视频上方。

---

## 5. Eagle 素材库与音效规范 (Eagle DAM & Sound Asset Pipeline)

### 5.1 Eagle API 调用标准
- **端口**：`http://localhost:41595/api/item/list?keyword=...`
- **库文件**：`X:\私人素材库.library` (206K+ 资产)
- **必备验证**：获得路径后，必须用 `os.path.exists()` 验证真实物理路径存在，排除占位符或已移动文件。

### 5.2 零废音与截断法则 (SFX Precision Rules)
- **拒绝电子合成音**：严禁使用廉价的电子 `whoosh`/`pop`/`snap`。
- **快门与真实触感音**：100% 使用真实的 `Film Sound 1~7` 与 `Paper Shuffle`（开箱纸盒摩擦）。
- **时长截断约束**：
  - 切点音效：`source_timerange.duration ≤ 1_200_000 us` (1.2s)
  - 文字/高光音效：`source_timerange.duration ≤ 800_000 us` (0.8s)
  - 音量比例：音效 volume 设为 `0.6 ~ 0.8`；背景音乐 BGM volume 设为 `≤ 0.35`。

---

## 6. 草稿损坏与数据冲突防崩溃手册 (Crash Prevention & Schema Traps)

在开发与自动化批量操作剪映过程中，必须避开的 5 大崩溃陷阱：

| 陷阱名称 | 引发行为 | 剪映报错表现 | 正确做法 |
|:---|:---|:---|:---|
| **属性互斥陷阱** | 同一片段同时写入 `uniform_scale` 开关与独立 `scale_x/y` 关键帧 | 「草稿内容已损坏，请联系客服」 | `uniform_scale` 设为 `{}` 原生字典，由 `common_keyframes` 内部对齐 ScaleX/Y 数值驱动 |
| **时间轴过期陷阱** | 多切片关键帧 `time_offset` 填切片相对时间（如 0） | 片段缩放死值不生效，面板菱形变灰 | 必须是绝对时间：`time_offset = source_start_us + local_offset` |
| **悬空素材引用** | `extra_material_refs` 填入了在 `materials` 中不存在的 UUID | 打开草稿直接崩溃闪退 | 修改前清洗，确保引用均在 `materials` 对应列表（`speeds`, `canvases` 等）中存在 |
| **缓存还原陷阱** | 修改了 JSON 但未删除工程目录下的 `.backup` | 重新打开草稿后自动还原为修改前的旧版本 | 每次保存后必须递归删除草稿目录与时间线目录下的所有 `.backup` 文件夹 |
| **混合模式黑屏陷阱** | 胶片漏光、VHS 噪波以 `normal` 模式全不透明叠加 | 主画面全黑，被覆盖素材完全遮挡 | 所有光效叠加层强制设置 `blend_mode = "screen"`（滤色）且时长 ≤ 1.5s |

---

## 7. 未来统一整理演进备忘 (Future Roadmap Notes)

供后续统一重构时的架构指导：

1. **统一 API 门面封装**：
   - 将 `breath_inject_clean.py`、`ffmpeg_preprocessor.py`、`auto_subtitle.py` 收敛为统一的 `CreatorOS` Python Package，对外只暴露一键式函数（如 `os_engine.process_project(draft_path)`）。
2. **多版本自动降级机制**：
   - 编写智能感知器：如果检测到草稿为明文 JSON（11.1 及以下），自动使用标准文件读写；如果检测到 `JHhe` / `I5Bi` 密文，自动切换至 `JianyingDraftCryptoCodec` 模式。
3. **镜头类型智能推断**：
   - 结合 Whisper 转写的台词内容自动推断镜头类型（提到“重量/外观”推断为细节特写，提到“包装/打开”推断为开箱动作），自适应匹配推拉速度与微旋转角度。
4. **统一草稿索引同步器**：
   - 将 `F:\trees\Documents\JianyingPro Drafts` 与 `AppData\Local\JianyingPro` 的双向同步封装为独立 Daemon 守护，确保任意一侧修改，另一侧实时无感更新。
