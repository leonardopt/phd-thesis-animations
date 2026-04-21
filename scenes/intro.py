"""
Introduction — sectioned production render.

Render from this file to keep all introduction outputs in the same
`media/videos/01_intro/...` folder.

Production render:
    uv run manim scenes/intro.py Introduction -ql --save_sections
"""
from __future__ import annotations

from pathlib import Path
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


# ── Palette ───────────────────────────────────────────────────────────────────
BG = WHITE
INK = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
BLUE = "#2563EB"
AMBER = "#D97706"
GREEN = "#16A34A"
RED = "#DC2626"
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
_HARRISON_TONG_2009_FIG = str(_REFERENCE_DIR / "harrisontong2009_decoding.png")

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


_SENSORY_PATTERN_LEFT = _seeded_pattern(11)
_MEMORY_PATTERN = _seeded_pattern(12)
_SENSORY_PATTERN_RIGHT = _seeded_pattern(13)


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
        subtitle = Tex(subtitle_text, color=MGREY, font_size=21)
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
    subtitle_color: str = MGREY,
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
        *[Tex(line, color=MGREY, font_size=14) for line in ref_lines]
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
    refs = Tex(ref_text, color=MGREY, font_size=14)
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
    left_image = _img(
        preferred_path(
            REPO_ROOT / "assets" / "images" / "ANI-FIS-T00.jpeg",
            REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-T00.jpeg",
            _INTRO_STIM_DIR / "animal_fish-00.png",
        ),
        image_h,
    )
    right_image = _img(
        preferred_path(
            REPO_ROOT / "assets" / "images" / "ANI-FIS-D01.jpeg",
            REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-D01.jpeg",
            _INTRO_STIM_DIR / "animal_fish-01.png",
        ),
        image_h,
    )

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
    time_label = MathTex("t", color=MGREY, font_size=24)
    time_label.next_to(phase_rule.get_right(), UP + LEFT, buff=0.10)

    left_brain = patterned_head(_SENSORY_PATTERN_LEFT, scale_factor=0.56)
    center_brain = patterned_head(_MEMORY_PATTERN, scale_factor=0.56)
    right_brain = patterned_head(_SENSORY_PATTERN_RIGHT, scale_factor=0.56)
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
    time_label = MathTex("t", color=MGREY, font_size=24)
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
    max_col_width = 2.95

    def _fit_width(mob: Mobject, width: float) -> Mobject:
        if mob.width > width:
            mob.scale_to_fit_width(width)
        return mob

    def _classical_column(
        title_text: str,
        claim_lines: tuple[str, ...],
        ref_lines: tuple[str, ...],
        *,
        image_path: str | None = None,
        image_height: float = 1.56,
    ) -> Group:
        heading = _fit_width(
            Tex(rf"\textbf{{{title_text}}}", color=AMBER, font_size=20),
            max_col_width,
        )
        parts: list[Mobject] = [heading]
        if image_path is not None:
            image = ImageMobject(image_path)
            image.height = image_height
            if image.width > max_col_width:
                image.scale_to_fit_width(max_col_width)
            parts.append(image)
        claim = VGroup(
            *[_fit_width(Tex(line, color=INK, font_size=17), max_col_width) for line in claim_lines]
        ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        refs = VGroup(
            *[_fit_width(Tex(line, color=MGREY, font_size=13), max_col_width) for line in ref_lines]
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        divider = Line(ORIGIN, RIGHT * max_col_width, color=LGREY, stroke_width=0.9)
        divider.set_opacity(0.7)
        parts.extend([claim, refs, divider])
        return Group(*parts).arrange(DOWN, buff=0.10, aligned_edge=LEFT)

    columns = Group(
        _classical_column(
            "Monkey lesions",
            ("Prefrontal damage impaired", "delayed-response performance"),
            ("Jacobsen (1936)", "Harlow (1952)"),
        ),
        _classical_column(
            "Persistent firing",
            ("Delay-period firing in dorsolateral PFC", "became the canonical maintenance signal"),
            (r"Fuster \& Alexander (1971)", "Funahashi et al. (1989, 1993)"),
            image_path=_FUNAHASHI_1989_FIG,
            image_height=1.42,
        ),
        _classical_column(
            "Human imaging",
            ("PET and fMRI reinforced a broader", "association-cortex account"),
            (r"Jonides et al. (1993); D'Esposito et al. (1995)", "Courtney et al. (1997, 1998)"),
            image_path=_JONIDES_1993_FIG,
            image_height=1.30,
        ),
    )

    dot_xs = (-4.15, 0.0, 4.15)
    timeline_y = title.get_bottom()[1] - 0.72
    timeline_line = Line(
        np.array([dot_xs[0] - 1.05, timeline_y, 0.0]),
        np.array([dot_xs[-1] + 1.05, timeline_y, 0.0]),
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
    takeaway = make_callout(
        "Early sensory cortex was not treated as the primary substrate of maintenance.",
        AMBER,
        font_size=22,
    )
    takeaway.next_to(columns, DOWN, buff=0.34)
    takeaway.align_to(timeline_line, LEFT)
    return {
        "title": title,
        "content": content,
        "takeaway": takeaway,
        "final_group": Group(title, content, takeaway),
    }


def _build_intro_e_layout() -> dict[str, Mobject]:
    title = title_block(
        r"\textbf{Sensory recruitment account}",
        "Theory papers and MVPA studies argued that maintained content can be represented in visual cortex",
    )
    paper_gallery = Group(
        make_paper_snapshot(
            _AWH_JONIDES_2001_FIG,
            "theory shift",
            r"Awh \& Jonides (2001)",
            accent=BLUE,
            height=1.84,
        ),
        make_paper_snapshot(
            _HARRISON_TONG_2009_FIG,
            "orientation decoding",
            r"Harrison \& Tong (2009)",
            accent=BLUE,
            height=1.84,
        ),
    ).arrange(RIGHT, buff=0.28, aligned_edge=UP)
    paper_stack = paper_gallery

    evidence = VGroup(
        make_literature_entry(
            "Theory shift",
            ("Working memory may reuse the same sensory", "circuits engaged during perception"),
            (r"Awh \& Jonides (2001); Pasternak \& Greenlee (2005)", "Postle (2006)"),
            accent=BLUE,
        ),
        make_literature_entry(
            "MVPA turning point",
            ("Multivoxel patterns can reveal feature", "information that mean activation can miss"),
            (r"Haynes \& Rees (2006); Norman et al. (2006)",),
            accent=BLUE,
        ),
        make_literature_entry(
            "Seminal delay decoding",
            ("Remembered visual features were decoded from", "early visual cortex during the delay"),
            (r"Harrison \& Tong (2009); Serences et al. (2009)",),
            accent=BLUE,
        ),
        make_literature_entry(
            "Open question",
            ("Decodable delay activity did not by itself", "prove a sensory-like or necessary code"),
            (r"Christophel et al. (2017)", r"Curtis \& Sprague (2021)"),
            accent=RED,
        ),
    ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

    content = Group(paper_stack, evidence).arrange(RIGHT, buff=0.92, aligned_edge=UP)
    content.scale(1.04)
    content.next_to(title, DOWN, buff=0.30)
    content.shift(DOWN * 0.18)
    takeaway = make_callout(
        "Delay-period information is decodable from early visual cortex, but its format remains open.",
        BLUE,
        font_size=21,
    )
    takeaway.next_to(content, DOWN, buff=0.44)
    takeaway.align_to(content, LEFT)
    return {
        "title": title,
        "content": content,
        "takeaway": takeaway,
        "final_group": Group(title, content, takeaway),
    }


_INTRO_RESEARCH_QUESTIONS: tuple[dict[str, str], ...] = (
    {
        "kicker": "Research question 1",
        "title": "Representational format",
        "subtitle": "Sensory-like or memory-specific?",
        "bullet_1": "Cross-decoding suggests a shared sensory code.",
        "bullet_2": "But delay codes may be transformed or dynamic.",
        "bullet_3": "We test this with an independent perception session.",
        "focus_primary": "cross-session decoding",
        "focus_secondary": "perception -> memory",
        "focus_tag": "format test",
        "accent": BLUE,
    },
    {
        "kicker": "Research question 2",
        "title": "Naturalistic stimuli",
        "subtitle": "Beyond simple laboratory stimuli?",
        "bullet_1": "Most evidence comes from gratings, colors, or locations.",
        "bullet_2": "Naturalistic sensory recruitment is still largely untested.",
        "bullet_3": "We use fine-grained object-scenes with perceptual demands.",
        "focus_primary": "naturalistic object-scenes",
        "focus_secondary": "fine-grained discrimination",
        "focus_tag": "ecological test",
        "accent": AMBER,
    },
    {
        "kicker": "Research question 3",
        "title": "Long-term memory",
        "subtitle": "Does long-term memory reshape WM representations?",
        "bullet_1": "Familiarity and meaning often improve working memory.",
        "bullet_2": "WM and LTM may rely on partially overlapping codes.",
        "bullet_3": "We test whether repetition reshapes EVC memory signals.",
        "focus_primary": "repeated vs novel items",
        "focus_secondary": "LTM-strength manipulation",
        "focus_tag": "modulation test",
        "accent": GREEN,
    },
)


def _build_intro_question_layout(question_idx: int) -> dict[str, Mobject]:
    spec = _INTRO_RESEARCH_QUESTIONS[question_idx]
    kicker = Tex(spec["kicker"], color=spec["accent"], font_size=20)
    kicker.to_edge(UP, buff=0.34)
    header = VGroup(
        kicker,
        Line(LEFT * 1.8, RIGHT * 1.8, color=LGREY, stroke_width=1.0),
    ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    header.to_edge(UP, buff=0.34)
    header.shift(LEFT * 2.95)

    question_title_row = VGroup(
        Dot(radius=0.045, color=spec["accent"]),
        Tex(rf"\textbf{{{spec['title']}}}", color=spec["accent"], font_size=22),
    ).arrange(RIGHT, buff=0.12)

    question_claim = Tex(spec["subtitle"], color=INK, font_size=24)

    def _question_bullet(text: str) -> VGroup:
        dot = Dot(radius=0.034, color=spec["accent"], stroke_width=0)
        line = Tex(text, color=INK, font_size=18)
        if line.width > 5.45:
            line.scale_to_fit_width(5.45)
        return VGroup(dot, line).arrange(RIGHT, buff=0.14, aligned_edge=UP)

    question_bullets = VGroup(
        _question_bullet(spec["bullet_1"]),
        _question_bullet(spec["bullet_2"]),
        _question_bullet(spec["bullet_3"]),
    ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)

    question_divider = Line(
        ORIGIN,
        RIGHT * max(5.2, question_claim.width, question_bullets.width),
        color=LGREY,
        stroke_width=1.0,
    )
    question_card = VGroup(
        question_title_row,
        question_claim,
        question_bullets,
        question_divider,
    ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)

    focus_title_row = VGroup(
        Dot(radius=0.040, color=MGREY),
        Tex(r"\textbf{Study 2 test}", color=INK, font_size=18),
    ).arrange(RIGHT, buff=0.12)
    focus_copy = VGroup(
        Tex(spec["focus_primary"], color=INK, font_size=22),
        Tex(spec["focus_secondary"], color=MGREY, font_size=16),
        Tex(spec["focus_tag"], color=spec["accent"], font_size=18),
    ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    focus_divider = Line(
        ORIGIN,
        RIGHT * max(3.4, focus_copy.width),
        color=LGREY,
        stroke_width=1.0,
    )
    focus_panel = VGroup(
        focus_title_row,
        focus_copy,
        focus_divider,
    ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

    content = Group(question_card, focus_panel).arrange(RIGHT, buff=1.00, aligned_edge=UP)
    content.next_to(header, DOWN, buff=0.42, aligned_edge=LEFT)
    content.shift(RIGHT * 0.55)

    return {
        "header": header,
        "question_card": question_card,
        "focus_panel": focus_panel,
        "content": content,
        "final_group": Group(header, content),
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

class IntroCognitiveProblemA(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        def _frame(path: str) -> ImageMobject:
            img = ImageMobject(path)
            img.height = 5.80
            img.move_to(ORIGIN)
            return img

        target = _frame(
            preferred_path(
                REPO_ROOT / "assets" / "images" / "ANI-FIS-T00.jpeg",
                REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-T00.jpeg",
                _INTRO_STIM_DIR / "animal_fish-00.png",
            )
        )
        foil = _frame(
            preferred_path(
                REPO_ROOT / "assets" / "images" / "ANI-FIS-D01.jpeg",
                REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-D01.jpeg",
                _INTRO_STIM_DIR / "animal_fish-01.png",
            )
        )

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


class IntroSensoryRepresentation(ThreeDScene):
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

        axis_label = MathTex("t", color=MGREY, font_size=28).move_to(
            screen_aligned_point(x4, right=0.38, up=0.10)
        )
        axis_label.set_z_index(15)

        travel = ValueTracker(0.0)
        x_past = np.array([-2 * x_step, 0.0, 0.0])
        x_future = np.array([2 * x_step, 0.0, 0.0])

        stim_left = framed_visual(
            _img(
                preferred_path(
                    REPO_ROOT / "assets" / "images" / "ANI-FIS-T00.jpeg",
                    REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-T00.jpeg",
                    _INTRO_STIM_DIR / "animal_fish-00.png",
                ),
                1.20,
            )
        )
        stim_mid = framed_visual(MathTex("+", color=MGREY, font_size=40))
        stim_right = framed_visual(
            _img(
                preferred_path(
                    REPO_ROOT / "assets" / "images" / "ANI-FIS-D01.jpeg",
                    REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-D01.jpeg",
                    _INTRO_STIM_DIR / "animal_fish-01.png",
                ),
                1.20,
            )
        )
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

        fixed_head = build_fixed_head(_SENSORY_PATTERN_LEFT)
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
        snapshot_targets = VGroup(
            *[
                Square(
                    side_length=fixed_head[1].width * snapshot_scale,
                    stroke_opacity=0.0,
                    fill_opacity=0.0,
                )
                for _ in range(3)
            ]
        ).arrange(RIGHT, buff=0.62, aligned_edge=DOWN)
        snapshot_targets.to_corner(DL, buff=0.52)
        snapshot_targets.shift(UP * 0.18)

        snapshot_label_texts = ("perception", "maintenance", "perception")
        snapshot_labels = VGroup()
        for label_text in snapshot_label_texts:
            label = Tex(label_text, color=BLACK, font_size=20)
            snapshot_labels.add(label)
        for placeholder, label in zip(snapshot_targets, snapshot_labels):
            if label.width > placeholder.width * 1.08:
                label.scale_to_fit_width(placeholder.width * 1.08)
        label_center_y = snapshot_targets[0].get_top()[1] + max(label.height for label in snapshot_labels) / 2 + 0.08
        for placeholder, label in zip(snapshot_targets, snapshot_labels):
            label.move_to(
                np.array(
                    [
                        placeholder.get_center()[0],
                        label_center_y,
                        0.0,
                    ]
                )
            )

        left_set_brace = MathTex(r"\Bigg\{", color=BLACK, font_size=58)
        left_set_brace.next_to(snapshot_targets[0], LEFT, buff=0.08)
        left_set_brace.move_to(
            np.array(
                [
                    left_set_brace.get_center()[0],
                    snapshot_targets.get_center()[1] - 0.02,
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
                    snapshot_targets.get_center()[1] - 0.02,
                    0.0,
                ]
            )
        )

        snapshot_commas = VGroup()
        for left_target, right_target in zip(snapshot_targets[:-1], snapshot_targets[1:]):
            comma = Tex(",", color=BLACK, font_size=28)
            comma.move_to(midpoint(left_target.get_right(), right_target.get_left()))
            comma.shift(DOWN * 0.08)
            snapshot_commas.add(comma)
        snapshot_trailing_comma = Tex(",", color=BLACK, font_size=28)
        snapshot_trailing_comma.next_to(snapshot_targets[-1], RIGHT, buff=0.16)
        snapshot_trailing_comma.align_to(snapshot_commas[0], DOWN)
        snapshot_ellipsis = MathTex(r"\cdots", color=BLACK, font_size=24)
        snapshot_ellipsis.next_to(snapshot_trailing_comma, RIGHT, buff=0.12)
        snapshot_ellipsis.align_to(snapshot_trailing_comma, DOWN)
        snapshot_ellipsis.shift(UP * 0.03)
        right_set_brace.next_to(snapshot_ellipsis, RIGHT, buff=0.14)
        right_set_brace.move_to(
            np.array(
                [
                    right_set_brace.get_center()[0],
                    snapshot_targets.get_center()[1] - 0.02,
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
        snapshot_equation = VGroup(snapshot_targets, snapshot_scaffold)
        left_safe = -config.frame_width / 2 + 0.20
        right_safe = config.frame_width / 2 - 0.20
        if snapshot_equation.get_left()[0] < left_safe:
            snapshot_equation.shift(RIGHT * (left_safe - snapshot_equation.get_left()[0]))
        if snapshot_equation.get_right()[0] > right_safe:
            snapshot_equation.shift(LEFT * (snapshot_equation.get_right()[0] - right_safe))

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
                return interpolate_matrix(_SENSORY_PATTERN_LEFT, _MEMORY_PATTERN, np.clip(t, 0.0, 1.0))
            return interpolate_matrix(_MEMORY_PATTERN, _SENSORY_PATTERN_RIGHT, np.clip(t - 1.0, 0.0, 1.0))

        def update_card(mob: Mobject, points: list[np.ndarray]) -> Mobject:
            place_card(mob, path_anchor(points, travel.get_value()))
            return mob

        def update_dot(mob: Mobject, points: list[np.ndarray]) -> Mobject:
            mob.move_to(path_anchor(points, travel.get_value()))
            return mob

        fixed_head_anchor = path_anchor(left_path, 0.0)

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
            animations: list[Animation] = [
                moving_copy.animate(run_time=move_run_time, rate_func=smooth).scale(snapshot_scale).move_to(
                    target.get_center()
                )
            ]
            self.add_fixed_in_frame_mobjects(moving_copy)
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
                snapshot_targets[0],
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
                snapshot_targets[1],
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
                snapshot_targets[2],
                reveal_items=(snapshot_labels[2], snapshot_trailing_comma, snapshot_ellipsis, right_set_brace),
            )
        )
        self.wait(1.0)


class IntroMemoryRepresentation(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        b_state = _build_intro_b_layout()
        self.add(*b_state["final_group"])
        _transition_b_to_c(self, b_state)


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
                FadeIn(state["left_image"], shift=UP * 0.04),
                Create(state["left_cut_line"]),
                FadeIn(state["dead_zone"]),
                Create(state["right_cut_line"]),
                FadeIn(state["right_image"], shift=UP * 0.04),
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


class IntroClassicalView(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_d_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["content"], shift=UP * 0.05), run_time=0.95)
        self.play(FadeIn(state["takeaway"], shift=UP * 0.04), run_time=0.55)
        self.wait(4.00)


class IntroSensoryRecruitment(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_e_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["content"], shift=UP * 0.05), run_time=0.95)
        self.play(FadeIn(state["takeaway"], shift=UP * 0.04), run_time=0.55)
        self.wait(4.50)


class IntroResearchQuestion1(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(0)
        self.play(FadeIn(state["header"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["question_card"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["focus_panel"], shift=UP * 0.05), run_time=0.75)
        self.wait(4.00)


class IntroResearchQuestion2(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(1)
        self.play(FadeIn(state["header"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["question_card"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["focus_panel"], shift=UP * 0.05), run_time=0.75)
        self.wait(4.00)


class IntroResearchQuestion3(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_question_layout(2)
        self.play(FadeIn(state["header"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["question_card"], shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(state["focus_panel"], shift=UP * 0.05), run_time=0.75)
        self.wait(4.00)


# Backward-compatible names retained for ad hoc renders.
class IntroCognitiveProblemB(IntroSensoryRepresentation):
    pass


class IntroCognitiveProblemC(IntroMemoryRepresentation):
    pass


class IntroResearchQuestions(IntroResearchQuestion1):
    pass


# ── Master scene ──────────────────────────────────────────────────────────────

_INTRO_SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = (
    ("intro_cognitive_problem", IntroCognitiveProblemA),
    ("sens-mem-representations", IntroSensoryRepresentation),
    ("intro_classical_view", IntroClassicalView),
    ("intro_sensory_recruitment", IntroSensoryRecruitment),
    ("intro_research_question_1", IntroResearchQuestion1),
    ("intro_research_question_2", IntroResearchQuestion2),
    ("intro_research_question_3", IntroResearchQuestion3),
)


class Introduction(ThreeDScene):
    def _reset_section_camera(self) -> None:
        self.set_camera_orientation(
            phi=0 * DEGREES,
            theta=-90 * DEGREES,
            gamma=0,
            zoom=1.0,
            frame_center=ORIGIN,
        )
        camera = self.renderer.camera
        if hasattr(camera, "fixed_orientation_mobjects"):
            camera.fixed_orientation_mobjects.clear()
        if hasattr(camera, "fixed_in_frame_mobjects"):
            camera.fixed_in_frame_mobjects.clear()

    def _render_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        self.next_section(section_name)
        if carry_previous_frame:
            self.wait(_SECTION_HOLD)
        self.clear()
        self.camera.background_color = BG
        self._reset_section_camera()
        scene_cls.construct(self)

    def construct(self) -> None:
        for idx, (name, cls) in enumerate(_INTRO_SECTION_SCENES):
            self._render_section(name, cls, carry_previous_frame=idx > 0)


_HIDDEN_INTRO_SCENES = (
    IntroCognitiveProblemA,
    IntroSensoryRepresentation,
    IntroMemoryRepresentation,
    IntroCognitiveProblemB,
    IntroCognitiveProblemC,
    IntroClassicalView,
    IntroSensoryRecruitment,
    IntroResearchQuestion1,
    IntroResearchQuestion2,
    IntroResearchQuestion3,
    IntroResearchQuestions,
)
for _scene_cls in _HIDDEN_INTRO_SCENES:
    _scene_cls.__module__ = "_intro_internal"
del _scene_cls
Introduction.__module__ = __name__
__all__ = ["Introduction"]
