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
from utils import env_path

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

FMRI_STIM_DIR = Path("/Users/leonardo/sd-wltm-fmri-experiment/images/stimuli_task")

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
    Phase 1 — Paradigm overview: show the two-session SVG diagram, then
              spotlight Session 2 as the source of training data.
    Phase 2 — Session 2 detail: three target images → voxel bar vectors.
    Phase 3 — Classification: 3-class scatter + decision boundaries.
    """

    _PARADIGM_SVG = Path(
        "/Users/leonardo/phd-thesis-animations/assets/images/study2/study2_paradigm.svg"
    )

    # Three target images from the fMRI stimulus set
    _IMGS = [
        ("ANI-CAT-T00.png", BLUE,          "cat"),
        ("BUI-MOD-T00.png", AMBER,          "building"),
        ("LAN-MOO-T00.png", "#7C3AED",      "landscape"),
    ]

    # Mock voxel vectors per image (8 dims, clearly distinct)
    _VECS = {
        "cat":       np.array([0.85, 0.15, 0.70, 0.30, 0.90, 0.20, 0.65, 0.40]),
        "building":  np.array([0.20, 0.85, 0.25, 0.80, 0.15, 0.75, 0.30, 0.90]),
        "landscape": np.array([0.50, 0.55, 0.90, 0.10, 0.45, 0.80, 0.15, 0.60]),
    }

    # 2-D scatter positions per class
    _PTS = {
        "cat":       [(-2.2, 0.8), (-1.8, -0.1), (-2.5, 0.2), (-1.9, 1.0), (-2.4, -0.5)],
        "building":  [( 1.6, 0.4), ( 2.0, -0.4), ( 1.3, 0.9), ( 2.2, 0.3), ( 1.8, -0.9)],
        "landscape": [( 0.1, 1.5), (-0.3, 1.1), ( 0.5, 1.8), (-0.1, 1.3), ( 0.3, 0.9)],
    }

    def construct(self) -> None:
        self.camera.background_color = BG

        # ══ Phase 1: Paradigm overview ════════════════════════════════════════

        title = Tex("How do we train the classifier?", color=INK, font_size=36)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)
        self.wait(0.2)

        # Show paradigm SVG centred on screen
        paradigm = SVGMobject(str(self._PARADIGM_SVG)) \
            .set_height(5.2).move_to(DOWN * 0.3)
        self.play(FadeIn(paradigm, shift=UP * 0.15), run_time=0.9)
        self.wait(0.6)

        # Session labels placed over the SVG halves (left = S1, right = S2)
        s1_lbl = Tex("Session 1", color=INK, font_size=24) \
            .move_to(LEFT * 3.4 + UP * 2.4)
        s1_sub = Tex("Working Memory task", color=MGREY, font_size=20) \
            .next_to(s1_lbl, DOWN, buff=0.1)
        s2_lbl = Tex("Session 2", color=BLUE, font_size=24) \
            .move_to(RIGHT * 3.4 + UP * 2.4)
        s2_sub = Tex("Perceptual task", color=BLUE, font_size=20) \
            .next_to(s2_lbl, DOWN, buff=0.1)

        self.play(
            Write(s1_lbl), FadeIn(s1_sub),
            Write(s2_lbl), FadeIn(s2_sub),
            run_time=0.7,
        )
        self.wait(0.5)

        # Highlight the Session 2 half with a blue rectangle
        s2_rect = Rectangle(
            width=6.2, height=5.5,
            color=BLUE, stroke_width=2.5,
        ).set_fill(BLUE, opacity=0.07).move_to(RIGHT * 3.4 + DOWN * 0.3)

        train_arrow = CurvedArrow(
            s2_rect.get_bottom() + DOWN * 0.1,
            RIGHT * 3.4 + DOWN * 3.2,
            angle=-TAU / 6, color=BLUE, stroke_width=2,
        )
        train_note = Tex("used to train classifier", color=BLUE, font_size=22) \
            .next_to(train_arrow.get_end(), DOWN, buff=0.08)

        self.play(Create(s2_rect), run_time=0.6)
        self.play(Create(train_arrow), Write(train_note), run_time=0.7)
        self.wait(0.8)

        # Fade out everything except the title; transition to Phase 2
        self.play(
            FadeOut(VGroup(
                paradigm, s1_lbl, s1_sub, s2_lbl, s2_sub,
                s2_rect, train_arrow, train_note,
            )),
            run_time=0.6,
        )

        # ══ Phase 2: image → voxel vector ════════════════════════════════════

        subtitle = Tex(
            r"Session 2: participant views each image once per run "
            r"$\;\cdot\;$ brain activity recorded",
            color=MGREY, font_size=22,
        ).next_to(title, DOWN, buff=0.16)
        self.play(FadeIn(subtitle), run_time=0.4)
        self.wait(0.2)

        # Three rows: image  →  bar vector
        row_ys = [1.15, 0.0, -1.15]

        all_bars   = []
        all_vlbls  = []

        for (fname, col, key), ry in zip(self._IMGS, row_ys):
            img = ImageMobject(fmri_stim(fname)).set_height(1.2) \
                .move_to(LEFT * 5.3 + UP * ry)
            bdr = SurroundingRectangle(img, color=LGREY, stroke_width=1.5, buff=0.04)
            lbl = Tex(key, color=col, font_size=21).next_to(img, LEFT, buff=0.14)

            arr = Arrow(
                LEFT * 4.4 + UP * ry,
                LEFT * 3.0 + UP * ry,
                color=MGREY, stroke_width=2, buff=0.1,
            )

            bar = make_voxel_bar(self._VECS[key], color=col, bar_max_h=0.85) \
                .scale(0.78).move_to(LEFT * 1.7 + UP * ry)
            vlbl = Tex(rf"$\mathbf{{v}}_\text{{{key[:3]}}}$", color=col, font_size=21) \
                .next_to(bar, RIGHT, buff=0.14)

            self.play(FadeIn(Group(img, bdr)), Write(lbl), run_time=0.4)
            self.play(GrowArrow(arr), run_time=0.35)
            self.play(FadeIn(bar), Write(vlbl), run_time=0.4)
            self.wait(0.1)

            all_bars.append(bar)
            all_vlbls.append(vlbl)

        self.wait(0.4)

        # ── Divider ───────────────────────────────────────────────────────────
        div = Line(UP * 2.6 + RIGHT * 0.0, DOWN * 2.6 + RIGHT * 0.0,
                   color=LGREY, stroke_width=1.2)
        self.play(Create(div), run_time=0.3)

        # ══ Phase 3: 2-D scatter + decision boundaries ════════════════════════

        ax = Axes(
            x_range=[-3.2, 3.2, 1],
            y_range=[-1.4, 2.4, 1],
            x_length=4.6,
            y_length=3.4,
            axis_config={
                "color": LGREY, "stroke_width": 1.5,
                "include_ticks": False,
                "tip_shape": StealthTip, "tip_length": 0.15,
            },
        ).move_to(RIGHT * 3.2 + DOWN * 0.1)

        ax_xl = Tex("Voxel dim 1", color=MGREY, font_size=17) \
            .next_to(ax.x_axis.get_right(), DOWN, buff=0.1)
        ax_yl = Tex("Voxel dim 2", color=MGREY, font_size=17) \
            .next_to(ax.y_axis.get_top(), LEFT, buff=0.1)

        self.play(Create(ax), Write(ax_xl), Write(ax_yl), run_time=0.7)

        colors_map = {"cat": BLUE, "building": AMBER, "landscape": "#7C3AED"}
        for key, col in colors_map.items():
            dots = VGroup(*[
                Dot(ax.c2p(x, y), radius=0.10, color=col, fill_opacity=0.85)
                for x, y in self._PTS[key]
            ])
            leg = Tex(key[:3], color=col, font_size=18) \
                .next_to(dots[0], UP, buff=0.08)
            self.play(
                LaggedStartMap(FadeIn, dots, lag_ratio=0.12),
                Write(leg),
                run_time=0.6,
            )

        self.wait(0.3)

        # Schematic decision boundaries (two dashed lines)
        b1 = DashedLine(ax.c2p(-1.0, -1.2), ax.c2p(1.5, 2.2),
                        color=RED, stroke_width=2.2, dash_length=0.11)
        b2 = DashedLine(ax.c2p(-3.0, 0.6), ax.c2p(0.8, -1.2),
                        color=RED, stroke_width=2.2, dash_length=0.11)
        bound_lbl = Tex("decision boundaries", color=RED, font_size=18) \
            .next_to(ax, DOWN, buff=0.18)

        self.play(Create(b1), Create(b2), run_time=0.7)
        self.play(Write(bound_lbl), run_time=0.4)
        self.wait(0.4)

        # ── Bottom message ─────────────────────────────────────────────────────
        msg = Tex(
            r"Classifier learns the \textit{perceptual} code from Session 2",
            color=INK, font_size=24,
        ).to_edge(DOWN, buff=0.35)
        self.play(Write(msg), run_time=0.9)
        self.wait(1.5)


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
