#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
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
        DEFAULT_SECTION_KEYS,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        discover_videos,
    )
    from presentation_preflight import (
        DEFAULT_JSON_REPORT,
        DEFAULT_TEXT_REPORT,
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
        DEFAULT_SECTION_KEYS,
        DEFAULT_VIDEOS_ROOT,
        REPO_ROOT,
        discover_videos,
    )
    from scripts.presentation_preflight import (
        DEFAULT_JSON_REPORT,
        DEFAULT_TEXT_REPORT,
    )


DEFAULT_BUNDLE_ROOT = REPO_ROOT / "media" / "emergency_bundle"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a portable emergency bundle with videos and backup presentation artifacts."
    )
    parser.add_argument(
        "--section",
        "--study",
        dest="sections",
        choices=DEFAULT_SECTION_KEYS,
        nargs="+",
        default=list(DEFAULT_SECTION_KEYS),
        help=(
            "Presentation sections to include in the bundle "
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
        "--bundle-root",
        type=Path,
        default=DEFAULT_BUNDLE_ROOT,
        help=f"Parent directory where the bundle folder should be created (default: {DEFAULT_BUNDLE_ROOT}).",
    )
    parser.add_argument(
        "--bundle-name",
        type=str,
        default=None,
        help="Optional fixed bundle folder name. Defaults to a timestamped name.",
    )
    parser.add_argument(
        "--presentation-file",
        action="append",
        default=[],
        help="Optional presentation file to include in the bundle. Repeat as needed.",
    )
    parser.add_argument(
        "--skip-zip",
        action="store_true",
        help="Create only the bundle folder and skip the zip archive.",
    )
    return parser.parse_args()


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_readme(
    presentation_files: list[Path],
    bundled_pdfs: list[Path],
    bundled_reports: list[Path],
) -> str:
    lines = [
        "Emergency Presentation Bundle",
        "===========================",
        "",
        "Primary fallback order:",
    ]
    if presentation_files:
        lines.append("1. Open the presentation file in the presentation/ folder.")
        lines.append(f"2. If embedded videos fail, switch to pdfs/{DEFAULT_RESCUE_DECK.name}.")
    else:
        lines.append(f"1. Open pdfs/{DEFAULT_RESCUE_DECK.name}.")
    lines.append("3. If you need the original renders, use the videos/ folder.")
    lines.append("4. For manual frame lookup, use the screener PDFs in pdfs/.")
    lines.append("")
    lines.append("Bundled PDFs:")
    for path in bundled_pdfs:
        lines.append(f"- {path.name}")
    lines.append("")
    lines.append("Bundled reports:")
    for path in bundled_reports:
        lines.append(f"- {path.name}")
    lines.append("")
    lines.append("Generated on:")
    lines.append(f"- {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("Tip:")
    lines.append("- Copy this whole folder and the zip archive to cloud storage and a USB drive.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    bundle_name = args.bundle_name or f"presentation_emergency_bundle_{datetime.now():%Y%m%d_%H%M%S}"
    bundle_dir = args.bundle_root / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=True)

    entries = discover_videos(args.videos_root, args.images_root, args.sections)

    pdf_sources = [
        DEFAULT_RESCUE_DECK,
        DEFAULT_LAST_FRAMES,
        DEFAULT_SCREENER,
        DEFAULT_SCREENER_FULL_PAGE,
    ]
    report_sources = [
        DEFAULT_TEXT_REPORT,
        DEFAULT_JSON_REPORT,
    ]
    existing_pdfs = [path for path in pdf_sources if path.exists()]
    existing_reports = [path for path in report_sources if path.exists()]
    for path in existing_pdfs:
        copy_file(path, bundle_dir / "pdfs" / path.name)
    for path in existing_reports:
        copy_file(path, bundle_dir / "reports" / path.name)

    presentation_paths = [
        Path(path).expanduser().resolve()
        for path in args.presentation_file
        if Path(path).expanduser().exists()
    ]
    for presentation_path in presentation_paths:
        copy_file(presentation_path, bundle_dir / "presentation" / presentation_path.name)

    for entry in entries:
        relative_video_dir = entry.video_path.parent.relative_to(args.videos_root)
        copy_file(
            entry.video_path,
            bundle_dir / "videos" / relative_video_dir / entry.video_path.name,
        )

    readme_path = bundle_dir / "README.txt"
    bundled_pdf_paths = [bundle_dir / "pdfs" / path.name for path in existing_pdfs]
    bundled_report_paths = [bundle_dir / "reports" / path.name for path in existing_reports]
    readme_path.write_text(
        build_readme(presentation_paths, bundled_pdf_paths, bundled_report_paths),
        encoding="utf-8",
    )

    if not args.skip_zip:
        archive_base = bundle_dir.parent / bundle_dir.name
        archive_path = shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=bundle_dir.parent,
            base_dir=bundle_dir.name,
        )
        print(f"Wrote zip archive to {archive_path}")

    print(f"Wrote bundle folder to {bundle_dir}")
    print(
        f"Included {len(entries)} videos, {len(existing_pdfs)} backup PDFs, "
        f"and {len(existing_reports)} report files."
    )
    if presentation_paths:
        print(f"Included {len(presentation_paths)} presentation file(s).")
    else:
        print("No presentation file was supplied; the bundle contains only the backups and videos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
