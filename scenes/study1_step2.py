"""
Study 1, Step 2 — generating exemplars.

Narrative arc:
  1. Fixed prompt appears large — the constant anchor
  2. Prompt shrinks to top-left banner; noise + SDXL + fish appear
  3. Noise/fish swap N_SWAPS× (accelerating) — z_i ~ N(0,I) shown below each noise
  4. Cloud bloom on RIGHT half; LEFT shows prompt + noise set with SDXL arrow

Render:
    uv run manim scenes/study1_step2.py Study1Step2 -qh
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

# ── Image source ───────────────────────────────────────────────────────────────
IMG_DIR = env_path("EXEMPLAR_FISH_DIR")

N_SWAPS = 59          # number of noise/fish swap cycles in Phase 3

# Total wall-clock seconds for all swaps (stays fixed regardless of N_SWAPS)
SWAP_TOTAL_DUR = 10

PROMPT_LINES = [
    r"``award-winning marine photo",
    r"of a colorful fish in a coral reef,",
    r"centered in the scene, vibrant",
    r"underwater scene, high detail''",
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def noise_magma(seed: int, sz: int = 128) -> np.ndarray:
    rng = np.random.default_rng(seed)
    gray = rng.random((sz, sz)).astype(np.float32)
    return (_mcm.magma(gray) * 255).astype(np.uint8)


def cloud_positions(n: int, cx: float, cy: float):
    """
    Ring-based layout centred at (cx, cy) with no random jitter.
    Ring radii and counts are chosen so that both the tangential spacing
    (within a ring) and the radial gap (between rings) are ≥ 0.65,
    comfortably larger than the image height of 0.45.

      ring 0 : r=0.00,  1
      ring 1 : r=0.65,  6  → tangential gap ≈ 0.68
      ring 2 : r=1.30, 12  → tangential gap ≈ 0.68
      ring 3 : r=1.95, 18  → tangential gap ≈ 0.68
      ring 4 : r=2.60, 23  → tangential gap ≈ 0.71   total = 60
    """
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


# ── Scene ──────────────────────────────────────────────────────────────────────

class Study1Step2(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Load all fish images ──────────────────────────────────────────────
        files  = sorted(IMG_DIR.glob("ANI-FIS-*.png"))
        N, SZ  = len(files), 512
        pixels = [
            np.asarray(
                PILImage.open(fp).convert("RGBA").resize((SZ, SZ), PILImage.LANCZOS)
            )
            for fp in files
        ]

        # ══════════════════════════════════════════════════════════════════════
        # Phase 1 — fixed prompt, large and centred
        # ══════════════════════════════════════════════════════════════════════
        p_label = Tex(r"Fixed prompt $p$\,:", color=GREY, font_size=26)
        p_body  = VGroup(*[
            Tex(ln, color=INK, font_size=36) for ln in PROMPT_LINES
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        p_block = VGroup(p_label, p_body).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        p_block.move_to(ORIGIN)

        self.play(FadeIn(p_label, shift=DOWN * 0.06), run_time=0.35)
        self.play(
            LaggedStart(*[FadeIn(ln, shift=DOWN * 0.06) for ln in p_body], lag_ratio=0.18),
            run_time=1.2,
        )
        self.wait(0.55)

        # ── Compact banner: same full prompt, smaller, top-left ───────────────
        b_label = Tex(r"Fixed prompt $p$\,:", color=GREY, font_size=22)
        b_body  = VGroup(*[
            Tex(ln, color=INK, font_size=25) for ln in PROMPT_LINES
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        p_banner = VGroup(b_label, b_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        p_banner.to_corner(UL, buff=0.32)

        self.play(FadeTransform(p_block, p_banner), run_time=0.65)

        # ══════════════════════════════════════════════════════════════════════
        # Phase 2 — first generation appears
        # ══════════════════════════════════════════════════════════════════════
        IMG_H  = 2.6
        CY     = -0.55          # vertical centre for noise / fish / arrow
        NX, FX = -3.1, 3.1

        arrow_mob = Arrow(
            LEFT * 0.85, RIGHT * 0.85,
            buff=0, color=GREY, stroke_width=2.5, tip_length=0.22,
            max_stroke_width_to_length_ratio=20,
        )
        sdxl_tex = Tex(r"\textbf{Stable Diffusion XL}", color=INK, font_size=22)
        sdxl_tex.next_to(arrow_mob, UP, buff=0.16)
        sdxl_grp = VGroup(arrow_mob, sdxl_tex).move_to(UP * CY)

        noise_mob = ImageMobject(noise_magma(seed=3)).set_height(IMG_H)
        noise_mob.move_to(RIGHT * NX + UP * CY)

        # seed label + static N(0,I) distribution label
        seed_lab = MathTex(r"\mathbf{z}_1", color=GREY, font_size=28)
        seed_lab.next_to(noise_mob, DOWN, buff=0.12)
        dist_lab = MathTex(r"\sim \mathcal{N}(\mathbf{0},\, \mathbf{I})", color=GREY, font_size=21)
        dist_lab.next_to(seed_lab, DOWN, buff=0.06)

        seq_idx  = [int(round(i * (N - 1) / N_SWAPS)) for i in range(N_SWAPS + 1)]
        fish_mob = ImageMobject(pixels[seq_idx[0]]).set_height(IMG_H)
        fish_mob.move_to(RIGHT * FX + UP * CY)

        self.play(
            FadeIn(noise_mob, shift=RIGHT * 0.12),
            FadeIn(seed_lab), FadeIn(dist_lab),
            Create(arrow_mob), Write(sdxl_tex),
            FadeIn(fish_mob, shift=LEFT * 0.12, scale=0.95),
            run_time=1.0,
        )
        self.wait(0.65)

        # ══════════════════════════════════════════════════════════════════════
        # Phase 3 — N_SWAPS swaps, accelerating  (dist_lab stays fixed throughout)
        #
        # Timing: geometric weights normalised to SWAP_TOTAL_DUR so the total
        # duration is independent of N_SWAPS.
        # ══════════════════════════════════════════════════════════════════════
        weights    = np.geomspace(1.0, 0.20, N_SWAPS)   # fast → slow ratio = 5×
        swap_times = list(SWAP_TOTAL_DUR * weights / weights.sum())

        for i, (rt, idx) in enumerate(zip(swap_times, seq_idx[1:])):
            new_noise = ImageMobject(noise_magma(seed=(i + 1) * 41 + 7)).set_height(IMG_H)
            new_noise.move_to(RIGHT * NX + UP * CY)
            new_fish  = ImageMobject(pixels[idx]).set_height(IMG_H)
            new_fish.move_to(RIGHT * FX + UP * CY)
            new_seed  = MathTex(rf"\mathbf{{z}}_{{{i + 2}}}", color=GREY, font_size=28)
            new_seed.next_to(new_noise, DOWN, buff=0.12)

            self.play(
                FadeTransform(noise_mob, new_noise),
                FadeTransform(fish_mob,  new_fish),
                FadeTransform(seed_lab,  new_seed),
                run_time=rt,
            )
            noise_mob = new_noise
            fish_mob  = new_fish
            seed_lab  = new_seed

        self.wait(0.4)

        # ══════════════════════════════════════════════════════════════════════
        # Phase 4 — cloud on RIGHT; LEFT shows prompt + noise set + SDXL arrow
        # ══════════════════════════════════════════════════════════════════════
        IMG_CLOUD_H = 0.45
        CLOUD_CX, CLOUD_CY = 4.3, -0.10
        cpos = cloud_positions(N, cx=CLOUD_CX, cy=CLOUD_CY)

        cloud_imgs = [
            ImageMobject(pixels[i]).set_height(IMG_CLOUD_H).move_to(RIGHT * px + UP * py)
            for i, (px, py) in enumerate(cpos[:N])
        ]

        c_title = Tex(
            r"\textbf{60 exemplars} — \textit{fish}",
            color=INK, font_size=24,
        ).move_to(RIGHT * CLOUD_CX + UP * 3.20)

        c_sub = Tex(
            r"Same semantic identity $\cdot$ Perceptually distinct realisations",
            color=GREY, font_size=19,
        ).to_edge(DOWN, buff=0.30)

        # ── Left panel: prompt (moved from banner) + ⊕ + noise set ──────────
        LEFT_CX = -3.8   # horizontal centre of the left panel

        # Re-build the prompt block at its destination (same style as banner)
        fp_label = Tex(r"Fixed prompt $p$\,:", color=GREY, font_size=22)
        fp_body  = VGroup(*[
            Tex(ln, color=INK, font_size=25) for ln in PROMPT_LINES
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        fp_block = VGroup(fp_label, fp_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        fp_block.move_to(RIGHT * LEFT_CX + UP * 1.70)

        # Composition symbol — ⊕ conveys "combined with", not arithmetic addition
        # Kept at y=0 so it sits on the same horizontal as the SDXL arrow
        comp_sym = MathTex(r"\oplus", color=GREY, font_size=52)
        comp_sym.move_to(RIGHT * LEFT_CX + UP * 0.0)

        # Three noise thumbnails + \ldots inside { }
        THUMB_H = 0.75
        thumb_seeds = [3, 44, 85]
        thumbs = [
            ImageMobject(noise_magma(seed=s)).set_height(THUMB_H)
            for s in thumb_seeds
        ]
        dots_tex = MathTex(r"\ldots", color=GREY, font_size=36)

        # Arrange thumbnails + dots in a row
        thumb_row = Group(*thumbs, dots_tex).arrange(RIGHT, buff=0.18)

        # Surrounding braces using plain Tex
        lbrace = MathTex(r"\bigl\{", color=INK, font_size=52)
        rbrace = MathTex(r"\bigr\}", color=INK, font_size=52)
        set_row = Group(lbrace, thumb_row, rbrace).arrange(RIGHT, buff=0.14)
        set_row.move_to(RIGHT * LEFT_CX + UP * -1.10)

        # Brace underneath labelled "60 noise tensors"
        set_brace = Brace(set_row, DOWN, color=GREY, buff=0.08)
        set_brace_lab = MathTex(
            r"60 \text{ noise tensors}", color=GREY, font_size=20
        ).next_to(set_brace, DOWN, buff=0.08)

        # Distribution hint
        dist_note = MathTex(
            r"\mathbf{z}_i \sim \mathcal{N}(\mathbf{0},\,\mathbf{I})",
            color=GREY, font_size=20,
        ).next_to(set_brace_lab, DOWN, buff=0.14)

        # ── SDXL arrow repositioned between left panel and right cloud ────────
        ARR_START = np.array([-0.85, 0.0, 0.0])
        ARR_END   = np.array([ 1.40, 0.0, 0.0])
        new_arrow = Arrow(
            ARR_START, ARR_END,
            buff=0, color=GREY, stroke_width=2.5, tip_length=0.22,
            max_stroke_width_to_length_ratio=20,
        )
        new_sdxl = Tex(r"\textbf{Stable Diffusion XL}", color=INK, font_size=22)
        new_sdxl.next_to(new_arrow, UP, buff=0.16)
        new_sdxl_grp = VGroup(new_arrow, new_sdxl).move_to(ORIGIN)

        # ── Transition: fade out noise/fish; morph banner → prompt block ─────
        self.play(
            FadeOut(noise_mob, seed_lab, dist_lab, fish_mob),
            FadeTransform(p_banner, fp_block),
            FadeTransform(sdxl_grp, new_sdxl_grp),
            run_time=0.65,
        )

        # Noise set appears
        self.play(
            FadeIn(comp_sym, shift=DOWN * 0.06),
            FadeIn(lbrace), FadeIn(rbrace),
            LaggedStart(*[FadeIn(t, scale=0.9) for t in thumbs], lag_ratio=0.15),
            Write(dots_tex),
            run_time=0.9,
        )
        self.play(
            FadeIn(set_brace, set_brace_lab, dist_note, shift=DOWN * 0.04),
            run_time=0.6,
        )
        self.wait(0.3)

        # ── Cloud blooms on the right ─────────────────────────────────────────
        self.play(
            Write(c_title),
            LaggedStart(
                *[FadeIn(m, shift=UP * 0.04) for m in cloud_imgs],
                lag_ratio=0.020,
            ),
            run_time=2.6,
        )
        self.play(Write(c_sub), run_time=0.55)
        self.wait(1.5)
