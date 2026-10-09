# africa-female-vc

Voice conversion into **21 African female voices**. Give it speech in any language - a file,
a folder, a recording - pick a voice, and get the same words spoken in that voice.

Built on [Seed-VC](https://github.com/Plachtaa/seed-vc), fine-tuned on
[AfriSpeech/africa-female-speech-v2-best60](https://huggingface.co/datasets/AfriSpeech/africa-female-speech-v2-best60)
(the cleanest hour of each language: Demucs-cleaned, UTMOS-ranked).

It is **not limited to those 21 languages**: voice conversion is audio-to-audio, so the words come from the
input speech and the voice from a reference clip - there is no text or language input to restrict it. The
21 training languages are the fine-tuning data; tested on **37 languages it never saw**, it still
beats zero-shot Seed-VC in 27 of them:

| | Languages | Floor (real audio) | Zero-shot Seed-VC | **africa-female-vc** | Fine-tuned better in |
|---|---:|---:|---:|---:|---:|
| **Out-of-domain** (never trained on) | 37 | 20.85 | 34.96 (+14.1) | **30.98 (+10.1)** | 27/37 |
| **Control** (training languages, new source) | 4 | 16.27 | 31.73 (+15.5) | **25.37 (+9.1)** | 3/4 |

(Character error rate after conversion, lower is better; brackets show points above the real-audio floor.
Details and per-language results on the
[model card](https://huggingface.co/AfriSpeech/africa-female-vc#out-of-domain-languages).)

- **Model:** [AfriSpeech/africa-female-vc](https://huggingface.co/AfriSpeech/africa-female-vc)
- **Try it:** [AfriSpeech/africa-female-vc-demo](https://huggingface.co/spaces/AfriSpeech/africa-female-vc-demo)

## The voices

**Voices are not tied to languages.** The model has no language input: it takes your audio (the words) and a
reference clip (the voice), so any voice can speak converted audio in any language - English into `warm-low`,
Swahili into `clear-high-slow`, anything into anything.

The 21 built-in voices are real speakers from the training data (one drawn from each language's portion, so the
set spans the whole dataset). They are named by how they sound - timbre, pitch, pace and intonation, measured
relative to each other - and ship with the package in
[`src/africa_female_vc/voices/`](src/africa_female_vc/voices). The language each was recorded in also works as
an alias (`--voice swahili` = `--voice clear-mid-steady`).

| Voice (`--voice`) | Sounds like | Recorded in | Preview |
|---|---|---|---|
| `bright-high` | bright timbre, high pitch (~220 Hz), steady pace, lively intonation | Yoruba | [bright-high.wav](src/africa_female_vc/voices/bright-high.wav) |
| `bright-high-calm` | bright timbre, high pitch (~243 Hz), quick pace, calm intonation | Oromo | [bright-high-calm.wav](src/africa_female_vc/voices/bright-high-calm.wav) |
| `bright-high-quick` | bright timbre, high pitch (~228 Hz), quick pace, calm intonation | Kinyarwanda | [bright-high-quick.wav](src/africa_female_vc/voices/bright-high-quick.wav) |
| `bright-low` | bright timbre, low pitch (~191 Hz), steady pace, calm intonation | Sesotho | [bright-low.wav](src/africa_female_vc/voices/bright-low.wav) |
| `bright-low-steady` | bright timbre, low pitch (~196 Hz), steady pace, calm intonation | Shona | [bright-low-steady.wav](src/africa_female_vc/voices/bright-low-steady.wav) |
| `bright-mid` | bright timbre, mid pitch (~207 Hz), slow pace, lively intonation | Swati | [bright-mid.wav](src/africa_female_vc/voices/bright-mid.wav) |
| `bright-mid-quick` | bright timbre, mid pitch (~215 Hz), quick pace, lively intonation | Zulu | [bright-mid-quick.wav](src/africa_female_vc/voices/bright-mid-quick.wav) |
| `clear-high` | clear timbre, high pitch (~230 Hz), slow pace, lively intonation | Tsonga | [clear-high.wav](src/africa_female_vc/voices/clear-high.wav) |
| `clear-high-slow` | clear timbre, high pitch (~261 Hz), slow pace, lively intonation | Twi | [clear-high-slow.wav](src/africa_female_vc/voices/clear-high-slow.wav) |
| `clear-low` | clear timbre, low pitch (~192 Hz), quick pace, calm intonation | Chichewa | [clear-low.wav](src/africa_female_vc/voices/clear-low.wav) |
| `clear-mid` | clear timbre, mid pitch (~203 Hz), slow pace, calm intonation | Kirundi | [clear-mid.wav](src/africa_female_vc/voices/clear-mid.wav) |
| `clear-mid-quick` | clear timbre, mid pitch (~210 Hz), quick pace, calm intonation | Ndebele | [clear-mid-quick.wav](src/africa_female_vc/voices/clear-mid-quick.wav) |
| `clear-mid-slow` | clear timbre, mid pitch (~204 Hz), slow pace, lively intonation | Xhosa | [clear-mid-slow.wav](src/africa_female_vc/voices/clear-mid-slow.wav) |
| `clear-mid-steady` | clear timbre, mid pitch (~209 Hz), steady pace, calm intonation | Swahili | [clear-mid-steady.wav](src/africa_female_vc/voices/clear-mid-steady.wav) |
| `warm-high` | warm timbre, high pitch (~217 Hz), quick pace, lively intonation | Hausa | [warm-high.wav](src/africa_female_vc/voices/warm-high.wav) |
| `warm-high-steady` | warm timbre, high pitch (~222 Hz), steady pace, calm intonation | Venda | [warm-high-steady.wav](src/africa_female_vc/voices/warm-high-steady.wav) |
| `warm-low` | warm timbre, low pitch (~167 Hz), slow pace, calm intonation | Tigrinya | [warm-low.wav](src/africa_female_vc/voices/warm-low.wav) |
| `warm-low-lively` | warm timbre, low pitch (~194 Hz), steady pace, lively intonation | Igbo | [warm-low-lively.wav](src/africa_female_vc/voices/warm-low-lively.wav) |
| `warm-low-quick` | warm timbre, low pitch (~197 Hz), quick pace, lively intonation | Setswana | [warm-low-quick.wav](src/africa_female_vc/voices/warm-low-quick.wav) |
| `warm-low-steady` | warm timbre, low pitch (~187 Hz), steady pace, lively intonation | Sepedi | [warm-low-steady.wav](src/africa_female_vc/voices/warm-low-steady.wav) |
| `warm-mid` | warm timbre, mid pitch (~209 Hz), slow pace, lively intonation | Amharic | [warm-mid.wav](src/africa_female_vc/voices/warm-mid.wav) |

Any other clip works as a voice too: pass `--reference`.

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
africa-female-vc convert-file talk.wav --voice warm-low -o talk_warm_low.wav
africa-female-vc convert-local recordings/ -o converted/ --voice bright-high
africa-female-vc convert-file talk.wav --reference my_voice.wav -o out.wav   # any reference clip
```

```python
from africa_female_vc import VoiceConverter

vc = VoiceConverter(voice="clear-high-slow")   # loads once, converts many
wav, sr = vc.convert_file("talk.wav")
wav, sr = vc.convert_file("talk.wav", voice="warm-low")
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
