import os, sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv()

key = os.environ.get("GOOGLE_API_KEY")

# Test 1: Imagen via predict endpoint
print("=== Test Imagen (predict endpoint) ===")
url1 = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict"
r1 = requests.post(url1, headers={"Content-Type": "application/json", "x-goog-api-key": key},
    json={"instances": [{"prompt": "a cute cat"}], "parameters": {"sampleCount": 1, "aspectRatio": "1:1"}}, timeout=30)
print(f"Status: {r1.status_code}")
print(f"Response: {r1.text[:500]}")

# Test 2: Imagen via generateImages endpoint (newer)
print("\n=== Test Imagen (generateImages endpoint) ===")
url2 = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:generateImages?key={key}"
r2 = requests.post(url2, json={"prompt": "a cute cat", "config": {"numberOfImages": 1}}, timeout=30)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:500]}")

# Test 3: TTS via Cloud Text-to-Speech
print("\n=== Test Google Cloud TTS ===")
url3 = f"https://texttospeech.googleapis.com/v1beta1/text:synthesize?key={key}"
r3 = requests.post(url3, json={
    "input": {"text": "hello"},
    "voice": {"languageCode": "en-US", "name": "en-US-Studio-O"},
    "audioConfig": {"audioEncoding": "MP3"}
}, timeout=15)
print(f"Status: {r3.status_code}")
print(f"Response: {r3.text[:500]}")

# Test 4: TTS via Gemini native TTS (newer approach)
print("\n=== Test Gemini Native TTS (2.5-flash) ===")
url4 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
r4 = requests.post(url4, json={
    "contents": [{"parts": [{"text": "Say 'hello world' in a friendly tone"}]}],
    "generationConfig": {"responseMimeType": "audio/mp3"}
}, timeout=15)
print(f"Status: {r4.status_code}")
print(f"Response prefix: {r4.text[:300]}")
