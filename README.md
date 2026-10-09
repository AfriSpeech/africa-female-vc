# africa-female-vc

Voice conversion into **21 African female voices**. Give it any speech - a file,
a folder, a recording - pick a voice, and get the same words spoken in that voice.

Built on [Seed-VC](https://github.com/Plachtaa/seed-vc), fine-tuned on
[AfriSpeech/africa-female-speech-v2-best60](https://huggingface.co/datasets/AfriSpeech/africa-female-speech-v2-best60)
(the cleanest hour of each language: Demucs-cleaned, UTMOS-ranked).

- **Model:** [AfriSpeech/africa-female-vc](https://huggingface.co/AfriSpeech/africa-female-vc)
- **Try it:** [AfriSpeech/africa-female-vc-demo](https://huggingface.co/spaces/AfriSpeech/africa-female-vc-demo)

## The voices

One speaker per language, shipped with the package in
[`src/africa_female_vc/voices/`](src/africa_female_vc/voices) - click a name to listen.

| Voice (`--voice`) | Language | Preview | Length | UTMOS |
|---|---|---|---:|---:|
| `amharic` | Amharic | [amharic.wav](src/africa_female_vc/voices/amharic.wav) | 8.3 s | 3.78 |
| `chichewa` | Chichewa | [chichewa.wav](src/africa_female_vc/voices/chichewa.wav) | 9.3 s | 4.10 |
| `hausa` | Hausa | [hausa.wav](src/africa_female_vc/voices/hausa.wav) | 13.8 s | 4.24 |
| `igbo` | Igbo | [igbo.wav](src/africa_female_vc/voices/igbo.wav) | 9.3 s | 4.13 |
| `kinyarwanda` | Kinyarwanda | [kinyarwanda.wav](src/africa_female_vc/voices/kinyarwanda.wav) | 8.8 s | 4.11 |
| `kirundi` | Kirundi | [kirundi.wav](src/africa_female_vc/voices/kirundi.wav) | 9.2 s | 4.08 |
| `ndebele` | Ndebele | [ndebele.wav](src/africa_female_vc/voices/ndebele.wav) | 8.1 s | 4.04 |
| `oromo` | Oromo | [oromo.wav](src/africa_female_vc/voices/oromo.wav) | 8.2 s | 3.84 |
| `sepedi` | Sepedi | [sepedi.wav](src/africa_female_vc/voices/sepedi.wav) | 8.3 s | 3.93 |
| `sesotho` | Sesotho | [sesotho.wav](src/africa_female_vc/voices/sesotho.wav) | 9.0 s | 3.89 |
| `setswana` | Setswana | [setswana.wav](src/africa_female_vc/voices/setswana.wav) | 10.0 s | 3.83 |
| `shona` | Shona | [shona.wav](src/africa_female_vc/voices/shona.wav) | 10.3 s | 4.23 |
| `swahili` | Swahili | [swahili.wav](src/africa_female_vc/voices/swahili.wav) | 8.8 s | 4.28 |
| `swati` | Swati | [swati.wav](src/africa_female_vc/voices/swati.wav) | 9.2 s | 3.99 |
| `tigrinya` | Tigrinya | [tigrinya.wav](src/africa_female_vc/voices/tigrinya.wav) | 9.5 s | 3.37 |
| `tsonga` | Tsonga | [tsonga.wav](src/africa_female_vc/voices/tsonga.wav) | 8.4 s | 4.02 |
| `twi` | Twi | [twi.wav](src/africa_female_vc/voices/twi.wav) | 11.3 s | 4.36 |
| `venda` | Venda | [venda.wav](src/africa_female_vc/voices/venda.wav) | 11.4 s | 4.21 |
| `xhosa` | Xhosa | [xhosa.wav](src/africa_female_vc/voices/xhosa.wav) | 13.5 s | 4.25 |
| `yoruba` | Yoruba | [yoruba.wav](src/africa_female_vc/voices/yoruba.wav) | 9.7 s | 4.23 |
| `zulu` | Zulu | [zulu.wav](src/africa_female_vc/voices/zulu.wav) | 8.9 s | 4.13 |

Each was picked as the highest-UTMOS 8-15 s clip of its language (among clips
Demucs barely had to clean). Any other clip works as a voice too: pass `--reference`.

## Install

```bash
pip install git+https://github.com/AfriSpeech/africa-female-vc
```

Seed-VC is not on PyPI, so it is cloned into `~/.cache/africa-female-vc/` on first
use (pinned to commit `51383efd`) and its requirements installed. Set
`AFRICA_FEMALE_VC_HOME` to change that location, or pass `--no-install-deps` if you
manage the environment yourself. Install into a clean environment and let Seed-VC
pull the torch stack it expects. A GPU is strongly recommended (~6 GB VRAM).

## Use

```bash
africa-female-vc voices                                         # list the voices
africa-female-vc convert-file talk.wav --voice swahili -o talk_swahili.wav
africa-female-vc convert-local recordings/ -o converted/ --voice yoruba
africa-female-vc convert-file talk.wav --reference my_voice.wav -o out.wav   # any reference clip
```

```python
from africa_female_vc import VoiceConverter

vc = VoiceConverter(voice="twi")          # loads once, converts many
wav, sr = vc.convert_file("talk.wav")
wav, sr = vc.convert_file("talk.wav", voice="zulu")
```

`--diffusion-steps 50` is the default (25 is faster but robotic, 100 slightly smoother).

## How it was trained

Seed-VC `seed-uvit-whisper-small-wavenet`, fine-tuned on the cleanest hour of each of 21 languages
(15,369 clips / 21.0 h, female speakers) for up to 30,000 steps at batch size 2. A checkpoint was saved every
200 steps and scored on a held-out set while training ran; the released checkpoint (step 25,200) was
then confirmed on an independent 105-clip set.

Content preservation (CER of omniASR-CTC-300M-v2 on the converted audio vs. the source transcript, 105 held-out
clips converted into unseen voices of the same language):

| | CER | above floor |
|---|---:|---:|
| Real recordings (floor) | 15.02 | - |
| Zero-shot Seed-VC | 22.57 | +7.55 |
| **africa-female-vc** | **18.73** | **+3.71** |

Per-language results and the training curve are on the [model card](https://huggingface.co/AfriSpeech/africa-female-vc).

## Hosted API

`deploy/modal_app.py` serves the model on a Modal L4 GPU (scales to zero) with
`GET /health`, `GET /voices` and `POST /convert` (multipart `file`, `voice`), and
powers the demo Space in [`space/`](space).

Public endpoint used by the demo: `https://michsethowusuwfp--africa-female-vc-converter-api.modal.run`
(30 s / 10 MB per request; the first request after an idle spell includes a ~1 min cold start).

```bash
modal deploy deploy/modal_app.py
```

## License

GPL-3.0, following upstream Seed-VC. Training data:
[AfriSpeech/africa-female-speech-v2](https://huggingface.co/datasets/AfriSpeech/africa-female-speech-v2) (CC BY-NC 4.0).
