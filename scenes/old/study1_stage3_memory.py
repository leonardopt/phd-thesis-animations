"""
Study 1, Stage 3 — Memory Validation Task.

Narrative arc:
  Scene 1 (Study1Stage3MemoryIntro):
    Introduce the memory-validation task, then show four example
    image continua and collapse each set down to the target plus
    selected distractors.

Render:
    uv run manim scenes/study1_stage3_memory.py Study1Stage3MemoryIntro -qh
    uv run manim scenes/study1_stage3_memory.py Study1Stage3MemoryExpDesignA -qh
    uv run manim scenes/study1_stage3_memory.py Study1Stage3MemoryExpDesignB -qh
    uv run manim scenes/study1_stage3_memory.py Study1Stage3MemoryExpResults -qh
"""
from __future__ import annotations

import csv
from pathlib import Path

from manim import *

from utils import REPO_ROOT, env_path

# ── Palette ─────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"

# ── Paths ────────────────────────────────────────────────────────────────────────
STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    REPO_ROOT / "assets" / "images" / "stimuli_reordered",
)
MEMORY_TASK_STIM_DIR = env_path(
    "MEMORY_TASK_STIM_DIR",
    REPO_ROOT / "assets" / "images" / "study1" / "memory_task",
)
STIM_INFO_CSV = env_path(
    "STIM_INFO_CSV",
    REPO_ROOT / "assets" / "data" / "study1" / "stimuli_info.csv",
)
FIXATION_PATH = str(REPO_ROOT / "assets" / "images" / "fixation_target.png")


def stimulus_path(prefix: str, idx: int) -> str:
    return str(STIM_DIR / f"{prefix}-{idx:02d}.png")


def memory_task_stimulus_path(name: str) -> str:
    return str(MEMORY_TASK_STIM_DIR / name)


def load_stimulus_lookup() -> dict[tuple[str, str], dict[str, str]]:
    with STIM_INFO_CSV.open() as f:
        rows = list(csv.DictReader(f))
    return {(row["category"], row["object"]): row for row in rows}


def stimulus_image(
    prefix: str,
    idx: int,
    height: float,
    pos: tuple[float, float, float] | np.ndarray,
) -> ImageMobject:
    img = ImageMobject(stimulus_path(prefix, idx))
    img.set_height(height)
    img.move_to(pos)
    return img


def fixation_on(
    mob: Mobject | np.ndarray,
    height: float = 0.18,
) -> ImageMobject:
    fixation = ImageMobject(FIXATION_PATH)
    fixation.set_height(height)
    fixation.set_z_index(10)
    if isinstance(mob, np.ndarray):
        fixation.move_to(mob)
    else:
        fixation.move_to(mob.get_center())
    return fixation


def _get_hex(color: ParsableManimColor | None) -> str | None:
    return color.to_hex().upper() if color else None


def recolor_svg(svg: SVGMobject, color_map: dict[str, ParsableManimColor]) -> None:
    for submob in svg.family_members_with_points():
        stroke_hex = _get_hex(submob.get_stroke_color())
        if stroke_hex in color_map:
            submob.set_stroke(
                color=color_map[stroke_hex],
                width=submob.get_stroke_width(),
                opacity=submob.get_stroke_opacity(),
            )

        fill_hex = _get_hex(submob.get_fill_color())
        if fill_hex in color_map:
            submob.set_fill(
                color=color_map[fill_hex],
                opacity=submob.get_fill_opacity(),
            )


def restore_agg_nonrepeated_dashes(svg: SVGMobject) -> None:
    """Manim drops SVG dash arrays here, so restore them after loading."""
    candidates = [
        submob
        for submob in svg.submobjects
        if (
            submob.get_fill_opacity() == 0
            and abs(submob.get_stroke_width() - 1.71) < 0.1
            and abs(submob.get_stroke_opacity() - 0.60) < 0.1
        )
    ]
    line_groups = {
        "series": [submob for submob in candidates if submob.get_center()[0] < 0],
        "legend": [submob for submob in candidates if submob.get_center()[0] > 0],
    }

    for group in line_groups.values():
        if not group:
            continue

        target = min(group, key=lambda submob: submob.get_center()[1])
        num_dashes = max(4, int(round(target.width / 0.10)))
        dashed = DashedVMobject(target.copy(), num_dashes=num_dashes, dashed_ratio=0.5)
        dashed.set_stroke(
            color=target.get_stroke_color(),
            width=target.get_stroke_width(),
            opacity=target.get_stroke_opacity(),
        )
        dashed.set_fill(opacity=0)
        target.set_stroke(opacity=0)
        svg.add(dashed)


def svg_local_point(svg: SVGMobject, x: float, y: float, *, base_height: float = 3.0) -> np.ndarray:
    scale = svg.height / base_height
    return svg.get_center() + np.array([x * scale, y * scale, 0.0])


def crisp_tex_label(
    text: str,
    center: np.ndarray,
    *,
    font_size: float,
    rotation: float = 0.0,
    buff: float = 0.04,
) -> VGroup:
    label = Tex(text, color=INK, font_size=font_size)
    if rotation:
        label.rotate(rotation)
    label.move_to(center)
    bg = BackgroundRectangle(label, color=WHITE, fill_opacity=1.0, buff=buff)
    bg.set_stroke(opacity=0)
    bg.set_z_index(9)
    label.set_z_index(10)
    return VGroup(bg, label)


def build_agg_tex_overlays(svg: SVGMobject) -> VGroup:
    scale = svg.height / 3.0
    tick_fs = 16 * scale
    label_fs = 18 * scale
    overlays = VGroup()

    for y, text in [
        (1.287, "1.0"),
        (0.899, "0.9"),
        (0.512, "0.8"),
        (0.127, "0.7"),
        (-0.261, "0.6"),
        (-0.647, "0.5"),
    ]:
        overlays.add(
            crisp_tex_label(
                text,
                svg_local_point(svg, -1.95, y),
                font_size=tick_fs,
                buff=0.015,
            )
        )

    for x, text in [
        (-1.313, "Hard"),
        (-0.583, "Medium"),
        (0.148, "Easy"),
    ]:
        overlays.add(
            crisp_tex_label(
                text,
                svg_local_point(svg, x, -1.11),
                font_size=tick_fs,
                buff=0.015,
            )
        )

    overlays.add(
        crisp_tex_label(
            "Mean accuracy",
            svg_local_point(svg, -2.18, 0.24),
            font_size=label_fs,
            rotation=PI / 2,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Difficulty level",
            svg_local_point(svg, -0.56, -1.31),
            font_size=label_fs,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Chance level",
            svg_local_point(svg, 0.47, -0.49),
            font_size=label_fs,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Target condition",
            svg_local_point(svg, 1.53, 0.50),
            font_size=label_fs,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Repeated",
            svg_local_point(svg, 1.58, 0.19),
            font_size=label_fs,
            buff=0.025,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Non-repeated",
            svg_local_point(svg, 1.70, -0.02),
            font_size=label_fs,
            buff=0.025,
        )
    )
    return overlays


def build_block_tex_overlays(svg: SVGMobject) -> VGroup:
    scale = svg.height / 3.0
    tick_fs = 15 * scale
    label_fs = 18 * scale
    overlays = VGroup()

    for y, text in [
        (1.053, "1.0"),
        (0.685, "0.9"),
        (0.319, "0.8"),
        (-0.047, "0.7"),
        (-0.413, "0.6"),
        (-0.779, "0.5"),
    ]:
        overlays.add(
            crisp_tex_label(
                text,
                svg_local_point(svg, -2.54, y),
                font_size=tick_fs,
                buff=0.015,
            )
        )

    for x, text in [
        (-1.97, "Hard"),
        (-1.28, "Medium"),
        (-0.59, "Easy"),
        (0.32, "Hard"),
        (1.01, "Medium"),
        (1.70, "Easy"),
    ]:
        overlays.add(
            crisp_tex_label(
                text,
                svg_local_point(svg, x, -1.19),
                font_size=tick_fs,
                buff=0.015,
            )
        )

    overlays.add(
        crisp_tex_label(
            "Repeated",
            svg_local_point(svg, -1.28, 1.28),
            font_size=label_fs,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Non-repeated",
            svg_local_point(svg, 1.03, 1.28),
            font_size=label_fs,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Mean accuracy",
            svg_local_point(svg, -2.72, 0.06),
            font_size=label_fs,
            rotation=PI / 2,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Difficulty level",
            svg_local_point(svg, -0.11, -1.34),
            font_size=label_fs,
            buff=0.03,
        )
    )
    overlays.add(
        crisp_tex_label(
            "Block",
            svg_local_point(svg, 2.56, 0.63),
            font_size=label_fs,
            buff=0.03,
        )
    )

    for y, text in [
        (0.395, "1"),
        (0.215, "2"),
        (0.033, "3"),
        (-0.145, "4"),
        (-0.327, "5"),
        (-0.507, "6"),
    ]:
        overlays.add(
            crisp_tex_label(
                text,
                svg_local_point(svg, 2.67, y),
                font_size=tick_fs,
                buff=0.015,
            )
        )

    return overlays


def load_visible_svg(path: str | Path, *, height: float) -> SVGMobject:
    """Load an SVG and drop any full-canvas white background rect."""
    svg = SVGMobject(str(path), use_svg_cache=False)
    for submob in list(svg.submobjects):
        if (
            _get_hex(submob.get_stroke_color()) == "#FFFFFF"
            and _get_hex(submob.get_fill_color()) == "#FFFFFF"
            and submob.width > 0.9 * svg.width
            and submob.height > 0.9 * svg.height
        ):
            svg.remove(submob)
            break
    svg.center()
    svg.set_height(height)
    recolor_svg(
        svg,
        {
            "#4D4D4D": INK,
            "#333333": INK,
            "#1A1A1A": INK,
            "#A9A9A9": INK,
        },
    )
    return svg


class Study1Stage3MemoryIntro(Scene):
    """Transition from similarity judgements into the memory-validation task."""

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Stage 3 title block ──────────────────────────────────────────────
        title = Tex(
            r"Memory validation task",
            color=INK,
            font_size=40,
        ).move_to(ORIGIN)
        title_top_target = title.copy().to_edge(UP, buff=0.28)

        question = VGroup(
            Tex(
                r"Does proximity along the perceptual continua",
                color=INK,
                font_size=26,
            ),
            Tex(
                r"of our image sets predict memory performance?",
                color=INK,
                font_size=26,
            ),
        ).arrange(DOWN, buff=0.10).next_to(title_top_target, DOWN, buff=0.24)

        def set_image(
            prefix: str,
            idx: int,
            height: float,
            pos: tuple[float, float, float],
        ) -> ImageMobject:
            img = ImageMobject(stimulus_path(prefix, idx))
            img.set_height(height)
            img.move_to(pos)
            return img

        with STIM_INFO_CSV.open() as f:
            rows = list(csv.DictReader(f))

        lookup: dict[tuple[str, str], dict[str, str]] = {}
        for row in rows:
            lookup[(row["category"], row["object"])] = row

        set_specs = [
            ("plant", "pine_med"),
            ("landscape_element", "lake_island"),
            ("building", "observatory"),
            ("item", "sofa"),
        ]
        question_bottom_y = question.get_bottom()[1]
        row_spacing = 1.05
        bottom_margin_y = -config.frame_height / 2 + 0.55
        row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
        row_y_positions = [
            row_block_center_y + row_spacing * offset
            for offset in (1.5, 0.5, -0.5, -1.5)
        ]
        left_column_center_x = -config.frame_width / 4
        example_center = np.array([0.0, row_block_center_y, 0.0])
        example_side_offset = 1.55
        example_image_height = 1.95 * 1.30
        target_color = "#5B7493"
        foil_color = "#B67A5D"
        axis_color = "#C7CDD4"
        criterion_color = "#6B7280"
        initial_row_center_x = left_column_center_x
        selected_spacing = 1.05
        selected_xs = [
            left_column_center_x + selected_spacing * offset
            for offset in (-1.5, -0.5, 0.5, 1.5)
        ]

        example_target = ImageMobject(memory_task_stimulus_path("LAN-MOU-T00.png"))
        example_target.set_height(example_image_height)
        example_target.move_to(example_center + LEFT * example_side_offset)
        example_target.set_z_index(5)

        example_foil = ImageMobject(memory_task_stimulus_path("LAN-MOU-D01.png"))
        example_foil.set_height(example_image_height)
        example_foil.move_to(example_center + RIGHT * example_side_offset)
        example_foil.set_z_index(4)
        example_left_row_center = np.array([left_column_center_x, row_block_center_y, 0.0])
        example_target_left_pos = example_left_row_center + LEFT * example_side_offset
        example_foil_left_pos = example_left_row_center + RIGHT * example_side_offset
        example_target_label = Tex(r"Target", color=target_color, font_size=26)
        example_target_label.move_to(
            example_target_left_pos + UP * (example_image_height / 2 + 0.28)
        )
        example_target_label.set_z_index(6)
        example_foil_label = Tex(r"Foil", color=foil_color, font_size=26)
        example_foil_label.move_to(
            example_foil_left_pos + UP * (example_image_height / 2 + 0.28)
        )
        example_foil_label.set_z_index(6)

        sdt_axes = Axes(
            x_range=[0.0, 1.85, 0.37],
            y_range=[0.0, 1.25, 0.5],
            x_length=5.10,
            y_length=2.25,
            axis_config={
                "color": axis_color,
                "stroke_width": 1.5,
                "include_ticks": False,
                "include_tip": True,
                "tip_width": 0.09,
                "tip_height": 0.09,
            },
        )
        sdt_axes.move_to(np.array([3.48, row_block_center_y - 0.05, 0.0]))
        foil_mean = 0.56
        target_mean = 0.94
        signal_sigma = 0.16
        signal_peak = 0.92
        foil_curve = sdt_axes.plot(
            lambda x: signal_peak * np.exp(-0.5 * ((x - foil_mean) / signal_sigma) ** 2),
            x_range=[0.0, 1.63],
            color=foil_color,
            stroke_width=4,
        )
        target_curve = sdt_axes.plot(
            lambda x: signal_peak * np.exp(-0.5 * ((x - target_mean) / signal_sigma) ** 2),
            x_range=[0.0, 1.63],
            color=target_color,
            stroke_width=4,
        )
        foil_area = sdt_axes.get_area(
            foil_curve,
            x_range=[0.0, 1.63],
            color=foil_color,
            opacity=0.20,
        )
        foil_area.set_stroke(width=0)
        target_area = sdt_axes.get_area(
            target_curve,
            x_range=[0.0, 1.63],
            color=target_color,
            opacity=0.20,
        )
        target_area.set_stroke(width=0)
        criterion_x = 0.75
        criterion_line = DashedLine(
            sdt_axes.c2p(criterion_x, 0.0),
            sdt_axes.c2p(criterion_x, 1.12),
            dash_length=0.10,
            dashed_ratio=0.55,
            color=criterion_color,
            stroke_width=2.0,
        )
        criterion_label = Tex(r"Criterion", color=criterion_color, font_size=22)
        criterion_label.next_to(criterion_line, UP, buff=0.12)
        foil_curve_label = Tex(r"Foil signal", color=foil_color, font_size=18)
        foil_curve_label.move_to(sdt_axes.c2p(0.33, 0.88))
        target_curve_label = Tex(r"Target signal", color=target_color, font_size=18)
        target_curve_label.move_to(sdt_axes.c2p(1.25, 0.88))
        memory_strength_label = Tex(r"Memory strength", color=INK, font_size=22)
        memory_strength_label.next_to(sdt_axes.x_axis, DOWN, buff=0.20)
        probability_density_label = Tex(r"Probability density", color=INK, font_size=18)
        probability_density_label.rotate(PI / 2)
        probability_density_label.next_to(sdt_axes.y_axis, LEFT, buff=0.18)
        target_pair_highlight = SurroundingRectangle(
            Group(example_target_label, target_curve_label),
            buff=0.10,
            corner_radius=0.08,
            color=target_color,
            stroke_width=2.0,
        )
        target_pair_highlight.set_fill(target_color, opacity=0.06)
        foil_pair_highlight = SurroundingRectangle(
            Group(example_foil_label, foil_curve_label),
            buff=0.10,
            corner_radius=0.08,
            color=foil_color,
            stroke_width=2.0,
        )
        foil_pair_highlight.set_fill(foil_color, opacity=0.06)
        criterion_sweep_offset = 0.09
        criterion_right_shift = sdt_axes.c2p(criterion_x + criterion_sweep_offset, 0.0) - sdt_axes.c2p(
            criterion_x, 0.0
        )
        criterion_left_shift = sdt_axes.c2p(criterion_x - criterion_sweep_offset, 0.0) - sdt_axes.c2p(
            criterion_x, 0.0
        )
        sdt_group = VGroup(
            sdt_axes,
            foil_area,
            target_area,
            foil_curve,
            target_curve,
            criterion_line,
            criterion_label,
            foil_curve_label,
            target_curve_label,
            memory_strength_label,
            probability_density_label,
        )

        panels = []
        for (category, obj), row_y in zip(set_specs, row_y_positions):
            row = lookup[(category, obj)]
            prefix = f"{category}_{obj}"
            cards = []
            for idx in range(10):
                cards.append(set_image(prefix, idx, 0.56, (0.0, 0.0, 0.0)))
            row_group = Group(*cards).arrange(RIGHT, buff=0.09).move_to([initial_row_center_x, row_y, 0.0])

            selected_indices = [
                int(row["target_position"]),
                int(row["distractor_1_position"]),
                int(row["distractor_2_position"]),
                int(row["distractor_3_position"]),
            ]
            selected_targets = [
                np.array([selected_xs[0], row_y, 0.0]),
                np.array([selected_xs[1], row_y, 0.0]),
                np.array([selected_xs[2], row_y, 0.0]),
                np.array([selected_xs[3], row_y, 0.0]),
            ]
            panels.append(
                {
                    "row_group": row_group,
                    "cards": cards,
                    "selected_indices": selected_indices,
                    "selected_targets": selected_targets,
                    "center": np.array([initial_row_center_x, row_y, 0.0]),
                }
            )

        bottom_panel = panels[-1]
        bottom_row_dots = VGroup(
            *[
                MathTex(r"\vdots", color=MGREY, font_size=24).next_to(card, DOWN, buff=0.10)
                for card in bottom_panel["cards"]
            ]
        )
        bottom_dot_offsets = [
            dot.get_center() - card.get_center()
            for card, dot in zip(bottom_panel["cards"], bottom_row_dots)
        ]

        # ── Animation ────────────────────────────────────────────────────────
        self.play(Write(title), run_time=0.70)
        self.wait(0.15)
        self.play(title.animate.move_to(title_top_target), run_time=0.55)
        self.play(FadeIn(question, shift=UP * 0.12), run_time=0.60)
        self.wait(0.60)

        self.play(
            FadeIn(example_target, scale=0.96),
            FadeIn(example_foil, scale=0.96),
            run_time=0.70,
        )
        self.wait(2.00)
        self.play(
            example_target.animate.move_to(example_center),
            example_foil.animate.move_to(example_center),
            run_time=0.70,
        )
        self.wait(2.00)

        target_visible = True

        def swap_example(delay: float) -> None:
            nonlocal target_visible
            target_visible = not target_visible
            self.play(
                example_target.animate.set_opacity(1.0 if target_visible else 0.0),
                run_time=0.10,
                rate_func=linear,
            )
            self.wait(delay)

        for _ in range(8):
            swap_example(0.20)
        self.wait(2.00)

        self.play(
            example_target.animate.move_to(example_target_left_pos).set_opacity(1.0),
            example_foil.animate.move_to(example_foil_left_pos).set_opacity(1.0),
            run_time=0.65,
            rate_func=smooth,
        )
        self.play(
            FadeIn(example_target_label, shift=UP * 0.10),
            FadeIn(example_foil_label, shift=UP * 0.10),
            LaggedStart(
                Create(sdt_axes),
                FadeIn(foil_area),
                FadeIn(target_area),
                Create(foil_curve),
                Create(target_curve),
                FadeIn(foil_curve_label, shift=UP * 0.08),
                FadeIn(target_curve_label, shift=UP * 0.08),
                FadeIn(memory_strength_label, shift=UP * 0.08),
                FadeIn(probability_density_label, shift=RIGHT * 0.08),
                lag_ratio=0.12,
            ),
            run_time=1.30,
        )
        self.play(
            Create(criterion_line),
            FadeIn(criterion_label, shift=UP * 0.08),
            run_time=0.55,
        )
        self.play(
            example_target_label.animate.scale(1.18),
            target_curve.animate.set_stroke(width=4.8, opacity=1.0),
            target_area.animate.set_fill(opacity=0.34),
            example_foil_label.animate.set_opacity(0.35),
            foil_curve.animate.set_stroke(opacity=0.28),
            foil_area.animate.set_fill(opacity=0.08),
            target_curve_label.animate.set_opacity(0.35),
            foil_curve_label.animate.set_opacity(0.25),
            run_time=0.80,
        )
        self.wait(0.40)
        self.play(
            example_target_label.animate.scale(1 / 1.18),
            target_curve.animate.set_stroke(width=2.2, opacity=0.28),
            target_area.animate.set_fill(opacity=0.08),
            example_target_label.animate.set_opacity(0.35),
            example_foil_label.animate.set_opacity(1.0),
            foil_curve.animate.set_stroke(width=2.2, opacity=0.28),
            foil_area.animate.set_fill(opacity=0.08),
            target_curve_label.animate.set_opacity(0.25),
            foil_curve_label.animate.set_opacity(0.35),
            run_time=0.30,
        )
        self.play(
            example_foil_label.animate.scale(1.18),
            foil_curve.animate.set_stroke(width=4.8, opacity=1.0),
            foil_area.animate.set_fill(opacity=0.34),
            run_time=0.85,
        )
        self.wait(0.40)
        self.play(
            example_foil_label.animate.scale(1 / 1.18),
            example_target_label.animate.set_opacity(1.0),
            target_curve.animate.set_stroke(width=2.2, opacity=1.0),
            target_area.animate.set_fill(opacity=0.16),
            example_foil_label.animate.set_opacity(1.0),
            foil_curve.animate.set_stroke(width=2.2, opacity=1.0),
            foil_area.animate.set_fill(opacity=0.16),
            target_curve_label.animate.set_opacity(1.0),
            foil_curve_label.animate.set_opacity(1.0),
            run_time=0.85,
        )
        self.play(
            Succession(
                AnimationGroup(
                    criterion_line.animate.shift(criterion_right_shift),
                    criterion_label.animate.shift(criterion_right_shift),
                    run_time=1.60,
                    rate_func=smooth,
                ),
                AnimationGroup(
                    criterion_line.animate.shift(criterion_left_shift - criterion_right_shift),
                    criterion_label.animate.shift(criterion_left_shift - criterion_right_shift),
                    run_time=2.40,
                    rate_func=smooth,
                ),
                AnimationGroup(
                    criterion_line.animate.shift(-criterion_left_shift),
                    criterion_label.animate.shift(-criterion_left_shift),
                    run_time=1.80,
                    rate_func=smooth,
                ),
            ),
        )
        self.wait(1.00)

        upper_row_center_y = row_block_center_y + 1.20
        upper_label_buff = 0.28
        subtitle_shift = UP * (0.10 * (upper_row_center_y - row_block_center_y))
        upper_example_center = np.array([left_column_center_x, upper_row_center_y, 0.0])
        upper_example_target_pos = upper_example_center + LEFT * example_side_offset
        upper_example_foil_pos = upper_example_center + RIGHT * example_side_offset
        upper_target_label_pos = upper_example_target_pos + UP * (example_image_height / 2 + upper_label_buff)
        upper_foil_label_pos = upper_example_foil_pos + UP * (example_image_height / 2 + upper_label_buff)
        upper_plot_center = np.array([3.48, upper_row_center_y - 0.05, 0.0])
        upper_plot_shift = upper_plot_center - sdt_axes.get_center()

        second_row_center_y = row_block_center_y - 1.50
        second_example_center = np.array([left_column_center_x, second_row_center_y, 0.0])
        second_example_target_pos = second_example_center + LEFT * example_side_offset
        second_example_foil_pos = second_example_center + RIGHT * example_side_offset
        second_plot_center = np.array([3.48, second_row_center_y - 0.05, 0.0])

        second_example_target = ImageMobject(memory_task_stimulus_path("LAN-MOU-T00.png"))
        second_example_target.set_height(example_image_height)
        second_example_target.move_to(second_example_target_pos)
        second_example_target.set_z_index(5)

        second_example_foil = ImageMobject(memory_task_stimulus_path("LAN-MOU-D03.png"))
        second_example_foil.set_height(example_image_height)
        second_example_foil.move_to(second_example_foil_pos)
        second_example_foil.set_z_index(4)

        second_sdt_axes = Axes(
            x_range=[0.0, 1.85, 0.37],
            y_range=[0.0, 1.25, 0.5],
            x_length=5.10,
            y_length=2.25,
            axis_config={
                "color": axis_color,
                "stroke_width": 1.5,
                "include_ticks": False,
                "include_tip": True,
                "tip_width": 0.09,
                "tip_height": 0.09,
            },
        )
        second_sdt_axes.move_to(second_plot_center)
        second_foil_mean = foil_mean
        second_target_mean = 1.18
        second_signal_sigma = 0.16
        second_signal_peak = 0.92
        second_foil_curve = second_sdt_axes.plot(
            lambda x: second_signal_peak * np.exp(-0.5 * ((x - second_foil_mean) / second_signal_sigma) ** 2),
            x_range=[0.0, 1.63],
            color=foil_color,
            stroke_width=2.2,
        )
        second_target_curve = second_sdt_axes.plot(
            lambda x: second_signal_peak * np.exp(-0.5 * ((x - second_target_mean) / second_signal_sigma) ** 2),
            x_range=[0.0, 1.63],
            color=target_color,
            stroke_width=2.2,
        )
        second_foil_area = second_sdt_axes.get_area(
            second_foil_curve,
            x_range=[0.0, 1.63],
            color=foil_color,
            opacity=0.16,
        )
        second_foil_area.set_stroke(width=0)
        second_target_area = second_sdt_axes.get_area(
            second_target_curve,
            x_range=[0.0, 1.63],
            color=target_color,
            opacity=0.16,
        )
        second_target_area.set_stroke(width=0)
        second_criterion_x = 0.5 * (second_foil_mean + second_target_mean)
        second_criterion_line = DashedLine(
            second_sdt_axes.c2p(second_criterion_x, 0.0),
            second_sdt_axes.c2p(second_criterion_x, 1.12),
            dash_length=0.10,
            dashed_ratio=0.55,
            color=criterion_color,
            stroke_width=2.0,
        )
        second_criterion_label = Tex(r"Criterion", color=criterion_color, font_size=22)
        second_criterion_label.next_to(second_criterion_line, UP, buff=0.12)
        second_foil_curve_label = Tex(r"Foil signal", color=foil_color, font_size=18)
        second_foil_curve_label.move_to(second_sdt_axes.c2p(0.33, 0.88))
        second_target_curve_label = Tex(r"Target signal", color=target_color, font_size=18)
        second_target_curve_label.move_to(second_sdt_axes.c2p(1.45, 0.88))
        second_memory_strength_label = Tex(r"Memory strength", color=INK, font_size=22)
        second_memory_strength_label.next_to(second_sdt_axes.x_axis, DOWN, buff=0.20)
        second_probability_density_label = Tex(r"Probability density", color=INK, font_size=18)
        second_probability_density_label.rotate(PI / 2)
        second_probability_density_label.next_to(second_sdt_axes.y_axis, LEFT, buff=0.18)

        self.wait(0.40)
        self.play(
            question.animate.shift(subtitle_shift),
            example_target.animate.move_to(upper_example_target_pos),
            example_foil.animate.move_to(upper_example_foil_pos),
            example_target_label.animate.move_to(upper_target_label_pos),
            example_foil_label.animate.move_to(upper_foil_label_pos),
            sdt_group.animate.shift(upper_plot_shift),
            run_time=1.05,
            rate_func=smooth,
        )
        self.wait(0.25)
        self.play(
            FadeIn(second_example_target, scale=0.96),
            FadeIn(second_example_foil, scale=0.96),
            run_time=0.70,
        )
        self.wait(0.25)
        self.play(
            LaggedStart(
                Create(second_sdt_axes),
                FadeIn(second_foil_area),
                FadeIn(second_target_area),
                Create(second_foil_curve),
                Create(second_target_curve),
                Create(second_criterion_line),
                FadeIn(second_criterion_label, shift=UP * 0.08),
                FadeIn(second_foil_curve_label, shift=UP * 0.08),
                FadeIn(second_target_curve_label, shift=UP * 0.08),
                FadeIn(second_memory_strength_label, shift=UP * 0.08),
                FadeIn(second_probability_density_label, shift=RIGHT * 0.08),
                lag_ratio=0.10,
            ),
            run_time=1.35,
        )
        self.wait(1.10)


class Study1Stage3MemoryExpDesignA(Scene):
    """Show the delayed match-to-sample design alongside the selected memory sets."""

    def construct(self) -> None:
        self.camera.background_color = BG

        title = Tex(
            r"Memory validation task",
            color=INK,
            font_size=40,
        ).to_edge(UP, buff=0.28)
        question = VGroup(
            Tex(
                r"Does proximity along the perceptual continua",
                color=INK,
                font_size=26,
            ),
            Tex(
                r"of our image sets predict memory performance?",
                color=INK,
                font_size=26,
            ),
        ).arrange(DOWN, buff=0.10).next_to(title, DOWN, buff=0.24)

        lookup = load_stimulus_lookup()
        set_specs = [
            ("plant", "pine_med"),
            ("landscape_element", "lake_island"),
            ("building", "observatory"),
            ("item", "sofa"),
        ]
        question_bottom_y = question.get_bottom()[1]
        row_spacing = 1.05
        bottom_margin_y = -config.frame_height / 2 + 0.55
        row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
        row_y_positions = [
            row_block_center_y + row_spacing * offset
            for offset in (1.5, 0.5, -0.5, -1.5)
        ]
        left_column_center_x = -config.frame_width / 4
        selected_spacing = 1.05
        selected_xs = [
            left_column_center_x + selected_spacing * offset
            for offset in (-1.5, -0.5, 0.5, 1.5)
        ]

        collapsed_cards = []
        bottom_continuation_marks = []
        lake_target_card = None
        lake_d3_card = None
        for (category, obj), row_y in zip(set_specs, row_y_positions):
            row = lookup[(category, obj)]
            prefix = f"{category}_{obj}"
            selected_indices = [
                int(row["target_position"]),
                int(row["distractor_1_position"]),
                int(row["distractor_2_position"]),
                int(row["distractor_3_position"]),
            ]
            for col_idx, stim_idx in enumerate(selected_indices):
                card = stimulus_image(prefix, stim_idx, 0.56, (selected_xs[col_idx], row_y, 0.0))
                card.scale(1.45)
                card.set_z_index(5)
                collapsed_cards.append(card)
                if category == "landscape_element" and obj == "lake_island" and col_idx == 0:
                    lake_target_card = card
                if category == "landscape_element" and obj == "lake_island" and col_idx == 3:
                    lake_d3_card = card
                if obj == "sofa":
                    dot = MathTex(r"\vdots", color=MGREY, font_size=24).next_to(card, DOWN, buff=0.19)
                    dot.set_z_index(5)
                    bottom_continuation_marks.append(dot)

        target_cards = Group(*collapsed_cards[0::4])
        foil_cards = Group(
            *[
                collapsed_cards[idx]
                for idx in range(len(collapsed_cards))
                if idx % 4 != 0
            ]
        )
        continuation_marks = VGroup(*bottom_continuation_marks)

        target_rect = SurroundingRectangle(
            Group(target_cards, continuation_marks[0]),
            color=MGREY,
            stroke_width=1.5,
            buff=0.10,
            corner_radius=0.06,
        )
        foil_rect = SurroundingRectangle(
            Group(foil_cards, *continuation_marks[1:]),
            color=MGREY,
            stroke_width=1.5,
            buff=0.10,
            corner_radius=0.06,
        )
        target_label = Tex(r"Targets", color=INK, font_size=24).next_to(target_rect, UP, buff=0.12)
        foil_label = Tex(r"Foils", color=INK, font_size=24).next_to(foil_rect, UP, buff=0.12)
        arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
        dissimilar_arrow = Arrow(
            start=np.array([target_rect.get_center()[0] - 0.20, arrow_y, 0.0]),
            end=np.array([foil_rect.get_right()[0] - 0.10, arrow_y, 0.0]),
            buff=0.0,
            stroke_width=2.0,
            color=MGREY,
            tip_length=0.18,
            max_stroke_width_to_length_ratio=8,
            max_tip_length_to_length_ratio=0.10,
        )
        dissimilar_text = Tex(
            r"More dissimilar",
            color=MGREY,
            font_size=22,
        ).next_to(dissimilar_arrow, DOWN, buff=0.10)

        self.add(
            title,
            question,
            *collapsed_cards,
            *continuation_marks,
            target_rect,
            foil_rect,
            target_label,
            foil_label,
            dissimilar_arrow,
            dissimilar_text,
        )

        frame_side = 1.75
        right_margin_x = config.frame_width / 2 - 0.35
        stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
        stage_center_y = 0.5 * (row_y_positions[1] + row_y_positions[2])
        right_center = np.array([stage_center_x, stage_center_y, 0.0])

        lake_prefix = "landscape_element_lake_island"
        lake_row = lookup[("landscape_element", "lake_island")]
        target_idx = int(lake_row["target_position"])
        probe1_idx = int(lake_row["distractor_3_position"])
        probe2_idx = target_idx

        def stage_content(
    kind: str,
    center: np.ndarray,
    large: bool,
        ) -> Group:
            image_height = 0.95 if large else 0.44
            fixation_height = 0.18 if large else 0.06

            if kind == "target":
                img = stimulus_image(lake_prefix, target_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind == "probe1":
                img = stimulus_image(lake_prefix, probe1_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind == "probe2":
                img = stimulus_image(lake_prefix, probe2_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind in {"delay", "buffer", "iti"}:
                fix = fixation_on(center, height=fixation_height)
                return Group(fix)

            if kind == "response":
                response_size = 18 if large else 8
                response_buff = 0.14 if large else 0.04

                fix = fixation_on(center, height=fixation_height)

                left_text = Tex(
                    r"TWO",
                    color=INK,
                    font_size=response_size,
                ).next_to(fix, LEFT, buff=response_buff)

                right_text = Tex(
                    r"ONE",
                    color=INK,
                    font_size=response_size,
                ).next_to(fix, RIGHT, buff=response_buff)

                # ── Arrow under "TWO" ─────────────────────────────
                arrow_length = 0.40 if large else 0.20
                arrow = Arrow(
                    start=left_text.get_center() + RIGHT * (arrow_length / 2),
                    end=left_text.get_center() + LEFT * (arrow_length / 2),
                    color=INK,
                    stroke_width=10 if large else 4,
                    buff=0,
                    tip_length=0.3 if large else 0.10,
                )

                arrow.next_to(left_text, DOWN, buff=0.06 if large else 0.035)

                # z-order
                fix.set_z_index(8 if large else 6)
                left_text.set_z_index(8 if large else 6)
                right_text.set_z_index(8 if large else 6)
                arrow.set_z_index(8 if large else 6)
            
                return Group(left_text, fix, right_text, arrow)

        stage_specs = [
            ("2s", "Target", "target"),
            ("8s", "Delay", "delay"),
            ("1s", "Probe 1", "probe1"),
            ("0.5s", "Buffer", "buffer"),
            ("1s", "Probe 2", "probe2"),
            ("2s", "Response", "response"),
            ("(M=4s)", "ITI", "iti"),
        ]

        stage_frame = RoundedRectangle(
            corner_radius=0.12,
            width=frame_side,
            height=frame_side,
            stroke_color=MGREY,
            stroke_width=1.6,
        ).move_to(right_center)
        stage_frame.set_fill(WHITE, opacity=1.0)
        stage_duration = Tex(stage_specs[0][0], color=INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
        stage_label = Tex(stage_specs[0][1], color=INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)

        strip_side = 0.82
        strip_gap = 0.10
        strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
        quadrant_bottom_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1])
        strip_start_y = quadrant_bottom_y + strip_side / 2
        strip_final_y = right_center[1] - 0.12
        strip_start_centers = [
            np.array(
                [
                    right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                    strip_start_y,
                    0.0,
                ]
            )
            for i in range(len(stage_specs))
        ]
        strip_final_centers = [
            np.array(
                [
                    right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                    strip_final_y,
                    0.0,
                ]
            )
            for i in range(len(stage_specs))
        ]

        parked_cards = []
        for (_, _, kind), center in zip(stage_specs, strip_start_centers):
            parked_frame = RoundedRectangle(
                corner_radius=0.08,
                width=strip_side,
                height=strip_side,
                stroke_color=MGREY,
                stroke_width=1.2,
            ).move_to(center)
            parked_frame.set_fill(WHITE, opacity=1.0)
            parked_content = stage_content(kind, center, large=False)
            parked_group = Group(parked_frame, parked_content)
            parked_group.set_z_index(6)
            parked_cards.append(parked_group)

        strip_arrow_start_x = strip_start_centers[0][0] - strip_side / 2
        strip_arrow_y = ValueTracker(strip_start_y - strip_side / 2 - 0.18)
        strip_arrow_progress_x = ValueTracker(strip_arrow_start_x + 0.04)
        progress_arrow = always_redraw(
            lambda: Arrow(
                start=np.array([strip_arrow_start_x, strip_arrow_y.get_value(), 0.0]),
                end=np.array(
                    [
                        max(strip_arrow_progress_x.get_value(), strip_arrow_start_x + 0.04),
                        strip_arrow_y.get_value(),
                        0.0,
                    ]
                ),
                color=LGREY,
                stroke_width=1.3,
                buff=0.0,
                tip_length=0.14,
            )
        )

        target_copy = lake_target_card.copy()
        target_copy.move_to(lake_target_card.get_center())
        target_copy.set_z_index(8)
        target_copy.generate_target()
        target_copy.target.set_height(0.95)
        target_copy.target.move_to(right_center)
        target_fixation = fixation_on(right_center, height=0.18)
        active_content = Group(target_copy, target_fixation)

        self.play(
            Create(stage_frame),
            MoveToTarget(target_copy),
            FadeIn(target_fixation),
            FadeIn(stage_duration),
            FadeIn(stage_label),
            run_time=0.80,
        )
        self.add(progress_arrow)
        self.wait(0.20)

        hold_before_park = 1
        park_run_time = 0.4
        hold_after_park = 0.08

        for idx, (duration, label, kind) in enumerate(stage_specs):
            self.wait(hold_before_park)

            self.play(
                TransformFromCopy(Group(stage_frame, active_content), parked_cards[idx]),
                strip_arrow_progress_x.animate.set_value(parked_cards[idx].get_right()[0]),
                run_time=park_run_time,
            )

            self.wait(hold_after_park)

            if idx == len(stage_specs) - 1:
                continue

            next_duration = Tex(stage_specs[idx + 1][0], color=INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
            next_label = Tex(stage_specs[idx + 1][1], color=INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)
            next_kind = stage_specs[idx + 1][2]
            step_run_time = 0.5

            if next_kind in ("probe1", "probe2"):
                source_card = lake_d3_card if next_kind == "probe1" else lake_target_card
                highlight_rect = SurroundingRectangle(
                    source_card,
                    color="#F63924",
                    stroke_width=2.5,
                    buff=0.06,
                    corner_radius=0.05,
                )
                highlight_rect.set_z_index(9)
                self.play(FadeIn(highlight_rect), run_time=0.25)
                self.wait(0.10)
                probe_copy = source_card.copy()
                probe_copy.move_to(source_card.get_center())
                probe_copy.set_z_index(8)
                probe_copy.generate_target()
                probe_copy.target.set_height(0.95)
                probe_copy.target.move_to(right_center)
                probe_fix = fixation_on(right_center, height=0.18)
                next_content = Group(probe_copy, probe_fix)
                self.play(
                    FadeOut(active_content, shift=DOWN * 0.06),
                    FadeOut(highlight_rect),
                    MoveToTarget(probe_copy),
                    FadeIn(probe_fix),
                    ReplacementTransform(stage_duration, next_duration),
                    ReplacementTransform(stage_label, next_label),
                    run_time=0.90,
                )
            else:
                next_content = stage_content(next_kind, right_center, large=True)
                self.play(
                    FadeOut(active_content, shift=DOWN * 0.06),
                    FadeIn(next_content, shift=UP * 0.06),
                    ReplacementTransform(stage_duration, next_duration),
                    ReplacementTransform(stage_label, next_label),
                    run_time=step_run_time,
                )
            active_content = next_content
            stage_duration = next_duration
            stage_label = next_label
            self.wait(0.30 if next_kind == "delay" else 0.18)

        left_panel = Group(
            *collapsed_cards,
            continuation_marks,
            target_rect,
            foil_rect,
            target_label,
            foil_label,
            dissimilar_arrow,
            dissimilar_text,
        )

        final_arrow_y = min(strip_final_y - (strip_side * 1.12) / 2 - 0.20, right_center[1] - 1.15)
        promotion_anims = [
            parked.animate.move_to(target_center)
            for parked, target_center in zip(parked_cards, strip_final_centers)
        ]
        self.play(
            FadeOut(active_content, shift=UP * 0.06),
            FadeOut(stage_frame, shift=UP * 0.06),
            FadeOut(stage_duration, shift=UP * 0.06),
            FadeOut(stage_label, shift=UP * 0.06),
            left_panel.animate.scale(0.80),
            strip_arrow_y.animate.set_value(final_arrow_y),
            *promotion_anims,
            run_time=0.85,
        )

        final_duration_labels = VGroup(
            *[
                Tex(duration, color=INK, font_size=16).next_to(card, UP, buff=0.10)
                for (duration, _, _), card in zip(stage_specs, parked_cards)
            ]
        )
        final_stage_labels = VGroup(
            *[
                Tex(label, color=INK, font_size=16).next_to(card, DOWN, buff=0.10)
                for (_, label, _), card in zip(stage_specs, parked_cards)
            ]
        )
        time_label = MathTex("t", color=INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.10)

        self.play(
            LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_duration_labels], lag_ratio=0.05),
            LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_stage_labels], lag_ratio=0.05),
            FadeIn(time_label, shift=RIGHT * 0.05),
            run_time=1.00,
        )
        self.wait(1.00)



class Study1Stage3MemoryExpDesignB(Scene):
    """Difficulty labels, N=240, and block structure — sequel to ExpDesignA."""

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Replicate ExpDesignA layout (static, no animation) ───────────────
        title = Tex(r"Memory validation task", color=INK, font_size=40).to_edge(UP, buff=0.28)
        question = VGroup(
            Tex(r"Does proximity along the perceptual continua", color=INK, font_size=26),
            Tex(r"of our image sets predict memory performance?", color=INK, font_size=26),
        ).arrange(DOWN, buff=0.10).next_to(title, DOWN, buff=0.24)

        lookup = load_stimulus_lookup()
        set_specs = [
            ("plant", "pine_med"),
            ("landscape_element", "lake_island"),
            ("building", "observatory"),
            ("item", "sofa"),
        ]
        question_bottom_y = question.get_bottom()[1]
        row_spacing = 1.05
        bottom_margin_y = -config.frame_height / 2 + 0.55
        row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
        row_y_positions = [row_block_center_y + row_spacing * o for o in (1.5, 0.5, -0.5, -1.5)]
        left_column_center_x = -config.frame_width / 4
        selected_spacing = 1.05
        selected_xs = [left_column_center_x + selected_spacing * o for o in (-1.5, -0.5, 0.5, 1.5)]

        collapsed_cards: list = []
        bottom_continuation_marks: list = []
        for (category, obj), row_y in zip(set_specs, row_y_positions):
            row = lookup[(category, obj)]
            prefix = f"{category}_{obj}"
            selected_indices = [
                int(row["target_position"]),
                int(row["distractor_1_position"]),
                int(row["distractor_2_position"]),
                int(row["distractor_3_position"]),
            ]
            for col_idx, stim_idx in enumerate(selected_indices):
                card = stimulus_image(prefix, stim_idx, 0.56, (selected_xs[col_idx], row_y, 0.0))
                card.scale(1.45)
                card.set_z_index(5)
                collapsed_cards.append(card)
                if obj == "sofa":
                    dot = MathTex(r"\vdots", color=MGREY, font_size=24).next_to(card, DOWN, buff=0.19)
                    dot.set_z_index(5)
                    bottom_continuation_marks.append(dot)

        target_cards = Group(*collapsed_cards[0::4])
        foil_cards = Group(*[collapsed_cards[i] for i in range(len(collapsed_cards)) if i % 4 != 0])
        continuation_marks = VGroup(*bottom_continuation_marks)

        target_rect = SurroundingRectangle(
            Group(target_cards, continuation_marks[0]), color=MGREY, stroke_width=1.5, buff=0.10, corner_radius=0.06,
        )
        foil_rect = SurroundingRectangle(
            Group(foil_cards, *continuation_marks[1:]), color=MGREY, stroke_width=1.5, buff=0.10, corner_radius=0.06,
        )
        target_label = Tex(r"Targets", color=INK, font_size=24).next_to(target_rect, UP, buff=0.12)
        foil_label   = Tex(r"Foils",   color=INK, font_size=24).next_to(foil_rect,   UP, buff=0.12)
        arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
        dissimilar_arrow = Arrow(
            start=np.array([target_rect.get_center()[0] - 0.20, arrow_y, 0.0]),
            end=np.array([foil_rect.get_right()[0] - 0.10, arrow_y, 0.0]),
            buff=0.0, stroke_width=2.0, color=MGREY, tip_length=0.18,
            max_stroke_width_to_length_ratio=8, max_tip_length_to_length_ratio=0.10,
        )
        dissimilar_text = Tex(r"More dissimilar", color=MGREY, font_size=22).next_to(
            dissimilar_arrow, DOWN, buff=0.10
        )

        # ── Stage strip (placed directly at final positions) ─────────────────
        frame_side = 1.75
        right_margin_x = config.frame_width / 2 - 0.35
        stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
        stage_center_y = 0.5 * (row_y_positions[1] + row_y_positions[2])
        right_center = np.array([stage_center_x, stage_center_y, 0.0])

        lake_prefix = "landscape_element_lake_island"
        lake_row    = lookup[("landscape_element", "lake_island")]
        target_idx  = int(lake_row["target_position"])
        probe1_idx  = int(lake_row["distractor_3_position"])
        probe2_idx  = target_idx

        def stage_content(kind: str, center: np.ndarray, large: bool) -> Group:
            image_height    = 0.95 if large else 0.44
            fixation_height = 0.18 if large else 0.06
            if kind == "target":
                img = stimulus_image(lake_prefix, target_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                return Group(img, fixation_on(img, height=fixation_height))
            if kind == "probe1":
                img = stimulus_image(lake_prefix, probe1_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                return Group(img, fixation_on(img, height=fixation_height))
            if kind == "probe2":
                img = stimulus_image(lake_prefix, probe2_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                return Group(img, fixation_on(img, height=fixation_height))
            if kind in {"delay", "buffer", "iti"}:
                return Group(fixation_on(center, height=fixation_height))
            # response
            response_size = 18 if large else 8
            response_buff = 0.14 if large else 0.04
            fix        = fixation_on(center, height=fixation_height)
            left_text  = Tex(r"TWO", color=INK, font_size=response_size).next_to(fix, LEFT,  buff=response_buff)
            right_text = Tex(r"ONE", color=INK, font_size=response_size).next_to(fix, RIGHT, buff=response_buff)
            arrow_len  = 0.40 if large else 0.20
            arr = Arrow(
                start=left_text.get_center() + RIGHT * (arrow_len / 2),
                end=left_text.get_center()   + LEFT  * (arrow_len / 2),
                color=INK, stroke_width=10 if large else 4, buff=0,
                tip_length=0.3 if large else 0.10,
            )
            arr.next_to(left_text, DOWN, buff=0.06 if large else 0.035)
            for m in (fix, left_text, right_text, arr):
                m.set_z_index(8 if large else 6)
            return Group(left_text, fix, right_text, arr)

        stage_specs = [
            ("2s",     "Target",   "target"),
            ("8s",     "Delay",    "delay"),
            ("1s",     "Probe 1",  "probe1"),
            ("0.5s",   "Buffer",   "buffer"),
            ("1s",     "Probe 2",  "probe2"),
            ("2s",     "Response", "response"),
            ("(M=4s)", "ITI",      "iti"),
        ]

        strip_side  = 0.82
        strip_gap   = 0.10
        strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
        strip_final_y = right_center[1] - 0.12
        strip_final_centers = [
            np.array([
                right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                strip_final_y,
                0.0,
            ])
            for i in range(len(stage_specs))
        ]

        parked_cards = []
        for (_, _, kind), center in zip(stage_specs, strip_final_centers):
            pf = RoundedRectangle(corner_radius=0.08, width=strip_side, height=strip_side,
                                  stroke_color=MGREY, stroke_width=1.2).move_to(center)
            pf.set_fill(WHITE, opacity=1.0)
            pc = stage_content(kind, center, large=False)
            pg = Group(pf, pc)
            pg.set_z_index(6)
            parked_cards.append(pg)

        final_duration_labels = VGroup(*[
            Tex(dur, color=INK, font_size=16).next_to(card, UP, buff=0.10)
            for (dur, _, _), card in zip(stage_specs, parked_cards)
        ])
        final_stage_labels = VGroup(*[
            Tex(lbl, color=INK, font_size=16).next_to(card, DOWN, buff=0.10)
            for (_, lbl, _), card in zip(stage_specs, parked_cards)
        ])

        final_arrow_y = min(strip_final_y - (strip_side * 1.12) / 2 - 0.20, right_center[1] - 1.15)
        strip_arrow_start_x = right_center[0] - strip_total_width / 2
        progress_arrow = Arrow(
            start=np.array([strip_arrow_start_x, final_arrow_y, 0.0]),
            end=np.array([right_center[0] + strip_total_width / 2, final_arrow_y, 0.0]),
            color=LGREY, stroke_width=1.3, buff=0.0, tip_length=0.14,
        )
        time_label = MathTex("t", color=INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.10)

        left_panel = Group(
            *collapsed_cards, continuation_marks,
            target_rect, foil_rect,
            target_label, foil_label,
            dissimilar_arrow, dissimilar_text,
        )
        left_panel.scale(0.80)   # match end-state of ExpDesignA

        self.add(
            title, question,
            *collapsed_cards, *continuation_marks,
            target_rect, foil_rect,
            target_label, foil_label,
            dissimilar_arrow, dissimilar_text,
            *parked_cards,
            final_duration_labels, final_stage_labels,
            progress_arrow, time_label,
        )

        # ── Difficulty labels ────────────────────────────────────────────────
        self.play(
            dissimilar_arrow.animate.shift(DOWN * 0.38),
            dissimilar_text.animate.shift(DOWN * 0.38),
            FadeOut(foil_rect),
            run_time=0.65,
        )

        foil_cols = [
            Group(*[collapsed_cards[4 * r + c] for r in range(4)], continuation_marks[c])
            for c in (1, 2, 3)
        ]
        for diff_label, color, col_group in [
            ("Hard",   "#C94040", foil_cols[0]),
            ("Medium", "#C87137", foil_cols[1]),
            ("Easy",   "#3A7EC8", foil_cols[2]),
        ]:
            col_rect = SurroundingRectangle(
                col_group, color=color, stroke_width=1.8, buff=0.08, corner_radius=0.06,
            )
            lbl = Tex(diff_label, color=color, font_size=22).next_to(col_group, DOWN, buff=0.18)
            self.play(Create(col_rect), FadeIn(lbl, shift=UP * 0.08), run_time=0.55)
            self.wait(0.35)

        self.wait(0.30)

        # ── N and block structure (under the strip) ──────────────────────────
        stats_block = VGroup(
            Tex(r"$N = 240$", color=INK, font_size=22),
            Tex(
                r"6 blocks $\cdot$ half repeated, half new targets per block",
                color=MGREY, font_size=20,
            ),
        ).arrange(DOWN, buff=0.12)
        timeline_bottom = min(
            final_stage_labels.get_bottom()[1],
            time_label.get_bottom()[1],
            progress_arrow.get_bottom()[1],
        )
        stats_block.align_to(final_stage_labels, LEFT)
        stats_block.set_y(timeline_bottom - stats_block.get_height() / 2 - 0.32)

        self.play(
            LaggedStart(
                FadeIn(stats_block[0], shift=UP * 0.08),
                FadeIn(stats_block[1], shift=UP * 0.08),
                lag_ratio=0.35,
            ),
            run_time=0.80,
        )
        self.wait(1.00)


class Study1Stage3MemoryExpResults(Scene):
    """Show the behavioural results of the memory validation task."""

    AGG_IMG   = str(REPO_ROOT / "assets" / "images" / "study1_stage3" / "behavior_agg_manim.svg")
    BLOCK_IMG = str(REPO_ROOT / "assets" / "images" / "study1_stage3" / "behaviour_block_manim.svg")

    def construct(self) -> None:
        self.camera.background_color = BG

        def build_expdesignb_final_frame() -> Group:
            title = Tex(r"Memory validation task", color=INK, font_size=40).to_edge(UP, buff=0.28)
            question = VGroup(
                Tex(r"Does proximity along the perceptual continua", color=INK, font_size=26),
                Tex(r"of our image sets predict memory performance?", color=INK, font_size=26),
            ).arrange(DOWN, buff=0.10).next_to(title, DOWN, buff=0.24)

            lookup = load_stimulus_lookup()
            set_specs = [
                ("plant", "pine_med"),
                ("landscape_element", "lake_island"),
                ("building", "observatory"),
                ("item", "sofa"),
            ]
            question_bottom_y = question.get_bottom()[1]
            row_spacing = 1.05
            bottom_margin_y = -config.frame_height / 2 + 0.55
            row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
            row_y_positions = [row_block_center_y + row_spacing * o for o in (1.5, 0.5, -0.5, -1.5)]
            left_column_center_x = -config.frame_width / 4
            selected_spacing = 1.05
            selected_xs = [left_column_center_x + selected_spacing * o for o in (-1.5, -0.5, 0.5, 1.5)]

            collapsed_cards: list[Mobject] = []
            bottom_continuation_marks: list[Mobject] = []
            for (category, obj), row_y in zip(set_specs, row_y_positions):
                row = lookup[(category, obj)]
                prefix = f"{category}_{obj}"
                selected_indices = [
                    int(row["target_position"]),
                    int(row["distractor_1_position"]),
                    int(row["distractor_2_position"]),
                    int(row["distractor_3_position"]),
                ]
                for col_idx, stim_idx in enumerate(selected_indices):
                    card = stimulus_image(prefix, stim_idx, 0.56, (selected_xs[col_idx], row_y, 0.0))
                    card.scale(1.45)
                    card.set_z_index(5)
                    collapsed_cards.append(card)
                    if obj == "sofa":
                        dot = MathTex(r"\vdots", color=MGREY, font_size=24).next_to(card, DOWN, buff=0.19)
                        dot.set_z_index(5)
                        bottom_continuation_marks.append(dot)

            target_cards = Group(*collapsed_cards[0::4])
            foil_cards = Group(*[collapsed_cards[i] for i in range(len(collapsed_cards)) if i % 4 != 0])
            continuation_marks = VGroup(*bottom_continuation_marks)
            target_rect = SurroundingRectangle(
                Group(target_cards, continuation_marks[0]),
                color=MGREY,
                stroke_width=1.5,
                buff=0.10,
                corner_radius=0.06,
            )
            foil_rect = SurroundingRectangle(
                Group(foil_cards, *continuation_marks[1:]),
                color=MGREY,
                stroke_width=1.5,
                buff=0.10,
                corner_radius=0.06,
            )
            target_label = Tex(r"Targets", color=INK, font_size=24).next_to(target_rect, UP, buff=0.12)
            foil_label = Tex(r"Foils", color=INK, font_size=24).next_to(foil_rect, UP, buff=0.12)
            arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
            dissimilar_arrow = Arrow(
                start=np.array([target_rect.get_center()[0] - 0.20, arrow_y, 0.0]),
                end=np.array([foil_rect.get_right()[0] - 0.10, arrow_y, 0.0]),
                buff=0.0,
                stroke_width=2.0,
                color=MGREY,
                tip_length=0.18,
                max_stroke_width_to_length_ratio=8,
                max_tip_length_to_length_ratio=0.10,
            )
            dissimilar_text = Tex(r"More dissimilar", color=MGREY, font_size=22).next_to(
                dissimilar_arrow, DOWN, buff=0.10
            )

            frame_side = 1.75
            right_margin_x = config.frame_width / 2 - 0.35
            stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
            stage_center_y = 0.5 * (row_y_positions[1] + row_y_positions[2])
            right_center = np.array([stage_center_x, stage_center_y, 0.0])

            lake_prefix = "landscape_element_lake_island"
            lake_row = lookup[("landscape_element", "lake_island")]
            target_idx = int(lake_row["target_position"])
            probe1_idx = int(lake_row["distractor_3_position"])
            probe2_idx = target_idx

            def stage_content(kind: str, center: np.ndarray) -> Group:
                image_height = 0.44
                fixation_height = 0.06
                if kind == "target":
                    img = stimulus_image(lake_prefix, target_idx, image_height, center)
                    img.set_z_index(6)
                    return Group(img, fixation_on(img, height=fixation_height))
                if kind == "probe1":
                    img = stimulus_image(lake_prefix, probe1_idx, image_height, center)
                    img.set_z_index(6)
                    return Group(img, fixation_on(img, height=fixation_height))
                if kind == "probe2":
                    img = stimulus_image(lake_prefix, probe2_idx, image_height, center)
                    img.set_z_index(6)
                    return Group(img, fixation_on(img, height=fixation_height))
                if kind in {"delay", "buffer", "iti"}:
                    return Group(fixation_on(center, height=fixation_height))

                fix = fixation_on(center, height=fixation_height)
                left_text = Tex(r"TWO", color=INK, font_size=8).next_to(fix, LEFT, buff=0.04)
                right_text = Tex(r"ONE", color=INK, font_size=8).next_to(fix, RIGHT, buff=0.04)
                arr = Arrow(
                    start=left_text.get_center() + RIGHT * 0.10,
                    end=left_text.get_center() + LEFT * 0.10,
                    color=INK,
                    stroke_width=4,
                    buff=0,
                    tip_length=0.10,
                )
                arr.next_to(left_text, DOWN, buff=0.035)
                for mob in (fix, left_text, right_text, arr):
                    mob.set_z_index(6)
                return Group(left_text, fix, right_text, arr)

            stage_specs = [
                ("2s", "Target", "target"),
                ("8s", "Delay", "delay"),
                ("1s", "Probe 1", "probe1"),
                ("0.5s", "Buffer", "buffer"),
                ("1s", "Probe 2", "probe2"),
                ("2s", "Response", "response"),
                ("(M=4s)", "ITI", "iti"),
            ]
            strip_side = 0.82
            strip_gap = 0.10
            strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
            strip_final_y = right_center[1] - 0.12
            strip_final_centers = [
                np.array([
                    right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                    strip_final_y,
                    0.0,
                ])
                for i in range(len(stage_specs))
            ]

            parked_cards = []
            for (_, _, kind), center in zip(stage_specs, strip_final_centers):
                pf = RoundedRectangle(
                    corner_radius=0.08,
                    width=strip_side,
                    height=strip_side,
                    stroke_color=MGREY,
                    stroke_width=1.2,
                ).move_to(center)
                pf.set_fill(WHITE, opacity=1.0)
                pg = Group(pf, stage_content(kind, center))
                pg.set_z_index(6)
                parked_cards.append(pg)

            final_duration_labels = VGroup(*[
                Tex(dur, color=INK, font_size=16).next_to(card, UP, buff=0.10)
                for (dur, _, _), card in zip(stage_specs, parked_cards)
            ])
            final_stage_labels = VGroup(*[
                Tex(lbl, color=INK, font_size=16).next_to(card, DOWN, buff=0.10)
                for (_, lbl, _), card in zip(stage_specs, parked_cards)
            ])

            final_arrow_y = min(strip_final_y - (strip_side * 1.12) / 2 - 0.20, right_center[1] - 1.15)
            strip_arrow_start_x = right_center[0] - strip_total_width / 2
            progress_arrow = Arrow(
                start=np.array([strip_arrow_start_x, final_arrow_y, 0.0]),
                end=np.array([right_center[0] + strip_total_width / 2, final_arrow_y, 0.0]),
                color=LGREY,
                stroke_width=1.3,
                buff=0.0,
                tip_length=0.14,
            )
            time_label = MathTex("t", color=INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.10)

            left_panel = Group(
                *collapsed_cards,
                continuation_marks,
                target_rect,
                foil_rect,
                target_label,
                foil_label,
                dissimilar_arrow,
                dissimilar_text,
            )
            left_panel.scale(0.80)
            dissimilar_arrow.shift(DOWN * 0.38)
            dissimilar_text.shift(DOWN * 0.38)

            foil_cols = [
                Group(*[collapsed_cards[4 * r + c] for r in range(4)], continuation_marks[c])
                for c in (1, 2, 3)
            ]
            diff_groups = []
            for diff_label, color, col_group in [
                ("Hard", "#C94040", foil_cols[0]),
                ("Medium", "#C87137", foil_cols[1]),
                ("Easy", "#3A7EC8", foil_cols[2]),
            ]:
                col_rect = SurroundingRectangle(
                    col_group, color=color, stroke_width=1.8, buff=0.08, corner_radius=0.06
                )
                lbl = Tex(diff_label, color=color, font_size=22).next_to(col_group, DOWN, buff=0.18)
                diff_groups.append(Group(col_rect, lbl))

            stats_block = VGroup(
                Tex(r"$N = 240$", color=INK, font_size=22),
                Tex(
                    r"6 blocks $\cdot$ half repeated, half new targets per block",
                    color=MGREY,
                    font_size=20,
                ),
            ).arrange(DOWN, buff=0.12)
            timeline_bottom = min(
                final_stage_labels.get_bottom()[1],
                time_label.get_bottom()[1],
                progress_arrow.get_bottom()[1],
            )
            stats_block.align_to(final_stage_labels, LEFT)
            stats_block.set_y(timeline_bottom - stats_block.height / 2 - 0.32)

            return Group(
                title,
                question,
                *collapsed_cards,
                continuation_marks,
                target_rect,
                target_label,
                foil_label,
                dissimilar_arrow,
                dissimilar_text,
                *parked_cards,
                final_duration_labels,
                final_stage_labels,
                progress_arrow,
                time_label,
                *diff_groups,
                stats_block,
            )

        previous_scene = build_expdesignb_final_frame()
        self.add(previous_scene)
        self.wait(0.20)

        # ── Title ────────────────────────────────────────────────────────────
        title = Tex(r"Memory validation results", color=INK, font_size=40).to_edge(UP, buff=0.28)

        # ── Plots ────────────────────────────────────────────────────────────
        plot_height = 0.7 * (2 * config.frame_height / 3)
        agg_img = load_visible_svg(self.AGG_IMG, height=plot_height)
        block_img = load_visible_svg(self.BLOCK_IMG, height=plot_height)
        restore_agg_nonrepeated_dashes(agg_img)
        plots = VGroup(agg_img, block_img).arrange(RIGHT, buff=0.85)
        max_plot_area_width = config.frame_width - 0.80
        if plots.width > max_plot_area_width:
            plots.scale_to_fit_width(max_plot_area_width)

        agg_caption = Tex(
            r"Lower accuracy for more similar\\target--foil pairs",
            color=INK,
            font_size=22,
        )
        block_caption = Tex(
            r"Repetition benefited\\working memory performance",
            color=INK,
            font_size=22,
        )

        plot_vertical_shift = 0.3 * plot_height
        plot_top_y = title.get_bottom()[1] - 0.45 - plot_vertical_shift
        plots.set_y(plot_top_y - plots.height / 2)
        plots.set_x(0)

        agg_labels = build_agg_tex_overlays(agg_img)
        block_labels = build_block_tex_overlays(block_img)
        agg_plot = VGroup(agg_img, agg_labels)
        block_plot = VGroup(block_img, block_labels)

        panel_width = max(agg_plot.width, block_plot.width)
        for caption in (agg_caption, block_caption):
            if caption.width > panel_width * 0.94:
                caption.scale_to_fit_width(panel_width * 0.94)

        agg_caption.next_to(agg_plot, DOWN, buff=0.30)
        block_caption.next_to(block_plot, DOWN, buff=0.30)
        panels = VGroup(agg_plot, agg_caption, block_plot, block_caption)

        # ── Bottom takeaway ──────────────────────────────────────────────────
        conclusion = Tex(
            r"Stimulus set captured a perceptual continuum.",
            color=INK,
            font_size=28,
        )
        conclusion.next_to(panels, DOWN, buff=0.55)

        # ── Fade in scene ─────────────────────────────────────────────────────
        self.play(
            FadeOut(previous_scene, shift=DOWN * 0.08),
            FadeIn(title, shift=UP * 0.10),
            run_time=0.80,
        )
        self.play(FadeIn(agg_plot, shift=UP * 0.08), run_time=0.75)
        self.play(Write(agg_caption), run_time=0.60)
        self.wait(0.15)
        self.play(FadeIn(block_plot, shift=UP * 0.08), run_time=0.75)
        self.play(Write(block_caption), run_time=0.60)
        self.wait(0.35)
        self.play(FadeIn(conclusion, shift=UP * 0.06), run_time=0.55)
        self.wait(1.20)
