"""Command line interface for africa-female-vc."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from .config import ALLOWED_DIFFUSION_STEPS, DEFAULT_DIFFUSION_STEPS, DEFAULT_VOICE, MODEL_REPO

AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".webm"}


def _steps(value: str) -> int:
    steps = int(value)
    if steps < 1:
        raise argparse.ArgumentTypeError("--diffusion-steps must be >= 1")
    if steps not in ALLOWED_DIFFUSION_STEPS:
        print(f"note: --diffusion-steps {steps} is outside the tested values {ALLOWED_DIFFUSION_STEPS}; 50 is recommended.",
              file=sys.stderr)
    return steps


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--voice", default=DEFAULT_VOICE, help="built-in voice (see `africa-female-vc voices`)")
    p.add_argument("--reference", default=None, help="use your own reference clip instead of a built-in voice")
    p.add_argument("--diffusion-steps", type=_steps, default=DEFAULT_DIFFUSION_STEPS, help="25 fast, 50 recommended, 100 slowest")
    p.add_argument("--model-repo", default=MODEL_REPO)
    p.add_argument("--token", default=None, help="HF token (falls back to $HF_TOKEN)")
    p.add_argument("--no-install-deps", action="store_true", help="skip installing Seed-VC requirements")
    p.add_argument("-v", "--verbose", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="africa-female-vc", description="Voice conversion into African female voices.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("voices", help="list the built-in voices")

    one = sub.add_parser("convert-file", help="convert a single audio file")
    one.add_argument("source")
    one.add_argument("-o", "--output", default="converted.wav")
    _common(one)

    loc = sub.add_parser("convert-local", help="convert audio files and/or folders")
    loc.add_argument("inputs", nargs="+")
    loc.add_argument("-o", "--output-dir", required=True)
    loc.add_argument("--overwrite", action="store_true")
    _common(loc)
    return parser


def _converter(args):
    from .engine import VoiceConverter

    return VoiceConverter(voice=args.voice, diffusion_steps=args.diffusion_steps, model_repo=args.model_repo,
                          token=args.token or os.environ.get("HF_TOKEN"), install_deps=not args.no_install_deps)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if getattr(args, "verbose", False) else logging.INFO, format="%(levelname)s %(message)s")

    if args.command == "voices":
        from .voices import list_voices

        for vid, meta in sorted(list_voices().items()):
            print(f"{vid:20s} {meta['description']:62s} (recorded in {meta['recorded_in']})")
        return 0

    import soundfile as sf

    if not args.reference:
        from .voices import resolve_voice

        try:
            args.voice = resolve_voice(args.voice)
        except KeyError as exc:
            print(f"error: {exc.args[0]}", file=sys.stderr)
            return 2
    conv = _converter(args)
    if args.command == "convert-file":
        wav, sr = conv.convert_file(args.source, voice=args.voice, reference=args.reference)
        sf.write(args.output, wav, sr)
        print(f"wrote {args.output} ({len(wav) / sr:.2f}s @ {sr} Hz)")
        return 0

    if args.command == "convert-local":
        files = []
        for raw in args.inputs:
            p = Path(raw).expanduser()
            files += sorted(f for f in (p.rglob("*") if p.is_dir() else [p]) if f.is_file() and f.suffix.lower() in AUDIO_SUFFIXES)
        out = Path(args.output_dir).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        done = 0
        for i, src in enumerate(files, 1):
            dst = out / (src.stem + ".wav")
            if dst.exists() and not args.overwrite:
                continue
            try:
                wav, sr = conv.convert_file(src, voice=args.voice, reference=args.reference)
                sf.write(dst, wav, sr)
                done += 1
                logging.info("[%d/%d] %s -> %s", i, len(files), src.name, dst)
            except Exception as exc:  # one bad file shouldn't end a long run
                logging.warning("[%d/%d] FAILED %s: %s", i, len(files), src.name, exc)
        print(f"converted {done} file(s) into {out}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
