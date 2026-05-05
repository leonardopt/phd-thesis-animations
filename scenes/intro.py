"""
Introduction — sectioned production render.

Render from this file to keep all introduction outputs in the same
`media/videos/01_intro/...` folder.

Production render:
    uv run manim scenes/intro.py Introduction -ql --save_sections
"""
from __future__ import annotations

from pathlib import Path
from queue import Queue
import random
import sys

import numpy as np
from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import REPO_ROOT, env_path, section_output_dir, simplify_manim_section_video_names


_SECTION_OUTPUT_DIR = section_output_dir("intro")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "intro"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)

_INTRO_SCENE_ORDER: dict[str, str] = {
    "IntroCognitiveProblemA": "00",
    "IntroSensoryMemoryRepresentationA": "01",
    "IntroSensoryMemoryRepresentationB": "02",
    "IntroClassicalView": "03",
    "IntroSensoryRecruitment": "04",
    "IntroResearchQuestion1": "05",
    "IntroResearchQuestion2": "06",
    "IntroResearchQuestion3": "07",
}


class _IntroNumberedScene:
    """Prefix standalone intro renders with their section order."""

    def __init__(self, *args, **kwargs):
        scene_name = self.__class__.__name__
        number = _INTRO_SCENE_ORDER.get(scene_name, "")
        if number and config.output_file == "intro":
            config.output_file = f"{number}_{scene_name}"
        super().__init__(*args, **kwargs)


# ── Palette ───────────────────────────────────────────────────────────────────
BG = WHITE
INK = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
BLUE = "#2563EB"
AMBER = "#D97706"
GREEN = "#16A34A"
RED = "#DC2626"
RQ_BLUE = "#4E647F"
RQ_RED = "#7A2E3A"
RQ_GREEN = "#2F5D50"
RQ_MUTED = "#6B7280"
PANEL = "#F8FAFC"
EVC_BLUE = "#6E839A"
EVC_TAUPE = "#9B8D80"
EVC_GREEN = "#7A9589"
PATTERN_BLUE = "#4C72B0"
PATTERN_RED = "#C44E52"
PATTERN_WHITE = "#F8F8F8"
_MATRIX_CELL = 0.16


# ── Assets ────────────────────────────────────────────────────────────────────
_INTRO_STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
_ANATOMY_IMAGE_DIR = REPO_ROOT / "assets" / "images" / "anatomy"
_INTRO_FIG_DIR = REPO_ROOT / "assets" / "images" / "intro"
_BRAIN_ICON_PATH = REPO_ROOT / "assets" / "images" / "study2" / "brain_icon_sagittal.png"
_HEAD_BRAIN_PATH = _ANATOMY_IMAGE_DIR / "head_brain.png"
_VISUAL_CORTEX_FIG = str(_ANATOMY_IMAGE_DIR / "visual_cortex_white.png")
_INTRO_HOOK_TARGET_FISH = str(_INTRO_STIM_DIR / "animal_fish-00.png")
_INTRO_HOOK_FOIL_FISH = str(_INTRO_STIM_DIR / "animal_fish-05.png")
_INTRO_HOOK_CANNY_FISH = str(_INTRO_FIG_DIR / "animal_fish-00_canny.png")
_INTRO_HOOK_QUESTION_NORMAL_FISH = str(_INTRO_STIM_DIR / "animal_fish-09.png")
_INTRO_HOOK_QUESTION_FISH = str(_INTRO_FIG_DIR / "animal_fish-09_soft.png")
_INTRO_HOOK_QUESTION_MEMORY_FISH = str(_INTRO_FIG_DIR / "animal_fish-09_memory.png")
_INTRO_RQ2_SIMPLE_STIMULI = (
    ("color_probe", r"Emrich et al. (2013)"),
    ("radial_probe", r"Sprague et al. (2014)"),
    ("orientation_probe", r"Harrison \& Tong (2009)"),
    ("grating_probe", r"Christophel et al. (2012)"),
)
_INTRO_RQ2_INTERMEDIATE_STIMULI = (
    ("object_probe", r"Lee et al. (2013)"),
    ("scene_probe", r"Xu (2023)"),
)
_INTRO_RQ2_NATURALISTIC_STIMULI = (
    str(_INTRO_STIM_DIR / "landscape_element_mountain_ridge-00.png"),
    str(_INTRO_STIM_DIR / "plant_bristlecone-00.png"),
    str(_INTRO_STIM_DIR / "item_lamp_table-00.png"),
)

_EXEMPLAR_CODE = "building_observatory"
_HOOK_CODE = "animal_fish"

# ── Intro constants ───────────────────────────────────────────────────────────
_SECTION_HOLD = 0.35
_ORDER = (5, 3, 7, 1, 8, 2, 6, 4)
_STRIP = (0, 2, 4, 6, 8)
_FROZEN_IDX = 4
_PRIOR_SPECS = ((0.62, 0.28), (0.74, 0.56), (0.86, 0.90))
_INTRO_QUESTION_BULLET_GAP = 0.44
_INTRO_QUESTION_TEXT_CENTER_X = -3.35
_INTRO_QUESTION_VISUAL_CENTER_X = 3.35
_INTRO_QUESTION_CONTENT_Y = -0.22
_INTRO_QUESTION_HEADER_DEFAULT_LEFT_X = -4.72
_INTRO_QUESTION_HEADER_DEFAULT_RIGHT_X = 4.80
_INTRO_QUESTION_HEADER_Y = 3.5
_INTRO_QUESTION_HEADER_FONT_SIZE = 28
_INTRO_QUESTION_BULLET_FONT_SIZE = 21
_INTRO_QUESTION_CLAIM_FONT_SIZE = 23.5
_INTRO_QUESTION_CLAIM_MAX_WIDTH = 5.35


def _seeded_pattern(seed: int) -> np.ndarray:
    """Return a deterministic 4x4 pattern matrix for small visual motifs."""
    rng = np.random.default_rng(seed)
    return rng.uniform(-1.0, 1.0, size=(4, 4))


_PLOT_SENSORY_PATTERN_LEFT = _seeded_pattern(11)
_PLOT_MEMORY_PATTERN = _seeded_pattern(12)
_PLOT_SENSORY_PATTERN_RIGHT = _seeded_pattern(13)


_REPRESENTATION_SENSORY_PATTERN_LEFT = np.array(
    [
        [-0.78, -0.26, 0.10, -0.72],
        [-0.56, 0.68, -0.40, -0.60],
        [0.64, 0.18, -0.10, 0.16],
        [-0.18, 0.04, -0.48, 0.54],
    ]
)
_REPRESENTATION_MEMORY_PATTERN = np.array(
    [
        [0.58, -0.68, 0.64, -0.10],
        [-0.14, 0.74, -0.56, 0.62],
        [0.70, -0.28, 0.18, -0.74],
        [-0.60, 0.52, -0.22, 0.68],
    ]
)
_REPRESENTATION_SENSORY_PATTERN_RIGHT = np.array(
    [
        [-0.62, -0.04, 0.26, -0.54],
        [-0.34, 0.80, -0.18, -0.38],
        [0.80, 0.10, 0.14, 0.08],
        [0.04, 0.24, -0.26, 0.68],
    ]
)


def stim_path(code: str, idx: int) -> str:
    """Return the absolute path for one intro stimulus exemplar image."""
    return str(_INTRO_STIM_DIR / f"{code}-{idx:02d}.png")


def preferred_path(*candidates: Path | str) -> str:
    """Return the first existing path from the candidate list."""
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)
    return str(Path(candidates[0]))


def _img(path: str, height: float) -> ImageMobject:
    """Load an image mobject and normalize it to the requested height."""
    img = ImageMobject(path)
    img.height = height
    return img


def _bold_tex(text: str) -> str:
    """Wrap plain text in `\\textbf{}` unless it is already bolded."""
    return text if r"\textbf{" in text else rf"\textbf{{{text}}}"


def _wrap_tex_to_lines(
    text: str,
    *,
    max_width: float,
    font_size: float,
    tex_environment: str = "flushleft",
) -> str:
    """Greedily wrap TeX text into lines that fit a measured width."""
    wrapped_paragraphs: list[str] = []
    for paragraph in text.split(r"\\"):
        words = paragraph.strip().split()
        if not words:
            continue
        lines: list[str] = []
        current_line: list[str] = []
        for word in words:
            candidate = " ".join([*current_line, word])
            candidate_mob = Tex(candidate, font_size=font_size, tex_environment=tex_environment)
            if candidate_mob.width <= max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        wrapped_paragraphs.append(r"\\ ".join(lines))
    return r"\\ ".join(wrapped_paragraphs)


def _wrapped_tex(
    text: str,
    *,
    max_width: float,
    color: str,
    font_size: float,
    tex_environment: str = "flushleft",
) -> Tex:
    """Build a `Tex` object after width-aware line wrapping."""
    return Tex(
        _wrap_tex_to_lines(
            text,
            max_width=max_width,
            font_size=font_size,
            tex_environment=tex_environment,
        ),
        color=color,
        font_size=font_size,
        tex_environment=tex_environment,
    )


def title_block(title_text: str, subtitle_text: str | None = None) -> VGroup:
    """Build the standard intro title and optional subtitle block."""
    title = Tex(_bold_tex(title_text), color=INK, font_size=34).to_edge(UP, buff=0.34)
    parts = [title]
    if subtitle_text is not None:
        subtitle = Tex(subtitle_text, color=INK, font_size=21)
        subtitle.next_to(title, DOWN, buff=0.14)
        parts.append(subtitle)
    return VGroup(*parts)



def make_callout(text: str, color: str, *, font_size: float = 23) -> VGroup:
    """Build a short underlined takeaway callout."""
    line = Tex(text, color=INK, font_size=font_size)
    underline = Line(
        line.get_left() + DOWN * 0.12,
        line.get_right() + DOWN * 0.12,
        color=color,
        stroke_width=2.0,
    )
    return VGroup(line, underline)


def make_info_card(
    title_text: str,
    subtitle_text: str,
    *,
    accent: str,
    width: float = 5.2,
    height: float = 1.28,
    title_font_size: float = 20,
    subtitle_font_size: float = 16,
    subtitle_color: str = INK,
) -> VGroup:
    """Build a framed info card with a colored accent rail."""
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.16,
        stroke_color=LGREY,
        stroke_width=1.4,
    ).set_fill(PANEL, opacity=0.96)
    accent_bar = RoundedRectangle(
        width=0.12,
        height=height - 0.24,
        corner_radius=0.06,
        stroke_width=0,
    ).set_fill(accent, opacity=1.0)
    accent_bar.move_to(np.array([frame.get_left()[0] + 0.22, frame.get_center()[1], 0.0]))

    title = Tex(title_text, color=INK, font_size=title_font_size)
    subtitle = Tex(subtitle_text, color=subtitle_color, font_size=subtitle_font_size)
    text_block = VGroup(title, subtitle).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
    max_text_width = width - 0.74
    if text_block.width > max_text_width:
        text_block.scale_to_fit_width(max_text_width)
    text_block.move_to(frame.get_center())
    text_block.align_to(frame, LEFT).shift(RIGHT * 0.48)

    return VGroup(frame, accent_bar, text_block)


def make_summary_panel(
    headline_lines: tuple[str, ...],
    body_lines: tuple[str, ...],
    ref_lines: tuple[str, ...],
    *,
    accent: str,
    width: float = 6.0,
    height: float = 3.36,
    headline_font_size: float = 20,
    body_font_size: float = 18,
    ref_font_size: float = 15,
) -> VGroup:
    """Build a stacked headline/body/reference summary panel."""
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.16,
        stroke_color=LGREY,
        stroke_width=1.4,
    ).set_fill(PANEL, opacity=0.96)
    accent_bar = RoundedRectangle(
        width=0.12,
        height=height - 0.24,
        corner_radius=0.06,
        stroke_width=0,
    ).set_fill(accent, opacity=1.0)
    accent_bar.move_to(np.array([frame.get_left()[0] + 0.22, frame.get_center()[1], 0.0]))

    headline = VGroup(
        *[Tex(line, color=INK, font_size=headline_font_size) for line in headline_lines]
    ).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
    body = VGroup(
        *[Tex(line, color=INK, font_size=body_font_size) for line in body_lines]
    ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
    refs = VGroup(
        *[Tex(line, color=INK, font_size=ref_font_size) for line in ref_lines]
    ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)

    text_block = VGroup(headline, body, refs).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    max_text_width = width - 0.74
    max_text_height = height - 0.32
    if text_block.width > max_text_width:
        text_block.scale_to_fit_width(max_text_width)
    if text_block.height > max_text_height:
        text_block.scale_to_fit_height(max_text_height)
    text_block.move_to(frame.get_center())
    text_block.align_to(frame, LEFT).shift(RIGHT * 0.48)

    return VGroup(frame, accent_bar, text_block)


def make_literature_entry(
    title_text: str,
    claim_lines: tuple[str, ...],
    ref_lines: tuple[str, ...],
    *,
    accent: str,
    divider_width: float = 4.60,
) -> VGroup:
    """Build one literature-review entry with claims, references, and divider."""
    title_row = VGroup(
        Dot(radius=0.045, color=accent),
        Tex(rf"\textbf{{{title_text}}}", color=accent, font_size=18),
    ).arrange(RIGHT, buff=0.12)
    claim = VGroup(
        *[Tex(line, color=INK, font_size=18) for line in claim_lines]
    ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
    refs = VGroup(
        *[Tex(line, color=INK, font_size=14) for line in ref_lines]
    ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
    divider = Line(LEFT * divider_width / 2, RIGHT * divider_width / 2, color=LGREY, stroke_width=1.0)
    group = VGroup(title_row, claim, refs, divider).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    divider.align_to(claim, LEFT)
    return group


def make_literature_schematic(
    kind: str,
    *,
    width: float,
    height: float,
    accent: str,
) -> Group:
    """Build a rights-safe schematic thumbnail for cited literature."""
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.08,
        stroke_color=LGREY,
        stroke_width=1.2,
    ).set_fill(PANEL, opacity=1.0)
    center = frame.get_center()

    def point(x: float, y: float) -> np.ndarray:
        return center + np.array([x * width, y * height, 0.0])

    def trace(points: tuple[tuple[float, float], ...], color: str = accent) -> VMobject:
        path = VMobject(color=color, stroke_width=2.0)
        path.set_points_smoothly([point(x, y) for x, y in points])
        return path

    elements = Group()
    if kind == "delay_firing":
        axes = Group(
            Line(point(-0.38, -0.28), point(-0.38, 0.30), color=MGREY, stroke_width=1.0),
            Line(point(-0.38, -0.28), point(0.38, -0.28), color=MGREY, stroke_width=1.0),
        )
        delay = Rectangle(
            width=0.30 * width,
            height=0.50 * height,
            stroke_width=0,
        ).set_fill(accent, opacity=0.10)
        delay.move_to(point(0.10, 0.01))
        spikes = Group(
            trace(((-0.34, -0.20), (-0.16, -0.04), (0.02, 0.02), (0.20, 0.18), (0.36, 0.24))),
            trace(((-0.34, -0.12), (-0.16, 0.10), (0.02, 0.20), (0.20, 0.12), (0.36, 0.16)), BLUE),
            trace(((-0.34, 0.04), (-0.12, 0.00), (0.10, 0.08), (0.28, -0.02), (0.36, 0.06)), GREEN),
        )
        elements = Group(delay, axes, spikes)
    elif kind == "activation_map":
        head = Ellipse(
            width=0.58 * width,
            height=0.72 * height,
            stroke_color=MGREY,
            stroke_width=1.1,
        ).set_fill(WHITE, opacity=1.0)
        head.move_to(point(-0.04, 0.00))
        hotspots = Group(
            Circle(radius=0.075 * min(width, height)).set_fill(accent, opacity=0.68).set_stroke(width=0).move_to(point(-0.18, 0.12)),
            Circle(radius=0.055 * min(width, height)).set_fill(BLUE, opacity=0.62).set_stroke(width=0).move_to(point(0.12, 0.06)),
            Circle(radius=0.050 * min(width, height)).set_fill(GREEN, opacity=0.58).set_stroke(width=0).move_to(point(0.02, -0.16)),
        )
        elements = Group(head, hotspots)
    elif kind == "orientation_decoder":
        ring = Circle(radius=0.29 * min(width, height), color=MGREY, stroke_width=1.0)
        ring.move_to(point(-0.16, 0.02))
        bars = Group()
        for index, angle in enumerate(np.linspace(0, PI, 6, endpoint=False)):
            bar = Line(LEFT * 0.12, RIGHT * 0.12, color=accent, stroke_width=2.0)
            bar.rotate(angle)
            bar.move_to(point(-0.16 + 0.14 * np.cos(angle), 0.02 + 0.18 * np.sin(angle)))
            bars.add(bar)
        matrix = _mini_matrix(_PLOT_MEMORY_PATTERN, cell=0.055 * min(width, height))
        matrix.move_to(point(0.24, 0.02))
        elements = Group(ring, bars, matrix)
    elif kind == "distributed_map":
        brain = Ellipse(
            width=0.70 * width,
            height=0.62 * height,
            stroke_color=MGREY,
            stroke_width=1.0,
        ).set_fill(WHITE, opacity=1.0)
        brain.move_to(point(0.0, 0.02))
        nodes = Group()
        for x, y, color in (
            (-0.22, 0.12, accent),
            (-0.04, 0.20, BLUE),
            (0.16, 0.10, GREEN),
            (-0.12, -0.12, RED),
            (0.18, -0.14, AMBER),
        ):
            nodes.add(
                Circle(radius=0.045 * min(width, height))
                .set_fill(color, opacity=0.72)
                .set_stroke(width=0)
                .move_to(point(x, y))
            )
        links = Group(
            Line(nodes[0].get_center(), nodes[1].get_center(), color=MGREY, stroke_width=0.8),
            Line(nodes[1].get_center(), nodes[2].get_center(), color=MGREY, stroke_width=0.8),
            Line(nodes[0].get_center(), nodes[3].get_center(), color=MGREY, stroke_width=0.8),
            Line(nodes[3].get_center(), nodes[4].get_center(), color=MGREY, stroke_width=0.8),
        )
        elements = Group(brain, links, nodes)
    elif kind == "color_probe":
        elements = Group(
            *[
                Circle(radius=0.10 * min(width, height))
                .set_fill(color, opacity=0.92)
                .set_stroke(WHITE, width=1.0)
                .move_to(point(x, y))
                for (x, y), color in zip(
                    ((-0.18, 0.14), (0.02, 0.16), (0.18, -0.02), (-0.08, -0.16)),
                    (BLUE, RED, GREEN, AMBER),
                )
            ]
        )
    elif kind == "radial_probe":
        rays = Group()
        for angle in np.linspace(0, TAU, 12, endpoint=False):
            ray = Line(point(0.0, 0.0), point(0.28 * np.cos(angle), 0.28 * np.sin(angle)), color=accent, stroke_width=1.6)
            rays.add(ray)
        elements = Group(Circle(radius=0.06 * min(width, height), color=accent).set_fill(accent, opacity=0.95).move_to(point(0, 0)), rays)
    elif kind == "orientation_probe":
        bars = Group()
        for x, y, angle in ((-0.24, 0.16, 0.20), (0.04, 0.16, 1.10), (0.24, -0.08, 2.10), (-0.10, -0.18, 2.65)):
            bar = Line(LEFT * 0.16, RIGHT * 0.16, color=accent, stroke_width=3.0)
            bar.rotate(angle)
            bar.move_to(point(x, y))
            bars.add(bar)
        elements = bars
    elif kind == "grating_probe":
        stripes = Group()
        for offset in np.linspace(-0.28, 0.28, 7):
            stripe = Rectangle(width=0.075 * width, height=0.58 * height, stroke_width=0)
            stripe.set_fill(accent if int((offset + 0.28) * 100) % 2 == 0 else MGREY, opacity=0.82)
            stripe.rotate(0.40)
            stripe.move_to(point(offset, 0.0))
            stripes.add(stripe)
        elements = stripes
    elif kind == "object_probe":
        body = RoundedRectangle(width=0.38 * width, height=0.34 * height, corner_radius=0.06)
        body.set_fill(accent, opacity=0.72).set_stroke(INK, width=0.8, opacity=0.45)
        body.move_to(point(0.0, -0.02))
        handle = Arc(radius=0.16 * min(width, height), angle=PI, color=INK, stroke_width=1.2)
        handle.rotate(PI)
        handle.next_to(body, UP, buff=-0.04)
        elements = Group(handle, body)
    elif kind == "scene_probe":
        sky = Rectangle(width=0.62 * width, height=0.30 * height, stroke_width=0).set_fill(BLUE, opacity=0.18)
        sky.move_to(point(0, 0.12))
        ground = Rectangle(width=0.62 * width, height=0.22 * height, stroke_width=0).set_fill(GREEN, opacity=0.20)
        ground.move_to(point(0, -0.18))
        mountain = Polygon(point(-0.28, -0.14), point(-0.06, 0.20), point(0.13, -0.14), color=MGREY)
        mountain.set_fill(MGREY, opacity=0.55).set_stroke(width=0)
        sun = Circle(radius=0.06 * min(width, height)).set_fill(AMBER, opacity=0.90).set_stroke(width=0).move_to(point(0.22, 0.20))
        elements = Group(sky, ground, mountain, sun)
    else:
        elements = Group(_mini_matrix(_PLOT_SENSORY_PATTERN_LEFT, cell=0.075 * min(width, height)))
        elements.move_to(center)

    elements.move_to(center)
    return Group(frame, elements)


def brain_icon_with_evc(*, highlight_color: str = BLUE, scale_factor: float = 1.0) -> dict[str, Mobject]:
    """Return the brain icon plus a highlighted early-visual-cortex overlay."""
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
    ).set_fill(highlight_color, opacity=0.14).move_to(highlight_center)
    highlight_ring = Ellipse(
        width=0.26 * brain.width,
        height=0.20 * brain.height,
        stroke_color=highlight_color,
        stroke_width=1.8,
    ).set_stroke(opacity=0.82).set_fill(highlight_color, opacity=0.0).move_to(highlight_center)
    highlight_fill.set_z_index(1)
    highlight_ring.set_z_index(2)
    brain.set_z_index(0)
    return {
        "group": Group(brain, highlight_fill, highlight_ring),
        "brain": brain,
        "highlight": VGroup(highlight_fill, highlight_ring),
    }


def brain_render(*, scale_factor: float = 1.0) -> ImageMobject:
    """Return the rendered head-and-brain illustration at a standard scale."""
    brain = ImageMobject(str(_HEAD_BRAIN_PATH))
    brain.scale_to_fit_height(2.85 * scale_factor)
    return brain


def _pattern_color(value: float) -> ManimColor:
    """Map signed pattern values onto the intro red/blue diverging palette."""
    clipped = max(-1.0, min(1.0, float(value)))
    if clipped < 0:
        return interpolate_color(ManimColor(PATTERN_WHITE), ManimColor(PATTERN_BLUE), abs(clipped))
    return interpolate_color(ManimColor(PATTERN_WHITE), ManimColor(PATTERN_RED), clipped)


def _mini_matrix(matrix: np.ndarray, *, cell: float = 0.12) -> VGroup:
    """Render a small colored square grid from a 2D pattern matrix."""
    rows, cols = matrix.shape
    cells = VGroup()
    for row in range(rows):
        for col in range(cols):
            square = Square(
                side_length=cell,
                stroke_color=LGREY,
                stroke_width=0.35,
            ).set_fill(_pattern_color(matrix[row, col]), opacity=1.0)
            cells.add(square)
    cells.arrange_in_grid(rows=rows, cols=cols, buff=0.006)
    return cells


def patterned_head(matrix: np.ndarray, *, scale_factor: float = 1.0) -> Group:
    """Overlay a miniature pattern matrix onto the rendered head graphic."""
    head = brain_render(scale_factor=scale_factor)
    cells = _mini_matrix(matrix, cell=_MATRIX_CELL * scale_factor)
    cells.move_to(
        head.get_center()
        + LEFT * (0.035 * head.width)
        + UP * (0.18 * head.height)
    )
    cells.set_z_index(2)
    head.set_z_index(0)
    head.set_opacity(1.0)
    return Group(head, cells)


def framed_visual(
    inner: Mobject,
    *,
    width: float = 1.42,
    height: float = 1.42,
    corner_radius: float = 0.08,
) -> Group:
    """Place a visual inside a rounded card with standard intro padding."""
    card = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
        stroke_color=LGREY,
        stroke_width=1.5,
    ).set_fill(WHITE, opacity=1.0)
    max_inner_width = width - 0.18
    max_inner_height = height - 0.18
    if inner.width > max_inner_width:
        inner.scale_to_fit_width(max_inner_width)
    if inner.height > max_inner_height:
        inner.scale_to_fit_height(max_inner_height)
    inner.move_to(card.get_center())
    return Group(card, inner)


def interpolate_matrix(a: np.ndarray, b: np.ndarray, alpha: float) -> np.ndarray:
    """Linearly interpolate between two pattern matrices."""
    return (1.0 - alpha) * a + alpha * b


# ── Layout builders ───────────────────────────────────────────────────────────

def _build_intro_a_end_state() -> dict[str, Mobject]:
    """Build the final hook layout with the probe-choice question and two images."""
    question = Tex(r"Which probe matches?", color=INK, font_size=44)
    probe_target = _img(stim_path(_HOOK_CODE, 5), 2.40)
    probe_foil = _img(stim_path(_HOOK_CODE, 8), 2.40)
    probes = Group(probe_target, probe_foil).arrange(RIGHT, buff=0.70)
    content = Group(question, probes).arrange(DOWN, buff=0.50)
    content.move_to(ORIGIN)
    return {
        "question": question,
        "probe_target": probe_target,
        "probe_foil": probe_foil,
        "content": content,
    }


def _build_intro_b_layout() -> dict[str, Mobject]:
    """Build the timeline layout comparing sensory input, delay, and reinstatement."""
    def _vertical_dotted_line(height: float, *, color: str, radius: float = 0.020, spacing: float = 0.125) -> VGroup:
        count = max(2, int(height / spacing) + 1)
        dots = VGroup(
            *[Dot(radius=radius, color=color, stroke_width=0) for _ in range(count)]
        ).arrange(DOWN, buff=max(0.02, spacing - 2 * radius))
        dots.set_opacity(0.72)
        dots.move_to(ORIGIN)
        return dots

    image_h = 1.70
    left_image = _img(_INTRO_HOOK_TARGET_FISH, image_h)
    right_image = _img(_INTRO_HOOK_FOIL_FISH, image_h)

    zone_height = image_h
    dead_zone = Rectangle(width=2.50, height=zone_height, stroke_width=0).set_fill(
        LGREY, opacity=0.18
    )
    dead_zone.set_stroke(width=0)

    separator_color = MGREY
    left_cut_line = _vertical_dotted_line(zone_height, color=separator_color)
    right_cut_line = left_cut_line.copy()

    strip_y = 0.90
    gap = 0.28
    separator_width = left_cut_line.width
    delay_width = dead_zone.width
    image_width = left_image.width
    total_width = (2 * image_width) + (2 * separator_width) + delay_width + (4 * gap)
    left_edge = -total_width / 2

    left_image.move_to(
        np.array([left_edge + image_width / 2, strip_y, 0.0])
    )
    left_cut_line.move_to(
        np.array([left_image.get_right()[0] + gap + separator_width / 2, strip_y, 0.0])
    )
    dead_zone.move_to(
        np.array([left_cut_line.get_right()[0] + gap + delay_width / 2, strip_y, 0.0])
    )
    right_cut_line.move_to(
        np.array([dead_zone.get_right()[0] + gap + separator_width / 2, strip_y, 0.0])
    )
    right_image.move_to(
        np.array([right_cut_line.get_right()[0] + gap + image_width / 2, strip_y, 0.0])
    )

    phase_y = strip_y + (zone_height / 2) + 0.46
    left_phase = Tex("sensory input", color=INK, font_size=18)
    center_phase = Tex("working memory maintenance", color=INK, font_size=18)
    right_phase = Tex("sensory input", color=INK, font_size=18)
    for label, anchor in zip((left_phase, center_phase, right_phase), (left_image, dead_zone, right_image)):
        label.move_to(np.array([anchor.get_center()[0], phase_y, 0.0]))

    top_rule_y = phase_y + 0.24
    phase_rule = Arrow(
        [left_image.get_left()[0] - 0.24, top_rule_y, 0.0],
        [right_image.get_right()[0] + 0.24, top_rule_y, 0.0],
        color=LGREY,
        stroke_width=1.0,
        buff=0.0,
        tip_length=0.14,
        max_tip_length_to_length_ratio=0.06,
        max_stroke_width_to_length_ratio=1.8,
    )
    phase_dots = VGroup(
        *[
            Dot(radius=0.030, color=MGREY, stroke_width=0).move_to([x, top_rule_y, 0.0])
            for x in (
                phase_rule.get_left()[0],
                left_cut_line.get_center()[0],
                right_cut_line.get_center()[0],
            )
        ]
    )
    time_label = MathTex("t", color=INK, font_size=24)
    time_label.next_to(phase_rule.get_right(), UP + LEFT, buff=0.10)

    left_brain = patterned_head(_PLOT_SENSORY_PATTERN_LEFT, scale_factor=0.56)
    center_brain = patterned_head(_PLOT_MEMORY_PATTERN, scale_factor=0.56)
    right_brain = patterned_head(_PLOT_SENSORY_PATTERN_RIGHT, scale_factor=0.56)
    for brain, anchor in zip((left_brain, center_brain, right_brain), (left_image, dead_zone, right_image)):
        brain.next_to(anchor, DOWN, buff=0.52)

    brain_row = Group(left_brain, center_brain, right_brain)
    final_group = Group(
        time_label,
        phase_rule,
        phase_dots,
        left_phase,
        center_phase,
        right_phase,
        left_image,
        left_cut_line,
        dead_zone,
        right_cut_line,
        right_image,
        left_brain,
        center_brain,
        right_brain,
    )
    return {
        "time_label": time_label,
        "phase_rule": phase_rule,
        "phase_dots": phase_dots,
        "left_phase": left_phase,
        "center_phase": center_phase,
        "right_phase": right_phase,
        "left_image": left_image,
        "left_cut_line": left_cut_line,
        "dead_zone": dead_zone,
        "right_cut_line": right_cut_line,
        "right_image": right_image,
        "left_brain": left_brain,
        "brain_group": center_brain,
        "right_brain": right_brain,
        "brain_row": brain_row,
        "final_group": final_group,
    }


def _build_intro_c_layout() -> dict[str, Mobject]:
    """Build the LTM-modulation slide linking prior exposure to the WM trace."""
    title = title_block(
        r"\textbf{Long-term memory modulates the maintained trace}",
        r"Prior exposure shapes the WM representation --- without replacing it",
    )
    time_arrow = Arrow(
        [config.frame_width / 2 - 5.80, config.frame_height / 2 - 0.34, 0.0],
        [config.frame_width / 2 - 0.88, config.frame_height / 2 - 0.34, 0.0],
        color=LGREY,
        stroke_width=1.0,
        buff=0.0,
        tip_length=0.14,
        max_tip_length_to_length_ratio=0.06,
        max_stroke_width_to_length_ratio=1.8,
    )
    time_label = MathTex("t", color=INK, font_size=24)
    time_label.next_to(time_arrow.get_right(), UP + LEFT, buff=0.10)
    brain_parts = brain_icon_with_evc(highlight_color=EVC_TAUPE, scale_factor=1.00)
    brain_group = brain_parts["group"]
    brain_group.move_to(RIGHT * 0.80 + DOWN * 0.40)

    wm_trace = _img(stim_path(_HOOK_CODE, _FROZEN_IDX), 0.86)
    wm_trace.move_to(brain_group.get_center() + LEFT * 0.20 + UP * 0.12)
    wm_label = Tex("WM trace", color=AMBER, font_size=17)
    wm_label.next_to(wm_trace, DOWN, buff=0.10)

    fan_anchors = [
        LEFT * 4.60 + DOWN * 0.90,
        LEFT * 4.20 + DOWN * 0.35,
        LEFT * 3.80 + UP * 0.20,
    ]
    prior_cards = Group(
        *[
            _img(stim_path(_HOOK_CODE, _FROZEN_IDX), h).set_opacity(op).move_to(anchor)
            for (h, op), anchor in zip(_PRIOR_SPECS, fan_anchors)
        ]
    )
    prior_header = Tex("prior exposures", color=GREEN, font_size=19)
    prior_header.move_to(LEFT * 4.20 + UP * 1.05)
    prior_sub = Tex("repetition history / familiarity", color=GREEN, font_size=15)
    prior_sub.next_to(prior_cards, DOWN, buff=0.18)

    mod_arrow = CurvedArrow(
        prior_cards[-1].get_right() + RIGHT * 0.08,
        wm_trace.get_left() + LEFT * 0.06,
        angle=-0.40,
        color=GREEN,
        stroke_width=2.0,
    )
    mod_label = Tex("top-down modulation", color=GREEN, font_size=16)
    mod_label.next_to(mod_arrow.get_center(), UP, buff=0.18)

    callout = make_callout(
        r"LTM shapes the trace --- it does not replace it.",
        GREEN,
        font_size=22,
    ).to_edge(DOWN, buff=0.34)

    final_group = Group(
        time_arrow,
        time_label,
        title,
        brain_group,
        wm_trace,
        wm_label,
        prior_cards,
        prior_header,
        prior_sub,
        mod_arrow,
        mod_label,
        callout,
    )
    return {
        "time_arrow": time_arrow,
        "time_label": time_label,
        "title": title,
        "brain_group": brain_group,
        "wm_trace": wm_trace,
        "wm_label": wm_label,
        "prior_cards": prior_cards,
        "prior_header": prior_header,
        "prior_sub": prior_sub,
        "mod_arrow": mod_arrow,
        "mod_label": mod_label,
        "callout": callout,
        "final_group": final_group,
    }


def _build_intro_d_layout() -> dict[str, Mobject]:
    """Build the classical working-memory slide with its historical milestones."""
    title = title_block(
        r"\textbf{Classical view on the neural substrates of working memory}",
    )
    max_col_width = 3.48

    def _classical_column(
        title_text: str,
        claim_lines: tuple[str, ...],
        ref_lines: tuple[str, ...] = (),
        *,
        schematic_kind: str | None = None,
        image_height: float = 1.56,
        image_ref_lines: tuple[str, ...] = (),
    ) -> Group:
        heading = _wrapped_tex(
            rf"\textbf{{{title_text}}}",
            max_width=max_col_width,
            color=AMBER,
            font_size=18,
        )
        centered_parts: list[Mobject] = [heading]
        figure: Mobject | None = None
        image_refs: VGroup | None = None
        refs: VGroup | None = None
        if schematic_kind is not None:
            figure = make_literature_schematic(
                schematic_kind,
                width=max_col_width,
                height=image_height,
                accent=AMBER,
            )
            centered_parts.append(figure)
        if image_ref_lines:
            image_refs = VGroup(
                *[
                    _wrapped_tex(
                        line,
                        max_width=max_col_width,
                        color=INK,
                        font_size=12,
                    )
                    for line in image_ref_lines
                ]
            ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
            centered_parts.append(image_refs)
        claim = VGroup(
            *[
                _wrapped_tex(
                    line,
                    max_width=max_col_width,
                    color=INK,
                    font_size=15,
                )
                for line in claim_lines
            ]
        ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        centered_parts.append(claim)
        if ref_lines:
            refs = VGroup(
                *[
                    _wrapped_tex(
                        line,
                        max_width=max_col_width,
                        color=INK,
                        font_size=12,
                    )
                    for line in ref_lines
                ]
            ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        centered_block = Group(*centered_parts).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        centered_anchor_x = centered_block.get_center()[0]
        for mob in centered_parts:
            mob.set_x(centered_anchor_x)

        column_parts: list[Mobject] = [centered_block]
        if refs is not None:
            refs.next_to(centered_block, DOWN, buff=0.10, aligned_edge=LEFT)
            refs.align_to(claim, LEFT)
            column_parts.append(refs)

        column = Group(*column_parts)
        column.centered_block = centered_block
        column.claim = claim
        column.refs = refs
        return column

    columns = Group(
        _classical_column(
            "Monkey lesion studies",
            (
                "Delayed-response deficits after",
                "prefrontal ablations",
            ),
            ("Jacobsen (1936)",),
        ),
        _classical_column(
            "Sustained activation",
            (
                "Persistent delay-period neural firing in dorsolateral PFC",
            ),
            ("Goldman-Rakic (1995)", r"Constantinidis \& Procyk (2004)"),
            schematic_kind="delay_firing",
            image_height=2.20,
            image_ref_lines=("Funahashi et al. (1989)",),
        ),
        _classical_column(
            "Early human neuroimaging",
            (
                "Early PET and fMRI activations in",
                "frontal and parietal regions",
            ),
            (
                r"D'Esposito et al. (1995)",
                "Doyon et al. (1996)",
                "Courtney et al. (1997)",
            ),
            schematic_kind="activation_map",
            image_height=1.82,
            image_ref_lines=("Jonides et al. (1993)",),
        ),
    )

    dot_xs = (-4.70, 0.0, 4.70)
    timeline_y = title.get_bottom()[1] - 0.72
    timeline_line = Line(
        np.array([dot_xs[0] - 1.20, timeline_y, 0.0]),
        np.array([dot_xs[-1] + 1.20, timeline_y, 0.0]),
        color=LGREY,
        stroke_width=1.5,
    )
    timeline_line.set_opacity(0.78)
    dots = VGroup(
        *[
            Dot(radius=0.055, color=AMBER, stroke_width=0).move_to(np.array([x, timeline_y, 0.0]))
            for x in dot_xs
        ]
    )

    for column, dot in zip(columns, dots):
        column.next_to(dot, DOWN, buff=0.20)
        column.centered_block.set_x(dot.get_x())
        if column.refs is not None:
            column.refs.align_to(column.claim, LEFT)

    content = Group(timeline_line, dots, columns)
    takeaway = _wrapped_tex(
        r"Focus on prefrontal and parietal areas as primary neural substrates of working memory",
        max_width=content.width + 0.15,
        color=INK,
        font_size=22,
    )
    takeaway.next_to(columns, DOWN, buff=0.52)
    takeaway.set_x(content.get_center()[0])
    content_block = Group(content, takeaway)
    content_block.set_y(0.0)
    return {
        "title": title,
        "timeline_line": timeline_line,
        "dots": dots,
        "columns": columns,
        "content": content,
        "takeaway": takeaway,
        "final_group": Group(title, content_block),
    }


def _build_intro_e_layout() -> dict[str, Mobject]:
    """Build the sensory-recruitment slide with evidence and exemplar figures."""
    title = title_block(
        r"\textbf{Sensory recruitment model}",
    )
    sensory_accent = "#18324D"

    def _sensory_text_entry(
        heading_lines: tuple[str, ...],
        body_lines: tuple[str, ...],
        ref_lines: tuple[str, ...],
    ) -> Group:
        heading = VGroup(
            *[
                Tex(line, color=INK, font_size=20, tex_environment="flushleft")
                for line in heading_lines
            ]
        ).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        parts: list[Mobject] = [heading]
        if body_lines:
            body = VGroup(
                *[
                    Tex(line, color=INK, font_size=16, tex_environment="flushleft")
                    for line in body_lines
                ]
            ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
            parts.append(body)
        if ref_lines:
            refs = VGroup(
                *[
                    Tex(line, color=INK, font_size=13, tex_environment="flushleft")
                    for line in ref_lines
                ]
            ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
            parts.append(refs)
        return Group(*parts).arrange(DOWN, buff=0.10, aligned_edge=LEFT)

    def _study_figure(
        schematic_kind: str,
        ref_text: str | None,
        *,
        width: float = 2.44,
        height: float = 2.24,
    ) -> Group:
        image = make_literature_schematic(
            schematic_kind,
            width=width,
            height=height,
            accent=sensory_accent,
        )
        if ref_text is None:
            return Group(image)
        refs = Tex(ref_text, color=INK, font_size=12)
        if refs.width > image.width + 0.16:
            refs.scale_to_fit_width(image.width + 0.16)
        return Group(image, refs).arrange(DOWN, buff=0.10)

    what_it_does = _sensory_text_entry(
        (
            r"Sensory areas support",
            r"working memory",
        ),
        (),
        (
            r"Awh \& Jonides (2001); Postle (2006)",
        ),
    )
    evidence_source = _sensory_text_entry(
        (
            r"MVPA decodes stimulus-specific",
            r"information during the delay",
        ),
        (),
        (
            r"Harrison \& Tong (2009); Serences et al. (2009)",
        ),
    )
    distributed_function = _sensory_text_entry(
        (
            r"Working memory is distributed",
            r"across cortex",
        ),
        (),
        (
            r"Christophel et al. (2017)",
        ),
    )
    entries = Group(what_it_does, evidence_source, distributed_function).arrange(
        DOWN,
        buff=0.92,
        aligned_edge=LEFT,
    )
    dot_anchor_ys = [
        Group(entry[0], entry[1]).get_center()[1] + 0.16
        for entry in entries
    ]
    timeline_x = entries.get_left()[0] - 0.88
    dots = VGroup(
        *[
            Dot(radius=0.055, color=sensory_accent, stroke_width=0).move_to(
                np.array([timeline_x, dot_y, 0.0])
            )
            for dot_y in dot_anchor_ys
        ]
    )
    hero_figure = Group()
    top_row = Group(
        _study_figure(
            "orientation_decoder",
            None,
            width=2.32,
            height=2.10,
        ),
        _study_figure(
            "activation_map",
            None,
            width=2.32,
            height=2.10,
        ),
    ).arrange(RIGHT, buff=0.20, aligned_edge=UP)
    top_row_ref = Tex(r"Harrison \& Tong (2009)", color=INK, font_size=12)
    top_row_ref.next_to(top_row, DOWN, buff=0.10)
    top_row_ref.set_x(top_row.get_center()[0])
    bottom_row = Group(
        _study_figure(
            "distributed_map",
            r"Christophel et al. (2017)",
            width=4.84,
            height=2.18,
        ),
    )
    bottom_row.next_to(top_row_ref, DOWN, buff=0.42)
    bottom_row.set_x(top_row.get_center()[0])
    figure_column = Group(top_row, top_row_ref, bottom_row)
    figure_column.next_to(entries, RIGHT, buff=1.02, aligned_edge=UP)
    figure_column.set_y(entries.get_center()[1])
    left_column_shift = LEFT * 0.34
    dots.shift(left_column_shift)
    entries.shift(left_column_shift)

    content = Group(dots, entries, figure_column)
    content.next_to(title, DOWN, buff=0.34)
    content.set_x(-0.26)
    dot_mid_y = 0.5 * (dots[0].get_center()[1] + dots[-1].get_center()[1])
    content.shift(DOWN * dot_mid_y)
    return {
        "title": title,
        "hero_figure": hero_figure,
        "dots": dots,
        "entries": entries,
        "figure_column": figure_column,
        "content": content,
        "final_group": Group(title, hero_figure, content),
    }


_INTRO_RESEARCH_QUESTIONS: tuple[dict[str, str], ...] = (
    {
        "kicker": "Research question 1",
        "title": "",
        "subtitle": "Are working memory representations sensory-like?",
        "header_left_x": -5.00,
        "header_right_x": config.frame_width / 2 - 0.42,
        "format_sensory_title": "Sensory-like",
        "format_sensory_1": "Efficient",
        "format_sensory_2": "High-fidelity",
        "format_sensory_2_refs": r"(Pasternak \& Greenlee, 2005; Serences, 2016)",
        "format_sensory_3": "Evidence of cross-decoding",
        "format_sensory_3_refs": r"(Harrison \& Tong, 2009; Albers et al., 2013; Rademaker et al., 2019; Iamshchinina et al., 2021; Vo et al., 2022)",
        "format_memory_title": "Memory-specific",
        "format_memory_1": "Avoid interference",
        "format_memory_1_refs": r"(Bettencourt \& Xu, 2016; Libby \& Buschman, 2021)",
        "format_memory_2": "Evidence of separate formats",
        "format_memory_2_refs": r"(Duan \& Curtis, 2024)",
        "format_memory_3": "Dynamic codes",
        "format_memory_3_refs": r"(Buschman \& Miller, 2022; Deguits et al., 2025)",
        "bullet_1": r"Overlapping neural populations could enable \textbf{efficient and high-fidelity} feature storage.",
        "bullet_1_refs": r"(Pasternak \& Greenlee, 2005; Serences, 2016)",
        "bullet_2": r"Some evidence of \textbf{cross-decoding} suggests shared sensory codes.",
        "bullet_2_refs": r"(Harrison \& Tong, 2009; Albers et al., 2013; Rademaker et al., 2019; Iamshchinina et al., 2021; Vo et al., 2022)",
        "bullet_3": r"Recent work reports no sensory-to-memory generalization and \textbf{dynamic codes} during working memory maintenance.",
        "bullet_3_refs": r"(Buschman \& Miller, 2022; Duan and Curtis, 2024; Deguits et al., 2025)",
        "bullet_4": r"\textbf{Memory-specific} code may limit interference with sensory processing.",
        "bullet_4_refs": r"(Bettencourt \& Xu, 2016; Libby \& Buschman, 2021)",
        "accent": RQ_BLUE,
    },
    {
        "kicker": "Research question 2",
        "title": "",
        "subtitle": r"Does sensory recruitment generalize to naturalistic WM?",
        "header_left_x": -5.00,
        "header_right_x": config.frame_width / 2 - 0.42,
        "bullet_1": "Commonly used WM stimuli are simple.",
        "bullet_2": "Real-world settings are perceptually and semantically rich.",
        "bullet_3": "Stimulus type and task demands may shape cross-decoding.",
        "bullet_3_refs": r"(Duan \& Curtis, 2024) (Serences, 2016; Christophel et al., 2017)",
        "accent": RQ_RED,
    },
    {
        "kicker": "Research question 3",
        "title": "Long-term memory interaction",
        "subtitle": r"Do pre-existing long-term memory representations\\affect how the early visual cortex represents\\working memory content?",
        "header_left_x": -5.00,
        "header_right_x": config.frame_width / 2 - 0.42,
        "bullet_1": "WM and LTM are often studied in isolation, despite continuous interaction.",
        "bullet_1_refs": r"(Schurgin, 2018; Singer, 2021)",
        "bullet_2": "Familiarity and meaning improve working-memory performance.",
        "bullet_2_refs": r"(Xie \& Zhang, 2018; Ngiam et al., 2019; Brady \& St{\"o}rmer, 2022)",
        "bullet_3": r"Shared format?",
        "bullet_3_refs": r"(Vo et al., 2022)",
        "accent": RQ_GREEN,
    },
)


def _intro_question_context_block(spec: dict[str, str]) -> VGroup:
    """Build the left-column bullet list and citations for one research question."""
    bullet_indices: list[int] = []
    bullet_idx = 1
    while f"bullet_{bullet_idx}" in spec:
        bullet_indices.append(bullet_idx)
        bullet_idx += 1

    cue_lines = VGroup(
        *[
            _wrapped_tex(
                spec[f"bullet_{idx}"],
                max_width=5.55,
                color=INK,
                font_size=_INTRO_QUESTION_BULLET_FONT_SIZE,
            )
            for idx in bullet_indices
        ]
    )
    for line in cue_lines[1:]:
        line.align_to(cue_lines[0], LEFT)

    bullet_items = VGroup()
    for idx, line in zip(bullet_indices, cue_lines):
        refs_key = f"bullet_{idx}_refs"
        refs_text = spec.get(refs_key)
        if refs_text:
            refs = _wrapped_tex(
                refs_text,
                max_width=5.35,
                color=INK,
                font_size=13,
            )
            item = VGroup(line, refs).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        else:
            item = VGroup(line)
        bullet_items.add(item)

    bullet_items.arrange(DOWN, buff=_INTRO_QUESTION_BULLET_GAP, aligned_edge=LEFT)
    for item in bullet_items[1:]:
        item.align_to(bullet_items[0], LEFT)

    cue_dots = VGroup(
        *[
            Dot(radius=0.028, color=spec["accent"], stroke_width=0)
            for _ in cue_lines
        ]
    )
    cue_dots.next_to(bullet_items, LEFT, buff=0.24)
    cue_dots.set_y(bullet_items.get_center()[1])
    dots_x = cue_dots.get_x()
    for dot, line in zip(cue_dots, cue_lines):
        dot.set_x(dots_x)
        dot.set_y(line.get_center()[1])
    return VGroup(cue_dots, bullet_items)


def _intro_question_matrix(
    matrix: np.ndarray,
    *,
    cell: float = 0.13,
    scale_factor: float = 1.28,
    target_width: float | None = None,
) -> VGroup:
    """Build a scaled matrix visual used in the research-question slides."""
    cells = _mini_matrix(matrix, cell=cell)
    cells.scale(scale_factor)
    if target_width is not None:
        cells.scale_to_fit_width(target_width)
    cells.set_opacity(0.95)
    return cells


def _intro_question_visual_chip(
    image_path: str,
    label_text: str,
    *,
    image_opacity: float = 1.0,
    hide_label: bool = False,
) -> Group:
    """Build a compact image-plus-label chip for question visuals."""
    image = ImageMobject(image_path)
    image.scale_to_fit_width(0.82)
    image.set_opacity(image_opacity)

    label = Tex(label_text, color=INK, font_size=15)
    if label.width > 1.90:
        label.scale_to_fit_width(1.90)
    if hide_label:
        label = Rectangle(width=0.01, height=label.height).set_stroke(width=0, opacity=0).set_fill(
            opacity=0
        )
    return Group(image, label).arrange(DOWN, buff=0.10)


def _intro_question_image_card(
    image_path: str,
    *,
    width: float,
    height: float,
    image_opacity: float = 1.0,
) -> Group:
    """Build a framed image card for one research-question example."""
    image = ImageMobject(image_path)
    image.set_opacity(image_opacity)
    return framed_visual(image, width=width, height=height, corner_radius=0.06)


def _intro_question_image_with_ref(
    image_path: str,
    ref_text: str,
    *,
    width: float,
    height: float,
) -> Group:
    """Build an image card with a citation line underneath."""
    card = _intro_question_image_card(image_path, width=width, height=height)
    ref = Tex(ref_text, color=INK, font_size=10)
    if ref.width > width + 0.22:
        ref.scale_to_fit_width(width + 0.22)
    return Group(card, ref).arrange(DOWN, buff=0.10)


def _intro_question_schematic_with_ref(
    schematic_kind: str,
    ref_text: str,
    *,
    width: float,
    height: float,
) -> Group:
    """Build a rights-safe schematic card with a citation line underneath."""
    card = make_literature_schematic(
        schematic_kind,
        width=width,
        height=height,
        accent=RQ_RED,
    )
    ref = Tex(ref_text, color=INK, font_size=10)
    if ref.width > width + 0.22:
        ref.scale_to_fit_width(width + 0.22)
    return Group(card, ref).arrange(DOWN, buff=0.10)


def _build_intro_question_visual_format(spec: dict[str, str]) -> Group:
    """Build the visual for the first question about representational format."""
    def _explanation_block(
        title_text: str,
        items: tuple[tuple[str, str | None], ...],
    ) -> VGroup:
        title = _wrapped_tex(
            rf"\textbf{{{title_text}}}",
            max_width=3.12,
            color=INK,
            font_size=20,
        )
        item_groups = VGroup()
        for line_text, refs_text in items:
            bullet = Dot(radius=0.022, color=spec["accent"], stroke_width=0)
            line = _wrapped_tex(
                line_text,
                max_width=2.90,
                color=INK,
                font_size=17,
            )
            bullet_line = VGroup(bullet, line).arrange(RIGHT, buff=0.12, aligned_edge=UP)
            if refs_text:
                refs = _wrapped_tex(
                    refs_text,
                    max_width=2.82,
                    color=INK,
                    font_size=11.5,
                )
                refs.next_to(bullet_line, DOWN, buff=0.04, aligned_edge=LEFT)
                refs.align_to(line, LEFT)
                item = VGroup(bullet_line, refs).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
            else:
                item = VGroup(bullet_line)
            item_groups.add(item)

        item_groups.arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        return VGroup(title, item_groups).arrange(DOWN, buff=0.16, aligned_edge=LEFT)

    chip_width = 0.82
    source_matrix = _intro_question_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT, target_width=chip_width)
    sensory_like_matrix = _intro_question_matrix(_REPRESENTATION_SENSORY_PATTERN_RIGHT, target_width=chip_width)
    memory_specific_matrix = _intro_question_matrix(_REPRESENTATION_MEMORY_PATTERN, target_width=chip_width)

    source_pair = Group(
        _intro_question_visual_chip(
            _INTRO_HOOK_QUESTION_NORMAL_FISH,
            "Sensory",
            hide_label=True,
        ),
        source_matrix,
    ).arrange(DOWN, buff=0.18)
    source_side_label = Tex(r"\textbf{Sensory}", color=INK, font_size=20)
    source_side_label.next_to(source_pair, LEFT, buff=0.18)
    source_side_label.set_y(source_pair.get_center()[1])
    left_column = Group(source_side_label, source_pair)
    top_target = Group(
        _intro_question_visual_chip(
            _INTRO_HOOK_QUESTION_FISH,
            "sensory-like",
            image_opacity=0.94,
            hide_label=True,
        ),
        sensory_like_matrix,
    ).arrange(DOWN, buff=0.18)
    bottom_target = Group(
        _intro_question_visual_chip(
            _INTRO_HOOK_QUESTION_MEMORY_FISH,
            "memory-specific",
            image_opacity=0.46,
            hide_label=True,
        ),
        memory_specific_matrix,
    ).arrange(DOWN, buff=0.18)

    right_stack_gap = 0.46
    max_target_height = max(top_target.height, bottom_target.height)
    target_center_offset = 0.5 * (max_target_height + right_stack_gap)
    right_stack_x = (
        left_column.get_right()[0]
        + 0.84
        + 0.5 * max(top_target.width, bottom_target.width)
    )
    top_target.set_x(right_stack_x)
    bottom_target.set_x(right_stack_x)
    top_target.set_y(left_column.get_y() + target_center_offset)
    bottom_target.set_y(left_column.get_y() - target_center_offset)

    right_stack = Group(top_target, bottom_target)

    columns = Group(left_column, right_stack)

    source_image = source_pair[0][0]
    top_image = top_target[0][0]
    bottom_image = bottom_target[0][0]
    source_lane_y = 0.5 * (source_image.get_bottom()[1] + source_pair[1].get_top()[1])
    top_lane_y = 0.5 * (top_image.get_bottom()[1] + top_target[1].get_top()[1])
    bottom_lane_y = 0.5 * (bottom_image.get_bottom()[1] + bottom_target[1].get_top()[1])

    branch_origin = np.array([source_image.get_right()[0] + 0.10, source_lane_y, 0.0])
    target_x = min(top_image.get_left()[0], bottom_image.get_left()[0]) - 0.14
    trunk_x = branch_origin[0] + 0.46 * (target_x - branch_origin[0])
    trunk_top_y = top_lane_y
    trunk_bottom_y = bottom_lane_y

    lead_out = Line(
        branch_origin,
        np.array([trunk_x, branch_origin[1], 0.0]),
        color=spec["accent"],
        stroke_width=1.2,
    )
    top_trunk = Line(
        np.array([trunk_x, branch_origin[1], 0.0]),
        np.array([trunk_x, trunk_top_y, 0.0]),
        color=spec["accent"],
        stroke_width=1.2,
    )
    bottom_trunk = Line(
        np.array([trunk_x, branch_origin[1], 0.0]),
        np.array([trunk_x, trunk_bottom_y, 0.0]),
        color=spec["accent"],
        stroke_width=1.2,
    )
    top_branch = Line(
        np.array([trunk_x, trunk_top_y, 0.0]),
        np.array([target_x, trunk_top_y, 0.0]),
        color=spec["accent"],
        stroke_width=1.2,
    )
    bottom_branch = Line(
        np.array([trunk_x, trunk_bottom_y, 0.0]),
        np.array([target_x, trunk_bottom_y, 0.0]),
        color=spec["accent"],
        stroke_width=1.2,
    )
    branch = VGroup(lead_out, top_trunk, bottom_trunk, top_branch, bottom_branch).set_stroke(opacity=0.82)
    main_visual = Group(columns, branch)
    main_visual.shift(LEFT * 0.92)

    top_block = _explanation_block(
        spec["format_sensory_title"],
        (
            (spec["format_sensory_1"], None),
            (spec["format_sensory_2"], spec["format_sensory_2_refs"]),
            (spec["format_sensory_3"], spec["format_sensory_3_refs"]),
        ),
    )
    bottom_block = _explanation_block(
        spec["format_memory_title"],
        (
            (spec["format_memory_1"], spec["format_memory_1_refs"]),
            (spec["format_memory_2"], spec["format_memory_2_refs"]),
            (spec["format_memory_3"], spec["format_memory_3_refs"]),
        ),
    )

    text_left_x = max(top_target.get_right()[0], bottom_target.get_right()[0]) + 1.00
    for block, lane_y in ((top_block, top_lane_y), (bottom_block, bottom_lane_y)):
        block.set_x(text_left_x + 0.5 * block.width)
        block.set_y(lane_y)

    arrow_color = spec["accent"]
    top_arrow = Arrow(
        np.array([top_image.get_right()[0] + 0.16, trunk_top_y, 0.0]),
        np.array([top_block.get_left()[0] - 0.16, trunk_top_y, 0.0]),
        buff=0.0,
        stroke_width=1.5,
        tip_length=0.12,
        max_stroke_width_to_length_ratio=6.0,
        color=arrow_color,
    )
    bottom_arrow = Arrow(
        np.array([bottom_image.get_right()[0] + 0.16, trunk_bottom_y, 0.0]),
        np.array([bottom_block.get_left()[0] - 0.16, trunk_bottom_y, 0.0]),
        buff=0.0,
        stroke_width=1.5,
        tip_length=0.12,
        max_stroke_width_to_length_ratio=6.0,
        color=arrow_color,
    )
    for arrow in (top_arrow, bottom_arrow):
        arrow.set_stroke(opacity=0.86)

    root = Group(main_visual, top_arrow, bottom_arrow, top_block, bottom_block)
    root.main_visual = main_visual
    root.top_arrow = top_arrow
    root.bottom_arrow = bottom_arrow
    root.top_block = top_block
    root.bottom_block = bottom_block
    root.left_column = left_column
    root.top_target = top_target
    root.bottom_target = bottom_target
    root.lead_out = lead_out
    root.top_trunk = top_trunk
    root.bottom_trunk = bottom_trunk
    root.top_branch = top_branch
    root.bottom_branch = bottom_branch
    return root


def _build_intro_question_visual_ecology(spec: dict[str, str]) -> Group:
    """Build the visual for the second question spanning simple to naturalistic stimuli."""
    def _row_header(text: str, *, font_size: float = 15) -> Tex:
        return Tex(text, color=INK, font_size=font_size)

    simple_cards = Group(
        *[
            _intro_question_schematic_with_ref(kind, ref, width=0.96, height=0.78)
            for kind, ref in _INTRO_RQ2_SIMPLE_STIMULI
        ]
    ).arrange(RIGHT, buff=0.12)
    simple_block = Group(simple_cards)

    intermediate_cards = Group(
        *[
            _intro_question_schematic_with_ref(kind, ref, width=1.10, height=0.90)
            for kind, ref in _INTRO_RQ2_INTERMEDIATE_STIMULI
        ]
    ).arrange(RIGHT, buff=0.18)
    intermediate_block = Group(intermediate_cards)

    natural_cards = Group(
        *[
            _intro_question_image_card(path, width=1.18, height=1.02)
            for path in _INTRO_RQ2_NATURALISTIC_STIMULI
        ]
    ).arrange(RIGHT, buff=0.16)
    natural_ref = Tex(r"Pettini et al. (2025)", color=INK, font_size=10)
    if natural_ref.width > natural_cards.width:
        natural_ref.scale_to_fit_width(natural_cards.width)
    natural_block = Group(natural_cards, natural_ref).arrange(DOWN, buff=0.12)

    rows = Group(simple_block, intermediate_block, natural_block).arrange(DOWN, buff=0.26)
    rows.simple_block = simple_block
    rows.bridge_block = intermediate_block
    rows.natural_block = natural_block
    return rows


def _build_intro_question_visual_ltm(spec: dict[str, str]) -> VGroup:
    """Build the visual for the third question about long-term-memory influences."""
    def _mushroom_icon(cap_color: str, spot_color: str) -> Group:
        cap = Circle(radius=0.34)
        cap.stretch(1.35, 0)
        cap.set_fill(cap_color, opacity=1.0)
        cap.set_stroke(INK, width=1.0, opacity=0.55)
        cap.shift(UP * 0.10)
        stem = RoundedRectangle(
            width=0.22,
            height=0.42,
            corner_radius=0.06,
            stroke_color=INK,
            stroke_width=0.9,
        ).set_fill("#F4E6C8", opacity=1.0)
        stem.next_to(cap.get_center(), DOWN, buff=-0.16)
        spots = VGroup(
            Dot(cap.get_center() + LEFT * 0.18 + UP * 0.09, radius=0.035),
            Dot(cap.get_center() + RIGHT * 0.05 + UP * 0.17, radius=0.028),
            Dot(cap.get_center() + RIGHT * 0.22 + UP * 0.05, radius=0.024),
        )
        spots.set_fill(spot_color, opacity=0.86)
        spots.set_stroke(width=0)
        return Group(stem, cap, spots)

    def _build_top_block() -> Group:
        fish_a = ImageMobject(_INTRO_HOOK_TARGET_FISH)
        fish_a.scale_to_fit_height(0.80)
        fish_b = ImageMobject(_INTRO_HOOK_FOIL_FISH)
        fish_b.scale_to_fit_height(0.80)
        fish_row = Group(fish_a, fish_b).arrange(RIGHT, buff=0.16)

        left_mushroom = _mushroom_icon("#D99A3A", "#FFF7D6")
        right_mushroom = _mushroom_icon("#C85445", "#F8E1D8")
        mushroom_row = Group(left_mushroom, right_mushroom).arrange(RIGHT, buff=0.16)
        mushroom_row.scale_to_fit_width(fish_row.width)

        left_label = Tex(r"edible", color=INK, font_size=_INTRO_QUESTION_BULLET_FONT_SIZE)
        right_label = Tex(r"poisonous", color=INK, font_size=_INTRO_QUESTION_BULLET_FONT_SIZE)
        left_label.move_to(np.array([left_mushroom.get_center()[0], left_mushroom.get_top()[1] + 0.08 + left_label.height / 2, 0.0]))
        right_label.move_to(np.array([right_mushroom.get_center()[0], right_mushroom.get_top()[1] + 0.08 + right_label.height / 2, 0.0]))
        mushroom_labels = Group(left_label, right_label)

        mushroom_credit = Tex(
            r"\textit{Dr.\ Rita L{\"u}der / BLV Verlag}",
            color=INK,
            font_size=12,
        )
        if mushroom_credit.width > mushroom_row.width:
            mushroom_credit.scale_to_fit_width(mushroom_row.width)
        mushroom_credit.set_x(mushroom_row.get_center()[0])
        mushroom_block = Group(mushroom_labels, mushroom_row, mushroom_credit).arrange(
            DOWN,
            buff=0.10,
            aligned_edge=LEFT,
        )
        mushroom_labels.set_x(mushroom_row.get_center()[0])
        mushroom_credit.set_x(mushroom_row.get_center()[0])

        return Group(fish_row, mushroom_block).arrange(DOWN, buff=0.26)

    def _matrix_with_label(matrix: np.ndarray, label_text: str) -> Group:
        matrix_mob = _intro_question_matrix(matrix, cell=0.13, scale_factor=1.10)
        label = Tex(label_text, color=INK, font_size=13.5)
        label.next_to(matrix_mob, UP, buff=0.10)
        label.set_x(matrix_mob.get_center()[0])
        return Group(label, matrix_mob)

    def _realign_matrix_group(group: Group) -> None:
        label, matrix_mob = group
        label.next_to(matrix_mob, UP, buff=0.10)
        label.set_x(matrix_mob.get_center()[0])

    top_block_intro = _build_top_block()
    top_block_final = _build_top_block()

    sensory_like_matrix = interpolate_matrix(
        _REPRESENTATION_MEMORY_PATTERN,
        _REPRESENTATION_SENSORY_PATTERN_RIGHT,
        0.72,
    )
    less_sensory_like_matrix = interpolate_matrix(
        _REPRESENTATION_MEMORY_PATTERN,
        _REPRESENTATION_SENSORY_PATTERN_RIGHT,
        0.18,
    )

    sensory_group = _matrix_with_label(_REPRESENTATION_SENSORY_PATTERN_RIGHT, "sensory pattern")
    memory_group = _matrix_with_label(_REPRESENTATION_MEMORY_PATTERN, "memory pattern")
    plus_group = _matrix_with_label(sensory_like_matrix, "+ sensory-like")
    minus_group = _matrix_with_label(less_sensory_like_matrix, "- sensory-like")

    left_column = Group(sensory_group, memory_group).arrange(
        DOWN,
        buff=0.34,
        aligned_edge=LEFT,
    )
    right_column = Group(plus_group, minus_group).arrange(
        DOWN,
        buff=0.34,
        aligned_edge=LEFT,
    )
    right_column.next_to(left_column, RIGHT, buff=0.70, aligned_edge=UP)

    # Align actual matrix centers by row/column so the branch geometry stays clean
    # even when labels have different widths.
    memory_group[1].set_x(sensory_group[1].get_x())
    plus_group[1].set_x(max(plus_group[1].get_x(), minus_group[1].get_x()))
    minus_group[1].set_x(plus_group[1].get_x())
    plus_group[1].set_y(sensory_group[1].get_y())
    minus_group[1].set_y(memory_group[1].get_y())
    for group in (sensory_group, memory_group, plus_group, minus_group):
        _realign_matrix_group(group)

    source_matrix = memory_group[1]
    top_target_matrix = plus_group[1]
    bottom_target_matrix = minus_group[1]
    source_point = source_matrix.get_right() + RIGHT * 0.08
    target_x = min(top_target_matrix.get_left()[0], bottom_target_matrix.get_left()[0]) - 0.14
    trunk_x = source_point[0] + 0.46 * (target_x - source_point[0])
    top_y = top_target_matrix.get_center()[1]
    bottom_y = bottom_target_matrix.get_center()[1]

    branch_lead = Line(
        source_point,
        np.array([trunk_x, source_point[1], 0.0]),
        color=spec["accent"],
        stroke_width=1.5,
    )
    branch_trunk = Line(
        np.array([trunk_x, top_y, 0.0]),
        np.array([trunk_x, bottom_y, 0.0]),
        color=spec["accent"],
        stroke_width=1.5,
    )
    top_branch = Arrow(
        np.array([trunk_x, top_y, 0.0]),
        np.array([target_x, top_y, 0.0]),
        buff=0.0,
        stroke_width=1.5,
        tip_length=0.11,
        max_stroke_width_to_length_ratio=6.0,
        color=spec["accent"],
    )
    bottom_branch = Arrow(
        np.array([trunk_x, bottom_y, 0.0]),
        np.array([target_x, bottom_y, 0.0]),
        buff=0.0,
        stroke_width=1.5,
        tip_length=0.11,
        max_stroke_width_to_length_ratio=6.0,
        color=spec["accent"],
    )
    for connector in (branch_lead, branch_trunk, top_branch, bottom_branch):
        connector.set_stroke(opacity=0.82)

    matrix_block = Group(
        left_column,
        right_column,
        branch_lead,
        branch_trunk,
        top_branch,
        bottom_branch,
    )

    matrix_block.next_to(top_block_final, DOWN, buff=0.30)

    top_shift = 0.5 * (matrix_block.height + 0.24)
    top_block_final.move_to(UP * top_shift)
    matrix_block.next_to(top_block_final, DOWN, buff=0.30)
    matrix_block.set_x(top_block_final.get_center()[0])
    top_block_intro.move_to(top_block_final)

    root = Group(top_block_intro, top_block_final, matrix_block)
    root.top_block_intro = top_block_intro
    root.top_block_final = top_block_final
    root.matrix_block = matrix_block
    return root


def _build_intro_question_visual(question_idx: int, spec: dict[str, str]) -> VGroup:
    """Dispatch to the question-specific visual builder for the given index."""
    if question_idx == 0:
        return _build_intro_question_visual_format(spec)
    if question_idx == 1:
        return _build_intro_question_visual_ecology(spec)
    return _build_intro_question_visual_ltm(spec)


def _build_intro_question_layout(question_idx: int) -> dict[str, Mobject]:
    """Assemble the full header, bullets, and visual layout for one question slide."""
    spec = _INTRO_RESEARCH_QUESTIONS[question_idx]
    header_y = _INTRO_QUESTION_HEADER_Y
    is_rq1 = question_idx == 0
    question_in_header = question_idx in (0, 1)
    kicker = Tex(spec["kicker"], color=INK, font_size=_INTRO_QUESTION_HEADER_FONT_SIZE)
    kicker.set_y(header_y)

    header_separator = Line(ORIGIN, RIGHT * 0.54, color=spec["accent"], stroke_width=1.8)
    header_separator.next_to(kicker, RIGHT, buff=0.22)
    header_separator.set_y(header_y)

    header_title_text = spec["subtitle"] if question_in_header else spec["title"]
    header_title = Tex(_bold_tex(header_title_text), color=INK, font_size=_INTRO_QUESTION_HEADER_FONT_SIZE)
    header_title.next_to(header_separator, RIGHT, buff=0.22)
    header_title.set_y(header_y)
    header_text_group = VGroup(kicker, header_separator, header_title)
    header_rule_extension = 0.18
    header_rule_half_width = 0.5 * header_text_group.width + header_rule_extension
    header_title_rule = Line(
        LEFT * header_rule_half_width,
        RIGHT * header_rule_half_width,
        color=spec["accent"],
        stroke_width=1.8,
    )
    header_title_rule.next_to(header_text_group, DOWN, buff=0.12)
    header_title_rule.set_x(header_text_group.get_center()[0])
    header_title_rule.set_opacity(0.82)

    frame_half_width = config.frame_width / 2
    row_half_width = header_rule_half_width
    row_padding = 0.28
    min_row_center_x = -frame_half_width + row_padding + row_half_width
    max_row_center_x = frame_half_width - row_padding - row_half_width
    header_text_group.set_x(np.clip(0.0, min_row_center_x, max_row_center_x))
    header_title_rule.set_x(header_text_group.get_center()[0])

    header = VGroup(header_text_group, header_title_rule)

    if is_rq1:
        question_claim = VGroup()
        cue_dots = VGroup()
        bullet_items = VGroup()
        visual = _build_intro_question_visual(question_idx, spec)
        visual.scale(0.98)
        visual.move_to(ORIGIN)
        question_card = Group(visual)
        return {
            "header": header,
            "question_claim": question_claim,
            "cue_dots": cue_dots,
            "bullet_items": bullet_items,
            "visual": visual,
            "question_card_without_rule": Group(visual),
            "question_card": question_card,
            "content": question_card,
            "final_group": Group(header, question_card),
            "visual_left_column": getattr(visual, "left_column", None),
            "visual_top_target": getattr(visual, "top_target", None),
            "visual_bottom_target": getattr(visual, "bottom_target", None),
            "visual_lead_out": getattr(visual, "lead_out", None),
            "visual_top_trunk": getattr(visual, "top_trunk", None),
            "visual_bottom_trunk": getattr(visual, "bottom_trunk", None),
            "visual_top_branch": getattr(visual, "top_branch", None),
            "visual_bottom_branch": getattr(visual, "bottom_branch", None),
            "visual_simple_block": getattr(visual, "simple_block", None),
            "visual_bridge_block": getattr(visual, "bridge_block", None),
            "visual_natural_block": getattr(visual, "natural_block", None),
            "visual_top_block_intro": getattr(visual, "top_block_intro", None),
            "visual_top_block_final": getattr(visual, "top_block_final", None),
            "visual_matrix_block": getattr(visual, "matrix_block", None),
        }

    context_block = _intro_question_context_block(spec)
    cue_dots = context_block[0]
    bullet_items = context_block[1]
    if question_idx == 2:
        question_claim = VGroup()
        visual = _build_intro_question_visual(question_idx, spec)
        visual.scale(1.07)

        visual_top_block_intro = getattr(visual, "top_block_intro")
        visual_top_block_final = getattr(visual, "top_block_final")
        visual_matrix_block = getattr(visual, "matrix_block")
        matrix_center_x = header.get_center()[0]

        visual_top_block_intro.move_to(np.array([2.35, 1.32, 0.0]))
        visual_top_block_final.move_to(visual_top_block_intro)
        visual_matrix_block.next_to(visual_top_block_intro, DOWN, buff=0.36)
        visual_matrix_block.set_x(matrix_center_x)

        top_bullets = VGroup(bullet_items[0], bullet_items[1]).arrange(
            DOWN,
            buff=_INTRO_QUESTION_BULLET_GAP,
            aligned_edge=LEFT,
        )
        top_dots = VGroup(cue_dots[0], cue_dots[1])
        top_dots.next_to(top_bullets, LEFT, buff=0.24)
        dots_x = top_dots.get_x()
        for dot, item in zip(top_dots, top_bullets):
            dot.set_x(dots_x)
            dot.set_y(item[0].get_center()[1])

        top_block = VGroup(top_dots, top_bullets)
        top_block.next_to(visual_top_block_intro, LEFT, buff=1.00, aligned_edge=UP)
        top_block.shift(DOWN * 0.04)

        third_item = bullet_items[2]
        third_dot = cue_dots[2]
        if len(third_item) > 1:
            third_item[1].scale(1.18)
            third_item.arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        third_dot.next_to(third_item, LEFT, buff=0.24)
        third_dot.set_y(third_item[0].get_center()[1])
        third_block = VGroup(third_dot, third_item)
        third_block.next_to(visual_matrix_block, DOWN, buff=0.22)
        third_block.set_x(matrix_center_x)

        question_card = Group(top_block, visual_top_block_intro, visual_matrix_block, third_block)
        question_card.set_x(0.0)
        question_card.next_to(header, DOWN, buff=0.55)
        visual_matrix_block.set_x(matrix_center_x)
        third_block.set_x(matrix_center_x)
        return {
            "header": header,
            "question_claim": question_claim,
            "cue_dots": cue_dots,
            "bullet_items": bullet_items,
            "visual": visual,
            "question_card_without_rule": question_card,
            "question_card": question_card,
            "content": question_card,
            "final_group": Group(header, question_card),
            "visual_left_column": getattr(visual, "left_column", None),
            "visual_top_target": getattr(visual, "top_target", None),
            "visual_bottom_target": getattr(visual, "bottom_target", None),
            "visual_lead_out": getattr(visual, "lead_out", None),
            "visual_top_trunk": getattr(visual, "top_trunk", None),
            "visual_bottom_trunk": getattr(visual, "bottom_trunk", None),
            "visual_top_branch": getattr(visual, "top_branch", None),
            "visual_bottom_branch": getattr(visual, "bottom_branch", None),
            "visual_simple_block": getattr(visual, "simple_block", None),
            "visual_bridge_block": getattr(visual, "bridge_block", None),
            "visual_natural_block": getattr(visual, "natural_block", None),
            "visual_top_block_intro": visual_top_block_intro,
            "visual_top_block_final": visual_top_block_final,
            "visual_matrix_block": visual_matrix_block,
        }
    show_question_claim = (not question_in_header) and question_idx != 2
    if question_in_header:
        question_claim = VGroup()
        text_column = context_block
    elif show_question_claim:
        question_claim = Tex(
            spec["subtitle"],
            color=INK,
            font_size=_INTRO_QUESTION_CLAIM_FONT_SIZE,
            tex_environment="flushleft",
        )
        if question_claim.width > _INTRO_QUESTION_CLAIM_MAX_WIDTH:
            question_claim.scale_to_fit_width(_INTRO_QUESTION_CLAIM_MAX_WIDTH)
        context_block.next_to(question_claim, DOWN, buff=0.28)
        question_claim.align_to(bullet_items, LEFT)
        text_column = Group(question_claim, context_block)
    else:
        question_claim = VGroup()
        text_column = context_block
    visual = _build_intro_question_visual(question_idx, spec)
    visual.scale(1.07)
    visual.move_to(np.array([_INTRO_QUESTION_VISUAL_CENTER_X, _INTRO_QUESTION_CONTENT_Y, 0.0]))

    text_group = text_column
    text_group.move_to(
        np.array([
            _INTRO_QUESTION_TEXT_CENTER_X,
            _INTRO_QUESTION_CONTENT_Y,
            0.0,
        ])
    )

    question_card = Group(text_group, visual)
    question_card_without_rule_items: list[Mobject] = [cue_dots, bullet_items, visual]
    if len(question_claim) > 0:
        question_card_without_rule_items.insert(0, question_claim)

    return {
        "header": header,
        "question_claim": question_claim,
        "cue_dots": cue_dots,
        "bullet_items": bullet_items,
        "visual": visual,
        "question_card_without_rule": Group(*question_card_without_rule_items),
        "question_card": question_card,
        "content": question_card,
        "final_group": Group(header, question_card),
        "visual_left_column": getattr(visual, "left_column", None),
        "visual_top_target": getattr(visual, "top_target", None),
        "visual_bottom_target": getattr(visual, "bottom_target", None),
        "visual_lead_out": getattr(visual, "lead_out", None),
        "visual_top_trunk": getattr(visual, "top_trunk", None),
        "visual_bottom_trunk": getattr(visual, "bottom_trunk", None),
        "visual_top_branch": getattr(visual, "top_branch", None),
        "visual_bottom_branch": getattr(visual, "bottom_branch", None),
        "visual_simple_block": getattr(visual, "simple_block", None),
        "visual_bridge_block": getattr(visual, "bridge_block", None),
        "visual_natural_block": getattr(visual, "natural_block", None),
        "visual_top_block_intro": getattr(visual, "top_block_intro", None),
        "visual_top_block_final": getattr(visual, "top_block_final", None),
        "visual_matrix_block": getattr(visual, "matrix_block", None),
    }


# ── B → C transition ──────────────────────────────────────────────────────────

def _transition_b_to_c(scene: Scene, b_state: dict[str, Mobject]) -> None:
    """Animate the transition from the sensory-memory strip into the LTM slide."""
    c_state = _build_intro_c_layout()
    scene.play(
        FadeOut(b_state["time_label"], shift=UP * 0.03),
        FadeOut(b_state["phase_rule"], shift=UP * 0.03),
        FadeOut(b_state["phase_dots"], shift=UP * 0.03),
        FadeOut(b_state["left_phase"], shift=UP * 0.03),
        FadeOut(b_state["center_phase"], shift=UP * 0.03),
        FadeOut(b_state["right_phase"], shift=UP * 0.03),
        FadeOut(b_state["left_image"], shift=UP * 0.05),
        FadeOut(b_state["left_cut_line"]),
        FadeOut(b_state["dead_zone"]),
        FadeOut(b_state["right_cut_line"]),
        FadeOut(b_state["right_image"], shift=UP * 0.05),
        FadeOut(b_state["left_brain"], shift=DOWN * 0.03),
        FadeOut(b_state["brain_group"], shift=DOWN * 0.03),
        FadeOut(b_state["right_brain"], shift=DOWN * 0.03),
        run_time=0.90,
    )
    scene.play(
        FadeIn(c_state["time_arrow"], shift=UP * 0.03),
        FadeIn(c_state["time_label"], shift=UP * 0.03),
        FadeIn(c_state["title"], shift=UP * 0.04),
        FadeIn(c_state["brain_group"], scale=0.97),
        run_time=0.70,
    )
    scene.play(
        FadeIn(c_state["wm_trace"], scale=0.97),
        FadeIn(c_state["wm_label"], shift=UP * 0.04),
        run_time=0.55,
    )
    scene.play(FadeIn(c_state["prior_header"], shift=DOWN * 0.04), run_time=0.40)
    scene.play(
        LaggedStart(
            *[FadeIn(card, scale=0.96) for card in c_state["prior_cards"]],
            lag_ratio=0.24,
        ),
        FadeIn(c_state["prior_sub"]),
        run_time=0.85,
    )
    scene.wait(0.50)
    scene.play(
        Create(c_state["mod_arrow"]),
        FadeIn(c_state["mod_label"], shift=DOWN * 0.04),
        run_time=0.80,
    )
    scene.wait(0.60)
    scene.play(FadeIn(c_state["callout"], shift=UP * 0.04), run_time=0.60)
    scene.wait(3.50)


# ── Standalone scenes ─────────────────────────────────────────────────────────

class IntroCognitiveProblemA(_IntroNumberedScene, Scene):
    """Present the opening probe-matching hook with a blank retention interval."""
    def construct(self) -> None:
        self.camera.background_color = BG

        def _frame(path: str) -> ImageMobject:
            img = ImageMobject(path)
            img.height = 5.80
            img.move_to(ORIGIN)
            return img

        target = _frame(_INTRO_HOOK_TARGET_FISH)
        foil = _frame(_INTRO_HOOK_FOIL_FISH)

        fix = VGroup(
            Line(UP * 0.20, DOWN * 0.20, stroke_width=2.4, color=MGREY),
            Line(LEFT * 0.20, RIGHT * 0.20, stroke_width=2.4, color=MGREY),
        )

        self.add(target)
        self.wait(0.60)
        self.remove(target)
        self.add(fix)
        self.wait(3.00)
        self.remove(fix)
        self.add(foil)
        self.wait(3.50)


class IntroSensoryMemoryRepresentationA(_IntroNumberedScene, ThreeDScene):
    """Animate the 3D perception-memory-perception trajectory and snapshot handoff."""
    def construct(self) -> None:
        self.camera.background_color = BG
        self.set_camera_orientation(
            phi=62 * DEGREES,
            theta=-42 * DEGREES,
            frame_center=np.array([-0.3, 0.3, 0.0]),
            zoom=1.0,
        )

        x_step = 3.6
        x0 = np.array([-8.6, 0.0, 0.0])
        x1 = np.array([-x_step, 0.0, 0.0])
        x2 = np.array([0.0, 0.0, 0.0])
        x3 = np.array([x_step, 0.0, 0.0])
        x4 = np.array([4.0, 0.0, 0.0])

        step = 0.5
        grid_x_min, grid_x_max = -8.0, 5.0
        grid_y_min, grid_y_max = -7.0, 5.0
        grid = VGroup(
            *[
                line
                for k in np.arange(grid_y_min, grid_y_max + step * 0.5, step)
                for line in (
                    Line(
                        np.array([grid_x_min, k, 0.0]),
                        np.array([grid_x_max, k, 0.0]),
                        color=LGREY,
                        stroke_width=0.9,
                    ),
                    Line(
                        np.array([k, grid_y_min, 0.0]),
                        np.array([k, grid_y_max, 0.0]),
                        color=LGREY,
                        stroke_width=0.9,
                    ),
                )
            ]
        )
        grid.set_z_index(-20)

        axis_x = Arrow(
            x0,
            x4,
            color=MGREY,
            stroke_width=2.4,
            tip_length=0.24,
            buff=0.0,
            max_stroke_width_to_length_ratio=100,
        )
        axis_x.set_z_index(-10)
        axis_y = Arrow(
            x0,
            [0.0, 4.8, 0.0],
            color=MGREY,
            stroke_width=2.4,
            tip_length=0.24,
            buff=0.0,
            max_stroke_width_to_length_ratio=100,
        )
        axis_y.set_opacity(0.0)
        axis_y.set_z_index(-10)
        ticks = VGroup(
            *[
                Line(
                    point + np.array([0.0, -0.13, 0.0]),
                    point + np.array([0.0, 0.13, 0.0]),
                    color=LGREY,
                    stroke_width=2.0,
                )
                for point in (x1, x2, x3)
            ]
        )
        ticks.set_z_index(-5)

        rotation = self.camera.generate_rotation_matrix()
        screen_right = rotation.T @ np.array([1.0, 0.0, 0.0])
        screen_up = rotation.T @ np.array([0.0, 1.0, 0.0])
        screen_out = rotation.T @ np.array([0.0, 0.0, 1.0])
        screen_right /= np.linalg.norm(screen_right)
        screen_up /= np.linalg.norm(screen_up)
        screen_out /= np.linalg.norm(screen_out)

        def screen_aligned_point(
            anchor: np.ndarray,
            *,
            right: float = 0.0,
            up: float = 0.0,
            front: float = 0.0,
        ) -> np.ndarray:
            return anchor + right * screen_right + up * screen_up + front * screen_out

        def bottom_aligned_point(
            anchor: np.ndarray,
            mob: Mobject,
            *,
            right: float = 0.0,
            front: float = 0.0,
            gap: float = 0.0,
        ) -> np.ndarray:
            return screen_aligned_point(
                anchor,
                right=right,
                up=mob.height / 2 + gap,
                front=front,
            )

        axis_label = MathTex("t", color=INK, font_size=28).move_to(
            screen_aligned_point(x4, right=0.38, up=0.10)
        )
        axis_label.set_z_index(15)

        travel = ValueTracker(0.0)
        x_past = np.array([-2 * x_step, 0.0, 0.0])
        x_future = np.array([2 * x_step, 0.0, 0.0])

        stim_left = framed_visual(_img(_INTRO_HOOK_TARGET_FISH, 1.20))
        stim_mid = framed_visual(MathTex("+", color=INK, font_size=40))
        stim_right = framed_visual(_img(_INTRO_HOOK_FOIL_FISH, 1.20))
        for stim in (stim_left, stim_mid, stim_right):
            stim.set_z_index(30)

        def build_fixed_head(matrix: np.ndarray) -> Group:
            head = ImageMobject(str(_HEAD_BRAIN_PATH))
            head.scale_to_fit_height(2.55 * 0.72)
            head.set_opacity(1.0)
            cells = _mini_matrix(matrix, cell=_MATRIX_CELL * 0.72)
            cells.move_to(
                head.get_center()
                + LEFT * (0.085 * head.width)
                + UP * (0.24 * head.height)
            )
            return Group(head, cells)

        fixed_head = build_fixed_head(_PLOT_SENSORY_PATTERN_LEFT)
        fixed_head.set_z_index(70)
        fixed_head[0].set_z_index(71)
        fixed_head[1].set_z_index(72)
        fixed_head[1].set_opacity(0.0)
        delay_fish_side = fixed_head[1].height + 0.08
        delay_fish_inner = stim_left[1].copy()
        delay_fish_inner.scale_to_fit_height(delay_fish_side * 0.74)
        delay_fish_inner.set_opacity(0.5)
        delay_fish = framed_visual(
            delay_fish_inner,
            width=delay_fish_side,
            height=delay_fish_side,
            corner_radius=0.0,
        )
        delay_fish.set_z_index(84)
        delay_fish[0].set_z_index(84)
        delay_fish[1].set_z_index(85)

        snapshot_scale = 2.1
        # These stored snapshots are copied out of the live head trace, so they
        # must use the same matrix family or the handoff visibly morphs.
        snapshot_matrices = VGroup(
            _mini_matrix(_PLOT_SENSORY_PATTERN_LEFT, cell=_MATRIX_CELL * 0.72),
            _mini_matrix(_PLOT_MEMORY_PATTERN, cell=_MATRIX_CELL * 0.72),
            _mini_matrix(_PLOT_SENSORY_PATTERN_RIGHT, cell=_MATRIX_CELL * 0.72),
        )
        for matrix in snapshot_matrices:
            matrix.scale(snapshot_scale)
            matrix.set_z_index(91)
        snapshot_matrices.arrange(RIGHT, buff=0.62, aligned_edge=DOWN)

        snapshot_label_texts = ("perception", "memory", "perception")
        snapshot_labels = VGroup()
        for label_text in snapshot_label_texts:
            label = Tex(label_text, color=BLACK, font_size=20)
            snapshot_labels.add(label)
        for matrix, label in zip(snapshot_matrices, snapshot_labels):
            if label.width > matrix.width * 1.08:
                label.scale_to_fit_width(matrix.width * 1.08)
        for matrix, label in zip(snapshot_matrices, snapshot_labels):
            label.next_to(matrix, UP, buff=0.08)
            label.set_x(matrix.get_center()[0])
        label_top_y = max(label.get_top()[1] for label in snapshot_labels)
        for label in snapshot_labels:
            label.shift(UP * (label_top_y - label.get_top()[1]))

        left_set_brace = MathTex(r"\Bigg\{", color=BLACK, font_size=58)
        left_set_brace.next_to(snapshot_matrices[0], LEFT, buff=0.08)
        left_set_brace.move_to(
            np.array(
                [
                    left_set_brace.get_center()[0],
                    snapshot_matrices.get_center()[1] - 0.02,
                    0.0,
                ]
            )
        )
        right_set_brace = MathTex(r"\Bigg\}", color=BLACK, font_size=58)

        snapshot_prefix = VGroup(
            MathTex(r"\mathit{Neural}", color=BLACK, font_size=18),
            MathTex(r"\mathit{Representations}", color=BLACK, font_size=18),
        ).arrange(DOWN, buff=0.03)
        snapshot_equals = MathTex("=", color=BLACK, font_size=24)
        snapshot_equals.next_to(snapshot_prefix, RIGHT, buff=0.08)
        snapshot_equals.align_to(snapshot_prefix, ORIGIN)
        snapshot_prefix_group = VGroup(snapshot_prefix, snapshot_equals)
        snapshot_prefix_group.next_to(left_set_brace, LEFT, buff=0.10)
        snapshot_prefix_group.move_to(
            np.array(
                [
                    snapshot_prefix_group.get_center()[0],
                    snapshot_matrices.get_center()[1] - 0.02,
                    0.0,
                ]
            )
        )

        snapshot_commas = VGroup()
        for left_target, right_target in zip(snapshot_matrices[:-1], snapshot_matrices[1:]):
            comma = Tex(",", color=BLACK, font_size=28)
            comma.move_to(midpoint(left_target.get_right(), right_target.get_left()))
            comma.shift(DOWN * 0.08)
            snapshot_commas.add(comma)
        snapshot_trailing_comma = Tex(",", color=BLACK, font_size=28)
        snapshot_trailing_comma.next_to(snapshot_matrices[-1], RIGHT, buff=0.08)
        snapshot_trailing_comma.align_to(snapshot_commas[0], DOWN)
        snapshot_ellipsis = MathTex(r"\cdots", color=BLACK, font_size=20)
        snapshot_ellipsis.next_to(snapshot_trailing_comma, RIGHT, buff=0.05)
        snapshot_ellipsis.align_to(snapshot_trailing_comma, DOWN)
        snapshot_ellipsis.shift(UP * 0.03)
        right_set_brace.next_to(snapshot_ellipsis, RIGHT, buff=0.05)
        right_set_brace.move_to(
            np.array(
                [
                    right_set_brace.get_center()[0],
                    snapshot_matrices.get_center()[1] - 0.02,
                    0.0,
                ]
            )
        )

        snapshot_scaffold = VGroup(
            snapshot_prefix_group,
            snapshot_labels,
            left_set_brace,
            snapshot_commas,
            snapshot_trailing_comma,
            snapshot_ellipsis,
            right_set_brace,
        )
        snapshot_equation = VGroup(snapshot_matrices, snapshot_scaffold)
        snapshot_equation.to_corner(DL, buff=0.34)
        snapshot_equation.shift(RIGHT * 0.14 + UP * 0.52)

        for mob in (
            snapshot_prefix_group,
            left_set_brace,
            right_set_brace,
            snapshot_trailing_comma,
            snapshot_ellipsis,
            *snapshot_labels,
            *snapshot_commas,
        ):
            mob.save_state()
            mob.shift(DOWN * 0.03)
            mob.set_opacity(0.0)
        snapshot_scaffold.set_z_index(92)

        dot_gap = 0.72
        front_offset = 0.62

        def path_anchor(points: list[np.ndarray], t: float) -> np.ndarray:
            clipped = float(np.clip(t, 0.0, len(points) - 1))
            idx = min(int(np.floor(clipped)), len(points) - 2)
            alpha = clipped - idx
            return interpolate(points[idx], points[idx + 1], alpha)

        def place_card(mob: Mobject, anchor: np.ndarray) -> None:
            mob.move_to(
                bottom_aligned_point(
                    anchor,
                    mob,
                    right=(dot_gap + mob.width / 2),
                    front=front_offset,
                )
            )

        left_path = [x2, x1, x_past]
        mid_path = [x3, x2, x1]
        right_path = [x_future, x3, x2]

        node_left = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0)
        node_mid = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0)
        node_right = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0)
        nodes = VGroup(node_left, node_mid, node_right)
        nodes.set_z_index(40)

        def current_matrix(t: float) -> np.ndarray:
            if t <= 1.0:
                return interpolate_matrix(
                    _PLOT_SENSORY_PATTERN_LEFT,
                    _PLOT_MEMORY_PATTERN,
                    np.clip(t, 0.0, 1.0),
                )
            return interpolate_matrix(
                _PLOT_MEMORY_PATTERN,
                _PLOT_SENSORY_PATTERN_RIGHT,
                np.clip(t - 1.0, 0.0, 1.0),
            )

        def update_card(mob: Mobject, points: list[np.ndarray]) -> Mobject:
            place_card(mob, path_anchor(points, travel.get_value()))
            return mob

        def update_dot(mob: Mobject, points: list[np.ndarray]) -> Mobject:
            mob.move_to(path_anchor(points, travel.get_value()))
            return mob

        fixed_head_anchor = x2

        def place_fixed_head(mob: Mobject) -> None:
            mob.move_to(
                bottom_aligned_point(
                    fixed_head_anchor,
                    mob,
                    right=-(dot_gap + mob.width / 2),
                    front=front_offset,
                )
            )

        def place_delay_fish(mob: Mobject) -> None:
            mob.move_to(
                bottom_aligned_point(
                    fixed_head_anchor,
                    mob,
                    right=-(dot_gap + fixed_head.width + 0.28 + mob.width / 2),
                    front=front_offset + 0.24,
                    gap=0.30 * mob.height,
                )
            )

        def update_fixed_head(mob: Mobject) -> Mobject:
            place_fixed_head(mob)
            new_matrix = _mini_matrix(current_matrix(travel.get_value()), cell=_MATRIX_CELL * 0.72)
            new_matrix.move_to(
                mob[0].get_center()
                + LEFT * (0.085 * mob[0].width)
                + UP * (0.24 * mob[0].height)
            )
            new_matrix.set_z_index(72)
            mob[1].become(new_matrix)
            return mob

        def snapshot_animation(
            source: Mobject,
            target: Mobject,
            *,
            move_run_time: float = 0.95,
            reveal_items: tuple[Mobject, ...] = (),
        ) -> AnimationGroup:
            moving_copy = source.copy()
            live_target = target.copy()
            live_target.save_state()
            live_target.set_opacity(0.0)
            live_target.set_z_index(target.z_index)
            center_func = None
            for submob in source.get_family():
                if submob in self.renderer.camera.fixed_orientation_mobjects:
                    center_func = self.renderer.camera.fixed_orientation_mobjects[submob]
                    break
            if center_func is None:
                moving_copy.move_to(self.camera.project_point(source.get_center()))
            else:
                center = center_func()
                moving_copy.shift(self.camera.project_point(center) - center)
            moving_copy.set_z_index(120)
            morph_run_time = min(0.22, move_run_time * 0.2)
            travel_run_time = max(0.0, move_run_time - morph_run_time)
            animations: list[Animation] = [
                Succession(
                    moving_copy.animate(run_time=travel_run_time, rate_func=smooth).scale(snapshot_scale).move_to(
                        target.get_center()
                    ),
                    AnimationGroup(
                        FadeOut(
                            moving_copy,
                            run_time=morph_run_time,
                            rate_func=smooth,
                        ),
                        Restore(
                            live_target,
                            run_time=morph_run_time,
                            rate_func=smooth,
                        ),
                    ),
                )
            ]
            self.add_fixed_in_frame_mobjects(moving_copy, live_target)
            if reveal_items:
                animations.append(
                    Succession(
                        Wait(0.68 * move_run_time),
                        AnimationGroup(
                            *[Restore(mob, run_time=0.24) for mob in reveal_items],
                            lag_ratio=0.08,
                        ),
                    )
                )
            return AnimationGroup(*animations, lag_ratio=0.0)

        place_card(stim_left, path_anchor(left_path, 0.0))
        place_card(stim_mid, path_anchor(mid_path, 0.0))
        place_card(stim_right, path_anchor(right_path, 0.0))
        place_fixed_head(fixed_head)
        place_delay_fish(delay_fish)
        delay_fish.set(opacity=0.0)
        update_dot(node_left, left_path)
        update_dot(node_mid, mid_path)
        update_dot(node_right, right_path)

        self.add_fixed_orientation_mobjects(
            axis_label,
            fixed_head,
        )
        self.add_fixed_in_frame_mobjects(
            snapshot_prefix_group,
            left_set_brace,
            right_set_brace,
            snapshot_trailing_comma,
            snapshot_ellipsis,
            *snapshot_labels,
            *snapshot_commas,
        )

        self.play(Create(grid), run_time=0.7)
        self.play(
            Create(axis_x),
            Create(axis_y),
            Create(ticks),
            FadeIn(axis_label, shift=UP * 0.03),
            run_time=1.0,
        )
        self.add_fixed_orientation_mobjects(stim_left)
        self.play(
            FadeIn(stim_left, scale=0.97),
            FadeIn(node_left),
            run_time=0.45,
        )
        self.play(
            FadeIn(fixed_head[1], scale=0.97),
            run_time=0.50,
        )
        self.wait(0.80)
        self.add_fixed_orientation_mobjects(stim_mid, stim_right)
        stim_left.add_updater(lambda mob: update_card(mob, left_path))
        stim_mid.add_updater(lambda mob: update_card(mob, mid_path))
        stim_right.add_updater(lambda mob: update_card(mob, right_path))
        node_left.add_updater(lambda mob: update_dot(mob, left_path))
        node_mid.add_updater(lambda mob: update_dot(mob, mid_path))
        node_right.add_updater(lambda mob: update_dot(mob, right_path))
        fixed_head.add_updater(update_fixed_head)
        self.play(
            FadeIn(VGroup(node_mid, node_right)),
            FadeIn(stim_mid, scale=0.97),
            FadeIn(stim_right, scale=0.97),
            run_time=0.35,
        )
        self.wait(0.35)
        self.play(
            Restore(snapshot_prefix_group),
            Restore(left_set_brace),
            run_time=0.35,
        )
        self.play(
            travel.animate.set_value(1.0),
            snapshot_animation(
                fixed_head[1],
                snapshot_matrices[0],
                move_run_time=2.0,
                reveal_items=(snapshot_labels[0], snapshot_commas[0]),
            ),
            run_time=2.3,
            rate_func=smooth,
        )
        self.add_fixed_orientation_mobjects(delay_fish)
        delay_fish.set(opacity=0.0)
        self.play(FadeIn(delay_fish, shift=LEFT * 0.04), run_time=0.25)
        self.wait(1.00)
        self.play(FadeOut(delay_fish, shift=LEFT * 0.04), run_time=0.25)
        self.remove(delay_fish)
        self.play(
            travel.animate.set_value(2.0),
            snapshot_animation(
                fixed_head[1],
                snapshot_matrices[1],
                move_run_time=2.0,
                reveal_items=(snapshot_labels[1], snapshot_commas[1]),
            ),
            run_time=2.3,
            rate_func=smooth,
        )
        self.wait(0.65)
        self.play(
            snapshot_animation(
                fixed_head[1],
                snapshot_matrices[2],
                reveal_items=(snapshot_labels[2], snapshot_trailing_comma, snapshot_ellipsis, right_set_brace),
            )
        )
        self.wait(1.0)


def _build_intro_sensmem_equation(
    *,
    labels_below: bool,
    anchor_corner: bool,
    matrix_buff: float = 0.62,
) -> dict[str, Mobject]:
    """Build the fixed-frame equation summarizing perception-memory-perception traces."""
    snapshot_scale = 2.1
    base_cell = _MATRIX_CELL * 0.72
    matrices = VGroup(
        _mini_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT, cell=base_cell),
        _mini_matrix(_REPRESENTATION_MEMORY_PATTERN, cell=base_cell),
        _mini_matrix(_REPRESENTATION_SENSORY_PATTERN_RIGHT, cell=base_cell),
    )
    for matrix in matrices:
        matrix.scale(snapshot_scale)
    matrices.arrange(RIGHT, buff=matrix_buff, aligned_edge=DOWN)

    label_texts = ("perception", "memory", "perception")
    labels = VGroup(*[Tex(text, color=BLACK, font_size=20) for text in label_texts])
    for matrix, label in zip(matrices, labels):
        if label.width > matrix.width * 1.08:
            label.scale_to_fit_width(matrix.width * 1.08)
        label.next_to(matrix, DOWN if labels_below else UP, buff=0.08)
        label.set_x(matrix.get_center()[0])
    if labels_below:
        label_top_y = max(label.get_top()[1] for label in labels)
        for label in labels:
            label.shift(UP * (label_top_y - label.get_top()[1]))
    else:
        label_top_y = max(label.get_top()[1] for label in labels)
        for label in labels:
            label.shift(UP * (label_top_y - label.get_top()[1]))

    left_set_brace = MathTex(r"\Bigg\{", color=BLACK, font_size=58)
    left_set_brace.next_to(matrices[0], LEFT, buff=0.08)
    left_set_brace.move_to(
        np.array(
            [
                left_set_brace.get_center()[0],
                matrices.get_center()[1] - 0.02,
                0.0,
            ]
        )
    )
    right_set_brace = MathTex(r"\Bigg\}", color=BLACK, font_size=58)

    prefix = VGroup(
        MathTex(r"\mathit{Neural}", color=BLACK, font_size=18),
        MathTex(r"\mathit{Representations}", color=BLACK, font_size=18),
    ).arrange(DOWN, buff=0.03)
    equals = MathTex("=", color=BLACK, font_size=24)
    equals.next_to(prefix, RIGHT, buff=0.08)
    equals.align_to(prefix, ORIGIN)
    prefix_group = VGroup(prefix, equals)
    prefix_group.next_to(left_set_brace, LEFT, buff=0.10)
    prefix_group.move_to(
        np.array(
            [
                prefix_group.get_center()[0],
                matrices.get_center()[1] - 0.02,
                0.0,
            ]
        )
    )

    commas = VGroup()
    for left_matrix, right_matrix in zip(matrices[:-1], matrices[1:]):
        comma = Tex(",", color=BLACK, font_size=28)
        comma.move_to(midpoint(left_matrix.get_right(), right_matrix.get_left()))
        comma.shift(DOWN * 0.08)
        commas.add(comma)
    trailing_comma = Tex(",", color=BLACK, font_size=28)
    trailing_comma.next_to(matrices[-1], RIGHT, buff=0.08)
    trailing_comma.align_to(commas[0], DOWN)
    ellipsis = MathTex(r"\cdots", color=BLACK, font_size=20)
    ellipsis.next_to(trailing_comma, RIGHT, buff=0.05)
    ellipsis.align_to(trailing_comma, DOWN)
    ellipsis.shift(UP * 0.03)
    right_set_brace.next_to(ellipsis, RIGHT, buff=0.05)
    right_set_brace.move_to(
        np.array(
            [
                right_set_brace.get_center()[0],
                matrices.get_center()[1] - 0.02,
                0.0,
            ]
        )
    )

    equation = VGroup(
        prefix_group,
        left_set_brace,
        matrices,
        labels,
        commas,
        trailing_comma,
        ellipsis,
        right_set_brace,
    )
    if anchor_corner:
        equation.to_corner(DL, buff=0.34)
        equation.shift(RIGHT * 0.14 + UP * 0.52)

    return {
        "equation": equation,
        "prefix_group": prefix_group,
        "left_set_brace": left_set_brace,
        "matrices": matrices,
        "labels": labels,
        "commas": commas,
        "trailing_comma": trailing_comma,
        "ellipsis": ellipsis,
        "right_set_brace": right_set_brace,
    }


def _build_intro_sensmem_b_center_state() -> dict[str, Mobject]:
    """Build the centered equation-and-card layout for the second sensory-memory slide."""
    equation_state = _build_intro_sensmem_equation(
        labels_below=True,
        anchor_corner=False,
        matrix_buff=1.16,
    )
    target_row = Group(equation_state["matrices"], equation_state["labels"])
    target_row.move_to(np.array([0.0, 0.22, 0.0]))

    cards = Group(
        framed_visual(_img(_INTRO_HOOK_TARGET_FISH, 1.20)),
        framed_visual(MathTex("+", color=INK, font_size=40)),
        framed_visual(_img(_INTRO_HOOK_FOIL_FISH, 1.20)),
    )
    for card, matrix in zip(cards, equation_state["matrices"]):
        card.next_to(matrix, UP, buff=0.22)
        card.set_x(matrix.get_center()[0])
        card.set_z_index(110)
        card[0].set_z_index(110)
        card[1].set_z_index(111)

    explanation = Tex(
        r"Maintenance and manipulation of information over short delays",
        color=INK,
        font_size=30,
    )
    explanation.scale_to_fit_width(min(explanation.width, config.frame_width - 1.30))
    explanation.move_to(
        np.array(
            [
                target_row.get_center()[0],
                0.5 * (target_row.get_bottom()[1] - config.frame_height / 2),
                0.0,
            ]
        )
    )
    explanation.set_z_index(110)

    return {
        "equation_state": equation_state,
        "cards": cards,
        "explanation": explanation,
        "final_group": Group(cards, equation_state["matrices"], equation_state["labels"], explanation),
    }


def _build_intro_sensmem_b_contours(matrices: VGroup, *, threshold: float = 0.18) -> VGroup:
    """Highlight cells whose values stay similar across the three pattern snapshots."""
    left_vals = _REPRESENTATION_SENSORY_PATTERN_LEFT.flatten()
    memory_vals = _REPRESENTATION_MEMORY_PATTERN.flatten()
    right_vals = _REPRESENTATION_SENSORY_PATTERN_RIGHT.flatten()
    cell_ids = [
        index
        for index, (left_value, memory_value, right_value) in enumerate(
            zip(left_vals, memory_vals, right_vals)
        )
        if max(
            abs(left_value - memory_value),
            abs(memory_value - right_value),
            abs(left_value - right_value),
        )
        < threshold
    ]
    contour_cells = VGroup(
        *[
            matrices[matrix_index][cell_index]
            for matrix_index in range(len(matrices))
            for cell_index in cell_ids
        ]
    )
    contour_group = VGroup(
        *[
            SurroundingRectangle(
                cell,
                color=BLACK,
                buff=0.02,
                stroke_width=1.8,
            )
            for cell in contour_cells
        ]
    )
    contour_group.set_z_index(120)
    return contour_group


def _build_intro_sensmem_b_end_state() -> dict[str, Mobject]:
    """Build the two-case comparison between sensory-like and memory-specific codes."""
    def _build_matrix(matrix: np.ndarray) -> VGroup:
        cells = _mini_matrix(matrix, cell=_MATRIX_CELL * 0.72)
        cells.scale(2.85)
        cells.set_z_index(100)
        return cells

    def _row_label(title_text: str, subtitle_text: str, accent: str) -> VGroup:
        title_row = VGroup(
            Dot(radius=0.045, color=accent, stroke_width=0),
            Tex(rf"\textbf{{{title_text}}}", color=accent, font_size=20),
        ).arrange(RIGHT, buff=0.12)
        subtitle = Tex(subtitle_text, color=INK, font_size=16)
        if subtitle.width > 2.70:
            subtitle.scale_to_fit_width(2.70)
        group = VGroup(title_row, subtitle).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        group.set_z_index(110)
        return group

    title = Tex(r"\textbf{Two possibilities for the WM code}", color=INK, font_size=30)
    title.to_edge(UP, buff=0.44)
    title_rule = Line(
        LEFT * max(2.10, title.width * 0.22),
        RIGHT * max(2.10, title.width * 0.22),
        color=LGREY,
        stroke_width=1.1,
    )
    title_rule.next_to(title, DOWN, buff=0.14)
    title_group = VGroup(title, title_rule)
    title_group.set_z_index(110)

    top_left = _build_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT)
    top_right = _build_matrix(_REPRESENTATION_SENSORY_PATTERN_RIGHT)
    bottom_left = _build_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT)
    bottom_right = _build_matrix(_REPRESENTATION_MEMORY_PATTERN)

    top_row = VGroup(top_left, top_right).arrange(RIGHT, buff=1.02, aligned_edge=DOWN)
    bottom_row = VGroup(bottom_left, bottom_right).arrange(RIGHT, buff=1.02, aligned_edge=DOWN)
    VGroup(top_row, bottom_row).arrange(DOWN, buff=0.84, aligned_edge=LEFT).move_to(
        np.array([1.30, -0.22, 0.0])
    )

    sensory_header = Tex(r"\textbf{Sensory code}", color=INK, font_size=22)
    wm_header = Tex(r"\textbf{WM code}", color=INK, font_size=22)
    sensory_header.next_to(top_left, UP, buff=0.24)
    sensory_header.set_x(top_left.get_center()[0])
    wm_header.next_to(top_right, UP, buff=0.24)
    wm_header.set_x(top_right.get_center()[0])
    column_headers = VGroup(sensory_header, wm_header)
    column_headers.set_z_index(110)

    row_labels = VGroup(
        _row_label("sensory-like", "case", BLUE),
        _row_label("memory-specific", "format case", AMBER),
    )
    for label, row in zip(row_labels, (top_row, bottom_row)):
        label.next_to(row, LEFT, buff=0.62)
        label.move_to(np.array([label.get_center()[0], row.get_center()[1], 0.0]))

    row_panels = VGroup()
    for accent, label, row in zip((BLUE, AMBER), row_labels, (top_row, bottom_row)):
        row_group = VGroup(label, row)
        panel = RoundedRectangle(
            width=row_group.width + 0.44,
            height=max(row.height + 0.42, row_group.height + 0.26),
            corner_radius=0.18,
            stroke_color=accent,
            stroke_width=1.4,
        ).set_fill(PANEL, opacity=0.98)
        panel.move_to(row_group.get_center())
        row_panels.add(panel)
    row_panels.set_z_index(85)

    matrices = VGroup(top_left, top_right, bottom_left, bottom_right)
    final_group = Group(title_group, row_panels, column_headers, row_labels, matrices)
    return {
        "title_group": title_group,
        "row_panels": row_panels,
        "column_headers": column_headers,
        "row_labels": row_labels,
        "top_row": top_row,
        "bottom_row": bottom_row,
        "matrices": matrices,
        "final_group": final_group,
    }


def _build_intro_sensmem_b_hook_state() -> dict[str, Mobject]:
    """Build the hook-state variant of the two-case WM-code comparison layout."""
    def _build_matrix(matrix: np.ndarray) -> VGroup:
        cells = _mini_matrix(matrix, cell=_MATRIX_CELL * 0.72)
        cells.scale(3.35)
        cells.set_z_index(100)
        return cells

    def _row_label(title_text: str, subtitle_text: str, accent: str) -> VGroup:
        title_row = VGroup(
            Dot(radius=0.045, color=accent, stroke_width=0),
            Tex(rf"\textbf{{{title_text}}}", color=accent, font_size=20),
        ).arrange(RIGHT, buff=0.12)
        subtitle = Tex(subtitle_text, color=INK, font_size=16)
        if subtitle.width > 2.70:
            subtitle.scale_to_fit_width(2.70)
        group = VGroup(title_row, subtitle).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        group.set_z_index(110)
        return group

    title = Tex(r"\textbf{Two possibilities for the WM code}", color=INK, font_size=30)
    title.to_edge(UP, buff=0.44)
    title_rule = Line(
        LEFT * max(2.10, title.width * 0.22),
        RIGHT * max(2.10, title.width * 0.22),
        color=LGREY,
        stroke_width=1.1,
    )
    title_rule.next_to(title, DOWN, buff=0.14)
    title_group = VGroup(title, title_rule)
    title_group.set_z_index(110)

    top_left = _build_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT)
    top_right = _build_matrix(_REPRESENTATION_SENSORY_PATTERN_RIGHT)
    bottom_left = _build_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT)
    bottom_right = _build_matrix(_REPRESENTATION_MEMORY_PATTERN)

    top_row = VGroup(top_left, top_right).arrange(RIGHT, buff=1.02, aligned_edge=DOWN)
    bottom_row = VGroup(bottom_left, bottom_right).arrange(RIGHT, buff=1.02, aligned_edge=DOWN)
    VGroup(top_row, bottom_row).arrange(DOWN, buff=0.76, aligned_edge=LEFT).move_to(
        np.array([1.28, -0.12, 0.0])
    )

    sensory_header = Tex(r"\textbf{Sensory code}", color=INK, font_size=24)
    wm_header = Tex(r"\textbf{WM code}", color=INK, font_size=24)
    sensory_header.next_to(top_left, UP, buff=0.24)
    sensory_header.set_x(top_left.get_center()[0])
    wm_header.next_to(top_right, UP, buff=0.24)
    wm_header.set_x(top_right.get_center()[0])
    column_headers = VGroup(sensory_header, wm_header)
    column_headers.set_z_index(110)

    row_labels = VGroup(
        _row_label("sensory-like", "case", BLUE),
        _row_label("memory-specific", "format case", AMBER),
    )
    for label, row in zip(row_labels, (top_row, bottom_row)):
        label.next_to(row, LEFT, buff=0.62)
        label.move_to(np.array([label.get_center()[0], row.get_center()[1], 0.0]))

    row_panels = VGroup()
    for accent, label, row in zip((BLUE, AMBER), row_labels, (top_row, bottom_row)):
        row_group = VGroup(label, row)
        panel = RoundedRectangle(
            width=row_group.width + 0.44,
            height=max(row.height + 0.42, row_group.height + 0.26),
            corner_radius=0.18,
            stroke_color=accent,
            stroke_width=1.4,
        ).set_fill(PANEL, opacity=0.98)
        panel.move_to(row_group.get_center())
        row_panels.add(panel)
    row_panels.set_z_index(85)

    matrices = VGroup(top_left, top_right, bottom_left, bottom_right)
    final_group = Group(title_group, row_panels, column_headers, row_labels, matrices)
    return {
        "title_group": title_group,
        "row_panels": row_panels,
        "column_headers": column_headers,
        "row_labels": row_labels,
        "top_row": top_row,
        "bottom_row": bottom_row,
        "matrices": matrices,
        "final_group": final_group,
    }


def _build_intro_sensmem_a_plot_state(scene: ThreeDScene) -> dict[str, Mobject]:
    """Build the 3D sensory-memory trajectory plot and attached stimulus markers."""
    x_step = 3.35
    x0 = np.array([-8.6, 0.0, 0.0])
    x1 = np.array([-x_step, 0.0, 0.0])
    x2 = np.array([0.0, 0.0, 0.0])
    x3 = np.array([x_step, 0.0, 0.0])
    x4 = np.array([4.0, 0.0, 0.0])
    x_past = np.array([-2 * x_step, 0.0, 0.0])

    step = 0.5
    grid_x_min, grid_x_max = -8.0, 5.0
    grid_y_min, grid_y_max = -7.0, 5.0
    grid = VGroup(
        *[
            line
            for k in np.arange(grid_y_min, grid_y_max + step * 0.5, step)
            for line in (
                Line(
                    np.array([grid_x_min, k, 0.0]),
                    np.array([grid_x_max, k, 0.0]),
                    color=LGREY,
                    stroke_width=0.9,
                ),
                Line(
                    np.array([k, grid_y_min, 0.0]),
                    np.array([k, grid_y_max, 0.0]),
                    color=LGREY,
                    stroke_width=0.9,
                ),
            )
        ]
    )
    grid.set_z_index(-20)

    axis_x = Arrow(
        x0,
        x4,
        color=MGREY,
        stroke_width=2.4,
        tip_length=0.24,
        buff=0.0,
        max_stroke_width_to_length_ratio=100,
    )
    axis_x.set_z_index(-10)
    ticks = VGroup(
        *[
            Line(
                point + np.array([0.0, -0.13, 0.0]),
                point + np.array([0.0, 0.13, 0.0]),
                color=LGREY,
                stroke_width=2.0,
            )
            for point in (x1, x2, x3)
        ]
    )
    ticks.set_z_index(-5)

    rotation = scene.camera.generate_rotation_matrix()
    screen_right = rotation.T @ np.array([1.0, 0.0, 0.0])
    screen_up = rotation.T @ np.array([0.0, 1.0, 0.0])
    screen_out = rotation.T @ np.array([0.0, 0.0, 1.0])
    screen_right /= np.linalg.norm(screen_right)
    screen_up /= np.linalg.norm(screen_up)
    screen_out /= np.linalg.norm(screen_out)

    def screen_aligned_point(
        anchor: np.ndarray,
        *,
        right: float = 0.0,
        up: float = 0.0,
        front: float = 0.0,
    ) -> np.ndarray:
        return anchor + right * screen_right + up * screen_up + front * screen_out

    def bottom_aligned_point(
        anchor: np.ndarray,
        mob: Mobject,
        *,
        right: float = 0.0,
        front: float = 0.0,
        gap: float = 0.0,
    ) -> np.ndarray:
        return screen_aligned_point(
            anchor,
            right=right,
            up=mob.height / 2 + gap,
            front=front,
        )

    axis_label = MathTex("t", color=INK, font_size=28).move_to(
        screen_aligned_point(x4, right=0.38, up=0.10)
    )
    axis_label.set_z_index(15)

    stim_left = framed_visual(_img(_INTRO_HOOK_TARGET_FISH, 1.20))
    stim_mid = framed_visual(MathTex("+", color=INK, font_size=40))
    stim_right = framed_visual(_img(_INTRO_HOOK_FOIL_FISH, 1.20))
    for stim in (stim_left, stim_mid, stim_right):
        stim.set_z_index(30)

    def build_fixed_head(matrix: np.ndarray) -> Group:
        head = ImageMobject(str(_HEAD_BRAIN_PATH))
        head.scale_to_fit_height(2.55 * 0.72)
        head.set_opacity(1.0)
        cells = _mini_matrix(matrix, cell=_MATRIX_CELL * 0.72)
        cells.move_to(
            head.get_center()
            + LEFT * (0.085 * head.width)
            + UP * (0.24 * head.height)
        )
        return Group(head, cells)

    fixed_head = build_fixed_head(_PLOT_SENSORY_PATTERN_RIGHT)
    fixed_head.set_z_index(70)
    fixed_head[0].set_z_index(71)
    fixed_head[1].set_z_index(72)
    fixed_head[1].set_opacity(1.0)

    dot_gap = 0.72
    front_offset = 0.62

    def place_card(mob: Mobject, anchor: np.ndarray) -> None:
        mob.move_to(
            bottom_aligned_point(
                anchor,
                mob,
                right=(dot_gap + mob.width / 2),
                front=front_offset,
            )
        )

    def place_fixed_head(mob: Mobject) -> None:
        mob.move_to(
            bottom_aligned_point(
                x2,
                mob,
                right=-(dot_gap + mob.width / 2),
                front=front_offset,
            )
        )

    place_card(stim_left, x_past)
    place_card(stim_mid, x1)
    place_card(stim_right, x2)
    place_fixed_head(fixed_head)

    node_left = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0).move_to(x_past)
    node_mid = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0).move_to(x1)
    node_right = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0).move_to(x2)
    nodes = VGroup(node_left, node_mid, node_right)
    nodes.set_z_index(40)

    return {
        "grid": grid,
        "axis_x": axis_x,
        "ticks": ticks,
        "axis_label": axis_label,
        "stim_left": stim_left,
        "stim_mid": stim_mid,
        "stim_right": stim_right,
        "fixed_head": fixed_head,
        "nodes": nodes,
    }


def _project_fixed_orientation_copy(scene: ThreeDScene, source: Mobject) -> Mobject:
    """Project a copy of a fixed-orientation mobject into current screen coordinates."""
    projected = source.copy()
    center_func = None
    for submob in source.get_family():
        if submob in scene.renderer.camera.fixed_orientation_mobjects:
            center_func = scene.renderer.camera.fixed_orientation_mobjects[submob]
            break
    if center_func is None:
        projected.move_to(scene.camera.project_point(source.get_center()))
    else:
        center = center_func()
        projected.shift(scene.camera.project_point(center) - center)
    return projected


class IntroSensoryMemoryRepresentationB(_IntroNumberedScene, ThreeDScene):
    """Flatten the trajectory into a fixed-frame equation and compare code structure."""
    def construct(self) -> None:
        self.camera.background_color = BG
        self.set_camera_orientation(
            phi=62 * DEGREES,
            theta=-42 * DEGREES,
            frame_center=np.array([-0.3, 0.3, 0.0]),
            zoom=1.0,
        )

        plot_state = _build_intro_sensmem_a_plot_state(self)
        equation_state = _build_intro_sensmem_equation(labels_below=False, anchor_corner=True)
        equation_group = equation_state["equation"]
        equation_group.set_z_index(90)

        self.add(plot_state["grid"], plot_state["axis_x"], plot_state["ticks"], plot_state["nodes"])
        self.add_fixed_orientation_mobjects(
            plot_state["axis_label"],
            plot_state["fixed_head"],
            plot_state["stim_left"],
            plot_state["stim_mid"],
            plot_state["stim_right"],
        )
        self.add(
            plot_state["stim_left"],
            plot_state["stim_mid"],
            plot_state["stim_right"],
            plot_state["fixed_head"],
            plot_state["axis_label"],
        )
        self.add_fixed_in_frame_mobjects(*equation_group)
        self.add(equation_group)

        center_state = _build_intro_sensmem_b_center_state()
        target_state = center_state["equation_state"]
        target_cards = center_state["cards"]
        target_card_centers = [card.get_center().copy() for card in target_cards]
        source_cards = (plot_state["stim_left"], plot_state["stim_mid"], plot_state["stim_right"])
        for source_card, target_card in zip(source_cards, target_cards):
            projected = _project_fixed_orientation_copy(self, source_card)
            target_card.move_to(projected.get_center())
            target_card[0].set_fill(opacity=0.0)
            target_card[0].set_stroke(opacity=0.0)
            target_card[1].set_opacity(0.0)
        self.add_fixed_in_frame_mobjects(*target_cards)
        self.add(*target_cards)
        center_state["explanation"].set_opacity(0.0)
        self.add_fixed_in_frame_mobjects(center_state["explanation"])
        self.add(center_state["explanation"])

        def transport_card(
            source: Group,
            card: Group,
            target_center: np.ndarray,
            *,
            run_time: float,
        ) -> list[Animation]:
            start_center = card.get_center().copy()

            def update_card(mob: Group, alpha: float) -> None:
                move_alpha = smooth(alpha)
                center = interpolate(start_center, target_center, move_alpha)
                mob[0].move_to(center)
                mob[1].move_to(center)
                mob[0].set_fill(opacity=1.0)
                mob[0].set_stroke(opacity=1.0)
                mob[1].set_opacity(1.0)

            return [
                FadeOut(
                    source,
                    run_time=0.01,
                ),
                UpdateFromAlphaFunc(card, update_card, run_time=run_time),
            ]

        dissolve_group = Group(
            plot_state["grid"],
            plot_state["axis_x"],
            plot_state["ticks"],
            plot_state["nodes"],
            plot_state["fixed_head"],
            plot_state["axis_label"],
        )

        self.wait(0.10)
        self.play(
            FadeOut(dissolve_group, run_time=1.7),
            FadeOut(equation_state["prefix_group"], run_time=1.1),
            FadeOut(equation_state["left_set_brace"], run_time=1.1),
            FadeOut(equation_state["commas"], run_time=1.1),
            FadeOut(equation_state["trailing_comma"], run_time=1.1),
            FadeOut(equation_state["ellipsis"], run_time=1.1),
            FadeOut(equation_state["right_set_brace"], run_time=1.1),
            *[
                animation
                for source, card, target_center in zip(
                    source_cards,
                    target_cards,
                    target_card_centers,
                )
                for animation in transport_card(
                    source,
                    card,
                    target_center,
                    run_time=1.7,
                )
            ],
            *[
                matrix.animate(run_time=1.7).move_to(target_matrix.get_center())
                for matrix, target_matrix in zip(
                    equation_state["matrices"],
                    target_state["matrices"],
                )
            ],
            *[
                label.animate(run_time=1.7).move_to(target_label.get_center())
                for label, target_label in zip(
                    equation_state["labels"],
                    target_state["labels"],
                )
            ],
            rate_func=smooth,
        )
        self.play(FadeIn(center_state["explanation"], shift=UP * 0.04), run_time=0.45)

        contour_group = _build_intro_sensmem_b_contours(equation_state["matrices"])
        self.add_fixed_in_frame_mobjects(*contour_group)
        self.play(
            LaggedStart(
                *[Create(contour) for contour in contour_group],
                lag_ratio=0.04,
            ),
            run_time=3.0,
        )
        self.wait(2.0)
        final_state = _build_intro_sensmem_b_center_state()
        final_contour_group = _build_intro_sensmem_b_contours(final_state["equation_state"]["matrices"])
        self.remove(
            target_cards,
            equation_state["matrices"],
            equation_state["labels"],
            center_state["explanation"],
            contour_group,
        )
        self.add_fixed_in_frame_mobjects(*final_state["final_group"], *final_contour_group)
        self.add(final_state["final_group"])
        self.add(final_contour_group)
        self._intro_sensmem_b_transition_group = Group(
            final_state["final_group"].copy(),
            final_contour_group.copy(),
        )
        self._intro_sensmem_b_transition_group.shift(-self.camera.frame_center)
        self.wait(0.30)


class IntroSensoryMemoryRepresentations(Scene):
    """Play the simplified sensory-memory timeline before transitioning onward."""
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_b_layout()
        self.play(
            FadeIn(state["time_label"], shift=UP * 0.03),
            Create(state["phase_rule"]),
            FadeIn(state["phase_dots"], scale=0.97),
            FadeIn(state["left_phase"], shift=UP * 0.03),
            FadeIn(state["center_phase"], shift=UP * 0.03),
            FadeIn(state["right_phase"], shift=UP * 0.03),
            run_time=0.65,
        )
        self.play(
            LaggedStart(
                FadeIn(state["left_image"]),
                Create(state["left_cut_line"]),
                FadeIn(state["dead_zone"]),
                Create(state["right_cut_line"]),
                FadeIn(state["right_image"]),
                lag_ratio=0.10,
            ),
            run_time=0.95,
        )
        self.play(
            LaggedStart(
                FadeIn(state["left_brain"], shift=UP * 0.05),
                FadeIn(state["brain_group"], shift=UP * 0.05),
                FadeIn(state["right_brain"], shift=UP * 0.05),
                lag_ratio=0.18,
            ),
            run_time=0.75,
        )
        self.wait(0.80)
        _transition_b_to_c(self, state)


class IntroClassicalView(_IntroNumberedScene, Scene):
    """Introduce the classical prefrontal account of working-memory substrates."""
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_d_layout()
        prior_group = getattr(self, "_intro_sensmem_b_transition_group", None)
        if prior_group is None:
            prior_group = _build_intro_sensmem_b_center_state()["final_group"]
        self.add(prior_group)
        self.wait(0.12)
        self.play(
            FadeOut(prior_group, shift=UP * 0.12),
            FadeIn(state["title"], shift=UP * 0.04),
            run_time=0.75,
        )
        self.play(Create(state["timeline_line"]), run_time=0.55)
        for dot, column in zip(state["dots"], state["columns"]):
            self.play(
                FadeIn(dot, scale=0.92),
                FadeIn(column, shift=UP * 0.04),
                run_time=0.72,
            )
        self.play(FadeIn(state["takeaway"], shift=UP * 0.04), run_time=0.55)
        self._intro_classical_state = state
        self.wait(4.00)


class IntroSensoryRecruitment(_IntroNumberedScene, Scene):
    """Introduce the sensory-recruitment account and its supporting studies."""
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_e_layout()
        dots = list(state["dots"])
        entries = list(state["entries"])
        previous_state = getattr(self, "_intro_classical_state", None)
        if previous_state is None:
            previous_state = _build_intro_d_layout()
            self.add(previous_state["final_group"])
            self.wait(0.12)
        classical_fade_group = Group(
            previous_state["title"],
            previous_state["dots"],
            previous_state["columns"],
            previous_state["takeaway"],
        )
        self.play(
            FadeIn(state["title"], shift=UP * 0.04),
            FadeOut(classical_fade_group, run_time=0.45),
            FadeOut(previous_state["timeline_line"], shift=UP * 0.04, run_time=0.45),
        )
        state["final_group"] = Group(state["title"], state["hero_figure"], state["content"])
        initial_anims = [
            FadeIn(dots[0], scale=0.92),
            FadeIn(entries[0], shift=RIGHT * 0.08),
        ]
        if len(entries) == 1:
            initial_anims.append(FadeIn(state["figure_column"], shift=RIGHT * 0.10))
        self.play(*initial_anims, run_time=0.75)
        self.wait(4.00)
        for idx in range(1, len(entries)):
            reveal_anims = [
                FadeIn(dots[idx], scale=0.92),
                FadeIn(entries[idx], shift=RIGHT * 0.08),
            ]
            if idx == len(entries) - 1:
                reveal_anims.append(FadeIn(state["figure_column"], shift=RIGHT * 0.10))
            self.play(*reveal_anims, run_time=0.90 if idx == len(entries) - 1 else 0.78)
            if idx < len(entries) - 1:
                self.wait(2.25)
        self._intro_sensory_recruitment_state = state
        self.wait(4.50)


class IntroResearchQuestion1(_IntroNumberedScene, Scene):
    """Present the first research question about the maintained representation format."""
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(0)
        previous_state = getattr(self, "_intro_sensory_recruitment_state", None)
        if previous_state is None:
            previous_state = _build_intro_e_layout()
            self.add(
                previous_state["title"],
                previous_state["hero_figure"],
                previous_state["dots"],
                previous_state["entries"],
                previous_state["figure_column"],
            )
            self.wait(0.12)
        sensory_fade_group = Group(
            previous_state["title"],
            previous_state["hero_figure"],
            previous_state["dots"],
            previous_state["entries"],
            previous_state["figure_column"],
        )
        self.play(
            FadeOut(sensory_fade_group, shift=UP * 0.04, run_time=0.55),
            FadeIn(state["header"], shift=UP * 0.04, run_time=0.70),
            FadeIn(state["content"], shift=UP * 0.04, run_time=0.95),
        )
        self.wait(8.25)


class IntroResearchQuestion2(_IntroNumberedScene, Scene):
    """Present the second research question about stimulus ecology and realism."""
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(1)
        self.play(FadeIn(state["header"], shift=UP * 0.04), run_time=0.70)
        self.play(
            FadeIn(state["cue_dots"][0], scale=0.92),
            FadeIn(state["bullet_items"][0], shift=UP * 0.03),
            FadeIn(state["visual_simple_block"], shift=RIGHT * 0.06, run_time=0.90),
        )
        self.wait(4.00)
        remaining_bullet_anims = []
        for idx in range(1, len(state["bullet_items"])):
            remaining_bullet_anims.extend(
                [
                    FadeIn(state["cue_dots"][idx], scale=0.92),
                    FadeIn(state["bullet_items"][idx], shift=UP * 0.03),
                ]
            )
        self.play(
            LaggedStart(
                FadeIn(state["visual_bridge_block"], shift=RIGHT * 0.06),
                FadeIn(state["visual_natural_block"], shift=RIGHT * 0.06),
                lag_ratio=0.16,
                run_time=0.95,
            ),
            LaggedStart(*remaining_bullet_anims, lag_ratio=0.10, run_time=1.00),
        )
        self.wait(4.25)


class IntroResearchQuestion3(_IntroNumberedScene, Scene):
    """Present the third research question about long-term-memory influences."""
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(2)
        full_group = Group(
            state["header"],
            state["cue_dots"],
            state["bullet_items"],
            state["visual_top_block_intro"],
            state["visual_matrix_block"],
        )
        self.play(FadeIn(full_group, run_time=0.10))
        self.wait(0.90)


# Backward-compatible names retained for ad hoc renders.
class IntroSensoryRepresentation(IntroSensoryMemoryRepresentationA):
    """Backward-compatible alias for `IntroSensoryMemoryRepresentationA`."""
    pass


class IntroMemoryRepresentation(IntroSensoryMemoryRepresentationB):
    """Backward-compatible alias for `IntroSensoryMemoryRepresentationB`."""
    pass


class IntroCognitiveProblemB(IntroSensoryMemoryRepresentationA):
    """Backward-compatible alias for `IntroSensoryMemoryRepresentationA`."""
    pass


class IntroCognitiveProblemC(IntroSensoryMemoryRepresentationB):
    """Backward-compatible alias for `IntroSensoryMemoryRepresentationB`."""
    pass


class IntroResearchQuestions(IntroResearchQuestion1):
    """Backward-compatible alias for the first intro research-question scene."""
    pass


# ── Master scene ──────────────────────────────────────────────────────────────

_INTRO_SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = (
    ("intro_cognitive_problem", IntroCognitiveProblemA),
    ("sens-mem-representations_a", IntroSensoryMemoryRepresentationA),
    ("sens-mem-representations_b", IntroSensoryMemoryRepresentationB),
    ("intro_classical_view", IntroClassicalView),
    ("intro_sensory_recruitment", IntroSensoryRecruitment),
    ("intro_research_question_1", IntroResearchQuestion1),
    ("intro_research_question_2", IntroResearchQuestion2),
    ("intro_research_question_3", IntroResearchQuestion3),
)


class Introduction(ThreeDScene):
    """Render the intro chapter as sequential save-section subscenes."""
    def _reset_section_scene_state(self, *, preserve_mobjects: bool = False) -> None:
        self.animations = None
        self.stop_condition = None
        self.moving_mobjects = []
        self.static_mobjects = []
        self.time_progression = None
        self.duration = 0.0
        self.last_t = 0.0
        self.queue = Queue()
        self.skip_animation_preview = False
        self.meshes = []
        self.camera_target = ORIGIN
        self.widgets = []
        self.updaters = []
        self.key_to_function_map = {}
        self.mouse_press_callbacks = []
        self.interactive_mode = False
        if not preserve_mobjects:
            self.mobjects = []
            self.foreground_mobjects = []

        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

        self.renderer.static_image = None

    def _reset_section_camera(self) -> None:
        self.renderer.camera = self.camera_class()
        self.set_camera_orientation(
            phi=0 * DEGREES,
            theta=-90 * DEGREES,
            gamma=0,
            zoom=1.0,
            frame_center=ORIGIN,
        )

    def _render_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        if carry_previous_frame and not config.save_sections:
            self.wait(_SECTION_HOLD)
        preserve_mobjects = (
            not config.save_sections
            and scene_cls in (IntroSensoryRecruitment, IntroResearchQuestion1)
        )
        if not preserve_mobjects:
            self.clear()
            if hasattr(self, "_intro_sensory_recruitment_state"):
                delattr(self, "_intro_sensory_recruitment_state")
        self._reset_section_scene_state(preserve_mobjects=preserve_mobjects)
        if scene_cls is not IntroSensoryRecruitment:
            self._reset_section_camera()
        self.camera.background_color = BG
        self.next_section(section_name)
        scene_cls.construct(self)

    def construct(self) -> None:
        for idx, (name, cls) in enumerate(_INTRO_SECTION_SCENES):
            self._render_section(name, cls, carry_previous_frame=idx > 0)


_HIDDEN_INTRO_SCENES = (
    IntroSensoryRepresentation,
    IntroMemoryRepresentation,
    IntroCognitiveProblemB,
    IntroCognitiveProblemC,
    IntroResearchQuestions,
)
for _scene_cls in _HIDDEN_INTRO_SCENES:
    _scene_cls.__module__ = "_intro_internal"
del _scene_cls
Introduction.__module__ = __name__
__all__ = [
    "IntroCognitiveProblemA",
    "IntroSensoryMemoryRepresentationA",
    "IntroSensoryMemoryRepresentationB",
    "IntroSensoryMemoryRepresentations",
    "IntroClassicalView",
    "IntroSensoryRecruitment",
    "IntroResearchQuestion1",
    "IntroResearchQuestion2",
    "IntroResearchQuestion3",
    "Introduction",
]
