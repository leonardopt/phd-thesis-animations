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


# ── Assets ────────────────────────────────────────────────────────────────────
_INTRO_STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
_BRAIN_ICON_PATH = REPO_ROOT / "assets" / "images" / "study2" / "brain_icon_sagittal.png"
_HEAD_BRAIN_PATH = REPO_ROOT / "assets" / "images" / "head_brain.png"
_REFERENCE_DIR = REPO_ROOT / "assets" / "images" / "references" / "working_memory"
_FUNAHASHI_1989_FIG = str(_REFERENCE_DIR / "funahashi1989_delay_activity.png")
_JONIDES_1993_FIG = str(_REFERENCE_DIR / "jonides1993_pet.png")
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
_SENSORY_PATTERN_LEFT = np.array(
    [
        [0.80, 0.15, -0.20, -0.75],
        [0.45, 0.10, -0.05, -0.40],
        [0.05, -0.10, 0.20, 0.55],
        [-0.55, -0.25, 0.35, 0.78],
    ]
)
_MEMORY_PATTERN = np.array(
    [
        [0.55, 0.25, -0.10, -0.35],
        [0.35, 0.15, 0.05, -0.20],
        [0.10, 0.00, 0.12, 0.30],
        [-0.18, -0.08, 0.22, 0.42],
    ]
)
_SENSORY_PATTERN_RIGHT = np.array(
    [
        [-0.72, -0.18, 0.22, 0.82],
        [-0.38, -0.08, 0.12, 0.48],
        [0.12, 0.02, -0.15, -0.52],
        [0.62, 0.28, -0.25, -0.78],
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
    label = Tex(label_text, color=accent, font_size=18)
    refs = Tex(ref_text, color=MGREY, font_size=14)
    return Group(image, label, refs).arrange(DOWN, buff=0.08)


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


def patterned_head(matrix: np.ndarray, *, scale_factor: float = 1.0) -> Group:
    head = brain_render(scale_factor=scale_factor)
    rows, cols = matrix.shape
    cell_size = 0.060 * head.width
    cells = VGroup()
    for row in range(rows):
        for col in range(cols):
            cell = Square(
                side_length=cell_size,
                stroke_color=LGREY,
                stroke_width=0.35,
            ).set_fill(_pattern_color(matrix[row, col]), opacity=1.0)
            cells.add(cell)
    cells.arrange_in_grid(rows=rows, cols=cols, buff=0.006)

    cells.move_to(
        head.get_center()
        + LEFT * (0.06 * head.width)
        + UP * (0.24 * head.height)
    )
    cells.set_z_index(2)
    head.set_z_index(0)
    return Group(head, cells)


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
            REPO_ROOT / "assets" / "images" / "ANI-FIS-D03.jpeg",
            REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-D03.jpeg",
            _INTRO_STIM_DIR / "animal_fish-03.png",
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
        r"\textbf{Classical view of working memory}",
        "Lesions, persistent firing, and early human imaging converged on association cortex",
    )
    paper_column = Group(
        make_paper_snapshot(
            _FUNAHASHI_1989_FIG,
            "delay-period firing",
            "Funahashi et al. (1989)",
            accent=AMBER,
            height=1.74,
        ),
        make_paper_snapshot(
            _JONIDES_1993_FIG,
            "PET evidence",
            "Jonides et al. (1993)",
            accent=AMBER,
            height=1.55,
        ),
    ).arrange(DOWN, buff=0.24)
    paper_header = Tex("Seminal evidence", color=MGREY, font_size=20)
    paper_stack = Group(paper_header, paper_column).arrange(DOWN, buff=0.14, aligned_edge=LEFT)

    evidence = VGroup(
        make_literature_entry(
            "Lesion evidence",
            ("PFC damage impaired delayed-response behaviour",),
            ("Jacobsen (1936); Harlow (1952)",),
            accent=AMBER,
        ),
        make_literature_entry(
            "Persistent firing",
            ("Sustained activity in monkey PFC", "looked like the memory trace itself"),
            (r"Fuster \& Alexander (1971); Kubota \& Niki (1971)", "Funahashi et al. (1989, 1993)"),
            accent=AMBER,
        ),
        make_literature_entry(
            "Human imaging",
            ("PET and fMRI reinforced a frontal-parietal", "maintenance network"),
            (r"Jonides et al. (1993); D'Esposito et al. (1995)", "Courtney et al. (1997, 1998)"),
            accent=AMBER,
        ),
    ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

    content = Group(paper_stack, evidence).arrange(RIGHT, buff=0.86, aligned_edge=UP)
    content.next_to(title, DOWN, buff=0.34)
    takeaway = make_callout(
        "Working memory was mainly localized to prefrontal and association cortex.",
        AMBER,
        font_size=22,
    ).to_edge(DOWN, buff=0.34)
    return {
        "title": title,
        "content": content,
        "takeaway": takeaway,
        "final_group": Group(title, content, takeaway),
    }


def _build_intro_e_layout() -> dict[str, Mobject]:
    title = title_block(
        r"\textbf{Sensory recruitment model}",
        "Theory papers and MVPA studies suggested that visual cortex also carries maintained content",
    )
    paper_column = Group(
        make_paper_snapshot(
            _AWH_JONIDES_2001_FIG,
            "theory shift",
            r"Awh \& Jonides (2001)",
            accent=BLUE,
            height=1.62,
        ),
        make_paper_snapshot(
            _HARRISON_TONG_2009_FIG,
            "orientation decoding",
            r"Harrison \& Tong (2009)",
            accent=BLUE,
            height=1.62,
        ),
    ).arrange(DOWN, buff=0.24)
    paper_header = Tex("Seminal evidence", color=MGREY, font_size=20)
    paper_stack = Group(paper_header, paper_column).arrange(DOWN, buff=0.14, aligned_edge=LEFT)

    evidence = VGroup(
        make_literature_entry(
            "Theory shift",
            ("Perception and memory may reuse", "the same sensory circuits"),
            (r"Awh \& Jonides (2001); Pasternak \& Greenlee (2005)", "Postle (2006)"),
            accent=BLUE,
        ),
        make_literature_entry(
            "Seminal MVPA",
            ("Remembered orientation decoded from V1--V4", "during the delay, with no stimulus present"),
            (r"Harrison \& Tong (2009); Serences et al. (2009)",),
            accent=BLUE,
        ),
        make_literature_entry(
            "Open debate",
            ("Human fMRI shows sustained delay activity;", "monkey electrophysiology rarely does"),
            (r"Leavitt et al. (2017); Curtis \& Sprague (2021)",),
            accent=RED,
        ),
    ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

    content = Group(paper_stack, evidence).arrange(RIGHT, buff=0.86, aligned_edge=UP)
    content.next_to(title, DOWN, buff=0.34)
    takeaway = make_callout(
        r"The key claim: early visual cortex may actively carry WM content --- but the debate continues.",
        BLUE,
        font_size=21,
    ).to_edge(DOWN, buff=0.34)
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
        "subtitle": "Are maintained representations sensory-like or memory-specific?",
        "accent": BLUE,
        "tag": "format",
    },
    {
        "kicker": "Research question 2",
        "title": "Naturalistic stimuli",
        "subtitle": "Does sensory recruitment extend beyond simple laboratory stimuli?",
        "accent": AMBER,
        "tag": "stimuli",
    },
    {
        "kicker": "Research question 3",
        "title": "Long-term memory",
        "subtitle": "Does long-term memory reshape working-memory representations?",
        "accent": GREEN,
        "tag": "ltm",
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
    question_claim = VGroup(
        Tex(spec["subtitle"], color=INK, font_size=26),
    ).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
    question_divider = Line(LEFT * 2.9, RIGHT * 2.9, color=LGREY, stroke_width=1.0)
    question_divider.align_to(question_claim, LEFT)
    question_card = VGroup(
        question_title_row,
        question_claim,
        question_divider,
    ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)

    focus_title_row = VGroup(
        Dot(radius=0.040, color=MGREY),
        Tex(r"\textbf{Project focus}", color=INK, font_size=18),
    ).arrange(RIGHT, buff=0.12)
    focus_copy = VGroup(
        Tex("visual cortex", color=INK, font_size=24),
        Tex("perception, working memory, and long-term memory", color=MGREY, font_size=16),
        Tex(spec["tag"], color=spec["accent"], font_size=18),
    ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    focus_divider = Line(LEFT * 2.5, RIGHT * 2.5, color=LGREY, stroke_width=1.0)
    focus_divider.align_to(focus_copy, LEFT)
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
                REPO_ROOT / "assets" / "images" / "ANI-FIS-D03.jpeg",
                REPO_ROOT / "assets" / "images" / "study1_stage3" / "ANI-FIS-D03.jpeg",
                _INTRO_STIM_DIR / "animal_fish-03.png",
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
        self.wait(1.00)
        self.remove(fix)
        self.add(foil)
        self.wait(3.50)


class IntroSensoryRepresentation(Scene):
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
        self.wait(3.50)


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
    ("intro_sensory_representation", IntroSensoryRepresentation),
    ("intro_classical_view", IntroClassicalView),
    ("intro_sensory_recruitment", IntroSensoryRecruitment),
    ("intro_research_question_1", IntroResearchQuestion1),
    ("intro_research_question_2", IntroResearchQuestion2),
    ("intro_research_question_3", IntroResearchQuestion3),
)


class Introduction(Scene):
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
