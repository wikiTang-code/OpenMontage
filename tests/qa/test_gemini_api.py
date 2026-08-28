# -*- coding: utf-8 -*-
"""Verify Gemini API Key cloud generation capabilities.

Tests:
1. Google Imagen 4.0 image generation
2. Google TTS speech synthesis
"""

import sys
import os
import io

# Fix Windows GBK encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dotenv import load_dotenv
load_dotenv()

from tools.tool_registry import registry
registry.discover()


def test_imagen():
    print("\n" + "=" * 60)
    print("[TEST 1] Google Imagen 4.0 Image Generation")
    print("=" * 60)

    tool = registry._tools.get("google_imagen")
    if not tool:
        print("[FAIL] google_imagen tool not found in registry")
        return False

    status = tool.get_status()
    print(f"Tool status: {status}")
    if str(status) != "ToolStatus.AVAILABLE":
        print("[FAIL] google_imagen not available, check GOOGLE_API_KEY")
        return False

    print("Calling Imagen 4.0...")
    print("Prompt: A cute robot reading a book in a cozy library, digital art, warm lighting")

    output_dir = os.path.join("projects", "gemini-test")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_imagen.png")

    result = tool.execute({
        "prompt": "A cute robot reading a book in a cozy library, digital art, warm lighting",
        "aspect_ratio": "16:9",
        "model": "imagen-4.0-generate-001",
        "output_path": output_path,
    })

    if result.success:
        print(f"[PASS] Image saved to: {result.data.get('output', output_path)}")
        print(f"  Model: {result.data.get('model')}")
        print(f"  Duration: {result.duration_seconds}s")
        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) / 1024
            print(f"  File size: {size_kb:.1f} KB")
        return True
    else:
        print(f"[FAIL] {result.error}")
        return False


def test_google_tts():
    print("\n" + "=" * 60)
    print("[TEST 2] Google TTS Speech Synthesis")
    print("=" * 60)

    tool = registry._tools.get("google_tts")
    if not tool:
        print("[FAIL] google_tts tool not found in registry")
        return False

    status = tool.get_status()
    print(f"Tool status: {status}")
    if str(status) != "ToolStatus.AVAILABLE":
        print("[FAIL] google_tts not available, check GOOGLE_API_KEY")
        return False

    print("Calling Google TTS...")
    print("Text: Welcome to OpenMontage video production platform.")

    output_dir = os.path.join("projects", "gemini-test")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_tts.mp3")

    result = tool.execute({
        "text": "Welcome to OpenMontage video production platform. AI helps you create amazing videos.",
        "language": "en-US",
        "output_path": output_path,
    })

    if result.success:
        print(f"[PASS] Audio saved to: {result.data.get('output', output_path)}")
        print(f"  Duration: {result.duration_seconds}s")
        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) / 1024
            print(f"  File size: {size_kb:.1f} KB")
        return True
    else:
        print(f"[FAIL] {result.error}")
        return False


if __name__ == "__main__":
    print("OpenMontage Gemini API Verification Test")
    print(f"GOOGLE_API_KEY set: {'YES' if os.environ.get('GOOGLE_API_KEY') else 'NO'}")

    results = {}
    results["imagen"] = test_imagen()
    results["tts"] = test_google_tts()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: [{status}]")

    all_passed = all(results.values())
    print(f"\n{'All tests passed! Cloud generation is ready.' if all_passed else 'Some tests failed, check logs above.'}")
    sys.exit(0 if all_passed else 1)
