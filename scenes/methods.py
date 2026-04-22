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
    uv run manim scenes/methods.py MethodsDiffusionPromptConditioning -ql
    uv run manim scenes/methods.py MethodsDiffusionTrainVsGenerate -ql
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
    "MethodsDiffusionOpportunity": "06",
    "MethodsDiffusionPromptConditioning": "07",
    "MethodsDiffusionTrainVsGenerate": "08",
    "MethodsProjectPlan": "09",
}
_METHODS_OUTPUT_NAMES: dict[str, str] = {
    "MethodsGANsProofOfConcept": "MethodsExistingApproaches",
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


# ── Assets ────────────────────────────────────────────────────────────────────
_INTRO_STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
_BRAIN_ICON_PATH = REPO_ROOT / "assets" / "images" / "study2" / "brain_icon_sagittal.png"
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
_METHODS_SNODGRASS_VANDERWART_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "Snodgrass & Vanderwart (1980).png"
)
_METHODS_BRODEUR_2010_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "Brodeur et al. (2010).png"
)
_METHODS_COCO_DATASET_PATH = (
    REPO_ROOT / "assets" / "images" / "methods" / "COCO dataset (Lin et al 2015) .png"
)
_METHODS_THINGS_GUITAR_PATH = REPO_ROOT / "assets" / "images" / "methods" / "thins_guitar.jpg"
_METHODS_THINGS_BALLON_PATH = REPO_ROOT / "assets" / "images" / "methods" / "things_ballon.jpg"
_METHODS_THINGS_FISH1_PATH = REPO_ROOT / "assets" / "images" / "methods" / "things_fish1.jpg"
_METHODS_THINGS_FISH2_PATH = REPO_ROOT / "assets" / "images" / "methods" / "things_fish2.jpg"
_METHODS_THINGS_FISH3_PATH = REPO_ROOT / "assets" / "images" / "methods" / "things_fish3.jpg"
_METHODS_SON_2021_PATH = REPO_ROOT / "assets" / "images" / "methods" / "son2021.png"
_METHODS_SON_2021B_PATH = REPO_ROOT / "assets" / "images" / "methods" / "son2021b.png"

_EXEMPLAR_CODE = "building_observatory"
_DIFFUSION_CODE = "animal_fish"
_DIFFUSION_PROMPT = r"\textit{prompt: observatory at dusk}"
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


def title_block(
    title_text: str,
    subtitle_text: str | None = None,
    *,
    subtitle_color: str = MGREY,
) -> VGroup:
    """Return the standard methods title group."""
    title = Tex(title_text, color=INK, font_size=34).to_edge(UP, buff=0.34)
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


_SHARED_NOISE: dict[tuple[int, ...], np.ndarray] = {}


def load_rgb(path: str | Path) -> np.ndarray:
    """Load an image as a float RGB array in [0, 1]."""
    return np.asarray(PILImage.open(path).convert("RGB")).astype(np.float32) / 255.0


def diffusion_noise(shape: tuple[int, ...]) -> np.ndarray:
    """Return one deterministic normalized noise array for a given shape."""
    if shape not in _SHARED_NOISE:
        rng = np.random.default_rng(42)
        noise = rng.normal(0, 1, shape).astype(np.float32)
        _SHARED_NOISE[shape] = (noise - noise.min()) / (noise.max() - noise.min())
    return _SHARED_NOISE[shape]


def blend_with_noise(clean: np.ndarray, alpha: float) -> np.ndarray:
    """Blend one clean image with shared noise."""
    return np.clip((1 - alpha) * clean + alpha * diffusion_noise(clean.shape), 0, 1)


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


_METHODS_REQUIREMENT_SPECS: tuple[dict[str, object], ...] = (
    {
        "heading": ("Ecological", "validity"),
        "accent": BLUE,
        "image_path": _METHODS_REQUIREMENTS_A_PNG_PATH,
        "bullets": (
            (
                "Approximate perceptual and",
                "semantic richness in",
                "naturalistic vision",
            ),
        ),
    },
    {
        "heading": ("Experimental", "control"),
        "accent": AMBER,
        "image_path": _METHODS_REQUIREMENTS_B_PNG_PATH,
        "bullets": (
            (
                "Dissociate perceptual",
                "similarity from",
                "semantic identity",
            ),
            (
                "Vary fine-grained",
                "visual details, not",
                "semantic content",
            ),
            (
                "Allow controlled",
                "manipulation of overall",
                "similarity",
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
                "Limit semantic rehearsal",
                "while preserving",
                "perceptual demands",
            ),
            (
                "Measure WM and LTM",
                "sensitively, avoiding",
                "floor and ceiling effects",
            ),
        ),
    },
    {
        "heading": ("Suitable for", "brain decoding"),
        "accent": BLUE,
        "custom_visual_builder": _build_methods_requirement_d_visual,
        "bullets": (
            (
                "Perceptual variability",
                "evokes distinct cortical",
                "patterns in V1-V3",
            ),
            (
                "Support multivariate",
                "decoding analyses",
            ),
            (
                "Enable comparison of",
                "sensory and memory",
                "representations",
            ),
        ),
    },
)
_METHODS_REQUIREMENT_FOCUS_GAP = 0.20


def _build_methods_stimulus_requirement_state(active_idx: int) -> dict[str, Mobject]:
    title = title_block(
        r"\textbf{Design requirements for naturalistic stimuli}",
        "Objective: delayed match-to-sample task with long-term memory component",
        subtitle_color=INK,
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
    requirement_index = 0


class MethodsStimulusRequirementsB(_MethodsStimulusRequirementScene):
    requirement_index = 1


class MethodsStimulusRequirementsC(_MethodsStimulusRequirementScene):
    requirement_index = 2


class MethodsStimulusRequirementsD(_MethodsStimulusRequirementScene):
    requirement_index = 3


class MethodsStimulusRequirements(MethodsStimulusRequirementsA):
    pass

class MethodsExistingApproaches(Scene):
    """Chapter 2.3 — survey existing approaches and the GAN proof of concept."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Existing approaches}",
        )

        def _bullet_list(
            bullets: tuple[str | tuple[str, ...], ...] | list[str | tuple[str, ...]],
            *,
            font_size: float = 18,
            color: str = INK,
            width: float = 2.85,
            bullet_radius: float = 0.026,
            line_buff: float = 0.05,
            item_buff: float = 0.19,
        ) -> VGroup:
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

        snodgrass_image = make_image_card(
            _METHODS_SNODGRASS_VANDERWART_PATH,
            height=0.62,
            border_color=LGREY,
            buff=0.02,
        )
        snodgrass_citation = caption_line(
            "Snodgrass \\& Vanderwart (1980)",
            color=MGREY,
            font_size=14,
            max_width=2.80,
        )
        snodgrass_citation.next_to(snodgrass_image, DOWN, buff=0.04)
        snodgrass_citation.set_x(snodgrass_image.get_center()[0])

        brodeur_image = make_image_card(
            _METHODS_BRODEUR_2010_PATH,
            height=0.62,
            border_color=LGREY,
            buff=0.02,
        )
        brodeur_citation = caption_line(
            "Brodeur et al. (2010)",
            color=MGREY,
            font_size=14,
            max_width=2.80,
        )
        brodeur_citation.next_to(brodeur_image, DOWN, buff=0.04)
        brodeur_citation.set_x(brodeur_image.get_center()[0])

        manual_images = Group(
            Group(snodgrass_image, snodgrass_citation),
            Group(brodeur_image, brodeur_citation),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        manual_body = Group(
            _bullet_list(
                (
                    ("time consuming",),
                    ("limited ecological validity",),
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

        things_top_row = Group(
            make_image_card(
                _METHODS_THINGS_GUITAR_PATH,
                height=0.40,
                border_color=LGREY,
                buff=0.02,
            ),
            make_image_card(
                _METHODS_THINGS_BALLON_PATH,
                height=0.40,
                border_color=LGREY,
                buff=0.02,
            ),
        ).arrange(RIGHT, buff=0.05, aligned_edge=UP)
        things_bottom_row = Group(
            make_image_card(
                _METHODS_THINGS_FISH1_PATH,
                height=0.40,
                border_color=LGREY,
                buff=0.02,
            ),
            make_image_card(
                _METHODS_THINGS_FISH2_PATH,
                height=0.40,
                border_color=LGREY,
                buff=0.02,
            ),
            make_image_card(
                _METHODS_THINGS_FISH3_PATH,
                height=0.40,
                border_color=LGREY,
                buff=0.02,
            ),
        ).arrange(RIGHT, buff=0.05, aligned_edge=UP)
        things_images = Group(
            things_top_row,
            things_bottom_row,
        ).arrange(DOWN, buff=0.05, aligned_edge=LEFT)

        scraping_body = Group(
            _bullet_list(
                (
                    ("limited experimental control",),
                    ("perceptually very dissimilar",),
                    ("limited number of exemplars",),
                    ("variable resolution and quality",),
                ),
                font_size=16,
                width=2.95,
            ),
            make_image_card(
                _METHODS_COCO_DATASET_PATH,
                height=0.66,
                border_color=LGREY,
                buff=0.02,
            ),
            caption_line(
                "COCO dataset (Lin et al. 2015)",
                color=MGREY,
                font_size=14,
                max_width=2.80,
            ),
            things_images,
            caption_line(
                "Hebart et al. (2019)",
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

        gan_bullets = _bullet_list(
            (
                (
                    "Generative Adversarial Networks",
                    "(Goodfellow et al., 2014)",
                    "have been explored",
                    "to synthesise stimuli",
                ),
                ("limited flexibility",),
                (
                    "Denoising Diffusion Probabilistic Models",
                    "(Ho et al., 2020; Nichol \\& Dhariwal, 2021;",
                    "Rombach et al., 2022; Song et al., 2022)",
                    "have been largely unexplored",
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
            make_image_card(_METHODS_SON_2021_PATH, height=0.96, border_color=LGREY, buff=0.025),
            make_image_card(_METHODS_SON_2021B_PATH, height=1.12, border_color=LGREY, buff=0.025),
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
        dot_xs = (-4.35, 0.0, 4.35)
        timeline_y = title.get_bottom()[1] - 0.78
        dots = VGroup(
            *[
                Dot(radius=0.055, color=BLACK, stroke_width=0).move_to(np.array([x, timeline_y, 0.0]))
                for x in dot_xs
            ]
        )
        for column, dot in zip(columns, dots):
            column.next_to(dot, DOWN, buff=0.22)
            column.set_x(dot.get_x())
        line_margin = 0.14
        timeline_line = Line(
            np.array([columns.get_left()[0] - line_margin, timeline_y, 0.0]),
            np.array([columns.get_right()[0] + line_margin, timeline_y, 0.0]),
            color=BLACK,
            stroke_width=1.45,
        )

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
    """Chapter 2.4 — diffusion models offered a broader stimulus-design engine."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Diffusion models: open opportunity}",
            "More flexible outputs, but still largely unexplored for cognitive stimulus design",
        )

        left_column = VGroup(
            make_section_block(
                "Promptable synthesis",
                (
                    "specify what should appear in the image",
                    "rather than search a fixed database for it",
                ),
                accent=BLUE,
                width=4.60,
            ),
            make_section_block(
                "Flexible outputs",
                (
                    "the same model can generate many different categories",
                    "and many different object-scene concepts",
                ),
                accent=AMBER,
                width=4.60,
            ),
            make_section_block(
                "Open opportunity",
                (
                    "for cognitive stimulus design, this route was still",
                    "largely unexplored but highly promising",
                ),
                accent=GREEN,
                width=4.60,
            ),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)

        example_cards = Group(
            *[
                Group(
                    caption_line(prompt, color=accent, font_size=17, max_width=2.45),
                    make_image_card(stim_path(code, idx), height=1.08, border_color=LGREY, buff=0.03),
                ).arrange(DOWN, buff=0.10)
                for code, idx, prompt, accent in _CATEGORY_EXAMPLES
            ]
        ).arrange(RIGHT, buff=0.24, aligned_edge=UP)
        right_column = Group(
            Tex(r"\textbf{One model, many outputs}", color=INK, font_size=24),
            caption_line(
                "same generative engine across different stimulus families",
                color=MGREY,
                font_size=18,
                max_width=7.2,
            ),
            example_cards,
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        content = split_columns(left_column, right_column, buff=0.56)
        content.next_to(title, DOWN, buff=0.34)

        callout = make_callout(
            "Diffusion models looked like a more flexible engine for building many controlled continua.",
            BLUE,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(left_column, shift=UP * 0.05), run_time=0.85)
        self.play(FadeIn(content[1]), FadeIn(right_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.20)


class MethodsDiffusionPromptConditioning(Scene):
    """Chapter 2.5 — explain prompt conditioning and controlled variation."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Stable Diffusion turns a text concept into many candidate images}",
            "A fixed prompt sets the semantic target; changing the noise seed yields different exemplars",
        )

        prompt_box = make_schematic_box(
            "Prompt",
            text_lines(
                _DIFFUSION_PROMPT_LINES,
                font_size=15,
                color=INK,
                max_width=2.70,
            ),
            accent=BLUE,
            width=3.10,
            min_height=1.85,
        )
        encoder_box = make_schematic_box(
            "Text encoder",
            text_lines(
                (
                    "CLIP-trained mapping",
                    "from text to semantic features",
                ),
                font_size=16,
                color=INK,
                max_width=2.35,
            ),
            accent=AMBER,
            width=2.80,
            min_height=1.38,
        )
        embedding_box = make_schematic_box(
            "Prompt embedding",
            MathTex(r"c", color=GREEN, font_size=34),
            accent=GREEN,
            width=1.95,
            min_height=1.12,
        )

        prompt_flow = Group(prompt_box, encoder_box, embedding_box).arrange(
            RIGHT, buff=0.26, aligned_edge=DOWN
        )
        prompt_arrows = VGroup(
            Arrow(
                prompt_box.get_right() + RIGHT * 0.03,
                encoder_box.get_left() + LEFT * 0.03,
                color=MGREY,
                stroke_width=1.5,
                buff=0.04,
                tip_length=0.12,
                tip_shape=StealthTip,
            ),
            Arrow(
                encoder_box.get_right() + RIGHT * 0.03,
                embedding_box.get_left() + LEFT * 0.03,
                color=MGREY,
                stroke_width=1.5,
                buff=0.04,
                tip_length=0.12,
                tip_shape=StealthTip,
            ),
        )

        left_column = Group(
            Tex(r"\textbf{Semantic instruction}", color=INK, font_size=24),
            caption_line(
                "The prompt specifies what should appear in the image.",
                color=MGREY,
                font_size=17,
                max_width=4.35,
            ),
            Group(prompt_flow, prompt_arrows),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        noise_box = make_schematic_box(
            "Random latent / noise seed",
            MathTex(r"z_T", color=BLUE, font_size=32),
            accent=BLUE,
            width=2.10,
            min_height=1.12,
        )
        denoiser_box = make_schematic_box(
            "Denoising model",
            text_lines(
                (
                    "use the prompt embedding",
                    "to guide image formation",
                ),
                font_size=16,
                color=INK,
                max_width=2.25,
            ),
            accent=GREEN,
            width=2.75,
            min_height=1.35,
        )
        model_row = Group(noise_box, denoiser_box).arrange(RIGHT, buff=0.32, aligned_edge=DOWN)
        model_arrow = Arrow(
            noise_box.get_right() + RIGHT * 0.03,
            denoiser_box.get_left() + LEFT * 0.03,
            color=MGREY,
            stroke_width=1.5,
            buff=0.04,
            tip_length=0.12,
            tip_shape=StealthTip,
        )
        candidates = make_image_strip(_DIFFUSION_CODE, (1, 3, 5, 7), height=0.78, buff=0.08)
        seed_badges = VGroup(
            *[make_badge(f"seed {idx + 1}", accent=AMBER, font_size=13) for idx in range(len(candidates))]
        )
        for badge, card in zip(seed_badges, candidates):
            badge.next_to(card, UP, buff=0.08)

        right_column = Group(
            Tex(r"\textbf{Controlled variation}", color=INK, font_size=24),
            caption_line(
                "Keep the prompt fixed, vary the noise seed, and sample multiple plausible exemplars.",
                color=MGREY,
                font_size=17,
                max_width=5.25,
            ),
            Group(model_row, model_arrow),
            Group(seed_badges, candidates),
            caption_line(
                "same prompt, different noise seeds $\rightarrow$ different candidate images",
                color=MGREY,
                font_size=15,
                max_width=5.20,
            ),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        content = split_columns(left_column, right_column, buff=0.46)
        content.next_to(title, DOWN, buff=0.34)
        content[2].shift(DOWN * 0.06)
        conditioning_arrow = Arrow(
            embedding_box.get_bottom() + DOWN * 0.02,
            denoiser_box.get_top() + UP * 0.04,
            color=GREEN,
            stroke_width=1.5,
            buff=0.04,
            tip_length=0.12,
            tip_shape=StealthTip,
        )
        output_arrow = Arrow(
            denoiser_box.get_right() + RIGHT * 0.03,
            candidates.get_left() + LEFT * 0.04,
            color=GREEN,
            stroke_width=1.5,
            buff=0.04,
            tip_length=0.12,
            tip_shape=StealthTip,
        )

        callout = make_callout(
            "One semantic description became a controllable stimulus family for Study 1 and Study 2.",
            BLUE,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(left_column[0:2], shift=UP * 0.04), run_time=0.45)
        self.play(FadeIn(prompt_box, scale=0.97), run_time=0.35)
        self.play(Create(prompt_arrows[0]), FadeIn(encoder_box, scale=0.97), run_time=0.35)
        self.play(Create(prompt_arrows[1]), FadeIn(embedding_box, scale=0.97), run_time=0.32)
        self.play(FadeIn(right_column[0:2], shift=UP * 0.04), run_time=0.42)
        self.play(FadeIn(noise_box, scale=0.97), FadeIn(denoiser_box, scale=0.97), Create(model_arrow), run_time=0.38)
        self.play(Create(conditioning_arrow), run_time=0.28)
        self.play(Create(output_arrow), FadeIn(seed_badges, shift=UP * 0.03), FadeIn(candidates, shift=UP * 0.03), run_time=0.42)
        self.play(FadeIn(right_column[-1], shift=UP * 0.03), FadeIn(callout, shift=UP * 0.04), run_time=0.40)
        self.wait(3.00)


class MethodsDiffusionTrainVsGenerate(Scene):
    """Chapter 2.6 — contrast forward diffusion with reverse denoising."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Train by adding noise, generate by reversing that process}",
            "During sampling, the model uses the current noisy latent, the timestep, and the prompt representation",
        )

        clean = load_rgb(stim_path(_EXEMPLAR_CODE, 5))
        levels = [0.0, 0.35, 0.70, 1.0]
        forward_sources = [blend_with_noise(clean, alpha) for alpha in levels]
        reverse_sources = list(reversed(forward_sources))

        def make_step_labels(cards: Group, labels: tuple[str, ...], *, color: str = MGREY) -> VGroup:
            label_group = VGroup(*[Tex(label, color=color, font_size=16) for label in labels])
            for label, card in zip(label_group, cards):
                label.next_to(card, DOWN, buff=0.08)
            return label_group

        def make_arrow_tags(arrows: VGroup, text: str, *, color: str) -> VGroup:
            tags = VGroup(*[Tex(text, color=color, font_size=15) for _ in arrows])
            for tag, arrow in zip(tags, arrows):
                tag.next_to(arrow, UP, buff=0.10)
            return tags

        forward_cards, forward_arrows = make_image_progression(
            forward_sources,
            height=0.70,
            arrow_color=MGREY,
            border_color=LGREY,
            item_buff=0.15,
        )
        forward_labels = make_step_labels(forward_cards, ("clean", "noisy", "noisier", "noise"))
        forward_tags = make_arrow_tags(forward_arrows, r"$+$ noise", color=AMBER)

        forward_block = Group(
            Group(
                make_badge("training", accent=AMBER, font_size=14),
                Tex(r"\textbf{Forward diffusion process}", color=INK, font_size=22),
            ).arrange(RIGHT, buff=0.14),
            caption_line(
                "Start from a real image and progressively corrupt it with Gaussian noise.",
                color=MGREY,
                font_size=16,
                max_width=4.85,
            ),
            Group(Group(forward_cards, forward_arrows), forward_tags, forward_labels),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)

        noisy_latent_box = make_schematic_box(
            "Current noisy latent",
            MathTex(r"z_t", color=BLUE, font_size=32),
            accent=BLUE,
            width=2.05,
            min_height=1.10,
        )
        denoiser_box = make_schematic_box(
            "Denoising model",
            text_lines(
                (
                    "predict the noise",
                    "that should be removed",
                ),
                font_size=16,
                color=INK,
                max_width=2.20,
            ),
            accent=GREEN,
            width=2.70,
            min_height=1.34,
        )
        timestep_badge = make_badge(r"timestep $t$", accent=AMBER, font_size=15)
        prompt_badge = make_badge(r"prompt embedding $c$", accent=GREEN, font_size=15)

        model_row = Group(noisy_latent_box, denoiser_box).arrange(RIGHT, buff=0.34, aligned_edge=DOWN)
        model_arrow = Arrow(
            noisy_latent_box.get_right() + RIGHT * 0.03,
            denoiser_box.get_left() + LEFT * 0.03,
            color=MGREY,
            stroke_width=1.5,
            buff=0.04,
            tip_length=0.12,
            tip_shape=StealthTip,
        )
        prompt_badge.next_to(denoiser_box, UP, buff=0.18).shift(LEFT * 0.10)
        timestep_badge.next_to(prompt_badge, LEFT, buff=0.14)
        prompt_arrow = Arrow(
            prompt_badge.get_bottom() + DOWN * 0.02,
            denoiser_box.get_top() + UP * 0.04,
            color=GREEN,
            stroke_width=1.4,
            buff=0.04,
            tip_length=0.11,
            tip_shape=StealthTip,
        )
        timestep_arrow = Arrow(
            timestep_badge.get_bottom() + DOWN * 0.02,
            denoiser_box.get_top() + UP * 0.04 + LEFT * 0.36,
            color=AMBER,
            stroke_width=1.4,
            buff=0.04,
            tip_length=0.11,
            tip_shape=StealthTip,
        )

        reverse_cards, reverse_arrows = make_image_progression(
            reverse_sources,
            height=0.70,
            arrow_color=BLUE,
            border_color=LGREY,
            item_buff=0.15,
        )
        reverse_labels = make_step_labels(
            reverse_cards,
            ("noise", "less noise", "clearer", "image"),
            color=BLUE,
        )
        reverse_tags = VGroup(
            Tex(r"predict noise", color=GREEN, font_size=15),
            Tex(r"remove noise", color=GREEN, font_size=15),
            Tex(r"repeat", color=GREEN, font_size=15),
        )
        for tag, arrow in zip(reverse_tags, reverse_arrows):
            tag.next_to(arrow, UP, buff=0.10)

        reverse_formula = MathTex(
            r"\hat{\epsilon}_{\theta}(z_t, t, c)",
            color=BLUE,
            font_size=24,
        )

        reverse_block = Group(
            Group(
                make_badge("generation", accent=GREEN, font_size=14),
                Tex(r"\textbf{Reverse denoising loop}", color=INK, font_size=22),
            ).arrange(RIGHT, buff=0.14),
            caption_line(
                "At each step, the model sees the current noisy latent, the timestep, and the prompt representation.",
                color=MGREY,
                font_size=16,
                max_width=5.05,
            ),
            Group(model_row, model_arrow, prompt_badge, timestep_badge, prompt_arrow, timestep_arrow),
            reverse_formula,
            Group(Group(reverse_cards, reverse_arrows), reverse_tags, reverse_labels),
            caption_line(
                "In Stable Diffusion, this loop runs in compressed latent space rather than directly in pixels.",
                color=MGREY,
                font_size=15,
                max_width=5.05,
            ),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)

        content = split_columns(forward_block, reverse_block, buff=0.42)
        content.next_to(title, DOWN, buff=0.32)

        callout = make_callout(
            "That made controlled sampling and later latent interpolation possible for the stimulus continua.",
            GREEN,
            font_size=19,
        ).to_edge(DOWN, buff=0.33)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(forward_block[0:2], shift=UP * 0.04), run_time=0.42)
        self.play(FadeIn(forward_cards[0], scale=0.97), run_time=0.24)
        for idx in range(1, len(forward_cards)):
            self.play(
                Create(forward_arrows[idx - 1]),
                FadeIn(forward_cards[idx], scale=0.97),
                FadeIn(forward_tags[idx - 1], shift=UP * 0.02),
                run_time=0.26,
            )
        self.play(FadeIn(forward_labels), run_time=0.24)
        self.play(FadeIn(reverse_block[0:2], shift=UP * 0.04), FadeIn(content[1]), run_time=0.38)
        self.play(
            FadeIn(noisy_latent_box, scale=0.97),
            FadeIn(denoiser_box, scale=0.97),
            Create(model_arrow),
            FadeIn(prompt_badge, shift=UP * 0.02),
            FadeIn(timestep_badge, shift=UP * 0.02),
            run_time=0.35,
        )
        self.play(Create(prompt_arrow), Create(timestep_arrow), FadeIn(reverse_formula, shift=UP * 0.02), run_time=0.28)
        self.play(FadeIn(reverse_cards[0], scale=0.97), run_time=0.22)
        for idx in range(1, len(reverse_cards)):
            self.play(
                Create(reverse_arrows[idx - 1]),
                FadeIn(reverse_cards[idx], scale=0.97),
                FadeIn(reverse_tags[idx - 1], shift=UP * 0.02),
                run_time=0.26,
            )
        self.play(FadeIn(reverse_labels), FadeIn(reverse_block[-1], shift=UP * 0.02), FadeIn(callout, shift=UP * 0.04), run_time=0.32)
        self.wait(3.00)


class MethodsProjectPlan(Scene):
    """Chapter 2.7 — end with the actual thesis plan."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Project plan}",
            "Generate the stimulus set, validate it behaviourally, then use it in neuroimaging",
        )

        generate_body = Group(
            make_image_strip(_EXEMPLAR_CODE, (0, 3, 6, 9), height=0.42, buff=0.04),
            text_lines(
                (
                    "generate many candidate continua",
                    "from fixed prompts and controlled variation",
                ),
                font_size=15,
                color=INK,
                max_width=2.80,
            ),
        ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)

        validate_body = text_lines(
            (
                "similarity judgments",
                "working-memory validation",
                "retain the usable stimulus sets",
            ),
            font_size=16,
            color=INK,
            max_width=2.60,
        )

        study2_brain = brain_icon_with_evc(highlight_color=BLUE, scale_factor=0.38)
        scan_body = Group(
            study2_brain["group"],
            text_lines(
                (
                    "use the validated set in fMRI",
                    "test representational format",
                    "and sensory recruitment",
                ),
                font_size=16,
                color=INK,
                max_width=2.90,
            ),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        stages = Group(
            make_pipeline_stage("01", "Generate", generate_body, accent=BLUE, width=2.90),
            make_pipeline_stage("02", "Validate", validate_body, accent=AMBER, width=2.65),
            make_pipeline_stage("03", "Neuroimaging", scan_body, accent=GREEN, width=3.00),
        )
        arrows = VGroup(
            *[
                Arrow(
                    LEFT * 0.34,
                    RIGHT * 0.34,
                    color=MGREY,
                    stroke_width=1.6,
                    buff=0.0,
                    tip_length=0.12,
                    tip_shape=StealthTip,
                )
                for _ in range(len(stages) - 1)
            ]
        )
        flow_items = Group()
        for idx, stage in enumerate(stages):
            flow_items.add(stage)
            if idx < len(arrows):
                flow_items.add(arrows[idx])
        flow = flow_items.arrange(RIGHT, buff=0.22, aligned_edge=UP)
        flow.next_to(title, DOWN, buff=0.44)

        callout = make_callout(
            "Generate a stimulus set, validate it behaviourally, then use it in the neuroimaging study.",
            GREEN,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(stages[0], shift=UP * 0.05), run_time=0.50)
        for idx in range(1, len(stages)):
            self.play(Create(arrows[idx - 1]), FadeIn(stages[idx], shift=UP * 0.05), run_time=0.55)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.20)


MethodsGANsProofOfConcept = MethodsExistingApproaches


_METHODS_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    MethodsStimulusRequirementsA,
    MethodsStimulusRequirementsB,
    MethodsStimulusRequirementsC,
    MethodsStimulusRequirementsD,
    MethodsExistingApproaches,
    MethodsDiffusionOpportunity,
    MethodsDiffusionPromptConditioning,
    MethodsDiffusionTrainVsGenerate,
    MethodsProjectPlan,
)
_METHODS_SECTION_NAMES: tuple[str, ...] = (
    "methods_stimulus_requirements_a",
    "methods_stimulus_requirements_b",
    "methods_stimulus_requirements_c",
    "methods_stimulus_requirements_d",
    "methods_existing_approaches",
    "methods_diffusion_opportunity",
    "methods_diffusion_prompt_conditioning",
    "methods_diffusion_train_vs_generate",
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
