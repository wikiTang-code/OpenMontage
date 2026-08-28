"""Microsoft Edge Text-to-Speech free provider tool."""

from __future__ import annotations

import os
import time
import asyncio
from pathlib import Path
from typing import Any

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


class EdgeTTS(BaseTool):
    name = "edge_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "edge"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Install edge-tts Python package:\n"
        "  pip install edge-tts"
    )
    fallback = "piper_tts"
    fallback_tools = ["piper_tts"]
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
    }
    best_for = [
        "free high-quality multilingual voiceovers",
        "zero-cost narration fallback",
    ]
    not_good_for = [
        "voice cloning",
        "fully offline production",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "voice": {
                "type": "string",
                "default": "zh-CN-XiaoxiaoNeural",
                "description": "Edge TTS voice name (e.g. zh-CN-XiaoxiaoNeural, zh-CN-YunxiNeural, en-US-AriaNeural)",
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["timeout"])
    idempotency_key_fields = ["text", "voice"]
    side_effects = ["writes audio file to output_path", "calls Edge TTS services"]
    user_visible_verification = ["Listen to generated audio for intelligibility"]

    def get_status(self) -> ToolStatus:
        try:
            import edge_tts  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(success=False, error="edge-tts package is not installed. " + self.install_instructions)

        start = time.time()
        try:
            # edge-tts is an async library, we run it in synchronous context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self._generate_async(inputs))
            finally:
                loop.close()
        except Exception as exc:
            return ToolResult(success=False, error=f"Edge TTS failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = 0.0
        return result

    async def _generate_async(self, inputs: dict[str, Any]) -> ToolResult:
        import edge_tts
        from tools.analysis.audio_probe import probe_duration

        text = inputs["text"]
        voice = inputs.get("voice", "zh-CN-XiaoxiaoNeural")
        
        # Mapping generic voices to Edge specific ones if needed
        if voice == "alloy" or voice == "mimo_default":
            # Fallback default voices
            voice = "zh-CN-XiaoxiaoNeural"

        output_path = Path(inputs.get("output_path", "edge_tts_output.mp3"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

        audio_duration = probe_duration(output_path)

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "voice": voice,
                "text_length": len(text),
                "audio_duration_seconds": round(audio_duration, 2) if audio_duration else None,
                "output": str(output_path),
                "format": "mp3",
            },
            artifacts=[str(output_path)],
            model=voice,
        )
