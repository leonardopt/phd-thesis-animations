"""
Diffusion explainer.

  Diffusion01ForwardReverse      — title plus forward/reverse intuition
  Diffusion02PromptToContinuum   — fixed prompt to stimulus continuum
  Diffusion03WhyItMattersForThesis — Study 1 / Study 2 payoff

Render:
    uv run manim intro_diffusion_explainer.py Diffusion01ForwardReverse -ql
    uv run manim intro_diffusion_explainer.py Diffusion02PromptToContinuum -ql
    uv run manim intro_diffusion_explainer.py Diffusion03WhyItMattersForThesis -ql
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from manim import *

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#6B7280"
BLUE  = "#2563EB"
PANEL = "#F8FAFC"

# ── Asset and DDPM notation ──────────────────────────────────────────────────
IMAGE_PATH = Path(
    "/Users/leonardo/sd-wltm-fmri-experiment/images/stimuli_task/ANI-CAT-T00.png"
)
CONTINUUM_PATHS = [
    IMAGE_PATH,
    Path("/Users/leonardo/sd-wltm-fmri-experiment/images/stimuli_task/ANI-CAT-D01.png"),
    Path("/Users/leonardo/sd-wltm-fmri-experiment/images/stimuli_task/ANI-CAT-D02.png"),
    Path("/Users/leonardo/sd-wltm-fmri-experiment/images/stimuli_task/ANI-CAT-D03.png"),
]

TITLE_TEXT = "How do diffusion models work?"
FORWARD_FORMULA = r"q(x_i \mid x_{i-1})"
REVERSE_FORMULA = r"p_{\theta}(x_{i-1} \mid x_i, c)"
PROMPT_TEXT = "a cat in a coherent indoor scene"

FORWARD_LEVELS = [0.00, 0.18, 0.38, 0.58, 0.78, 1.00]
FORWARD_LABELS = [r"x_0", r"x_1", r"x_2", r"x_3", r"x_{T-1}", r"x_T"]
REVERSE_LABELS = [r"x_T", r"x_{T-1}", r"x_3", r"x_2", r"x_1", r"x_0"]

# ── Layout ────────────────────────────────────────────────────────────────────
CARD_HEIGHT = 1.16
TOP_ROW_Y = 1.28
BOTTOM_ROW_Y = -1.72
DIVIDER_Y = -0.10
TOP_HEADING_Y = 2.16
BOTTOM_HEADING_Y = -0.56
STATE_XS = np.linspace(-3.15, 4.15, len(FORWARD_LEVELS))
FORWARD_CENTER_SHIFT = DOWN * 0.90

np.random.seed(7)
_BASE_NOISE: np.ndarray | None = None
_FORWARD_ARRAYS: list[np.ndarray] | None = None


@dataclass
class BoardParts:
    top_heading: VGroup
    bottom_heading: VGroup
    divider: Line
    top_cards: Group
    top_labels: VGroup
    top_arrows: VGroup
    bottom_cards: Group
    bottom_labels: VGroup
    bottom_arrows: VGroup
    top_highlight: SurroundingRectangle
    bottom_highlight: SurroundingRectangle


@dataclass
class CenteredForwardParts:
    heading: VGroup
    cards: Group
    labels: VGroup
    arrows: VGroup
    highlight: SurroundingRectangle


def load_image_array(path: str | Path) -> np.ndarray:
    """Load an RGB image as float32 in [0, 1]."""
    image = Image.open(path).convert("RGB")
    return np.asarray(image).astype(np.float32) / 255.0


def to_uint8(image_array: np.ndarray) -> np.ndarray:
    """Convert a float image in [0, 1] to uint8."""
    return (255 * np.clip(image_array, 0.0, 1.0)).astype(np.uint8)


def add_noise(image_array: np.ndarray, noise_level: float) -> np.ndarray:
    """Blend an image with Gaussian noise."""
    global _BASE_NOISE

    if _BASE_NOISE is None or _BASE_NOISE.shape != image_array.shape:
        noise = np.random.normal(0, 1, image_array.shape)
        noise = (noise - noise.min()) / (noise.max() - noise.min())
        _BASE_NOISE = noise.astype(np.float32)

    alpha = float(np.clip(noise_level, 0.0, 1.0))
    blended = (1.0 - alpha) * image_array + alpha * _BASE_NOISE
    return np.clip(blended, 0.0, 1.0)


def get_forward_arrays() -> list[np.ndarray]:
    """Return the deterministic forward DDPM states."""
    global _FORWARD_ARRAYS

    if _FORWARD_ARRAYS is None:
        clean = load_image_array(IMAGE_PATH)
        _FORWARD_ARRAYS = [add_noise(clean, level) for level in FORWARD_LEVELS]
    return _FORWARD_ARRAYS


def get_reverse_arrays() -> list[np.ndarray]:
    """Return the deterministic reverse DDPM states."""
    return list(reversed(get_forward_arrays()))


def make_image_mobject(content: str | Path | np.ndarray, height: float) -> ImageMobject:
    """Create an ImageMobject from a path or array."""
    if isinstance(content, (str, Path)):
        image = ImageMobject(str(content))
    else:
        image = ImageMobject(to_uint8(content))
    image.scale_to_fit_height(height)
    return image


def make_frame(image: ImageMobject, color: str = LGREY, buff: float = 0.08) -> RoundedRectangle:
    """Create a rounded frame around an image."""
    frame = RoundedRectangle(
        width=image.width + 2 * buff,
        height=image.height + 2 * buff,
        corner_radius=0.16,
        stroke_color=color,
        stroke_width=1.5,
    )
    frame.set_fill(PANEL, opacity=0.0)
    frame.move_to(image)
    return frame


def make_card(content: str | Path | np.ndarray, height: float) -> Group:
    """Create a framed image card."""
    image = make_image_mobject(content, height=height)
    frame = make_frame(image)
    return Group(image, frame)


def make_embedding_block() -> VGroup:
    """Create a numeric text-embedding stand-in."""
    rng = np.random.default_rng(7)
    values = [[f"{value:+.2f}" for value in rng.normal(0.0, 0.65, 4)] for _ in range(4)]
    matrix = Matrix(
        values,
        h_buff=0.72,
        v_buff=0.22,
        element_to_mobject=lambda entry: MathTex(entry, color=MGREY, font_size=18),
    )
    matrix.get_brackets().set_color(MGREY)
    matrix.scale(0.48)
    return matrix


def make_heading(title_text: str, formula: str, formula_color: str, y: float) -> VGroup:
    """Create the left-aligned heading block for one process."""
    heading = VGroup(
        Tex(title_text, color=INK, font_size=26),
        MathTex(formula, color=formula_color, font_size=26),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    heading.to_edge(LEFT, buff=0.50)
    heading.shift(UP * (y - heading.get_center()[1]))
    return heading


def build_cards(arrays: list[np.ndarray], y: float) -> Group:
    """Create a horizontal row of image cards."""
    cards = Group()
    for x, array in zip(STATE_XS, arrays):
        card = make_card(array, height=CARD_HEIGHT)
        card.move_to(RIGHT * x + UP * y)
        cards.add(card)
    return cards


def build_state_labels(cards: Group, labels: list[str], direction: np.ndarray, color: str) -> VGroup:
    """Create mathematical timestep labels for a row of cards."""
    state_labels = VGroup()
    for label, card in zip(labels, cards):
        state = MathTex(label, color=color, font_size=24)
        state.next_to(card, direction, buff=0.14)
        state_labels.add(state)
    return state_labels


def build_arrows(cards: Group, color: str) -> VGroup:
    """Create arrows between consecutive cards."""
    arrows = VGroup()
    for left_card, right_card in zip(cards[:-1], cards[1:]):
        arrow = Arrow(
            start=left_card.get_right() + RIGHT * 0.08,
            end=right_card.get_left() + LEFT * 0.08,
            buff=0.06,
            color=color,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        arrows.add(arrow)
    return arrows


def build_board() -> BoardParts:
    """Build the full DDPM board with all elements available."""
    forward_arrays = get_forward_arrays()
    reverse_arrays = get_reverse_arrays()

    top_cards = build_cards(forward_arrays, TOP_ROW_Y)
    bottom_cards = build_cards(reverse_arrays, BOTTOM_ROW_Y)

    top_labels = build_state_labels(top_cards, FORWARD_LABELS, DOWN, MGREY)
    bottom_labels = build_state_labels(bottom_cards, REVERSE_LABELS, UP, BLUE)

    divider = Line(
        start=LEFT * 6.55 + UP * DIVIDER_Y,
        end=RIGHT * 6.55 + UP * DIVIDER_Y,
        color=LGREY,
        stroke_width=1.5,
    )

    return BoardParts(
        top_heading=make_heading("Forward", FORWARD_FORMULA, MGREY, TOP_HEADING_Y),
        bottom_heading=make_heading("Reverse", REVERSE_FORMULA, BLUE, BOTTOM_HEADING_Y),
        divider=divider,
        top_cards=top_cards,
        top_labels=top_labels,
        top_arrows=build_arrows(top_cards, MGREY),
        bottom_cards=bottom_cards,
        bottom_labels=bottom_labels,
        bottom_arrows=build_arrows(bottom_cards, BLUE),
        top_highlight=SurroundingRectangle(
            top_cards[-1], color=MGREY, stroke_width=2.1, buff=0.08
        ),
        bottom_highlight=SurroundingRectangle(
            bottom_cards[-1], color=BLUE, stroke_width=2.1, buff=0.08
        ),
    )


def visible_process_group(cards: Group, labels: VGroup, arrows: VGroup, count: int) -> Group:
    """Return the visible subset of one row up to count states."""
    parts: list[Mobject] = []
    if count <= 0:
        return Group()

    parts.extend([cards[0], labels[0]])
    for idx in range(1, count):
        parts.extend([arrows[idx - 1], cards[idx], labels[idx]])
    return Group(*parts)


def build_centered_forward_parts(board: BoardParts) -> CenteredForwardParts:
    """Return a centered version of the full forward process."""
    heading = board.top_heading.copy()
    cards = board.top_cards.copy()
    labels = board.top_labels.copy()
    arrows = board.top_arrows.copy()
    highlight = board.top_highlight.copy()

    heading.shift(FORWARD_CENTER_SHIFT)
    cards.shift(FORWARD_CENTER_SHIFT)
    labels.shift(FORWARD_CENTER_SHIFT)
    arrows.shift(FORWARD_CENTER_SHIFT)
    highlight.shift(FORWARD_CENTER_SHIFT)

    return CenteredForwardParts(
        heading=heading,
        cards=cards,
        labels=labels,
        arrows=arrows,
        highlight=highlight,
    )

def make_center_statement(text: str, color: str = INK, font_size: int = 34) -> Tex:
    """Create a centered statement for the current clip."""
    line = Tex(text, color=color, font_size=font_size)
    line.move_to(UP * 0.18)
    return line


def make_top_statement(text: str, color: str = INK, font_size: int = 28) -> Tex:
    """Create a top-aligned statement shared across clips."""
    line = Tex(text, color=color, font_size=font_size)
    line.to_edge(UP, buff=0.34)
    return line


def make_prompt_text(font_size: int = 28) -> Tex:
    """Create the literal prompt string."""
    return Tex(f'"{PROMPT_TEXT}"', color=INK, font_size=font_size)


def make_text_embedding_group() -> VGroup:
    """Create a compact text-embedding visual labeled by c."""
    label = Tex("text embedding", color=MGREY, font_size=16)
    symbol = MathTex(r"c", color=MGREY, font_size=26)
    block = make_embedding_block()
    return VGroup(label, block, symbol).arrange(DOWN, buff=0.06)


def make_condition_stack(
    prompt_position: np.ndarray,
    embedding_position: np.ndarray,
    prompt_font_size: int = 22,
    embedding_scale: float = 0.95,
) -> tuple[Tex, VGroup, Arrow]:
    """Create a prompt plus embedding stack used for conditioning."""
    prompt = make_prompt_text(font_size=prompt_font_size)
    prompt.move_to(prompt_position)

    embedding = make_text_embedding_group()
    embedding.scale(embedding_scale)
    embedding.move_to(embedding_position)

    arrow = Arrow(
        start=prompt.get_bottom() + DOWN * 0.05,
        end=embedding.get_top() + UP * 0.05,
        buff=0.08,
        color=MGREY,
        stroke_width=1.8,
        tip_shape=StealthTip,
    )
    return prompt, embedding, arrow


def make_continuum_strip(height: float = 1.44) -> tuple[Group, Line, VGroup, Tex]:
    """Create the selected Study 1 continuum strip from real stimulus images."""
    cards = Group(*[make_card(path, height=height) for path in CONTINUUM_PATHS])
    cards.arrange(RIGHT, buff=0.22)
    cards.move_to(RIGHT * 1.55 + UP * 0.15)

    dots = VGroup(*[Dot(radius=0.045, color=MGREY, fill_opacity=1.0) for _ in cards])
    for dot, card in zip(dots, cards):
        dot.move_to(card.get_bottom() + DOWN * 0.35)

    line = Line(
        dots[0].get_center(),
        dots[-1].get_center(),
        color=LGREY,
        stroke_width=2.0,
    )
    slider_label = Tex("latent interpolation", color=MGREY, font_size=20)
    slider_label.next_to(line, DOWN, buff=0.16)
    return cards, line, dots, slider_label


class Diffusion01ForwardReverse(Scene):
    """Title plus forward noising and reverse denoising."""

    def construct(self) -> None:
        self.camera.background_color = BG

        board = build_board()
        centered = build_centered_forward_parts(board)

        title = make_center_statement(TITLE_TEXT, font_size=38)
        top_line = make_top_statement(TITLE_TEXT, color=INK, font_size=29)
        centered_heading = VGroup(
            Tex("Forward", color=INK, font_size=28),
            MathTex(FORWARD_FORMULA, color=MGREY, font_size=28),
        ).arrange(DOWN, buff=0.08)
        centered_heading.next_to(centered.cards, UP, buff=0.26)

        forward_note = Tex("Forward: add noise", color=MGREY, font_size=22)
        forward_note.next_to(top_line, DOWN, buff=0.28)
        reverse_note = Tex("Reverse: remove noise, guided by text", color=BLUE, font_size=22)
        reverse_note.next_to(top_line, DOWN, buff=0.28)

        prompt_text, embedding_group, prompt_arrow = make_condition_stack(
            prompt_position=LEFT * 5.05 + DOWN * 1.20,
            embedding_position=LEFT * 5.05 + DOWN * 2.15,
            prompt_font_size=22,
            embedding_scale=0.95,
        )

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.75)
        self.wait(0.20)
        self.play(
            Transform(title, top_line),
            FadeIn(forward_note, shift=UP * 0.04),
            FadeIn(centered_heading, shift=UP * 0.05),
            FadeIn(centered.cards[0], scale=0.97),
            FadeIn(centered.labels[0], shift=UP * 0.03),
            run_time=0.80,
        )

        for idx in range(1, len(FORWARD_LABELS)):
            self.play(
                Create(centered.arrows[idx - 1]),
                FadeIn(centered.cards[idx], scale=0.97),
                FadeIn(centered.labels[idx], shift=UP * 0.03),
                run_time=0.56,
            )

        self.play(Create(centered.highlight), run_time=0.40)
        self.play(
            Transform(centered_heading, board.top_heading),
            centered.cards.animate.shift(-FORWARD_CENTER_SHIFT),
            centered.labels.animate.shift(-FORWARD_CENTER_SHIFT),
            centered.arrows.animate.shift(-FORWARD_CENTER_SHIFT),
            centered.highlight.animate.shift(-FORWARD_CENTER_SHIFT),
            Create(board.divider),
            FadeIn(board.bottom_heading, shift=UP * 0.05),
            FadeOut(forward_note, shift=UP * 0.03),
            FadeIn(reverse_note, shift=UP * 0.03),
            FadeIn(prompt_text, shift=UP * 0.04),
            run_time=0.95,
        )
        self.play(FadeIn(embedding_group, shift=UP * 0.03), Create(prompt_arrow), run_time=0.55)
        self.play(
            FadeIn(board.bottom_cards[0], scale=0.97),
            FadeIn(board.bottom_labels[0], shift=DOWN * 0.03),
            run_time=0.45,
        )

        for idx in range(1, len(REVERSE_LABELS)):
            self.play(
                Create(board.bottom_arrows[idx - 1]),
                FadeIn(board.bottom_cards[idx], scale=0.97),
                FadeIn(board.bottom_labels[idx], shift=DOWN * 0.03),
                run_time=0.58,
            )

        self.play(Create(board.bottom_highlight), run_time=0.40)
        self.play(FadeOut(reverse_note, shift=UP * 0.03), run_time=0.25)
        self.wait(0.9)


class Diffusion02PromptToContinuum(Scene):
    """From fixed prompt to an actual Study 1 stimulus continuum."""

    def construct(self) -> None:
        self.camera.background_color = BG

        board = build_board()
        top_line = make_top_statement(TITLE_TEXT, color=INK, font_size=29)
        method_line = make_top_statement(
            "In Study 1, we fixed the prompt and varied the latent noise.",
            color=INK,
            font_size=27,
        )

        top_group = visible_process_group(
            board.top_cards,
            board.top_labels,
            board.top_arrows,
            len(FORWARD_LABELS),
        )
        bottom_group = visible_process_group(
            board.bottom_cards,
            board.bottom_labels,
            board.bottom_arrows,
            len(REVERSE_LABELS),
        )
        board_group = Group(
            board.top_heading,
            top_group,
            board.top_highlight,
            board.divider,
            board.bottom_heading,
            bottom_group,
            board.bottom_highlight,
        )

        prompt_text, embedding_group, prompt_arrow = make_condition_stack(
            prompt_position=LEFT * 5.05 + DOWN * 1.20,
            embedding_position=LEFT * 5.05 + DOWN * 2.15,
            prompt_font_size=22,
            embedding_scale=0.95,
        )

        prompt_target = make_prompt_text(font_size=25)
        prompt_target.move_to(LEFT * 4.65 + UP * 0.80)
        prompt_label = Tex("representative prompt", color=MGREY, font_size=18)
        prompt_label.next_to(prompt_target, UP, buff=0.14)

        embedding_target = make_text_embedding_group()
        embedding_target.scale(0.98)
        embedding_target.move_to(LEFT * 4.65 + DOWN * 0.55)

        continuum_cards, continuum_line, continuum_dots, continuum_label = make_continuum_strip(height=1.42)
        continuum_label_group = VGroup(continuum_line, continuum_dots, continuum_label)

        self.add(
            top_line,
            board.top_heading,
            top_group,
            board.top_highlight,
            board.divider,
            board.bottom_heading,
            bottom_group,
            board.bottom_highlight,
            prompt_text,
            embedding_group,
            prompt_arrow,
        )
        self.play(
            Transform(top_line, method_line),
            FadeOut(board_group, shift=UP * 0.02),
            Transform(prompt_text, prompt_target),
            FadeOut(embedding_group, shift=DOWN * 0.02),
            FadeOut(prompt_arrow),
            run_time=0.95,
        )
        self.play(FadeIn(prompt_label, shift=UP * 0.03), run_time=0.30)
        self.play(FadeTransform(prompt_text.copy(), embedding_target), run_time=0.60)
        self.play(FadeIn(continuum_cards[0], scale=0.97), run_time=0.45)
        self.play(
            LaggedStart(*[FadeIn(card, scale=0.97) for card in continuum_cards[1:]], lag_ratio=0.18),
            run_time=1.00,
        )
        self.play(FadeIn(continuum_label_group, shift=UP * 0.04), run_time=0.45)
        self.wait(1.5)


class Diffusion03WhyItMattersForThesis(Scene):
    """Methods payoff for Study 1 and Study 2."""

    def construct(self) -> None:
        self.camera.background_color = BG

        top_line = make_top_statement(
            "In Study 1, we fixed the prompt and varied the latent noise.",
            color=INK,
            font_size=27,
        )

        prompt_target = make_prompt_text(font_size=25)
        prompt_target.move_to(LEFT * 4.65 + UP * 0.80)
        prompt_label = Tex("representative prompt", color=MGREY, font_size=18)
        prompt_label.next_to(prompt_target, UP, buff=0.14)
        embedding_target = make_text_embedding_group()
        embedding_target.scale(0.98)
        embedding_target.move_to(LEFT * 4.65 + DOWN * 0.55)

        continuum_cards, continuum_line, continuum_dots, continuum_label = make_continuum_strip(height=1.42)
        takeaway_1 = Tex("same prompt = same semantic content", color=INK, font_size=22)
        takeaway_2 = Tex("latent variation = controlled perceptual differences", color=MGREY, font_size=22)
        takeaway_group = VGroup(takeaway_1, takeaway_2).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        takeaway_group.move_to(LEFT * 3.05 + DOWN * 2.00)

        study1_text = VGroup(
            Tex("Study 1", color=INK, font_size=23),
            Tex("perceptual scaling", color=MGREY, font_size=21),
        ).arrange(DOWN, buff=0.04)
        study2_text = VGroup(
            Tex("Study 2", color=INK, font_size=23),
            Tex("memory + fMRI", color=BLUE, font_size=21),
        ).arrange(DOWN, buff=0.04)
        study1_text.move_to(RIGHT * 0.55 + DOWN * 2.22)
        study2_text.move_to(RIGHT * 4.00 + DOWN * 2.22)

        study_arrow_1 = Arrow(
            start=continuum_cards[1].get_bottom() + DOWN * 0.06,
            end=study1_text.get_top() + UP * 0.05,
            buff=0.05,
            color=MGREY,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        study_arrow_2 = Arrow(
            start=continuum_cards[2].get_bottom() + DOWN * 0.06,
            end=study2_text.get_top() + UP * 0.05,
            buff=0.05,
            color=BLUE,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )

        caption = Tex(
            "This enabled controlled naturalistic stimulus sets for Study 1 and Study 2.",
            color=INK,
            font_size=23,
        )
        caption.to_edge(DOWN, buff=0.25)

        self.add(
            top_line,
            prompt_target,
            prompt_label,
            embedding_target,
            continuum_cards,
            continuum_line,
            continuum_dots,
            continuum_label,
        )
        self.play(FadeIn(takeaway_group, shift=UP * 0.04), run_time=0.70)
        self.play(
            FadeIn(study1_text, shift=UP * 0.03),
            FadeIn(study2_text, shift=UP * 0.03),
            Create(study_arrow_1),
            Create(study_arrow_2),
            run_time=0.90,
        )
        self.play(FadeIn(caption, shift=UP * 0.05), run_time=0.65)
        self.wait(2.4)
