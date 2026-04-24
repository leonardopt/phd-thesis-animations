#!/usr/bin/env python3
"""Generate native Keynote layout specs for selected intro slides.

These specs rebuild static intro literature slides as native Keynote objects
instead of flattened still images, so text and images remain selectable inside
the exported `.key` deck.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable

from manim import Dot, ImageMobject, Line, Tex, VGroup

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scenes.intro import _build_intro_d_layout, _build_intro_e_layout

OUTPUT_DIR = REPO_ROOT / "assets" / "native_specs"
FRAME_WIDTH = 14.2222222222
FRAME_HEIGHT = 8.0
PX_PER_UNIT = 135.0
DEFAULT_FONT = "CMUSerif-Roman"
DEFAULT_BOLD_FONT = "CMUSerif-Bold"


def px_x(x: float) -> float:
    return round((x + (FRAME_WIDTH / 2.0)) * PX_PER_UNIT, 2)


def px_y(y: float) -> float:
    return round(((FRAME_HEIGHT / 2.0) - y) * PX_PER_UNIT, 2)


def bbox_for_mobject(mobject) -> dict[str, float]:
    center_x, center_y, _ = mobject.get_center()
    width = float(mobject.width) * PX_PER_UNIT
    height = float(mobject.height) * PX_PER_UNIT
    return {
        "x": round(px_x(center_x) - (width / 2.0), 2),
        "y": round(px_y(center_y) - (height / 2.0), 2),
        "w": round(width, 2),
        "h": round(height, 2),
    }


def line_points_for_mobject(line: Line) -> dict[str, float]:
    start_x, start_y, _ = line.get_start()
    end_x, end_y, _ = line.get_end()
    return {
        "x1": px_x(float(start_x)),
        "y1": px_y(float(start_y)),
        "x2": px_x(float(end_x)),
        "y2": px_y(float(end_y)),
    }


def normalize_tex_string(tex_string: str) -> tuple[str, str]:
    font_name = DEFAULT_BOLD_FONT if r"\textbf{" in tex_string else DEFAULT_FONT
    text = tex_string
    replacements = {
        r"\textbf{": "",
        r"\&": "&",
        r"\\": "\n",
        "{": "",
        "}": "",
        "~": " ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"\s+", " ", text.replace("\n ", "\n")).strip()
    return text, font_name


def color_hex_for_mobject(mobject) -> str:
    color = mobject.get_color()
    if hasattr(color, "to_hex"):
        return color.to_hex()
    return str(color)


def text_item_for_tex(tex: Tex) -> dict[str, object]:
    bbox = bbox_for_mobject(tex)
    text, font_name = normalize_tex_string(tex.tex_string)
    return {
        "kind": "text",
        "text": text,
        "font": font_name,
        "size": round(float(tex.font_size), 2),
        "color": color_hex_for_mobject(tex),
        **bbox,
    }


def image_item_for_image(image: ImageMobject) -> dict[str, object]:
    bbox = bbox_for_mobject(image)
    path = Path(image.path).resolve().relative_to(REPO_ROOT).as_posix()
    return {"kind": "image", "path": path, **bbox}


def line_item_for_line(line: Line) -> dict[str, object]:
    return {
        "kind": "line",
        "color": color_hex_for_mobject(line),
        "stroke_width": round(float(line.stroke_width), 2),
        **line_points_for_mobject(line),
    }


def dot_item_for_dot(dot: Dot) -> dict[str, object]:
    bbox = bbox_for_mobject(dot)
    size_guess = max(14.0, round(float(dot.height) * PX_PER_UNIT * 1.15, 2))
    return {
        "kind": "text",
        "text": "●",
        "font": DEFAULT_FONT,
        "size": size_guess,
        "color": color_hex_for_mobject(dot),
        **bbox,
    }


def iter_leaf_elements(mobject) -> Iterable[object]:
    if isinstance(mobject, (Tex, ImageMobject, Line, Dot)):
        yield mobject
        return
    if isinstance(mobject, VGroup) or hasattr(mobject, "__iter__"):
        for child in mobject:
            yield from iter_leaf_elements(child)


def item_for_element(element) -> dict[str, object] | None:
    if isinstance(element, Tex):
        return text_item_for_tex(element)
    if isinstance(element, ImageMobject):
        return image_item_for_image(element)
    if isinstance(element, Line):
        return line_item_for_line(element)
    if isinstance(element, Dot):
        return dot_item_for_dot(element)
    return None


def spec_for_elements(elements: Iterable[object]) -> dict[str, object]:
    spec_items: list[dict[str, object]] = []
    for element in elements:
        item = item_for_element(element)
        if item is not None:
            spec_items.append(item)
    return {"elements": spec_items}


def write_spec(name: str, spec: dict[str, object]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / name
    output_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def build_intro_classical_view_spec() -> dict[str, object]:
    state = _build_intro_d_layout()
    elements: list[object] = []
    elements.extend(iter_leaf_elements(state["title"]))
    elements.append(state["timeline_line"])
    for column in state["columns"]:
        elements.extend(iter_leaf_elements(column))
    elements.extend(iter_leaf_elements(state["takeaway"]))
    return spec_for_elements(elements)


def build_intro_sensory_recruitment_spec() -> dict[str, object]:
    state = _build_intro_e_layout()
    elements: list[object] = []
    elements.extend(iter_leaf_elements(state["title"]))
    elements.append(state["timeline_line"])
    elements.extend(iter_leaf_elements(state["dots"]))
    for entry in state["entries"]:
        elements.extend(iter_leaf_elements(entry))
    elements.extend(iter_leaf_elements(state["figure_column"]))
    return spec_for_elements(elements)


def main() -> int:
    written_paths = [
        write_spec("intro_classical_view.json", build_intro_classical_view_spec()),
        write_spec(
            "intro_sensory_recruitment.json",
            build_intro_sensory_recruitment_spec(),
        ),
    ]
    for path in written_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
