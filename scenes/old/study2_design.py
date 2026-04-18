"""
Study 2 — Experimental Design.

  Study2ExperimentalDesign — two-session paradigm diagram:
      Session 1: Memory task    (Target → Delay → Probe 1 → Buffer → Probe 2 → Response → ITI)
      Session 2: Perceptual task (Stimulus 1 → ISI → Stimulus 2 → ISI → Stimulus 3)

Render:
    uv run manim scenes/study2_design.py Study2ExperimentalDesign -qh
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from manim import *

REPO_ROOT = Path(__file__).resolve().parents[2]
_STUDY2_ASSET_DIR = REPO_ROOT / "assets" / "images" / "study2"
_STUDY2_STIM_DIR = _STUDY2_ASSET_DIR / "stimuli_task"

# ── Palette ───────────────────────────────────────────────────────────────────
BG   = WHITE
INK  = "#1C1C1E"
GREY = "#D1D5DB"   # box border only

# ── Image paths ───────────────────────────────────────────────────────────────
_STIM   = _STUDY2_STIM_DIR
LAKE    = str(_STIM / "LAN-LAK-T00.png")
LAKE_D1 = str(_STIM / "LAN-LAK-D01.png")
LAKE_D2 = str(_STIM / "LAN-LAK-D02.png")
PINE    = str(_STIM / "PLA-PIN-T00.png")
OBS     = str(_STIM / "BUI-OBS-T00.png")
FIX     = str(REPO_ROOT / "assets" / "images" / "fixation_target.png")

# ── Layout constants ──────────────────────────────────────────────────────────
BOX_W    = 1.18    # box width
BOX_H    = 1.18    # box height
CORNER   = 0.15    # corner radius
IMG_H    = 0.98    # stimulus image height inside box
FIX_H    = 0.10    # fixation dot height (overlaid on every box)
GAP      = 0.28    # horizontal gap between boxes
S1_Y     = 1.72    # vertical centre, Session 1 row
S2_Y     = -1.72   # vertical centre, Session 2 row
TL_Y_OFF = -0.78   # timeline offset below row centre
LBL_SIZE = 18      # phase label font size (below timeline)
TIME_SIZE = 16     # time label font size (above boxes)
TTL_SIZE = 30      # section title font size


def _box(img_path: str | None, resp: bool = False) -> Group:
    """
    Rounded rect + optional stimulus image + fixation dot always overlaid.
    resp=True → add 'TWO  ONE' text overlay (Response phase).
    """
    rect = RoundedRectangle(
        width=BOX_W, height=BOX_H,
        corner_radius=CORNER,
        stroke_color=GREY,
        stroke_width=1.8,
    ).set_fill(WHITE, opacity=1.0)

    parts: list = [rect]

    if img_path is not None:
        img = ImageMobject(img_path).set_height(IMG_H)
        img.move_to(rect.get_center())
        parts.append(img)

    # Fixation dot on every box
    fix = ImageMobject(FIX).set_height(FIX_H)
    fix.move_to(rect.get_center())
    parts.append(fix)

    if resp:
        two = Tex("TWO", color=INK, font_size=13).move_to(rect.get_center() + LEFT  * 0.30)
        one = Tex("ONE", color=INK, font_size=13).move_to(rect.get_center() + RIGHT * 0.30)
        parts.extend([two, one])

    return Group(*parts)


def _build_row(specs: list[dict], row_y: float) -> tuple[list[Group], list[float]]:
    """Return (boxes, x_centres) for a row of trial-phase boxes centred at x=0."""
    n       = len(specs)
    total_w = n * BOX_W + (n - 1) * GAP
    x0      = -total_w / 2 + BOX_W / 2

    boxes, xs = [], []
    for i, sp in enumerate(specs):
        x = x0 + i * (BOX_W + GAP)
        b = _box(sp.get("img"), sp.get("resp", False))
        b.move_to(RIGHT * x + UP * row_y)
        boxes.append(b)
        xs.append(x)
    return boxes, xs


_DOT_SPACING = 0.20
_DOT_RADIUS  = 0.030
_DOT_COLOR   = "#9CA3AF"


def _ellipsis(xs: list[float], row_y: float) -> tuple[VGroup, float]:
    """
    Three small grey dots after the last box.
    Returns (dots_vgroup, x_of_last_dot) so the timeline can extend to them.
    """
    x_start = xs[-1] + BOX_W / 2 + GAP * 0.65
    dots = VGroup(*[
        Dot(radius=_DOT_RADIUS, color=_DOT_COLOR, fill_opacity=1.0)
        .move_to(RIGHT * (x_start + i * _DOT_SPACING) + UP * row_y)
        for i in range(3)
    ])
    return dots, x_start + 2 * _DOT_SPACING


def _timeline(xs: list[float], row_y: float, x_end: float) -> tuple[Arrow, Tex]:
    """Horizontal arrow from before the first box to just past the last dot."""
    tl_y  = row_y + TL_Y_OFF
    x_l   = xs[0] - BOX_W / 2 - 0.08
    x_r   = x_end + _DOT_RADIUS + 0.20
    arrow = Arrow(
        RIGHT * x_l + UP * tl_y,
        RIGHT * x_r + UP * tl_y,
        color=INK, stroke_width=1.5, buff=0,
        tip_length=0.18, tip_shape=StealthTip,
    )
    t_lbl = Tex(r"$t$", color=INK, font_size=22).next_to(arrow.get_end(), RIGHT, buff=0.07)
    return arrow, t_lbl


def _labels(
    specs: list[dict], xs: list[float], row_y: float
) -> tuple[VGroup, VGroup]:
    """Time labels (above boxes) and phase labels (below timeline)."""
    tl_y      = row_y + TL_Y_OFF
    time_grp  = VGroup()
    phase_grp = VGroup()
    for sp, x in zip(specs, xs):
        t = Tex(sp["time"], color=INK, font_size=TIME_SIZE) \
            .move_to(RIGHT * x + UP * (row_y + BOX_H / 2 + 0.24))
        p = Tex(sp["lbl"],  color=INK, font_size=LBL_SIZE) \
            .move_to(RIGHT * x + UP * (tl_y - 0.27))
        time_grp.add(t)
        phase_grp.add(p)
    return time_grp, phase_grp


# ── Shared time string for jittered ITI / ISI ─────────────────────────────────
_JITTER = r"$M = 4\,\mathrm{s}$"


class Study2ExperimentalDesign(Scene):

    _S1 = [
        {"img": LAKE,    "time": "2 s",     "lbl": "Target"},
        {"img": None,    "time": "8 s",     "lbl": "Delay"},
        {"img": LAKE_D1, "time": "1 s",     "lbl": "Probe 1"},
        {"img": None,    "time": "0.5 s",   "lbl": "Buffer"},
        {"img": LAKE_D2, "time": "1 s",     "lbl": "Probe 2"},
        {"img": None,    "time": "2 s",     "lbl": "Response", "resp": True},
        {"img": None,    "time": _JITTER,   "lbl": "ITI"},
    ]

    _S2 = [
        {"img": LAKE, "time": "2 s",    "lbl": "Stimulus 1"},
        {"img": None, "time": _JITTER,  "lbl": "ISI"},
        {"img": PINE, "time": "2 s",    "lbl": "Stimulus 2"},
        {"img": None, "time": _JITTER,  "lbl": "ISI"},
        {"img": OBS,  "time": "2 s",    "lbl": "Stimulus 3"},
    ]

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Session 1 ──────────────────────────────────────────────────────────
        s1_title = Tex(
            r"\textbf{Session 1 :} Memory task",
            color=INK, font_size=TTL_SIZE,
        ).move_to(UP * 3.05)

        boxes1, xs1       = _build_row(self._S1, S1_Y)
        dots1, x_end1     = _ellipsis(xs1, S1_Y)
        arrow1, t1        = _timeline(xs1, S1_Y, x_end1)
        time_lbl1, ph_lb1 = _labels(self._S1, xs1, S1_Y)

        self.play(Write(s1_title), run_time=0.6)
        self.play(
            LaggedStartMap(FadeIn, Group(*boxes1), lag_ratio=0.10),
            run_time=1.1,
        )
        self.play(
            Create(arrow1), Write(t1),
            FadeIn(time_lbl1), FadeIn(ph_lb1),
            run_time=0.7,
        )
        self.play(
            LaggedStartMap(FadeIn, dots1, lag_ratio=0.2),
            run_time=0.4,
        )
        self.wait(0.5)

        # ── Session 2 ──────────────────────────────────────────────────────────
        s2_title = Tex(
            r"\textbf{Session 2 :} Perceptual task",
            color=INK, font_size=TTL_SIZE,
        ).move_to(UP * (S2_Y + BOX_H / 2 + 0.74))

        boxes2, xs2       = _build_row(self._S2, S2_Y)
        dots2, x_end2     = _ellipsis(xs2, S2_Y)
        arrow2, t2        = _timeline(xs2, S2_Y, x_end2)
        time_lbl2, ph_lb2 = _labels(self._S2, xs2, S2_Y)

        self.play(Write(s2_title), run_time=0.6)
        self.play(
            LaggedStartMap(FadeIn, Group(*boxes2), lag_ratio=0.13),
            run_time=0.9,
        )
        self.play(
            Create(arrow2), Write(t2),
            FadeIn(time_lbl2), FadeIn(ph_lb2),
            run_time=0.7,
        )
        self.play(
            LaggedStartMap(FadeIn, dots2, lag_ratio=0.2),
            run_time=0.4,
        )
        n_lbl = Tex(r"$N = 42$ participants", color=INK, font_size=18) \
            .to_edge(DOWN, buff=0.38)
        slide_title = Tex(r"\textbf{Session 2 :} Perceptual task", color=INK, font_size=TTL_SIZE).move_to(UP * 3.05)
        self.play(FadeIn(n_lbl), run_time=0.5)
        self.wait(2.0)


# ══════════════════════════════════════════════════════════════════════════════
# Study2DecodingOverview
# ══════════════════════════════════════════════════════════════════════════════

_D_BLUE  = "#2563EB"
_D_AMBER = "#D97706"
_D_GREEN = "#16A34A"
_D_RED   = "#DC2626"
_D_PURP  = "#7C3AED"
_D_CYAN  = "#0891B2"
_D_LGREY = "#D1D5DB"
_D_MGREY = "#9CA3AF"

# Brain icon used in the decoding overview
_BRAIN_PNG_PATH = _STUDY2_ASSET_DIR / "brain_icon_sagittal.png"


class Study2DecodingOverview(Scene):
    """
    Opens on the full experimental-design layout, isolates the Session 2
    stimuli, and then maps each image to a coloured feature vector via a
    brain icon and activity-pattern matrix.

    Render:
        uv run manim scenes/study2_design.py Study2DecodingOverview -qh
    """

    # Three S2 stimulus colours (matching Stimulus 1/2/3 order)
    _COLS = [_D_BLUE, _D_AMBER, _D_GREEN]

    # Target column (left side, after transition)
    _COL_X  = -5.50
    _COL_YS = [1.20, 0.00, -1.20]
    _STACK_SCALE = 0.86

    # Brain / vector layout
    _BRAIN_Y = 0.00
    _H_GAP   = 1.15

    # Activity matrix shown below the brain before becoming a feature vector
    _GRID_PAT = np.array([[0.9, 0.2, 0.7],
                          [0.3, 0.8, 0.1],
                          [0.5, 0.4, 0.9]])
    _GRID_PERMS = [
        np.array([0, 1, 2, 3, 4, 5, 6, 7, 8]),
        np.array([2, 6, 0, 7, 4, 8, 1, 5, 3]),
        np.array([8, 3, 6, 1, 4, 7, 2, 5, 0]),
        np.array([1, 4, 7, 0, 8, 5, 2, 6, 3]),
        np.array([5, 0, 8, 2, 6, 1, 7, 3, 4]),
        np.array([6, 2, 5, 8, 1, 4, 0, 3, 7]),
    ]
    _GRID_CS  = 0.22
    _GRID_GAP = 0.035
    _VEC_CS   = 0.17
    _VEC_GAP  = 0.055
    _ROLLING_TARGETS = [
        (str(_STIM / "ANI-CAT-T00.png"), _D_RED),
        (str(_STIM / "ITE-VAS-T00.png"), _D_PURP),
        (str(_STIM / "PLA-BRI-T00.png"), _D_CYAN),
    ]

    def _pattern_for_index(self, idx: int) -> np.ndarray:
        flat = self._GRID_PAT.flatten()
        return flat[self._GRID_PERMS[idx]].reshape(self._GRID_PAT.shape)

    def _make_grid(self, center: np.ndarray, col: str, pattern: np.ndarray) -> VGroup:
        step = self._GRID_CS + self._GRID_GAP
        group = VGroup()
        for r in range(3):
            for c in range(3):
                v = float(pattern[r, c])
                sq = Square(
                    side_length=self._GRID_CS,
                    stroke_width=0.7,
                    stroke_color=_D_LGREY,
                ).set_fill(
                    interpolate_color(
                        ManimColor(WHITE), ManimColor(col), 0.10 + 0.90 * v
                    ),
                    opacity=1.0,
                )
                sq.move_to(
                    center
                    + RIGHT * (c - 1) * step
                    + UP    * (1 - r) * step
                )
                group.add(sq)
        return group

    def _make_feature_vector(self, center: np.ndarray, col: str, pattern: np.ndarray) -> VGroup:
        step = self._VEC_CS + self._VEC_GAP
        group = VGroup()
        for i, v in enumerate(pattern.flatten()):
            cell = Square(
                side_length=self._VEC_CS,
                stroke_width=0.7,
                stroke_color=_D_LGREY,
            ).set_fill(
                interpolate_color(
                    ManimColor(WHITE), ManimColor(col), 0.10 + 0.90 * float(v)
                ),
                opacity=1.0,
            )
            cell.move_to(center + RIGHT * (i - 4) * step)
            group.add(cell)
        return group

    def _make_grid_frame(self, grid: VGroup, center: np.ndarray) -> Rectangle:
        return Rectangle(
            width=grid.width,
            height=grid.height,
            stroke_color=_D_MGREY,
            stroke_width=1.8,
        ).move_to(center)

    def _brain_source_point(
        self, brain: ImageMobject, x_norm: float = 0.6, y_norm: float = 0.0
    ) -> np.ndarray:
        """Map normalized [-1, 1] image coordinates to scene coordinates."""
        return (
            brain.get_center()
            + RIGHT * (0.5 * x_norm * brain.width)
            + UP * (0.5 * y_norm * brain.height)
        )

    # ── Scene ─────────────────────────────────────────────────────────────────

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Phase 0: Start from the full experimental-design end state ─────────
        s1_title = Tex(
            r"\textbf{Session 1 :} Memory task",
            color=INK, font_size=TTL_SIZE,
        ).move_to(UP * 3.05)

        boxes1, xs1       = _build_row(Study2ExperimentalDesign._S1, S1_Y)
        dots1, x_end1     = _ellipsis(xs1, S1_Y)
        arrow1, t1        = _timeline(xs1, S1_Y, x_end1)
        time_lbl1, ph_lb1 = _labels(Study2ExperimentalDesign._S1, xs1, S1_Y)

        _S2 = [
            {"img": LAKE, "time": "2 s",   "lbl": "Stimulus 1"},
            {"img": None, "time": _JITTER, "lbl": "ISI"},
            {"img": PINE, "time": "2 s",   "lbl": "Stimulus 2"},
            {"img": None, "time": _JITTER, "lbl": "ISI"},
            {"img": OBS,  "time": "2 s",   "lbl": "Stimulus 3"},
        ]
        boxes2, xs2       = _build_row(_S2, S2_Y)
        dots2, x_end2     = _ellipsis(xs2, S2_Y)
        arrow2, t2        = _timeline(xs2, S2_Y, x_end2)
        time_lbl2, ph_lb2 = _labels(_S2, xs2, S2_Y)

        s2_title = Tex(
            r"\textbf{Session 2 :} Perceptual task",
            color=INK, font_size=TTL_SIZE,
        ).move_to(UP * (S2_Y + BOX_H / 2 + 0.74))
        slide_title = Tex(
            r"\textbf{Session 2 :} Perceptual task",
            color=INK,
            font_size=TTL_SIZE,
        ).move_to(UP * 3.05)

        n_lbl = Tex(r"$N = 42$ participants", color=INK, font_size=18) \
            .to_edge(DOWN, buff=0.38)

        self.add(
            s1_title, Group(*boxes1), dots1, arrow1, t1, time_lbl1, ph_lb1,
            s2_title, Group(*boxes2), dots2, arrow2, t2, time_lbl2, ph_lb2,
            n_lbl,
        )
        self.wait(0.4)

        # Stimulus boxes are at indices 0, 2, 4; ISIs at 1, 3
        stim_boxes = [boxes2[0], boxes2[2], boxes2[4]]
        isi_boxes  = [boxes2[1], boxes2[3]]
        stim_rects = [box[0] for box in stim_boxes]
        stim_icons = [Group(box[1], box[2]) for box in stim_boxes]
        session1_group = Group(
            s1_title, Group(*boxes1), dots1, arrow1, t1, time_lbl1, ph_lb1,
        )

        # ── Phase 1: Highlight stimuli ─────────────────────────────────────────
        highlights = VGroup(*[
            SurroundingRectangle(
                b, color=col, stroke_width=3.0, buff=0.06, corner_radius=0.12,
            )
            for b, col in zip(stim_boxes, self._COLS)
        ])
        self.play(
            LaggedStartMap(Create, highlights, lag_ratio=0.15),
            run_time=0.65,
        )
        self.wait(0.25)

        # ── Phase 2: Fade non-stimuli; move stimuli to left column ─────────────
        self.play(
            FadeOut(session1_group),
            FadeOut(Group(*isi_boxes)),
            FadeOut(dots2), FadeOut(arrow2), FadeOut(t2),
            FadeOut(time_lbl2), FadeOut(ph_lb2),
            FadeOut(n_lbl),
            run_time=0.5,
        )

        stim_box_targets = [
            box.copy().scale(self._STACK_SCALE).move_to(RIGHT * self._COL_X + UP * ry)
            for box, ry in zip(stim_boxes, self._COL_YS)
        ]
        moving_highlights = VGroup(*[
            SurroundingRectangle(
                target_box, color=col, stroke_width=3.0, buff=0.06, corner_radius=0.12,
            )
            for target_box, col in zip(stim_box_targets, self._COLS)
        ])

        self.play(
            *[
                box.animate.scale(self._STACK_SCALE).move_to(RIGHT * self._COL_X + UP * ry)
                for box, ry in zip(stim_boxes, self._COL_YS)
            ],
            *[
                Transform(highlight, moving_highlight)
                for highlight, moving_highlight in zip(highlights, moving_highlights)
            ],
            Transform(s2_title, slide_title),
            run_time=0.85,
        )

        # Keep the same coloured frame and let it travel with the image while
        # the grey trial card outline disappears.
        stacked_highlights = VGroup(*[
            SurroundingRectangle(
                icon, color=col, stroke_width=2.4, buff=0.05, corner_radius=0.10,
            )
            for icon, col in zip(stim_icons, self._COLS)
        ])
        self.play(
            *[
                rect.animate.set_stroke(opacity=0).set_fill(opacity=0)
                for rect in stim_rects
            ],
            *[
                Transform(highlight, stacked_highlight)
                for highlight, stacked_highlight in zip(highlights, stacked_highlights)
            ],
            run_time=0.45,
        )
        self.wait(0.3)

        # ── Phase 3: Brain icon is twice the stimulus-icon height ──────────────
        icon_h = max(icon.height for icon in stim_icons)
        brain = (
            ImageMobject(str(_BRAIN_PNG_PATH))
            .set_height(2.0 * icon_h)
            .move_to(UP * self._BRAIN_Y)
        )
        brain.set_z_index(-20)
        vector_template = self._make_feature_vector(
            ORIGIN, self._COLS[0], self._pattern_for_index(0)
        )
        stack_right = max(highlight.get_right()[0] for highlight in highlights)
        brain_x = stack_right + self._H_GAP + brain.width / 2
        vector_left_x = brain_x + brain.width / 2 + self._H_GAP
        vector_center_x = vector_left_x + vector_template.width / 2
        brain.move_to(np.array([brain_x, self._BRAIN_Y, 0.0]))
        self.play(FadeIn(brain, shift=RIGHT * 0.15), run_time=0.75)
        self.bring_to_back(brain)
        self.wait(0.25)

        # ── Phase 4: Each image maps to a feature vector ───────────────────────
        matrix_center = brain.get_bottom() + DOWN * 0.58
        matrix_source = self._brain_source_point(brain, x_norm=0.7, y_norm=-0.1)
        vector_centers = [
            np.array([vector_center_x, row_y, 0.0]) for row_y in self._COL_YS
        ]
        visible_vectors: list[VGroup] = []
        matrix_template = self._make_grid(matrix_center, self._COLS[0], self._pattern_for_index(0))
        matrix_frame = self._make_grid_frame(matrix_template, matrix_center)
        source_frame = self._make_grid_frame(matrix_template, matrix_source).scale(0.56)
        source_label = Tex("V1-V3", color=_D_MGREY, font_size=20).next_to(source_frame, RIGHT, buff=0.10)
        projection_lines = VGroup(
            Line(
                source_frame.get_corner(UL),
                matrix_frame.get_corner(UL),
                color=_D_MGREY,
                stroke_width=1.1,
            ),
            Line(
                source_frame.get_corner(UR),
                matrix_frame.get_corner(UR),
                color=_D_MGREY,
                stroke_width=1.1,
            ),
            Line(
                source_frame.get_corner(DL),
                matrix_frame.get_corner(DL),
                color=_D_MGREY,
                stroke_width=1.1,
            ),
            Line(
                source_frame.get_corner(DR),
                matrix_frame.get_corner(DR),
                color=_D_MGREY,
                stroke_width=1.1,
            ),
        )
        projection_lines.set_z_index(-10)
        matrix_frame.set_z_index(1)
        source_frame.set_z_index(2)
        source_label.set_z_index(2)
        source_frame_base_width = source_frame.get_stroke_width()
        source_frame_pulse_width = source_frame_base_width * 1.8
        current_grid: VGroup | None = None

        def synced_source_pulse(t: float) -> float:
            if t <= 0.12:
                return 0.0
            return there_and_back((t - 0.12) / 0.88)

        def vector_layout(count: int) -> list[np.ndarray]:
            ys = np.linspace(self._COL_YS[0], self._COL_YS[2], count)
            return [np.array([vector_center_x, float(y), 0.0]) for y in ys]

        vector_label = Tex("Feature vectors", color=_D_MGREY, font_size=24).move_to(
            np.array([vector_center_x, self._COL_YS[0] + 0.52, 0.0])
        )

        for idx, (icon, col, vec_center) in enumerate(zip(stim_icons, self._COLS, vector_centers)):
            pattern = self._pattern_for_index(idx)
            arr_to_brain = Arrow(
                icon.get_right() + RIGHT * 0.12,
                brain.get_left() + LEFT * 0.10,
                color=_D_MGREY,
                stroke_width=2.0,
                buff=0.02,
                tip_length=0.16,
            )
            self.play(GrowArrow(arr_to_brain), run_time=0.45)

            new_grid = self._make_grid(matrix_center, col, pattern)
            if current_grid is None:
                self.add(projection_lines)
                self.bring_to_back(projection_lines)
                projection_lines.set_stroke(opacity=0.0)
                self.play(FadeIn(source_frame, scale=0.94), run_time=0.22)
                self.play(
                    FadeIn(source_label),
                    FadeIn(matrix_frame),
                    projection_lines.animate.set_stroke(opacity=1.0),
                    run_time=0.36,
                )
                self.wait(0.12)
                self.play(FadeIn(new_grid), FadeOut(matrix_frame), run_time=0.40)
                self.play(FadeOut(projection_lines), run_time=0.18)
                current_grid = new_grid
            else:
                self.play(
                    source_frame.animate(rate_func=synced_source_pulse).set_stroke(
                        width=source_frame_pulse_width
                    ),
                    ReplacementTransform(current_grid, new_grid),
                    run_time=0.32,
                )
                source_frame.set_stroke(width=source_frame_base_width)
                current_grid = new_grid

            arr_to_vec = Arrow(
                current_grid.get_right() + RIGHT * 0.04,
                vec_center + LEFT * (vector_template.width / 2 + 0.18),
                color=_D_MGREY,
                stroke_width=2.0,
                buff=0.03,
                tip_length=0.16,
            )
            self.play(GrowArrow(arr_to_vec), run_time=0.40)

            vector = self._make_feature_vector(vec_center, col, pattern)
            grid_copy = current_grid.copy()
            self.add(grid_copy)
            if idx == 0:
                self.play(FadeIn(vector_label), ReplacementTransform(grid_copy, vector), run_time=0.70)
            else:
                self.play(ReplacementTransform(grid_copy, vector), run_time=0.70)
            self.play(FadeOut(arr_to_brain), FadeOut(arr_to_vec), run_time=0.20)
            visible_vectors.append(vector)

        # ── Phase 5: Roll new targets into the left column and decode them ────
        row_step = self._COL_YS[0] - self._COL_YS[1]
        icon_center_x = stim_icons[0].get_center()[0]
        icon_img_h = stim_icons[0][0].height
        icon_fix_h = stim_icons[0][1].height

        def make_stack_target(img_path: str, col: str) -> tuple[Group, SurroundingRectangle]:
            img = ImageMobject(img_path).set_height(icon_img_h)
            fix = ImageMobject(FIX).set_height(icon_fix_h).move_to(img.get_center())
            icon = Group(img, fix)
            frame = SurroundingRectangle(
                icon, color=col, stroke_width=2.4, buff=0.05, corner_radius=0.10,
            )
            return icon, frame

        visible_icons: list[Group] = list(stim_icons)
        visible_frames: list[VMobject] = list(highlights)
        ghost_icon: Group | None = None
        ghost_frame: VMobject | None = None
        ghost_y = self._COL_YS[0] + row_step * 1.02

        for idx, (target_path, col) in enumerate(self._ROLLING_TARGETS, start=3):
            new_icon, new_frame = make_stack_target(target_path, col)
            new_icon.move_to(np.array([icon_center_x, self._COL_YS[-1] - row_step, 0.0]))
            new_frame.move_to(new_icon.get_center())
            self.add(new_icon, new_frame)

            future_vector_centers = vector_layout(len(visible_vectors) + 1)
            old_top_icon = visible_icons[0]
            old_top_frame = visible_frames[0]
            roll_anims = [
                old_top_icon[0].animate.move_to(np.array([icon_center_x, ghost_y, 0.0])).set_opacity(0.18),
                old_top_icon[1].animate.move_to(np.array([icon_center_x, ghost_y, 0.0])).set_opacity(0.18),
                old_top_frame.animate.move_to(np.array([icon_center_x, ghost_y, 0.0])).set_stroke(opacity=0.18),
                visible_icons[1].animate.move_to(np.array([icon_center_x, self._COL_YS[0], 0.0])),
                visible_frames[1].animate.move_to(np.array([icon_center_x, self._COL_YS[0], 0.0])),
                visible_icons[2].animate.move_to(np.array([icon_center_x, self._COL_YS[1], 0.0])),
                visible_frames[2].animate.move_to(np.array([icon_center_x, self._COL_YS[1], 0.0])),
                new_icon.animate.move_to(np.array([icon_center_x, self._COL_YS[2], 0.0])),
                new_frame.animate.move_to(np.array([icon_center_x, self._COL_YS[2], 0.0])),
            ]
            if ghost_icon is not None and ghost_frame is not None:
                roll_anims.extend([FadeOut(ghost_icon), FadeOut(ghost_frame)])
            roll_anims.extend([
                vector.animate.move_to(target_center)
                for vector, target_center in zip(visible_vectors, future_vector_centers[:-1])
            ])

            self.play(
                *roll_anims,
                run_time=0.55,
            )

            ghost_icon = old_top_icon
            ghost_frame = old_top_frame
            visible_icons = [visible_icons[1], visible_icons[2], new_icon]
            visible_frames = [visible_frames[1], visible_frames[2], new_frame]

            pattern = self._pattern_for_index(idx)
            arr_to_brain = Arrow(
                new_icon.get_right() + RIGHT * 0.12,
                brain.get_left() + LEFT * 0.10,
                color=_D_MGREY,
                stroke_width=2.0,
                buff=0.02,
                tip_length=0.16,
            )
            self.play(GrowArrow(arr_to_brain), run_time=0.45)

            new_grid = self._make_grid(matrix_center, col, pattern)
            self.play(
                source_frame.animate(rate_func=synced_source_pulse).set_stroke(
                    width=source_frame_pulse_width
                ),
                ReplacementTransform(current_grid, new_grid),
                run_time=0.32,
            )
            source_frame.set_stroke(width=source_frame_base_width)
            current_grid = new_grid

            arr_to_vec = Arrow(
                current_grid.get_right() + RIGHT * 0.04,
                future_vector_centers[-1] + LEFT * (vector_template.width / 2 + 0.18),
                color=_D_MGREY,
                stroke_width=2.0,
                buff=0.03,
                tip_length=0.16,
            )
            self.play(GrowArrow(arr_to_vec), run_time=0.40)

            vector = self._make_feature_vector(future_vector_centers[-1], col, pattern)
            grid_copy = current_grid.copy()
            self.add(grid_copy)
            self.play(ReplacementTransform(grid_copy, vector), run_time=0.70)
            self.play(FadeOut(arr_to_brain), FadeOut(arr_to_vec), run_time=0.20)
            visible_vectors.append(vector)
            self.wait(0.15)

        summary_matrix_x = vector_center_x + 3.85
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
        ).move_to(np.array([summary_group.get_center()[0] + 0.38, summary_matrix.get_center()[1] + 1.45, 0.0]))
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

        self.play(
            FadeIn(summary_title),
            FadeIn(summary_symbol),
            Write(summary_matrix),
            FadeIn(sample_arrow),
            FadeIn(sample_label),
            FadeIn(feature_arrow),
            FadeIn(feature_label),
            Indicate(VGroup(*visible_vectors), color=_D_MGREY, scale_factor=1.02),
            run_time=1.10,
        )

        self.wait(2.0)
