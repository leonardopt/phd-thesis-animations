#!/usr/bin/env python3
"""Flatten the repo's presentation manifest into simple records for AppleScript.

The primary path uses `tomllib` when available. A narrow fallback parser is kept
for environments such as older system Python installations; it intentionally
supports only the TOML subset used by `assets/presentation_deck.toml`.

Optional presenter notes can live in a separate Markdown file referenced from
the deck config. That file uses one `## media-target` section per media slide,
where the heading points at a video/image/PDF path and the section body becomes
the Keynote presenter notes for that slide.
"""

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
NUMBERED_SECTION_VIDEO_RE = re.compile(r"(?P<prefix>\d{3})_(?P<name>.+)$")
KNOWN_QUALITY_DIRS = ("480p15", "720p30", "1080p60", "2160p60")
AUTO_QUALITY_PREFERENCE = ("1080p60", "720p30", "480p15", "2160p60")


def parse_args() -> argparse.Namespace:
    """Parse CLI flags for manifest expansion and quality placeholder rendering."""
    parser = argparse.ArgumentParser(
        description="Expand the presentation deck manifest into flat slide records."
    )
    parser.add_argument("--manifest", required=True, help="Path to assets/presentation_deck.toml")
    parser.add_argument("--project-root", required=True, help="Repository root")
    parser.add_argument(
        "--quality-dir",
        default="auto",
        help=(
            "Video-quality directory to substitute into {{quality_dir}} placeholders. "
            "Use 'auto' to keep explicit mixed-quality manifest paths and to pick "
            "the best existing clips for {{quality_dir}} placeholders. Use a "
            "concrete quality such as 2160p60 to override explicit media/video "
            "quality folders too."
        ),
    )
    return parser.parse_args()


def manifest_error(message: str) -> "NoReturn":
    """Exit immediately with a manifest-specific error message."""
    raise SystemExit(f"Manifest error: {message}")


def resolve_path(raw_path: str, project_root: Path) -> Path:
    """Resolve a manifest path relative to the project root when needed."""
    path = Path(raw_path)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def render_template(value: str, quality_dir: str) -> str:
    """Substitute `{{quality_dir}}` placeholders in manifest path templates."""
    return value.replace("{{quality_dir}}", quality_dir)


def replace_explicit_quality_dir(value: str, quality_dir: str) -> str | None:
    """Replace one concrete quality directory inside a media path or glob."""
    parts = value.split("/")
    for index, part in enumerate(parts):
        if part in KNOWN_QUALITY_DIRS:
            updated_parts = list(parts)
            updated_parts[index] = quality_dir
            return "/".join(updated_parts)
    return None


def render_value_for_quality(value: str, quality_dir: str) -> str:
    """Render one path or glob against a concrete quality selection."""
    if "{{quality_dir}}" in value:
        return render_template(value, quality_dir)

    overridden = replace_explicit_quality_dir(value, quality_dir)
    if overridden is not None:
        return overridden
    return value


def quality_dir_candidates(quality_dir: str) -> tuple[str, ...]:
    """Return the ordered concrete quality directories to try for one lookup."""
    if quality_dir == "auto":
        return AUTO_QUALITY_PREFERENCE
    return (quality_dir,)


def render_template_candidates(value: str, quality_dir: str) -> list[str]:
    """Render one path or glob against the requested quality selection."""
    if quality_dir == "auto":
        if "{{quality_dir}}" not in value:
            return [value]
        return [render_template(value, candidate) for candidate in quality_dir_candidates(quality_dir)]

    return [render_value_for_quality(value, quality_dir)]


def available_quality_dirs_for_value(
    value: str,
    project_root: Path,
    *,
    require_matches: bool,
) -> list[str]:
    """Report which concrete quality folders currently satisfy one templated value."""
    if "{{quality_dir}}" not in value and replace_explicit_quality_dir(value, KNOWN_QUALITY_DIRS[0]) is None:
        return []

    available: list[str] = []
    for candidate in KNOWN_QUALITY_DIRS:
        rendered_value = render_value_for_quality(value, candidate)
        resolved_path = resolve_path(rendered_value, project_root)
        if require_matches:
            matches = [
                Path(match).resolve()
                for match in glob.glob(str(resolved_path))
                if include_media_path(Path(match).resolve())
            ]
            if matches:
                available.append(candidate)
            continue

        if resolved_path.is_file():
            available.append(candidate)

    return available


def resolve_media_path(raw_path: str, project_root: Path, quality_dir: str, slide_type: str) -> Path:
    """Resolve one manifest media path, optionally auto-selecting an existing quality."""
    for rendered_path in render_template_candidates(raw_path, quality_dir):
        resolved_path = resolve_path(rendered_path, project_root)
        if resolved_path.is_file():
            return resolved_path

    if quality_dir != "auto":
        available_quality_dirs = available_quality_dirs_for_value(
            raw_path,
            project_root,
            require_matches=False,
        )
        if available_quality_dirs:
            manifest_error(
                f"{slide_type!r} slide path not found for quality {quality_dir}: "
                f"{resolve_path(render_template(raw_path, quality_dir), project_root)} "
                f"(available qualities: {', '.join(available_quality_dirs)})"
            )

    manifest_error(
        f"{slide_type!r} slide path not found: "
        f"{resolve_path(render_template_candidates(raw_path, quality_dir)[0], project_root)}"
    )


def ordered_paths_for_sequence(slide: dict, project_root: Path, quality_dir: str) -> list[Path]:
    """Resolve an explicit ordered path list for one video sequence slide."""
    ordered_matches: list[Path] = []
    for raw_path in slide["paths"]:
        ordered_matches.append(resolve_media_path(raw_path, project_root, quality_dir, "video_sequence"))
    return ordered_matches


def matches_for_pattern(pattern: str, project_root: Path, quality_dir: str) -> list[Path]:
    """Expand one media glob, optionally auto-selecting the first quality with clips."""
    for rendered_pattern in render_template_candidates(pattern, quality_dir):
        absolute_pattern = str(resolve_path(rendered_pattern, project_root))
        matches = [
            Path(path).resolve()
            for path in glob.glob(absolute_pattern)
            if include_media_path(Path(path).resolve())
        ]
        if matches:
            return matches
        if quality_dir != "auto":
            break
    return []


def ordered_media_paths(patterns: list[str], project_root: Path, quality_dir: str) -> list[Path]:
    """Expand media globs, de-duplicate matches, and return them in slide order."""
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(matches_for_pattern(pattern, project_root, quality_dir))

    unique_matches = sorted(set(matches), key=slide_sort_key)
    return [path for path in unique_matches if path.is_file()]


def include_media_path(path: Path) -> bool:
    if path.suffix.lower() != ".mp4" or path.parent.name != "sections":
        return True
    if not NUMBERED_SECTION_VIDEO_RE.fullmatch(path.stem):
        return False
    return not path.stem.endswith("_autocreated")


def is_numbered_section_video_path(path: Path) -> bool:
    """Return whether a path matches the deck's numbered section-clip contract."""
    if path.suffix.lower() != ".mp4":
        return False
    if path.parent.name != "sections":
        return False
    if NUMBERED_SECTION_VIDEO_RE.fullmatch(path.stem) is None:
        return False
    return not path.stem.endswith("_autocreated")


def validate_deck_video_path(path: Path) -> None:
    """Reject any deck video that does not come from numbered /sections/ clips."""
    if not is_numbered_section_video_path(path):
        manifest_error(
            "deck videos must point at numbered section clips under a /sections/ "
            f"directory: {path}"
        )


def slide_sort_key(path: Path) -> tuple:
    """Return a natural sort key that keeps numbered slide exports in narrative order."""
    name = path.name
    match = re.match(r"(\d+)([A-Za-z]*)_(.*)", name)
    if match:
        prefix, suffix, remainder = match.groups()
        return (0, int(prefix), suffix.casefold(), natural_key(remainder))
    return (1, natural_key(name))


def natural_key(text: str) -> tuple:
    """Split a string into alternating text and integer chunks for natural sorting."""
    parts = re.split(r"(\d+)", text)
    key: list[object] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.casefold())
    return tuple(key)


def load_manifest(manifest_path: Path) -> dict:
    """Load the manifest with `tomllib` or the repo-specific fallback parser."""
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
    """Parse the limited TOML subset used by this repository's deck manifest.

    Supported constructs are:
    - `[deck]` and `[[slide]]` tables
    - quoted strings and triple-quoted multiline strings
    - booleans and integers
    - flat lists containing those supported scalar values

    The fallback parser is intentionally not a full TOML implementation. It does
    not aim to support nested tables, floats, dates, inline tables, or arbitrary
    TOML edge cases beyond what the presentation manifest currently needs.
    """
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
    """Remove TOML comments from one line while preserving `#` inside strings."""
    result: list[str] = []
    in_string = False
    escaped = False

    for character in line:
        # Track quote state so we only treat `#` as a comment delimiter when the
        # character appears outside the string literal we are currently reading.
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
    """Parse one supported scalar or flat-list value from the fallback subset."""
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
    """Split a flat TOML list on top-level commas while honoring quoted strings."""
    parts: list[str] = []
    current: list[str] = []
    in_string = False
    escaped = False

    for character in raw_list:
        # The fallback parser only needs top-level list splitting, so it tracks
        # whether the current comma is inside a quoted string before splitting.
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
    """Validate and normalize one media slide entry from the manifest."""
    raw_path = slide.get("path")
    if not raw_path:
        manifest_error(f"{slide_type!r} slide requires a path")

    resolved_path = resolve_media_path(raw_path, project_root, quality_dir, slide_type)
    if slide_type == "video":
        validate_deck_video_path(resolved_path)

    return {
        "type": slide_type,
        "path": str(resolved_path),
        "title": slide.get("title", ""),
        "subtitle": slide.get("subtitle", ""),
        "body": slide.get("body", ""),
        "notes": slide.get("notes", ""),
    }


def validate_text_slide(slide_type: str, slide: dict) -> dict:
    """Validate and normalize one text-based slide entry from the manifest."""
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


def validate_native_slide(slide: dict, project_root: Path) -> dict:
    """Validate one native-object slide backed by a JSON layout spec."""
    raw_path = slide.get("path")
    if not raw_path:
        manifest_error("'native' slide requires a path")

    resolved_path = resolve_path(raw_path, project_root)
    if not resolved_path.is_file():
        manifest_error(f"'native' slide spec not found: {resolved_path}")

    return {
        "type": "native",
        "path": str(resolved_path),
        "title": slide.get("title", ""),
        "subtitle": slide.get("subtitle", ""),
        "body": slide.get("body", ""),
        "notes": slide.get("notes", ""),
    }


def trim_blank_lines(lines: list[str]) -> str:
    """Remove blank lines from the start/end of a block while preserving content."""
    start_index = 0
    end_index = len(lines)

    while start_index < end_index and lines[start_index].strip() == "":
        start_index += 1
    while end_index > start_index and lines[end_index - 1].strip() == "":
        end_index -= 1

    return "\n".join(lines[start_index:end_index])


def presenter_notes_path(deck: dict, project_root: Path) -> Path | None:
    """Resolve the optional deck-level presenter notes file path."""
    configured_keys = [
        key for key in ("presenter_notes_path", "notes_path") if deck.get(key)
    ]
    if len(configured_keys) > 1:
        manifest_error("deck may define only one of presenter_notes_path or notes_path")
    if not configured_keys:
        return None

    notes_path = resolve_path(deck[configured_keys[0]], project_root)
    if not notes_path.is_file():
        manifest_error(f"presenter notes file not found: {notes_path}")
    return notes_path


def parse_presenter_notes_heading(raw_line: str) -> str | None:
    """Return a media target from one `##` heading, or None for non-entry lines."""
    match = re.fullmatch(r"\s{0,3}##\s+(.+?)\s*", raw_line)
    if match is None:
        return None
    return normalize_presenter_notes_target(match.group(1))


def normalize_presenter_notes_target(raw_target: str) -> str:
    """Support plain paths, inline-code paths, or Markdown links in note headings."""
    target = raw_target.strip()

    link_match = re.fullmatch(r"\[[^]]*]\((.+)\)", target)
    if link_match is not None:
        target = link_match.group(1).strip()

    if target.startswith("`") and target.endswith("`") and len(target) >= 2:
        target = target[1:-1].strip()

    if target.startswith("<") and target.endswith(">") and len(target) >= 2:
        target = target[1:-1].strip()

    if target == "":
        manifest_error("presenter notes entry is missing its media target")

    return target


def stem_without_numeric_prefix(stem: str) -> str:
    """Drop the numbered slide prefix used by both old and current media names."""
    match = re.match(r"\d+[A-Za-z]*_(.*)", stem)
    if match is not None:
        return match.group(1)
    return stem


def canonical_media_stem(stem: str) -> str:
    """Normalize legacy CamelCase and current snake-case stems onto one alias."""
    stem = stem_without_numeric_prefix(stem)
    stem = stem.replace("-", "_").replace(" ", "_")

    tokens: list[str] = []
    for chunk in stem.split("_"):
        if not chunk:
            continue
        chunk_tokens = re.findall(
            r"[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+|\d+[a-z]?|[A-Z]",
            chunk,
        )
        if chunk_tokens:
            tokens.extend(token.lower() for token in chunk_tokens)
        else:
            tokens.append(chunk.lower())

    return "_".join(tokens)


def media_path_aliases(path: Path, project_root: Path, quality_dir: str) -> set[str]:
    """Build matching aliases for one concrete media path."""
    resolved_path = path.resolve()
    aliases = {
        str(resolved_path),
        resolved_path.name,
        resolved_path.stem,
        stem_without_numeric_prefix(resolved_path.stem),
        canonical_media_stem(resolved_path.stem),
    }

    try:
        relative_path = resolved_path.relative_to(project_root)
    except ValueError:
        return aliases

    aliases.add(relative_path.as_posix())
    templated_path = quality_placeholder_path(relative_path)
    if templated_path is not None:
        aliases.add(templated_path)

    return aliases


def quality_placeholder_path(relative_path: Path) -> str | None:
    """Replace one concrete quality directory with `{{quality_dir}}` when present."""
    path_parts = list(relative_path.parts)
    for index, path_part in enumerate(path_parts):
        if path_part in KNOWN_QUALITY_DIRS:
            path_parts[index] = "{{quality_dir}}"
            return Path(*path_parts).as_posix()
    return None


def presenter_note_aliases(raw_target: str, project_root: Path, quality_dir: str) -> set[str]:
    """Normalize one presenter-notes target into comparable aliases."""
    aliases = {raw_target}
    for rendered_target in render_template_candidates(raw_target, quality_dir):
        aliases.add(rendered_target)
        aliases.update(
            media_path_aliases(
                resolve_path(rendered_target, project_root),
                project_root,
                quality_dir,
            )
        )
    return {alias for alias in aliases if alias}


def presenter_note_exact_aliases(
    raw_target: str, project_root: Path, quality_dir: str
) -> set[str]:
    """Return only exact-path aliases for one presenter-notes target."""
    aliases = {raw_target}
    for rendered_target in render_template_candidates(raw_target, quality_dir):
        aliases.add(rendered_target)
        aliases.add(str(resolve_path(rendered_target, project_root)))
    return {alias for alias in aliases if alias}


def presenter_note_label_from_path(path_text: str) -> str:
    """Build a readable fallback note label from a rendered media filename."""
    stem = Path(path_text).stem
    stem = stem_without_numeric_prefix(stem)

    tokens = re.findall(
        r"[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+|\d+[a-z]?|[A-Z]",
        stem,
    )
    if not tokens:
        return stem

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_chunk_has_digit = False

    for token in tokens:
        token_has_digit = any(character.isdigit() for character in token)
        token_is_suffix = (len(token) == 1 and token.isalpha()) or token_has_digit

        if not current_chunk:
            current_chunk = [token]
            current_chunk_has_digit = token_has_digit
            continue

        if token_is_suffix:
            current_chunk.append(token)
            current_chunk_has_digit = current_chunk_has_digit or token_has_digit
            continue

        if current_chunk_has_digit:
            chunks.append(" ".join(current_chunk))
            current_chunk = [token]
            current_chunk_has_digit = token_has_digit
            continue

        current_chunk.append(token)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return " - ".join(chunks)


def load_presenter_notes(notes_path: Path, project_root: Path, quality_dir: str) -> list[dict]:
    """Parse the optional Markdown presenter-notes file into target/body records."""
    entries: list[dict] = []
    current_target: str | None = None
    current_lines: list[str] = []

    for raw_line in notes_path.read_text(encoding="utf-8").splitlines():
        heading_target = parse_presenter_notes_heading(raw_line)
        if heading_target is None:
            if current_target is not None:
                current_lines.append(raw_line)
            continue

        if current_target is not None:
            entries.append(
                {
                    "target": current_target,
                    "aliases": presenter_note_aliases(current_target, project_root, quality_dir),
                    "notes": trim_blank_lines(current_lines),
                }
            )

        current_target = heading_target
        current_lines = []

    if current_target is not None:
        entries.append(
            {
                "target": current_target,
                "aliases": presenter_note_aliases(current_target, project_root, quality_dir),
                "notes": trim_blank_lines(current_lines),
            }
        )

    return entries


def display_path(path_text: str, project_root: Path) -> str:
    """Prefer project-relative paths in manifest error messages when possible."""
    path = Path(path_text)
    try:
        return path.resolve().relative_to(project_root).as_posix()
    except ValueError:
        return str(path)


def merge_presenter_notes(
    deck: dict, slides: list[dict], project_root: Path, quality_dir: str
) -> list[dict]:
    """Inject deck-level presenter notes onto matching media slides."""
    notes_path = presenter_notes_path(deck, project_root)
    if notes_path is None:
        return slides

    note_entries = load_presenter_notes(notes_path, project_root, quality_dir)
    if not note_entries:
        return slides

    eligible_slide_aliases = {
        slide["path"]: media_path_aliases(Path(slide["path"]), project_root, quality_dir)
        for slide in slides
        if slide["path"] and not slide["notes"]
    }

    notes_by_slide_path: dict[str, str] = {}
    for entry in note_entries:
        exact_aliases = presenter_note_exact_aliases(
            entry["target"], project_root, quality_dir
        )
        exact_matched_paths = [
            slide_path
            for slide_path, aliases in eligible_slide_aliases.items()
            if aliases & exact_aliases
        ]

        matched_paths = exact_matched_paths or [
            slide_path
            for slide_path, aliases in eligible_slide_aliases.items()
            if aliases & entry["aliases"]
        ]

        if len(matched_paths) > 1:
            matching_slides = ", ".join(
                display_path(slide_path, project_root) for slide_path in matched_paths
            )
            manifest_error(
                "presenter notes target "
                f"{entry['target']!r} matched multiple slides: {matching_slides}"
            )

        if not matched_paths:
            continue

        matched_path = matched_paths[0]
        if matched_path in notes_by_slide_path:
            manifest_error(
                "multiple presenter notes entries matched slide "
                f"{display_path(matched_path, project_root)}"
            )
        notes_by_slide_path[matched_path] = entry["notes"] or presenter_note_label_from_path(
            matched_path
        )

    merged_slides: list[dict] = []
    for slide in slides:
        notes_text = notes_by_slide_path.get(slide["path"])
        if notes_text is not None and not slide["notes"]:
            merged_slides.append({**slide, "notes": notes_text})
        else:
            merged_slides.append(slide)

    return merged_slides


def expand_slides(slides: list[dict], project_root: Path, quality_dir: str) -> list[dict]:
    """Expand manifest slide entries into the flat records consumed by AppleScript.

    `video_sequence` entries are expanded into one normalized `video` record per
    matched media file so downstream consumers do not need to understand the
    higher-level sequencing directive.
    """
    expanded: list[dict] = []

    for slide in slides:
        slide_type = slide.get("type")
        if not slide_type:
            manifest_error("every [[slide]] entry requires a type")

        if slide_type in {"title", "section", "text"}:
            expanded.append(validate_text_slide(slide_type, slide))
            continue

        if slide_type == "native":
            expanded.append(validate_native_slide(slide, project_root))
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
                matches = ordered_paths_for_sequence(slide, project_root, quality_dir)
            else:
                matches = ordered_media_paths(patterns, project_root, quality_dir)

            if not matches:
                if quality_dir != "auto":
                    available_quality_dirs = sorted(
                        {
                            available_quality_dir
                            for pattern in patterns
                            for available_quality_dir in available_quality_dirs_for_value(
                                pattern,
                                project_root,
                                require_matches=True,
                            )
                        }
                    )
                    if available_quality_dirs:
                        manifest_error(
                            "video_sequence slide did not match any files for quality "
                            f"{quality_dir} (available qualities: {', '.join(available_quality_dirs)})"
                        )
                manifest_error("video_sequence slide did not match any files")

            for match in matches:
                if not match.is_file():
                    manifest_error(f"video_sequence file not found: {match}")
                validate_deck_video_path(match.resolve())
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
    """Serialize deck metadata and normalized slides into record-separated text."""
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
    """Load, validate, expand, and serialize the presentation manifest."""
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    manifest_path = resolve_path(args.manifest, project_root)
    quality_dir = args.quality_dir

    manifest = load_manifest(manifest_path)
    deck = manifest.get("deck", {})
    slides = manifest.get("slide", [])
    if not isinstance(slides, list) or not slides:
        manifest_error("manifest must contain at least one [[slide]] entry")

    expanded_slides = expand_slides(slides, project_root, quality_dir)
    expanded_slides = merge_presenter_notes(deck, expanded_slides, project_root, quality_dir)
    if not expanded_slides:
        manifest_error("manifest expanded to zero slides")

    sys.stdout.write(serialize(deck, expanded_slides, project_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
