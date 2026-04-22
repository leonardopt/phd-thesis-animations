#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "cm"

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

try:
    from export_last_frames_pdf import (
        DEFAULT_IMAGES_ROOT,
        DEFAULT_SECTION_KEYS,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        VideoEntry,
        discover_videos,
    )
except ModuleNotFoundError:
    from scripts.export_last_frames_pdf import (
        DEFAULT_IMAGES_ROOT,
        DEFAULT_SECTION_KEYS,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        VideoEntry,
        discover_videos,
    )


DEFAULT_OUTPUT = REPO_ROOT / "media" / "pdfs" / "study_frame_screener.pdf"
DEFAULT_FULL_PAGE_OUTPUT = REPO_ROOT / "media" / "pdfs" / "study_frame_screener_full_pages.pdf"


@dataclass(frozen=True)
class CandidateFrame:
    """One candidate still frame plus the sampled timestamp it represents."""

    image_path: Path
    timestamp_seconds: float


@dataclass(frozen=True)
class VideoScreen:
    """Stable-frame candidates collected for one rendered video."""

    entry: VideoEntry
    candidates: tuple[CandidateFrame, ...]


def parse_args() -> argparse.Namespace:
    """Parse CLI flags for stable-frame discovery and PDF layout generation."""
    parser = argparse.ArgumentParser(
        description=(
            "Build a screener PDF with candidate still frames from numbered "
            "presentation section clips, preferring frames that sit in stable "
            "holds rather than in the middle of an animation."
        )
    )
    parser.add_argument(
        "--section",
        "--study",
        dest="sections",
        choices=DEFAULT_SECTION_KEYS,
        nargs="+",
        default=list(DEFAULT_SECTION_KEYS),
        help=(
            "Presentation sections to include in the screener "
            f"(default: {' '.join(DEFAULT_SECTION_KEYS)})."
        ),
    )
    parser.add_argument(
        "--videos-root",
        type=Path,
        default=DEFAULT_VIDEOS_ROOT,
        help=f"Root directory containing numbered section video folders (default: {DEFAULT_VIDEOS_ROOT}).",
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
        "--full-page-output",
        type=Path,
        default=DEFAULT_FULL_PAGE_OUTPUT,
        help=(
            "Destination PDF path for the landscape one-frame-per-page export "
            f"(default: {DEFAULT_FULL_PAGE_OUTPUT})."
        ),
    )
    parser.add_argument(
        "--sample-fps",
        type=float,
        default=4.0,
        help="Sampling rate used while looking for stable holds (default: 4.0 fps).",
    )
    parser.add_argument(
        "--analysis-width",
        type=int,
        default=320,
        help="Width of sampled frames used for motion analysis and the screener thumbnails (default: 320).",
    )
    parser.add_argument(
        "--min-still-seconds",
        type=float,
        default=0.5,
        help="Minimum length of a stable hold to keep as a candidate frame (default: 0.5s).",
    )
    parser.add_argument(
        "--motion-threshold",
        type=float,
        default=None,
        help=(
            "Optional absolute motion threshold in normalized mean pixel "
            "difference units. Leave unset to infer a threshold per video."
        ),
    )
    parser.add_argument(
        "--frames-per-page",
        type=int,
        default=6,
        help="How many candidate frames to show on each screener page (default: 6).",
    )
    return parser.parse_args()


def sample_video_frames(
    ffmpeg_path: str,
    video_path: Path,
    output_dir: Path,
    sample_fps: float,
    analysis_width: int,
) -> list[Path]:
    """Sample a video into uniformly spaced PNG frames for motion analysis."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_pattern = output_dir / "frame_%05d.png"
    vf = f"fps={sample_fps:g},scale={analysis_width}:-1:flags=lanczos"
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        vf,
        str(output_pattern),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        error = result.stderr.strip() or "ffmpeg failed to sample frames."
        raise RuntimeError(f"Could not sample {video_path}: {error}")
    return sorted(output_dir.glob("frame_*.png"))


def load_grayscale_frames(frame_paths: list[Path]) -> list[np.ndarray]:
    """Load sampled frames as grayscale arrays suitable for motion comparison."""
    arrays: list[np.ndarray] = []
    for frame_path in frame_paths:
        image = mpimg.imread(frame_path).astype(np.float32)
        if image.ndim == 3:
            image = image[..., :3].mean(axis=2)
        arrays.append(image)
    return arrays


def infer_motion_threshold(adjacent_diffs: np.ndarray) -> float:
    """Infer a per-video motion threshold from sampled frame-to-frame differences.

    The heuristic anchors itself to the lower-motion portion of the adjacent
    difference distribution, then expands that baseline slightly so quiet holds
    survive while ongoing animation stays above threshold. The result is clipped
    into a conservative range to avoid extreme thresholds on unusual videos.
    """
    if adjacent_diffs.size == 0:
        return 0.003
    base = float(np.quantile(adjacent_diffs, 0.35))
    return min(0.010, max(0.0015, base * 1.5))


def select_stable_frame_indices(
    arrays: list[np.ndarray],
    sample_fps: float,
    min_still_seconds: float,
    motion_threshold: float | None,
) -> list[int]:
    """Pick representative frame indices from stable visual holds.

    The algorithm measures adjacent frame motion, marks a frame as stable when
    both of its neighboring differences stay under threshold, groups contiguous
    stable frames into runs, and keeps the midpoint of each run that lasts at
    least `min_still_seconds`. When no run qualifies, it falls back to the
    calmest observed transition region so each video still yields one reviewable
    candidate.
    """
    if not arrays:
        return []
    if len(arrays) == 1:
        return [0]

    adjacent_diffs = np.array(
        [float(np.mean(np.abs(curr - prev))) for prev, curr in zip(arrays, arrays[1:])],
        dtype=np.float32,
    )
    threshold = motion_threshold if motion_threshold is not None else infer_motion_threshold(adjacent_diffs)

    stable_flags: list[bool] = []
    for index in range(len(arrays)):
        neighbor_diffs: list[float] = []
        if index > 0:
            neighbor_diffs.append(float(adjacent_diffs[index - 1]))
        if index < len(arrays) - 1:
            neighbor_diffs.append(float(adjacent_diffs[index]))
        stable_flags.append(bool(neighbor_diffs) and max(neighbor_diffs) <= threshold)

    min_run_frames = max(1, math.ceil(min_still_seconds * sample_fps))

    selected_indices: list[int] = []
    run_start: int | None = None
    for index, is_stable in enumerate(stable_flags):
        if is_stable and run_start is None:
            run_start = index
        elif not is_stable and run_start is not None:
            run_end = index - 1
            if run_end - run_start + 1 >= min_run_frames:
                selected_indices.append((run_start + run_end) // 2)
            run_start = None
    if run_start is not None:
        run_end = len(stable_flags) - 1
        if run_end - run_start + 1 >= min_run_frames:
            selected_indices.append((run_start + run_end) // 2)

    if selected_indices:
        return selected_indices

    calmest_index = int(np.argmin(adjacent_diffs))
    # Use the later frame from the calmest pair so the fallback lands on the
    # frame that best represents the end of that low-motion transition.
    fallback_index = min(calmest_index + 1, len(arrays) - 1)
    return [fallback_index]


def build_video_screen(
    ffmpeg_path: str,
    entry: VideoEntry,
    temp_dir: Path,
    sample_fps: float,
    analysis_width: int,
    min_still_seconds: float,
    motion_threshold: float | None,
) -> VideoScreen:
    """Sample one video and package its stable-frame candidates for downstream PDFs."""
    video_dir = temp_dir / entry.stem
    frame_paths = sample_video_frames(
        ffmpeg_path=ffmpeg_path,
        video_path=entry.video_path,
        output_dir=video_dir,
        sample_fps=sample_fps,
        analysis_width=analysis_width,
    )
    arrays = load_grayscale_frames(frame_paths)
    selected_indices = select_stable_frame_indices(
        arrays=arrays,
        sample_fps=sample_fps,
        min_still_seconds=min_still_seconds,
        motion_threshold=motion_threshold,
    )
    candidates = tuple(
        CandidateFrame(
            image_path=frame_paths[index],
            timestamp_seconds=index / sample_fps,
        )
        for index in selected_indices
    )
    return VideoScreen(entry=entry, candidates=candidates)


def chunked_candidates(candidates: tuple[CandidateFrame, ...], chunk_size: int) -> list[tuple[CandidateFrame, ...]]:
    """Split a candidate tuple into fixed-size page chunks."""
    return [
        candidates[start : start + chunk_size]
        for start in range(0, len(candidates), chunk_size)
    ]


def add_screener_page(
    pdf: PdfPages,
    screen: VideoScreen,
    candidates: tuple[CandidateFrame, ...],
    page_number: int,
    page_count: int,
    local_page_number: int,
    local_page_count: int,
) -> None:
    """Render one grid page of candidate stills for a single video."""
    fig = plt.figure(figsize=(13.333, 7.5), facecolor="white")
    fig.text(
        0.03,
        0.972,
        screen.entry.stem,
        ha="left",
        va="top",
        fontsize=14,
        family="monospace",
    )
    fig.text(
        0.5,
        0.972,
        f"{len(screen.candidates)} still candidates",
        ha="center",
        va="top",
        fontsize=12,
        color="#666666",
    )
    fig.text(
        0.97,
        0.972,
        rf"${page_number}/{page_count}$",
        ha="right",
        va="top",
        fontsize=14,
        color="#555555",
    )

    if local_page_count > 1:
        fig.text(
            0.97,
            0.938,
            f"sheet {local_page_number}/{local_page_count}",
            ha="right",
            va="top",
            fontsize=10,
            color="#777777",
        )

    cols = 3
    rows = 2
    cell_width = 0.29
    cell_height = 0.31
    x_positions = [0.035, 0.355, 0.675]
    y_positions = [0.56, 0.14]

    for index, candidate in enumerate(candidates):
        row = index // cols
        col = index % cols
        left = x_positions[col]
        bottom = y_positions[row]
        ax = fig.add_axes([left, bottom, cell_width, cell_height])
        ax.imshow(mpimg.imread(candidate.image_path))
        ax.axis("off")
        fig.text(
            left,
            bottom - 0.028,
            rf"${candidate.timestamp_seconds:.1f}$",
            ha="left",
            va="top",
            fontsize=11,
            color="#444444",
        )

    pdf.savefig(fig, dpi=180)
    plt.close(fig)


def add_full_page_frame(
    pdf: PdfPages,
    screen: VideoScreen,
    candidate: CandidateFrame,
    page_number: int,
    page_count: int,
) -> None:
    """Render one full-slide candidate preview page for a single sampled frame."""
    fig = plt.figure(figsize=(13.333, 7.5), facecolor="white")
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.86])
    ax.imshow(mpimg.imread(candidate.image_path))
    ax.axis("off")

    fig.text(
        0.03,
        0.972,
        screen.entry.stem,
        ha="left",
        va="top",
        fontsize=14,
        family="monospace",
    )
    fig.text(
        0.5,
        0.972,
        rf"${candidate.timestamp_seconds:.1f}$",
        ha="center",
        va="top",
        fontsize=14,
        color="#555555",
    )
    fig.text(
        0.97,
        0.972,
        rf"${page_number}/{page_count}$",
        ha="right",
        va="top",
        fontsize=14,
        color="#555555",
    )

    pdf.savefig(fig, dpi=200)
    plt.close(fig)


def main() -> int:
    """Generate both the multi-candidate screener PDF and the full-page export."""
    args = parse_args()
    if not 1 <= args.frames_per_page <= 6:
        raise SystemExit("--frames-per-page must be between 1 and 6 for the current screener layout.")
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise SystemExit("ffmpeg is required but was not found on PATH.")

    entries = discover_videos(args.videos_root, args.images_root, args.sections)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.full_page_output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="frame_screener_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        screens: list[VideoScreen] = []
        for index, entry in enumerate(entries, start=1):
            print(f"[{index:02d}/{len(entries):02d}] sampling {entry.stem}")
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

        page_plan: list[tuple[VideoScreen, tuple[CandidateFrame, ...], int, int]] = []
        for screen in screens:
            candidate_pages = chunked_candidates(screen.candidates, args.frames_per_page)
            for local_index, candidate_page in enumerate(candidate_pages, start=1):
                page_plan.append((screen, candidate_page, local_index, len(candidate_pages)))
        full_page_plan = [
            (screen, candidate)
            for screen in screens
            for candidate in screen.candidates
        ]

        with PdfPages(args.output) as pdf:
            for page_number, (screen, candidate_page, local_index, local_count) in enumerate(page_plan, start=1):
                add_screener_page(
                    pdf=pdf,
                    screen=screen,
                    candidates=candidate_page,
                    page_number=page_number,
                    page_count=len(page_plan),
                    local_page_number=local_index,
                    local_page_count=local_count,
                )

        with PdfPages(args.full_page_output) as pdf:
            for page_number, (screen, candidate) in enumerate(full_page_plan, start=1):
                add_full_page_frame(
                    pdf=pdf,
                    screen=screen,
                    candidate=candidate,
                    page_number=page_number,
                    page_count=len(full_page_plan),
                )

    print(f"Wrote {len(page_plan)} screener pages to {args.output}")
    print(f"Wrote {len(full_page_plan)} full-page frames to {args.full_page_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
