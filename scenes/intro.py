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
RQ_BLUE = "#264C73"
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
_INTRO_FIG_DIR = REPO_ROOT / "assets" / "images" / "intro"
_BRAIN_ICON_PATH = REPO_ROOT / "assets" / "images" / "study2" / "brain_icon_sagittal.png"
_HEAD_BRAIN_PATH = REPO_ROOT / "assets" / "images" / "head_brain.png"
_REFERENCE_DIR = REPO_ROOT / "assets" / "images" / "references" / "working_memory"
_FUNAHASHI_1989_FIG = str(_INTRO_FIG_DIR / "funahashi1989a.png")
_JONIDES_1993_FIG = str(_INTRO_FIG_DIR / "jonides1993.png")
_AWH_JONIDES_2001_FIG = str(_REFERENCE_DIR / "awhjonides2001_spatial_wm.png")
_HARRISON_TONG_2009_FIG = str(_INTRO_FIG_DIR / "harrisontong2009.png")
_HARRISON_TONG_2009_PARADIGM_FIG = str(_INTRO_FIG_DIR / "harrisontong2009paradigm.png")
_CHRISTOPHEL_2012_FIG = str(_INTRO_FIG_DIR / "christophel2012.png")
_VISUAL_CORTEX_FIG = str(REPO_ROOT / "assets" / "images" / "visual_cortex_white.png")
_INTRO_HOOK_TARGET_FISH = str(_INTRO_STIM_DIR / "animal_fish-00.png")
_INTRO_HOOK_FOIL_FISH = str(_INTRO_STIM_DIR / "animal_fish-05.png")

_EXEMPLAR_CODE = "building_observatory"
_HOOK_CODE = "animal_fish"

# ── Intro constants ───────────────────────────────────────────────────────────
_SECTION_HOLD = 0.35
_ORDER = (5, 3, 7, 1, 8, 2, 6, 4)
_STRIP = (0, 2, 4, 6, 8)
_FROZEN_IDX = 4
_PRIOR_SPECS = ((0.62, 0.28), (0.74, 0.56), (0.86, 0.90))


def _seeded_pattern(seed: int) -> np.ndarray:
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
    return str(_INTRO_STIM_DIR / f"{code}-{idx:02d}.png")


def preferred_path(*candidates: Path | str) -> str:
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)
    return str(Path(candidates[0]))


def _img(path: str, height: float) -> ImageMobject:
    img = ImageMobject(path)
    img.height = height
    return img


def title_block(title_text: str, subtitle_text: str | None = None) -> VGroup:
    title = Tex(title_text, color=INK, font_size=34).to_edge(UP, buff=0.34)
    parts = [title]
    if subtitle_text is not None:
        subtitle = Tex(subtitle_text, color=INK, font_size=21)
        subtitle.next_to(title, DOWN, buff=0.14)
        parts.append(subtitle)
    return VGroup(*parts)



def make_callout(text: str, color: str, *, font_size: float = 23) -> VGroup:
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
        *[Tex(line, color=MGREY, font_size=ref_font_size) for line in ref_lines]
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


def make_paper_snapshot(
    image_path: str,
    label_text: str,
    ref_text: str,
    *,
    accent: str,
    height: float = 1.56,
) -> Group:
    image = ImageMobject(image_path)
    image.height = height
    image_card = RoundedRectangle(
        width=image.width + 0.26,
        height=image.height + 0.26,
        corner_radius=0.08,
        stroke_color=LGREY,
        stroke_width=1.2,
    ).set_fill(PANEL, opacity=1.0)
    image.move_to(image_card.get_center())
    image_frame = Group(image_card, image)
    label = Tex(label_text, color=accent, font_size=18)
    refs = Tex(ref_text, color=INK, font_size=14)
    return Group(image_frame, label, refs).arrange(DOWN, buff=0.10)


def brain_icon_with_evc(*, highlight_color: str = BLUE, scale_factor: float = 1.0) -> dict[str, Mobject]:
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
    brain = ImageMobject(str(_HEAD_BRAIN_PATH))
    brain.scale_to_fit_height(2.85 * scale_factor)
    return brain


def _pattern_color(value: float) -> ManimColor:
    clipped = max(-1.0, min(1.0, float(value)))
    if clipped < 0:
        return interpolate_color(ManimColor(PATTERN_WHITE), ManimColor(PATTERN_BLUE), abs(clipped))
    return interpolate_color(ManimColor(PATTERN_WHITE), ManimColor(PATTERN_RED), clipped)


def _mini_matrix(matrix: np.ndarray, *, cell: float = 0.12) -> VGroup:
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
    return (1.0 - alpha) * a + alpha * b


# ── Layout builders ───────────────────────────────────────────────────────────

def _build_intro_a_end_state() -> dict[str, Mobject]:
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
    title = title_block(
        r"\textbf{Classical view on the neural substrates of working memory}",
    )
    max_col_width = 3.48

    def _fit_width(mob: Mobject, width: float) -> Mobject:
        if mob.width > width:
            mob.scale_to_fit_width(width)
        return mob

    def _classical_column(
        title_text: str,
        claim_lines: tuple[str, ...],
        ref_lines: tuple[str, ...] = (),
        *,
        image_path: str | None = None,
        image_height: float = 1.56,
        image_ref_lines: tuple[str, ...] = (),
    ) -> Group:
        heading = _fit_width(
            Tex(rf"\textbf{{{title_text}}}", color=AMBER, font_size=18),
            max_col_width,
        )
        parts: list[Mobject] = [heading]
        if image_path is not None:
            image = ImageMobject(image_path)
            image.height = image_height
            if image.width > max_col_width:
                image.scale_to_fit_width(max_col_width)
            parts.append(image)
        if image_ref_lines:
            image_refs = VGroup(
                *[_fit_width(Tex(line, color=INK, font_size=12), max_col_width) for line in image_ref_lines]
            ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
            parts.append(image_refs)
        claim = VGroup(
            *[_fit_width(Tex(line, color=INK, font_size=15), max_col_width) for line in claim_lines]
        ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        divider = Line(ORIGIN, RIGHT * max_col_width, color=LGREY, stroke_width=0.9)
        divider.set_opacity(0.7)
        parts.append(claim)
        if ref_lines:
            refs = VGroup(
                *[_fit_width(Tex(line, color=INK, font_size=12), max_col_width) for line in ref_lines]
            ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
            parts.append(refs)
        parts.append(divider)
        column = Group(*parts).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        anchor_x = column.get_center()[0]
        for mob in parts:
            mob.set_x(anchor_x)
        return column

    columns = Group(
        _classical_column(
            "Monkey lesion studies",
            (
                "Delayed-response deficits after",
                "prefrontal lesions in monkeys",
            ),
            ("Jacobsen (1936)",),
        ),
        _classical_column(
            "Sustained activation",
            (
                "Persistent delay-period firing in dorsolateral PFC",
                "as neural signature of active maintenance",
            ),
            ("Goldman-Rakic (1995)", r"Constantinidis \& Procyk (2004)"),
            image_path=_FUNAHASHI_1989_FIG,
            image_height=2.20,
            image_ref_lines=("Funahashi et al. (1989)",),
        ),
        _classical_column(
            "Early human neuroimaging",
            (
                "Early PET and fMRI studies reported",
                "activations in frontal and parietal",
                "regions",
            ),
            (
                r"D'Esposito et al. (1995)",
                "Doyon et al. (1996)",
                "Courtney et al. (1997)",
            ),
            image_path=_JONIDES_1993_FIG,
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

    content = Group(timeline_line, dots, columns)
    takeaway = Tex(
        r"\textbf{Focus} on \textbf{association areas} as primary neural substrates of working memory",
        color=INK,
        font_size=22,
    )
    takeaway.scale_to_fit_width(min(takeaway.width, content.width + 0.15))
    takeaway.next_to(columns, DOWN, buff=0.34)
    takeaway.set_x(content.get_center()[0])
    return {
        "title": title,
        "timeline_line": timeline_line,
        "dots": dots,
        "columns": columns,
        "content": content,
        "takeaway": takeaway,
        "final_group": Group(title, content, takeaway),
    }


def _build_intro_e_layout() -> dict[str, Mobject]:
    title = title_block(
        r"\textbf{Sensory recruitment model}",
    )
    sensory_accent = "#18324D"

    def _fit_width(mob: Mobject, width: float) -> Mobject:
        if mob.width > width:
            mob.scale_to_fit_width(width)
        return mob

    def _sensory_text_entry(
        heading_lines: tuple[str, ...],
        body_lines: tuple[str, ...],
        ref_lines: tuple[str, ...],
        *,
        width: float = 4.95,
    ) -> Group:
        heading = VGroup(
            *[_fit_width(Tex(line, color=sensory_accent, font_size=20), width) for line in heading_lines]
        ).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        body = VGroup(
            *[_fit_width(Tex(line, color=INK, font_size=16), width) for line in body_lines]
        ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        refs = VGroup(
            *[_fit_width(Tex(line, color=MGREY, font_size=13), width) for line in ref_lines]
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        return Group(heading, body, refs).arrange(DOWN, buff=0.10, aligned_edge=LEFT)

    def _study_figure(
        image_path: str,
        ref_text: str | None,
        *,
        height: float = 2.24,
    ) -> Group:
        image = ImageMobject(image_path)
        image.height = height
        if ref_text is None:
            return Group(image)
        refs = Tex(ref_text, color=MGREY, font_size=14)
        return Group(image, refs).arrange(DOWN, buff=0.10)

    what_it_does = _sensory_text_entry(
        (
            r"\textbf{Sensory areas are actively recruited}",
        ),
        (
            "for working memory maintenance.",
        ),
        (
            r"Awh \& Jonides (2001); Pasternak \& Greenlee (2005)",
            r"Postle (2006)",
        ),
    )
    evidence_source = _sensory_text_entry(
        (
            r"\textbf{Multivariate Pattern Analysis studies}",
        ),
        (
            "show that remembered visual information can be decoded",
            "from visual cortex during maintenance.",
        ),
        (
            r"Harrison \& Tong (2009); Serences et al. (2009)",
            r"Christophel et al. (2012)",
        ),
    )
    entries = Group(what_it_does, evidence_source).arrange(DOWN, buff=1.28, aligned_edge=LEFT)
    dot_anchor_ys = [
        Group(entry[0], entry[1]).get_center()[1] + 0.16
        for entry in entries
    ]
    timeline_x = entries.get_left()[0] - 0.88
    line_margin = 0.82
    top_y = max(dot_anchor_ys) + line_margin
    bottom_y = min(dot_anchor_ys) - line_margin
    timeline_line = Line(
        np.array([timeline_x, top_y, 0.0]),
        np.array([timeline_x, bottom_y, 0.0]),
        color=MGREY,
        stroke_width=1.5,
    )
    timeline_line.set_opacity(0.78)
    dots = VGroup(
        *[
            Dot(radius=0.055, color=sensory_accent, stroke_width=0).move_to(
                np.array([timeline_x, dot_y, 0.0])
            )
            for dot_y in dot_anchor_ys
        ]
    )
    hero_figure = _study_figure(
        _VISUAL_CORTEX_FIG,
        None,
        height=0.78,
    )
    hero_figure.next_to(title, DOWN, buff=0.18)
    hero_figure.match_x(title)
    paradigm_figure = _study_figure(
        _HARRISON_TONG_2009_PARADIGM_FIG,
        None,
        height=2.18,
    )
    harrison_figure = _study_figure(
        _HARRISON_TONG_2009_FIG,
        None,
        height=2.22,
    )
    christophel_figure = _study_figure(
        _CHRISTOPHEL_2012_FIG,
        r"Christophel et al. (2012)",
        height=1.98,
    )
    top_row = Group(harrison_figure, paradigm_figure).arrange(RIGHT, buff=0.22, aligned_edge=UP)
    harrison_ref = Tex(r"Harrison \& Tong (2009)", color=MGREY, font_size=14)
    harrison_ref.next_to(top_row, DOWN, buff=0.12)
    harrison_ref.set_x(top_row.get_center()[0])
    separator = Line(ORIGIN, RIGHT * (top_row.width * 0.88), color=LGREY, stroke_width=1.0)
    separator.set_opacity(0.42)
    separator.next_to(harrison_ref, DOWN, buff=0.12)
    separator.set_x(top_row.get_center()[0])
    christophel_figure.next_to(separator, DOWN, buff=0.16)
    christophel_figure.set_x(top_row.get_center()[0])
    upper_row_shift = DOWN * (top_row.height * 0.10)
    top_row.shift(upper_row_shift)
    harrison_ref.shift(upper_row_shift)
    separator.shift(upper_row_shift)
    figure_column = Group(top_row, harrison_ref, separator, christophel_figure)
    figure_column.next_to(entries, RIGHT, buff=1.02, aligned_edge=UP)
    figure_column.set_y(entries.get_center()[1])
    left_column_shift = LEFT * 0.34
    timeline_line.shift(left_column_shift)
    dots.shift(left_column_shift)
    entries.shift(left_column_shift)

    content = Group(timeline_line, dots, entries, figure_column)
    content.next_to(hero_figure, DOWN, buff=0.24)
    content.set_x(-0.26)
    dot_mid_y = 0.5 * (dots[0].get_center()[1] + dots[1].get_center()[1])
    content.shift(DOWN * dot_mid_y)
    return {
        "title": title,
        "hero_figure": hero_figure,
        "timeline_line": timeline_line,
        "dots": dots,
        "entries": entries,
        "figure_column": figure_column,
        "content": content,
        "final_group": Group(title, hero_figure, content),
    }


_INTRO_RESEARCH_QUESTIONS: tuple[dict[str, str], ...] = (
    {
        "kicker": "Research question 1",
        "title": "Representational format",
        "subtitle": "Is the maintained code still sensory-like?",
        "bullet_1": "Early cross-decoding suggested shared sensory codes.",
        "bullet_2": "Recent work finds weaker generalization and dynamic delay codes.",
        "bullet_3": "A separate perception session enables direct format comparison.",
        "accent": RQ_BLUE,
    },
    {
        "kicker": "Research question 2",
        "title": "Ecological validity",
        "subtitle": "Does it generalize beyond simple lab stimuli?",
        "bullet_1": "Most evidence comes from orientations, colors, or locations.",
        "bullet_2": "Stimulus properties may change how sensory and memory codes align.",
        "bullet_3": "Naturalistic WM evidence remains limited and hard to obtain.",
        "accent": RQ_RED,
    },
    {
        "kicker": "Research question 3",
        "title": "Long-term memory",
        "subtitle": "Do LTM traces modulate the WM code?",
        "bullet_1": "Familiarity and meaning can improve working-memory performance.",
        "bullet_2": "WM and LTM retrieval may share sensory-like codes in EVC.",
        "bullet_3": "LTM may make WM more sensory-like or shift processing elsewhere.",
        "accent": RQ_GREEN,
    },
)


def _intro_question_context_block(spec: dict[str, str]) -> VGroup:
    cue_lines = VGroup(
        *[
            Tex(text, color=INK, font_size=17)
            for text in (spec["bullet_1"], spec["bullet_2"], spec["bullet_3"])
        ]
    ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    for line in cue_lines:
        if line.width > 4.90:
            line.scale_to_fit_width(4.90)

    cue_rule = Line(UP * 0.5, DOWN * 0.5, color=spec["accent"], stroke_width=1.4)
    cue_rule.set(height=max(0.92, cue_lines.height - 0.04))
    cue_rule.set_stroke(opacity=0.52)
    cue_dot = Dot(radius=0.028, color=spec["accent"], stroke_width=0)
    cue_dot.move_to(cue_rule.get_top() + UP * 0.11)
    cue_anchor = VGroup(cue_rule, cue_dot)
    return VGroup(cue_anchor, cue_lines).arrange(RIGHT, buff=0.20, aligned_edge=UP)


def _intro_question_matrix(matrix: np.ndarray, label_text: str) -> VGroup:
    cells = _mini_matrix(matrix, cell=0.15)
    cells.scale(1.60)
    cells.set_opacity(0.95)
    label = Tex(label_text, color=INK, font_size=15)
    if label.width > max(1.90, cells.width * 1.50):
        label.scale_to_fit_width(max(1.90, cells.width * 1.50))
    label.next_to(cells, DOWN, buff=0.10)
    return VGroup(cells, label)


def _build_intro_question_visual_format(spec: dict[str, str]) -> VGroup:
    source = _intro_question_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT, "perception")
    top_target = _intro_question_matrix(_REPRESENTATION_SENSORY_PATTERN_RIGHT, "sensory-like")
    bottom_target = _intro_question_matrix(_REPRESENTATION_MEMORY_PATTERN, "transformed")

    source.move_to(LEFT * 1.65)
    top_target.move_to(RIGHT * 1.45 + UP * 0.92)
    bottom_target.move_to(RIGHT * 1.45 + DOWN * 0.92)

    branch = Dot(radius=0.038, color=spec["accent"], stroke_width=0).move_to(LEFT * 0.12)
    branch_lines = VGroup(
        Line(
            source[0].get_right() + RIGHT * 0.16,
            branch.get_center(),
            color=LGREY,
            stroke_width=1.0,
        ),
        Line(
            branch.get_center(),
            top_target[0].get_left() + LEFT * 0.14,
            color=spec["accent"],
            stroke_width=1.15,
        ).set_stroke(opacity=0.74),
        Line(
            branch.get_center(),
            bottom_target[0].get_left() + LEFT * 0.14,
            color=LGREY,
            stroke_width=1.0,
        ).set_stroke(opacity=0.82),
    )

    caption = Tex(r"\textbf{Two plausible mappings}", color=INK, font_size=15)
    caption.move_to(np.array([0.02, 1.78, 0.0]))
    return VGroup(caption, branch_lines, branch, source, top_target, bottom_target)


def _build_intro_question_visual_ecology(spec: dict[str, str]) -> VGroup:
    orientation = Line(LEFT * 0.24, RIGHT * 0.24, color=spec["accent"], stroke_width=2.4)
    orientation.rotate(PI / 5)
    color_dot = Dot(radius=0.11, color=spec["accent"], stroke_width=0).set_opacity(0.82)
    location = VGroup(
        Circle(radius=0.17, color=spec["accent"], stroke_width=1.2).set_fill(opacity=0.0),
        Line(UP * 0.08, DOWN * 0.08, color=spec["accent"], stroke_width=1.0),
        Line(LEFT * 0.08, RIGHT * 0.08, color=spec["accent"], stroke_width=1.0),
    )
    simple_glyphs = VGroup(orientation, color_dot, location).arrange(RIGHT, buff=0.28)
    simple_label = Tex("simple tasks", color=INK, font_size=15)
    simple = VGroup(simple_label, simple_glyphs).arrange(DOWN, buff=0.14)
    simple.move_to(LEFT * 1.92)

    cloud_points = (
        (-0.72, 0.34),
        (-0.48, 0.72),
        (-0.12, 0.46),
        (0.18, 0.78),
        (0.56, 0.44),
        (-0.58, -0.02),
        (-0.18, -0.20),
        (0.22, 0.02),
        (0.66, -0.16),
        (-0.30, -0.58),
        (0.14, -0.50),
        (0.50, -0.72),
    )
    accent_ids = {1, 3, 7, 10}
    radii = (0.06, 0.075, 0.05, 0.068, 0.058, 0.05, 0.055, 0.062, 0.048, 0.052, 0.06, 0.05)
    cloud_dots = VGroup(
        *[
            Dot(
                radius=radii[idx],
                color=spec["accent"] if idx in accent_ids else RQ_MUTED,
                stroke_width=0,
            ).move_to(np.array([x, y, 0.0]))
            for idx, (x, y) in enumerate(cloud_points)
        ]
    )
    cloud_lines = VGroup(
        *[
            Line(
                cloud_dots[i].get_center(),
                cloud_dots[j].get_center(),
                color=LGREY,
                stroke_width=0.9,
            ).set_stroke(opacity=0.45)
            for i, j in ((0, 5), (1, 2), (2, 7), (5, 9), (6, 10), (7, 8), (10, 11))
        ]
    )
    natural_cluster = VGroup(cloud_lines, cloud_dots)
    natural_label = Tex("natural scenes", color=INK, font_size=15)
    natural = Group(natural_label, natural_cluster).arrange(DOWN, buff=0.14)
    natural.move_to(RIGHT * 1.56)

    bridge = Line(
        simple_glyphs.get_right() + RIGHT * 0.22,
        natural_cluster.get_left() + LEFT * 0.22,
        color=LGREY,
        stroke_width=1.0,
    ).set_stroke(opacity=0.7)
    bridge_dots = VGroup(
        *[
            Dot(radius=0.022, color=LGREY, stroke_width=0).move_to(
                bridge.point_from_proportion(alpha)
            )
            for alpha in (0.34, 0.68)
        ]
    )
    caption = Tex(r"\textbf{From canonical stimuli to rich scenes}", color=INK, font_size=15)
    caption.move_to(np.array([0.0, 1.72, 0.0]))
    return Group(caption, bridge, bridge_dots, simple, natural)


def _build_intro_question_visual_ltm(spec: dict[str, str]) -> VGroup:
    brain_parts = brain_icon_with_evc(highlight_color=spec["accent"], scale_factor=0.72)
    brain = brain_parts["group"]
    brain.move_to(RIGHT * 1.55 + DOWN * 0.08)

    wm_cluster = VGroup(
        Dot(radius=0.055, color=spec["accent"], stroke_width=0),
        Dot(radius=0.040, color=RQ_MUTED, stroke_width=0),
        Dot(radius=0.048, color=RQ_MUTED, stroke_width=0),
        Dot(radius=0.036, color=RQ_MUTED, stroke_width=0),
    )
    wm_cluster[0].move_to(np.array([-1.10, 0.88, 0.0]))
    wm_cluster[1].move_to(np.array([-0.80, 1.05, 0.0]))
    wm_cluster[2].move_to(np.array([-0.62, 0.74, 0.0]))
    wm_cluster[3].move_to(np.array([-0.92, 0.54, 0.0]))
    wm_label = Tex("working memory", color=INK, font_size=15)
    wm_label.next_to(wm_cluster, UP, buff=0.14)

    ltm_cluster = VGroup(
        Dot(radius=0.050, color=RQ_MUTED, stroke_width=0),
        Dot(radius=0.062, color=spec["accent"], stroke_width=0),
        Dot(radius=0.046, color=RQ_MUTED, stroke_width=0),
        Dot(radius=0.040, color=RQ_MUTED, stroke_width=0),
        Dot(radius=0.056, color=RQ_MUTED, stroke_width=0),
        Dot(radius=0.042, color=RQ_MUTED, stroke_width=0),
    )
    ltm_positions = (
        (-1.14, -0.56),
        (-0.90, -0.88),
        (-0.56, -0.72),
        (-0.68, -1.14),
        (-0.34, -0.96),
        (-0.18, -0.60),
    )
    for dot, (x, y) in zip(ltm_cluster, ltm_positions):
        dot.move_to(np.array([x, y, 0.0]))
    ltm_label = Tex("long-term memory", color=INK, font_size=15)
    ltm_label.next_to(ltm_cluster, DOWN, buff=0.14)

    wm_line = Line(
        wm_cluster.get_right() + RIGHT * 0.18,
        brain.get_left() + LEFT * 0.08 + UP * 0.24,
        color=LGREY,
        stroke_width=1.0,
    ).set_stroke(opacity=0.78)
    ltm_line = DashedLine(
        ltm_cluster.get_right() + RIGHT * 0.16,
        brain.get_left() + LEFT * 0.08 + DOWN * 0.18,
        dash_length=0.09,
        color=LGREY,
        stroke_width=1.0,
    ).set_stroke(opacity=0.72)

    convergence = Dot(radius=0.040, color=spec["accent"], stroke_width=0)
    convergence.move_to(brain.get_left() + LEFT * 0.10 + DOWN * 0.02)
    convergence_halo = Circle(radius=0.14, color=spec["accent"], stroke_width=1.0)
    convergence_halo.move_to(convergence.get_center())
    convergence_halo.set_stroke(opacity=0.46)

    caption = Tex(r"\textbf{Prior traces may bias the maintained code}", color=INK, font_size=15)
    caption.move_to(np.array([0.05, 1.72, 0.0]))
    return Group(
        caption,
        wm_line,
        ltm_line,
        convergence_halo,
        convergence,
        brain,
        wm_cluster,
        wm_label,
        ltm_cluster,
        ltm_label,
    )


def _build_intro_question_visual(question_idx: int, spec: dict[str, str]) -> VGroup:
    if question_idx == 0:
        return _build_intro_question_visual_format(spec)
    if question_idx == 1:
        return _build_intro_question_visual_ecology(spec)
    return _build_intro_question_visual_ltm(spec)


def _build_intro_question_layout(question_idx: int) -> dict[str, Mobject]:
    spec = _INTRO_RESEARCH_QUESTIONS[question_idx]
    kicker = VGroup(
        Dot(radius=0.042, color=spec["accent"], stroke_width=0),
        Tex(spec["kicker"], color=INK, font_size=18),
    ).arrange(RIGHT, buff=0.12)
    header_rule = Line(ORIGIN, RIGHT * 4.90, color=LGREY, stroke_width=1.0)
    header_rule.set_stroke(opacity=0.72)
    header = VGroup(kicker, header_rule).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)

    question_title = Tex(rf"\textbf{{{spec['title']}}}", color=spec["accent"], font_size=19)
    if question_title.width > 5.05:
        question_title.scale_to_fit_width(5.05)

    question_claim = Tex(spec["subtitle"], color=INK, font_size=31)
    if question_claim.width > 5.35:
        question_claim.scale_to_fit_width(5.35)

    context_block = _intro_question_context_block(spec)
    text_column = VGroup(question_title, question_claim, context_block).arrange(
        DOWN,
        buff=0.24,
        aligned_edge=LEFT,
    )
    text_group = text_column

    visual = _build_intro_question_visual(question_idx, spec)
    visual.scale(1.07)
    visual.shift(DOWN * 0.08)

    question_card = Group(text_group, visual).arrange(RIGHT, buff=0.92, aligned_edge=UP)
    max_width = config.frame_width - 0.90
    if question_card.width > max_width:
        question_card.scale_to_fit_width(max_width)
    question_card.move_to(DOWN * 0.44)
    header.next_to(question_card, UP, buff=0.46, aligned_edge=LEFT)

    return {
        "header": header,
        "question_card": question_card,
        "content": question_card,
        "final_group": Group(header, question_card),
    }


# ── B → C transition ──────────────────────────────────────────────────────────

def _transition_b_to_c(scene: Scene, b_state: dict[str, Mobject]) -> None:
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
                + LEFT * (0.015 * head.width)
                + UP * (0.18 * head.height)
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
        snapshot_matrices = VGroup(
            _mini_matrix(_REPRESENTATION_SENSORY_PATTERN_LEFT, cell=_MATRIX_CELL * 0.72),
            _mini_matrix(_REPRESENTATION_MEMORY_PATTERN, cell=_MATRIX_CELL * 0.72),
            _mini_matrix(_REPRESENTATION_SENSORY_PATTERN_RIGHT, cell=_MATRIX_CELL * 0.72),
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
                    ReplacementTransform(
                        moving_copy,
                        target,
                        run_time=morph_run_time,
                        rate_func=smooth,
                    ),
                )
            ]
            self.add_fixed_in_frame_mobjects(moving_copy, target)
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
            *snapshot_matrices,
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
    equation_state = _build_intro_sensmem_equation(
        labels_below=True,
        anchor_corner=False,
        matrix_buff=1.16,
    )
    target_row = Group(equation_state["matrices"], equation_state["labels"])
    target_row.move_to(np.array([0.0, -0.02, 0.0]))

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

    return {
        "equation_state": equation_state,
        "cards": cards,
        "final_group": Group(cards, equation_state["matrices"], equation_state["labels"]),
    }


def _build_intro_sensmem_b_end_state() -> dict[str, Mobject]:
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

        def transport_card(
            source: Group,
            card: Group,
            target_center: np.ndarray,
            *,
            run_time: float,
        ) -> list[Animation]:
            start_center = card.get_center().copy()

            def update_card(mob: Group, alpha: float) -> None:
                reveal_alpha = np.clip(alpha / 0.06, 0.0, 1.0)
                move_alpha = smooth(np.clip((alpha - 0.06) / 0.94, 0.0, 1.0))
                center = interpolate(start_center, target_center, move_alpha)
                mob[0].move_to(center)
                mob[1].move_to(center)
                mob[0].set_fill(opacity=reveal_alpha)
                mob[0].set_stroke(opacity=reveal_alpha)
                mob[1].set_opacity(reveal_alpha)

            return [
                FadeOut(
                    source,
                    run_time=0.06,
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

        def similar_cell_ids(threshold: float = 0.18) -> list[int]:
            left_vals = _REPRESENTATION_SENSORY_PATTERN_LEFT.flatten()
            memory_vals = _REPRESENTATION_MEMORY_PATTERN.flatten()
            right_vals = _REPRESENTATION_SENSORY_PATTERN_RIGHT.flatten()
            return [
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
                equation_state["matrices"][matrix_index][cell_index]
                for matrix_index in range(3)
                for cell_index in similar_cell_ids()
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
        self.add_fixed_in_frame_mobjects(*contour_group)
        self.play(
            LaggedStart(
                *[Create(contour) for contour in contour_group],
                lag_ratio=0.04,
            ),
            run_time=3.0,
        )
        self.wait(2.0)
        self.play(FadeOut(contour_group, run_time=0.25))
        self._intro_sensmem_b_transition_group = Group(
            target_cards.copy(),
            equation_state["matrices"].copy(),
            equation_state["labels"].copy(),
        )
        self.wait(0.75)


class IntroSensoryMemoryRepresentations(Scene):
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
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_e_layout()
        first_dot, second_dot = state["dots"]
        first_entry, second_entry = state["entries"]
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
        )
        self.play(
            Transform(previous_state["timeline_line"], state["timeline_line"]),
            run_time=0.85,
        )
        self.play(
            FadeIn(state["hero_figure"], shift=UP * 0.03),
            FadeIn(first_dot, scale=0.92),
            FadeIn(first_entry, shift=RIGHT * 0.08),
            run_time=0.75,
        )
        self.wait(4.00)
        self.play(
            FadeIn(second_dot, scale=0.92),
            FadeIn(second_entry, shift=RIGHT * 0.08),
            FadeIn(state["figure_column"], shift=RIGHT * 0.10),
            run_time=0.90,
        )
        self.wait(4.50)


class IntroResearchQuestion1(_IntroNumberedScene, Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(0)
        comparison_state = _build_intro_sensmem_b_hook_state()
        self.play(FadeIn(state["header"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["question_card"], shift=UP * 0.04), run_time=0.90)
        self.wait(0.90)
        self.play(
            FadeOut(state["header"], shift=UP * 0.04, run_time=0.45),
            FadeOut(state["question_card"], shift=UP * 0.04, run_time=0.55),
            FadeIn(comparison_state["title_group"], shift=UP * 0.03, run_time=0.60),
            FadeIn(comparison_state["column_headers"], shift=UP * 0.03, run_time=0.60),
            FadeIn(comparison_state["row_panels"][0], scale=0.98, run_time=0.60),
            FadeIn(comparison_state["row_labels"][0], shift=RIGHT * 0.04, run_time=0.60),
            LaggedStart(
                FadeIn(comparison_state["top_row"][0], shift=UP * 0.04),
                FadeIn(comparison_state["top_row"][1], shift=UP * 0.04),
                lag_ratio=0.12,
                run_time=0.72,
            ),
        )
        self.wait(0.65)
        self.play(
            FadeIn(comparison_state["row_panels"][1], scale=0.98, run_time=0.55),
            FadeIn(comparison_state["row_labels"][1], shift=RIGHT * 0.04, run_time=0.55),
            LaggedStart(
                FadeIn(comparison_state["bottom_row"][0], shift=UP * 0.04),
                FadeIn(comparison_state["bottom_row"][1], shift=UP * 0.04),
                lag_ratio=0.12,
                run_time=0.68,
            ),
        )
        self.wait(3.15)


class IntroResearchQuestion2(_IntroNumberedScene, Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(1)
        self.play(FadeIn(state["header"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["question_card"], shift=UP * 0.04), run_time=0.90)
        self.wait(4.25)


class IntroResearchQuestion3(_IntroNumberedScene, Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(2)
        self.play(FadeIn(state["header"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["question_card"], shift=UP * 0.04), run_time=0.90)
        self.wait(4.25)


# Backward-compatible names retained for ad hoc renders.
class IntroSensoryRepresentation(IntroSensoryMemoryRepresentationA):
    pass


class IntroMemoryRepresentation(IntroSensoryMemoryRepresentationB):
    pass


class IntroCognitiveProblemB(IntroSensoryMemoryRepresentationA):
    pass


class IntroCognitiveProblemC(IntroSensoryMemoryRepresentationB):
    pass


class IntroResearchQuestions(IntroResearchQuestion1):
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
        preserve_mobjects = scene_cls is IntroSensoryRecruitment
        if not preserve_mobjects:
            self.clear()
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
