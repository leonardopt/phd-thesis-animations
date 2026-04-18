"""
Slide clip: SLERP interpolation – 3-D version.

Left panel  : 3-D coordinate space (thin VMobject arrows + XY grid) with
              anchor (z₀) and guide (z₁) vectors; each tip carries a small
              image thumbnail.  Amber z_α vector sweeps the great-circle arc.
Right panel : generated fish image updating in lock-step (2-D overlay).

Note: all vectors use thin VMobject Arrow (not Arrow3D) so that always_redraw
on the animated z_α is fast (~50 ms/frame instead of ~1 s/frame).

Render:
    uv run manim scenes/study1_step4.py Study1Step4Detailed -qh
    uv run manim scenes/study1_step4.py Study1Step4Setup -qh -o study1_step4_setup.mp4
    uv run manim scenes/study1_step4.py Study1Step4Interpolation -qh -o study1_step4_interpolation.mp4
    uv run manim scenes/study1_step4.py Study1Step4 -qh -o study1_step4.mp4
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from PIL import Image as PILImage

from manim import *
from utils import REPO_ROOT, env_path

# ── Palette ────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
C_Z0  = "#2563EB"
C_Z1  = "#DC2626"
C_ZA  = "#D97706"
C_ARC = "#93C5FD"

# ── Image source ───────────────────────────────────────────────────────────────
IMG_DIR = env_path(
    "FISH_INTERPOLATIONS_DIR",
    env_path(
        "INTERPOLATIONS_DIR",
        REPO_ROOT / "assets" / "images" / "study1" / "fish_interpolations",
    ),
)

PROMPT = r"\textit{``a fish swimming in the ocean''}"
PROMPT_BOX_LINES = (
    "\"award-winning marine photo",
    "of a colorful fish",
    "in a coral reef,",
    "centered in the scene,",
    "vibrant underwater scene,",
    "high detail\"",
)
COMPACT_PROMPT_LINES = (
    r"``award-winning marine photo",
    r"of a colorful fish in a coral reef,",
    r"centered in the scene,",
    r"vibrant underwater scene,",
    r"high detail''",
)


def slerp(u: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
    cos_t = float(np.clip(np.dot(u, v), -1.0, 1.0))
    theta = np.arccos(cos_t)
    if abs(np.sin(theta)) < 1e-8:
        return (1 - t) * u + t * v
    return (np.sin((1 - t) * theta) * u + np.sin(t * theta) * v) / np.sin(theta)


def vec3(start, end, color, sw=3.5, tl=0.18) -> Arrow:
    """Thin VMobject arrow in 3-D space (fast to create, projects correctly)."""
    return Arrow(
        np.asarray(start, dtype=float),
        np.asarray(end,   dtype=float),
        color=color,
        stroke_width=sw,
        tip_length=tl,
        buff=0,
        max_stroke_width_to_length_ratio=100,
    )


def load_interpolation_pixels() -> tuple[np.ndarray, int]:
    files = sorted(IMG_DIR.glob("ANI-FIS-interpol-*.png"))
    if not files:
        raise FileNotFoundError(
            "No interpolation frames found for Study 1 Step 4. "
            f"Looked in {IMG_DIR} for files matching 'ANI-FIS-interpol-*.png'. "
            "Set FISH_INTERPOLATIONS_DIR in .env to the directory containing the fish interpolation frames."
        )
    N, SZ = len(files), 512
    pixels = np.empty((N, SZ, SZ, 4), dtype=np.uint8)
    for i, fp in enumerate(files):
        pixels[i] = np.asarray(
            PILImage.open(fp).convert("RGBA").resize((SZ, SZ), PILImage.LANCZOS)
        )
    return pixels, N


class Study1Step4Detailed(ThreeDScene):
    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Layout controls ───────────────────────────────────────────────────
        # Edit these anchors/offsets to reposition the three main blocks.
        #
        # Example preset:
        # LEFT_BLOCK_CENTER  = np.array([2.0, 0.15, 0.0])
        # MID_BLOCK_SHIFT    = UP * 0.80
        # RIGHT_BLOCK_CENTER = RIGHT * 6.60 + MID_BLOCK_SHIFT
        # MID_ARROW_CENTER_X = 4.45
        # MID_ARROW_HALF_LEN = 0.45
        # PROGRESS_Y         = -3.2
        #
        # Current preset:
        LEFT_BLOCK_CENTER  = np.array([2.3, 0.0, 0.0])
        MID_BLOCK_SHIFT    = UP * 0.55
        RIGHT_BLOCK_CENTER = RIGHT * 6.15 + MID_BLOCK_SHIFT
        MID_ARROW_CENTER_X = 4.15
        MID_ARROW_HALF_LEN = 0.50
        PROGRESS_Y         = -3.5
        PANEL_TITLE_CORNER = UL
        PANEL_TITLE_BUFF   = 0.45

        AXIS_LABEL_OFFSET = 0.30
        Z0_THUMB_DIST = 0.98
        Z0_LABEL_EXTRA = 0.34
        Z1_THUMB_OFFSET_EXTRA = np.array([0.05, 0.0, 0.16])
        Z1_LABEL_OFFSET_XYZ = np.array([0.0, 0.02, 0.30])
        ZA_LABEL_SCALE = 1.28

        # ── 1. Load frames ────────────────────────────────────────────────────
        pixels, N = load_interpolation_pixels()

        # ── 2. Camera ─────────────────────────────────────────────────────────
        self.set_camera_orientation(
            phi=65 * DEGREES,
            theta=-45 * DEGREES,
            frame_center=LEFT_BLOCK_CENTER,
        )

        # ── 3. XY ground grid ─────────────────────────────────────────────────
        GRID_R, STEP = 2.2, 0.5
        grid_lines = VGroup(*[
            line
            for k in np.arange(-GRID_R, GRID_R + STEP * 0.5, STEP)
            for line in (
                Line(np.array([k, -GRID_R, 0.0]), np.array([k,  GRID_R, 0.0]),
                     color=LGREY, stroke_width=0.9),
                Line(np.array([-GRID_R, k, 0.0]), np.array([GRID_R, k, 0.0]),
                     color=LGREY, stroke_width=0.9),
            )
        ])

        # ── 4. Coordinate axes (thin VMobject arrows) ─────────────────────────
        L = 3.0
        ax_x = vec3(ORIGIN, [L, 0, 0], MGREY, sw=2.2, tl=0.18)
        ax_y = vec3(ORIGIN, [0, L, 0], MGREY, sw=2.2, tl=0.18)
        ax_z = vec3(ORIGIN, [0, 0, L], MGREY, sw=2.2, tl=0.18)

        FS = 28
        lab_x = MathTex(r"x", color=MGREY, font_size=FS).move_to(np.array([L + AXIS_LABEL_OFFSET, 0.0, 0.0]))
        lab_y = MathTex(r"y", color=MGREY, font_size=FS).move_to(np.array([0.0, L + AXIS_LABEL_OFFSET, 0.0]))
        lab_z = MathTex(r"z", color=MGREY, font_size=FS).move_to(np.array([0.0, 0.0, L + AXIS_LABEL_OFFSET]))

        # ── 5. Data vectors ───────────────────────────────────────────────────
        # Both in upper positive quadrant, exactly 60° apart:
        #   normalize(0.2, 0.2, 1.0) · normalize(1.0, 0.5, 0.3) ≈ cos(60°) = 0.5
        R = 1.7
        z0_dir = np.array([0.52, -0.18, 1.00]);  z0_dir /= np.linalg.norm(z0_dir)
        z1_dir = np.array([1.00, 0.50, 0.30]);  z1_dir /= np.linalg.norm(z1_dir)
        tip0, tip1 = R * z0_dir, R * z1_dir

        vec_z0 = vec3(ORIGIN, tip0, C_Z0, sw=4.0, tl=0.22)
        vec_z1 = vec3(ORIGIN, tip1, C_Z1, sw=4.0, tl=0.22)

        # ── 6. SLERP arc ──────────────────────────────────────────────────────
        arc_3d = ParametricFunction(
            lambda t: R * slerp(z0_dir, z1_dir, t),
            t_range=[0.0, 1.0, 0.005],
            color=C_ARC,
            stroke_width=4,
        )

        # ── 7. Image thumbnails at tips (fixed orientation = face camera) ─────
        THUMB_H = 0.85
        z0_label_dist = Z0_THUMB_DIST + THUMB_H / 2 + Z0_LABEL_EXTRA
        z1_thumb_offset = np.array([THUMB_H / 2, THUMB_H / 2, 0.0]) + Z1_THUMB_OFFSET_EXTRA
        z1_label_offset = np.array([0.0, 0.0, THUMB_H / 2]) + Z1_LABEL_OFFSET_XYZ

        thumb0  = ImageMobject(pixels[0]).set_height(THUMB_H).move_to(tip0 + z0_dir * Z0_THUMB_DIST)
        border0 = SurroundingRectangle(thumb0, color=C_Z0, stroke_width=2.5, buff=0.03)
        # Place the z1 image so the vector tip lands on its lower-left corner.
        thumb1  = ImageMobject(pixels[-1]).set_height(THUMB_H).move_to(tip1 + z1_thumb_offset)
        border1 = SurroundingRectangle(thumb1, color=C_Z1, stroke_width=2.5, buff=0.03)

        lab_z0_3d = MathTex(
            r"\mathbf{z}_0", r"\text{(anchor)}", color=C_Z0, font_size=30
        ).arrange(DOWN, buff=0.06).move_to(
            tip0 + z0_dir * z0_label_dist
        )
        lab_z1_3d = MathTex(
            r"\mathbf{z}_1", r"\text{(guide)}", color=C_Z1, font_size=30
        ).arrange(DOWN, buff=0.06).move_to(
            thumb1.get_center() + z1_label_offset
        )
        # ── 8. Alpha tracker + animated z_α (fast VMobject arrow) ─────────────
        alpha = ValueTracker(0.0)

        # Use always_redraw with vec3() — creating a VMobject Arrow is ~50 ms vs
        # ~1 s for Arrow3D, so 600-frame render completes in ~30 s instead of 10 min.
        vec_za = always_redraw(lambda: vec3(
            ORIGIN,
            R * slerp(z0_dir, z1_dir, alpha.get_value()),
            C_ZA, sw=4.0, tl=0.22,
        ))

        # z_α label (fixed orientation, tracks tip)
        lab_za_3d = MathTex(r"\mathbf{z}_\alpha", color=C_ZA, font_size=36)
        lab_za_3d.move_to(R * slerp(z0_dir, z1_dir, 0.0) * ZA_LABEL_SCALE)
        lab_za_3d.add_updater(
            lambda mob: mob.move_to(
                R * slerp(z0_dir, z1_dir, alpha.get_value()) * ZA_LABEL_SCALE
            )
        )
        # ── 9. 2-D fixed-in-frame overlay (right panel) ───────────────────────
        IMG_H   = 3.0
        img_display = ImageMobject(pixels[0]).set_height(IMG_H).move_to(RIGHT_BLOCK_CENTER)

        def upd_img(mob):
            idx = int(round(alpha.get_value() * (N - 1)))
            mob.become(
                ImageMobject(pixels[np.clip(idx, 0, N - 1)])
                .set_height(IMG_H).move_to(RIGHT_BLOCK_CENTER)
            )

        img_display.add_updater(upd_img)

        img_frame  = SurroundingRectangle(img_display, color=LGREY, stroke_width=1.5, buff=0.03)
        title_img  = Tex(r"\textit{Generated image}", color=INK, font_size=24).next_to(img_frame, UP, buff=0.20)

        # Keep a visible gap between the denoising arrow and the generated image.
        arrow_dn = Arrow(
                         RIGHT * (MID_ARROW_CENTER_X - MID_ARROW_HALF_LEN) + MID_BLOCK_SHIFT,
                         RIGHT * (MID_ARROW_CENTER_X + MID_ARROW_HALF_LEN) + MID_BLOCK_SHIFT,
                         buff=0, color=MGREY, stroke_width=2.5, tip_length=0.22)
        lab_fn   = MathTex(r"f_\theta(\mathbf{z}_\alpha)",
                           color=INK, font_size=24).next_to(arrow_dn, UP, buff=0.14)

        # Progress bar centred at same x as the denoising arrow
        BW, BY, BAR_CX = 4.6, PROGRESS_Y, MID_ARROW_CENTER_X
        bl     = RIGHT * (BAR_CX - BW / 2) + DOWN * abs(BY)
        bar_bg = Line(bl, bl + RIGHT * BW, color=LGREY, stroke_width=4)
        lab_al0 = MathTex(r"\alpha=0", color=MGREY, font_size=24).next_to(bar_bg, LEFT,  buff=0.1)
        lab_al1 = MathTex(r"\alpha=1", color=MGREY, font_size=24).next_to(bar_bg, RIGHT, buff=0.1)

        bar_fill = always_redraw(lambda: Line(
            bl, bl + RIGHT * (alpha.get_value() * BW), color=C_ZA, stroke_width=4
        ))

        slerp_eq = MathTex(
            r"\mathbf{z}_\alpha"
            r"= \dfrac{\sin((1-\alpha)\theta)}{\sin\theta}\;\mathbf{z}_0"
            r"+ \dfrac{\sin(\alpha\theta)}{\sin\theta}\;\mathbf{z}_1",
            color=INK, font_size=24,
        ).next_to(bar_bg, UP, buff=0.26)

        panel_title = Tex(
            r"\textit{Noise latent space} ($\mathbb{R}^n$)",
            color=INK, font_size=26,
        ).to_corner(PANEL_TITLE_CORNER, buff=PANEL_TITLE_BUFF)

        # ── 10. Animation ─────────────────────────────────────────────────────
        self.play(Create(grid_lines), run_time=0.7)
        self.add_fixed_orientation_mobjects(lab_x, lab_y, lab_z)
        self.play(
            Create(ax_x), Create(ax_y), Create(ax_z),
            Write(lab_x), Write(lab_y), Write(lab_z),
            run_time=0.9,
        )
        self.add_fixed_orientation_mobjects(
            thumb0, border0, lab_z0_3d,
            thumb1, border1, lab_z1_3d,
        )
        self.add_fixed_in_frame_mobjects(slerp_eq)
        self.play(
            Create(vec_z0),
            FadeIn(thumb0), FadeIn(border0), Write(lab_z0_3d),
            Create(vec_z1),
            FadeIn(thumb1), FadeIn(border1), Write(lab_z1_3d),
            Write(slerp_eq),
            run_time=1.2,
        )
        self.add_fixed_in_frame_mobjects(panel_title, arrow_dn, lab_fn)
        self.add_fixed_orientation_mobjects(lab_za_3d)
        self.play(
            Write(panel_title),
            Create(arc_3d), FadeIn(vec_za), FadeIn(lab_za_3d),
            Create(arrow_dn), Write(lab_fn),
            run_time=1.0,
        )
        self.wait(0.3)

        # ── Main sweep α: 0 → 1 ──────────────────────────────────────────────
        self.add_fixed_in_frame_mobjects(
            img_display, img_frame, title_img,
            bar_bg, lab_al0, lab_al1, bar_fill,
        )
        self.play(
            FadeIn(img_display), FadeIn(img_frame), Write(title_img),
            FadeIn(bar_bg), FadeIn(bar_fill), Write(lab_al0), Write(lab_al1),
            alpha.animate.set_value(1.0),
            run_time=10.0,
            rate_func=linear,
        )
        self.wait(0.8)


class _Study1Step4CompactBase(ThreeDScene):
    def build_common_state(self) -> dict[str, object]:
        self.camera.background_color = BG

        pixels, N = load_interpolation_pixels()

        self.set_camera_orientation(
            phi=62 * DEGREES,
            theta=-42 * DEGREES,
            frame_center=np.array([0.35, 0.2, 0.0]),
        )

        STEP = 0.5
        L_XY, L_Z = 4.8, 3.95
        GRID_R = L_XY * 0.9
        grid_lines = VGroup(*[
            line
            for k in np.arange(-GRID_R, GRID_R + STEP * 0.5, STEP)
            for line in (
                Line(np.array([k, -GRID_R, 0.0]), np.array([k, GRID_R, 0.0]),
                     color=LGREY, stroke_width=0.9),
                Line(np.array([-GRID_R, k, 0.0]), np.array([GRID_R, k, 0.0]),
                     color=LGREY, stroke_width=0.9),
            )
        ])

        ax_x = vec3(ORIGIN, [L_XY, 0, 0], MGREY, sw=2.4, tl=0.24)
        ax_y = vec3(ORIGIN, [0, L_XY, 0], MGREY, sw=2.4, tl=0.24)
        ax_z = vec3(ORIGIN, [0, 0, L_Z], MGREY, sw=2.4, tl=0.24)

        lab_x = MathTex(r"x", color=MGREY, font_size=30).move_to(np.array([L_XY + 0.32, 0.0, 0.0]))
        lab_y = MathTex(r"y", color=MGREY, font_size=30).move_to(np.array([0.0, L_XY + 0.32, 0.0]))
        lab_z = MathTex(r"z", color=MGREY, font_size=30).move_to(np.array([0.18, 0.18, L_Z - 0.08]))

        R = 2.85
        # anchor: halfway between z and y, guide: halfway between y and x
        z0_dir = np.array([0.0, 1.0, 1.0]); z0_dir /= np.linalg.norm(z0_dir)
        z1_dir = np.array([1.0, 1.0, 0.0]); z1_dir /= np.linalg.norm(z1_dir)
        tip0, tip1 = R * z0_dir, R * z1_dir

        vec_z0 = vec3(ORIGIN, tip0, C_Z0, sw=4.2, tl=0.28)
        vec_z1 = vec3(ORIGIN, tip1, C_Z1, sw=4.2, tl=0.28)
        arc_3d = ParametricFunction(
            lambda t: R * slerp(z0_dir, z1_dir, t),
            t_range=[0.0, 1.0, 0.005],
            color=C_ARC,
            stroke_width=4,
        )

        thumb_h = 0.95
        thumb0 = ImageMobject(pixels[0]).set_height(thumb_h).move_to(tip0 + z0_dir * 0.92)
        border0 = SurroundingRectangle(thumb0, color=C_Z0, stroke_width=2.5, buff=0.03)
        thumb1_offset = np.array([thumb_h / 2 + 0.05, thumb_h / 2, 0.16])
        thumb1 = ImageMobject(pixels[-1]).set_height(thumb_h).move_to(tip1 + thumb1_offset)
        border1 = SurroundingRectangle(thumb1, color=C_Z1, stroke_width=2.5, buff=0.03)

        lab_z0 = Tex(r"\text{anchor}", color=C_Z0, font_size=30)
        lab_z0.move_to(thumb0.get_center() + np.array([0.0, 0.0, thumb_h / 2 + 0.26]))
        lab_z0.set_z_index(10)
        lab_z1 = Tex(r"\text{guide}", color=C_Z1, font_size=30)
        lab_z1.set_z_index(10)
        lab_z1.move_to(thumb1.get_center() + np.array([0.0, 0.0, -(thumb_h / 2 + 0.28)]))

        alpha = ValueTracker(0.0)
        vec_za = always_redraw(lambda: vec3(
            ORIGIN,
            R * slerp(z0_dir, z1_dir, alpha.get_value()),
            C_ZA, sw=4.2, tl=0.28,
        ))
        lab_za = MathTex(r"\mathbf{z}_\alpha", color=C_ZA, font_size=36)
        lab_za.add_updater(
            lambda mob: mob.move_to(R * slerp(z0_dir, z1_dir, alpha.get_value()) * 1.30)
        )

        follow_start_offset = thumb0.get_center() - tip0
        follow_end_offset = thumb1.get_center() - tip1

        def follow_center(t: float) -> np.ndarray:
            tip = R * slerp(z0_dir, z1_dir, t)
            offset = (1 - t) * follow_start_offset + t * follow_end_offset
            return tip + offset

        img_follow = ImageMobject(pixels[0]).set_height(thumb_h)
        img_follow.add_updater(lambda mob: mob.become(
            ImageMobject(pixels[np.clip(int(round(alpha.get_value() * (N - 1))), 0, N - 1)])
            .set_height(thumb_h)
            .move_to(follow_center(alpha.get_value()))
        ))
        img_follow.move_to(follow_center(0.0))
        img_follow_border = always_redraw(lambda: SurroundingRectangle(
            img_follow, color=C_ZA, stroke_width=2.5, buff=0.03
        ))

        # Title positioned above the axes (in screen space, shifted right from UL corner)
        scene_title = Tex(
            r"\textit{Noise latent space} ($\mathbb{R}^n$)", color=INK, font_size=24
        ).to_corner(UL, buff=0.45).shift(RIGHT * 1.8)

        # Prompt box — flat structure, all Tex for consistent Computer Modern font
        prompt_bg = RoundedRectangle(
            corner_radius=0.12, width=3.1, height=2.55,
            stroke_color=LGREY, stroke_width=1.5,
        ).set_fill(WHITE, opacity=0.95).to_corner(UR, buff=0.22)

        p_title = Tex(r"\textbf{Prompt}", color=INK, font_size=21)
        p_lines = VGroup(*[
            Tex(line, color=BLACK, font_size=17)
            for line in COMPACT_PROMPT_LINES
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        VGroup(p_title, p_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(
            prompt_bg.get_center()
        )

        return {
            "alpha": alpha,
            "grid_lines": grid_lines,
            "ax_x": ax_x,
            "ax_y": ax_y,
            "ax_z": ax_z,
            "lab_x": lab_x,
            "lab_y": lab_y,
            "lab_z": lab_z,
            "vec_z0": vec_z0,
            "vec_z1": vec_z1,
            "thumb0": thumb0,
            "border0": border0,
            "lab_z0": lab_z0,
            "thumb1": thumb1,
            "border1": border1,
            "lab_z1": lab_z1,
            "scene_title": scene_title,
            "prompt_bg": prompt_bg,
            "p_title": p_title,
            "p_lines": p_lines,
            "arc_3d": arc_3d,
            "vec_za": vec_za,
            "lab_za": lab_za,
            "img_follow": img_follow,
            "img_follow_border": img_follow_border,
        }

    def play_setup_intro(self, state: dict[str, object]) -> None:
        self.play(Create(state["grid_lines"]), run_time=0.8)
        self.add_fixed_orientation_mobjects(
            state["lab_x"], state["lab_y"], state["lab_z"],
        )
        self.add_fixed_in_frame_mobjects(
            state["scene_title"], state["prompt_bg"], state["p_title"], state["p_lines"],
        )
        self.play(
            Create(state["ax_x"]), Create(state["ax_y"]), Create(state["ax_z"]),
            Write(state["lab_x"]), Write(state["lab_y"]), Write(state["lab_z"]),
            Write(state["scene_title"]),
            FadeIn(state["prompt_bg"]), Write(state["p_title"]), Write(state["p_lines"]),
            run_time=1.0,
        )

        self.add_fixed_orientation_mobjects(
            state["thumb0"], state["border0"], state["lab_z0"],
            state["thumb1"], state["border1"], state["lab_z1"],
        )
        self.play(
            Create(state["vec_z0"]),
            FadeIn(state["thumb0"]), FadeIn(state["border0"]), Write(state["lab_z0"]),
            Create(state["vec_z1"]),
            FadeIn(state["thumb1"]), FadeIn(state["border1"]), Write(state["lab_z1"]),
            run_time=1.2,
        )

    def add_setup_static(self, state: dict[str, object]) -> None:
        self.add(
            state["grid_lines"],
            state["ax_x"], state["ax_y"], state["ax_z"],
            state["vec_z0"], state["vec_z1"],
        )
        self.add_fixed_orientation_mobjects(
            state["lab_x"], state["lab_y"], state["lab_z"],
            state["thumb0"], state["border0"], state["lab_z0"],
            state["thumb1"], state["border1"], state["lab_z1"],
        )
        self.add_fixed_in_frame_mobjects(
            state["scene_title"], state["prompt_bg"], state["p_title"], state["p_lines"],
        )
        self.add(
            state["lab_x"], state["lab_y"], state["lab_z"],
            state["thumb0"], state["border0"], state["lab_z0"],
            state["thumb1"], state["border1"], state["lab_z1"],
            state["scene_title"], state["prompt_bg"], state["p_title"], state["p_lines"],
        )

    def play_interpolation(self, state: dict[str, object]) -> None:
        self.add_fixed_orientation_mobjects(
            state["lab_za"], state["img_follow"], state["img_follow_border"],
        )
        self.play(
            Create(state["arc_3d"]),
            FadeIn(state["vec_za"]), FadeIn(state["lab_za"]),
            FadeIn(state["img_follow"]), FadeIn(state["img_follow_border"]),
            run_time=0.9,
        )
        self.wait(0.2)
        self.play(
            state["alpha"].animate.set_value(1.0),
            run_time=10.0,
            rate_func=linear,
        )
        self.wait(0.8)


class Study1Step4Setup(_Study1Step4CompactBase):
    def construct(self) -> None:
        state = self.build_common_state()
        self.play_setup_intro(state)
        self.wait(0.8)


class Study1Step4Interpolation(_Study1Step4CompactBase):
    def construct(self) -> None:
        state = self.build_common_state()
        self.add_setup_static(state)
        self.play_interpolation(state)


class Study1Step4(_Study1Step4CompactBase):
    def construct(self) -> None:
        state = self.build_common_state()
        self.play_setup_intro(state)
        self.play_interpolation(state)
