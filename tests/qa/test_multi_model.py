import os, sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv()

key = os.environ.get("GOOGLE_API_KEY")
models = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
    r = requests.post(url, json={"contents": [{"parts": [{"text": "hi"}]}]}, timeout=15)
    print(f"{m}: HTTP {r.status_code}")
    if r.status_code != 200:
        # Extract limit info
        text = r.text
        if "limit:" in text:
            idx = text.index("limit:")
            print(f"  -> {text[idx:idx+30]}")
    else:
        data = r.json()
        content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        print(f"  -> OK: {content[:50]}")
