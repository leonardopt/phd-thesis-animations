"""
Introduction — consolidated public entrypoint.

Render from this file to keep all introduction outputs in the same
`media/videos/01_intro/...` folder.

Public scenes (narrative order):
    IntroCognitiveProblemA     — naturalistic input                   (~15 s)
    IntroCognitiveProblemB     — delay with fixation                  (~15 s)
    IntroCognitiveProblemC     — memory-guided decision               (~15 s)
    IntroClassicalView         — PFC / parietal classical view        (~45 s)
    IntroSensoryRecruitment    — MVPA + open debate                   (~75 s)
    IntroResearchQuestions     — three open questions                 (~60 s)

Render examples:
    uv run manim scenes/intro.py IntroCognitiveProblemA -ql
    uv run manim scenes/intro.py IntroCognitiveProblemB -ql
    uv run manim scenes/intro.py IntroCognitiveProblemC -ql
    uv run manim scenes/intro.py IntroClassicalView -ql
    uv run manim scenes/intro.py IntroSensoryRecruitment -ql
    uv run manim scenes/intro.py IntroResearchQuestions -ql
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


_SECTION_OUTPUT_DIR = section_output_dir("intro")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"


# Narrative order — drives output filenames via _wrap_scene / _IntroductionNumberedScene.
_INTRODUCTION_SCENE_ORDER: dict[str, str] = {
    "IntroCognitiveProblemA": "01",
    "IntroCognitiveProblemB": "02",
    "IntroCognitiveProblemC": "03",
    "IntroClassicalView": "04",
    "IntroSensoryRecruitment": "05",
    "IntroResearchQuestions": "06",
}


class _IntroductionNumberedScene:
    """Mixin that assigns intro output filenames while preserving future numbering."""

    def __init__(self, *args, **kwargs):
        """Set `config.output_file` from the intro registry before scene init."""
        scene_name = self.__class__.__name__
        number = _INTRODUCTION_SCENE_ORDER.get(scene_name, "")
        config.output_file = f"{number}_{scene_name}" if number else scene_name
        super().__init__(*args, **kwargs)


def _wrap_scene(scene_cls: type[Scene]) -> type[Scene]:
    """Wrap a scene so it inherits the intro output naming without renaming it."""

    class _Wrapped(_IntroductionNumberedScene, scene_cls):
        """Wrapped scene type that adds intro output naming while preserving metadata."""

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
_REFERENCE_DIR = REPO_ROOT / "assets" / "images" / "references" / "working_memory"
_FUNAHASHI_1989_FIG = str(_REFERENCE_DIR / "funahashi1989_delay_activity.png")
_JONIDES_1993_FIG = str(_REFERENCE_DIR / "jonides1993_pet.png")
_AWH_JONIDES_2001_FIG = str(_REFERENCE_DIR / "awhjonides2001_spatial_wm.png")
_HARRISON_TONG_2009_FIG = str(_REFERENCE_DIR / "harrisontong2009_decoding.png")

_EXEMPLAR_CODE = "building_observatory"
_HOOK_CODE = "landscape_element_forest_river"  # opening hook scenes A–C


def stim_path(code: str, idx: int) -> str:
    """Return an absolute path to a local stimulus image."""
    return str(_INTRO_STIM_DIR / f"{code}-{idx:02d}.png")


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


def make_literature_entry(
    title_text: str,
    claim_lines: tuple[str, ...],
    ref_lines: tuple[str, ...],
    *,
    accent: str,
    divider_width: float = 4.60,
) -> VGroup:
    """Create a compact literature block with short claims and citation lines."""
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
) -> VGroup:
    """Create a framed snapshot from a seminal paper with a short caption."""
    image_card = make_image_card(
        image_path,
        height=height,
        border_color=accent,
        fill_color=WHITE,
        fill_opacity=1.0,
        buff=0.045,
    )
    label = Tex(label_text, color=accent, font_size=18)
    refs = Tex(ref_text, color=MGREY, font_size=14)
    return Group(image_card, label, refs).arrange(DOWN, buff=0.08)


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


class IntroCognitiveProblemA(Scene):
    """Scene A — behavioral problem: naturalistic input → abrupt interruption → probe."""

    _ORDER = (5, 3, 7, 1, 8, 2, 6, 4)  # frame cycling order (pseudo-random)

    def construct(self) -> None:
        self.camera.background_color = BLACK

        # ── Video simulation: hard cuts, no dissolve ───────────────────────────
        def _frame(idx: int) -> ImageMobject:
            img = ImageMobject(stim_path(_HOOK_CODE, idx))
            img.height = 5.80
            img.move_to(ORIGIN)
            return img

        first = _frame(self._ORDER[0])
        self.play(FadeIn(first, run_time=0.40))
        self.wait(0.45)

        current = first
        for idx in self._ORDER[1:]:
            nxt = _frame(idx)
            self.remove(current)
            self.add(nxt)
            self.wait(0.12)
            current = nxt

        # Abrupt blackout — no fade
        self.remove(current)

        # Fixation cross during delay: mirrors the actual experiment
        fix = VGroup(
            Line(UP * 0.20, DOWN * 0.20, stroke_width=2.4, color="#666666"),
            Line(LEFT * 0.20, RIGHT * 0.20, stroke_width=2.4, color="#666666"),
        )
        self.add(fix)
        self.wait(1.00)
        self.remove(fix)
        self.wait(0.10)

        # ── Probe question ─────────────────────────────────────────────────────
        question = Tex(r"Which probe matches?", color=WHITE, font_size=44)

        probe_target = make_image_card(
            stim_path(_HOOK_CODE, 5), height=2.40,
            border_color=AMBER, fill_color=BLACK, fill_opacity=1.0, buff=0.05,
        )
        probe_foil = make_image_card(
            stim_path(_HOOK_CODE, 8), height=2.40,
            border_color="#555555", fill_color=BLACK, fill_opacity=1.0, buff=0.05,
        )
        probes = Group(probe_target, probe_foil).arrange(RIGHT, buff=0.70)

        # Anchor question + probes as a unit so spacing is always consistent
        content = Group(question, probes).arrange(DOWN, buff=0.50)
        content.move_to(ORIGIN)

        self.play(FadeIn(question, shift=DOWN * 0.06), run_time=0.50)
        self.play(
            LaggedStart(
                FadeIn(probe_target, scale=0.97),
                FadeIn(probe_foil, scale=0.97),
                lag_ratio=0.28,
            ),
            run_time=0.70,
        )
        self.wait(3.50)


class IntroCognitiveProblemB(Scene):
    """Scene B — make perception → interruption → maintenance → comparison visible."""

    _STRIP = (0, 2, 4, 6, 8)
    _FROZEN_IDX = 4   # frame kept in memory

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"Perception $\to$ interruption $\to$ maintenance $\to$ comparison"
        )

        # ── Row 1: frame strip (left-biased so cut line + dead zone fit right) ─
        CARD_H = 1.05
        frozen_pos = list(self._STRIP).index(self._FROZEN_IDX)
        strip_cards = Group(
            *[
                make_image_card(
                    stim_path(_HOOK_CODE, idx),
                    height=CARD_H,
                    border_color=BLUE if idx == self._FROZEN_IDX else LGREY,
                    fill_color=WHITE, fill_opacity=1.0, buff=0.035,
                )
                for idx in self._STRIP
            ]
        ).arrange(RIGHT, buff=0.22)
        strip_cards.next_to(title, DOWN, buff=0.40)
        strip_cards.shift(LEFT * 1.50)  # push left: leaves ~3 u on right for cut + dead zone

        time_dots = VGroup(
            *[
                Dot(radius=0.05, color=BLUE if idx == self._FROZEN_IDX else MGREY)
                for idx in self._STRIP
            ]
        )
        for dot, card in zip(time_dots, strip_cards):
            dot.next_to(card, DOWN, buff=0.12)

        frozen_card = strip_cards[frozen_pos]
        frozen_ring = SurroundingRectangle(
            frozen_card, color=BLUE, stroke_width=2.4, buff=0.07, corner_radius=0.07,
        )

        # ── Interruption: dashed line + grey dead zone ─────────────────────────
        cut_x = strip_cards[-1].get_right()[0] + 0.50
        zone_top = strip_cards.get_top()[1] + 0.22
        zone_bot = time_dots.get_bottom()[1] - 0.16
        cut_line = DashedLine(
            [cut_x, zone_top, 0], [cut_x, zone_bot, 0],
            color=RED, stroke_width=2.0, dash_length=0.10,
        )
        cut_label = Tex(r"\textbf{interruption}", color=RED, font_size=15)
        cut_label.next_to(cut_line, UP, buff=0.10)

        dead_zone = Rectangle(
            width=2.40, height=zone_top - zone_bot, stroke_width=0,
        ).set_fill(LGREY, opacity=0.16)
        dead_zone.next_to(cut_line, RIGHT, buff=0.0)
        dead_zone.align_to([0, zone_bot, 0], DOWN)

        # ── Row 2: brain (center-left) and probe (right) ───────────────────────
        brain_parts = brain_icon_with_evc(highlight_color=AMBER, scale_factor=0.76)
        brain_group = brain_parts["group"]
        brain_group.move_to(LEFT * 0.60 + DOWN * 1.20)

        wm_trace = make_image_card(
            stim_path(_HOOK_CODE, self._FROZEN_IDX), height=0.76,
            border_color=AMBER, fill_color=WHITE, fill_opacity=1.0, buff=0.025,
        )
        wm_trace.move_to(brain_group.get_center() + LEFT * 0.18 + UP * 0.10)
        wm_label = Tex("WM trace", color=AMBER, font_size=14)
        wm_label.next_to(wm_trace, DOWN, buff=0.08)

        # Straight arrow: frozen frame bottom → brain top
        encode_arrow = Arrow(
            frozen_card.get_bottom() + DOWN * 0.06,
            brain_group.get_top() + UP * 0.06,
            color=BLUE, stroke_width=1.8, buff=0.06, tip_shape=StealthTip,
        )

        probe = make_image_card(
            stim_path(_HOOK_CODE, self._FROZEN_IDX), height=0.82,
            border_color=GREEN, fill_color=WHITE, fill_opacity=1.0, buff=0.03,
        )
        probe.move_to(RIGHT * 4.60 + DOWN * 1.20)
        probe_label = Tex("probe", color=GREEN, font_size=14)
        probe_label.next_to(probe, DOWN, buff=0.08)

        compare_arrow = Arrow(
            probe.get_left() + LEFT * 0.04,
            brain_group.get_right() + RIGHT * 0.04,
            color=GREEN, stroke_width=1.8, buff=0.06, tip_shape=StealthTip,
        )
        compare_label = Tex("compare", color=GREEN, font_size=14)
        compare_label.next_to(compare_arrow, UP, buff=0.08)

        # ── Phase bar ─────────────────────────────────────────────────────────
        phase_bar = VGroup(
            Tex("perception", color=BLUE, font_size=18),
            Tex(r"$\to$", color=LGREY, font_size=18),
            Tex("interruption", color=RED, font_size=18),
            Tex(r"$\to$", color=LGREY, font_size=18),
            Tex("maintenance", color=AMBER, font_size=18),
            Tex(r"$\to$", color=LGREY, font_size=18),
            Tex("comparison", color=GREEN, font_size=18),
        ).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.28)

        # ── Animation ─────────────────────────────────────────────────────────
        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.65)
        self.play(
            LaggedStart(*[FadeIn(c, shift=UP * 0.04) for c in strip_cards], lag_ratio=0.12),
            FadeIn(time_dots),
            run_time=0.80,
        )
        self.play(Create(frozen_ring), run_time=0.45)
        self.wait(0.40)
        self.play(
            Create(cut_line),
            FadeIn(cut_label, shift=DOWN * 0.04),
            FadeIn(dead_zone),
            run_time=0.55,
        )
        self.wait(0.30)
        self.play(FadeIn(brain_group, scale=0.97), run_time=0.55)
        self.play(
            Create(encode_arrow),
            TransformFromCopy(frozen_card, wm_trace),
            FadeIn(wm_label, shift=UP * 0.04),
            run_time=0.85,
        )
        self.wait(0.60)
        self.play(FadeIn(probe, scale=0.97), FadeIn(probe_label), run_time=0.50)
        self.play(Create(compare_arrow), FadeIn(compare_label, shift=DOWN * 0.04), run_time=0.50)
        self.play(FadeIn(phase_bar, shift=UP * 0.04), run_time=0.55)
        self.wait(3.50)


class IntroCognitiveProblemC(Scene):
    """Scene C — LTM as a top-down modulator of the maintained WM trace."""

    _FROZEN_IDX = 4
    # Prior specs: (height, opacity) — smallest+faintest = oldest, largest+brightest = most recent
    _PRIOR_SPECS = [(0.62, 0.28), (0.74, 0.56), (0.86, 0.90)]

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Long-term memory modulates the maintained trace}",
            r"Prior exposure shapes the WM representation --- without replacing it",
        )

        # ── Brain + WM trace (prominent; this is the focal element) ───────────
        brain_parts = brain_icon_with_evc(highlight_color=AMBER, scale_factor=1.00)
        brain_group = brain_parts["group"]
        brain_group.move_to(RIGHT * 0.80 + DOWN * 0.40)

        wm_trace = make_image_card(
            stim_path(_HOOK_CODE, self._FROZEN_IDX), height=0.86,
            border_color=AMBER, fill_color=WHITE, fill_opacity=1.0, buff=0.03,
        )
        wm_trace.move_to(brain_group.get_center() + LEFT * 0.20 + UP * 0.12)
        wm_label = Tex("WM trace", color=AMBER, font_size=17)
        wm_label.next_to(wm_trace, DOWN, buff=0.10)

        # ── Prior exposures: diagonal fan (oldest bottom-left → newest top-right)
        fan_anchors = [
            LEFT * 4.60 + DOWN * 0.90,
            LEFT * 4.20 + DOWN * 0.35,
            LEFT * 3.80 + UP * 0.20,
        ]
        prior_cards = Group(
            *[
                make_image_card(
                    stim_path(_HOOK_CODE, self._FROZEN_IDX), height=h,
                    border_color=GREEN, fill_color=WHITE, fill_opacity=1.0, buff=0.025,
                ).set(opacity=op).move_to(anchor)
                for (h, op), anchor in zip(self._PRIOR_SPECS, fan_anchors)
            ]
        )

        prior_header = Tex("prior exposures", color=GREEN, font_size=19)
        prior_header.move_to(LEFT * 4.20 + UP * 1.05)
        prior_sub = Tex("repetition history / familiarity", color=GREEN, font_size=15)
        prior_sub.next_to(prior_cards, DOWN, buff=0.18)

        # ── Modulatory arrow: most-recent card → WM trace ─────────────────────
        mod_start = prior_cards[-1].get_right() + RIGHT * 0.08
        mod_end = wm_trace.get_left() + LEFT * 0.06
        mod_arrow = CurvedArrow(
            mod_start, mod_end,
            angle=-0.40, color=GREEN, stroke_width=2.0, tip_shape=StealthTip,
        )
        mod_label = Tex("top-down modulation", color=GREEN, font_size=16)
        mod_label.next_to(mod_arrow.get_center(), UP, buff=0.18)

        # ── Callout ────────────────────────────────────────────────────────────
        callout = make_callout(
            r"LTM shapes the trace --- it does not replace it.",
            GREEN, font_size=22,
        ).to_edge(DOWN, buff=0.34)

        # ── Animation ─────────────────────────────────────────────────────────
        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(brain_group, scale=0.97), run_time=0.60)
        self.play(
            FadeIn(wm_trace, scale=0.97),
            FadeIn(wm_label, shift=UP * 0.04),
            run_time=0.60,
        )
        self.wait(0.60)
        self.play(FadeIn(prior_header, shift=DOWN * 0.04), run_time=0.40)
        self.play(
            LaggedStart(
                *[FadeIn(c, scale=0.96) for c in prior_cards],
                lag_ratio=0.24,
            ),
            FadeIn(prior_sub),
            run_time=0.85,
        )
        self.wait(0.50)
        self.play(Create(mod_arrow), FadeIn(mod_label, shift=DOWN * 0.04), run_time=0.80)
        self.wait(0.60)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.60)
        self.wait(3.50)


class IntroClassicalView(Scene):
    """Classical view of working memory --- PFC, parietal, and temporal regions."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Classical view of working memory}",
            "Lesions, persistent firing, and early human imaging converged on association cortex",
        )

        paper_column = Group(
            make_paper_snapshot(
                _FUNAHASHI_1989_FIG, "delay-period firing", "Funahashi et al. (1989)",
                accent=AMBER, height=1.74,
            ),
            make_paper_snapshot(
                _JONIDES_1993_FIG, "PET evidence", "Jonides et al. (1993)",
                accent=AMBER, height=1.55,
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
                (r"Fuster \& Alexander (1971); Kubota \& Niki (1971)",
                 "Funahashi et al. (1989, 1993)"),
                accent=AMBER,
            ),
            make_literature_entry(
                "Human imaging",
                ("PET and fMRI reinforced a frontal-parietal", "maintenance network"),
                (r"Jonides et al. (1993); D'Esposito et al. (1995)",
                 "Courtney et al. (1997, 1998)"),
                accent=AMBER,
            ),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        content = Group(paper_stack, evidence).arrange(RIGHT, buff=0.86, aligned_edge=UP)
        content.next_to(title, DOWN, buff=0.34)

        takeaway = make_callout(
            "Working memory was mainly localized to prefrontal and association cortex.",
            AMBER, font_size=22,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(content, shift=UP * 0.05), run_time=0.95)
        self.play(FadeIn(takeaway, shift=UP * 0.04), run_time=0.55)
        self.wait(4.00)


class IntroSensoryRecruitment(Scene):
    """Sensory recruitment model --- MVPA evidence and the ongoing debate."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Sensory recruitment model}",
            "Theory papers and MVPA studies suggested that visual cortex also carries maintained content",
        )

        paper_column = Group(
            make_paper_snapshot(
                _AWH_JONIDES_2001_FIG, "theory shift", r"Awh \& Jonides (2001)",
                accent=BLUE, height=1.62,
            ),
            make_paper_snapshot(
                _HARRISON_TONG_2009_FIG, "orientation decoding", r"Harrison \& Tong (2009)",
                accent=BLUE, height=1.62,
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
            BLUE, font_size=21,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(content, shift=UP * 0.05), run_time=0.95)
        self.play(FadeIn(takeaway, shift=UP * 0.04), run_time=0.55)
        self.wait(4.50)


class IntroResearchQuestions(Scene):
    """Introduce the three research questions motivating the thesis."""

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

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
        question_stack = question_cards

        content = Group(focus_panel, question_stack).arrange(RIGHT, buff=0.78, aligned_edge=UP)
        content.next_to(title, DOWN, buff=0.36)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(focus_panel, shift=UP * 0.05), run_time=0.85)
        self.play(
            LaggedStart(
                *[FadeIn(card, shift=RIGHT * 0.08) for card in question_cards],
                lag_ratio=0.18,
            ),
            run_time=1.20,
        )
        self.wait(4.00)


_PUBLIC_SCENES: tuple[type[Scene], ...] = (
    IntroCognitiveProblemA,
    IntroCognitiveProblemB,
    IntroCognitiveProblemC,
    IntroClassicalView,
    IntroSensoryRecruitment,
    IntroResearchQuestions,
)

for _scene_cls in _PUBLIC_SCENES:
    globals()[_scene_cls.__name__] = _wrap_scene(_scene_cls)

__all__ = [scene_cls.__name__ for scene_cls in _PUBLIC_SCENES]
