# -*- coding: utf-8 -*-
"""Verify Pexels Image API functionality."""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

from tools.tool_registry import registry
registry.discover()

def test_pexels():
    print("=" * 60)
    print("[TEST] Pexels Image Search & Download")
    print("=" * 60)
    
    tool = registry.get("pexels_image")
    if not tool:
        print("❌ 错误: 找不到 pexels_image 工具")
        return False
        
    status = tool.get_status()
    print(f"工具状态: {status}")
    if str(status) != "ToolStatus.AVAILABLE":
        print("❌ 错误: 工具状态不可用，请检查 PEXELS_API_KEY 是否正确载入")
        return False
        
    out_path = "projects/gemini-test/test_pexels.jpg"
    print("正在向 Pexels 请求检索词: 'office technology coding'...")
    
    result = tool.execute({
        "query": "office technology coding",
        "orientation": "landscape",
        "output_path": out_path
    })
    
    print(f"执行成功: {result.success}")
    if result.success:
        print(f"✅ 成功下载摄影图!")
        print(f"   摄影师: {result.data.get('photographer')}")
        print(f"   图片描述/ALT: {result.data.get('alt')}")
        print(f"   保存路径: {result.data.get('output')}")
        if os.path.exists(out_path):
            print(f"   文件大小: {os.path.getsize(out_path)/1024:.1f} KB")
        return True
    else:
        print(f"❌ 失败: {result.error}")
        return False

if __name__ == "__main__":
    test_pexels()
