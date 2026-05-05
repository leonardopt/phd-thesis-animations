"""
Methods — sectioned production render.

Render from this file to keep all methods outputs in the same
`media/videos/02_methods/...` folder.

Production render:
    uv run manim scenes/methods.py Methods -ql --save_sections

Legacy standalone renders:
    uv run manim scenes/methods.py MethodsStimulusRequirementsA -ql
    uv run manim scenes/methods.py MethodsStimulusRequirementsB -ql
    uv run manim scenes/methods.py MethodsStimulusRequirementsC -ql
    uv run manim scenes/methods.py MethodsStimulusRequirementsD -ql
    uv run manim scenes/methods.py MethodsExistingApproaches -ql
    uv run manim scenes/methods.py MethodsDiffusionOpportunity -ql
    uv run manim scenes/methods.py MethodsDiffusionExplainerA -ql
    uv run manim scenes/methods.py MethodsDiffusionExplainerB -ql
    uv run manim scenes/methods.py MethodsProjectPlan -ql
"""
from __future__ import annotations

import base64
from functools import lru_cache
from io import BytesIO
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np
from matplotlib import colormaps
from PIL import Image as PILImage
from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import REPO_ROOT, env_path, section_output_dir, simplify_manim_section_video_names


_SECTION_OUTPUT_DIR = section_output_dir("methods")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "methods"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)

_METHODS_SCENE_ORDER: dict[str, str] = {
    "MethodsStimulusRequirements": "01",
    "MethodsStimulusRequirementsA": "01",
    "MethodsStimulusRequirementsB": "02",
    "MethodsStimulusRequirementsC": "03",
    "MethodsStimulusRequirementsD": "04",
    "MethodsExistingApproaches": "05",
    "MethodsGANsProofOfConcept": "05",
    "MethodsDiffusionExplainerA": "06",
    "MethodsDiffusionExplainerB": "07",
    "MethodsDiffusionOpportunity": "08",
    "MethodsProjectPlan": "09",
}
_METHODS_OUTPUT_NAMES: dict[str, str] = {
    "MethodsGANsProofOfConcept": "MethodsExistingApproaches",
    "MethodsDiffusionExplainerA": "MethodsDiffusionModelsExplainerA",
    "MethodsDiffusionExplainerB": "MethodsDiffusionModelsExplainerB",
}


class _MethodsNumberedScene:
    """Mixin that assigns methods output filenames while preserving scene names."""

    def __init__(self, *args, **kwargs):
        scene_name = self.__class__.__name__
        number = _METHODS_SCENE_ORDER.get(scene_name, "")
        output_name = _METHODS_OUTPUT_NAMES.get(scene_name, scene_name)
        if config.output_file == "methods":
            config.output_file = f"{number}_{output_name}" if number else output_name
        super().__init__(*args, **kwargs)


def _wrap_scene(scene_cls: type[Scene]) -> type[Scene]:
    """Wrap a scene so it inherits section numbering without renaming it."""

    class _Wrapped(_MethodsNumberedScene, scene_cls):
        pass

    _Wrapped.__name__ = scene_cls.__name__
    _Wrapped.__qualname__ = scene_cls.__name__
    _Wrapped.__module__ = __name__
    _Wrapped.__doc__ = scene_cls.__doc__
    return _Wrapped


# ── Palette ───────────────────────────────────────────────────────────────────
BG = WHITE
INK = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#374151"
BLUE = "#3E5C76"
AMBER = "#8A6642"
GREEN = "#4F6D5E"
RED = "#8B5A52"
ACCENT = BLUE
PANEL = "#F8FAFC"


# ── Assets ────────────────────────────────────────────────────────────────────
_INTRO_STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
_ANATOMY_IMAGE_DIR = REPO_ROOT / "assets" / "images" / "anatomy"
_BRAIN_ICON_PATH = REPO_ROOT / "assets" / "images" / "study2" / "brain_icon_sagittal.png"
_METHODS_PROJECT_PLAN_MODEL_ICON_PATH = (
    REPO_ROOT / "assets" / "images" / "references" / "neural_network_schematic.svg"
)
_METHODS_PROJECT_PLAN_VALIDATION_ICON_PATH = (
    REPO_ROOT / "assets" / "images" / "study1" / "stage2" / "computer.png"
)
_METHODS_PROJECT_PLAN_NEURO_ICON_PATH = (
    _ANATOMY_IMAGE_DIR / "visual_cortex.png"
)
_METHODS_REQUIREMENTS_A_PNG_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "requirements_a.png"
)
_METHODS_REQUIREMENTS_A_SVG_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "requirements_a.svg"
)
_METHODS_REQUIREMENTS_B_PNG_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "requirements_b.png"
)
_METHODS_REQUIREMENTS_B_SVG_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "requirements_b.svg"
)
_METHODS_REQUIREMENTS_C_PNG_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "requirements_c.png"
)
_METHODS_REQUIREMENTS_C_SVG_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "requirements_c.svg"
)
_METHODS_REQUIREMENTS_D_V1V2V3_PNG_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "requirements_d_v1v2v3.png"
)

_EXEMPLAR_CODE = "building_observatory"
_DIFFUSION_CODE = "animal_fish"
_DIFFUSION_PROMPT = r"\textit{``photo of an observatory...''}"
_DIFFUSION_PROMPT_LINES: tuple[str, ...] = (
    r"``award-winning marine photo''",
    r"``of a colorful fish in a coral reef''",
    r"``vibrant underwater scene, high detail''",
)
_CATEGORY_EXAMPLES: tuple[tuple[str, int, str, str], ...] = (
    ("animal_fish", 5, r"\textit{fish in water}", BLUE),
    ("building_observatory", 5, r"\textit{observatory at dusk}", AMBER),
    ("plant_pine", 5, r"\textit{pine tree in a landscape}", GREEN),
)
_SCENE_WHEELS_CITATION = "Scene Wheels (Son et al., 2022)"


def stim_path(code: str, idx: int) -> str:
    """Return an absolute path to a local stimulus image."""
    return str(_INTRO_STIM_DIR / f"{code}-{idx:02d}.png")


def _bold_tex(text: str) -> str:
    """Wrap plain text in `\\textbf{}` unless it is already bolded."""
    return text if r"\textbf{" in text else rf"\textbf{{{text}}}"


def title_block(
    title_text: str,
    subtitle_text: str | None = None,
    *,
    subtitle_color: str = MGREY,
) -> VGroup:
    """Return the standard methods title group."""
    title = Tex(_bold_tex(title_text), color=INK, font_size=34).to_edge(UP, buff=0.34)
    parts = [title]
    if subtitle_text is not None:
        subtitle = Tex(subtitle_text, color=subtitle_color, font_size=21)
        subtitle.next_to(title, DOWN, buff=0.14)
        parts.append(subtitle)
    return VGroup(*parts)


def make_image_card(
    image_source: str | Path | np.ndarray,
    *,
    height: float = 1.6,
    border_color: str = LGREY,
    fill_color: str = WHITE,
    fill_opacity: float = 1.0,
    buff: float = 0.06,
    corner_radius: float = 0.14,
) -> Group:
    """Create a framed image card."""
    if isinstance(image_source, np.ndarray):
        array = image_source
        if array.dtype != np.uint8:
            array = (255 * np.clip(array, 0, 1)).astype(np.uint8)
        image = ImageMobject(array)
    else:
        image = ImageMobject(str(image_source))
    image.height = height
    frame = RoundedRectangle(
        width=image.width + 2 * buff,
        height=image.height + 2 * buff,
        corner_radius=corner_radius,
        stroke_color=border_color,
        stroke_width=1.4,
    ).set_fill(fill_color, opacity=fill_opacity)
    image.move_to(frame.get_center())
    return Group(frame, image)


def make_reference_card(
    title_text: str,
    subtitle_text: str,
    *,
    width: float,
    height: float,
    accent: str = ACCENT,
    fill_color: str = PANEL,
) -> Group:
    """Create a small schematic card for cited material without shipping copies."""
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.10,
        stroke_color=LGREY,
        stroke_width=1.2,
    ).set_fill(fill_color, opacity=1.0)
    marker = Rectangle(
        width=0.08,
        height=height - 0.22,
        stroke_width=0,
    ).set_fill(accent, opacity=0.82)
    marker.align_to(frame, LEFT)
    marker.shift(RIGHT * 0.07)
    title = Tex(_bold_tex(title_text), color=INK, font_size=15)
    subtitle = Tex(subtitle_text, color=MGREY, font_size=11.5)
    text = VGroup(title, subtitle).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
    if text.width > width - 0.34:
        text.scale_to_fit_width(width - 0.34)
    text.move_to(frame.get_center())
    text.align_to(frame, LEFT)
    text.shift(RIGHT * 0.22)
    return Group(frame, marker, text)


def make_stimulus_mosaic(*, width: float, height: float, accent: str = ACCENT) -> Group:
    """Create a schematic multi-image collection used in the methods overview."""
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.10,
        stroke_color=LGREY,
        stroke_width=1.2,
    ).set_fill(WHITE, opacity=1.0)
    colors = (accent, "#B8C2CC", "#D8C3A5", "#86A6A6", "#B7A9CC", "#D6A06F")
    tiles = VGroup()
    tile_w = (width - 0.34) / 3
    tile_h = (height - 0.28) / 2
    for index, color in enumerate(colors):
        tile = RoundedRectangle(
            width=tile_w,
            height=tile_h,
            corner_radius=0.035,
            stroke_color=WHITE,
            stroke_width=1.0,
        ).set_fill(color, opacity=0.82)
        row = index // 3
        col = index % 3
        tile.move_to(
            frame.get_center()
            + LEFT * ((1 - col) * (tile_w + 0.05))
            + UP * ((0.5 - row) * (tile_h + 0.06))
        )
        tiles.add(tile)
    return Group(frame, tiles)


def make_callout(text: str, color: str, *, font_size: float = 23) -> VGroup:
    """Create a takeaway line."""
    line = Tex(text, color=INK, font_size=font_size)
    if line.width > 8.9:
        line.scale_to_fit_width(8.9)
    underline = Line(
        line.get_corner(DL) + DOWN * 0.10,
        line.get_corner(DR) + DOWN * 0.10,
        color=color,
        stroke_width=1.8,
    )
    return VGroup(line, underline)


def caption_line(
    text: str,
    *,
    color: str = MGREY,
    font_size: float = 18,
    max_width: float | None = None,
) -> Tex:
    """Build one single-line caption with optional width cap."""
    line = Tex(text, color=color, font_size=font_size)
    if max_width is not None and line.width > max_width:
        line.scale_to_fit_width(max_width)
    return line


def text_lines(
    rows: tuple[str, ...] | list[str],
    *,
    font_size: float = 18,
    color: str = INK,
    buff: float = 0.06,
    max_width: float | None = None,
) -> VGroup:
    """Build a left-aligned text stack with optional width capping."""
    block = VGroup(
        *[Tex(row, color=color, font_size=font_size) for row in rows]
    ).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if max_width is not None and block.width > max_width:
        block.scale_to_fit_width(max_width)
    return block


def make_bullet_list(
    bullets: tuple[str | tuple[str, ...], ...] | list[str | tuple[str, ...]],
    *,
    font_size: float = 18,
    color: str = INK,
    width: float = 2.85,
    bullet_radius: float = 0.026,
    line_buff: float = 0.05,
    item_buff: float = 0.19,
) -> VGroup:
    """Build a compact bullet stack used across methods slides."""
    items = VGroup()
    for entry in bullets:
        lines = (entry,) if isinstance(entry, str) else entry
        marker = Dot(radius=bullet_radius, color=BLACK, stroke_width=0)
        text_block = text_lines(
            lines,
            font_size=font_size,
            color=color,
            buff=line_buff,
            max_width=width - 0.24,
        )
        items.add(VGroup(marker, text_block).arrange(RIGHT, buff=0.10, aligned_edge=UP))
    return items.arrange(DOWN, buff=item_buff, aligned_edge=LEFT)


def simple_divider(width: float, *, color: str = LGREY, stroke_width: float = 1.2) -> Line:
    """Build a centered horizontal divider."""
    return Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=stroke_width)


def split_columns(
    left: Mobject,
    right: Mobject,
    *,
    buff: float = 0.48,
    divider_color: str = LGREY,
) -> Group:
    """Arrange two columns with an automatically sized divider."""
    divider = Line(UP * 0.5, DOWN * 0.5, color=divider_color, stroke_width=1.2)
    divider.set(height=max(left.height, right.height) - 0.06)
    return Group(left, divider, right).arrange(RIGHT, buff=buff, aligned_edge=UP)


def make_section_block(
    heading: str,
    rows: tuple[str, ...] | list[str],
    *,
    accent: str,
    width: float = 4.4,
    heading_size: float = 22,
    line_size: float = 18,
) -> VGroup:
    """Build one unframed section block with a small accent marker."""
    heading_row = VGroup(
        Dot(radius=0.045, color=accent),
        Tex(rf"\textbf{{{heading}}}", color=INK, font_size=heading_size),
    ).arrange(RIGHT, buff=0.12)
    body = text_lines(rows, font_size=line_size, color=INK, max_width=width)
    divider = simple_divider(max(heading_row.width, body.width, width * 0.62), stroke_width=1.0)
    divider.align_to(body, LEFT)
    return VGroup(heading_row, body, divider).arrange(DOWN, buff=0.10, aligned_edge=LEFT)


def make_centered_timeline_column(
    heading: str | tuple[str, ...],
    body: Mobject,
    *,
    width: float = 3.10,
    heading_size: float = 22,
    divider_color: str = BLACK,
    show_divider: bool = True,
    title_body_buff: float = 0.14,
) -> Group:
    """Build a centered text block suitable for a dot-anchored timeline."""
    if isinstance(heading, str):
        heading_block = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=heading_size)
    else:
        heading_block = VGroup(
            *[Tex(rf"\textbf{{{row}}}", color=INK, font_size=heading_size) for row in heading]
        ).arrange(DOWN, buff=0.03)
    if heading_block.width > width:
        heading_block.scale_to_fit_width(width)

    body_group = body.copy()
    if body_group.width > width:
        body_group.scale_to_fit_width(width)

    column_parts = [heading_block]
    if show_divider:
        divider = simple_divider(
            max(heading_block.width, body_group.width, width * 0.84),
            color=divider_color,
            stroke_width=1.0,
        )
        column_parts.append(divider)
        column_parts.append(body_group)
        column = Group(*column_parts).arrange(DOWN, buff=0.12)
    else:
        column_parts.append(body_group)
        column = Group(*column_parts).arrange(DOWN, buff=title_body_buff)
    anchor_x = column.get_center()[0]
    for mob in column:
        mob.set_x(anchor_x)
    return column


def layout_dot_timeline(
    title: Mobject,
    columns: Group,
    *,
    dot_xs: tuple[float, ...] = (-4.35, 0.0, 4.35),
    timeline_gap: float = 0.78,
    column_buff: float = 0.22,
    line_margin: float = 0.14,
) -> tuple[Line, VGroup]:
    """Position centered columns on the standard methods dot timeline."""
    timeline_y = title.get_bottom()[1] - timeline_gap
    dots = VGroup(
        *[
            Dot(radius=0.055, color=BLACK, stroke_width=0).move_to(np.array([x, timeline_y, 0.0]))
            for x in dot_xs
        ]
    )
    for column, dot in zip(columns, dots):
        column.next_to(dot, DOWN, buff=column_buff)
        column.set_x(dot.get_x())

    timeline_line = Line(
        np.array([columns.get_left()[0] - line_margin, timeline_y, 0.0]),
        np.array([columns.get_right()[0] + line_margin, timeline_y, 0.0]),
        color=BLACK,
        stroke_width=1.45,
    )
    return timeline_line, dots


def make_requirement_column_scaffold(
    heading: str | tuple[str, ...] | list[str],
    *,
    accent: str,
    width: float = 2.72,
    body_height: float = 4.40,
    heading_size: float = 22,
) -> VGroup:
    """Build an empty requirement column with room for later text or images."""
    if isinstance(heading, str):
        heading_text = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=heading_size)
    else:
        heading_text = VGroup(
            *[Tex(rf"\textbf{{{row}}}", color=INK, font_size=heading_size) for row in heading]
        ).arrange(DOWN, buff=0.03)
    if heading_text.width > width:
        heading_text.scale_to_fit_width(width)

    header_rule = Line(ORIGIN, RIGHT * width, color=LGREY, stroke_width=1.0)
    header_rule.set_stroke(opacity=0.72)

    body_area = Rectangle(width=width, height=body_height, stroke_width=0)
    body_area.set_fill(WHITE, opacity=0.0)

    column = VGroup(heading_text, header_rule, body_area).arrange(
        DOWN, buff=0.14, aligned_edge=LEFT
    )
    anchor_x = column.get_center()[0]
    for mob in column:
        mob.set_x(anchor_x)
    return column


def make_intersection_vertical_divider(
    upper_length: float,
    *,
    lower_length: float = 0.26,
    color: str = LGREY,
    dot_color: str = MGREY,
    junction_padding: float = 0.26,
) -> VGroup:
    """Build a clean vertical divider with a single intersection marker."""
    dot = Dot(radius=0.028, color=dot_color, stroke_width=0)
    dot.set_opacity(0.92)
    gap_edge = dot.radius + junction_padding

    top_segment = Line(UP * upper_length, UP * gap_edge, color=color, stroke_width=1.0)
    bottom_segment = Line(DOWN * gap_edge, DOWN * lower_length, color=color, stroke_width=1.0)
    top_segment.set_stroke(opacity=0.72)
    bottom_segment.set_stroke(opacity=0.72)

    return VGroup(top_segment, dot, bottom_segment)


def make_pipeline_stage(
    step_label: str,
    title_text: str,
    body: Mobject,
    *,
    accent: str,
    width: float = 2.55,
) -> Group:
    """Build a plain pipeline stage with a step label and divider."""
    step = Tex(step_label, color=accent, font_size=16)
    title = Tex(rf"\textbf{{{title_text}}}", color=INK, font_size=20)
    header = VGroup(step, title).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)

    body_group = body.copy()
    if body_group.width > width:
        body_group.scale_to_fit_width(width)

    rule = simple_divider(max(header.width, body_group.width, width * 0.84), stroke_width=1.0)
    rule.align_to(header, LEFT)
    return Group(header, rule, body_group).arrange(DOWN, buff=0.12, aligned_edge=LEFT)


def make_image_strip(
    code: str,
    idxs: tuple[int, ...] | list[int],
    *,
    height: float,
    buff: float = 0.08,
    border_color: str = LGREY,
) -> Group:
    """Build a horizontal strip of framed stimulus images."""
    return Group(
        *[
            make_image_card(stim_path(code, idx), height=height, border_color=border_color, buff=0.03)
            for idx in idxs
        ]
    ).arrange(RIGHT, buff=buff)


@lru_cache(maxsize=None)
def _embedded_png_from_svg(svg_path: str | Path) -> np.ndarray:
    """Extract one embedded PNG from an SVG wrapper for direct ImageMobject use."""
    root = ET.parse(str(svg_path)).getroot()
    href_key = "{http://www.w3.org/1999/xlink}href"
    image_nodes = root.findall(".//{http://www.w3.org/2000/svg}image")
    if not image_nodes:
        raise ValueError(f"No embedded image found in {svg_path}")
    href = image_nodes[0].attrib.get(href_key, "")
    prefix = "data:image/png;base64,"
    if not href.startswith(prefix):
        raise ValueError(f"Expected embedded PNG data URL in {svg_path}")
    png_bytes = base64.b64decode("".join(href[len(prefix) :].split()))
    return np.array(PILImage.open(BytesIO(png_bytes)).convert("RGBA"))


_METHODS_STUDY2_BLUE = "#2563EB"
_METHODS_STUDY2_RED = "#DC2626"
_METHODS_STUDY2_CYAN = "#0891B2"
_METHODS_STUDY2_GRID_PAT = np.array([
    [0.9, 0.2, 0.7],
    [0.3, 0.8, 0.1],
    [0.5, 0.4, 0.9],
])
_METHODS_STUDY2_GRID_PERMS = (
    np.array([0, 1, 2, 3, 4, 5, 6, 7, 8]),
    np.array([2, 6, 0, 7, 4, 8, 1, 5, 3]),
    np.array([8, 3, 6, 1, 4, 7, 2, 5, 0]),
    np.array([1, 4, 7, 0, 8, 5, 2, 6, 3]),
    np.array([5, 0, 8, 2, 6, 1, 7, 3, 4]),
    np.array([6, 2, 5, 8, 1, 4, 0, 3, 7]),
)


def _methods_study2_pattern_for_index(idx: int) -> np.ndarray:
    """Return one Study 2-style multivoxel pattern."""
    flat = _METHODS_STUDY2_GRID_PAT.flatten()
    perm = _METHODS_STUDY2_GRID_PERMS[idx % len(_METHODS_STUDY2_GRID_PERMS)]
    return flat[perm].reshape(_METHODS_STUDY2_GRID_PAT.shape)


def _make_methods_study2_grid(
    color: str,
    pattern: np.ndarray,
    *,
    cell_size: float = 0.108,
    gap: float = 0.017,
) -> VGroup:
    """Build a compact multivoxel grid matching the Study 2 visual grammar."""
    step = cell_size + gap
    group = VGroup()
    for r in range(pattern.shape[0]):
        for c in range(pattern.shape[1]):
            value = float(pattern[r, c])
            cell = Square(
                side_length=cell_size,
                stroke_width=0.7,
                stroke_color=LGREY,
            ).set_fill(
                interpolate_color(ManimColor(WHITE), ManimColor(color), 0.10 + 0.90 * value),
                opacity=1.0,
            )
            cell.move_to(
                RIGHT * (c - 1) * step
                + UP * (1 - r) * step
            )
            group.add(cell)
    return group


def _make_methods_requirement_flow_arrow(
    start: np.ndarray,
    end: np.ndarray,
    *,
    color: str,
) -> Arrow:
    """Build one thin branch arrow for the decoding requirement diagram."""
    arrow = Arrow(
        start,
        end,
        buff=0.03,
        color=color,
        stroke_width=1.9,
        tip_length=0.12,
        max_tip_length_to_length_ratio=0.18,
    )
    arrow.set_stroke(opacity=0.88)
    return arrow


def _build_methods_requirement_d_visual(*, width: float) -> VGroup:
    """Build the custom V1-V3 decoding diagram for requirement D."""
    branch_specs = (
        {
            "image_path": stim_path("animal_cat", 0),
            "color": _METHODS_STUDY2_RED,
            "pattern_idx": 3,
        },
        {
            "image_path": stim_path("plant_bristlecone", 0),
            "color": _METHODS_STUDY2_CYAN,
            "pattern_idx": 5,
        },
        {
            # Study 2 has no sailboat identity entry; reuse its blue-family accent.
            "image_path": stim_path("vehicle_sailboat", 0),
            "color": _METHODS_STUDY2_BLUE,
            "pattern_idx": 1,
        },
    )

    cards = Group(
        *[
            make_image_card(
                spec["image_path"],
                height=0.34,
                border_color=spec["color"],
                buff=0.028,
                corner_radius=0.10,
            )
            for spec in branch_specs
        ]
    ).arrange(RIGHT, buff=0.10, aligned_edge=UP)
    cards.set_z_index(4)

    brain = ImageMobject(str(_METHODS_REQUIREMENTS_D_V1V2V3_PNG_PATH))
    brain.scale_to_fit_width(width * 0.58)
    brain.set_z_index(2)

    patterns = VGroup(
        *[
            _make_methods_study2_grid(
                spec["color"],
                _methods_study2_pattern_for_index(spec["pattern_idx"]),
            )
            for spec in branch_specs
        ]
    ).arrange(RIGHT, buff=0.18, aligned_edge=UP)
    patterns.set_z_index(4)

    cards.next_to(brain, DOWN, buff=0.22)
    patterns.next_to(cards, DOWN, buff=0.36)

    flow_arrows = VGroup()
    for card, pattern, spec in zip(cards, patterns, branch_specs):
        color = str(spec["color"])
        flow_arrows.add(
            _make_methods_requirement_flow_arrow(
                card.get_bottom() + DOWN * 0.02,
                pattern.get_top() + UP * 0.02,
                color=color,
            )
        )
    flow_arrows.set_z_index(3)

    diagram = Group(brain, cards, flow_arrows, patterns)
    frame = Rectangle(width=width, height=diagram.height, stroke_width=0)
    frame.set_fill(WHITE, opacity=0.0)
    diagram.move_to(frame.get_center())
    return Group(frame, diagram)


_DDPM_ALPHA_BAR_CHECKPOINTS: tuple[float, ...] = (1.0, 0.85, 0.50, 0.02)


def load_rgb(path: str | Path) -> np.ndarray:
    """Load an image as a float RGB array in [0, 1]."""
    return np.asarray(PILImage.open(path).convert("RGB")).astype(np.float32) / 255.0


def _to_diffusion_range(image: np.ndarray) -> np.ndarray:
    """Map an RGB image from [0, 1] into the DDPM-friendly range [-1, 1]."""
    return (2.0 * image - 1.0).astype(np.float32)


def _from_diffusion_range(state: np.ndarray) -> np.ndarray:
    """Map a DDPM state back into displayable RGB space."""
    return np.clip((state + 1.0) / 2.0, 0.0, 1.0)


def _gaussian_noise(shape: tuple[int, ...], rng: np.random.Generator) -> np.ndarray:
    """Draw independent-channel Gaussian noise matching ε ~ N(0, I)."""
    return rng.normal(0.0, 1.0, shape).astype(np.float32)


def _magma_noise_image(noise: np.ndarray) -> np.ndarray:
    """Map a scalar Gaussian noise field to a displayable magma RGB image."""
    scalar_noise = noise[..., 0] if noise.ndim == 3 else noise
    normalized = np.clip((scalar_noise + 2.5) / 5.0, 0.0, 1.0)
    return colormaps["magma"](normalized)[..., :3].astype(np.float32)


def _render_ddpm_state(
    state: np.ndarray,
    x_0: np.ndarray,
    *,
    alpha_bar: float,
) -> np.ndarray:
    """Render a DDPM state with a magma-tinted noise component."""
    if alpha_bar >= 1.0 - 1e-6:
        return _from_diffusion_range(state)

    base_rgb = _from_diffusion_range(state)
    residual = state - float(np.sqrt(alpha_bar)) * x_0
    noise_scale = max(float(np.sqrt(1.0 - alpha_bar)), 1e-6)
    magma_noise = _magma_noise_image(residual / noise_scale)
    # Keep early checkpoints visually readable while still making late checkpoints noise-dominated.
    noise_weight = float(np.clip(0.85 * (1.0 - alpha_bar), 0.0, 0.9))
    return np.clip((1.0 - noise_weight) * base_rgb + noise_weight * magma_noise, 0.0, 1.0)


def build_ddpm_checkpoint_sources(
    clean: np.ndarray,
    *,
    alpha_bars: tuple[float, ...] = _DDPM_ALPHA_BAR_CHECKPOINTS,
    seed: int = 7,
) -> list[np.ndarray]:
    """Render display cards at chosen ᾱ checkpoints via direct reparameterization.

    Each underlying state satisfies the closed-form DDPM marginal with a single shared ε draw;
    the rendered card uses a tinted noise overlay for visual clarity, not a literal RGB display.
    """
    x_0 = _to_diffusion_range(clean)
    rng = np.random.default_rng(seed)
    epsilon = _gaussian_noise(x_0.shape, rng)
    return [
        _render_ddpm_state(
            float(np.sqrt(ab)) * x_0 + float(np.sqrt(1.0 - ab)) * epsilon,
            x_0,
            alpha_bar=ab,
        )
        for ab in alpha_bars
    ]


def make_image_progression(
    sources: list[str | Path | np.ndarray],
    *,
    height: float,
    arrow_color: str,
    border_color: str = LGREY,
    card_buff: float = 0.05,
    item_buff: float = 0.18,
) -> tuple[Group, VGroup]:
    """Build a card strip plus arrows between adjacent cards."""
    cards = Group(
        *[
            make_image_card(src, height=height, border_color=border_color, buff=0.03)
            for src in sources
        ]
    ).arrange(RIGHT, buff=item_buff)
    arrows = VGroup(
        *[
            Arrow(
                cards[idx].get_right() + RIGHT * 0.04,
                cards[idx + 1].get_left() + LEFT * 0.04,
                color=arrow_color,
                stroke_width=1.4,
                buff=card_buff,
                tip_shape=StealthTip,
                tip_length=0.12,
            )
            for idx in range(len(cards) - 1)
        ]
    )
    return cards, arrows


def make_schematic_box(
    title_text: str,
    body: Mobject,
    *,
    accent: str,
    width: float = 2.7,
    min_height: float = 1.10,
    fill_color: str = "#FAFBFC",
) -> VGroup:
    """Build a simple boxed module for the diffusion schematics."""
    body_group = body.copy()
    max_body_width = max(width - 0.42, 0.6)
    if body_group.width > max_body_width:
        body_group.scale_to_fit_width(max_body_width)

    title = Tex(rf"\textbf{{{title_text}}}", color=INK, font_size=20)
    content = VGroup(title, body_group).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    box = RoundedRectangle(
        width=max(width, content.width + 0.36),
        height=max(min_height, content.height + 0.34),
        corner_radius=0.14,
        stroke_color=accent,
        stroke_width=1.5,
    ).set_fill(fill_color, opacity=1.0)
    content.move_to(box.get_center()).align_to(box, LEFT).shift(RIGHT * 0.18)
    return VGroup(box, content)


def make_badge(
    text: str,
    *,
    accent: str,
    font_size: float = 16,
    fill_color: str = WHITE,
) -> VGroup:
    """Build a compact badge used for seed and timestep labels."""
    label = Tex(text, color=INK, font_size=font_size)
    frame = RoundedRectangle(
        width=label.width + 0.30,
        height=label.height + 0.18,
        corner_radius=0.12,
        stroke_color=accent,
        stroke_width=1.2,
    ).set_fill(fill_color, opacity=1.0)
    label.move_to(frame.get_center())
    return VGroup(frame, label)


def brain_icon_with_evc(*, highlight_color: str = BLUE, scale_factor: float = 1.0) -> dict[str, Mobject]:
    """Return the Study 2 brain icon with an early-visual-cortex highlight overlay."""
    brain = ImageMobject(str(_BRAIN_ICON_PATH)).scale_to_fit_height(2.85 * scale_factor)
    highlight_center = (
        brain.get_center()
        + RIGHT * (0.32 * brain.width)
        + DOWN * (0.04 * brain.height)
    )
    highlight_fill = Ellipse(
        width=0.18 * brain.width,
        height=0.14 * brain.height,
        stroke_width=0,
    ).set_fill(highlight_color, opacity=0.22).move_to(highlight_center)
    highlight_ring = Ellipse(
        width=0.26 * brain.width,
        height=0.20 * brain.height,
        stroke_color=highlight_color,
        stroke_width=2.4,
    ).set_fill(highlight_color, opacity=0.0).move_to(highlight_center)
    highlight_fill.set_z_index(1)
    highlight_ring.set_z_index(2)
    brain.set_z_index(0)
    return {
        "group": Group(brain, highlight_fill, highlight_ring),
        "brain": brain,
        "highlight": VGroup(highlight_fill, highlight_ring),
    }


def _methods_project_plan_model_icon(*, height: float = 0.58) -> SVGMobject:
    """Return the Study 1 Step 3-style neural-network icon in soft grey."""
    svg = SVGMobject(str(_METHODS_PROJECT_PLAN_MODEL_ICON_PATH), use_svg_cache=False)
    svg.scale_to_fit_height(height)

    if len(svg.submobjects) >= 19:
        left_edges = VGroup(*svg.submobjects[:6])
        right_edges = VGroup(*svg.submobjects[6:12])
        input_nodes = VGroup(*svg.submobjects[12:14])
        output_nodes = VGroup(*svg.submobjects[14:16])
        hidden_nodes = VGroup(*svg.submobjects[16:19])

        for edge_group in (left_edges, right_edges):
            edge_group.set_stroke(MGREY, width=1.8, opacity=0.42)
            edge_group.set_fill(opacity=0.0)

        for node_group in (input_nodes, hidden_nodes, output_nodes):
            node_group.set_fill(MGREY, opacity=0.58)
            node_group.set_stroke(MGREY, width=1.1, opacity=0.18)
    else:
        svg.set_stroke(MGREY, opacity=0.50, width=1.8)
        svg.set_fill(MGREY, opacity=0.58)

    return svg


_METHODS_REQUIREMENT_SPECS: tuple[dict[str, object], ...] = (
    {
        "heading": ("Ecological", "validity"),
        "accent": BLUE,
        "image_path": _METHODS_REQUIREMENTS_A_PNG_PATH,
        "bullets": (
            (
                "Approximate perceptual and",
                "semantic richness of",
                "naturalistic vision",
            ),
        ),
    },
    {
        "heading": ("Experimental", "control"),
        "accent": AMBER,
        "image_path": _METHODS_REQUIREMENTS_B_PNG_PATH,
        "image_scale_factor": 1.7,
        "bullets": (

            (
                "Vary fine-grained",
                "perceptual details",
            ), (
                "Maintain overall",
                "semantic identity",
            ),
        ),
    },
    {
        "heading": ("Unified memory", "paradigm"),
        "accent": GREEN,
        "image_path": _METHODS_REQUIREMENTS_C_PNG_PATH,
        "image_text_buff": 0.30,
        "bullets": (
            (
                "Perceptual task demands",
            ),            
            (
                "Measure WM and LTM",
                "with adequate sensitivity",
            ),
        ),
    },
    {
        "heading": ("Suitable for", "brain decoding"),
        "accent": BLUE,
        "custom_visual_builder": _build_methods_requirement_d_visual,
        "bullets": (
            (
                "Distinct cortical patterns",
                "in V1-V3",
            ),
            (
                "Support robust multivariate",
                "decoding analyses",
            ),
        ),
    },
)
_METHODS_REQUIREMENT_FOCUS_GAP = 0.20


def _build_methods_stimulus_requirement_state(active_idx: int) -> dict[str, Mobject]:
    """Build the scaffold and highlighted state for one requirement focus step."""
    title = title_block(
        r"\textbf{Design requirements for naturalistic stimuli}",
    )

    columns = VGroup(
        *[
            make_requirement_column_scaffold(spec["heading"], accent=spec["accent"])
            for spec in _METHODS_REQUIREMENT_SPECS
        ]
    )

    for idx, (column, spec) in enumerate(zip(columns, _METHODS_REQUIREMENT_SPECS)):
        heading_text = column[0]
        header_rule = column[1]
        if idx <= active_idx:
            heading_text.set_color(spec["accent"])
            header_rule.set_color(spec["accent"])
            header_rule.set_stroke(opacity=1.0, width=1.6)
        else:
            heading_text.set_color(INK)
            header_rule.set_color(LGREY)
            header_rule.set_stroke(opacity=0.72, width=1.0)

    divider_gap = 0.26
    heading_height = max(column[0].height for column in columns)
    body_depth = max(column[2].height for column in columns)
    divider_upper = heading_height + 0.08
    divider_lower = body_depth + 0.10
    vertical_dividers = VGroup(
        *[
            make_intersection_vertical_divider(
                divider_upper,
                lower_length=divider_lower,
                junction_padding=divider_gap,
            )
            for _ in range(len(columns) - 1)
        ]
    )

    requirement_layout = VGroup()
    for idx, column in enumerate(columns):
        requirement_layout.add(column)
        if idx < len(vertical_dividers):
            requirement_layout.add(vertical_dividers[idx])
    requirement_layout.arrange(RIGHT, buff=divider_gap, aligned_edge=UP)
    requirement_layout.next_to(title, DOWN, buff=0.58)

    intersection_y = columns[0][1].get_center()[1]
    for divider in vertical_dividers:
        divider.shift(UP * (intersection_y - divider[1].get_center()[1]))

    def _selection_bounds(idx: int) -> tuple[float, float, float, float]:
        column = columns[idx]
        body_area = column[2]
        rule = column[1]
        inner_side_span = (
            divider_gap + vertical_dividers[0][1].radius
            if len(vertical_dividers)
            else divider_gap
        )
        left_boundary = (
            vertical_dividers[idx - 1][1].get_x()
            if idx > 0
            else body_area.get_left()[0] - inner_side_span
        )
        right_boundary = (
            vertical_dividers[idx][1].get_x()
            if idx < len(vertical_dividers)
            else body_area.get_right()[0] + inner_side_span
        )
        rect_left = left_boundary + _METHODS_REQUIREMENT_FOCUS_GAP
        rect_right = right_boundary - _METHODS_REQUIREMENT_FOCUS_GAP
        rect_top = rule.get_y() - _METHODS_REQUIREMENT_FOCUS_GAP
        rect_bottom = body_area.get_bottom()[1] + _METHODS_REQUIREMENT_FOCUS_GAP
        return rect_left, rect_right, rect_top, rect_bottom

    bodies = Group()
    for idx, (column, spec) in enumerate(zip(columns, _METHODS_REQUIREMENT_SPECS)):
        accent = spec["accent"]
        body_items = Group()
        image_path = spec.get("image_path")
        custom_visual_builder = spec.get("custom_visual_builder")
        bullet_items = VGroup()
        for bullet_rows in spec["bullets"]:
            bullet = Dot(radius=0.034, color=accent, stroke_width=0)
            bullet_text = text_lines(
                bullet_rows,
                font_size=16,
                color=INK,
                buff=0.06,
                max_width=column[2].width - 0.56,
            )
            item = VGroup(bullet, bullet_text).arrange(RIGHT, buff=0.12, aligned_edge=UP)
            bullet_items.add(item)
        text_group = None
        if len(bullet_items) > 0:
            text_group = bullet_items.arrange(DOWN, buff=0.22, aligned_edge=LEFT)

        image = None
        if custom_visual_builder is not None:
            image = custom_visual_builder(width=column[2].width - 0.30)
            body_items.add(image)
        elif image_path is not None:
            if Path(image_path).suffix.lower() == ".svg":
                image = ImageMobject(_embedded_png_from_svg(image_path))
            else:
                image = ImageMobject(str(image_path))
            if text_group is not None:
                text_width = max(item[1].width for item in bullet_items)
                image.scale_to_fit_width(text_width)
            else:
                image.scale_to_fit_width(column[2].width - 0.56)
            image_scale_factor = float(spec.get("image_scale_factor", 1.0))
            if image_scale_factor != 1.0:
                image.scale(image_scale_factor)
            body_items.add(image)

        if text_group is not None:
            body_items.add(text_group)

        image_text_buff = float(spec.get("image_text_buff", 0.18))
        if image is not None and text_group is not None:
            body = Group(image, text_group)
            text_group.next_to(image, DOWN, buff=image_text_buff)
            text_group.set_x(image.get_center()[0])
        else:
            body = body_items.arrange(DOWN, buff=0.18)
        if body.width > column[2].width - 0.18:
            body.scale_to_fit_width(column[2].width - 0.18)
        if body.height > column[2].height - 0.24:
            body.scale_to_fit_height(column[2].height - 0.24)
        col_rect_left, col_rect_right, _, _ = _selection_bounds(idx)
        body.move_to(
            np.array(
                [
                    0.5 * (col_rect_left + col_rect_right),
                    column[2].get_top()[1] - (0.18 + body.height / 2),
                    0.0,
                ]
            )
        )
        body.set_z_index(15)
        target_opacity = 1.0 if idx <= active_idx else 0.0
        for submob in body.get_family():
            if hasattr(submob, "set_opacity"):
                submob.set_opacity(target_opacity)
            elif hasattr(submob, "set"):
                submob.set(opacity=target_opacity)
        bodies.add(body)

    active_column = columns[active_idx]
    active_spec = _METHODS_REQUIREMENT_SPECS[active_idx]
    base_left, base_right, base_top, base_bottom = _selection_bounds(active_idx)
    active_body_group = bodies[active_idx]
    content_pad_x = 0.12
    content_pad_y = 0.12
    rect_left = min(base_left, active_body_group.get_left()[0] - content_pad_x)
    rect_right = max(base_right, active_body_group.get_right()[0] + content_pad_x)
    rect_top = max(base_top, active_body_group.get_top()[1] + content_pad_y)
    rect_bottom = min(base_bottom, active_body_group.get_bottom()[1] - content_pad_y)

    focus_rect = RoundedRectangle(
        width=rect_right - rect_left,
        height=rect_top - rect_bottom,
        corner_radius=0.18,
        stroke_color=active_spec["accent"],
        stroke_width=1.5,
    ).set_fill(WHITE, opacity=0.0)
    focus_rect.move_to(
        np.array(
            [
                0.5 * (rect_left + rect_right),
                0.5 * (rect_top + rect_bottom),
                0.0,
            ]
        )
    )
    focus_rect.set_z_index(5)

    return {
        "title": title,
        "columns": columns,
        "vertical_dividers": vertical_dividers,
        "focus_rect": focus_rect,
        "bodies": bodies,
        "layout": requirement_layout,
        "final_group": Group(title, requirement_layout, focus_rect, bodies),
    }


class _MethodsStimulusRequirementScene(Scene):
    """Base scene for stepping through the stimulus-requirements sequence."""
    requirement_index: int = 0

    def construct(self) -> None:
        self.camera.background_color = BG
        current_state = _build_methods_stimulus_requirement_state(self.requirement_index)

        if self.requirement_index == 0:
            self.play(FadeIn(current_state["title"], shift=UP * 0.04), run_time=0.75)
            self.play(
                FadeIn(current_state["focus_rect"], shift=UP * 0.03),
                FadeIn(current_state["layout"], shift=UP * 0.05),
                run_time=0.90,
            )
            self.play(FadeIn(current_state["bodies"][0], shift=UP * 0.04), run_time=0.55)
            self.wait(2.10)
            return

        previous_state = _build_methods_stimulus_requirement_state(self.requirement_index - 1)
        self.add(previous_state["final_group"])
        self.play(
            Transform(previous_state["columns"], current_state["columns"]),
            Transform(previous_state["vertical_dividers"], current_state["vertical_dividers"]),
            Transform(previous_state["focus_rect"], current_state["focus_rect"]),
            FadeIn(
                current_state["bodies"][self.requirement_index],
                shift=UP * 0.04,
                run_time=0.55,
            ),
            run_time=0.80,
        )
        self.wait(2.10)


class MethodsStimulusRequirementsA(_MethodsStimulusRequirementScene):
    """Show the first highlighted stimulus requirement."""
    requirement_index = 0


class MethodsStimulusRequirementsB(_MethodsStimulusRequirementScene):
    """Show the second highlighted stimulus requirement."""
    requirement_index = 1


class MethodsStimulusRequirementsC(_MethodsStimulusRequirementScene):
    """Show the third highlighted stimulus requirement."""
    requirement_index = 2


class MethodsStimulusRequirementsD(_MethodsStimulusRequirementScene):
    """Show the fourth highlighted stimulus requirement."""
    requirement_index = 3


class MethodsStimulusRequirements(MethodsStimulusRequirementsA):
    """Alias the first stimulus-requirement scene as the chapter entrypoint."""
    pass

class MethodsExistingApproaches(Scene):
    """Chapter 2.3 — survey existing approaches and the GAN proof of concept."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Existing approaches}",
        )

        line_drawing_card = make_reference_card(
            "Line drawings",
            r"Snodgrass \& Vanderwart (1980)",
            width=2.50,
            height=0.58,
            accent=BLUE,
        )
        photo_norm_card = make_reference_card(
            "Photo norms",
            "Brodeur et al. (2010)",
            width=2.50,
            height=0.58,
            accent=RED,
        )

        manual_images = Group(
            line_drawing_card,
            photo_norm_card,
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        manual_body = Group(
            make_bullet_list(
                (
                    ("Time consuming",),
                    ("Limited ecological validity",),
                ),
                font_size=17,
                width=2.75,
            ),
            manual_images,
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        manual_column = make_centered_timeline_column(
            "Manual selection",
            manual_body,
            width=3.10,
            show_divider=False,
            title_body_buff=0.17,
        )

        scraping_body = Group(
            make_bullet_list(
                (
                    ("Limited experimental control",),
                    ("Perceptually very dissimilar",),
                    ("Limited number of exemplars",),
                    ("Variable resolution and quality",),
                ),
                font_size=16,
                width=2.95,
            ),
            make_reference_card(
                "Natural image corpora",
                "COCO; THINGS",
                width=2.72,
                height=0.58,
                accent=GREEN,
            ),
            make_stimulus_mosaic(
                width=2.72,
                height=0.80,
                accent=ACCENT,
            ),
            caption_line(
                "Lin et al. (2015); Hebart et al. (2019)",
                color=MGREY,
                font_size=14,
                max_width=2.80,
            ),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)

        scraping_column = make_centered_timeline_column(
            "Web scraping",
            scraping_body,
            width=3.18,
            show_divider=False,
            title_body_buff=0.17,
        )

        gan_bullets = make_bullet_list(
            (
                (
                    "Generative Adversarial Networks (GANs)",
                    "to synthesise stimuli (Goodfellow et al., 2014; Son et al., 2022)",
                ),
                ("Limited flexibility",),
                (
                    "Diffusion models have been largely unexplored",
                    "(Ho et al., 2020; Nichol \\& Dhariwal, 2021; Rombach et al., 2022)"
                ),
            ),
            font_size=13.5,
            color=INK,
            width=3.85,
            bullet_radius=0.024,
            line_buff=0.04,
            item_buff=0.20,
        )
        gan_images = Group(
            make_reference_card(
                "GAN synthesis",
                "Son et al. (2022)",
                width=3.05,
                height=0.72,
                accent=ACCENT,
            ),
            make_reference_card(
                "Latent stimulus wheels",
                "continuous but model-specific",
                width=3.05,
                height=0.72,
                accent="#B8894D",
            ),
        ).arrange(DOWN, buff=0.14)
        gan_citation = caption_line(
            _SCENE_WHEELS_CITATION,
            color=MGREY,
            font_size=14,
            max_width=3.35,
        )
        gan_citation.next_to(gan_images, DOWN, buff=0.08)
        gan_citation.set_x(gan_images.get_center()[0])
        gan_visuals = Group(gan_images, gan_citation)

        gan_body = Group(
            gan_bullets,
            gan_visuals,
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        gan_column = make_centered_timeline_column(
            ("Deep generative", "models"),
            gan_body,
            width=4.15,
            heading_size=21,
            show_divider=False,
            title_body_buff=0.17,
        )

        columns = Group(manual_column, scraping_column, gan_column)
        timeline_line, dots = layout_dot_timeline(title, columns)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(Create(timeline_line), run_time=0.50)
        for dot, column in zip(dots, columns):
            self.play(
                FadeIn(dot, scale=0.92),
                FadeIn(column, shift=UP * 0.04),
                run_time=0.38 if column is not gan_column else 0.48,
            )
        self.wait(3.20)


class MethodsDiffusionOpportunity(Scene):
    """Chapter 2.4 — advantages and one remaining limitation of diffusion models."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = Tex(
            r"\textbf{Advantages of diffusion models}",
            color=BLACK,
            font_size=34,
        ).to_edge(UP, buff=0.34)

        entry_specs = (
            {
                "heading": "Text-to-image synthesis",
                "bullets": (
                    ("describe image with natural language",),
                ),
            },
            {
                "heading": "Output scalability",
                "bullets": (
                    ("no limitation to existing images",),
                ),
            },
            {
                "heading": "Variability",
                "bullets": (
                    ("possibility to generate images of all kinds",),
                ),
            },
            {
                "heading": "Open question",
                "bullets": (
                    ("less straightforward to generate controlled variations",),
                ),
            },
        )

        def make_vertical_entry(
            heading: str,
            bullets: tuple[tuple[str, ...], ...],
            *,
            width: float = 5.55,
        ) -> Group:
            heading_tex = Tex(rf"\textbf{{{heading}}}", color=BLACK, font_size=24)
            if heading_tex.width > width:
                heading_tex.scale_to_fit_width(width)
            detail_lines = tuple(
                line for entry in bullets for line in ((entry,) if isinstance(entry, str) else entry)
            )
            detail_block = text_lines(
                detail_lines,
                font_size=18,
                color=BLACK,
                max_width=width,
            )
            text_group = Group(heading_tex, detail_block).arrange(
                DOWN,
                buff=0.11,
                aligned_edge=LEFT,
            )
            return text_group

        rows = Group(
            *[
                make_vertical_entry(
                    spec["heading"],
                    spec["bullets"],
                )
                for spec in entry_specs
            ]
        ).arrange(DOWN, buff=0.60)

        dots = VGroup()
        for text_group in rows:
            dot = Dot(radius=0.045, color=BLACK, stroke_width=0)
            dot.move_to(np.array([0.0, text_group[0].get_center()[1], 0.0]))
            text_group.next_to(dot, RIGHT, buff=0.24, aligned_edge=UP)
            dots.add(dot)

        content = Group(dots, rows)
        available_top = title.get_bottom()[1] - 0.42
        available_bottom = -config.frame_height / 2 + 0.55
        content.shift(
            UP * (((available_top + available_bottom) / 2) - content.get_center()[1])
        )
        content.shift(RIGHT * (0.0 - rows.get_center()[0]))

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        for dot, row in zip(dots, rows):
            self.play(
                FadeIn(dot, scale=0.92),
                FadeIn(row, shift=RIGHT * 0.08),
                run_time=0.42,
            )
        self.wait(3.20)


def _build_diffusion_process_strip(
    *,
    title_tex: str,
    sources: list[np.ndarray],
    state_specs: tuple[tuple[str, str], ...],
    process_title: str | tuple[str, ...],
    subtitle_text: str,
    process_formula: str,
    action_text: str | tuple[str, ...],
    action_formula: str | None = None,
    process_color: str = INK,
    card_height: float = 1.08,
    footer: Mobject | None = None,
    legend: Mobject | None = None,
) -> dict[str, Mobject]:
    """Build a single diffusion strip with side annotations and state labels."""

    def make_cards(card_sources: list[np.ndarray]) -> Group:
        return Group(
            *[
                make_image_card(src, height=card_height, border_color=LGREY, buff=0.03)
                for src in card_sources
            ]
        ).arrange(RIGHT, buff=0.24)

    def make_arrows(cards: Group) -> VGroup:
        return VGroup(
            *[
                Arrow(
                    cards[idx].get_right() + RIGHT * 0.03,
                    cards[idx + 1].get_left() + LEFT * 0.03,
                    color=process_color,
                    stroke_width=1.9,
                    buff=0.04,
                    tip_length=0.14,
                    tip_shape=StealthTip,
                )
                for idx in range(len(cards) - 1)
            ]
        )

    title = title_block(title_tex)
    cards = make_cards(sources)
    arrows = make_arrows(cards)

    state_labels = Group(
        *[
            Group(
                MathTex(latent_text, color=INK, font_size=23),
                MathTex(sigma_text, color=INK, font_size=19),
            ).arrange(DOWN, buff=0.03)
            for latent_text, sigma_text in state_specs
        ]
    )
    for label, card in zip(state_labels, cards):
        label.next_to(card, DOWN, buff=0.18)

    if isinstance(process_title, tuple):
        process_title_block = VGroup(
            *[
                Tex(rf"\textbf{{{line}}}", color=INK, font_size=25)
                for line in process_title
            ]
        ).arrange(DOWN, buff=0.02, aligned_edge=LEFT)
    else:
        process_title_block = Tex(
            rf"\textbf{{{process_title}}}",
            color=INK,
            font_size=25,
        )

    left_text = Group(
        process_title_block,
        Tex(subtitle_text, color=INK, font_size=16),
        MathTex(process_formula, color=INK, font_size=23),
    ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
    if isinstance(action_text, tuple):
        action_text_block = VGroup(
            *[Tex(line, color=INK, font_size=16) for line in action_text]
        ).arrange(DOWN, buff=0.02, aligned_edge=LEFT)
    else:
        action_text_block = Tex(action_text, color=INK, font_size=16)
    right_items: list[Mobject] = [action_text_block]
    if action_formula is not None:
        right_items.append(MathTex(action_formula, color=INK, font_size=23))
    right_text = Group(*right_items).arrange(DOWN, buff=0.08, aligned_edge=RIGHT)

    left_text.next_to(cards[0], LEFT, buff=0.26)
    left_text.align_to(cards, UP)
    right_text.next_to(cards[-1], RIGHT, buff=0.46)
    right_text.align_to(cards, UP)

    diagram_parts: list[Mobject] = [cards, arrows, state_labels, left_text, right_text]
    if footer is not None:
        footer.next_to(state_labels, DOWN, buff=0.46)
        footer.move_to(np.array([cards.get_center()[0], footer.get_center()[1], 0.0]))
        diagram_parts.append(footer)
    if legend is not None:
        legend.next_to(right_text, DOWN, buff=0.18, aligned_edge=LEFT)
        diagram_parts.append(legend)

    diagram = Group(*diagram_parts)
    if diagram.width > config.frame_width - 0.95:
        diagram.scale_to_fit_width(config.frame_width - 0.95)
    if diagram.height > config.frame_height - 1.95:
        diagram.scale_to_fit_height(config.frame_height - 1.95)
    diagram.move_to(ORIGIN).shift(DOWN * 0.08)
    title.to_edge(UP, buff=0.28)

    return {
        "title": title,
        "cards": cards,
        "arrows": arrows,
        "state_labels": state_labels,
        "left_text": left_text,
        "right_text": right_text,
        "footer": footer,
        "legend": legend,
        "diagram": diagram,
    }


def _build_diffusion_training_schematic(
    x_t_source: np.ndarray,
    *,
    card_height: float = 0.92,
) -> dict[str, Mobject]:
    """Build the training row: x_t card → ε_θ network box → ε̂, with left/right annotations."""
    card = make_image_card(x_t_source, height=card_height, border_color=LGREY, buff=0.03)

    net_label = MathTex(r"\epsilon_\theta", color=INK, font_size=26)
    net_rect = RoundedRectangle(
        width=1.10,
        height=card_height * 0.78,
        corner_radius=0.13,
        stroke_color=GREEN,
        stroke_width=1.5,
    ).set_fill("#FAFBFC", opacity=1.0)
    net_label.move_to(net_rect.get_center())
    net_box = VGroup(net_rect, net_label)

    eps_hat = MathTex(r"\hat{\epsilon}", color=INK, font_size=28)

    net_box.next_to(card, RIGHT, buff=0.52)
    eps_hat.next_to(net_box, RIGHT, buff=0.52)

    arrow_in = Arrow(
        card.get_right() + RIGHT * 0.02,
        net_rect.get_left() + LEFT * 0.02,
        color=AMBER,
        stroke_width=1.6,
        buff=0.04,
        tip_length=0.13,
        tip_shape=StealthTip,
    )
    arrow_out = Arrow(
        net_rect.get_right() + RIGHT * 0.02,
        eps_hat.get_left() + LEFT * 0.06,
        color=GREEN,
        stroke_width=1.6,
        buff=0.04,
        tip_length=0.13,
        tip_shape=StealthTip,
    )

    t_label = MathTex(r"t\ \text{(step)}", color=INK, font_size=16)
    c_label = MathTex(r"c\ \text{(prompt)}", color=INK, font_size=16)
    cond_row = VGroup(t_label, c_label).arrange(RIGHT, buff=0.32)
    cond_row.next_to(net_rect, DOWN, buff=0.22)

    t_arrow = Arrow(
        t_label.get_top(),
        net_rect.get_bottom() + LEFT * 0.16,
        color=MGREY,
        stroke_width=1.1,
        buff=0.05,
        tip_length=0.08,
        tip_shape=StealthTip,
    )
    c_arrow = Arrow(
        c_label.get_top(),
        net_rect.get_bottom() + RIGHT * 0.16,
        color=MGREY,
        stroke_width=1.1,
        buff=0.05,
        tip_length=0.08,
        tip_shape=StealthTip,
    )

    schematic = Group(card, arrow_in, net_box, arrow_out, eps_hat, cond_row, t_arrow, c_arrow)

    left_text = Group(
        Tex(r"\textbf{Training}", color=INK, font_size=25),
        MathTex(
            r"\hat{\epsilon}_{\theta}(x_t,t,c)\approx\epsilon",
            color=INK,
            font_size=23,
        ),
    ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
    left_text.next_to(card, LEFT, buff=0.26)
    left_text.align_to(card, UP)

    right_text = VGroup(
        Tex(r"Training: predict the noise", color=INK, font_size=16),
        Tex(r"component in $x_t$.", color=INK, font_size=16),
    ).arrange(DOWN, buff=0.02, aligned_edge=LEFT)
    right_text.next_to(eps_hat, RIGHT, buff=0.46)
    right_text.align_to(card, UP)

    diagram = Group(schematic, left_text, right_text)
    return {
        "card": card,
        "schematic": schematic,
        "left_text": left_text,
        "right_text": right_text,
        "diagram": diagram,
    }


def _align_diffusion_strip_left_edges(
    reference_content: dict[str, Mobject],
    target_content: dict[str, Mobject],
) -> None:
    """Align one diffusion row to another using the image-strip left edge."""
    reference_cards = reference_content["cards"]
    target_cards = target_content["cards"]
    target_diagram = target_content["diagram"]
    target_diagram.shift(RIGHT * (reference_cards.get_left()[0] - target_cards.get_left()[0]))


def _play_diffusion_process_sequential(scene: Scene, content: dict[str, Mobject]) -> None:
    """Animate a diffusion strip card by card."""
    cards = content["cards"]
    arrows = content["arrows"]
    state_labels = content["state_labels"]
    left_text = content["left_text"]
    right_text = content["right_text"]
    footer = content.get("footer")
    legend = content.get("legend")

    scene.play(
        FadeIn(left_text, shift=RIGHT * 0.04),
        FadeIn(right_text, shift=LEFT * 0.04),
        FadeIn(cards[0], shift=UP * 0.03),
        FadeIn(state_labels[0], shift=UP * 0.03),
        run_time=0.65,
    )
    for idx in range(len(arrows)):
        scene.play(
            Create(arrows[idx]),
            FadeIn(cards[idx + 1], shift=RIGHT * 0.03),
            FadeIn(state_labels[idx + 1], shift=UP * 0.03),
            run_time=0.50,
        )
    if footer is not None:
        scene.play(FadeIn(footer, shift=UP * 0.03), run_time=0.35)
    if legend is not None:
        scene.play(FadeIn(legend, shift=UP * 0.03), run_time=0.35)


def _fit_rows_below_title(title: Mobject, rows: Group) -> None:
    """Scale and center a vertical row stack below the title."""
    available_top = title.get_bottom()[1] - 0.28
    available_bottom = -config.frame_height / 2 + 0.28
    available_height = available_top - available_bottom
    if rows.height > available_height:
        rows.scale_to_fit_height(available_height)
    if rows.width > config.frame_width - 0.80:
        rows.scale_to_fit_width(config.frame_width - 0.80)
    rows.move_to(np.array([0.0, (available_top + available_bottom) / 2, 0.0]))


def _align_training_row_to_forward(
    forward_content: dict[str, Mobject],
    training_content: dict[str, Mobject],
) -> None:
    """Center the training example card under the first noisy forward checkpoint."""
    training_content["diagram"].shift(
        RIGHT
        * (
            forward_content["cards"][1].get_center()[0]
            - training_content["card"].get_center()[0]
        )
    )


class MethodsDiffusionExplainerA(Scene):
    """Chapter 2.5 — diffusion explainer A: forward noising and training."""

    def construct(self) -> None:
        self.camera.background_color = BG

        clean = load_rgb(stim_path(_EXEMPLAR_CODE, 5))
        forward_sources = build_ddpm_checkpoint_sources(clean, seed=7)

        forward_content = _build_diffusion_process_strip(
            title_tex=r"\textbf{Diffusion models}",
            sources=forward_sources,
            state_specs=(
                (r"x_0", r"\bar{\alpha}_0 = 1"),
                (r"x_{t_1}", r"\bar{\alpha}_{t_1}"),
                (r"x_{t_2}", r"\bar{\alpha}_{t_2}"),
                (r"x_T", r"\bar{\alpha}_T \approx 0"),
            ),
            process_title="Forward process",
            subtitle_text="corrupt training images",
            process_formula=r"x_t=\sqrt{\bar{\alpha}_t}\,x_0+\sqrt{1-\bar{\alpha}_t}\,\epsilon",
            action_text=("Create noisy versions", "of training images."),
            process_color=AMBER,
        )

        training_content = _build_diffusion_training_schematic(forward_sources[1])

        title = title_block(r"\textbf{Diffusion models}")
        title.to_edge(UP, buff=0.28)

        forward_diagram = forward_content["diagram"]
        training_diagram = training_content["diagram"]

        rows = Group(forward_diagram, training_diagram).arrange(DOWN, buff=0.65)
        _align_training_row_to_forward(forward_content, training_content)
        _fit_rows_below_title(title, rows)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.60)
        _play_diffusion_process_sequential(self, forward_content)
        self.play(FadeIn(training_diagram, shift=UP * 0.03), run_time=0.65)
        self.wait(3.20)


class MethodsDiffusionExplainerB(Scene):
    """Chapter 2.6 — diffusion explainer B: add sampling beneath the earlier rows."""

    def construct(self) -> None:
        self.camera.background_color = BG

        clean = load_rgb(stim_path(_EXEMPLAR_CODE, 5))
        forward_sources = build_ddpm_checkpoint_sources(clean, seed=7)
        reverse_sources = list(reversed(build_ddpm_checkpoint_sources(clean, seed=13)))

        forward_content = _build_diffusion_process_strip(
            title_tex=r"\textbf{Diffusion models}",
            sources=forward_sources,
            state_specs=(
                (r"x_0", r"\bar{\alpha}_0 = 1"),
                (r"x_{t_1}", r"\bar{\alpha}_{t_1}"),
                (r"x_{t_2}", r"\bar{\alpha}_{t_2}"),
                (r"x_T", r"\bar{\alpha}_T \approx 0"),
            ),
            process_title="Forward process",
            subtitle_text="corrupt training images",
            process_formula=r"x_t=\sqrt{\bar{\alpha}_t}\,x_0+\sqrt{1-\bar{\alpha}_t}\,\epsilon",
            action_text=("Create noisy versions", "of training images."),
            process_color=AMBER,
        )

        training_content = _build_diffusion_training_schematic(forward_sources[1])

        reverse_content = _build_diffusion_process_strip(
            title_tex=r"\textbf{Diffusion models}",
            sources=reverse_sources,
            state_specs=(
                (r"x_T", r"\bar{\alpha}_T \approx 0"),
                (r"x_{t_2}", r"\bar{\alpha}_{t_2}"),
                (r"x_{t_1}", r"\bar{\alpha}_{t_1}"),
                (r"x_0", r"\bar{\alpha}_0 = 1"),
            ),
            process_title="Sampling",
            subtitle_text=r"$x_T\!\sim\!\mathcal{N}(0,I)$; chain learned reverse steps",
            process_formula=r"x_{t-1}\sim p_{\theta}(x_{t-1}\mid x_t,c)",
            action_text=(
                r"Generate by iterative reverse",
                r"denoising, conditioned on prompt $c$.",
            ),
            process_color=BLUE,
        )

        title = title_block(r"\textbf{Diffusion models}")
        title.to_edge(UP, buff=0.28)

        forward_diagram = forward_content["diagram"]
        training_diagram = training_content["diagram"]
        reverse_diagram = reverse_content["diagram"]

        start_rows = Group(forward_diagram, training_diagram).arrange(DOWN, buff=0.65)
        _align_training_row_to_forward(forward_content, training_content)
        _fit_rows_below_title(title, start_rows)

        target_forward = forward_diagram.copy()
        target_training = training_diagram.copy()
        target_reverse = reverse_diagram.copy()
        target_rows = Group(target_forward, target_training, target_reverse).arrange(
            DOWN, buff=0.52
        )
        target_training.shift(
            RIGHT
            * (
                target_forward[0][1].get_center()[0]
                - target_training[0][0].get_center()[0]
            )
        )
        target_reverse.shift(
            RIGHT * (target_forward[0].get_left()[0] - target_reverse[0].get_left()[0])
        )
        _fit_rows_below_title(title, target_rows)
        reverse_diagram.move_to(target_reverse.get_center())

        self.add(title, forward_diagram, training_diagram)
        self.play(
            forward_diagram.animate.move_to(target_forward.get_center()),
            training_diagram.animate.move_to(target_training.get_center()),
            run_time=0.70,
        )
        _play_diffusion_process_sequential(self, reverse_content)
        self.wait(3.20)


class MethodsProjectPlan(Scene):
    """Chapter 2.7 — summarise the rationale and overall study plan."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Project plan}",
        )

        study1_generate_rows: tuple[str | tuple[str, ...], ...] = (
            (
                "follow design requirements",
            ),
            (
                "manipulation of",
                "stimulus similarity",
            ),
        )
        study1_validate_rows: tuple[str | tuple[str, ...], ...] = (
            (
                "alignment between model-based and",
                "human similarity judgments",
            ),
            "memory validation task",
        )
        study2_rows: tuple[str | tuple[str, ...], ...] = (
            "two-session fMRI study",
            "address 3 research questions",
        )

        def make_flow_step(
            icon_path: Path,
            heading: str,
            rows: tuple[str | tuple[str, ...], ...],
            *,
            width: float,
        ) -> Group:
            if icon_path == _METHODS_PROJECT_PLAN_MODEL_ICON_PATH:
                icon = _methods_project_plan_model_icon()
            elif icon_path.suffix.lower() == ".svg":
                icon = SVGMobject(str(icon_path))
                icon.scale_to_fit_height(0.58)
            else:
                icon = ImageMobject(str(icon_path))
                icon.scale_to_fit_height(0.58)

            heading_tex = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=22)
            if heading_tex.width > width:
                heading_tex.scale_to_fit_width(width)
            icon.next_to(heading_tex, UP, buff=0.18)
            icon.set_x(heading_tex.get_center()[0])
            return Group(icon, heading_tex)

        def make_study_bracket(
            left: Mobject,
            right: Mobject,
            label: str,
            *,
            y: float,
            color: str = MGREY,
        ) -> VGroup:
            pad = 0.10
            tick = 0.16
            x0 = left.get_left()[0] - pad
            x1 = right.get_right()[0] + pad
            bracket = VGroup(
                Line(
                    np.array([x0, y + tick, 0.0]),
                    np.array([x0, y, 0.0]),
                    color=color,
                    stroke_width=1.05,
                ),
                Line(
                    np.array([x0, y, 0.0]),
                    np.array([x1, y, 0.0]),
                    color=color,
                    stroke_width=1.05,
                ),
                Line(
                    np.array([x1, y, 0.0]),
                    np.array([x1, y + tick, 0.0]),
                    color=color,
                    stroke_width=1.05,
                ),
            )
            label_tex = Tex(rf"\textbf{{{label}}}", color=color, font_size=18)
            label_tex.next_to(bracket, DOWN, buff=0.08)
            return VGroup(bracket, label_tex)

        steps = Group(
            make_flow_step(
                _METHODS_PROJECT_PLAN_MODEL_ICON_PATH,
                "Generate stimulus set",
                study1_generate_rows,
                width=3.35,
            ),
            make_flow_step(
                _METHODS_PROJECT_PLAN_VALIDATION_ICON_PATH,
                "Behavioural validation",
                study1_validate_rows,
                width=3.05,
            ),
            make_flow_step(
                _METHODS_PROJECT_PLAN_NEURO_ICON_PATH,
                "Neuroimaging study",
                study2_rows,
                width=3.15,
            ),
        )
        steps.arrange(RIGHT, buff=1.35, aligned_edge=UP)
        if steps.width > config.frame_width - 1.90:
            steps.scale_to_fit_width(config.frame_width - 1.90)
            steps.arrange(RIGHT, buff=1.10, aligned_edge=UP)

        arrow_y = float(np.mean([step[1].get_center()[1] for step in steps]))
        arrows = VGroup(
            *[
                Arrow(
                    np.array([steps[idx].get_right()[0] + 0.18, arrow_y, 0.0]),
                    np.array([steps[idx + 1].get_left()[0] - 0.18, arrow_y, 0.0]),
                    color=MGREY,
                    stroke_width=1.5,
                    buff=0.0,
                    tip_length=0.14,
                    tip_shape=StealthTip,
                )
                for idx in range(len(steps) - 1)
            ]
        )

        flow = Group(steps, arrows)
        bracket_y = min(step.get_bottom()[1] for step in steps) - 0.52
        study1_group = make_study_bracket(steps[0], steps[1], "Study 1", y=bracket_y)
        study2_group = make_study_bracket(steps[2], steps[2], "Study 2", y=bracket_y)
        content = Group(flow, study1_group, study2_group)
        content.move_to(ORIGIN)

        self.add(title, steps[0])
        self.play(Create(arrows[0]), FadeIn(steps[1], shift=UP * 0.04), run_time=0.48)
        self.play(Create(arrows[1]), FadeIn(steps[2], shift=UP * 0.04), run_time=0.48)
        self.play(
            Create(study1_group[0]),
            FadeIn(study1_group[1], shift=UP * 0.02),
            Create(study2_group[0]),
            FadeIn(study2_group[1], shift=UP * 0.02),
            run_time=0.40,
        )
        self.wait(3.20)


MethodsGANsProofOfConcept = MethodsExistingApproaches


_METHODS_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    MethodsStimulusRequirementsA,
    MethodsStimulusRequirementsB,
    MethodsStimulusRequirementsC,
    MethodsStimulusRequirementsD,
    MethodsExistingApproaches,
    MethodsDiffusionExplainerA,
    MethodsDiffusionExplainerB,
    MethodsDiffusionOpportunity,
    MethodsProjectPlan,
)
_METHODS_SECTION_NAMES: tuple[str, ...] = (
    "methods_stimulus_requirements_a",
    "methods_stimulus_requirements_b",
    "methods_stimulus_requirements_c",
    "methods_stimulus_requirements_d",
    "methods_existing_approaches",
    "methods_diffusion_models_explainer_a",
    "methods_diffusion_models_explainer_b",
    "methods_diffusion_opportunity",
    "methods_project_plan",
)


class Methods(Scene):
    """Unified production render for the methods chapter."""

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        zip(_METHODS_SECTION_NAMES, _METHODS_MASTER_SECTION_ORDER)
    )

    def __init__(self, *args, **kwargs):
        config.output_file = "methods"
        super().__init__(*args, **kwargs)

    def _reset_master_scene_state(self) -> None:
        """Reset mobjects and camera placement before replaying one section."""
        self.clear()
        self.camera.background_color = BG
        if hasattr(self.camera, "frame_center"):
            self.camera.frame_center = ORIGIN.copy()

    def _hold_previous_section_frame(self) -> None:
        """Pin the previous section's last frame into the next section."""
        self.wait(1 / config.frame_rate)

    def _render_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        """Replay one existing methods scene inside the master section render."""
        self.next_section(section_name)
        if carry_previous_frame:
            self._hold_previous_section_frame()
        self._reset_master_scene_state()
        if hasattr(scene_cls, "requirement_index"):
            self.requirement_index = scene_cls.requirement_index
        scene_cls.construct(self)
        if hasattr(self, "requirement_index"):
            delattr(self, "requirement_index")

    def construct(self) -> None:
        """Render the full methods chapter as one sectioned scene."""
        self._reset_master_scene_state()
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._render_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )


_PUBLIC_SCENES: tuple[type[Scene], ...] = _METHODS_MASTER_SECTION_ORDER

for _scene_cls in _PUBLIC_SCENES:
    _wrapped = _wrap_scene(_scene_cls)
    _wrapped.__module__ = __name__
    globals()[_scene_cls.__name__] = _wrapped
del _scene_cls

MethodsStimulusRequirements = MethodsStimulusRequirementsA
MethodsGANsProofOfConcept = MethodsExistingApproaches
Methods.__module__ = __name__
__all__ = [
    "Methods",
    "MethodsStimulusRequirements",
    "MethodsGANsProofOfConcept",
    *[scene.__name__ for scene in _PUBLIC_SCENES],
]
