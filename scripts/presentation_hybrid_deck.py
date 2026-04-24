#!/usr/bin/env python3
"""Build a hybrid Keynote deck scaffold from the slide-by-slide audit report.

The current repo automation can choose between full-slide media and static slide
assets, but it does not fully script native Keynote builds. This script
therefore applies the audit as follows:

- `No -> Embedded video` stays as an MP4 slide.
- `Yes -> Static still` becomes a still-image slide.
- `Yes -> Keynote build` also becomes a still-image slide, plus a short
  presenter-note flag so those slides are easy to rebuild manually in Keynote.

The result is a concrete hybrid deck scaffold that follows the audit's
video-vs-non-video split and is ready for manual refinement where native
Keynote builds are still preferable.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import presentation_manifest
from build_static_rescue_deck import (
    DEFAULT_OVERRIDES,
    choose_frame_timestamp,
    extract_frame_at_timestamp,
    extract_last_frame,
    load_overrides,
    override_for_entry,
)
from export_frame_screener_pdf import build_video_screen
from export_last_frames_pdf import VideoEntry


DEFAULT_SOURCE_MANIFEST = REPO_ROOT / "assets" / "presentation_deck.toml"
DEFAULT_REPORT_DIR = REPO_ROOT / "media" / "reports"
DEFAULT_MANIFEST_OUTPUT = REPO_ROOT / "assets" / "presentation_hybrid_deck.toml"
DEFAULT_STILLS_ROOT = REPO_ROOT / "media" / "hybrid_stills"
DEFAULT_APPLESCRIPT = REPO_ROOT / "scripts" / "create_keynote_presentation.applescript"
DEFAULT_DECK_BASE_NAME = "presentation_hybrid"
HYBRID_BUILD_NOTE = (
    "[Hybrid scaffold] Audit decision: Keynote build. "
    "This auto-generated deck uses a stable still placeholder for now."
)
REPORT_ROW_RE = re.compile(
    r"^\|\s*`(?P<stem>[^`]+)`\s*"
    r"\|\s*(?P<duration>[^|]+?)\s*"
    r"\|\s*(?P<animation>[^|]+?)\s*"
    r"\|\s*(?P<decision>Yes -> Static still|Yes -> Keynote build|No -> Embedded video)\s*"
    r"\|\s*(?P<why>.+?)\s*\|$"
)


class HybridDisposition(str, Enum):
    STATIC_STILL = "static_still"
    KEYNOTE_BUILD = "keynote_build"
    EMBEDDED_VIDEO = "embedded_video"


REPORT_DECISION_MAP = {
    "Yes -> Static still": HybridDisposition.STATIC_STILL,
    "Yes -> Keynote build": HybridDisposition.KEYNOTE_BUILD,
    "No -> Embedded video": HybridDisposition.EMBEDDED_VIDEO,
}


@dataclass(frozen=True)
class AuditDecision:
    stem: str
    disposition: HybridDisposition
    duration_text: str
    animation_summary: str
    why: str


@dataclass(frozen=True)
class StillJob:
    stem: str
    video_path: Path
    disposition: HybridDisposition


@dataclass(frozen=True)
class ExtractedStill:
    output_path: Path
    mode: str
    timestamp_seconds: float | None


def latest_hybrid_report_path() -> Path:
    candidates = sorted(DEFAULT_REPORT_DIR.glob("hybrid_keynote_animation_audit_*.md"))
    if not candidates:
        raise FileNotFoundError(
            "No hybrid audit report found under "
            f"{DEFAULT_REPORT_DIR} (expected hybrid_keynote_animation_audit_*.md)."
        )
    return candidates[-1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a hybrid Keynote deck scaffold from the hybrid animation "
            "audit report, using stills for skippable animations and MP4s only "
            "for clips marked as indispensable."
        )
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=latest_hybrid_report_path(),
        help="Markdown audit report to apply.",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=DEFAULT_SOURCE_MANIFEST,
        help="Source deck manifest to expand before applying audit decisions.",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=DEFAULT_MANIFEST_OUTPUT,
        help="Destination path for the generated hybrid manifest.",
    )
    parser.add_argument(
        "--stills-root",
        type=Path,
        default=DEFAULT_STILLS_ROOT,
        help="Root directory for extracted still-image placeholders.",
    )
    parser.add_argument(
        "--frame-overrides",
        type=Path,
        default=DEFAULT_OVERRIDES,
        help="Optional per-clip frame selection overrides TOML.",
    )
    parser.add_argument(
        "--deck-base-name",
        default=None,
        help="Optional deck_base_name override for the generated hybrid manifest.",
    )
    parser.add_argument(
        "--quality-folder",
        default="auto",
        help=(
            "Render quality selector used when expanding the source manifest. "
            "When set to ql/qm/qh/qk instead of auto, explicit media/video "
            "quality folders in the source manifest are overridden too."
        ),
    )
    parser.add_argument(
        "--render-everything-qk",
        action="store_true",
        help=(
            "Rerender all section clips at 2160p60 before building the hybrid deck, "
            "then use those qk renders for still extraction and embedded videos."
        ),
    )
    parser.add_argument(
        "--sample-fps",
        type=float,
        default=4.0,
        help="Sampling rate used while detecting stable still frames.",
    )
    parser.add_argument(
        "--analysis-width",
        type=int,
        default=320,
        help="Width used when analyzing motion for stable-frame extraction.",
    )
    parser.add_argument(
        "--min-still-seconds",
        type=float,
        default=0.5,
        help="Minimum stable hold duration for candidate still frames.",
    )
    parser.add_argument(
        "--motion-threshold",
        type=float,
        default=None,
        help="Optional absolute motion threshold override for stable-frame extraction.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Write the hybrid manifest and stills, but do not launch Keynote.",
    )
    parser.add_argument(
        "--apple-script",
        type=Path,
        default=DEFAULT_APPLESCRIPT,
        help="Keynote builder AppleScript to use when creating the deck.",
    )
    return parser.parse_args()


def normalize_quality_value(raw_value: str) -> str:
    trimmed_value = raw_value.strip().lower()
    if trimmed_value in {"", "auto", "mixed", "existing"}:
        return "auto"
    if trimmed_value in {"-ql", "ql", "low", "480p15"}:
        return "480p15"
    if trimmed_value in {"-qm", "qm", "medium", "720p30"}:
        return "720p30"
    if trimmed_value in {"-qh", "qh", "high", "1080p60"}:
        return "1080p60"
    if trimmed_value in {"-qk", "qk", "4k", "2160p60"}:
        return "2160p60"
    raise ValueError(
        f"Unsupported quality argument {raw_value!r}. "
        "Use auto, -ql, -qm, -qh, -qk, or an explicit folder like 1080p60."
    )


def quality_flag_for_folder(quality_folder: str) -> str:
    quality_flag_by_folder = {
        "480p15": "-ql",
        "720p30": "-qm",
        "1080p60": "-qh",
        "2160p60": "-qk",
    }
    try:
        return quality_flag_by_folder[quality_folder]
    except KeyError as exc:
        raise ValueError(f"Unsupported quality folder {quality_folder!r}.") from exc


def resolve_effective_quality_folder(
    raw_quality_value: str,
    *,
    render_everything_qk: bool,
) -> str:
    quality_folder = normalize_quality_value(raw_quality_value)
    if not render_everything_qk:
        return quality_folder

    if quality_folder not in {"auto", "2160p60"}:
        raise ValueError(
            "--render-everything-qk conflicts with --quality-folder. "
            "Use auto/qk/2160p60 with that flag."
        )
    return "2160p60"


def rerender_all_sections(quality_folder: str) -> None:
    command = [str((REPO_ROOT / "render_all.sh").resolve()), quality_flag_for_folder(quality_folder)]
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Full-section rerender failed for {quality_folder} "
            f"(exit status {result.returncode})."
        )


def parse_report(report_path: Path) -> dict[str, AuditDecision]:
    decisions: dict[str, AuditDecision] = {}
    for line in report_path.read_text(encoding="utf-8").splitlines():
        match = REPORT_ROW_RE.fullmatch(line.strip())
        if match is None:
            continue

        stem = match.group("stem")
        if stem in decisions:
            raise ValueError(f"Duplicate audit row for clip {stem!r} in {report_path}.")
        decisions[stem] = AuditDecision(
            stem=stem,
            disposition=REPORT_DECISION_MAP[match.group("decision")],
            duration_text=match.group("duration").strip(),
            animation_summary=match.group("animation").strip(),
            why=match.group("why").strip(),
        )

    if not decisions:
        raise ValueError(f"No audit table rows were found in {report_path}.")
    return decisions


def repo_relative_string(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def decorate_notes_for_keynote_build(original_notes: str) -> str:
    if not original_notes:
        return HYBRID_BUILD_NOTE
    return HYBRID_BUILD_NOTE + "\n\n" + original_notes


def load_expanded_source_slides(
    source_manifest: Path,
    quality_folder: str,
) -> tuple[dict, list[dict]]:
    manifest = presentation_manifest.load_manifest(source_manifest.resolve())
    deck = manifest.get("deck", {})
    slides = manifest.get("slide", [])
    if not isinstance(slides, list) or not slides:
        raise ValueError(f"Manifest {source_manifest} does not contain any [[slide]] entries.")

    expanded_slides = presentation_manifest.expand_slides(slides, REPO_ROOT, quality_folder)
    expanded_slides = presentation_manifest.merge_presenter_notes(
        deck,
        expanded_slides,
        REPO_ROOT,
        quality_folder,
    )
    return deck, expanded_slides


def collect_still_jobs(
    expanded_slides: list[dict],
    audit_decisions: dict[str, AuditDecision],
) -> tuple[list[StillJob], list[str]]:
    jobs: list[StillJob] = []
    missing_stems: list[str] = []
    seen_video_paths: set[Path] = set()

    for slide in expanded_slides:
        if slide["type"] != "video":
            continue

        video_path = Path(slide["path"]).resolve()
        stem = video_path.stem
        decision = audit_decisions.get(stem)
        if decision is None:
            missing_stems.append(stem)
            continue
        if decision.disposition is HybridDisposition.EMBEDDED_VIDEO:
            continue
        if video_path in seen_video_paths:
            continue

        jobs.append(
            StillJob(
                stem=stem,
                video_path=video_path,
                disposition=decision.disposition,
            )
        )
        seen_video_paths.add(video_path)

    return jobs, sorted(set(missing_stems))


def still_output_path(stills_root: Path, quality_folder: str, video_path: Path) -> Path:
    videos_root = (REPO_ROOT / "media" / "videos").resolve()
    resolved_video = video_path.resolve()
    try:
        relative_video = resolved_video.relative_to(videos_root)
    except ValueError:
        return stills_root / quality_folder / f"{resolved_video.stem}.png"

    section_dir = relative_video.parts[0]
    return stills_root / quality_folder / section_dir / f"{resolved_video.stem}.png"


def output_is_stale(output_path: Path, dependencies: list[Path]) -> bool:
    if not output_path.exists():
        return True
    output_mtime = output_path.stat().st_mtime
    return any(
        dependency.exists() and dependency.stat().st_mtime > output_mtime
        for dependency in dependencies
    )


def ensure_still_for_video(
    *,
    job: StillJob,
    output_path: Path,
    ffmpeg_path: str,
    ffprobe_path: str,
    overrides: dict[str, dict[str, object]],
    overrides_path: Path,
    report_path: Path,
    sample_fps: float,
    analysis_width: int,
    min_still_seconds: float,
    motion_threshold: float | None,
) -> ExtractedStill:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_is_stale(output_path, [job.video_path, overrides_path, report_path]):
        return ExtractedStill(output_path=output_path, mode="existing", timestamp_seconds=None)

    entry = VideoEntry(
        video_path=job.video_path,
        still_fallback=None,
        sort_key=(0, job.video_path.stem),
    )
    with tempfile.TemporaryDirectory(prefix=f"hybrid_still_{job.stem}_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        screen = build_video_screen(
            ffmpeg_path=ffmpeg_path,
            entry=entry,
            temp_dir=temp_dir,
            sample_fps=sample_fps,
            analysis_width=analysis_width,
            min_still_seconds=min_still_seconds,
            motion_threshold=motion_threshold,
        )
        candidate_timestamps = [candidate.timestamp_seconds for candidate in screen.candidates]
        mode, timestamp_seconds = choose_frame_timestamp(
            entry=entry,
            screen_timestamps=candidate_timestamps,
            default_mode="last-stable",
            override=override_for_entry(overrides, entry.stem),
            ffprobe_path=ffprobe_path,
        )
        if mode == "last-frame":
            extract_last_frame(
                ffmpeg_path=ffmpeg_path,
                video_path=job.video_path,
                output_path=output_path,
                seek_window_seconds=3.0,
            )
        else:
            if timestamp_seconds is None:
                raise RuntimeError(f"Frame-selection mode {mode!r} requires a timestamp.")
            extract_frame_at_timestamp(
                ffmpeg_path=ffmpeg_path,
                video_path=job.video_path,
                timestamp_seconds=timestamp_seconds,
                output_path=output_path,
            )

    return ExtractedStill(
        output_path=output_path,
        mode=mode,
        timestamp_seconds=timestamp_seconds,
    )


def build_hybrid_slide_records(
    expanded_slides: list[dict],
    audit_decisions: dict[str, AuditDecision],
    extracted_stills: dict[Path, Path],
) -> tuple[list[dict], set[str]]:
    hybrid_slides: list[dict] = []
    used_stems: set[str] = set()

    for slide in expanded_slides:
        slide_copy = dict(slide)
        if slide_copy["path"]:
            slide_copy["path"] = repo_relative_string(Path(slide_copy["path"]))

        if slide["type"] != "video":
            hybrid_slides.append(slide_copy)
            continue

        video_path = Path(slide["path"]).resolve()
        stem = video_path.stem
        decision = audit_decisions.get(stem)
        if decision is None:
            raise ValueError(
                f"No audit decision found for video slide {stem!r} ({video_path})."
            )
        used_stems.add(stem)

        if decision.disposition is HybridDisposition.EMBEDDED_VIDEO:
            hybrid_slides.append(slide_copy)
            continue

        still_path = extracted_stills.get(video_path)
        if still_path is None:
            raise ValueError(f"No extracted still was generated for {video_path}.")

        image_slide = dict(slide_copy)
        image_slide["type"] = "image"
        image_slide["path"] = repo_relative_string(still_path)
        if decision.disposition is HybridDisposition.KEYNOTE_BUILD:
            image_slide["notes"] = decorate_notes_for_keynote_build(slide_copy["notes"])
        hybrid_slides.append(image_slide)

    return hybrid_slides, used_stems


def toml_string(value: str) -> str:
    if "\n" in value and '"""' not in value:
        return '"""\n' + value + '\n"""'
    return json.dumps(value, ensure_ascii=False)


def append_optional_string(lines: list[str], key: str, value: str) -> None:
    if value == "":
        return
    lines.append(f"{key} = {toml_string(value)}")


def serialize_hybrid_manifest(deck: dict, slides: list[dict], deck_base_name: str) -> str:
    lines = [
        "# Auto-generated by scripts/presentation_hybrid_deck.py",
        "# Keynote-build audit rows are currently emitted as still-image placeholders.",
        "",
        "[deck]",
        f"deck_base_name = {toml_string(deck_base_name)}",
        f"output_dir = {toml_string(deck.get('output_dir', 'media/keynote'))}",
        f"slide_width = {int(deck.get('slide_width', 1920))}",
        f"slide_height = {int(deck.get('slide_height', 1080))}",
    ]

    for slide in slides:
        lines.append("")
        lines.append("[[slide]]")
        lines.append(f"type = {toml_string(slide['type'])}")
        append_optional_string(lines, "path", slide["path"])
        append_optional_string(lines, "title", slide["title"])
        append_optional_string(lines, "subtitle", slide["subtitle"])
        append_optional_string(lines, "body", slide["body"])
        append_optional_string(lines, "notes", slide["notes"])

    lines.append("")
    return "\n".join(lines)


def write_hybrid_manifest(
    manifest_output: Path,
    deck: dict,
    slides: list[dict],
    deck_base_name: str,
) -> None:
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    manifest_output.write_text(
        serialize_hybrid_manifest(deck, slides, deck_base_name),
        encoding="utf-8",
    )


def build_keynote_deck(applescript_path: Path, manifest_path: Path) -> Path:
    command = [
        "osascript",
        str(applescript_path.resolve()),
        "--manifest",
        str(manifest_path.resolve()),
        "--no-dialog",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        error_text = result.stderr.strip() or result.stdout.strip() or "osascript failed."
        raise RuntimeError(error_text)
    output_text = result.stdout.strip()
    if output_text == "":
        raise RuntimeError("Keynote builder returned no output path.")
    return Path(output_text.splitlines()[-1].strip()).expanduser().resolve()


def main() -> int:
    args = parse_args()
    report_path = args.report.expanduser().resolve()
    source_manifest = args.source_manifest.expanduser().resolve()
    manifest_output = args.manifest_output.expanduser().resolve()
    stills_root = args.stills_root.expanduser().resolve()
    overrides_path = args.frame_overrides.expanduser().resolve()
    applescript_path = args.apple_script.expanduser().resolve()
    quality_folder = resolve_effective_quality_folder(
        args.quality_folder,
        render_everything_qk=args.render_everything_qk,
    )

    if args.render_everything_qk:
        print("Rerendering all presentation sections at 2160p60 before building hybrid deck.")
        rerender_all_sections(quality_folder)

    audit_decisions = parse_report(report_path)
    deck, expanded_slides = load_expanded_source_slides(source_manifest, quality_folder)

    manifest_video_stems = {
        Path(slide["path"]).stem for slide in expanded_slides if slide["type"] == "video"
    }
    missing_decisions = sorted(manifest_video_stems - set(audit_decisions))
    if missing_decisions:
        raise ValueError(
            "The audit report does not cover these manifest video slides: "
            + ", ".join(missing_decisions)
        )

    jobs, unresolved_stems = collect_still_jobs(expanded_slides, audit_decisions)
    if unresolved_stems:
        raise ValueError(
            "Missing audit decisions for these expanded video slides: "
            + ", ".join(unresolved_stems)
        )

    unused_report_stems = sorted(set(audit_decisions) - manifest_video_stems)
    if unused_report_stems:
        print(
            "Warning: the audit report contains extra clip rows not present in the "
            "current source manifest:",
            ", ".join(unused_report_stems),
            file=sys.stderr,
        )

    extracted_stills: dict[Path, Path] = {}
    if jobs:
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        if ffmpeg_path is None or ffprobe_path is None:
            raise RuntimeError("ffmpeg and ffprobe are required to extract hybrid stills.")

        overrides = load_overrides(overrides_path)
        for index, job in enumerate(jobs, start=1):
            output_path = still_output_path(stills_root, quality_folder, job.video_path)
            extracted = ensure_still_for_video(
                job=job,
                output_path=output_path,
                ffmpeg_path=ffmpeg_path,
                ffprobe_path=ffprobe_path,
                overrides=overrides,
                overrides_path=overrides_path,
                report_path=report_path,
                sample_fps=args.sample_fps,
                analysis_width=args.analysis_width,
                min_still_seconds=args.min_still_seconds,
                motion_threshold=args.motion_threshold,
            )
            extracted_stills[job.video_path] = extracted.output_path
            if extracted.timestamp_seconds is None:
                timing_text = extracted.mode
            else:
                timing_text = f"{extracted.mode} @ {extracted.timestamp_seconds:.2f}s"
            print(
                f"[{index:02d}/{len(jobs):02d}] {job.stem} -> "
                f"{repo_relative_string(extracted.output_path)} ({timing_text})"
            )

    hybrid_slides, used_stems = build_hybrid_slide_records(
        expanded_slides,
        audit_decisions,
        extracted_stills,
    )

    if used_stems != manifest_video_stems:
        missing_used = sorted(manifest_video_stems - used_stems)
        if missing_used:
            raise ValueError(
                "The hybrid manifest rewrite skipped these manifest video slides: "
                + ", ".join(missing_used)
            )

    deck_base_name = args.deck_base_name or (
        DEFAULT_DECK_BASE_NAME
    )
    write_hybrid_manifest(manifest_output, deck, hybrid_slides, deck_base_name)

    disposition_counts = Counter(
        audit_decisions[stem].disposition for stem in manifest_video_stems
    )
    print(f"Wrote hybrid manifest to {repo_relative_string(manifest_output)}")
    print(
        "Applied audit decisions: "
        f"{disposition_counts[HybridDisposition.STATIC_STILL]} static still, "
        f"{disposition_counts[HybridDisposition.KEYNOTE_BUILD]} keynote build placeholder, "
        f"{disposition_counts[HybridDisposition.EMBEDDED_VIDEO]} embedded video."
    )

    if args.manifest_only:
        return 0

    deck_path = build_keynote_deck(applescript_path, manifest_output)
    print(f"Created hybrid Keynote deck at {deck_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
