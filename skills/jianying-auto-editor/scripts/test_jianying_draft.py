import os
import sys
import pyJianYingDraft as pjy

def test_create_draft():
    # 剪映默认草稿保存路径
    default_draft_dir = os.path.expanduser("~/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft")
    
    if not os.path.exists(default_draft_dir):
        print(f"[-] 错误：找不到剪映草稿目录 {default_draft_dir}")
        return False
        
    print(f"[+] 剪映草稿目录: {default_draft_dir}")
    
    try:
        # 初始化草稿文件夹
        draft_folder = pjy.DraftFolder(default_draft_dir)
        draft_name = "Antigravity_AutoEdit_Test"
        
        # 创建新草稿工程 (1080x1920 30fps)
        script_proj = draft_folder.create_draft(draft_name, width=1080, height=1920, fps=30, allow_replace=True)
        
        # 追加字幕轨道
        script_proj.append_track(pjy.TrackSpec(pjy.TrackType.text, name="字幕轨"))
        
        # 添加测试字幕片段 (0 -> 5秒，微秒单位: 5000000)
        seg = pjy.TextSegment("Hello Antigravity 2.0! 剪映自动剪辑环境配置成功！", pjy.Timerange(0, 5000000))
        script_proj.add_segment(seg, track="字幕轨")
        
        # 保存草稿
        script_proj.save()
        
        target_path = os.path.join(default_draft_dir, draft_name)
        print(f"[✓] 测试草稿生成成功！项目路径: {target_path}")
        print(f"[✓] 请打开剪映专业版，首页中即可直接看到名为 '{draft_name}' 的工程。")
        return True
        
    except Exception as e:
        print(f"[-] 生成草稿时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_create_draft()
    sys.exit(0 if success else 1)
