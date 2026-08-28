import os, sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MIMO_KEY = "tp-cnavc5c5n5w3g310grrw6x94rvturlewhsrpjazvet3n2mvi"
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

# 尝试利用 OpenAI 兼容的 /audio/speech 接口来测试 mimo-v2.5-tts 语音合成
print("=" * 60)
print("[TEST] Token Plan: TTS (mimo-v2.5-tts)")
print("=" * 60)

r = requests.post(f"{BASE_URL}/audio/speech",
    headers={"api-key": MIMO_KEY, "Content-Type": "application/json"},
    json={
        "model": "mimo-v2.5-tts",
        "input": "欢迎使用 OpenMontage 平台。这是通过小米 MiMo 合成的语音声音。",
        "voice": "alloy"  # 或者是文档支持的默认发音人
    }, timeout=30)

print(f"Status: {r.status_code}")
if r.status_code == 200:
    os.makedirs("projects/mimo-test", exist_ok=True)
    out_path = "projects/mimo-test/test_tts_mimo.mp3"
    with open(out_path, "wb") as f:
        f.write(r.content)
    size_kb = len(r.content) / 1024
    print(f"[PASS] Audio saved to: {out_path} ({size_kb:.1f} KB)")
else:
    print(f"[FAIL] Response: {r.text[:500]}")
