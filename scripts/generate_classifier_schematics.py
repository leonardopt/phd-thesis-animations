#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "assets" / "images" / "references"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate schematic SVGs for a simple neural network and a simple SVM classifier."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory where the SVG files will be written (default: {DEFAULT_OUTPUT_DIR}).",
    )
    return parser.parse_args()


def _fmt(value: float) -> str:
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return text if text and text != "-0" else "0"


def _attrs(**kwargs: object) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, value in kwargs.items():
        if value is None:
            continue
        key = key.rstrip("_").replace("__", ":").replace("_", "-")
        if isinstance(value, float):
            attrs[key] = _fmt(value)
        else:
            attrs[key] = str(value)
    return attrs


def _add(parent: ET.Element, tag: str, **kwargs: object) -> ET.Element:
    return ET.SubElement(parent, tag, _attrs(**kwargs))


def _svg_root(width: int, height: int) -> ET.Element:
    return ET.Element(
        "svg",
        _attrs(
            xmlns=SVG_NS,
            width=width,
            height=height,
            viewBox=f"0 0 {width} {height}",
            fill="none",
        ),
    )


def _write_svg(path: Path, root: ET.Element) -> None:
    ET.indent(root, space="  ")
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode"),
        encoding="utf-8",
    )


def _trimmed_segment(
    start: tuple[float, float],
    end: tuple[float, float],
    start_radius: float,
    end_radius: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    norm = math.hypot(dx, dy)
    ux = dx / norm
    uy = dy / norm
    return (
        (start[0] + ux * start_radius, start[1] + uy * start_radius),
        (end[0] - ux * end_radius, end[1] - uy * end_radius),
    )


def build_neural_network_svg() -> ET.Element:
    width, height = 520, 341
    node_color = "#111827"
    link_color = "#4B5563"
    line_width = 2.8
    io_radius = 18
    hidden_radius = 15

    root = _svg_root(width, height)

    input_nodes = [(78, 124), (78, 241)]
    hidden_nodes = [(260, 58), (260, 170), (260, 282)]
    output_nodes = [(442, 124), (442, 241)]

    connections = _add(
        root,
        "g",
        stroke=link_color,
        stroke_width=line_width,
        stroke_linecap="round",
        stroke_linejoin="round",
    )

    for x1, y1 in input_nodes:
        for x2, y2 in hidden_nodes:
            (sx, sy), (ex, ey) = _trimmed_segment(
                (x1, y1),
                (x2, y2),
                io_radius,
                hidden_radius,
            )
            _add(connections, "line", x1=sx, y1=sy, x2=ex, y2=ey)

    for x1, y1 in hidden_nodes:
        for x2, y2 in output_nodes:
            (sx, sy), (ex, ey) = _trimmed_segment(
                (x1, y1),
                (x2, y2),
                hidden_radius,
                io_radius,
            )
            _add(connections, "line", x1=sx, y1=sy, x2=ex, y2=ey)

    io_nodes = _add(root, "g", fill=node_color)
    for x, y in [*input_nodes, *output_nodes]:
        _add(io_nodes, "circle", cx=x, cy=y, r=io_radius)

    hidden_group = _add(root, "g", fill=node_color)
    for x, y in hidden_nodes:
        _add(hidden_group, "circle", cx=x, cy=y, r=hidden_radius)

    return root


def _offset_segment(
    start: tuple[float, float],
    end: tuple[float, float],
    offset: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    norm = math.hypot(dx, dy)
    nx = -dy / norm
    ny = dx / norm
    return (
        (start[0] + nx * offset, start[1] + ny * offset),
        (end[0] + nx * offset, end[1] + ny * offset),
    )


def build_svm_svg() -> ET.Element:
    width, height = 117, 110
    axis_color = "#5B6B7A"
    decision_color = "#1D4ED8"
    margin_color = "#93C5FD"
    circle_color = "#0F766E"
    square_color = "#C2410C"
    point_size = 7.0

    root = _svg_root(width, height)

    axes = _add(
        root,
        "g",
        stroke=axis_color,
        stroke_width=3.0,
        stroke_linecap="round",
    )
    _add(axes, "line", x1=13, y1=13, x2=13, y2=96)
    _add(axes, "line", x1=13, y1=96, x2=104, y2=96)

    lines = _add(
        root,
        "g",
        stroke=margin_color,
        stroke_width=2.6,
        stroke_linecap="round",
        fill="none",
    )

    base_start = (28.0, 74.0)
    base_end = (82.0, 20.0)
    offsets = (-9.0, 0.0, 9.0)
    dash_patterns = ["7 5", None, "7 5"]
    opacities = [0.9, 1.0, 0.9]
    for offset, dasharray, opacity in zip(offsets, dash_patterns, opacities):
        (x1, y1), (x2, y2) = _offset_segment(base_start, base_end, offset)
        _add(
            lines,
            "line",
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            stroke_dasharray=dasharray,
            opacity=opacity,
            stroke=decision_color if dasharray is None else margin_color,
        )

    # Keep all circles on one side of the lower-left margin, with one marker
    # touching that margin.
    top_left_points = [
        (27, 22),
        (41, 17),
        (57, 22),
        (31, 38),
        (49.322, 35.0),
    ]
    # Keep all squares on the opposite side of the upper-right margin, with one
    # marker touching that margin.
    bottom_right_points = [
        (69.728, 52.0),
        (83, 42),
        (62, 64),
        (78, 61),
        (71, 78),
        (90, 71),
    ]

    circles = _add(root, "g", fill=circle_color, stroke="none")
    for x, y in top_left_points:
        _add(
            circles,
            "circle",
            cx=x,
            cy=y,
            r=point_size / 2,
        )

    squares = _add(root, "g", fill=square_color, stroke="none")
    for x, y in bottom_right_points:
        _add(
            squares,
            "rect",
            x=x - point_size / 2,
            y=y - point_size / 2,
            width=point_size,
            height=point_size,
            rx=1.3,
            ry=1.3,
        )

    return root


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "neural_network_schematic.svg": build_neural_network_svg(),
        "svm_classifier_schematic.svg": build_svm_svg(),
    }
    for filename, svg_root in outputs.items():
        _write_svg(output_dir / filename, svg_root)

    print(f"Wrote {len(outputs)} SVG files to {output_dir}")
    for filename in outputs:
        print(f"- {output_dir / filename}")


if __name__ == "__main__":
    main()
