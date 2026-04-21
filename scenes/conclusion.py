"""
Conclusion - sectioned production render.

Render from this file to keep all conclusion outputs in the same
`media/videos/05_conclusion/...` folder.

Production render:
    uv run manim scenes/conclusion.py Conclusion -ql --save_sections

Legacy standalone renders:
    uv run manim scenes/conclusion.py ConclusionQuestions -ql
    uv run manim scenes/conclusion.py ConclusionApproach -ql
    uv run manim scenes/conclusion.py ConclusionResults -ql
    uv run manim scenes/conclusion.py ConclusionLimitations -ql
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from PIL import Image as PILImage
import subprocess
import sys
import tempfile

from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import section_output_dir, simplify_manim_section_video_names


_SECTION_OUTPUT_DIR = section_output_dir("conclusion")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "conclusion"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)

_CONCLUSION_SCENE_ORDER: dict[str, str] = {
    "ConclusionQuestions": "01",
    "ConclusionApproach": "02",
    "ConclusionResults": "03",
    "ConclusionLimitations": "04",
    "ConclusionFutureDirections": "05",
}


class _ConclusionNumberedScene:
    """Mixin that prefixes standalone renders with their chapter order."""

    def __init__(self, *args, **kwargs):
        scene_name = self.__class__.__name__
        number = _CONCLUSION_SCENE_ORDER.get(scene_name, "")
        if number and config.output_file == "conclusion":
            config.output_file = f"{number}_{scene_name}"
        super().__init__(*args, **kwargs)


BG = WHITE
INK = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#374151"
BLUE = "#3E5C76"
AMBER = "#8A6642"
GREEN = "#4F6D5E"
RED = "#8B5A52"
_FISH_VIDEO_PATH = _SCENES_DIR.parent / "assets" / "images" / "fish_video.mp4"
_VIDEO_FRAME_CACHE: dict[tuple[str, int, int, int, int], list[np.ndarray]] = {}


def title_block(title_text: str, subtitle_text: str | None = None) -> VGroup:
    """Build a chapter-style title and subtitle block."""
    title = Tex(title_text, color=INK, font_size=34).to_edge(UP, buff=0.34)
    parts = [title]
    if subtitle_text is not None:
        subtitle = Tex(subtitle_text, color=MGREY, font_size=21)
        subtitle.next_to(title, DOWN, buff=0.14)
        parts.append(subtitle)
    return VGroup(*parts)


def make_callout(text: str, color: str, *, font_size: float = 22) -> VGroup:
    """Build a short concluding takeaway with an underline."""
    line = Tex(text, color=INK, font_size=font_size)
    if line.width > 9.1:
        line.scale_to_fit_width(9.1)
    underline = Line(
        line.get_corner(DL) + DOWN * 0.10,
        line.get_corner(DR) + DOWN * 0.10,
        color=color,
        stroke_width=1.8,
    )
    return VGroup(line, underline)


def caption_line(
    text: str,
    *,
    color: str = MGREY,
    font_size: float = 18,
    max_width: float | None = None,
) -> Tex:
    """Build one caption line with optional width capping."""
    line = Tex(text, color=color, font_size=font_size)
    if max_width is not None and line.width > max_width:
        line.scale_to_fit_width(max_width)
    return line


def text_lines(
    rows: tuple[str, ...] | list[str],
    *,
    font_size: float = 18,
    color: str = INK,
    buff: float = 0.06,
    max_width: float | None = None,
) -> VGroup:
    """Build a left-aligned text stack."""
    block = VGroup(
        *[Tex(row, color=color, font_size=font_size) for row in rows]
    ).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if max_width is not None and block.width > max_width:
        block.scale_to_fit_width(max_width)
    return block


def simple_divider(width: float, *, color: str = LGREY, stroke_width: float = 1.2) -> Line:
    """Build a centered divider."""
    return Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=stroke_width)


def load_video_frames(
    video_path: Path,
    *,
    fps: int = 12,
    frame_width_px: int = 420,
) -> list[np.ndarray]:
    """Decode a short mp4 into cached RGBA frames for lightweight playback."""
    stat = video_path.stat()
    cache_key = (
        str(video_path.resolve()),
        int(stat.st_mtime_ns),
        int(stat.st_size),
        fps,
        frame_width_px,
    )
    cached = _VIDEO_FRAME_CACHE.get(cache_key)
    if cached is not None:
        return cached

    digest = hashlib.sha1(
        f"{video_path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}:{fps}:{frame_width_px}".encode()
    ).hexdigest()[:12]
    frame_dir = Path(tempfile.gettempdir()) / "phd_thesis_conclusion_video_frames" / digest
    frame_pattern = frame_dir / "frame_%04d.png"

    if not any(frame_dir.glob("frame_*.png")):
        frame_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vf",
                f"fps={fps},scale={frame_width_px}:{frame_width_px}:force_original_aspect_ratio=decrease",
                str(frame_pattern),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    frame_paths = sorted(frame_dir.glob("frame_*.png"))
    if not frame_paths:
        raise RuntimeError(f"No frames extracted from {video_path}")

    frames = [np.asarray(PILImage.open(fp).convert("RGBA")) for fp in frame_paths]
    _VIDEO_FRAME_CACHE[cache_key] = frames
    return frames


def video_mobject(
    video_path: Path,
    *,
    width: float,
    fps: int = 12,
) -> ImageMobject:
    """Create a looping video mobject from cached frame arrays."""
    frames = load_video_frames(video_path, fps=fps)
    mob = ImageMobject(frames[0]).scale_to_fit_width(width)
    elapsed = {"t": 0.0}

    def _update_frame(m: ImageMobject, dt: float) -> None:
        elapsed["t"] += dt
        idx = int(elapsed["t"] * fps) % len(frames)
        center = m.get_center()
        next_frame = ImageMobject(frames[idx]).scale_to_fit_width(width).move_to(center)
        m.become(next_frame)

    mob.add_updater(_update_frame)
    return mob


def split_columns(
    left: Mobject,
    right: Mobject,
    *,
    buff: float = 0.48,
    divider_color: str = LGREY,
) -> Group:
    """Arrange two columns with a central divider."""
    divider = Line(UP * 0.5, DOWN * 0.5, color=divider_color, stroke_width=1.2)
    divider.set(height=max(left.height, right.height) - 0.06)
    return Group(left, divider, right).arrange(RIGHT, buff=buff, aligned_edge=UP)


def make_section_block(
    heading: str,
    rows: tuple[str, ...] | list[str],
    *,
    accent: str,
    width: float = 4.4,
    heading_size: float = 22,
    line_size: float = 18,
) -> VGroup:
    """Build one unframed section block with a small accent marker."""
    heading_row = VGroup(
        Dot(radius=0.045, color=accent),
        Tex(rf"\textbf{{{heading}}}", color=INK, font_size=heading_size),
    ).arrange(RIGHT, buff=0.12)
    body = text_lines(rows, font_size=line_size, color=INK, max_width=width)
    divider = simple_divider(max(heading_row.width, body.width, width * 0.62), stroke_width=1.0)
    divider.align_to(body, LEFT)
    return VGroup(heading_row, body, divider).arrange(DOWN, buff=0.10, aligned_edge=LEFT)


def make_question_panel(
    label: str,
    heading: str,
    rows: tuple[str, ...] | list[str],
    *,
    accent: str,
    width: float = 3.10,
) -> VGroup:
    """Build one research-question panel."""
    header = VGroup(
        Tex(label, color=accent, font_size=16),
        Tex(rf"\textbf{{{heading}}}", color=INK, font_size=22),
    ).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)
    body = text_lines(rows, font_size=17, color=INK, max_width=width)
    divider = simple_divider(max(header.width, body.width, width * 0.84), stroke_width=1.0)
    divider.align_to(header, LEFT)
    return VGroup(header, divider, body).arrange(DOWN, buff=0.12, aligned_edge=LEFT)


def make_result_panel(
    label: str,
    heading: str,
    rows: tuple[str, ...] | list[str],
    *,
    accent: str,
    width: float = 3.10,
) -> VGroup:
    """Build one concise answer block for a research question."""
    header = VGroup(
        Tex(label, color=accent, font_size=16),
        Tex(rf"\textbf{{{heading}}}", color=INK, font_size=22),
    ).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)
    body = text_lines(rows, font_size=17, color=INK, max_width=width)
    divider = simple_divider(max(header.width, body.width, width * 0.84), stroke_width=1.0)
    divider.align_to(header, LEFT)
    answer = caption_line(r"\textbf{Answer}", color=accent, font_size=16)
    block = VGroup(header, divider, answer, body).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    return block


def three_panel_row(left: Mobject, middle: Mobject, right: Mobject, *, buff: float = 0.34) -> Group:
    """Arrange three panels with vertical dividers."""
    divider_height = max(left.height, middle.height, right.height) - 0.06
    dividers = VGroup(
        Line(UP * divider_height / 2, DOWN * divider_height / 2, color=LGREY, stroke_width=1.2),
        Line(UP * divider_height / 2, DOWN * divider_height / 2, color=LGREY, stroke_width=1.2),
    )
    row = Group(left, dividers[0], middle, dividers[1], right).arrange(
        RIGHT,
        buff=buff,
        aligned_edge=UP,
    )
    max_width = config.frame_width - 1.0
    if row.width > max_width:
        row.scale_to_fit_width(max_width)
    return row


class ConclusionQuestions(_ConclusionNumberedScene, Scene):
    """Chapter 5.1 - restate the thesis questions."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Research questions}",
            "Three open questions about sensory recruitment under naturalistic conditions",
        )

        questions = three_panel_row(
            make_question_panel(
                "RQ1",
                "Representational format",
                (
                    "are working-memory codes",
                    "in early visual cortex",
                    "sensory-like or",
                    "memory-specific?",
                ),
                accent=BLUE,
                width=3.00,
            ),
            make_question_panel(
                "RQ2",
                "Naturalistic stimuli",
                (
                    "does sensory recruitment",
                    "extend to controlled",
                    "high-resolution",
                    "naturalistic images?",
                ),
                accent=AMBER,
                width=3.00,
            ),
            make_question_panel(
                "RQ3",
                "Long-term memory",
                (
                    "does long-term memory",
                    "reshape working-memory",
                    "representations in",
                    "early visual cortex?",
                ),
                accent=GREEN,
                width=3.00,
            ),
            buff=0.30,
        )
        questions.next_to(title, DOWN, buff=0.72)

        callout = make_callout(
            "The thesis asked about format, generalisability, and long-term memory interactions.",
            BLUE,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(questions, shift=UP * 0.05), run_time=0.95)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.00)


class ConclusionApproach(_ConclusionNumberedScene, Scene):
    """Chapter 5.2 - summarise what the dissertation did."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{What the dissertation did}",
            "Study 1 solved the stimulus problem; Study 2 used the set to test sensory recruitment",
        )

        left_column = VGroup(
            make_section_block(
                "Study 1: stimulus synthesis",
                (
                    "built a diffusion-based pipeline for naturalistic object-scene images",
                    "108 high-resolution images with 10 graded variations per object-scene",
                    "behavioural validation showed a perceptual continuum",
                ),
                accent=BLUE,
                width=4.80,
            ),
            make_section_block(
                "Methodological contribution",
                (
                    "naturalistic stimuli with fine control over similarity",
                    "usable in behavioural tasks and neuroimaging",
                ),
                accent=GREEN,
                width=4.80,
            ),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)

        right_column = VGroup(
            make_section_block(
                "Study 2: fMRI test",
                (
                    "used the validated set in a two-session fMRI design",
                    "decoded stimulus-specific information in early visual cortex",
                    "tested sensory-like generalisation and repetition effects",
                ),
                accent=AMBER,
                width=4.80,
            ),
            make_section_block(
                "Theoretical contribution",
                (
                    "tested the sensory recruitment model with naturalistic stimuli",
                    "and refined it by separating information from format",
                ),
                accent=RED,
                width=4.80,
            ),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)

        content = split_columns(left_column, right_column, buff=0.48)
        content.next_to(title, DOWN, buff=0.34)

        callout = make_callout(
            "The thesis combined controlled stimulus synthesis with neuroimaging to test naturalistic working memory.",
            GREEN,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(left_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(content[1]), FadeIn(right_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.00)


class ConclusionResults(_ConclusionNumberedScene, Scene):
    """Chapter 5.3 - answer the research questions."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Main results}",
            "Summary of the answers to the three research questions",
        )

        results = three_panel_row(
            make_result_panel(
                "RQ1",
                "Representational format",
                (
                    "stimulus-specific information",
                    "was retained in early visual",
                    "cortex, but not in a stable",
                    "sensory-like format",
                ),
                accent=BLUE,
                width=3.00,
            ),
            make_result_panel(
                "RQ2",
                "Naturalistic stimuli",
                (
                    "sensory recruitment extended",
                    "to high-resolution",
                    "naturalistic images during",
                    "perception and delay",
                ),
                accent=AMBER,
                width=3.00,
            ),
            make_result_panel(
                "RQ3",
                "Long-term memory",
                (
                    "repetition improved",
                    "behavioural performance,",
                    "but did not increase",
                    "sensory-memory similarity",
                ),
                accent=GREEN,
                width=3.00,
            ),
            buff=0.30,
        )
        results.next_to(title, DOWN, buff=0.66)

        callout = make_callout(
            "Naturalistic sensory recruitment was robust, but its mnemonic code was transformed rather than a stable sensory copy.",
            RED,
            font_size=19,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(results, shift=UP * 0.05), run_time=1.00)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.10)


class ConclusionLimitations(_ConclusionNumberedScene, Scene):
    """Chapter 5.4 - state the main limitations."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Main limitations}",
            "The scope of the method and the theory is clearer than before, but not yet exhaustive",
        )

        left_column = VGroup(
            make_section_block(
                "Selection and coverage",
                (
                    "category and object-scene selection was partly subjective",
                    "the stimulus space was broad, but not an exhaustive semantic sample",
                ),
                accent=RED,
                width=4.80,
            ),
            make_section_block(
                "Controlled dimensions",
                (
                    "the continua varied along multiple features at once",
                    "this limits feature-specific interpretation",
                ),
                accent=AMBER,
                width=4.80,
            ),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)

        right_column = VGroup(
            make_section_block(
                "Stimulus realism",
                (
                    "the images were synthetic and object-centred",
                    "they were less suited for cluttered scenes, natural gaze, and artefact-focused questions",
                ),
                accent=BLUE,
                width=4.80,
            ),
            make_section_block(
                "Memory manipulation",
                (
                    "the long-term memory test was a brief repetition manipulation",
                    "it targeted sensory-memory similarity in early visual cortex rather than broader format changes",
                ),
                accent=GREEN,
                width=4.80,
            ),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)

        content = split_columns(left_column, right_column, buff=0.48)
        content.next_to(title, DOWN, buff=0.34)

        callout = make_callout(
            "These limitations set the scope of the claims without overturning the main methodological and neural findings.",
            AMBER,
            font_size=19,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(left_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(content[1]), FadeIn(right_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.00)


class ConclusionFutureDirections(_ConclusionNumberedScene, Scene):
    """Chapter 5.5 - argue for generative stimulus synthesis as a general platform."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Future directions}",
            "From a single pipeline to a broader standard for controlled naturalistic experiments",
        )

        left_column = VGroup(
            make_section_block(
                "Next methodological steps",
                (
                    "extend synthesis beyond static exemplars to dynamic and interactive stimuli",
                    "increase control over scene clutter, viewpoint, motion, and task relevance",
                    "pair generation with stronger validation loops across behaviour and neuroimaging",
                ),
                accent=BLUE,
                width=4.55,
            ),
            make_section_block(
                "Wider opportunity",
                (
                    "shared generative pipelines could make naturalistic stimulus control reproducible across labs",
                    "this would reduce the trade-off between ecological realism and experimental precision",
                ),
                accent=GREEN,
                width=4.55,
            ),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)

        video_title = Tex(r"\textbf{Dynamic synthetic stimuli}", color=INK, font_size=22)
        video_clip = video_mobject(_FISH_VIDEO_PATH, width=4.1, fps=12)
        video_frame = RoundedRectangle(
            corner_radius=0.14,
            width=4.42,
            height=4.42,
            stroke_color=BLUE,
            stroke_width=1.6,
        )
        video_frame.set_fill(WHITE, opacity=0.0)
        video_stack = Group(video_frame, video_clip)
        video_clip.move_to(video_frame.get_center())
        video_caption = text_lines(
            (
                "Dynamic fish render from the same synthesis line of work.",
                "The same logic can scale from stills to richer, time-varying stimulus sets.",
            ),
            font_size=17,
            color=INK,
            max_width=4.35,
        )
        right_column = Group(video_title, video_stack, video_caption).arrange(
            DOWN,
            buff=0.18,
            aligned_edge=LEFT,
        )

        content = split_columns(left_column, right_column, buff=0.52)
        content.next_to(title, DOWN, buff=0.34)

        callout = make_callout(
            "Generative stimulus synthesis has the potential to become a new standard.",
            BLUE,
            font_size=21,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(left_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(content[1]), FadeIn(right_column, shift=UP * 0.05), run_time=0.95)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(5.00)


_CONCLUSION_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    ConclusionQuestions,
    ConclusionApproach,
    ConclusionResults,
    ConclusionLimitations,
    ConclusionFutureDirections,
)
_CONCLUSION_SECTION_NAMES: tuple[str, ...] = (
    "conclusion_questions",
    "conclusion_summary",
    "conclusion_results",
    "conclusion_limitations",
    "conclusion_future_directions",
)


class Conclusion(Scene):
    """Unified production render for the conclusion chapter."""

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        zip(_CONCLUSION_SECTION_NAMES, _CONCLUSION_MASTER_SECTION_ORDER)
    )

    def __init__(self, *args, **kwargs):
        config.output_file = "conclusion"
        super().__init__(*args, **kwargs)

    def _reset_master_scene_state(self) -> None:
        """Reset mobjects and camera placement before replaying one section."""
        self.clear()
        self.camera.background_color = BG
        if hasattr(self.camera, "frame_center"):
            self.camera.frame_center = ORIGIN.copy()

    def _hold_previous_section_frame(self) -> None:
        """Pin the previous section's last frame into the next section."""
        self.wait(1 / config.frame_rate)

    def _render_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        """Replay one existing conclusion scene inside the master render."""
        self.next_section(section_name)
        if carry_previous_frame:
            self._hold_previous_section_frame()
        self._reset_master_scene_state()
        scene_cls.construct(self)

    def construct(self) -> None:
        """Render the full conclusion as one sectioned scene."""
        self._reset_master_scene_state()
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._render_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )


__all__ = ["Conclusion", *list(_CONCLUSION_SCENE_ORDER)]


for _scene_cls in _CONCLUSION_MASTER_SECTION_ORDER:
    _scene_cls.__module__ = "_conclusion_internal"
del _scene_cls
Conclusion.__module__ = __name__
__all__ = ["Conclusion"]
