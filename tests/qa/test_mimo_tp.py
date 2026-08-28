import os, sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MIMO_KEY = "tp-cnavc5c5n5w3g310grrw6x94rvturlewhsrpjazvet3n2mvi"
# 更改为 Token Plan 中国节点的 Base URL
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

payload = {
    "model": "mimo-v2.5-pro",
    "messages": [{"role": "user", "content": "Say hello in Chinese, one sentence only."}],
    "max_completion_tokens": 100,
    "temperature": 0.7,
    "stream": False
}

# Test 1: api-key header
print("=" * 60)
print("[TEST 1] Token Plan: api-key header")
print("=" * 60)
r1 = requests.post(f"{BASE_URL}/chat/completions",
    headers={"api-key": MIMO_KEY, "Content-Type": "application/json"},
    json=payload, timeout=15)
print(f"Status: {r1.status_code}")
print(f"Response: {r1.text[:300]}")

# Test 2: Authorization Bearer header
print("\n" + "=" * 60)
print("[TEST 2] Token Plan: Bearer header")
print("=" * 60)
r2 = requests.post(f"{BASE_URL}/chat/completions",
    headers={"Authorization": f"Bearer {MIMO_KEY}", "Content-Type": "application/json"},
    json=payload, timeout=15)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:300]}")
