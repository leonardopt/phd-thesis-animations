"""
Study 2 — Experimental Design.

  Study2ExperimentalDesign — two-session paradigm diagram:
      Session 1: Memory task    (Target → Delay → Probe 1 → Buffer → Probe 2 → Response → ITI)
      Session 2: Perceptual task (Stimulus 1 → ISI → Stimulus 2 → ISI → Stimulus 3)

Render:
    uv run manim scenes/study2_design.py Study2ExperimentalDesign -qh
"""
from __future__ import annotations

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
        self.play(FadeIn(n_lbl), run_time=0.5)
        self.wait(2.0)
