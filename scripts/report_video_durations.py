#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCENES_DIR = REPO_ROOT / "scenes"
if str(SCENES_DIR) not in sys.path:
    sys.path.insert(0, str(SCENES_DIR))

try:
    from utils import section_display_name, section_output_dir
except ModuleNotFoundError:
    from scripts.utils import section_display_name, section_output_dir

DEFAULT_VIDEOS_ROOT = REPO_ROOT / "media" / "videos"
DEFAULT_REPORT_DIR = REPO_ROOT / "media" / "reports"
DEFAULT_EXCLUDED_SECTIONS = (
    "old",
    "clips",
)
SECTION_ORDER_HINTS = (
    section_output_dir("intro"),
    section_output_dir("methods"),
    section_output_dir("study1"),
    section_output_dir("study2"),
    section_output_dir("conclusion"),
    section_output_dir("supplementary"),
    "intro_visual_memory",
    "intro_diffusion_explainer",
)
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
DISPLAY_SECTION_NAMES = {
    "intro_visual_memory": "Intro Visual Memory",
    "intro_diffusion_explainer": "Intro Diffusion Explainer",
}
SPLIT_RE = re.compile(r"(\d+)")
NUMBERED_SECTION_VIDEO_RE = re.compile(r"(?P<prefix>\d{3})_(?P<name>.+)$")


@dataclass(frozen=True)
class VideoRecord:
    section_key: str
    section_label: str
    quality_dir: Path
    video_path: Path
    duration_seconds: float

    @property
    def stem(self) -> str:
        return self.video_path.stem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Probe rendered video durations for one selected quality folder under "
            "media/videos and write a markdown timing report."
        )
    )
    parser.add_argument(
        "--quality",
        "-q",
        required=True,
        help=(
            "Quality folder to inspect (for example 480p15 or 1080p60). "
            "Manim quality flags like -ql and -qh are also accepted."
        ),
    )
    parser.add_argument(
        "--videos-root",
        type=Path,
        default=DEFAULT_VIDEOS_ROOT,
        help=f"Videos root directory (default: {DEFAULT_VIDEOS_ROOT}).",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=list(DEFAULT_EXCLUDED_SECTIONS),
        help=(
            "Top-level video folders to exclude. Defaults to: "
            f"{', '.join(DEFAULT_EXCLUDED_SECTIONS)}."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Destination markdown path. Defaults to "
            "media/reports/video_durations_<quality>.md."
        ),
    )
    return parser.parse_args()


def normalize_quality(raw_quality: str) -> str:
    normalized = QUALITY_ALIASES.get(raw_quality.strip().lower())
    if normalized is None:
        raise SystemExit(
            f"Unsupported quality {raw_quality!r}. "
            "Use a render folder like 480p15 or a known manim flag like -ql/-qm/-qh."
        )
    return normalized


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def natural_sort_key(text: str) -> tuple[object, ...]:
    parts = SPLIT_RE.split(text)
    key: list[object] = []
    for part in parts:
        if not part:
            continue
        key.append(int(part) if part.isdigit() else part.lower())
    return tuple(key)


def section_sort_key(section_name: str) -> tuple[object, ...]:
    try:
        return (0, SECTION_ORDER_HINTS.index(section_name))
    except ValueError:
        return (1, *natural_sort_key(section_name))


def section_label(section_name: str) -> str:
    return DISPLAY_SECTION_NAMES.get(section_name, section_display_name(section_name))


def available_quality_names(section_dir: Path) -> list[str]:
    qualities = []
    for child in sorted(section_dir.iterdir()):
        if child.is_dir() and child.name != "partial_movie_files":
            qualities.append(child.name)
    return qualities


def is_numbered_section_video(path: Path) -> bool:
    if path.suffix.lower() != ".mp4":
        return False
    if path.parent.name != "sections":
        return False
    if not NUMBERED_SECTION_VIDEO_RE.fullmatch(path.stem):
        return False
    return not path.stem.endswith("_autocreated")


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
        raise SystemExit(f"Could not probe duration for {video_path}: {error}")
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise SystemExit(
            f"Unexpected ffprobe output for {video_path}: {result.stdout!r}"
        ) from exc


def discover_video_records(
    *,
    videos_root: Path,
    quality: str,
    excluded_sections: set[str],
    ffprobe_path: str,
) -> list[VideoRecord]:
    if not videos_root.exists():
        raise SystemExit(f"Videos root directory not found: {videos_root}")

    section_dirs = [
        child
        for child in sorted(videos_root.iterdir(), key=lambda path: section_sort_key(path.name))
        if child.is_dir() and child.name not in excluded_sections
    ]
    if not section_dirs:
        raise SystemExit(
            f"No included section folders found under {videos_root}. "
            f"Excluded: {', '.join(sorted(excluded_sections)) or '(none)'}"
        )

    missing_quality_sections: list[str] = []
    empty_sections: list[str] = []
    records: list[VideoRecord] = []

    for section_dir in section_dirs:
        quality_dir = section_dir / quality
        if not quality_dir.exists():
            available = available_quality_names(section_dir)
            available_display = ", ".join(available) if available else "(none found)"
            missing_quality_sections.append(f"{section_dir.name} [{available_display}]")
            continue

        sections_dir = quality_dir / "sections"
        video_paths = sorted(
            [path for path in sections_dir.glob("*.mp4") if is_numbered_section_video(path)]
            if sections_dir.is_dir()
            else [],
            key=lambda path: natural_sort_key(path.stem),
        )
        if not video_paths:
            empty_sections.append(section_dir.name)
            continue

        label = section_label(section_dir.name)
        for video_path in video_paths:
            records.append(
                VideoRecord(
                    section_key=section_dir.name,
                    section_label=label,
                    quality_dir=quality_dir,
                    video_path=video_path,
                    duration_seconds=probe_duration_seconds(ffprobe_path, video_path),
                )
            )

    if missing_quality_sections:
        missing_lines = "\n".join(f"  - {entry}" for entry in missing_quality_sections)
        raise SystemExit(
            "The selected quality is missing for one or more included sections:\n"
            f"{missing_lines}"
        )

    if empty_sections:
        empty_lines = "\n".join(f"  - {entry}" for entry in empty_sections)
        raise SystemExit(
            "No numbered section MP4 files were found in one or more included sections:\n"
            f"{empty_lines}"
        )

    if not records:
        raise SystemExit(f"No videos found under {videos_root} for quality {quality}.")

    return records


def format_duration(seconds: float) -> str:
    total_centiseconds = round(seconds * 100)
    hours, remainder = divmod(total_centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole_seconds, centiseconds = divmod(remainder, 100)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{centiseconds:02d}"


def render_report(
    *,
    records: list[VideoRecord],
    quality: str,
    videos_root: Path,
    excluded_sections: list[str],
    output_path: Path,
) -> str:
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    overall_total = sum(record.duration_seconds for record in records)

    grouped_records: dict[str, list[VideoRecord]] = {}
    for record in records:
        grouped_records.setdefault(record.section_key, []).append(record)

    section_keys = sorted(grouped_records, key=section_sort_key)
    lines: list[str] = [
        "# Presentation Video Duration Report",
        "",
        f"- Generated: `{generated_at}`",
        f"- Quality: `{quality}`",
        f"- Source root: `{display_path(videos_root)}`",
        f"- Excluded folders: `{', '.join(excluded_sections)}`",
        f"- Sections counted: `{len(section_keys)}`",
        f"- Videos counted: `{len(records)}`",
        f"- Total presentation duration: `{format_duration(overall_total)}`",
        "",
        "## Section Summary",
        "",
        "| # | Section | Videos | Duration |",
        "|---:|---|---:|---:|",
    ]

    for index, section_key in enumerate(section_keys, start=1):
        section_records = grouped_records[section_key]
        section_total = sum(record.duration_seconds for record in section_records)
        lines.append(
            f"| {index} | {section_records[0].section_label} | {len(section_records)} | "
            f"`{format_duration(section_total)}` |"
        )

    lines.extend(
        [
            f"|  | **Total presentation** | **{len(records)}** | **`{format_duration(overall_total)}`** |",
            "",
            "## Per-Section Timing",
            "",
        ]
    )

    overall_index = 0
    for section_index, section_key in enumerate(section_keys, start=1):
        section_records = grouped_records[section_key]
        section_total = sum(record.duration_seconds for record in section_records)
        quality_dir = section_records[0].quality_dir
        lines.extend(
            [
                f"### {section_index}. {section_records[0].section_label}",
                "",
                f"- Folder: `{display_path(quality_dir)}`",
                f"- Videos: `{len(section_records)}`",
                f"- Section total: `{format_duration(section_total)}`",
                "",
                "| Global # | Section # | Video | Duration |",
                "|---:|---:|---|---:|",
            ]
        )
        for local_index, record in enumerate(section_records, start=1):
            overall_index += 1
            lines.append(
                f"| {overall_index} | {local_index} | `{record.stem}` | "
                f"`{format_duration(record.duration_seconds)}` |"
            )
        lines.append("")

    lines.extend(
        [
            "## Output",
            "",
            f"- Report file: `{display_path(output_path)}`",
            "",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    quality = normalize_quality(args.quality)
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path is None:
        raise SystemExit("ffprobe is required but was not found on PATH.")

    excluded_sections = [name for name in args.exclude if name]
    records = discover_video_records(
        videos_root=args.videos_root,
        quality=quality,
        excluded_sections=set(excluded_sections),
        ffprobe_path=ffprobe_path,
    )

    output_path = args.output
    if output_path is None:
        output_path = DEFAULT_REPORT_DIR / f"video_durations_{quality}.md"

    report = render_report(
        records=records,
        quality=quality,
        videos_root=args.videos_root,
        excluded_sections=excluded_sections,
        output_path=output_path,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    print(f"Wrote video duration report for {len(records)} videos to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
