"""africa-female-vc: voice conversion into African female voices (Seed-VC fine-tune)."""

from .config import DEFAULT_DIFFUSION_STEPS, MODEL_REPO
from .voices import list_voices, resolve_voice, voice_path

__all__ = ["VoiceConverter", "ensure_seedvc", "list_voices", "resolve_voice", "voice_path", "MODEL_REPO", "DEFAULT_DIFFUSION_STEPS"]
__version__ = "0.1.0"


def __getattr__(name):
    # engine imports numpy and may clone Seed-VC; keep `import africa_female_vc` light
    if name in ("VoiceConverter", "ensure_seedvc"):
        from . import engine

        return getattr(engine, name)
    raise AttributeError(name)
