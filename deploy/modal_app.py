"""Modal deployment: public voice-conversion API for the demo Space.

    modal deploy deploy/modal_app.py

Endpoints (CORS-enabled for the Hugging Face Space):
    GET  /health   -> {"status": "ok", ...}   (also wakes a cold container)
    GET  /voices   -> built-in voices
    POST /convert  -> multipart: file=<audio>, voice=<voice id>[, diffusion_steps=25|50]  => audio/wav

L4 GPU, scales to zero after 5 idle minutes. Model weights are cached in a
Modal Volume so only the very first start downloads them.
"""

from pathlib import Path

import modal

PKG_DIR = Path(__file__).resolve().parent.parent / "src" / "africa_female_vc"
SEEDVC_COMMIT = "51383efd921027683c89e5348211d93ff12ac2a8"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_SECONDS = 30.0

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "libsndfile1")
    .run_commands(
        "git clone https://github.com/Plachtaa/seed-vc.git /opt/afvc/seed-vc",
        f"git -C /opt/afvc/seed-vc checkout {SEEDVC_COMMIT}",
        "pip install -r /opt/afvc/seed-vc/requirements.txt",
    )
    .pip_install("fastapi[standard]", "python-multipart")
    .env({"AFRICA_FEMALE_VC_HOME": "/opt/afvc", "HF_HOME": "/cache/hf", "PYTHONPATH": "/root/pkg"})
    .add_local_dir(str(PKG_DIR), remote_path="/root/pkg/africa_female_vc")
)

app = modal.App("africa-female-vc", image=image)
hf_cache = modal.Volume.from_name("africa-female-vc-hf-cache", create_if_missing=True)


@app.cls(gpu="L4", scaledown_window=300, timeout=600, max_containers=3, volumes={"/cache/hf": hf_cache})
class Converter:
    @modal.enter()
    def load(self):
        from africa_female_vc.engine import VoiceConverter

        self.vc = VoiceConverter(install_deps=False)
        self.vc.load()
        hf_cache.commit()

    @modal.asgi_app()
    def api(self):
        import io
        import subprocess
        import tempfile

        import soundfile as sf
        from fastapi import FastAPI, File, Form, HTTPException, UploadFile
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import Response

        from africa_female_vc.voices import list_voices, resolve_voice

        web = FastAPI(title="africa-female-vc")
        web.add_middleware(
            CORSMiddleware,
            # static Spaces are served from https://<owner>-<space>.static.hf.space
            allow_origin_regex=r"https://([a-z0-9-]+\.)*(hf\.space|huggingface\.co)",
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

        @web.get("/health")
        def health():
            return {"status": "ok", "voices": len(list_voices()), "max_seconds": MAX_SECONDS}

        @web.get("/voices")
        def voices():
            return {vid: {k: m[k] for k in ("description", "recorded_in", "pitch_hz", "duration", "utmos")}
                    for vid, m in list_voices().items()}

        @web.post("/convert")
        async def convert(file: UploadFile = File(...), voice: str = Form("clear-high-slow"), diffusion_steps: int = Form(50)):
            try:
                voice = resolve_voice(voice)  # ids, or aliases such as the language a voice was recorded in
            except KeyError:
                raise HTTPException(400, f"unknown voice {voice!r}")
            if diffusion_steps not in (25, 50):
                raise HTTPException(400, "diffusion_steps must be 25 or 50")
            data = await file.read()
            if len(data) > MAX_UPLOAD_BYTES:
                raise HTTPException(413, "file larger than 10 MB")
            with tempfile.TemporaryDirectory() as tmp:
                raw, wav = Path(tmp) / "upload", Path(tmp) / "source.wav"
                raw.write_bytes(data)
                # normalise anything (webm/opus from the browser, mp3, m4a ...) to mono 22.05 kHz wav
                r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ac", "1", "-ar", "22050", str(wav)],
                                   capture_output=True)
                if r.returncode != 0:
                    raise HTTPException(400, "could not decode audio")
                if sf.info(str(wav)).duration > MAX_SECONDS:
                    raise HTTPException(413, f"audio longer than {MAX_SECONDS:.0f} s")
                out, sr = self.vc.convert_file(wav, voice=voice, diffusion_steps=diffusion_steps)
            buf = io.BytesIO()
            sf.write(buf, out, sr, format="WAV")
            return Response(buf.getvalue(), media_type="audio/wav")

        return web
