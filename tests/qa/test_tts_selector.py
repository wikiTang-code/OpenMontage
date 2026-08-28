import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

from tools.tool_registry import registry
registry.discover()

def test_selector_with_mimo():
    print("=" * 60)
    print("[TEST 1] tts_selector using preferred_provider='mimo'")
    print("=" * 60)
    
    selector = registry.get("tts_selector")
    if not selector:
        print("❌ 错误: 找不到 tts_selector")
        return False
        
    out_path = "projects/mimo-test/test_selector_mimo.mp3"
    result = selector.execute({
        "text": "你好，这是通过选择器调用 MiMo 语音生成的音频测试。",
        "preferred_provider": "mimo",
        "output_path": out_path
    })
    
    print(f"执行状态: {result.success}")
    if result.success:
        print(f"✅ 成功! 实际使用提供商: {result.data.get('selected_provider')}")
        print(f"   输出路径: {result.data.get('output')}")
        print(f"   选择理由: {result.data.get('selection_reason')}")
        if os.path.exists(out_path):
            print(f"   文件大小: {os.path.getsize(out_path)/1024:.1f} KB")
        return True
    else:
        print(f"❌ 失败: {result.error}")
        return False

def test_selector_edge_directly():
    print("\n" + "=" * 60)
    print("[TEST 2] tts_selector using preferred_provider='edge' (free backup)")
    print("=" * 60)
    
    selector = registry.get("tts_selector")
    if not selector:
        print("❌ 错误: 找不到 tts_selector")
        return False
        
    out_path = "projects/mimo-test/test_selector_edge.mp3"
    result = selector.execute({
        "text": "你好，这是直接调用微软 Edge 免费语音合成的测试。",
        "preferred_provider": "edge",
        "output_path": out_path
    })
    
    print(f"执行状态: {result.success}")
    if result.success:
        print(f"✅ 成功! 实际使用提供商: {result.data.get('selected_provider')}")
        print(f"   输出路径: {result.data.get('output')}")
        if os.path.exists(out_path):
            print(f"   文件大小: {os.path.getsize(out_path)/1024:.1f} KB")
        return True
    else:
        print(f"❌ 失败: {result.error}")
        return False

def test_selector_fallback_to_edge():
    print("\n" + "=" * 60)
    print("[TEST 3] tts_selector automatic fallback (MiMo Key Invalid -> Edge)")
    print("=" * 60)
    
    # 临时备份真实的 MIMO_API_KEY
    orig_key = os.environ.get("MIMO_API_KEY")
    # 故意破坏 Key，模拟失效或网络崩溃状态
    os.environ["MIMO_API_KEY"] = "tp-invalidkey123456"
    
    try:
        selector = registry.get("tts_selector")
        out_path = "projects/mimo-test/test_selector_fallback.mp3"
        
        # 请求 preferred_provider="mimo"，但因为 key 不正当，应该抛出异常并自动 fallback 到 edge_tts
        result = selector.execute({
            "text": "因为小米秘钥失效，这条语音应该自动降级并使用微软免费合成。",
            "preferred_provider": "mimo",
            "output_path": out_path
        })
        
        print(f"执行状态: {result.success}")
        if result.success:
            print(f"✅ 成功! 实际使用提供商: {result.data.get('selected_provider')}")
            print(f"   输出路径: {result.data.get('output')}")
            if os.path.exists(out_path):
                print(f"   文件大小: {os.path.getsize(out_path)/1024:.1f} KB")
            return True
        else:
            print(f"❌ 失败: {result.error}")
            return False
            
    finally:
        # 恢复真实的 Key 保证不影响后续使用
        if orig_key:
            os.environ["MIMO_API_KEY"] = orig_key
        else:
            del os.environ["MIMO_API_KEY"]

if __name__ == "__main__":
    test_selector_with_mimo()
    test_selector_edge_directly()
    test_selector_fallback_to_edge()

