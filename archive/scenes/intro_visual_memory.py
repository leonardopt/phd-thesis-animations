"""
Visual-memory introduction for the thesis defence.

  Intro01VisualMemoryHook           — visible scene -> delay -> decision
  Intro02MemoryTimescales           — one representation across time scales
  Intro03SensoryRecruitmentTension  — two competing hypotheses
  Intro04ThreeOpenQuestions         — three consequences of the sensory-recruitment idea
  Intro05MethodologicalBottleneck   — why the stimulus problem is the bottleneck
  Intro06ThesisRoadmap              — build the stimulus space, then test the theory

Render:
    uv run manim scenes/intro_visual_memory.py Intro01VisualMemoryHook -ql
    uv run manim scenes/intro_visual_memory.py Intro02MemoryTimescales -ql
    uv run manim scenes/intro_visual_memory.py Intro03SensoryRecruitmentTension -ql
    uv run manim scenes/intro_visual_memory.py Intro04ThreeOpenQuestions -ql
    uv run manim scenes/intro_visual_memory.py Intro05MethodologicalBottleneck -ql
    uv run manim scenes/intro_visual_memory.py Intro06ThesisRoadmap -ql
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import *

from utils import env_path

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = WHITE
INK     = "#1C1C1E"
LGREY   = "#D1D5DB"
MGREY   = "#9CA3AF"
BLUE    = "#2563EB"
AMBER   = "#D97706"
GREEN   = "#16A34A"
RED     = "#DC2626"
PANEL   = "#F8FAFC"

# ── Assets ────────────────────────────────────────────────────────────────────
STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    Path(__file__).parent.parent / "assets" / "images" / "stimuli_reordered",
)

HOOK_CODE = "building_observatory"
CONTINUUM_CODE = "building_observatory"

CLASSICAL_REGION_POS = {
    "PFC": RIGHT * 0.95 + UP * 0.10,
    "Parietal": RIGHT * 0.00 + UP * 0.50,
    "Temporal": RIGHT * 0.05 + DOWN * 0.58,
}
OCCIPITAL_POS = LEFT * 1.05 + UP * 0.08


def stim_path(code: str, idx: int) -> str:
    """Return an absolute path to a local stimulus image."""
    return str(STIM_DIR / f"{code}-{idx:02d}.png")


def title_block(title_text: str, subtitle_text: str | None = None) -> VGroup:
    """Return the standard intro title group."""
    title = Tex(title_text, color=INK, font_size=34).to_edge(UP, buff=0.34)
    parts = [title]
    if subtitle_text is not None:
        subtitle = Tex(subtitle_text, color=MGREY, font_size=21)
        subtitle.next_to(title, DOWN, buff=0.14)
        parts.append(subtitle)
    return VGroup(*parts)


def make_image_card(
    image_path: str,
    *,
    height: float = 1.6,
    border_color: str = LGREY,
    fill_color: str = PANEL,
    fill_opacity: float = 0.96,
    buff: float = 0.06,
    corner_radius: float = 0.14,
) -> Group:
    """Create a framed image card."""
    image = ImageMobject(image_path)
    image.height = height
    frame = RoundedRectangle(
        width=image.width + 2 * buff,
        height=image.height + 2 * buff,
        corner_radius=corner_radius,
        stroke_color=border_color,
        stroke_width=1.6,
    ).set_fill(fill_color, opacity=fill_opacity)
    frame.move_to(image)
    return Group(frame, image)


def make_pill(text: str, color: str, *, font_size: float = 18) -> VGroup:
    """Create a compact colored label."""
    label = Tex(text, color=color, font_size=font_size)
    dot = Dot(radius=0.045, color=color)
    return VGroup(dot, label).arrange(RIGHT, buff=0.12)


def make_callout(text: str, color: str, *, font_size: float = 23) -> VGroup:
    """Create a larger takeaway line."""
    line = Tex(text, color=INK, font_size=font_size)
    underline = Line(
        line.get_left() + DOWN * 0.12,
        line.get_right() + DOWN * 0.12,
        color=color,
        stroke_width=2.0,
    )
    return VGroup(line, underline)


def make_feature_row(
    values: np.ndarray,
    *,
    color: str,
    cell_w: float = 0.20,
    cell_h: float = 0.20,
    gap: float = 0.06,
) -> VGroup:
    """Create a compact 1-D feature vector as coloured cells."""
    group = VGroup()
    mid = (len(values) - 1) / 2
    for idx, value in enumerate(values):
        alpha = 0.18 + 0.82 * float(value)
        cell = Rectangle(
            width=cell_w,
            height=cell_h,
            stroke_color=LGREY,
            stroke_width=0.8,
        ).set_fill(
            interpolate_color(ManimColor(WHITE), ManimColor(color), alpha),
            opacity=1.0,
        )
        cell.move_to(RIGHT * (idx - mid) * (cell_w + gap))
        group.add(cell)
    return group


def make_pattern_grid(
    values: np.ndarray,
    *,
    color: str,
    cell_size: float = 0.20,
    gap: float = 0.04,
) -> VGroup:
    """Create a compact multivoxel-style pattern grid."""
    rows, cols = values.shape
    group = VGroup()
    for row in range(rows):
        for col in range(cols):
            alpha = 0.14 + 0.86 * float(values[row, col])
            cell = Square(
                side_length=cell_size,
                stroke_color=LGREY,
                stroke_width=0.8,
            ).set_fill(
                interpolate_color(ManimColor(WHITE), ManimColor(color), alpha),
                opacity=1.0,
            )
            cell.move_to(
                RIGHT * (col - (cols - 1) / 2) * (cell_size + gap)
                + DOWN * (row - (rows - 1) / 2) * (cell_size + gap)
            )
            group.add(cell)
    return group


def brain_schematic(
    *,
    occipital_color: str | None = None,
    classical_color: str = MGREY,
    scale_factor: float = 1.0,
) -> dict[str, Mobject]:
    """Return a compact schematic brain with association and occipital regions."""
    outline = Ellipse(
        width=4.25,
        height=2.70,
        stroke_color=LGREY,
        stroke_width=2.0,
    ).set_fill("#F3F4F6", opacity=0.78)
    cerebellum = Circle(
        radius=0.34,
        stroke_color=LGREY,
        stroke_width=1.4,
    ).set_fill("#F3F4F6", opacity=0.78)
    cerebellum.move_to(outline.get_center() + LEFT * 1.22 + DOWN * 0.78)

    region_group = VGroup()
    for offset in CLASSICAL_REGION_POS.values():
        region = Circle(radius=0.34, stroke_width=0)
        region.set_fill(classical_color, opacity=0.22)
        region.move_to(outline.get_center() + offset)
        region_group.add(region)

    occipital = Circle(radius=0.34, stroke_width=0)
    occipital.set_fill(occipital_color or classical_color, opacity=0.22)
    occipital.move_to(outline.get_center() + OCCIPITAL_POS)

    arcs = VGroup(
        ArcBetweenPoints(
            outline.get_center() + LEFT * 1.28 + UP * 0.05,
            outline.get_center() + RIGHT * 1.52 + UP * 0.05,
            angle=-0.55,
            stroke_color=LGREY,
            stroke_width=1.0,
        ),
        ArcBetweenPoints(
            outline.get_center() + LEFT * 1.05 + DOWN * 0.28,
            outline.get_center() + RIGHT * 1.15 + DOWN * 0.40,
            angle=0.24,
            stroke_color=LGREY,
            stroke_width=1.0,
        ),
    )

    group = VGroup(outline, cerebellum, arcs, region_group, occipital).scale(scale_factor)
    return {
        "group": group,
        "regions": region_group,
        "occipital": occipital,
    }


def make_source_block(title_text: str, image_specs: list[tuple[str, int]], failure_text: str) -> Group:
    """Create a source-of-stimuli block with a red failure note."""
    title = Tex(title_text, color=INK, font_size=24)
    underline = Line(LEFT * 1.20, RIGHT * 1.20, color=LGREY, stroke_width=1.6)
    underline.next_to(title, DOWN, buff=0.10)

    cards = Group(*[
        make_image_card(
            stim_path(code, idx),
            height=0.88,
            border_color=LGREY,
            fill_color=WHITE,
            fill_opacity=1.0,
            buff=0.035,
        )
        for code, idx in image_specs
    ])
    cards.arrange(RIGHT, buff=0.10)
    cards.next_to(underline, DOWN, buff=0.22)

    fail = Group(
        MathTex(r"\times", color=RED, font_size=26),
        Tex(failure_text, color=RED, font_size=16),
    ).arrange(RIGHT, buff=0.12)
    fail.next_to(cards, DOWN, buff=0.18)

    return Group(title, underline, cards, fail)


class Intro01VisualMemoryHook(Scene):
    """Visible scene -> blank delay -> decision still guided by memory."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(r"Perception ends quickly. Behaviour still depends on what was seen.")

        timeline = Arrow(
            LEFT * 5.8 + DOWN * 2.05,
            RIGHT * 5.8 + DOWN * 2.05,
            color=LGREY,
            stroke_width=2.0,
            buff=0.0,
            tip_shape=StealthTip,
        )
        phase_specs = [
            (LEFT * 4.55 + DOWN * 2.05, "Perception", BLUE),
            (ORIGIN + DOWN * 2.05, "Delay", AMBER),
            (RIGHT * 4.45 + DOWN * 2.05, "Decision", GREEN),
        ]
        phase_marks = VGroup()
        phase_labels = VGroup()
        for pos, text, color in phase_specs:
            dot = Dot(radius=0.07, color=color).move_to(pos)
            label = Tex(text, color=color, font_size=21).next_to(dot, DOWN, buff=0.18)
            phase_marks.add(dot)
            phase_labels.add(label)

        scene_card = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=2.40,
            border_color=BLUE,
            fill_color=WHITE,
            fill_opacity=1.0,
        ).move_to(LEFT * 4.35 + UP * 0.05)
        scene_label = Tex("rich visual input", color=BLUE, font_size=19).next_to(scene_card, DOWN, buff=0.16)
        scene_focus = SurroundingRectangle(scene_card, color=BLUE, stroke_width=2.0, buff=0.06)

        blank_card = RoundedRectangle(
            width=2.55,
            height=1.90,
            corner_radius=0.16,
            stroke_color=LGREY,
            stroke_width=1.6,
        ).set_fill("#F3F4F6", opacity=0.95)
        blank_card.move_to(ORIGIN + UP * 0.05)
        blank_cross = VGroup(
            Line(blank_card.get_corner(UL) + DR * 0.18, blank_card.get_corner(DR) + UL * 0.18, color=MGREY, stroke_width=2.0),
            Line(blank_card.get_corner(UR) + DL * 0.18, blank_card.get_corner(DL) + UR * 0.18, color=MGREY, stroke_width=2.0),
        )
        blank_label = Tex("sensory input is gone", color=MGREY, font_size=19).next_to(blank_card, DOWN, buff=0.16)

        memory_trace = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=0.92,
            border_color=AMBER,
            fill_color=WHITE,
            fill_opacity=1.0,
        ).move_to(blank_card.get_center() + UP * 1.35)
        memory_label = Tex("working memory trace", color=AMBER, font_size=20).next_to(memory_trace, DOWN, buff=0.12)

        probe_left = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=1.00,
            border_color=AMBER,
            fill_color=WHITE,
            fill_opacity=1.0,
        )
        probe_right = make_image_card(
            stim_path(HOOK_CODE, 6),
            height=1.00,
            border_color=LGREY,
            fill_color=WHITE,
            fill_opacity=1.0,
        )
        probes = Group(probe_left, probe_right).arrange(RIGHT, buff=0.30)
        probes.move_to(RIGHT * 4.60 + UP * 0.30)
        question = Tex("Which one matches?", color=INK, font_size=21).next_to(probes, UP, buff=0.18)

        choice_arrow = CurvedArrow(
            memory_trace.get_right() + RIGHT * 0.04,
            probe_left.get_top() + UP * 0.06,
            angle=-0.85,
            color=AMBER,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        check = Tex(r"\checkmark", color=GREEN, font_size=34).next_to(probe_left, DOWN, buff=0.14)

        takeaway = make_callout(
            r"The decision depends on information that is no longer on the retina.",
            AMBER,
            font_size=22,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(Create(timeline), FadeIn(phase_marks), FadeIn(phase_labels), run_time=0.90)
        self.play(FadeIn(scene_card, scale=0.97), FadeIn(scene_label), Create(scene_focus), run_time=0.95)
        self.wait(1.10)
        self.play(FadeIn(blank_card), Create(blank_cross), FadeIn(blank_label), run_time=0.80)
        self.play(
            TransformFromCopy(scene_card, memory_trace),
            FadeIn(memory_label, shift=UP * 0.05),
            run_time=0.95,
        )
        self.wait(1.40)
        self.play(FadeIn(question, shift=UP * 0.05), FadeIn(probes), run_time=0.85)
        self.play(Create(choice_arrow), Write(check), run_time=0.90)
        self.wait(1.70)
        self.play(FadeIn(takeaway, shift=UP * 0.05), run_time=0.70)
        self.wait(3.00)


class Intro02MemoryTimescales(Scene):
    """One visual representation spanning multiple time scales."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"The same visual information can matter across very different timescales"
        )

        timeline = Arrow(
            LEFT * 5.7 + DOWN * 1.55,
            RIGHT * 5.7 + DOWN * 1.55,
            color=LGREY,
            stroke_width=2.0,
            buff=0.0,
            tip_shape=StealthTip,
        )
        braces = VGroup(
            BraceBetweenPoints(LEFT * 5.1 + DOWN * 1.75, LEFT * 1.3 + DOWN * 1.75, color=BLUE),
            BraceBetweenPoints(LEFT * 1.1 + DOWN * 1.75, RIGHT * 1.1 + DOWN * 1.75, color=AMBER),
            BraceBetweenPoints(RIGHT * 1.3 + DOWN * 1.75, RIGHT * 5.1 + DOWN * 1.75, color=GREEN),
        )
        brace_labels = VGroup(
            VGroup(Tex("Perception", color=BLUE, font_size=22), Tex("while visible", color=MGREY, font_size=16)).arrange(DOWN, buff=0.04),
            VGroup(Tex("Working memory", color=AMBER, font_size=22), Tex("seconds", color=MGREY, font_size=16)).arrange(DOWN, buff=0.04),
            VGroup(Tex("Long-term memory", color=GREEN, font_size=22), Tex("days to years", color=MGREY, font_size=16)).arrange(DOWN, buff=0.04),
        )
        for brace, label in zip(braces, brace_labels):
            label.next_to(brace, DOWN, buff=0.16)

        percept = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=2.05,
            border_color=BLUE,
            fill_color=WHITE,
            fill_opacity=1.0,
        ).move_to(LEFT * 4.10 + UP * 0.25)

        wm_trace = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=1.08,
            border_color=AMBER,
            fill_color=WHITE,
            fill_opacity=1.0,
        ).move_to(ORIGIN + UP * 0.25)
        wm_label = Tex("maintained after the stimulus disappears", color=AMBER, font_size=18).next_to(wm_trace, DOWN, buff=0.16)

        ltm_cards = Group(*[
            make_image_card(
                stim_path(HOOK_CODE, idx),
                height=0.90,
                border_color=GREEN,
                fill_color=WHITE,
                fill_opacity=1.0,
                buff=0.035,
            )
            for idx in (0, 3, 6)
        ])
        ltm_cards[0].move_to(RIGHT * 3.95 + UP * 0.18)
        ltm_cards[1].move_to(RIGHT * 4.18 + UP * 0.33)
        ltm_cards[2].move_to(RIGHT * 4.42 + UP * 0.48)
        ltm_label = Tex("stabilised across repeated experience", color=GREEN, font_size=18).next_to(ltm_cards, DOWN, buff=0.16)

        arrow_1 = Arrow(
            percept.get_right() + RIGHT * 0.12,
            wm_trace.get_left() + LEFT * 0.12,
            color=AMBER,
            stroke_width=2.0,
            buff=0.06,
            tip_shape=StealthTip,
        )
        arrow_2 = Arrow(
            wm_trace.get_right() + RIGHT * 0.12,
            ltm_cards.get_left() + LEFT * 0.12,
            color=GREEN,
            stroke_width=2.0,
            buff=0.06,
            tip_shape=StealthTip,
        )
        repeat_dots = VGroup(*[
            Dot(radius=0.035, color=GREEN).move_to(
                interpolate(wm_trace.get_right(), ltm_cards.get_left(), alpha) + DOWN * 0.12
            )
            for alpha in np.linspace(0.24, 0.76, 5)
        ])

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(Create(timeline), run_time=0.70)
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(GrowFromCenter(brace), FadeIn(label, shift=UP * 0.04))
                    for brace, label in zip(braces, brace_labels)
                ],
                lag_ratio=0.18,
            ),
            run_time=1.30,
        )
        self.play(FadeIn(percept, scale=0.97), run_time=0.90)
        self.wait(1.20)
        self.play(
            TransformFromCopy(percept, wm_trace),
            Create(arrow_1),
            FadeIn(wm_label, shift=UP * 0.05),
            run_time=1.10,
        )
        self.wait(1.70)
        self.play(
            Create(arrow_2),
            FadeIn(repeat_dots),
            TransformFromCopy(wm_trace, ltm_cards[0]),
            FadeIn(ltm_cards[1:]),
            FadeIn(ltm_label, shift=UP * 0.05),
            run_time=1.15,
        )
        self.wait(3.10)


class Intro03SensoryRecruitmentTension(Scene):
    """Competing hypotheses for where maintained information lives."""

    _MVPA_PATTERN = np.array([
        [0.20, 0.82, 0.34, 0.76],
        [0.88, 0.25, 0.64, 0.31],
        [0.44, 0.92, 0.22, 0.70],
        [0.78, 0.38, 0.58, 0.18],
    ])

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(r"Where is the maintained information stored?")

        stimulus = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=1.38,
            border_color=BLUE,
            fill_color=WHITE,
            fill_opacity=1.0,
        ).move_to(UP * 2.05 + LEFT * 4.65)
        stimulus_label = Tex("memorised image", color=BLUE, font_size=19).next_to(stimulus, RIGHT, buff=0.18)
        memory_token = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=0.86,
            border_color=AMBER,
            fill_color=WHITE,
            fill_opacity=1.0,
        ).move_to(UP * 2.00 + LEFT * 0.20)
        token_label = Tex("maintained content", color=AMBER, font_size=19).next_to(memory_token, RIGHT, buff=0.16)

        classical = brain_schematic(occipital_color=MGREY, classical_color=MGREY, scale_factor=0.78)
        classical_group = classical["group"].move_to(LEFT * 3.40 + DOWN * 0.35)

        sensory = brain_schematic(occipital_color=BLUE, classical_color=MGREY, scale_factor=0.78)
        sensory_group = sensory["group"].move_to(RIGHT * 3.25 + DOWN * 0.35)

        left_caption = VGroup(
            Tex("Classical view", color=MGREY, font_size=24),
            Tex("higher-order areas carry the memory", color=INK, font_size=18),
        ).arrange(DOWN, buff=0.05).next_to(classical_group, DOWN, buff=0.24)
        right_caption = VGroup(
            Tex("Sensory recruitment", color=BLUE, font_size=24),
            Tex("early visual cortex also carries content", color=INK, font_size=18),
        ).arrange(DOWN, buff=0.05).next_to(sensory_group, DOWN, buff=0.24)

        split_arrows = VGroup(
            CurvedArrow(memory_token.get_bottom() + DOWN * 0.04, classical_group.get_top() + UP * 0.04,
                        angle=0.45, color=MGREY, stroke_width=1.8, tip_shape=StealthTip),
            CurvedArrow(memory_token.get_bottom() + DOWN * 0.04, sensory_group.get_top() + UP * 0.04,
                        angle=-0.45, color=BLUE, stroke_width=1.8, tip_shape=StealthTip),
        )

        mvpa_grid = make_pattern_grid(self._MVPA_PATTERN, color=BLUE, cell_size=0.17).move_to(RIGHT * 5.55 + DOWN * 0.15)
        mvpa_arrow = Arrow(
            sensory_group.get_right() + RIGHT * 0.06 + DOWN * 0.12,
            mvpa_grid.get_left() + LEFT * 0.06,
            color=BLUE,
            stroke_width=1.8,
            buff=0.04,
            tip_shape=StealthTip,
        )
        mvpa_label = VGroup(
            Tex("stimulus-specific pattern", color=BLUE, font_size=19),
            Tex("read out with MVPA", color=MGREY, font_size=16),
        ).arrange(DOWN, buff=0.04).next_to(mvpa_grid, DOWN, buff=0.18)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(stimulus, scale=0.97), FadeIn(stimulus_label, shift=RIGHT * 0.04), run_time=0.90)
        self.play(
            TransformFromCopy(stimulus, memory_token),
            FadeIn(token_label, shift=UP * 0.04),
            run_time=0.95,
        )
        self.wait(1.20)
        self.play(
            FadeIn(classical_group, scale=0.96),
            Create(split_arrows[0]),
            FadeIn(left_caption, shift=UP * 0.05),
            run_time=1.00,
        )
        self.wait(1.50)
        self.play(
            FadeIn(sensory_group, scale=0.96),
            Create(split_arrows[1]),
            FadeIn(right_caption, shift=UP * 0.05),
            run_time=1.00,
        )
        self.wait(1.00)
        self.play(
            Create(mvpa_arrow),
            FadeIn(mvpa_grid, scale=0.95),
            FadeIn(mvpa_label, shift=UP * 0.04),
            run_time=0.90,
        )
        self.wait(3.00)


class Intro04ThreeOpenQuestions(Scene):
    """Three consequences of the sensory-recruitment idea."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(r"If early visual cortex matters, three questions immediately follow")

        brain = brain_schematic(occipital_color=BLUE, classical_color=MGREY, scale_factor=0.72)
        brain_group = brain["group"].move_to(ORIGIN + UP * 0.20)
        center_label = Tex("early visual cortex", color=BLUE, font_size=22).next_to(brain_group, DOWN, buff=0.18)

        sensory_row = make_feature_row(
            np.array([0.92, 0.20, 0.74, 0.36, 0.86, 0.18]),
            color=BLUE,
            cell_w=0.18,
            cell_h=0.18,
        )
        memory_row = make_feature_row(
            np.array([0.38, 0.58, 0.44, 0.62, 0.36, 0.56]),
            color=AMBER,
            cell_w=0.18,
            cell_h=0.18,
        )
        sensory_row.move_to(UP * 0.34)
        memory_row.move_to(DOWN * 0.34)
        q1_arrow = Arrow(
            sensory_row.get_bottom() + DOWN * 0.02,
            memory_row.get_top() + UP * 0.02,
            color=MGREY,
            stroke_width=1.4,
            buff=0.04,
            tip_shape=StealthTip,
        )
        format_question = Group(sensory_row, q1_arrow, memory_row).move_to(LEFT * 4.10 + UP * 1.35)
        format_label = VGroup(
            Tex("Same format?", color=BLUE, font_size=22),
            Tex("or transformed memory code?", color=INK, font_size=18),
        ).arrange(DOWN, buff=0.04).next_to(format_question, DOWN, buff=0.16)
        format_branch = CurvedArrow(
            brain_group.get_left() + LEFT * 0.06 + UP * 0.20,
            format_question.get_right() + RIGHT * 0.08,
            angle=0.40,
            color=BLUE,
            stroke_width=1.8,
            tip_shape=StealthTip,
        )

        simple_pattern = VGroup(*[
            Line(LEFT * 0.34 + DOWN * y, RIGHT * 0.34 + DOWN * y, color=MGREY, stroke_width=1.6)
            for y in np.linspace(-0.22, 0.22, 5)
        ]).rotate(PI / 6)
        simple_circle = Circle(radius=0.52, color=MGREY, stroke_width=1.4).set_fill(WHITE, opacity=0.0)
        simple_icon = VGroup(simple_circle, simple_pattern)
        naturalistic = make_image_card(
            stim_path(HOOK_CODE, 0),
            height=0.90,
            border_color=AMBER,
            fill_color=WHITE,
            fill_opacity=1.0,
            buff=0.035,
        )
        simple_icon.move_to(LEFT * 0.62)
        naturalistic.move_to(RIGHT * 0.76)
        q2_arrow = Arrow(
            simple_icon.get_right() + RIGHT * 0.04,
            naturalistic.get_left() + LEFT * 0.04,
            color=AMBER,
            stroke_width=1.6,
            buff=0.04,
            tip_shape=StealthTip,
        )
        stimulus_question = Group(simple_icon, q2_arrow, naturalistic).move_to(RIGHT * 4.15 + UP * 1.20)
        stimulus_label = VGroup(
            Tex("Does it generalise", color=AMBER, font_size=22),
            Tex("from simple stimuli to naturalistic scenes?", color=INK, font_size=18),
        ).arrange(DOWN, buff=0.04).next_to(stimulus_question, DOWN, buff=0.16)
        stimulus_branch = CurvedArrow(
            brain_group.get_right() + RIGHT * 0.06 + UP * 0.10,
            stimulus_question.get_left() + LEFT * 0.08,
            angle=-0.36,
            color=AMBER,
            stroke_width=1.8,
            tip_shape=StealthTip,
        )

        ltm_stack = Group(*[
            make_image_card(
                stim_path(HOOK_CODE, idx),
                height=0.70,
                border_color=GREEN,
                fill_color=WHITE,
                fill_opacity=1.0,
                buff=0.03,
            )
            for idx in (0, 3)
        ])
        ltm_stack.arrange(RIGHT, buff=0.08)
        wm_chip = Group(
            make_image_card(
                stim_path(HOOK_CODE, 6),
                height=0.74,
                border_color=AMBER,
                fill_color=WHITE,
                fill_opacity=1.0,
                buff=0.03,
            ),
            make_pill("delay code", AMBER, font_size=16),
        )
        wm_chip.arrange(DOWN, buff=0.10)
        ltm_stack.move_to(UP * 0.36)
        wm_chip.move_to(DOWN * 0.40)
        q3_arrow = Arrow(
            ltm_stack.get_bottom() + DOWN * 0.02,
            wm_chip.get_top() + UP * 0.02,
            color=GREEN,
            stroke_width=1.6,
            buff=0.04,
            tip_shape=StealthTip,
        )
        ltm_question = Group(ltm_stack, q3_arrow, wm_chip).move_to(DOWN * 2.10)
        ltm_label = VGroup(
            Tex("Does long-term memory", color=GREEN, font_size=22),
            Tex("reshape the working-memory code?", color=INK, font_size=18),
        ).arrange(DOWN, buff=0.04).next_to(ltm_question, DOWN, buff=0.16)
        ltm_branch = Arrow(
            brain_group.get_bottom() + DOWN * 0.08,
            ltm_question.get_top() + UP * 0.08,
            color=GREEN,
            stroke_width=1.8,
            buff=0.04,
            tip_shape=StealthTip,
        )

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(brain_group, scale=0.96), FadeIn(center_label, shift=UP * 0.04), run_time=0.90)
        self.wait(1.00)
        self.play(
            Create(format_branch),
            FadeIn(format_question, scale=0.95),
            FadeIn(format_label, shift=UP * 0.04),
            run_time=0.95,
        )
        self.wait(1.20)
        self.play(
            Create(stimulus_branch),
            FadeIn(stimulus_question, scale=0.95),
            FadeIn(stimulus_label, shift=UP * 0.04),
            run_time=0.95,
        )
        self.wait(1.20)
        self.play(
            Create(ltm_branch),
            FadeIn(ltm_question, scale=0.95),
            FadeIn(ltm_label, shift=UP * 0.04),
            run_time=0.95,
        )
        self.wait(3.10)


class Intro05MethodologicalBottleneck(Scene):
    """Constraint intersection that legacy stimulus sources rarely satisfy."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"Testing all three questions requires an unusually precise stimulus set"
        )

        continuum = Group(*[
            make_image_card(
                stim_path(CONTINUUM_CODE, idx),
                height=1.08,
                border_color=BLUE,
                fill_color=WHITE,
                fill_opacity=1.0,
                buff=0.035,
            )
            for idx in (0, 3, 6, 9)
        ])
        continuum.arrange(RIGHT, buff=0.12)
        continuum.move_to(ORIGIN + UP * 0.25)
        continuum_ring = SurroundingRectangle(continuum, color=BLUE, stroke_width=2.0, buff=0.10)
        continuum_label = Tex("the stimulus set we actually need", color=BLUE, font_size=22).next_to(continuum, DOWN, buff=0.18)

        req_specs = [
            ("naturalistic", BLUE, LEFT * 4.45 + UP * 2.10, continuum.get_left() + LEFT * 0.12 + UP * 0.20),
            ("fine-grained control", AMBER, RIGHT * 4.40 + UP * 2.10, continuum.get_right() + RIGHT * 0.12 + UP * 0.20),
            (r"usable for WM + LTM", GREEN, LEFT * 4.30 + DOWN * 1.25, continuum.get_left() + LEFT * 0.06 + DOWN * 0.20),
            ("distinct EVC patterns", BLUE, RIGHT * 4.35 + DOWN * 1.25, continuum.get_right() + RIGHT * 0.06 + DOWN * 0.20),
        ]
        req_labels = VGroup()
        req_arrows = VGroup()
        for text, color, pos, end in req_specs:
            label = Tex(text, color=color, font_size=20).move_to(pos)
            arrow = Arrow(
                label.get_center() + (DOWN if pos[1] > 0 else UP) * 0.18,
                end,
                color=color,
                stroke_width=1.7,
                buff=0.10,
                tip_shape=StealthTip,
            )
            req_labels.add(label)
            req_arrows.add(arrow)

        left_block = make_source_block(
            "Manual selection",
            [("building_observatory", 0), ("item_sofa", 0), ("animal_fish", 0)],
            "too ad hoc",
        ).move_to(LEFT * 4.05 + DOWN * 2.55)
        right_block = make_source_block(
            r"THINGS / web images",
            [("vehicle_campervan", 0), ("vehicle_sailboat", 0), ("vehicle_scooter", 0)],
            "too dissimilar",
        ).move_to(RIGHT * 4.05 + DOWN * 2.55)

        new_way = make_callout(
            r"Existing sources rarely land in this narrow intersection.",
            RED,
            font_size=22,
        ).to_edge(DOWN, buff=0.30)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(continuum), Create(continuum_ring), FadeIn(continuum_label, shift=UP * 0.04), run_time=1.00)
        self.wait(0.90)
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(
                        FadeIn(label, shift=UP * 0.04 if label.get_center()[1] > 0 else DOWN * 0.04),
                        Create(arrow),
                    )
                    for label, arrow in zip(req_labels, req_arrows)
                ],
                lag_ratio=0.16,
            ),
            run_time=1.80,
        )
        self.wait(1.30)
        self.play(FadeIn(left_block, shift=UP * 0.08), FadeIn(right_block, shift=UP * 0.08), run_time=1.10)
        self.wait(1.60)
        self.play(FadeIn(new_way, shift=UP * 0.05), run_time=0.70)
        self.wait(3.10)


class Intro06ThesisRoadmap(Scene):
    """Build a continuum, validate it, then use it in fMRI."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"Thesis strategy: build the right stimulus space, then test the theory"
        )

        prompt_text = Tex(
            r'"observatory in a coherent scene"',
            color=INK,
            font_size=20,
        )
        prompt_rule = Line(
            prompt_text.get_left() + DOWN * 0.14,
            prompt_text.get_right() + DOWN * 0.14,
            color=LGREY,
            stroke_width=1.6,
        )
        prompt_group = VGroup(
            Tex("prompt", color=MGREY, font_size=17),
            prompt_text,
            prompt_rule,
        ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        prompt_group.move_to(LEFT * 5.00 + UP * 2.00)

        generated = Group(*[
            make_image_card(
                stim_path(CONTINUUM_CODE, idx),
                height=0.92,
                border_color=BLUE,
                fill_color=WHITE,
                fill_opacity=1.0,
                buff=0.04,
            )
            for idx in (0, 5, 9)
        ])
        generated.arrange(RIGHT, buff=0.12)
        generated.move_to(LEFT * 0.65 + UP * 2.00)
        generated_label = Tex("generated variations", color=BLUE, font_size=18).next_to(generated, UP, buff=0.12)

        top_arrow = Arrow(
            prompt_group.get_right() + RIGHT * 0.10,
            generated.get_left() + LEFT * 0.10,
            color=BLUE,
            stroke_width=1.8,
            buff=0.06,
            tip_shape=StealthTip,
        )

        continuum = Group(*[
            make_image_card(
                stim_path(CONTINUUM_CODE, idx),
                height=1.10,
                border_color=BLUE,
                fill_color=WHITE,
                fill_opacity=1.0,
                buff=0.04,
            )
            for idx in (0, 3, 6, 9)
        ])
        continuum.arrange(RIGHT, buff=0.12)
        continuum.move_to(ORIGIN + UP * 0.55)
        continuum_label = Tex("selected perceptual continuum", color=BLUE, font_size=20).next_to(continuum, DOWN, buff=0.16)
        down_arrow = Arrow(
            generated.get_bottom() + DOWN * 0.04,
            continuum.get_top() + UP * 0.04,
            color=BLUE,
            stroke_width=1.8,
            buff=0.06,
            tip_shape=StealthTip,
        )

        study1_triplet = Group(*[
            make_image_card(
                stim_path(CONTINUUM_CODE, idx),
                height=0.72,
                border_color=BLUE if idx == 3 else LGREY,
                fill_color=WHITE,
                fill_opacity=1.0,
                buff=0.03,
            )
            for idx in (0, 3, 6)
        ]).arrange(RIGHT, buff=0.12)
        study1_q = Tex("which is closer?", color=INK, font_size=18).next_to(study1_triplet, UP, buff=0.14)
        study1_panel = Group(
            Tex("Study 1", color=BLUE, font_size=24),
            Line(LEFT * 1.00, RIGHT * 1.00, color=BLUE, stroke_width=2.4),
            study1_q,
            study1_triplet,
            Tex("validate perceptual scaling and memory sensitivity", color=INK, font_size=17),
        )
        study1_panel.arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        study1_panel.move_to(LEFT * 3.70 + DOWN * 2.00)

        brain = brain_schematic(occipital_color=BLUE, classical_color=MGREY, scale_factor=0.42)
        study2_rows = Group(
            make_feature_row(np.array([0.90, 0.20, 0.75, 0.35, 0.88]), color=BLUE, cell_w=0.12, cell_h=0.12),
            make_feature_row(np.array([0.42, 0.58, 0.46, 0.60, 0.40]), color=AMBER, cell_w=0.12, cell_h=0.12),
        ).arrange(DOWN, buff=0.18)
        study2_panel = Group(
            Tex("Study 2", color=GREEN, font_size=24),
            Line(LEFT * 1.00, RIGHT * 1.00, color=GREEN, stroke_width=2.4),
            brain["group"],
            Tex("compare perception and working-memory formats", color=INK, font_size=17),
            study2_rows,
        )
        study2_panel.arrange(DOWN, buff=0.14)
        study2_panel.move_to(RIGHT * 3.70 + DOWN * 2.00)

        down_arrow_1 = Arrow(
            continuum.get_bottom() + LEFT * 1.00 + DOWN * 0.05,
            study1_panel.get_top() + UP * 0.08,
            color=BLUE,
            stroke_width=1.8,
            buff=0.06,
            tip_shape=StealthTip,
        )
        down_arrow_2 = Arrow(
            continuum.get_bottom() + RIGHT * 1.00 + DOWN * 0.05,
            study2_panel.get_top() + UP * 0.08,
            color=GREEN,
            stroke_width=1.8,
            buff=0.06,
            tip_shape=StealthTip,
        )

        callout = make_callout(
            r"First build the right stimulus space. Then use it to test the theory.",
            GREEN,
            font_size=22,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(prompt_group, shift=UP * 0.05), run_time=0.75)
        self.wait(0.90)
        self.play(
            Create(top_arrow),
            LaggedStartMap(FadeIn, generated, lag_ratio=0.16),
            FadeIn(generated_label, shift=UP * 0.04),
            run_time=1.10,
        )
        self.wait(1.00)
        self.play(
            Create(down_arrow),
            LaggedStartMap(FadeIn, continuum, lag_ratio=0.12),
            FadeIn(continuum_label, shift=UP * 0.04),
            run_time=1.00,
        )
        self.wait(1.10)
        self.play(
            FadeIn(study1_panel, shift=UP * 0.08),
            FadeIn(study2_panel, shift=UP * 0.08),
            Create(down_arrow_1),
            Create(down_arrow_2),
            run_time=1.30,
        )
        self.wait(1.60)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.60)
        self.wait(3.00)
