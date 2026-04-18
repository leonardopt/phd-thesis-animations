"""
Diffusion explainer — thesis defence, 3Blue1Brown style.

  Diffusion01TheIdea          — hook: noise becomes image; forward and reverse passes
  Diffusion02Conditioning     — text prompt controls what emerges; three objects
  Diffusion03ThesisConnection — why diffusion models; stimulus design payoff

Render:
    uv run manim scenes/intro_diffusion_explainer.py Diffusion01TheIdea -ql
    uv run manim scenes/intro_diffusion_explainer.py Diffusion02Conditioning -ql
    uv run manim scenes/intro_diffusion_explainer.py Diffusion03ThesisConnection -ql
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from manim import *

REPO_ROOT = Path(__file__).resolve().parents[2]
_STUDY2_STIM_DIR = REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task"

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#6B7280"
BLUE  = "#2563EB"
GREEN = "#16A34A"
RED   = "#DC2626"
PANEL = "#F8FAFC"

# ── Assets ────────────────────────────────────────────────────────────────────
_STIM = _STUDY2_STIM_DIR

CAT_PATH = _STIM / "ANI-CAT-T00.png"
OBS_PATH = _STIM / "BUI-OBS-T00.png"
PIN_PATH = _STIM / "PLA-PIN-T00.png"

CONTINUUM_PATHS = [
    _STIM / "ANI-CAT-T00.png",
    _STIM / "ANI-CAT-D01.png",
    _STIM / "ANI-CAT-D02.png",
    _STIM / "ANI-CAT-D03.png",
]

# ── Image helpers ─────────────────────────────────────────────────────────────
np.random.seed(42)
_SHARED_NOISE: dict[tuple, np.ndarray] = {}


def _get_noise(shape: tuple) -> np.ndarray:
    if shape not in _SHARED_NOISE:
        n = np.random.normal(0, 1, shape).astype(np.float32)
        _SHARED_NOISE[shape] = (n - n.min()) / (n.max() - n.min())
    return _SHARED_NOISE[shape]


def load_rgb(path: Path | str) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0


def blend(clean: np.ndarray, alpha: float) -> np.ndarray:
    return np.clip((1 - alpha) * clean + alpha * _get_noise(clean.shape), 0, 1)


def to_u8(arr: np.ndarray) -> np.ndarray:
    return (255 * np.clip(arr, 0, 1)).astype(np.uint8)


def imob(src: Path | str | np.ndarray, h: float) -> ImageMobject:
    m = ImageMobject(str(src)) if isinstance(src, (Path, str)) else ImageMobject(to_u8(src))
    return m.scale_to_fit_height(h)


def framed(src: Path | str | np.ndarray, h: float,
           stroke: str = LGREY, sw: float = 1.5) -> Group:
    im = imob(src, h)
    fr = RoundedRectangle(
        width=im.width + 0.14, height=im.height + 0.14,
        corner_radius=0.12, stroke_color=stroke, stroke_width=sw,
    ).set_fill(PANEL, opacity=0).move_to(im)
    return Group(im, fr)


def noise_steps(path: Path | str, n: int) -> list[np.ndarray]:
    """n arrays going from clean to pure noise."""
    clean = load_rgb(path)
    return [blend(clean, float(t) / (n - 1)) for t in range(n)]


def _arrow(start: np.ndarray, end: np.ndarray,
           color: str, sw: float = 1.8) -> Arrow:
    return Arrow(start, end, buff=0.04, color=color,
                 stroke_width=sw, tip_shape=StealthTip)


def _row(arrays: list[np.ndarray], h: float, y: float,
         stroke: str = LGREY) -> tuple[Group, VGroup]:
    """Horizontal strip of framed cards + connecting arrows."""
    n  = len(arrays)
    xs = np.linspace(-5.10, 5.10, n)
    cards = Group(*[
        framed(a, h, stroke).move_to(RIGHT * x + UP * y)
        for a, x in zip(arrays, xs)
    ])
    arrows = VGroup(*[
        _arrow(cards[i].get_right() + RIGHT * 0.04,
               cards[i + 1].get_left() + LEFT * 0.04, stroke)
        for i in range(n - 1)
    ])
    return cards, arrows


# ══════════════════════════════════════════════════════════════════════════════
# Scene 1 — The idea: noise → image; forward and reverse passes
# ══════════════════════════════════════════════════════════════════════════════

class Diffusion01TheIdea(Scene):
    """
    Open on a large noisy image of a cat — then reveal it was generated from
    that very noise by a diffusion model. Build the forward/reverse intuition.
    """

    _LARGE_H = 2.20
    _SMALL_H = 0.88
    _N       = 6         # number of states in each strip

    def construct(self) -> None:
        self.camera.background_color = BG

        cat_clean = load_rgb(CAT_PATH)
        levels    = np.linspace(0.0, 1.0, self._N)
        fwd_arrs  = [blend(cat_clean, float(a)) for a in levels]
        rev_arrs  = list(reversed(fwd_arrs))

        # ── 1. Hook: pure noise filling the frame ─────────────────────────────
        noise_img = imob(fwd_arrs[-1], self._LARGE_H).move_to(UP * 0.15)
        self.play(FadeIn(noise_img), run_time=0.50)
        self.wait(0.30)

        caption = Tex(
            r"What if a neural network could clean this up, one step at a time?",
            color=INK, font_size=26,
        )
        caption.next_to(noise_img, DOWN, buff=0.28)
        self.play(FadeIn(caption, shift=UP * 0.05), run_time=0.55)
        self.wait(0.60)

        # ── 2. Answer: reveal the cat ─────────────────────────────────────────
        cat_img = imob(fwd_arrs[0], self._LARGE_H).move_to(noise_img.get_center())
        self.play(
            FadeOut(noise_img),
            FadeIn(cat_img),
            FadeOut(caption),
            run_time=0.70,
        )
        self.wait(0.25)
        answer = Tex(
            "That is exactly what a diffusion model does.",
            color=INK, font_size=26,
        )
        answer.next_to(cat_img, DOWN, buff=0.28)
        self.play(FadeIn(answer, shift=UP * 0.04), run_time=0.50)
        self.wait(0.45)

        # ── 3. Shrink cat to left anchor; build forward row ───────────────────
        scale_factor = self._SMALL_H / self._LARGE_H
        fwd_y = 0.90

        # Pre-build the whole strip; first card goes where cat currently is
        fwd_cards, fwd_arrows = _row(fwd_arrs, self._SMALL_H, fwd_y)

        self.play(
            FadeOut(answer),
            cat_img.animate.scale(scale_factor).move_to(fwd_cards[0].get_center()),
            run_time=0.55,
        )
        self.remove(cat_img)
        self.add(fwd_cards[0])   # swap in the framed version

        fwd_label = Tex(
            "Forward: add a little noise at each step",
            color=MGREY, font_size=22,
        )
        fwd_formula = MathTex(
            r"q(z_t \mid z_{t-1})",
            color=MGREY, font_size=22,
        )
        fwd_header = VGroup(fwd_label, fwd_formula).arrange(RIGHT, buff=0.28)
        fwd_header.next_to(fwd_cards, UP, buff=0.24)

        self.play(FadeIn(fwd_header), run_time=0.35)
        for i in range(1, self._N):
            self.play(
                Create(fwd_arrows[i - 1]),
                FadeIn(fwd_cards[i], scale=0.96),
                run_time=0.30,
            )
        self.wait(0.20)

        # ── 4. Reverse row ────────────────────────────────────────────────────
        rev_y    = -1.40
        rev_cards, rev_arrows = _row(rev_arrs, self._SMALL_H, rev_y, BLUE)

        rev_label = Tex(
            "Reverse: neural network removes the noise, guided by text",
            color=BLUE, font_size=22,
        )
        rev_formula = MathTex(
            r"p_\theta(z_{t-1} \mid z_t,\, c)",
            color=BLUE, font_size=22,
        )
        rev_header = VGroup(rev_label, rev_formula).arrange(RIGHT, buff=0.28)
        rev_header.next_to(rev_cards, UP, buff=0.24)

        divider = Line(
            LEFT * 6.5 + UP * (fwd_y - self._SMALL_H / 2 - 0.28),
            RIGHT * 6.5 + UP * (fwd_y - self._SMALL_H / 2 - 0.28),
            color=LGREY, stroke_width=1.0,
        )

        c_note = MathTex(r"c = \text{text prompt}", color=BLUE, font_size=20)
        c_note.next_to(rev_cards, DOWN, buff=0.22)

        self.play(Create(divider), FadeIn(rev_header), run_time=0.40)
        for i in range(self._N):
            anims = [FadeIn(rev_cards[i], scale=0.96)]
            if i > 0:
                anims.insert(0, Create(rev_arrows[i - 1]))
            self.play(*anims, run_time=0.30)

        self.play(FadeIn(c_note, shift=UP * 0.04), run_time=0.35)

        clean_box = SurroundingRectangle(
            rev_cards[-1], color=BLUE, stroke_width=2.0, buff=0.06,
        )
        self.play(Create(clean_box), run_time=0.35)
        self.wait(1.20)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 2 — The text prompt c controls what emerges
# ══════════════════════════════════════════════════════════════════════════════

class Diffusion02Conditioning(Scene):
    """
    Same z_T, three different prompts → three different images.
    The mechanism from Scene 1 already showed *how*; this shows *control*.
    Latent space framing added as a brief footnote.
    """

    _IMG_H = 1.60

    _OBJECTS = [
        {"path": CAT_PATH, "prompt": "a cat in an indoor scene",   "color": BLUE},
        {"path": OBS_PATH, "prompt": "an observatory at dusk",     "color": RED},
        {"path": PIN_PATH, "prompt": "a pine tree in a landscape", "color": GREEN},
    ]
    _ROW_YS = [1.50, 0.00, -1.50]

    def construct(self) -> None:
        self.camera.background_color = BG

        heading = Tex(
            r"The text prompt $c$ steers the reverse pass",
            color=INK, font_size=30,
        )
        heading.to_edge(UP, buff=0.38)
        self.play(FadeIn(heading, shift=UP * 0.06), run_time=0.55)

        # ── Shared noise on the left (load once from path, add noise in numpy) ─
        noise_arr = blend(load_rgb(CAT_PATH), 1.0)

        noise_cards = Group(*[
            framed(noise_arr, self._IMG_H)
            .move_to(LEFT * 4.60 + UP * y)
            for y in self._ROW_YS
        ])
        shared_label = Tex(r"same noise $z_T$", color=MGREY, font_size=19)
        shared_label.next_to(noise_cards, LEFT, buff=0.14)

        self.play(
            LaggedStartMap(FadeIn, noise_cards, lag_ratio=0.12),
            FadeIn(shared_label),
            run_time=0.65,
        )
        self.wait(0.20)

        # ── Three text prompts in the centre ──────────────────────────────────
        prompts = [
            Tex(f'"{obj["prompt"]}"', color=obj["color"], font_size=19)
            .move_to(UP * y)
            for obj, y in zip(self._OBJECTS, self._ROW_YS)
        ]
        self.play(
            LaggedStart(*[FadeIn(p, shift=RIGHT * 0.04) for p in prompts],
                        lag_ratio=0.14),
            run_time=0.65,
        )

        # Arrows: noise → prompt
        arrows_in = VGroup(*[
            _arrow(noise_cards[i].get_right() + RIGHT * 0.05,
                   prompts[i].get_left()       + LEFT  * 0.05,
                   obj["color"], sw=1.6)
            for i, obj in enumerate(self._OBJECTS)
        ])
        self.play(LaggedStartMap(Create, arrows_in, lag_ratio=0.12), run_time=0.50)
        self.wait(0.20)

        # ── Clean outputs on the right (loaded from disk, fast) ───────────────
        result_cards = Group(*[
            framed(obj["path"], self._IMG_H, obj["color"])
            .move_to(RIGHT * 4.60 + UP * y)
            for obj, y in zip(self._OBJECTS, self._ROW_YS)
        ])
        arrows_out = VGroup(*[
            _arrow(prompts[i].get_right() + RIGHT * 0.05,
                   result_cards[i].get_left() + LEFT * 0.05,
                   obj["color"], sw=1.6)
            for i, obj in enumerate(self._OBJECTS)
        ])
        self.play(LaggedStartMap(Create, arrows_out, lag_ratio=0.12), run_time=0.50)
        self.play(
            LaggedStartMap(FadeIn, result_cards, lag_ratio=0.12),
            run_time=0.65,
        )

        highlights = VGroup(*[
            SurroundingRectangle(
                result_cards[i], color=obj["color"],
                stroke_width=2.2, buff=0.06,
            )
            for i, obj in enumerate(self._OBJECTS)
        ])
        self.play(LaggedStartMap(Create, highlights, lag_ratio=0.10), run_time=0.50)
        self.wait(0.30)

        # ── Key callouts ──────────────────────────────────────────────────────
        note = Tex(
            r"Same $z_T$, different $c$ $\;\Rightarrow\;$ different image",
            color=INK, font_size=23,
        )
        note.to_edge(DOWN, buff=0.38)
        latent_note = Tex(
            r"All of this runs in a compressed \textit{latent} space"
            r" \textemdash\ 8$\times$ smaller than pixels, but semantically rich.",
            color=MGREY, font_size=19,
        )
        latent_note.next_to(note, UP, buff=0.16)

        self.play(FadeIn(note, shift=UP * 0.04), run_time=0.45)
        self.play(FadeIn(latent_note, shift=UP * 0.03), run_time=0.45)
        self.wait(1.80)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 3 — Why diffusion models for the thesis
# ══════════════════════════════════════════════════════════════════════════════

class Diffusion03ThesisConnection(Scene):
    """
    Three properties map directly onto the experimental needs.
    Payoff: the actual Study 1 continuum — same prompt, varied noise.
    """

    _CARD_H = 1.05
    _CONT_H = 1.42

    def construct(self) -> None:
        self.camera.background_color = BG

        heading = Tex(r"Why latent diffusion for stimulus synthesis?",
                      color=INK, font_size=30)
        heading.to_edge(UP, buff=0.38)
        self.play(FadeIn(heading, shift=UP * 0.06), run_time=0.50)

        # ── Three properties ──────────────────────────────────────────────────
        props = [
            (BLUE,  r"\textbf{Photorealistic}",
             "naturalistic images with ecological validity",
             CAT_PATH),
            (RED,   r"\textbf{Semantically controlled}",
             r"text prompt $=$ category; change prompt $\Rightarrow$ change object",
             OBS_PATH),
            (GREEN, r"\textbf{Parametrically graded}",
             r"same prompt + varied noise $\Rightarrow$ graded stimulus instances",
             PIN_PATH),
        ]
        ys = [1.50, 0.18, -1.14]

        blocks: list[VGroup] = []
        imgs:   list[Group]  = []

        for (col, title_s, body_s, img_path), y in zip(props, ys):
            title_tex = Tex(title_s, color=col,  font_size=22)
            body_tex  = Tex(body_s,  color=INK,  font_size=19)
            blk = VGroup(title_tex, body_tex).arrange(RIGHT, buff=0.22)
            blk.move_to(LEFT * 1.00 + UP * y)
            blocks.append(blk)

            im = framed(img_path, self._CARD_H, col)
            im.move_to(RIGHT * 5.30 + UP * y)
            imgs.append(im)

        for blk, im in zip(blocks, imgs):
            self.play(
                FadeIn(blk, shift=RIGHT * 0.05),
                FadeIn(im, scale=0.94),
                run_time=0.58,
            )
        self.wait(0.50)

        # ── Zoom into property 3: show the continuum ──────────────────────────
        method_line = Tex(
            r"Study 1: fixed prompt, varied noise seed $\Rightarrow$ stimulus continuum",
            color=INK, font_size=23,
        )
        method_line.next_to(heading, DOWN, buff=0.35)

        self.play(
            FadeOut(blocks[0]), FadeOut(blocks[1]),
            FadeOut(imgs[0]),   FadeOut(imgs[1]),
            blocks[2].animate.move_to(UP * 2.60).scale(0.82),
            FadeOut(imgs[2]),
            FadeIn(method_line, shift=UP * 0.04),
            run_time=0.70,
        )

        # Continuum strip
        cont_cards = Group(*[framed(p, self._CONT_H, BLUE) for p in CONTINUUM_PATHS])
        cont_cards.arrange(RIGHT, buff=0.24).move_to(UP * 0.55)

        prompt_lbl = Tex(
            r'prompt: \textit{"a cat in an indoor scene"} (fixed)',
            color=BLUE, font_size=20,
        )
        prompt_lbl.next_to(cont_cards, UP, buff=0.22)

        # Axis under continuum
        dots = VGroup(*[
            Dot(radius=0.045, color=MGREY, fill_opacity=1.0)
            .move_to(c.get_bottom() + DOWN * 0.26)
            for c in cont_cards
        ])
        axis = Line(dots[0].get_center(), dots[-1].get_center(),
                    color=LGREY, stroke_width=2.0)
        axis_lbl = Tex(r"different noise seeds $z_T$", color=MGREY, font_size=18)
        axis_lbl.next_to(axis, DOWN, buff=0.12)

        self.play(FadeIn(prompt_lbl), run_time=0.35)
        self.play(
            LaggedStartMap(FadeIn, cont_cards, lag_ratio=0.14),
            run_time=0.80,
        )
        self.play(Create(axis), FadeIn(dots), FadeIn(axis_lbl), run_time=0.45)

        # Study payoffs
        s1 = VGroup(
            Tex(r"\textbf{Study 1}", color=INK,  font_size=21),
            Tex("perceptual scaling", color=MGREY, font_size=18),
        ).arrange(DOWN, buff=0.04).move_to(cont_cards[1].get_center() + DOWN * 1.50)

        s2 = VGroup(
            Tex(r"\textbf{Study 2}", color=INK,  font_size=21),
            Tex("fMRI decoding",      color=BLUE,  font_size=18),
        ).arrange(DOWN, buff=0.04).move_to(cont_cards[2].get_center() + DOWN * 1.50)

        a1 = _arrow(cont_cards[1].get_bottom() + DOWN * 0.06,
                    s1.get_top() + UP * 0.05, MGREY)
        a2 = _arrow(cont_cards[2].get_bottom() + DOWN * 0.06,
                    s2.get_top() + UP * 0.05, BLUE)

        self.play(
            FadeIn(s1, shift=UP * 0.03), Create(a1),
            FadeIn(s2, shift=UP * 0.03), Create(a2),
            run_time=0.75,
        )

        caption = Tex(
            "Photorealistic. Semantically controlled. Parametrically graded. "
            "Diffusion models were the right tool.",
            color=INK, font_size=21,
        )
        caption.to_edge(DOWN, buff=0.26)
        self.play(FadeIn(caption, shift=UP * 0.04), run_time=0.55)
        self.wait(2.20)
