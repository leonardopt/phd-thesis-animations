#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.render.helpers import (
    QUALITY_ALIASES,
    bootstrap_environment,
    normalize_quality_dir,
    quality_flag_for_dir,
)


def looks_like_quality_token(token: str) -> bool:
    lowered = token.lower()
    return lowered in QUALITY_ALIASES or lowered.startswith("-q")


def rewrite_quality_tokens(argv: list[str]) -> list[str]:
    if argv and looks_like_quality_token(argv[0]):
        return [f"--quality={argv[0]}", *argv[1:]]
    return argv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the full presentation refresh pipeline for one render quality."
    )
    parser.add_argument("quality_value", nargs="?", help="Quality flag or quality directory.")
    parser.add_argument("--quality", help="Quality flag or quality directory.")
    return parser


def resolve_quality(args: argparse.Namespace) -> tuple[str, str]:
    raw_quality = args.quality or args.quality_value or os.environ.get("QUALITY", "-qh")
    quality_dir = normalize_quality_dir(raw_quality)
    quality_flag = quality_flag_for_dir(quality_dir)
    return quality_flag, quality_dir


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run_command_capture(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(rewrite_quality_tokens(list(sys.argv[1:] if argv is None else argv)))
    quality_flag, quality_dir = resolve_quality(args)
    bootstrap_environment(REPO_ROOT)

    print(f"Refreshing presentation pipeline with quality {quality_flag} ({quality_dir})")

    print("\n[1/8] Syncing Python environment")
    run_command(["uv", "sync"])

    print("\n[2/8] Syncing small external assets")
    run_command(["uv", "run", "python", "scripts/sync_external_assets.py", "--groups", "small"])

    print("\n[3/8] Rendering all presentation sections")
    run_command([sys.executable, str(REPO_ROOT / "scripts" / "render" / "cli.py"), "all", quality_flag])

    print("\n[4/8] Writing duration report")
    run_command(["uv", "run", "python", "scripts/report_video_durations.py", "--quality", quality_dir])

    print("\n[5/8] Regenerating backup PDFs")
    run_command(["uv", "run", "python", "scripts/export_last_frames_pdf.py"])
    run_command(["uv", "run", "python", "scripts/export_frame_screener_pdf.py"])
    run_command(["uv", "run", "python", "scripts/build_static_rescue_deck.py"])

    print("\n[6/8] Building Keynote deck")
    deck_path = run_command_capture(
        ["osascript", "scripts/create_keynote_presentation.applescript", quality_flag]
    )
    if not deck_path:
        raise SystemExit("Keynote builder did not return a deck path.")
    print(f"Deck created at: {deck_path}")

    print("\n[7/8] Running presentation preflight")
    run_command(
        ["uv", "run", "python", "scripts/presentation_preflight.py", "--presentation-file", deck_path]
    )

    print("\n[8/8] Packaging emergency bundle")
    run_command(
        ["uv", "run", "python", "scripts/package_emergency_bundle.py", "--presentation-file", deck_path]
    )

    print("\nRefresh complete.")
    print(f"Quality: {quality_flag} ({quality_dir})")
    print(f"Deck: {deck_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
