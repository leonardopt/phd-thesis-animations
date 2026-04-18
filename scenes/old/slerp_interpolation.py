"""
Slide clip: SLERP interpolation between two noise latent tensors.

A rotating vector traces a great-circle arc on the unit hypersphere while the
corresponding generated image updates in lockstep — illustrating how a fixed
text prompt + varying noise latent produces a smooth perceptual continuum.

Render (from the thesis-animations directory):
    uv run manim scenes/slerp_interpolation.py SlerpInterpolation -qh
Output → media/videos/slerp_interpolation/1080p60/SlerpInterpolation.mp4
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from PIL import Image as PILImage

from manim import *
from utils import REPO_ROOT

# ── Colour palette (white background, 3B1B-inspired) ──────────────────────────
BG    = WHITE
INK   = "#1C1C1E"   # near-black for titles / main text
LGREY = "#D1D5DB"   # light grey for borders, circle stroke
MGREY = "#6B7280"   # mid-grey for secondary labels
C_Z0  = "#2563EB"   # anchor vector – deep blue
C_Z1  = "#DC2626"   # guide vector  – deep red
C_ZA  = "#D97706"   # slerp vector  – amber
C_ARC = "#93C5FD"   # great-circle arc – pale blue

# ── Image source ──────────────────────────────────────────────────────────────
IMG_DIR = REPO_ROOT / "assets" / "images" / "study1" / "fish_interpolations"

PROMPT = r"\textit{``a fish swimming in the ocean''}"


class SlerpInterpolation(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        # ── 1. Pre-load all interpolation frames ─────────────────────────────
        files  = sorted(IMG_DIR.glob("ANI-FIS-interpol-*.png"))
        N, SZ  = len(files), 512
        pixels = np.empty((N, SZ, SZ, 4), dtype=np.uint8)
        for i, fp in enumerate(files):
            pixels[i] = np.asarray(
                PILImage.open(fp).convert("RGBA").resize((SZ, SZ), PILImage.LANCZOS)
            )

        # ── 2. Layout constants ───────────────────────────────────────────────
        OC    = np.array([-4.4,  0.0, 0.0])   # sphere origin
        R     = 1.75                            # sphere radius
        IC    = np.array([ 3.9,  0.0, 0.0])   # image centre
        IMG_H = 3.6

        # Angle positions of z₀ and z₁ on the unit circle
        a0 = np.radians(132)    # anchor
        a1 = np.radians(-18)    # guide

        tip0 = OC + R * np.array([np.cos(a0), np.sin(a0), 0.0])
        tip1 = OC + R * np.array([np.cos(a1), np.sin(a1), 0.0])
        mid_ang = (a0 + a1) / 2

        # ── 3. Static mobjects ────────────────────────────────────────────────

        # — Sphere (unit circle cross-section) —
        sphere = Circle(radius=R, color=LGREY, stroke_width=2.0).move_to(OC)
        origin = Dot(OC, radius=0.055, color=INK)

        AKW = dict(
            buff=0,
            stroke_width=3.5,
            tip_length=0.20,
            max_stroke_width_to_length_ratio=25,
        )
        vec_z0 = Arrow(OC, tip0, color=C_Z0, **AKW)
        vec_z1 = Arrow(OC, tip1, color=C_Z1, **AKW)

        lab_z0 = MathTex(r"\mathbf{z}_0", color=C_Z0, font_size=42).next_to(
            tip0, UP + LEFT * 0.4, buff=0.10
        )
        lab_z1 = MathTex(r"\mathbf{z}_1", color=C_Z1, font_size=42).next_to(
            tip1, RIGHT + DOWN * 0.1, buff=0.10
        )

        # Great-circle arc (the SLERP path)
        slerp_arc = Arc(
            radius=R,
            start_angle=a0,
            angle=(a1 - a0),
            arc_center=OC,
            color=C_ARC,
            stroke_width=8,
        )

        # θ indicator
        theta_arc = Arc(
            radius=0.50,
            start_angle=a1,
            angle=(a0 - a1),
            arc_center=OC,
            color=MGREY,
            stroke_width=1.5,
        )
        lab_theta = MathTex(r"\theta", color=MGREY, font_size=28).move_to(
            OC + 0.78 * np.array([np.cos(mid_ang), np.sin(mid_ang), 0.0])
        )

        title_sphere = Tex(
            r"\textit{Noise latent space} ($\mathbb{R}^n$)",
            color=INK,
            font_size=27,
        ).next_to(sphere, UP, buff=0.22)

        # — Denoising arrow —
        ARR_S = np.array([-1.85, 0.0, 0.0])
        ARR_E = np.array([ 1.60, 0.0, 0.0])
        arrow_dn = Arrow(ARR_S, ARR_E, buff=0, color=MGREY,
                         stroke_width=2.5, tip_length=0.24)
        lab_fn = MathTex(
            r"f_\theta(\mathbf{z}_\alpha,\;\textit{prompt})",
            color=INK,
            font_size=28,
        ).next_to(arrow_dn, UP, buff=0.16)
        lab_prompt = Tex(PROMPT, color=MGREY, font_size=20).next_to(
            arrow_dn, DOWN, buff=0.18
        )

        # — Image panel —
        img_mob = ImageMobject(pixels[0])
        img_mob.set_height(IMG_H).move_to(IC)
        img_border = SurroundingRectangle(
            img_mob, color=LGREY, stroke_width=1.5, buff=0.03
        )
        title_image = Tex(
            r"\textit{Generated image}", color=INK, font_size=27
        ).next_to(img_border, UP, buff=0.22)

        # — Alpha progress bar —
        BW, BY = 6.2, -3.45
        bl = np.array([-BW / 2, BY, 0.0])
        br = np.array([ BW / 2, BY, 0.0])
        bar_bg  = Line(bl, br, color=LGREY, stroke_width=4)
        lab_al0 = MathTex(r"\alpha=0", color=MGREY, font_size=25).next_to(
            bar_bg, LEFT, buff=0.12
        )
        lab_al1 = MathTex(r"\alpha=1", color=MGREY, font_size=25).next_to(
            bar_bg, RIGHT, buff=0.12
        )

        # — SLERP formula —
        slerp_eq = MathTex(
            r"\mathbf{z}_\alpha"
            r"= \dfrac{\sin\!\left((1-\alpha)\,\theta\right)}{\sin\theta}\;\mathbf{z}_0"
            r"+ \dfrac{\sin(\alpha\,\theta)}{\sin\theta}\;\mathbf{z}_1",
            color=INK,
            font_size=26,
        ).next_to(bar_bg, UP, buff=0.28)

        # ── 4. Alpha tracker + animated objects ───────────────────────────────
        alpha = ValueTracker(0.0)

        def _ang(a: float) -> float:
            """Linearly interpolate the angle (equivalent to SLERP on the unit circle)."""
            return a0 + a * (a1 - a0)

        def _tip_a(a: float) -> np.ndarray:
            return OC + R * np.array([np.cos(_ang(a)), np.sin(_ang(a)), 0.0])

        vec_a = always_redraw(
            lambda: Arrow(OC, _tip_a(alpha.get_value()), color=C_ZA, **AKW)
        )
        dot_a = always_redraw(
            lambda: Dot(_tip_a(alpha.get_value()), radius=0.11, color=C_ZA)
        )
        lab_a = always_redraw(lambda: MathTex(
            r"\mathbf{z}_\alpha", color=C_ZA, font_size=38
        ).move_to(
            OC + (R + 0.44) * np.array([
                np.cos(_ang(alpha.get_value())),
                np.sin(_ang(alpha.get_value())),
                0.0,
            ])
        ))
        bar_f = always_redraw(lambda: Line(
            bl,
            np.array([-BW / 2 + alpha.get_value() * BW, BY, 0.0]),
            color=C_ZA,
            stroke_width=4,
        ))

        # Swap pixel array each frame — no file I/O after initial load
        def upd_image(mob: ImageMobject) -> None:
            idx = int(round(alpha.get_value() * (N - 1)))
            mob.pixel_array = pixels[np.clip(idx, 0, N - 1)]

        img_mob.add_updater(upd_image)

        # ── 5. Animation ──────────────────────────────────────────────────────

        # Build the latent-space panel
        self.play(Create(sphere), run_time=0.7)
        self.play(
            FadeIn(origin),
            Create(vec_z0), Write(lab_z0),
            Create(vec_z1), Write(lab_z1),
            run_time=1.1,
        )
        self.play(Create(slerp_arc), run_time=0.5)
        self.play(
            Create(theta_arc), Write(lab_theta),
            Write(title_sphere),
            run_time=0.7,
        )

        # Denoising arrow + image panel
        self.play(
            Create(arrow_dn), Write(lab_fn), FadeIn(lab_prompt),
            run_time=0.9,
        )
        self.play(
            FadeIn(img_mob), FadeIn(img_border), Write(title_image),
            run_time=0.8,
        )

        # SLERP formula
        self.play(Write(slerp_eq), run_time=1.2)
        self.wait(0.4)

        # Introduce z_alpha + progress bar
        self.add(vec_a, dot_a, lab_a, bar_f)
        self.play(FadeIn(bar_bg), Write(lab_al0), Write(lab_al1), run_time=0.5)
        self.wait(0.3)

        # ── Main sweep: α 0 → 1 (linear, 10 s = 200 images at 20 fps) ───────
        self.play(
            alpha.animate.set_value(1.0),
            run_time=10.0,
            rate_func=linear,
        )
        self.wait(0.8)
