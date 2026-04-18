"""
Conclusion.

Closing scenes for the thesis-defence summary.

Public scenes:
    ConclusionResults
    ConclusionDiscussion
    ConclusionLimitations

Render:
    uv run manim scenes/conclusion.py ConclusionResults -ql
    uv run manim scenes/conclusion.py ConclusionDiscussion -ql
    uv run manim scenes/conclusion.py ConclusionLimitations -ql
"""
from __future__ import annotations

from manim import *


_CONCLUSION_SCENE_ORDER: dict[str, str] = {
    "ConclusionResults": "01",
    "ConclusionDiscussion": "02",
    "ConclusionLimitations": "03",
}


class _ConclusionNumberedScene:
    """Mixin that prefixes rendered files with the closing-scene number."""

    def __init__(self, *args, **kwargs):
        scene_name = self.__class__.__name__
        number = _CONCLUSION_SCENE_ORDER.get(scene_name, "")
        if number:
            config.output_file = f"{number}_{scene_name}"
        super().__init__(*args, **kwargs)


BG = WHITE
INK = "#1C1C1E"


def _title(text: str) -> Tex:
    """Build a clean scene title."""
    return Tex(text, color=INK, font_size=36).to_edge(UP, buff=0.32)


def _lines(rows: list[str], *, font_size: float = 23, buff: float = 0.08) -> VGroup:
    """Build a left-aligned stack of LaTeX text lines."""
    return VGroup(
        *[Tex(row, color=INK, font_size=font_size) for row in rows]
    ).arrange(DOWN, aligned_edge=LEFT, buff=buff)


def _section(
    heading: str,
    rows: list[str],
    *,
    heading_size: float = 28,
    line_size: float = 22,
    buff: float = 0.18,
) -> VGroup:
    """Build a heading plus left-aligned text block."""
    header = Tex(rf"\textbf{{{heading}}}", color=INK, font_size=heading_size)
    body = _lines(rows, font_size=line_size)
    return VGroup(header, body).arrange(DOWN, aligned_edge=LEFT, buff=buff)


class ConclusionResults(_ConclusionNumberedScene, Scene):
    """Summarise the main results using the same clean text style as the study scenes."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = _title("Results")

        study1 = _section(
            "Study 1",
            [
                r"Controlled synthesis produced naturalistic object-scenes",
                r"with graded perceptual variants.",
                r"Similarity judgements ($N = 1{,}113$) confirmed",
                r"a perceptual continuum and broadly matched LPIPS ordering",
                r"($\rho = 0.73$).",
                r"In delayed match-to-sample ($N = 260$), accuracy tracked",
                r"target--foil distance, and repetition improved performance.",
            ],
            line_size=21,
        )

        study2 = _section(
            "Study 2",
            [
                r"In fMRI ($N = 42$), early visual cortex carried robust",
                r"stimulus-specific information for naturalistic scenes.",
                r"Sensory-trained classifiers generalised to encoding,",
                r"but not across the full delay period.",
                r"Within-session decoding still recovered delay-period content,",
                r"implying an informative but non-sensory-like mnemonic code.",
                r"Repetition did not change sensory-memory similarity in EVC.",
            ],
            line_size=21,
        )

        blocks = VGroup(study1, study2).arrange(RIGHT, buff=0.92, aligned_edge=UP)
        max_width = config.frame_width - 1.0
        if blocks.width > max_width:
            blocks.scale_to_fit_width(max_width)
        blocks.next_to(title, DOWN, buff=0.65)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(study1, shift=UP * 0.06), run_time=0.65)
        self.play(FadeIn(study2, shift=UP * 0.06), run_time=0.65)
        self.wait(1.2)


class ConclusionDiscussion(_ConclusionNumberedScene, Scene):
    """Interpret the main findings without extra visual scaffolding."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = _title("Discussion")

        discussion = _lines(
            [
                r"Early visual cortex contributes to working memory maintenance,",
                r"but delay representations are transformed rather than copied",
                r"from perception.",
                r"Naturalistic stimuli therefore support sensory recruitment",
                r"without implying identical sensory and mnemonic formats.",
                r"Repeated exposure improved behaviour, but did not produce",
                r"a more sensory-like code in early visual cortex.",
                r"Methodologically, generative synthesis makes it possible",
                r"to combine ecological relevance with experimental control",
                r"in one unified paradigm.",
            ],
            font_size=24,
        )
        discussion.next_to(title, DOWN, buff=0.9)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(discussion, shift=UP * 0.06), run_time=0.8)
        self.wait(1.2)


class ConclusionLimitations(_ConclusionNumberedScene, Scene):
    """State the main limitations in the same minimal study-slide style."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = _title("Limitations")

        limitations = _lines(
            [
                r"Stimulus selection and quality control still involved",
                r"researcher judgement; the semantic space was broad, not exhaustive.",
                r"The continua varied along multiple features rather than single",
                r"controlled dimensions, so feature-specific mechanisms remain unclear.",
                r"The images were synthetic, object-centred scenes and still contained",
                r"some artefacts, limiting generalisation to full real-world vision.",
                r"The long-term memory manipulation was brief, and the design tested",
                r"similarity to sensory codes rather than changes in memory-specific formats.",
            ],
            font_size=24,
        )
        limitations.next_to(title, DOWN, buff=0.9)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(limitations, shift=UP * 0.06), run_time=0.8)
        self.wait(1.2)
