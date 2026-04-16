"""
Study 2.

  Study2ExperimentalDesign — two-session paradigm diagram
  Study2DecodingOverview   — Session 2 stimuli -> feature vectors -> sensory matrix
  Study2WithinSession2Decoding — crossvalidated prediction within Session 2
  Study2CrossSessionDecoding   — train on sensory, test on sensory and memory
  Study2WithinSession1Decoding — explain Session 1 within-session decoding and reveal results

Render:
    uv run manim scenes/study2.py Study2ExperimentalDesign -qh
    uv run manim scenes/study2.py Study2DecodingOverview -qh
    uv run manim scenes/study2.py Study2WithinSession2Decoding -qh
    uv run manim scenes/study2.py Study2CrossSessionDecoding -qh
    uv run manim scenes/study2.py Study2WithinSession1Decoding -qh
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
        self.wait(0.35)

        matrix_rows = [*visible_vectors, *target_rows[len(visible_vectors):]]
        matrix_shell = VGroup(*matrix_rows, left_bracket, right_bracket)

        matrix_mid_y = matrix_body.get_center()[1]
        right_block_y_shift = -0.10
        svm_label = VGroup(
            Tex("Linear", color=INK, font_size=20),
            Tex(r"\textbf{Support Vector Machine}", color=INK, font_size=20),
            Tex("Classifier", color=INK, font_size=20),
        ).arrange(DOWN, buff=0.05).move_to(np.array([0.55, matrix_mid_y + right_block_y_shift, 0.0]))
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
            np.array([arrow_center_x - arrow_len / 2, matrix_mid_y + right_block_y_shift, 0.0]),
            np.array([arrow_center_x + arrow_len / 2, matrix_mid_y + right_block_y_shift, 0.0]),
            color=_D_MGREY,
            stroke_width=3.8,
            buff=0.02,
            tip_length=0.18,
        )
        train_col = _D_BLUE
        test_col = "#EF4444"
        class_one_col = _D_PURP

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
        ).move_to(np.array([4.80, 1.16 + right_block_y_shift, 0.0]))
        test_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([4.80, -1.12 + right_block_y_shift, 0.0]))
        train_frame = SurroundingRectangle(
            train_ax, color=train_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )
        test_frame = SurroundingRectangle(
            test_ax, color=test_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )
        train_title = Tex("training data", color=train_col, font_size=18).next_to(train_ax, UP, buff=0.08)
        test_title = Tex("held-out test data", color=test_col, font_size=18).next_to(test_ax, UP, buff=0.08)
        train_x_label = Tex("voxel 1", color=INK, font_size=18).next_to(train_ax, DOWN, buff=0.10)
        train_y_label = Tex("voxel 2", color=INK, font_size=18).rotate(PI / 2).next_to(
            train_ax, LEFT, buff=0.08
        )
        test_x_label = Tex("voxel 1", color=INK, font_size=18).next_to(test_ax, DOWN, buff=0.10)
        test_y_label = Tex("voxel 2", color=INK, font_size=18).rotate(PI / 2).next_to(
            test_ax, LEFT, buff=0.08
        )
        class_example_paths = [CAT, PINE, SOFA]
        class_cols = [class_one_col, _D_GREEN, _D_AMBER]
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
        class_examples.arrange(RIGHT, buff=0.18).move_to(np.array([4.80, 2.54, 0.0]))

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
        crossvalidated_accuracy = 100 * (12 * len(fold_error_counts) - sum(fold_error_counts)) / (
            12 * len(fold_error_counts)
        )

        def _decision_shift(fold_idx: int) -> tuple[float, float]:
            return 0.13 * np.sin(0.72 * fold_idx), 0.09 * np.cos(0.86 * fold_idx)

        def _class_centers(fold_idx: int) -> dict[str, tuple[float, float]]:
            x_shift, y_shift = _decision_shift(fold_idx)
            return {
                "blue": (-1.25 + 0.28 * x_shift, -0.02 + 0.20 * y_shift),
                "green": (0.05 + 0.56 * x_shift, 0.96 + 1.05 * y_shift),
                "amber": (1.18 + 0.44 * x_shift, -0.06 + 0.22 * y_shift),
            }

        def make_train_plot_state(
            fold_idx: int,
        ) -> tuple[VGroup, VGroup, VGroup, VGroup]:
            centers = _class_centers(fold_idx)
            blue_pts = [
                (-1.88 + 0.11 * np.sin(0.70 * fold_idx), 0.98 + 0.10 * np.cos(0.52 * fold_idx)),
                (-1.56 + 0.10 * np.cos(0.94 * fold_idx), 0.56 + 0.10 * np.sin(0.82 * fold_idx)),
                (-1.42 + 0.11 * np.sin(0.78 * fold_idx), -0.06 + 0.10 * np.cos(1.02 * fold_idx)),
                (-1.72 + 0.085 * np.cos(0.60 * fold_idx), -0.64 + 0.085 * np.sin(0.76 * fold_idx)),
                (-1.12 + 0.11 * np.sin(1.02 * fold_idx), 0.34 + 0.10 * np.cos(0.74 * fold_idx)),
                (-0.76 + 0.10 * np.cos(0.86 * fold_idx), -0.26 + 0.085 * np.sin(0.66 * fold_idx)),
                (-0.52 + 0.10 * np.sin(0.90 * fold_idx), 0.12 + 0.085 * np.cos(0.80 * fold_idx)),
                (-0.40 + 0.10 * np.cos(0.74 * fold_idx), -0.38 + 0.085 * np.sin(0.88 * fold_idx)),
            ]
            green_pts = [
                (-0.12 + 0.10 * np.cos(0.86 * fold_idx), 1.34 + 0.075 * np.sin(0.60 * fold_idx)),
                (0.22 + 0.085 * np.sin(0.84 * fold_idx), 1.06 + 0.085 * np.cos(0.74 * fold_idx)),
                (0.58 + 0.10 * np.cos(0.92 * fold_idx), 0.78 + 0.085 * np.sin(0.66 * fold_idx)),
                (0.10 + 0.085 * np.sin(0.70 * fold_idx), 0.62 + 0.085 * np.cos(0.88 * fold_idx)),
                (0.42 + 0.10 * np.cos(0.98 * fold_idx), 0.44 + 0.085 * np.sin(0.72 * fold_idx)),
                (-0.20 + 0.085 * np.sin(0.90 * fold_idx), 0.86 + 0.075 * np.cos(0.78 * fold_idx)),
                (0.72 + 0.10 * np.cos(0.76 * fold_idx), 0.22 + 0.075 * np.sin(0.90 * fold_idx)),
                (-0.34 + 0.075 * np.sin(0.82 * fold_idx), 0.42 + 0.085 * np.cos(0.84 * fold_idx)),
            ]
            amber_pts = [
                (1.06 + 0.11 * np.cos(0.82 * fold_idx), 0.84 + 0.10 * np.sin(0.70 * fold_idx)),
                (1.42 + 0.10 * np.sin(0.88 * fold_idx), 0.34 + 0.10 * np.cos(0.64 * fold_idx)),
                (1.80 + 0.10 * np.cos(1.12 * fold_idx), -0.18 + 0.085 * np.sin(0.88 * fold_idx)),
                (1.52 + 0.11 * np.sin(0.72 * fold_idx), -0.76 + 0.10 * np.cos(0.98 * fold_idx)),
                (1.02 + 0.10 * np.cos(1.00 * fold_idx), 0.06 + 0.10 * np.sin(0.84 * fold_idx)),
                (0.74 + 0.11 * np.sin(1.06 * fold_idx), -0.42 + 0.10 * np.cos(0.90 * fold_idx)),
                (0.52 + 0.10 * np.cos(0.76 * fold_idx), -0.02 + 0.075 * np.sin(0.86 * fold_idx)),
                (0.34 + 0.10 * np.sin(0.84 * fold_idx), -0.54 + 0.075 * np.cos(0.72 * fold_idx)),
            ]
            blue_group = VGroup(*[
                Dot(train_ax.c2p(x, y), radius=0.055, color=class_one_col, fill_opacity=0.88)
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
            regions = _decision_regions(train_ax, centers)
            return regions, blue_group, green_group, amber_group

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
            color_map = {"blue": class_one_col, "green": _D_GREEN, "amber": _D_AMBER}
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
            anchor = Circle(radius=0.082).move_to(center)
            mark = Cross(
                anchor,
                stroke_color=_D_RED,
                stroke_width=2.6,
            ).move_to(center)
            mark.set_z_index(6)
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
                Dot(test_ax.c2p(x, y), radius=0.070, color=class_one_col, fill_opacity=0.92)
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

        train_regions, train_blue_pts, train_green_pts, train_amber_pts = make_train_plot_state(0)
        test_regions, test_blue_pts, test_green_pts, test_amber_pts, test_error_marks = make_test_plot_state(0)
        fold_label = Tex("held-out run 1 / 8", color=INK, font_size=20).move_to(
            np.array([4.80, -2.42 + right_block_y_shift, 0.0])
        )
        def make_accuracy_display(n_filled: int) -> MathTex:
            if n_filled <= 0:
                tex = r"[\ ]"
            else:
                tex = r"[" + r", ".join(fold_accuracy_tex[:n_filled]) + r"]"
            return MathTex(tex, color=INK, font_size=20).next_to(fold_label, DOWN, buff=0.16)

        accuracy_display = make_accuracy_display(0)

        self.play(
            FadeIn(svm_label),
            FadeIn(svm_question),
            run_time=0.55,
        )
        self.wait(2.0)

        self.play(
            GrowArrow(data_arrow),
            FadeIn(class_examples),
            Create(train_ax),
            FadeIn(train_frame),
            FadeIn(train_regions),
            FadeIn(train_title),
            FadeIn(train_x_label),
            FadeIn(train_y_label),
            Create(test_ax),
            FadeIn(test_frame),
            FadeIn(test_regions),
            FadeIn(test_title),
            FadeIn(test_x_label),
            FadeIn(test_y_label),
            FadeIn(train_blue_pts),
            FadeIn(train_green_pts),
            FadeIn(train_amber_pts),
            FadeIn(test_blue_pts),
            FadeIn(test_green_pts),
            FadeIn(test_amber_pts),
            FadeIn(test_error_marks),
            FadeIn(fold_label),
            FadeIn(accuracy_display),
            run_time=1.0,
        )
        self.wait(0.35)

        class_highlight_specs = [
            (class_examples[0], train_blue_pts, test_blue_pts, class_one_col),
            (class_examples[1], train_green_pts, test_green_pts, _D_GREEN),
            (class_examples[2], train_amber_pts, test_amber_pts, _D_AMBER),
        ]
        for icon, train_pts, test_pts, col in class_highlight_specs:
            self.play(
                AnimationGroup(
                    Indicate(icon, color=col, scale_factor=1.08),
                    Indicate(train_pts, color=col, scale_factor=1.06),
                    Indicate(test_pts, color=col, scale_factor=1.06),
                    lag_ratio=0.0,
                ),
                run_time=0.55,
            )
            self.wait(0.10)
        self.wait(0.35)

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
                color=train_col,
                stroke_width=0.0,
                fill_opacity=0.0,
            ).set_stroke(opacity=0.0)

        def _empty_train_label(box: Mobject) -> Tex:
            return Tex("train", color=train_col, font_size=16).move_to(
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
                    color=train_col,
                    stroke_width=1.6,
                    fill_opacity=0.04,
                    x_pad=0.015,
                    top_pad=0.03,
                    bottom_pad=-0.015,
                ).set_z_index(-1)
                top_label = _set_tag("train", train_col, top_box)
            else:
                top_box = _empty_train_box()
                top_label = _empty_train_label(top_box)
            if bottom_rows:
                bottom_box = _make_block_box(
                    bottom_rows,
                    color=train_col,
                    stroke_width=1.6,
                    fill_opacity=0.04,
                    x_pad=0.015,
                    top_pad=-0.015,
                    bottom_pad=0.03,
                ).set_z_index(-1)
                bottom_label = _set_tag("train", train_col, bottom_box)
            else:
                bottom_box = _empty_train_box()
                bottom_label = _empty_train_label(bottom_box)
            return Group(top_box, top_label, bottom_box, bottom_label)

        test_boxes = [
            _make_block_box(
                matrix_rows[4 * run_idx : 4 * run_idx + 4],
                color=test_col,
                stroke_width=2.6,
                fill_opacity=0.10,
                x_pad=0.035,
                top_pad=0.015,
                bottom_pad=0.015,
            )
            for run_idx in range(8)
        ]
        test_labels = [
            _set_tag("test", test_col, box)
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
        self.wait(0.35)

        for fold_idx in range(8):
            new_fold_label = Tex(
                f"held-out run {fold_idx + 1} / 8",
                color=INK,
                font_size=20,
            ).move_to(fold_label.get_center())
            new_train_regions, new_train_blue_pts, new_train_green_pts, new_train_amber_pts = make_train_plot_state(fold_idx)
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
            if fold_idx < 7:
                self.wait(0.2)
        self.wait(0.35)

        final_acc = VGroup(
            Tex("crossvalidated accuracy", color=INK, font_size=20),
            MathTex(rf"= {crossvalidated_accuracy:.1f}\%", color=INK, font_size=20),
        ).arrange(RIGHT, buff=0.10).move_to(accuracy_display.get_center())
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
            FadeTransform(accuracy_display, final_acc),
            run_time=0.8,
        )

        self.wait(1.6)


# ══════════════════════════════════════════════════════════════════════════════
# Study2WithinSession2DecodingResults
# ══════════════════════════════════════════════════════════════════════════════


class Study2WithinSession2DecodingResults(Study2WithinSession2Decoding):
    """
    Start from the final frame of within-session decoding, then transition to
    the results figure.

    Render:
        uv run manim scenes/study2.py Study2WithinSession2DecodingResults -ql
        uv run manim scenes/study2.py Study2WithinSession2DecodingResults -qh
    """

    def _build_final_frame(self) -> dict[str, Mobject]:
        title = Tex(
            "Decoding object-identity during perception from early visual cortex",
            color=INK,
            font_size=30,
        )
        title.to_edge(UP, buff=0.35)

        matrix_x = -4.67
        row_centers = self._matrix_row_centers(matrix_x, y_shift=-0.18)
        matrix_rows = [
            _make_feature_row(
                self._row_values(global_idx % len(self._BASE_ROWS), global_idx // 4),
                color=self._ROW_COLS[global_idx % len(self._ROW_COLS)],
                cell_w=0.11,
                cell_h=0.11,
                gap=0.025,
            ).move_to(row_centers[global_idx])
            for global_idx in range(32)
        ]
        matrix_body = VGroup(*matrix_rows)
        run_labels = VGroup(*[
            Tex(f"run {run_idx + 1}", color=_D_MGREY, font_size=16).next_to(
                VGroup(*matrix_rows[4 * run_idx : 4 * run_idx + 4]),
                LEFT,
                buff=0.52,
            )
            for run_idx in range(8)
        ])

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

        summary_title = Tex(
            r"Multivoxel activity patterns\\during perception",
            color=INK,
            font_size=24,
            tex_environment="center",
        ).scale(0.86).next_to(VGroup(left_bracket, matrix_body, right_bracket), UP, buff=0.20)

        matrix_mid_y = matrix_body.get_center()[1]
        right_block_y_shift = -0.10
        svm_label = VGroup(
            Tex("Linear", color=INK, font_size=20),
            Tex(r"\textbf{Support Vector Machine}", color=INK, font_size=20),
            Tex("Classifier", color=INK, font_size=20),
        ).arrange(DOWN, buff=0.05).move_to(np.array([0.55, matrix_mid_y + right_block_y_shift, 0.0]))
        question = Tex(
            "How well can the classifier\\\\discriminate between object-scene\\\\representations during perception?",
            color=INK,
            font_size=17,
            tex_environment="center",
        ).next_to(svm_label, DOWN, buff=0.22)

        label_col_x = right_bracket.get_right()[0] + 0.58
        arrow_len = 0.77
        arrow_center_x = 0.5 * (label_col_x + 0.42 + svm_label.get_left()[0])
        data_arrow = Arrow(
            np.array([arrow_center_x - arrow_len / 2, matrix_mid_y + right_block_y_shift, 0.0]),
            np.array([arrow_center_x + arrow_len / 2, matrix_mid_y + right_block_y_shift, 0.0]),
            color=_D_MGREY,
            stroke_width=3.8,
            buff=0.02,
            tip_length=0.18,
        )

        train_col = _D_BLUE
        test_col = "#EF4444"
        class_one_col = _D_PURP

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
        ).move_to(np.array([4.80, 1.16 + right_block_y_shift, 0.0]))
        test_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([4.80, -1.12 + right_block_y_shift, 0.0]))
        train_frame = SurroundingRectangle(
            train_ax, color=train_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )
        test_frame = SurroundingRectangle(
            test_ax, color=test_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )

        class_examples = Group(*[
            Group(ImageMobject(path).set_height(0.42))
            for path in [CAT, PINE, SOFA]
        ])
        for icon, col in zip(class_examples, [class_one_col, _D_GREEN, _D_AMBER]):
            frame = SurroundingRectangle(
                icon[0],
                color=col,
                stroke_width=2.1,
                buff=0.04,
                corner_radius=0.06,
            )
            icon.add(frame)
            icon[1].move_to(icon[0].get_center())
        class_examples.arrange(RIGHT, buff=0.18).move_to(np.array([4.80, 2.54, 0.0]))

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
        crossvalidated_accuracy = 100 * (12 * len(fold_error_counts) - sum(fold_error_counts)) / (
            12 * len(fold_error_counts)
        )

        def _decision_shift(fold_idx: int) -> tuple[float, float]:
            return 0.13 * np.sin(0.72 * fold_idx), 0.09 * np.cos(0.86 * fold_idx)

        def _class_centers(fold_idx: int) -> dict[str, tuple[float, float]]:
            x_shift, y_shift = _decision_shift(fold_idx)
            return {
                "blue": (-1.25 + 0.28 * x_shift, -0.02 + 0.20 * y_shift),
                "green": (0.05 + 0.56 * x_shift, 0.96 + 1.05 * y_shift),
                "amber": (1.18 + 0.44 * x_shift, -0.06 + 0.22 * y_shift),
            }

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
            color_map = {"blue": class_one_col, "green": _D_GREEN, "amber": _D_AMBER}
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

        def _error_mark(center: np.ndarray) -> VGroup:
            anchor = Circle(radius=0.082).move_to(center)
            mark = Cross(
                anchor,
                stroke_color=_D_RED,
                stroke_width=2.6,
            ).move_to(center)
            mark.set_z_index(6)
            return mark

        def make_train_plot_state(
            fold_idx: int,
        ) -> tuple[VGroup, VGroup, VGroup, VGroup]:
            centers = _class_centers(fold_idx)
            blue_pts = [
                (-1.88 + 0.11 * np.sin(0.70 * fold_idx), 0.98 + 0.10 * np.cos(0.52 * fold_idx)),
                (-1.56 + 0.10 * np.cos(0.94 * fold_idx), 0.56 + 0.10 * np.sin(0.82 * fold_idx)),
                (-1.42 + 0.11 * np.sin(0.78 * fold_idx), -0.06 + 0.10 * np.cos(1.02 * fold_idx)),
                (-1.72 + 0.085 * np.cos(0.60 * fold_idx), -0.64 + 0.085 * np.sin(0.76 * fold_idx)),
                (-1.12 + 0.11 * np.sin(1.02 * fold_idx), 0.34 + 0.10 * np.cos(0.74 * fold_idx)),
                (-0.76 + 0.10 * np.cos(0.86 * fold_idx), -0.26 + 0.085 * np.sin(0.66 * fold_idx)),
                (-0.52 + 0.10 * np.sin(0.90 * fold_idx), 0.12 + 0.085 * np.cos(0.80 * fold_idx)),
                (-0.40 + 0.10 * np.cos(0.74 * fold_idx), -0.38 + 0.085 * np.sin(0.88 * fold_idx)),
            ]
            green_pts = [
                (-0.12 + 0.10 * np.cos(0.86 * fold_idx), 1.34 + 0.075 * np.sin(0.60 * fold_idx)),
                (0.22 + 0.085 * np.sin(0.84 * fold_idx), 1.06 + 0.085 * np.cos(0.74 * fold_idx)),
                (0.58 + 0.10 * np.cos(0.92 * fold_idx), 0.78 + 0.085 * np.sin(0.66 * fold_idx)),
                (0.10 + 0.085 * np.sin(0.70 * fold_idx), 0.62 + 0.085 * np.cos(0.88 * fold_idx)),
                (0.42 + 0.10 * np.cos(0.98 * fold_idx), 0.44 + 0.085 * np.sin(0.72 * fold_idx)),
                (-0.20 + 0.085 * np.sin(0.90 * fold_idx), 0.86 + 0.075 * np.cos(0.78 * fold_idx)),
                (0.72 + 0.10 * np.cos(0.76 * fold_idx), 0.22 + 0.075 * np.sin(0.90 * fold_idx)),
                (-0.34 + 0.075 * np.sin(0.82 * fold_idx), 0.42 + 0.085 * np.cos(0.84 * fold_idx)),
            ]
            amber_pts = [
                (1.06 + 0.11 * np.cos(0.82 * fold_idx), 0.84 + 0.10 * np.sin(0.70 * fold_idx)),
                (1.42 + 0.10 * np.sin(0.88 * fold_idx), 0.34 + 0.10 * np.cos(0.64 * fold_idx)),
                (1.80 + 0.10 * np.cos(1.12 * fold_idx), -0.18 + 0.085 * np.sin(0.88 * fold_idx)),
                (1.52 + 0.11 * np.sin(0.72 * fold_idx), -0.76 + 0.10 * np.cos(0.98 * fold_idx)),
                (1.02 + 0.10 * np.cos(1.00 * fold_idx), 0.06 + 0.10 * np.sin(0.84 * fold_idx)),
                (0.74 + 0.11 * np.sin(1.06 * fold_idx), -0.42 + 0.10 * np.cos(0.90 * fold_idx)),
                (0.52 + 0.10 * np.cos(0.76 * fold_idx), -0.02 + 0.075 * np.sin(0.86 * fold_idx)),
                (0.34 + 0.10 * np.sin(0.84 * fold_idx), -0.54 + 0.075 * np.cos(0.72 * fold_idx)),
            ]
            blue_group = VGroup(*[
                Dot(train_ax.c2p(x, y), radius=0.055, color=class_one_col, fill_opacity=0.88)
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
            return _decision_regions(train_ax, centers), blue_group, green_group, amber_group

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
                Dot(test_ax.c2p(x, y), radius=0.070, color=class_one_col, fill_opacity=0.92)
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
                error_marks.add(_error_mark(error_lookup[class_name][idx].get_center()))
            return _decision_regions(test_ax, centers), blue_group, green_group, amber_group, error_marks

        fold_idx = 7
        train_regions, train_blue_pts, train_green_pts, train_amber_pts = make_train_plot_state(fold_idx)
        test_regions, test_blue_pts, test_green_pts, test_amber_pts, test_error_marks = make_test_plot_state(fold_idx)

        fold_label = Tex("held-out run 8 / 8", color=INK, font_size=20).move_to(
            np.array([4.80, -2.42 + right_block_y_shift, 0.0])
        )
        accuracy_anchor = MathTex(
            r"["
            + r", ".join([
                rf"{int(round(100 * (12 - n_err) / 12))}\%"
                for n_err in fold_error_counts
            ])
            + r"]",
            color=INK,
            font_size=20,
        ).next_to(fold_label, DOWN, buff=0.16)
        final_acc = VGroup(
            Tex("crossvalidated accuracy", color=INK, font_size=20),
            MathTex(rf"= {crossvalidated_accuracy:.1f}\%", color=INK, font_size=20),
        ).arrange(RIGHT, buff=0.10).move_to(accuracy_anchor.get_center())

        static_frame = Group(
            title,
            summary_title,
            matrix_body,
            left_bracket,
            right_bracket,
            run_labels,
            data_arrow,
            svm_label,
            question,
            class_examples,
            train_ax,
            train_frame,
            train_regions,
            train_blue_pts,
            train_green_pts,
            train_amber_pts,
            test_ax,
            test_frame,
            test_regions,
            test_blue_pts,
            test_green_pts,
            test_amber_pts,
            test_error_marks,
            final_acc,
        )

        fade_group = Group(
            title,
            summary_title,
            matrix_body,
            left_bracket,
            right_bracket,
            run_labels,
            data_arrow,
            svm_label,
            class_examples,
            train_ax,
            train_frame,
            train_regions,
            train_blue_pts,
            train_green_pts,
            train_amber_pts,
            test_ax,
            test_frame,
            test_regions,
            test_blue_pts,
            test_green_pts,
            test_amber_pts,
            test_error_marks,
            final_acc,
        )
        return {
            "static_frame": static_frame,
            "fade_group": fade_group,
            "question": question,
        }

    def _build_results_end_static(self) -> dict[str, Mobject]:
        def make_small_icon(img_path: str, frame_col: str) -> Group:
            img = ImageMobject(img_path).set_height(0.52)
            frame = SurroundingRectangle(
                img,
                color=frame_col,
                stroke_width=2.2,
                buff=0.04,
                corner_radius=0.06,
            )
            return Group(img, frame)

        question = Tex(
            "How well can the classifier\\\\discriminate between object-scene\\\\representations during perception?",
            color=INK,
            font_size=26,
            tex_environment="center",
        ).move_to(np.array([-3.15, 1.42, 0.0]))

        example_specs = [
            (SOFA, _D_AMBER, 1, 0.34),
            (str(_STIM / "ANI-CAT-T00.png"), _D_RED, 3, 1.00),
            (str(_STIM / "ITE-VAS-T00.png"), _D_PURP, 4, 1.00),
            (str(_STIM / "PLA-BRI-T00.png"), _D_CYAN, 5, 1.00),
            (PINE, _D_GREEN, 2, 0.34),
        ]
        example_columns = Group()
        for img_path, frame_col, pattern_idx, opacity in example_specs:
            icon = make_small_icon(img_path, frame_col)
            grid = self._make_grid(ORIGIN, frame_col, self._pattern_for_index(pattern_idx))
            if opacity < 1.0:
                icon[0].set_opacity(opacity)
                icon[1].set_stroke(opacity=opacity)
                grid.set_opacity(opacity)
            column = Group(icon, grid).arrange(DOWN, buff=0.18)
            example_columns.add(column)
        example_columns.arrange(RIGHT, buff=0.22, aligned_edge=UP)
        example_columns.move_to(np.array([-3.15, -0.02, 0.0]))

        results_img = (
            ImageMobject("/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_results.png")
            .set_height(3.82)
            .move_to(np.array([2.85, 0.00, 0.0]))
        )

        takeaway = Tex(
            "Robust above-chance decoding\\\\of sensory stimuli (63 labels)",
            color=INK,
            font_size=30,
            tex_environment="center",
        ).move_to(np.array([-3.15, -1.90, 0.0]))

        frame = Group(question, example_columns, results_img, takeaway)
        return {
            "frame": frame,
            "question": question,
            "example_columns": example_columns,
            "results_img": results_img,
            "takeaway": takeaway,
        }

    def construct(self) -> None:
        self.camera.background_color = BG
        layout = self._build_final_frame()
        static_frame = layout["static_frame"]
        fade_group = layout["fade_group"]
        question = layout["question"]

        end_layout = self._build_results_end_static()
        question_target = end_layout["question"]
        example_columns = end_layout["example_columns"]
        results_img = end_layout["results_img"]
        takeaway = end_layout["takeaway"]

        self.add(static_frame)
        self.wait(0.25)

        self.play(
            FadeOut(fade_group),
            Transform(question, question_target),
            run_time=0.9,
        )
        self.play(FadeIn(example_columns, shift=UP * 0.08), run_time=0.65)
        self.wait(0.7)

        self.play(
            FadeIn(results_img, shift=RIGHT * 0.18),
            run_time=0.85,
        )
        self.play(FadeIn(takeaway, shift=UP * 0.10), run_time=0.65)
        self.wait(1.5)


# ══════════════════════════════════════════════════════════════════════════════
# Study2CrossSessionDecoding
# ══════════════════════════════════════════════════════════════════════════════


class Study2CrossSessionDecoding(Study2WithinSession2Decoding):
    """
    Build a conceptual cross-session decoding setup that shows Session 2
    stimulation providing the training patterns, then tests the fixed decoder
    on Session 1 stimulation and delay-period patterns.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecoding -ql
        uv run manim scenes/study2.py Study2CrossSessionDecoding -qh
    """

    _S2_ROW_SCALE = 0.58
    _S2_ROW_CENTER = np.array([-3.55, 1.72, 0.0])
    _S1_ROW_SCALE = 0.58
    _S1_ROW_CENTER = np.array([3.55, 1.72, 0.0])
    _TRAIN_PANEL_CENTER = np.array([-4.05, -1.20, 0.0])
    _PERCEPTION_PANEL_CENTER = np.array([1.15, -1.20, 0.0])
    _DELAY_PANEL_CENTER = np.array([4.75, -1.20, 0.0])
    _S1_STIM_ACCENT = ManimColor("#A855F7")
    _TARGET_TEST = _S1_STIM_ACCENT
    _DELAY_TEST = _D_GREEN
    _TRAIN_ACCENT = _D_PURP
    _PERCEPTION_ACCENT = _S1_STIM_ACCENT
    _DELAY_ACCENT = _D_GREEN
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
    _TRAIN_ROW_ORDER = [0, 1, 2, 3, 4, 5, 6, 7]
    _PERCEPTION_ROW_ORDER = [1, 4, 6, 0, 3, 7, 2, 5]
    _DELAY_ROW_ORDER = [6, 2, 7, 4, 1, 5, 0, 3]
    _PANEL_ROLE_IDX = 0
    _PANEL_BODY_IDX = 1
    _PANEL_CONTENT_IDX = 2
    _ROW_TIME_LABEL_SCALE = 1.16
    _ROW_PHASE_LABEL_SCALE = 1.22

    def _make_session_row(
        self,
        specs: list[dict],
        row_y: float,
        title_text: str,
        scale: float,
        center: np.ndarray,
    ) -> tuple[Tex, Group, list[Group], VGroup, VGroup, VGroup]:
        title = Tex(title_text, color=INK, font_size=24)
        boxes, xs = _build_row(specs, row_y)
        dots, x_end = _ellipsis(xs, row_y)
        arrow, t_lbl = _timeline(xs, row_y, x_end)
        time_lbl, ph_lbl = _labels(specs, xs, row_y)
        row_group = Group(Group(*boxes), dots, arrow, t_lbl, time_lbl, ph_lbl)
        row_group.scale(scale).move_to(center)
        title.next_to(row_group, UP, buff=0.16)
        return title, row_group, boxes, dots, time_lbl, ph_lbl

    def _delay_row_values(self, base_idx: int, exemplar_idx: int = 0) -> np.ndarray:
        base = self._row_values(base_idx, exemplar_idx)
        rolled = np.roll(base, 1 + ((base_idx + exemplar_idx) % 4))
        ripple = 0.035 * np.cos(
            np.arange(base.size) * 0.85 + 0.55 * base_idx + 0.65 * exemplar_idx
        )
        return np.clip(0.62 * base + 0.38 * rolled + ripple, 0.10, 0.90)

    def _ordered_examples(self, order: list[int]) -> list[tuple[int, int]]:
        return [self._TEST_EXAMPLES[idx] for idx in order]

    def _make_matrix_panel(
        self,
        center: np.ndarray,
        role_text: str,
        content_text: str,
        row_values: list[np.ndarray],
        row_colors: list[str],
        *,
        accent_color: str,
        cell_w: float = 0.104,
        cell_h: float = 0.104,
        gap: float = 0.026,
        row_gap: float = 0.048,
        role_font_size: int = 19,
        content_font_size: int = 19,
    ) -> VGroup:
        rows = VGroup(*[
            _make_feature_row(
                values,
                color=col,
                cell_w=cell_w,
                cell_h=cell_h,
                gap=gap,
            )
            for values, col in zip(row_values, row_colors)
        ]).arrange(DOWN, buff=row_gap, aligned_edge=LEFT)
        left_bracket = MathTex(r"[", color=accent_color, font_size=26) \
            .stretch_to_fit_height(rows.height + 0.14)
        right_bracket = MathTex(r"]", color=accent_color, font_size=26) \
            .stretch_to_fit_height(rows.height + 0.14)
        left_bracket.next_to(rows, LEFT, buff=0.05)
        right_bracket.next_to(rows, RIGHT, buff=0.05)
        pattern_group = VGroup(left_bracket, rows, right_bracket)
        pattern_group.move_to(center)
        role_label = Tex(
            role_text,
            color=INK,
            font_size=role_font_size,
            tex_environment="center",
        ).next_to(pattern_group, UP, buff=0.16)
        content_label = Tex(
            content_text,
            color=accent_color,
            font_size=content_font_size,
            tex_environment="center",
        ).next_to(pattern_group, DOWN, buff=0.12)
        return VGroup(role_label, pattern_group, content_label)

    def _make_panel_focus_frame(self, target: Mobject) -> VMobject:
        return DashedVMobject(
            SurroundingRectangle(
                target,
                color=_D_MGREY,
                stroke_width=1.6,
                buff=0.10,
                corner_radius=0.08,
            ),
            num_dashes=44,
            dashed_ratio=0.48,
        )

    def _make_decode_arrow(
        self,
        source: Mobject,
        target: Mobject,
        *,
        angle: float,
    ) -> CurvedArrow:
        return CurvedArrow(
            source.get_right() + UP * 0.20 + RIGHT * 0.02,
            target.get_left() + UP * 0.20 + LEFT * 0.02,
            angle=angle,
            color=_D_MGREY,
            stroke_width=1.8,
            tip_length=0.14,
        )

    def _build_cross_session_layout(self) -> dict[str, object]:
        slide_title = Tex("Between-session decoding", color=INK, font_size=30)
        slide_title.to_edge(UP, buff=0.18)

        s2_title, s2_row_group, boxes2, dots2, time_lbl2, ph_lbl2 = self._make_session_row(
            Study2ExperimentalDesign._S2,
            S2_Y,
            r"\textbf{Session 2 :} Perceptual task",
            self._S2_ROW_SCALE,
            self._S2_ROW_CENTER,
        )
        s1_title, s1_row_group, boxes1, dots1, time_lbl1, ph_lbl1 = self._make_session_row(
            Study2ExperimentalDesign._S1,
            S1_Y,
            r"\textbf{Session 1 :} Memory task",
            self._S1_ROW_SCALE,
            self._S1_ROW_CENTER,
        )

        for label_group in (time_lbl2, time_lbl1):
            for label in label_group:
                label.scale(self._ROW_TIME_LABEL_SCALE)
        for label_group in (ph_lbl2, ph_lbl1):
            for label in label_group:
                label.scale(self._ROW_PHASE_LABEL_SCALE)

        s2_stim_highlights = VGroup(*[
            SurroundingRectangle(
                boxes2[idx],
                color=col,
                stroke_width=2.6,
                buff=0.04,
                corner_radius=0.08,
            )
            for idx, col in zip([0, 2, 4], self._COLS)
        ])
        s2_dim_mobs = [
            boxes2[idx] for idx in [1, 3]
        ] + [
            time_lbl2[idx] for idx in [1, 3]
        ] + [
            ph_lbl2[idx] for idx in [1, 3]
        ] + [dots2]

        train_examples = self._ordered_examples(self._TRAIN_ROW_ORDER)
        perception_examples = self._ordered_examples(self._PERCEPTION_ROW_ORDER)
        delay_examples = self._ordered_examples(self._DELAY_ROW_ORDER)

        train_panel = self._make_matrix_panel(
            self._TRAIN_PANEL_CENTER,
            "Train",
            "Stimulation",
            [
                self._row_values(base_idx, exemplar_idx)
                for base_idx, exemplar_idx in train_examples
            ],
            [
                self._ROW_COLS[base_idx % len(self._ROW_COLS)]
                for base_idx, _ in train_examples
            ],
            accent_color=self._TRAIN_ACCENT,
        )
        perception_panel = self._make_matrix_panel(
            self._PERCEPTION_PANEL_CENTER,
            "Test",
            "Stimulation",
            [
                self._row_values(base_idx, exemplar_idx)
                for base_idx, exemplar_idx in perception_examples
            ],
            [
                self._ROW_COLS[base_idx % len(self._ROW_COLS)]
                for base_idx, _ in perception_examples
            ],
            accent_color=self._PERCEPTION_ACCENT,
        )
        delay_panel = self._make_matrix_panel(
            self._DELAY_PANEL_CENTER,
            "Test",
            "Delay",
            [
                self._delay_row_values(base_idx, exemplar_idx)
                for base_idx, exemplar_idx in delay_examples
            ],
            [
                self._ROW_COLS[base_idx % len(self._ROW_COLS)]
                for base_idx, _ in delay_examples
            ],
            accent_color=self._DELAY_ACCENT,
        )

        train_arrow_targets = [
            train_panel[self._PANEL_BODY_IDX].get_top() + LEFT * 0.48 + UP * 0.02,
            train_panel[self._PANEL_BODY_IDX].get_top() + UP * 0.02,
            train_panel[self._PANEL_BODY_IDX].get_top() + RIGHT * 0.48 + UP * 0.02,
        ]
        s2_to_train_arrows = VGroup(*[
            Arrow(
                boxes2[idx].get_bottom() + DOWN * 0.04,
                target_point,
                color=col,
                stroke_width=1.6,
                buff=0.02,
                tip_length=0.12,
            )
            for idx, col, target_point in zip([0, 2, 4], self._COLS, train_arrow_targets)
        ])

        dim_right_mobs = [
            boxes1[idx] for idx in range(len(boxes1)) if idx not in {0, 1}
        ] + [
            time_lbl1[idx] for idx in range(len(time_lbl1)) if idx not in {0, 1}
        ] + [
            ph_lbl1[idx] for idx in range(len(ph_lbl1)) if idx not in {0, 1}
        ] + [dots1]

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

        target_arrow = Arrow(
            target_box.get_bottom() + DOWN * 0.03,
            perception_panel[self._PANEL_BODY_IDX].get_top() + LEFT * 0.12 + UP * 0.02,
            color=self._TARGET_TEST,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.12,
        )
        delay_arrow = Arrow(
            delay_box.get_bottom() + DOWN * 0.03,
            delay_panel[self._PANEL_BODY_IDX].get_top() + LEFT * 0.08 + UP * 0.02,
            color=self._DELAY_TEST,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.12,
        )

        return {
            "slide_title": slide_title,
            "s2_title": s2_title,
            "s2_row_group": s2_row_group,
            "s2_dim_mobs": s2_dim_mobs,
            "s2_stim_highlights": s2_stim_highlights,
            "train_panel": train_panel,
            "s2_to_train_arrows": s2_to_train_arrows,
            "s1_title": s1_title,
            "s1_row_group": s1_row_group,
            "dim_right_mobs": dim_right_mobs,
            "target_hi": target_hi,
            "delay_hi": delay_hi,
            "perception_panel": perception_panel,
            "delay_panel": delay_panel,
            "target_arrow": target_arrow,
            "delay_arrow": delay_arrow,
        }

    def construct(self) -> None:
        self.camera.background_color = BG
        layout = self._build_cross_session_layout()
        slide_title = layout["slide_title"]
        s2_title = layout["s2_title"]
        s2_row_group = layout["s2_row_group"]
        s2_dim_mobs = layout["s2_dim_mobs"]
        s2_stim_highlights = layout["s2_stim_highlights"]
        train_panel = layout["train_panel"]
        s2_to_train_arrows = layout["s2_to_train_arrows"]
        s1_title = layout["s1_title"]
        s1_row_group = layout["s1_row_group"]
        dim_right_mobs = layout["dim_right_mobs"]
        target_hi = layout["target_hi"]
        delay_hi = layout["delay_hi"]
        perception_panel = layout["perception_panel"]
        delay_panel = layout["delay_panel"]
        target_arrow = layout["target_arrow"]
        delay_arrow = layout["delay_arrow"]
        train_body = train_panel[self._PANEL_BODY_IDX]
        perception_body = perception_panel[self._PANEL_BODY_IDX]
        delay_body = delay_panel[self._PANEL_BODY_IDX]

        train_focus_frame = self._make_panel_focus_frame(train_body)
        stim_focus_frame = self._make_panel_focus_frame(perception_body)
        delay_focus_frame = self._make_panel_focus_frame(delay_body)
        stim_decode_arrow = self._make_decode_arrow(train_body, perception_body, angle=-0.55)
        delay_decode_arrow = self._make_decode_arrow(train_body, delay_body, angle=-0.34)

        previous_scene = Study2WithinSession2DecodingResults._build_results_end_static(self)
        previous_frame = previous_scene["frame"]
        self.add(previous_frame)

        self.play(
            FadeOut(previous_frame),
            FadeIn(slide_title),
            FadeIn(s2_title),
            FadeIn(s2_row_group),
            run_time=0.75,
        )
        self.wait(0.15)

        self.play(
            *[mob.animate.set_opacity(0.18) for mob in s2_dim_mobs],
            LaggedStart(*[Create(hl) for hl in s2_stim_highlights], lag_ratio=0.12),
            run_time=0.55,
        )

        self.play(
            LaggedStart(*[GrowArrow(arr) for arr in s2_to_train_arrows], lag_ratio=0.08),
            FadeIn(train_panel[self._PANEL_BODY_IDX], shift=UP * 0.06),
            FadeIn(train_panel[self._PANEL_CONTENT_IDX], shift=UP * 0.04),
            run_time=0.75,
        )
        self.wait(0.25)

        self.play(
            FadeIn(s1_title),
            FadeIn(s1_row_group),
            run_time=0.75,
        )
        self.wait(0.15)

        self.play(
            *[mob.animate.set_opacity(0.18) for mob in dim_right_mobs],
            run_time=0.35,
        )

        self.play(
            Create(target_hi),
            GrowArrow(target_arrow),
            FadeIn(perception_panel[self._PANEL_BODY_IDX], shift=UP * 0.06),
            FadeIn(perception_panel[self._PANEL_CONTENT_IDX], shift=UP * 0.04),
            run_time=0.55,
        )
        self.wait(0.20)
        self.play(
            Create(delay_hi),
            GrowArrow(delay_arrow),
            FadeIn(delay_panel[self._PANEL_BODY_IDX], shift=UP * 0.06),
            FadeIn(delay_panel[self._PANEL_CONTENT_IDX], shift=UP * 0.04),
            run_time=0.55,
        )
        self.wait(0.50)

        self.play(
            FadeOut(s2_to_train_arrows),
            FadeOut(target_arrow),
            FadeOut(delay_arrow),
            FadeOut(s2_stim_highlights),
            FadeOut(target_hi),
            FadeOut(delay_hi),
            Create(train_focus_frame),
            FadeIn(train_panel[self._PANEL_ROLE_IDX], shift=UP * 0.05),
            run_time=0.45,
        )
        self.play(
            Create(stim_focus_frame),
            FadeIn(perception_panel[self._PANEL_ROLE_IDX], shift=UP * 0.05),
            Create(stim_decode_arrow),
            run_time=0.75,
        )
        self.wait(0.85)
        self.play(
            ReplacementTransform(stim_focus_frame, delay_focus_frame),
            FadeOut(perception_panel[self._PANEL_ROLE_IDX], shift=UP * 0.04),
            FadeIn(delay_panel[self._PANEL_ROLE_IDX], shift=UP * 0.05),
            ReplacementTransform(stim_decode_arrow, delay_decode_arrow),
            run_time=0.85,
        )
        self.wait(1.2)


class Study2CrossSessionDecodingResults(Study2CrossSessionDecoding):
    """
    Start from the last frame of cross-session decoding.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecodingResults -ql
        uv run manim scenes/study2.py Study2CrossSessionDecodingResults -qh
    """

    _RESULTS_GLM = "/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_results_ses02ses01glm.png"
    _RESULTS_TIMERES = "/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_results_ses02ses01timeres.png"
    _MINI_TRAIN_VALUES = np.array([0.88, 0.26, 0.74, 0.34, 0.94, 0.42, 0.68, 0.20, 0.82])
    _MINI_STIM_VALUES = np.array([0.84, 0.30, 0.70, 0.38, 0.90, 0.46, 0.64, 0.24, 0.78])
    _MINI_DELAY_VALUES = np.array([0.20, 0.74, 0.34, 0.58, 0.26, 0.80, 0.42, 0.68, 0.24])
    _MINI_MATRIX_SCALE = 1.5
    _TIMERES_TRACE_IDX = 60
    _TIMERES_SCHEMA_IDXS = {67, 68, 69, 70, 71, 72}

    def _make_small_results_matrix(
        self,
        values: np.ndarray,
        color: str,
        label: str,
        *,
        label_direction: np.ndarray = UP,
    ) -> VGroup:
        rows = VGroup(*[
            _make_feature_row(
                values[row_idx * 3 : (row_idx + 1) * 3],
                color=color,
                cell_w=0.12,
                cell_h=0.12,
                gap=0.024,
            )
            for row_idx in range(3)
        ]).arrange(DOWN, buff=0.024)
        frame = SurroundingRectangle(
            rows,
            color=color,
            stroke_width=1.5,
            buff=0.045,
            corner_radius=0.035,
        )
        matrix_label = Tex(label, color=color, font_size=13).next_to(
            frame,
            label_direction,
            buff=0.04,
        )
        return VGroup(rows, frame, matrix_label).scale(self._MINI_MATRIX_SCALE)

    def _position_small_results_matrix(
        self,
        matrix: VGroup,
        center: np.ndarray,
        *,
        label_direction: np.ndarray = UP,
    ) -> None:
        rows, frame, label = matrix
        rows.move_to(center)
        frame.move_to(rows)
        label.next_to(frame, label_direction, buff=0.04)

    def _make_partial_path(self, template: VMobject, alpha: float) -> VMobject:
        partial = template.copy()
        alpha = float(np.clip(alpha, 0.0, 1.0))
        if alpha <= 1e-4:
            partial.set_stroke(opacity=0.0)
            partial.set_fill(opacity=0.0)
            return partial
        partial.pointwise_become_partial(template, 0.0, alpha)
        return partial

    def _trace_step_proportions(self, trace_template: VMobject, step_count: int) -> np.ndarray:
        sample_props = np.linspace(0.0, 1.0, 1200)
        sample_xs = np.array([
            trace_template.point_from_proportion(float(prop))[0]
            for prop in sample_props
        ])
        target_xs = np.linspace(sample_xs[0], sample_xs[-1], step_count)

        step_props: list[float] = []
        for target_x in target_xs:
            idx = int(np.searchsorted(sample_xs, target_x, side="left"))
            idx = min(max(idx, 0), len(sample_props) - 1)
            if idx > 0 and abs(sample_xs[idx - 1] - target_x) <= abs(sample_xs[idx] - target_x):
                idx -= 1
            step_props.append(float(sample_props[idx]))
        return np.array(step_props)

    def _glm_svg_hex(self, color) -> str | None:
        if color is None:
            return None
        if isinstance(color, str):
            return ManimColor(color).to_hex().upper()
        return color.to_hex().upper()

    def _glm_svg_plot_frame(self, svg: SVGMobject) -> VGroup:
        candidates = [
            submob
            for submob in svg.submobjects
            if (
                len(submob.get_all_points()) == 4
                and submob.get_stroke_opacity() > 0.0
                and (
                    submob.width >= svg.width * 0.7
                    or submob.height >= svg.height * 0.7
                )
            )
        ]
        verticals = [submob for submob in candidates if submob.height > submob.width]
        horizontals = [submob for submob in candidates if submob.width >= submob.height]
        if len(verticals) < 2 or len(horizontals) < 2:
            raise ValueError("Could not identify GLM plot frame in SVG")
        left = min(verticals, key=lambda mob: mob.get_center()[0])
        right = max(verticals, key=lambda mob: mob.get_center()[0])
        bottom = min(horizontals, key=lambda mob: mob.get_center()[1])
        top = max(horizontals, key=lambda mob: mob.get_center()[1])
        return VGroup(left, right, bottom, top)

    def _glm_svg_group(self, svg: SVGMobject, color_hex: str, side: str) -> VGroup:
        frame_center_x = self._glm_svg_plot_frame(svg).get_center()[0]
        color_hex = color_hex.upper()
        return VGroup(*[
            submob
            for submob in svg.submobjects
            if (
                self._glm_svg_hex(submob.get_stroke_color()) == color_hex
                or self._glm_svg_hex(submob.get_fill_color()) == color_hex
            )
            and (
                submob.get_center()[0] < frame_center_x
                if side == "left"
                else submob.get_center()[0] > frame_center_x
            )
        ])

    def _glm_svg_scatter_points(self, group: VGroup) -> VGroup:
        points = sorted(
            [
                submob
                for submob in group
                if submob.get_fill_opacity() < 0.5 and len(submob.get_all_points()) == 32
            ],
            key=lambda mob: (mob.get_center()[1], mob.get_center()[0]),
        )
        return VGroup(*points)

    def _glm_svg_chance_line(self, svg: SVGMobject) -> VMobject:
        plot_frame = self._glm_svg_plot_frame(svg)
        x_tol = plot_frame.width * 0.02
        y_tol = plot_frame.height * 0.02

        candidates = [
            submob
            for submob in svg.submobjects
            if (
                len(submob.get_all_points()) == 4
                and abs(submob.get_left()[0] - plot_frame.get_left()[0]) <= x_tol
                and abs(submob.get_right()[0] - plot_frame.get_right()[0]) <= x_tol
                and plot_frame.get_bottom()[1] + y_tol < submob.get_center()[1] < plot_frame.get_top()[1] - y_tol
                and submob.height <= plot_frame.height * 0.02
            )
        ]
        if not candidates:
            raise ValueError("Could not identify GLM chance line in SVG")
        return max(candidates, key=lambda mob: mob.width)

    def _glm_svg_significance_marker(self, svg: SVGMobject, color_hex: str, side: str) -> VGroup:
        plot_top = self._glm_svg_plot_frame(svg).get_top()[1]
        frame_center_x = self._glm_svg_plot_frame(svg).get_center()[0]
        color_hex = color_hex.upper()
        return VGroup(*[
            submob
            for submob in svg.submobjects
            if (
                self._glm_svg_hex(submob.get_fill_color()) == color_hex
                or self._glm_svg_hex(submob.get_stroke_color()) == color_hex
            )
            and submob.get_center()[1] > plot_top
            and (
                submob.get_center()[0] < frame_center_x
                if side == "left"
                else submob.get_center()[0] > frame_center_x
            )
        ])

    def _glm_svg_hide_color_groups(self, svg: SVGMobject) -> None:
        for submob in svg.submobjects:
            if (
                self._glm_svg_hex(submob.get_fill_color()) in {"#7B51A0", "#3C9553"}
                or self._glm_svg_hex(submob.get_stroke_color()) in {"#7B51A0", "#3C9553"}
            ):
                submob.set_opacity(0)

    def _glm_svg_bottom_label(self, plot_frame: VGroup, x: float, tex: str) -> MathTex:
        label = MathTex(tex, color=BLACK)
        label.scale_to_fit_width(plot_frame.width * 0.21)
        label.move_to([x, plot_frame.get_bottom()[1] - 0.19, 0.0])
        return label

    def _remap_plot_mobject(
        self,
        mob: Mobject,
        source_frame: Mobject,
        target_frame: Mobject,
    ) -> Mobject:
        mapped = mob.copy()
        source_center = source_frame.get_center()
        mapped.stretch(
            target_frame.width / source_frame.width,
            dim=0,
            about_point=source_center,
        )
        mapped.stretch(
            target_frame.height / source_frame.height,
            dim=1,
            about_point=source_center,
        )
        mapped.shift(target_frame.get_center() - source_center)
        return mapped

    def _build_results_context(self) -> dict:
        self.camera.background_color = BG
        layout = self._build_cross_session_layout()
        test_s1_purple = ManimColor("#A855F7")

        for mob in layout["s2_dim_mobs"]:
            mob.set_opacity(0.18)
        for mob in layout["dim_right_mobs"]:
            mob.set_opacity(0.18)

        train_panel = layout["train_panel"]
        perception_panel = layout["perception_panel"]
        delay_panel = layout["delay_panel"]
        train_body = train_panel[self._PANEL_BODY_IDX]
        delay_body = delay_panel[self._PANEL_BODY_IDX]
        train_focus_frame = self._make_panel_focus_frame(train_body)
        delay_focus_frame = self._make_panel_focus_frame(delay_body)
        delay_decode_arrow = self._make_decode_arrow(train_body, delay_body, angle=-0.34)

        plot_height = 3.55
        left_panel_center = np.array([-3.95, -1.15, 0.0])
        left_panel_shift_x = abs(left_panel_center[0]) * 0.10
        left_panel_center[0] += left_panel_shift_x
        glm_plot_center = left_panel_center.copy()
        glm_plot_center[0] -= abs(left_panel_center[0]) * 0.05
        suptitle_y = 3.70
        glm_svg = (
            SVGMobject(str(Path(self._RESULTS_GLM).with_suffix(".svg")))
            .set_height(plot_height)
            .move_to(glm_plot_center)
        )
        glm_plot_base = glm_svg.copy()
        self._glm_svg_hide_color_groups(glm_plot_base)
        glm_plot_frame = self._glm_svg_plot_frame(glm_plot_base)
        glm_chance_template = self._glm_svg_chance_line(glm_plot_base)
        glm_plot_rest = VGroup(*[
            submob
            for submob in glm_plot_base.submobjects
            if submob not in glm_plot_frame.submobjects
            and submob is not glm_chance_template
        ])
        glm_accuracy_label = VGroup(*[glm_plot_rest[idx].copy() for idx in range(21, 29)])
        glm_left_group = self._glm_svg_group(glm_svg, "#7B51A0", "left")
        glm_right_group = self._glm_svg_group(glm_svg, "#3C9553", "right")
        glm_left_significance = self._glm_svg_significance_marker(glm_svg, "#7B51A0", "left")
        glm_right_significance = self._glm_svg_significance_marker(glm_svg, "#3C9553", "right")
        glm_left_visual = VGroup(*[
            submob for submob in glm_left_group if submob not in glm_left_significance
        ])
        glm_right_visual = VGroup(*[
            submob for submob in glm_right_group if submob not in glm_right_significance
        ])
        glm_left_points = self._glm_svg_scatter_points(glm_left_visual)
        glm_right_points = self._glm_svg_scatter_points(glm_right_visual)
        glm_left_extras = VGroup(*[
            submob for submob in glm_left_visual if submob not in glm_left_points
        ])
        glm_right_extras = VGroup(*[
            submob for submob in glm_right_visual if submob not in glm_right_points
        ])
        glm_title_shift_right = glm_svg.width * 0.10
        glm_title = Tex(
            r"GLM-based decoding",
            color=INK,
            font_size=22,
        ).move_to(np.array([glm_plot_center[0] + glm_title_shift_right, suptitle_y, 0.0]))
        takeaway_line_1 = Tex(
            r"{{Sensory-trained}} classifiers can decode stimulus identity",
            color=INK,
            font_size=22,
        )
        takeaway_line_1.set_color_by_tex("Sensory-trained", _D_PURP)

        takeaway_line_2 = Tex(
            r"from the {{stimulation period}}, but do not generalise throughout the {{delay phase}}",
            color=INK,
            font_size=22,
        )
        takeaway_line_2.set_color_by_tex("stimulation period", test_s1_purple)
        takeaway_line_2.set_color_by_tex("delay phase", _D_GREEN)

        glm_takeaway = VGroup(
            takeaway_line_1,
            takeaway_line_2,
        ).arrange(DOWN, buff=0.10, center=True)
        glm_takeaway.move_to(np.array([0.0, -3.42, 0.0]))

        glm_row_shift_down = plot_height * 0.10
        glm_bottom_y = 1.86 - glm_row_shift_down
        glm_train_y = glm_bottom_y + 1.04
        frame_width_final = 1.5
        frame_opacity_final = 0.48
        frame_width_emphasis = 3.0

        glm_train = self._make_small_results_matrix(
            self._MINI_TRAIN_VALUES,
            _D_PURP,
            r"$S_2$",
            label_direction=UP,
        )
        glm_stim_test = self._make_small_results_matrix(
            self._MINI_STIM_VALUES,
            test_s1_purple,
            r"$S_1$",
            label_direction=DOWN,
        )
        glm_delay_test = self._make_small_results_matrix(
            self._MINI_DELAY_VALUES,
            _D_GREEN,
            r"$D_1$",
            label_direction=DOWN,
        )
        glm_train_explainer = VGroup(
            Tex("Train on", color=INK, font_size=17),
            Tex("Stimulation", color=_D_PURP, font_size=17),
            Tex("Session 2", color=_D_PURP, font_size=17),
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        glm_stim_explainer = VGroup(
            Tex("Test on", color=INK, font_size=17),
            Tex("Stimulation", color=test_s1_purple, font_size=17),
            Tex("Session 1", color=test_s1_purple, font_size=17),
        ).arrange(DOWN, buff=0.03, aligned_edge=RIGHT)
        glm_delay_explainer = VGroup(
            Tex("Test on", color=INK, font_size=17),
            Tex("Delay", color=_D_GREEN, font_size=17),
            Tex("Session 1", color=_D_GREEN, font_size=17),
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)

        glm_left_x = (
            glm_left_points.get_center()[0]
            if len(glm_left_points) > 0
            else glm_left_group.get_center()[0]
        )
        glm_right_x = (
            glm_right_points.get_center()[0]
            if len(glm_right_points) > 0
            else glm_right_group.get_center()[0]
        )
        glm_train_x = (glm_left_x + glm_right_x) / 2

        self._position_small_results_matrix(
            glm_train,
            np.array([glm_train_x, glm_train_y, 0.0]),
            label_direction=UP,
        )
        self._position_small_results_matrix(
            glm_stim_test,
            np.array([glm_left_x, glm_bottom_y, 0.0]),
            label_direction=DOWN,
        )
        self._position_small_results_matrix(
            glm_delay_test,
            np.array([glm_right_x, glm_bottom_y, 0.0]),
            label_direction=DOWN,
        )
        glm_train_explainer.next_to(glm_train[1], RIGHT, buff=0.16)
        glm_train_explainer.shift(UP * 0.02)
        glm_stim_explainer.next_to(glm_stim_test[1], LEFT, buff=0.16)
        glm_delay_explainer.next_to(glm_delay_test[1], RIGHT, buff=0.16)
        glm_stim_plot_label = self._glm_svg_bottom_label(
            glm_plot_frame,
            glm_left_x,
            r"S_2 \rightarrow S_1",
        )
        glm_delay_plot_label = self._glm_svg_bottom_label(
            glm_plot_frame,
            glm_right_x,
            r"S_2 \rightarrow D_1",
        )
        glm_chance_y = glm_chance_template.get_center()[1]
        glm_chance_color = glm_chance_template.get_stroke_color()
        glm_chance_line = DashedLine(
            np.array([glm_plot_frame.get_left()[0], glm_chance_y, 0.0]),
            np.array([glm_plot_frame.get_right()[0], glm_chance_y, 0.0]),
            color=glm_chance_color,
            stroke_width=2.0,
            dash_length=0.08,
            dashed_ratio=0.55,
        )
        glm_chance_label = Tex(
            "Chance",
            color=glm_chance_color,
            font_size=14,
        ).move_to(
            np.array([glm_plot_frame.get_right()[0] - 0.26, glm_chance_y + 0.14, 0.0])
        )
        glm_plot_scaffold = VGroup(
            glm_plot_frame,
            glm_plot_rest,
            glm_chance_line,
            glm_chance_label,
        )
        glm_left_cloud = VGroup(
            glm_left_points,
            glm_left_extras,
            glm_stim_plot_label,
        )
        glm_right_cloud = VGroup(
            glm_right_points,
            glm_right_extras,
            glm_delay_plot_label,
        )
        glm_significance_markers = VGroup(
            glm_left_significance,
            glm_right_significance,
        )

        for matrix in (glm_train, glm_stim_test, glm_delay_test):
            matrix[1].set_stroke(width=frame_width_final, opacity=0.0)

        glm_left_arrow = Arrow(
            glm_train[1].get_bottom() + DOWN * 0.11 + LEFT * 0.18,
            glm_stim_test[1].get_top() + UP * 0.03 + LEFT * 0.08,
            color=_D_MGREY,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.10,
        )
        glm_right_arrow = Arrow(
            glm_train[1].get_bottom() + DOWN * 0.11 + RIGHT * 0.18,
            glm_delay_test[1].get_top() + UP * 0.03 + RIGHT * 0.08,
            color=_D_MGREY,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.10,
        )

        right_panel_center = np.array([3.75, -1.15, 0.0])
        right_panel_shift_x = right_panel_center[0] * 0.10
        right_panel_center[0] -= right_panel_shift_x
        timeres_svg = (
            SVGMobject(str(Path(self._RESULTS_TIMERES).with_suffix(".svg")))
            .set_height(plot_height)
            .move_to(right_panel_center)
        )
        timeres_source_frame = VGroup(*[timeres_svg[idx].copy() for idx in [61, 62, 63, 64]])
        timeres_frame = glm_plot_frame.copy()
        timeres_frame.set_x(timeres_source_frame.get_center()[0])
        timeres_frame.align_to(glm_plot_frame, DOWN)
        pixel_step_x = config.frame_width / config.pixel_width
        ref_phase = (glm_plot_frame.get_left()[0] / pixel_step_x) % 1.0
        timeres_phase = (timeres_frame.get_left()[0] / pixel_step_x) % 1.0
        phase_delta = ((ref_phase - timeres_phase + 0.5) % 1.0) - 0.5
        timeres_frame.shift(RIGHT * (phase_delta * pixel_step_x))
        timeres_background = self._remap_plot_mobject(
            timeres_svg[0].copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_guides = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in [2, 3, 4, 5]]),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_x_ticks = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in range(6, 13)]),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_y_ticks = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in range(22, 38)]),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_trace_template = self._remap_plot_mobject(
            timeres_svg[self._TIMERES_TRACE_IDX].copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_chance_template = self._remap_plot_mobject(
            timeres_svg[1].copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_ci = self._remap_plot_mobject(
            timeres_svg[59].copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_sig_lines = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in [65, 66]]),
            timeres_source_frame,
            timeres_frame,
        )
        # Reuse vector glyphs from the source plots so the right panel matches
        # the left panel's line weight and label styling exactly.
        timeres_x_label_template = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in range(13, 22)]),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_x_label = Tex("Test time (s)", color=INK)
        timeres_x_label.scale_to_fit_height(timeres_x_label_template.height)
        if timeres_x_label.width > timeres_x_label_template.width:
            timeres_x_label.scale_to_fit_width(timeres_x_label_template.width)
        timeres_x_label.move_to(timeres_x_label_template.get_center())
        timeres_y_label = self._remap_plot_mobject(
            glm_accuracy_label,
            glm_plot_frame,
            timeres_frame,
        )
        timeres_chance_y = timeres_chance_template.get_center()[1]
        timeres_chance_color = glm_chance_color
        timeres_chance_line = DashedLine(
            np.array([timeres_frame.get_left()[0], timeres_chance_y, 0.0]),
            np.array([timeres_frame.get_right()[0], timeres_chance_y, 0.0]),
            color=timeres_chance_color,
            stroke_width=2.0,
            dash_length=0.08,
            dashed_ratio=0.55,
        )
        timeres_chance_label = Tex(
            "Chance",
            color=timeres_chance_color,
            font_size=14,
        ).next_to(timeres_chance_line, DOWN, buff=0.08).align_to(
            timeres_chance_line, RIGHT
        ).shift(LEFT * 0.02)
        timeres_plot_scaffold = VGroup(
            timeres_frame,
            timeres_background,
            timeres_guides,
            timeres_x_ticks,
            timeres_y_ticks,
            timeres_x_label,
            timeres_y_label,
        )
        timeres_chance_group = VGroup(timeres_chance_line, timeres_chance_label)
        timeres_title = Tex(
            r"Raw voxel time series decoding",
            color=INK,
            font_size=22,
        ).move_to(np.array([3.82 - right_panel_shift_x, suptitle_y, 0.0]))

        timeres_trace_step_props = self._trace_step_proportions(timeres_trace_template, 25)
        timeres_trace_xs = np.linspace(
            timeres_trace_template.get_left()[0],
            timeres_trace_template.get_right()[0],
            25,
        )
        timeres_strip_y = timeres_frame.get_top()[1] + 0.76
        timeres_bin_spacing = timeres_trace_xs[1] - timeres_trace_xs[0]
        timeres_bin_width = timeres_bin_spacing * 0.74
        timeres_bin_height = 0.23

        schematic_train = self._make_small_results_matrix(
            self._MINI_TRAIN_VALUES,
            _D_PURP,
            r"$S_2$",
            label_direction=UP,
        )
        timeres_train_explainer = VGroup(
            Tex("Train on", color=INK, font_size=17),
            Tex("Stimulation", color=_D_PURP, font_size=17),
            Tex("Session 2", color=_D_PURP, font_size=17),
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        self._position_small_results_matrix(
            schematic_train,
            np.array([float(np.mean(timeres_trace_xs)), glm_train[1].get_center()[1], 0.0]),
            label_direction=UP,
        )
        schematic_train[1].set_stroke(width=frame_width_final, opacity=frame_opacity_final)
        timeres_train_explainer.next_to(schematic_train[1], RIGHT, buff=0.16)
        timeres_train_explainer.shift(UP * 0.02)

        time_bins = VGroup(*[
            RoundedRectangle(
                width=timeres_bin_width,
                height=timeres_bin_height,
                corner_radius=0.03,
                stroke_color=GREY,
                stroke_width=1.0,
            ).set_fill(WHITE, opacity=1.0).move_to(np.array([x, timeres_strip_y, 0.0]))
            for x in timeres_trace_xs
        ])
        stim_strip = RoundedRectangle(
            width=VGroup(*time_bins[:3]).width + 0.08,
            height=timeres_bin_height + 0.10,
            corner_radius=0.05,
            stroke_width=0.0,
        ).set_fill(test_s1_purple, opacity=0.12).move_to(VGroup(*time_bins[:3]))
        delay_strip = RoundedRectangle(
            width=VGroup(*time_bins[3:13]).width + 0.08,
            height=timeres_bin_height + 0.10,
            corner_radius=0.05,
            stroke_width=0.0,
        ).set_fill(_D_GREEN, opacity=0.12).move_to(VGroup(*time_bins[3:13]))
        post_strip = RoundedRectangle(
            width=VGroup(*time_bins[13:]).width + 0.08,
            height=timeres_bin_height + 0.10,
            corner_radius=0.05,
            stroke_width=0.0,
        ).set_fill(_D_LGREY, opacity=0.18).move_to(VGroup(*time_bins[13:]))
        experimental_design = VGroup(stim_strip, delay_strip, post_strip)
        design_seed = RoundedRectangle(
            width=timeres_bin_width * 1.05,
            height=timeres_bin_height + 0.10,
            corner_radius=0.05,
            stroke_color=GREY,
            stroke_width=1.3,
        ).set_fill(WHITE, opacity=0.0).move_to(experimental_design)

        time_bins_label = Tex(
            "Time points",
            color=INK,
            font_size=16,
        ).next_to(VGroup(*time_bins), UP, buff=0.12)

        delay_fixations = VGroup(*[
            Dot(radius=0.018, color=INK, fill_opacity=0.90).move_to(time_bins[idx])
            for idx in range(3, 13)
        ])

        active_target = _box(LAKE)
        active_target.scale_to_fit_height(timeres_bin_height * 0.82)
        active_target.move_to(time_bins[0])

        memory_target = _box(LAKE)
        memory_target.scale_to_fit_height(timeres_bin_height * 0.82)
        memory_frame = SurroundingRectangle(
            memory_target,
            color=test_s1_purple,
            stroke_width=1.3,
            buff=0.02,
            corner_radius=0.03,
        )
        memory_item = Group(memory_frame, memory_target)
        memory_item.move_to(
            np.array([
                time_bins[0].get_left()[0] - (memory_item.width / 2) - 0.12,
                timeres_strip_y,
                0.0,
            ])
        )

        step_tracker = ValueTracker(0)

        def active_step() -> int:
            return int(np.clip(np.round(step_tracker.get_value()), 0, len(time_bins) - 1))

        def step_center(step_value: float) -> np.ndarray:
            step_value = float(np.clip(step_value, 0.0, len(time_bins) - 1))
            low_idx = int(np.floor(step_value))
            high_idx = min(low_idx + 1, len(time_bins) - 1)
            alpha = step_value - low_idx
            return interpolate(time_bins[low_idx].get_center(), time_bins[high_idx].get_center(), alpha)

        def sweep_trace_prop() -> float:
            step_value = float(np.clip(step_tracker.get_value(), 0.0, len(time_bins) - 1))
            low_idx = int(np.floor(step_value))
            high_idx = min(low_idx + 1, len(timeres_trace_step_props) - 1)
            alpha = step_value - low_idx
            return float(interpolate(
                timeres_trace_step_props[low_idx],
                timeres_trace_step_props[high_idx],
                alpha,
            ))

        def phase_color(step_value: float) -> ManimColor:
            if step_value < 3:
                return test_s1_purple
            if step_value < 13:
                return ManimColor(_D_GREEN)
            return ManimColor(_D_MGREY)

        active_bin = always_redraw(lambda: RoundedRectangle(
            width=timeres_bin_width + 0.05,
            height=timeres_bin_height + 0.07,
            corner_radius=0.04,
            stroke_color=phase_color(step_tracker.get_value()),
            stroke_width=2.0,
        ).set_fill(phase_color(step_tracker.get_value()), opacity=0.16).move_to(step_center(step_tracker.get_value())))
        design_intro_arrow = always_redraw(lambda: Arrow(
            schematic_train[1].get_bottom() + DOWN * 0.04,
            experimental_design.get_center() + UP * (experimental_design.height / 2 + 0.05),
            color=_D_MGREY,
            stroke_width=1.6,
            buff=0.02,
            tip_length=0.10,
        ))
        sweep_arrow = always_redraw(lambda: Arrow(
            schematic_train[1].get_bottom() + DOWN * 0.04,
            step_center(step_tracker.get_value()) + UP * (timeres_bin_height / 2 + 0.05),
            color=_D_MGREY,
            stroke_width=1.6,
            buff=0.02,
            tip_length=0.10,
        ))
        plot_cursor = always_redraw(lambda: DashedLine(
            step_center(step_tracker.get_value()) + DOWN * (timeres_bin_height / 2 + 0.05),
            np.array([
                step_center(step_tracker.get_value())[0],
                timeres_frame.get_top()[1] + 0.03,
                0.0,
            ]),
            color=_D_MGREY,
            stroke_width=1.0,
            dash_length=0.05,
            dashed_ratio=0.65,
        ))
        timeres_trace = always_redraw(
            lambda: self._make_partial_path(timeres_trace_template, sweep_trace_prop())
        )
        timeres_trace_head = always_redraw(lambda: Dot(
            self._make_partial_path(
                timeres_trace_template,
                max(sweep_trace_prop(), 1e-3),
            ).get_end(),
            radius=0.040,
            color=BLACK,
            fill_opacity=1.0,
        ).set_stroke(WHITE, width=1.0))
        timeres_ci.set_z_index(1)
        timeres_chance_group.set_z_index(2)
        timeres_plot_scaffold.set_z_index(2)
        design_intro_arrow.set_z_index(3)
        plot_cursor.set_z_index(3)
        timeres_sig_lines.set_z_index(3)
        timeres_trace.set_z_index(4)
        timeres_trace_head.set_z_index(5)

        return {
            "layout": layout,
            "train_focus_frame": train_focus_frame,
            "delay_focus_frame": delay_focus_frame,
            "delay_decode_arrow": delay_decode_arrow,
            "glm_train": glm_train,
            "glm_stim_test": glm_stim_test,
            "glm_delay_test": glm_delay_test,
            "glm_train_explainer": glm_train_explainer,
            "glm_stim_explainer": glm_stim_explainer,
            "glm_delay_explainer": glm_delay_explainer,
            "glm_plot_frame": glm_plot_frame,
            "glm_plot_rest": glm_plot_rest,
            "glm_plot_scaffold": glm_plot_scaffold,
            "glm_chance_line": glm_chance_line,
            "glm_chance_label": glm_chance_label,
            "glm_left_visual": glm_left_visual,
            "glm_right_visual": glm_right_visual,
            "glm_left_points": glm_left_points,
            "glm_right_points": glm_right_points,
            "glm_left_extras": glm_left_extras,
            "glm_right_extras": glm_right_extras,
            "glm_left_significance": glm_left_significance,
            "glm_right_significance": glm_right_significance,
            "glm_significance_markers": glm_significance_markers,
            "glm_stim_plot_label": glm_stim_plot_label,
            "glm_delay_plot_label": glm_delay_plot_label,
            "glm_left_cloud": glm_left_cloud,
            "glm_right_cloud": glm_right_cloud,
            "glm_left_arrow": glm_left_arrow,
            "glm_right_arrow": glm_right_arrow,
            "glm_title": glm_title,
            "glm_takeaway": glm_takeaway,
            "timeres_title": timeres_title,
            "timeres_plot_scaffold": timeres_plot_scaffold,
            "timeres_frame": timeres_frame,
            "timeres_chance_group": timeres_chance_group,
            "timeres_ci": timeres_ci,
            "timeres_sig_lines": timeres_sig_lines,
            "schematic_train": schematic_train,
            "timeres_train_explainer": timeres_train_explainer,
            "experimental_design": experimental_design,
            "design_seed": design_seed,
            "design_intro_arrow": design_intro_arrow,
            "stim_strip": stim_strip,
            "delay_strip": delay_strip,
            "post_strip": post_strip,
            "time_bins": time_bins,
            "time_bins_label": time_bins_label,
            "delay_fixations": delay_fixations,
            "active_target": active_target,
            "memory_item": memory_item,
            "active_bin": active_bin,
            "sweep_arrow": sweep_arrow,
            "plot_cursor": plot_cursor,
            "timeres_trace": timeres_trace,
            "timeres_trace_head": timeres_trace_head,
            "step_tracker": step_tracker,
            "frame_width_final": frame_width_final,
            "frame_opacity_final": frame_opacity_final,
            "frame_width_emphasis": frame_width_emphasis,
        }

    def _animate_left_results(self, ctx: dict) -> None:
        layout = ctx["layout"]
        glm_train = ctx["glm_train"]
        glm_stim_test = ctx["glm_stim_test"]
        glm_delay_test = ctx["glm_delay_test"]

        self.add(
            layout["slide_title"],
            layout["s2_title"],
            layout["s2_row_group"],
            layout["s1_title"],
            layout["s1_row_group"],
            layout["train_panel"][self._PANEL_BODY_IDX],
            layout["train_panel"][self._PANEL_CONTENT_IDX],
            layout["train_panel"][self._PANEL_ROLE_IDX],
            ctx["train_focus_frame"],
            layout["perception_panel"][self._PANEL_BODY_IDX],
            layout["perception_panel"][self._PANEL_CONTENT_IDX],
            layout["delay_panel"][self._PANEL_BODY_IDX],
            layout["delay_panel"][self._PANEL_CONTENT_IDX],
            layout["delay_panel"][self._PANEL_ROLE_IDX],
            ctx["delay_focus_frame"],
            ctx["delay_decode_arrow"],
        )
        self.wait(0.35)

        self.add(glm_train[1], glm_stim_test[1], glm_delay_test[1])

        self.play(
            FadeOut(layout["slide_title"]),
            FadeOut(layout["s2_title"]),
            FadeOut(layout["s2_row_group"]),
            FadeOut(layout["s1_title"]),
            FadeOut(layout["s1_row_group"]),
            FadeOut(ctx["train_focus_frame"]),
            FadeOut(ctx["delay_focus_frame"]),
            FadeOut(ctx["delay_decode_arrow"]),
            FadeOut(layout["train_panel"][self._PANEL_ROLE_IDX]),
            FadeOut(layout["train_panel"][self._PANEL_CONTENT_IDX]),
            FadeOut(layout["perception_panel"][self._PANEL_CONTENT_IDX]),
            FadeOut(layout["delay_panel"][self._PANEL_ROLE_IDX]),
            FadeOut(layout["delay_panel"][self._PANEL_CONTENT_IDX]),
            ReplacementTransform(layout["train_panel"][self._PANEL_BODY_IDX], glm_train[0]),
            ReplacementTransform(
                layout["perception_panel"][self._PANEL_BODY_IDX],
                glm_stim_test[0],
            ),
            ReplacementTransform(layout["delay_panel"][self._PANEL_BODY_IDX], glm_delay_test[0]),
            FadeIn(glm_train[2], shift=UP * 0.04),
            FadeIn(glm_stim_test[2], shift=UP * 0.04),
            FadeIn(glm_delay_test[2], shift=UP * 0.04),
            FadeIn(ctx["glm_title"], shift=UP * 0.06),
            Create(ctx["glm_plot_frame"]),
            FadeIn(ctx["glm_plot_rest"], shift=UP * 0.08),
            Create(ctx["glm_chance_line"]),
            FadeIn(ctx["glm_chance_label"], shift=UP * 0.04),
            run_time=1.15,
        )
        self.play(
            glm_train[1].animate.set_stroke(width=ctx["frame_width_emphasis"], opacity=1.0),
            FadeIn(ctx["glm_train_explainer"], shift=RIGHT * 0.06),
            run_time=0.45,
        )
        self.wait(2.0)
        self.play(
            GrowArrow(ctx["glm_left_arrow"]),
            GrowArrow(ctx["glm_right_arrow"]),
            run_time=0.55,
        )
        self.wait(0.45)
        self.play(
            glm_stim_test[1].animate.set_stroke(width=ctx["frame_width_emphasis"], opacity=1.0),
            FadeIn(ctx["glm_stim_explainer"], shift=LEFT * 0.06),
            run_time=0.45,
        )
        self.wait(0.25)
        left_cloud_anim = (
            AnimationGroup(
                LaggedStart(
                    *[FadeIn(dot, scale=0.75) for dot in ctx["glm_left_points"]],
                    lag_ratio=0.04,
                ),
                FadeIn(ctx["glm_left_extras"], shift=UP * 0.04),
                lag_ratio=0.18,
            )
            if len(ctx["glm_left_points"]) > 0
            else FadeIn(ctx["glm_left_visual"], shift=UP * 0.04)
        )
        self.play(
            AnimationGroup(
                left_cloud_anim,
                Write(ctx["glm_stim_plot_label"]),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.wait(1.0)
        self.play(
            glm_delay_test[1].animate.set_stroke(width=ctx["frame_width_emphasis"], opacity=1.0),
            FadeIn(ctx["glm_delay_explainer"], shift=RIGHT * 0.06),
            run_time=0.45,
        )
        self.wait(0.25)
        right_cloud_anim = (
            AnimationGroup(
                LaggedStart(
                    *[FadeIn(dot, scale=0.75) for dot in ctx["glm_right_points"]],
                    lag_ratio=0.04,
                ),
                FadeIn(ctx["glm_right_extras"], shift=UP * 0.04),
                lag_ratio=0.18,
            )
            if len(ctx["glm_right_points"]) > 0
            else FadeIn(ctx["glm_right_visual"], shift=UP * 0.04)
        )
        self.play(
            AnimationGroup(
                right_cloud_anim,
                Write(ctx["glm_delay_plot_label"]),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        significance_anims = []
        if len(ctx["glm_left_significance"]) > 0:
            significance_anims.append(
                LaggedStart(
                    *[
                        FadeIn(marker, shift=UP * 0.03)
                        for marker in ctx["glm_left_significance"]
                    ],
                    lag_ratio=0.12,
                )
            )
        if len(ctx["glm_right_significance"]) > 0:
            significance_anims.append(
                FadeIn(ctx["glm_right_significance"], shift=UP * 0.03)
            )
        if significance_anims:
            self.wait(0.35)
            self.play(
                AnimationGroup(*significance_anims, lag_ratio=0.22),
                run_time=0.55,
            )
        self.wait(0.75)
        self.play(
            glm_train[1].animate.set_stroke(
                width=ctx["frame_width_final"], opacity=ctx["frame_opacity_final"]
            ),
            glm_stim_test[1].animate.set_stroke(
                width=ctx["frame_width_final"], opacity=ctx["frame_opacity_final"]
            ),
            glm_delay_test[1].animate.set_stroke(
                width=ctx["frame_width_final"], opacity=ctx["frame_opacity_final"]
            ),
            run_time=0.35,
        )
        self.wait(2.0)

    def _show_left_results_final_state(self, ctx: dict) -> None:
        for matrix in (ctx["glm_train"], ctx["glm_stim_test"], ctx["glm_delay_test"]):
            matrix[1].set_stroke(
                width=ctx["frame_width_final"],
                opacity=ctx["frame_opacity_final"],
            )

        self.add(
            ctx["glm_train"][0],
            ctx["glm_train"][1],
            ctx["glm_train"][2],
            ctx["glm_stim_test"][0],
            ctx["glm_stim_test"][1],
            ctx["glm_stim_test"][2],
            ctx["glm_delay_test"][0],
            ctx["glm_delay_test"][1],
            ctx["glm_delay_test"][2],
            ctx["glm_left_arrow"],
            ctx["glm_right_arrow"],
            ctx["glm_train_explainer"],
            ctx["glm_stim_explainer"],
            ctx["glm_delay_explainer"],
            ctx["glm_title"],
            ctx["glm_plot_scaffold"],
            ctx["glm_left_cloud"],
            ctx["glm_right_cloud"],
            ctx["glm_significance_markers"],
        )

    def _reset_to_left_results_final_state(self, ctx: dict) -> None:
        self.clear()
        self._show_left_results_final_state(ctx)

    def _animate_right_results(self, ctx: dict) -> None:
        design_drop = DOWN * 0.22

        self.play(
            FadeIn(ctx["timeres_title"], shift=UP * 0.06),
            FadeIn(ctx["schematic_train"], shift=UP * 0.06),
            FadeIn(ctx["timeres_train_explainer"], shift=RIGHT * 0.06),
            run_time=0.75,
        )
        self.wait(0.25)
        self.play(
            GrowArrow(ctx["design_intro_arrow"]),
            run_time=0.35,
        )
        self.play(GrowFromCenter(ctx["design_seed"]), run_time=0.28)
        self.play(
            ctx["design_seed"].animate.stretch_to_fit_width(ctx["experimental_design"].width).move_to(
                ctx["experimental_design"]
            ),
            LaggedStart(
                FadeIn(ctx["stim_strip"], scale=0.88),
                FadeIn(ctx["delay_strip"], scale=0.88),
                FadeIn(ctx["post_strip"], scale=0.88),
                lag_ratio=0.16,
            ),
            run_time=0.75,
        )
        self.play(FadeOut(ctx["design_seed"], scale=0.85), run_time=0.2)
        self.play(
            ctx["experimental_design"].animate.shift(design_drop),
            run_time=0.35,
        )
        self.play(
            FadeIn(ctx["timeres_plot_scaffold"], shift=UP * 0.08),
            FadeIn(ctx["timeres_chance_group"]),
            LaggedStart(
                *[FadeIn(bin_mob, shift=UP * 0.03) for bin_mob in ctx["time_bins"]],
                lag_ratio=0.03,
            ),
            run_time=0.8,
        )
        self.play(FadeIn(ctx["time_bins_label"], shift=UP * 0.04), run_time=0.35)
        self.wait(0.2)
        self.play(
            FadeOut(ctx["design_intro_arrow"]),
            FadeIn(ctx["active_bin"]),
            GrowArrow(ctx["sweep_arrow"]),
            FadeIn(ctx["plot_cursor"]),
            FadeIn(ctx["timeres_trace"]),
            FadeIn(ctx["timeres_trace_head"]),
            FadeIn(ctx["active_target"], scale=0.92),
            run_time=0.45,
        )
        self.play(
            ctx["step_tracker"].animate.set_value(2.0),
            ctx["active_target"].animate.move_to(ctx["time_bins"][2]),
            run_time=1.0,
            rate_func=linear,
        )
        self.wait(0.35)
        self.play(
            ctx["active_target"].animate.move_to(ctx["memory_item"].get_center()).set_opacity(0.0),
            FadeIn(ctx["memory_item"]),
            LaggedStart(*[FadeIn(dot) for dot in ctx["delay_fixations"]], lag_ratio=0.08),
            run_time=0.55,
        )
        self.play(
            ctx["step_tracker"].animate.set_value(12.0),
            run_time=2.1,
            rate_func=linear,
        )
        self.wait(0.30)
        self.play(
            ctx["step_tracker"].animate.set_value(len(ctx["time_bins"]) - 1),
            run_time=1.65,
            rate_func=linear,
        )
        self.play(
            FadeIn(ctx["timeres_ci"]),
            FadeIn(ctx["timeres_sig_lines"]),
            run_time=0.6,
        )
        self.play(FadeIn(ctx["glm_takeaway"], shift=UP * 0.08), run_time=0.6)
        self.wait(2.0)

    def construct(self) -> None:
        ctx = self._build_results_context()
        self._animate_left_results(ctx)
        self._animate_right_results(ctx)


class Study2CrossSessionDecodingResultsA(Study2CrossSessionDecodingResults):
    """
    Part A: stop on the GLM plot summary.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsA -ql
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsA -qh
    """

    def construct(self) -> None:
        ctx = self._build_results_context()
        self._animate_left_results(ctx)
        self._reset_to_left_results_final_state(ctx)
        self.wait(2.0)


class Study2CrossSessionDecodingResultsB(Study2CrossSessionDecodingResults):
    """
    Part B: start from the final GLM summary frame and continue to time-resolved decoding.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsB -ql
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsB -qh
    """

    def construct(self) -> None:
        ctx = self._build_results_context()
        self._reset_to_left_results_final_state(ctx)
        self.wait(0.6)
        self._animate_right_results(ctx)


# ══════════════════════════════════════════════════════════════════════════════
# Study2WithinSession1Decoding
# ══════════════════════════════════════════════════════════════════════════════


class Study2WithinSession1Decoding(Study2CrossSessionDecodingResults):
    """
    Explain the rationale for within-session decoding in Session 1, then
    reveal the Session 1 GLM, time-resolved, cross-phase GLM, and
    temporal-generalisation results in two acts.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1Decoding -ql
        uv run manim scenes/study2.py Study2WithinSession1Decoding -qh
    """

    _RESULTS_GLM = "/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_results_ses01glm.svg"
    _RESULTS_TIMERES = "/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_results_ses01timeres.svg"
    _RESULTS_GLM_2 = "/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_results_ses01glm_2.svg"
    _RESULTS_TEMPGEN = "/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_results_ses01tempgen.svg"
    _GLM_ACCENT = _D_PURP
    _DELAY_ACCENT = _D_GREEN

    def _make_results_heading(self, text: str, color: ManimColor = _D_MGREY) -> Tex:
        return Tex(
            text,
            color=color,
            font_size=22,
            tex_environment="center",
        ).next_to(self.slide_title, DOWN, buff=0.12)

    def _make_takeaway(self, lines: list[Tex]) -> VGroup:
        takeaway = VGroup(*lines).arrange(DOWN, buff=0.08, center=True)
        takeaway.move_to(np.array([0.0, -3.15, 0.0]))
        return takeaway

    def _load_svg_plot(
        self,
        path: str,
        *,
        center: np.ndarray,
        height: float,
    ) -> SVGMobject:
        return SVGMobject(path).set_height(height).move_to(center)

    def _hide_svg_background_rect(self, svg: SVGMobject) -> None:
        for submob in svg.submobjects:
            fill_hex = self._glm_svg_hex(submob.get_fill_color())
            stroke_hex = self._glm_svg_hex(submob.get_stroke_color())
            if (
                fill_hex == "#FFFFFF"
                and stroke_hex == "#FFFFFF"
                and submob.width > 0.9 * svg.width
                and submob.height > 0.9 * svg.height
            ):
                submob.set_fill(opacity=0.0)
                submob.set_stroke(opacity=0.0)
                return

    def _hide_svg_white_regions(self, svg: SVGMobject, min_area_ratio: float = 0.02) -> None:
        min_area = svg.width * svg.height * min_area_ratio
        for submob in svg.submobjects:
            fill_hex = self._glm_svg_hex(submob.get_fill_color())
            stroke_hex = self._glm_svg_hex(submob.get_stroke_color())
            if fill_hex == "#FFFFFF" and submob.width * submob.height >= min_area:
                submob.set_fill(opacity=0.0)
                if stroke_hex == "#FFFFFF":
                    submob.set_stroke(opacity=0.0)

    def _timeres_select_many(
        self,
        svg: SVGMobject,
        *,
        stroke_hex: str | None = None,
        fill_hex: str | None = None,
        min_points: int = 0,
    ) -> list[VMobject]:
        stroke_hex = stroke_hex.upper() if stroke_hex else None
        fill_hex = fill_hex.upper() if fill_hex else None
        matches: list[VMobject] = []
        for submob in svg.submobjects:
            if len(submob.get_all_points()) < min_points:
                continue
            stroke_value = self._glm_svg_hex(submob.get_stroke_color())
            fill_value = self._glm_svg_hex(submob.get_fill_color())
            if stroke_hex and stroke_value != stroke_hex:
                continue
            if fill_hex and fill_value != fill_hex:
                continue
            matches.append(submob)
        return matches

    def _timeres_select_single(
        self,
        svg: SVGMobject,
        *,
        stroke_hex: str | None = None,
        fill_hex: str | None = None,
        min_points: int = 0,
    ) -> VMobject:
        matches = self._timeres_select_many(
            svg,
            stroke_hex=stroke_hex,
            fill_hex=fill_hex,
            min_points=min_points,
        )
        if len(matches) != 1:
            raise ValueError(
                f"Expected one timeres match for stroke={stroke_hex} fill={fill_hex}, found {len(matches)}"
            )
        return matches[0]

    def _timeres_significance_bands(self, svg: SVGMobject) -> VGroup:
        return VGroup(*self._timeres_select_many(svg, stroke_hex="#C49A00", min_points=4))

    def _glm_svg_center_group(self, svg: SVGMobject, color_hex: str) -> VGroup:
        plot_frame = self._glm_svg_plot_frame(svg)
        x_pad = plot_frame.width * 0.03
        y_pad = plot_frame.height * 0.03
        color_hex = color_hex.upper()
        return VGroup(*[
            submob
            for submob in svg.submobjects
            if (
                self._glm_svg_hex(submob.get_fill_color()) == color_hex
                or self._glm_svg_hex(submob.get_stroke_color()) == color_hex
            )
            and plot_frame.get_left()[0] - x_pad <= submob.get_center()[0] <= plot_frame.get_right()[0] + x_pad
            and plot_frame.get_bottom()[1] - y_pad <= submob.get_center()[1] <= plot_frame.get_top()[1] + y_pad
        ])

    def _glm_svg_center_significance_marker(self, svg: SVGMobject, color_hex: str) -> VGroup:
        plot_frame = self._glm_svg_plot_frame(svg)
        color_hex = color_hex.upper()
        return VGroup(*[
            submob
            for submob in svg.submobjects
            if (
                self._glm_svg_hex(submob.get_fill_color()) == color_hex
                or self._glm_svg_hex(submob.get_stroke_color()) == color_hex
            )
            and submob.get_center()[1] > plot_frame.get_top()[1]
        ])

    def construct(self) -> None:
        self.camera.background_color = BG

        layout = self._build_cross_session_layout()
        for mob in layout["s2_dim_mobs"]:
            mob.set_opacity(0.18)
        for mob in layout["dim_right_mobs"]:
            mob.set_opacity(0.18)

        self.slide_title = Tex("Within-session decoding in Session 1", color=INK, font_size=30)
        self.slide_title.to_edge(UP, buff=0.18)
        act1_heading = self._make_results_heading(
            r"1. Is there any stimulus-specific information in the delay period in V1-V3?",
            color=BLACK,
        )
        act2_heading = self._make_results_heading(
            r"2. Does the encoding code generalise to the delay?"
        )

        intro_question = VGroup(
            Tex(
                "Cross-session decoding showed that sensory-trained",
                color=INK,
                font_size=21,
            ),
            Tex(
                "classifiers do not generalise throughout the full delay.",
                color=INK,
                font_size=21,
            ),
            Tex(
                "We now ask whether Session 1 still carries",
                color=INK,
                font_size=21,
            ),
            Tex(
                "stimulus-specific information in its own format.",
                color=INK,
                font_size=21,
            ),
        ).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
        intro_question.move_to(np.array([-4.00, -1.08, 0.0]))

        repeated_note = Tex(
            r"Within-Session 1 identity decoding uses repeated stimuli only.",
            color=_D_MGREY,
            font_size=18,
            tex_environment="center",
        ).move_to(np.array([-4.00, -2.32, 0.0]))

        plot_title_y = self.slide_title.get_bottom()[1] - 0.95

        glm_title = Tex("GLM-based decoding", color=INK, font_size=22).move_to(
            np.array([-3.05, plot_title_y, 0.0])
        )
        glm_svg = self._load_svg_plot(
            self._RESULTS_GLM,
            center=np.array([-3.05, -0.10, 0.0]),
            height=3.55,
        )
        glm_base = glm_svg.copy()
        self._glm_svg_hide_color_groups(glm_base)
        glm_plot_frame = self._glm_svg_plot_frame(glm_base)
        glm_chance_template = self._glm_svg_chance_line(glm_base)
        glm_plot_rest = VGroup(*[
            submob
            for submob in glm_base.submobjects
            if submob not in glm_plot_frame.submobjects
            and submob is not glm_chance_template
        ])
        glm_left_group = self._glm_svg_group(glm_svg, "#7B51A0", "left")
        glm_right_group = self._glm_svg_group(glm_svg, "#3C9553", "right")
        glm_left_significance = self._glm_svg_significance_marker(glm_svg, "#7B51A0", "left")
        glm_right_significance = self._glm_svg_significance_marker(glm_svg, "#3C9553", "right")
        glm_left_visual = VGroup(*[
            submob for submob in glm_left_group if submob not in glm_left_significance
        ])
        glm_right_visual = VGroup(*[
            submob for submob in glm_right_group if submob not in glm_right_significance
        ])
        glm_left_points = self._glm_svg_scatter_points(glm_left_visual)
        glm_right_points = self._glm_svg_scatter_points(glm_right_visual)
        glm_left_extras = VGroup(*[
            submob for submob in glm_left_visual if submob not in glm_left_points
        ])
        glm_right_extras = VGroup(*[
            submob for submob in glm_right_visual if submob not in glm_right_points
        ])
        glm_left_x = (
            glm_left_points.get_center()[0]
            if len(glm_left_points) > 0
            else glm_left_group.get_center()[0]
        )
        glm_right_x = (
            glm_right_points.get_center()[0]
            if len(glm_right_points) > 0
            else glm_right_group.get_center()[0]
        )
        glm_left_label = self._glm_svg_bottom_label(
            glm_plot_frame,
            glm_left_x,
            r"S_1 \rightarrow S_1",
        )
        glm_right_label = self._glm_svg_bottom_label(
            glm_plot_frame,
            glm_right_x,
            r"D_1 \rightarrow D_1",
        )
        glm_chance_y = glm_chance_template.get_center()[1]
        glm_chance_color = glm_chance_template.get_stroke_color()
        glm_chance_line = DashedLine(
            np.array([glm_plot_frame.get_left()[0], glm_chance_y, 0.0]),
            np.array([glm_plot_frame.get_right()[0], glm_chance_y, 0.0]),
            color=glm_chance_color,
            stroke_width=2.0,
            dash_length=0.08,
            dashed_ratio=0.55,
        )
        glm_chance_label = Tex(
            "Chance",
            color=glm_chance_color,
            font_size=14,
        ).move_to(
            np.array([glm_plot_frame.get_right()[0] - 0.26, glm_chance_y + 0.14, 0.0])
        )
        glm_left_cloud = VGroup(glm_left_points, glm_left_extras, glm_left_label)
        glm_right_cloud = VGroup(glm_right_points, glm_right_extras, glm_right_label)
        glm_significance = VGroup(glm_left_significance, glm_right_significance)
        glm_plot = Group(
            glm_title,
            glm_plot_frame,
            glm_plot_rest,
            glm_chance_line,
            glm_chance_label,
            glm_left_cloud,
            glm_right_cloud,
            glm_significance,
        )

        timeres_title = Tex("Time-resolved decoding", color=INK, font_size=22).move_to(
            np.array([3.05, plot_title_y, 0.0])
        )
        timeres_svg = self._load_svg_plot(
            self._RESULTS_TIMERES,
            center=np.array([3.05, -0.10, 0.0]),
            height=3.55,
        )
        self._hide_svg_background_rect(timeres_svg)
        timeres_base = timeres_svg.copy()
        self._hide_svg_background_rect(timeres_base)
        timeres_ci = self._timeres_select_single(timeres_svg, fill_hex="#6E6E6E", min_points=100)
        timeres_trace = self._timeres_select_single(timeres_svg, stroke_hex="#000000", min_points=50)
        timeres_sig_bands = self._timeres_significance_bands(timeres_svg)
        self._timeres_select_single(timeres_base, fill_hex="#6E6E6E", min_points=100).set_opacity(0.0)
        self._timeres_select_single(timeres_base, stroke_hex="#000000", min_points=50).set_opacity(0.0)
        self._timeres_significance_bands(timeres_base).set_opacity(0.0)
        timeres_ci.set_stroke(opacity=0.0)
        timeres_ci.set_fill(color="#6E6E6E", opacity=0.28)
        timeres_trace.set_fill(opacity=0.0)
        timeres_trace.set_stroke(color=BLACK, width=5.0)
        timeres_sig_bands.set_stroke(color="#C49A00", width=4.2)
        timeres_plot = Group(
            timeres_title,
            timeres_base,
            timeres_ci,
            timeres_trace,
            timeres_sig_bands,
        )

        act1_takeaway_line_1 = Tex(
            r"Object identity is decodable within {{encoding}} and within {{delay}}.",
            color=INK,
            font_size=24,
        )
        act1_takeaway_line_1.set_color_by_tex("encoding", self._GLM_ACCENT)
        act1_takeaway_line_1.set_color_by_tex("delay", self._DELAY_ACCENT)
        act1_takeaway_line_2 = Tex(
            r"Time-resolved decoding shows reliable delay-period information in Session 1.",
            color=INK,
            font_size=24,
            tex_environment="center",
        )
        act1_takeaway = self._make_takeaway([
            act1_takeaway_line_1,
            act1_takeaway_line_2,
        ])

        glm2_title = Tex("Cross-phase GLM decoding", color=INK, font_size=22).move_to(
            np.array([-3.05, plot_title_y, 0.0])
        )
        glm2_svg = self._load_svg_plot(
            self._RESULTS_GLM_2,
            center=np.array([-3.05, -0.15, 0.0]),
            height=3.42,
        )
        self._hide_svg_background_rect(glm2_svg)
        glm2_base = glm2_svg.copy()
        self._hide_svg_background_rect(glm2_base)
        self._glm_svg_center_group(glm2_base, "#0D0F0E").set_opacity(0.0)
        self._glm_svg_center_significance_marker(glm2_base, "#0D0F0E").set_opacity(0.0)
        glm2_plot_frame = self._glm_svg_plot_frame(glm2_base)
        glm2_chance_template = self._glm_svg_chance_line(glm2_base)
        glm2_plot_rest = VGroup(*[
            submob
            for submob in glm2_base.submobjects
            if submob not in glm2_plot_frame.submobjects
            and submob is not glm2_chance_template
        ])
        glm2_group = self._glm_svg_center_group(glm2_svg, "#0D0F0E")
        glm2_sig = self._glm_svg_center_significance_marker(glm2_svg, "#0D0F0E")
        glm2_points = self._glm_svg_scatter_points(glm2_group)
        glm2_extras = VGroup(*[
            submob for submob in glm2_group if submob not in glm2_points
        ])
        glm2_label = self._glm_svg_bottom_label(
            glm2_plot_frame,
            glm2_points.get_center()[0] if len(glm2_points) > 0 else glm2_group.get_center()[0],
            r"S_1 \rightarrow D_1",
        )
        glm2_chance_y = glm2_chance_template.get_center()[1]
        glm2_chance_color = glm2_chance_template.get_stroke_color()
        glm2_chance_line = DashedLine(
            np.array([glm2_plot_frame.get_left()[0], glm2_chance_y, 0.0]),
            np.array([glm2_plot_frame.get_right()[0], glm2_chance_y, 0.0]),
            color=glm2_chance_color,
            stroke_width=2.0,
            dash_length=0.08,
            dashed_ratio=0.55,
        )
        glm2_chance_label = Tex(
            "Chance",
            color=glm2_chance_color,
            font_size=14,
        ).move_to(
            np.array([glm2_plot_frame.get_right()[0] - 0.24, glm2_chance_y + 0.14, 0.0])
        )
        glm2_plot = Group(
            glm2_title,
            glm2_plot_frame,
            glm2_plot_rest,
            glm2_chance_line,
            glm2_chance_label,
            glm2_points,
            glm2_extras,
            glm2_label,
            glm2_sig,
        )

        tempgen_title = Tex("Temporal generalisation", color=INK, font_size=22).move_to(
            np.array([3.15, plot_title_y, 0.0])
        )
        tempgen_center = np.array([3.15, -0.12, 0.0])
        tempgen_underlay = (
            ImageMobject(str(Path(self._RESULTS_TEMPGEN).with_suffix(".png")))
            .set_height(3.55)
            .move_to(tempgen_center)
        )
        tempgen_underlay.set_opacity(0.86)
        tempgen_overlay = self._load_svg_plot(
            self._RESULTS_TEMPGEN,
            center=tempgen_center,
            height=3.55,
        )
        self._hide_svg_white_regions(tempgen_overlay)
        tempgen_plot = Group(
            tempgen_title,
            tempgen_underlay,
            tempgen_overlay,
        )

        stim_small = self._make_small_results_matrix(
            self._row_values(0, 0),
            self._GLM_ACCENT,
            r"$S_1$",
            label_direction=UP,
        )
        delay_small = self._make_small_results_matrix(
            self._delay_row_values(0, 0),
            self._DELAY_ACCENT,
            r"$D_1$",
            label_direction=UP,
        )
        self._position_small_results_matrix(
            stim_small,
            np.array([-0.95, 2.18, 0.0]),
            label_direction=UP,
        )
        self._position_small_results_matrix(
            delay_small,
            np.array([0.95, 2.18, 0.0]),
            label_direction=UP,
        )
        cross_phase_arrow = Arrow(
            stim_small[1].get_right() + RIGHT * 0.06,
            delay_small[1].get_left() + LEFT * 0.06,
            color=_D_MGREY,
            stroke_width=1.8,
            buff=0.02,
            tip_length=0.12,
        )
        cross_phase_label = Tex(
            "Cross-phase test",
            color=_D_MGREY,
            font_size=17,
        ).next_to(cross_phase_arrow, UP, buff=0.08)

        act2_takeaway_line_1 = Tex(
            r"{{Encoding}} patterns do not generalise cleanly to the {{delay}}.",
            color=INK,
            font_size=24,
        )
        act2_takeaway_line_1.set_color_by_tex("Encoding", self._GLM_ACCENT)
        act2_takeaway_line_1.set_color_by_tex("delay", self._DELAY_ACCENT)
        act2_takeaway_line_2 = Tex(
            r"Temporal generalisation indicates a distinct, non-stationary code across the trial.",
            color=INK,
            font_size=24,
            tex_environment="center",
        )
        act2_takeaway = self._make_takeaway([
            act2_takeaway_line_1,
            act2_takeaway_line_2,
        ])

        self.add(self.slide_title, act1_heading)
        self.play(
            FadeIn(layout["s2_title"]),
            FadeIn(layout["s2_row_group"]),
            FadeIn(layout["s1_title"]),
            FadeIn(layout["s1_row_group"]),
            run_time=0.80,
        )
        self.wait(0.15)
        self.play(
            layout["s2_title"].animate.set_opacity(0.18),
            layout["s2_row_group"].animate.set_opacity(0.18),
            run_time=0.40,
        )
        self.play(
            Create(layout["target_hi"]),
            Create(layout["delay_hi"]),
            FadeIn(intro_question, shift=UP * 0.06),
            FadeIn(repeated_note, shift=UP * 0.04),
            run_time=0.75,
        )
        self.play(
            GrowArrow(layout["target_arrow"]),
            GrowArrow(layout["delay_arrow"]),
            FadeIn(layout["perception_panel"], shift=UP * 0.08),
            FadeIn(layout["delay_panel"], shift=UP * 0.08),
            run_time=0.80,
        )
        self.wait(1.3)

        self.play(
            FadeOut(layout["s2_title"]),
            FadeOut(layout["s2_row_group"]),
            FadeOut(layout["s1_title"]),
            FadeOut(layout["s1_row_group"]),
            FadeOut(layout["target_hi"]),
            FadeOut(layout["delay_hi"]),
            FadeOut(layout["target_arrow"]),
            FadeOut(layout["delay_arrow"]),
            FadeOut(layout["perception_panel"]),
            FadeOut(layout["delay_panel"]),
            FadeOut(intro_question),
            FadeOut(repeated_note),
            run_time=0.75,
        )

        self.play(
            FadeIn(glm_title, shift=UP * 0.05),
            AnimationGroup(
                Create(glm_plot_frame),
                FadeIn(glm_plot_rest, shift=UP * 0.08),
                Create(glm_chance_line),
                FadeIn(glm_chance_label, shift=UP * 0.04),
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )
        self.play(
            AnimationGroup(
                LaggedStart(*[FadeIn(dot, scale=0.75) for dot in glm_left_points], lag_ratio=0.04),
                FadeIn(glm_left_extras, shift=UP * 0.04),
                Write(glm_left_label),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                LaggedStart(*[FadeIn(dot, scale=0.75) for dot in glm_right_points], lag_ratio=0.04),
                FadeIn(glm_right_extras, shift=UP * 0.04),
                Write(glm_right_label),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.play(
            LaggedStart(
                *[FadeIn(marker, shift=UP * 0.03) for marker in glm_left_significance],
                *[FadeIn(marker, shift=UP * 0.03) for marker in glm_right_significance],
                lag_ratio=0.10,
            ),
            run_time=0.65,
        )
        self.wait(0.35)
        self.play(
            FadeIn(timeres_title, shift=UP * 0.05),
            FadeIn(timeres_base, shift=UP * 0.08),
            run_time=0.85,
        )
        self.play(Create(timeres_trace), run_time=1.9)
        self.play(
            AnimationGroup(
                FadeIn(timeres_ci),
                LaggedStart(*[Create(sig_band) for sig_band in timeres_sig_bands], lag_ratio=0.12),
                lag_ratio=0.0,
            ),
            run_time=0.9,
        )
        self.play(FadeIn(act1_takeaway, shift=UP * 0.08), run_time=0.65)
        self.wait(1.8)

        self.play(
            Transform(act1_heading, act2_heading),
            FadeOut(act1_takeaway, shift=DOWN * 0.06),
            FadeOut(glm_plot, shift=DOWN * 0.08),
            FadeOut(timeres_plot, shift=DOWN * 0.08),
            run_time=0.75,
        )
        self.play(
            FadeIn(stim_small, shift=UP * 0.05),
            FadeIn(delay_small, shift=UP * 0.05),
            GrowArrow(cross_phase_arrow),
            FadeIn(cross_phase_label, shift=UP * 0.04),
            run_time=0.70,
        )
        self.wait(0.45)
        self.play(
            FadeIn(glm2_title, shift=UP * 0.05),
            AnimationGroup(
                Create(glm2_plot_frame),
                FadeIn(glm2_plot_rest, shift=UP * 0.08),
                Create(glm2_chance_line),
                FadeIn(glm2_chance_label, shift=UP * 0.04),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                LaggedStart(*[FadeIn(dot, scale=0.75) for dot in glm2_points], lag_ratio=0.04),
                FadeIn(glm2_extras, shift=UP * 0.04),
                Write(glm2_label),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.play(FadeIn(glm2_sig, shift=UP * 0.03), run_time=0.5)
        self.wait(0.35)
        self.play(
            FadeIn(tempgen_title, shift=UP * 0.05),
            FadeIn(tempgen_underlay, shift=UP * 0.08),
            FadeIn(tempgen_overlay, shift=UP * 0.06),
            run_time=0.90,
        )
        self.play(FadeIn(act2_takeaway, shift=UP * 0.08), run_time=0.65)
        self.wait(2.0)
