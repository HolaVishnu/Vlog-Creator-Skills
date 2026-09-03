"""Render a deterministic, non-destructive vlog rough cut from manifest v1."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile


class ManifestError(ValueError):
    """Raised when a rough-cut manifest or source probe is invalid."""


class RenderError(RuntimeError):
    """Raised when FFmpeg rendering or output verification fails."""


@dataclass(frozen=True)
class Clip:
    """One source range selected for the rough cut."""

    id: str
    path: Path
    in_time: float
    out_time: float
    has_audio: bool


@dataclass(frozen=True)
class Settings:
    """Normalized render settings from manifest v1."""

    width: int
    height: int
    fps: float
    sample_rate: int


def selected_duration(clips: list[Clip]) -> float:
    """Return the total selected runtime in seconds."""
    return sum(clip.out_time - clip.in_time for clip in clips)


def load_manifest(path: Path) -> dict:
    """Load a JSON manifest and require a top-level object."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ManifestError(f"Could not read manifest {path}: {error}") from error
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ManifestError(f"Manifest {path} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise ManifestError("Manifest must be a top-level JSON object.")
    return data


def _run_probe(command: list[str], subject: Path) -> dict:
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as error:
        raise ManifestError(
            f"FFprobe executable {command[0]!r} was not found; install FFprobe and try again."
        ) from error
    except OSError as error:
        raise ManifestError(f"FFprobe could not inspect {subject}: {error}") from error

    if completed.returncode != 0:
        details = (completed.stderr or "").strip() or "no diagnostic output"
        raise ManifestError(
            f"FFprobe failed for {subject} (exit {completed.returncode}): {details}"
        )
    try:
        result = json.loads(completed.stdout)
    except (TypeError, json.JSONDecodeError) as error:
        raise ManifestError(f"FFprobe returned invalid JSON for {subject}.") from error
    if not isinstance(result, dict):
        raise ManifestError(f"FFprobe returned invalid JSON for {subject}.")
    return result


def probe_has_audio(path: Path, ffprobe: str = "ffprobe") -> bool:
    """Return whether FFprobe finds an audio stream in one source file."""
    result = _run_probe(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "json",
            str(path),
        ],
        path,
    )
    streams = result.get("streams")
    return isinstance(streams, list) and any(
        isinstance(stream, dict) and stream.get("codec_type") == "audio"
        for stream in streams
    )


def _finite_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        number = float(value)
    except OverflowError:
        return None
    return number if math.isfinite(number) else None


def _integer_setting(
    settings: dict, name: str, lower: int, upper: int, errors: list[str]
) -> int | None:
    value = settings.get(name)
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        errors.append(f"settings.{name} must be an integer from {lower} to {upper}.")
        return None
    return value


def _even_dimension_setting(
    settings: dict, name: str, lower: int, upper: int, errors: list[str]
) -> int | None:
    value = _integer_setting(settings, name, lower, upper, errors)
    if value is not None and value % 2 != 0:
        errors.append(f"settings.{name} must be an even integer for MP4/H.264 output.")
        return None
    return value


def _fps_setting(settings: dict, errors: list[str]) -> float | None:
    fps = _finite_number(settings.get("fps"))
    if fps is None or not 1 <= fps <= 120:
        errors.append("settings.fps must be a finite number from 1 to 120.")
        return None
    return fps


def _raise_validation_errors(errors: list[str]) -> None:
    if errors:
        numbered = "\n".join(
            f"{index}. {message}" for index, message in enumerate(errors, start=1)
        )
        raise ManifestError(f"Invalid manifest:\n{numbered}")


def validate_manifest(
    data: dict, base_dir: Path, ffprobe: str = "ffprobe"
) -> tuple[Settings, list[Clip]]:
    """Validate all manifest fields, resolve sources, and probe their audio."""
    if not isinstance(data, dict):
        raise ManifestError("Invalid manifest:\n1. Manifest must be a top-level object.")

    errors: list[str] = []
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        errors.append("version must be the integer 1.")

    raw_settings = data.get("settings")
    settings: Settings | None = None
    if not isinstance(raw_settings, dict):
        errors.append("settings must be an object.")
    else:
        width = _even_dimension_setting(raw_settings, "width", 320, 7680, errors)
        height = _even_dimension_setting(raw_settings, "height", 240, 4320, errors)
        fps = _fps_setting(raw_settings, errors)
        sample_rate = _integer_setting(
            raw_settings, "sample_rate", 8000, 192000, errors
        )
        if (
            width is not None
            and height is not None
            and fps is not None
            and sample_rate is not None
        ):
            settings = Settings(width, height, fps, sample_rate)

    raw_clips = data.get("clips")
    if not isinstance(raw_clips, list) or not raw_clips:
        errors.append("clips must be a non-empty list.")
        raw_clips = []

    clips: list[Clip] = []
    seen_ids: set[str] = set()
    resolved_base = base_dir.resolve()
    for index, raw_clip in enumerate(raw_clips, start=1):
        prefix = f"clips[{index - 1}]"
        starting_error_count = len(errors)
        if not isinstance(raw_clip, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        clip_id = raw_clip.get("id")
        if not isinstance(clip_id, str) or not clip_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string.")
        elif clip_id in seen_ids:
            errors.append(f"{prefix}.id must be unique; duplicate {clip_id!r}.")
        else:
            seen_ids.add(clip_id)

        raw_path = raw_clip.get("path")
        path: Path | None = None
        if not isinstance(raw_path, str) or not raw_path.strip():
            errors.append(f"{prefix}.path must be a non-empty string.")
        else:
            try:
                candidate = Path(raw_path)
                path = (
                    candidate.resolve()
                    if candidate.is_absolute()
                    else (resolved_base / candidate).resolve()
                )
                if not path.is_file():
                    errors.append(f"{prefix}.path must reference an existing regular file: {path}")
            except (OSError, RuntimeError, ValueError) as error:
                errors.append(f"{prefix}.path is invalid: {error}")
                path = None

        in_time = _finite_number(raw_clip.get("in"))
        if in_time is None or in_time < 0:
            errors.append(f"{prefix}.in must be a finite number greater than or equal to zero.")

        out_time = _finite_number(raw_clip.get("out"))
        if out_time is None:
            errors.append(f"{prefix}.out must be a finite number.")
        elif in_time is not None and out_time <= in_time:
            errors.append(f"{prefix}.out must be greater than in.")

        if len(errors) != starting_error_count:
            continue
        assert isinstance(clip_id, str)
        assert path is not None
        assert in_time is not None
        assert out_time is not None
        try:
            has_audio = probe_has_audio(path, ffprobe)
        except ManifestError as error:
            errors.append(f"{prefix} ({clip_id}) could not be probed: {error}")
            continue
        clips.append(Clip(clip_id, path, in_time, out_time, has_audio))

    _raise_validation_errors(errors)
    assert settings is not None
    return settings, clips


def _format_number(value: float) -> str:
    return format(float(value), ".15g")


def build_ffmpeg_command(
    clips: list[Clip],
    settings: Settings,
    output: Path,
    ffmpeg: str = "ffmpeg",
) -> list[str]:
    """Build one FFmpeg argument list and concat filter graph."""
    if not clips:
        raise ManifestError("clips must be a non-empty list.")

    resolved_output = output.resolve()
    for clip in clips:
        if clip.path.resolve() == resolved_output:
            raise ManifestError("output path must not be the same as a source path.")

    command = [ffmpeg, "-nostdin", "-n"]
    for clip in clips:
        command.extend(["-i", str(clip.path)])

    width = str(settings.width)
    height = str(settings.height)
    fps = _format_number(settings.fps)
    sample_rate = str(settings.sample_rate)
    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, clip in enumerate(clips):
        in_time = _format_number(clip.in_time)
        out_time = _format_number(clip.out_time)
        duration = _format_number(clip.out_time - clip.in_time)
        filters.append(
            f"[{index}:v]trim=start={in_time}:end={out_time},"
            "setpts=PTS-STARTPTS,"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={fps}[v{index}]"
        )
        if clip.has_audio:
            filters.append(
                f"[{index}:a]atrim=start={in_time}:end={out_time},"
                "asetpts=PTS-STARTPTS,"
                f"aresample={sample_rate},"
                f"aformat=sample_rates={sample_rate}:channel_layouts=stereo[a{index}]"
            )
        else:
            filters.append(
                f"anullsrc=channel_layout=stereo:sample_rate={sample_rate},"
                f"atrim=duration={duration},asetpts=PTS-STARTPTS[a{index}]"
            )
        concat_inputs.extend([f"[v{index}]", f"[a{index}]"])

    filters.append(
        "".join(concat_inputs)
        + f"concat=n={len(clips)}:v=1:a=1[outv][outa]"
    )
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            "-f",
            "mp4",
            str(output),
        ]
    )
    return command


def _diagnostic_tail(value: str | None, limit: int = 4000) -> str:
    details = (value or "").strip()
    if not details:
        return "no diagnostic output"
    return details[-limit:]


def run_ffmpeg(command: list[str]) -> None:
    """Execute one FFmpeg argument list without a shell."""
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as error:
        raise RenderError(
            f"FFmpeg executable {command[0]!r} was not found; install FFmpeg and try again."
        ) from error
    except UnicodeError as error:
        raise RenderError(f"FFmpeg diagnostics could not be decoded: {error}") from error
    except OSError as error:
        raise RenderError(f"FFmpeg could not start: {error}") from error
    if completed.returncode != 0:
        details = _diagnostic_tail(completed.stderr)
        raise RenderError(
            f"FFmpeg failed with exit code {completed.returncode}: {details}"
        )


def probe_output(output: Path, ffprobe: str = "ffprobe") -> dict:
    """Probe an output file and return normalized duration and stream records."""
    try:
        result = _run_probe(
            [
                ffprobe,
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(output),
            ],
            output,
        )
    except ManifestError as error:
        raise RenderError(str(error)) from error

    raw_format = result.get("format")
    raw_duration = raw_format.get("duration") if isinstance(raw_format, dict) else None
    try:
        duration = float(raw_duration) if raw_duration is not None else None
    except (OverflowError, TypeError, ValueError):
        duration = None
    if duration is not None and not math.isfinite(duration):
        duration = None
    streams = result.get("streams")
    return {
        "duration": duration,
        "streams": streams if isinstance(streams, list) else [],
    }


def _stream_fps(stream: dict) -> float | None:
    for key in ("avg_frame_rate", "r_frame_rate"):
        raw = stream.get(key)
        if not raw or raw == "0/0":
            continue
        try:
            fps = float(Fraction(str(raw)))
        except (OverflowError, ValueError, ZeroDivisionError):
            continue
        if math.isfinite(fps) and fps > 0:
            return fps
    return None


def decode_output(output: Path, ffmpeg: str = "ffmpeg") -> None:
    """Require FFmpeg to decode the whole output without emitting errors."""
    command = [ffmpeg, "-v", "error", "-i", str(output), "-f", "null", "-"]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as error:
        raise RenderError(
            f"FFmpeg executable {ffmpeg!r} was not found; install FFmpeg and try again."
        ) from error
    except OSError as error:
        raise RenderError(f"FFmpeg could not verify {output}: {error}") from error
    if completed.returncode != 0:
        details = _diagnostic_tail(completed.stderr)
        raise RenderError(
            f"Output verification failed: full decode failed with exit code {completed.returncode}: {details}"
        )


def verify_output(
    output: Path,
    settings: Settings,
    expected_duration: float,
    ffprobe: str = "ffprobe",
    ffmpeg: str | None = None,
) -> dict:
    """Require a non-empty MP4 matching the manifest's expected output."""
    if output.suffix.lower() != ".mp4":
        raise RenderError("Output verification failed: output filename must end with .mp4.")
    try:
        if not output.is_file():
            raise RenderError(f"Output verification failed: file does not exist: {output}")
        if output.stat().st_size <= 0:
            raise RenderError(f"Output verification failed: file is empty: {output}")
    except OSError as error:
        raise RenderError(f"Output verification failed for {output}: {error}") from error

    probe = probe_output(output, ffprobe)
    streams = probe.get("streams")
    if not isinstance(streams, list):
        streams = []
    video_stream = next(
        (
            stream
            for stream in streams
            if isinstance(stream, dict) and stream.get("codec_type") == "video"
        ),
        None,
    )
    audio_stream = next(
        (
            stream
            for stream in streams
            if isinstance(stream, dict) and stream.get("codec_type") == "audio"
        ),
        None,
    )
    duration = _finite_number(probe.get("duration"))
    observed_fps = _stream_fps(video_stream) if isinstance(video_stream, dict) else None
    duration_tolerance = max(0.25, 2 / settings.fps)
    errors = []
    if video_stream is None:
        errors.append("a video stream is required")
    else:
        if video_stream.get("width") != settings.width:
            errors.append(f"width must be {settings.width}")
        if video_stream.get("height") != settings.height:
            errors.append(f"height must be {settings.height}")
        if observed_fps is None or abs(observed_fps - settings.fps) > 0.01:
            errors.append(f"frame rate must be {settings.fps:g} fps")
    if audio_stream is None:
        errors.append("an audio stream is required")
    if duration is None or duration <= 0:
        errors.append("duration must be greater than zero")
    elif abs(duration - expected_duration) > duration_tolerance:
        errors.append(
            f"duration must be within {duration_tolerance:.3f}s of {expected_duration:.3f}s"
        )
    if errors:
        raise RenderError("Output verification failed: " + "; ".join(errors) + ".")
    if ffmpeg is not None:
        decode_output(output, ffmpeg)
    return {
        "output": str(output.resolve()),
        "duration": duration,
        "expected_duration": expected_duration,
        "width": settings.width,
        "height": settings.height,
        "fps": settings.fps,
        "has_video": video_stream is not None,
        "has_audio": audio_stream is not None,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a verified MP4 rough cut from manifest v1."
    )
    parser.add_argument("manifest", type=Path, metavar="MANIFEST")
    parser.add_argument("output", type=Path, metavar="OUTPUT")
    parser.add_argument("--ffmpeg", default="ffmpeg", metavar="BINARY")
    parser.add_argument("--ffprobe", default="ffprobe", metavar="BINARY")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Render a manifest to a new MP4 and print its production report as JSON."""
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)

    output: Path = args.output
    if output.suffix.lower() != ".mp4":
        print("error: output must end with .mp4", file=sys.stderr)
        return 2
    if output.exists() or output.is_symlink():
        print(f"error: output already exists: {output}", file=sys.stderr)
        return 2

    try:
        data = load_manifest(args.manifest)
        settings, clips = validate_manifest(data, args.manifest.parent, args.ffprobe)
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise RenderError(f"Could not create output directory {output.parent}: {error}") from error

        with tempfile.TemporaryDirectory(
            prefix=".rough-cut-render-", dir=output.parent
        ) as workspace:
            temporary_output = Path(workspace) / output.name
            command = build_ffmpeg_command(
                clips, settings, temporary_output, args.ffmpeg
            )
            run_ffmpeg(command)
            report = verify_output(
                temporary_output,
                settings,
                selected_duration(clips),
                args.ffprobe,
                args.ffmpeg,
            )
            try:
                os.link(temporary_output, output)
            except FileExistsError as error:
                raise RenderError(
                    f"Output appeared during rendering and was not overwritten: {output}"
                ) from error
            except OSError as error:
                raise RenderError(f"Could not publish output {output}: {error}") from error
            report["output"] = str(output.resolve())
    except ManifestError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except RenderError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"error: could not clean temporary render workspace: {error}", file=sys.stderr)
        return 1

    report["clip_count"] = len(clips)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
