#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

try:
    from build_static_rescue_deck import DEFAULT_OUTPUT as DEFAULT_RESCUE_DECK
    from export_frame_screener_pdf import (
        DEFAULT_FULL_PAGE_OUTPUT as DEFAULT_SCREENER_FULL_PAGE,
        DEFAULT_OUTPUT as DEFAULT_SCREENER,
    )
    from export_last_frames_pdf import (
        DEFAULT_IMAGES_ROOT,
        DEFAULT_OUTPUT as DEFAULT_LAST_FRAMES,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        discover_videos,
    )
except ModuleNotFoundError:
    from scripts.build_static_rescue_deck import DEFAULT_OUTPUT as DEFAULT_RESCUE_DECK
    from scripts.export_frame_screener_pdf import (
        DEFAULT_FULL_PAGE_OUTPUT as DEFAULT_SCREENER_FULL_PAGE,
        DEFAULT_OUTPUT as DEFAULT_SCREENER,
    )
    from scripts.export_last_frames_pdf import (
        DEFAULT_IMAGES_ROOT,
        DEFAULT_OUTPUT as DEFAULT_LAST_FRAMES,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        discover_videos,
    )


DEFAULT_TEXT_REPORT = REPO_ROOT / "media" / "reports" / "presentation_preflight.txt"
DEFAULT_JSON_REPORT = REPO_ROOT / "media" / "reports" / "presentation_preflight.json"


@dataclass(frozen=True)
class CheckResult:
    status: str
    category: str
    label: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the presentation backups and video renders are ready for use."
    )
    parser.add_argument(
        "--study",
        choices=("study1", "study2"),
        nargs="+",
        default=["study1", "study2"],
        help="Studies to include in the preflight check (default: study1 study2).",
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
        "--presentation-file",
        action="append",
        default=[],
        help="Optional presentation file to verify and include in the report. Repeat as needed.",
    )
    parser.add_argument(
        "--text-report",
        type=Path,
        default=DEFAULT_TEXT_REPORT,
        help=f"Path for the human-readable report (default: {DEFAULT_TEXT_REPORT}).",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        default=DEFAULT_JSON_REPORT,
        help=f"Path for the machine-readable report (default: {DEFAULT_JSON_REPORT}).",
    )
    return parser.parse_args()


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def pass_result(category: str, label: str, detail: str) -> CheckResult:
    return CheckResult("PASS", category, label, detail)


def warn_result(category: str, label: str, detail: str) -> CheckResult:
    return CheckResult("WARN", category, label, detail)


def fail_result(category: str, label: str, detail: str) -> CheckResult:
    return CheckResult("FAIL", category, label, detail)


def check_command(name: str) -> CheckResult:
    path = shutil.which(name)
    if path is None:
        return fail_result("dependency", name, "Not found on PATH.")
    return pass_result("dependency", name, path)


def probe_video(ffprobe_path: str, video_path: Path) -> tuple[bool, str]:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,width,height,avg_frame_rate:format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        error = result.stderr.strip() or "ffprobe failed."
        return (False, error)
    payload = json.loads(result.stdout)
    streams = payload.get("streams") or []
    format_info = payload.get("format") or {}
    if not streams:
        return (False, "No video stream found.")
    stream = streams[0]
    codec = stream.get("codec_name", "unknown")
    width = stream.get("width", "?")
    height = stream.get("height", "?")
    fps = stream.get("avg_frame_rate", "0/0")
    duration = float(format_info.get("duration", 0.0))
    if duration <= 0:
        return (False, "Duration is zero or missing.")
    return (True, f"{codec}, {width}x{height}, {fps} fps, {duration:.2f}s")


def check_pdf(path: Path) -> CheckResult:
    if not path.exists():
        return fail_result("artifact", path.name, "Missing.")
    size = path.stat().st_size
    if size == 0:
        return fail_result("artifact", path.name, "File exists but is empty.")
    return pass_result("artifact", path.name, f"{human_size(size)} at {path}")


def check_optional_file(path: Path) -> CheckResult:
    if not path.exists():
        return fail_result("presentation", path.name, "Missing.")
    size = path.stat().st_size
    if size == 0:
        return fail_result("presentation", path.name, "File exists but is empty.")
    return pass_result("presentation", path.name, f"{human_size(size)} at {path}")


def render_text_report(results: list[CheckResult]) -> str:
    lines = ["Presentation Preflight", "=====================", ""]
    summary = {
        "PASS": sum(result.status == "PASS" for result in results),
        "WARN": sum(result.status == "WARN" for result in results),
        "FAIL": sum(result.status == "FAIL" for result in results),
    }
    lines.append(
        f"Summary: {summary['PASS']} pass, {summary['WARN']} warn, {summary['FAIL']} fail"
    )
    lines.append("")
    for category in ("dependency", "artifact", "presentation", "video"):
        category_results = [result for result in results if result.category == category]
        if not category_results:
            continue
        lines.append(category.capitalize())
        lines.append("-" * len(category))
        for result in category_results:
            lines.append(f"[{result.status}] {result.label}: {result.detail}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_json_report(results: list[CheckResult]) -> str:
    payload = {
        "summary": {
            "pass": sum(result.status == "PASS" for result in results),
            "warn": sum(result.status == "WARN" for result in results),
            "fail": sum(result.status == "FAIL" for result in results),
        },
        "results": [
            {
                "status": result.status,
                "category": result.category,
                "label": result.label,
                "detail": result.detail,
            }
            for result in results
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def main() -> int:
    args = parse_args()
    results: list[CheckResult] = []

    for command_name in ("ffmpeg", "ffprobe"):
        results.append(check_command(command_name))
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path is None:
        raise SystemExit("ffprobe is required for preflight checks.")

    for path in (
        DEFAULT_LAST_FRAMES,
        DEFAULT_SCREENER,
        DEFAULT_SCREENER_FULL_PAGE,
        DEFAULT_RESCUE_DECK,
    ):
        results.append(check_pdf(path))

    if args.presentation_file:
        for presentation_path in args.presentation_file:
            results.append(check_optional_file(Path(presentation_path).expanduser().resolve()))
    else:
        results.append(
            warn_result(
                "presentation",
                "presentation file",
                "No presentation file supplied. Re-run with --presentation-file to validate the actual deck too.",
            )
        )

    entries = discover_videos(args.videos_root, args.images_root, args.study)
    results.append(
        pass_result(
            "video",
            "video inventory",
            f"Discovered {len(entries)} top-level study render videos.",
        )
    )
    for entry in entries:
        exists = entry.video_path.exists()
        if not exists:
            results.append(fail_result("video", entry.stem, "Video file is missing."))
            continue
        if entry.video_path.stat().st_size == 0:
            results.append(fail_result("video", entry.stem, "Video file is empty."))
            continue
        ok, detail = probe_video(ffprobe_path, entry.video_path)
        if ok:
            results.append(pass_result("video", entry.stem, detail))
        else:
            results.append(fail_result("video", entry.stem, detail))

    args.text_report.parent.mkdir(parents=True, exist_ok=True)
    args.json_report.parent.mkdir(parents=True, exist_ok=True)
    text_report = render_text_report(results)
    json_report = render_json_report(results)
    args.text_report.write_text(text_report, encoding="utf-8")
    args.json_report.write_text(json_report, encoding="utf-8")

    print(text_report, end="")
    print(f"Saved text report to {args.text_report}")
    print(f"Saved JSON report to {args.json_report}")

    has_failures = any(result.status == "FAIL" for result in results)
    return 1 if has_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
