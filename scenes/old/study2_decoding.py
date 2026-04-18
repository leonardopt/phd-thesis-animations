"""
Study 2 — Decoding (Scene 3, three videos).

  Study2Scene3A  — What is a voxel activity pattern?
  Study2Scene3B  — Training a classifier on Session 2 (perception)
  Study2Scene3C  — Testing on Session 1 (working memory delay) → format shift

Render:
    uv run manim scenes/study2_decoding.py Study2Scene3A -qh
    uv run manim scenes/study2_decoding.py Study2Scene3B -qh
    uv run manim scenes/study2_decoding.py Study2Scene3C -qh
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from manim import *
from utils import REPO_ROOT, env_path

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
BLUE  = "#2563EB"
AMBER = "#D97706"
GREEN = "#16A34A"
RED   = "#DC2626"

STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    Path(__file__).parent.parent / "assets" / "images" / "stimuli_reordered",
)

FMRI_STIM_DIR = REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task"

def stim(name: str, idx: int) -> str:
    return str(STIM_DIR / f"{name}-{idx:02d}.png")

def fmri_stim(name: str) -> str:
    return str(FMRI_STIM_DIR / name)


# ── Shared helper: voxel grid ─────────────────────────────────────────────────

def make_voxel_grid(
    values: np.ndarray,
    cell_size: float = 0.38,
    low_col: str = "#DBEAFE",
    high_col: str = BLUE,
) -> VGroup:
    """Coloured square grid representing a 2-D voxel activation pattern."""
    rows, cols = values.shape
    grid = VGroup()
    for r in range(rows):
        for c in range(cols):
            v = float(values[r, c])
            cell = Square(
                side_length=cell_size,
                stroke_width=1.2,
                stroke_color=LGREY,
            ).set_fill(
                interpolate_color(ManimColor(low_col), ManimColor(high_col), v),
                opacity=1.0,
            )
            cell.move_to(
                RIGHT * c * (cell_size + 0.04)
                + DOWN  * r * (cell_size + 0.04)
            )
            grid.add(cell)
    grid.move_to(ORIGIN)
    return grid


def make_voxel_bar(
    values: np.ndarray,
    bar_w: float = 0.22,
    bar_max_h: float = 1.2,
    color: str = BLUE,
) -> VGroup:
    """Vertical bar chart representing one flattened voxel pattern vector."""
    group = VGroup()
    for i, v in enumerate(values):
        bar = Rectangle(
            width=bar_w,
            height=max(float(v) * bar_max_h, 0.02),
            stroke_width=0,
        ).set_fill(color, opacity=0.85)
        bar.move_to(RIGHT * i * (bar_w + 0.08), aligned_edge=DOWN)
        group.add(bar)
    group.move_to(ORIGIN)
    return group


def make_feature_row(
    values: np.ndarray,
    color: str = BLUE,
    cell_w: float = 0.18,
    cell_h: float | None = None,
    gap: float = 0.055,
) -> VGroup:
    """Horizontal row of voxel-feature cells."""
    if cell_h is None:
        cell_h = cell_w

    group = VGroup()
    mid = (len(values) - 1) / 2
    for i, v in enumerate(values):
        cell = Rectangle(
            width=cell_w,
            height=cell_h,
            stroke_width=0.7,
            stroke_color=LGREY,
        ).set_fill(
            interpolate_color(
                ManimColor(WHITE), ManimColor(color), 0.10 + 0.90 * float(v)
            ),
            opacity=1.0,
        )
        cell.move_to(RIGHT * (i - mid) * (cell_w + gap))
        group.add(cell)
    group.move_to(ORIGIN)
    return group


# ══════════════════════════════════════════════════════════════════════════════
# Scene 3A — What is a voxel activity pattern?
# ══════════════════════════════════════════════════════════════════════════════

class Study2Scene3A(Scene):
    """
    1. Brain outline with V1-V3 ROI circle.
    2. ROI → 4×4 voxel grid, each cell coloured by activation.
    3. Three stimulus images → three distinct patterns side by side.
    4. Key message: pattern, not mean level, encodes identity.
    """

    _PAT = {
        "A": np.array([[0.9,0.2,0.7,0.4],[0.3,0.8,0.1,0.6],[0.5,0.4,0.9,0.2],[0.1,0.7,0.3,0.8]]),
        "B": np.array([[0.2,0.8,0.3,0.9],[0.7,0.1,0.6,0.3],[0.4,0.9,0.2,0.7],[0.8,0.3,0.5,0.1]]),
        "C": np.array([[0.5,0.5,0.8,0.1],[0.9,0.2,0.4,0.7],[0.1,0.6,0.3,0.9],[0.7,0.4,0.8,0.2]]),
        "D": np.array([[0.3,0.9,0.1,0.7],[0.6,0.2,0.8,0.4],[0.9,0.5,0.3,0.7],[0.2,0.8,0.6,0.1]]),
    }
    _IMGS = [
        "ANI-CAT-T00.png",
        "LAN-MOO-D01.png",
        "BUI-MOD-T00.png",
        "PLA-BRI-T00.png",
    ]

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Tex("What does the brain encode?", color=INK, font_size=36)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.9)
        self.wait(0.3)

        # ── Brain (ellipse stand-in) + ROI ────────────────────────────────────
        brain = Ellipse(width=3.2, height=2.6, color=LGREY, stroke_width=2) \
            .set_fill("#F3F4F6", opacity=0.6) \
            .move_to(LEFT * 3.5 + DOWN * 0.3)

        roi = Circle(radius=0.55, color=BLUE, stroke_width=2.5) \
            .set_fill(BLUE, opacity=0.18) \
            .move_to(brain.get_center() + LEFT * 0.45 + DOWN * 0.55)
        roi_lbl = Tex("V1–V3", color=BLUE, font_size=22).next_to(roi, DOWN, buff=0.12)

        self.play(FadeIn(brain), run_time=0.6)
        self.play(Create(roi), Write(roi_lbl), run_time=0.7)
        self.wait(0.3)

        # ── Arrow + single voxel grid ──────────────────────────────────────────
        grid_center = RIGHT * 0.5 + DOWN * 0.3
        zoom_arrow = Arrow(
            roi.get_right(), grid_center + LEFT * 1.4,
            color=MGREY, stroke_width=2, buff=0.1,
        )
        zoom_lbl = Tex("zoom in", color=MGREY, font_size=20) \
            .next_to(zoom_arrow, UP, buff=0.08)

        grid_A = make_voxel_grid(self._PAT["A"], cell_size=0.40).move_to(grid_center)
        grid_lbl = Tex("voxels", color=MGREY, font_size=20) \
            .next_to(grid_A, DOWN, buff=0.14)

        self.play(GrowArrow(zoom_arrow), Write(zoom_lbl), run_time=0.6)
        self.play(FadeIn(grid_A), Write(grid_lbl), run_time=0.7)
        self.wait(0.4)

        pattern_note = Tex(
            r"One image $\;\longrightarrow\;$ one activation pattern",
            color=INK, font_size=24,
        ).next_to(grid_A, RIGHT, buff=0.5)
        self.play(Write(pattern_note), run_time=0.7)
        self.wait(0.8)

        # ── Transition: show 3 images × 3 patterns ────────────────────────────
        self.play(
            FadeOut(brain), FadeOut(roi), FadeOut(roi_lbl),
            FadeOut(zoom_arrow), FadeOut(zoom_lbl),
            FadeOut(grid_A), FadeOut(grid_lbl), FadeOut(pattern_note),
            run_time=0.5,
        )

        subtitle = Tex(
            "Each image produces a distinct spatial pattern",
            color=MGREY, font_size=24,
        ).next_to(title, DOWN, buff=0.18)
        self.play(FadeIn(subtitle), run_time=0.4)

        keys   = ["A", "B", "C", "D"]
        colors = [BLUE, AMBER, GREEN, "#7C3AED"]
        xs     = [-5.4, -1.8, 1.8, 5.4]

        for key, img_name, col, x in zip(keys, self._IMGS, colors, xs):
            img = ImageMobject(fmri_stim(img_name)).set_height(1.4) \
                .move_to(RIGHT * x + UP * 1.1)
            bdr = SurroundingRectangle(img, color=LGREY, stroke_width=1.5, buff=0.04)
            lbl = Tex(f"Image {key}", color=col, font_size=20) \
                .next_to(img, UP, buff=0.10)
            grid = make_voxel_grid(self._PAT[key], cell_size=0.30, high_col=col) \
                .move_to(RIGHT * x + DOWN * 0.92)
            vox_lbl = Tex("voxels", color=MGREY, font_size=17) \
                .next_to(grid, DOWN, buff=0.10)

            self.play(FadeIn(Group(img, bdr)), Write(lbl), run_time=0.4)
            self.play(FadeIn(grid), Write(vox_lbl), run_time=0.5)
            self.wait(0.15)

        # ── Key message ───────────────────────────────────────────────────────
        self.wait(0.4)
        key_msg = Tex(
            r"The \textit{pattern} — not the mean signal — encodes identity",
            color=INK, font_size=24,
        ).to_edge(DOWN, buff=0.4)
        self.play(Write(key_msg), run_time=0.9)
        self.wait(1.5)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 3B — Training a classifier on Session 2 (perception)
# ══════════════════════════════════════════════════════════════════════════════

class Study2Scene3B(Scene):
    """
    Crossvalidated prediction within Session 2:
    previous end state -> concrete samples x features matrix -> leave-one-run-out
    train/test highlighting -> schematic linear SVM plot with support vectors.
    """

    _ROW_COLS = [BLUE, AMBER, GREEN, RED, "#7C3AED", "#0891B2"]
    _BASE_ROWS = [
        np.array([0.90, 0.20, 0.70, 0.30, 0.80, 0.10, 0.50, 0.40, 0.90]),
        np.array([0.25, 0.82, 0.18, 0.74, 0.22, 0.88, 0.30, 0.68, 0.24]),
        np.array([0.58, 0.34, 0.86, 0.18, 0.42, 0.80, 0.16, 0.66, 0.54]),
        np.array([0.84, 0.46, 0.12, 0.70, 0.26, 0.52, 0.92, 0.24, 0.60]),
        np.array([0.20, 0.62, 0.48, 0.86, 0.36, 0.14, 0.74, 0.54, 0.92]),
        np.array([0.76, 0.12, 0.56, 0.28, 0.90, 0.44, 0.18, 0.82, 0.34]),
    ]

    def _row_values(self, base_idx: int, run_idx: int) -> np.ndarray:
        base = self._BASE_ROWS[base_idx % len(self._BASE_ROWS)]
        rolled = np.roll(base, (run_idx + base_idx) % 3)
        jitter = 0.05 * np.sin(np.arange(base.size) * 1.15 + 0.75 * run_idx + 0.35 * base_idx)
        return np.clip(0.84 * base + 0.16 * rolled + jitter, 0.08, 0.98)

    def _matrix_row_centers(self, x: float) -> list[np.ndarray]:
        row_h = 0.082
        row_gap = 0.020
        run_gap = 0.070
        block_h = 4 * row_h + 3 * row_gap
        total_h = 8 * block_h + 7 * run_gap
        top = total_h / 2 - row_h / 2
        centers: list[np.ndarray] = []
        for run_idx in range(8):
            block_top = top - run_idx * (block_h + run_gap)
            for row_idx in range(4):
                centers.append(
                    np.array([x, block_top - row_idx * (row_h + row_gap), 0.0])
                )
        return centers

    def _make_test_points(self, ax: Axes, fold_idx: int) -> VGroup:
        pts = [
            (-1.55 + 0.10 * np.sin(0.8 * fold_idx),  0.74 + 0.08 * np.cos(1.1 * fold_idx), BLUE),
            (-1.20 + 0.12 * np.cos(0.9 * fold_idx), -0.18 + 0.08 * np.sin(1.3 * fold_idx), BLUE),
            ( 1.20 + 0.10 * np.cos(0.7 * fold_idx),  0.52 + 0.10 * np.sin(1.0 * fold_idx), AMBER),
            ( 1.62 + 0.12 * np.sin(1.2 * fold_idx), -0.56 + 0.08 * np.cos(0.85 * fold_idx), AMBER),
        ]
        return VGroup(*[
            Dot(
                ax.c2p(x, y),
                radius=0.085,
                color=col,
                fill_color=WHITE,
                fill_opacity=1.0,
                stroke_width=2.2,
            )
            for x, y, col in pts
        ])

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Start from previous end state ────────────────────────────────────
        title = Tex(r"\textbf{Session 2 :} Perceptual task", color=INK, font_size=30)
        title.to_edge(UP, buff=0.35)
        vector_x = -1.15
        vector_ys = np.linspace(1.45, -1.45, 6)
        visible_vectors = VGroup(*[
            make_feature_row(
                self._row_values(idx, 0),
                color=self._ROW_COLS[idx],
                cell_w=0.17,
                cell_h=0.17,
                gap=0.055,
            ).move_to(np.array([vector_x, y, 0.0]))
            for idx, y in enumerate(vector_ys)
        ])
        vector_label = Tex("Feature vectors", color=MGREY, font_size=24) \
            .next_to(visible_vectors, UP, buff=0.24)

        summary_matrix_x = 3.35
        summary_symbol = MathTex(
            r"\mathbf{X}_{\mathrm{S2}} =",
            color=INK,
            font_size=28,
        )
        summary_matrix = MathTex(
            r"\begin{bmatrix}"
            r"x_{11} & x_{12} & \cdots & x_{1v} \\"
            r"x_{21} & x_{22} & \cdots & x_{2v} \\"
            r"\vdots & \vdots & \ddots & \vdots \\"
            r"x_{n1} & x_{n2} & \cdots & x_{nv}"
            r"\end{bmatrix}",
            color=INK,
            font_size=24,
        )
        summary_group = VGroup(summary_symbol, summary_matrix).arrange(RIGHT, buff=0.18)
        summary_group.move_to(np.array([summary_matrix_x, -0.05, 0.0]))
        summary_title = Tex(
            r"Multivoxel activity patterns\\during perception",
            color=INK,
            font_size=24,
            tex_environment="center",
        ).move_to(np.array([summary_group.get_center()[0], summary_matrix.get_center()[1] + 1.35, 0.0]))
        sample_arrow = DoubleArrow(
            summary_matrix.get_corner(UR) + RIGHT * 0.42 + UP * 0.02,
            summary_matrix.get_corner(DR) + RIGHT * 0.42 + DOWN * 0.02,
            color=INK,
            stroke_width=1.8,
            buff=0.0,
            tip_length=0.12,
        )
        sample_label = MathTex(
            r"\text{samples (object-scenes)}",
            color=INK,
            font_size=18,
        ).rotate(-PI / 2).next_to(sample_arrow, RIGHT, buff=0.10)
        feature_arrow = DoubleArrow(
            summary_matrix.get_corner(DL) + DOWN * 0.36,
            summary_matrix.get_corner(DR) + DOWN * 0.36,
            color=INK,
            stroke_width=1.8,
            buff=0.0,
            tip_length=0.12,
        )
        feature_label = MathTex(
            r"\text{features (voxels)}",
            color=INK,
            font_size=20,
        ).next_to(feature_arrow, DOWN, buff=0.10)

        self.add(
            title,
            visible_vectors,
            vector_label,
            summary_title,
            summary_symbol,
            summary_matrix,
            sample_arrow,
            sample_label,
            feature_arrow,
            feature_label,
        )
        self.wait(0.45)

        # ── Merge vectors into a full 32-row matrix ──────────────────────────
        matrix_x = -3.20
        row_centers = self._matrix_row_centers(matrix_x)
        target_rows = [
            make_feature_row(
                self._row_values(global_idx % len(self._BASE_ROWS), global_idx // 4),
                color=self._ROW_COLS[global_idx % len(self._ROW_COLS)],
                cell_w=0.17,
                cell_h=0.082,
                gap=0.055,
            ).move_to(row_centers[global_idx])
            for global_idx in range(32)
        ]
        run_labels = VGroup(*[
            Tex(f"run {run_idx + 1}", color=MGREY, font_size=16).next_to(
                VGroup(*target_rows[4 * run_idx : 4 * run_idx + 4]),
                LEFT,
                buff=0.18,
            )
            for run_idx in range(8)
        ])
        matrix_body = VGroup(*target_rows)
        left_bracket = MathTex(r"[", color=INK).stretch_to_fit_height(matrix_body.height + 0.24)
        right_bracket = MathTex(r"]", color=INK).stretch_to_fit_height(matrix_body.height + 0.24)
        left_bracket.next_to(matrix_body, LEFT, buff=0.06)
        right_bracket.next_to(matrix_body, RIGHT, buff=0.06)
        summary_symbol_target = MathTex(
            r"\mathbf{X}_{\mathrm{S2}}",
            color=INK,
            font_size=28,
        ).next_to(left_bracket, LEFT, buff=0.22)
        summary_title_target = summary_title.copy().scale(0.86).next_to(
            VGroup(left_bracket, matrix_body, right_bracket), UP, buff=0.20
        )

        self.play(
            summary_title.animate.move_to(summary_title_target.get_center()).scale(0.86),
            summary_symbol.animate.move_to(summary_symbol_target.get_center()),
            FadeTransform(summary_matrix, VGroup(left_bracket, right_bracket)),
            FadeOut(sample_arrow),
            FadeOut(sample_label),
            FadeOut(feature_arrow),
            FadeOut(feature_label),
            FadeOut(vector_label),
            *[
                Transform(visible_vectors[idx], target_rows[idx])
                for idx in range(len(visible_vectors))
            ],
            LaggedStart(
                *[FadeIn(row) for row in target_rows[len(visible_vectors):]],
                lag_ratio=0.03,
            ),
            LaggedStart(*[FadeIn(lbl) for lbl in run_labels], lag_ratio=0.05),
            run_time=1.8,
        )

        matrix_rows = [*visible_vectors, *target_rows[len(visible_vectors):]]
        matrix_shell = VGroup(*matrix_rows, left_bracket, right_bracket)

        # ── Arrow to classifier + SVM schematic plot ─────────────────────────
        svm_box = RoundedRectangle(
            width=2.95,
            height=0.92,
            corner_radius=0.14,
            color=RED,
            stroke_width=2.0,
        ).set_fill("#FEF2F2", opacity=0.82).move_to(np.array([0.35, 0.10, 0.0]))
        svm_label = VGroup(
            Tex("Linear Support Vector", color=RED, font_size=18),
            Tex("Machine Classifier", color=RED, font_size=18),
        ).arrange(DOWN, buff=0.05).move_to(svm_box.get_center())
        data_arrow = Arrow(
            right_bracket.get_right() + RIGHT * 0.18,
            svm_box.get_left() + LEFT * 0.14,
            color=MGREY,
            stroke_width=2.2,
            buff=0.02,
            tip_length=0.16,
        )

        ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=3.0,
            y_length=2.5,
            axis_config={
                "color": LGREY,
                "stroke_width": 1.4,
                "include_ticks": False,
                "tip_shape": StealthTip,
                "tip_length": 0.12,
            },
        ).move_to(np.array([4.55, -0.05, 0.0]))
        boundary = Line(ax.c2p(-0.15, -1.35), ax.c2p(0.95, 1.55), color=RED, stroke_width=2.2)
        margin_1 = DashedLine(ax.c2p(-0.55, -1.25), ax.c2p(0.55, 1.65), color=RED, stroke_width=1.5, dash_length=0.10)
        margin_2 = DashedLine(ax.c2p(0.25, -1.45), ax.c2p(1.35, 1.45), color=RED, stroke_width=1.5, dash_length=0.10)

        train_blue_pts = VGroup(*[
            Dot(ax.c2p(x, y), radius=0.075, color=BLUE, fill_opacity=0.85)
            for x, y in [(-1.85, 0.95), (-1.55, 0.42), (-1.30, -0.10), (-1.72, -0.62), (-0.92, 0.32), (-0.58, -0.28)]
        ])
        train_amber_pts = VGroup(*[
            Dot(ax.c2p(x, y), radius=0.075, color=AMBER, fill_opacity=0.85)
            for x, y in [(1.05, 0.88), (1.44, 0.34), (1.78, -0.12), (1.52, -0.72), (0.84, 0.10), (0.58, -0.48)]
        ])
        support_vectors = VGroup(*[
            Circle(radius=0.12, color=RED, stroke_width=1.8).move_to(pt.get_center())
            for pt in [train_blue_pts[4], train_blue_pts[5], train_amber_pts[4], train_amber_pts[5]]
        ])
        support_label = Tex("support vectors", color=RED, font_size=16) \
            .next_to(ax, DOWN, buff=0.18)
        fold_label = Tex("held-out run 1 / 8", color=INK, font_size=20) \
            .next_to(ax, UP, buff=0.12)
        current_test_pts = self._make_test_points(ax, 0)

        self.play(
            GrowArrow(data_arrow),
            FadeIn(svm_box),
            FadeIn(svm_label),
            Create(ax),
            Create(boundary),
            Create(margin_1),
            Create(margin_2),
            FadeIn(train_blue_pts),
            FadeIn(train_amber_pts),
            FadeIn(support_vectors),
            FadeIn(support_label),
            FadeIn(fold_label),
            FadeIn(current_test_pts),
            run_time=1.15,
        )

        # ── Leave-one-run-out highlight ──────────────────────────────────────
        train_box = SurroundingRectangle(
            matrix_shell,
            color=BLUE,
            stroke_width=1.8,
            buff=0.05,
            corner_radius=0.04,
        ).set_fill(BLUE, opacity=0.04)
        train_box.set_z_index(-1)
        train_label = Tex("training set", color=BLUE, font_size=18) \
            .next_to(train_box, LEFT, buff=0.14).align_to(train_box, UP)
        test_boxes = [
            SurroundingRectangle(
                VGroup(*matrix_rows[4 * run_idx : 4 * run_idx + 4]),
                color=AMBER,
                stroke_width=2.6,
                buff=0.03,
                corner_radius=0.04,
            ).set_fill(AMBER, opacity=0.10)
            for run_idx in range(8)
        ]
        test_labels = [
            Tex("test set", color=AMBER, font_size=18).next_to(box, RIGHT, buff=0.10)
            for box in test_boxes
        ]

        current_test_box = test_boxes[0]
        current_test_label = test_labels[0]
        self.play(
            FadeIn(train_box),
            FadeIn(train_label),
            Create(current_test_box),
            FadeIn(current_test_label),
            run_time=0.5,
        )

        for fold_idx in range(8):
            new_fold_label = Tex(
                f"held-out run {fold_idx + 1} / 8",
                color=INK,
                font_size=20,
            ).move_to(fold_label.get_center())
            new_test_pts = self._make_test_points(ax, fold_idx)

            if fold_idx == 0:
                self.play(
                    Transform(fold_label, new_fold_label),
                    ReplacementTransform(current_test_pts, new_test_pts),
                    Indicate(svm_box, color=RED, scale_factor=1.02),
                    run_time=0.55,
                )
                current_test_pts = new_test_pts
            else:
                self.play(
                    Transform(current_test_box, test_boxes[fold_idx]),
                    Transform(current_test_label, test_labels[fold_idx]),
                    Transform(fold_label, new_fold_label),
                    ReplacementTransform(current_test_pts, new_test_pts),
                    Indicate(svm_box, color=RED, scale_factor=1.02),
                    run_time=0.55,
                )
                current_test_pts = new_test_pts

        self.wait(1.6)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 3C — Testing on Session 1 delay → representational format shift
# ══════════════════════════════════════════════════════════════════════════════

class Study2Scene3C(Scene):
    """
    1. Trial timeline: stimulus → delay → probe.
    2. Stimulus onset: S2 classifier decodes correctly (tick).
    3. Delay: pattern shifts → S2 classifier fails (cross).
    4. S1 classifier trained on delay succeeds.
    5. Conclusion: memory code ≠ sensory code, but information is present.
    """

    _VEC_STIM  = np.array([0.85, 0.20, 0.70, 0.35, 0.90, 0.15, 0.60, 0.45])
    _VEC_DELAY = np.array([0.45, 0.55, 0.40, 0.60, 0.48, 0.52, 0.42, 0.58])

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Tex("Testing: Session 1 (Working Memory)", color=INK, font_size=36)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.9)

        question = Tex(
            r"Does the perceptual code generalise to the delay period?",
            color=MGREY, font_size=23,
        ).next_to(title, DOWN, buff=0.16)
        self.play(FadeIn(question), run_time=0.5)
        self.wait(0.4)

        # ── Trial timeline ─────────────────────────────────────────────────────
        tl_y = 1.05
        tl   = Line(LEFT * 5.5 + UP * tl_y, RIGHT * 5.5 + UP * tl_y,
                    color=LGREY, stroke_width=2)
        self.play(Create(tl), run_time=0.4)

        phase_data = [
            ("Stimulus",  LEFT  * 3.6, BLUE,  "0 s"),
            ("Delay",     ORIGIN,       AMBER, "2 s"),
            ("Probe",     RIGHT * 3.6, GREEN, "10 s"),
        ]
        phase_group = VGroup()
        for name, xoff, col, t_lbl in phase_data:
            dot = Dot(xoff + UP * tl_y, radius=0.12, color=col)
            nl  = Tex(name,  color=col,   font_size=22).next_to(dot, UP,   buff=0.18)
            tl2 = Tex(t_lbl, color=MGREY, font_size=18).next_to(dot, DOWN, buff=0.14)
            phase_group.add(dot, nl, tl2)

        self.play(LaggedStartMap(FadeIn, phase_group, lag_ratio=0.2), run_time=0.8)

        # Shaded bands
        band_s = Rectangle(width=3.0, height=0.28, fill_color=BLUE,
                            fill_opacity=0.12, stroke_width=0) \
            .move_to(LEFT * 3.6 + UP * tl_y)
        band_d = Rectangle(width=4.8, height=0.28, fill_color=AMBER,
                            fill_opacity=0.12, stroke_width=0) \
            .move_to(ORIGIN + UP * tl_y)
        self.play(FadeIn(band_s), FadeIn(band_d), run_time=0.3)

        # ── Voxel bar vectors ──────────────────────────────────────────────────
        bar_s = make_voxel_bar(self._VEC_STIM,  color=BLUE,  bar_max_h=0.85).scale(0.72) \
            .move_to(LEFT * 3.6 + DOWN * 0.55)
        bar_d = make_voxel_bar(self._VEC_DELAY, color=AMBER, bar_max_h=0.85).scale(0.72) \
            .move_to(ORIGIN + DOWN * 0.55)

        lbl_s = Tex(r"$\mathbf{v}_\text{stim}$",  color=BLUE,  font_size=22) \
            .next_to(bar_s, DOWN, buff=0.12)
        lbl_d = Tex(r"$\mathbf{v}_\text{delay}$", color=AMBER, font_size=22) \
            .next_to(bar_d, DOWN, buff=0.12)

        self.play(FadeIn(bar_s), Write(lbl_s), run_time=0.5)
        self.wait(0.2)
        self.play(FadeIn(bar_d), Write(lbl_d), run_time=0.5)
        self.wait(0.3)

        # ── S2 classifier box ──────────────────────────────────────────────────
        clf_box = RoundedRectangle(
            width=2.3, height=0.72, corner_radius=0.12,
            color=RED, stroke_width=2,
        ).set_fill("#FEF2F2", opacity=0.7).move_to(RIGHT * 3.8 + DOWN * 0.3)
        clf_lbl = Tex("S2 classifier", color=RED, font_size=21).move_to(clf_box)

        self.play(FadeIn(clf_box), Write(clf_lbl), run_time=0.6)

        # Stimulus → tick
        arr_s = Arrow(bar_s.get_right(), clf_box.get_left() + LEFT * 0.2 + UP * 0.2,
                      color=BLUE, stroke_width=2, buff=0.08)
        tick = Tex(r"\checkmark", color=GREEN, font_size=40) \
            .next_to(clf_box, RIGHT, buff=0.2).shift(UP * 0.2)

        self.play(GrowArrow(arr_s), run_time=0.5)
        self.play(Write(tick), run_time=0.4)
        self.wait(0.3)

        # Delay → cross
        arr_d = Arrow(bar_d.get_right(), clf_box.get_left() + LEFT * 0.2 + DOWN * 0.2,
                      color=AMBER, stroke_width=2, buff=0.08)
        cross = Text("✗", color=RED, font_size=36) \
            .next_to(clf_box, RIGHT, buff=0.2).shift(DOWN * 0.4)

        self.play(GrowArrow(arr_d), run_time=0.5)
        self.play(Write(cross), run_time=0.4)

        fail_note = Tex(
            r"Perceptual code does not\\generalise to delay",
            color=AMBER, font_size=20,
        ).next_to(cross, DOWN, buff=0.18).align_to(clf_box, LEFT)
        self.play(FadeIn(fail_note), run_time=0.5)
        self.wait(0.7)

        # ── Replace with S1 classifier ─────────────────────────────────────────
        self.play(
            FadeOut(VGroup(arr_s, arr_d, tick, cross, fail_note,
                           clf_box, clf_lbl)),
            run_time=0.4,
        )

        clf2_box = RoundedRectangle(
            width=2.5, height=0.72, corner_radius=0.12,
            color=BLUE, stroke_width=2,
        ).set_fill("#EFF6FF", opacity=0.7).move_to(RIGHT * 3.8 + DOWN * 0.3)
        clf2_lbl = Tex("S1 classifier", color=BLUE, font_size=21).move_to(clf2_box)

        self.play(FadeIn(clf2_box), Write(clf2_lbl), run_time=0.6)

        arr_d2 = Arrow(bar_d.get_right(), clf2_box.get_left() + LEFT * 0.1,
                       color=AMBER, stroke_width=2, buff=0.08)
        tick2 = Tex(r"\checkmark", color=GREEN, font_size=40) \
            .next_to(clf2_box, RIGHT, buff=0.2)

        self.play(GrowArrow(arr_d2), run_time=0.5)
        self.play(Write(tick2), run_time=0.4)

        ok_note = Tex(
            r"Memory code \textit{is} present\\— just in a different format",
            color=BLUE, font_size=20,
        ).next_to(tick2, DOWN, buff=0.18).align_to(clf2_box, LEFT)
        self.play(FadeIn(ok_note), run_time=0.5)
        self.wait(0.7)

        # ── Conclusion ─────────────────────────────────────────────────────────
        self.play(
            FadeOut(VGroup(
                bar_s, bar_d, lbl_s, lbl_d,
                arr_d2, tick2, ok_note, clf2_box, clf2_lbl,
                band_s, band_d, phase_group, tl,
            )),
            run_time=0.5,
        )

        concl = VGroup(
            Tex(r"Working memory $\neq$ sensory code", color=INK, font_size=28),
            Tex(r"Early visual cortex \textit{does} maintain stimulus identity,",
                color=INK, font_size=22),
            Tex(r"but in a memory-specific representational format.",
                color=INK, font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(DOWN * 0.55)

        concl_box = SurroundingRectangle(
            concl, color=BLUE, stroke_width=2, corner_radius=0.14, buff=0.28,
        ).set_fill("#EFF6FF", opacity=0.55)

        self.play(FadeIn(concl_box), run_time=0.4)
        self.play(Write(concl), run_time=1.2)
        self.wait(2.0)
