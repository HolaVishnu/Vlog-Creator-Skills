"""Create a deterministic, non-destructive inventory of media files."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from fractions import Fraction


SUPPORTED_SUFFIXES = frozenset(
    {
        ".mp4",
        ".mov",
        ".m4v",
        ".mkv",
        ".webm",
        ".avi",
        ".mts",
        ".m2ts",
        ".wav",
        ".m4a",
        ".aac",
        ".mp3",
        ".flac",
        ".aiff",
        ".aif",
        ".ogg",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".tif",
        ".tiff",
        ".heic",
        ".heif",
    }
)


class ProbeError(RuntimeError):
    """Raised when FFprobe cannot inspect one media file."""


def discover_media(inputs: list[Path]) -> list[Path]:
    """Return supported input files, resolved, deduplicated, and sorted."""
    found: set[Path] = set()
    for input_path in inputs:
        path = input_path.resolve()
        if path.is_file():
            candidates = (path,)
        elif path.is_dir():
            candidates = path.rglob("*")
        else:
            continue
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES:
                found.add(candidate.resolve())
    return sorted(found, key=lambda path: (str(path).casefold(), str(path)))


def _parse_fps(value: object) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        fps = float(Fraction(str(value)))
    except (OverflowError, ValueError, ZeroDivisionError):
        return None
    return fps if math.isfinite(fps) else None


def _number(value: object) -> float | None:
    try:
        number = float(value) if value is not None else None
    except (OverflowError, TypeError, ValueError):
        return None
    return number if number is not None and math.isfinite(number) else None


def _orientation(width: object, height: object) -> str | None:
    if not isinstance(width, int) or not isinstance(height, int):
        return None
    if width > height:
        return "landscape"
    if height > width:
        return "portrait"
    return "square"


def probe_media(path: Path, ffprobe: str = "ffprobe") -> dict:
    """Inspect one file with FFprobe and return normalized media metadata."""
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-of",
        "json",
        str(path),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as error:
        raise ProbeError(
            f"FFprobe executable {ffprobe!r} was not found; install FFprobe and try again."
        ) from error
    except OSError as error:
        raise ProbeError(f"FFprobe could not inspect {path}: {error}") from error

    if completed.returncode != 0:
        details = completed.stderr.strip() or "no diagnostic output"
        raise ProbeError(
            f"FFprobe failed for {path} (exit {completed.returncode}): {details}"
        )
    try:
        probe = json.loads(completed.stdout)
    except (TypeError, json.JSONDecodeError) as error:
        raise ProbeError(f"FFprobe returned invalid JSON for {path}.") from error

    streams = probe.get("streams") if isinstance(probe, dict) else None
    if not isinstance(streams, list):
        raise ProbeError(f"FFprobe returned no stream list for {path}.")
    video = next(
        (stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "video"),
        None,
    )
    audio = next(
        (stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "audio"),
        None,
    )
    if video is None and audio is None:
        raise ProbeError(f"FFprobe found no video or audio stream in {path}.")
    format_data = probe.get("format") if isinstance(probe.get("format"), dict) else {}
    width = video.get("width") if video else None
    height = video.get("height") if video else None
    return {
        "duration": _number(format_data.get("duration")),
        "width": width if isinstance(width, int) else None,
        "height": height if isinstance(height, int) else None,
        "fps": _parse_fps(video.get("avg_frame_rate")) if video else None,
        "video_codec": video.get("codec_name") if video else None,
        "audio_codec": audio.get("codec_name") if audio else None,
        "has_audio": audio is not None,
        "orientation": _orientation(width, height),
    }


def _clip_record(identifier: str, path: Path) -> dict:
    return {
        "id": identifier,
        "path": str(path),
        "status": "error",
        "duration": None,
        "width": None,
        "height": None,
        "fps": None,
        "video_codec": None,
        "audio_codec": None,
        "has_audio": False,
        "orientation": None,
    }


def build_inventory(inputs: list[Path], ffprobe: str = "ffprobe") -> dict:
    """Build an inventory while retaining a record for every probe failure."""
    clips = []
    for index, path in enumerate(discover_media(inputs), start=1):
        clip = _clip_record(f"A{index:03d}", path)
        try:
            clip.update(probe_media(path, ffprobe))
            clip["status"] = "ok"
        except ProbeError as error:
            clip["error"] = str(error)
        clips.append(clip)
    return {"version": 1, "clips": clips}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a JSON inventory of media files.")
    parser.add_argument("inputs", nargs="+", metavar="INPUT")
    parser.add_argument("--output", type=Path, metavar="PATH")
    parser.add_argument("--ffprobe", default="ffprobe", metavar="BINARY")
    return parser


def _validate_inputs(inputs: list[str]) -> list[Path] | None:
    paths = [Path(value) for value in inputs]
    for path in paths:
        if not path.exists():
            print(f"error: input does not exist: {path}", file=sys.stderr)
            return None
        if not (path.is_file() or path.is_dir()):
            print(f"error: input is not a file or directory: {path}", file=sys.stderr)
            return None
    return paths


def main(argv: list[str] | None = None) -> int:
    """Run the CLI without ever overwriting an existing output file."""
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)

    inputs = _validate_inputs(args.inputs)
    if inputs is None:
        return 2
    if args.output is not None and args.output.exists():
        print(f"error: output already exists: {args.output}", file=sys.stderr)
        return 2

    inventory = build_inventory(inputs, args.ffprobe)
    rendered = json.dumps(inventory, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
        return 0

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(rendered)
    except FileExistsError:
        print(f"error: output already exists: {args.output}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"error: could not create output {args.output}: {error}", file=sys.stderr)
        return 2
    print(args.output, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
