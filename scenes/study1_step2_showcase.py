"""
Study 1, Step 2 — multi-category showcase.

Each entry in SHOWCASE gets its own named Scene class:
    Showcase_sequoia, Showcase_lake_island, Showcase_observatory, …

Render a single entry:
    uv run manim scenes/study1_step2_showcase.py Showcase_sequoia -qh

Render all at once:
    uv run manim scenes/study1_step2_showcase.py -qh -a

The combined scene Study1Step2Showcase is also available.
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from PIL import Image as PILImage
import matplotlib.cm as _mcm

from manim import *
from scenes.utils import env_path

# ── Palette ────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
GREY  = "#6B7280"
LGREY = "#D1D5DB"

BASE = env_path("EXEMPLAR_IMAGES_DIR")

# ══════════════════════════════════════════════════════════════════════════════
# SHOWCASE — edit this list to change what is shown and in what order.
# ══════════════════════════════════════════════════════════════════════════════
SHOWCASE = [
    dict(
        category="plant", folder="sequoia", glob="PLA-SEQ-*.png",
        label="sequoia",
        prompt_lines=[
            r"``film shot of a majestic Sequoia tree in the centre,",
            r"forest and mountains in the background,",
            r"high resolution photography,",
            r"crisp clear sky''",
        ],
    ),
    dict(
        category="landscape_element", folder="lake_island", glob="LAN-LAK-*.png",
        label="lake island",
        prompt_lines=[
            r"``film shot of a towering rocky lake island in the center,",
            r"hilly meadows on the horizon,",
            r"high resolution photography,",
            r"vibrant natural light''",
        ],
    ),
    dict(
        category="building", folder="observatory", glob="BUI-OBS-*.png",
        label="observatory",
        prompt_lines=[
            r"``film shot of an observatory",
            r"on a remote hilly landscape,",
            r"high resolution photography,",
            r"exploratory, cinematic''",
        ],
    ),
    dict(
        category="vehicle", folder="campervan", glob="VEH-CAM-*.png",
        label="camper van",
        prompt_lines=[
            r"``photo of a solitary vintage camper van",
            r"in a countryside camping spot,",
            r"mountains in the background,",
            r"high resolution photography, cinematic''",
        ],
    ),
    dict(
        category="item", folder="sofa", glob="ITE-SOF-*.png",
        label="sofa",
        prompt_lines=[
            r"``film shot of an art deco sofa,",
            r"minimalistic background,",
            r"high resolution photography''",
        ],
    ),
]

# ── Layout constants (match Study1Step2 Phase 4) ───────────────────────────────
IMG_CLOUD_H = 0.45
CLOUD_CX    = 4.3
CLOUD_CY    = -0.10
LEFT_CX     = -3.8
THUMB_H     = 0.75

HOLD_TIME   = 1.6


# ── Helpers ────────────────────────────────────────────────────────────────────

def noise_magma(seed: int, sz: int = 128) -> np.ndarray:
    rng = np.random.default_rng(seed)
    gray = rng.random((sz, sz)).astype(np.float32)
    return (_mcm.magma(gray) * 255).astype(np.uint8)


def cloud_positions(n: int, cx: float, cy: float):
    rings = [
        (0.00,  1, 0.00),
        (0.65,  6, 0.00),
        (1.30, 12, 0.26),
        (1.95, 18, 0.00),
        (2.60, 23, 0.14),
    ]
    out, total = [], 0
    for r, n_def, off in rings:
        cnt = min(n_def, n - total)
        if cnt <= 0:
            break
        for k in range(cnt):
            ang = 2 * np.pi * k / max(cnt, 1) + off
            out.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))
        total += cnt
    return out


SZ = 512

def load_pixels(img_dir: Path, glob: str) -> list[np.ndarray]:
    return [
        np.asarray(
            PILImage.open(fp).convert("RGBA").resize((SZ, SZ), PILImage.LANCZOS)
        )
        for fp in sorted(img_dir.glob(glob))
    ]


def make_prompt_block(prompt_lines: list[str], label: str) -> VGroup:
    """Prompt block with labelled subscript: Fixed prompt p(label) :"""
    p_label = Tex(
        rf"Fixed prompt $p(\text{{{label}}})$\,:",
        color=GREY, font_size=22,
    )
    p_body = VGroup(*[
        Tex(ln, color=INK, font_size=25) for ln in prompt_lines
    ]).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
    block = VGroup(p_label, p_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    block.move_to(RIGHT * LEFT_CX + UP * 1.70)
    return block


def make_cloud(pixels: list[np.ndarray]) -> Group:
    N = len(pixels)
    cpos = cloud_positions(N, cx=CLOUD_CX, cy=CLOUD_CY)
    return Group(*[
        ImageMobject(pixels[i]).set_height(IMG_CLOUD_H).move_to(RIGHT * px + UP * py)
        for i, (px, py) in enumerate(cpos[:N])
    ])


def make_title(label: str) -> Tex:
    return Tex(
        rf"\textbf{{60 exemplars}} — \textit{{{label}}}",
        color=INK, font_size=24,
    ).move_to(RIGHT * CLOUD_CX + UP * 3.20)


def make_thumbs(entry_idx: int, positions: list) -> list:
    """Three noise ImageMobjects at pre-computed fixed positions."""
    base = entry_idx * 97 + 3
    return [
        ImageMobject(noise_magma(seed=base + k * 41)).set_height(THUMB_H).move_to(pos)
        for k, pos in enumerate(positions)
    ]


def build_static_frame(scene: Scene) -> list:
    """
    Add the structural frame that never changes (⊕, braces, SDXL arrow, subtitle)
    directly to the scene with no animation.  Returns the list of fixed thumbnail
    slot positions so callers can place ImageMobjects there.
    """
    comp_sym = MathTex(r"\oplus", color=GREY, font_size=52)
    comp_sym.move_to(RIGHT * LEFT_CX)

    # Dummy thumbs just to fix geometry / slot positions
    _dummy = [ImageMobject(noise_magma(seed=0)).set_height(THUMB_H) for _ in range(3)]
    dots_tex  = MathTex(r"\ldots", color=GREY, font_size=36)
    thumb_row = Group(*_dummy, dots_tex).arrange(RIGHT, buff=0.18)
    lbrace    = MathTex(r"\bigl\{", color=INK, font_size=52)
    rbrace    = MathTex(r"\bigr\}", color=INK, font_size=52)
    set_row   = Group(lbrace, thumb_row, rbrace).arrange(RIGHT, buff=0.14)
    set_row.move_to(RIGHT * LEFT_CX + UP * -1.10)
    thumb_positions = [d.get_center().copy() for d in _dummy]

    set_brace = Brace(set_row, DOWN, color=GREY, buff=0.08)
    set_brace_lab = MathTex(
        r"60 \text{ noise tensors}", color=GREY, font_size=20
    ).next_to(set_brace, DOWN, buff=0.08)
    dist_note = MathTex(
        r"\mathbf{z}_i \sim \mathcal{N}(\mathbf{0},\,\mathbf{I})",
        color=GREY, font_size=20,
    ).next_to(set_brace_lab, DOWN, buff=0.14)

    sdxl_arrow = Arrow(
        np.array([-0.85, 0.0, 0.0]), np.array([1.40, 0.0, 0.0]),
        buff=0, color=GREY, stroke_width=2.5, tip_length=0.22,
        max_stroke_width_to_length_ratio=20,
    )
    sdxl_tex = Tex(r"\textbf{Stable Diffusion XL}", color=INK, font_size=22)
    sdxl_tex.next_to(sdxl_arrow, UP, buff=0.16)
    sdxl_grp = VGroup(sdxl_arrow, sdxl_tex).move_to(ORIGIN)

    c_sub = Tex(
        r"Same semantic identity $\cdot$ Perceptually distinct realisations",
        color=GREY, font_size=19,
    ).to_edge(DOWN, buff=0.30)

    scene.add(
        comp_sym, lbrace, dots_tex, rbrace,
        set_brace, set_brace_lab, dist_note,
        sdxl_grp, c_sub,
    )
    return thumb_positions


def animate_entry(scene: Scene, entry: dict, pixels: list,
                  thumb_positions: list, entry_idx: int,
                  prev_state: dict | None) -> dict:
    """
    Animate one showcase entry.  If prev_state is None this is the first entry
    (fade in).  Otherwise swap out the previous mobjects.
    Returns the current state dict for the next call.
    """
    fp_block  = make_prompt_block(entry["prompt_lines"], entry["label"])
    thumbs    = make_thumbs(entry_idx, thumb_positions)
    cloud_grp = make_cloud(pixels)
    c_title   = make_title(entry["label"])

    if prev_state is None:
        scene.play(
            FadeIn(fp_block, shift=DOWN * 0.06),
            *[FadeIn(t, scale=0.9) for t in thumbs],
            run_time=0.50,
        )
        scene.play(
            Write(c_title),
            LaggedStart(
                *[FadeIn(m, shift=UP * 0.04) for m in cloud_grp],
                lag_ratio=0.020,
            ),
            run_time=2.0,
        )
    else:
        scene.play(
            FadeTransform(prev_state["fp_block"], fp_block),
            FadeTransform(prev_state["c_title"],  c_title),
            *[FadeOut(t) for t in prev_state["thumbs"]],
            FadeOut(prev_state["cloud_grp"]),
            run_time=0.50,
        )
        scene.play(
            *[FadeIn(t, scale=0.9) for t in thumbs],
            LaggedStart(
                *[FadeIn(m, shift=UP * 0.04) for m in cloud_grp],
                lag_ratio=0.020,
            ),
            run_time=1.8,
        )

    scene.wait(HOLD_TIME)
    return dict(fp_block=fp_block, thumbs=thumbs,
                cloud_grp=cloud_grp, c_title=c_title)


# ══════════════════════════════════════════════════════════════════════════════
# Individual per-entry scenes  (Showcase_sequoia, Showcase_lake_island, …)
# ══════════════════════════════════════════════════════════════════════════════

def _make_single_scene(idx: int) -> type:
    entry = SHOWCASE[idx]

    class _S(Scene):
        def construct(self_):
            self_.camera.background_color = BG
            pixels = load_pixels(
                BASE / entry["category"] / entry["folder"], entry["glob"]
            )
            thumb_pos = build_static_frame(self_)
            animate_entry(self_, entry, pixels, thumb_pos, idx, None)

    name = f"Showcase_{entry['folder']}"
    _S.__name__ = name
    _S.__qualname__ = name
    return _S


for _i, _e in enumerate(SHOWCASE):
    globals()[f"Showcase_{_e['folder']}"] = _make_single_scene(_i)


# ══════════════════════════════════════════════════════════════════════════════
# Combined scene — all entries in sequence
# ══════════════════════════════════════════════════════════════════════════════

class Study1Step2Showcase(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        all_pixels = [
            load_pixels(BASE / e["category"] / e["folder"], e["glob"])
            for e in SHOWCASE
        ]

        thumb_pos = build_static_frame(self)

        state = None
        for i, (entry, pixels) in enumerate(zip(SHOWCASE, all_pixels)):
            state = animate_entry(self, entry, pixels, thumb_pos, i, state)
