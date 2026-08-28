import os, sys, io, requests, json, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MIMO_KEY = "tp-cnavc5c5n5w3g310grrw6x94rvturlewhsrpjazvet3n2mvi"
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

print("=" * 60)
print("[TEST] Token Plan: TTS via Chat Completions")
print("=" * 60)

# 使用 OpenAI Chat Completion 格式的音频生成 payload
payload = {
    "model": "mimo-v2.5-tts",
    "messages": [
        {
            "role": "assistant",
            "content": "欢迎使用 OpenMontage 视频创作平台。这是通过小米 MiMo 进行的语音合成测试。"
        }
    ],
    # 启用音频输出配置
    "modalities": ["audio", "text"],
    "audio": {
        "voice": "mimo_default", # 或者使用 mimo-v2.5-tts 支持的默认 voice
        "format": "mp3"
    }
}

r = requests.post(f"{BASE_URL}/chat/completions",
    headers={"api-key": MIMO_KEY, "Content-Type": "application/json"},
    json=payload, timeout=30)

print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    # 检查返回的数据中是否包含音频字段
    # 根据 OpenAI 的音频返回格式，一般在 choices[0].message.audio 字段中
    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})
    audio_data = message.get("audio", {})
    
    if audio_data and "data" in audio_data:
        audio_bytes = base64.b64decode(audio_data["data"])
        os.makedirs("projects/mimo-test", exist_ok=True)
        out_path = "projects/mimo-test/test_tts_mimo_chat.mp3"
        with open(out_path, "wb") as f:
            f.write(audio_bytes)
        print(f"[PASS] Audio saved to: {out_path} ({len(audio_bytes)/1024:.1f} KB)")
    else:
        print("[FAIL] Response does not contain audio data.")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
else:
    print(f"[FAIL] Response: {r.text[:1000]}")
