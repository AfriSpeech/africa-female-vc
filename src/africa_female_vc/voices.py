"""Built-in reference voices: one female speaker per language, shipped with the package.

Each was chosen from AfriSpeech/africa-female-speech-v2-best60 as the highest-UTMOS
8-15 s clip of its language that Demucs barely had to clean.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path


def _voices_dir() -> Path:
    return Path(str(resources.files("africa_female_vc") / "voices"))


def list_voices() -> dict[str, dict]:
    """``{voice_id: {language, config, file, utmos, duration, transcript, ...}}``."""
    return json.loads((_voices_dir() / "voices.json").read_text(encoding="utf-8"))


def voice_path(voice: str) -> Path:
    """Path of a built-in voice's reference wav (raises with the valid names otherwise)."""
    voices = list_voices()
    key = voice.strip().lower()
    if key not in voices:
        # accept language names and dataset config names too ("Swahili", "swahili_swa")
        for vid, meta in voices.items():
            if key in (meta["language"].lower(), meta["config"].lower()):
                key = vid
                break
        else:
            raise KeyError(f"unknown voice {voice!r}; choose one of: {', '.join(sorted(voices))}")
    return _voices_dir() / voices[key]["file"]
