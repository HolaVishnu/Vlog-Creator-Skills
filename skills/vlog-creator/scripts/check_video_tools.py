"""Check whether common local video tools are available."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def _version(binary: str) -> str | None:
    path = shutil.which(binary)
    if path is None:
        return None
    try:
        completed = subprocess.run(
            [binary, "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return path
    first_line = (completed.stdout or completed.stderr).splitlines()
    return first_line[0] if first_line else path


def inspect_tools() -> dict:
    """Return availability for the tools this skill can use directly."""
    ffmpeg = _version("ffmpeg")
    ffprobe = _version("ffprobe")
    return {
        "version": 1,
        "tools": {
            "ffmpeg": {"available": ffmpeg is not None, "version": ffmpeg},
            "ffprobe": {"available": ffprobe is not None, "version": ffprobe},
        },
        "can_inventory_media": ffprobe is not None,
        "can_render_rough_cut": ffmpeg is not None and ffprobe is not None,
    }


def _parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Report whether FFmpeg and FFprobe are available."
    )


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    try:
        parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    json.dump(inspect_tools(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
