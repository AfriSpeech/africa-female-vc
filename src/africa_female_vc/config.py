"""Defaults for africa-female-vc."""

from __future__ import annotations

SEEDVC_REPO = "https://github.com/Plachtaa/seed-vc.git"
# Pinned to the commit this project is tested against. Seed-VC's
# requirements.txt drives the whole dependency stack (torch 2.4.0,
# numpy==1.26.4, an older huggingface_hub API used by BigVGAN), so tracking
# its main branch means an upstream change can silently break installs.
SEEDVC_COMMIT = "51383efd921027683c89e5348211d93ff12ac2a8"

MODEL_REPO = "AfriSpeech/africa-female-vc"
MODEL_FILE = "ft_model.pth"
MODEL_CONFIG = "config_dit_mel_seed_uvit_whisper_small_wavenet.yml"

# 50 matches ghana-vc's tested default: 25 is audibly robotic, 100 only
# marginally better for roughly double the compute.
DEFAULT_DIFFUSION_STEPS = 50
ALLOWED_DIFFUSION_STEPS = (25, 50, 100)
DEFAULT_LENGTH_ADJUST = 1.0
DEFAULT_CFG_RATE = 0.7

DEFAULT_VOICE = "twi"
