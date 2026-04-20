"""
Quick concept test for abstract sensory vs memory representations.

Usage:
    uv run manim scenes/intro_representation_test.py IntroRepresentationTest -ql
    uv run manim scenes/intro_representation_test.py IntroRepresentation3DTest -ql
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import REPO_ROOT


BG = WHITE
INK = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
PANEL = "#F8FAFC"
SENSORY = "#5F7D99"
MEMORY = "#977C6B"
EDGE = "#AEB8C2"
PATTERN_BLUE = "#4C72B0"
PATTERN_RED = "#C44E52"
PATTERN_WHITE = "#F8F8F8"
_MATRIX_CELL = 0.16

_FISH_T00 = REPO_ROOT / "assets" / "images" / "ANI-FIS-T00.jpeg"
_FISH_D03 = REPO_ROOT / "assets" / "images" / "ANI-FIS-D03.jpeg"
_FALLBACK_T00 = REPO_ROOT / "assets" / "images" / "stimuli_reordered" / "animal_fish-00.png"
_FALLBACK_D03 = REPO_ROOT / "assets" / "images" / "stimuli_reordered" / "animal_fish-03.png"
_HEAD_BRAIN = REPO_ROOT / "assets" / "images" / "head_brain.png"

def _seeded_pattern(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(-1.0, 1.0, size=(4, 4))


_SENSORY_PATTERN_LEFT = _seeded_pattern(11)
_MEMORY_PATTERN = _seeded_pattern(12)
_SENSORY_PATTERN_RIGHT = _seeded_pattern(13)


def _preferred_path(primary: Path, fallback: Path) -> str:
    return str(primary if primary.exists() else fallback)


def _pattern_color(value: float) -> ManimColor:
    clipped = max(-1.0, min(1.0, float(value)))
    if clipped < 0:
        return interpolate_color(ManimColor(PATTERN_WHITE), ManimColor(PATTERN_BLUE), abs(clipped))
    return interpolate_color(ManimColor(PATTERN_WHITE), ManimColor(PATTERN_RED), clipped)


def _mini_matrix(matrix: np.ndarray, *, cell: float = 0.12) -> VGroup:
    rows, cols = matrix.shape
    cells = VGroup()
    for row in range(rows):
        for col in range(cols):
            square = Square(
                side_length=cell,
                stroke_color=LGREY,
                stroke_width=0.35,
            ).set_fill(_pattern_color(matrix[row, col]), opacity=1.0)
            cells.add(square)
    cells.arrange_in_grid(rows=rows, cols=cols, buff=0.01)
    return cells


def _head_with_matrix(matrix: np.ndarray, *, scale: float = 0.90) -> Group:
    head = ImageMobject(str(_HEAD_BRAIN))
    head.scale_to_fit_height(2.55 * scale)
    head.set_opacity(1.0)
    mini = _mini_matrix(matrix, cell=_MATRIX_CELL * scale)
    mini.move_to(
        head.get_center()
        + LEFT * (0.035 * head.width)
        + UP * (0.18 * head.height)
    )
    return Group(head, mini)


def _framed_visual(
    inner: Mobject,
    *,
    width: float = 1.42,
    height: float = 1.42,
    corner_radius: float = 0.08,
) -> Group:
    card = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
        stroke_color=LGREY,
        stroke_width=1.5,
    ).set_fill(WHITE, opacity=1.0)
    inner.move_to(card.get_center())
    return Group(card, inner)


def _interpolate_matrix(a: np.ndarray, b: np.ndarray, alpha: float) -> np.ndarray:
    return (1.0 - alpha) * a + alpha * b


def _vec3(start, end, color, *, sw: float = 2.4, tl: float = 0.18) -> Arrow:
    return Arrow(
        np.asarray(start, dtype=float),
        np.asarray(end, dtype=float),
        color=color,
        stroke_width=sw,
        tip_length=tl,
        buff=0,
        max_stroke_width_to_length_ratio=100,
    )


def _panel(title: str, subtitle: str, *, width: float = 5.4, height: float = 5.3) -> tuple[VGroup, RoundedRectangle]:
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.18,
        stroke_color=LGREY,
        stroke_width=1.4,
    ).set_fill(PANEL, opacity=0.95)
    title_mob = Tex(title, color=INK, font_size=26)
    subtitle_mob = Tex(subtitle, color=MGREY, font_size=16)
    header = VGroup(title_mob, subtitle_mob).arrange(DOWN, buff=0.08)
    header.next_to(frame.get_top(), DOWN, buff=0.28)
    return VGroup(frame, header), frame


def _representation_network(
    center: np.ndarray,
    *,
    accent: str,
    compactness: float,
    recurrent: bool,
) -> dict[str, Mobject]:
    offsets = [
        np.array([-1.00, 0.45, 0.0]),
        np.array([-0.35, 0.95, 0.0]),
        np.array([0.45, 0.75, 0.0]),
        np.array([1.00, 0.15, 0.0]),
        np.array([0.60, -0.55, 0.0]),
        np.array([-0.10, -0.90, 0.0]),
        np.array([-0.95, -0.45, 0.0]),
    ]
    node_positions = [center + compactness * off for off in offsets]

    edge_pairs = [
        (0, 1), (1, 2), (2, 3),
        (0, 6), (6, 5), (5, 4), (4, 3),
        (1, 5), (2, 4), (0, 2),
    ]
    if recurrent:
        edge_pairs.extend([(1, 4), (2, 5), (0, 5)])

    edges = VGroup(
        *[
            Line(
                node_positions[a],
                node_positions[b],
                color=EDGE,
                stroke_width=2.0 if recurrent else 1.8,
                stroke_opacity=0.65 if recurrent else 0.55,
            )
            for a, b in edge_pairs
        ]
    )

    nodes = VGroup(
        *[
            Circle(
                radius=0.12 if idx in (1, 2, 5) else 0.10,
                stroke_color=accent,
                stroke_width=1.7,
            ).set_fill(accent, opacity=0.18 if idx in (1, 2, 5) else 0.10).move_to(pos)
            for idx, pos in enumerate(node_positions)
        ]
    )

    core = Ellipse(
        width=1.85 * compactness,
        height=1.30 * compactness,
        stroke_color=accent,
        stroke_width=1.6,
    ).set_fill(accent, opacity=0.08 if recurrent else 0.05).move_to(center + np.array([0.0, 0.05, 0.0]))

    recurrence = VGroup()
    if recurrent:
        recurrence = VGroup(
            CurvedArrow(
                center + np.array([0.75, 0.32, 0.0]),
                center + np.array([0.10, 0.88, 0.0]),
                angle=-1.1,
                color=accent,
                stroke_width=1.7,
                tip_length=0.12,
            ),
            CurvedArrow(
                center + np.array([-0.65, -0.30, 0.0]),
                center + np.array([0.05, -0.78, 0.0]),
                angle=-1.0,
                color=accent,
                stroke_width=1.7,
                tip_length=0.12,
            ),
        )
        recurrence.set_opacity(0.8)

    return {
        "group": VGroup(core, edges, nodes, recurrence),
        "nodes": nodes,
        "edges": edges,
        "core": core,
        "recurrence": recurrence,
    }


class IntroRepresentationTest(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        title = Tex(r"\textbf{Representation Motif Test}", color=INK, font_size=34).to_edge(UP, buff=0.28)

        left_panel, left_frame = _panel("sensory representation", "input-coupled pattern")
        right_panel, right_frame = _panel("memory representation", "internally sustained pattern")
        panels = VGroup(left_panel, right_panel).arrange(RIGHT, buff=0.46).move_to(DOWN * 0.10)

        stim = ImageMobject(_preferred_path(_FISH_T00, _FALLBACK_T00))
        stim.scale_to_fit_height(1.25)
        stim.move_to(left_frame.get_center() + np.array([0.0, 1.02, 0.0]))

        probe = ImageMobject(_preferred_path(_FISH_D03, _FALLBACK_D03))
        probe.scale_to_fit_height(1.25)
        probe.move_to(right_frame.get_center() + np.array([0.0, 1.02, 0.0]))
        probe.set_opacity(0.55)

        sensory_net = _representation_network(
            left_frame.get_center() + np.array([0.0, -0.35, 0.0]),
            accent=SENSORY,
            compactness=0.94,
            recurrent=False,
        )
        memory_net = _representation_network(
            right_frame.get_center() + np.array([0.0, -0.35, 0.0]),
            accent=MEMORY,
            compactness=0.78,
            recurrent=True,
        )

        sensory_arrow = Arrow(
            stim.get_bottom() + DOWN * 0.06,
            sensory_net["group"].get_top() + UP * 0.05,
            color=SENSORY,
            stroke_width=1.8,
            buff=0.08,
        )
        memory_badge = VGroup(
            Dot(radius=0.04, color=MEMORY),
            Tex("no stimulus present", color=MGREY, font_size=15),
        ).arrange(RIGHT, buff=0.10)
        memory_badge.move_to(right_frame.get_center() + np.array([0.0, 0.42, 0.0]))

        bridge_arrow = Arrow(
            sensory_net["group"].get_right() + RIGHT * 0.28,
            memory_net["group"].get_left() + LEFT * 0.28,
            color=MGREY,
            stroke_width=1.5,
            buff=0.0,
            tip_length=0.16,
            max_tip_length_to_length_ratio=0.10,
            max_stroke_width_to_length_ratio=2.0,
        )
        bridge_label = Tex("transformed carry-over", color=MGREY, font_size=16)
        bridge_label.next_to(bridge_arrow, UP, buff=0.14)
        bridge_t = MathTex("t", color=MGREY, font_size=24)
        bridge_t.next_to(bridge_label, UP, buff=0.10)

        self.play(FadeIn(title, shift=UP * 0.04), FadeIn(panels, shift=UP * 0.04), run_time=0.8)
        self.play(FadeIn(stim, scale=0.98), FadeIn(probe, scale=0.98), run_time=0.6)
        self.play(
            Create(sensory_arrow),
            FadeIn(sensory_net["core"], scale=0.96),
            LaggedStart(*[FadeIn(edge) for edge in sensory_net["edges"]], lag_ratio=0.08),
            LaggedStart(*[FadeIn(node, scale=0.9) for node in sensory_net["nodes"]], lag_ratio=0.06),
            run_time=1.15,
        )
        self.play(
            FadeIn(memory_badge, shift=UP * 0.03),
            FadeIn(memory_net["core"], scale=0.96),
            LaggedStart(*[FadeIn(edge) for edge in memory_net["edges"]], lag_ratio=0.08),
            LaggedStart(*[FadeIn(node, scale=0.9) for node in memory_net["nodes"]], lag_ratio=0.06),
            run_time=1.10,
        )
        self.play(
            Create(memory_net["recurrence"]),
            Create(bridge_arrow),
            FadeIn(bridge_label, shift=UP * 0.03),
            FadeIn(bridge_t, shift=UP * 0.03),
            run_time=0.9,
        )
        self.wait(2.5)


class IntroRepresentation3DTest(ThreeDScene):
    def construct(self) -> None:
        self.camera.background_color = BG
        self.set_camera_orientation(
            phi=62 * DEGREES,
            theta=-42 * DEGREES,
            frame_center=np.array([-0.3, 0.3, 0.0]),
            zoom=1.0,
        )

        x_step = 3.6
        x0 = np.array([-8.6, 0.0, 0.0])
        x1 = np.array([-x_step, 0.0, 0.0])
        x2 = np.array([0.0, 0.0, 0.0])
        x3 = np.array([x_step, 0.0, 0.0])
        x4 = np.array([4, 0.0, 0.0])

        step = 0.5
        grid_x_min, grid_x_max = -8.0, 5
        grid_y_min, grid_y_max = -7.0, 5
        grid = VGroup(
            *[
                line
                for k in np.arange(grid_y_min, grid_y_max + step * 0.5, step)
                for line in (
                    Line(
                        np.array([grid_x_min, k, 0.0]),
                        np.array([grid_x_max, k, 0.0]),
                        color=LGREY,
                        stroke_width=0.9,
                    ),
                    Line(
                        np.array([k, grid_y_min, 0.0]),
                        np.array([k, grid_y_max, 0.0]),
                        color=LGREY,
                        stroke_width=0.9,
                    ),
                )
            ]
        )
        grid.set_z_index(-20)

        axis_x = _vec3(x0, x4, MGREY, sw=2.4, tl=0.24)
        axis_x.set_z_index(-10)
        axis_y = _vec3(x0, [0.0, 4.8, 0.0], MGREY, sw=2.4, tl=0.24)
        axis_y.set_opacity(0.0)
        axis_y.set_z_index(-10)
        ticks = VGroup(
            *[
                Line(
                    point + np.array([0.0, -0.13, 0.0]),
                    point + np.array([0.0, 0.13, 0.0]),
                    color=LGREY,
                    stroke_width=2.0,
                )
                for point in (x1, x2, x3)
            ]
        )
        ticks.set_z_index(-5)

        rotation = self.camera.generate_rotation_matrix()
        screen_right = rotation.T @ np.array([1.0, 0.0, 0.0])
        screen_up = rotation.T @ np.array([0.0, 1.0, 0.0])
        screen_out = rotation.T @ np.array([0.0, 0.0, 1.0])
        screen_right /= np.linalg.norm(screen_right)
        screen_up /= np.linalg.norm(screen_up)
        screen_out /= np.linalg.norm(screen_out)

        def screen_aligned_point(
            anchor: np.ndarray,
            *,
            right: float = 0.0,
            up: float = 0.0,
            front: float = 0.0,
        ) -> np.ndarray:
            return (
                anchor
                + right * screen_right
                + up * screen_up
                + front * screen_out
            )

        def bottom_aligned_point(
            anchor: np.ndarray,
            mob: Mobject,
            *,
            right: float = 0.0,
            front: float = 0.0,
            gap: float = 0.0,
        ) -> np.ndarray:
            return screen_aligned_point(
                anchor,
                right=right,
                up=mob.height / 2 + gap,
                front=front,
            )

        axis_labels = VGroup(
            MathTex("t", color=MGREY, font_size=28).move_to(
                screen_aligned_point(x4, right=0.38, up=0.10)
            ),
        )
        axis_labels.set_z_index(15)
        travel = ValueTracker(0.0)
        x_past = np.array([-2 * x_step, 0.0, 0.0])
        x_future = np.array([2 * x_step, 0.0, 0.0])

        stim_left = _framed_visual(
            ImageMobject(_preferred_path(_FISH_T00, _FALLBACK_T00)).scale_to_fit_height(1.20)
        )
        stim_mid = _framed_visual(
            MathTex("+", color=MGREY, font_size=40),
        )
        stim_right = _framed_visual(
            ImageMobject(_preferred_path(_FISH_D03, _FALLBACK_D03)).scale_to_fit_height(1.20)
        )
        for stim in (stim_left, stim_mid, stim_right):
            stim.set_z_index(30)

        fixed_head = _head_with_matrix(_SENSORY_PATTERN_LEFT, scale=0.72)
        fixed_head.set_z_index(70)
        fixed_head[0].set_z_index(71)
        fixed_head[1].set_z_index(72)

        dot_gap = 0.72
        front_offset = 0.62

        def path_anchor(points: list[np.ndarray], t: float) -> np.ndarray:
            clipped = float(np.clip(t, 0.0, len(points) - 1))
            idx = min(int(np.floor(clipped)), len(points) - 2)
            alpha = clipped - idx
            return interpolate(points[idx], points[idx + 1], alpha)

        def place_card(mob: Mobject, anchor: np.ndarray) -> None:
            mob.move_to(
                bottom_aligned_point(
                    anchor,
                    mob,
                    right=(dot_gap + mob.width / 2),
                    front=front_offset,
                )
            )

        def place_head(mob: Mobject, anchor: np.ndarray) -> None:
            mob.move_to(
                bottom_aligned_point(
                    anchor,
                    mob,
                    right=-(dot_gap + mob.width / 2),
                    front=front_offset,
                )
            )

        left_path = [x2, x1, x_past]
        mid_path = [x3, x2, x1]
        right_path = [x_future, x3, x2]

        node_left = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0)
        node_mid = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0)
        node_right = Dot(radius=0.08, color=MGREY, fill_opacity=1.0, stroke_width=0.0)
        nodes = VGroup(node_left, node_mid, node_right)
        nodes.set_z_index(40)

        def current_matrix(t: float) -> np.ndarray:
            if t <= 1.0:
                return _interpolate_matrix(_SENSORY_PATTERN_LEFT, _MEMORY_PATTERN, np.clip(t, 0.0, 1.0))
            return _interpolate_matrix(_MEMORY_PATTERN, _SENSORY_PATTERN_RIGHT, np.clip(t - 1.0, 0.0, 1.0))

        def update_card(mob: Mobject, points: list[np.ndarray]) -> Mobject:
            place_card(mob, path_anchor(points, travel.get_value()))
            return mob

        def update_dot(mob: Mobject, points: list[np.ndarray]) -> Mobject:
            mob.move_to(path_anchor(points, travel.get_value()))
            return mob

        def update_fixed_head(mob: Mobject) -> Mobject:
            place_fixed_head(mob)
            new_matrix = _mini_matrix(current_matrix(travel.get_value()), cell=_MATRIX_CELL * 0.72)
            new_matrix.move_to(
                mob[0].get_center()
                + LEFT * (0.055 * mob[0].width)
                + UP * (0.23 * mob[0].height)
            )
            mob[1].become(new_matrix)
            return mob

        fixed_head_anchor = path_anchor(left_path, 0.0)

        def place_fixed_head(mob: Mobject) -> None:
            place_head(mob, fixed_head_anchor)

        place_card(stim_left, path_anchor(left_path, 0.0))
        place_card(stim_mid, path_anchor(mid_path, 0.0))
        place_card(stim_right, path_anchor(right_path, 0.0))
        place_fixed_head(fixed_head)
        update_dot(node_left, left_path)
        update_dot(node_mid, mid_path)
        update_dot(node_right, right_path)

        stim_left.add_updater(lambda mob: update_card(mob, left_path))
        stim_mid.add_updater(lambda mob: update_card(mob, mid_path))
        stim_right.add_updater(lambda mob: update_card(mob, right_path))
        node_left.add_updater(lambda mob: update_dot(mob, left_path))
        node_mid.add_updater(lambda mob: update_dot(mob, mid_path))
        node_right.add_updater(lambda mob: update_dot(mob, right_path))
        fixed_head.add_updater(update_fixed_head)

        self.add_fixed_orientation_mobjects(
            axis_labels,
            fixed_head,
            stim_left,
            stim_mid,
            stim_right,
        )

        self.play(Create(grid), run_time=0.7)
        self.play(
            Create(axis_x),
            Create(axis_y),
            Create(ticks),
            FadeIn(nodes),
            FadeIn(axis_labels, shift=UP * 0.03),
            run_time=1.0,
        )
        self.wait(0.5)
        self.play(travel.animate.set_value(1.0), run_time=2.3, rate_func=smooth)
        self.wait(0.55)
        self.play(travel.animate.set_value(2.0), run_time=2.3, rate_func=smooth)
        self.wait(1.0)
