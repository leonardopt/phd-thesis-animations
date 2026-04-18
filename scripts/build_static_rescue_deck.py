#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "cm"

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

try:
    from export_frame_screener_pdf import build_video_screen
    from export_last_frames_pdf import (
        DEFAULT_IMAGES_ROOT,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        VideoEntry,
        discover_videos,
        extract_last_frame,
    )
except ModuleNotFoundError:
    from scripts.export_frame_screener_pdf import build_video_screen
    from scripts.export_last_frames_pdf import (
        DEFAULT_IMAGES_ROOT,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        VideoEntry,
        discover_videos,
        extract_last_frame,
    )


DEFAULT_OUTPUT = REPO_ROOT / "media" / "pdfs" / "study_static_rescue_deck.pdf"
DEFAULT_OVERRIDES = REPO_ROOT / "assets" / "presentation_frame_overrides.toml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build an audience-ready static rescue deck PDF with one frame per "
            "Study 1/2 video."
        )
    )
    parser.add_argument(
        "--study",
        choices=("study1", "study2"),
        nargs="+",
        default=["study1", "study2"],
        help="Studies to include in the rescue deck (default: study1 study2).",
    )
    parser.add_argument(
        "--videos-root",
        type=Path,
        default=DEFAULT_VIDEOS_ROOT,
        help=f"Root directory containing study video folders (default: {DEFAULT_VIDEOS_ROOT}).",
    )
    parser.add_argument(
        "--images-root",
        type=Path,
        default=DEFAULT_IMAGES_ROOT,
        help=f"Root directory containing study still images (default: {DEFAULT_IMAGES_ROOT}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Destination rescue-deck PDF path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=DEFAULT_OVERRIDES,
        help=(
            "Optional TOML file with per-video frame overrides "
            f"(default: {DEFAULT_OVERRIDES})."
        ),
    )
    parser.add_argument(
        "--default-mode",
        choices=("last-stable", "first-stable", "last-frame"),
        default="last-stable",
        help="Fallback frame-selection rule when no override is present (default: last-stable).",
    )
    parser.add_argument(
        "--sample-fps",
        type=float,
        default=4.0,
        help="Sampling rate used while detecting stable holds (default: 4.0 fps).",
    )
    parser.add_argument(
        "--analysis-width",
        type=int,
        default=320,
        help="Width of sampled frames used for motion analysis (default: 320).",
    )
    parser.add_argument(
        "--min-still-seconds",
        type=float,
        default=0.5,
        help="Minimum stable-hold duration used by the screener heuristic (default: 0.5s).",
    )
    parser.add_argument(
        "--motion-threshold",
        type=float,
        default=None,
        help="Optional absolute motion threshold used by the screener heuristic.",
    )
    return parser.parse_args()


def load_overrides(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return {str(key): value for key, value in data.items() if isinstance(value, dict)}


def class_name_from_stem(stem: str) -> str:
    parts = stem.split("_", 1)
    if len(parts) == 2 and parts[0]:
        prefix = parts[0]
        if prefix[:-1].isdigit() and prefix[-1:].isalpha():
            return parts[1]
        if prefix.isdigit():
            return parts[1]
    return stem


def override_for_entry(
    overrides: dict[str, dict[str, object]],
    stem: str,
) -> dict[str, object] | None:
    return overrides.get(stem) or overrides.get(class_name_from_stem(stem))


def probe_duration_seconds(ffprobe_path: str, video_path: Path) -> float:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        error = result.stderr.strip() or "ffprobe could not read the file."
        raise RuntimeError(f"Could not probe duration for {video_path}: {error}")
    return float(result.stdout.strip())


def extract_frame_at_timestamp(
    ffmpeg_path: str,
    video_path: Path,
    timestamp_seconds: float,
    output_path: Path,
) -> None:
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{max(0.0, timestamp_seconds):.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not output_path.exists():
        error = result.stderr.strip() or "ffmpeg did not produce an output frame."
        raise RuntimeError(f"Could not extract frame from {video_path}: {error}")


def choose_override_timestamp(
    override: dict[str, object],
    screen_timestamps: list[float],
    duration_seconds: float,
) -> tuple[str, float | None]:
    mode = str(override.get("mode", "")).strip().lower()
    value = override.get("value")
    if mode == "timestamp":
        return (mode, float(value))
    if mode == "percent":
        return (mode, max(0.0, min(1.0, float(value))) * duration_seconds)
    if mode == "candidate_index":
        if not screen_timestamps:
            raise RuntimeError("candidate_index override requested, but no stable candidates were found.")
        index = int(value)
        if index < 1 or index > len(screen_timestamps):
            raise RuntimeError(
                f"candidate_index={index} is out of range for a video with {len(screen_timestamps)} candidates."
            )
        return (mode, screen_timestamps[index - 1])
    if mode == "last_frame":
        return (mode, None)
    raise RuntimeError(f"Unsupported override mode: {override.get('mode')!r}")


def choose_frame_timestamp(
    entry: VideoEntry,
    screen_timestamps: list[float],
    default_mode: str,
    override: dict[str, object] | None,
    ffprobe_path: str,
) -> tuple[str, float | None]:
    if override is not None:
        duration_seconds = probe_duration_seconds(ffprobe_path, entry.video_path)
        return choose_override_timestamp(override, screen_timestamps, duration_seconds)
    if default_mode == "last-frame":
        return ("last-frame", None)
    if not screen_timestamps:
        return ("last-frame", None)
    if default_mode == "first-stable":
        return ("first-stable", screen_timestamps[0])
    return ("last-stable", screen_timestamps[-1])


def add_rescue_page(
    pdf: PdfPages,
    image_path: Path,
    page_number: int,
    page_count: int,
) -> None:
    image = plt.imread(image_path)
    fig = plt.figure(figsize=(13.333, 7.5), facecolor="white")
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.9])
    ax.imshow(image)
    ax.axis("off")
    fig.text(
        0.975,
        0.975,
        rf"${page_number}/{page_count}$",
        ha="right",
        va="top",
        fontsize=16,
        color="#555555",
    )
    pdf.savefig(fig, dpi=200)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path is None:
        raise SystemExit("ffmpeg is required but was not found on PATH.")
    if ffprobe_path is None:
        raise SystemExit("ffprobe is required but was not found on PATH.")

    overrides = load_overrides(args.overrides)
    entries = discover_videos(args.videos_root, args.images_root, args.study)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="rescue_deck_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        screens = []
        for index, entry in enumerate(entries, start=1):
            print(f"[{index:02d}/{len(entries):02d}] analyzing {entry.stem}")
            screens.append(
                build_video_screen(
                    ffmpeg_path=ffmpeg_path,
                    entry=entry,
                    temp_dir=temp_dir,
                    sample_fps=args.sample_fps,
                    analysis_width=args.analysis_width,
                    min_still_seconds=args.min_still_seconds,
                    motion_threshold=args.motion_threshold,
                )
            )

        with PdfPages(args.output) as pdf:
            for page_number, screen in enumerate(screens, start=1):
                candidate_timestamps = [candidate.timestamp_seconds for candidate in screen.candidates]
                mode, timestamp_seconds = choose_frame_timestamp(
                    entry=screen.entry,
                    screen_timestamps=candidate_timestamps,
                    default_mode=args.default_mode,
                    override=override_for_entry(overrides, screen.entry.stem),
                    ffprobe_path=ffprobe_path,
                )
                output_frame = temp_dir / f"{page_number:03d}_{screen.entry.stem}.png"
                if mode == "last-frame":
                    extract_last_frame(
                        ffmpeg_path=ffmpeg_path,
                        video_path=screen.entry.video_path,
                        output_path=output_frame,
                        seek_window_seconds=3.0,
                    )
                else:
                    if timestamp_seconds is None:
                        raise RuntimeError(f"Frame-selection mode {mode!r} requires a timestamp.")
                    extract_frame_at_timestamp(
                        ffmpeg_path=ffmpeg_path,
                        video_path=screen.entry.video_path,
                        timestamp_seconds=timestamp_seconds,
                        output_path=output_frame,
                    )
                print(
                    f"    -> {screen.entry.stem}: "
                    f"{mode}{'' if timestamp_seconds is None else f' @ {timestamp_seconds:.2f}'}"
                )
                add_rescue_page(
                    pdf=pdf,
                    image_path=output_frame,
                    page_number=page_number,
                    page_count=len(screens),
                )

    print(f"Wrote {len(screens)} rescue slides to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
