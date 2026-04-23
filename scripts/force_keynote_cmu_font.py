#!/usr/bin/env python3
"""Rewrite Keynote deck font references to Computer Modern Unicode."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
import zipfile
from pathlib import Path


FONT_MAP = {
    "HelveticaNeue": "CMUSerif-Roman",
    "HelveticaNeue-Bold": "CMUSerif-Bold",
    "HelveticaNeue-Medium": "CMUSerif-Bold",
    "LucidaGrande": "CMUSerif-Roman",
    "MarkerFelt-Thin": "CMUSerif-Italic",
}

FONT_NAME_RE = re.compile(r'(<sf:fontName><sf:string sfa:string=")([^"]+)("/>)')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite a Keynote .key bundle to use CMU Serif fonts."
    )
    parser.add_argument(
        "--presentation-file",
        required=True,
        type=Path,
        help="Path to the Keynote .key file to update in place.",
    )
    return parser.parse_args()


def build_zipinfo_from(source: zipfile.ZipInfo) -> zipfile.ZipInfo:
    target = zipfile.ZipInfo(filename=source.filename, date_time=source.date_time)
    target.comment = source.comment
    target.extra = source.extra
    target.create_system = source.create_system
    target.create_version = source.create_version
    target.extract_version = source.extract_version
    target.flag_bits = source.flag_bits
    target.volume = source.volume
    target.internal_attr = source.internal_attr
    target.external_attr = source.external_attr
    target.compress_type = source.compress_type
    return target


def rewrite_index_apxl(index_text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        original_name = match.group(2)
        replacement_name = FONT_MAP.get(original_name)
        if replacement_name is None:
            return match.group(0)
        replacements[original_name] = replacement_name
        return f'{match.group(1)}{replacement_name}{match.group(3)}'

    return FONT_NAME_RE.sub(replace, index_text), replacements


def rewrite_keynote_bundle(presentation_file: Path) -> dict[str, str]:
    if not presentation_file.exists():
        raise FileNotFoundError(f"Presentation file not found: {presentation_file}")

    with zipfile.ZipFile(presentation_file, "r") as source_zip:
        try:
            index_text = source_zip.read("index.apxl").decode("utf-8")
        except KeyError as exc:
            raise RuntimeError(f"{presentation_file} does not contain index.apxl") from exc

        rewritten_index, replacements = rewrite_index_apxl(index_text)
        if not replacements:
            return {}

        with tempfile.NamedTemporaryFile(
            prefix=presentation_file.stem + "_",
            suffix=".key",
            dir=presentation_file.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)

        try:
            with zipfile.ZipFile(temp_path, "w") as target_zip:
                for item in source_zip.infolist():
                    payload = source_zip.read(item.filename)
                    if item.filename == "index.apxl":
                        payload = rewritten_index.encode("utf-8")
                    target_zip.writestr(build_zipinfo_from(item), payload)
            temp_path.replace(presentation_file)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    return replacements


def main() -> int:
    args = parse_args()
    replacements = rewrite_keynote_bundle(args.presentation_file.resolve())
    if not replacements:
        print(f"No font replacements applied to {args.presentation_file}")
        return 0

    summary = ", ".join(
        f"{source}->{target}" for source, target in sorted(replacements.items())
    )
    print(f"Updated {args.presentation_file} with CMU Serif fonts: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
