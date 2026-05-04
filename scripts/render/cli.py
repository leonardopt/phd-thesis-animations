#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.render.config import ORDERED_SECTIONS, SECTION_CONFIGS, SectionConfig
from scripts.render.helpers import (
    QUALITY_ALIASES,
    bootstrap_environment,
    clear_stale_section_clips,
    collect_concat_inputs,
    delete_combined_scene_renders,
    ensure_ffmpeg_available,
    normalize_quality_dir,
    quality_flag_for_dir,
    resolve_output_path,
)


VIDEOS_ROOT = REPO_ROOT / "media" / "videos"


def looks_like_quality_token(token: str) -> bool:
    lowered = token.lower()
    return lowered in QUALITY_ALIASES or lowered.startswith("-q")


def rewrite_quality_tokens(argv: list[str]) -> list[str]:
    if not argv:
        return argv

    tokens = list(argv)
    if tokens[0] == "section" and len(tokens) >= 3 and looks_like_quality_token(tokens[2]):
        return tokens[:2] + [f"--quality={tokens[2]}"] + tokens[3:]
    if tokens[0] in {"all", "single-video"} and len(tokens) >= 2 and looks_like_quality_token(tokens[1]):
        return tokens[:1] + [f"--quality={tokens[1]}"] + tokens[2:]
    return tokens


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render numbered presentation sections and concatenate them when needed."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    section_parser = subparsers.add_parser("section", help="Render one numbered presentation section.")
    section_parser.add_argument("section", choices=tuple(SECTION_CONFIGS))
    section_parser.add_argument("quality_value", nargs="?", help="Quality flag or quality directory.")
    section_parser.add_argument("--quality", help="Quality flag or quality directory.")
    section_parser.set_defaults(func=command_section)

    all_parser = subparsers.add_parser("all", help="Render all numbered presentation sections.")
    all_parser.add_argument("quality_value", nargs="?", help="Quality flag or quality directory.")
    all_parser.add_argument("--quality", help="Quality flag or quality directory.")
    all_parser.set_defaults(func=command_all)

    single_video_parser = subparsers.add_parser(
        "single-video",
        help="Render all numbered sections and concatenate them into one MP4.",
    )
    single_video_parser.add_argument("quality_value", nargs="?", help="Quality flag or quality directory.")
    single_video_parser.add_argument("--quality", help="Quality flag or quality directory.")
    single_video_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Destination MP4 path. Defaults to media/videos/presentation_full_<quality>.mp4.",
    )
    single_video_parser.set_defaults(func=command_single_video)

    return parser


def resolve_quality(args: argparse.Namespace, *, default: str) -> tuple[str, str]:
    raw_quality = args.quality or args.quality_value or default
    quality_dir = normalize_quality_dir(raw_quality)
    quality_flag = quality_flag_for_dir(quality_dir)
    return quality_flag, quality_dir


def render_section(
    section: SectionConfig,
    *,
    quality_flag: str,
    quality_dir: str,
    bootstrap_env: bool = True,
) -> None:
    if bootstrap_env:
        bootstrap_environment(REPO_ROOT)

    clear_stale_section_clips(VIDEOS_ROOT, section.output_dir, quality_dir)
    print(f"[1/1] {section.status_line}")

    command = [
        "uv",
        "run",
        "manim",
        str(section.scene_file.relative_to(REPO_ROOT)),
        section.scene_class,
        quality_flag,
        "--save_sections",
    ]
    if section.disable_caching:
        command.append("--disable_caching")

    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    delete_combined_scene_renders(VIDEOS_ROOT, section.output_dir, quality_dir)
    print(f"Done. Section videos saved to media/videos/{section.output_dir}/{quality_dir}/sections/")


def render_named_section(section_key: str, quality_value: str) -> None:
    quality_dir = normalize_quality_dir(quality_value)
    quality_flag = quality_flag_for_dir(quality_dir)
    render_section(SECTION_CONFIGS[section_key], quality_flag=quality_flag, quality_dir=quality_dir)


def render_all_sections(quality_value: str) -> None:
    quality_dir = normalize_quality_dir(quality_value)
    quality_flag = quality_flag_for_dir(quality_dir)
    bootstrap_environment(REPO_ROOT)

    total = len(ORDERED_SECTIONS)
    for idx, section in enumerate(ORDERED_SECTIONS, start=1):
        print(f"[{idx}/{total}] Running {section.key} {quality_flag}")
        render_section(
            section,
            quality_flag=quality_flag,
            quality_dir=quality_dir,
            bootstrap_env=False,
        )

    print(f"Done. Rendered all presentation sections with quality {quality_flag}.")


def render_single_video(quality_value: str, output: Path | None = None) -> None:
    quality_dir = normalize_quality_dir(quality_value)
    quality_flag = quality_flag_for_dir(quality_dir)
    bootstrap_environment(REPO_ROOT)
    ffmpeg_path = ensure_ffmpeg_available()

    print("[1/2] Rendering all presentation sections")
    render_all_sections(quality_flag)

    print("[2/2] Collecting section clips for concatenation")
    clip_paths = collect_concat_inputs(
        VIDEOS_ROOT,
        quality_dir,
        [section.output_dir for section in ORDERED_SECTIONS],
    )
    output_path = resolve_output_path(REPO_ROOT, output, quality_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as concat_file:
        concat_path = Path(concat_file.name)
        for clip_path in clip_paths:
            concat_file.write(f"file '{clip_path}'\n")

    try:
        print(f"Concatenating all rendered clips into {output_path}")
        result = subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-c",
                "copy",
                str(output_path),
            ],
            cwd=REPO_ROOT,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)
    finally:
        concat_path.unlink(missing_ok=True)

    print(f"Done. Single video saved to {output_path}")


def command_section(args: argparse.Namespace) -> int:
    quality_flag, _quality_dir = resolve_quality(args, default="-ql")
    render_named_section(args.section, quality_flag)
    return 0


def command_all(args: argparse.Namespace) -> int:
    quality_flag, _quality_dir = resolve_quality(args, default="-ql")
    render_all_sections(quality_flag)
    return 0


def command_single_video(args: argparse.Namespace) -> int:
    quality_flag, _quality_dir = resolve_quality(args, default="-ql")
    render_single_video(quality_flag, args.output)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(rewrite_quality_tokens(list(sys.argv[1:] if argv is None else argv)))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
