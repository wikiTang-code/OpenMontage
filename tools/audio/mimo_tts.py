"""Xiaomi MiMo text-to-speech provider tool."""

from __future__ import annotations

import os
import time
import base64
from pathlib import Path
from typing import Any
import requests

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class MiMoTTS(BaseTool):
    name = "mimo_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "mimo"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set the MIMO_API_KEY environment variable:\n"
        "  export MIMO_API_KEY=your_tp_key_here\n"
        "Get a subscription key at https://platform.xiaomimimo.com/"
    )
    fallback = "edge_tts"
    fallback_tools = ["edge_tts", "piper_tts"]
    agent_skills = ["mimo-docs"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
    ]
    supports = {
        "voice_cloning": True,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
    }
    best_for = [
        "high-quality Chinese speech synthesis",
        "voice cloning and tone custom design",
    ]
    not_good_for = [
        "fully offline production",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "voice": {
                "type": "string",
                "default": "mimo_default",
                "description": "MiMo voice name (e.g. mimo_default)",
            },
            "model": {
                "type": "string",
                "default": "mimo-v2.5-tts",
                "description": "MiMo speech model",
            },
            "format": {
                "type": "string",
                "default": "mp3",
                "enum": ["mp3", "wav"],
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["text", "voice", "model", "format"]
    side_effects = ["writes audio file to output_path", "calls MiMo API"]
    user_visible_verification = ["Listen to generated audio for intelligibility and tone"]

    def get_status(self) -> ToolStatus:
        if os.environ.get("MIMO_API_KEY"):
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # Token Plan provides flat subscriptions, meaning 0 marginal cost
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if not os.environ.get("MIMO_API_KEY"):
            return ToolResult(success=False, error="No MiMo API key found. " + self.install_instructions)

        start = time.time()
        try:
            result = self._generate(inputs)
        except Exception as exc:
            return ToolResult(success=False, error=f"MiMo TTS failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = self.estimate_cost(inputs)
        return result

    def _generate(self, inputs: dict[str, Any]) -> ToolResult:
        from tools.analysis.audio_probe import probe_duration

        api_key = os.environ.get("MIMO_API_KEY")
        # Token Plan China Cluster endpoint
        base_url = os.environ.get("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
        
        text = inputs["text"]
        model = inputs.get("model", "mimo-v2.5-tts")
        voice = inputs.get("voice", "mimo_default")
        fmt = inputs.get("format", "mp3")
        output_path = Path(inputs.get("output_path", f"mimo_tts.{fmt}"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "assistant",
                    "content": text
                }
            ],
            "modalities": ["audio", "text"],
            "audio": {
                "voice": voice,
                "format": fmt
            }
        }

        r = requests.post(
            f"{base_url}/chat/completions",
            headers={"api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        if r.status_code != 200:
            return ToolResult(success=False, error=f"MiMo API returned error {r.status_code}: {r.text}")

        data = r.json()
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        audio_data = message.get("audio", {})

        if not audio_data or "data" not in audio_data:
            return ToolResult(success=False, error=f"MiMo API response did not contain audio data. Response: {data}")

        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data["data"])
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        audio_duration = probe_duration(output_path)

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": model,
                "voice": voice,
                "format": fmt,
                "text_length": len(text),
                "audio_duration_seconds": round(audio_duration, 2) if audio_duration else None,
                "output": str(output_path),
            },
            artifacts=[str(output_path)],
            model=model,
        )
