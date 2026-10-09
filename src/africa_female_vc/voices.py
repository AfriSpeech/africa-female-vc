"""Built-in reference voices shipped with the package.

Voices are not tied to languages: the model has no language input, so any
voice can speak converted audio in any language. The 21 voices are real
speakers drawn from the training data (one from each language's portion of
AfriSpeech/africa-female-speech-v2-best60), named by how they sound. The
language each was recorded in is kept as metadata and as an alias.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path


def _voices_dir() -> Path:
    return Path(str(resources.files("africa_female_vc") / "voices"))


def list_voices() -> dict[str, dict]:
    """``{voice_id: {description, recorded_in, aliases, pitch_hz, utmos, duration, ...}}``."""
    return json.loads((_voices_dir() / "voices.json").read_text(encoding="utf-8"))


def resolve_voice(voice: str) -> str:
    """Return the canonical voice id for an id or alias (e.g. the language it was recorded in)."""
    voices = list_voices()
    key = voice.strip().lower()
    if key in voices:
        return key
    for vid, meta in voices.items():
        if key in meta.get("aliases", []):
            return vid
    raise KeyError(f"unknown voice {voice!r}; choose one of: {', '.join(sorted(voices))}")


def voice_path(voice: str) -> Path:
    """Path of a built-in voice's reference wav."""
    vid = resolve_voice(voice)
    return _voices_dir() / list_voices()[vid]["file"]
