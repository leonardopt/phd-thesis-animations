"""
Methods — sectioned production render.

Render from this file to keep all methods outputs in the same
`media/videos/02_methods/...` folder.

Production render:
    uv run manim scenes/methods.py Methods -ql --save_sections

Legacy standalone renders:
    uv run manim scenes/methods.py MethodsStimulusRequirements -ql
    uv run manim scenes/methods.py MethodsTraditionalLimits -ql
    uv run manim scenes/methods.py MethodsGANsProofOfConcept -ql
    uv run manim scenes/methods.py MethodsDiffusionOpportunity -ql
    uv run manim scenes/methods.py MethodsDiffusionExplainer -ql
    uv run manim scenes/methods.py MethodsProjectPlan -ql
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
from PIL import Image as PILImage
from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import REPO_ROOT, env_path, section_output_dir, simplify_manim_section_video_names


_SECTION_OUTPUT_DIR = section_output_dir("methods")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "methods"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)

_METHODS_SCENE_ORDER: dict[str, str] = {
    "MethodsStimulusRequirements": "01",
    "MethodsTraditionalLimits": "02",
    "MethodsGANsProofOfConcept": "03",
    "MethodsDiffusionOpportunity": "04",
    "MethodsDiffusionExplainer": "05",
    "MethodsProjectPlan": "06",
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
MGREY = "#374151"
BLUE = "#3E5C76"
AMBER = "#8A6642"
GREEN = "#4F6D5E"
RED = "#8B5A52"


# ── Assets ────────────────────────────────────────────────────────────────────
_INTRO_STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
_BRAIN_ICON_PATH = REPO_ROOT / "assets" / "images" / "study2" / "brain_icon_sagittal.png"

_EXEMPLAR_CODE = "building_observatory"
_DIFFUSION_CODE = "animal_fish"
_DIFFUSION_PROMPT = r"\textit{prompt: observatory at dusk}"
_CATEGORY_EXAMPLES: tuple[tuple[str, int, str, str], ...] = (
    ("animal_fish", 5, r"\textit{fish in water}", BLUE),
    ("building_observatory", 5, r"\textit{observatory at dusk}", AMBER),
    ("plant_pine", 5, r"\textit{pine tree in a landscape}", GREEN),
)
_SCENE_WHEELS_CITATION = "Scene Wheels (Son et al., 2022)"


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
    image_source: str | Path | np.ndarray,
    *,
    height: float = 1.6,
    border_color: str = LGREY,
    fill_color: str = WHITE,
    fill_opacity: float = 1.0,
    buff: float = 0.06,
    corner_radius: float = 0.14,
) -> Group:
    """Create a framed image card."""
    if isinstance(image_source, np.ndarray):
        array = image_source
        if array.dtype != np.uint8:
            array = (255 * np.clip(array, 0, 1)).astype(np.uint8)
        image = ImageMobject(array)
    else:
        image = ImageMobject(str(image_source))
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
    if line.width > 8.9:
        line.scale_to_fit_width(8.9)
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
    """Build one single-line caption with optional width cap."""
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
    """Build a left-aligned text stack with optional width capping."""
    block = VGroup(
        *[Tex(row, color=color, font_size=font_size) for row in rows]
    ).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if max_width is not None and block.width > max_width:
        block.scale_to_fit_width(max_width)
    return block


def simple_divider(width: float, *, color: str = LGREY, stroke_width: float = 1.2) -> Line:
    """Build a centered horizontal divider."""
    return Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=stroke_width)


def split_columns(
    left: Mobject,
    right: Mobject,
    *,
    buff: float = 0.48,
    divider_color: str = LGREY,
) -> Group:
    """Arrange two columns with an automatically sized divider."""
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


def make_pipeline_stage(
    step_label: str,
    title_text: str,
    body: Mobject,
    *,
    accent: str,
    width: float = 2.55,
) -> Group:
    """Build a plain pipeline stage with a step label and divider."""
    step = Tex(step_label, color=accent, font_size=16)
    title = Tex(rf"\textbf{{{title_text}}}", color=INK, font_size=20)
    header = VGroup(step, title).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)

    body_group = body.copy()
    if body_group.width > width:
        body_group.scale_to_fit_width(width)

    rule = simple_divider(max(header.width, body_group.width, width * 0.84), stroke_width=1.0)
    rule.align_to(header, LEFT)
    return Group(header, rule, body_group).arrange(DOWN, buff=0.12, aligned_edge=LEFT)


def make_image_strip(
    code: str,
    idxs: tuple[int, ...] | list[int],
    *,
    height: float,
    buff: float = 0.08,
    border_color: str = LGREY,
) -> Group:
    """Build a horizontal strip of framed stimulus images."""
    return Group(
        *[
            make_image_card(stim_path(code, idx), height=height, border_color=border_color, buff=0.03)
            for idx in idxs
        ]
    ).arrange(RIGHT, buff=buff)


_SHARED_NOISE: dict[tuple[int, ...], np.ndarray] = {}


def load_rgb(path: str | Path) -> np.ndarray:
    """Load an image as a float RGB array in [0, 1]."""
    return np.asarray(PILImage.open(path).convert("RGB")).astype(np.float32) / 255.0


def diffusion_noise(shape: tuple[int, ...]) -> np.ndarray:
    """Return one deterministic normalized noise array for a given shape."""
    if shape not in _SHARED_NOISE:
        rng = np.random.default_rng(42)
        noise = rng.normal(0, 1, shape).astype(np.float32)
        _SHARED_NOISE[shape] = (noise - noise.min()) / (noise.max() - noise.min())
    return _SHARED_NOISE[shape]


def blend_with_noise(clean: np.ndarray, alpha: float) -> np.ndarray:
    """Blend one clean image with shared noise."""
    return np.clip((1 - alpha) * clean + alpha * diffusion_noise(clean.shape), 0, 1)


def make_image_progression(
    sources: list[str | Path | np.ndarray],
    *,
    height: float,
    arrow_color: str,
    border_color: str = LGREY,
    card_buff: float = 0.05,
    item_buff: float = 0.18,
) -> tuple[Group, VGroup]:
    """Build a card strip plus arrows between adjacent cards."""
    cards = Group(
        *[
            make_image_card(src, height=height, border_color=border_color, buff=0.03)
            for src in sources
        ]
    ).arrange(RIGHT, buff=item_buff)
    arrows = VGroup(
        *[
            Arrow(
                cards[idx].get_right() + RIGHT * 0.04,
                cards[idx + 1].get_left() + LEFT * 0.04,
                color=arrow_color,
                stroke_width=1.4,
                buff=card_buff,
                tip_shape=StealthTip,
                tip_length=0.12,
            )
            for idx in range(len(cards) - 1)
        ]
    )
    return cards, arrows


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
    """Chapter 2.1 — define the stimulus properties the project required."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Stimulus requirements}",
            "Ecological validity without sacrificing experimental control",
        )

        continuum = make_image_strip(_EXEMPLAR_CODE, (0, 3, 6, 9), height=1.00, buff=0.10)
        continuum_stack = Group(
            Tex(r"\textbf{Target stimulus space}", color=INK, font_size=24),
            continuum,
            text_lines(
                (
                    "same object-scene identity across controlled variants",
                    "fine-grained perceptual change without losing naturalism",
                ),
                font_size=18,
                color=MGREY,
                max_width=8.8,
            ),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        left_column = VGroup(
            make_section_block(
                "Naturalistic",
                (
                    "rich perceptual structure and recognisable semantic content",
                    "rather than abstract laboratory stimuli",
                ),
                accent=BLUE,
                width=4.65,
            ),
            make_section_block(
                "Reusable across studies",
                (
                    "the same stimulus family should support behavioural work",
                    "and later neuroimaging experiments",
                ),
                accent=GREEN,
                width=4.65,
            ),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        right_column = VGroup(
            make_section_block(
                "Perceptually controlled",
                (
                    "graded similarity while semantic identity remains stable",
                    "across the continuum",
                ),
                accent=AMBER,
                width=4.65,
            ),
            make_section_block(
                "fMRI-compatible",
                (
                    "visual detail sufficient for multivariate analyses",
                    r"in [V1, V2, V3]",
                ),
                accent=BLUE,
                width=4.65,
            ),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        requirements = split_columns(left_column, right_column, buff=0.42)

        content = Group(
            continuum_stack,
            simple_divider(10.0),
            requirements,
        ).arrange(DOWN, buff=0.28)
        content.next_to(title, DOWN, buff=0.28)

        callout = make_callout(
            "The target set had to look natural, vary smoothly, and survive both behavioural and fMRI experiments.",
            BLUE,
            font_size=19,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(continuum_stack, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(content[1]), FadeIn(requirements, shift=UP * 0.05), run_time=0.85)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.20)


class MethodsTraditionalLimits(Scene):
    """Chapter 2.2 — explain why traditional routes could not provide that set."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Traditional methods could not provide them}",
            "No off-the-shelf route gave us realism, continuity, and reuse together",
        )

        requirement_row = VGroup(
            Tex(r"\textbf{naturalistic}", color=INK, font_size=22),
            Dot(radius=0.04, color=LGREY),
            Tex(r"\textbf{continuous}", color=INK, font_size=22),
            Dot(radius=0.04, color=LGREY),
            Tex(r"\textbf{reusable}", color=INK, font_size=22),
        ).arrange(RIGHT, buff=0.18)
        requirement_row.next_to(title, DOWN, buff=0.34)

        limits = VGroup(
            make_section_block(
                "Curated photographs",
                (
                    "realistic images, but uncontrolled low-level variation",
                    "and very few matched continua within one object-scene concept",
                ),
                accent=RED,
                width=8.90,
            ),
            make_section_block(
                "Existing databases",
                (
                    "broad coverage, but limited fine-grained sets with stable semantic identity",
                    "and insufficient control over perceptual spacing",
                ),
                accent=RED,
                width=8.90,
            ),
            make_section_block(
                "Manual morphing or editing",
                (
                    "better control, but weaker realism and poor scalability across many categories",
                    "and many different stimulus families",
                ),
                accent=AMBER,
                width=8.90,
            ),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        limits.next_to(requirement_row, DOWN, buff=0.28)

        callout = make_callout(
            "We could find realism or control, but not both at the scale the project required.",
            RED,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(requirement_row, shift=UP * 0.04), run_time=0.55)
        self.play(
            LaggedStart(*[FadeIn(block, shift=UP * 0.05) for block in limits], lag_ratio=0.16),
            run_time=1.00,
        )
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.20)


class MethodsGANsProofOfConcept(Scene):
    """Chapter 2.3 — GANs provided the first convincing proof of concept."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Deep generative modelling: GAN proof of concept}",
            "Image synthesis in this space had mostly used GANs",
        )

        gan_column = Group(
            Tex(r"\textbf{GAN precedent}", color=INK, font_size=24),
            caption_line(_SCENE_WHEELS_CITATION, color=BLUE, font_size=20),
            text_lines(
                (
                    '"continuous stimulus space" for realistic scenes',
                    "important proof of concept for perception and memory",
                ),
                font_size=18,
                color=INK,
                max_width=4.55,
            ),
            make_image_strip(_EXEMPLAR_CODE, (0, 3, 6, 9), height=0.66, buff=0.06),
            caption_line(
                "continuous naturalistic variation was now plausible",
                color=MGREY,
                font_size=17,
                max_width=4.55,
            ),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        limit_column = VGroup(
            make_section_block(
                "What GANs established",
                (
                    "continuous image spaces could be engineered",
                    "for realistic perception and memory experiments",
                ),
                accent=BLUE,
                width=4.70,
            ),
            make_section_block(
                "Why not enough here",
                (
                    "the thesis needed many heterogeneous object-scene outputs",
                    "with more direct control over what the model should generate",
                ),
                accent=RED,
                width=4.70,
            ),
            make_section_block(
                "Main limitation",
                (
                    "strong proof of concept, but not yet the most flexible route",
                    "for our broader stimulus-design problem",
                ),
                accent=AMBER,
                width=4.70,
            ),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)

        content = split_columns(gan_column, limit_column, buff=0.52)
        content.next_to(title, DOWN, buff=0.34)

        callout = make_callout(
            "GANs showed the direction, but not yet the flexibility we needed.",
            AMBER,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(gan_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(content[1]), FadeIn(limit_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.20)


class MethodsDiffusionOpportunity(Scene):
    """Chapter 2.4 — diffusion models offered a broader stimulus-design engine."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Diffusion models: open opportunity}",
            "More flexible outputs, but still largely unexplored for cognitive stimulus design",
        )

        left_column = VGroup(
            make_section_block(
                "Promptable synthesis",
                (
                    "specify what should appear in the image",
                    "rather than search a fixed database for it",
                ),
                accent=BLUE,
                width=4.60,
            ),
            make_section_block(
                "Flexible outputs",
                (
                    "the same model can generate many different categories",
                    "and many different object-scene concepts",
                ),
                accent=AMBER,
                width=4.60,
            ),
            make_section_block(
                "Open opportunity",
                (
                    "for cognitive stimulus design, this route was still",
                    "largely unexplored but highly promising",
                ),
                accent=GREEN,
                width=4.60,
            ),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)

        example_cards = Group(
            *[
                Group(
                    caption_line(prompt, color=accent, font_size=17, max_width=2.45),
                    make_image_card(stim_path(code, idx), height=1.08, border_color=LGREY, buff=0.03),
                ).arrange(DOWN, buff=0.10)
                for code, idx, prompt, accent in _CATEGORY_EXAMPLES
            ]
        ).arrange(RIGHT, buff=0.24, aligned_edge=UP)
        right_column = Group(
            Tex(r"\textbf{One model, many outputs}", color=INK, font_size=24),
            caption_line(
                "same generative engine across different stimulus families",
                color=MGREY,
                font_size=18,
                max_width=7.2,
            ),
            example_cards,
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        content = split_columns(left_column, right_column, buff=0.56)
        content.next_to(title, DOWN, buff=0.34)

        callout = make_callout(
            "Diffusion models looked like a more flexible engine for building many controlled continua.",
            BLUE,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(left_column, shift=UP * 0.05), run_time=0.85)
        self.play(FadeIn(content[1]), FadeIn(right_column, shift=UP * 0.05), run_time=0.90)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.20)


class MethodsDiffusionExplainer(Scene):
    """Chapter 2.5 — explain forward corruption and prompt-conditioned denoising."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Diffusion model explainer}",
            "Forward corruption during training; prompt-conditioned reverse denoising at sampling",
        )

        clean = load_rgb(stim_path(_EXEMPLAR_CODE, 5))
        levels = [0.0, 0.35, 0.70, 1.0]
        forward_sources = [blend_with_noise(clean, alpha) for alpha in levels]
        reverse_sources = list(reversed(forward_sources))

        why_block = VGroup(
            Tex(r"\textbf{Why diffusion here rather than GANs?}", color=BLUE, font_size=20),
            text_lines(
                (
                    "Prompt conditioning let one model specify many heterogeneous object-scene concepts directly.",
                    "That semantic control was central for this project's high-resolution stimulus pipeline.",
                ),
                font_size=17,
                color=INK,
                max_width=10.2,
            ),
            simple_divider(10.4),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        why_block.next_to(title, DOWN, buff=0.18)

        def make_state_labels(cards: Group, labels: tuple[str, ...], *, color: str = MGREY) -> VGroup:
            state_labels = VGroup(*[MathTex(label, color=color, font_size=20) for label in labels])
            for label, card in zip(state_labels, cards):
                label.next_to(card, DOWN, buff=0.08)
            return state_labels

        forward_cards, forward_arrows = make_image_progression(
            forward_sources,
            height=0.80,
            arrow_color=MGREY,
            border_color=LGREY,
        )
        reverse_cards, reverse_arrows = make_image_progression(
            reverse_sources,
            height=0.80,
            arrow_color=BLUE,
            border_color=LGREY,
        )

        forward_labels = make_state_labels(
            forward_cards,
            (r"z_0", r"z_t", r"z_{t+\Delta}", r"z_T"),
        )
        reverse_labels = make_state_labels(
            reverse_cards,
            (r"z_T", r"z_t", r"z_{t-\Delta}", r"z_0"),
            color=BLUE,
        )

        forward_row = Group(Group(forward_cards, forward_arrows), forward_labels).arrange(
            DOWN, buff=0.02
        )
        reverse_row = Group(Group(reverse_cards, reverse_arrows), reverse_labels).arrange(
            DOWN, buff=0.02
        )

        forward_formula = MathTex(
            r"z_t = \sqrt{\bar{\alpha}_t}\, z_0 + \sqrt{1-\bar{\alpha}_t}\,\epsilon,"
            r"\quad \epsilon \sim \mathcal{N}(0, I)",
            color=MGREY,
            font_size=22,
        )
        if forward_formula.width > 10.0:
            forward_formula.scale_to_fit_width(10.0)

        forward_block = Group(
            Group(
                Tex(r"\textbf{Forward corruption process}", color=INK, font_size=22),
                caption_line(
                    "During training, sample a real example and progressively corrupt it with Gaussian noise.",
                    color=MGREY,
                    font_size=17,
                    max_width=10.0,
                ),
                forward_formula,
            ).arrange(DOWN, buff=0.06, aligned_edge=LEFT),
            forward_row,
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        prompt_pipeline = Group(
            caption_line(_DIFFUSION_PROMPT, color=BLUE, font_size=18, max_width=3.0),
            MathTex(r"\xrightarrow{\text{text encoder}}", color=AMBER, font_size=21),
            MathTex(r"c", color=GREEN, font_size=26),
        ).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)

        reverse_formula = MathTex(
            r"\hat{\epsilon}_{\theta}(z_t, t, c)"
            r"\;\Longrightarrow\; p_{\theta}(z_{t-1}\mid z_t, c)",
            color=BLUE,
            font_size=22,
        )
        if reverse_formula.width > 10.0:
            reverse_formula.scale_to_fit_width(10.0)

        reverse_block = Group(
            Group(
                Tex(r"\textbf{Reverse denoising process}", color=INK, font_size=22),
                caption_line(
                    "At sampling time, start from noise and iteratively remove predicted noise under prompt conditioning.",
                    color=MGREY,
                    font_size=17,
                    max_width=10.0,
                ),
                prompt_pipeline,
                reverse_formula,
            ).arrange(DOWN, buff=0.06, aligned_edge=LEFT),
            reverse_row,
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        content = Group(
            forward_block,
            simple_divider(10.2),
            reverse_block,
        ).arrange(DOWN, buff=0.28)

        latent_note = caption_line(
            "Shown in image space for intuition; in Stable Diffusion XL, denoising is performed in a compressed latent space.",
            color=MGREY,
            font_size=15,
            max_width=10.4,
        )

        content_with_note = Group(content, latent_note).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        bottom_limit = -config.frame_y_radius + 0.34
        available_height = why_block.get_bottom()[1] - bottom_limit - 0.22
        if content_with_note.height > available_height:
            content_with_note.scale_to_fit_height(available_height)
        content_with_note.next_to(why_block, DOWN, buff=0.18)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(why_block, shift=UP * 0.04), run_time=0.70)
        self.play(FadeIn(forward_block[0], shift=UP * 0.04), run_time=0.45)
        self.play(FadeIn(forward_cards[0], scale=0.96), run_time=0.28)
        for idx in range(1, len(forward_cards)):
            self.play(Create(forward_arrows[idx - 1]), FadeIn(forward_cards[idx], scale=0.96), run_time=0.28)
        self.play(FadeIn(forward_labels), run_time=0.28)
        self.play(FadeIn(content[1]), FadeIn(reverse_block[0], shift=UP * 0.04), run_time=0.38)
        self.play(FadeIn(reverse_cards[0], scale=0.96), run_time=0.28)
        for idx in range(1, len(reverse_cards)):
            self.play(Create(reverse_arrows[idx - 1]), FadeIn(reverse_cards[idx], scale=0.96), run_time=0.28)
        self.play(FadeIn(reverse_labels), FadeIn(latent_note, shift=UP * 0.03), run_time=0.32)
        self.wait(3.00)


class MethodsProjectPlan(Scene):
    """Chapter 2.6 — end with the actual thesis plan."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = title_block(
            r"\textbf{Project plan}",
            "Generate the stimulus set, validate it behaviourally, then use it in neuroimaging",
        )

        generate_body = Group(
            make_image_strip(_EXEMPLAR_CODE, (0, 3, 6, 9), height=0.42, buff=0.04),
            text_lines(
                (
                    "generate many candidate continua",
                    "from fixed prompts and controlled variation",
                ),
                font_size=15,
                color=INK,
                max_width=2.80,
            ),
        ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)

        validate_body = text_lines(
            (
                "similarity judgments",
                "working-memory validation",
                "retain the usable stimulus sets",
            ),
            font_size=16,
            color=INK,
            max_width=2.60,
        )

        study2_brain = brain_icon_with_evc(highlight_color=BLUE, scale_factor=0.38)
        scan_body = Group(
            study2_brain["group"],
            text_lines(
                (
                    "use the validated set in fMRI",
                    "test representational format",
                    "and sensory recruitment",
                ),
                font_size=16,
                color=INK,
                max_width=2.90,
            ),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        stages = Group(
            make_pipeline_stage("01", "Generate", generate_body, accent=BLUE, width=2.90),
            make_pipeline_stage("02", "Validate", validate_body, accent=AMBER, width=2.65),
            make_pipeline_stage("03", "Neuroimaging", scan_body, accent=GREEN, width=3.00),
        )
        arrows = VGroup(
            *[
                Arrow(
                    LEFT * 0.34,
                    RIGHT * 0.34,
                    color=MGREY,
                    stroke_width=1.6,
                    buff=0.0,
                    tip_length=0.12,
                    tip_shape=StealthTip,
                )
                for _ in range(len(stages) - 1)
            ]
        )
        flow_items = Group()
        for idx, stage in enumerate(stages):
            flow_items.add(stage)
            if idx < len(arrows):
                flow_items.add(arrows[idx])
        flow = flow_items.arrange(RIGHT, buff=0.22, aligned_edge=UP)
        flow.next_to(title, DOWN, buff=0.44)

        callout = make_callout(
            "Generate a stimulus set, validate it behaviourally, then use it in the neuroimaging study.",
            GREEN,
            font_size=20,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title, shift=UP * 0.04), run_time=0.75)
        self.play(FadeIn(stages[0], shift=UP * 0.05), run_time=0.50)
        for idx in range(1, len(stages)):
            self.play(Create(arrows[idx - 1]), FadeIn(stages[idx], shift=UP * 0.05), run_time=0.55)
        self.play(FadeIn(callout, shift=UP * 0.04), run_time=0.55)
        self.wait(3.20)


_METHODS_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    MethodsStimulusRequirements,
    MethodsTraditionalLimits,
    MethodsGANsProofOfConcept,
    MethodsDiffusionOpportunity,
    MethodsDiffusionExplainer,
    MethodsProjectPlan,
)
_METHODS_SECTION_NAMES: tuple[str, ...] = (
    "methods_stimulus_requirements",
    "methods_traditional_limits",
    "methods_gans_proof_of_concept",
    "methods_diffusion_opportunity",
    "methods_diffusion_explainer",
    "methods_project_plan",
)


class Methods(Scene):
    """Unified production render for the methods chapter."""

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        zip(_METHODS_SECTION_NAMES, _METHODS_MASTER_SECTION_ORDER)
    )

    def __init__(self, *args, **kwargs):
        config.output_file = "methods"
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
        """Replay one existing methods scene inside the master section render."""
        self.next_section(section_name)
        if carry_previous_frame:
            self._hold_previous_section_frame()
        self._reset_master_scene_state()
        scene_cls.construct(self)

    def construct(self) -> None:
        """Render the full methods chapter as one sectioned scene."""
        self._reset_master_scene_state()
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._render_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )


_PUBLIC_SCENES: tuple[type[Scene], ...] = _METHODS_MASTER_SECTION_ORDER

for _scene_cls in _PUBLIC_SCENES:
    _wrapped = _wrap_scene(_scene_cls)
    _wrapped.__module__ = "_methods_internal"
    globals()[_scene_cls.__name__] = _wrapped
del _scene_cls

Methods.__module__ = __name__
__all__ = ["Methods"]
