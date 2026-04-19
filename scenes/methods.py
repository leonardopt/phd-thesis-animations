"""
Methodological framework — consolidated public entrypoint.

Public scenes (thesis Chapter 2 order):
    MethodsStimulusRequirements — design requirements for the stimuli
    MethodsGenerativeSynthesis  — why deep generative modelling solved the problem
    MethodsFrameworkPipeline    — how the framework fed Study 1 and Study 2

Render examples:
    uv run manim scenes/methods.py MethodsStimulusRequirements -ql
    uv run manim scenes/methods.py MethodsGenerativeSynthesis -ql
    uv run manim scenes/methods.py MethodsFrameworkPipeline -ql
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
if str(_SCENES_DIR) not in sys.path:
    sys.path.insert(0, str(_SCENES_DIR))

from utils import REPO_ROOT, env_path, section_output_dir


_SECTION_OUTPUT_DIR = section_output_dir("methods")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"

_METHODS_SCENE_ORDER: dict[str, str] = {
    "MethodsStimulusRequirements": "01",
    "MethodsGenerativeSynthesis": "02",
    "MethodsFrameworkPipeline": "03",
}


class _MethodsNumberedScene:
    """Mixin that assigns methods output filenames while preserving scene names."""

    def __init__(self, *args, **kwargs):
        scene_name = self.__class__.__name__
        number = _METHODS_SCENE_ORDER.get(scene_name, "")
        config.output_file = f"{number}_{scene_name}" if number else scene_name
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

_EXEMPLAR_CODE = "building_observatory"


def stim_path(code: str, idx: int) -> str:
    """Return an absolute path to a local stimulus image."""
    return str(_INTRO_STIM_DIR / f"{code}-{idx:02d}.png")


def title_block(title_text: str, subtitle_text: str | None = None) -> VGroup:
    """Return the standard methods title group."""
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
        stroke_width=1.4,
    ).set_fill(fill_color, opacity=fill_opacity)
    image.move_to(frame.get_center())
    return Group(frame, image)


def make_callout(text: str, color: str, *, font_size: float = 23) -> VGroup:
    """Create a takeaway line."""
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
    """Create a clean two-line information card with a left accent bar."""
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


def make_step_card(
    step_number: int,
    title_text: str,
    body: Mobject,
    *,
    accent: str,
    width: float = 2.62,
    height: float = 3.08,
) -> Group:
    """Create a compact workflow card with a numbered header."""
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.16,
        stroke_color=LGREY,
        stroke_width=1.4,
    ).set_fill(PANEL, opacity=0.96)

    badge_box = RoundedRectangle(
        width=0.34,
        height=0.34,
        corner_radius=0.08,
        stroke_width=0,
    ).set_fill(accent, opacity=1.0)
    badge_text = Tex(str(step_number), color=WHITE, font_size=16)
    badge = VGroup(badge_box, badge_text)

    title = Tex(title_text, color=INK, font_size=18)
    header = VGroup(badge, title).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
    header.next_to(frame.get_top(), DOWN, buff=0.18)
    header.align_to(frame, LEFT).shift(RIGHT * 0.18)

    body_group = body.copy()
    max_body_width = width - 0.30
    max_body_height = height - header.height - 0.52
    if body_group.width > max_body_width:
        body_group.scale_to_fit_width(max_body_width)
    if body_group.height > max_body_height:
        body_group.scale_to_fit_height(max_body_height)
    body_group.next_to(header, DOWN, buff=0.18)
    body_group.set_x(frame.get_center()[0])

    return Group(frame, header, body_group)


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


class MethodsStimulusRequirements(Scene):
    """Chapter 2.1 — design requirements for naturalistic stimuli."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Design requirements for naturalistic stimuli}",
            "Ecological validity without sacrificing experimental control",
        )

        continuum = Group(
            *[
                make_image_card(
                    stim_path(_EXEMPLAR_CODE, idx),
                    height=0.96,
                    border_color=BLUE,
                    fill_color=WHITE,
                    fill_opacity=1.0,
                    buff=0.035,
                )
                for idx in (0, 3, 6, 9)
            ]
        ).arrange(RIGHT, buff=0.10)
        continuum_frame = RoundedRectangle(
            width=9.30,
            height=2.72,
            corner_radius=0.18,
            stroke_color=LGREY,
            stroke_width=1.4,
        ).set_fill(PANEL, opacity=0.96)
        continuum_title = Tex("Target stimulus space", color=BLUE, font_size=22)
        continuum_title.next_to(continuum_frame.get_top(), DOWN, buff=0.18)
        continuum.move_to(continuum_frame.get_center() + UP * 0.05)
        continuum_caption = Tex(
            "same semantic identity, fine-grained perceptual variation",
            color=MGREY,
            font_size=17,
        ).next_to(continuum, DOWN, buff=0.18)
        continuum_panel = Group(continuum_frame, continuum_title, continuum, continuum_caption)

        requirement_cards = VGroup(
            VGroup(
                make_info_card(
                    "Ecological validity",
                    "naturalistic images with rich perceptual and semantic structure",
                    accent=BLUE,
                    width=4.70,
                    height=1.22,
                ),
                make_info_card(
                    "Perceptual control",
                    "graded similarity with stable semantic identity",
                    accent=AMBER,
                    width=4.70,
                    height=1.22,
                ),
            ).arrange(RIGHT, buff=0.22),
            VGroup(
                make_info_card(
                    "Unified paradigm",
                    "usable in both working-memory and long-term-memory tasks",
                    accent=GREEN,
                    width=4.70,
                    height=1.22,
                ),
                make_info_card(
                    "fMRI sensitivity",
                    "detailed visual features for multivariate analyses in [V1, V2, V3]",
                    accent=BLUE,
                    width=4.70,
                    height=1.22,
                ),
            ).arrange(RIGHT, buff=0.22),
        ).arrange(DOWN, buff=0.18)

        callout = make_callout(
            "The stimuli should maintain ecological validity while providing sufficient experimental control.",
            GREEN,
            font_size=19,
        ).to_edge(DOWN, buff=0.34)

        content = Group(continuum_panel, requirement_cards).arrange(DOWN, buff=0.30)
        content.next_to(title, DOWN, buff=0.28)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(continuum_panel, shift=UP * 0.05), run_time=0.95)
        self.play(
            LaggedStart(
                *[FadeIn(card, shift=UP * 0.06) for row in requirement_cards for card in row],
                lag_ratio=0.14,
            ),
            run_time=1.15,
        )
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.50)


class MethodsGenerativeSynthesis(Scene):
    """Chapter 2.2 — why deep generative modelling solves the design problem."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Why stimulus synthesis?}",
            "Traditional sources were suboptimal for the full design space",
        )

        source_header = Tex("Traditional sources", color=MGREY, font_size=20)
        source_cards = VGroup(
            make_info_card(
                "Manual selection",
                "ad hoc, slow, limited stimulus sets",
                accent=RED,
                width=4.55,
                height=1.10,
                subtitle_color=RED,
            ),
            make_info_card(
                "Web datasets",
                "cluttered images, heterogeneous features, poor control",
                accent=RED,
                width=4.55,
                height=1.10,
                subtitle_color=RED,
            ),
            make_info_card(
                "Existing databases",
                "too few matched variants; often low resolution or too dissimilar",
                accent=RED,
                width=4.55,
                height=1.10,
                subtitle_color=RED,
            ),
        ).arrange(DOWN, buff=0.16)
        source_column = VGroup(source_header, source_cards).arrange(DOWN, buff=0.16, aligned_edge=LEFT)

        synth_header = Tex("Deep generative modelling", color=BLUE, font_size=20)
        synth_examples = Group(
            *[
                make_image_card(
                    stim_path(_EXEMPLAR_CODE, idx),
                    height=0.62,
                    border_color=BLUE,
                    fill_color=WHITE,
                    fill_opacity=1.0,
                    buff=0.03,
                )
                for idx in (0, 5, 9)
            ]
        ).arrange(RIGHT, buff=0.05)
        synth_cards = VGroup(
            make_info_card(
                "Promptable generation",
                "tailor images directly to the experimental goal",
                accent=BLUE,
                width=4.65,
                height=1.10,
            ),
            make_info_card(
                "High-resolution output",
                "photorealistic detail suitable for neuroimaging",
                accent=GREEN,
                width=4.65,
                height=1.10,
            ),
            make_info_card(
                "Flexible variation",
                "generate large numbers of controlled exemplars",
                accent=BLUE,
                width=4.65,
                height=1.10,
            ),
        ).arrange(DOWN, buff=0.16)
        synth_column = Group(synth_header, synth_examples, synth_cards).arrange(
            DOWN,
            buff=0.16,
            aligned_edge=LEFT,
        )

        arrow = Arrow(
            LEFT * 0.60,
            RIGHT * 0.60,
            color=MGREY,
            stroke_width=1.8,
            buff=0.0,
            tip_length=0.14,
        )

        content = Group(source_column, arrow, synth_column).arrange(
            RIGHT,
            buff=0.42,
            aligned_edge=UP,
        )
        content.next_to(title, DOWN, buff=0.34)

        callout = make_callout(
            "Deep generative models increase ecological validity while maintaining experimental control.",
            BLUE,
            font_size=19,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(source_column, shift=UP * 0.05), run_time=0.85)
        self.play(GrowArrow(arrow), run_time=0.35)
        self.play(FadeIn(synth_column, shift=UP * 0.05), run_time=0.85)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.50)


class MethodsFrameworkPipeline(Scene):
    """Chapter 2.3 — summary and rationale bridging the framework to the studies."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{From framework to studies}",
            "Study 1 built and validated the stimulus space; Study 2 used it in fMRI",
        )

        prompt_body = VGroup(
            Tex("text prompt", color=MGREY, font_size=14),
            Tex(r"``observatory''", color=INK, font_size=17),
            Tex("same object-scene identity", color=MGREY, font_size=14),
        ).arrange(DOWN, buff=0.06)

        interpolate_body = Group(
            Group(
                *[
                    make_image_card(
                        stim_path(_EXEMPLAR_CODE, idx),
                        height=0.34,
                        border_color=BLUE,
                        fill_color=WHITE,
                        fill_opacity=1.0,
                        buff=0.02,
                    )
                    for idx in (0, 3, 6, 9)
                ]
            ).arrange(RIGHT, buff=0.03),
            Tex("anchor/guide + interpolation", color=MGREY, font_size=14),
            Tex("ordered perceptual continuum", color=MGREY, font_size=14),
        ).arrange(DOWN, buff=0.08)

        study1_body = VGroup(
            Tex("Stage 1: generation", color=INK, font_size=15),
            Tex("Stage 2: triplet scaling (N = 1,113)", color=MGREY, font_size=14),
            Tex("Stage 3: WM pre-test (N = 260)", color=MGREY, font_size=14),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        study2_brain = brain_icon_with_evc(highlight_color=BLUE, scale_factor=0.36)
        study2_body = Group(
            study2_brain["group"],
            Tex("2-session fMRI", color=GREEN, font_size=15),
            Tex("memory task + perceptual task", color=MGREY, font_size=14),
            Tex("format, recruitment, LTM", color=MGREY, font_size=14),
        ).arrange(DOWN, buff=0.08)

        cards = Group(
            make_step_card(1, "Prompt", prompt_body, accent=BLUE),
            make_step_card(2, "Interpolate", interpolate_body, accent=BLUE),
            make_step_card(3, "Study 1", study1_body, accent=BLUE),
            make_step_card(4, "Study 2", study2_body, accent=GREEN),
        ).arrange(RIGHT, buff=0.24, aligned_edge=UP)
        cards.next_to(title, DOWN, buff=0.42)

        arrows = VGroup(
            *[
                Arrow(
                    cards[idx].get_right() + RIGHT * 0.04,
                    cards[idx + 1].get_left() + LEFT * 0.04,
                    color=MGREY,
                    stroke_width=1.6,
                    buff=0.04,
                    tip_shape=StealthTip,
                    tip_length=0.14,
                )
                for idx in range(len(cards) - 1)
            ]
        )

        callout = make_callout(
            "Build the stimulus space first. Then use it to test the theory.",
            GREEN,
            font_size=21,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(cards[0], shift=UP * 0.05), run_time=0.50)
        for idx in range(1, len(cards)):
            self.play(
                Create(arrows[idx - 1]),
                FadeIn(cards[idx], shift=UP * 0.05),
                run_time=0.52,
            )
        self.wait(1.00)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.50)


_PUBLIC_SCENES: tuple[type[Scene], ...] = (
    MethodsStimulusRequirements,
    MethodsGenerativeSynthesis,
    MethodsFrameworkPipeline,
)

for _scene_cls in _PUBLIC_SCENES:
    globals()[_scene_cls.__name__] = _wrap_scene(_scene_cls)

__all__ = [scene_cls.__name__ for scene_cls in _PUBLIC_SCENES]
