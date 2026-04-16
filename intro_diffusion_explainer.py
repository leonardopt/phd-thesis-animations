"""
Diffusion explainer.

  Diffusion01Intro       — DDPM framing: two stochastic processes
  Diffusion02ForwardPass — fixed forward pass from data to noise
  Diffusion03ReversePass — learned reverse pass from noise to data
  Diffusion04PromptGuidance — Stable Diffusion prompt guidance
  Diffusion05BigPicture  — final DDPM summary board

Render:
    uv run manim intro_diffusion_explainer.py Diffusion01Intro -ql
    uv run manim intro_diffusion_explainer.py Diffusion02ForwardPass -ql
    uv run manim intro_diffusion_explainer.py Diffusion03ReversePass -ql
    uv run manim intro_diffusion_explainer.py Diffusion04PromptGuidance -ql
    uv run manim intro_diffusion_explainer.py Diffusion05BigPicture -ql
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

TITLE_TEXT = "How do diffusion models work?"
FORWARD_FORMULA = r"p(x_i \mid x_{i-1})"
REVERSE_FORMULA = r"p_{\theta}(x_{i-1} \mid x_i)"
PROMPT_TEXT = "photo of a cat in a room"

FORWARD_LEVELS = [0.00, 0.18, 0.38, 0.58, 0.78, 1.00]
FORWARD_LABELS = [r"x_0", r"x_1", r"x_2", r"x_3", r"x_{T-1}", r"x_T"]
REVERSE_LABELS = [r"x_T", r"x_{T-1}", r"x_3", r"x_2", r"x_1", r"x_0"]

# ── Layout ────────────────────────────────────────────────────────────────────
CARD_HEIGHT = 1.16
TITLE_TOP_SCALE = 0.70
TOP_ROW_Y = 1.28
BOTTOM_ROW_Y = -1.72
DIVIDER_Y = -0.10
TOP_HEADING_Y = 2.16
BOTTOM_HEADING_Y = -0.56
EXPLANATION_Y = 2.56
STATE_XS = np.linspace(-3.15, 4.15, len(FORWARD_LEVELS))

np.random.seed(7)
_BASE_NOISE: np.ndarray | None = None
_FORWARD_ARRAYS: list[np.ndarray] | None = None


@dataclass
class BoardParts:
    title: Tex
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


def pixelate_array(image_array: np.ndarray, pixels: int = 18) -> np.ndarray:
    """Downsample and upsample an image to suggest a latent-space representation."""
    image = Image.fromarray(to_uint8(image_array))
    resampling = Image.Resampling if hasattr(Image, "Resampling") else Image
    small = image.resize((pixels, pixels), resample=resampling.BILINEAR)
    pixelated = small.resize(image.size, resample=resampling.NEAREST)
    return np.asarray(pixelated).astype(np.float32) / 255.0


def make_overlay_panel(width: float, height: float, opacity: float = 0.96) -> RoundedRectangle:
    """Create a soft panel for temporary overlays."""
    panel = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.18,
        stroke_color=LGREY,
        stroke_width=1.6,
    )
    panel.set_fill(WHITE, opacity=opacity)
    return panel


def make_prompt_chip(prompt_text: str) -> VGroup:
    """Create a compact prompt chip."""
    text = Tex(f'"{prompt_text}"', color=INK, font_size=22)
    box = RoundedRectangle(
        width=text.width + 0.34,
        height=text.height + 0.24,
        corner_radius=0.14,
        stroke_color=BLUE,
        stroke_width=1.8,
    )
    box.set_fill(BLUE, opacity=0.08)
    return VGroup(box, text)


def make_model_box(label: str = "model") -> VGroup:
    """Create a compact denoiser box."""
    box = RoundedRectangle(
        width=1.65,
        height=0.88,
        corner_radius=0.14,
        stroke_color=BLUE,
        stroke_width=1.8,
    )
    box.set_fill(BLUE, opacity=0.08)
    text = Tex(label, color=INK, font_size=22)
    return VGroup(box, text)


def make_labeled_box(
    label: str,
    width: float = 1.65,
    height: float = 0.88,
    color: str = BLUE,
    font_size: int = 22,
) -> VGroup:
    """Create a rounded process box with a centered label."""
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.14,
        stroke_color=color,
        stroke_width=1.8,
    )
    box.set_fill(color, opacity=0.08)
    text = Tex(label, color=INK, font_size=font_size)
    return VGroup(box, text)


def make_embedding_block() -> VGroup:
    """Create a simple visual stand-in for a text embedding."""
    frame = RoundedRectangle(
        width=1.55,
        height=0.78,
        corner_radius=0.14,
        stroke_color=BLUE,
        stroke_width=1.8,
    )
    frame.set_fill(BLUE, opacity=0.04)

    rng = np.random.default_rng(7)
    cells = VGroup(
        *[
            Square(side_length=0.10, stroke_width=0)
            for _ in range(24)
        ]
    )
    colors = [BLUE, "#60A5FA", MGREY, LGREY]
    for cell in cells:
        cell.set_fill(colors[int(rng.integers(0, len(colors)))], opacity=0.95)
    cells.arrange_in_grid(rows=4, cols=6, buff=0.04)
    cells.move_to(frame)
    return VGroup(frame, cells)


def make_title(centered: bool) -> Tex:
    """Create the shared title in intro or board position."""
    title = Tex(TITLE_TEXT, color=INK, font_size=40)
    if centered:
        title.move_to(UP * 0.20)
    else:
        title.scale(TITLE_TOP_SCALE)
        title.to_edge(UP, buff=0.30)
    return title


def make_explanation_line(text: str) -> Tex:
    """Create a single centered explanatory sentence."""
    line = Tex(text, color=MGREY, font_size=24)
    line.move_to(UP * EXPLANATION_Y)
    return line


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
        title=make_title(centered=False),
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


def add_board_state(
    scene: Scene,
    board: BoardParts,
    n_forward_visible: int,
    n_reverse_visible: int,
    show_top_highlight: bool = False,
    show_bottom_highlight: bool = False,
) -> None:
    """Add a deterministic board state directly to the scene."""
    scene.add(board.title, board.top_heading, board.bottom_heading, board.divider)

    top_group = visible_process_group(board.top_cards, board.top_labels, board.top_arrows, n_forward_visible)
    bottom_group = visible_process_group(
        board.bottom_cards, board.bottom_labels, board.bottom_arrows, n_reverse_visible
    )

    if top_group.submobjects:
        scene.add(top_group)
    if bottom_group.submobjects:
        scene.add(bottom_group)
    if show_top_highlight:
        scene.add(board.top_highlight)
    if show_bottom_highlight:
        scene.add(board.bottom_highlight)


class Diffusion01Intro(Scene):
    """DDPM framing with the two stochastic processes."""

    def construct(self) -> None:
        self.camera.background_color = BG

        board = build_board()
        title = make_title(centered=True)
        intro_line = make_explanation_line("DDPMs use two stochastic processes.")

        self.play(FadeIn(title, shift=UP * 0.12), run_time=1.1)
        self.wait(1.5)

        self.play(Transform(title, board.title), run_time=1.4)
        self.play(FadeIn(intro_line, shift=UP * 0.08), run_time=0.7)
        self.wait(1.0)

        self.play(
            FadeIn(board.top_heading, shift=UP * 0.08),
            FadeIn(board.bottom_heading, shift=UP * 0.08),
            Create(board.divider),
            run_time=1.1,
        )
        self.play(
            FadeIn(board.top_cards[0], scale=0.96),
            FadeIn(board.top_labels[0], shift=UP * 0.05),
            FadeIn(board.bottom_cards[0], scale=0.96),
            FadeIn(board.bottom_labels[0], shift=DOWN * 0.05),
            run_time=1.3,
        )
        self.wait(0.6)

        self.play(FadeOut(intro_line, shift=UP * 0.06), run_time=0.6)
        self.wait(1.0)


class Diffusion02ForwardPass(Scene):
    """Fixed forward DDPM corruption from data to noise."""

    def construct(self) -> None:
        self.camera.background_color = BG

        board = build_board()
        line = make_explanation_line("The forward pass gradually corrupts data into noise.")

        add_board_state(self, board, n_forward_visible=1, n_reverse_visible=1)

        self.play(FadeIn(line, shift=UP * 0.08), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(line, shift=UP * 0.06), run_time=0.5)

        for idx in range(1, len(FORWARD_LABELS)):
            self.play(
                Create(board.top_arrows[idx - 1]),
                FadeIn(board.top_cards[idx], scale=0.96),
                FadeIn(board.top_labels[idx], shift=UP * 0.05),
                run_time=1.3,
            )
            self.wait(0.65)

        self.play(Create(board.top_highlight), run_time=0.8)
        self.wait(1.6)


class Diffusion03ReversePass(Scene):
    """Learned reverse DDPM denoising from noise to data."""

    def construct(self) -> None:
        self.camera.background_color = BG

        board = build_board()
        line = make_explanation_line("The reverse process learns to undo that corruption.")

        add_board_state(
            self,
            board,
            n_forward_visible=len(FORWARD_LABELS),
            n_reverse_visible=1,
            show_top_highlight=True,
        )

        self.play(FadeIn(line, shift=UP * 0.08), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(line, shift=UP * 0.06), run_time=0.5)

        for idx in range(1, len(REVERSE_LABELS)):
            self.play(
                Create(board.bottom_arrows[idx - 1]),
                FadeIn(board.bottom_cards[idx], scale=0.96),
                FadeIn(board.bottom_labels[idx], shift=DOWN * 0.05),
                run_time=1.35,
            )
            self.wait(0.70)

        self.play(Create(board.bottom_highlight), run_time=0.8)
        self.wait(1.8)


class Diffusion04PromptGuidance(Scene):
    """Stable Diffusion prompt guidance as a text-steered reverse step."""

    def construct(self) -> None:
        self.camera.background_color = BG

        board = build_board()
        clean_array = get_forward_arrays()[0]
        rough_latent_array = pixelate_array(add_noise(clean_array, 0.40), pixels=18)
        clean_latent_array = pixelate_array(clean_array, pixels=18)

        line = make_explanation_line("The prompt is encoded, then guides denoising.")
        reference = Tex(
            r"Rombach et al. (2022); Podell et al. (2023)",
            color=MGREY,
            font_size=14,
        )
        reference.to_corner(DR, buff=0.18)

        dim = RoundedRectangle(
            width=12.35,
            height=4.10,
            corner_radius=0.16,
            stroke_width=0,
        )
        dim.set_fill(WHITE, opacity=0.92)
        dim.move_to(DOWN * 0.10)

        prompt_label = Tex("prompt", color=MGREY, font_size=18)
        prompt_text = Tex(r'"photo of a cat\\in a room"', color=INK, font_size=25)
        prompt_group = VGroup(prompt_label, prompt_text).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
        prompt_group.move_to(LEFT * 5.00 + UP * 0.84)

        text_encoder = make_labeled_box("text encoder", width=1.95, height=0.86, color=BLUE, font_size=20)
        text_encoder.move_to(LEFT * 2.45 + UP * 0.78)

        embedding_block = make_embedding_block()
        embedding_title = Tex("text embedding", color=BLUE, font_size=18)
        embedding_symbol = MathTex(r"c", color=BLUE, font_size=22)
        embedding_label = VGroup(embedding_title, embedding_symbol).arrange(RIGHT, buff=0.08)
        embedding_group = Group(embedding_block, embedding_label)
        embedding_group.arrange(DOWN, buff=0.10, center=False)
        embedding_label.next_to(embedding_block, UP, buff=0.10)
        embedding_group.move_to(LEFT * 0.20 + UP * 0.82)

        prompt_to_encoder = Arrow(
            start=prompt_text.get_right() + RIGHT * 0.08,
            end=text_encoder[0].get_left() + LEFT * 0.08,
            buff=0.04,
            color=MGREY,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        encoder_to_embedding = Arrow(
            start=text_encoder[0].get_right() + RIGHT * 0.06,
            end=embedding_block[0].get_left() + LEFT * 0.06,
            buff=0.04,
            color=BLUE,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )

        noisy_latent = make_card(pixelate_array(add_noise(clean_array, 1.0), pixels=18), height=0.88)
        noisy_latent.move_to(LEFT * 4.35 + DOWN * 0.12)
        noisy_group_label = Tex("noise latent", color=MGREY, font_size=18)
        noisy_group_label.next_to(noisy_latent, DOWN, buff=0.10)

        base_box = make_labeled_box("base", width=1.35, height=1.00, color=BLUE, font_size=22)
        base_box.move_to(LEFT * 2.65 + DOWN * 0.12)

        rough_latent = make_card(rough_latent_array, height=0.88)
        rough_latent.move_to(LEFT * 0.95 + DOWN * 0.12)

        refiner_box = make_labeled_box("refiner", width=1.55, height=1.00, color="#7CB66F", font_size=21)
        refiner_box.move_to(RIGHT * 0.75 + DOWN * 0.12)

        clean_latent = make_card(clean_latent_array, height=0.88)
        clean_latent.move_to(RIGHT * 2.45 + DOWN * 0.12)
        clean_label = Tex("clean latent", color=BLUE, font_size=18)
        clean_math = MathTex(r"z_0", color=BLUE, font_size=22)
        clean_group_label = VGroup(clean_label, clean_math).arrange(RIGHT, buff=0.08)
        clean_group_label.next_to(clean_latent, DOWN, buff=0.10)

        decoder_box = make_labeled_box("VAE\\\\decoder", width=1.45, height=1.00, color="#C77C6E", font_size=18)
        decoder_box.move_to(RIGHT * 4.05 + DOWN * 0.12)

        final_image = make_card(IMAGE_PATH, height=1.18)
        final_image.move_to(RIGHT * 5.85 + DOWN * 0.12)
        final_label = Tex("image", color=INK, font_size=18)
        final_label.next_to(final_image, UP, buff=0.12)

        noise_to_base = Arrow(
            start=noisy_latent.get_right() + RIGHT * 0.06,
            end=base_box[0].get_left() + LEFT * 0.06,
            buff=0.04,
            color=MGREY,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        base_to_rough = Arrow(
            start=base_box[0].get_right() + RIGHT * 0.05,
            end=rough_latent.get_left() + LEFT * 0.05,
            buff=0.04,
            color=MGREY,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        rough_to_refiner = Arrow(
            start=rough_latent.get_right() + RIGHT * 0.06,
            end=refiner_box[0].get_left() + LEFT * 0.06,
            buff=0.04,
            color=MGREY,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        refiner_to_clean = Arrow(
            start=refiner_box[0].get_right() + RIGHT * 0.05,
            end=clean_latent.get_left() + LEFT * 0.05,
            buff=0.04,
            color=BLUE,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        clean_to_decoder = Arrow(
            start=clean_latent.get_right() + RIGHT * 0.06,
            end=decoder_box[0].get_left() + LEFT * 0.06,
            buff=0.04,
            color=MGREY,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        decoder_to_image = Arrow(
            start=decoder_box[0].get_right() + RIGHT * 0.06,
            end=final_image.get_left() + LEFT * 0.06,
            buff=0.04,
            color=MGREY,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        embedding_to_base = Arrow(
            start=embedding_block[0].get_bottom() + DOWN * 0.03 + RIGHT * 0.20,
            end=base_box[0].get_top() + UP * 0.03,
            buff=0.04,
            color=BLUE,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )
        embedding_to_refiner = Arrow(
            start=embedding_block[0].get_bottom() + DOWN * 0.03 + RIGHT * 0.30,
            end=refiner_box[0].get_top() + UP * 0.03,
            buff=0.04,
            color=BLUE,
            stroke_width=2.0,
            tip_shape=StealthTip,
        )

        thesis_caption = Tex("fixed prompt = same semantic concept", color=INK, font_size=24)
        thesis_caption.move_to(DOWN * 1.03 + LEFT * 0.20)
        variation_note = Tex("vary the latent = different exemplar", color=MGREY, font_size=20)
        variation_note.next_to(thesis_caption, DOWN, buff=0.10)
        variation_note.align_to(thesis_caption, LEFT)

        overlay_group = Group(
            dim,
            line,
            reference,
            prompt_group,
            text_encoder,
            embedding_group,
            prompt_to_encoder,
            encoder_to_embedding,
            noisy_latent,
            noisy_group_label,
            base_box,
            rough_latent,
            refiner_box,
            clean_latent,
            clean_group_label,
            decoder_box,
            final_image,
            final_label,
            noise_to_base,
            base_to_rough,
            rough_to_refiner,
            refiner_to_clean,
            clean_to_decoder,
            decoder_to_image,
            embedding_to_base,
            embedding_to_refiner,
            thesis_caption,
            variation_note,
        )

        add_board_state(
            self,
            board,
            n_forward_visible=len(FORWARD_LABELS),
            n_reverse_visible=len(REVERSE_LABELS),
            show_top_highlight=True,
            show_bottom_highlight=True,
        )

        self.play(FadeIn(dim), FadeIn(reference), FadeIn(line, shift=UP * 0.08), run_time=0.7)
        self.play(FadeIn(prompt_group, shift=UP * 0.04), run_time=0.7)
        self.play(
            FadeIn(text_encoder, scale=0.96),
            Create(prompt_to_encoder),
            run_time=0.8,
        )
        self.play(
            Create(encoder_to_embedding),
            FadeIn(embedding_block, scale=0.96),
            FadeIn(embedding_label, shift=UP * 0.03),
            run_time=0.8,
        )
        self.play(
            Create(embedding_to_base),
            Create(embedding_to_refiner),
            run_time=0.8,
        )
        self.play(
            FadeIn(noisy_latent, scale=0.96),
            FadeIn(noisy_group_label, shift=UP * 0.03),
            FadeIn(base_box, scale=0.96),
            Create(noise_to_base),
            run_time=0.8,
        )
        self.play(
            Indicate(base_box[0], color=BLUE, scale_factor=1.02),
            Create(base_to_rough),
            FadeIn(rough_latent, scale=0.96),
            run_time=0.9,
        )
        self.play(
            FadeIn(refiner_box, scale=0.96),
            Create(rough_to_refiner),
            run_time=0.7,
        )
        self.play(
            Indicate(refiner_box[0], color="#7CB66F", scale_factor=1.02),
            Create(refiner_to_clean),
            FadeIn(clean_latent, scale=0.96),
            FadeIn(clean_group_label, shift=UP * 0.03),
            run_time=0.9,
        )
        self.play(
            FadeIn(decoder_box, scale=0.96),
            Create(clean_to_decoder),
            run_time=0.7,
        )
        self.play(
            Indicate(decoder_box[0], color="#C77C6E", scale_factor=1.02),
            Create(decoder_to_image),
            FadeIn(final_image, scale=0.96),
            FadeIn(final_label, shift=UP * 0.03),
            run_time=0.9,
        )
        self.play(
            FadeIn(thesis_caption, shift=UP * 0.03),
            FadeIn(variation_note, shift=UP * 0.03),
            run_time=0.8,
        )
        self.play(
            Indicate(prompt_text, color=BLUE, scale_factor=1.02),
            Indicate(final_image[1], color=BLUE, scale_factor=1.02),
            run_time=0.9,
        )
        self.wait(0.6)
        self.play(FadeOut(overlay_group, shift=DOWN * 0.04), run_time=1.0)
        self.wait(1.0)


class Diffusion05BigPicture(Scene):
    """Final DDPM summary with fixed and learned process contrast."""

    def construct(self) -> None:
        self.camera.background_color = BG

        board = build_board()
        top_note = Tex("fixed forward pass", color=MGREY, font_size=20)
        bottom_note = Tex("learned reverse pass", color=BLUE, font_size=20)
        caption = Tex("Diffusion models learn to reverse noise", color=INK, font_size=30)

        top_note.next_to(board.top_heading, DOWN, buff=0.18)
        top_note.align_to(board.top_heading, LEFT)

        bottom_note.next_to(board.bottom_heading, DOWN, buff=0.18)
        bottom_note.align_to(board.bottom_heading, LEFT)

        caption.to_edge(DOWN, buff=0.42)

        add_board_state(
            self,
            board,
            n_forward_visible=len(FORWARD_LABELS),
            n_reverse_visible=len(REVERSE_LABELS),
            show_top_highlight=True,
            show_bottom_highlight=True,
        )

        self.play(
            FadeIn(top_note, shift=UP * 0.05),
            FadeIn(bottom_note, shift=UP * 0.05),
            run_time=0.8,
        )
        self.play(
            Indicate(board.top_highlight, color=MGREY, scale_factor=1.02),
            Indicate(board.bottom_highlight, color=BLUE, scale_factor=1.02),
            run_time=1.0,
        )
        self.play(FadeIn(caption, shift=UP * 0.08), run_time=0.8)
        self.wait(8.2)
