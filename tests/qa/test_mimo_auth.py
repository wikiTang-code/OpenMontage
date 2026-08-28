import os, sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MIMO_KEY = "tp-cnavc5c5n5w3g310grrw6x94rvturlewhsrpjazvet3n2mvi"
BASE_URL = "https://api.xiaomimimo.com/v1"

payload = {
    "model": "mimo-v2.5-pro",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_completion_tokens": 50, "stream": False
}

# Method 1: api-key header (from docs curl example)
print("Method 1: api-key header")
r1 = requests.post(f"{BASE_URL}/chat/completions",
    headers={"api-key": MIMO_KEY, "Content-Type": "application/json"},
    json=payload, timeout=15)
print(f"  Status: {r1.status_code} -> {r1.text[:150]}")

# Method 2: Authorization: Bearer (OpenAI SDK style)
print("\nMethod 2: Authorization: Bearer")
r2 = requests.post(f"{BASE_URL}/chat/completions",
    headers={"Authorization": f"Bearer {MIMO_KEY}", "Content-Type": "application/json"},
    json=payload, timeout=15)
print(f"  Status: {r2.status_code} -> {r2.text[:150]}")

# Method 3: Both headers
print("\nMethod 3: Both api-key and Bearer")
r3 = requests.post(f"{BASE_URL}/chat/completions",
    headers={"api-key": MIMO_KEY, "Authorization": f"Bearer {MIMO_KEY}", "Content-Type": "application/json"},
    json=payload, timeout=15)
print(f"  Status: {r3.status_code} -> {r3.text[:150]}")
