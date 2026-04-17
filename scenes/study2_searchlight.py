"""
Study 2 searchlight stat-map figure in MNI152 space.

Render:
    uv run manim scenes/study2_searchlight.py Study2SearchlightMniOverlay -qh
    uv run manim scenes/study2_searchlight.py Study2SearchlightMniOverlay -ql -s
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from manim import *
from nilearn.plotting import plot_stat_map
from PIL import Image

try:
    from scenes.utils import REPO_ROOT
except ModuleNotFoundError:
    from utils import REPO_ROOT  # type: ignore[no-redef]


BG = WHITE
INK = "#1C1C1E"
MUTED = "#6B7280"
LGREY = "#D1D5DB"
PURPLE = "#7C3AED"
LILAC = "#A855F7"
GREEN = "#16A34A"

STUDY2_DIR = REPO_ROOT / "assets" / "images" / "study2"
OVERLAY_PATH = REPO_ROOT / "assets" / "images" / "study2" / "searchlight-ses01_encoding_overlaid.nii"
SLIDE_TITLE = "Train and test on Stimulation (Session 1)"
SEARCHLIGHT_SPECS = r"Searchlight specifications: thresholded $z$ map, FPR $< .001$, clusters $> 9$ voxels"
CUT_COORDS_Z = (-12, 0, 10, 21, 32, 46, 61)
MONTAGE_TITLE = "GLM-based searchlight decoding analyses during Stimulation"

MINI_S2_VALUES = np.array([0.88, 0.26, 0.74, 0.34, 0.94, 0.42, 0.68, 0.20, 0.82])
MINI_S1_VALUES = np.array([0.84, 0.30, 0.70, 0.38, 0.90, 0.46, 0.64, 0.24, 0.78])
MINI_SEARCHLIGHT_VALUES = np.array([0.30, 0.74, 0.40, 0.58, 0.24, 0.82, 0.46, 0.68, 0.28])

STAT_MAP_SPECS = [
    {
        "path": STUDY2_DIR / "spm_fwec_k-09_p-001_session02.nii",
        "cluster_info": r"FPR $< .001$, clusters $> 9$ voxels",
        "mini_specs": [
            {
                "values": MINI_S2_VALUES,
                "color": PURPLE,
                "label": r"$S_2$",
                "label_direction": UP,
                "description": ("Stimulation", "Session 2"),
            },
            {
                "values": MINI_S2_VALUES,
                "color": PURPLE,
                "label": r"$S_2$",
                "label_direction": DOWN,
                "description": ("Stimulation", "Session 2"),
            },
        ],
    },
    {
        "path": STUDY2_DIR / "spm_fwec_k-27_p-001_ses02-01_encoding.nii",
        "cluster_info": r"FPR $< .001$, clusters $> 27$ voxels",
        "mini_specs": [
            {
                "values": MINI_S2_VALUES,
                "color": PURPLE,
                "label": r"$S_2$",
                "label_direction": UP,
                "description": ("Stimulation", "Session 2"),
            },
            {
                "values": MINI_S1_VALUES,
                "color": LILAC,
                "label": r"$S_1$",
                "label_direction": DOWN,
                "description": ("Stimulation", "Session 1"),
            },
        ],
    },
    {
        "path": STUDY2_DIR / "searchlight_spm_fwec_k-13_p-001_within-ses01_encoding.nii",
        "cluster_info": r"FPR $< .001$, clusters $> 13$ voxels",
        "mini_specs": [
            {
                "values": MINI_SEARCHLIGHT_VALUES,
                "color": LILAC,
                "label": r"$S_1$",
                "label_direction": UP,
                "description": ("Stimulation", "Session 1"),
            },
            {
                "values": MINI_S1_VALUES,
                "color": LILAC,
                "label": r"$S_1$",
                "label_direction": DOWN,
                "description": ("Stimulation", "Session 1"),
            },
        ],
    },
]


def build_plot_stat_map_rgba(
    map_path3: str | Path = OVERLAY_PATH,
    *,
    figure_size: tuple[float, float] = (11.6, 3.5),
    colorbar: bool = True,
    cut_coords: tuple[int, ...] = CUT_COORDS_Z,
) -> np.ndarray:
    with mpl.rc_context(
        {
            "text.usetex": True,
            "font.family": "serif",
            "font.serif": ["Computer Modern Roman", "CMU Serif", "DejaVu Serif"],
            "mathtext.fontset": "cm",
        }
    ):
        fig = plt.figure(figsize=figure_size, facecolor="white")
        display = plot_stat_map(
            # figure=fig,
            stat_map_img=str(map_path3),
            title=None,
            cmap="magma",
            display_mode="z",
            figure=fig,
            black_bg=False,
            colorbar=colorbar,
            cut_coords=cut_coords,
            draw_cross=False,
            annotate=True,
        )

        buffer = BytesIO()
        fig.savefig(
            buffer,
            format="png",
            dpi=220,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
        )
        buffer.seek(0)
        rgba = np.asarray(Image.open(buffer).convert("RGBA")).copy()
        buffer.close()
        display.close()
        plt.close(fig)
    return rgba


def make_feature_row(
    values: np.ndarray,
    color: str,
    *,
    cell_w: float = 0.11,
    cell_h: float = 0.11,
    gap: float = 0.022,
) -> VGroup:
    group = VGroup()
    mid = (len(values) - 1) / 2
    for i, value in enumerate(values):
        cell = Rectangle(
            width=cell_w,
            height=cell_h,
            stroke_width=0.7,
            stroke_color=LGREY,
        ).set_fill(
            interpolate_color(
                ManimColor(WHITE),
                ManimColor(color),
                0.10 + 0.90 * float(value),
            ),
            opacity=1.0,
        )
        cell.move_to(RIGHT * (i - mid) * (cell_w + gap))
        group.add(cell)
    return group.move_to(ORIGIN)


def make_small_results_matrix(
    values: np.ndarray,
    color: str,
    label: str,
    *,
    label_direction: np.ndarray = UP,
    scale_factor: float = 1.35,
) -> VGroup:
    rows = VGroup(*[
        make_feature_row(values[row_idx * 3 : (row_idx + 1) * 3], color)
        for row_idx in range(3)
    ]).arrange(DOWN, buff=0.022)
    frame = SurroundingRectangle(
        rows,
        color=color,
        stroke_width=1.5,
        buff=0.042,
        corner_radius=0.03,
    )
    matrix_label = Tex(label, color=color, font_size=13).next_to(
        frame,
        label_direction,
        buff=0.04,
    )
    return VGroup(rows, frame, matrix_label).scale(scale_factor)


class Study2SearchlightMniOverlay(Scene):
    """Display a nilearn plot_stat_map figure inside a Manim slide frame."""

    def construct(self) -> None:
        self.camera.background_color = BG
        title = Tex(
            rf"\textbf{{{SLIDE_TITLE}}}",
            color=INK,
            font_size=32,
        ).to_edge(UP, buff=0.42)

        plot_image = ImageMobject(build_plot_stat_map_rgba()).scale_to_fit_width(config.frame_width - 0.5)
        plot_image.next_to(title, DOWN, buff=0.22)

        searchlight_specs = Tex(
            SEARCHLIGHT_SPECS,
            color=MUTED,
            font_size=20,
        ).next_to(plot_image, DOWN, buff=0.22)

        self.play(
            FadeIn(title, shift=UP * 0.10),
            FadeIn(plot_image, shift=UP * 0.12, scale=0.98),
            run_time=0.75,
        )
        self.play(FadeIn(searchlight_specs, shift=UP * 0.06), run_time=0.35)
        self.wait(1.5)


class Study2StatMapMontage(Scene):
    """Presentation-ready montage of three Study 2 z-map results."""

    def _matrix_stack(self, mini_specs: list[dict]) -> Group:
        matrices = Group()
        matrix_objects: list[VGroup] = []
        for spec in mini_specs:
            matrix = make_small_results_matrix(
                spec["values"],
                spec["color"],
                spec["label"],
                label_direction=spec["label_direction"],
            )
            matrix_objects.append(matrix)
            desc_top, desc_bottom = spec["description"]
            desc_group = VGroup(
                Tex(desc_top, color=INK, font_size=15),
                Tex(desc_bottom, color=INK, font_size=15),
            ).arrange(DOWN, aligned_edge=RIGHT, buff=0.02)
            matrices.add(Group(desc_group, matrix).arrange(RIGHT, buff=0.20, aligned_edge=ORIGIN))

        matrices.arrange(DOWN, buff=0.29)
        if len(mini_specs) > 1:
            arrow = Arrow(
                matrix_objects[0][1].get_bottom() + DOWN * 0.10,
                matrix_objects[-1][1].get_top() + UP * 0.10,
                color=INK,
                stroke_width=6.0,
                buff=0.0,
                tip_length=0.24,
            )
            return Group(matrices, arrow)
        return Group(matrices)

    def _row_group(self, *, path: Path, cluster_info: str, mini_specs: list[dict]) -> Group:
        matrix_stack = self._matrix_stack(mini_specs)

        plot_image = ImageMobject(
            build_plot_stat_map_rgba(
                path,
                figure_size=(8.6, 1.65),
                colorbar=False,
            )
        ).scale_to_fit_width(9.9)
        cluster_caption = Tex(cluster_info, color=MUTED, font_size=18)
        plot_group = Group(plot_image, cluster_caption).arrange(DOWN, buff=0.05)

        row = Group(matrix_stack, plot_group).arrange(RIGHT, buff=1.12, aligned_edge=UP)
        return row

    def construct(self) -> None:
        self.camera.background_color = BG
        title = Tex(rf"\textbf{{{MONTAGE_TITLE}}}", color=INK, font_size=28).to_edge(UP, buff=0.28)

        rows = Group(*[self._row_group(**spec) for spec in STAT_MAP_SPECS])
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        rows.scale_to_fit_width(config.frame_width - 0.15)
        rows.scale_to_fit_height(config.frame_height - 0.95)
        rows.next_to(title, DOWN, buff=0.16)

        self.play(
            FadeIn(title, shift=UP * 0.08),
            run_time=0.45,
        )
        self.play(
            LaggedStart(
                *[FadeIn(row, shift=UP * 0.10) for row in rows],
                lag_ratio=0.18,
            ),
            run_time=1.35,
        )
        self.wait(1.6)
