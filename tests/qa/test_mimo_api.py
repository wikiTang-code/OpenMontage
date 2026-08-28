import os, sys, io, requests, json, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MIMO_KEY = "tp-cnavc5c5n5w3g310grrw6x94rvturlewhsrpjazvet3n2mvi"
BASE_URL = "https://api.xiaomimimo.com/v1"

# Test 1: Text generation (chat completions)
print("=" * 60)
print("[TEST 1] MiMo Text Generation (mimo-v2.5-pro)")
print("=" * 60)
r1 = requests.post(f"{BASE_URL}/chat/completions",
    headers={"api-key": MIMO_KEY, "Content-Type": "application/json"},
    json={
        "model": "mimo-v2.5-pro",
        "messages": [{"role": "user", "content": "Say hello in Chinese, one sentence only."}],
        "max_completion_tokens": 100, "temperature": 0.7, "stream": False
    }, timeout=30)
print(f"Status: {r1.status_code}")
if r1.status_code == 200:
    data = r1.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    print(f"[PASS] Response: {content}")
else:
    print(f"[FAIL] {r1.text[:300]}")

# Test 2: TTS (mimo-v2.5-tts)
print("\n" + "=" * 60)
print("[TEST 2] MiMo TTS (mimo-v2.5-tts)")
print("=" * 60)

# Try OpenAI-compatible /audio/speech endpoint
r2 = requests.post(f"{BASE_URL}/audio/speech",
    headers={"api-key": MIMO_KEY, "Content-Type": "application/json"},
    json={
        "model": "mimo-v2.5-tts",
        "input": "Hello, welcome to OpenMontage video platform.",
        "voice": "alloy"
    }, timeout=30)
print(f"Status: {r2.status_code}")
if r2.status_code == 200:
    os.makedirs("projects/mimo-test", exist_ok=True)
    with open("projects/mimo-test/test_tts.mp3", "wb") as f:
        f.write(r2.content)
    size_kb = len(r2.content) / 1024
    print(f"[PASS] Audio saved: projects/mimo-test/test_tts.mp3 ({size_kb:.1f} KB)")
else:
    print(f"[FAIL] {r2.text[:300]}")

# Test 3: Check if image generation endpoint exists
print("\n" + "=" * 60)
print("[TEST 3] MiMo Image Generation (check endpoint)")
print("=" * 60)
r3 = requests.post(f"{BASE_URL}/images/generations",
    headers={"api-key": MIMO_KEY, "Content-Type": "application/json"},
    json={"model": "mimo-image", "prompt": "a cute cat", "n": 1, "size": "1024x1024"},
    timeout=15)
print(f"Status: {r3.status_code}")
if r3.status_code == 200:
    print("[PASS] Image generation available!")
else:
    print(f"[INFO] Image generation not available: {r3.text[:200]}")

# Test 4: List available models
print("\n" + "=" * 60)
print("[TEST 4] MiMo Available Models")
print("=" * 60)
r4 = requests.get(f"{BASE_URL}/models",
    headers={"api-key": MIMO_KEY}, timeout=15)
print(f"Status: {r4.status_code}")
if r4.status_code == 200:
    models = r4.json().get("data", [])
    print(f"[PASS] Found {len(models)} models:")
    for m in models:
        print(f"  - {m.get('id', 'unknown')}")
else:
    print(f"[FAIL] {r4.text[:200]}")
