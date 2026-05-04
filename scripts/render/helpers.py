from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Sequence


QUALITY_ALIASES = {
    "-ql": "480p15",
    "ql": "480p15",
    "low": "480p15",
    "480p15": "480p15",
    "-qm": "720p30",
    "qm": "720p30",
    "medium": "720p30",
    "720p30": "720p30",
    "-qh": "1080p60",
    "qh": "1080p60",
    "high": "1080p60",
    "1080p60": "1080p60",
    "-qk": "2160p60",
    "qk": "2160p60",
    "4k": "2160p60",
    "2160p60": "2160p60",
}
QUALITY_FLAGS_BY_DIR = {
    "480p15": "-ql",
    "720p30": "-qm",
    "1080p60": "-qh",
    "2160p60": "-qk",
}


def normalize_quality_dir(raw_value: str) -> str:
    normalized = QUALITY_ALIASES.get(raw_value.strip().lower())
    if normalized is None:
        raise SystemExit(
            f"Unsupported quality: {raw_value}\n"
            "Use -ql, -qm, -qh, -qk or 480p15/720p30/1080p60/2160p60."
        )
    return normalized


def quality_flag_for_dir(quality_dir: str) -> str:
    try:
        return QUALITY_FLAGS_BY_DIR[quality_dir]
    except KeyError as exc:
        raise SystemExit(
            f"Unsupported quality directory: {quality_dir}\n"
            "Use 480p15, 720p30, 1080p60, or 2160p60."
        ) from exc


def bootstrap_environment(repo_root: Path) -> None:
    uv_cache_dir = Path(os.environ.setdefault("UV_CACHE_DIR", str(repo_root / ".uv-cache")))
    mplconfigdir = Path(os.environ.setdefault("MPLCONFIGDIR", str(repo_root / ".mplconfig")))
    uv_cache_dir.mkdir(parents=True, exist_ok=True)
    mplconfigdir.mkdir(parents=True, exist_ok=True)


def section_quality_dir(videos_root: Path, output_dir: str, quality_dir: str) -> Path:
    return videos_root / output_dir / quality_dir


def section_clip_dir(videos_root: Path, output_dir: str, quality_dir: str) -> Path:
    return section_quality_dir(videos_root, output_dir, quality_dir) / "sections"


def clear_stale_section_clips(videos_root: Path, output_dir: str, quality_dir: str) -> Path:
    clips_dir = section_clip_dir(videos_root, output_dir, quality_dir)
    if clips_dir.exists():
        for path in sorted(clips_dir.rglob("*")):
            if path.is_file():
                path.unlink()
    return clips_dir


def delete_combined_scene_renders(videos_root: Path, output_dir: str, quality_dir: str) -> Path:
    quality_path = section_quality_dir(videos_root, output_dir, quality_dir)
    if quality_path.exists():
        for path in sorted(quality_path.glob("*.mp4")):
            path.unlink()
    return quality_path


def collect_concat_inputs(
    videos_root: Path,
    quality_dir: str,
    section_output_dirs: Sequence[str],
) -> list[Path]:
    clip_paths: list[Path] = []
    for section_output_dir in section_output_dirs:
        clips_dir = section_clip_dir(videos_root, section_output_dir, quality_dir)
        if not clips_dir.is_dir():
            raise SystemExit(f"Missing section directory: {clips_dir}")

        rendered_paths = sorted(
            path
            for path in clips_dir.glob("*.mp4")
            if not path.name.endswith("_autocreated.mp4")
        )
        if not rendered_paths:
            raise SystemExit(f"No section clips found under {clips_dir}")
        clip_paths.extend(path.resolve() for path in rendered_paths)
    return clip_paths


def resolve_output_path(repo_root: Path, output: str | Path | None, quality_dir: str) -> Path:
    if output is None:
        return (repo_root / "media" / "videos" / f"presentation_full_{quality_dir}.mp4").resolve()

    output_path = Path(output).expanduser()
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    return output_path.resolve()


def ensure_ffmpeg_available() -> str:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise SystemExit("ffmpeg is required but was not found in PATH.")
    return ffmpeg_path
