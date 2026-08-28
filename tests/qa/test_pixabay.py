# -*- coding: utf-8 -*-
"""Verify Pixabay Image API functionality."""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

from tools.tool_registry import registry
registry.discover()

def test_pixabay():
    print("=" * 60)
    print("[TEST] Pixabay Image Search & Download")
    print("=" * 60)
    
    tool = registry.get("pixabay_image")
    if not tool:
        print("❌ 错误: 找不到 pixabay_image 工具")
        return False
        
    status = tool.get_status()
    print(f"工具状态: {status}")
    if str(status) != "ToolStatus.AVAILABLE":
        print("❌ 错误: 工具状态不可用，请检查 PIXABAY_API_KEY 是否正确载入")
        return False
        
    out_path = "projects/gemini-test/test_pixabay.jpg"
    print("正在向 Pixabay 请求检索词: 'nature landscape background'...")
    
    result = tool.execute({
        "query": "nature landscape background",
        "orientation": "horizontal",
        "output_path": out_path
    })
    
    print(f"执行成功: {result.success}")
    if result.success:
        print(f"✅ 成功下载摄影图!")
        print(f"   图片来源: {result.data.get('provider')}")
        print(f"   标签/Tags: {result.data.get('tags')}")
        print(f"   保存路径: {result.data.get('output')}")
        if os.path.exists(out_path):
            print(f"   文件大小: {os.path.getsize(out_path)/1024:.1f} KB")
        return True
    else:
        print(f"❌ 失败: {result.error}")
        return False

if __name__ == "__main__":
    test_pixabay()
