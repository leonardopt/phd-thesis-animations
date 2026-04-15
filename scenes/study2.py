"""
Study 2.

  Study2ExperimentalDesign — two-session paradigm diagram
  Study2DecodingOverview   — Session 2 stimuli -> feature vectors -> sensory matrix
  Study2WithinSession2Decoding — crossvalidated prediction within Session 2
  Study2CrossSessionDecoding   — train on sensory, test on sensory and memory

Render:
    uv run manim scenes/study2.py Study2ExperimentalDesign -qh
    uv run manim scenes/study2.py Study2DecodingOverview -qh
    uv run manim scenes/study2.py Study2WithinSession2Decoding -qh
    uv run manim scenes/study2.py Study2CrossSessionDecoding -qh
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from manim import *

# ── Palette ───────────────────────────────────────────────────────────────────
BG   = WHITE
INK  = "#1C1C1E"
GREY = "#D1D5DB"   # box border only

# ── Image paths ───────────────────────────────────────────────────────────────
_STIM   = Path("/Users/leonardo/sd-wltm-fmri-experiment/images/stimuli_task")
LAKE    = str(_STIM / "LAN-LAK-T00.png")
LAKE_D1 = str(_STIM / "LAN-LAK-D01.png")
LAKE_D2 = str(_STIM / "LAN-LAK-D02.png")
PINE    = str(_STIM / "PLA-PIN-T00.png")
OBS     = str(_STIM / "BUI-OBS-T00.png")
CAT     = str(_STIM / "ANI-CAT-T00.png")
SOFA    = str(Path("/Users/leonardo/sd-wltm-fmri-experiment/images/stimuli_training/ITE-SOF-T00.png"))
FIX     = str(Path("/Users/leonardo/phd-thesis-animations/assets/images/fixation_target.png"))

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
_BRAIN_PNG_PATH = Path(
    "/Users/leonardo/phd-thesis-animations/assets/images/study2/brain_icon_sagittal.png"
)


class Study2DecodingOverview(Scene):
    """
    Opens on the full experimental-design layout, isolates the Session 2
    stimuli, and then maps each image to a coloured feature vector via a
    brain icon and activity-pattern matrix.

    Render:
        uv run manim scenes/study2.py Study2DecodingOverview -qh
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


# ══════════════════════════════════════════════════════════════════════════════
# Study2WithinSession2Decoding
# ══════════════════════════════════════════════════════════════════════════════


def _make_feature_row(
    values: np.ndarray,
    color: str = _D_BLUE,
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
            stroke_color=_D_LGREY,
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


class Study2WithinSession2Decoding(Study2DecodingOverview):
    """
    Starts from the previous end state, merges feature vectors into a
    samples x features matrix, and illustrates leave-one-run-out decoding.

    Render:
        uv run manim scenes/study2.py Study2WithinSession2Decoding -qh
    """

    _ROW_COLS = [_D_BLUE, _D_AMBER, _D_GREEN, _D_RED, _D_PURP, _D_CYAN]
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
        jitter = 0.05 * np.sin(
            np.arange(base.size) * 1.15 + 0.75 * run_idx + 0.35 * base_idx
        )
        return np.clip(0.84 * base + 0.16 * rolled + jitter, 0.08, 0.98)

    def _matrix_row_centers(self, x: float, y_shift: float = 0.0) -> list[np.ndarray]:
        row_h = 0.11
        row_gap = 0.025
        run_gap = 0.080
        block_h = 4 * row_h + 3 * row_gap
        total_h = 8 * block_h + 7 * run_gap
        top = total_h / 2 - row_h / 2
        centers: list[np.ndarray] = []
        for run_idx in range(8):
            block_top = top - run_idx * (block_h + run_gap)
            for row_idx in range(4):
                centers.append(
                    np.array([x, block_top - row_idx * (row_h + row_gap) + y_shift, 0.0])
                )
        return centers

    def _make_test_points(self, ax: Axes, fold_idx: int) -> VGroup:
        pts = [
            (
                -1.55 + 0.10 * np.sin(0.8 * fold_idx),
                0.74 + 0.08 * np.cos(1.1 * fold_idx),
                _D_BLUE,
            ),
            (
                -1.20 + 0.12 * np.cos(0.9 * fold_idx),
                -0.18 + 0.08 * np.sin(1.3 * fold_idx),
                _D_BLUE,
            ),
            (
                1.20 + 0.10 * np.cos(0.7 * fold_idx),
                0.52 + 0.10 * np.sin(1.0 * fold_idx),
                _D_AMBER,
            ),
            (
                1.62 + 0.12 * np.sin(1.2 * fold_idx),
                -0.56 + 0.08 * np.cos(0.85 * fold_idx),
                _D_AMBER,
            ),
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

        title = Tex(
            "Decoding object-identity during perception from early visual cortex",
            color=INK,
            font_size=30,
        )
        title.to_edge(UP, buff=0.35)

        stack_img_h = IMG_H * self._STACK_SCALE
        stack_fix_h = FIX_H * self._STACK_SCALE
        icon_center_x = self._COL_X
        row_step = self._COL_YS[0] - self._COL_YS[1]
        ghost_y = self._COL_YS[0] + row_step * 1.02

        def make_stack_icon(img_path: str) -> Group:
            img = ImageMobject(img_path).set_height(stack_img_h)
            fix = ImageMobject(FIX).set_height(stack_fix_h).move_to(img.get_center())
            return Group(img, fix)

        final_icon_paths = [path for path, _ in self._ROLLING_TARGETS]
        final_icon_cols = [_D_RED, _D_PURP, _D_CYAN]
        visible_icons = Group(*[
            make_stack_icon(path).move_to(np.array([icon_center_x, y, 0.0]))
            for path, y in zip(final_icon_paths, self._COL_YS)
        ])
        visible_frames = VGroup(*[
            SurroundingRectangle(
                icon, color=col, stroke_width=2.4, buff=0.05, corner_radius=0.10,
            )
            for icon, col in zip(visible_icons, final_icon_cols)
        ])
        ghost_icon = make_stack_icon(OBS).move_to(np.array([icon_center_x, ghost_y, 0.0]))
        ghost_icon[0].set_opacity(0.18)
        ghost_icon[1].set_opacity(0.18)
        ghost_frame = SurroundingRectangle(
            ghost_icon, color=_D_GREEN, stroke_width=2.4, buff=0.05, corner_radius=0.10,
        ).set_stroke(opacity=0.18)

        icon_h = max(icon.height for icon in visible_icons)
        brain = (
            ImageMobject(str(_BRAIN_PNG_PATH))
            .set_height(2.0 * icon_h)
            .move_to(UP * self._BRAIN_Y)
        )
        brain.set_z_index(-20)
        stack_right = max(frame.get_right()[0] for frame in visible_frames)
        vector_template = self._make_feature_vector(ORIGIN, self._COLS[0], self._pattern_for_index(0))
        brain_x = stack_right + self._H_GAP + brain.width / 2
        vector_left_x = brain_x + brain.width / 2 + self._H_GAP
        vector_center_x = vector_left_x + vector_template.width / 2
        brain.move_to(np.array([brain_x, self._BRAIN_Y, 0.0]))

        matrix_center = brain.get_bottom() + DOWN * 0.58
        matrix_source = self._brain_source_point(brain, x_norm=0.7, y_norm=-0.1)
        matrix_template = self._make_grid(matrix_center, self._COLS[0], self._pattern_for_index(0))
        source_frame = self._make_grid_frame(matrix_template, matrix_source).scale(0.56)
        source_frame.set_z_index(2)
        source_label = Tex("V1-V3", color=_D_MGREY, font_size=20).next_to(source_frame, RIGHT, buff=0.10)
        source_label.set_z_index(2)
        current_grid = self._make_grid(matrix_center, _D_CYAN, self._pattern_for_index(5))

        vector_centers = [
            np.array([vector_center_x, float(y), 0.0]) for y in np.linspace(self._COL_YS[0], self._COL_YS[2], 6)
        ]
        vector_cols = [_D_BLUE, _D_AMBER, _D_GREEN, _D_RED, _D_PURP, _D_CYAN]
        visible_vectors = VGroup(*[
            self._make_feature_vector(center, col, self._pattern_for_index(idx))
            for idx, (center, col) in enumerate(zip(vector_centers, vector_cols))
        ])
        vector_label = Tex("Feature vectors", color=_D_MGREY, font_size=24).move_to(
            np.array([vector_center_x, self._COL_YS[0] + 0.52, 0.0])
        )

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
        ).move_to(
            np.array([summary_group.get_center()[0], summary_matrix.get_center()[1] + 1.35, 0.0])
        )
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

        previous_context = Group(
            visible_icons,
            visible_frames,
            ghost_icon,
            ghost_frame,
            brain,
            source_frame,
            source_label,
            current_grid,
        )
        self.add(
            title,
            previous_context,
            visible_vectors,
            vector_label,
            summary_title,
            summary_matrix,
            sample_arrow,
            sample_label,
            feature_arrow,
            feature_label,
        )
        self.wait(0.45)

        matrix_x = -4.67
        row_centers = self._matrix_row_centers(matrix_x, y_shift=-0.18)
        target_rows = [
            _make_feature_row(
                self._row_values(global_idx % len(self._BASE_ROWS), global_idx // 4),
                color=self._ROW_COLS[global_idx % len(self._ROW_COLS)],
                cell_w=0.11,
                cell_h=0.11,
                gap=0.025,
            ).move_to(row_centers[global_idx])
            for global_idx in range(32)
        ]
        run_labels = VGroup(*[
            Tex(f"run {run_idx + 1}", color=_D_MGREY, font_size=16).next_to(
                VGroup(*target_rows[4 * run_idx : 4 * run_idx + 4]),
                LEFT,
                buff=0.52,
            )
            for run_idx in range(8)
        ])
        matrix_body = VGroup(*target_rows)
        bracket_h = matrix_body.height + 0.34
        bracket_arm = 0.13
        left_bracket = VGroup(
            Line(UP * (bracket_h / 2), DOWN * (bracket_h / 2), color=_D_LGREY, stroke_width=1.8),
            Line(UP * (bracket_h / 2) + RIGHT * bracket_arm, UP * (bracket_h / 2), color=_D_LGREY, stroke_width=1.8),
            Line(DOWN * (bracket_h / 2) + RIGHT * bracket_arm, DOWN * (bracket_h / 2), color=_D_LGREY, stroke_width=1.8),
        )
        right_bracket = VGroup(
            Line(UP * (bracket_h / 2), DOWN * (bracket_h / 2), color=_D_LGREY, stroke_width=1.8),
            Line(UP * (bracket_h / 2) + LEFT * bracket_arm, UP * (bracket_h / 2), color=_D_LGREY, stroke_width=1.8),
            Line(DOWN * (bracket_h / 2) + LEFT * bracket_arm, DOWN * (bracket_h / 2), color=_D_LGREY, stroke_width=1.8),
        )
        left_bracket.next_to(matrix_body, LEFT, buff=0.18)
        right_bracket.next_to(matrix_body, RIGHT, buff=0.18)
        summary_title_target = summary_title.copy().scale(0.86).next_to(
            VGroup(left_bracket, matrix_body, right_bracket), UP, buff=0.20
        )
        summary_matrix_target = summary_matrix.copy().move_to(matrix_body.get_center())

        self.play(
            FadeOut(previous_context),
            FadeOut(sample_arrow),
            FadeOut(sample_label),
            FadeOut(feature_arrow),
            FadeOut(feature_label),
            FadeOut(vector_label),
            FadeOut(summary_symbol),
            run_time=0.35,
        )

        self.play(
            summary_title.animate.move_to(summary_title_target.get_center()).scale(0.86),
            summary_matrix.animate.move_to(summary_matrix_target.get_center()),
            *[
                Transform(visible_vectors[idx], target_rows[idx])
                for idx in range(len(visible_vectors))
            ],
            run_time=0.95,
        )

        self.play(
            FadeTransform(summary_matrix, VGroup(left_bracket, right_bracket)),
            LaggedStart(
                *[FadeIn(row) for row in target_rows[len(visible_vectors):]],
                lag_ratio=0.03,
            ),
            LaggedStart(*[FadeIn(lbl) for lbl in run_labels], lag_ratio=0.05),
            run_time=0.9,
        )

        matrix_rows = [*visible_vectors, *target_rows[len(visible_vectors):]]
        matrix_shell = VGroup(*matrix_rows, left_bracket, right_bracket)

        matrix_mid_y = matrix_body.get_center()[1]
        svm_label = VGroup(
            Tex("Linear", color=INK, font_size=18),
            Tex(r"\textbf{Support Vector Machine}", color=INK, font_size=18),
            Tex("Classifier", color=INK, font_size=18),
        ).arrange(DOWN, buff=0.05).move_to(np.array([0.55, matrix_mid_y, 0.0]))
        svm_question = Tex(
            "How well can the classifier\\\\discriminate between object-scene\\\\representations during perception?",
            color=INK,
            font_size=17,
            tex_environment="center",
        ).next_to(svm_label, DOWN, buff=0.22)
        label_col_x = right_bracket.get_right()[0] + 0.58
        arrow_len = 0.77
        arrow_center_x = 0.5 * (label_col_x + 0.42 + svm_label.get_left()[0])
        data_arrow = Arrow(
            np.array([arrow_center_x - arrow_len / 2, matrix_mid_y, 0.0]),
            np.array([arrow_center_x + arrow_len / 2, matrix_mid_y, 0.0]),
            color=_D_MGREY,
            stroke_width=3.8,
            buff=0.02,
            tip_length=0.18,
        )

        plot_axis_config = {
            "color": _D_LGREY,
            "stroke_width": 1.4,
            "include_ticks": False,
            "include_tip": False,
        }
        train_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([4.80, 1.16, 0.0]))
        test_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([4.80, -1.12, 0.0]))
        train_title = Tex("training data", color=INK, font_size=18).next_to(train_ax, UP, buff=0.08)
        test_title = Tex("held-out test data", color=INK, font_size=18).next_to(test_ax, UP, buff=0.08)
        train_x_label = Tex("voxel 1", color=INK, font_size=15).next_to(train_ax, DOWN, buff=0.10)
        train_y_label = Tex("voxel 2", color=INK, font_size=15).rotate(PI / 2).next_to(
            train_ax, LEFT, buff=0.08
        )
        test_x_label = Tex("voxel 1", color=INK, font_size=15).next_to(test_ax, DOWN, buff=0.10)
        test_y_label = Tex("voxel 2", color=INK, font_size=15).rotate(PI / 2).next_to(
            test_ax, LEFT, buff=0.08
        )
        class_example_paths = [CAT, PINE, SOFA]
        class_cols = [_D_BLUE, _D_GREEN, _D_AMBER]
        class_examples = Group(*[
            Group(
                ImageMobject(path).set_height(0.42),
            )
            for path in class_example_paths
        ])
        for icon, col in zip(class_examples, class_cols):
            frame = SurroundingRectangle(
                icon[0],
                color=col,
                stroke_width=2.1,
                buff=0.04,
                corner_radius=0.06,
            )
            icon.add(frame)
            icon[1].move_to(icon[0].get_center())
        class_examples.arrange(DOWN, buff=0.10).move_to(np.array([3.00, 0.98, 0.0]))

        fold_misclassified = [
            [("blue", 3), ("amber", 1)],
            [("green", 0)],
            [("blue", 2), ("amber", 2)],
            [("blue", 3), ("green", 1), ("amber", 0)],
            [("green", 2)],
            [("blue", 2), ("amber", 1)],
            [("green", 0)],
            [("blue", 3), ("amber", 2)],
        ]
        fold_error_counts = [len(items) for items in fold_misclassified]
        fold_accuracy_tex = [
            rf"{int(round(100 * (12 - n_err) / 12))}\%"
            for n_err in fold_error_counts
        ]

        def _decision_shift(fold_idx: int) -> tuple[float, float]:
            return 0.07 * np.sin(0.72 * fold_idx), 0.05 * np.cos(0.86 * fold_idx)

        def _class_centers(fold_idx: int) -> dict[str, tuple[float, float]]:
            x_shift, y_shift = _decision_shift(fold_idx)
            return {
                "blue": (-1.25 + 0.15 * x_shift, -0.02 + 0.10 * y_shift),
                "green": (0.05 + 0.30 * x_shift, 0.96 + 0.70 * y_shift),
                "amber": (1.18 + 0.25 * x_shift, -0.06 + 0.12 * y_shift),
            }

        def make_train_plot_state(
            fold_idx: int,
        ) -> tuple[VGroup, VGroup, VGroup, VGroup, VGroup]:
            centers = _class_centers(fold_idx)
            blue_pts = [
                (-1.88 + 0.09 * np.sin(0.70 * fold_idx), 0.98 + 0.08 * np.cos(0.52 * fold_idx)),
                (-1.56 + 0.08 * np.cos(0.94 * fold_idx), 0.56 + 0.08 * np.sin(0.82 * fold_idx)),
                (-1.42 + 0.09 * np.sin(0.78 * fold_idx), -0.06 + 0.08 * np.cos(1.02 * fold_idx)),
                (-1.72 + 0.07 * np.cos(0.60 * fold_idx), -0.64 + 0.07 * np.sin(0.76 * fold_idx)),
                (-1.12 + 0.09 * np.sin(1.02 * fold_idx), 0.34 + 0.08 * np.cos(0.74 * fold_idx)),
                (-0.76 + 0.08 * np.cos(0.86 * fold_idx), -0.26 + 0.07 * np.sin(0.66 * fold_idx)),
                (-0.52 + 0.08 * np.sin(0.90 * fold_idx), 0.12 + 0.07 * np.cos(0.80 * fold_idx)),
                (-0.40 + 0.08 * np.cos(0.74 * fold_idx), -0.38 + 0.07 * np.sin(0.88 * fold_idx)),
            ]
            green_pts = [
                (-0.12 + 0.08 * np.cos(0.86 * fold_idx), 1.34 + 0.06 * np.sin(0.60 * fold_idx)),
                (0.22 + 0.07 * np.sin(0.84 * fold_idx), 1.06 + 0.07 * np.cos(0.74 * fold_idx)),
                (0.58 + 0.08 * np.cos(0.92 * fold_idx), 0.78 + 0.07 * np.sin(0.66 * fold_idx)),
                (0.10 + 0.07 * np.sin(0.70 * fold_idx), 0.62 + 0.07 * np.cos(0.88 * fold_idx)),
                (0.42 + 0.08 * np.cos(0.98 * fold_idx), 0.44 + 0.07 * np.sin(0.72 * fold_idx)),
                (-0.20 + 0.07 * np.sin(0.90 * fold_idx), 0.86 + 0.06 * np.cos(0.78 * fold_idx)),
                (0.72 + 0.08 * np.cos(0.76 * fold_idx), 0.22 + 0.06 * np.sin(0.90 * fold_idx)),
                (-0.34 + 0.06 * np.sin(0.82 * fold_idx), 0.42 + 0.07 * np.cos(0.84 * fold_idx)),
            ]
            amber_pts = [
                (1.06 + 0.09 * np.cos(0.82 * fold_idx), 0.84 + 0.08 * np.sin(0.70 * fold_idx)),
                (1.42 + 0.08 * np.sin(0.88 * fold_idx), 0.34 + 0.08 * np.cos(0.64 * fold_idx)),
                (1.80 + 0.08 * np.cos(1.12 * fold_idx), -0.18 + 0.07 * np.sin(0.88 * fold_idx)),
                (1.52 + 0.09 * np.sin(0.72 * fold_idx), -0.76 + 0.08 * np.cos(0.98 * fold_idx)),
                (1.02 + 0.08 * np.cos(1.00 * fold_idx), 0.06 + 0.08 * np.sin(0.84 * fold_idx)),
                (0.74 + 0.09 * np.sin(1.06 * fold_idx), -0.42 + 0.08 * np.cos(0.90 * fold_idx)),
                (0.52 + 0.08 * np.cos(0.76 * fold_idx), -0.02 + 0.06 * np.sin(0.86 * fold_idx)),
                (0.34 + 0.08 * np.sin(0.84 * fold_idx), -0.54 + 0.06 * np.cos(0.72 * fold_idx)),
            ]
            blue_group = VGroup(*[
                Dot(train_ax.c2p(x, y), radius=0.055, color=_D_BLUE, fill_opacity=0.88)
                for x, y in blue_pts
            ])
            green_group = VGroup(*[
                Dot(train_ax.c2p(x, y), radius=0.055, color=_D_GREEN, fill_opacity=0.88)
                for x, y in green_pts
            ])
            amber_group = VGroup(*[
                Dot(train_ax.c2p(x, y), radius=0.055, color=_D_AMBER, fill_opacity=0.88)
                for x, y in amber_pts
            ])
            support_vectors = VGroup(*[
                Circle(radius=0.09, color=_D_RED, stroke_width=1.7).move_to(pt.get_center())
                for pt in [
                    blue_group[6],
                    green_group[6],
                    amber_group[6],
                    blue_group[7],
                    amber_group[7],
                ]
            ])
            regions = _decision_regions(train_ax, centers)
            return regions, blue_group, green_group, amber_group, support_vectors

        def _region_fill(col: str) -> ManimColor:
            return interpolate_color(WHITE, ManimColor(col), 0.58)

        def _clip_polygon_halfplane(
            poly: list[np.ndarray], normal: np.ndarray, offset: float
        ) -> list[np.ndarray]:
            if not poly:
                return []

            def inside(p: np.ndarray) -> bool:
                return float(np.dot(normal, p)) <= offset + 1e-9

            def intersect(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
                direction = p2 - p1
                denom = float(np.dot(normal, direction))
                if abs(denom) < 1e-9:
                    return p2
                t = (offset - float(np.dot(normal, p1))) / denom
                return p1 + t * direction

            clipped: list[np.ndarray] = []
            for idx in range(len(poly)):
                prev = poly[idx - 1]
                curr = poly[idx]
                prev_in = inside(prev)
                curr_in = inside(curr)
                if curr_in:
                    if not prev_in:
                        clipped.append(intersect(prev, curr))
                    clipped.append(curr)
                elif prev_in:
                    clipped.append(intersect(prev, curr))
            return clipped

        def _linear_region_polygon(
            label: str, centers: dict[str, tuple[float, float]]
        ) -> list[np.ndarray]:
            x_min, x_max = -2.45, 2.45
            y_min, y_max = -1.35, 1.55
            poly = [
                np.array([x_min, y_min]),
                np.array([x_max, y_min]),
                np.array([x_max, y_max]),
                np.array([x_min, y_max]),
            ]
            c_i = np.array(centers[label], dtype=float)
            for other_label, other_center in centers.items():
                if other_label == label:
                    continue
                c_j = np.array(other_center, dtype=float)
                normal = c_j - c_i
                offset = 0.5 * (float(np.dot(c_j, c_j)) - float(np.dot(c_i, c_i)))
                poly = _clip_polygon_halfplane(poly, normal, offset)
                if len(poly) < 3:
                    return []
            return poly

        def _decision_regions(ax: Axes, centers: dict[str, tuple[float, float]]) -> VGroup:
            color_map = {"blue": _D_BLUE, "green": _D_GREEN, "amber": _D_AMBER}
            regions = VGroup()
            for label in ["blue", "green", "amber"]:
                poly = _linear_region_polygon(label, centers)
                if len(poly) < 3:
                    continue
                region = Polygon(
                    *[ax.c2p(float(x), float(y)) for x, y in poly],
                    stroke_width=0.0,
                )
                region.set_fill(_region_fill(color_map[label]), opacity=0.92)
                region.set_z_index(-8)
                regions.add(region)
            return regions

        def _error_mark(center: np.ndarray, *, visible: bool) -> VGroup:
            size = 0.12
            mark = VGroup(
                Line(center + UL * size, center + DR * size, color=_D_RED, stroke_width=2.4),
                Line(center + DL * size, center + UR * size, color=_D_RED, stroke_width=2.4),
            )
            if not visible:
                mark.set_stroke(opacity=0.0)
            return mark

        def make_test_plot_state(
            fold_idx: int,
        ) -> tuple[VGroup, VGroup, VGroup, VGroup, VGroup]:
            centers = _class_centers(fold_idx)
            misclassified = fold_misclassified[fold_idx]
            blue_pts = [
                (-1.62 + 0.05 * np.sin(0.72 * fold_idx), 0.86 + 0.05 * np.cos(0.52 * fold_idx)),
                (-1.30 + 0.05 * np.cos(0.82 * fold_idx), 0.46 + 0.05 * np.sin(0.74 * fold_idx)),
                (-1.10 + 0.05 * np.sin(0.88 * fold_idx), -0.08 + 0.04 * np.cos(0.80 * fold_idx)),
                (-0.90 + 0.04 * np.cos(0.78 * fold_idx), 0.18 + 0.05 * np.sin(0.70 * fold_idx)),
            ]
            green_pts = [
                (-0.08 + 0.05 * np.cos(0.84 * fold_idx), 1.18 + 0.05 * np.sin(0.66 * fold_idx)),
                (0.28 + 0.04 * np.sin(0.78 * fold_idx), 0.94 + 0.05 * np.cos(0.80 * fold_idx)),
                (0.56 + 0.05 * np.cos(0.88 * fold_idx), 0.62 + 0.04 * np.sin(0.72 * fold_idx)),
                (-0.18 + 0.04 * np.sin(0.82 * fold_idx), 0.74 + 0.04 * np.cos(0.74 * fold_idx)),
            ]
            amber_pts = [
                (1.24 + 0.05 * np.cos(0.78 * fold_idx), 0.72 + 0.05 * np.sin(0.66 * fold_idx)),
                (1.44 + 0.04 * np.sin(0.84 * fold_idx), 0.20 + 0.05 * np.cos(0.70 * fold_idx)),
                (1.52 + 0.05 * np.sin(0.90 * fold_idx), -0.34 + 0.05 * np.cos(0.82 * fold_idx)),
                (0.98 + 0.04 * np.cos(0.76 * fold_idx), -0.08 + 0.04 * np.sin(0.68 * fold_idx)),
            ]
            wrong_positions = {
                ("blue", 2): (0.42, 0.24),
                ("blue", 3): (0.98, -0.08),
                ("green", 0): (1.04, 0.08),
                ("green", 1): (-0.92, 0.24),
                ("green", 2): (1.10, -0.18),
                ("amber", 0): (-0.14, 0.80),
                ("amber", 1): (-0.88, 0.10),
                ("amber", 2): (0.28, 0.34),
            }
            point_lookup = {"blue": blue_pts, "green": green_pts, "amber": amber_pts}
            for class_name, idx in misclassified:
                base_x, base_y = wrong_positions[(class_name, idx)]
                point_lookup[class_name][idx] = (
                    base_x + 0.04 * np.sin(0.88 * fold_idx + idx),
                    base_y + 0.04 * np.cos(0.76 * fold_idx + idx),
                )
            blue_group = VGroup(*[
                Dot(test_ax.c2p(x, y), radius=0.070, color=_D_BLUE, fill_opacity=0.92)
                for x, y in blue_pts
            ])
            green_group = VGroup(*[
                Dot(test_ax.c2p(x, y), radius=0.070, color=_D_GREEN, fill_opacity=0.92)
                for x, y in green_pts
            ])
            amber_group = VGroup(*[
                Dot(test_ax.c2p(x, y), radius=0.070, color=_D_AMBER, fill_opacity=0.92)
                for x, y in amber_pts
            ])
            error_marks = VGroup()
            error_lookup = {"blue": blue_group, "green": green_group, "amber": amber_group}
            for class_name, idx in misclassified:
                error_marks.add(_error_mark(error_lookup[class_name][idx].get_center(), visible=True))
            regions = _decision_regions(test_ax, centers)
            return regions, blue_group, green_group, amber_group, error_marks

        train_regions, train_blue_pts, train_green_pts, train_amber_pts, support_vectors = make_train_plot_state(0)
        test_regions, test_blue_pts, test_green_pts, test_amber_pts, test_error_marks = make_test_plot_state(0)
        fold_label = Tex("held-out run 1 / 8", color=INK, font_size=20).next_to(
            train_title, UP, buff=0.10
        )
        def make_accuracy_display(n_filled: int) -> MathTex:
            if n_filled <= 0:
                tex = r"[\ ]"
            else:
                tex = r"[" + r", ".join(fold_accuracy_tex[:n_filled]) + r"]"
            return MathTex(tex, color=INK, font_size=20).next_to(test_ax, DOWN, buff=0.34)

        accuracy_display = make_accuracy_display(0)

        self.play(
            GrowArrow(data_arrow),
            FadeIn(svm_label),
            FadeIn(svm_question),
            FadeIn(class_examples),
            Create(train_ax),
            FadeIn(train_regions),
            FadeIn(train_title),
            FadeIn(train_x_label),
            FadeIn(train_y_label),
            Create(test_ax),
            FadeIn(test_regions),
            FadeIn(test_title),
            FadeIn(test_x_label),
            FadeIn(test_y_label),
            FadeIn(train_blue_pts),
            FadeIn(train_green_pts),
            FadeIn(train_amber_pts),
            FadeIn(support_vectors),
            FadeIn(test_blue_pts),
            FadeIn(test_green_pts),
            FadeIn(test_amber_pts),
            FadeIn(test_error_marks),
            FadeIn(fold_label),
            FadeIn(accuracy_display),
            run_time=1.15,
        )

        def _make_block_box(
            rows: list[Mobject],
            *,
            color: ManimColor,
            stroke_width: float,
            fill_opacity: float,
            x_pad: float = 0.05,
            top_pad: float = 0.04,
            bottom_pad: float = 0.04,
        ) -> RoundedRectangle:
            group = VGroup(*rows)
            left = group.get_left()[0] - x_pad
            right = group.get_right()[0] + x_pad
            top = group.get_top()[1] + top_pad
            bottom = group.get_bottom()[1] - bottom_pad
            return RoundedRectangle(
                corner_radius=0.04,
                width=right - left,
                height=top - bottom,
                color=color,
                stroke_width=stroke_width,
            ).move_to(
                np.array([(left + right) / 2, (top + bottom) / 2, 0.0])
            ).set_fill(color, opacity=fill_opacity)

        def _empty_train_box() -> RoundedRectangle:
            return _make_block_box(
                [matrix_rows[0]],
                color=_D_BLUE,
                stroke_width=0.0,
                fill_opacity=0.0,
            ).set_stroke(opacity=0.0)

        def _empty_train_label(box: Mobject) -> Tex:
            return Tex("train", color=_D_BLUE, font_size=16).move_to(
                np.array([label_col_x, box.get_center()[1], 0.0])
            ).set_opacity(0.0)

        def _set_tag(text: str, color: ManimColor, box: Mobject) -> VGroup:
            tag_text = Tex(text, color=color, font_size=16)
            tag_bg = RoundedRectangle(
                corner_radius=0.05,
                width=tag_text.width + 0.16,
                height=tag_text.height + 0.10,
                color=color,
                stroke_width=1.1,
            ).set_fill(BG, opacity=0.96)
            tag = VGroup(tag_bg, tag_text)
            tag.move_to(
                np.array([
                    label_col_x,
                    box.get_center()[1],
                    0.0,
                ])
            )
            tag.set_z_index(4)
            return tag

        def make_train_overlays(fold_idx: int) -> Group:
            top_rows = matrix_rows[: 4 * fold_idx]
            bottom_rows = matrix_rows[4 * (fold_idx + 1) :]
            if top_rows:
                top_box = _make_block_box(
                    top_rows,
                    color=_D_BLUE,
                    stroke_width=1.6,
                    fill_opacity=0.04,
                    x_pad=0.015,
                    top_pad=0.03,
                    bottom_pad=-0.015,
                ).set_z_index(-1)
                top_label = _set_tag("train", _D_BLUE, top_box)
            else:
                top_box = _empty_train_box()
                top_label = _empty_train_label(top_box)
            if bottom_rows:
                bottom_box = _make_block_box(
                    bottom_rows,
                    color=_D_BLUE,
                    stroke_width=1.6,
                    fill_opacity=0.04,
                    x_pad=0.015,
                    top_pad=-0.015,
                    bottom_pad=0.03,
                ).set_z_index(-1)
                bottom_label = _set_tag("train", _D_BLUE, bottom_box)
            else:
                bottom_box = _empty_train_box()
                bottom_label = _empty_train_label(bottom_box)
            return Group(top_box, top_label, bottom_box, bottom_label)

        test_boxes = [
            _make_block_box(
                matrix_rows[4 * run_idx : 4 * run_idx + 4],
                color=_D_AMBER,
                stroke_width=2.6,
                fill_opacity=0.10,
                x_pad=0.035,
                top_pad=0.015,
                bottom_pad=0.015,
            )
            for run_idx in range(8)
        ]
        test_labels = [
            _set_tag("test", _D_AMBER, box)
            for box in test_boxes
        ]

        current_train_overlays = make_train_overlays(0)
        current_test_box = test_boxes[0]
        current_test_label = test_labels[0]
        self.play(
            FadeIn(current_train_overlays),
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
            new_train_regions, new_train_blue_pts, new_train_green_pts, new_train_amber_pts, new_support_vectors = make_train_plot_state(fold_idx)
            new_test_regions, new_test_blue_pts, new_test_green_pts, new_test_amber_pts, new_test_error_marks = make_test_plot_state(fold_idx)
            new_train_overlays = make_train_overlays(fold_idx)
            new_accuracy_display = make_accuracy_display(fold_idx + 1)

            if fold_idx == 0:
                self.play(
                    Transform(fold_label, new_fold_label),
                    Transform(train_regions, new_train_regions),
                    Transform(train_blue_pts, new_train_blue_pts),
                    Transform(train_green_pts, new_train_green_pts),
                    Transform(train_amber_pts, new_train_amber_pts),
                    Transform(support_vectors, new_support_vectors),
                    Transform(test_regions, new_test_regions),
                    Transform(test_blue_pts, new_test_blue_pts),
                    Transform(test_green_pts, new_test_green_pts),
                    Transform(test_amber_pts, new_test_amber_pts),
                    Transform(test_error_marks, new_test_error_marks),
                    TransformMatchingTex(accuracy_display, new_accuracy_display),
                    Indicate(svm_label, color=INK, scale_factor=1.02),
                    run_time=0.55,
                )
                accuracy_display = new_accuracy_display
            else:
                self.play(
                    Transform(fold_label, new_fold_label),
                    Transform(train_regions, new_train_regions),
                    Transform(train_blue_pts, new_train_blue_pts),
                    Transform(train_green_pts, new_train_green_pts),
                    Transform(train_amber_pts, new_train_amber_pts),
                    Transform(support_vectors, new_support_vectors),
                    Transform(test_regions, new_test_regions),
                    Transform(test_blue_pts, new_test_blue_pts),
                    Transform(test_green_pts, new_test_green_pts),
                    Transform(test_amber_pts, new_test_amber_pts),
                    Transform(test_error_marks, new_test_error_marks),
                    FadeOut(current_train_overlays),
                    FadeOut(current_test_box),
                    FadeOut(current_test_label),
                    FadeIn(new_train_overlays),
                    FadeIn(test_boxes[fold_idx]),
                    FadeIn(test_labels[fold_idx]),
                    TransformMatchingTex(accuracy_display, new_accuracy_display),
                    Indicate(svm_label, color=INK, scale_factor=1.02),
                    run_time=0.55,
                )
                current_test_box = test_boxes[fold_idx]
                current_test_label = test_labels[fold_idx]
                accuracy_display = new_accuracy_display
                current_train_overlays = new_train_overlays

        final_acc = Tex("crossvalidated accuracy", color=INK, font_size=20).move_to(accuracy_display.get_center())
        self.play(
            FadeOut(fold_label),
            FadeOut(current_test_box),
            FadeOut(current_test_label),
            FadeOut(current_train_overlays),
            FadeOut(train_title),
            FadeOut(test_title),
            FadeOut(train_x_label),
            FadeOut(train_y_label),
            FadeOut(test_x_label),
            FadeOut(test_y_label),
            TransformMatchingTex(accuracy_display, final_acc),
            run_time=0.8,
        )

        self.wait(1.6)


# ══════════════════════════════════════════════════════════════════════════════
# Study2CrossSessionDecoding
# ══════════════════════════════════════════════════════════════════════════════


class Study2CrossSessionDecoding(Study2WithinSession2Decoding):
    """
    Build a compact cross-session decoding setup that conceptually shows
    training on Session 2 sensory patterns and testing on Session 1 sensory
    and delay-period patterns.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecoding -ql
        uv run manim scenes/study2.py Study2CrossSessionDecoding -qh
    """

    _RIGHT_ROW_SCALE = 0.56
    _RIGHT_ROW_CENTER = np.array([3.55, 0.85, 0.0])
    _TRAIN_PANEL_CENTER = np.array([-4.45, -2.05, 0.0])
    _PERCEPTION_PANEL_CENTER = np.array([2.35, -2.05, 0.0])
    _DELAY_PANEL_CENTER = np.array([5.10, -2.05, 0.0])
    _TARGET_TEST = _D_PURP
    _DELAY_TEST = _D_GREEN
    _TEST_EXAMPLES = [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 0),
        (4, 0),
        (5, 0),
        (0, 1),
        (3, 1),
    ]

    def _delay_row_values(self, base_idx: int, exemplar_idx: int = 0) -> np.ndarray:
        base = self._row_values(base_idx, exemplar_idx)
        rolled = np.roll(base, 1 + ((base_idx + exemplar_idx) % 4))
        ripple = 0.035 * np.cos(
            np.arange(base.size) * 0.85 + 0.55 * base_idx + 0.65 * exemplar_idx
        )
        return np.clip(0.62 * base + 0.38 * rolled + ripple, 0.10, 0.90)

    def _make_test_matrix_panel(
        self,
        center: np.ndarray,
        title_text: str,
        row_values: list[np.ndarray],
        row_colors: list[str],
    ) -> Group:
        rows = VGroup(*[
            _make_feature_row(
                values,
                color=col,
                cell_w=0.078,
                cell_h=0.078,
                gap=0.022,
            )
            for values, col in zip(row_values, row_colors)
        ]).arrange(DOWN, buff=0.038, aligned_edge=LEFT)
        left_bracket = MathTex(r"[", color=INK, font_size=26) \
            .stretch_to_fit_height(rows.height + 0.14)
        right_bracket = MathTex(r"]", color=INK, font_size=26) \
            .stretch_to_fit_height(rows.height + 0.14)
        left_bracket.next_to(rows, LEFT, buff=0.05)
        right_bracket.next_to(rows, RIGHT, buff=0.05)
        pattern_group = VGroup(left_bracket, rows, right_bracket)
        title = Tex(
            title_text,
            color=INK,
            font_size=17,
            tex_environment="center",
        ).next_to(pattern_group, UP, buff=0.08)
        return Group(title, pattern_group).move_to(center)

    def construct(self) -> None:
        self.camera.background_color = BG

        train_panel = self._make_test_matrix_panel(
            self._TRAIN_PANEL_CENTER,
            r"Train on sensory\\(Session 2)",
            [
                self._row_values(base_idx, exemplar_idx)
                for base_idx, exemplar_idx in self._TEST_EXAMPLES
            ],
            [
                self._ROW_COLS[base_idx % len(self._ROW_COLS)]
                for base_idx, _ in self._TEST_EXAMPLES
            ],
        )

        s1_title = Tex(
            r"\textbf{Session 1 :} Memory task",
            color=INK,
            font_size=26,
        )
        boxes1, xs1 = _build_row(Study2ExperimentalDesign._S1, S1_Y)
        dots1, x_end1 = _ellipsis(xs1, S1_Y)
        arrow1, t1 = _timeline(xs1, S1_Y, x_end1)
        time_lbl1, ph_lb1 = _labels(Study2ExperimentalDesign._S1, xs1, S1_Y)
        s1_row_group = Group(Group(*boxes1), dots1, arrow1, t1, time_lbl1, ph_lb1)
        s1_row_group.scale(self._RIGHT_ROW_SCALE).move_to(self._RIGHT_ROW_CENTER)
        s1_title.next_to(s1_row_group, UP, buff=0.18)

        self.play(
            FadeIn(train_panel),
            FadeIn(s1_title),
            FadeIn(s1_row_group),
            run_time=0.85,
        )
        self.wait(0.25)

        # ── Show setup on Session 1 target and delay ────────────────────────
        dim_right_mobs = [
            boxes1[idx] for idx in range(len(boxes1)) if idx not in {0, 1}
        ] + [
            time_lbl1[idx] for idx in range(len(time_lbl1)) if idx not in {0, 1}
        ] + [
            ph_lb1[idx] for idx in range(len(ph_lb1)) if idx not in {0, 1}
        ] + [dots1]
        self.play(
            *[mob.animate.set_opacity(0.18) for mob in dim_right_mobs],
            run_time=0.45,
        )

        target_box = boxes1[0]
        delay_box = boxes1[1]
        target_hi = SurroundingRectangle(
            target_box,
            color=self._TARGET_TEST,
            stroke_width=3.0,
            buff=0.05,
            corner_radius=0.10,
        )
        delay_hi = SurroundingRectangle(
            delay_box,
            color=self._DELAY_TEST,
            stroke_width=3.0,
            buff=0.05,
            corner_radius=0.10,
        )

        perception_panel = self._make_test_matrix_panel(
            self._PERCEPTION_PANEL_CENTER,
            r"Test on sensory\\(Session 1 target)",
            [
                self._row_values(base_idx, exemplar_idx)
                for base_idx, exemplar_idx in self._TEST_EXAMPLES
            ],
            [
                self._ROW_COLS[base_idx % len(self._ROW_COLS)]
                for base_idx, _ in self._TEST_EXAMPLES
            ],
        )
        delay_panel = self._make_test_matrix_panel(
            self._DELAY_PANEL_CENTER,
            r"Test on memory\\(Session 1 delay)",
            [
                self._delay_row_values(base_idx, exemplar_idx)
                for base_idx, exemplar_idx in self._TEST_EXAMPLES
            ],
            [
                self._ROW_COLS[base_idx % len(self._ROW_COLS)]
                for base_idx, _ in self._TEST_EXAMPLES
            ],
        )

        target_arrow = Arrow(
            target_box.get_bottom() + DOWN * 0.03,
            perception_panel[1].get_top() + UP * 0.03,
            color=self._TARGET_TEST,
            stroke_width=2.6,
            buff=0.02,
            tip_length=0.18,
        )
        delay_arrow = Arrow(
            delay_box.get_bottom() + DOWN * 0.03,
            delay_panel[1].get_top() + UP * 0.03,
            color=self._DELAY_TEST,
            stroke_width=2.6,
            buff=0.02,
            tip_length=0.18,
        )

        self.play(
            Create(target_hi),
            GrowArrow(target_arrow),
            FadeIn(perception_panel),
            run_time=0.7,
        )
        self.wait(0.20)
        self.play(
            Create(delay_hi),
            GrowArrow(delay_arrow),
            FadeIn(delay_panel),
            run_time=0.7,
        )
        self.wait(1.6)
