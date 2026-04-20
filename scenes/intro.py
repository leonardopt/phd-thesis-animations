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


# ── Assets ────────────────────────────────────────────────────────────────────
_INTRO_STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
_BRAIN_ICON_PATH = REPO_ROOT / "assets" / "images" / "study2" / "brain_icon_sagittal.png"
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


def stim_path(code: str, idx: int) -> str:
    return str(_INTRO_STIM_DIR / f"{code}-{idx:02d}.png")


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
    title = title_block(r"Perception $\to$ interruption $\to$ maintenance $\to$ comparison")
    card_h = 1.05
    frozen_pos = list(_STRIP).index(_FROZEN_IDX)
    strip_cards = Group(
        *[
            _img(stim_path(_HOOK_CODE, idx), card_h)
            for idx in _STRIP
        ]
    ).arrange(RIGHT, buff=0.22)
    strip_cards.next_to(title, DOWN, buff=0.40)
    strip_cards.shift(LEFT * 1.50)

    time_dots = VGroup(
        *[
            Dot(radius=0.05, color=BLUE if idx == _FROZEN_IDX else MGREY)
            for idx in _STRIP
        ]
    )
    for dot, card in zip(time_dots, strip_cards):
        dot.next_to(card, DOWN, buff=0.12)

    frozen_card = strip_cards[frozen_pos]
    frozen_ring = SurroundingRectangle(
        frozen_card,
        color=BLUE,
        stroke_width=2.4,
        buff=0.07,
        corner_radius=0.07,
    )

    cut_x = strip_cards[-1].get_right()[0] + 0.50
    zone_top = strip_cards.get_top()[1] + 0.22
    zone_bot = time_dots.get_bottom()[1] - 0.16
    cut_line = DashedLine(
        [cut_x, zone_top, 0],
        [cut_x, zone_bot, 0],
        color=RED,
        stroke_width=2.0,
        dash_length=0.10,
    )
    cut_label = Tex(r"\textbf{interruption}", color=RED, font_size=15)
    cut_label.next_to(cut_line, UP, buff=0.10)

    dead_zone = Rectangle(width=2.40, height=zone_top - zone_bot, stroke_width=0).set_fill(
        LGREY, opacity=0.16
    )
    dead_zone.next_to(cut_line, RIGHT, buff=0.0)
    dead_zone.align_to([0, zone_bot, 0], DOWN)

    brain_parts = brain_icon_with_evc(highlight_color=AMBER, scale_factor=0.76)
    brain_group = brain_parts["group"]
    brain_group.move_to(LEFT * 0.60 + DOWN * 1.20)

    wm_trace = _img(stim_path(_HOOK_CODE, _FROZEN_IDX), 0.76)
    wm_trace.move_to(brain_group.get_center() + LEFT * 0.18 + UP * 0.10)
    wm_label = Tex("WM trace", color=AMBER, font_size=14)
    wm_label.next_to(wm_trace, DOWN, buff=0.08)

    encode_arrow = Arrow(
        frozen_card.get_bottom() + DOWN * 0.06,
        brain_group.get_top() + UP * 0.06,
        color=BLUE,
        stroke_width=1.8,
        buff=0.06,
    )

    probe = _img(stim_path(_HOOK_CODE, _FROZEN_IDX), 0.82)
    probe.move_to(RIGHT * 4.60 + DOWN * 1.20)
    probe_label = Tex("probe", color=GREEN, font_size=14)
    probe_label.next_to(probe, DOWN, buff=0.08)

    compare_arrow = Arrow(
        probe.get_left() + LEFT * 0.04,
        brain_group.get_right() + RIGHT * 0.04,
        color=GREEN,
        stroke_width=1.8,
        buff=0.06,
    )
    compare_label = Tex("compare", color=GREEN, font_size=14)
    compare_label.next_to(compare_arrow, UP, buff=0.08)

    phase_bar = VGroup(
        Tex("perception", color=BLUE, font_size=18),
        Tex(r"$\to$", color=LGREY, font_size=18),
        Tex("interruption", color=RED, font_size=18),
        Tex(r"$\to$", color=LGREY, font_size=18),
        Tex("maintenance", color=AMBER, font_size=18),
        Tex(r"$\to$", color=LGREY, font_size=18),
        Tex("comparison", color=GREEN, font_size=18),
    ).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.28)

    final_group = Group(
        title,
        strip_cards,
        time_dots,
        frozen_ring,
        cut_line,
        cut_label,
        dead_zone,
        brain_group,
        wm_trace,
        wm_label,
        encode_arrow,
        probe,
        probe_label,
        compare_arrow,
        compare_label,
        phase_bar,
    )
    return {
        "title": title,
        "strip_cards": strip_cards,
        "time_dots": time_dots,
        "frozen_ring": frozen_ring,
        "cut_line": cut_line,
        "cut_label": cut_label,
        "dead_zone": dead_zone,
        "brain_group": brain_group,
        "wm_trace": wm_trace,
        "wm_label": wm_label,
        "encode_arrow": encode_arrow,
        "probe": probe,
        "probe_label": probe_label,
        "compare_arrow": compare_arrow,
        "compare_label": compare_label,
        "phase_bar": phase_bar,
        "final_group": final_group,
    }


def _build_intro_c_layout() -> dict[str, Mobject]:
    title = title_block(
        r"\textbf{Long-term memory modulates the maintained trace}",
        r"Prior exposure shapes the WM representation --- without replacing it",
    )
    brain_parts = brain_icon_with_evc(highlight_color=AMBER, scale_factor=1.00)
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


def _build_intro_f_layout() -> dict[str, Mobject]:
    title = title_block(r"\textbf{Three research questions}")
    brain = brain_icon_with_evc(highlight_color=BLUE, scale_factor=0.82)
    focus_frame = RoundedRectangle(
        width=4.45,
        height=4.70,
        corner_radius=0.18,
        stroke_color=LGREY,
        stroke_width=1.4,
    ).set_fill(PANEL, opacity=0.96)
    focus_title = Tex("Project focus", color=BLUE, font_size=22)
    focus_title.next_to(focus_frame.get_top(), DOWN, buff=0.20)
    brain["group"].move_to(focus_frame.get_center() + UP * 0.30)
    focus_copy = VGroup(
        Tex("visual cortex", color=INK, font_size=21),
        Tex("perception, working memory, and long-term memory", color=MGREY, font_size=16),
    ).arrange(DOWN, buff=0.06)
    focus_copy.next_to(brain["group"], DOWN, buff=0.20)
    focus_panel = Group(focus_frame, focus_title, brain["group"], focus_copy)

    question_cards = VGroup(
        make_info_card(
            "Representational format",
            "sensory-like or memory-specific?",
            accent=BLUE,
            width=5.90,
            height=1.18,
        ),
        make_info_card(
            "Naturalistic stimuli",
            "does sensory recruitment extend beyond simple laboratory stimuli?",
            accent=AMBER,
            width=5.90,
            height=1.18,
        ),
        make_info_card(
            "Long-term memory",
            "does long-term memory reshape working-memory representations?",
            accent=GREEN,
            width=5.90,
            height=1.18,
        ),
    ).arrange(DOWN, buff=0.22)

    content = Group(focus_panel, question_cards).arrange(RIGHT, buff=0.78, aligned_edge=UP)
    content.next_to(title, DOWN, buff=0.36)
    return {
        "title": title,
        "focus_panel": focus_panel,
        "question_cards": question_cards,
        "content": content,
        "final_group": Group(title, focus_panel, question_cards),
    }


# ── B → C transition ──────────────────────────────────────────────────────────

def _transition_b_to_c(scene: Scene, b_state: dict[str, Mobject]) -> None:
    c_state = _build_intro_c_layout()
    scene.play(
        FadeOut(b_state["title"], shift=UP * 0.04),
        FadeOut(b_state["strip_cards"], shift=UP * 0.05),
        FadeOut(b_state["time_dots"], shift=UP * 0.03),
        FadeOut(b_state["frozen_ring"]),
        FadeOut(b_state["cut_line"]),
        FadeOut(b_state["cut_label"], shift=DOWN * 0.03),
        FadeOut(b_state["dead_zone"]),
        FadeOut(b_state["encode_arrow"]),
        FadeOut(b_state["probe"]),
        FadeOut(b_state["probe_label"]),
        FadeOut(b_state["compare_arrow"]),
        FadeOut(b_state["compare_label"], shift=DOWN * 0.03),
        FadeOut(b_state["phase_bar"], shift=DOWN * 0.04),
        Transform(b_state["brain_group"], c_state["brain_group"]),
        Transform(b_state["wm_trace"], c_state["wm_trace"]),
        Transform(b_state["wm_label"], c_state["wm_label"]),
        run_time=0.90,
    )
    scene.play(FadeIn(c_state["title"], shift=UP * 0.04), run_time=0.70)
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

        def _frame(idx: int) -> ImageMobject:
            img = ImageMobject(stim_path(_HOOK_CODE, idx))
            img.height = 5.80
            img.move_to(ORIGIN)
            return img

        first = _frame(_ORDER[0])
        self.play(FadeIn(first, run_time=0.40))
        self.wait(0.45)

        current = first
        for idx in _ORDER[1:]:
            nxt = _frame(idx)
            self.remove(current)
            self.add(nxt)
            self.wait(0.12)
            current = nxt

        self.remove(current)

        fix = VGroup(
            Line(UP * 0.20, DOWN * 0.20, stroke_width=2.4, color=MGREY),
            Line(LEFT * 0.20, RIGHT * 0.20, stroke_width=2.4, color=MGREY),
        )
        self.add(fix)
        self.wait(1.00)
        self.remove(fix)
        self.wait(0.10)

        state = _build_intro_a_end_state()
        self.play(FadeIn(state["question"], shift=DOWN * 0.06), run_time=0.50)
        self.play(
            LaggedStart(
                FadeIn(state["probe_target"], scale=0.97),
                FadeIn(state["probe_foil"], scale=0.97),
                lag_ratio=0.28,
            ),
            run_time=0.70,
        )
        self.wait(3.50)


class IntroCognitiveProblemB(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_b_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.65)
        self.play(
            LaggedStart(
                *[FadeIn(card, shift=UP * 0.04) for card in state["strip_cards"]],
                lag_ratio=0.12,
            ),
            FadeIn(state["time_dots"]),
            run_time=0.80,
        )
        self.play(Create(state["frozen_ring"]), run_time=0.45)
        self.wait(0.40)
        self.play(
            Create(state["cut_line"]),
            FadeIn(state["cut_label"], shift=DOWN * 0.04),
            FadeIn(state["dead_zone"]),
            run_time=0.55,
        )
        self.wait(0.30)
        self.play(FadeIn(state["brain_group"], scale=0.97), run_time=0.55)
        self.play(
            Create(state["encode_arrow"]),
            TransformFromCopy(state["strip_cards"][list(_STRIP).index(_FROZEN_IDX)], state["wm_trace"]),
            FadeIn(state["wm_label"], shift=UP * 0.04),
            run_time=0.85,
        )
        self.wait(0.60)
        self.play(
            FadeIn(state["probe"], scale=0.97),
            FadeIn(state["probe_label"]),
            run_time=0.50,
        )
        self.play(
            Create(state["compare_arrow"]),
            FadeIn(state["compare_label"], shift=DOWN * 0.04),
            run_time=0.50,
        )
        self.play(FadeIn(state["phase_bar"], shift=UP * 0.04), run_time=0.55)
        self.wait(3.50)


class IntroCognitiveProblemC(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        b_state = _build_intro_b_layout()
        self.add(*b_state["final_group"])
        _transition_b_to_c(self, b_state)


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


class IntroResearchQuestions(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        state = _build_intro_f_layout()
        self.play(FadeIn(state["title"], shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(state["focus_panel"], shift=UP * 0.05), run_time=0.85)
        self.play(
            LaggedStart(
                *[FadeIn(card, shift=RIGHT * 0.08) for card in state["question_cards"]],
                lag_ratio=0.18,
            ),
            run_time=1.20,
        )
        self.wait(4.00)


# ── Master scene ──────────────────────────────────────────────────────────────

_INTRO_SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = (
    ("intro_cognitive_problem_a", IntroCognitiveProblemA),
    ("intro_cognitive_problem_b", IntroCognitiveProblemB),
    ("intro_cognitive_problem_c", IntroCognitiveProblemC),
    ("intro_classical_view", IntroClassicalView),
    ("intro_sensory_recruitment", IntroSensoryRecruitment),
    ("intro_research_questions", IntroResearchQuestions),
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
    IntroCognitiveProblemB,
    IntroCognitiveProblemC,
    IntroClassicalView,
    IntroSensoryRecruitment,
    IntroResearchQuestions,
)
for _scene_cls in _HIDDEN_INTRO_SCENES:
    _scene_cls.__module__ = "_intro_internal"
del _scene_cls
Introduction.__module__ = __name__
__all__ = ["Introduction"]
