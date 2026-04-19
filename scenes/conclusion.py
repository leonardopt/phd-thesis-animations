"""
Conclusion.

Closing scenes for the thesis-defence summary.

Public scenes:
    ConclusionQuestions
    ConclusionApproach
    ConclusionResults
    ConclusionLimitations

Render:
    uv run manim scenes/conclusion.py ConclusionQuestions -ql
    uv run manim scenes/conclusion.py ConclusionApproach -ql
    uv run manim scenes/conclusion.py ConclusionResults -ql
    uv run manim scenes/conclusion.py ConclusionLimitations -ql
"""
from __future__ import annotations

from pathlib import Path
import sys

from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import section_output_dir

_SECTION_OUTPUT_DIR = section_output_dir("conclusion")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"

_CONCLUSION_SCENE_ORDER: dict[str, str] = {
    "ConclusionQuestions": "01",
    "ConclusionApproach": "02",
    "ConclusionResults": "03",
    "ConclusionLimitations": "04",
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


def _centered_bullets(
    items: list[str],
    *,
    font_size: float = 23,
    line_width: float | None = None,
    dot_radius: float = 0.05,
    row_buff: float = 0.28,
) -> VGroup:
    """Build a centered bullet list."""
    rows = VGroup()
    for item in items:
        dot = Dot(radius=dot_radius, color=INK)
        line = Tex(item, color=INK, font_size=font_size)
        if line_width is not None and line.width > line_width:
            line.scale_to_fit_width(line_width)
        row = VGroup(dot, line).arrange(RIGHT, buff=0.18, aligned_edge=UP)
        rows.add(row)
    return rows.arrange(DOWN, buff=row_buff, aligned_edge=LEFT)


def _rq_column(
    heading: str,
    question_rows: list[str],
    *,
    answer_rows: list[str] | None = None,
) -> VGroup:
    """Build one RQ column, optionally with a short answer block."""
    question = _section(
        heading,
        question_rows,
        heading_size=26,
        line_size=20,
        buff=0.14,
    )

    if not answer_rows:
        return question

    divider = Line(LEFT * 0.95, RIGHT * 0.95, color="#B8B8B8", stroke_width=1.0)
    answer = _lines(answer_rows, font_size=18, buff=0.07)
    column = VGroup(question, divider, answer).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    divider.align_to(answer, LEFT)
    return column


def _rq_layout(*, with_answers: bool = False) -> VGroup:
    """Build the shared RQ1 | RQ2 | RQ3 layout."""
    rq1_answer = [
        r"\textbf{Result:} no stable sensory copy.",
        r"EVC retained information,",
        r"but in a transformed mnemonic format.",
    ]
    rq2_answer = [
        r"\textbf{Result:} yes.",
        r"Naturalistic scenes were decodable",
        r"in EVC during perception and delay.",
    ]
    rq3_answer = [
        r"\textbf{Result:} behavioural yes,",
        r"neural no in EVC.",
        r"Repetition improved performance,",
        r"not sensory--memory similarity.",
    ]

    rq1 = _rq_column(
        "RQ1",
        [
            r"\textbf{Representational format}",
            r"sensory-like or memory-specific?",
        ],
        answer_rows=rq1_answer if with_answers else None,
    )
    rq2 = _rq_column(
        "RQ2",
        [
            r"\textbf{Naturalistic stimuli}",
            r"does sensory recruitment extend",
            r"beyond simple laboratory stimuli?",
        ],
        answer_rows=rq2_answer if with_answers else None,
    )
    rq3 = _rq_column(
        "RQ3",
        [
            r"\textbf{Long-term memory}",
            r"does long-term memory reshape",
            r"working-memory representations?",
        ],
        answer_rows=rq3_answer if with_answers else None,
    )

    separators = VGroup(
        Line(UP * (2.35 if with_answers else 1.35), DOWN * (2.35 if with_answers else 1.35), color="#B8B8B8", stroke_width=1.2),
        Line(UP * (2.35 if with_answers else 1.35), DOWN * (2.35 if with_answers else 1.35), color="#B8B8B8", stroke_width=1.2),
    )

    layout = VGroup(
        rq1,
        separators[0],
        rq2,
        separators[1],
        rq3,
    ).arrange(RIGHT, buff=0.48, aligned_edge=UP)

    max_width = config.frame_width - 1.1
    if layout.width > max_width:
        layout.scale_to_fit_width(max_width)
    return layout


class ConclusionQuestions(_ConclusionNumberedScene, Scene):
    """Restate the three main questions from the introduction."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = _title("Main questions")

        questions = _rq_layout(with_answers=False)
        questions.next_to(title, DOWN, buff=1.0)
        questions.set_x(0)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(questions, shift=UP * 0.06), run_time=0.8)
        self.wait(1.2)


class ConclusionApproach(_ConclusionNumberedScene, Scene):
    """Show how the thesis design answered the three questions."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = _title("How we approached them")

        approach = _lines(
            [
                r"\textbf{Study 1:} build a controlled naturalistic stimulus set",
                r"with deep generative modelling.",
                r"Validate perceptual scaling with similarity judgements",
                r"and memory-task sensitivity with delayed match-to-sample.",
                r"\textbf{Study 2:} use the validated set in a two-session fMRI design.",
                r"Cross-session decoding tests sensory-like generalisation;",
                r"repetition tests long-term memory modulation.",
            ],
            font_size=24,
        )
        approach.next_to(title, DOWN, buff=0.9)
        approach.set_x(0)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(approach, shift=UP * 0.06), run_time=0.8)
        self.wait(1.2)


class ConclusionResults(_ConclusionNumberedScene, Scene):
    """Answer the three main questions with the key results."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = _title("Main questions")

        results = _rq_layout(with_answers=True)
        results.next_to(title, DOWN, buff=0.82)
        results.set_x(0)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(results, shift=UP * 0.06), run_time=0.8)
        self.wait(1.2)


class ConclusionLimitations(_ConclusionNumberedScene, Scene):
    """State the main limitations as a centered bullet list."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = _title("Limitations")

        bullets = _centered_bullets(
            [
                r"Stimuli were synthetic, object-centred, and partly selected by researcher judgement;\\"
                r"semantic coverage is broad, but not exhaustive.",
                r"The perceptual continua varied along multiple features rather than isolated dimensions,\\"
                r"which limits feature-specific interpretation.",
                r"The long-term memory manipulation was brief and tested sensory--memory similarity in EVC,\\"
                r"not changes in memory-specific representational formats.",
            ],
            font_size=22,
            line_width=7.8,
            row_buff=0.22,
        )
        bullets.next_to(title, DOWN, buff=1.0)
        bullets.set_x(0)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.5)
        self.play(FadeIn(bullets, shift=UP * 0.06), run_time=0.8)
        self.wait(1.2)


_CONCLUSION_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    ConclusionQuestions,
    ConclusionApproach,
    ConclusionResults,
    ConclusionLimitations,
)


class Conclusion(Scene):
    """Unified production render for the conclusion."""

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        (
            f"{_CONCLUSION_SCENE_ORDER[scene_cls.__name__]}_{scene_cls.__name__}",
            scene_cls,
        )
        for scene_cls in _CONCLUSION_MASTER_SECTION_ORDER
    )

    def _reset_master_scene_state(self) -> None:
        """Reset mobjects and camera placement before replaying one legacy scene."""
        self.clear()
        self.camera.background_color = BG
        if hasattr(self.camera, "frame_center"):
            self.camera.frame_center = ORIGIN.copy()

    def _hold_previous_section_frame(self) -> None:
        """Pin the previous section's last frame into the next section."""
        self.wait(1 / config.frame_rate)

    def _run_legacy_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        """Replay one conclusion scene inside the master section render."""
        self.next_section(section_name)
        if carry_previous_frame:
            self._hold_previous_section_frame()
        self._reset_master_scene_state()
        scene_cls.construct(self)

    def construct(self) -> None:
        """Render the full conclusion as one sectioned scene."""
        self._reset_master_scene_state()
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._run_legacy_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )


__all__ = ["Conclusion", *list(_CONCLUSION_SCENE_ORDER)]
