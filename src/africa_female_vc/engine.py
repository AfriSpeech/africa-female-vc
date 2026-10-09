"""Seed-VC engine wrapper.

Seed-VC ships as a git repository with an ``inference.py`` script rather than as
an installable package, and that script loads the checkpoint on every call. We
call the upstream ``load_models()`` a single time, cache the result, and
monkeypatch it so the upstream ``main()`` reuses the loaded models. The
conversion maths (chunking, overlap crossfade) stays exactly as upstream wrote
it, and the reference voice can change on every call.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
from argparse import Namespace
from pathlib import Path

import numpy as np

from .config import (
    DEFAULT_CFG_RATE,
    DEFAULT_DIFFUSION_STEPS,
    DEFAULT_LENGTH_ADJUST,
    DEFAULT_VOICE,
    MODEL_CONFIG,
    MODEL_FILE,
    MODEL_REPO,
    SEEDVC_COMMIT,
    SEEDVC_REPO,
)
from .voices import voice_path

log = logging.getLogger(__name__)


def _cache_root() -> Path:
    root = os.environ.get("AFRICA_FEMALE_VC_HOME")
    if root:
        return Path(root)
    return Path.home() / ".cache" / "africa-female-vc"


def ensure_seedvc(install_deps: bool = True) -> Path:
    """Clone Seed-VC into the cache directory (pinned commit) and return its path."""
    dest = _cache_root() / "seed-vc"
    if not (dest / "inference.py").exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        log.info("Cloning Seed-VC into %s", dest)
        subprocess.run(["git", "clone", SEEDVC_REPO, str(dest)], check=True)
        subprocess.run(["git", "-C", str(dest), "checkout", SEEDVC_COMMIT], check=True)
        if install_deps:
            log.info("Installing Seed-VC requirements")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(dest / "requirements.txt")],
                check=True,
            )
    return dest


class VoiceConverter:
    """Convert speech into one of the built-in voices, or any reference clip.

    Voices are independent of the input language: any voice can be used for speech in any language.

    Parameters
    ----------
    voice:
        Default built-in voice (``clear-high-slow``, ``warm-low``, ... see ``list_voices()``).
    diffusion_steps:
        50 recommended; 25 is faster but robotic, 100 slightly smoother.
    """

    def __init__(
        self,
        voice: str = DEFAULT_VOICE,
        diffusion_steps: int = DEFAULT_DIFFUSION_STEPS,
        model_repo: str = MODEL_REPO,
        length_adjust: float = DEFAULT_LENGTH_ADJUST,
        cfg_rate: float = DEFAULT_CFG_RATE,
        fp16: bool = True,
        token: str | None = None,
        install_deps: bool = True,
    ) -> None:
        self.voice = voice
        self.diffusion_steps = int(diffusion_steps)
        self.length_adjust = float(length_adjust)
        self.cfg_rate = float(cfg_rate)
        self.fp16 = bool(fp16)
        self.model_repo = model_repo
        self._token = token
        self._seed_dir = ensure_seedvc(install_deps=install_deps)
        self._inference = None
        self._loaded = False

    # -- model loading -----------------------------------------------------
    def load(self) -> None:
        """Download the checkpoint and load every model once. Idempotent."""
        if self._loaded:
            return
        from huggingface_hub import hf_hub_download

        kw = {"token": self._token} if self._token else {}
        self._cfg = hf_hub_download(self.model_repo, MODEL_CONFIG, **kw)
        self._ckpt = hf_hub_download(self.model_repo, MODEL_FILE, **kw)

        seed_dir = str(self._seed_dir)
        if seed_dir not in sys.path:
            sys.path.insert(0, seed_dir)
        cwd = os.getcwd()
        os.chdir(seed_dir)  # Seed-VC's modules import relative to its own root
        try:
            import inference as seedvc  # type: ignore

            log.info("Loading Seed-VC checkpoint (once)")
            models = seedvc.load_models(self._make_args("", str(voice_path(self.voice)), ""))
            seedvc.load_models = lambda _args, _m=models: _m
            self._inference = seedvc
        finally:
            os.chdir(cwd)
        self._loaded = True

    def _make_args(self, source, target, output, diffusion_steps=None) -> Namespace:
        return Namespace(
            source=source, target=target, output=output,
            diffusion_steps=int(diffusion_steps or self.diffusion_steps),
            length_adjust=self.length_adjust, inference_cfg_rate=self.cfg_rate,
            f0_condition=False, auto_f0_adjust=False, semi_tone_shift=0,
            checkpoint=getattr(self, "_ckpt", None), config=getattr(self, "_cfg", None), fp16=self.fp16,
        )

    # -- conversion --------------------------------------------------------
    def convert_file(
        self,
        path: str | os.PathLike,
        voice: str | None = None,
        reference: str | os.PathLike | None = None,
        diffusion_steps: int | None = None,
    ) -> tuple[np.ndarray, int]:
        """Convert an audio file. ``reference`` (any clip) overrides ``voice``.

        Returns ``(waveform, sample_rate)``.
        """
        import soundfile as sf

        self.load()
        target = Path(reference) if reference else voice_path(voice or self.voice)
        cwd = os.getcwd()
        os.chdir(self._seed_dir)
        tmp = tempfile.mkdtemp(prefix="africa-female-vc-")
        try:
            self._inference.main(self._make_args(str(Path(path).resolve()), str(target.resolve()), tmp, diffusion_steps))
            produced = sorted(Path(tmp).glob("*.wav"))
            if not produced:
                raise RuntimeError(f"Seed-VC produced no output for {path}")
            return sf.read(produced[0], dtype="float32")
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)

    def convert_array(self, audio: np.ndarray, sampling_rate: int, **kw) -> tuple[np.ndarray, int]:
        """Convert an in-memory waveform. Returns ``(waveform, sample_rate)``."""
        import soundfile as sf

        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        tmp = tempfile.mkdtemp(prefix="africa-female-vc-src-")
        try:
            src = Path(tmp) / "source.wav"
            sf.write(src, audio, sampling_rate)
            return self.convert_file(src, **kw)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
