#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "cm"

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEOS_ROOT = REPO_ROOT / "media" / "videos"
DEFAULT_IMAGES_ROOT = REPO_ROOT / "media" / "images"
DEFAULT_OUTPUT = REPO_ROOT / "media" / "pdfs" / "study_last_frames_backup.pdf"
QUALITY_RE = re.compile(r"(?P<height>\d+)p(?P<fps>\d+)$")
STEM_RE = re.compile(r"(?P<prefix>\d+)(?P<suffix>[A-Za-z]*)_(?P<name>.+)$")


@dataclass(frozen=True)
class VideoEntry:
    video_path: Path
    still_fallback: Path | None
    sort_key: tuple[object, ...]

    @property
    def stem(self) -> str:
        return self.video_path.stem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract the last frame from each rendered Study 1/2 video and "
            "assemble them into a one-slide-per-page PDF."
        )
    )
    parser.add_argument(
        "--study",
        choices=("study1", "study2"),
        nargs="+",
        default=["study1", "study2"],
        help="Studies to include in the PDF (default: study1 study2).",
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
        help=f"Destination PDF path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--seek-window-seconds",
        type=float,
        default=3.0,
        help=(
            "How far back from the end ffmpeg should begin decoding when "
            "capturing the final frame (default: 3.0)."
        ),
    )
    return parser.parse_args()


def video_quality_key(path: Path) -> tuple[int, int, int]:
    height = 0
    fps = 0
    for part in path.parts:
        match = QUALITY_RE.fullmatch(part)
        if match:
            height = int(match.group("height"))
            fps = int(match.group("fps"))
            break
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return (height, fps, size)


def stem_sort_key(stem: str) -> tuple[object, ...]:
    match = STEM_RE.match(stem)
    if not match:
        return (sys.maxsize, stem)
    return (
        int(match.group("prefix")),
        match.group("suffix"),
        match.group("name"),
    )


def discover_videos(videos_root: Path, images_root: Path, studies: list[str]) -> list[VideoEntry]:
    entries: list[VideoEntry] = []
    for study in studies:
        study_dir = videos_root / study
        if not study_dir.exists():
            raise SystemExit(f"Video directory not found for {study}: {study_dir}")

        grouped: dict[str, list[Path]] = defaultdict(list)
        for path in study_dir.rglob("*.mp4"):
            if "partial_movie_files" in path.parts:
                continue
            grouped[path.stem].append(path)

        if not grouped:
            raise SystemExit(f"No top-level MP4 renders found under {study_dir}")

        for stem, candidates in grouped.items():
            best_video = max(candidates, key=video_quality_key)
            still_fallback = images_root / study / f"{stem}.png"
            if not still_fallback.exists():
                still_fallback = None
            entries.append(
                VideoEntry(
                    video_path=best_video,
                    still_fallback=still_fallback,
                    sort_key=(study, *stem_sort_key(stem)),
                )
            )

    return sorted(entries, key=lambda entry: entry.sort_key)


def extract_last_frame(
    ffmpeg_path: str,
    video_path: Path,
    output_path: Path,
    seek_window_seconds: float,
) -> None:
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-sseof",
        f"-{seek_window_seconds:g}",
        "-i",
        str(video_path),
        "-map",
        "0:v:0",
        "-update",
        "1",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not output_path.exists():
        error = result.stderr.strip() or "ffmpeg did not produce an output frame."
        raise RuntimeError(f"Could not extract last frame from {video_path}: {error}")


def add_pdf_page(
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
    if ffmpeg_path is None:
        raise SystemExit("ffmpeg is required but was not found on PATH.")

    entries = discover_videos(args.videos_root, args.images_root, args.study)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="last_frames_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        with PdfPages(args.output) as pdf:
            for page_number, entry in enumerate(entries, start=1):
                extracted_frame = temp_dir / f"{page_number:03d}_{entry.stem}.png"
                try:
                    extract_last_frame(
                        ffmpeg_path=ffmpeg_path,
                        video_path=entry.video_path,
                        output_path=extracted_frame,
                        seek_window_seconds=args.seek_window_seconds,
                    )
                    page_image = extracted_frame
                except RuntimeError:
                    if entry.still_fallback is None:
                        raise
                    page_image = entry.still_fallback

                print(f"[{page_number:02d}/{len(entries):02d}] {entry.stem}")
                add_pdf_page(
                    pdf=pdf,
                    image_path=page_image,
                    page_number=page_number,
                    page_count=len(entries),
                )

    print(f"Wrote {len(entries)} pages to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
