#!/usr/bin/env python3
"""Flatten the presentation TOML manifest into simple records for AppleScript."""

from __future__ import annotations

import argparse
import ast
import glob
import re
import sys
from pathlib import Path

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - macOS system Python can be < 3.11
    tomllib = None

RECORD_SEPARATOR = "\x1e"
FIELD_SEPARATOR = "\x1f"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Expand the presentation deck manifest into flat slide records."
    )
    parser.add_argument("--manifest", required=True, help="Path to assets/presentation_deck.toml")
    parser.add_argument("--project-root", required=True, help="Repository root")
    parser.add_argument(
        "--quality-dir",
        default="480p15",
        help="Video-quality directory to substitute into {{quality_dir}} placeholders.",
    )
    return parser.parse_args()


def manifest_error(message: str) -> "NoReturn":
    raise SystemExit(f"Manifest error: {message}")


def resolve_path(raw_path: str, project_root: Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def render_template(value: str, quality_dir: str) -> str:
    return value.replace("{{quality_dir}}", quality_dir)


def ordered_media_paths(patterns: list[str], project_root: Path, quality_dir: str) -> list[Path]:
    matches: list[Path] = []
    for pattern in patterns:
        absolute_pattern = str(resolve_path(render_template(pattern, quality_dir), project_root))
        matches.extend(Path(p).resolve() for p in glob.glob(absolute_pattern))

    unique_matches = sorted(set(matches), key=slide_sort_key)
    return [path for path in unique_matches if path.is_file()]


def slide_sort_key(path: Path) -> tuple:
    name = path.name
    match = re.match(r"(\d+)([A-Za-z]*)_(.*)", name)
    if match:
        prefix, suffix, remainder = match.groups()
        return (0, int(prefix), suffix.casefold(), natural_key(remainder))
    return (1, natural_key(name))


def natural_key(text: str) -> tuple:
    parts = re.split(r"(\d+)", text)
    key: list[object] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.casefold())
    return tuple(key)


def load_manifest(manifest_path: Path) -> dict:
    try:
        if tomllib is not None:
            with manifest_path.open("rb") as handle:
                return tomllib.load(handle)

        return parse_basic_toml(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        manifest_error(f"manifest not found: {exc.filename}")
    except Exception as exc:
        manifest_error(str(exc))


def parse_basic_toml(source_text: str) -> dict:
    manifest: dict = {}
    current_target: dict | None = None
    lines = source_text.splitlines()
    line_index = 0

    while line_index < len(lines):
        raw_line = lines[line_index]
        stripped = strip_comments(raw_line).strip()
        line_index += 1

        if not stripped:
            continue

        if stripped == "[deck]":
            current_target = manifest.setdefault("deck", {})
            continue

        if stripped == "[[slide]]":
            slide_entry: dict = {}
            manifest.setdefault("slide", []).append(slide_entry)
            current_target = slide_entry
            continue

        if current_target is None:
            raise ValueError("Found a key/value pair before any [deck] or [[slide]] table.")

        if "=" not in stripped:
            raise ValueError(f"Invalid TOML line: {raw_line}")

        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value.startswith('"""'):
            multiline_value = raw_value[3:]
            while True:
                closing_index = multiline_value.find('"""')
                if closing_index != -1:
                    current_target[key] = multiline_value[:closing_index]
                    break
                if line_index >= len(lines):
                    raise ValueError(f"Unterminated multiline string for key {key!r}.")
                multiline_value += "\n" + lines[line_index]
                line_index += 1
            continue

        current_target[key] = parse_basic_toml_value(raw_value)

    return manifest


def strip_comments(line: str) -> str:
    result: list[str] = []
    in_string = False
    escaped = False

    for character in line:
        if character == '"' and not escaped:
            in_string = not in_string
        if character == "#" and not in_string:
            break
        result.append(character)
        escaped = character == "\\" and not escaped
        if character != "\\":
            escaped = False

    return "".join(result)


def parse_basic_toml_value(raw_value: str):
    if raw_value.startswith('"') and raw_value.endswith('"'):
        return ast.literal_eval(raw_value)

    if raw_value.startswith("[") and raw_value.endswith("]"):
        inner = raw_value[1:-1].strip()
        if not inner:
            return []
        parts = split_basic_toml_list(inner)
        return [parse_basic_toml_value(part.strip()) for part in parts]

    if raw_value.lower() == "true":
        return True

    if raw_value.lower() == "false":
        return False

    if re.fullmatch(r"-?\d+", raw_value):
        return int(raw_value)

    raise ValueError(f"Unsupported TOML value: {raw_value}")


def split_basic_toml_list(raw_list: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_string = False
    escaped = False

    for character in raw_list:
        if character == '"' and not escaped:
            in_string = not in_string
        if character == "," and not in_string:
            parts.append("".join(current))
            current = []
            escaped = False
            continue
        current.append(character)
        escaped = character == "\\" and not escaped
        if character != "\\":
            escaped = False

    if current:
        parts.append("".join(current))

    return parts


def validate_media_slide(
    slide_type: str, slide: dict, project_root: Path, quality_dir: str
) -> dict:
    raw_path = slide.get("path")
    if not raw_path:
        manifest_error(f"{slide_type!r} slide requires a path")

    resolved_path = resolve_path(render_template(raw_path, quality_dir), project_root)
    if not resolved_path.is_file():
        manifest_error(f"{slide_type!r} slide path not found: {resolved_path}")

    return {
        "type": slide_type,
        "path": str(resolved_path),
        "title": slide.get("title", ""),
        "subtitle": slide.get("subtitle", ""),
        "body": slide.get("body", ""),
        "notes": slide.get("notes", ""),
    }


def validate_text_slide(slide_type: str, slide: dict) -> dict:
    if not slide.get("title"):
        manifest_error(f"{slide_type!r} slide requires a title")

    return {
        "type": slide_type,
        "path": "",
        "title": slide.get("title", ""),
        "subtitle": slide.get("subtitle", ""),
        "body": slide.get("body", ""),
        "notes": slide.get("notes", ""),
    }


def expand_slides(slides: list[dict], project_root: Path, quality_dir: str) -> list[dict]:
    expanded: list[dict] = []

    for slide in slides:
        slide_type = slide.get("type")
        if not slide_type:
            manifest_error("every [[slide]] entry requires a type")

        if slide_type in {"title", "section", "text"}:
            expanded.append(validate_text_slide(slide_type, slide))
            continue

        if slide_type in {"video", "image", "pdf"}:
            expanded.append(validate_media_slide(slide_type, slide, project_root, quality_dir))
            continue

        if slide_type == "video_sequence":
            patterns: list[str] = []
            if "glob" in slide:
                patterns.append(slide["glob"])
            if "globs" in slide:
                patterns.extend(slide["globs"])
            if "paths" in slide:
                ordered_paths = [
                    str(resolve_path(render_template(path, quality_dir), project_root))
                    for path in slide["paths"]
                ]
                matches = [Path(path) for path in ordered_paths]
            else:
                matches = ordered_media_paths(patterns, project_root, quality_dir)

            if not matches:
                manifest_error("video_sequence slide did not match any files")

            for match in matches:
                if not match.is_file():
                    manifest_error(f"video_sequence file not found: {match}")
                expanded.append(
                    {
                        "type": "video",
                        "path": str(match.resolve()),
                        "title": "",
                        "subtitle": "",
                        "body": "",
                        "notes": "",
                    }
                )
            continue

        manifest_error(f"unsupported slide type: {slide_type}")

    return expanded


def serialize(deck: dict, slides: list[dict], project_root: Path) -> str:
    output_dir = resolve_path(deck.get("output_dir", "media/keynote"), project_root)
    slide_width = str(deck.get("slide_width", 1920))
    slide_height = str(deck.get("slide_height", 1080))
    deck_base_name = deck.get("deck_base_name", "phd-defence-presentation")

    records = [
        FIELD_SEPARATOR.join(
            [
                "deck",
                str(output_dir),
                deck_base_name,
                slide_width,
                slide_height,
            ]
        )
    ]

    for slide in slides:
        records.append(
            FIELD_SEPARATOR.join(
                [
                    "slide",
                    slide["type"],
                    slide["path"],
                    slide["title"],
                    slide["subtitle"],
                    slide["body"],
                    slide["notes"],
                ]
            )
        )

    return RECORD_SEPARATOR.join(records)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    manifest_path = resolve_path(args.manifest, project_root)

    manifest = load_manifest(manifest_path)
    deck = manifest.get("deck", {})
    slides = manifest.get("slide", [])
    if not isinstance(slides, list) or not slides:
        manifest_error("manifest must contain at least one [[slide]] entry")

    expanded_slides = expand_slides(slides, project_root, args.quality_dir)
    if not expanded_slides:
        manifest_error("manifest expanded to zero slides")

    sys.stdout.write(serialize(deck, expanded_slides, project_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
