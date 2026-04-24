"""
Study 2 — sectioned production render.

Render from this file to keep all Study 2 outputs in the same
`media/videos/04_study2/...` folder.

Production render:
    uv run manim scenes/study2.py Study2 -ql --save_sections
"""
from __future__ import annotations
import base64
import gc
from io import BytesIO
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from nilearn.plotting import plot_stat_map
from pathlib import Path
from PIL import Image
from manim import *
from svgelements import Path as SVGPath

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from utils import section_output_dir, simplify_manim_section_video_names

REPO_ROOT = Path(__file__).resolve().parent.parent
_SECTION_OUTPUT_DIR = section_output_dir("study2")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "study2"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)
_STUDY2_ASSET_DIR = REPO_ROOT / "assets" / "images" / "study2"
_STUDY2_STIM_DIR = _STUDY2_ASSET_DIR / "stimuli_task"
_STUDY2_TRAINING_DIR = _STUDY2_ASSET_DIR / "stimuli_training"


class _Study2NumberedScene:
    """Compatibility mixin for legacy Study 2 scene classes."""

    def __init__(self, *args, **kwargs):
        """Forward to the regular Scene initialization."""
        super().__init__(*args, **kwargs)


def _study2_lookup_color(
    image_path: str,
    color_map: dict[str, str],
    label: str,
) -> str:
    """Return one registered color from the provided image-to-color map."""
    # Keep the label text caller-specific so helper reuse does not flatten the
    # public KeyError surface that the scene-specific wrappers already expose.
    if image_path not in color_map:
        raise KeyError(f"No {label} registered for {image_path}")
    return color_map[image_path]


def _study2_vector_layout(
    col_ys: tuple[float, float, float] | list[float],
    vector_center_x: float,
    count: int,
) -> list[np.ndarray]:
    """Return evenly spaced vector centres across the shared Study 2 column."""
    # Only the top and bottom y positions matter here; the centre is derived so
    # all three overview variants stay vertically aligned.
    ys = np.linspace(col_ys[0], col_ys[2], count)
    return [np.array([vector_center_x, float(y), 0.0]) for y in ys]


def _study2_synced_source_pulse(t: float) -> float:
    """Return the synchronized source pulse animation."""
    if t <= 0.12:
        return 0.0
    return there_and_back((t - 0.12) / 0.88)


def _study2_color_hex(color) -> str | None:
    """Return the normalized uppercase hex representation for a color."""
    if color is None:
        return None
    if isinstance(color, str):
        return ManimColor(color).to_hex().upper()
    return color.to_hex().upper()


def _study2_clear_camera_context_cache(camera: object) -> None:
    """Drop cached Cairo contexts after changing the camera frame transform."""
    cache = getattr(camera, "pixel_array_to_cairo_context", None)
    if isinstance(cache, dict):
        cache.clear()


# ── Palette ───────────────────────────────────────────────────────────────────
BG   = WHITE
INK  = "#1C1C1E"
GREY = "#D1D5DB"   # box border only

# ── Image paths ───────────────────────────────────────────────────────────────
_STIM = _STUDY2_STIM_DIR
LAKE = str(_STIM / "LAN-LAK-T00.png")
LAKE_D1 = str(_STIM / "LAN-LAK-D01.png")
LAKE_D2 = str(_STIM / "LAN-LAK-D02.png")
PINE = str(_STIM / "PLA-PIN-T00.png")
OBS = str(_STIM / "BUI-OBS-T00.png")
CAT = str(_STIM / "ANI-CAT-T00.png")
VASE = str(_STIM / "ITE-VAS-T00.png")
BRI = str(_STIM / "PLA-BRI-T00.png")
SOFA = str(_STUDY2_TRAINING_DIR / "ITE-SOF-T00.png")
FIX = str(REPO_ROOT / "assets" / "images" / "fixation_target.png")

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
    rect.set_z_index(0)

    parts: list = [rect]

    if img_path is not None:
        img = ImageMobject(img_path).scale_to_fit_height(IMG_H)
        img.move_to(rect.get_center())
        img.set_z_index(1)
        parts.append(img)

    # Fixation dot on every box
    fix = ImageMobject(FIX).scale_to_fit_height(FIX_H)
    fix.move_to(rect.get_center())
    fix.set_z_index(2)
    parts.append(fix)

    if resp:
        two = Tex("TWO", color=INK, font_size=13).move_to(rect.get_center() + LEFT  * 0.30)
        one = Tex("ONE", color=INK, font_size=13).move_to(rect.get_center() + RIGHT * 0.30)
        two.set_z_index(3)
        one.set_z_index(3)
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

_RQ_MUTED = "#6B7280"
_RQ_RULE  = "#D1D5DB"
_RQ_ACCENT = "#BFA5AA"


class Study2ResearchQuestions(_Study2NumberedScene, Scene):
    """
    Opening slide for Study 2: three research questions addressed by the
    fMRI experiment, anchored to the early visual cortex.

    Render:
        uv run manim scenes/study2.py Study2ResearchQuestions -ql
    """

    def _make_rq_item(
        self,
        number: str,
        title: str,
        body: str,
    ) -> VGroup:
        num_label = Tex(
            rf"\textbf{{{number}}}",
            color=_RQ_ACCENT,
            font_size=18,
        )
        title_mob = Tex(
            r"\textbf{" + title + "}",
            color=INK,
            font_size=23,
        )
        body_mob = Tex(
            body,
            color=INK,
            font_size=17,
        )
        text_block = VGroup(title_mob, body_mob).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.10,
        )
        return VGroup(num_label, text_block).arrange(
            RIGHT,
            aligned_edge=UP,
            buff=0.38,
        )

    def _make_evc_brain(self) -> Group:
        brain = ImageMobject(str(_BRAIN_PNG_PATH)).scale_to_fit_width(2.55)

        roi_box = RoundedRectangle(
            width=0.52,
            height=0.68,
            corner_radius=0.04,
            stroke_color=_RQ_ACCENT,
            stroke_width=1.0,
        ).set_fill(WHITE, opacity=0.18)
        roi_box.move_to(brain.get_center() + RIGHT * 0.74 + DOWN * 0.05)

        connector = Line(
            roi_box.get_right(),
            roi_box.get_right() + RIGHT * 0.52,
            stroke_color=_RQ_ACCENT,
            stroke_width=1.0,
        )
        region_label = Tex(
            "[V1, V2, V3]",
            color=INK,
            font_size=15,
        ).next_to(connector, RIGHT, buff=0.10)

        return Group(brain, roi_box, connector, region_label)

    def construct(self) -> None:
        self.camera.background_color = BG

        title = Tex(
            r"\textbf{Three research questions}",
            color=INK,
            font_size=33,
        ).to_edge(UP, buff=0.46)

        title_dot = Dot(
            radius=0.04,
            color=_RQ_ACCENT,
            fill_opacity=1.0,
            stroke_width=0.0,
        )
        underline = Line(
            ORIGIN,
            RIGHT * 2.30,
            stroke_color=_RQ_RULE,
            stroke_width=1.0,
        )
        title_rule = VGroup(title_dot, underline).arrange(RIGHT, buff=0.16)
        title_rule.next_to(title, DOWN, buff=0.22)

        brain_img = self._make_evc_brain()
        brain_target = UP * 0.86
        brain_img.shift(brain_target - brain_img[0].get_center())
        focus_title = Tex(r"\textbf{Early visual cortex}", color=INK, font_size=20)
        focus_title.next_to(brain_img[0], DOWN, buff=0.18)
        focus_panel = Group(brain_img, focus_title)

        rq_cards = [
            self._make_rq_item(
                "01",
                "Representational format",
                "Sensory-like or memory-specific code?",
            ),
            self._make_rq_item(
                "02",
                "Naturalistic stimuli",
                "Does sensory recruitment extend beyond simple laboratory stimuli?",
            ),
            self._make_rq_item(
                "03",
                "Long-term memory",
                "Does long-term memory reshape working-memory representations?",
            ),
        ]
        rq_separators = [
            Line(
                ORIGIN,
                RIGHT * 4.90,
                stroke_color=_RQ_RULE,
                stroke_width=0.8,
            ).set_stroke(opacity=0.60)
            for _ in range(len(rq_cards) - 1)
        ]
        rq_stack = VGroup()
        for i, card in enumerate(rq_cards):
            rq_stack.add(card)
            if i < len(rq_cards) - 1:
                rq_stack.add(rq_separators[i])
        rq_stack.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        rq_stack.next_to(focus_panel, DOWN, buff=0.92)
        rq_stack.set_x(0.72)

        self.play(FadeIn(title, shift=UP * 0.05), run_time=0.70)
        self.play(FadeIn(title_dot, scale=0.6), Create(underline), run_time=0.35)
        self.play(FadeIn(focus_panel, shift=UP * 0.05), run_time=0.80)
        self.play(
            LaggedStart(
                *[
                    FadeIn(item, shift=RIGHT * 0.06)
                    if i % 2 == 0
                    else Create(item)
                    for i, item in enumerate(rq_stack)
                ],
                lag_ratio=0.18,
            ),
            run_time=1.25,
        )
        self.wait(4.00)


class Study2ExperimentalDesign(_Study2NumberedScene, Scene):
    """Present the Session 1 memory-task and Session 2 perceptual-task timelines side by side."""
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
        """Run the animation sequence for this scene."""
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
        self.wait(6.0)


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
_DIVERGING_MATRIX_VALUE_MIN = 0.16
_DIVERGING_MATRIX_VALUE_MAX = 0.84
_RESULTS_MATRIX_STROKE_COLOR = "#D8D1C7"
_RESULTS_MATRIX_DIVERGING_LOW_COLOR = "#6E8FB3"
_RESULTS_MATRIX_DIVERGING_MID_COLOR = "#F5F3EE"
_RESULTS_MATRIX_DIVERGING_HIGH_COLOR = "#C46A5A"
_CROSSSESSION_STIM_SCATTER_HEX = "#7B51A0"
_CROSSSESSION_DELAY_SCATTER_HEX = "#3C9553"
_CROSSSESSION_STIM_SCATTER = ManimColor(_CROSSSESSION_STIM_SCATTER_HEX)
_CROSSSESSION_DELAY_SCATTER = ManimColor(_CROSSSESSION_DELAY_SCATTER_HEX)

# ── Overview-only identity palette ───────────────────────────────────────────
_OVERVIEW_ID_COLOR_BY_IMAGE: dict[str, str] = {
    LAKE: "#4F78A8",
    PINE: "#2E8B94",
    OBS: "#4E8B62",
    CAT: "#C76A4E",
    VASE: "#8B6FB3",
    BRI: "#B45A7A",
    SOFA: "#2E8B94",
}


def _overview_identity_color(image_path: str) -> str:
    """Return the overview-scene accent color for one stimulus identity."""
    return _study2_lookup_color(
        image_path,
        _OVERVIEW_ID_COLOR_BY_IMAGE,
        "overview identity color",
    )

# ── Image identity palette ───────────────────────────────────────────────────
_ID_COLOR_BY_IMAGE: dict[str, str] = {
    LAKE: _D_BLUE,
    LAKE_D1: _D_BLUE,
    LAKE_D2: _D_BLUE,
    PINE: _D_AMBER,
    OBS: _D_GREEN,
    CAT: _D_RED,
    VASE: _D_PURP,
    BRI: _D_CYAN,
    SOFA: _D_AMBER,
}


def _identity_color(image_path: str) -> str:
    """Return the shared accent color for one stimulus identity."""
    return _study2_lookup_color(image_path, _ID_COLOR_BY_IMAGE, "identity color")


def _identity_colors(image_paths: list[str]) -> list[str]:
    """Return shared accent colors for a sequence of stimulus identities."""
    return [_identity_color(path) for path in image_paths]

# Brain icon used in the decoding overview
_BRAIN_PNG_PATH = _STUDY2_ASSET_DIR / "brain_icon_sagittal.png"
_OVERVIEW_BRAIN_PNG_PATH = REPO_ROOT / "assets" / "images" / "v1v2v3_multiplanar.png"
_MRI_SCANNER_PNG_PATH = _STUDY2_ASSET_DIR / "MRIscanner.png"
_V1V2V3_VIEWING_PNG_PATH = REPO_ROOT / "assets" / "images" / "v1v2v3_viewing.png"
_SVM_CLASSIFIER_SVG_PATH = REPO_ROOT / "assets" / "images" / "references" / "svm_classifier_schematic.svg"
_SVM_CLASSIFIER_GREYSCALE_SVG_PATH = REPO_ROOT / "assets" / "images" / "references" / "svm_classifier_schematic_greyscale.svg"
_OVERVIEW_BRAIN_ASSET_W = 1520.0
_OVERVIEW_BRAIN_CONTENT_LEFT = 13.0
_OVERVIEW_BRAIN_CONTENT_RIGHT = 1442.0
_OVERVIEW_BRAIN_CONTENT_W = _OVERVIEW_BRAIN_CONTENT_RIGHT - _OVERVIEW_BRAIN_CONTENT_LEFT
_OVERVIEW_BRAIN_CONTENT_CENTER_X = (
    _OVERVIEW_BRAIN_CONTENT_LEFT + _OVERVIEW_BRAIN_CONTENT_RIGHT
) / 2.0

# Current PNG asset is cropped tightly around the beam + brain composition.
_V1V2V3_VIEWING_ASSET_W = 422.0
_V1V2V3_VIEWING_ASSET_H = 285.0
_V1V2V3_VIEWING_BRAIN_LEFT = 94.0
_V1V2V3_VIEWING_BRAIN_W = 328.0
_V1V2V3_VIEWING_BRAIN_H = 285.0
_V1V2V3_VIEWING_BRAIN_CENTER_X = _V1V2V3_VIEWING_BRAIN_LEFT + _V1V2V3_VIEWING_BRAIN_W / 2.0
_V1V2V3_VIEWING_BRAIN_CENTER_Y = _V1V2V3_VIEWING_BRAIN_H / 2.0


def _make_v1v2v3_viewing_brain(
    *,
    brain_left_x: float,
    brain_center_y: float,
    target_brain_height: float,
) -> ImageMobject:
    """Return the positioned viewing-brain asset using its internal brain bounds."""
    viewing_brain = ImageMobject(str(_V1V2V3_VIEWING_PNG_PATH))
    viewing_brain.scale_to_fit_height(
        target_brain_height / (_V1V2V3_VIEWING_BRAIN_H / _V1V2V3_VIEWING_ASSET_H)
    )
    # The PNG is cropped around the full beam+brain composition, not around the
    # brain alone, so positioning must go through the measured brain sub-bounds.
    brain_center_offset = np.array([
        ((_V1V2V3_VIEWING_BRAIN_CENTER_X / _V1V2V3_VIEWING_ASSET_W) - 0.5) * viewing_brain.width,
        (0.5 - (_V1V2V3_VIEWING_BRAIN_CENTER_Y / _V1V2V3_VIEWING_ASSET_H)) * viewing_brain.height,
        0.0,
    ])
    brain_width = viewing_brain.width * (
        _V1V2V3_VIEWING_BRAIN_W / _V1V2V3_VIEWING_ASSET_W
    )
    brain_center_x = brain_left_x + brain_width / 2.0
    viewing_brain.move_to(
        np.array([brain_center_x, brain_center_y, 0.0]) - brain_center_offset
    )
    return viewing_brain


class Study2DecodingOverviewA(_Study2NumberedScene, Scene):
    """
    Opens on the full experimental-design layout, isolates the Session 2
    stimuli, and then maps each image to a coloured feature vector via a
    brain icon and activity-pattern matrix.

    Render:
        uv run manim scenes/study2.py Study2DecodingOverviewA -qh
    """

    # Three S2 stimulus colours (matching Stimulus 1/2/3 order)
    _COLS = [
        _overview_identity_color(LAKE),
        _overview_identity_color(PINE),
        _overview_identity_color(OBS),
    ]

    # Target column (left side, after transition)
    _COL_X  = -5.50
    _COL_YS = [1.20, 0.00, -1.20]
    _STACK_SCALE = 0.86

    # Brain / vector layout
    _BRAIN_Y = 0.00
    _H_GAP   = 1.15
    _TITLE_TOP_BUFF = 0.24
    _SCANNER_TO_BRAIN_BUFF = 0.18
    _SCANNER_WIDTH_SCALE = 1.02
    _SCANNER_LABEL_TEXT = "3T"
    _SCANNER_LABEL_FONT_SIZE = 18
    _SCANNER_LABEL_BUFF = 0.04
    _BRAIN_SOURCE_X_NORM = 0.64
    _BRAIN_SOURCE_Y_NORM = -0.47
    _BRAIN_SOURCE_FRAME_SCALE = 0.30
    _BRAIN_SOURCE_FRAME_COLOR = "#4F4339"
    _BRAIN_SOURCE_FRAME_STROKE_WIDTH = 2.4
    _BRAIN_SOURCE_LABEL_BUFF = 0.08

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
        (CAT, _overview_identity_color(CAT)),
        (VASE, _overview_identity_color(VASE)),
        (BRI, _overview_identity_color(BRI)),
    ]
    _RESTORE_TARGETS = [
        (OBS, _overview_identity_color(OBS)),
        (PINE, _overview_identity_color(PINE)),
        (LAKE, _overview_identity_color(LAKE)),
    ]
    _ICON_FRAME_STROKE_WIDTH = 2.4
    _ICON_FRAME_BUFF = 0.05
    _OVERVIEW_CAMERA_CENTER = np.array([0.0, 0.55, 0.0])

    def _set_overview_camera_frame(self) -> None:
        """Shift the overview scenes downward as one rigid block."""
        self.camera.frame_center = self._OVERVIEW_CAMERA_CENTER.copy()
        _study2_clear_camera_context_cache(self.camera)

    def _pattern_for_index(self, idx: int) -> np.ndarray:
        """Return the permuted activity pattern for one overview stimulus."""
        flat = self._GRID_PAT.flatten()
        return flat[self._GRID_PERMS[idx]].reshape(self._GRID_PAT.shape)

    def _make_grid(self, center: np.ndarray, col: str, pattern: np.ndarray) -> VGroup:
        """Build the grid."""
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
        """Build the feature vector."""
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
        """Build the grid frame."""
        return Rectangle(
            width=grid.width,
            height=grid.height,
            stroke_color=_D_MGREY,
            stroke_width=1.8,
        ).move_to(center)

    def _brain_source_point(
        self,
        brain: ImageMobject,
        x_norm: float | None = None,
        y_norm: float | None = None,
    ) -> np.ndarray:
        """Map normalized [-1, 1] image coordinates to scene coordinates."""
        if x_norm is None:
            x_norm = self._BRAIN_SOURCE_X_NORM
        if y_norm is None:
            y_norm = self._BRAIN_SOURCE_Y_NORM
        return (
            brain.get_center()
            + RIGHT * (0.5 * x_norm * brain.width)
            + UP * (0.5 * y_norm * brain.height)
        )

    def _vector_layout(self, vector_center_x: float, count: int) -> list[np.ndarray]:
        """Return the vector layout."""
        return _study2_vector_layout(self._COL_YS, vector_center_x, count)

    def _make_overview_title(self, tex: str) -> Tex:
        """Build the overview title anchored close to the top edge."""
        return Tex(tex, color=INK, font_size=TTL_SIZE).to_edge(
            UP, buff=self._TITLE_TOP_BUFF
        )

    def _make_brain_and_scanner(
        self,
        brain_height: float,
    ) -> tuple[ImageMobject, Group]:
        """Build the paired brain/scanner column for the overview scenes."""
        brain = (
            ImageMobject(str(_OVERVIEW_BRAIN_PNG_PATH))
            .scale_to_fit_height(brain_height)
            .move_to(UP * self._BRAIN_Y)
        )
        brain.set_z_index(-20)

        scanner_img = ImageMobject(str(_MRI_SCANNER_PNG_PATH))
        scanner_img.scale_to_fit_width(brain.width * self._SCANNER_WIDTH_SCALE)
        scanner_img.set_z_index(-21)
        scanner_label = Tex(
            self._SCANNER_LABEL_TEXT,
            color=INK,
            font_size=self._SCANNER_LABEL_FONT_SIZE,
        ).next_to(scanner_img, UP, buff=self._SCANNER_LABEL_BUFF)
        scanner_label.set_z_index(-19)
        scanner = Group(scanner_img, scanner_label)
        return brain, scanner

    def _overview_brain_content_width(self, brain: ImageMobject) -> float:
        """Return the width of the visible MRI montage within the brain asset."""
        return brain.width * (_OVERVIEW_BRAIN_CONTENT_W / _OVERVIEW_BRAIN_ASSET_W)

    def _overview_brain_content_center_offset_x(self, brain: ImageMobject) -> float:
        """Return the visible MRI montage centre offset from the asset centre."""
        return brain.width * (
            (_OVERVIEW_BRAIN_CONTENT_CENTER_X / _OVERVIEW_BRAIN_ASSET_W) - 0.5
        )

    def _overview_column_center_x(self, stack_right: float, brain: ImageMobject) -> float:
        """Return the shared x-axis for the scanner, MRI montage, and matrix."""
        return stack_right + self._H_GAP + self._overview_brain_content_width(brain) / 2.0

    def _overview_matrix_center(
        self,
        brain: ImageMobject,
        column_center_x: float,
    ) -> np.ndarray:
        """Return the matrix centre aligned to the MRI column centre."""
        return np.array([column_center_x, brain.get_bottom()[1] - 0.58, 0.0])

    def _make_brain_source_frame(
        self,
        matrix_template: VGroup,
        brain: ImageMobject,
    ) -> tuple[Rectangle, Tex]:
        """Build the V1-V3 ROI marker and label for the overview brain asset."""
        source_frame = self._make_grid_frame(
            matrix_template,
            self._brain_source_point(brain),
        ).scale(self._BRAIN_SOURCE_FRAME_SCALE)
        source_frame.set_stroke(
            color=self._BRAIN_SOURCE_FRAME_COLOR,
            width=self._BRAIN_SOURCE_FRAME_STROKE_WIDTH,
        )
        source_label = Tex(
            "V1-V3",
            color=INK,
            font_size=20,
        ).next_to(source_frame, RIGHT, buff=self._BRAIN_SOURCE_LABEL_BUFF)
        return source_frame, source_label

    def _position_brain_and_scanner(
        self,
        brain: ImageMobject,
        scanner: Group,
        column_center_x: float,
    ) -> None:
        """Position the scanner directly above the brain icon."""
        scanner_img, scanner_label = scanner
        brain.move_to(np.array([
            column_center_x - self._overview_brain_content_center_offset_x(brain),
            self._BRAIN_Y,
            0.0,
        ]))
        scanner_img.next_to(brain, UP, buff=self._SCANNER_TO_BRAIN_BUFF)
        scanner_img.move_to(np.array([column_center_x, scanner_img.get_center()[1], 0.0]))
        scanner_label.next_to(scanner_img, UP, buff=self._SCANNER_LABEL_BUFF)

    def _make_stack_target(
        self,
        img_path: str,
        col: str,
        *,
        image_height: float = IMG_H * _STACK_SCALE,
        fixation_height: float = FIX_H * _STACK_SCALE,
    ) -> tuple[Group, SurroundingRectangle]:
        """Build the stack target."""
        img = ImageMobject(img_path).scale_to_fit_height(image_height)
        fix = ImageMobject(FIX).scale_to_fit_height(fixation_height).move_to(img.get_center())
        icon = Group(img, fix)
        frame = SurroundingRectangle(
            icon,
            color=col,
            stroke_width=self._ICON_FRAME_STROKE_WIDTH,
            buff=self._ICON_FRAME_BUFF,
            corner_radius=0.10,
        )
        return icon, frame

    def _make_delay_card(
        self,
        col: str,
    ) -> tuple[Group, SurroundingRectangle]:
        """Build the delay card."""
        card = _box(None)
        card.scale(self._STACK_SCALE)
        card[0].set_stroke(color=GREY, width=1.5, opacity=0.85)
        card[0].set_fill(WHITE, opacity=1.0)
        frame = SurroundingRectangle(
            card,
            color=col,
            stroke_width=self._ICON_FRAME_STROKE_WIDTH,
            buff=self._ICON_FRAME_BUFF,
            corner_radius=0.10,
        )
        return card, frame

    def _build_overview_end_state(self) -> dict[str, object]:
        """Build the overview end state."""
        slide_title = self._make_overview_title(
            r"\textbf{Session 2 :} Perceptual task"
        )

        visible_icons: list[Group] = []
        visible_frames: list[VMobject] = []
        for row_y, (img_path, col) in zip(self._COL_YS, self._ROLLING_TARGETS):
            icon, frame = self._make_stack_target(img_path, col)
            pos = np.array([self._COL_X, row_y, 0.0])
            icon.move_to(pos)
            frame.move_to(icon.get_center())
            visible_icons.append(icon)
            visible_frames.append(frame)

        row_step = self._COL_YS[0] - self._COL_YS[1]
        ghost_y = self._COL_YS[0] + row_step * 1.02
        ghost_icon, ghost_frame = self._make_stack_target(*self._RESTORE_TARGETS[0])
        ghost_icon.move_to(np.array([self._COL_X, ghost_y, 0.0]))
        ghost_frame.move_to(ghost_icon.get_center())
        ghost_icon.set_opacity(0.18)
        ghost_frame.set_stroke(opacity=0.18)

        icon_h = max(icon.height for icon in visible_icons)
        brain, scanner = self._make_brain_and_scanner(2.0 * icon_h)

        vector_template = self._make_feature_vector(
            ORIGIN, self._COLS[0], self._pattern_for_index(0)
        )
        stack_right = max(frame.get_right()[0] for frame in visible_frames)
        brain_x = self._overview_column_center_x(stack_right, brain)
        vector_left_x = brain_x + self._overview_brain_content_width(brain) / 2 + self._H_GAP
        vector_center_x = vector_left_x + vector_template.width / 2
        self._position_brain_and_scanner(brain, scanner, brain_x)

        matrix_center = self._overview_matrix_center(brain, brain_x)
        matrix_template = self._make_grid(
            matrix_center,
            self._COLS[0],
            self._pattern_for_index(0),
        )
        current_grid = self._make_grid(
            matrix_center,
            self._ROLLING_TARGETS[-1][1],
            self._pattern_for_index(len(self._ROLLING_TARGETS) + 2),
        )
        source_frame, source_label = self._make_brain_source_frame(matrix_template, brain)
        source_frame.set_z_index(2)
        source_label.set_z_index(2)

        vector_centers = self._vector_layout(
            vector_center_x,
            len(self._COLS) + len(self._ROLLING_TARGETS),
        )
        vector_colors = self._COLS + [col for _, col in self._ROLLING_TARGETS]
        visible_vectors = [
            self._make_feature_vector(center, color, self._pattern_for_index(idx))
            for idx, (center, color) in enumerate(zip(vector_centers, vector_colors))
        ]
        vector_label = Tex(
            "Feature vectors",
            color=INK,
            font_size=24,
        ).move_to(np.array([vector_center_x, self._COL_YS[0] + 0.52, 0.0]))

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
            np.array([
                summary_group.get_center()[0] + 0.38,
                summary_matrix.get_center()[1] + 1.45,
                0.0,
            ])
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

        stack_group = Group(
            *visible_icons,
            *visible_frames,
            ghost_icon,
            ghost_frame,
        )
        vector_group = VGroup(*visible_vectors)
        support_group = Group(
            current_grid,
            source_frame,
            source_label,
            vector_label,
            vector_group,
            summary_title,
            summary_group,
            sample_arrow,
            sample_label,
            feature_arrow,
            feature_label,
        )
        frame = Group(
            slide_title,
            stack_group,
            scanner,
            brain,
            support_group,
        )
        return {
            "frame": frame,
            "slide_title": slide_title,
            "stack_group": stack_group,
            "visible_icons": visible_icons,
            "visible_frames": visible_frames,
            "ghost_icon": ghost_icon,
            "ghost_frame": ghost_frame,
            "scanner": scanner,
            "brain": brain,
            "support_group": support_group,
            "current_grid": current_grid,
            "source_frame": source_frame,
            "source_label": source_label,
            "vector_group": vector_group,
            "vector_label": vector_label,
            "summary_title": summary_title,
            "summary_group": summary_group,
            "sample_arrow": sample_arrow,
            "sample_label": sample_label,
            "feature_arrow": feature_arrow,
            "feature_label": feature_label,
            "icon_center_x": self._COL_X,
            "row_step": row_step,
            "ghost_y": ghost_y,
            "bottom_exit_y": self._COL_YS[-1] - row_step,
        }

    # ── Scene ─────────────────────────────────────────────────────────────────

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        self._set_overview_camera_frame()

        # ── Phase 0: Start from the full experimental-design end state ─────────
        s1_title = Tex(
            r"\textbf{Session 1 :} Memory task",
            color=INK, font_size=TTL_SIZE,
        ).to_edge(UP, buff=self._TITLE_TOP_BUFF)

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
        slide_title = self._make_overview_title(
            r"\textbf{Session 2 :} Perceptual task"
        )

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
        stacked_targets = []
        for stim_box, stim_spec, col in zip(stim_boxes, _S2[::2], self._COLS):
            icon, frame = self._make_stack_target(
                stim_spec["img"],
                col,
                image_height=stim_box[1].height,
                fixation_height=stim_box[2].height,
            )
            icon.move_to(stim_box.get_center())
            frame.move_to(icon.get_center())
            stacked_targets.append((icon, frame))
        stim_icons = [icon for icon, _ in stacked_targets]
        stacked_highlights = VGroup(*[frame for _, frame in stacked_targets])
        self.play(
            *[
                rect.animate.set_stroke(opacity=0).set_fill(opacity=0)
                for rect in stim_rects
            ],
            *[
                ReplacementTransform(Group(box[1], box[2]), icon)
                for box, icon in zip(stim_boxes, stim_icons)
            ],
            *[
                Transform(highlight, stacked_highlight)
                for highlight, stacked_highlight in zip(highlights, stacked_highlights)
            ],
            run_time=0.45,
        )
        self.remove(*stim_boxes)
        self.wait(0.3)

        # ── Phase 3: Brain icon is twice the stimulus-icon height ──────────────
        icon_h = max(icon.height for icon in stim_icons)
        brain, scanner = self._make_brain_and_scanner(2.0 * icon_h)
        vector_template = self._make_feature_vector(
            ORIGIN, self._COLS[0], self._pattern_for_index(0)
        )
        stack_right = max(highlight.get_right()[0] for highlight in highlights)
        brain_x = self._overview_column_center_x(stack_right, brain)
        vector_left_x = brain_x + self._overview_brain_content_width(brain) / 2 + self._H_GAP
        vector_center_x = vector_left_x + vector_template.width / 2
        self._position_brain_and_scanner(brain, scanner, brain_x)
        self.play(
            FadeIn(brain, shift=RIGHT * 0.15),
            FadeIn(scanner, shift=RIGHT * 0.15 + UP * 0.08),
            run_time=0.75,
        )
        self.bring_to_back(scanner, brain)
        self.wait(0.25)

        # ── Phase 4: Each image maps to a feature vector ───────────────────────
        matrix_center = self._overview_matrix_center(brain, brain_x)
        vector_centers = [
            np.array([vector_center_x, row_y, 0.0]) for row_y in self._COL_YS
        ]
        visible_vectors: list[VGroup] = []
        matrix_template = self._make_grid(matrix_center, self._COLS[0], self._pattern_for_index(0))
        matrix_frame = self._make_grid_frame(matrix_template, matrix_center)
        source_frame, source_label = self._make_brain_source_frame(matrix_template, brain)
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

        vector_label = Tex("Feature vectors", color=INK, font_size=24).move_to(
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
                    source_frame.animate(rate_func=_study2_synced_source_pulse).set_stroke(
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
            """Build the stack target."""
            img = ImageMobject(img_path).scale_to_fit_height(icon_img_h)
            fix = ImageMobject(FIX).scale_to_fit_height(icon_fix_h).move_to(img.get_center())
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

            future_vector_centers = self._vector_layout(
                vector_center_x,
                len(visible_vectors) + 1,
            )
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
                source_frame.animate(rate_func=_study2_synced_source_pulse).set_stroke(
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
# Study2DecodingOverviewB
# ══════════════════════════════════════════════════════════════════════════════


class Study2DecodingOverviewB(Study2DecodingOverviewA):
    """
    Start from the final DecodingOverview frame, restore the original
    perceptual images, and lay out matched delay cards to motivate the
    cross-decoding interpretation.

    Render:
        uv run manim scenes/study2.py Study2DecodingOverviewB -ql
        uv run manim scenes/study2.py Study2DecodingOverviewB -qh
    """

    _OVERVIEW_B_TITLE = r"\textbf{Session 1 :} Memory task"
    _MEMORY_STIM_OPACITY = 0.62
    _PAIR_GAP = 0.20

    def _reverse_roll_step(
        self,
        visible_icons: list[Group],
        visible_frames: list[VMobject],
        incoming_icon: Group,
        incoming_frame: VMobject,
        *,
        icon_center_x: float,
        ghost_y: float,
        bottom_exit_y: float,
        fade_group: Mobject | None = None,
        title_pair: tuple[Mobject, Mobject] | None = None,
        exit_ghost_pair: tuple[Mobject, Mobject] | None = None,
    ) -> tuple[list[Group], list[VMobject], tuple[Mobject, Mobject]]:
        """Return the data for one reverse roll step in the overview carousel."""
        incoming_icon.move_to(np.array([icon_center_x, ghost_y, 0.0]))
        incoming_frame.move_to(incoming_icon.get_center())
        incoming_icon.set_opacity(0.18)
        incoming_frame.set_stroke(opacity=0.18)
        self.add(incoming_icon, incoming_frame)

        roll_anims = []
        if fade_group is not None:
            roll_anims.append(FadeOut(fade_group))
        if title_pair is not None:
            roll_anims.append(Transform(*title_pair))
        if exit_ghost_pair is not None:
            roll_anims.extend([FadeOut(exit_ghost_pair[0]), FadeOut(exit_ghost_pair[1])])

        top_pos = np.array([icon_center_x, self._COL_YS[0], 0.0])
        mid_pos = np.array([icon_center_x, self._COL_YS[1], 0.0])
        bottom_pos = np.array([icon_center_x, self._COL_YS[2], 0.0])
        exit_pos = np.array([icon_center_x, bottom_exit_y, 0.0])

        roll_anims.extend([
            incoming_icon.animate.move_to(top_pos).set_opacity(1.0),
            incoming_frame.animate.move_to(top_pos).set_stroke(opacity=1.0),
            visible_icons[0].animate.move_to(mid_pos),
            visible_frames[0].animate.move_to(mid_pos),
            visible_icons[1].animate.move_to(bottom_pos),
            visible_frames[1].animate.move_to(bottom_pos),
            visible_icons[2].animate.move_to(exit_pos).set_opacity(0.18),
            visible_frames[2].animate.move_to(exit_pos).set_stroke(opacity=0.18),
        ])

        self.play(*roll_anims, run_time=0.62)

        new_visible_icons = [incoming_icon, visible_icons[0], visible_icons[1]]
        new_visible_frames = [incoming_frame, visible_frames[0], visible_frames[1]]
        new_exit_ghost = (visible_icons[2], visible_frames[2])
        return new_visible_icons, new_visible_frames, new_exit_ghost

    def _make_memory_pair_target(
        self, img_path: str, col: str
    ) -> tuple[Group, Group, SurroundingRectangle, Group, SurroundingRectangle]:
        """Build one memory-decoding row with grey stimulus frame and colored delay frame."""
        stim_icon, stim_frame = self._make_stack_target(img_path, col)
        stim_icon[0].set_opacity(self._MEMORY_STIM_OPACITY)
        stim_frame.set_stroke(color=GREY, opacity=0.9)
        delay_card, delay_frame = self._make_delay_card(col)
        pair = Group(stim_icon, stim_frame, delay_card, delay_frame)
        stim_icon.move_to(ORIGIN)
        stim_frame.move_to(stim_icon.get_center())
        delay_card.move_to(
            stim_icon.get_center()
            + RIGHT * (stim_frame.width / 2 + self._PAIR_GAP + delay_frame.width / 2)
        )
        delay_frame.move_to(delay_card.get_center())
        pair.move_to(ORIGIN)
        return pair, stim_icon, stim_frame, delay_card, delay_frame

    def _anchor_memory_pair_to_stimulus(
        self,
        pair: Group,
        stim_icon: Group,
        target_center: np.ndarray,
    ) -> None:
        """Place a memory-decoding row so the stimulus card stays on the legacy column anchor."""
        pair.shift(target_center - stim_icon.get_center())

    def _memory_pattern_for_index(self, idx: int) -> np.ndarray:
        """Return a memory-scene voxel pattern with a different composition from Overview A."""
        base = self._pattern_for_index(idx % len(self._GRID_PERMS))
        alt = self._pattern_for_index((idx + 2) % len(self._GRID_PERMS))
        mixed = 0.58 * base + 0.42 * np.rot90(alt, k=(idx % 3) + 1)
        if idx % 2 == 0:
            mixed = np.roll(mixed, shift=1, axis=1)
        else:
            mixed = np.roll(mixed, shift=1, axis=0)
        return np.clip(mixed, 0.08, 0.98)

    def _build_overview_b_end_state(self) -> dict[str, Mobject]:
        """Build the held final state of DecodingOverviewB."""
        slide_title = self._make_overview_title(self._OVERVIEW_B_TITLE)

        memory_targets = []
        memory_stim_icons = []
        for img_path, row_y, col in zip(
            [spec["img"] for spec in Study2ExperimentalDesign._S2[::2]],
            self._COL_YS,
            self._COLS,
        ):
            target_pair, stim_icon, _, _, _ = self._make_memory_pair_target(img_path, col)
            self._anchor_memory_pair_to_stimulus(
                target_pair,
                stim_icon,
                np.array([self._COL_X, row_y, 0.0]),
            )
            memory_targets.append(target_pair)
            memory_stim_icons.append(stim_icon)

        icon_h = max(icon.height for icon in memory_stim_icons)
        brain, scanner = self._make_brain_and_scanner(2.0 * icon_h)
        stack_right = max(pair.get_right()[0] for pair in memory_targets)
        brain_x = self._overview_column_center_x(stack_right, brain)
        self._position_brain_and_scanner(brain, scanner, brain_x)

        vector_template = self._make_feature_vector(
            ORIGIN, self._COLS[0], self._memory_pattern_for_index(0)
        )
        vector_left_x = brain_x + self._overview_brain_content_width(brain) / 2 + self._H_GAP
        vector_center_x = vector_left_x + vector_template.width / 2

        matrix_center = self._overview_matrix_center(brain, brain_x)
        matrix_template = self._make_grid(
            matrix_center,
            self._COLS[0],
            self._memory_pattern_for_index(0),
        )
        source_frame, source_label = self._make_brain_source_frame(matrix_template, brain)
        source_frame.set_z_index(2)
        source_label.set_z_index(2)
        current_grid = self._make_grid(
            matrix_center,
            self._COLS[-1],
            self._memory_pattern_for_index(len(self._COLS) - 1),
        )

        vector_centers = [
            np.array([vector_center_x, row_y, 0.0]) for row_y in self._COL_YS
        ]
        visible_vectors = VGroup(*[
            self._make_feature_vector(center, col, self._memory_pattern_for_index(idx))
            for idx, (center, col) in enumerate(zip(vector_centers, self._COLS))
        ])
        vector_label = Tex("Feature vectors", color=INK, font_size=24).move_to(
            np.array([vector_center_x, self._COL_YS[0] + 0.52, 0.0])
        )

        summary_symbol = MathTex(
            r"\mathbf{X}_{\mathrm{D1}} =",
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
        summary_title = Tex(
            r"Multivoxel activity patterns\\during memory",
            color=INK,
            font_size=24,
            tex_environment="center",
        ).next_to(summary_group, UP, buff=0.22)
        sample_arrow = DoubleArrow(
            summary_matrix.get_corner(UR) + RIGHT * 0.42 + UP * 0.02,
            summary_matrix.get_corner(DR) + RIGHT * 0.42 + DOWN * 0.02,
            color=INK,
            stroke_width=1.8,
            buff=0.0,
            tip_length=0.12,
        )
        sample_label = MathTex(
            r"\text{samples (delay periods)}",
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
        summary_block = VGroup(
            summary_title,
            summary_group,
            sample_arrow,
            sample_label,
            feature_arrow,
            feature_label,
        )
        right_vectors_edge = max(vector.get_right()[0] for vector in visible_vectors)
        block_left = right_vectors_edge + 0.35
        block_right = config.frame_width / 2 - 0.35
        available_width = max(1.0, block_right - block_left)
        if summary_block.width > available_width:
            summary_block.scale_to_fit_width(available_width)
        summary_block.move_to(np.array([(block_left + block_right) / 2, -0.02, 0.0]))
        top_limit = slide_title.get_bottom()[1] - 0.18
        if summary_block.get_top()[1] > top_limit:
            summary_block.shift(DOWN * (summary_block.get_top()[1] - top_limit))
        bottom_limit = -config.frame_height / 2 + 0.32
        if summary_block.get_bottom()[1] < bottom_limit:
            summary_block.shift(UP * (bottom_limit - summary_block.get_bottom()[1]))

        frame = Group(
            slide_title,
            *memory_targets,
            brain,
            scanner,
            source_frame,
            source_label,
            current_grid,
            visible_vectors,
            vector_label,
            summary_block,
        )
        return {
            "frame": frame,
            "title": slide_title,
            "memory_targets": Group(*memory_targets),
            "brain": brain,
            "scanner": scanner,
            "source_frame": source_frame,
            "source_label": source_label,
            "current_grid": current_grid,
            "visible_vectors": visible_vectors,
            "vector_label": vector_label,
            "summary_block": summary_block,
        }

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        self._set_overview_camera_frame()
        ctx = self._build_overview_end_state()
        self.add(ctx["frame"])
        self.wait(0.25)

        s1_title = self._make_overview_title(r"\textbf{Session 1 :} Memory task")
        boxes1, xs1 = _build_row(Study2ExperimentalDesign._S1, S1_Y)
        dots1, x_end1 = _ellipsis(xs1, S1_Y)
        arrow1, t1 = _timeline(xs1, S1_Y, x_end1)
        time_lbl1, ph_lb1 = _labels(Study2ExperimentalDesign._S1, xs1, S1_Y)

        s2_title = Tex(
            r"\textbf{Session 2 :} Perceptual task",
            color=INK, font_size=TTL_SIZE,
        ).move_to(UP * (S2_Y + BOX_H / 2 + 0.74))
        boxes2, xs2 = _build_row(Study2ExperimentalDesign._S2, S2_Y)
        dots2, x_end2 = _ellipsis(xs2, S2_Y)
        arrow2, t2 = _timeline(xs2, S2_Y, x_end2)
        time_lbl2, ph_lb2 = _labels(Study2ExperimentalDesign._S2, xs2, S2_Y)
        n_lbl = Tex(r"$N = 42$ participants", color=INK, font_size=18).to_edge(DOWN, buff=0.38)

        design_group = Group(
            s1_title, Group(*boxes1), dots1, arrow1, t1, time_lbl1, ph_lb1,
            s2_title, Group(*boxes2), dots2, arrow2, t2, time_lbl2, ph_lb2,
            n_lbl,
        )

        self.play(
            FadeOut(ctx["frame"]),
            FadeIn(design_group),
            run_time=0.7,
        )
        # The master Study 2 render can accumulate hidden duplicate image
        # mobjects across section replays during this cross-fade. Rebinding the
        # scene to the freshly rebuilt design layout keeps later frames clean.
        self.clear()
        self.camera.background_color = BG
        self._set_overview_camera_frame()
        self.add(design_group)
        self.wait(0.2)

        s1_delay_highlight = SurroundingRectangle(
            boxes1[1], color=_D_GREEN, stroke_width=3.0, buff=0.06, corner_radius=0.12,
        )
        self.play(
            Create(s1_delay_highlight),
            run_time=0.35,
        )
        self.wait(0.5)

        self.play(
            FadeOut(Group(
                *[box for idx, box in enumerate(boxes1) if idx != 1],
                dots1, arrow1, t1, time_lbl1, ph_lb1,
            )),
            FadeOut(s2_title),
            FadeOut(Group(*boxes2)),
            FadeOut(dots2), FadeOut(arrow2), FadeOut(t2),
            FadeOut(time_lbl2), FadeOut(ph_lb2),
            FadeOut(n_lbl),
            run_time=0.55,
        )

        stim_boxes = [boxes2[0], boxes2[2], boxes2[4]]
        slide_title = self._make_overview_title(self._OVERVIEW_B_TITLE)

        memory_targets = []
        memory_stim_icons = []
        memory_stim_frames = []
        memory_delay_cards = []
        memory_delay_frames = []
        for img_path, row_y, col in zip(
            [spec["img"] for spec in Study2ExperimentalDesign._S2[::2]],
            self._COL_YS,
            self._COLS,
        ):
            target_pair, stim_icon, stim_frame, delay_card, delay_frame = self._make_memory_pair_target(img_path, col)
            self._anchor_memory_pair_to_stimulus(
                target_pair,
                stim_icon,
                np.array([self._COL_X, row_y, 0.0]),
            )
            memory_targets.append(target_pair)
            memory_stim_icons.append(stim_icon)
            memory_stim_frames.append(stim_frame)
            memory_delay_cards.append(delay_card)
            memory_delay_frames.append(delay_frame)

        delay_source_box = boxes1[1]

        self.play(
            *[FadeIn(stim_icon, shift=LEFT * 0.08) for stim_icon in memory_stim_icons],
            *[FadeIn(stim_frame, shift=LEFT * 0.08) for stim_frame in memory_stim_frames],
            *[
                TransformFromCopy(delay_source_box, delay_card)
                for delay_card in memory_delay_cards
            ],
            *[
                TransformFromCopy(s1_delay_highlight, delay_frame)
                for delay_frame in memory_delay_frames
            ],
            FadeOut(delay_source_box),
            FadeOut(s1_delay_highlight),
            Transform(s1_title, slide_title),
            run_time=0.95,
        )
        self.add(*memory_targets)
        self.wait(0.25)

        icon_h = max(icon.height for icon in memory_stim_icons)
        brain, scanner = self._make_brain_and_scanner(2.0 * icon_h)
        stack_right = max(pair.get_right()[0] for pair in memory_targets)
        brain_x = self._overview_column_center_x(stack_right, brain)
        self._position_brain_and_scanner(brain, scanner, brain_x)
        self.play(
            FadeIn(brain, shift=RIGHT * 0.15),
            FadeIn(scanner, shift=RIGHT * 0.15 + UP * 0.08),
            run_time=0.75,
        )
        self.bring_to_back(scanner, brain)
        self.wait(0.25)

        vector_template = self._make_feature_vector(
            ORIGIN, self._COLS[0], self._memory_pattern_for_index(0)
        )
        vector_left_x = brain_x + self._overview_brain_content_width(brain) / 2 + self._H_GAP
        vector_center_x = vector_left_x + vector_template.width / 2
        matrix_center = self._overview_matrix_center(brain, brain_x)
        matrix_template = self._make_grid(
            matrix_center,
            self._COLS[0],
            self._memory_pattern_for_index(0),
        )
        matrix_frame = self._make_grid_frame(matrix_template, matrix_center)
        source_frame, source_label = self._make_brain_source_frame(matrix_template, brain)
        source_frame.set_z_index(2)
        source_label.set_z_index(2)
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
        source_frame_base_width = source_frame.get_stroke_width()
        source_frame_pulse_width = source_frame_base_width * 1.8
        current_grid: VGroup | None = None
        vector_centers = self._vector_layout(vector_center_x, len(memory_targets))
        visible_vectors: list[VGroup] = []
        vector_label = Tex(
            "Feature vectors",
            color=INK,
            font_size=24,
        ).move_to(np.array([vector_center_x, self._COL_YS[0] + 0.52, 0.0]))

        for idx, (pair, col, vec_center) in enumerate(zip(memory_targets, self._COLS, vector_centers)):
            pattern = self._memory_pattern_for_index(idx)
            arr_to_brain = Arrow(
                pair.get_right() + RIGHT * 0.12,
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
                    source_frame.animate(rate_func=_study2_synced_source_pulse).set_stroke(
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
                self.play(
                    FadeIn(vector_label),
                    ReplacementTransform(grid_copy, vector),
                    run_time=0.70,
                )
            else:
                self.play(ReplacementTransform(grid_copy, vector), run_time=0.70)
            self.play(FadeOut(arr_to_brain), FadeOut(arr_to_vec), run_time=0.20)
            visible_vectors.append(vector)

        summary_symbol = MathTex(
            r"\mathbf{X}_{\mathrm{D1}} =",
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
        summary_title = Tex(
            r"Multivoxel activity patterns\\during memory",
            color=INK,
            font_size=24,
            tex_environment="center",
        ).next_to(summary_group, UP, buff=0.22)
        sample_arrow = DoubleArrow(
            summary_matrix.get_corner(UR) + RIGHT * 0.42 + UP * 0.02,
            summary_matrix.get_corner(DR) + RIGHT * 0.42 + DOWN * 0.02,
            color=INK,
            stroke_width=1.8,
            buff=0.0,
            tip_length=0.12,
        )
        sample_label = MathTex(
            r"\text{samples (delay periods)}",
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
        summary_block = VGroup(
            summary_title,
            summary_group,
            sample_arrow,
            sample_label,
            feature_arrow,
            feature_label,
        )
        right_vectors_edge = max(vector.get_right()[0] for vector in visible_vectors)
        block_left = right_vectors_edge + 0.35
        block_right = config.frame_width / 2 - 0.35
        available_width = max(1.0, block_right - block_left)
        if summary_block.width > available_width:
            summary_block.scale_to_fit_width(available_width)
        summary_block.move_to(np.array([(block_left + block_right) / 2, -0.02, 0.0]))
        top_limit = slide_title.get_bottom()[1] - 0.18
        if summary_block.get_top()[1] > top_limit:
            summary_block.shift(DOWN * (summary_block.get_top()[1] - top_limit))
        bottom_limit = -config.frame_height / 2 + 0.32
        if summary_block.get_bottom()[1] < bottom_limit:
            summary_block.shift(UP * (bottom_limit - summary_block.get_bottom()[1]))

        self.play(
            FadeIn(summary_title),
            FadeIn(summary_symbol),
            Write(summary_matrix),
            FadeIn(sample_arrow),
            FadeIn(sample_label),
            FadeIn(feature_arrow),
            FadeIn(feature_label),
            Indicate(VGroup(*visible_vectors), color=_D_MGREY, scale_factor=1.02),
            run_time=0.65,
        )

        self.wait(1.0)


class Study2DecodingOverviewC(Study2DecodingOverviewB):
    """
    Open on the final held frame of DecodingOverviewB, then introduce the
    decoding-schema rationale for shared representational format.

    Render:
        uv run manim scenes/study2.py Study2DecodingOverviewC -ql
        uv run manim scenes/study2.py Study2DecodingOverviewC -qh
    """

    _OVERVIEW_B_TITLE = r"\textbf{Cross-decoding of sensory and mnemonic representations}"
    _SCHEMA_OVERVIEW_CASES = [
        ("train", "sensory", "none"),
        ("predict", "memory", "question"),
    ]
    _SCHEMA_SUMMARY_CASES = [
        ("train", "sensory", "none"),
        ("predict", "sensory", "cat"),
        ("predict", "memory", "question"),
    ]
    _INTUITION_LEFT_COLOR = "#7F8898"
    _INTUITION_RIGHT_COLOR = "#9C7A2B"
    _SCHEMA_TRAIN_COLOR = "#8B95A5"
    _SCHEMA_TEST_COLOR = "#9C7A2B"
    _SCHEMA_ITEM_HEIGHT = IMG_H * Study2DecodingOverviewA._STACK_SCALE * 1.10
    _SCHEMA_ARROW_LABEL_BUFF = 0.18
    _SCHEMA_PROJECTION_COLOR = "#B4BAC4"
    _SCHEMA_MEMORY_GHOST_OFFSET = 0.42
    _SCHEMA_MEMORY_GHOST_IMAGE_OPACITY = 0.28
    _SCHEMA_MEMORY_GHOST_CARD_OPACITY = 0.44
    _SCHEMA_HORIZONTAL_GAP = 0.14
    _SCHEMA_PROJECTION_OPENING_DEG = 60
    _SCHEMA_PROJECTION_END_INSET = 0.05
    _SCHEMA_PATTERN_BOX_TO_DECODER_RATIO = 0.86
    _SCHEMA_DECODER_HEIGHT_RATIO = 0.98
    _SCHEMA_PATTERN_REFERENCE_HEIGHT_RATIO = 1.16
    _SCHEMA_LINK_ARROW_LENGTH = 0.74
    _SCHEMA_LINK_SPAN = 2 * _SCHEMA_HORIZONTAL_GAP + _SCHEMA_LINK_ARROW_LENGTH
    _SCHEMA_COLUMN_GAP = 1.5
    _SCHEMA_ROW_SCALE = 1.14
    _SCHEMA_TRAIN_TO_PREDICT_GAP = 0.78
    _SCHEMA_PREDICT_TO_PREDICT_GAP = 0.48
    _SCHEMA_ROW_REVEAL_TIME = 0.95
    _SCHEMA_COMPONENT_REVEAL_TIME = 0.34
    _SCHEMA_CLASSIFIER_TRANSFER_TIME = 1.05
    _SCHEMA_OUTPUT_REVEAL_TIME = 0.55
    _SCHEMA_FORK_REVEAL_TIME = 0.95
    _SCHEMA_CLASSIFIER_PATH_ARC = -PI / 3
    _SCHEMA_INTRO_PANEL_PAUSE = 5.0
    _SCHEMA_TRAIN_EXPLAIN_PAUSE = 3.0
    _SCHEMA_INPUT_EXPLAIN_PAUSE = 1.4
    _SCHEMA_CLASSIFIER_EXPLAIN_PAUSE = 1.7
    _SCHEMA_OUTPUT_EXPLAIN_PAUSE = 1.6
    _SCHEMA_FORK_EXPLAIN_PAUSE = 2.6
    _SCHEMA_FORK_HORIZONTAL_GAP = 0.86
    _SCHEMA_FORK_VERTICAL_GAP = 0.34
    _SCHEMA_FORK_ARROW_GAP = 0.10
    _SCHEMA_ROW_BRACE_BUFF = 0.20
    _SCHEMA_ROW_BRACE_HEIGHT_SCALE = 1.04
    _SCHEMA_ROW_BRACE_STROKE = 1.3
    _SCHEMA_ROW_BRACE_OPACITY = 0.72
    _SCHEMA_ROW_LABEL_BUFF = 0.12
    _SCHEMA_ROW_LABEL_FONT_SIZE = 20

    def _schema_row_label_text(self, mode: str) -> str:
        """Return the row-level role label shown next to the left brace."""
        if mode == "train":
            return r"\textbf{Train}"
        if mode == "predict":
            return r"\textbf{Test}"
        raise ValueError(f"Unknown schema mode: {mode}")

    def _schema_row_label_color(self, mode: str) -> str:
        """Return the color used for the row-level brace annotation."""
        if mode == "train":
            return self._SCHEMA_TRAIN_COLOR
        if mode == "predict":
            return self._SCHEMA_TEST_COLOR
        raise ValueError(f"Unknown schema mode: {mode}")

    def _make_schema_decoder(self, center: np.ndarray, height: float) -> SVGMobject:
        """Build the classifier schematic used in the schema rows."""
        return (
            SVGMobject(str(_SVM_CLASSIFIER_SVG_PATH))
            .scale_to_fit_height(height)
            .move_to(center)
        )

    def _schema_pattern(self, variant: str) -> np.ndarray:
        """Return the sensory or memory voxel grid used by the schema."""
        if variant == "sensory":
            return self._pattern_for_index(3)
        return self._memory_pattern_for_index(3)

    def _schema_color(self, variant: str) -> str:
        """Return the condition color used by the schema."""
        return _D_PURP if variant == "sensory" else _D_GREEN

    def _make_schema_card(self, variant: str) -> Group:
        """Build one schema trial card with optional in-card memory label."""
        if variant == "sensory":
            card = _box(CAT)
            card.scale_to_fit_height(self._SCHEMA_ITEM_HEIGHT)
            card[-1].set_opacity(0.0)
            card[0].set_stroke(color=GREY, width=1.5, opacity=0.85)
            card[0].set_fill(WHITE, opacity=1.0)
            card.projection_source = card[0]
            card.layout_anchor = card[0]
            return card

        ghost_card = _box(CAT)
        ghost_card.scale_to_fit_height(self._SCHEMA_ITEM_HEIGHT)
        ghost_card[-1].set_opacity(0.0)
        ghost_card[0].set_stroke(color=GREY, width=1.3, opacity=self._SCHEMA_MEMORY_GHOST_CARD_OPACITY)
        ghost_card[0].set_fill(WHITE, opacity=0.70)
        ghost_card[1].set_opacity(self._SCHEMA_MEMORY_GHOST_IMAGE_OPACITY)
        ghost_card.set_z_index(-1)
        ghost_card.shift(
            LEFT * self._SCHEMA_MEMORY_GHOST_OFFSET
            + UP * self._SCHEMA_MEMORY_GHOST_OFFSET
        )

        card = _box(None)
        card.scale_to_fit_height(self._SCHEMA_ITEM_HEIGHT)
        card[-1].set_opacity(0.0)
        card[0].set_stroke(color=GREY, width=1.5, opacity=0.85)
        card[0].set_fill(WHITE, opacity=1.0)
        memory_text = Tex(
            "Memory",
            color=INK,
            font_size=18,
        ).move_to(card[0].get_center())

        memory_group = Group(ghost_card, card, memory_text)
        memory_group.projection_source = card[0]
        memory_group.layout_anchor = card[0]
        return memory_group

    def _make_schema_cat_label(self, font_size: int) -> Tex:
        """Build the quoted class label used in the train/test schema."""
        return Tex(
            r"\textbf{``Cat''}",
            color=INK,
            font_size=font_size,
        )

    def _make_schema_question_label(self, font_size: int) -> Tex:
        """Build the unresolved class label used before the conceptual fork."""
        return Tex(
            r"\textbf{?}",
            color=INK,
            font_size=font_size + 2,
        )

    def _make_schema_train_block(self, variant: str) -> Group:
        """Build the framed train block with label, stimulus, and grey voxel pattern."""
        card = self._make_schema_card(variant)
        object_label = self._make_schema_cat_label(font_size=19)
        pattern = self._make_grid(
            ORIGIN,
            self._SCHEMA_TRAIN_COLOR,
            self._schema_pattern(variant),
        )
        pattern.scale_to_fit_height(card.height * 0.90)
        content = Group(object_label, card, pattern).arrange(DOWN, buff=0.10)
        frame = RoundedRectangle(
            width=content.width + 0.28,
            height=content.height + 0.26,
            corner_radius=0.12,
            stroke_color=_D_MGREY,
            stroke_width=1.7,
        ).move_to(content)
        train_label = Tex(
            "Train",
            color=INK,
            font_size=15,
        ).next_to(frame, UP, buff=0.05).align_to(frame, LEFT)
        return Group(train_label, frame, object_label, card, pattern)

    def _make_schema_grid(
        self,
        variant: str,
        col: str,
        reference_card: Mobject,
    ) -> VGroup:
        """Build one square voxel grid matched to the trial-card size."""
        grid = self._make_grid(ORIGIN, col, self._schema_pattern(variant))
        grid.scale_to_fit_height(self._SCHEMA_ITEM_HEIGHT)
        return grid

    def _make_intuition_row(
        self,
        left_pattern: np.ndarray,
        right_pattern: np.ndarray,
    ) -> Group:
        """Build one central matrix-only intuition row."""
        left_x = -1.22
        right_x = 1.22
        left_grid = self._make_grid(
            ORIGIN,
            self._INTUITION_LEFT_COLOR,
            left_pattern,
        ).scale(1.20)
        right_grid = self._make_grid(
            ORIGIN,
            self._INTUITION_RIGHT_COLOR,
            right_pattern,
        ).scale(1.20)
        left_grid.move_to(np.array([left_x, 0.0, 0.0]))
        right_grid.move_to(np.array([right_x, 0.0, 0.0]))

        bidirectional_arrow = DoubleArrow(
            left_grid.get_right(),
            right_grid.get_left(),
            color=_D_MGREY,
            stroke_width=1.6,
            buff=0.10,
            tip_length=0.07,
        )
        return Group(left_grid, bidirectional_arrow, right_grid)

    def _make_overlap_ghost(self, source_grid: VGroup) -> VGroup:
        """Build a translucent copy of a voxel pattern for overlap animation."""
        ghost = source_grid.copy()
        for cell in ghost:
            cell.set_stroke(width=0.5, opacity=0.18)
            cell.set_fill(opacity=0.34)
        return ghost

    def _make_schema_projection_lines(
        self,
        source_card: Mobject,
        brain: Mobject,
    ) -> VGroup:
        """Build converging card-to-brain guide lines that stop short of the brain."""
        start_x = source_card.get_right()[0] + self._SCHEMA_HORIZONTAL_GAP
        focus_x = (
            brain.get_left()[0]
            - self._SCHEMA_HORIZONTAL_GAP
            - self._SCHEMA_PROJECTION_END_INSET
        )
        source_y = source_card.get_center()[1]
        half_angle = 0.5 * DEGREES * self._SCHEMA_PROJECTION_OPENING_DEG
        dx = max(0.01, focus_x - start_x)
        dy = np.tan(half_angle) * dx

        lines = VGroup(
            Line(
                np.array([start_x, source_y + dy, 0.0]),
                np.array([focus_x, source_y, 0.0]),
                color=self._SCHEMA_PROJECTION_COLOR,
                stroke_width=0.9,
            ).set_stroke(opacity=0.85),
            Line(
                np.array([start_x, source_y - dy, 0.0]),
                np.array([focus_x, source_y, 0.0]),
                color=self._SCHEMA_PROJECTION_COLOR,
                stroke_width=0.9,
            ).set_stroke(opacity=0.85),
        )
        lines.set_z_index(-1)
        return lines

    def _make_schema_pattern_box(
        self,
        variant: str,
        col: str,
        decoder_height: float,
        *,
        label_style: str,
    ) -> Group:
        """Build the multivoxel-pattern group for train or predict rows."""
        pattern = self._make_grid(
            ORIGIN,
            col,
            self._schema_pattern(variant),
        )
        reference_pattern = pattern.copy()
        reference_label = self._make_schema_cat_label(font_size=20)
        reference_group = Group(reference_pattern, reference_label).arrange(
            DOWN,
            buff=0.16,
        )
        reference_group.scale_to_fit_height(
            decoder_height * self._SCHEMA_PATTERN_BOX_TO_DECODER_RATIO
        )
        pattern_target_height = reference_pattern.height

        if label_style == "cat":
            pattern_label = self._make_schema_cat_label(font_size=20)
            pattern.scale_to_fit_height(pattern_target_height)
            pattern_group = Group(pattern, pattern_label).arrange(DOWN, buff=0.16)
            pattern_group.scale_to_fit_height(
                decoder_height * self._SCHEMA_PATTERN_BOX_TO_DECODER_RATIO
            )
            pattern_group.matrix = pattern
        elif label_style == "none":
            pattern.scale_to_fit_height(pattern_target_height)
            pattern_group = Group(pattern)
            pattern_group.matrix = pattern
        else:
            raise ValueError(f"Unknown schema label style: {label_style}")
        return pattern_group

    def _make_schema_link_arrow(self, source_right_x: float, y: float) -> Arrow:
        """Build one detached horizontal connector with standardized span."""
        return Arrow(
            np.array([
                source_right_x + self._SCHEMA_HORIZONTAL_GAP,
                y,
                0.0,
            ]),
            np.array([
                source_right_x + self._SCHEMA_HORIZONTAL_GAP + self._SCHEMA_LINK_ARROW_LENGTH,
                y,
                0.0,
            ]),
            color=_D_MGREY,
            stroke_width=1.6,
            buff=0.0,
            tip_length=0.08,
        )

    def _make_schema_action_label(self, text: str, arrow: Arrow) -> Tex:
        """Build the action label centered above a schema connector."""
        label = Tex(
            text,
            color=INK,
            font_size=17,
        )
        label.move_to(
            arrow.get_center() + UP * self._SCHEMA_ARROW_LABEL_BUFF
        )
        label.add_background_rectangle(color=BG, opacity=1.0, buff=0.05)
        return label

    def _make_schema_output_label(
        self,
        kind: str,
        *,
        font_size: int,
    ) -> Mobject:
        """Build the terminal label for a predict row."""
        if kind == "cat":
            return self._make_schema_cat_label(font_size=font_size)
        if kind == "question":
            return self._make_schema_question_label(font_size=font_size)
        raise ValueError(f"Unknown schema output label kind: {kind}")

    def _make_schema_outcome_group(
        self,
        headline: Mobject,
        subtitle_tex: str,
    ) -> VGroup:
        """Build one conceptual outcome shown after the memory-test question."""
        subtitle = Tex(
            subtitle_tex,
            color=INK,
            font_size=16,
            tex_environment="center",
        )
        return VGroup(headline, subtitle).arrange(DOWN, buff=0.08)

    def _make_schema_memory_fork(self, question_label: Mobject) -> Group:
        """Build the conceptual fork that follows the unresolved memory prediction."""
        shared_outcome = self._make_schema_outcome_group(
            self._make_schema_cat_label(font_size=20),
            r"shared format",
        )
        discontinuity_outcome = self._make_schema_outcome_group(
            Tex(r"\textbf{Chance}", color=INK, font_size=20),
            r"different format",
        )
        outcomes = VGroup(shared_outcome, discontinuity_outcome).arrange(
            DOWN,
            buff=self._SCHEMA_FORK_VERTICAL_GAP,
        )
        outcomes.move_to(
            np.array([
                question_label.get_right()[0]
                + self._SCHEMA_FORK_HORIZONTAL_GAP
                + outcomes.width / 2,
                question_label.get_center()[1],
                0.0,
            ])
        )

        start_x = question_label.get_right()[0] + self._SCHEMA_FORK_ARROW_GAP
        shared_arrow = Arrow(
            np.array([start_x, question_label.get_center()[1], 0.0]),
            np.array([
                shared_outcome.get_left()[0] - self._SCHEMA_FORK_ARROW_GAP,
                shared_outcome.get_center()[1],
                0.0,
            ]),
            color=_D_MGREY,
            stroke_width=1.5,
            buff=0.0,
            tip_length=0.08,
        )
        discontinuity_arrow = Arrow(
            np.array([start_x, question_label.get_center()[1], 0.0]),
            np.array([
                discontinuity_outcome.get_left()[0] - self._SCHEMA_FORK_ARROW_GAP,
                discontinuity_outcome.get_center()[1],
                0.0,
            ]),
            color=_D_MGREY,
            stroke_width=1.5,
            buff=0.0,
            tip_length=0.08,
        )

        fork = Group(shared_arrow, discontinuity_arrow, shared_outcome, discontinuity_outcome)
        fork.arrows = VGroup(shared_arrow, discontinuity_arrow)
        fork.outcomes = VGroup(shared_outcome, discontinuity_outcome)
        return fork

    def _make_single_stroke_row_brace(
        self,
        *,
        x_left: float,
        y_center: float,
        height: float,
        color: str,
    ) -> MathTex:
        """Build a standard mathematical left brace aligned to the main row items."""
        brace = MathTex(r"\{", color=color)
        brace.set_stroke(width=0.0, opacity=0.0)
        brace.set_fill(color=color, opacity=self._SCHEMA_ROW_BRACE_OPACITY)
        brace.stretch_to_fit_height(height * self._SCHEMA_ROW_BRACE_HEIGHT_SCALE)
        brace.move_to(
            np.array([
                x_left - self._SCHEMA_ROW_BRACE_BUFF - brace.width / 2,
                y_center,
                0.0,
            ])
        )
        return brace

    def _make_schema_row_annotation(self, row: Group) -> VGroup:
        """Build the left brace and role label for one schema row."""
        row_col = self._schema_row_label_color(row.mode)
        anchor_items = row.annotation_items
        x_left = min(mob.get_left()[0] for mob in anchor_items)
        y_center = row.layout_anchor.get_center()[1]
        top_extent = max(mob.get_top()[1] - y_center for mob in anchor_items)
        bottom_extent = max(y_center - mob.get_bottom()[1] for mob in anchor_items)
        brace = self._make_single_stroke_row_brace(
            x_left=x_left,
            y_center=y_center,
            height=2.0 * max(top_extent, bottom_extent),
            color=row_col,
        )
        label = Tex(
            self._schema_row_label_text(row.mode),
            color=row_col,
            font_size=self._SCHEMA_ROW_LABEL_FONT_SIZE,
        )
        label.move_to(
            np.array([
                brace.get_left()[0] - self._SCHEMA_ROW_LABEL_BUFF - label.width / 2,
                y_center,
                0.0,
            ])
        )
        return VGroup(brace, label)

    def _make_schema_row(
        self,
        *,
        mode: str,
        variant: str,
        output_kind: str,
    ) -> Group:
        """Build one centered train-input schema row."""
        shared_item_height = self._SCHEMA_ITEM_HEIGHT
        row_center_y = 0.0
        card = self._make_schema_card(variant)
        decoder = self._make_schema_decoder(
            ORIGIN,
            shared_item_height * self._SCHEMA_DECODER_HEIGHT_RATIO,
        )
        pattern_box = self._make_schema_pattern_box(
            variant,
            self._SCHEMA_TRAIN_COLOR if mode == "train" else self._SCHEMA_TEST_COLOR,
            shared_item_height * self._SCHEMA_PATTERN_REFERENCE_HEIGHT_RATIO,
            label_style="cat" if mode == "train" else "none",
        )

        card.shift(ORIGIN - card.layout_anchor.get_center())
        brain = _make_v1v2v3_viewing_brain(
            brain_left_x=card.layout_anchor.get_right()[0] + 0.92,
            brain_center_y=row_center_y,
            target_brain_height=shared_item_height,
        )
        pattern_box.next_to(brain, RIGHT, buff=self._SCHEMA_LINK_SPAN)
        pattern_box.shift(UP * (row_center_y - pattern_box.matrix.get_center()[1]))
        arrow_y = row_center_y
        brain_to_pattern_arrow = self._make_schema_link_arrow(brain.get_right()[0], arrow_y)

        decoder.next_to(pattern_box, RIGHT, buff=self._SCHEMA_LINK_SPAN)
        decoder.move_to(
            np.array([decoder.get_center()[0], row_center_y, 0.0])
        )
        decode_arrow = self._make_schema_link_arrow(pattern_box.get_right()[0], arrow_y)
        action_label = self._make_schema_action_label(
            "Train" if mode == "train" else "Predict",
            decode_arrow,
        )

        row_items: list[Mobject] = [
            card,
            brain,
            brain_to_pattern_arrow,
            pattern_box,
            decode_arrow,
            action_label,
            decoder,
        ]
        output_items: list[Mobject] = []
        if mode == "predict" and output_kind != "none":
            output_arrow = self._make_schema_link_arrow(decoder.get_right()[0], arrow_y)
            output_label = self._make_schema_output_label(
                output_kind,
                font_size=20,
            ).next_to(
                decoder,
                RIGHT,
                buff=self._SCHEMA_LINK_SPAN,
            )
            output_items = [output_arrow, output_label]
            row_items.extend(output_items)

        row = Group(*row_items)
        row.decoder = decoder
        row.mode = mode
        row.card_group = Group(card)
        row.brain_group = Group(brain)
        row.pattern_group = Group(brain_to_pattern_arrow, pattern_box)
        row.decoder_group = Group(decode_arrow, action_label, decoder)
        row.input_group = Group(
            card,
            brain,
            brain_to_pattern_arrow,
            pattern_box,
        )
        row.decode_support = Group(decode_arrow, action_label)
        row.output_group = Group(*output_items)
        row.output_target = output_items[-1] if output_items else None
        row.layout_anchor = card.layout_anchor
        row.annotation_items = (
            card,
            brain,
            pattern_box.matrix,
            decoder,
            *([row.output_target] if row.output_target is not None else []),
        )
        row.layout_group = Group(
            card.layout_anchor,
            brain,
            brain_to_pattern_arrow,
            pattern_box,
            decode_arrow,
            action_label,
            decoder,
            *output_items,
        )
        row.shift(ORIGIN - row.layout_group.get_center())
        return row

    def _build_schema_block(
        self,
        *,
        cases: list[tuple[str, str, str]],
        top_limit: float,
        bottom_limit: float,
        first_gap: float | None = None,
        show_row_annotations: bool = False,
        vertical_align: str = "center",
        top_margin: float = 0.0,
    ) -> dict[str, object]:
        """Build and position a reusable schema block for one or more rows."""
        rows = [
            self._make_schema_row(
                mode=mode,
                variant=variant,
                output_kind=output_kind,
            )
            for mode, variant, output_kind in cases
        ]
        for row in rows:
            row.scale(self._SCHEMA_ROW_SCALE)

        rows[0].shift(ORIGIN - rows[0].layout_group.get_center())
        for idx in range(1, len(rows)):
            vertical_gap = (
                (
                    first_gap
                    if first_gap is not None
                    else self._SCHEMA_TRAIN_TO_PREDICT_GAP
                )
                if idx == 1
                else self._SCHEMA_PREDICT_TO_PREDICT_GAP
            )
            dx = (
                rows[idx - 1].layout_anchor.get_left()[0]
                - rows[idx].layout_anchor.get_left()[0]
            )
            dy = (
                rows[idx - 1].layout_group.get_bottom()[1]
                - vertical_gap
                - rows[idx].layout_group.get_top()[1]
            )
            rows[idx].shift(np.array([dx, dy, 0.0]))

        memory_fork = None
        last_output_kind = cases[-1][2]
        if last_output_kind == "question" and rows[-1].output_target is not None:
            memory_fork = self._make_schema_memory_fork(rows[-1].output_target)

        if show_row_annotations:
            for row in rows:
                annotation = self._make_schema_row_annotation(row)
                row.annotation_group = annotation
                row.input_group.add(annotation)
                row.add(annotation)

        schema_members: list[Mobject] = [*rows]
        if memory_fork is not None:
            schema_members.append(memory_fork)
        schema_block = Group(*schema_members)
        layout_members: list[Mobject] = [*(row.layout_group for row in rows)]
        if memory_fork is not None:
            layout_members.append(memory_fork)
        schema_layout_group = Group(*layout_members)
        available_height = top_limit - bottom_limit - (
            top_margin if vertical_align == "top" else 0.0
        )
        if schema_layout_group.height > available_height:
            schema_block.scale(available_height / schema_layout_group.height)
        schema_available_width = config.frame_width - 0.80
        if schema_layout_group.width > schema_available_width:
            schema_block.scale(schema_available_width / schema_layout_group.width)
        if vertical_align == "top":
            schema_block.shift(
                np.array([
                    -schema_layout_group.get_center()[0],
                    top_limit - top_margin - schema_layout_group.get_top()[1],
                    0.0,
                ])
            )
        elif vertical_align == "center":
            schema_block.shift(
                np.array([0.0, 0.5 * (top_limit + bottom_limit), 0.0])
                - schema_layout_group.get_center()
            )
        else:
            raise ValueError(f"Unknown schema vertical alignment: {vertical_align}")
        return {
            "rows": rows,
            "memory_fork": memory_fork,
            "schema_block": schema_block,
        }

    def _build_overview_schema_block(
        self,
        *,
        cases: list[tuple[str, str, str]],
        top_limit: float,
        bottom_limit: float,
    ) -> dict[str, object]:
        """Build the shared overview schema with the canonical brace layout."""
        return self._build_schema_block(
            cases=cases,
            top_limit=top_limit,
            bottom_limit=bottom_limit,
            first_gap=1.12,
            show_row_annotations=True,
            vertical_align="top",
            top_margin=0.28 + 0.15 * (top_limit - bottom_limit),
        )

    def _play_schema_row_sequence(
        self,
        row: Group,
        *,
        source_decoder: Mobject | None = None,
        include_output: bool = True,
    ) -> None:
        """Reveal one schema row from left to right."""
        if hasattr(row, "annotation_group"):
            self.play(
                FadeIn(row.annotation_group, shift=LEFT * 0.05),
                run_time=self._SCHEMA_COMPONENT_REVEAL_TIME,
            )
        self.play(
            FadeIn(row.card_group, shift=UP * 0.06),
            run_time=self._SCHEMA_COMPONENT_REVEAL_TIME,
        )
        self.play(
            FadeIn(row.brain_group, shift=RIGHT * 0.05),
            run_time=self._SCHEMA_COMPONENT_REVEAL_TIME,
        )
        self.play(
            FadeIn(row.pattern_group, shift=RIGHT * 0.05),
            run_time=self._SCHEMA_COMPONENT_REVEAL_TIME,
        )
        if source_decoder is None:
            self.play(
                FadeIn(row.decode_support, shift=RIGHT * 0.05),
                FadeIn(row.decoder, shift=RIGHT * 0.05),
                run_time=self._SCHEMA_COMPONENT_REVEAL_TIME,
            )
        else:
            self.play(
                FadeIn(row.decode_support, shift=RIGHT * 0.05),
                TransformFromCopy(
                    source_decoder,
                    row.decoder,
                    path_arc=self._SCHEMA_CLASSIFIER_PATH_ARC,
                ),
                run_time=self._SCHEMA_CLASSIFIER_TRANSFER_TIME,
            )
        if include_output and len(row.output_group) > 0:
            self.play(
                FadeIn(row.output_group, shift=RIGHT * 0.05),
                run_time=self._SCHEMA_OUTPUT_REVEAL_TIME,
            )

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        self._set_overview_camera_frame()
        ctx = self._build_overview_b_end_state()
        self.add(ctx["frame"])
        self.wait(0.70)

        similar_pattern = self._pattern_for_index(3)
        different_pattern = np.array([
            [0.18, 0.86, 0.24],
            [0.78, 0.14, 0.70],
            [0.34, 0.76, 0.20],
        ])
        similar_label = Tex(
            r"\textbf{Similar} multivoxel \textbf{patterns}\\"
            r"suggest a \textbf{similar} neural \textbf{representation}",
            color=INK,
            font_size=21,
            tex_environment="center",
        )
        different_label = Tex(
            r"\textbf{Dissimilar} multivoxel \textbf{patterns}\\"
            r"suggest a \textbf{different} neural \textbf{representation}",
            color=INK,
            font_size=21,
            tex_environment="center",
        )
        similar_case = Group(
            similar_label,
            self._make_intuition_row(similar_pattern, similar_pattern.copy()),
        ).arrange(DOWN, buff=0.28)
        different_case = Group(
            different_label,
            self._make_intuition_row(similar_pattern, different_pattern),
        ).arrange(DOWN, buff=0.28)
        intuition_rows = Group(
            similar_case,
            different_case,
        ).arrange(DOWN, buff=1.10)
        content_top_limit = ctx["title"].get_bottom()[1] - 0.18
        content_bottom_limit = -config.frame_height / 2 + 0.36
        intro_top_limit = content_top_limit
        intro_bottom_limit = content_bottom_limit
        intro_available_height = intro_top_limit - intro_bottom_limit
        if intuition_rows.height > intro_available_height:
            intuition_rows.scale_to_fit_height(intro_available_height)
        intro_center_y = 0.5 * (intro_top_limit + intro_bottom_limit)
        intuition_rows.move_to(
            np.array([0.0, intro_center_y, 0.0])
        )
        if intuition_rows.get_top()[1] > intro_top_limit:
            intuition_rows.shift(DOWN * (intuition_rows.get_top()[1] - intro_top_limit))
        if intuition_rows.get_bottom()[1] < intro_bottom_limit:
            intuition_rows.shift(UP * (intro_bottom_limit - intuition_rows.get_bottom()[1]))

        schema_ctx = self._build_overview_schema_block(
            cases=self._SCHEMA_OVERVIEW_CASES,
            top_limit=content_top_limit,
            bottom_limit=content_bottom_limit,
        )
        rows = schema_ctx["rows"]
        memory_fork = schema_ctx["memory_fork"]
        overview_body = Group(*(mob for mob in ctx["frame"] if mob is not ctx["title"]))

        self.play(
            FadeOut(overview_body),
            FadeIn(intuition_rows, shift=UP * 0.08),
            run_time=1.05,
        )
        self.wait(self._SCHEMA_INTRO_PANEL_PAUSE)

        self.play(
            FadeOut(intuition_rows, shift=LEFT * 0.10),
            run_time=0.75,
        )
        self._play_schema_row_sequence(rows[0])
        self.wait(self._SCHEMA_TRAIN_EXPLAIN_PAUSE)
        self._play_schema_row_sequence(rows[1], source_decoder=rows[0].decoder)
        self.wait(self._SCHEMA_OUTPUT_EXPLAIN_PAUSE)
        if memory_fork is not None:
            self.play(
                LaggedStart(
                    GrowArrow(memory_fork.arrows[0]),
                    FadeIn(memory_fork.outcomes[0], shift=RIGHT * 0.06),
                    GrowArrow(memory_fork.arrows[1]),
                    FadeIn(memory_fork.outcomes[1], shift=RIGHT * 0.06),
                    lag_ratio=0.15,
                ),
                run_time=self._SCHEMA_FORK_REVEAL_TIME,
            )
            self.wait(self._SCHEMA_FORK_EXPLAIN_PAUSE)


class Study2DecodingSummary(Study2DecodingOverviewC):
    """
    End-of-study summary placeholder for the decoding-combinations overview.

    Render:
        uv run manim scenes/study2.py Study2DecodingSummary -ql
        uv run manim scenes/study2.py Study2DecodingSummary -qh
    """

    _SUMMARY_TITLE = r"\textbf{Decoding Summary}"
    _SUMMARY_MEMORY_CASES = [
        ("train", "memory", "none"),
        ("predict", "memory", "cat"),
    ]
    _SUMMARY_COLUMN_GAP = 1.02
    _SUMMARY_MEMORY_SCALE = 0.90

    def construct(self) -> None:
        """Show a static copy of the current three-row decoding schema."""
        self.camera.background_color = BG
        title = Tex(
            self._SUMMARY_TITLE,
            color=INK,
            font_size=28,
        ).to_edge(UP, buff=0.28)

        sensory_ctx = self._build_schema_block(
            cases=self._SCHEMA_SUMMARY_CASES,
            top_limit=title.get_bottom()[1] - 0.22,
            bottom_limit=-config.frame_height / 2 + 0.24,
        )
        memory_ctx = self._build_schema_block(
            cases=self._SUMMARY_MEMORY_CASES,
            top_limit=title.get_bottom()[1] - 0.22,
            bottom_limit=-config.frame_height / 2 + 0.24,
        )

        sensory_block = sensory_ctx["schema_block"]
        sensory_rows = sensory_ctx["rows"]
        memory_block = memory_ctx["schema_block"]
        memory_rows = memory_ctx["rows"]
        memory_block.scale(self._SUMMARY_MEMORY_SCALE)

        upper_right_anchor = max(
            sensory_rows[0].decoder.get_right()[0],
            sensory_rows[1].output_target.get_right()[0],
        )
        memory_target_left = upper_right_anchor + self._SUMMARY_COLUMN_GAP
        memory_block.shift(
            RIGHT * (memory_target_left - memory_rows[0].layout_anchor.get_left()[0])
        )
        memory_block.shift(
            UP * (sensory_rows[0].get_center()[1] - memory_rows[0].get_center()[1])
        )

        summary_group = Group(sensory_block, memory_block)
        top_limit = title.get_bottom()[1] - 0.22
        bottom_limit = -config.frame_height / 2 + 0.24
        available_height = top_limit - bottom_limit
        if summary_group.height > available_height:
            summary_group.scale_to_fit_height(available_height)
        available_width = config.frame_width - 0.70
        if summary_group.width > available_width:
            summary_group.scale_to_fit_width(available_width)
        summary_group.move_to(np.array([0.0, 0.5 * (top_limit + bottom_limit), 0.0]))
        if summary_group.get_top()[1] > top_limit:
            summary_group.shift(DOWN * (summary_group.get_top()[1] - top_limit))
        if summary_group.get_bottom()[1] < bottom_limit:
            summary_group.shift(UP * (bottom_limit - summary_group.get_bottom()[1]))

        self.play(FadeIn(title, shift=UP * 0.06), run_time=0.45)
        self.play(FadeIn(summary_group, shift=UP * 0.08), run_time=0.9)
        self.wait(2.0)


# ══════════════════════════════════════════════════════════════════════════════
# Study2WithinSession2DecodingSetup
# ══════════════════════════════════════════════════════════════════════════════


def _make_feature_row(
    values: np.ndarray,
    color: str = _D_BLUE,
    cell_w: float = 0.18,
    cell_h: float | None = None,
    gap: float = 0.055,
    low_color=WHITE,
    mid_color=None,
    high_color=None,
    stroke_color=_D_LGREY,
    stroke_width: float = 0.7,
    midpoint: float = 0.5,
) -> VGroup:
    """Horizontal row of voxel-feature cells."""
    if cell_h is None:
        cell_h = cell_w
    if high_color is None:
        high_color = color

    group = VGroup()
    mid = (len(values) - 1) / 2
    for i, v in enumerate(values):
        value = float(np.clip(v, 0.0, 1.0))
        if mid_color is None:
            # Sequential mode: interpolate directly from low -> high while
            # keeping a small floor so zero-valued cells are still visible.
            fill_color = interpolate_color(
                ManimColor(low_color),
                ManimColor(high_color),
                0.10 + 0.90 * value,
            )
        else:
            # Diverging mode: first map values into the narrower range used by
            # the manuscript plots, then split interpolation around the midpoint.
            value = (
                _DIVERGING_MATRIX_VALUE_MIN
                + (_DIVERGING_MATRIX_VALUE_MAX - _DIVERGING_MATRIX_VALUE_MIN) * value
            )
            midpoint = float(np.clip(midpoint, 1e-6, 1.0 - 1e-6))
            if value <= midpoint:
                local_t = value / midpoint
                fill_color = interpolate_color(
                    ManimColor(low_color),
                    ManimColor(mid_color),
                    local_t,
                )
            else:
                local_t = (value - midpoint) / (1.0 - midpoint)
                fill_color = interpolate_color(
                    ManimColor(mid_color),
                    ManimColor(high_color),
                    local_t,
                )
        cell = Rectangle(
            width=cell_w,
            height=cell_h,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
        ).set_fill(fill_color, opacity=1.0)
        cell.move_to(RIGHT * (i - mid) * (cell_w + gap))
        group.add(cell)
    group.move_to(ORIGIN)
    return group


class Study2WithinSession2DecodingSetup(Study2DecodingOverviewC):
    """
    Starts from the previous end state, merges feature vectors into a
    samples x features matrix, and illustrates leave-one-run-out decoding.

    Render:
        uv run manim scenes/study2.py Study2WithinSession2DecodingSetup -qh
    """

    _ROW_COLS = [_D_BLUE, _D_AMBER, _D_GREEN, _D_RED, _D_PURP, _D_CYAN]
    _OVERVIEW_SETUP_CASES = [
        ("train", "sensory", "none"),
        ("predict", "sensory", "question"),
    ]
    _SENSORY_CASE_TITLE = r"\textbf{Within-session sensory-sensory decoding}"
    _CV_TITLE = r"\textbf{Leave-One-Run-Out Cross-Validation}"
    _MATRIX_STROKE_COLOR = "#D8D1C7"
    _MATRIX_DIVERGING_LOW_COLOR = "#6E8FB3"
    _MATRIX_DIVERGING_MID_COLOR = "#F5F3EE"
    _MATRIX_DIVERGING_HIGH_COLOR = "#C46A5A"
    _SETUP_ROWS_RIGHT_SHIFT_RATIO = 0.10
    _BASE_ROWS = [
        np.array([0.90, 0.20, 0.70, 0.30, 0.80, 0.10, 0.50, 0.40, 0.90]),
        np.array([0.25, 0.82, 0.18, 0.74, 0.22, 0.88, 0.30, 0.68, 0.24]),
        np.array([0.58, 0.34, 0.86, 0.18, 0.42, 0.80, 0.16, 0.66, 0.54]),
        np.array([0.84, 0.46, 0.12, 0.70, 0.26, 0.52, 0.92, 0.24, 0.60]),
        np.array([0.20, 0.62, 0.48, 0.86, 0.36, 0.14, 0.74, 0.54, 0.92]),
        np.array([0.76, 0.12, 0.56, 0.28, 0.90, 0.44, 0.18, 0.82, 0.34]),
    ]

    def _row_values(self, base_idx: int, run_idx: int) -> np.ndarray:
        """Return the conceptual row values for the within-session decoding matrix."""
        base = self._BASE_ROWS[base_idx % len(self._BASE_ROWS)]
        rolled = np.roll(base, (run_idx + base_idx) % 3)
        jitter = 0.05 * np.sin(
            np.arange(base.size) * 1.15 + 0.75 * run_idx + 0.35 * base_idx
        )
        return np.clip(0.84 * base + 0.16 * rolled + jitter, 0.08, 0.98)

    def _make_cv_matrix_row(
        self,
        global_idx: int,
        center: np.ndarray,
    ) -> VGroup:
        """Build one diverging-heatmap voxel row for the conceptual CV matrix."""
        return _make_feature_row(
            self._row_values(global_idx % len(self._BASE_ROWS), global_idx // 4),
            color=self._MATRIX_DIVERGING_HIGH_COLOR,
            cell_w=0.11,
            cell_h=0.11,
            gap=0.025,
            low_color=self._MATRIX_DIVERGING_LOW_COLOR,
            mid_color=self._MATRIX_DIVERGING_MID_COLOR,
            high_color=self._MATRIX_DIVERGING_HIGH_COLOR,
            stroke_color=self._MATRIX_STROKE_COLOR,
            stroke_width=0.65,
        ).move_to(center)

    def _matrix_row_centers(self, x: float, y_shift: float = 0.0) -> list[np.ndarray]:
        """Return the scene centres for the conceptual decoding-matrix rows."""
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
        """Build the test-point markers for the conceptual decoding matrix."""
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

    def _make_cv_detail_callout(
        self,
        matrix_body: Mobject,
        right_bracket: Mobject,
        train_col: str,
        test_col: str,
        *,
        include_label: bool = False,
    ) -> VGroup:
        """Build the train/test callout beside the cross-validation matrix."""
        detail = VGroup(
            Tex(r"\textbf{Train on 7 runs}", color=train_col, font_size=24),
            Tex(r"\textbf{Test on the held-out run}", color=test_col, font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        if include_label:
            label = Tex(
                r"\textbf{Leave-One-Run-Out Cross-Validation}",
                color=INK,
                font_size=18,
            )
            callout = VGroup(label, detail).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        else:
            callout = detail
        callout.next_to(right_bracket, RIGHT, buff=0.92)
        callout.align_to(matrix_body, UP).shift(DOWN * 0.28)
        return callout

    def _make_test_flow_annotation(
        self,
        train_frame: Mobject,
        test_frame: Mobject,
        test_col: str,
    ) -> VGroup:
        """Build the downward arrow showing the test flow on the right."""
        arrow_x = train_frame.get_right()[0] + 0.34
        test_arrow = Arrow(
            np.array([arrow_x, train_frame.get_bottom()[1] - 0.02, 0.0]),
            np.array([arrow_x, test_frame.get_top()[1] + 0.02, 0.0]),
            color=test_col,
            stroke_width=3.4,
            buff=0.02,
            tip_length=0.18,
        )
        test_label = Tex(r"\textbf{Test}", color=test_col, font_size=20).next_to(
            test_arrow, RIGHT, buff=0.08
        )
        return VGroup(test_arrow, test_label)

    def _build_results_handoff_frame(self) -> dict[str, Mobject]:
        """Build the locked setup/results handoff frame."""
        return Study2WithinSession2DecodingResults._build_locked_setup_frame(self)

    def _build_cross_session_handoff_frame(self) -> dict[str, Mobject]:
        """Build the locked results/cross-session handoff frame."""
        return Study2WithinSession2DecodingResults._build_results_end_static(self)

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        self._set_overview_camera_frame()

        overview_title = self._make_overview_title(self._OVERVIEW_B_TITLE)
        overview_content_top_limit = overview_title.get_bottom()[1] - 0.18
        overview_content_bottom_limit = -config.frame_height / 2 + 0.36
        overview_final_schema_ctx = self._build_overview_schema_block(
            cases=self._SCHEMA_OVERVIEW_CASES,
            top_limit=overview_content_top_limit,
            bottom_limit=overview_content_bottom_limit,
        )
        overview_final_schema = overview_final_schema_ctx["schema_block"]
        overview_final_rows = overview_final_schema_ctx["rows"]
        overview_memory_fork = overview_final_schema_ctx["memory_fork"]
        top_row = overview_final_rows[0]
        overview_memory_row = overview_final_rows[1]
        overview_setup_schema_ctx = self._build_overview_schema_block(
            cases=self._OVERVIEW_SETUP_CASES,
            top_limit=overview_content_top_limit,
            bottom_limit=overview_content_bottom_limit,
        )
        bottom_row = overview_setup_schema_ctx["rows"][1]
        bottom_row.shift(
            RIGHT
            * (
                top_row.layout_anchor.get_left()[0]
                - bottom_row.layout_anchor.get_left()[0]
            )
        )
        row_pair_width = Group(top_row.layout_anchor, bottom_row.layout_anchor).width
        setup_rows_right_shift = RIGHT * (
            row_pair_width * self._SETUP_ROWS_RIGHT_SHIFT_RATIO
        )
        bottom_row.shift(setup_rows_right_shift)

        title = self._make_overview_title(self._SENSORY_CASE_TITLE)

        self.add(overview_title, overview_final_schema)
        self.wait(0.45)

        self.play(
            TransformMatchingTex(overview_title, title),
            top_row.animate.shift(setup_rows_right_shift),
            FadeOut(overview_memory_fork, shift=RIGHT * 0.08),
            FadeOut(overview_memory_row, shift=DOWN * 0.04),
            run_time=0.70,
        )
        self._play_schema_row_sequence(
            bottom_row,
            source_decoder=top_row.decoder,
            include_output=False,
        )
        uncertain_output_label = VGroup(
            self._make_schema_cat_label(font_size=20),
            self._make_schema_question_label(font_size=20),
        ).arrange(RIGHT, buff=0.10)
        uncertain_output_label.next_to(
            bottom_row.output_group[0],
            RIGHT,
            buff=0.24,
        )
        uncertain_output_label.align_to(bottom_row.output_group[1], DOWN)
        self.play(
            FadeIn(bottom_row.output_group[0], shift=RIGHT * 0.05),
            FadeIn(uncertain_output_label, shift=RIGHT * 0.05),
            run_time=self._SCHEMA_OUTPUT_REVEAL_TIME,
        )
        bottom_input_components = bottom_row.input_group
        bottom_output_components = Group(
            bottom_row.output_group[0],
            uncertain_output_label,
        )
        self.wait(0.75)

        matrix_x = -4.30
        row_centers = self._matrix_row_centers(matrix_x, y_shift=-0.18)
        target_rows = [
            self._make_cv_matrix_row(
                global_idx,
                row_centers[global_idx],
            )
            for global_idx in range(32)
        ]
        run_labels = VGroup(*[
            Tex(f"run {run_idx + 1}", color=INK, font_size=16).next_to(
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
        train_col = self._SCHEMA_TRAIN_COLOR
        test_col = self._SCHEMA_TEST_COLOR
        class_one_col = _identity_color(CAT)
        class_two_col = _identity_color(OBS)
        class_three_col = _identity_color(VASE)
        summary_title = Tex(
            r"Sensory responses\\in Session 2",
            color=INK,
            font_size=24,
            tex_environment="center",
        ).next_to(
            VGroup(left_bracket, matrix_body, right_bracket), UP, buff=0.20
        )
        right_block_y_shift = -0.10
        svm_gap_y = right_block_y_shift + 0.02
        cv_title = self._make_overview_title(self._CV_TITLE).shift(UP * 0.18)
        svm_label = VGroup(
            Tex("Linear", color=INK, font_size=20),
            Tex(r"\textbf{Support Vector Machine}", color=INK, font_size=20),
            Tex("Classifier", color=INK, font_size=20),
        ).arrange(DOWN, buff=0.05)
        cv_detail = self._make_cv_detail_callout(
            matrix_body,
            right_bracket,
            train_col,
            test_col,
        )

        self.play(
            TransformMatchingTex(title, cv_title),
            FadeOut(top_row.input_group, shift=UP * 0.06),
            FadeOut(top_row.decode_support, shift=UP * 0.04),
            FadeOut(top_row.decoder, shift=RIGHT * 0.04),
            FadeOut(bottom_input_components, shift=UP * 0.06),
            FadeOut(bottom_row.decode_support, shift=UP * 0.04),
            FadeOut(bottom_row.decoder, shift=RIGHT * 0.04),
            FadeOut(bottom_output_components, shift=RIGHT * 0.04),
            FadeIn(summary_title, shift=UP * 0.06),
            FadeIn(VGroup(left_bracket, right_bracket), shift=UP * 0.04),
            LaggedStart(
                *[FadeIn(row) for row in target_rows],
                lag_ratio=0.03,
            ),
            LaggedStart(*[FadeIn(lbl) for lbl in run_labels], lag_ratio=0.05),
            run_time=1.0,
        )
        self.remove(top_row.decoder, bottom_row.decoder)
        self.wait(0.40)
        self.play(
            FadeIn(cv_detail, shift=DOWN * 0.04),
            run_time=0.45,
        )
        self.wait(0.55)

        matrix_rows = target_rows
        initial_matrix_rows = [row.copy() for row in target_rows]
        split_focus_matrix_rows = [
            row.copy().set_fill(opacity=0.38).set_stroke(opacity=0.42)
            for row in initial_matrix_rows
        ]

        plot_axis_config = {
            "color": _D_LGREY,
            "stroke_width": 1.4,
            "include_ticks": False,
            "include_tip": False,
        }
        plot_column_x = 4.12
        train_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([plot_column_x, 1.16 + right_block_y_shift, 0.0]))
        test_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([plot_column_x, -1.12 + right_block_y_shift, 0.0]))
        svm_column_x = 0.5 * (right_bracket.get_right()[0] + train_ax.get_left()[0]) + 0.12
        svm_label.move_to(np.array([svm_column_x, svm_gap_y, 0.0]))
        merged_decoder_target = (
            SVGMobject(str(_SVM_CLASSIFIER_GREYSCALE_SVG_PATH))
            .scale_to_fit_height(top_row.decoder.height * 0.52)
            .next_to(svm_label, DOWN, buff=0.12)
        )
        label_col_x = right_bracket.get_right()[0] + 0.42
        arrow_len = 0.77
        arrow_center_x = 0.5 * (label_col_x + 0.42 + svm_label.get_left()[0])
        data_arrow = Arrow(
            np.array([arrow_center_x - arrow_len / 2, svm_gap_y, 0.0]),
            np.array([arrow_center_x + arrow_len / 2, svm_gap_y, 0.0]),
            color=_D_MGREY,
            stroke_width=3.8,
            buff=0.02,
            tip_length=0.18,
        )
        train_frame = SurroundingRectangle(
            train_ax, color=train_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )
        test_frame = SurroundingRectangle(
            test_ax, color=test_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )
        train_title = Tex("training runs", color=train_col, font_size=18).next_to(train_ax, UP, buff=0.08)
        test_title = Tex("held-out run", color=test_col, font_size=18).next_to(test_ax, UP, buff=0.08)
        test_flow_annotation = self._make_test_flow_annotation(
            train_frame,
            test_frame,
            test_col,
        )
        train_x_label = Tex("voxel 1", color=INK, font_size=18).next_to(train_ax, DOWN, buff=0.10)
        train_y_label = Tex("voxel 2", color=INK, font_size=18).rotate(PI / 2).next_to(
            train_ax, LEFT, buff=0.08
        )
        test_x_label = Tex("voxel 1", color=INK, font_size=18).next_to(test_ax, DOWN, buff=0.10)
        test_y_label = Tex("voxel 2", color=INK, font_size=18).rotate(PI / 2).next_to(
            test_ax, LEFT, buff=0.08
        )
        class_example_paths = [CAT, OBS, VASE]
        class_cols = [class_one_col, class_two_col, class_three_col]
        class_examples = Group(*[
            Group(
                ImageMobject(path).scale_to_fit_height(0.50),
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
        class_examples.arrange(RIGHT, buff=0.15).move_to(
            np.array([plot_column_x, train_ax.get_top()[1] + 0.76, 0.0])
        )

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

        train_point_radius = 0.055
        test_point_radius = 0.070
        train_active_opacity = 0.88
        train_inactive_opacity = 0.18
        test_active_opacity = 0.92
        test_inactive_opacity = 0.16
        point_class_order = ["blue", "green", "amber"]
        fixed_class_centers = {
            "blue": (-1.25, -0.02),
            "green": (0.05, 0.96),
            "amber": (1.18, -0.06),
        }
        run_offset_scales = {
            "blue": (0.34, 0.22, 0.12),
            "green": (0.28, 0.18, 0.55),
            "amber": (0.34, 0.22, -0.18),
        }
        replicate_offsets = {
            "blue": [
                (-0.18, 0.20),
                (-0.08, 0.08),
                (0.14, 0.08),
                (0.24, -0.02),
            ],
            "green": [
                (-0.12, 0.18),
                (0.04, 0.08),
                (0.16, -0.08),
                (-0.08, -0.02),
            ],
            "amber": [
                (-0.18, 0.14),
                (-0.08, 0.04),
                (0.10, -0.10),
                (0.22, -0.02),
            ],
        }

        def _build_master_point_specs() -> list[dict[str, float | int | str]]:
            """Return one fixed synthetic dataset shared across all CV folds."""
            specs: list[dict[str, float | int | str]] = []
            for class_name in point_class_order:
                base_x, base_y = fixed_class_centers[class_name]
                x_scale, y_scale, phase = run_offset_scales[class_name]
                for run_idx in range(8):
                    angle = TAU * run_idx / 8.0 + phase
                    run_dx = x_scale * np.cos(angle)
                    run_dy = y_scale * np.sin(angle)
                    for replicate_idx, (rep_dx, rep_dy) in enumerate(
                        replicate_offsets[class_name]
                    ):
                        specs.append(
                            {
                                "class_name": class_name,
                                "run_idx": run_idx,
                                "replicate_idx": replicate_idx,
                                "x": base_x + run_dx + rep_dx,
                                "y": base_y + run_dy + rep_dy,
                            }
                        )
            return specs

        master_point_specs = _build_master_point_specs()

        # Model the class regions as Voronoi cells around slowly moving class
        # centres. The dataset stays fixed while the fold-specific classifier
        # shifts slightly as one run is held out.
        def _decision_shift(fold_idx: int) -> tuple[float, float]:
            """Return the decision shift."""
            return 0.13 * np.sin(0.72 * fold_idx), 0.09 * np.cos(0.86 * fold_idx)

        def _class_centers(fold_idx: int) -> dict[str, tuple[float, float]]:
            """Return the class centers."""
            x_shift, y_shift = _decision_shift(fold_idx)
            return {
                "blue": (-1.25 + 0.28 * x_shift, -0.02 + 0.20 * y_shift),
                "green": (0.05 + 0.56 * x_shift, 0.96 + 1.05 * y_shift),
                "amber": (1.18 + 0.44 * x_shift, -0.06 + 0.22 * y_shift),
            }

        def _region_fill(col: str) -> ManimColor:
            """Return the region fill."""
            return interpolate_color(WHITE, ManimColor(col), 0.58)

        def _clip_polygon_halfplane(
            poly: list[np.ndarray], normal: np.ndarray, offset: float
        ) -> list[np.ndarray]:
            """Return the clip polygon halfplane."""
            if not poly:
                return []

            def inside(p: np.ndarray) -> bool:
                """Return whether the current point lies inside the active region."""
                return float(np.dot(normal, p)) <= offset + 1e-9

            def intersect(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
                """Return the intersection point for the current line segment."""
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
            """Return the linear region polygon."""
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
                # The Voronoi boundary between class i and j is the perpendicular
                # bisector of their centres, expressed here as a half-plane.
                normal = c_j - c_i
                offset = 0.5 * (float(np.dot(c_j, c_j)) - float(np.dot(c_i, c_i)))
                poly = _clip_polygon_halfplane(poly, normal, offset)
                if len(poly) < 3:
                    return []
            return poly

        def _decision_regions(ax: Axes, centers: dict[str, tuple[float, float]]) -> VGroup:
            """Return the decision regions."""
            color_map = {"blue": class_one_col, "green": class_two_col, "amber": class_three_col}
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
            """Return the error mark."""
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

        def _make_panel_points(
            ax: Axes,
            fold_idx: int,
            *,
            mode: str,
            active_opacity: float,
            inactive_opacity: float,
            radius: float,
        ) -> tuple[VGroup, VGroup, VGroup]:
            """Build one fixed dataset view with fold-specific emphasis."""
            color_map = {
                "blue": class_one_col,
                "green": class_two_col,
                "amber": class_three_col,
            }
            points_by_class = {class_name: VGroup() for class_name in point_class_order}
            for spec in master_point_specs:
                is_active = (
                    spec["run_idx"] != fold_idx
                    if mode == "train"
                    else spec["run_idx"] == fold_idx
                )
                opacity = active_opacity if is_active else inactive_opacity
                point = Dot(
                    ax.c2p(float(spec["x"]), float(spec["y"])),
                    radius=radius,
                    color=color_map[str(spec["class_name"])],
                    fill_opacity=opacity,
                )
                point.set_z_index(2 if is_active else 1)
                points_by_class[str(spec["class_name"])].add(point)
            return (
                points_by_class["blue"],
                points_by_class["green"],
                points_by_class["amber"],
            )

        def _decision_margin(
            spec: dict[str, float | int | str],
            centers: dict[str, tuple[float, float]],
        ) -> float:
            """Return the minimum distance from one point to any class boundary."""
            point = np.array([float(spec["x"]), float(spec["y"])], dtype=float)
            class_name = str(spec["class_name"])
            c_i = np.array(centers[class_name], dtype=float)
            margins: list[float] = []
            for other_label, other_center in centers.items():
                if other_label == class_name:
                    continue
                c_j = np.array(other_center, dtype=float)
                normal = c_j - c_i
                offset = 0.5 * (float(np.dot(c_j, c_j)) - float(np.dot(c_i, c_i)))
                denom = max(float(np.linalg.norm(normal)), 1e-6)
                margins.append(abs(offset - float(np.dot(normal, point))) / denom)
            return min(margins) if margins else 0.0

        def _support_vector_ring(center: np.ndarray, *, visible: bool) -> Circle:
            """Return one support-vector highlight ring."""
            ring = Circle(
                radius=train_point_radius + 0.045,
                color=train_col,
                stroke_width=1.8,
            ).move_to(center)
            ring.set_fill(opacity=0.0)
            ring.set_z_index(5)
            if not visible:
                ring.set_stroke(opacity=0.0)
            return ring

        def make_support_vector_marks(
            fold_idx: int,
            blue_group: VGroup,
            green_group: VGroup,
            amber_group: VGroup,
        ) -> VGroup:
            """Highlight conceptual support vectors among the active training points."""
            centers = _class_centers(fold_idx)
            active_specs = [
                spec for spec in master_point_specs if spec["run_idx"] != fold_idx
            ]
            ranked_by_class = {
                class_name: sorted(
                    [spec for spec in active_specs if spec["class_name"] == class_name],
                    key=lambda spec: _decision_margin(spec, centers),
                )
                for class_name in point_class_order
            }
            selected_specs: list[dict[str, float | int | str]] = []
            for class_name in point_class_order:
                if ranked_by_class[class_name]:
                    selected_specs.append(ranked_by_class[class_name][0])
            remainder = sorted(
                [spec for spec in active_specs if spec not in selected_specs],
                key=lambda spec: _decision_margin(spec, centers),
            )
            if remainder:
                selected_specs.append(remainder[0])

            point_groups = {
                "blue": blue_group,
                "green": green_group,
                "amber": amber_group,
            }
            marks = VGroup()
            for spec in selected_specs[:4]:
                point_idx = int(spec["run_idx"]) * 4 + int(spec["replicate_idx"])
                point = point_groups[str(spec["class_name"])][point_idx]
                marks.add(_support_vector_ring(point.get_center(), visible=True))
            return marks

        def make_test_plot_state(
            fold_idx: int,
        ) -> tuple[VGroup, VGroup, VGroup, VGroup, VGroup]:
            """Build the current held-out plot state."""
            centers = _class_centers(fold_idx)
            blue_group, green_group, amber_group = _make_panel_points(
                test_ax,
                fold_idx,
                mode="test",
                active_opacity=test_active_opacity,
                inactive_opacity=test_inactive_opacity,
                radius=test_point_radius,
            )
            misclassified = fold_misclassified[fold_idx]
            error_lookup = {
                "blue": blue_group,
                "green": green_group,
                "amber": amber_group,
            }
            error_marks = VGroup()
            for class_name, idx in misclassified:
                point_idx = 4 * fold_idx + idx
                error_marks.add(
                    _error_mark(
                        error_lookup[class_name][point_idx].get_center(),
                        visible=True,
                    )
                )
            regions = _decision_regions(test_ax, centers)
            return regions, blue_group, green_group, amber_group, error_marks

        def make_train_plot_state(
            fold_idx: int,
        ) -> tuple[VGroup, VGroup, VGroup, VGroup, VGroup]:
            """Build the current training-plot state."""
            centers = _class_centers(fold_idx)
            blue_group, green_group, amber_group = _make_panel_points(
                train_ax,
                fold_idx,
                mode="train",
                active_opacity=train_active_opacity,
                inactive_opacity=train_inactive_opacity,
                radius=train_point_radius,
            )
            regions = _decision_regions(train_ax, centers)
            support_marks = make_support_vector_marks(
                fold_idx,
                blue_group,
                green_group,
                amber_group,
            )
            return regions, blue_group, green_group, amber_group, support_marks

        train_regions, train_blue_pts, train_green_pts, train_amber_pts, train_support_marks = make_train_plot_state(0)
        test_regions, test_blue_pts, test_green_pts, test_amber_pts, test_error_marks = make_test_plot_state(0)
        fold_label = Tex("held-out run 1 / 8", color=INK, font_size=20).move_to(
            np.array([plot_column_x, -2.42 + right_block_y_shift, 0.0])
        )
        def make_accuracy_display(n_filled: int) -> MathTex:
            """Build the current accuracy display."""
            if n_filled <= 0:
                tex = r"[\ ]"
            else:
                tex = r"[" + r", ".join(fold_accuracy_tex[:n_filled]) + r"]"
            return MathTex(tex, color=INK, font_size=20).next_to(fold_label, DOWN, buff=0.16)

        accuracy_display = make_accuracy_display(0)

        self.play(
            FadeIn(svm_label, shift=RIGHT * 0.06),
            FadeIn(merged_decoder_target, shift=RIGHT * 0.06),
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
            GrowArrow(test_flow_annotation[0]),
            FadeIn(test_flow_annotation[1], shift=RIGHT * 0.04),
            FadeIn(train_blue_pts),
            FadeIn(train_green_pts),
            FadeIn(train_amber_pts),
            FadeIn(train_support_marks),
            FadeIn(test_blue_pts),
            FadeIn(test_green_pts),
            FadeIn(test_amber_pts),
            FadeIn(test_error_marks),
            run_time=1.0,
        )
        self.wait(0.60)

        row_selection_train_stroke = 2.3
        row_selection_test_stroke = 3.4

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
            """Build the block box."""
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
            """Return the empty train box."""
            return _make_block_box(
                [matrix_rows[0]],
                color=train_col,
                stroke_width=0.0,
                fill_opacity=0.0,
            ).set_stroke(opacity=0.0)

        def _empty_train_label(box: Mobject) -> Tex:
            """Return the empty train label."""
            return Tex("train", color=train_col, font_size=16).move_to(
                np.array([label_col_x, box.get_center()[1], 0.0])
            ).set_opacity(0.0)

        def _set_tag(text: str, color: ManimColor, box: Mobject) -> VGroup:
            """Set up the tag."""
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
            """Build the train overlays for the current panel."""
            top_rows = matrix_rows[: 4 * fold_idx]
            bottom_rows = matrix_rows[4 * (fold_idx + 1) :]
            if top_rows:
                top_box = _make_block_box(
                    top_rows,
                    color=train_col,
                    stroke_width=row_selection_train_stroke,
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
                    stroke_width=row_selection_train_stroke,
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
                stroke_width=row_selection_test_stroke,
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
            *[
                Transform(target_rows[row_idx], split_focus_matrix_rows[row_idx].copy())
                for row_idx in range(32)
            ],
            FadeIn(current_train_overlays),
            Create(current_test_box),
            FadeIn(current_test_label),
            FadeIn(fold_label, shift=DOWN * 0.04),
            FadeIn(accuracy_display, shift=DOWN * 0.04),
            run_time=0.5,
        )
        self.wait(0.35)

        for fold_idx in range(8):
            new_fold_label = Tex(
                f"held-out run {fold_idx + 1} / 8",
                color=INK,
                font_size=20,
            ).move_to(fold_label.get_center())
            new_train_regions, new_train_blue_pts, new_train_green_pts, new_train_amber_pts, new_train_support_marks = make_train_plot_state(fold_idx)
            new_test_regions, new_test_blue_pts, new_test_green_pts, new_test_amber_pts, new_test_error_marks = make_test_plot_state(fold_idx)
            new_train_overlays = make_train_overlays(fold_idx)
            new_accuracy_display = make_accuracy_display(fold_idx + 1)

            if fold_idx == 0:
                self.play(
                    TransformMatchingTex(accuracy_display, new_accuracy_display),
                    Indicate(svm_label, color=INK, scale_factor=1.02),
                    run_time=0.45,
                )
                accuracy_display = new_accuracy_display
            else:
                self.play(
                    Transform(fold_label, new_fold_label),
                    Transform(train_regions, new_train_regions),
                    Transform(train_blue_pts, new_train_blue_pts),
                    Transform(train_green_pts, new_train_green_pts),
                    Transform(train_amber_pts, new_train_amber_pts),
                    Transform(train_support_marks, new_train_support_marks),
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
            *[
                Transform(target_rows[row_idx], initial_matrix_rows[row_idx].copy())
                for row_idx in range(32)
            ],
            FadeOut(fold_label),
            FadeOut(current_test_box),
            FadeOut(current_test_label),
            FadeOut(current_train_overlays),
            FadeOut(train_title),
            FadeOut(test_title),
            FadeOut(train_support_marks),
            FadeOut(train_x_label),
            FadeOut(train_y_label),
            FadeOut(test_x_label),
            FadeOut(test_y_label),
            FadeOut(test_flow_annotation[0]),
            FadeOut(test_flow_annotation[1]),
            FadeTransform(accuracy_display, final_acc),
            run_time=0.8,
        )

        locked_layout = self._build_results_handoff_frame()
        self.clear()
        self.add(locked_layout["static_frame"])
        self.wait(1.6)


# ══════════════════════════════════════════════════════════════════════════════
# Study2WithinSession2DecodingResults
# ══════════════════════════════════════════════════════════════════════════════


class Study2WithinSession2DecodingResults(Study2WithinSession2DecodingSetup):
    """
    Start from the final frame of within-session decoding, then transition to
    the results figure.

    Render:
        uv run manim scenes/study2.py Study2WithinSession2DecodingResults -ql
        uv run manim scenes/study2.py Study2WithinSession2DecodingResults -qh
    """

    _RESULTS_DECK_DEPTH = 5
    _RESULTS_DECK_OFFSET = np.array([-0.18, 0.12, 0.0])
    _RESULTS_DECK_SCALE_STEP = 0.04
    _RESULTS_DECK_MIN_OPACITY = 0.34
    _RESULTS_ICON_HEIGHT = 0.58
    _RESULTS_ICON_FRAME_OPACITY = 0.36
    _RESULTS_MATRIX_FRAME_OPACITY = 0.34
    _RESULTS_MATRIX_FILL_OPACITY = 0.92
    _RESULTS_STRIP_GAP = 0.30
    _RESULTS_CHAIN_GAP = 0.18
    _RESULTS_STRIP_TO_QUESTION_GAP = 0.34
    _RESULTS_BRAIN_HEIGHT = 1.08
    _RESULTS_DECODER_HEIGHT = 0.60
    _RESULTS_PROJECTION_SOURCE_INSET = 0.16
    _RESULTS_PROJECTION_TARGET_INSET = 0.03
    _RESULTS_LINK_ARROW_LENGTH = 0.24

    def _build_locked_setup_frame(self) -> dict[str, Mobject]:
        """Build the locked setup/results handoff frame."""
        title = self._make_overview_title(self._CV_TITLE).shift(UP * 0.18)

        matrix_x = -4.30
        row_centers = self._matrix_row_centers(matrix_x, y_shift=-0.18)
        matrix_rows = [
            self._make_cv_matrix_row(
                global_idx,
                row_centers[global_idx],
            )
            for global_idx in range(32)
        ]
        matrix_body = VGroup(*matrix_rows)
        run_labels = VGroup(*[
            Tex(f"run {run_idx + 1}", color=INK, font_size=16).next_to(
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
        train_col = self._SCHEMA_TRAIN_COLOR
        test_col = self._SCHEMA_TEST_COLOR
        class_one_col = _identity_color(CAT)
        class_two_col = _identity_color(OBS)
        class_three_col = _identity_color(VASE)

        summary_title = Tex(
            r"Sensory responses\\in Session 2",
            color=INK,
            font_size=24,
            tex_environment="center",
        ).next_to(VGroup(left_bracket, matrix_body, right_bracket), UP, buff=0.20)

        right_block_y_shift = -0.10
        svm_gap_y = right_block_y_shift + 0.02
        svm_label = VGroup(
            Tex("Linear", color=INK, font_size=20),
            Tex(r"\textbf{Support Vector Machine}", color=INK, font_size=20),
            Tex("Classifier", color=INK, font_size=20),
        ).arrange(DOWN, buff=0.05)
        question = self._make_cv_detail_callout(
            matrix_body,
            right_bracket,
            train_col,
            test_col,
        )

        plot_axis_config = {
            "color": _D_LGREY,
            "stroke_width": 1.4,
            "include_ticks": False,
            "include_tip": False,
        }
        plot_column_x = 4.12
        train_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([plot_column_x, 1.16 + right_block_y_shift, 0.0]))
        test_ax = Axes(
            x_range=[-2.6, 2.6, 1],
            y_range=[-1.6, 1.9, 1],
            x_length=2.70,
            y_length=1.58,
            axis_config=plot_axis_config,
        ).move_to(np.array([plot_column_x, -1.12 + right_block_y_shift, 0.0]))
        svm_column_x = 0.5 * (right_bracket.get_right()[0] + train_ax.get_left()[0]) + 0.12
        svm_label.move_to(np.array([svm_column_x, svm_gap_y, 0.0]))
        merged_decoder_target = self._make_schema_decoder(
            ORIGIN,
            self._SCHEMA_ITEM_HEIGHT
            * self._SCHEMA_DECODER_HEIGHT_RATIO
            * self._SCHEMA_ROW_SCALE
            * 0.52,
        ).next_to(svm_label, DOWN, buff=0.12)
        label_col_x = right_bracket.get_right()[0] + 0.58
        arrow_len = 0.77
        arrow_center_x = 0.5 * (label_col_x + 0.42 + svm_label.get_left()[0])
        data_arrow = Arrow(
            np.array([arrow_center_x - arrow_len / 2, svm_gap_y, 0.0]),
            np.array([arrow_center_x + arrow_len / 2, svm_gap_y, 0.0]),
            color=_D_MGREY,
            stroke_width=3.8,
            buff=0.02,
            tip_length=0.18,
        )
        train_frame = SurroundingRectangle(
            train_ax, color=train_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )
        test_frame = SurroundingRectangle(
            test_ax, color=test_col, stroke_width=2.0, buff=0.0, corner_radius=0.02,
        )

        class_examples = Group(*[
            Group(ImageMobject(path).scale_to_fit_height(0.50))
            for path in [CAT, OBS, VASE]
        ])
        for icon, col in zip(class_examples, [class_one_col, class_two_col, class_three_col]):
            frame = SurroundingRectangle(
                icon[0],
                color=col,
                stroke_width=2.1,
                buff=0.04,
                corner_radius=0.06,
            )
            icon.add(frame)
            icon[1].move_to(icon[0].get_center())
        class_examples.arrange(RIGHT, buff=0.15).move_to(
            np.array([plot_column_x, train_ax.get_top()[1] + 0.76, 0.0])
        )

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

        # Same Voronoi construction as the setup scene above; keep the
        # explanation local because this block is edited independently.
        def _decision_shift(fold_idx: int) -> tuple[float, float]:
            """Return the decision shift."""
            return 0.13 * np.sin(0.72 * fold_idx), 0.09 * np.cos(0.86 * fold_idx)

        def _class_centers(fold_idx: int) -> dict[str, tuple[float, float]]:
            """Return the class centers."""
            x_shift, y_shift = _decision_shift(fold_idx)
            return {
                "blue": (-1.25 + 0.28 * x_shift, -0.02 + 0.20 * y_shift),
                "green": (0.05 + 0.56 * x_shift, 0.96 + 1.05 * y_shift),
                "amber": (1.18 + 0.44 * x_shift, -0.06 + 0.22 * y_shift),
            }

        def _region_fill(col: str) -> ManimColor:
            """Return the region fill."""
            return interpolate_color(WHITE, ManimColor(col), 0.58)

        def _clip_polygon_halfplane(
            poly: list[np.ndarray], normal: np.ndarray, offset: float
        ) -> list[np.ndarray]:
            """Return the clip polygon halfplane."""
            if not poly:
                return []

            def inside(p: np.ndarray) -> bool:
                """Return whether the current point lies inside the active region."""
                return float(np.dot(normal, p)) <= offset + 1e-9

            def intersect(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
                """Return the intersection point for the current line segment."""
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
            """Return the linear region polygon."""
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
                # Intersect the current polygon with each pairwise Voronoi
                # half-plane to recover one class region.
                normal = c_j - c_i
                offset = 0.5 * (float(np.dot(c_j, c_j)) - float(np.dot(c_i, c_i)))
                poly = _clip_polygon_halfplane(poly, normal, offset)
                if len(poly) < 3:
                    return []
            return poly

        def _decision_regions(ax: Axes, centers: dict[str, tuple[float, float]]) -> VGroup:
            """Return the decision regions."""
            color_map = {"blue": class_one_col, "green": class_two_col, "amber": class_three_col}
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
            """Return the error mark."""
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
            """Build the current train-plot state."""
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
                Dot(train_ax.c2p(x, y), radius=0.055, color=class_two_col, fill_opacity=0.88)
                for x, y in green_pts
            ])
            amber_group = VGroup(*[
                Dot(train_ax.c2p(x, y), radius=0.055, color=class_three_col, fill_opacity=0.88)
                for x, y in amber_pts
            ])
            return _decision_regions(train_ax, centers), blue_group, green_group, amber_group

        def make_test_plot_state(
            fold_idx: int,
        ) -> tuple[VGroup, VGroup, VGroup, VGroup, VGroup]:
            """Build the current test-plot state."""
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
                Dot(test_ax.c2p(x, y), radius=0.070, color=class_two_col, fill_opacity=0.92)
                for x, y in green_pts
            ])
            amber_group = VGroup(*[
                Dot(test_ax.c2p(x, y), radius=0.070, color=class_three_col, fill_opacity=0.92)
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
            np.array([plot_column_x, -2.42 + right_block_y_shift, 0.0])
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
            merged_decoder_target,
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
            merged_decoder_target,
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
        """Build the held within-session results state without replaying the animation."""
        def make_small_icon(img_path: str, frame_col: str, opacity: float) -> Group:
            """Build one small icon for the current layout."""
            img = ImageMobject(img_path).scale_to_fit_height(self._RESULTS_ICON_HEIGHT)
            img.set_opacity(opacity)
            frame = SurroundingRectangle(
                img,
                color=frame_col,
                stroke_width=2.2,
                buff=0.04,
                corner_radius=0.06,
            )
            background = RoundedRectangle(
                width=frame.width,
                height=frame.height,
                corner_radius=0.06,
                stroke_width=0.0,
            ).move_to(frame.get_center())
            background.set_fill(WHITE, opacity=1.0)
            if opacity >= 0.99:
                frame.set_stroke(opacity=1.0)
            else:
                frame.set_stroke(opacity=self._RESULTS_ICON_FRAME_OPACITY * opacity)
            icon = Group(background, img, frame)
            icon.card_anchor = background
            return icon

        def make_pattern_card(
            frame_col: str,
            pattern_idx: int,
            opacity: float,
            target_width: float,
            target_height: float,
        ) -> VGroup:
            """Build one multivoxel pattern card for the example deck."""
            grid = self._make_grid(ORIGIN, frame_col, self._pattern_for_index(pattern_idx))
            grid.scale_to_fit_height(min(target_width, target_height) - 0.18)
            frame = SurroundingRectangle(
                grid,
                color=_D_MGREY,
                stroke_width=1.0,
                buff=0.08,
                corner_radius=0.04,
            )
            frame.stretch_to_fit_width(target_width)
            frame.stretch_to_fit_height(target_height)
            frame.set_fill(WHITE, opacity=self._RESULTS_MATRIX_FILL_OPACITY)
            frame.set_stroke(opacity=self._RESULTS_MATRIX_FRAME_OPACITY * opacity)
            grid.move_to(frame.get_center())
            grid.set_opacity(opacity)
            return VGroup(frame, grid)

        def make_results_brain(brain_left_x: float, center_y: float) -> Group:
            """Build the viewing-brain asset for the strip from its own bounds."""
            return Group(
                _make_v1v2v3_viewing_brain(
                    brain_left_x=brain_left_x,
                    brain_center_y=center_y,
                    target_brain_height=self._RESULTS_BRAIN_HEIGHT,
                )
            )

        def make_results_link_arrow(source_right_x: float, y: float) -> Arrow:
            """Build one detached horizontal connector for the results strip."""
            return Arrow(
                np.array([
                    source_right_x + self._RESULTS_CHAIN_GAP,
                    y,
                    0.0,
                ]),
                np.array([
                    source_right_x + self._RESULTS_CHAIN_GAP + self._RESULTS_LINK_ARROW_LENGTH,
                    y,
                    0.0,
                ]),
                color=_D_MGREY,
                stroke_width=1.6,
                buff=0.0,
                tip_length=0.08,
            )

        def place_strip_item(item: Mobject, left_x: float, center_y: float) -> Mobject:
            """Place one strip item by its full bounds on a shared centerline."""
            item.shift(
                np.array([
                    left_x - item.get_left()[0],
                    center_y - item.get_center()[1],
                    0.0,
                ])
            )
            return item

        def make_deck(specs, builder):
            """Build one diagonal deck and return the front-most item anchor."""
            active_specs = specs[-self._RESULTS_DECK_DEPTH :]
            deck = Group()
            depth_count = len(active_specs)
            for spec_idx, spec in enumerate(active_specs):
                layer_idx = depth_count - spec_idx - 1
                if depth_count == 1:
                    layer_opacity = 1.0
                else:
                    layer_opacity = self._RESULTS_DECK_MIN_OPACITY + (
                        1.0 - self._RESULTS_DECK_MIN_OPACITY
                    ) * (1.0 - layer_idx / (depth_count - 1))
                item = builder(*spec, layer_opacity)
                item.scale(1.0 - self._RESULTS_DECK_SCALE_STEP * layer_idx)
                item.shift(self._RESULTS_DECK_OFFSET * layer_idx)
                deck.add(item)
            return deck, deck[-1]

        def make_results_plot() -> Group:
            """Build the current results plot."""
            svg = (
                SVGMobject(str(_STUDY2_ASSET_DIR / "study2_results.svg"))
                .scale_to_fit_height(3.64)
                .move_to(np.array([3.20, 0.02, 0.0]))
            )

            for submob in svg.submobjects:
                if (
                    _study2_color_hex(submob.get_fill_color()) == "#FFFFFF"
                    and _study2_color_hex(submob.get_stroke_color()) == "#FFFFFF"
                    and submob.width > 0.9 * svg.width
                    and submob.height > 0.9 * svg.height
                ):
                    submob.set_fill(opacity=0.0)
                    submob.set_stroke(opacity=0.0)
                    break

            plot_frame = VGroup(*[
                submob
                for submob in svg.submobjects
                if _study2_color_hex(submob.get_stroke_color()) == "#262626"
                and len(submob.get_all_points()) == 4
            ])
            plot_top = plot_frame.get_top()[1]
            plot_bottom = plot_frame.get_bottom()[1]
            plot_left = plot_frame.get_left()[0]
            plot_right = plot_frame.get_right()[0]
            x_label_template = VGroup(*[
                submob
                for submob in svg.submobjects
                if (
                    _study2_color_hex(submob.get_fill_color()) == "#000000"
                    and submob.get_center()[1] < plot_bottom - 0.02
                    and plot_left <= submob.get_center()[0] <= plot_right
                )
            ])
            x_label_template.set_opacity(0.0)

            chance_template = max(
                [
                    submob
                    for submob in svg.submobjects
                    if (
                        _study2_color_hex(submob.get_stroke_color()) == "#808080"
                        and len(submob.get_all_points()) == 4
                    )
                ],
                key=lambda mob: mob.width,
            )
            chance_template.set_opacity(0.0)

            scatter_points = [
                submob
                for submob in svg.submobjects
                if (
                    _study2_color_hex(submob.get_fill_color()) == "#000000"
                    and 0.1 < submob.get_fill_opacity() < 0.5
                    and len(submob.get_all_points()) == 32
                    and plot_bottom <= submob.get_center()[1] <= plot_top
                )
            ]
            for dot in scatter_points:
                dot.scale(0.88, about_point=dot.get_center())
                dot.set_fill(color="#6A6A6A", opacity=0.34)
                dot.set_stroke(opacity=0.0)

            summary_fill = next(
                submob
                for submob in svg.submobjects
                if (
                    _study2_color_hex(submob.get_fill_color()) == "#000000"
                    and submob.get_fill_opacity() > 0.9
                    and len(submob.get_all_points()) <= 20
                    and plot_bottom <= submob.get_center()[1] <= plot_top
                )
            )
            summary_stroke = next(
                submob
                for submob in svg.submobjects
                if (
                    _study2_color_hex(submob.get_stroke_color()) == "#000000"
                    and submob.get_fill_opacity() == 0.0
                    and len(submob.get_all_points()) <= 20
                    and plot_bottom <= submob.get_center()[1] <= plot_top
                )
            )
            summary_fill.scale(0.92, about_point=summary_fill.get_center())
            summary_stroke.scale(0.92, about_point=summary_stroke.get_center())
            summary_fill.set_fill(color=BLACK, opacity=0.94)
            summary_fill.set_stroke(color=BLACK, width=1.2, opacity=0.94)
            summary_stroke.set_stroke(color=BLACK, width=4.0, opacity=0.94)

            significance = [
                submob
                for submob in svg.submobjects
                if (
                    _study2_color_hex(submob.get_fill_color()) == "#000000"
                    and submob.get_fill_opacity() > 0.9
                    and submob.get_center()[1] > plot_top
                )
            ]
            for marker in significance:
                marker.scale(0.94, about_point=marker.get_center())
                marker.set_fill(color=BLACK, opacity=0.82)
                marker.set_stroke(opacity=0.0)

            plot_frame.set_stroke(color="#2F2F2F", width=2.3, opacity=0.92)

            chance_y = chance_template.get_center()[1]
            chance_line = DashedLine(
                np.array([plot_left, chance_y, 0.0]),
                np.array([plot_right, chance_y, 0.0]),
                color="#9A9A9A",
                stroke_width=1.8,
                dash_length=0.10,
                dashed_ratio=0.58,
            )
            chance_label_fs = 16
            chance_label = VGroup(
                Tex(
                    "Chance",
                    color=BLACK,
                    font_size=chance_label_fs,
                ),
                MathTex(
                    r"1.6\%",
                    color=BLACK,
                    font_size=chance_label_fs,
                ),
            ).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)
            chance_label.next_to(chance_line, UP, buff=0.10).align_to(chance_line, RIGHT).shift(LEFT * 0.24 + UP * 0.01)
            x_label = MathTex(r"S_2 \rightarrow S_2", color=BLACK)
            x_label.scale_to_fit_width(x_label_template.width * 0.92)
            x_label.move_to(x_label_template.get_center() + DOWN * 0.01)

            return Group(svg, chance_line, chance_label, x_label)

        question = Tex(
            "How well can the classifier\\\\discriminate between object-scene\\\\representations during perception?",
            color=INK,
            font_size=26,
            tex_environment="center",
        ).move_to(np.array([-3.15, 1.42, 0.0]))

        example_specs = [
            (SOFA, _identity_color(SOFA), 1),
            (PINE, _identity_color(PINE), 2),
            (VASE, _identity_color(VASE), 4),
            (BRI, _identity_color(BRI), 5),
            (CAT, _identity_color(CAT), 3),
        ]
        image_deck, image_front = make_deck(
            example_specs,
            lambda img_path, frame_col, pattern_idx, opacity: make_small_icon(
                img_path,
                frame_col,
                opacity,
            ),
        )
        image_card_width = image_front.width
        image_card_height = image_front.height
        pattern_deck, pattern_front = make_deck(
            example_specs,
            lambda img_path, frame_col, pattern_idx, opacity: make_pattern_card(
                frame_col,
                pattern_idx,
                opacity,
                image_card_width,
                image_card_height,
            ),
        )
        image_deck.shift(-image_deck.get_center())
        strip_center_y = image_deck.get_center()[1]
        strip_gap = self._RESULTS_STRIP_GAP
        chain_gap = self._RESULTS_CHAIN_GAP

        brain_left_x = image_deck.get_right()[0] + strip_gap
        brain_group = make_results_brain(brain_left_x, strip_center_y)

        brain_to_pattern_arrow = make_results_link_arrow(
            brain_group.get_right()[0],
            strip_center_y,
        )

        pattern_left_x = brain_to_pattern_arrow.get_end()[0] + chain_gap
        place_strip_item(pattern_deck, pattern_left_x, strip_center_y)

        decoder_icon = (
            SVGMobject(str(_SVM_CLASSIFIER_GREYSCALE_SVG_PATH))
            .scale_to_fit_height(self._RESULTS_DECODER_HEIGHT)
        )
        pattern_to_decoder_arrow = make_results_link_arrow(
            pattern_deck.get_right()[0],
            strip_center_y,
        )
        decoder_left_x = pattern_to_decoder_arrow.get_end()[0] + chain_gap
        place_strip_item(decoder_icon, decoder_left_x, strip_center_y)
        strip_group = Group(
            image_deck,
            brain_group,
            brain_to_pattern_arrow,
            pattern_deck,
            pattern_to_decoder_arrow,
            decoder_icon,
        )
        strip_group.next_to(question, DOWN, buff=self._RESULTS_STRIP_TO_QUESTION_GAP)
        example_column = Group(image_deck, pattern_deck)

        results_plot = make_results_plot()

        takeaway = Tex(
            r"Robust \textbf{above chance decoding}\\of sensory representations",
            color=INK,
            font_size=30,
            tex_environment="center",
        ).move_to(np.array([-3.15, -1.90, 0.0]))

        frame = Group(
            question,
            example_column,
            brain_group,
            brain_to_pattern_arrow,
            pattern_to_decoder_arrow,
            decoder_icon,
            results_plot,
            takeaway,
        )
        return {
            "frame": frame,
            "question": question,
            "example_column": example_column,
            "brain_group": brain_group,
            "brain_to_pattern_arrow": brain_to_pattern_arrow,
            "pattern_to_decoder_arrow": pattern_to_decoder_arrow,
            "decoder_icon": decoder_icon,
            "results_plot": results_plot,
            "takeaway": takeaway,
        }

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        layout = self._build_results_handoff_frame()
        static_frame = layout["static_frame"]
        fade_group = layout["fade_group"]
        question = layout["question"]

        end_layout = self._build_results_end_static()
        question_target = end_layout["question"]
        example_column = end_layout["example_column"]
        brain_group = end_layout["brain_group"]
        brain_to_pattern_arrow = end_layout["brain_to_pattern_arrow"]
        pattern_to_decoder_arrow = end_layout["pattern_to_decoder_arrow"]
        decoder_icon = end_layout["decoder_icon"]
        results_plot = end_layout["results_plot"]
        takeaway = end_layout["takeaway"]

        self.add(static_frame)
        self.wait(0.25)

        self.play(
            FadeOut(fade_group),
            Transform(question, question_target),
            run_time=0.9,
        )
        self.play(
            FadeIn(example_column, shift=UP * 0.08),
            FadeIn(brain_group, shift=RIGHT * 0.06),
            FadeIn(brain_to_pattern_arrow, shift=RIGHT * 0.05),
            FadeIn(pattern_to_decoder_arrow, shift=RIGHT * 0.05),
            FadeIn(decoder_icon, shift=RIGHT * 0.08),
            run_time=0.65,
        )
        self.wait(0.7)

        self.play(
            FadeIn(results_plot, shift=RIGHT * 0.18),
            run_time=0.85,
        )
        self.play(FadeIn(takeaway, shift=UP * 0.10), run_time=0.65)
        locked_layout = self._build_cross_session_handoff_frame()
        locked_frame = locked_layout["frame"]
        self.remove(
            question,
            example_column,
            brain_group,
            brain_to_pattern_arrow,
            pattern_to_decoder_arrow,
            decoder_icon,
            results_plot,
            takeaway,
        )
        self.add(locked_frame)
        self.wait(1.5)


# ══════════════════════════════════════════════════════════════════════════════
# Study2CrossSessionDecodingSetup
# ══════════════════════════════════════════════════════════════════════════════


class Study2CrossSessionDecodingSetup(Study2WithinSession2DecodingResults):
    """
    Build a conceptual cross-session decoding setup that shows Session 2
    stimulation providing the training patterns, then tests the fixed decoder
    on Session 1 stimulation and delay-period patterns.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecodingSetup -ql
        uv run manim scenes/study2.py Study2CrossSessionDecodingSetup -qh
    """

    _S2_ROW_SCALE = 0.58
    _S2_ROW_CENTER = np.array([-3.55, 1.72, 0.0])
    _S1_ROW_SCALE = 0.58
    _S1_ROW_CENTER = np.array([3.55, 1.72, 0.0])
    _TRAIN_PANEL_CENTER = np.array([-4.05, -1.20, 0.0])
    _PERCEPTION_PANEL_CENTER = np.array([1.15, -1.20, 0.0])
    _DELAY_PANEL_CENTER = np.array([4.75, -1.20, 0.0])
    _S1_STIM_ACCENT = _CROSSSESSION_STIM_SCATTER
    _TARGET_TEST = _S1_STIM_ACCENT
    _DELAY_TEST = _CROSSSESSION_DELAY_SCATTER
    _TRAIN_ACCENT = Study2WithinSession2DecodingSetup._SCHEMA_TRAIN_COLOR
    _PERCEPTION_ACCENT = Study2WithinSession2DecodingSetup._SCHEMA_TEST_COLOR
    _DELAY_ACCENT = Study2WithinSession2DecodingSetup._SCHEMA_TEST_COLOR
    _STIMULATION_LABEL_COLOR = _CROSSSESSION_STIM_SCATTER
    _DELAY_LABEL_COLOR = _CROSSSESSION_DELAY_SCATTER
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
        """Build one session row for the cross-session decoding layout."""
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
        """Return the y-values used for the delay row in the cross-session layout."""
        base = self._row_values(base_idx, exemplar_idx)
        rolled = np.roll(base, 1 + ((base_idx + exemplar_idx) % 4))
        ripple = 0.035 * np.cos(
            np.arange(base.size) * 0.85 + 0.55 * base_idx + 0.65 * exemplar_idx
        )
        return np.clip(0.62 * base + 0.38 * rolled + ripple, 0.10, 0.90)

    def _ordered_examples(self, order: list[int]) -> list[tuple[int, int]]:
        """Return the example stimuli in the presentation order used by the layout."""
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
        content_color: str | None = None,
        cell_w: float = 0.104,
        cell_h: float = 0.104,
        gap: float = 0.026,
        row_gap: float = 0.048,
        role_font_size: int = 19,
        content_font_size: int = 19,
        content_buff: float = 0.18,
    ) -> VGroup:
        """Build one conceptual train-test matrix panel."""
        rows = VGroup(*[
            _make_feature_row(
                values,
                color=self._MATRIX_DIVERGING_HIGH_COLOR,
                cell_w=cell_w,
                cell_h=cell_h,
                gap=gap,
                low_color=self._MATRIX_DIVERGING_LOW_COLOR,
                mid_color=self._MATRIX_DIVERGING_MID_COLOR,
                high_color=self._MATRIX_DIVERGING_HIGH_COLOR,
                stroke_color=self._MATRIX_STROKE_COLOR,
                stroke_width=0.65,
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
            color=content_color if content_color is not None else accent_color,
            font_size=content_font_size,
            tex_environment="center",
        ).next_to(pattern_group, DOWN, buff=content_buff)
        return VGroup(role_label, pattern_group, content_label)

    def _make_panel_focus_frame(self, target: Mobject) -> VMobject:
        """Build a focus frame around one conceptual matrix panel."""
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
        """Build the decode arrow used in the cross-session layout."""
        return CurvedArrow(
            source.get_right() + UP * 0.20 + RIGHT * 0.02,
            target.get_left() + UP * 0.20 + LEFT * 0.02,
            angle=angle,
            color=_D_MGREY,
            stroke_width=1.8,
            tip_length=0.14,
        )

    def _build_cross_session_setup_handoff_frame(self) -> dict[str, object]:
        """Build the locked cross-session setup state shared with Results A."""
        layout = self._build_cross_session_layout()
        for mob in layout["s2_dim_mobs"]:
            mob.set_opacity(0.18)
        for mob in layout["dim_right_mobs"]:
            mob.set_opacity(0.18)

        train_body = layout["train_panel"][self._PANEL_BODY_IDX]
        delay_body = layout["delay_panel"][self._PANEL_BODY_IDX]
        train_focus_frame = self._make_panel_focus_frame(train_body)
        delay_focus_frame = self._make_panel_focus_frame(delay_body)
        delay_decode_arrow = self._make_decode_arrow(train_body, delay_body, angle=-0.34)

        frame = Group(
            layout["slide_title"],
            layout["s2_title"],
            layout["s2_row_group"],
            layout["s1_title"],
            layout["s1_row_group"],
            layout["train_panel"][self._PANEL_BODY_IDX],
            layout["train_panel"][self._PANEL_CONTENT_IDX],
            layout["train_panel"][self._PANEL_ROLE_IDX],
            train_focus_frame,
            layout["perception_panel"][self._PANEL_BODY_IDX],
            layout["perception_panel"][self._PANEL_CONTENT_IDX],
            layout["delay_panel"][self._PANEL_BODY_IDX],
            layout["delay_panel"][self._PANEL_CONTENT_IDX],
            layout["delay_panel"][self._PANEL_ROLE_IDX],
            delay_focus_frame,
            delay_decode_arrow,
        )
        return {
            "layout": layout,
            "train_focus_frame": train_focus_frame,
            "delay_focus_frame": delay_focus_frame,
            "delay_decode_arrow": delay_decode_arrow,
            "frame": frame,
        }

    def _build_cross_session_layout(self) -> dict[str, object]:
        """Build the reusable cross-session decoding layout and its parts."""
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
            content_color=self._STIMULATION_LABEL_COLOR,
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
            content_color=self._STIMULATION_LABEL_COLOR,
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
            content_color=self._DELAY_LABEL_COLOR,
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
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        handoff = self._build_cross_session_setup_handoff_frame()
        layout = handoff["layout"]
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

        train_focus_frame = handoff["train_focus_frame"]
        stim_focus_frame = self._make_panel_focus_frame(perception_body)
        delay_focus_frame = handoff["delay_focus_frame"]
        stim_decode_arrow = self._make_decode_arrow(train_body, perception_body, angle=-0.55)
        delay_decode_arrow = handoff["delay_decode_arrow"]

        previous_scene = self._build_cross_session_handoff_frame()
        previous_frame = previous_scene["frame"]
        self.add(previous_frame)
        self.wait(0.25)

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
        self.clear()
        self.add(handoff["frame"])
        self.wait(1.2)


class Study2CrossSessionDecodingResultsCombined(Study2CrossSessionDecodingSetup):
    """
    Start from the last frame of cross-session decoding.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsCombined -ql
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsCombined -qh
    """

    _RESULTS_GLM = str(_STUDY2_ASSET_DIR / "study2_results_ses02ses01glm.png")
    _RESULTS_TIMERES = str(_STUDY2_ASSET_DIR / "study2_results_ses02ses01timeres.png")
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
        """Build the compact results matrix reused in summary layouts."""
        rows = VGroup(*[
            _make_feature_row(
                values[row_idx * 3 : (row_idx + 1) * 3],
                color=self._MATRIX_DIVERGING_HIGH_COLOR,
                cell_w=0.12,
                cell_h=0.12,
                gap=0.024,
                low_color=self._MATRIX_DIVERGING_LOW_COLOR,
                mid_color=self._MATRIX_DIVERGING_MID_COLOR,
                high_color=self._MATRIX_DIVERGING_HIGH_COLOR,
                stroke_color=self._MATRIX_STROKE_COLOR,
                stroke_width=0.65,
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
        """Position the compact results matrix relative to the current summary layout."""
        rows, frame, label = matrix
        rows.move_to(center)
        frame.move_to(rows)
        label.next_to(frame, label_direction, buff=0.04)

    def _make_cross_session_takeaway(
        self,
        *,
        center: np.ndarray,
        font_size: int = 22,
    ) -> VGroup:
        """Build the takeaway text for the cross-session results summary."""
        test_s1_purple = self._S1_STIM_ACCENT
        takeaway_line_1 = Tex(
            r"{{Sensory-trained}} classifiers can decode stimulus identity",
            color=INK,
            font_size=font_size,
        )
        takeaway_line_1.set_color_by_tex("Sensory-trained", self._S1_STIM_ACCENT)

        takeaway_line_2 = Tex(
            r"from the {{stimulation period}}, but do not generalise throughout the {{delay phase}}",
            color=INK,
            font_size=font_size,
        )
        takeaway_line_2.set_color_by_tex("stimulation period", test_s1_purple)
        takeaway_line_2.set_color_by_tex("delay phase", self._DELAY_TEST)

        takeaway = VGroup(
            takeaway_line_1,
            takeaway_line_2,
        ).arrange(DOWN, buff=0.10, center=True)
        takeaway.move_to(center)
        return takeaway

    def _make_partial_path(self, template: VMobject, alpha: float) -> VMobject:
        """Build the partial path."""
        partial = template.copy()
        alpha = float(np.clip(alpha, 0.0, 1.0))
        if alpha <= 1e-4:
            # Keep the geometry pinned to the true curve start so callers that
            # query the partial endpoint never momentarily see the far end.
            partial.pointwise_become_partial(template, 0.0, 1e-4)
            partial.set_stroke(opacity=0.0)
            partial.set_fill(opacity=0.0)
            return partial
        partial.pointwise_become_partial(template, 0.0, alpha)
        return partial

    def _trace_step_proportions(self, trace_template: VMobject, step_count: int) -> np.ndarray:
        """Animate the step proportions."""
        sample_props = np.linspace(0.0, 1.0, 1200)
        sample_xs = np.array([
            trace_template.point_from_proportion(float(prop))[0]
            for prop in sample_props
        ])
        # The curve parameter is not linear in x, so sample densely once and
        # snap each evenly spaced x target to the nearest path proportion.
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
        """Return the GLM SVG hex."""
        return _study2_color_hex(color)

    def _glm_svg_plot_frame(self, svg: SVGMobject) -> VGroup:
        """Return the GLM SVG plot frame."""
        # The imported SVG contains many stroked objects. The outer frame is the
        # pair of longest horizontal lines plus the pair of longest verticals.
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
        """Return the GLM SVG group."""
        frame_center_x = self._glm_svg_plot_frame(svg).get_center()[0]
        color_hex = color_hex.upper()
        # The cross-session result SVG is a two-panel figure, so split matching
        # marks by panel side after filtering by stroke/fill color.
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
        """Return the GLM SVG scatter points."""
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
        """Return the GLM SVG chance line."""
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
        """Return the GLM SVG significance marker."""
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
        """Return the GLM SVG hide color groups."""
        for submob in svg.submobjects:
            if (
                self._glm_svg_hex(submob.get_fill_color()) in {
                    _CROSSSESSION_STIM_SCATTER_HEX,
                    _CROSSSESSION_DELAY_SCATTER_HEX,
                }
                or self._glm_svg_hex(submob.get_stroke_color()) in {
                    _CROSSSESSION_STIM_SCATTER_HEX,
                    _CROSSSESSION_DELAY_SCATTER_HEX,
                }
            ):
                submob.set_opacity(0)

    def _glm_svg_bottom_label(self, plot_frame: VGroup, x: float, tex: str) -> MathTex:
        """Return the GLM SVG bottom label."""
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
        """Position the plot mobject."""
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
        """Build the results context."""
        self.camera.background_color = BG
        handoff = self._build_cross_session_setup_handoff_frame()
        layout = handoff["layout"]
        test_s1_purple = self._S1_STIM_ACCENT

        train_panel = layout["train_panel"]
        perception_panel = layout["perception_panel"]
        delay_panel = layout["delay_panel"]
        train_body = train_panel[self._PANEL_BODY_IDX]
        delay_body = delay_panel[self._PANEL_BODY_IDX]
        train_focus_frame = handoff["train_focus_frame"]
        delay_focus_frame = handoff["delay_focus_frame"]
        delay_decode_arrow = handoff["delay_decode_arrow"]

        plot_height = 3.55
        left_panel_center = np.array([-3.95, -1.15, 0.0])
        left_panel_shift_x = abs(left_panel_center[0]) * 0.10
        left_panel_center[0] += left_panel_shift_x
        glm_plot_center = left_panel_center.copy()
        glm_plot_center[0] -= abs(left_panel_center[0]) * 0.05
        suptitle_y = 3.70
        glm_svg = (
            SVGMobject(str(Path(self._RESULTS_GLM).with_suffix(".svg")))
            .scale_to_fit_height(plot_height)
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
        glm_left_group = self._glm_svg_group(glm_svg, _CROSSSESSION_STIM_SCATTER_HEX, "left")
        glm_right_group = self._glm_svg_group(glm_svg, _CROSSSESSION_DELAY_SCATTER_HEX, "right")
        glm_left_significance = self._glm_svg_significance_marker(
            glm_svg,
            _CROSSSESSION_STIM_SCATTER_HEX,
            "left",
        )
        glm_right_significance = self._glm_svg_significance_marker(
            glm_svg,
            _CROSSSESSION_DELAY_SCATTER_HEX,
            "right",
        )
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
        glm_takeaway = self._make_cross_session_takeaway(
            center=np.array([0.0, -3.42, 0.0]),
            font_size=22,
        )

        glm_row_shift_down = plot_height * 0.10
        glm_bottom_y = 1.86 - glm_row_shift_down
        glm_train_y = glm_bottom_y + 1.04
        frame_width_final = 1.5
        frame_opacity_final = 0.48
        frame_width_emphasis = 3.0

        glm_train = self._make_small_results_matrix(
            self._MINI_TRAIN_VALUES,
            self._S1_STIM_ACCENT,
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
            self._DELAY_TEST,
            r"$D_1$",
            label_direction=DOWN,
        )
        glm_train_explainer = VGroup(
            Tex("Train on", color=INK, font_size=17),
            Tex("Stimulation", color=self._S1_STIM_ACCENT, font_size=17),
            Tex("Session 2", color=self._S1_STIM_ACCENT, font_size=17),
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        glm_stim_explainer = VGroup(
            Tex("Test on", color=INK, font_size=17),
            Tex("Stimulation", color=test_s1_purple, font_size=17),
            Tex("Session 1", color=test_s1_purple, font_size=17),
        ).arrange(DOWN, buff=0.03, aligned_edge=RIGHT)
        glm_delay_explainer = VGroup(
            Tex("Test on", color=INK, font_size=17),
            Tex("Delay", color=self._DELAY_TEST, font_size=17),
            Tex("Session 1", color=self._DELAY_TEST, font_size=17),
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
            .scale_to_fit_height(plot_height)
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
        timeres_hrf_rectangles = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in [67, 68, 69]]),
            timeres_source_frame,
            timeres_frame,
        )

        def make_diagonal_striped_rect(template: Mobject) -> VGroup:
            """Build a diagonally striped highlight rectangle."""
            x0, x1 = template.get_left()[0], template.get_right()[0]
            y0, y1 = template.get_bottom()[1], template.get_top()[1]
            background = Rectangle(
                width=template.width,
                height=template.height,
                stroke_width=0.0,
            ).set_fill(WHITE, opacity=1.0).move_to(template)

            def stripe_segment(diagonal_offset: float) -> tuple[np.ndarray, np.ndarray] | None:
                """Build one diagonal stripe segment."""
                candidates = [
                    np.array([x0, x0 + diagonal_offset, 0.0]),
                    np.array([x1, x1 + diagonal_offset, 0.0]),
                    np.array([y0 - diagonal_offset, y0, 0.0]),
                    np.array([y1 - diagonal_offset, y1, 0.0]),
                ]
                points: list[np.ndarray] = []
                for point in candidates:
                    if x0 - 1e-6 <= point[0] <= x1 + 1e-6 and y0 - 1e-6 <= point[1] <= y1 + 1e-6:
                        if not any(np.linalg.norm(point - other) < 1e-6 for other in points):
                            points.append(point)
                if len(points) < 2:
                    return None
                max_pair = None
                max_distance = -1.0
                for idx_a in range(len(points)):
                    for idx_b in range(idx_a + 1, len(points)):
                        distance = np.linalg.norm(points[idx_a] - points[idx_b])
                        if distance > max_distance:
                            max_distance = distance
                            max_pair = (points[idx_a], points[idx_b])
                return max_pair

            stripe_spacing = template.height * 0.42
            stripe_group = VGroup()
            diagonal_min = y0 - x1
            diagonal_max = y1 - x0
            for diagonal_offset in np.arange(
                diagonal_min - stripe_spacing,
                diagonal_max + 2 * stripe_spacing,
                stripe_spacing,
            ):
                segment = stripe_segment(float(diagonal_offset))
                if segment is None:
                    continue
                stripe_group.add(Line(
                    segment[0],
                    segment[1],
                    color=self._S1_STIM_ACCENT,
                    stroke_width=2.2,
                    stroke_opacity=0.95,
                ))

            border = Rectangle(
                width=template.width,
                height=template.height,
                stroke_color=self._S1_STIM_ACCENT,
                stroke_width=max(template.get_stroke_width(), 0.8),
            ).set_fill(opacity=0.0).move_to(template)
            border.set_stroke(opacity=0.20)
            return VGroup(background, stripe_group, border)

        timeres_hrf_rectangles = VGroup(
            timeres_hrf_rectangles[0],
            timeres_hrf_rectangles[1],
            make_diagonal_striped_rect(timeres_hrf_rectangles[2]),
        )
        timeres_hrf_lines = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in [70, 71, 72]]),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_trace_start_x = timeres_trace_template.get_left()[0]
        for line in timeres_hrf_lines:
            line.shift(RIGHT * (timeres_trace_start_x - line.get_left()[0]))
        # Reuse vector glyphs from the source plots so the right panel matches
        # the left panel's line weight and label styling exactly.
        timeres_x_label_template = self._remap_plot_mobject(
            VGroup(*[timeres_svg[idx].copy() for idx in range(13, 22)]),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_y_label = self._remap_plot_mobject(
            glm_accuracy_label,
            glm_plot_frame,
            timeres_frame,
        )
        timeres_x_label = Tex("Test time (s)", color=INK)
        # The rotated SVG y-label's width corresponds to its actual font height.
        timeres_x_label.scale_to_fit_height(timeres_y_label.width)
        timeres_x_label.move_to(timeres_x_label_template.get_center())
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

        timeres_trace_xs = np.linspace(
            timeres_trace_template.get_left()[0],
            timeres_trace_template.get_right()[0],
            25,
        )
        trace_sample_props = np.linspace(0.0, 1.0, 2400)
        trace_sample_points = np.array([
            timeres_trace_template.point_from_proportion(float(prop))
            for prop in trace_sample_props
        ])
        trace_sort_order = np.argsort(trace_sample_points[:, 0])
        trace_sample_points = trace_sample_points[trace_sort_order]
        trace_sample_props = trace_sample_props[trace_sort_order]
        trace_sample_xs = trace_sample_points[:, 0]
        trace_sample_ys = trace_sample_points[:, 1]
        trace_unique_xs, trace_unique_idx = np.unique(trace_sample_xs, return_index=True)
        trace_unique_props = trace_sample_props[trace_unique_idx]
        trace_unique_ys = trace_sample_ys[trace_unique_idx]
        timeres_strip_y = timeres_frame.get_top()[1] + 0.76
        timeres_bin_spacing = timeres_trace_xs[1] - timeres_trace_xs[0]
        timeres_bin_width = timeres_bin_spacing * 0.74
        timeres_bin_height = 0.23

        schematic_train = self._make_small_results_matrix(
            self._MINI_TRAIN_VALUES,
            self._S1_STIM_ACCENT,
            r"$S_2$",
            label_direction=UP,
        )
        timeres_train_explainer = VGroup(
            Tex("Train on", color=INK, font_size=17),
            Tex("Stimulation", color=self._S1_STIM_ACCENT, font_size=17),
            Tex("Session 2", color=self._S1_STIM_ACCENT, font_size=17),
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
        timeres_total_time = 19.2
        design_track_height = timeres_bin_height + 0.03
        design_fill_height = design_track_height - 0.06
        design_start_x = timeres_trace_template.get_left()[0]
        design_end_x = timeres_trace_template.get_right()[0]
        design_drop = DOWN * 0.26
        event_boundary_times = [2.0, 10.0, 12.5, 14.5]
        design_center = np.array([
            (design_start_x + design_end_x) / 2,
            timeres_strip_y,
            0.0,
        ])

        def time_to_x(time_s: float) -> float:
            """Map a time index onto the x-axis position."""
            return float(interpolate(
                design_start_x,
                design_end_x,
                np.clip(time_s / timeres_total_time, 0.0, 1.0),
            ))

        def make_design_icon(
            img_path: str | None,
            start_s: float,
            end_s: float,
            *,
            resp: bool = False,
        ) -> Group:
            """Build one compact design icon."""
            icon = _box(img_path, resp=resp)
            icon.scale_to_fit_height(design_fill_height * 0.78)
            max_width = max(time_to_x(end_s) - time_to_x(start_s) - 0.07, 0.08)
            if icon.width > max_width:
                icon.scale_to_fit_width(max_width)
            return icon

        def make_design_phase(
            start_s: float,
            end_s: float,
            fill_color: str,
            fill_opacity: float,
            icon: Mobject | None,
        ) -> Group:
            """Build one compact design phase card."""
            phase_fill = Rectangle(
                width=time_to_x(end_s) - time_to_x(start_s),
                height=design_fill_height,
                stroke_width=0.0,
            ).set_fill(fill_color, opacity=fill_opacity)
            phase_fill.move_to(np.array([
                (time_to_x(start_s) + time_to_x(end_s)) / 2,
                timeres_strip_y,
                0.0,
            ]))
            parts: list[Mobject] = [phase_fill]
            if icon is not None:
                phase_icon = icon.copy().move_to(phase_fill)
                parts.append(phase_icon)
            return Group(*parts)

        design_frame = RoundedRectangle(
            width=timeres_bin_width * 1.05,
            height=design_track_height,
            corner_radius=0.05,
            stroke_color=GREY,
            stroke_width=1.3,
        ).set_fill(WHITE, opacity=0.0).move_to(design_center)
        design_frame_target = RoundedRectangle(
            width=design_end_x - design_start_x,
            height=design_track_height,
            corner_radius=0.05,
            stroke_color=GREY,
            stroke_width=1.3,
        ).set_fill(WHITE, opacity=0.0).move_to(design_center)
        design_dividers = VGroup(*[
            Line(
                np.array([time_to_x(boundary), timeres_strip_y - design_fill_height / 2, 0.0]),
                np.array([time_to_x(boundary), timeres_strip_y + design_fill_height / 2, 0.0]),
                color=_D_MGREY,
                stroke_width=0.9,
                stroke_opacity=0.55,
            )
            for idx, boundary in enumerate(event_boundary_times)
        ])
        event_projection_lines = VGroup(*[
            DashedLine(
                np.array([
                    time_to_x(boundary),
                    timeres_strip_y - design_fill_height / 2 + design_drop[1],
                    0.0,
                ]),
                np.array([
                    time_to_x(boundary),
                    timeres_frame.get_bottom()[1],
                    0.0,
                ]),
                color=_D_MGREY,
                stroke_width=0.9,
                dash_length=0.05,
                dashed_ratio=0.65,
            )
            for idx, boundary in enumerate(event_boundary_times)
        ])
        delay_end_arrow_length = 0.75
        delay_end_arrow_lift = delay_end_arrow_length * 0.15 * 1.30
        delay_end_chance_arrow = Arrow(
            np.array([
                time_to_x(10.0),
                timeres_chance_y + delay_end_arrow_lift + delay_end_arrow_length,
                0.0,
            ]),
            np.array([
                time_to_x(10.0),
                timeres_chance_y + delay_end_arrow_lift,
                0.0,
            ]),
            color=_D_RED,
            stroke_width=3.6,
            buff=0.0,
            tip_length=0.17,
            tip_shape=StealthTip,
        )
        target_phase = make_design_phase(
            0.0,
            2.0,
            test_s1_purple,
            0.16,
            make_design_icon(LAKE, 0.0, 2.0),
        )
        delay_phase = make_design_phase(
            2.0,
            10.0,
            self._DELAY_TEST,
            0.14,
            make_design_icon(None, 2.0, 10.0),
        )
        probe_icons = Group(
            make_design_icon(LAKE_D1, 10.0, 12.5),
            make_design_icon(None, 10.0, 12.5),
            make_design_icon(LAKE_D2, 10.0, 12.5),
        ).arrange(RIGHT, buff=0.03)
        probe_width = max(time_to_x(12.5) - time_to_x(10.0) - 0.07, 0.10)
        if probe_icons.width > probe_width:
            probe_icons.scale_to_fit_width(probe_width)
        probe_phase = make_design_phase(
            10.0,
            12.5,
            test_s1_purple,
            0.16,
            probe_icons,
        )
        response_phase = make_design_phase(
            12.5,
            14.5,
            _D_LGREY,
            0.20,
            make_design_icon(None, 12.5, 14.5, resp=True),
        )
        rest_phase = make_design_phase(
            14.5,
            timeres_total_time,
            _D_LGREY,
            0.10,
            VGroup(*[
                Dot(radius=0.014, color=_D_MGREY, fill_opacity=0.70)
                for _ in range(3)
            ]).arrange(RIGHT, buff=0.05),
        )
        design_phases = Group(
            target_phase,
            delay_phase,
            probe_phase,
            response_phase,
            rest_phase,
        )
        experimental_design = Group(design_frame, design_dividers, design_phases)
        design_label_y = design_frame_target.get_bottom()[1] - 0.20

        def make_design_phase_label(text: str, center_x: float, color: str) -> Tex:
            """Build the label for one compact design phase."""
            return Tex(
                rf"\textbf{{{text}}}",
                color=color,
                font_size=20,
            ).move_to(np.array([center_x, design_label_y, 0.0]))

        design_stimulation_label = make_design_phase_label(
            "Stimulation",
            target_phase.get_center()[0],
            self._S1_STIM_ACCENT,
        )
        design_delay_label = make_design_phase_label(
            "Delay",
            delay_phase.get_center()[0],
            self._DELAY_TEST,
        )
        design_probes_label = make_design_phase_label(
            "Probes",
            probe_phase.get_center()[0],
            self._S1_STIM_ACCENT,
        )
        design_response_label = make_design_phase_label(
            "Response",
            response_phase.get_center()[0],
            INK,
        )

        trs_label = Tex(
            "TRs",
            color=INK,
            font_size=16,
        ).next_to(VGroup(*time_bins), RIGHT, buff=0.10)

        step_tracker = ValueTracker(0)

        def sweep_target_x(step_value: float) -> float:
            """Return the current x target for the sweep animation."""
            step_value = float(np.clip(step_value, 0.0, len(time_bins) - 1))
            return float(interpolate(
                timeres_trace_xs[0],
                timeres_trace_xs[-1],
                step_value / (len(time_bins) - 1),
            ))

        def step_center(step_value: float) -> np.ndarray:
            """Return the centre point for the current step."""
            return np.array([sweep_target_x(step_value), timeres_strip_y, 0.0])

        def sweep_trace_prop() -> float:
            """Return the current trace proportion for the sweep animation."""
            return float(np.interp(
                sweep_target_x(step_tracker.get_value()),
                trace_unique_xs,
                trace_unique_props,
            ))

        def current_curve_point() -> np.ndarray:
            """Return the current point on the animated curve."""
            target_x = sweep_target_x(step_tracker.get_value())
            return np.array([
                target_x,
                float(np.interp(target_x, trace_unique_xs, trace_unique_ys)),
                0.0,
            ])

        def current_trace_mobject() -> VMobject:
            """Build the trace mobject for the current animation state."""
            target_x = sweep_target_x(step_tracker.get_value())
            curve_point = current_curve_point()
            idx = int(np.searchsorted(trace_unique_xs, target_x, side="right"))
            points = np.column_stack([
                trace_unique_xs[:max(idx, 1)],
                trace_unique_ys[:max(idx, 1)],
                np.zeros(max(idx, 1)),
            ])
            if np.linalg.norm(points[-1] - curve_point) > 1e-6:
                points = np.vstack([points, curve_point])
            if len(points) < 2:
                points = np.vstack([points[0], curve_point])
            trace = VMobject()
            trace.set_points_as_corners(points)
            trace.set_stroke(
                color=timeres_trace_template.get_stroke_color(),
                width=timeres_trace_template.get_stroke_width(),
                opacity=timeres_trace_template.get_stroke_opacity(),
            )
            trace.set_fill(opacity=0.0)
            if target_x <= trace_unique_xs[0] + 1e-6:
                trace.set_stroke(opacity=0.0)
            return trace

        def phase_color(step_value: float) -> ManimColor:
            """Return the colour assigned to the current phase."""
            current_time = float(
                interpolate(
                    0.0,
                    timeres_total_time,
                    np.clip(step_value / (len(time_bins) - 1), 0.0, 1.0),
                )
            )
            if current_time < 2.0:
                return ManimColor(test_s1_purple)
            if current_time < 10.0:
                return ManimColor(self._DELAY_TEST)
            if current_time < 12.5:
                return ManimColor(test_s1_purple)
            return ManimColor(_D_MGREY)

        timeres_trace = always_redraw(current_trace_mobject)

        def current_selector_center() -> np.ndarray:
            """Return the centre of the active selector."""
            return np.array([sweep_target_x(step_tracker.get_value()), timeres_strip_y, 0.0])

        active_bin = always_redraw(lambda: RoundedRectangle(
            width=timeres_bin_width + 0.05,
            height=timeres_bin_height + 0.07,
            corner_radius=0.04,
            stroke_color=phase_color(step_tracker.get_value()),
            stroke_width=2.0,
        ).set_fill(phase_color(step_tracker.get_value()), opacity=0.16).move_to(current_selector_center()))
        sweep_arrow_start = schematic_train[1].get_bottom() + DOWN * 0.04

        def sweep_arrow_tip(step_value: float) -> np.ndarray:
            """Return the current tip position of the sweep arrow."""
            return step_center(step_value) + UP * (timeres_bin_height / 2 + 0.05)

        def make_arrow_to_tip(tip_point: np.ndarray) -> Arrow:
            """Build an arrow that points to the current tip location."""
            return Arrow(
                sweep_arrow_start,
                tip_point,
                color=_D_MGREY,
                stroke_width=1.6,
                buff=0.02,
                tip_length=0.10,
            )

        def make_sweep_arrow(step_value: float) -> Arrow:
            """Build the sweep arrow for the current panel."""
            return make_arrow_to_tip(sweep_arrow_tip(step_value))

        design_intro_arrow = Arrow(
            sweep_arrow_start,
            design_frame.get_center() + UP * (design_track_height / 2 + 0.05),
            color=_D_MGREY,
            stroke_width=1.6,
            buff=0.02,
            tip_length=0.10,
        )
        sweep_arrow = always_redraw(lambda: make_sweep_arrow(step_tracker.get_value()))
        sweep_arrow_reset_target = make_arrow_to_tip(
            design_frame.get_center() + UP * (design_track_height / 2 + 0.05)
        )
        sweep_test_label_template = Tex("Test", color=INK, font_size=16)

        def sweep_test_label_position_for_tip(arrow_end: np.ndarray) -> np.ndarray:
            """Return the sweep test-label position for the current arrow tip."""
            arrow_start = sweep_arrow_start
            arrow_direction = arrow_end - arrow_start
            arrow_norm = np.linalg.norm(arrow_direction[:2])
            if arrow_norm < 1e-6:
                return arrow_start + RIGHT * 0.18
            arrow_unit = arrow_direction / arrow_norm
            arrow_perp = np.array([-arrow_unit[1], arrow_unit[0], 0.0])
            return interpolate(arrow_start, arrow_end, 0.52) + arrow_perp * 0.18

        def sweep_test_label_position_for_step(step_value: float) -> np.ndarray:
            """Return the sweep test-label position for one step index."""
            return sweep_test_label_position_for_tip(sweep_arrow_tip(step_value))

        def sweep_test_label_position() -> np.ndarray:
            """Return the current position of the sweep test label."""
            return sweep_test_label_position_for_step(step_tracker.get_value())

        sweep_test_label = always_redraw(
            lambda: sweep_test_label_template.copy().move_to(sweep_test_label_position())
        )
        sweep_test_label_reset_target = sweep_test_label_template.copy().move_to(
            sweep_test_label_position_for_tip(
                design_frame.get_center() + UP * (design_track_height / 2 + 0.05)
            )
        )

        plot_cursor = always_redraw(lambda: DashedLine(
            np.array([
                current_selector_center()[0],
                current_selector_center()[1] - (timeres_bin_height / 2 + 0.05),
                0.0,
            ]),
            current_curve_point(),
            color=_D_MGREY,
            stroke_width=1.0,
            dash_length=0.05,
            dashed_ratio=0.65,
        ))
        timeres_trace_head = always_redraw(lambda: Dot(
            current_curve_point(),
            radius=0.040,
            color=BLACK,
            fill_opacity=1.0,
        ).set_stroke(WHITE, width=1.0))
        timeres_ci.set_z_index(2.5)
        timeres_chance_group.set_z_index(2)
        timeres_plot_scaffold.set_z_index(2)
        design_intro_arrow.set_z_index(3)
        event_projection_lines.set_z_index(3)
        delay_end_chance_arrow.set_z_index(4)
        plot_cursor.set_z_index(3)
        sweep_test_label.set_z_index(4)
        timeres_sig_lines.set_z_index(3)
        timeres_hrf_rectangles.set_z_index(3)
        timeres_hrf_lines.set_z_index(3)
        timeres_trace.set_z_index(4)
        timeres_trace_head.set_z_index(5)

        return {
            "layout": layout,
            "setup_handoff_frame": handoff["frame"],
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
            "timeres_hrf_rectangles": timeres_hrf_rectangles,
            "timeres_hrf_lines": timeres_hrf_lines,
            "schematic_train": schematic_train,
            "timeres_train_explainer": timeres_train_explainer,
            "design_drop": design_drop,
            "experimental_design": experimental_design,
            "design_frame": design_frame,
            "design_frame_target": design_frame_target,
            "design_intro_arrow": design_intro_arrow,
            "design_dividers": design_dividers,
            "event_projection_lines": event_projection_lines,
            "delay_end_chance_arrow": delay_end_chance_arrow,
            "target_phase": target_phase,
            "delay_phase": delay_phase,
            "probe_phase": probe_phase,
            "response_phase": response_phase,
            "rest_phase": rest_phase,
            "design_stimulation_label": design_stimulation_label,
            "design_delay_label": design_delay_label,
            "design_probes_label": design_probes_label,
            "design_response_label": design_response_label,
            "time_bins": time_bins,
            "trs_label": trs_label,
            "active_bin": active_bin,
            "sweep_arrow": sweep_arrow,
            "sweep_arrow_reset_target": sweep_arrow_reset_target,
            "sweep_test_label": sweep_test_label,
            "sweep_test_label_reset_target": sweep_test_label_reset_target,
            "plot_cursor": plot_cursor,
            "timeres_trace": timeres_trace,
            "timeres_trace_head": timeres_trace_head,
            "step_tracker": step_tracker,
            "frame_width_final": frame_width_final,
            "frame_opacity_final": frame_opacity_final,
            "frame_width_emphasis": frame_width_emphasis,
        }

    def _animate_left_results(self, ctx: dict) -> None:
        """Animate the left results."""
        layout = ctx["layout"]
        glm_train = ctx["glm_train"]
        glm_stim_test = ctx["glm_stim_test"]
        glm_delay_test = ctx["glm_delay_test"]

        self.add(ctx["setup_handoff_frame"])
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
        self._animate_left_results_followthrough(ctx)

    def _animate_left_results_followthrough(self, ctx: dict) -> None:
        """Animate the left results followthrough."""
        glm_train = ctx["glm_train"]
        glm_stim_test = ctx["glm_stim_test"]
        glm_delay_test = ctx["glm_delay_test"]

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
                (
                    LaggedStart(
                        *[FadeIn(dot, scale=0.75) for dot in ctx["glm_left_points"]],
                        lag_ratio=0.04,
                    )
                    if len(ctx["glm_left_points"]) > 0
                    else AnimationGroup()
                ),
                FadeIn(ctx["glm_left_extras"], shift=UP * 0.04),
                lag_ratio=0.18,
            )
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

    def _animate_left_results_from_within_session_rationale(
        self,
        rationale: dict[str, Mobject],
        ctx: dict[str, Mobject],
    ) -> None:
        """Animate the left results from within session rationale."""
        stim_case = rationale["stim_stim_case"]
        delay_case = rationale["delay_delay_case"]
        cross_case = rationale["stim_delay_case"]
        frame_width_final = 1.5
        frame_opacity_final = 0.48
        frame_width_emphasis = 3.0

        for matrix in (
            ctx["glm_left_train"],
            ctx["glm_left_test"],
            ctx["glm_right_train"],
            ctx["glm_right_test"],
        ):
            matrix[1].set_stroke(width=frame_width_final, opacity=0.0)

        target_groups = [
            (stim_case["left_matrix"], ctx["glm_left_train"]),
            (stim_case["right_matrix"], ctx["glm_left_test"]),
            (delay_case["left_matrix"], ctx["glm_right_train"]),
            (delay_case["right_matrix"], ctx["glm_right_test"]),
        ]

        for _, target_matrix in target_groups:
            self.add(target_matrix[1])

        self.play(
            FadeOut(rationale["question_title"]),
            FadeOut(rationale["s1_title"]),
            FadeOut(rationale["s1_row_group"]),
            FadeOut(rationale["within_session_label"]),
            FadeOut(rationale["target_hi"]),
            FadeOut(rationale["delay_hi"]),
            FadeOut(rationale["repeated_note"]),
            FadeOut(stim_case["left_phase_label"], shift=DOWN * 0.03),
            FadeOut(stim_case["right_phase_label"], shift=DOWN * 0.03),
            FadeOut(stim_case["train_frame"]),
            FadeOut(stim_case["train_label"], shift=UP * 0.03),
            FadeOut(stim_case["test_arrow"], shift=DOWN * 0.02),
            FadeOut(stim_case["test_label"], shift=UP * 0.03),
            FadeOut(stim_case["test_frame"]),
            FadeOut(delay_case["left_phase_label"], shift=DOWN * 0.03),
            FadeOut(delay_case["right_phase_label"], shift=DOWN * 0.03),
            FadeOut(delay_case["train_frame"]),
            FadeOut(delay_case["train_label"], shift=UP * 0.03),
            FadeOut(delay_case["test_arrow"], shift=DOWN * 0.02),
            FadeOut(delay_case["test_label"], shift=UP * 0.03),
            FadeOut(delay_case["test_frame"]),
            FadeOut(cross_case["group"], shift=DOWN * 0.06),
            FadeOut(stim_case["left_matrix"][1]),
            FadeOut(stim_case["right_matrix"][1]),
            FadeOut(delay_case["left_matrix"][1]),
            FadeOut(delay_case["right_matrix"][1]),
            ReplacementTransform(
                VGroup(stim_case["left_matrix"][0], stim_case["left_matrix"][2]),
                VGroup(ctx["glm_left_train"][0], ctx["glm_left_train"][2]),
            ),
            ReplacementTransform(
                VGroup(stim_case["right_matrix"][0], stim_case["right_matrix"][2]),
                VGroup(ctx["glm_left_test"][0], ctx["glm_left_test"][2]),
            ),
            ReplacementTransform(
                VGroup(delay_case["left_matrix"][0], delay_case["left_matrix"][2]),
                VGroup(ctx["glm_right_train"][0], ctx["glm_right_train"][2]),
            ),
            ReplacementTransform(
                VGroup(delay_case["right_matrix"][0], delay_case["right_matrix"][2]),
                VGroup(ctx["glm_right_test"][0], ctx["glm_right_test"][2]),
            ),
            FadeIn(ctx["glm_title"], shift=UP * 0.06),
            Create(ctx["glm_plot_frame"]),
            FadeIn(ctx["glm_plot_rest"], shift=UP * 0.08),
            Create(ctx["glm_chance_line"]),
            FadeIn(ctx["glm_chance_label"], shift=UP * 0.04),
            run_time=0.95,
        )

        self.play(
            ctx["glm_left_train"][1].animate.set_stroke(width=frame_width_emphasis, opacity=1.0),
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
            else FadeIn(ctx["glm_left_extras"], shift=UP * 0.04)
        )
        self.play(
            GrowArrow(ctx["glm_left_column_arrow"]),
            run_time=0.55,
        )
        self.play(
            ctx["glm_left_test"][1].animate.set_stroke(width=frame_width_emphasis, opacity=1.0),
            FadeIn(ctx["glm_left_train_explainer"], shift=RIGHT * 0.05),
            FadeIn(ctx["glm_left_test_explainer"], shift=RIGHT * 0.05),
            AnimationGroup(
                left_cloud_anim,
                Write(ctx["glm_left_label"]),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.wait(0.80)

        self.play(
            ctx["glm_right_train"][1].animate.set_stroke(width=frame_width_emphasis, opacity=1.0),
            run_time=0.45,
        )
        self.wait(0.25)

        self.play(
            GrowArrow(ctx["glm_right_column_arrow"]),
            run_time=0.55,
        )
        self.play(
            ctx["glm_right_test"][1].animate.set_stroke(width=frame_width_emphasis, opacity=1.0),
            FadeIn(ctx["glm_right_train_explainer"], shift=LEFT * 0.05),
            FadeIn(ctx["glm_right_test_explainer"], shift=LEFT * 0.05),
            AnimationGroup(
                (
                    AnimationGroup(
                        LaggedStart(
                            *[FadeIn(dot, scale=0.75) for dot in ctx["glm_right_points"]],
                            lag_ratio=0.04,
                        ),
                        FadeIn(ctx["glm_right_extras"], shift=UP * 0.04),
                        lag_ratio=0.18,
                    )
                    if len(ctx["glm_right_points"]) > 0
                    else FadeIn(ctx["glm_right_extras"], shift=UP * 0.04)
                ),
                Write(ctx["glm_right_label"]),
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
                LaggedStart(
                    *[
                        FadeIn(marker, shift=UP * 0.03)
                        for marker in ctx["glm_right_significance"]
                    ],
                    lag_ratio=0.12,
                )
            )
        if significance_anims:
            self.wait(0.35)
            self.play(
                AnimationGroup(*significance_anims, lag_ratio=0.22),
                run_time=0.55,
            )
        self.wait(0.60)
        self.play(
            ctx["glm_left_train"][1].animate.set_stroke(
                width=frame_width_final, opacity=frame_opacity_final
            ),
            ctx["glm_left_test"][1].animate.set_stroke(
                width=frame_width_final, opacity=frame_opacity_final
            ),
            ctx["glm_right_train"][1].animate.set_stroke(
                width=frame_width_final, opacity=frame_opacity_final
            ),
            ctx["glm_right_test"][1].animate.set_stroke(
                width=frame_width_final, opacity=frame_opacity_final
            ),
            run_time=0.35,
        )
        self.wait(2.0)

    def _align_within_session_act1_to_shared_layout(
        self,
        ctx: dict[str, Mobject],
    ) -> None:
        """Position the within session act-1 to shared layout."""
        shared_ctx = self._build_results_context()
        ctx["shared_timeres_title"] = shared_ctx["timeres_title"].copy()
        plot_shift = (
            shared_ctx["glm_plot_frame"].get_center()
            - ctx["glm_plot_frame"].get_center()
        )
        for mob in (
            ctx["glm_plot_scaffold"],
            ctx["glm_left_column"],
            ctx["glm_right_column"],
            ctx["glm_left_cloud"],
            ctx["glm_right_cloud"],
            ctx["glm_left_significance"],
            ctx["glm_right_significance"],
        ):
            mob.shift(plot_shift)
        ctx["glm_title"].move_to(shared_ctx["glm_title"].get_center())

        left_x = (
            ctx["glm_left_points"].get_center()[0]
            if len(ctx["glm_left_points"]) > 0
            else ctx["glm_left_cloud"].get_center()[0]
        )
        right_x = (
            ctx["glm_right_points"].get_center()[0]
            if len(ctx["glm_right_points"]) > 0
            else ctx["glm_right_cloud"].get_center()[0]
        )
        title_bottom_y = ctx["glm_title"].get_bottom()[1]
        plot_top_y = ctx["glm_plot_frame"].get_top()[1]
        matrix_band_center_y = (title_bottom_y + plot_top_y) / 2
        matrix_row_gap = 1.18
        train_y = matrix_band_center_y + matrix_row_gap / 2
        test_y = matrix_band_center_y - matrix_row_gap / 2

        self._position_small_results_matrix(
            ctx["glm_left_train"],
            np.array([left_x, train_y, 0.0]),
            label_direction=UP,
        )
        self._position_small_results_matrix(
            ctx["glm_right_train"],
            np.array([right_x, train_y, 0.0]),
            label_direction=UP,
        )
        self._position_small_results_matrix(
            ctx["glm_left_test"],
            np.array([left_x, test_y, 0.0]),
            label_direction=DOWN,
        )
        self._position_small_results_matrix(
            ctx["glm_right_test"],
            np.array([right_x, test_y, 0.0]),
            label_direction=DOWN,
        )
        ctx["glm_left_train_explainer"].next_to(ctx["glm_left_train"][1], LEFT, buff=0.16)
        ctx["glm_left_test_explainer"].next_to(ctx["glm_left_test"][1], LEFT, buff=0.16)
        ctx["glm_right_train_explainer"].next_to(ctx["glm_right_train"][1], RIGHT, buff=0.16)
        ctx["glm_right_test_explainer"].next_to(ctx["glm_right_test"][1], RIGHT, buff=0.16)

        ctx["glm_left_column_arrow"].become(Arrow(
            ctx["glm_left_train"][1].get_bottom() + DOWN * 0.08,
            ctx["glm_left_test"][1].get_top() + UP * 0.08,
            color=_D_MGREY,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.10,
        ))
        ctx["glm_right_column_arrow"].become(Arrow(
            ctx["glm_right_train"][1].get_bottom() + DOWN * 0.08,
            ctx["glm_right_test"][1].get_top() + UP * 0.08,
            color=_D_MGREY,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.10,
        ))

    def _show_left_results_final_state(self, ctx: dict) -> None:
        """Animate the left results final state."""
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
        """Animate the to left results final state."""
        self.clear()
        self._show_left_results_final_state(ctx)

    def _animate_right_results(self, ctx: dict) -> None:
        """Animate the right results."""
        design_drop = ctx["design_drop"]
        intro_test_label = ctx["sweep_test_label_reset_target"].copy()
        intro_test_label.set_z_index(ctx["sweep_test_label"].z_index)

        self.play(
            FadeIn(ctx["timeres_title"], shift=UP * 0.06),
            FadeIn(ctx["schematic_train"], shift=UP * 0.06),
            FadeIn(ctx["timeres_train_explainer"], shift=RIGHT * 0.06),
            run_time=0.75,
        )
        self.wait(0.25)
        self.play(
            GrowArrow(ctx["design_intro_arrow"]),
            FadeIn(intro_test_label),
            run_time=0.35,
        )
        self.play(
            GrowFromCenter(ctx["design_frame"]),
            run_time=0.28,
        )
        self.play(
            Transform(ctx["design_frame"], ctx["design_frame_target"]),
            FadeIn(ctx["design_dividers"]),
            run_time=0.7,
        )
        design_phase_sequence = [
            ("target_phase", "design_stimulation_label"),
            ("delay_phase", "design_delay_label"),
            ("probe_phase", "design_probes_label"),
            ("response_phase", "design_response_label"),
        ]
        previous_label_key = None
        for phase_key, label_key in design_phase_sequence:
            animations = [FadeIn(ctx[phase_key], scale=0.90), FadeIn(ctx[label_key], shift=UP * 0.04)]
            if previous_label_key is not None:
                animations.insert(0, FadeOut(ctx[previous_label_key], shift=DOWN * 0.03))
            self.play(*animations, run_time=0.45)
            self.wait(0.55)
            previous_label_key = label_key
        self.play(
            FadeOut(ctx["design_response_label"], shift=DOWN * 0.03),
            FadeIn(ctx["rest_phase"], scale=0.90),
            run_time=0.40,
        )
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
            FadeIn(ctx["trs_label"], shift=RIGHT * 0.04),
            run_time=0.8,
        )
        self.wait(0.2)
        self.play(
            FadeOut(ctx["design_intro_arrow"]),
            FadeIn(ctx["active_bin"]),
            GrowArrow(ctx["sweep_arrow"]),
            Transform(intro_test_label, ctx["sweep_test_label"].copy()),
            FadeIn(ctx["plot_cursor"]),
            FadeIn(ctx["timeres_trace"]),
            FadeIn(ctx["timeres_trace_head"]),
            run_time=0.45,
        )
        self.remove(intro_test_label)
        self.add(ctx["sweep_test_label"])
        self.play(
            ctx["step_tracker"].animate.set_value(len(ctx["time_bins"]) - 1),
            run_time=0.5 * (len(ctx["time_bins"]) - 1),
            rate_func=linear,
        )
        sweep_arrow_static = ctx["sweep_arrow"].copy()
        sweep_arrow_static.clear_updaters()
        sweep_test_label_static = ctx["sweep_test_label"].copy()
        sweep_test_label_static.clear_updaters()
        sweep_arrow_static.set_z_index(ctx["sweep_test_label"].z_index - 1)
        sweep_test_label_static.set_z_index(ctx["sweep_test_label"].z_index)
        self.remove(ctx["sweep_arrow"], ctx["sweep_test_label"])
        self.add(sweep_arrow_static, sweep_test_label_static)
        self.play(
            FadeOut(ctx["active_bin"]),
            FadeOut(ctx["plot_cursor"]),
            Transform(sweep_arrow_static, ctx["sweep_arrow_reset_target"].copy()),
            Transform(sweep_test_label_static, ctx["sweep_test_label_reset_target"].copy()),
            LaggedStart(
                *[Create(line) for line in ctx["event_projection_lines"]],
                lag_ratio=0.08,
            ),
            run_time=0.65,
        )
        self.play(
            AnimationGroup(
                FadeIn(ctx["timeres_ci"]),
                FadeIn(ctx["timeres_sig_lines"]),
                FadeIn(ctx["timeres_hrf_rectangles"]),
                LaggedStart(
                    *[Create(line) for line in ctx["timeres_hrf_lines"]],
                    lag_ratio=0.12,
                ),
                lag_ratio=0.12,
            ),
            run_time=0.75,
        )
        self.play(
            GrowArrow(
                ctx["delay_end_chance_arrow"],
                rate_func=smooth,
            ),
            run_time=0.72,
        )
        for _ in range(3):
            self.play(
                ctx["delay_end_chance_arrow"].animate(
                    rate_func=there_and_back,
                ).shift(DOWN * 0.045),
                run_time=0.42,
            )
        self.wait(2.0)

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        ctx = self._build_results_context()
        self._animate_left_results(ctx)
        self._animate_right_results(ctx)


class Study2CrossSessionDecodingResultsA(Study2CrossSessionDecodingResultsCombined):
    """
    Part A: stop on the GLM plot summary.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsA -ql
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsA -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        ctx = self._build_results_context()
        self._animate_left_results(ctx)
        self._reset_to_left_results_final_state(ctx)
        self.wait(2.0)


class Study2CrossSessionDecodingResultsB(Study2CrossSessionDecodingResultsCombined):
    """
    Part B: start from the final GLM summary frame and continue to time-resolved decoding.

    Render:
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsB -ql
        uv run manim scenes/study2.py Study2CrossSessionDecodingResultsB -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        ctx = self._build_results_context()
        self._reset_to_left_results_final_state(ctx)
        self.wait(0.6)
        self._animate_right_results(ctx)


# ══════════════════════════════════════════════════════════════════════════════
# Study2WithinSession1DecodingSetup
# ══════════════════════════════════════════════════════════════════════════════


class _Study2WithinSession1DecodingBase(Study2CrossSessionDecodingResultsCombined):
    """
    Shared helpers for the Session 1 within-session decoding rationale and results scenes.
    """

    _RESULTS_GLM = str(_STUDY2_ASSET_DIR / "study2_results_ses01glm.svg")
    _RESULTS_TIMERES = str(_STUDY2_ASSET_DIR / "study2_results_ses01timeres.svg")
    _RESULTS_GLM_2 = str(_STUDY2_ASSET_DIR / "study2_results_ses01glm_2.svg")
    _TEMPGEN_LOGIC_MATRIX = str(_STUDY2_ASSET_DIR / "temp_gen_mat.svg")
    _TEMPGEN_SOURCE_PLOT_BOX = (53.5, 0.625, 291.61024, 238.73523)
    _TEMPGEN_SOURCE_COLORBAR_IMAGE_BOX = (303.60837, 0.5305, 312.9683697, 238.6105)
    _CROSSSESSION_RESULTSB_LAST = str(_STUDY2_ASSET_DIR / "study2_crosssession_resultsb_last_frame.png")
    _CROSSSESSION_RESULTSB_LEFT_PLOT = str(_STUDY2_ASSET_DIR / "study2_crosssession_resultsb_left_plot.png")
    _CROSSSESSION_RESULTSB_RIGHT_PLOT = str(_STUDY2_ASSET_DIR / "study2_crosssession_resultsb_right_plot.png")
    _CROSSSESSION_RESULTSB_SNAPSHOT_SIZE = (854, 480)
    _CROSSSESSION_RESULTSB_LEFT_BOX = (82, 124, 390, 442)
    _CROSSSESSION_RESULTSB_RIGHT_BOX = (460, 52, 802, 442)
    _GLM_ACCENT = _CROSSSESSION_STIM_SCATTER
    _DELAY_ACCENT = _CROSSSESSION_DELAY_SCATTER
    _RATIONALE_S1_ROW_SCALE = 0.56
    _RATIONALE_S1_ROW_CENTER = np.array([0.0, 1.78, 0.0])
    _RATIONALE_CASE_CENTERS = [
        np.array([0.0, 0.10, 0.0]),
        np.array([0.0, -1.34, 0.0]),
        np.array([0.0, -2.78, 0.0]),
    ]
    _RATIONALE_MATRIX_SCALE = 0.70
    _RATIONALE_MATRIX_HALF_SPACING = 0.82
    _RATIONALE_PHASE_FONT_SIZE = 18
    _RATIONALE_ROLE_FONT_SIZE = 16
    _RATIONALE_PHASE_LABEL_BUFF = 0.18

    def _make_results_heading(
        self,
        text: str,
        color: ManimColor = _D_MGREY,
        font_size: int = 22,
    ) -> Tex:
        """Build the results heading."""
        return Tex(
            text,
            color=color,
            font_size=font_size,
            tex_environment="center",
        )

    def _make_takeaway(self, lines: list[Tex]) -> VGroup:
        """Build the takeaway."""
        takeaway = VGroup(*lines).arrange(DOWN, buff=0.08, center=True)
        takeaway.move_to(np.array([0.0, -3.15, 0.0]))
        return takeaway

    def _make_cross_session_intro_summary(
        self,
        *,
        center: np.ndarray,
        font_size: int = 24,
    ) -> VGroup:
        """Build the cross session intro summary."""
        summary_line_1 = Tex(
            r"{{Sensory trained}} classifiers",
            color=INK,
            font_size=font_size,
        )
        summary_line_1.set_color_by_tex("Sensory trained", self._GLM_ACCENT)

        summary_line_2 = Tex(
            r"can decode object-scene identity",
            color=INK,
            font_size=font_size,
        )

        summary_line_3 = Tex(
            r"from the {{stimulation period}},",
            color=INK,
            font_size=font_size,
        )
        summary_line_3.set_color_by_tex("stimulation period", self._GLM_ACCENT)

        summary_line_4 = Tex(
            r"but not throughout the {{delay period}}.",
            color=INK,
            font_size=font_size,
        )
        summary_line_4.set_color_by_tex("delay period", self._DELAY_ACCENT)

        summary = VGroup(
            summary_line_1,
            summary_line_2,
            summary_line_3,
            summary_line_4,
        ).arrange(DOWN, buff=0.06, center=True)
        summary.move_to(center)
        return summary

    def _build_within_session_intro_context(self) -> dict[str, Mobject]:
        """Build the within session intro context."""
        return {
            "layout": self._build_cross_session_layout(),
            "rationale": self._build_rationale_end_static(),
            "result_intro": self._make_cross_session_intro_summary(
                center=np.array([0.0, 0.84, 0.0]),
                font_size=24,
            ),
            "question_intro": self._make_results_heading(
                self._rationale_question_text(),
                color=BLACK,
                font_size=30,
            ).move_to(np.array([0.0, 0.48, 0.0])),
        }

    def _prepare_cross_session_resultsb_final_state(
        self,
        results_ctx: dict[str, Mobject],
    ) -> None:
        """Animate the cross session resultsb final state."""
        for matrix in (
            results_ctx["glm_train"],
            results_ctx["glm_stim_test"],
            results_ctx["glm_delay_test"],
        ):
            matrix[1].set_stroke(
                width=results_ctx["frame_width_final"],
                opacity=results_ctx["frame_opacity_final"],
            )

        results_ctx["step_tracker"].set_value(len(results_ctx["time_bins"]) - 1)
        results_ctx["design_frame"].become(results_ctx["design_frame_target"].copy())
        results_ctx["experimental_design"].shift(results_ctx["design_drop"])
        results_ctx["timeres_trace"].update()
        results_ctx["timeres_trace_head"].update()
        results_ctx["sweep_test_label"].update()

    def _build_cross_session_resultsb_summary_card(self) -> dict[str, Mobject]:
        """Build the cross session resultsb summary card."""
        results_ctx = self._build_results_context()
        self._prepare_cross_session_resultsb_final_state(results_ctx)

        left_plot_full = Group(
            results_ctx["glm_title"],
            results_ctx["glm_plot_scaffold"],
            results_ctx["glm_left_cloud"],
            results_ctx["glm_right_cloud"],
            results_ctx["glm_significance_markers"],
        )
        left_support = Group(
            results_ctx["glm_train"],
            results_ctx["glm_stim_test"],
            results_ctx["glm_delay_test"],
            results_ctx["glm_left_arrow"],
            results_ctx["glm_right_arrow"],
            results_ctx["glm_train_explainer"],
            results_ctx["glm_stim_explainer"],
            results_ctx["glm_delay_explainer"],
        )

        right_plot_full = Group(
            results_ctx["timeres_title"],
            results_ctx["timeres_plot_scaffold"],
            results_ctx["timeres_chance_group"],
            results_ctx["timeres_trace"],
            results_ctx["timeres_trace_head"],
            results_ctx["timeres_ci"],
            results_ctx["timeres_sig_lines"],
            results_ctx["timeres_hrf_rectangles"],
            results_ctx["timeres_hrf_lines"],
        )
        right_support = Group(
            results_ctx["schematic_train"],
            results_ctx["timeres_train_explainer"],
            results_ctx["experimental_design"],
            results_ctx["time_bins"],
            results_ctx["trs_label"],
            results_ctx["sweep_arrow_reset_target"],
            results_ctx["sweep_test_label_reset_target"],
            results_ctx["event_projection_lines"],
            results_ctx["delay_end_chance_arrow"],
        )
        full_frame = Group(
            left_plot_full,
            left_support,
            right_plot_full,
            right_support,
        )

        takeaway = self._make_cross_session_takeaway(
            center=np.array([0.0, 2.18, 0.0]),
            font_size=26,
        )

        left_plot_compact = left_plot_full.copy()
        left_plot_compact.scale_to_fit_width(4.05)
        left_plot_compact.move_to(np.array([-2.28, 0.10, 0.0]))
        left_plot_compact.set_opacity(0.94)

        right_plot_compact = right_plot_full.copy()
        right_plot_compact.scale_to_fit_width(4.05)
        right_plot_compact.move_to(np.array([2.28, 0.10, 0.0]))
        right_plot_compact.set_opacity(0.94)

        return {
            "results_ctx": results_ctx,
            "full_frame": full_frame,
            "takeaway": takeaway,
            "left_plot_full": left_plot_full,
            "left_support": left_support,
            "right_plot_full": right_plot_full,
            "right_support": right_support,
            "left_plot_compact": left_plot_compact,
            "right_plot_compact": right_plot_compact,
        }

    def _make_snapshot_plot_overlay(
        self,
        image_path: str,
        crop_box: tuple[int, int, int, int],
        full_snapshot: ImageMobject,
    ) -> ImageMobject:
        """Build the snapshot plot overlay."""
        source_w, source_h = self._CROSSSESSION_RESULTSB_SNAPSHOT_SIZE
        x0, y0, x1, y1 = crop_box
        crop_center_x = (x0 + x1) / 2
        crop_center_y = (y0 + y1) / 2

        overlay = ImageMobject(image_path)
        overlay.scale_to_fit_width(full_snapshot.width * ((x1 - x0) / source_w))
        overlay.move_to(
            full_snapshot.get_center()
            + np.array([
                ((crop_center_x - (source_w / 2)) / source_w) * full_snapshot.width,
                (((source_h / 2) - crop_center_y) / source_h) * full_snapshot.height,
                0.0,
            ])
        )
        return overlay

    def _build_within_session_summary_card(self) -> dict[str, Mobject]:
        """Build the within session summary card."""
        takeaway = self._make_cross_session_takeaway(
            center=np.array([0.0, 2.18, 0.0]),
            font_size=26,
        )
        left_plot = (
            ImageMobject(self._CROSSSESSION_RESULTSB_LEFT_PLOT)
            .scale_to_fit_height(2.55)
            .move_to(np.array([-2.15, -0.02, 0.0]))
        )
        right_plot = (
            ImageMobject(self._CROSSSESSION_RESULTSB_RIGHT_PLOT)
            .scale_to_fit_height(2.55)
            .move_to(np.array([2.15, -0.02, 0.0]))
        )
        question = self._make_results_heading(
            self._rationale_question_text(),
            color=BLACK,
            font_size=28,
        ).move_to(np.array([0.0, -2.72, 0.0]))
        plots = Group(left_plot, right_plot)
        return {
            "takeaway": takeaway,
            "left_plot": left_plot,
            "right_plot": right_plot,
            "plots": plots,
            "question": question,
            "frame": Group(takeaway, plots, question),
        }

    def _animate_within_session_intro(
        self,
        ctx: dict[str, Mobject],
        *,
        summary_hold: float = 3.0,
        question_hold: float = 2.0,
    ) -> None:
        """Animate the within session intro."""
        self.play(FadeIn(ctx["result_intro"], shift=UP * 0.08), run_time=0.75)
        self.wait(summary_hold)
        self.play(
            FadeOut(ctx["result_intro"], shift=UP * 0.04),
            FadeIn(ctx["question_intro"], shift=UP * 0.08),
            run_time=0.85,
        )
        self.wait(question_hold)

    def _animate_within_session_scheme_from_question(
        self,
        ctx: dict[str, Mobject],
        *,
        question_already_at_title: bool = False,
    ) -> None:
        """Animate the within session scheme from question."""
        layout = ctx["layout"]
        rationale = ctx["rationale"]
        question_intro = ctx["question_intro"]
        reference_values = self._session1_reference_values()

        if not question_already_at_title:
            self.play(
                Transform(question_intro, rationale["question_title"]),
                run_time=0.75,
            )
        self.wait(0.15)
        self.play(
            FadeIn(layout["s2_title"]),
            FadeIn(layout["s2_row_group"]),
            FadeIn(layout["s1_title"]),
            FadeIn(layout["s1_row_group"]),
            run_time=0.80,
        )
        self.wait(0.15)
        self.play(
            FadeOut(layout["s2_title"]),
            FadeOut(layout["s2_row_group"]),
            Transform(layout["s1_title"], rationale["s1_title"]),
            Transform(layout["s1_row_group"], rationale["s1_row_group"]),
            run_time=0.95,
        )
        self.play(
            Create(rationale["target_hi"]),
            Create(rationale["delay_hi"]),
            run_time=0.55,
        )
        self.play(
            FadeIn(rationale["within_session_label"], shift=RIGHT * 0.08),
            FadeIn(rationale["repeated_note"], shift=UP * 0.04),
            run_time=0.50,
        )
        case_sequence = [
            {
                "key": "stim_stim_case",
                "highlights": [rationale["target_hi"]],
                "left_source_box": rationale["s1_boxes"][0],
                "right_source_box": rationale["s1_boxes"][0],
                "train_values": reference_values["stim_train"],
                "train_color": self._GLM_ACCENT,
                "train_code": r"$S_1$",
                "train_phase": "Stimulation",
                "test_values": reference_values["stim_test"],
                "test_color": self._GLM_ACCENT,
                "test_code": r"$S_1$",
                "test_phase": "Stimulation",
            },
            {
                "key": "delay_delay_case",
                "highlights": [rationale["delay_hi"]],
                "left_source_box": rationale["s1_boxes"][1],
                "right_source_box": rationale["s1_boxes"][1],
                "train_values": reference_values["delay_train"],
                "train_color": self._DELAY_ACCENT,
                "train_code": r"$D_1$",
                "train_phase": "Delay",
                "test_values": reference_values["delay_test"],
                "test_color": self._DELAY_ACCENT,
                "test_code": r"$D_1$",
                "test_phase": "Delay",
            },
            {
                "key": "stim_delay_case",
                "highlights": [rationale["target_hi"], rationale["delay_hi"]],
                "left_source_box": rationale["s1_boxes"][0],
                "right_source_box": rationale["s1_boxes"][1],
                "train_values": reference_values["stim_train"],
                "train_color": self._GLM_ACCENT,
                "train_code": r"$S_1$",
                "train_phase": "Stimulation",
                "test_values": reference_values["delay_train"],
                "test_color": self._DELAY_ACCENT,
                "test_code": r"$D_1$",
                "test_phase": "Delay",
            },
        ]
        focus_center = np.array([-0.70, -1.22, 0.0])
        parked_centers = [
            np.array([4.00, -0.20, 0.0]),
            np.array([4.00, -1.85, 0.0]),
            np.array([4.00, -3.50, 0.0]),
        ]
        parked_groups: list[Mobject] = []
        for spec, parked_center in zip(case_sequence, parked_centers):
            case = self._make_within_session_case(
                left_source_box=spec["left_source_box"],
                right_source_box=spec["right_source_box"],
                center=focus_center,
                train_values=spec["train_values"],
                train_color=spec["train_color"],
                train_code=spec["train_code"],
                train_phase=spec["train_phase"],
                test_values=spec["test_values"],
                test_color=spec["test_color"],
                test_code=spec["test_code"],
                test_phase=spec["test_phase"],
                matrix_scale=1.28,
                matrix_half_spacing=1.62,
                phase_font_size=22,
                role_font_size=22,
                phase_label_buff=0.20,
            )
            parked_target = self._make_within_session_case(
                left_source_box=spec["left_source_box"],
                right_source_box=spec["right_source_box"],
                center=parked_center,
                train_values=spec["train_values"],
                train_color=spec["train_color"],
                train_code=spec["train_code"],
                train_phase=spec["train_phase"],
                test_values=spec["test_values"],
                test_color=spec["test_color"],
                test_code=spec["test_code"],
                test_phase=spec["test_phase"],
                matrix_scale=0.44,
                matrix_half_spacing=0.72,
                phase_font_size=12,
                role_font_size=12,
                phase_label_buff=0.16,
            )
            self.play(
                AnimationGroup(
                    *[
                        Indicate(
                            mob,
                            color=mob.get_stroke_color(),
                            scale_factor=1.03,
                        )
                        for mob in spec["highlights"]
                    ],
                    lag_ratio=0.10,
                ),
                run_time=0.65,
            )
            self.play(
                Succession(
                    GrowArrow(case["left_source_arrow"]),
                    AnimationGroup(
                        FadeIn(case["left_matrix"]),
                        FadeIn(case["left_phase_label"], shift=UP * 0.03),
                        lag_ratio=0.0,
                    ),
                ),
                run_time=0.85,
            )
            self.play(
                Succession(
                    GrowArrow(case["right_source_arrow"]),
                    AnimationGroup(
                        FadeIn(case["right_matrix"]),
                        FadeIn(case["right_phase_label"], shift=UP * 0.03),
                        lag_ratio=0.0,
                    ),
                ),
                run_time=0.85,
            )
            self.play(
                FadeOut(case["left_source_arrow"], shift=DOWN * 0.02),
                FadeOut(case["right_source_arrow"], shift=DOWN * 0.02),
                Create(case["train_frame"]),
                FadeIn(case["train_label"], shift=UP * 0.03),
                run_time=0.60,
            )
            self.play(
                GrowArrow(case["test_arrow"]),
                FadeIn(case["test_label"], shift=UP * 0.03),
                Create(case["test_frame"]),
                run_time=0.65,
            )
            self.play(
                Transform(case["group"], parked_target["group"]),
                run_time=0.60,
            )
            parked_groups.append(case["group"])
        self.play(
            Transform(parked_groups[0], rationale["stim_stim_case"]["group"]),
            Transform(parked_groups[1], rationale["delay_delay_case"]["group"]),
            Transform(parked_groups[2], rationale["stim_delay_case"]["group"]),
            run_time=0.85,
        )
        self.wait(1.6)

    def _load_svg_plot(
        self,
        path: str,
        *,
        center: np.ndarray,
        height: float,
    ) -> SVGMobject:
        """Load the SVG plot."""
        return SVGMobject(path).scale_to_fit_height(height).move_to(center)

    def _tempgen_svg_plot_frame(self, svg: SVGMobject) -> VGroup:
        """Return the temporal-generalisation SVG plot frame."""
        return self._svg_plot_frame_from_long_lines(
            svg,
            min_span_ratio=0.48,
            max_thickness_ratio=0.02,
        )

    def _shared_sanitized_tempgen_svg(self, svg_path: str | Path) -> Path:
        """Return the shared sanitized temporal-generalisation SVG."""
        svg_path = Path(svg_path)
        cache_dir = Path(tempfile.gettempdir()) / "study2_tempgen_svg_sanitized"
        cache_dir.mkdir(parents=True, exist_ok=True)
        sanitized_path = cache_dir / svg_path.name
        if sanitized_path.exists() and sanitized_path.stat().st_mtime >= svg_path.stat().st_mtime:
            return sanitized_path

        tree = ET.parse(svg_path)
        root = tree.getroot()
        parent_map = {child: parent for parent in root.iter() for child in parent}
        for elem in list(root.iter()):
            # Some export pipelines emit empty <path> elements that svgelements
            # treats inconsistently; strip them once and cache the cleaned file.
            if elem.tag.endswith("path") and elem.get("d") is None:
                parent = parent_map.get(elem)
                if parent is not None:
                    parent.remove(elem)
        tree.write(sanitized_path, encoding="utf-8", xml_declaration=True)
        return sanitized_path

    def _cached_tempgen_colorbar_gradient_png(self) -> Path:
        """Return the cached temporal-generalisation colorbar gradient PNG."""
        svg_path = Path(self._TEMPGEN_LOGIC_MATRIX)
        cache_dir = Path(tempfile.gettempdir()) / "study2_tempgen_colorbar_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        png_path = cache_dir / f"{svg_path.stem}_colorbar_gradient_v2.png"
        if png_path.exists() and png_path.stat().st_mtime >= svg_path.stat().st_mtime:
            return png_path

        root = ET.parse(svg_path).getroot()
        image_elem = next((elem for elem in root.iter() if elem.tag.endswith("image")), None)
        if image_elem is None:
            raise RuntimeError(f"Could not locate embedded colorbar image in {svg_path}")

        href = (
            image_elem.get("{http://www.w3.org/1999/xlink}href")
            or image_elem.get("href")
        )
        if href is None or not href.startswith("data:image/png;base64,"):
            raise RuntimeError(f"Embedded colorbar image in {svg_path} is not a base64 PNG")

        gradient_bytes = base64.b64decode(href.split(",", 1)[1].strip())
        with Image.open(BytesIO(gradient_bytes)) as image:
            # The embedded raster uses SVG image coordinates, so flip it once to
            # match the plot's Cartesian y-direction before caching.
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            image.save(png_path)
        return png_path

    def _make_tempgen_colorbar_gradient_overlay(
        self,
        plot_frame: Mobject,
        *,
        z_index: float,
    ) -> ImageMobject:
        """Build the temporal-generalisation colorbar gradient overlay."""
        plot_x0, plot_y0, plot_x1, plot_y1 = self._TEMPGEN_SOURCE_PLOT_BOX
        cbar_x0, cbar_y0, cbar_x1, cbar_y1 = self._TEMPGEN_SOURCE_COLORBAR_IMAGE_BOX
        plot_width = plot_x1 - plot_x0
        plot_height = plot_y1 - plot_y0
        gap_ratio = (cbar_x0 - plot_x1) / plot_width
        height_ratio = (cbar_y1 - cbar_y0) / plot_height
        center_y_ratio = (
            ((cbar_y0 + cbar_y1) / 2) - ((plot_y0 + plot_y1) / 2)
        ) / plot_height

        overlay = ImageMobject(str(self._cached_tempgen_colorbar_gradient_png()))
        overlay.scale_to_fit_height(plot_frame.height * height_ratio)
        overlay.move_to(np.array([
            plot_frame.get_right()[0] + plot_frame.width * gap_ratio + overlay.width / 2,
            plot_frame.get_center()[1] + plot_frame.height * center_y_ratio,
            0.0,
        ]))
        overlay.set_z_index(z_index)
        return overlay

    def _make_tempgen_colorbar_mask(
        self,
        plot_frame: Mobject,
        *,
        z_index: float,
    ) -> Rectangle:
        """Build the temporal-generalisation colorbar mask."""
        plot_x0, plot_y0, plot_x1, plot_y1 = self._TEMPGEN_SOURCE_PLOT_BOX
        cbar_x0, cbar_y0, cbar_x1, cbar_y1 = self._TEMPGEN_SOURCE_COLORBAR_IMAGE_BOX
        plot_width = plot_x1 - plot_x0
        plot_height = plot_y1 - plot_y0
        gap_ratio = (cbar_x0 - plot_x1) / plot_width
        width_ratio = (cbar_x1 - cbar_x0) / plot_width
        height_ratio = (cbar_y1 - cbar_y0) / plot_height
        center_y_ratio = (
            ((cbar_y0 + cbar_y1) / 2) - ((plot_y0 + plot_y1) / 2)
        ) / plot_height

        mask = Rectangle(
            width=plot_frame.width * width_ratio,
            height=plot_frame.height * height_ratio,
            stroke_width=0.0,
        ).set_fill(BG, opacity=1.0)
        mask.move_to(np.array([
            plot_frame.get_right()[0] + plot_frame.width * gap_ratio + mask.width / 2,
            plot_frame.get_center()[1] + plot_frame.height * center_y_ratio,
            0.0,
        ]))
        mask.set_z_index(z_index)
        return mask

    def _load_tempgen_svg_with_frame(
        self,
        *,
        center: np.ndarray,
        height: float,
    ) -> tuple[SVGMobject, VGroup]:
        """Load the temporal-generalisation SVG with frame."""
        svg = self._load_svg_plot(
            str(self._shared_sanitized_tempgen_svg(self._TEMPGEN_LOGIC_MATRIX)),
            center=center,
            height=height,
        )
        self._hide_svg_background_rect(svg)
        return svg, self._tempgen_svg_plot_frame(svg)

    def _tempgen_plot_clip_masks(
        self,
        panel: Mobject,
        plot_frame: Mobject,
        *,
        fill_color: ParsableManimColor = BG,
        cover_left: bool = True,
        cover_bottom: bool = True,
        cover_top: bool = True,
        bottom_min_height: float = 0.0,
        right_gutter_width: float = 0.0,
        top_gutter_height: float = 0.0,
        z_index: float = 2.2,
    ) -> VGroup:
        # Matplotlib clips the heatmap and contours to the square plot box, but
        # Manim's SVG importer does not consistently honor that clip path.
        """Return the temporal-generalisation plot clip masks."""
        masks = VGroup()
        bleed = 0.002

        if cover_left:
            left_mask_width = max(
                0.0,
                plot_frame.get_left()[0] - panel.get_left()[0] - bleed,
            )
            if left_mask_width > 1e-3:
                left_mask = Rectangle(
                    width=left_mask_width,
                    height=panel.height,
                    stroke_width=0.0,
                ).set_fill(fill_color, opacity=1.0)
                left_mask.move_to(np.array([
                    panel.get_left()[0] + left_mask_width / 2,
                    panel.get_center()[1],
                    0.0,
                ]))
                left_mask.set_z_index(z_index)
                masks.add(left_mask)

        if cover_bottom:
            bottom_mask_height = max(
                0.0,
                plot_frame.get_bottom()[1] - panel.get_bottom()[1] - bleed,
            )
            if bottom_mask_height > 1e-3 or bottom_min_height > 1e-3:
                bottom_mask_height = max(bottom_mask_height, bottom_min_height)
                bottom_mask = Rectangle(
                    width=panel.width,
                    height=bottom_mask_height,
                    stroke_width=0.0,
                ).set_fill(fill_color, opacity=1.0)
                bottom_mask.move_to(np.array([
                    panel.get_center()[0],
                    plot_frame.get_bottom()[1] - bottom_mask_height / 2 - 0.01,
                    0.0,
                ]))
                bottom_mask.set_z_index(z_index)
                masks.add(bottom_mask)

        if cover_top:
            top_mask_height = max(
                0.0,
                panel.get_top()[1] - plot_frame.get_top()[1] - bleed,
            )
            if top_mask_height > 1e-3:
                top_mask = Rectangle(
                    width=plot_frame.width,
                    height=top_mask_height,
                    stroke_width=0.0,
                ).set_fill(fill_color, opacity=1.0)
                top_mask.move_to(np.array([
                    plot_frame.get_center()[0],
                    plot_frame.get_top()[1] + top_mask_height / 2 + 0.01,
                    0.0,
                ]))
                top_mask.set_z_index(z_index)
                masks.add(top_mask)

        if right_gutter_width > 1e-3:
            right_gutter = Rectangle(
                width=right_gutter_width,
                height=plot_frame.height + 2 * bleed,
                stroke_width=0.0,
            ).set_fill(fill_color, opacity=1.0)
            right_gutter.move_to(np.array([
                plot_frame.get_right()[0] + right_gutter_width / 2,
                plot_frame.get_center()[1],
                0.0,
            ]))
            right_gutter.set_z_index(z_index)
            masks.add(right_gutter)

        if top_gutter_height > 1e-3:
            top_gutter = Rectangle(
                width=plot_frame.width + right_gutter_width,
                height=top_gutter_height,
                stroke_width=0.0,
            ).set_fill(fill_color, opacity=1.0)
            top_gutter.move_to(np.array([
                plot_frame.get_center()[0] + right_gutter_width / 2,
                plot_frame.get_top()[1] + top_gutter_height / 2,
                0.0,
            ]))
            top_gutter.set_z_index(z_index)
            masks.add(top_gutter)

        return masks

    def _hide_svg_background_rect(self, svg: SVGMobject) -> None:
        """Return the hide SVG background rect."""
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
        """Return the hide SVG white regions."""
        min_area = svg.width * svg.height * min_area_ratio
        for submob in svg.submobjects:
            fill_hex = self._glm_svg_hex(submob.get_fill_color())
            stroke_hex = self._glm_svg_hex(submob.get_stroke_color())
            if fill_hex == "#FFFFFF" and submob.width * submob.height >= min_area:
                submob.set_fill(opacity=0.0)
                if stroke_hex == "#FFFFFF":
                    submob.set_stroke(opacity=0.0)

    def _svg_plot_frame_from_long_lines(
        self,
        svg: SVGMobject,
        *,
        min_span_ratio: float = 0.7,
        max_thickness_ratio: float | None = None,
    ) -> VGroup:
        """Return the SVG plot frame from long lines."""
        candidates = [
            submob
            for submob in svg.submobjects
            if (
                submob.get_stroke_opacity() > 0.0
                and (
                    (
                        submob.width >= svg.width * min_span_ratio
                        and submob.height <= svg.height * 0.12
                    )
                    or (
                        submob.height >= svg.height * min_span_ratio
                        and submob.width <= svg.width * 0.12
                    )
                )
            )
        ]
        verticals = [submob for submob in candidates if submob.height > submob.width]
        horizontals = [submob for submob in candidates if submob.width >= submob.height]
        if max_thickness_ratio is not None:
            verticals = [
                submob
                for submob in verticals
                if submob.width <= svg.width * max_thickness_ratio
            ]
            horizontals = [
                submob
                for submob in horizontals
                if submob.height <= svg.height * max_thickness_ratio
            ]
        if len(verticals) < 2 or len(horizontals) < 2:
            raise ValueError("Could not identify SVG plot frame from long lines")
        left = min(verticals, key=lambda mob: mob.get_center()[0])
        right = max(verticals, key=lambda mob: mob.get_center()[0])
        bottom = min(horizontals, key=lambda mob: mob.get_center()[1])
        top = max(horizontals, key=lambda mob: mob.get_center()[1])
        return VGroup(left, right, bottom, top)

    def _make_tempgen_column_covers(
        self,
        plot_frame: VGroup,
        *,
        columns: int = 16,
        rows: int = 16,
        inset: float = 0.02,
        fill_color: ParsableManimColor = BG,
    ) -> list[VGroup]:
        """Build the temporal-generalisation column covers."""
        left = plot_frame.get_left()[0] + inset
        right = plot_frame.get_right()[0] - inset
        bottom = plot_frame.get_bottom()[1] + inset
        top = plot_frame.get_top()[1] - inset
        cell_width = (right - left) / columns
        cell_height = (top - bottom) / rows

        column_groups: list[VGroup] = []
        for column_idx in range(columns):
            column_group = VGroup()
            for row_idx in range(rows):
                cover = Rectangle(
                    width=cell_width + 0.01,
                    height=cell_height + 0.01,
                    stroke_width=0.0,
                ).set_fill(fill_color, opacity=1.0)
                cover.move_to(np.array([
                    left + (column_idx + 0.5) * cell_width,
                    bottom + (row_idx + 0.5) * cell_height,
                    0.0,
                ]))
                cover.set_z_index(3.5)
                column_group.add(cover)
            column_groups.append(column_group)
        return column_groups

    def _timeres_select_many(
        self,
        svg: SVGMobject,
        *,
        stroke_hex: str | None = None,
        fill_hex: str | None = None,
        min_points: int = 0,
    ) -> list[VMobject]:
        """Return the time-resolved select many."""
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
        """Return the time-resolved select single."""
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
        """Return the time-resolved significance bands."""
        return VGroup(*self._timeres_select_many(svg, stroke_hex="#C49A00", min_points=4))

    def _glm_svg_center_group(self, svg: SVGMobject, color_hex: str) -> VGroup:
        """Return the GLM SVG center group."""
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
        """Return the GLM SVG center significance marker."""
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

    def _scale_session_label_groups(self, time_labels: VGroup, phase_labels: VGroup) -> None:
        """Position the session label groups."""
        for label in time_labels:
            label.scale(self._ROW_TIME_LABEL_SCALE)
        for label in phase_labels:
            label.scale(self._ROW_PHASE_LABEL_SCALE)

    def _rationale_question_text(self) -> str:
        """Return the rationale question text."""
        return (
            r"Is there any stimulus-specific information\\"
            r"in the delay period in V1-V3?"
        )

    def _session1_reference_values(self) -> dict[str, np.ndarray]:
        """Return the frozen Session 1 matrix exemplars reused across scenes."""
        cache_name = "_session1_reference_values_cache"
        if not hasattr(self, cache_name):
            setattr(
                self,
                cache_name,
                {
                    "stim_train": self._row_values(0, 0).copy(),
                    "stim_test": self._row_values(0, 1).copy(),
                    "delay_train": self._delay_row_values(0, 0).copy(),
                    "delay_test": self._delay_row_values(0, 1).copy(),
                },
            )
        cached = getattr(self, cache_name)
        return {key: values.copy() for key, values in cached.items()}

    def _make_within_session_case(
        self,
        *,
        left_source_box: Mobject,
        right_source_box: Mobject,
        center: np.ndarray,
        train_values: np.ndarray,
        train_color: ManimColor,
        train_code: str,
        train_phase: str,
        test_values: np.ndarray,
        test_color: ManimColor,
        test_code: str,
        test_phase: str,
        matrix_scale: float = 0.76,
        matrix_half_spacing: float = 1.16,
        phase_font_size: int = 16,
        role_font_size: int = 16,
        phase_label_buff: float = 0.08,
    ) -> dict[str, Mobject]:
        """Build the within session case."""
        left_matrix = self._make_small_results_matrix(
            train_values,
            train_color,
            train_code,
            label_direction=DOWN,
        ).scale(matrix_scale)
        right_matrix = self._make_small_results_matrix(
            test_values,
            test_color,
            test_code,
            label_direction=DOWN,
        ).scale(matrix_scale)

        for matrix in (left_matrix, right_matrix):
            matrix[1].set_stroke(width=1.45, opacity=0.82)
            matrix[2].set_opacity(0.0)

        left_center = center + LEFT * matrix_half_spacing
        right_center = center + RIGHT * matrix_half_spacing
        self._position_small_results_matrix(
            left_matrix,
            left_center,
            label_direction=DOWN,
        )
        self._position_small_results_matrix(
            right_matrix,
            right_center,
            label_direction=DOWN,
        )

        left_phase_label = Tex(
            train_phase,
            color=train_color,
            font_size=phase_font_size,
        ).next_to(left_matrix[1], DOWN, buff=phase_label_buff)
        right_phase_label = Tex(
            test_phase,
            color=test_color,
            font_size=phase_font_size,
        ).next_to(right_matrix[1], DOWN, buff=phase_label_buff)

        train_frame = self._make_panel_focus_frame(left_matrix[1])
        train_label = Tex(
            "Train",
            color=INK,
            font_size=role_font_size,
        ).next_to(train_frame, UP, buff=0.08)
        test_frame = self._make_panel_focus_frame(right_matrix[1])
        test_label = Tex(
            "Test",
            color=INK,
            font_size=role_font_size,
        ).next_to(test_frame, UP, buff=0.08)

        left_arrow_tip = np.array([
            left_matrix[1].get_center()[0],
            left_matrix[1].get_top()[1] - 0.02,
            0.0,
        ])
        right_arrow_tip = np.array([
            right_matrix[1].get_center()[0],
            right_matrix[1].get_top()[1] - 0.02,
            0.0,
        ])
        left_source_arrow = Arrow(
            left_source_box.get_bottom() + DOWN * 0.05,
            left_arrow_tip,
            color=train_color,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.11,
        )
        right_source_arrow = Arrow(
            right_source_box.get_bottom() + DOWN * 0.05,
            right_arrow_tip,
            color=test_color,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.11,
        )

        gap_left = left_matrix[1].get_right()[0]
        gap_right = right_matrix[1].get_left()[0]
        gap_y = (left_matrix[1].get_center()[1] + right_matrix[1].get_center()[1]) / 2
        gap_half_len = max((gap_right - gap_left) * 0.25, 0.18)
        test_arrow = Arrow(
            np.array([((gap_left + gap_right) / 2) - gap_half_len, gap_y, 0.0]),
            np.array([((gap_left + gap_right) / 2) + gap_half_len, gap_y, 0.0]),
            color=_D_MGREY,
            stroke_width=1.85,
            buff=0.02,
            tip_length=0.11,
        )

        final_group = Group(
            left_matrix,
            left_phase_label,
            right_matrix,
            right_phase_label,
            train_frame,
            train_label,
            test_arrow,
            test_label,
            test_frame,
        )
        return {
            "group": final_group,
            "left_source_arrow": left_source_arrow,
            "right_source_arrow": right_source_arrow,
            "left_matrix": left_matrix,
            "left_phase_label": left_phase_label,
            "right_matrix": right_matrix,
            "right_phase_label": right_phase_label,
            "train_frame": train_frame,
            "train_label": train_label,
            "test_arrow": test_arrow,
            "test_label": test_label,
            "test_frame": test_frame,
        }

    def _build_rationale_end_static(self) -> dict[str, Mobject]:
        """Build the rationale end static."""
        reference_values = self._session1_reference_values()
        question_title = self._make_results_heading(
            self._rationale_question_text(),
            color=BLACK,
            font_size=24,
        ).to_edge(UP, buff=0.18)

        s1_title, s1_row_group, s1_boxes, _, s1_time_lbl, s1_ph_lbl = self._make_session_row(
            Study2ExperimentalDesign._S1,
            S1_Y,
            r"\textbf{Session 1 :} Memory task",
            self._RATIONALE_S1_ROW_SCALE,
            self._RATIONALE_S1_ROW_CENTER,
        )
        self._scale_session_label_groups(s1_time_lbl, s1_ph_lbl)

        within_session_anchor = Group(s1_boxes[0], s1_boxes[1])
        within_session_label = Tex(
            "Within-session decoding",
            color=BLACK,
            font_size=18,
        ).next_to(s1_row_group, RIGHT, buff=0.24)
        within_session_label.align_to(within_session_anchor, UP).shift(LEFT * 0.10 + DOWN * 0.02)
        within_session_label.set_opacity(0.92)

        target_hi = SurroundingRectangle(
            s1_boxes[0],
            color=self._GLM_ACCENT,
            stroke_width=2.8,
            buff=0.05,
            corner_radius=0.10,
        )
        delay_hi = SurroundingRectangle(
            s1_boxes[1],
            color=self._DELAY_ACCENT,
            stroke_width=2.8,
            buff=0.05,
            corner_radius=0.10,
        )
        target_hi.set_stroke(opacity=0.90)
        delay_hi.set_stroke(opacity=0.90)

        repeated_note = Tex(
            "Repeated stimuli only",
            color=BLACK,
            font_size=18,
            tex_environment="center",
        ).next_to(within_session_label, DOWN, buff=0.10)
        repeated_note.align_to(within_session_label, LEFT)

        stim_stim_case = self._make_within_session_case(
            left_source_box=s1_boxes[0],
            right_source_box=s1_boxes[0],
            center=self._RATIONALE_CASE_CENTERS[0],
            train_values=reference_values["stim_train"],
            train_color=self._GLM_ACCENT,
            train_code=r"$S_1$",
            train_phase="Stimulation",
            test_values=reference_values["stim_test"],
            test_color=self._GLM_ACCENT,
            test_code=r"$S_1$",
            test_phase="Stimulation",
            matrix_scale=self._RATIONALE_MATRIX_SCALE,
            matrix_half_spacing=self._RATIONALE_MATRIX_HALF_SPACING,
            phase_font_size=self._RATIONALE_PHASE_FONT_SIZE,
            role_font_size=self._RATIONALE_ROLE_FONT_SIZE,
            phase_label_buff=self._RATIONALE_PHASE_LABEL_BUFF,
        )
        delay_delay_case = self._make_within_session_case(
            left_source_box=s1_boxes[1],
            right_source_box=s1_boxes[1],
            center=self._RATIONALE_CASE_CENTERS[1],
            train_values=reference_values["delay_train"],
            train_color=self._DELAY_ACCENT,
            train_code=r"$D_1$",
            train_phase="Delay",
            test_values=reference_values["delay_test"],
            test_color=self._DELAY_ACCENT,
            test_code=r"$D_1$",
            test_phase="Delay",
            matrix_scale=self._RATIONALE_MATRIX_SCALE,
            matrix_half_spacing=self._RATIONALE_MATRIX_HALF_SPACING,
            phase_font_size=self._RATIONALE_PHASE_FONT_SIZE,
            role_font_size=self._RATIONALE_ROLE_FONT_SIZE,
            phase_label_buff=self._RATIONALE_PHASE_LABEL_BUFF,
        )
        stim_delay_case = self._make_within_session_case(
            left_source_box=s1_boxes[0],
            right_source_box=s1_boxes[1],
            center=self._RATIONALE_CASE_CENTERS[2],
            train_values=reference_values["stim_train"],
            train_color=self._GLM_ACCENT,
            train_code=r"$S_1$",
            train_phase="Stimulation",
            test_values=reference_values["delay_train"],
            test_color=self._DELAY_ACCENT,
            test_code=r"$D_1$",
            test_phase="Delay",
            matrix_scale=self._RATIONALE_MATRIX_SCALE,
            matrix_half_spacing=self._RATIONALE_MATRIX_HALF_SPACING,
            phase_font_size=self._RATIONALE_PHASE_FONT_SIZE,
            role_font_size=self._RATIONALE_ROLE_FONT_SIZE,
            phase_label_buff=self._RATIONALE_PHASE_LABEL_BUFF,
        )
        matrix_triptych = Group(
            stim_stim_case["group"],
            delay_delay_case["group"],
            stim_delay_case["group"],
        )

        frame = Group(
            question_title,
            s1_title,
            s1_row_group,
            within_session_label,
            target_hi,
            delay_hi,
            repeated_note,
            matrix_triptych,
        )

        return {
            "frame": frame,
            "question_title": question_title,
            "s1_title": s1_title,
            "s1_row_group": s1_row_group,
            "s1_boxes": s1_boxes,
            "within_session_label": within_session_label,
            "target_hi": target_hi,
            "delay_hi": delay_hi,
            "repeated_note": repeated_note,
            "stim_stim_case": stim_stim_case,
            "delay_delay_case": delay_delay_case,
            "stim_delay_case": stim_delay_case,
            "matrix_triptych": matrix_triptych,
        }

    def _build_results_stage(self) -> dict[str, Mobject]:
        """Build the results stage."""
        reference_values = self._session1_reference_values()
        plot_title_y = self.slide_title.get_bottom()[1] - 0.95
        act2_heading = self._make_results_heading(
            r"Does the encoding code generalise\\to the delay?",
            color=BLACK,
            font_size=24,
        ).move_to(self.slide_title)

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
        glm_left_group = self._glm_svg_group(glm_svg, _CROSSSESSION_STIM_SCATTER_HEX, "left")
        glm_right_group = self._glm_svg_group(glm_svg, _CROSSSESSION_DELAY_SCATTER_HEX, "right")
        glm_left_significance = self._glm_svg_significance_marker(
            glm_svg,
            _CROSSSESSION_STIM_SCATTER_HEX,
            "left",
        )
        glm_right_significance = self._glm_svg_significance_marker(
            glm_svg,
            _CROSSSESSION_DELAY_SCATTER_HEX,
            "right",
        )
        glm_title = Tex("GLM-based decoding", color=INK, font_size=22).move_to(
            np.array([glm_plot_frame.get_left()[0] - 0.35, plot_title_y, 0.0])
        )
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
        glm_plot_scaffold = Group(
            glm_plot_frame,
            glm_plot_rest,
            glm_chance_line,
            glm_chance_label,
        )
        glm_left_cloud = VGroup(glm_left_points, glm_left_extras, glm_left_label)
        glm_right_cloud = VGroup(glm_right_points, glm_right_extras, glm_right_label)
        glm_significance = VGroup(glm_left_significance, glm_right_significance)

        glm_left_train = self._make_small_results_matrix(
            reference_values["stim_train"],
            self._GLM_ACCENT,
            r"$S_1$",
            label_direction=UP,
        ).scale(0.82)
        glm_right_train = self._make_small_results_matrix(
            reference_values["delay_train"],
            self._DELAY_ACCENT,
            r"$D_1$",
            label_direction=UP,
        ).scale(0.82)
        glm_left_test = self._make_small_results_matrix(
            reference_values["stim_test"],
            self._GLM_ACCENT,
            r"$S_1$",
            label_direction=DOWN,
        ).scale(0.82)
        glm_right_test = self._make_small_results_matrix(
            reference_values["delay_test"],
            self._DELAY_ACCENT,
            r"$D_1$",
            label_direction=DOWN,
        ).scale(0.82)

        matrix_band_center_y = (glm_title.get_bottom()[1] + glm_plot_frame.get_top()[1]) / 2
        matrix_row_gap = 0.74
        glm_train_y = matrix_band_center_y + matrix_row_gap / 2
        glm_test_y = matrix_band_center_y - matrix_row_gap / 2
        self._position_small_results_matrix(
            glm_left_train,
            np.array([glm_left_x, glm_train_y, 0.0]),
            label_direction=UP,
        )
        self._position_small_results_matrix(
            glm_right_train,
            np.array([glm_right_x, glm_train_y, 0.0]),
            label_direction=UP,
        )
        self._position_small_results_matrix(
            glm_left_test,
            np.array([glm_left_x, glm_test_y, 0.0]),
            label_direction=DOWN,
        )
        self._position_small_results_matrix(
            glm_right_test,
            np.array([glm_right_x, glm_test_y, 0.0]),
            label_direction=DOWN,
        )

        glm_left_column_arrow = Arrow(
            glm_left_train[1].get_bottom() + DOWN * 0.05,
            glm_left_test[1].get_top() + UP * 0.05,
            color=_D_MGREY,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.10,
        )
        glm_right_column_arrow = Arrow(
            glm_right_train[1].get_bottom() + DOWN * 0.05,
            glm_right_test[1].get_top() + UP * 0.05,
            color=_D_MGREY,
            stroke_width=1.7,
            buff=0.02,
            tip_length=0.10,
        )
        glm_left_column = Group(
            glm_left_train,
            glm_left_test,
            glm_left_column_arrow,
        )
        glm_right_column = Group(
            glm_right_train,
            glm_right_test,
            glm_right_column_arrow,
        )
        glm_left_train_explainer = VGroup(
            Tex("Train on", color=INK, font_size=16),
            Tex("Stimulation", color=self._GLM_ACCENT, font_size=16),
            Tex("Session 1", color=self._GLM_ACCENT, font_size=16),
        ).arrange(DOWN, buff=0.03, aligned_edge=RIGHT)
        glm_left_test_explainer = VGroup(
            Tex("Test on", color=INK, font_size=16),
            Tex("Stimulation", color=self._GLM_ACCENT, font_size=16),
            Tex("Session 1", color=self._GLM_ACCENT, font_size=16),
        ).arrange(DOWN, buff=0.03, aligned_edge=RIGHT)
        glm_right_train_explainer = VGroup(
            Tex("Train on", color=INK, font_size=16),
            Tex("Delay", color=self._DELAY_ACCENT, font_size=16),
            Tex("Session 1", color=self._DELAY_ACCENT, font_size=16),
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        glm_right_test_explainer = VGroup(
            Tex("Test on", color=INK, font_size=16),
            Tex("Delay", color=self._DELAY_ACCENT, font_size=16),
            Tex("Session 1", color=self._DELAY_ACCENT, font_size=16),
        ).arrange(DOWN, buff=0.03, aligned_edge=LEFT)
        glm_left_train_explainer.next_to(glm_left_train[1], LEFT, buff=0.16)
        glm_left_test_explainer.next_to(glm_left_test[1], LEFT, buff=0.16)
        glm_right_train_explainer.next_to(glm_right_train[1], RIGHT, buff=0.16)
        glm_right_test_explainer.next_to(glm_right_test[1], RIGHT, buff=0.16)
        glm_plot = Group(
            glm_title,
            glm_plot_scaffold,
            glm_left_column,
            glm_right_column,
            glm_left_train_explainer,
            glm_left_test_explainer,
            glm_right_train_explainer,
            glm_right_test_explainer,
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
        tempgen_underlay, tempgen_source_frame = self._load_tempgen_svg_with_frame(
            center=tempgen_center,
            height=3.55,
        )
        tempgen_source_frame.set_opacity(0.0)
        tempgen_underlay.set_opacity(0.86)
        tempgen_plot_frame = tempgen_source_frame.copy().set_stroke(
            color="#262626",
            width=1.8,
        )
        tempgen_overlay = self._tempgen_plot_clip_masks(
            tempgen_underlay,
            tempgen_plot_frame,
            z_index=3.0,
        )
        tempgen_colorbar_mask = self._make_tempgen_colorbar_mask(
            tempgen_plot_frame,
            z_index=2.15,
        )
        tempgen_colorbar_gradient = self._make_tempgen_colorbar_gradient_overlay(
            tempgen_plot_frame,
            z_index=2.16,
        )
        tempgen_plot_frame.set_z_index(4)
        tempgen_underlay_final_opacity = 0.86
        tempgen_underlay.set_opacity(tempgen_underlay_final_opacity)
        tempgen_underlay.set_z_index(1)
        tempgen_overlay.set_z_index(3)
        tempgen_plot = Group(
            tempgen_title,
            tempgen_underlay,
            tempgen_colorbar_mask,
            tempgen_colorbar_gradient,
            tempgen_plot_frame,
            tempgen_overlay,
        )

        stim_small = self._make_small_results_matrix(
            reference_values["stim_train"],
            self._GLM_ACCENT,
            r"$S_1$",
            label_direction=UP,
        )
        delay_small = self._make_small_results_matrix(
            reference_values["delay_train"],
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
            color=INK,
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

        return {
            "act2_heading": act2_heading,
            "glm_title": glm_title,
            "glm_plot_scaffold": glm_plot_scaffold,
            "glm_plot_frame": glm_plot_frame,
            "glm_plot_rest": glm_plot_rest,
            "glm_chance_line": glm_chance_line,
            "glm_chance_label": glm_chance_label,
            "glm_left_train": glm_left_train,
            "glm_right_train": glm_right_train,
            "glm_left_test": glm_left_test,
            "glm_right_test": glm_right_test,
            "glm_left_column_arrow": glm_left_column_arrow,
            "glm_right_column_arrow": glm_right_column_arrow,
            "glm_left_column": glm_left_column,
            "glm_right_column": glm_right_column,
            "glm_left_train_explainer": glm_left_train_explainer,
            "glm_left_test_explainer": glm_left_test_explainer,
            "glm_right_train_explainer": glm_right_train_explainer,
            "glm_right_test_explainer": glm_right_test_explainer,
            "glm_left_cloud": glm_left_cloud,
            "glm_right_cloud": glm_right_cloud,
            "glm_left_points": glm_left_points,
            "glm_left_extras": glm_left_extras,
            "glm_left_label": glm_left_label,
            "glm_right_points": glm_right_points,
            "glm_right_extras": glm_right_extras,
            "glm_right_label": glm_right_label,
            "glm_left_significance": glm_left_significance,
            "glm_right_significance": glm_right_significance,
            "glm_significance": glm_significance,
            "glm_plot": glm_plot,
            "timeres_title": timeres_title,
            "timeres_base": timeres_base,
            "timeres_trace": timeres_trace,
            "timeres_ci": timeres_ci,
            "timeres_sig_bands": timeres_sig_bands,
            "timeres_plot": timeres_plot,
            "act1_takeaway": act1_takeaway,
            "glm2_title": glm2_title,
            "glm2_plot_frame": glm2_plot_frame,
            "glm2_plot_rest": glm2_plot_rest,
            "glm2_chance_line": glm2_chance_line,
            "glm2_chance_label": glm2_chance_label,
            "glm2_points": glm2_points,
            "glm2_extras": glm2_extras,
            "glm2_label": glm2_label,
            "glm2_sig": glm2_sig,
            "glm2_plot": glm2_plot,
            "tempgen_title": tempgen_title,
            "tempgen_underlay": tempgen_underlay,
            "tempgen_underlay_final_opacity": tempgen_underlay_final_opacity,
            "tempgen_plot_frame": tempgen_plot_frame,
            "tempgen_overlay": tempgen_overlay,
            "tempgen_colorbar_mask": tempgen_colorbar_mask,
            "tempgen_colorbar_gradient": tempgen_colorbar_gradient,
            "tempgen_plot": tempgen_plot,
            "stim_small": stim_small,
            "delay_small": delay_small,
            "cross_phase_arrow": cross_phase_arrow,
            "cross_phase_label": cross_phase_label,
            "act2_takeaway": act2_takeaway,
        }

    def _build_within_session_timeres_context(
        self,
        ctx: dict[str, Mobject],
    ) -> dict[str, Mobject]:
        """Build the within session time-resolved context."""
        timeres_svg = self._load_svg_plot(
            self._RESULTS_TIMERES,
            center=ctx["timeres_base"].get_center(),
            height=ctx["timeres_base"].height,
        )
        self._hide_svg_background_rect(timeres_svg)
        timeres_source_frame = self._svg_plot_frame_from_long_lines(
            timeres_svg,
            min_span_ratio=0.62,
        )
        timeres_frame = ctx["glm_plot_frame"].copy()
        timeres_frame.set_x(timeres_source_frame.get_center()[0])
        timeres_frame.align_to(ctx["glm_plot_frame"], DOWN)
        pixel_step_x = config.frame_width / config.pixel_width
        ref_phase = (ctx["glm_plot_frame"].get_left()[0] / pixel_step_x) % 1.0
        timeres_phase = (timeres_frame.get_left()[0] / pixel_step_x) % 1.0
        phase_delta = ((ref_phase - timeres_phase + 0.5) % 1.0) - 0.5
        timeres_frame.shift(RIGHT * (phase_delta * pixel_step_x))

        timeres_ci = self._timeres_select_single(timeres_svg, fill_hex="#6E6E6E", min_points=100)
        timeres_trace_source = self._timeres_select_single(
            timeres_svg,
            stroke_hex="#000000",
            min_points=50,
        )
        timeres_sig_bands = self._timeres_significance_bands(timeres_svg)
        zero_line_candidates = [
            submob
            for submob in timeres_svg.submobjects
            if len(submob.get_all_points()) >= 4
            if self._glm_svg_hex(submob.get_stroke_color()) == "#999999"
            if submob.width > timeres_source_frame.width * 0.8
            if submob.width >= submob.height
        ]
        zero_line_source = (
            max(zero_line_candidates, key=lambda mob: mob.width)
            if zero_line_candidates
            else None
        )
        timeres_hrf_rect_sources = VGroup(
            self._timeres_select_single(
                timeres_svg,
                fill_hex=_CROSSSESSION_DELAY_SCATTER_HEX,
                min_points=4,
            ),
            self._timeres_select_single(timeres_svg, fill_hex="#7570B3", min_points=4),
            self._timeres_select_single(timeres_svg, fill_hex="#000000", min_points=4),
        )
        timeres_hrf_line_sources = VGroup(
            *self._timeres_select_many(
                timeres_svg,
                stroke_hex=_CROSSSESSION_DELAY_SCATTER_HEX,
                min_points=200,
            ),
            *self._timeres_select_many(
                timeres_svg,
                stroke_hex=_CROSSSESSION_STIM_SCATTER_HEX,
                min_points=200,
            ),
        )
        excluded_ids = {
            id(submob)
            for submob in [
                timeres_ci,
                timeres_trace_source,
                *timeres_source_frame,
                *timeres_sig_bands,
                *timeres_hrf_rect_sources,
                *timeres_hrf_line_sources,
            ]
        }
        timeres_plot_rest_source = VGroup(*[
            submob.copy()
            for submob in timeres_svg.submobjects
            if submob.get_fill_opacity() > 0.0 or submob.get_stroke_opacity() > 0.0
            if id(submob) not in excluded_ids
        ])
        timeres_plot_rest = self._remap_plot_mobject(
            timeres_plot_rest_source,
            timeres_source_frame,
            timeres_frame,
        )
        timeres_ci = self._remap_plot_mobject(
            timeres_ci.copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_ci.set_stroke(opacity=0.0)
        timeres_ci.set_fill(color="#6E6E6E", opacity=0.28)
        timeres_trace_template = self._remap_plot_mobject(
            timeres_trace_source.copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_trace_template.set_fill(opacity=0.0)
        timeres_trace_template.set_stroke(color=BLACK, width=5.0)
        timeres_sig_bands = self._remap_plot_mobject(
            timeres_sig_bands.copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_sig_bands.set_stroke(color="#C49A00", width=4.2)

        timeres_hrf_rectangles = self._remap_plot_mobject(
            timeres_hrf_rect_sources.copy(),
            timeres_source_frame,
            timeres_frame,
        )

        def make_diagonal_striped_rect(template: Mobject) -> VGroup:
            """Build a diagonally striped highlight rectangle."""
            x0, x1 = template.get_left()[0], template.get_right()[0]
            y0, y1 = template.get_bottom()[1], template.get_top()[1]
            background = Rectangle(
                width=template.width,
                height=template.height,
                stroke_width=0.0,
            ).set_fill(WHITE, opacity=1.0).move_to(template)

            def stripe_segment(diagonal_offset: float) -> tuple[np.ndarray, np.ndarray] | None:
                """Build one diagonal stripe segment."""
                candidates = [
                    np.array([x0, x0 + diagonal_offset, 0.0]),
                    np.array([x1, x1 + diagonal_offset, 0.0]),
                    np.array([y0 - diagonal_offset, y0, 0.0]),
                    np.array([y1 - diagonal_offset, y1, 0.0]),
                ]
                points: list[np.ndarray] = []
                for point in candidates:
                    if x0 - 1e-6 <= point[0] <= x1 + 1e-6 and y0 - 1e-6 <= point[1] <= y1 + 1e-6:
                        if not any(np.linalg.norm(point - other) < 1e-6 for other in points):
                            points.append(point)
                if len(points) < 2:
                    return None
                max_pair = None
                max_distance = -1.0
                for idx_a in range(len(points)):
                    for idx_b in range(idx_a + 1, len(points)):
                        distance = np.linalg.norm(points[idx_a] - points[idx_b])
                        if distance > max_distance:
                            max_distance = distance
                            max_pair = (points[idx_a], points[idx_b])
                return max_pair

            stripe_spacing = template.height * 0.42
            stripe_group = VGroup()
            diagonal_min = y0 - x1
            diagonal_max = y1 - x0
            for diagonal_offset in np.arange(
                diagonal_min - stripe_spacing,
                diagonal_max + 2 * stripe_spacing,
                stripe_spacing,
            ):
                segment = stripe_segment(float(diagonal_offset))
                if segment is None:
                    continue
                stripe_group.add(Line(
                    segment[0],
                    segment[1],
                    color=self._GLM_ACCENT,
                    stroke_width=2.2,
                    stroke_opacity=0.95,
                ))

            border = Rectangle(
                width=template.width,
                height=template.height,
                stroke_color=self._GLM_ACCENT,
                stroke_width=max(template.get_stroke_width(), 0.8),
            ).set_fill(opacity=0.0).move_to(template)
            border.set_stroke(opacity=0.20)
            return VGroup(background, stripe_group, border)

        timeres_hrf_rectangles = VGroup(
            timeres_hrf_rectangles[0],
            timeres_hrf_rectangles[1],
            make_diagonal_striped_rect(timeres_hrf_rectangles[2]),
        )
        timeres_hrf_lines = self._remap_plot_mobject(
            timeres_hrf_line_sources.copy(),
            timeres_source_frame,
            timeres_frame,
        )
        timeres_trace_start_x = timeres_trace_template.get_left()[0]
        for line in timeres_hrf_lines:
            line.shift(RIGHT * (timeres_trace_start_x - line.get_left()[0]))

        timeres_plot_scaffold = VGroup(
            timeres_frame,
            timeres_plot_rest,
        )
        timeres_title = ctx.get(
            "shared_timeres_title",
            ctx["timeres_title"],
        ).copy()

        trace_sample_props = np.linspace(0.0, 1.0, 2400)
        trace_sample_points = np.array([
            timeres_trace_template.point_from_proportion(float(prop))
            for prop in trace_sample_props
        ])
        trace_sort_order = np.argsort(trace_sample_points[:, 0])
        trace_sample_points = trace_sample_points[trace_sort_order]
        trace_sample_props = trace_sample_props[trace_sort_order]
        trace_sample_xs = trace_sample_points[:, 0]
        trace_sample_ys = trace_sample_points[:, 1]
        trace_unique_xs, trace_unique_idx = np.unique(trace_sample_xs, return_index=True)
        trace_unique_props = trace_sample_props[trace_unique_idx]
        trace_unique_ys = trace_sample_ys[trace_unique_idx]

        timeres_trace_xs = np.linspace(
            timeres_frame.get_left()[0],
            timeres_frame.get_right()[0],
            25,
        )
        test_strip_y = timeres_frame.get_top()[1] + 0.42
        train_strip_y = test_strip_y + 0.34
        design_strip_y = train_strip_y + 0.43
        timeres_bin_spacing = timeres_trace_xs[1] - timeres_trace_xs[0]
        timeres_bin_width = timeres_bin_spacing * 0.74
        timeres_bin_height = 0.23
        timeres_total_time = 19.2
        design_track_height = timeres_bin_height + 0.03
        design_fill_height = design_track_height - 0.06
        design_start_x = timeres_trace_xs[0]
        design_end_x = timeres_trace_xs[-1]
        event_boundary_times = [2.0, 10.0, 12.5, 14.5]
        zero_line_y = (
            self._remap_plot_mobject(
                zero_line_source.copy(),
                timeres_source_frame,
                timeres_frame,
            ).get_center()[1]
            if zero_line_source is not None
            else timeres_frame.get_bottom()[1] + timeres_frame.height * 0.12
        )
        design_center = np.array([
            (design_start_x + design_end_x) / 2,
            design_strip_y,
            0.0,
        ])

        def phase_color(step_value: float) -> ManimColor:
            """Return the colour assigned to the current phase."""
            current_time = float(
                interpolate(
                    0.0,
                    timeres_total_time,
                    np.clip(step_value / (len(timeres_trace_xs) - 1), 0.0, 1.0),
                )
            )
            if current_time < 2.0:
                return self._GLM_ACCENT
            if current_time < 10.0:
                return self._DELAY_ACCENT
            if current_time < 12.5:
                return self._GLM_ACCENT
            return ManimColor(_D_MGREY)

        def time_to_x(time_s: float) -> float:
            """Map a time index onto the x-axis position."""
            return float(interpolate(
                design_start_x,
                design_end_x,
                np.clip(time_s / timeres_total_time, 0.0, 1.0),
            ))

        def make_design_icon(
            img_path: str | None,
            start_s: float,
            end_s: float,
            *,
            resp: bool = False,
        ) -> Group:
            """Build one compact design icon."""
            icon = _box(img_path, resp=resp)
            icon.scale_to_fit_height(design_fill_height * 0.78)
            max_width = max(time_to_x(end_s) - time_to_x(start_s) - 0.07, 0.08)
            if icon.width > max_width:
                icon.scale_to_fit_width(max_width)
            return icon

        def make_design_phase(
            start_s: float,
            end_s: float,
            fill_color: str,
            fill_opacity: float,
            icon: Mobject | None,
        ) -> Group:
            """Build one compact design phase card."""
            phase_fill = Rectangle(
                width=time_to_x(end_s) - time_to_x(start_s),
                height=design_fill_height,
                stroke_width=0.0,
            ).set_fill(fill_color, opacity=fill_opacity)
            phase_fill.move_to(np.array([
                (time_to_x(start_s) + time_to_x(end_s)) / 2,
                design_strip_y,
                0.0,
            ]))
            parts: list[Mobject] = [phase_fill]
            if icon is not None:
                parts.append(icon.copy().move_to(phase_fill))
            return Group(*parts)

        intro_timepoint = RoundedRectangle(
            width=timeres_bin_width * 1.05,
            height=timeres_bin_height + 0.07,
            corner_radius=0.05,
            stroke_color=phase_color(0.0),
            stroke_width=2.0,
        ).set_fill(phase_color(0.0), opacity=0.18)
        intro_timepoint.move_to(np.array([
            timeres_trace_xs[0],
            train_strip_y,
            0.0,
        ]))
        intro_train_label = Tex(
            "Train",
            color=INK,
            font_size=16,
        ).next_to(intro_timepoint, UP, buff=0.08)
        timeres_train_explainer = VGroup(
            Tex("Train and test on", color=INK, font_size=17),
            Tex("matching trial timepoints", color=INK, font_size=17),
            Tex("Session 1", color=INK, font_size=17),
        ).arrange(DOWN, buff=0.03)

        design_frame = RoundedRectangle(
            width=timeres_bin_width * 1.05,
            height=design_track_height,
            corner_radius=0.05,
            stroke_color=GREY,
            stroke_width=1.3,
        ).set_fill(WHITE, opacity=0.0).move_to(design_center)
        design_frame_target = RoundedRectangle(
            width=design_end_x - design_start_x,
            height=design_track_height,
            corner_radius=0.05,
            stroke_color=GREY,
            stroke_width=1.3,
        ).set_fill(WHITE, opacity=0.0).move_to(design_center)
        timeres_train_explainer.next_to(design_frame_target, UP, buff=0.14)
        explainer_top_limit = min(
            timeres_title.get_bottom()[1] - 0.08,
            config.frame_height / 2 - 0.12,
        )
        explainer_shift_room = explainer_top_limit - timeres_train_explainer.get_top()[1]
        if explainer_shift_room > 0.0:
            timeres_train_explainer.shift(UP * (0.20 * explainer_shift_room))

        design_dividers = VGroup(*[
            Line(
                np.array([time_to_x(boundary), design_strip_y - design_fill_height / 2, 0.0]),
                np.array([time_to_x(boundary), design_strip_y + design_fill_height / 2, 0.0]),
                color=_D_MGREY,
                stroke_width=0.9,
                stroke_opacity=0.55,
            )
            for boundary in event_boundary_times
        ])
        target_phase = make_design_phase(
            0.0,
            2.0,
            self._GLM_ACCENT,
            0.16,
            make_design_icon(LAKE, 0.0, 2.0),
        )
        delay_phase = make_design_phase(
            2.0,
            10.0,
            self._DELAY_ACCENT,
            0.14,
            make_design_icon(None, 2.0, 10.0),
        )
        probe_icons = Group(
            make_design_icon(LAKE_D1, 10.0, 12.5),
            make_design_icon(None, 10.0, 12.5),
            make_design_icon(LAKE_D2, 10.0, 12.5),
        ).arrange(RIGHT, buff=0.03)
        probe_width = max(time_to_x(12.5) - time_to_x(10.0) - 0.07, 0.10)
        if probe_icons.width > probe_width:
            probe_icons.scale_to_fit_width(probe_width)
        probe_phase = make_design_phase(
            10.0,
            12.5,
            self._GLM_ACCENT,
            0.16,
            probe_icons,
        )
        response_phase = make_design_phase(
            12.5,
            14.5,
            _D_LGREY,
            0.20,
            make_design_icon(None, 12.5, 14.5, resp=True),
        )
        rest_phase = make_design_phase(
            14.5,
            timeres_total_time,
            _D_LGREY,
            0.10,
            VGroup(*[
                Dot(radius=0.014, color=_D_MGREY, fill_opacity=0.70)
                for _ in range(3)
            ]).arrange(RIGHT, buff=0.05),
        )
        design_phases = Group(
            target_phase,
            delay_phase,
            probe_phase,
            response_phase,
            rest_phase,
        )
        experimental_design = Group(design_frame, design_dividers, design_phases)
        design_label_y = design_frame_target.get_bottom()[1] - 0.20

        def make_design_phase_label(text: str, center_x: float, color: str) -> Tex:
            """Build the label for one compact design phase."""
            return Tex(
                rf"\textbf{{{text}}}",
                color=color,
                font_size=20,
            ).move_to(np.array([center_x, design_label_y, 0.0]))

        design_stimulation_label = make_design_phase_label(
            "Stimulation",
            target_phase.get_center()[0],
            self._GLM_ACCENT,
        )
        design_delay_label = make_design_phase_label(
            "Delay",
            delay_phase.get_center()[0],
            self._DELAY_ACCENT,
        )
        design_probes_label = make_design_phase_label(
            "Probes",
            probe_phase.get_center()[0],
            self._GLM_ACCENT,
        )
        design_response_label = make_design_phase_label(
            "Response",
            response_phase.get_center()[0],
            INK,
        )

        train_time_bins = VGroup(*[
            RoundedRectangle(
                width=timeres_bin_width,
                height=timeres_bin_height,
                corner_radius=0.03,
                stroke_color=GREY,
                stroke_width=1.0,
            ).set_fill(WHITE, opacity=1.0).move_to(np.array([x, train_strip_y, 0.0]))
            for x in timeres_trace_xs
        ])
        test_time_bins = VGroup(*[
            RoundedRectangle(
                width=timeres_bin_width,
                height=timeres_bin_height,
                corner_radius=0.03,
                stroke_color=GREY,
                stroke_width=1.0,
            ).set_fill(WHITE, opacity=1.0).move_to(np.array([x, test_strip_y, 0.0]))
            for x in timeres_trace_xs
        ])
        time_rows = VGroup(train_time_bins, test_time_bins)
        train_row_label = Tex(
            "Train",
            color=INK,
            font_size=16,
        ).next_to(train_time_bins, LEFT, buff=0.10)
        test_row_label = Tex(
            "Test",
            color=INK,
            font_size=16,
        ).next_to(test_time_bins, LEFT, buff=0.14)
        trs_label = Tex(
            "TRs",
            color=INK,
            font_size=16,
        ).next_to(time_rows, RIGHT, buff=0.10)

        step_tracker = ValueTracker(0)

        def sweep_target_x(step_value: float) -> float:
            """Return the current x target for the sweep animation."""
            step_value = float(np.clip(step_value, 0.0, len(train_time_bins) - 1))
            return float(interpolate(
                timeres_trace_xs[0],
                timeres_trace_xs[-1],
                step_value / (len(train_time_bins) - 1),
            ))

        def current_curve_point() -> np.ndarray:
            """Return the current point on the animated curve."""
            target_x = sweep_target_x(step_tracker.get_value())
            return np.array([
                target_x,
                float(np.interp(target_x, trace_unique_xs, trace_unique_ys)),
                0.0,
            ])

        def current_trace_mobject() -> VMobject:
            """Build the trace mobject for the current animation state."""
            target_x = sweep_target_x(step_tracker.get_value())
            curve_point = current_curve_point()
            idx = int(np.searchsorted(trace_unique_xs, target_x, side="right"))
            points = np.column_stack([
                trace_unique_xs[:max(idx, 1)],
                trace_unique_ys[:max(idx, 1)],
                np.zeros(max(idx, 1)),
            ])
            if np.linalg.norm(points[-1] - curve_point) > 1e-6:
                points = np.vstack([points, curve_point])
            if len(points) < 2:
                points = np.vstack([points[0], curve_point])
            trace = VMobject()
            trace.set_points_as_corners(points)
            trace.set_stroke(
                color=timeres_trace_template.get_stroke_color(),
                width=timeres_trace_template.get_stroke_width(),
                opacity=timeres_trace_template.get_stroke_opacity(),
            )
            trace.set_fill(opacity=0.0)
            if target_x <= trace_unique_xs[0] + 1e-6:
                trace.set_stroke(opacity=0.0)
            return trace

        plot_trace = always_redraw(current_trace_mobject).set_z_index(4)
        plot_trace_head = always_redraw(lambda: Dot(
            current_curve_point(),
            radius=0.040,
            color=BLACK,
            fill_opacity=1.0,
        ).set_stroke(WHITE, width=1.0).set_z_index(5))

        def train_selector_center() -> np.ndarray:
            """Return the centre of the current train selector."""
            return np.array([
                sweep_target_x(step_tracker.get_value()),
                train_strip_y,
                0.0,
            ])

        def test_selector_center() -> np.ndarray:
            """Return the centre of the current test selector."""
            return np.array([
                sweep_target_x(step_tracker.get_value()),
                test_strip_y,
                0.0,
            ])

        train_selector = always_redraw(lambda: RoundedRectangle(
            width=timeres_bin_width + 0.05,
            height=timeres_bin_height + 0.07,
            corner_radius=0.04,
            stroke_color=phase_color(step_tracker.get_value()),
            stroke_width=2.0,
        ).set_fill(
            phase_color(step_tracker.get_value()),
            opacity=0.16,
        ).move_to(train_selector_center()).set_z_index(4))
        test_selector = always_redraw(lambda: RoundedRectangle(
            width=timeres_bin_width + 0.05,
            height=timeres_bin_height + 0.07,
            corner_radius=0.04,
            stroke_color=phase_color(step_tracker.get_value()),
            stroke_width=2.0,
        ).set_fill(
            phase_color(step_tracker.get_value()),
            opacity=0.16,
        ).move_to(test_selector_center()).set_z_index(4))
        plot_cursor = always_redraw(lambda: DashedLine(
            test_selector_center() + DOWN * (timeres_bin_height / 2 + 0.05),
            current_curve_point(),
            color=_D_MGREY,
            stroke_width=1.0,
            dash_length=0.05,
            dashed_ratio=0.65,
        ).set_z_index(3))

        event_projection_lines = VGroup(*[
            DashedLine(
                np.array([
                    time_to_x(boundary),
                    design_strip_y - design_fill_height / 2,
                    0.0,
                ]),
                np.array([
                    time_to_x(boundary),
                    timeres_frame.get_bottom()[1],
                    0.0,
                ]),
                color=_D_MGREY,
                stroke_width=0.9,
                dash_length=0.05,
                dashed_ratio=0.65,
            )
            for boundary in event_boundary_times
        ]).set_z_index(3)
        delay_end_x = time_to_x(10.0)
        ci_sample_props = np.linspace(0.0, 1.0, 3200)
        ci_sample_points = np.array([
            timeres_ci.point_from_proportion(float(prop))
            for prop in ci_sample_props
        ])
        ci_sample_window = max(timeres_frame.width / 300, 0.015)
        ci_points_near_delay_end = ci_sample_points[
            np.abs(ci_sample_points[:, 0] - delay_end_x) <= ci_sample_window
        ]
        if len(ci_points_near_delay_end) > 0:
            delay_end_ci_upper_y = float(np.max(ci_points_near_delay_end[:, 1]))
        else:
            delay_end_ci_upper_y = float(
                ci_sample_points[
                    int(np.argmin(np.abs(ci_sample_points[:, 0] - delay_end_x))),
                    1,
                ]
            )
        delay_end_arrow_length = 0.75
        delay_end_arrow_gap = 0.06
        delay_end_chance_arrow = Arrow(
            np.array([
                delay_end_x,
                delay_end_ci_upper_y + delay_end_arrow_gap + delay_end_arrow_length,
                0.0,
            ]),
            np.array([
                delay_end_x,
                delay_end_ci_upper_y + delay_end_arrow_gap,
                0.0,
            ]),
            color=_D_RED,
            stroke_width=3.6,
            buff=0.0,
            tip_length=0.17,
            tip_shape=StealthTip,
        ).set_z_index(4)

        timeres_plot_scaffold.set_z_index(2)
        timeres_ci.set_z_index(2.5)
        timeres_sig_bands.set_z_index(3)
        timeres_hrf_rectangles.set_z_index(3)
        timeres_hrf_lines.set_z_index(3)

        timeres_full_state_group = Group(
            timeres_title,
            experimental_design,
            timeres_plot_scaffold,
            train_time_bins,
            test_time_bins,
            train_row_label,
            test_row_label,
            trs_label,
            event_projection_lines,
            plot_trace,
            timeres_ci,
            timeres_sig_bands,
            timeres_hrf_rectangles,
            timeres_hrf_lines,
            delay_end_chance_arrow,
        )

        ctx["timeres_frame"] = timeres_frame
        ctx["trace_unique_xs"] = trace_unique_xs
        ctx["trace_unique_ys"] = trace_unique_ys
        ctx["trace_unique_props"] = trace_unique_props
        ctx["timeres_plot_scaffold"] = timeres_plot_scaffold
        ctx["timeres_plot_rest"] = timeres_plot_rest
        ctx["intro_timepoint"] = intro_timepoint
        ctx["intro_train_label"] = intro_train_label
        ctx["timeres_train_explainer"] = timeres_train_explainer
        ctx["design_frame"] = design_frame
        ctx["design_frame_target"] = design_frame_target
        ctx["design_dividers"] = design_dividers
        ctx["target_phase"] = target_phase
        ctx["delay_phase"] = delay_phase
        ctx["probe_phase"] = probe_phase
        ctx["response_phase"] = response_phase
        ctx["rest_phase"] = rest_phase
        ctx["design_stimulation_label"] = design_stimulation_label
        ctx["design_delay_label"] = design_delay_label
        ctx["design_probes_label"] = design_probes_label
        ctx["design_response_label"] = design_response_label
        ctx["experimental_design"] = experimental_design
        ctx["train_time_bins"] = train_time_bins
        ctx["test_time_bins"] = test_time_bins
        ctx["time_bins"] = test_time_bins
        ctx["train_row_label"] = train_row_label
        ctx["test_row_label"] = test_row_label
        ctx["trs_label"] = trs_label
        ctx["step_tracker"] = step_tracker
        ctx["train_selector"] = train_selector
        ctx["test_selector"] = test_selector
        ctx["plot_cursor"] = plot_cursor
        ctx["timeres_title"] = timeres_title
        ctx["timeres_trace"] = plot_trace
        ctx["timeres_trace_head"] = plot_trace_head
        ctx["timeres_ci"] = timeres_ci
        ctx["timeres_sig_bands"] = timeres_sig_bands
        ctx["timeres_hrf_rectangles"] = timeres_hrf_rectangles
        ctx["timeres_hrf_lines"] = timeres_hrf_lines
        ctx["event_projection_lines"] = event_projection_lines
        ctx["delay_end_chance_arrow"] = delay_end_chance_arrow
        ctx["timeres_plot"] = Group(
            timeres_title,
            timeres_plot_scaffold,
            timeres_ci,
            plot_trace,
            timeres_sig_bands,
            timeres_hrf_rectangles,
            timeres_hrf_lines,
            delay_end_chance_arrow,
        )
        ctx["timeres_full_state_group"] = timeres_full_state_group
        return ctx

    def _show_within_session_results_rationale(self, rationale: dict[str, Mobject]) -> None:
        """Animate the within session results rationale."""
        self.add(rationale["frame"])
        self.wait(0.25)

    def _fade_from_within_session_rationale(self, rationale: dict[str, Mobject]) -> None:
        """Return the fade from within session rationale."""
        self.play(
            FadeOut(rationale["s1_title"]),
            FadeOut(rationale["s1_row_group"]),
            FadeOut(rationale["within_session_label"]),
            FadeOut(rationale["target_hi"]),
            FadeOut(rationale["delay_hi"]),
            FadeOut(rationale["repeated_note"]),
            FadeOut(rationale["matrix_triptych"], shift=DOWN * 0.06),
            run_time=0.75,
        )

    def _animate_within_session_act1_results(self, ctx: dict[str, Mobject]) -> None:
        """Animate the within session act-1 results."""
        self.play(
            FadeIn(ctx["glm_title"], shift=UP * 0.05),
            AnimationGroup(
                Create(ctx["glm_plot_frame"]),
                FadeIn(ctx["glm_plot_rest"], shift=UP * 0.08),
                Create(ctx["glm_chance_line"]),
                FadeIn(ctx["glm_chance_label"], shift=UP * 0.04),
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )

        left_cloud_anim = AnimationGroup(
            LaggedStart(
                *[FadeIn(dot, scale=0.75) for dot in ctx["glm_left_points"]],
                lag_ratio=0.04,
            ),
            FadeIn(ctx["glm_left_extras"], shift=UP * 0.04),
            Write(ctx["glm_left_label"]),
            lag_ratio=0.18,
        )
        right_cloud_anim = AnimationGroup(
            LaggedStart(
                *[FadeIn(dot, scale=0.75) for dot in ctx["glm_right_points"]],
                lag_ratio=0.04,
            ),
            FadeIn(ctx["glm_right_extras"], shift=UP * 0.04),
            Write(ctx["glm_right_label"]),
            lag_ratio=0.18,
        )

        self.play(
            AnimationGroup(
                FadeIn(ctx["glm_left_train"], shift=UP * 0.04),
                FadeIn(ctx["glm_left_test"], shift=DOWN * 0.04),
                GrowArrow(ctx["glm_left_column_arrow"]),
                left_cloud_anim,
                lag_ratio=0.16,
            ),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                FadeIn(ctx["glm_right_train"], shift=UP * 0.04),
                FadeIn(ctx["glm_right_test"], shift=DOWN * 0.04),
                GrowArrow(ctx["glm_right_column_arrow"]),
                right_cloud_anim,
                lag_ratio=0.16,
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
                LaggedStart(
                    *[
                        FadeIn(marker, shift=UP * 0.03)
                        for marker in ctx["glm_right_significance"]
                    ],
                    lag_ratio=0.12,
                )
            )
        if significance_anims:
            self.wait(0.35)
            self.play(
                AnimationGroup(*significance_anims, lag_ratio=0.22),
                run_time=0.55,
            )
        self.wait(0.75)

    def _show_within_session_act1_final_state(self, ctx: dict[str, Mobject]) -> None:
        """Animate the within session act-1 final state."""
        self.add(ctx["glm_plot"])

    def _reset_to_within_session_act1_final_state(self, ctx: dict[str, Mobject]) -> None:
        """Animate the to within session act-1 final state."""
        self.clear()
        self._show_within_session_act1_final_state(ctx)

    def _prepare_within_session_resultsb_final_state(
        self,
        timeres_ctx: dict[str, Mobject],
    ) -> None:
        """Animate the within session resultsb final state."""
        timeres_ctx["step_tracker"].set_value(len(timeres_ctx["time_bins"]) - 1)
        timeres_ctx["design_frame"].become(timeres_ctx["design_frame_target"].copy())
        timeres_ctx["timeres_trace"].update()
        timeres_ctx["timeres_trace_head"].update()

    def _show_within_session_resultsb_final_state(
        self,
        timeres_ctx: dict[str, Mobject],
    ) -> None:
        """Animate the within session resultsb final state."""
        self._prepare_within_session_resultsb_final_state(timeres_ctx)
        self.add(
            timeres_ctx["timeres_title"],
            timeres_ctx["timeres_train_explainer"],
            timeres_ctx["experimental_design"],
            timeres_ctx["train_time_bins"],
            timeres_ctx["test_time_bins"],
            timeres_ctx["train_row_label"],
            timeres_ctx["test_row_label"],
            timeres_ctx["trs_label"],
            timeres_ctx["event_projection_lines"],
            timeres_ctx["timeres_plot_scaffold"],
            timeres_ctx["timeres_trace"],
            timeres_ctx["timeres_ci"],
            timeres_ctx["timeres_sig_bands"],
            timeres_ctx["timeres_hrf_rectangles"],
            timeres_ctx["timeres_hrf_lines"],
            timeres_ctx["delay_end_chance_arrow"],
        )

    def _animate_within_session_timeres_results(self, ctx: dict[str, Mobject]) -> None:
        """Animate the within session time-resolved results."""
        self.play(
            FadeIn(ctx["timeres_title"], shift=UP * 0.06),
            FadeIn(ctx["timeres_train_explainer"], shift=UP * 0.05),
            run_time=0.75,
        )
        self.wait(0.25)
        self.play(
            GrowFromCenter(ctx["design_frame"]),
            run_time=0.28,
        )
        self.play(
            Transform(ctx["design_frame"], ctx["design_frame_target"]),
            FadeIn(ctx["design_dividers"]),
            run_time=0.7,
        )
        self.play(
            FadeIn(
                Group(
                    ctx["target_phase"],
                    ctx["delay_phase"],
                    ctx["probe_phase"],
                    ctx["response_phase"],
                    ctx["rest_phase"],
                ),
                scale=0.96,
            ),
            run_time=0.55,
        )
        self.play(
            FadeIn(ctx["timeres_plot_scaffold"], shift=UP * 0.08),
            LaggedStart(
                *[FadeIn(bin_mob, shift=UP * 0.03) for bin_mob in ctx["train_time_bins"]],
                lag_ratio=0.03,
            ),
            LaggedStart(
                *[FadeIn(bin_mob, shift=UP * 0.03) for bin_mob in ctx["test_time_bins"]],
                lag_ratio=0.03,
            ),
            FadeIn(ctx["train_row_label"], shift=RIGHT * 0.04),
            FadeIn(ctx["test_row_label"], shift=RIGHT * 0.04),
            FadeIn(ctx["trs_label"], shift=RIGHT * 0.04),
            FadeIn(ctx["train_selector"]),
            FadeIn(ctx["test_selector"]),
            FadeIn(ctx["plot_cursor"]),
            FadeIn(ctx["timeres_trace"]),
            FadeIn(ctx["timeres_trace_head"]),
            run_time=0.8,
        )
        self.wait(0.2)
        self.add(ctx["train_selector"])
        self.play(
            ctx["step_tracker"].animate.set_value(len(ctx["time_bins"]) - 1),
            run_time=0.5 * (len(ctx["time_bins"]) - 1),
            rate_func=linear,
        )

        train_selector_static = ctx["train_selector"].copy()
        train_selector_static.clear_updaters()
        test_selector_static = ctx["test_selector"].copy()
        test_selector_static.clear_updaters()
        self.remove(ctx["train_selector"], ctx["test_selector"])
        self.add(train_selector_static, test_selector_static)
        self.play(
            FadeOut(train_selector_static),
            FadeOut(test_selector_static),
            FadeOut(ctx["plot_cursor"]),
            FadeOut(ctx["timeres_trace_head"]),
            LaggedStart(
                *[Create(line) for line in ctx["event_projection_lines"]],
                lag_ratio=0.08,
            ),
            run_time=0.65,
        )
        self.play(
            AnimationGroup(
                FadeIn(ctx["timeres_ci"]),
                LaggedStart(
                    *[Create(sig_band) for sig_band in ctx["timeres_sig_bands"]],
                    lag_ratio=0.12,
                ),
                lag_ratio=0.12,
            ),
            run_time=0.75,
        )
        self.play(
            AnimationGroup(
                FadeIn(ctx["timeres_hrf_rectangles"]),
                LaggedStart(
                    *[Create(line) for line in ctx["timeres_hrf_lines"]],
                    lag_ratio=0.12,
                ),
                lag_ratio=0.12,
            ),
            run_time=0.70,
        )
        self.play(
            GrowArrow(
                ctx["delay_end_chance_arrow"],
                rate_func=smooth,
            ),
            run_time=0.72,
        )
        for _ in range(3):
            self.play(
                ctx["delay_end_chance_arrow"].animate(
                    rate_func=there_and_back,
                ).shift(DOWN * 0.045),
                run_time=0.42,
            )
        self.wait(2.0)

    def _build_within_session_tempgen_logic_context(
        self,
        ctx: dict[str, Mobject],
        timeres_ctx: dict[str, Mobject],
    ) -> dict[str, object]:
        """Build the within session temporal-generalisation logic context."""
        logic_matrix_frame = ctx["tempgen_plot_frame"].copy().move_to(
            ctx["glm2_plot_frame"].get_center()
        )
        logic_matrix_frame.set_stroke(color="#2F2F2F", width=2.0, opacity=0.92)
        logic_matrix_frame.set_z_index(4.05)

        design_stacked_target = timeres_ctx["experimental_design"].copy()
        design_stacked_target.scale_to_fit_width(logic_matrix_frame.width)
        train_bins_stacked_target = timeres_ctx["train_time_bins"].copy()
        train_bins_stacked_target.scale_to_fit_width(logic_matrix_frame.width)
        test_bins_stacked_target = timeres_ctx["test_time_bins"].copy()
        test_bins_stacked_target.scale_to_fit_width(logic_matrix_frame.width)

        stacked_center_x = ctx["glm2_plot_frame"].get_center()[0]
        stacked_train_y = ctx["glm2_plot_frame"].get_center()[1] - 0.10
        stacked_test_gap = 0.18
        stacked_design_gap = 0.26
        train_bins_stacked_target.move_to(np.array([stacked_center_x, stacked_train_y, 0.0]))
        test_bins_stacked_target.next_to(train_bins_stacked_target, DOWN, buff=stacked_test_gap)
        design_stacked_target.next_to(train_bins_stacked_target, UP, buff=stacked_design_gap)

        train_label_stacked_target = timeres_ctx["train_row_label"].copy()
        train_label_stacked_target.next_to(train_bins_stacked_target, LEFT, buff=0.10)

        test_label_stacked_target = timeres_ctx["test_row_label"].copy()
        test_label_stacked_target.next_to(test_bins_stacked_target, LEFT, buff=0.14)

        logic_axis_seconds_gap = 0.42

        design_target = timeres_ctx["experimental_design"].copy()
        design_target.scale_to_fit_width(logic_matrix_frame.width)
        design_target.next_to(logic_matrix_frame, UP, buff=0.38)

        train_bins_target = timeres_ctx["train_time_bins"].copy()
        train_bins_target.scale_to_fit_width(logic_matrix_frame.width)
        train_bins_target.next_to(logic_matrix_frame, DOWN, buff=logic_axis_seconds_gap)

        test_bins_target = timeres_ctx["test_time_bins"].copy()
        test_bins_target.rotate(PI / 2)
        test_bins_target.scale_to_fit_height(logic_matrix_frame.height)
        test_bins_target.next_to(logic_matrix_frame, LEFT, buff=logic_axis_seconds_gap)

        train_label_target = Tex(
            "Train time (s)",
            color=INK,
            font_size=16,
        )
        train_label_target.next_to(train_bins_target, DOWN, buff=0.12)

        test_label_target = Tex(
            "Test time (s)",
            color=INK,
            font_size=16,
        )
        test_label_target.next_to(test_bins_target, LEFT, buff=0.12)

        for mob in [
            design_stacked_target,
            train_bins_stacked_target,
            test_bins_stacked_target,
            train_label_stacked_target,
            test_label_stacked_target,
            design_target,
            train_bins_target,
            test_bins_target,
            train_label_target,
            test_label_target,
        ]:
            mob.set_z_index(4.25)

        cell_count = len(train_bins_target)

        def axis_spacing(axis_values: np.ndarray, fallback: float) -> float:
            """Return the spacing between the active axis anchors."""
            if len(axis_values) <= 1:
                return fallback
            deltas = np.abs(np.diff(axis_values))
            deltas = deltas[deltas > 1e-6]
            if len(deltas) == 0:
                return fallback
            return float(np.mean(deltas))

        train_center_xs = np.array([
            bin_mobject.get_center()[0]
            for bin_mobject in train_bins_target
        ])
        test_center_ys = np.array([
            bin_mobject.get_center()[1]
            for bin_mobject in test_bins_target
        ])
        cell_width = axis_spacing(train_center_xs, train_bins_target[0].width)
        cell_height = axis_spacing(test_center_ys, test_bins_target[0].height)
        cell_size = min(cell_width, cell_height)
        matrix_left = float(logic_matrix_frame.get_left()[0])
        matrix_right = float(logic_matrix_frame.get_right()[0])
        matrix_bottom = float(logic_matrix_frame.get_bottom()[1])
        matrix_top = float(logic_matrix_frame.get_top()[1])
        matrix_total_time = 19.2

        def matrix_time_to_x(time_s: float) -> float:
            """Map a matrix time index onto the x-axis position."""
            return float(interpolate(
                matrix_left,
                matrix_right,
                np.clip(time_s / matrix_total_time, 0.0, 1.0),
            ))

        def matrix_time_to_y(time_s: float) -> float:
            """Map a matrix time index onto the y-axis position."""
            return float(interpolate(
                matrix_bottom,
                matrix_top,
                np.clip(time_s / matrix_total_time, 0.0, 1.0),
            ))

        axis_tick_specs = [
            (0.0, "0"),
            (5.0, "5"),
            (10.0, "10"),
            (15.0, "15"),
        ]
        matrix_x_ticks = VGroup()
        for tick_time, tick_label in axis_tick_specs:
            tick_x = matrix_time_to_x(tick_time)
            tick_mark = Line(
                np.array([tick_x, logic_matrix_frame.get_bottom()[1], 0.0]),
                np.array([tick_x, logic_matrix_frame.get_bottom()[1] - 0.055, 0.0]),
                color="#5A5A5A",
                stroke_width=1.2,
            )
            tick_text = Tex(tick_label, color=INK, font_size=15).next_to(
                tick_mark,
                DOWN,
                buff=0.05,
            )
            matrix_x_ticks.add(VGroup(tick_mark, tick_text))
        matrix_x_ticks.set_z_index(4.15)
        matrix_y_ticks = VGroup()
        for tick_time, tick_label in axis_tick_specs:
            tick_y = matrix_time_to_y(tick_time)
            tick_mark = Line(
                np.array([logic_matrix_frame.get_left()[0], tick_y, 0.0]),
                np.array([logic_matrix_frame.get_left()[0] - 0.055, tick_y, 0.0]),
                color="#5A5A5A",
                stroke_width=1.2,
            )
            tick_text = Tex(tick_label, color=INK, font_size=15).next_to(
                tick_mark,
                LEFT,
                buff=0.05,
            )
            matrix_y_ticks.add(VGroup(tick_mark, tick_text))
        matrix_y_ticks.set_z_index(4.15)

        logic_matrix_svg, logic_matrix_source_frame = self._load_tempgen_svg_with_frame(
            center=logic_matrix_frame.get_center(),
            height=logic_matrix_frame.height + 0.10,
        )
        logic_matrix_source_frame.set_opacity(0.0)
        logic_matrix_panel = self._remap_plot_mobject(
            logic_matrix_svg,
            logic_matrix_source_frame,
            logic_matrix_frame,
        )
        logic_matrix_panel.set_z_index(2.1)
        logic_matrix_colorbar_mask = self._make_tempgen_colorbar_mask(
            logic_matrix_frame,
            z_index=2.12,
        )
        logic_matrix_colorbar_gradient = self._make_tempgen_colorbar_gradient_overlay(
            logic_matrix_frame,
            z_index=2.13,
        )
        logic_matrix_label_masks = self._tempgen_plot_clip_masks(
            logic_matrix_panel,
            logic_matrix_frame,
            bottom_min_height=logic_matrix_panel.height * 0.18,
            right_gutter_width=cell_width * 0.55,
            top_gutter_height=cell_height * 0.55,
            z_index=2.2,
        )
        logic_matrix_underlay = VGroup(logic_matrix_panel, logic_matrix_label_masks)

        def interpolated_center(bin_group: VGroup, value: float) -> np.ndarray:
            """Return the interpolated centre for the current transition."""
            low_idx = int(np.clip(np.floor(value), 0, len(bin_group) - 1))
            high_idx = min(low_idx + 1, len(bin_group) - 1)
            alpha = float(np.clip(value - low_idx, 0.0, 1.0))
            return interpolate(
                bin_group[low_idx].get_center(),
                bin_group[high_idx].get_center(),
                alpha,
            )

        def axis_center(axis_values: np.ndarray, value: float) -> float:
            """Return the centre of the active axis."""
            low_idx = int(np.clip(np.floor(value), 0, len(axis_values) - 1))
            high_idx = min(low_idx + 1, len(axis_values) - 1)
            alpha = float(np.clip(value - low_idx, 0.0, 1.0))
            return float(interpolate(axis_values[low_idx], axis_values[high_idx], alpha))

        def matrix_cell_center(column_value: float, row_value: float) -> np.ndarray:
            """Return the centre of one matrix cell in scene coordinates."""
            x = axis_center(train_center_xs, column_value)
            y = axis_center(test_center_ys, row_value)
            return np.array([x, y, 0.0])

        train_tracker = ValueTracker(0.0)
        test_tracker = ValueTracker(0.0)
        selector_color = ManimColor("#0D0F0E")
        selector_fill_opacity = 0.12

        train_selector = always_redraw(lambda: RoundedRectangle(
            width=train_bins_target[0].width + 0.05,
            height=train_bins_target[0].height + 0.07,
            corner_radius=0.04,
            stroke_color=selector_color,
            stroke_width=2.0,
        ).set_fill(selector_color, opacity=selector_fill_opacity).move_to(
            interpolated_center(train_bins_target, train_tracker.get_value())
        ).set_z_index(4.6))

        test_selector = always_redraw(lambda: RoundedRectangle(
            width=test_bins_target[0].width + 0.05,
            height=test_bins_target[0].height + 0.07,
            corner_radius=0.04,
            stroke_color=selector_color,
            stroke_width=2.0,
        ).set_fill(selector_color, opacity=selector_fill_opacity).move_to(
            interpolated_center(test_bins_target, test_tracker.get_value())
        ).set_z_index(4.6))

        cursor_corner_radius = min(cell_width, cell_height) * 0.08
        matrix_cursor = always_redraw(lambda: RoundedRectangle(
            width=cell_width * 0.96,
            height=cell_height * 0.96,
            corner_radius=cursor_corner_radius,
            stroke_color=selector_color,
            stroke_width=1.5,
        ).set_fill(selector_color, opacity=0.08).move_to(
            matrix_cell_center(train_tracker.get_value(), test_tracker.get_value())
        ).set_z_index(4.7))

        train_projection = always_redraw(lambda: DashedLine(
            interpolated_center(train_bins_target, train_tracker.get_value()) + UP * (
                train_bins_target[0].height / 2 + 0.04
            ),
            matrix_cell_center(train_tracker.get_value(), test_tracker.get_value()) + DOWN * (cell_height / 2),
            color="#7D7D7D",
            stroke_width=1.0,
            dash_length=0.045,
            dashed_ratio=0.65,
        ).set_z_index(4.45))

        test_projection = always_redraw(lambda: DashedLine(
            interpolated_center(test_bins_target, test_tracker.get_value()) + RIGHT * (
                test_bins_target[0].width / 2 + 0.04
            ),
            matrix_cell_center(train_tracker.get_value(), test_tracker.get_value()) + LEFT * (cell_width / 2),
            color="#7D7D7D",
            stroke_width=1.0,
            dash_length=0.045,
            dashed_ratio=0.65,
        ).set_z_index(4.45))

        right_plot_frame_target = logic_matrix_frame.copy()
        right_plot_frame_target.set_x(ctx["tempgen_plot_frame"].get_center()[0])
        right_plot_frame_target.align_to(logic_matrix_frame, DOWN)
        right_plot_frame_target.set_y(logic_matrix_frame.get_center()[1])
        right_plot_chance_source = max(
            [
                submob
                for submob in timeres_ctx["timeres_plot_rest"].submobjects
                if timeres_ctx["timeres_frame"].get_left()[0] - 0.02
                <= submob.get_center()[0]
                <= timeres_ctx["timeres_frame"].get_right()[0] + 0.02
                if submob.width >= timeres_ctx["timeres_frame"].width * 0.8
                if submob.height <= timeres_ctx["timeres_frame"].height * 0.03
            ],
            key=lambda mob: mob.width,
        )
        right_plot_inner_source = [
            submob.copy()
            for submob in timeres_ctx["timeres_plot_rest"].submobjects
            if timeres_ctx["timeres_frame"].get_left()[0] - 0.02
            <= submob.get_center()[0]
            <= timeres_ctx["timeres_frame"].get_right()[0] + 0.02
            if timeres_ctx["timeres_frame"].get_bottom()[1] - 0.02
            <= submob.get_center()[1]
            <= timeres_ctx["timeres_frame"].get_top()[1] + 0.02
            if submob is not right_plot_chance_source
        ]
        right_plot_frame = right_plot_frame_target.copy()
        right_plot_rest = self._remap_plot_mobject(
            VGroup(*right_plot_inner_source),
            timeres_ctx["timeres_frame"],
            right_plot_frame_target,
        )
        right_plot_chance_template = self._remap_plot_mobject(
            right_plot_chance_source.copy(),
            timeres_ctx["timeres_frame"],
            right_plot_frame_target,
        )
        right_plot_chance_y = right_plot_chance_template.get_center()[1]
        right_plot_chance_color = right_plot_chance_template.get_stroke_color()
        right_plot_chance_line = DashedLine(
            np.array([right_plot_frame.get_left()[0], right_plot_chance_y, 0.0]),
            np.array([right_plot_frame.get_right()[0], right_plot_chance_y, 0.0]),
            color=right_plot_chance_color,
            stroke_width=max(1.8, right_plot_chance_template.get_stroke_width()),
            dash_length=0.08,
            dashed_ratio=0.55,
        )
        right_plot_chance_label = Tex(
            "Chance",
            color=right_plot_chance_color,
            font_size=14,
        ).next_to(right_plot_chance_line, DOWN, buff=0.08).align_to(
            right_plot_chance_line,
            RIGHT,
        ).shift(LEFT * 0.02)
        right_plot_x_ticks = VGroup()
        for tick_time, tick_label in axis_tick_specs:
            tick_x = float(interpolate(
                right_plot_frame.get_left()[0],
                right_plot_frame.get_right()[0],
                np.clip(tick_time / matrix_total_time, 0.0, 1.0),
            ))
            tick_mark = Line(
                np.array([tick_x, right_plot_frame.get_bottom()[1], 0.0]),
                np.array([tick_x, right_plot_frame.get_bottom()[1] - 0.055, 0.0]),
                color="#5A5A5A",
                stroke_width=1.2,
            )
            tick_text = Tex(tick_label, color=INK, font_size=15).next_to(
                tick_mark,
                DOWN,
                buff=0.05,
            )
            right_plot_x_ticks.add(VGroup(tick_mark, tick_text))
        right_plot_x_ticks.set_z_index(2.2)

        right_plot_y_tick_values = ["0.00", "0.05", "0.10", "0.15", "0.20"]
        right_plot_y_positions = np.linspace(
            right_plot_chance_y,
            right_plot_frame.get_top()[1] - 0.14,
            len(right_plot_y_tick_values),
        )
        right_plot_y_ticks = VGroup()
        for tick_y, tick_label in zip(right_plot_y_positions, right_plot_y_tick_values):
            tick_mark = Line(
                np.array([right_plot_frame.get_left()[0], tick_y, 0.0]),
                np.array([right_plot_frame.get_left()[0] - 0.055, tick_y, 0.0]),
                color="#5A5A5A",
                stroke_width=1.2,
            )
            tick_text = Tex(tick_label, color=INK, font_size=15).next_to(
                tick_mark,
                LEFT,
                buff=0.05,
            )
            right_plot_y_ticks.add(VGroup(tick_mark, tick_text))
        right_plot_y_ticks.set_z_index(2.2)

        right_plot_y_label = Tex(
            "Accuracy",
            color=INK,
            font_size=float(train_label_target.font_size),
        )
        right_plot_y_label.rotate(PI / 2)
        right_plot_y_label.scale_to_fit_width(train_label_target.height * 1.25)
        right_plot_y_label.next_to(right_plot_y_ticks, LEFT, buff=0.14)
        right_plot_scaffold = VGroup(
            right_plot_frame,
            right_plot_rest,
            right_plot_y_ticks,
            right_plot_chance_line,
            right_plot_chance_label,
            right_plot_x_ticks,
            right_plot_y_label,
        )
        right_plot_ci = self._remap_plot_mobject(
            timeres_ctx["timeres_ci"].copy(),
            timeres_ctx["timeres_frame"],
            right_plot_frame_target,
        )
        right_timeres_trace = timeres_ctx["timeres_trace"].copy()
        right_timeres_trace.clear_updaters()
        right_plot_trace = self._remap_plot_mobject(
            right_timeres_trace,
            timeres_ctx["timeres_frame"],
            right_plot_frame_target,
        )
        for submob in right_plot_trace.family_members_with_points():
            submob.set_stroke(color=BLACK, opacity=1.0)
            submob.set_fill(opacity=0.0)
        right_plot_trace.set_stroke(color=BLACK, opacity=1.0)
        right_plot_scaffold.set_z_index(2.15)
        right_plot_ci.set_z_index(2.8)
        right_plot_trace.set_z_index(4.6)

        peak_trace_idx = int(np.argmax(timeres_ctx["trace_unique_ys"]))
        peak_source_x = float(timeres_ctx["trace_unique_xs"][peak_trace_idx])
        peak_source_y = float(timeres_ctx["trace_unique_ys"][peak_trace_idx])
        peak_x_alpha = np.clip(
            (peak_source_x - timeres_ctx["timeres_frame"].get_left()[0]) / timeres_ctx["timeres_frame"].width,
            0.0,
            1.0,
        )
        peak_y_alpha = np.clip(
            (peak_source_y - timeres_ctx["timeres_frame"].get_bottom()[1]) / timeres_ctx["timeres_frame"].height,
            0.0,
            1.0,
        )
        peak_curve_point = np.array([
            interpolate(
                right_plot_frame_target.get_left()[0],
                right_plot_frame_target.get_right()[0],
                peak_x_alpha,
            ),
            interpolate(
                right_plot_frame_target.get_bottom()[1],
                right_plot_frame_target.get_top()[1],
                peak_y_alpha,
            ),
            0.0,
        ])
        peak_column_center_x = float(interpolate(
            matrix_left + cell_width / 2,
            matrix_right - cell_width / 2,
            peak_x_alpha,
        ))
        peak_column_idx = int(np.argmin(np.abs(train_center_xs - peak_column_center_x)))
        peak_column_center_x = float(train_center_xs[peak_column_idx])
        peak_curve_marker = Dot(
            peak_curve_point,
            radius=0.055,
            color=_D_RED,
            fill_opacity=1.0,
        ).set_stroke(WHITE, width=1.8).set_z_index(5.2)
        peak_curve_ring = Circle(
            radius=0.13,
            stroke_color=_D_RED,
            stroke_width=2.0,
        ).set_fill(opacity=0.0).move_to(peak_curve_point).set_z_index(5.1)
        def make_peak_matrix_column(
            height: float,
            center_y: float,
        ) -> VGroup:
            """Build the highlighted peak matrix column."""
            peak_matrix_column_fill = Rectangle(
                width=cell_width * 1.02,
                height=height,
                stroke_width=0.0,
            ).set_fill(WHITE, opacity=0.16)
            peak_matrix_column_outer = RoundedRectangle(
                width=cell_width * 1.04,
                height=height,
                corner_radius=min(cell_width, cell_height) * 0.11,
                stroke_color=WHITE,
                stroke_width=4.0,
            ).set_fill(opacity=0.0)
            peak_matrix_column_inner = RoundedRectangle(
                width=cell_width * 1.00,
                height=height,
                corner_radius=min(cell_width, cell_height) * 0.10,
                stroke_color=BLACK,
                stroke_width=1.8,
            ).set_fill(opacity=0.0)
            return VGroup(
                peak_matrix_column_fill.set_z_index(3.72),
                peak_matrix_column_outer.set_z_index(3.94),
                peak_matrix_column_inner.set_z_index(3.95),
            ).move_to(
                np.array([
                    peak_column_center_x,
                    center_y,
                    0.0,
                ])
            )

        peak_column_height = (matrix_top - matrix_bottom) + 0.14
        peak_matrix_column = make_peak_matrix_column(
            peak_column_height,
            (matrix_bottom + matrix_top) / 2,
        )
        subselect_low_value = 12.0
        subselect_high_value = 15.0
        subselect_low_y = axis_center(test_center_ys, subselect_low_value)
        subselect_high_y = axis_center(test_center_ys, subselect_high_value)
        peak_matrix_column_focus = make_peak_matrix_column(
            abs(subselect_high_y - subselect_low_y) + cell_height * 1.12,
            (subselect_low_y + subselect_high_y) / 2,
        )
        final_takeaway = Tex(
            r"Representational discontinuity throughout the delay phase",
            color=INK,
            font_size=24,
            tex_environment="center",
        )
        final_takeaway.scale_to_fit_width(config.frame_width * 0.68)
        final_takeaway.to_edge(UP, buff=0.26)
        final_takeaway.set_z_index(5.3)

        matrix_cover_columns: list[VGroup] = []
        for column_idx in range(cell_count):
            column_covers = VGroup()
            for row_idx in range(cell_count):
                cell_center = np.array([
                    train_center_xs[column_idx],
                    test_center_ys[row_idx],
                    0.0,
                ])
                cover = Rectangle(
                    width=cell_width + 0.012,
                    height=cell_height + 0.012,
                    stroke_width=0.0,
                ).set_fill(BG, opacity=1.0).move_to(cell_center)
                cover.set_z_index(3.25)
                column_covers.add(cover)
            matrix_cover_columns.append(column_covers)
        matrix_cover_group = VGroup(*matrix_cover_columns)

        diagonal_trace = VMobject()
        diagonal_trace.set_points_as_corners([
            matrix_cell_center(float(diag_idx), float(diag_idx))
            for diag_idx in range(cell_count)
        ])
        diagonal_trace.set_stroke(
            color=BLACK,
            width=2.7,
            opacity=0.94,
        )
        diagonal_trace.set_fill(opacity=0.0)
        diagonal_trace.set_z_index(4.8)
        diagonal_transfer_trace = VMobject()
        diagonal_transfer_trace.set_points_as_corners([
            matrix_cell_center(0.0, 0.0),
            matrix_cell_center(float(cell_count - 1), float(cell_count - 1)),
        ])
        diagonal_transfer_trace.match_style(diagonal_trace)
        diagonal_transfer_trace.set_z_index(4.85)

        demo_column_count = min(10, cell_count)
        demo_fill_durations = [
            1.55,
            0.94,
            0.84,
            0.76,
            0.68,
            0.61,
            0.55,
            0.50,
            0.46,
            0.42,
        ][:demo_column_count]
        demo_shift_durations = [
            0.28,
            0.25,
            0.22,
            0.20,
            0.18,
            0.16,
            0.14,
            0.13,
            0.12,
        ][: max(demo_column_count - 1, 0)]

        return {
            "ctx": ctx,
            "timeres_ctx": timeres_ctx,
            "design_stacked_target": design_stacked_target,
            "train_bins_stacked_target": train_bins_stacked_target,
            "test_bins_stacked_target": test_bins_stacked_target,
            "train_label_stacked_target": train_label_stacked_target,
            "test_label_stacked_target": test_label_stacked_target,
            "design_target": design_target,
            "train_bins_target": train_bins_target,
            "test_bins_target": test_bins_target,
            "train_label_target": train_label_target,
            "test_label_target": test_label_target,
            "logic_matrix_frame": logic_matrix_frame,
            "logic_matrix_panel": logic_matrix_panel,
            "logic_matrix_colorbar_mask": logic_matrix_colorbar_mask,
            "logic_matrix_colorbar_gradient": logic_matrix_colorbar_gradient,
            "logic_matrix_label_masks": logic_matrix_label_masks,
            "logic_matrix_underlay": logic_matrix_underlay,
            "matrix_x_ticks": matrix_x_ticks,
            "matrix_y_ticks": matrix_y_ticks,
            "right_plot_scaffold": right_plot_scaffold,
            "right_plot_ci": right_plot_ci,
            "right_plot_trace": right_plot_trace,
            "peak_curve_marker": peak_curve_marker,
            "peak_curve_ring": peak_curve_ring,
            "peak_matrix_column": peak_matrix_column,
            "peak_matrix_column_focus": peak_matrix_column_focus,
            "peak_column_idx": peak_column_idx,
            "final_takeaway": final_takeaway,
            "matrix_cover_columns": matrix_cover_columns,
            "matrix_cover_group": matrix_cover_group,
            "train_tracker": train_tracker,
            "test_tracker": test_tracker,
            "train_selector": train_selector,
            "test_selector": test_selector,
            "matrix_cursor": matrix_cursor,
            "train_projection": train_projection,
            "test_projection": test_projection,
            "diagonal_trace": diagonal_trace,
            "diagonal_transfer_trace": diagonal_transfer_trace,
            "cell_count": cell_count,
            "demo_column_count": demo_column_count,
            "demo_fill_durations": demo_fill_durations,
            "demo_shift_durations": demo_shift_durations,
            "subselect_low_value": subselect_low_value,
            "subselect_high_value": subselect_high_value,
        }

    def _show_within_session_resultsc_final_state(
        self,
        ctx: dict[str, Mobject],
        timeres_ctx: dict[str, Mobject],
    ) -> dict[str, object]:
        """Animate the within session resultsc final state."""
        self._prepare_within_session_resultsb_final_state(timeres_ctx)
        logic_ctx = self._build_within_session_tempgen_logic_context(ctx, timeres_ctx)

        timeres_ctx["experimental_design"] = logic_ctx["design_target"].copy()
        timeres_ctx["train_time_bins"] = logic_ctx["train_bins_target"].copy()
        timeres_ctx["test_time_bins"] = logic_ctx["test_bins_target"].copy()
        timeres_ctx["train_row_label"] = logic_ctx["train_label_target"].copy()
        timeres_ctx["test_row_label"] = logic_ctx["test_label_target"].copy()
        logic_ctx["train_tracker"].set_value(0.0)
        logic_ctx["test_tracker"].set_value(0.0)

        self.add(
            timeres_ctx["experimental_design"],
            timeres_ctx["train_time_bins"],
            timeres_ctx["test_time_bins"],
            timeres_ctx["train_row_label"],
            timeres_ctx["test_row_label"],
            logic_ctx["logic_matrix_frame"],
            logic_ctx["logic_matrix_underlay"],
            logic_ctx["logic_matrix_colorbar_mask"],
            logic_ctx["logic_matrix_colorbar_gradient"],
            logic_ctx["matrix_x_ticks"],
            logic_ctx["matrix_y_ticks"],
            logic_ctx["train_selector"],
            logic_ctx["test_selector"],
            logic_ctx["matrix_cursor"],
        )
        return logic_ctx

    def _animate_within_session_tempgen_logic(
        self,
        ctx: dict[str, Mobject],
        timeres_ctx: dict[str, Mobject],
    ) -> None:
        """Animate the within session temporal-generalisation logic."""
        logic_ctx = self._build_within_session_tempgen_logic_context(ctx, timeres_ctx)
        design_stacked_target = logic_ctx["design_stacked_target"]
        train_bins_stacked_target = logic_ctx["train_bins_stacked_target"]
        test_bins_stacked_target = logic_ctx["test_bins_stacked_target"]
        train_label_stacked_target = logic_ctx["train_label_stacked_target"]
        test_label_stacked_target = logic_ctx["test_label_stacked_target"]
        design_target = logic_ctx["design_target"]
        train_bins_target = logic_ctx["train_bins_target"]
        test_bins_target = logic_ctx["test_bins_target"]
        train_label_target = logic_ctx["train_label_target"]
        test_label_target = logic_ctx["test_label_target"]
        logic_matrix_frame = logic_ctx["logic_matrix_frame"]
        logic_matrix_panel = logic_ctx["logic_matrix_panel"]
        logic_matrix_colorbar_mask = logic_ctx["logic_matrix_colorbar_mask"]
        logic_matrix_colorbar_gradient = logic_ctx["logic_matrix_colorbar_gradient"]
        logic_matrix_label_masks = logic_ctx["logic_matrix_label_masks"]
        logic_matrix_underlay = logic_ctx["logic_matrix_underlay"]
        matrix_x_ticks = logic_ctx["matrix_x_ticks"]
        matrix_y_ticks = logic_ctx["matrix_y_ticks"]
        matrix_cover_columns = logic_ctx["matrix_cover_columns"]
        matrix_cover_group = logic_ctx["matrix_cover_group"]
        train_tracker = logic_ctx["train_tracker"]
        test_tracker = logic_ctx["test_tracker"]
        train_selector = logic_ctx["train_selector"]
        test_selector = logic_ctx["test_selector"]
        matrix_cursor = logic_ctx["matrix_cursor"]
        train_projection = logic_ctx["train_projection"]
        test_projection = logic_ctx["test_projection"]
        diagonal_trace = logic_ctx["diagonal_trace"]
        cell_count = logic_ctx["cell_count"]
        demo_column_count = logic_ctx["demo_column_count"]
        demo_fill_durations = logic_ctx["demo_fill_durations"]
        demo_shift_durations = logic_ctx["demo_shift_durations"]
        tempgen_c_title = ctx.get("tempgen_c_title")

        for mob in [
            timeres_ctx["experimental_design"],
            timeres_ctx["train_time_bins"],
            timeres_ctx["test_time_bins"],
            timeres_ctx["train_row_label"],
            timeres_ctx["test_row_label"],
        ]:
            mob.set_z_index(4.25)

        self.play(
            FadeOut(ctx["glm_plot"], shift=LEFT * 0.45),
            FadeOut(timeres_ctx["timeres_title"], shift=UP * 0.05),
            FadeOut(timeres_ctx["timeres_train_explainer"], shift=UP * 0.05),
            FadeOut(timeres_ctx["timeres_plot_scaffold"], shift=DOWN * 0.05),
            FadeOut(timeres_ctx["timeres_trace"], shift=DOWN * 0.05),
            FadeOut(timeres_ctx["timeres_ci"], shift=DOWN * 0.05),
            FadeOut(timeres_ctx["timeres_sig_bands"], shift=DOWN * 0.05),
            FadeOut(timeres_ctx["timeres_hrf_rectangles"], shift=DOWN * 0.05),
            FadeOut(timeres_ctx["timeres_hrf_lines"], shift=DOWN * 0.05),
            FadeOut(timeres_ctx["event_projection_lines"]),
            FadeOut(timeres_ctx["delay_end_chance_arrow"], shift=UP * 0.05),
            FadeOut(timeres_ctx["trs_label"], shift=RIGHT * 0.04),
            *(
                [FadeIn(tempgen_c_title, shift=UP * 0.05)]
                if tempgen_c_title is not None
                else []
            ),
            Transform(timeres_ctx["experimental_design"], design_stacked_target),
            Transform(timeres_ctx["train_time_bins"], train_bins_stacked_target),
            Transform(timeres_ctx["test_time_bins"], test_bins_stacked_target),
            Transform(timeres_ctx["train_row_label"], train_label_stacked_target),
            Transform(timeres_ctx["test_row_label"], test_label_stacked_target),
            run_time=1.55,
            rate_func=smooth,
        )
        self.wait(0.20)
        self.play(
            Transform(timeres_ctx["experimental_design"], design_target),
            Transform(timeres_ctx["train_time_bins"], train_bins_target),
            Transform(timeres_ctx["test_time_bins"], test_bins_target),
            Transform(timeres_ctx["train_row_label"], train_label_target),
            Transform(timeres_ctx["test_row_label"], test_label_target),
            run_time=1.35,
            rate_func=smooth,
        )
        self.wait(0.15)
        self.add(matrix_cover_group, logic_matrix_label_masks, logic_matrix_colorbar_mask)
        self.play(
            Create(logic_matrix_frame),
            run_time=0.55,
        )
        self.play(
            FadeIn(logic_matrix_panel, shift=LEFT * 0.04),
            FadeIn(logic_matrix_colorbar_gradient, shift=LEFT * 0.04),
            run_time=0.45,
        )
        self.play(
            FadeIn(matrix_x_ticks, shift=DOWN * 0.02),
            FadeIn(matrix_y_ticks, shift=LEFT * 0.02),
            run_time=0.35,
        )

        self.play(
            FadeIn(train_selector),
            FadeIn(test_selector),
            FadeIn(matrix_cursor),
            FadeIn(train_projection),
            FadeIn(test_projection),
            run_time=0.40,
        )

        def sync_demo_column_to_test_tracker(column_group: VGroup) -> None:
            """Synchronize the demo column to the active test tracker."""
            def update_column(group: VGroup) -> VGroup:
                """Update the active column in place."""
                revealed_row_idx = int(np.floor(test_tracker.get_value() + 1e-6))
                for row_idx, cover in enumerate(group):
                    cover.set_fill(opacity=0.0 if row_idx <= revealed_row_idx else 1.0)
                return group

            column_group.add_updater(update_column)
            update_column(column_group)

        for demo_step_idx in range(demo_column_count):
            column_group = matrix_cover_columns[demo_step_idx]
            if demo_step_idx > 0:
                self.play(
                    train_tracker.animate.set_value(demo_step_idx),
                    test_tracker.animate.set_value(0.0),
                    run_time=demo_shift_durations[demo_step_idx - 1],
                    rate_func=smooth,
                )
            sync_demo_column_to_test_tracker(column_group)
            self.play(
                test_tracker.animate.set_value(cell_count - 1),
                run_time=demo_fill_durations[demo_step_idx],
                rate_func=linear,
            )
            column_group.clear_updaters()
            for cover in column_group:
                cover.set_fill(opacity=0.0)

        remaining_cover_groups = [
            column_group
            for column_idx, column_group in enumerate(matrix_cover_columns)
            if column_idx >= demo_column_count
        ]
        self.play(
            FadeOut(train_projection),
            FadeOut(test_projection),
            run_time=0.18,
        )
        self.play(
            train_tracker.animate.set_value(cell_count - 1),
            test_tracker.animate.set_value(cell_count - 1),
            LaggedStart(
                *[FadeOut(group) for group in remaining_cover_groups],
                lag_ratio=0.035,
            ),
            run_time=1.05,
        )
        self.wait(0.18)
        self.play(
            train_tracker.animate.set_value(0.0),
            test_tracker.animate.set_value(0.0),
            run_time=0.42,
            rate_func=smooth,
        )
        self.wait(2.0)

    def _animate_within_session_tempgen_followup(
        self,
        logic_ctx: dict[str, object],
    ) -> None:
        """Animate the within session temporal-generalisation followup."""
        train_tracker = logic_ctx["train_tracker"]
        test_tracker = logic_ctx["test_tracker"]
        train_selector = logic_ctx["train_selector"]
        test_selector = logic_ctx["test_selector"]
        matrix_cursor = logic_ctx["matrix_cursor"]
        diagonal_trace = logic_ctx["diagonal_trace"]
        right_plot_scaffold = logic_ctx["right_plot_scaffold"]
        right_plot_ci = logic_ctx["right_plot_ci"]
        right_plot_trace = logic_ctx["right_plot_trace"]
        peak_curve_marker = logic_ctx["peak_curve_marker"]
        peak_curve_ring = logic_ctx["peak_curve_ring"]
        peak_matrix_column = logic_ctx["peak_matrix_column"]
        peak_matrix_column_focus = logic_ctx["peak_matrix_column_focus"]
        peak_column_idx = logic_ctx["peak_column_idx"]
        cell_count = logic_ctx["cell_count"]
        subselect_low_value = logic_ctx["subselect_low_value"]
        subselect_high_value = logic_ctx["subselect_high_value"]
        final_takeaway = logic_ctx["final_takeaway"]

        self.play(
            train_tracker.animate.set_value(cell_count - 1),
            test_tracker.animate.set_value(cell_count - 1),
            Create(diagonal_trace),
            run_time=1.0,
            rate_func=linear,
        )
        self.play(
            FadeIn(right_plot_scaffold, shift=LEFT * 0.06),
            FadeOut(train_selector),
            FadeOut(test_selector),
            FadeOut(matrix_cursor),
            run_time=0.85,
        )

        def sampled_polyline(
            path: VMobject,
            *,
            color: str = BLACK,
            stroke_width: float | None = None,
            sample_count: int = 64,
            z_index: float = 4.85,
        ) -> VMobject:
            """Sample a polyline at evenly spaced proportions."""
            sampled = VMobject()
            props = np.linspace(0.0, 1.0, sample_count)
            sampled.set_points_as_corners([
                path.point_from_proportion(float(prop))
                for prop in props
            ])
            sampled.set_z_index(z_index)
            sampled.set_stroke(
                color=color,
                width=stroke_width if stroke_width is not None else path.get_stroke_width(),
                opacity=1.0,
            )
            sampled.set_fill(opacity=0.0)
            return sampled

        diagonal_home = diagonal_trace.copy()
        morph_trace = sampled_polyline(
            diagonal_home,
            color=BLACK,
            stroke_width=diagonal_home.get_stroke_width(),
            z_index=diagonal_home.get_z_index(),
        )
        right_curve_target = sampled_polyline(
            right_plot_trace,
            color="#C49A00",
            stroke_width=right_plot_trace.get_stroke_width(),
            z_index=morph_trace.get_z_index(),
        )
        morph_return = morph_trace.copy()
        self.remove(diagonal_trace)
        self.add(morph_trace)
        self.play(
            Transform(morph_trace, right_curve_target),
            run_time=1.15,
            rate_func=smooth,
        )
        self.wait(0.25)
        self.play(
            Transform(morph_trace, morph_return),
            run_time=1.05,
            rate_func=smooth,
        )
        self.wait(0.18)
        self.play(
            Transform(morph_trace, right_curve_target),
            FadeIn(diagonal_trace),
            FadeIn(right_plot_trace),
            FadeIn(right_plot_ci),
            run_time=1.15,
            rate_func=smooth,
        )
        self.remove(morph_trace)
        self.wait(2.0)
        for submob in right_plot_trace.family_members_with_points():
            submob.set_stroke(color=BLACK, opacity=1.0)
            submob.set_fill(opacity=0.0)
        right_plot_trace.set_stroke(color=BLACK, opacity=1.0)
        self.play(
            FadeIn(peak_curve_marker, scale=0.65),
            Create(peak_curve_ring),
            FadeIn(peak_matrix_column, scale=1.03),
            run_time=0.55,
        )
        self.play(
            Indicate(peak_curve_ring, scale_factor=1.06),
            AnimationGroup(
                Indicate(peak_matrix_column[1], scale_factor=1.01),
                Indicate(peak_matrix_column[2], scale_factor=1.01),
                lag_ratio=0.0,
            ),
            run_time=0.70,
        )
        train_tracker.set_value(float(peak_column_idx))
        test_tracker.set_value(0.0)
        train_selector.update()
        test_selector.update()
        matrix_cursor.update()
        train_selector_snapshot = train_selector.copy().clear_updaters()
        test_selector_snapshot = test_selector.copy().clear_updaters()
        matrix_cursor_snapshot = matrix_cursor.copy().clear_updaters()
        self.play(
            FadeIn(train_selector_snapshot),
            FadeIn(test_selector_snapshot),
            FadeIn(matrix_cursor_snapshot),
            run_time=0.30,
        )
        self.add(train_selector, test_selector, matrix_cursor)
        self.remove(
            train_selector_snapshot,
            test_selector_snapshot,
            matrix_cursor_snapshot,
        )
        self.play(
            test_tracker.animate.set_value(subselect_low_value),
            run_time=0.85,
            rate_func=smooth,
        )
        for target_value in [
            subselect_high_value,
            subselect_low_value,
            subselect_high_value,
            subselect_low_value,
        ]:
            self.play(
                test_tracker.animate.set_value(target_value),
                run_time=0.42,
                rate_func=smooth,
            )
        peak_matrix_column_full = peak_matrix_column.copy()
        self.play(
            Transform(peak_matrix_column, peak_matrix_column_focus),
            FadeOut(matrix_cursor),
            run_time=0.55,
            rate_func=smooth,
        )
        blink_fill_color = "#F4D03F"
        for blink_idx in range(4):
            flash_on_anims = [
                peak_matrix_column[0].animate.set_fill(blink_fill_color, opacity=0.24),
                peak_matrix_column[1].animate.set_stroke(color=blink_fill_color, width=4.2),
                peak_matrix_column[2].animate.set_stroke(color=blink_fill_color, width=2.2),
            ]
            if blink_idx == 3:
                flash_on_anims.append(FadeIn(final_takeaway, shift=DOWN * 0.06))
            self.play(
                *flash_on_anims,
                run_time=0.32,
            )
            self.play(
                peak_matrix_column[0].animate.set_fill(WHITE, opacity=0.16),
                peak_matrix_column[1].animate.set_stroke(color=WHITE, width=4.0),
                peak_matrix_column[2].animate.set_stroke(color=BLACK, width=1.8),
                run_time=0.32,
            )
        self.play(
            Transform(peak_matrix_column, peak_matrix_column_full),
            FadeOut(test_selector),
            run_time=0.55,
            rate_func=smooth,
        )
        self.wait(2.0)

    def _build_within_session_resultsd_handoff_frame(self) -> Group:
        """Build the shared static handoff frame between ResultsD and the LTM explainer."""
        rationale = self._build_rationale_end_static()
        self.slide_title = rationale["question_title"]
        ctx = self._build_results_stage()
        self._align_within_session_act1_to_shared_layout(ctx)
        timeres_ctx = self._build_within_session_timeres_context(ctx)
        self._prepare_within_session_resultsb_final_state(timeres_ctx)
        logic_ctx = self._build_within_session_tempgen_logic_context(ctx, timeres_ctx)

        experimental_design = logic_ctx["design_target"].copy()
        train_time_bins = logic_ctx["train_bins_target"].copy()
        test_time_bins = logic_ctx["test_bins_target"].copy()
        train_row_label = logic_ctx["train_label_target"].copy()
        test_row_label = logic_ctx["test_label_target"].copy()

        train_tracker = logic_ctx["train_tracker"]
        test_tracker = logic_ctx["test_tracker"]
        train_tracker.set_value(float(logic_ctx["peak_column_idx"]))
        test_tracker.set_value(float(logic_ctx["subselect_low_value"]))

        handoff_frame = Group(
            experimental_design,
            train_time_bins,
            test_time_bins,
            train_row_label,
            test_row_label,
            logic_ctx["logic_matrix_frame"],
            logic_ctx["logic_matrix_underlay"],
            logic_ctx["logic_matrix_colorbar_mask"],
            logic_ctx["logic_matrix_colorbar_gradient"],
            logic_ctx["matrix_x_ticks"],
            logic_ctx["matrix_y_ticks"],
            logic_ctx["diagonal_trace"],
            logic_ctx["train_selector"],
            logic_ctx["right_plot_scaffold"],
            logic_ctx["right_plot_ci"],
            logic_ctx["right_plot_trace"],
            logic_ctx["peak_curve_marker"],
            logic_ctx["peak_curve_ring"],
            logic_ctx["peak_matrix_column"],
            logic_ctx["final_takeaway"],
        )
        return handoff_frame

    def _animate_tempgen_results(self, ctx: dict[str, Mobject]) -> None:
        """Animate the temporal-generalisation results."""
        tempgen_title = ctx["tempgen_title"]
        tempgen_underlay = ctx["tempgen_underlay"]
        tempgen_plot_frame = ctx["tempgen_plot_frame"]
        tempgen_overlay = ctx["tempgen_overlay"]
        tempgen_colorbar_mask = ctx["tempgen_colorbar_mask"]
        tempgen_colorbar_gradient = ctx["tempgen_colorbar_gradient"]
        tempgen_underlay.set_opacity(ctx["tempgen_underlay_final_opacity"])
        tempgen_overlay.set_opacity(1.0)
        tempgen_column_covers = self._make_tempgen_column_covers(
            tempgen_plot_frame,
            fill_color=BG,
        )
        tempgen_cover_group = VGroup(*[
            cover
            for column in tempgen_column_covers
            for cover in column
        ])
        self.add(tempgen_colorbar_mask)

        self.play(
            FadeIn(tempgen_title, shift=UP * 0.05),
            AnimationGroup(
                Create(tempgen_plot_frame),
                FadeIn(tempgen_underlay, shift=UP * 0.08),
                FadeIn(tempgen_colorbar_gradient, shift=UP * 0.08),
                FadeIn(tempgen_overlay, shift=UP * 0.08),
                FadeIn(tempgen_cover_group),
                lag_ratio=0.12,
            ),
            run_time=0.95,
        )
        self.play(
            LaggedStart(
                *[
                    LaggedStart(
                        *[
                            FadeOut(cover, scale=0.92)
                            for cover in column
                        ],
                        lag_ratio=0.1,
                    )
                    for column in tempgen_column_covers
                ],
                lag_ratio=0.14,
            ),
            run_time=2.6,
        )


class Study2WithinSession1DecodingSetupCombined(_Study2WithinSession1DecodingBase):
    """
    Combined intro + rationale for within-session decoding in Session 1.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingSetupCombined -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingSetupCombined -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        ctx = self._build_within_session_intro_context()
        self._animate_within_session_intro(
            ctx,
            summary_hold=3.0,
            question_hold=0.6,
        )
        self._animate_within_session_scheme_from_question(ctx)


class Study2WithinSession1DecodingSetupA(_Study2WithinSession1DecodingBase):
    """
    Part A: start from the final cross-session results frame and compress it into
    a takeaway card with compact plots underneath.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingSetupA -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingSetupA -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        summary_card = self._build_within_session_summary_card()
        full_snapshot = (
            ImageMobject(self._CROSSSESSION_RESULTSB_LAST)
            .scale_to_fit_width(config.frame_width)
            .move_to(ORIGIN)
        )
        left_plot_overlay = self._make_snapshot_plot_overlay(
            self._CROSSSESSION_RESULTSB_LEFT_PLOT,
            self._CROSSSESSION_RESULTSB_LEFT_BOX,
            full_snapshot,
        )
        right_plot_overlay = self._make_snapshot_plot_overlay(
            self._CROSSSESSION_RESULTSB_RIGHT_PLOT,
            self._CROSSSESSION_RESULTSB_RIGHT_BOX,
            full_snapshot,
        )

        self.add(full_snapshot, left_plot_overlay, right_plot_overlay)
        self.wait(0.35)
        self.play(
            FadeIn(summary_card["takeaway"], shift=UP * 0.08),
            FadeOut(full_snapshot),
            Transform(left_plot_overlay, summary_card["left_plot"]),
            Transform(right_plot_overlay, summary_card["right_plot"]),
            run_time=1.0,
            rate_func=smooth,
        )
        self.wait(3.0)
        self.play(
            FadeIn(summary_card["question"], shift=UP * 0.08),
            run_time=0.65,
        )
        self.wait(2.0)


class Study2WithinSession1DecodingSetupB(_Study2WithinSession1DecodingBase):
    """
    Part B: start from the summary card and lift the question into the rationale.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingSetupB -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingSetupB -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        ctx = self._build_within_session_intro_context()
        summary_card = self._build_within_session_summary_card()
        self.add(
            summary_card["takeaway"],
            summary_card["left_plot"],
            summary_card["right_plot"],
            summary_card["question"],
        )
        self.wait(0.6)
        self.play(
            Transform(summary_card["question"], ctx["rationale"]["question_title"]),
            FadeOut(summary_card["takeaway"], shift=UP * 0.05),
            FadeOut(summary_card["left_plot"], shift=DOWN * 0.05),
            FadeOut(summary_card["right_plot"], shift=DOWN * 0.05),
            run_time=0.95,
            rate_func=smooth,
        )
        ctx["question_intro"] = summary_card["question"]
        self._animate_within_session_scheme_from_question(
            ctx,
            question_already_at_title=True,
        )


class Study2WithinSession1DecodingResultsCombined(_Study2WithinSession1DecodingBase):
    """
    Start from the end of the Session 1 within-session rationale and reveal results.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsCombined -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsCombined -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        rationale = self._build_rationale_end_static()
        self.slide_title = rationale["question_title"]
        ctx = self._build_results_stage()
        self._align_within_session_act1_to_shared_layout(ctx)
        timeres_ctx = self._build_within_session_timeres_context(ctx)
        self._show_within_session_results_rationale(rationale)
        self._animate_left_results_from_within_session_rationale(rationale, ctx)
        self._reset_to_within_session_act1_final_state(ctx)
        self.wait(0.35)
        self._animate_within_session_timeres_results(timeres_ctx)
        self.play(FadeIn(ctx["act1_takeaway"], shift=UP * 0.08), run_time=0.65)
        self.wait(1.8)

        self.play(
            FadeIn(ctx["act2_heading"], shift=UP * 0.05),
            FadeOut(ctx["act1_takeaway"], shift=DOWN * 0.06),
            FadeOut(ctx["glm_plot"], shift=DOWN * 0.08),
            FadeOut(timeres_ctx["timeres_full_state_group"], shift=DOWN * 0.08),
            run_time=0.75,
        )
        self.play(
            FadeIn(ctx["stim_small"], shift=UP * 0.05),
            FadeIn(ctx["delay_small"], shift=UP * 0.05),
            GrowArrow(ctx["cross_phase_arrow"]),
            FadeIn(ctx["cross_phase_label"], shift=UP * 0.04),
            run_time=0.70,
        )
        self.wait(0.45)
        self.play(
            FadeIn(ctx["glm2_title"], shift=UP * 0.05),
            AnimationGroup(
                Create(ctx["glm2_plot_frame"]),
                FadeIn(ctx["glm2_plot_rest"], shift=UP * 0.08),
                Create(ctx["glm2_chance_line"]),
                FadeIn(ctx["glm2_chance_label"], shift=UP * 0.04),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.play(
            AnimationGroup(
                LaggedStart(*[FadeIn(dot, scale=0.75) for dot in ctx["glm2_points"]], lag_ratio=0.04),
                FadeIn(ctx["glm2_extras"], shift=UP * 0.04),
                Write(ctx["glm2_label"]),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.play(FadeIn(ctx["glm2_sig"], shift=UP * 0.03), run_time=0.5)
        self.wait(0.35)
        self._animate_tempgen_results(ctx)
        self.play(FadeIn(ctx["act2_takeaway"], shift=UP * 0.08), run_time=0.65)
        self.wait(2.0)


class Study2WithinSession1DecodingResultsA(_Study2WithinSession1DecodingBase):
    """
    Part A: stop on the within-session GLM summary.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsA -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsA -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        rationale = self._build_rationale_end_static()
        self._show_within_session_results_rationale(rationale)
        self.slide_title = rationale["question_title"]
        ctx = self._build_results_stage()
        self._align_within_session_act1_to_shared_layout(ctx)
        self._animate_left_results_from_within_session_rationale(rationale, ctx)
        self._reset_to_within_session_act1_final_state(ctx)
        self.wait(2.0)


class Study2WithinSession1DecodingResultsB(_Study2WithinSession1DecodingBase):
    """
    Part B: start from the within-session GLM summary frame and continue to time-resolved decoding.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsB -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsB -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        rationale = self._build_rationale_end_static()
        self.slide_title = rationale["question_title"]
        ctx = self._build_results_stage()
        self._align_within_session_act1_to_shared_layout(ctx)
        timeres_ctx = self._build_within_session_timeres_context(ctx)
        self._reset_to_within_session_act1_final_state(ctx)
        self.wait(0.6)
        self._animate_within_session_timeres_results(timeres_ctx)


class Study2WithinSession1DecodingResultsC(_Study2WithinSession1DecodingBase):
    """
    Part C: start from the final time-resolved frame and turn the train/test TR
    logic into an orthogonal temporal-generalisation matrix construction, stopping
    once the matrix diagonal is highlighted.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsC -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsC -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        rationale = self._build_rationale_end_static()
        self.slide_title = rationale["question_title"]
        ctx = self._build_results_stage()
        self._align_within_session_act1_to_shared_layout(ctx)
        timeres_ctx = self._build_within_session_timeres_context(ctx)
        ctx["tempgen_c_title"] = Tex(
            "Temporal generalisation within Session 1 trials",
            color=INK,
            font_size=24,
        ).move_to(self.slide_title.get_center()).set_z_index(4.25)
        self._show_within_session_act1_final_state(ctx)
        self._show_within_session_resultsb_final_state(timeres_ctx)
        self.wait(0.6)
        self._animate_within_session_tempgen_logic(ctx, timeres_ctx)


class Study2WithinSession1DecodingResultsD(_Study2WithinSession1DecodingBase):
    """
    Part D: start from the highlighted temporal-generalisation diagonal and map
    it onto the time-resolved curve and late-stage interpretation.

    Render:
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsD -ql
        uv run manim scenes/study2.py Study2WithinSession1DecodingResultsD -qh
    """

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        rationale = self._build_rationale_end_static()
        self.slide_title = rationale["question_title"]
        ctx = self._build_results_stage()
        self._align_within_session_act1_to_shared_layout(ctx)
        timeres_ctx = self._build_within_session_timeres_context(ctx)
        logic_ctx = self._show_within_session_resultsc_final_state(ctx, timeres_ctx)
        self.wait(0.6)
        self._animate_within_session_tempgen_followup(logic_ctx)
        handoff_frame = self._build_within_session_resultsd_handoff_frame()
        self.clear()
        self.add(handoff_frame)
        self.wait(0.25)


class Study2LTMResultsExplainer(_Study2WithinSession1DecodingBase):
    """
    One-slide explainer for the Study 2 long-term-memory repetition results.

    Render:
        uv run manim scenes/study2.py Study2LTMResultsExplainer -ql
        uv run manim scenes/study2.py Study2LTMResultsExplainer -qh
    """

    _LTM_BEH = str(_STUDY2_ASSET_DIR / "study2_behresults.svg")
    _LTM_GLM = str(_STUDY2_ASSET_DIR / "figure_LTM_decoding_stimulation-delay_GLM.svg")
    _LTM_TIMERES = str(_STUDY2_ASSET_DIR / "figure_LTM_decoding_timeresolved.svg")

    def _ltm_question_text(self) -> str:
        """Return the LTM question text."""
        return (
            r"Do {{Repeated}} and {{Non-repeated}} stimuli differ\\"
            r"in their similarity to sensory representations?"
        )

    def _clean_ltm_svg_path(self, svg_path: str, *, remove_text: bool = False) -> Path:
        """Normalize the LTM SVG path."""
        svg_file = Path(svg_path)
        cache_dir = Path(tempfile.gettempdir()) / "study2_ltm_svg_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        suffix = "_clean_notext" if remove_text else "_clean"
        clean_path = cache_dir / f"{svg_file.stem}{suffix}.svg"
        if clean_path.exists() and clean_path.stat().st_mtime >= svg_file.stat().st_mtime:
            return clean_path

        tree = ET.parse(svg_file)
        root = tree.getroot()
        parent_map = {child: parent for parent in root.iter() for child in parent}

        removed_any = False
        for element in list(root.iter()):
            tag = element.tag.split("}")[-1]
            if tag == "path" and element.get("d") is None:
                parent = parent_map.get(element)
                if parent is not None:
                    parent.remove(element)
                    removed_any = True
            elif remove_text and tag == "text":
                parent = parent_map.get(element)
                if parent is not None:
                    parent.remove(element)
                    removed_any = True

        if removed_any:
            tree.write(clean_path, encoding="utf-8", xml_declaration=True)
        else:
            clean_path.write_text(svg_file.read_text())
        return clean_path

    def _load_ltm_svg_plot(
        self,
        svg_path: str,
        *,
        center: np.ndarray,
        height: float,
        remove_text: bool = False,
    ) -> SVGMobject:
        """Load the LTM SVG plot."""
        svg = SVGMobject(str(self._clean_ltm_svg_path(svg_path, remove_text=remove_text)))
        svg.scale_to_fit_height(height)
        svg.move_to(center)
        self._hide_svg_background_rect(svg)
        return svg

    def _swap_svg_hex_colors(
        self,
        svg: SVGMobject,
        color_map: dict[str, str],
    ) -> None:
        """Position the SVG hex colors."""
        for submob in svg.family_members_with_points():
            stroke_hex = self._glm_svg_hex(submob.get_stroke_color())
            if stroke_hex in color_map:
                submob.set_stroke(
                    color=color_map[stroke_hex],
                    width=submob.get_stroke_width(),
                    opacity=submob.get_stroke_opacity(),
                )

            fill_hex = self._glm_svg_hex(submob.get_fill_color())
            if fill_hex in color_map:
                submob.set_fill(
                    color=color_map[fill_hex],
                    opacity=submob.get_fill_opacity(),
                )

    def _set_behaviour_svg_text_black(self, svg: SVGMobject) -> None:
        """Set up the behaviour SVG text black."""
        for submob in svg.family_members_with_points():
            stroke_hex = self._glm_svg_hex(submob.get_stroke_color())
            fill_hex = self._glm_svg_hex(submob.get_fill_color())
            if stroke_hex == "#FFFFFF" and fill_hex in {"#000000", "#4D4D4D"}:
                submob.set_stroke(opacity=0.0)
                submob.set_fill(color=BLACK, opacity=submob.get_fill_opacity())

    def _make_ltm_takeaway(self) -> VGroup:
        """Build the LTM takeaway."""
        takeaway_line = Tex(
            r"{{Repetition}} improved {{working memory performance}}, but did not make {{memory representations}} more {{sensory-like}}.",
            color=INK,
            font_size=21,
            tex_environment="center",
        )
        takeaway_line.set_color_by_tex("Repetition", _D_AMBER)
        takeaway_line.set_color_by_tex("working memory performance", self._DELAY_ACCENT)
        takeaway_line.set_color_by_tex("memory representations", self._DELAY_ACCENT)
        takeaway_line.set_color_by_tex("sensory-like", self._GLM_ACCENT)
        return self._make_takeaway([takeaway_line])

    def _ltm_timeres_frame(self, timeres_svg: SVGMobject) -> VGroup:
        """Return the LTM time-resolved frame."""
        frame_lines = [
            submob
            for submob in timeres_svg.submobjects
            if self._glm_svg_hex(submob.get_stroke_color()) == "#262626"
        ]
        verticals = [
            submob
            for submob in frame_lines
            if submob.height > submob.width and submob.height > timeres_svg.height * 0.55
        ]
        horizontals = [
            submob
            for submob in frame_lines
            if submob.width >= submob.height and submob.width > timeres_svg.width * 0.30
        ]
        if len(verticals) < 2 or len(horizontals) < 2:
            raise ValueError("Could not identify LTM time-resolved plot frame")
        return VGroup(
            min(verticals, key=lambda mob: mob.get_center()[0]),
            max(verticals, key=lambda mob: mob.get_center()[0]),
            min(horizontals, key=lambda mob: mob.get_center()[1]),
            max(horizontals, key=lambda mob: mob.get_center()[1]),
        )

    def _ltm_beh_frame(self, beh_svg: SVGMobject) -> Mobject:
        """Return the LTM behaviour frame."""
        black_lines = [
            submob
            for submob in beh_svg.submobjects
            if self._glm_svg_hex(submob.get_stroke_color()) == "#000000"
            and submob.get_stroke_opacity() > 0.0
        ]
        verticals = [
            submob
            for submob in black_lines
            if submob.height > submob.width and submob.height > beh_svg.height * 0.45
        ]
        horizontals = [
            submob
            for submob in black_lines
            if submob.width >= submob.height and submob.width > beh_svg.width * 0.55
        ]
        if not verticals or not horizontals:
            raise ValueError("Could not identify LTM behavioural plot frame")

        left_axis = max(verticals, key=lambda mob: mob.height)
        bottom_axis = max(horizontals, key=lambda mob: mob.width)
        return Rectangle(
            width=bottom_axis.width,
            height=left_axis.height,
            stroke_opacity=0.0,
            fill_opacity=0.0,
        ).move_to(
            np.array([
                left_axis.get_center()[0] + bottom_axis.width / 2,
                bottom_axis.get_center()[1] + left_axis.height / 2,
                0.0,
            ])
        )

    def _align_ltm_plot_frame(
        self,
        svg: SVGMobject,
        frame: Mobject,
        *,
        target_center_x: float,
        target_top: float,
        target_height: float,
    ) -> Mobject:
        """Position the LTM plot frame."""
        scale_factor = target_height / frame.height
        svg.scale(scale_factor)
        svg.shift(RIGHT * (target_center_x - frame.get_center()[0]))
        svg.shift(UP * (target_top - frame.get_top()[1]))
        return frame

    def _make_ltm_timeres_text_overlay(self, timeres_svg: SVGMobject, frame: VGroup) -> VGroup:

        """Build the LTM time-resolved text overlay."""
        chance_candidates = [
            submob
            for submob in self._timeres_select_many(timeres_svg, stroke_hex="#808080", min_points=4)
            if submob.width > frame.width * 0.80
        ]
        if not chance_candidates:
            raise ValueError("Could not identify LTM time-resolved chance line")
        chance_line = max(chance_candidates, key=lambda mob: mob.width)

        def _legend_line(color_hex: str) -> VMobject:
            """Return the legend line."""
            candidates = [
                submob
                for submob in self._timeres_select_many(timeres_svg, stroke_hex=color_hex, min_points=4)
                if submob.width < frame.width * 0.20
                and submob.width >= submob.height
                and submob.get_center()[0] < frame.get_center()[0]
                and submob.get_center()[1] > frame.get_top()[1] - frame.height * 0.25
            ]
            if not candidates:
                candidates = [
                    submob
                    for submob in self._timeres_select_many(timeres_svg, stroke_hex=color_hex, min_points=4)
                    if submob.get_center()[0] > frame.get_right()[0] + 0.05
                    and submob.width < frame.width * 0.25
                ]
            if not candidates:
                raise ValueError(f"Could not identify LTM legend line for {color_hex}")
            return max(candidates, key=lambda mob: mob.width)

        legend_blue = _legend_line("#4E79A7")
        legend_orange = _legend_line("#F28E2B")

        x_tick_values = ["0", "4", "8", "12", "16"]
        x_tick_positions = np.linspace(frame.get_left()[0], frame.get_right()[0], len(x_tick_values))
        x_ticks = VGroup(*[
            Tex(value, color=INK, font_size=18).move_to(
                np.array([x, frame.get_bottom()[1] - 0.14, 0.0])
            )
            for value, x in zip(x_tick_values, x_tick_positions)
        ])
        x_label = Tex("Test time (s)", color=INK, font_size=20).move_to(
            np.array([frame.get_center()[0], frame.get_bottom()[1] - 0.38, 0.0])
        )

        y_step = (chance_line.get_center()[1] - (frame.get_top()[1] - 0.14)) / 3
        y_tick_values = ["0.00", "0.06", "0.12", "0.18"]
        y_ticks = VGroup(*[
            Tex(value, color=INK, font_size=18).move_to(
                np.array([frame.get_left()[0] - 0.32, chance_line.get_center()[1] - idx * y_step, 0.0])
            )
            for idx, value in enumerate(y_tick_values)
        ])
        y_label = Tex("Accuracy (minus chance)", color=INK, font_size=20)
        y_label.rotate(PI / 2)
        y_label.move_to(
            np.array([
                frame.get_left()[0] - 0.82 + frame.width * 0.05,
                frame.get_center()[1],
                0.0,
            ])
        )

        roi_title = Tex("EVC (V1, V2, V3)", color=INK, font_size=13).move_to(
            np.array([frame.get_center()[0], frame.get_top()[1] + 0.12, 0.0])
        )

        legend_blue_label = Tex("Non-repeated", color=INK, font_size=15).next_to(
            legend_blue,
            RIGHT,
            buff=0.12,
        )
        legend_orange_label = Tex("Repeated", color=INK, font_size=15).next_to(
            legend_orange,
            RIGHT,
            buff=0.12,
        )

        return VGroup(
            x_ticks,
            x_label,
            y_ticks,
            y_label,
            roi_title,
            legend_blue_label,
            legend_orange_label,
        )

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        handoff_frame = self._build_within_session_resultsd_handoff_frame()

        question = self._make_results_heading(
            self._ltm_question_text(),
            color=BLACK,
            font_size=24,
        ).to_edge(UP, buff=0.18)
        question.set_color_by_tex("Repeated", _D_AMBER)
        question.set_color_by_tex("Non-repeated", _D_BLUE)

        plot_title_y = question.get_bottom()[1] - 0.88
        beh_title = Tex("Behavioural results", color=INK, font_size=22).move_to(
            np.array([-4.45, plot_title_y, 0.0])
        )
        glm_title = Tex("GLM-based decoding", color=INK, font_size=22).move_to(
            np.array([0.0, plot_title_y, 0.0])
        )
        timeres_title = Tex("Time-resolved decoding", color=INK, font_size=22).move_to(
            np.array([4.1, plot_title_y, 0.0])
        )
        beh_frame_center_x = -4.45
        glm_frame_center_x = 0.0
        timeres_frame_center_x = 4.1
        target_frame_top = beh_title.get_bottom()[1] - 0.84
        beh_target_frame_height = 2.74
        target_frame_height = 3.34

        beh_svg = self._load_ltm_svg_plot(
            self._LTM_BEH,
            center=np.array([beh_frame_center_x, -0.28, 0.0]),
            height=4.28,
        )
        self._swap_svg_hex_colors(
            beh_svg,
            {
                "#4E79A7": "#F28E2B",
                "#F28E2B": "#4E79A7",
            },
        )
        self._set_behaviour_svg_text_black(beh_svg)
        beh_frame = self._ltm_beh_frame(beh_svg)
        self._align_ltm_plot_frame(
            beh_svg,
            beh_frame,
            target_center_x=beh_frame_center_x,
            target_top=target_frame_top,
            target_height=beh_target_frame_height,
        )
        glm_svg = self._load_ltm_svg_plot(
            self._LTM_GLM,
            center=np.array([glm_frame_center_x, -0.28, 0.0]),
            height=4.28,
        )
        glm_frame = self._glm_svg_plot_frame(glm_svg)
        self._align_ltm_plot_frame(
            glm_svg,
            glm_frame,
            target_center_x=glm_frame_center_x,
            target_top=target_frame_top,
            target_height=target_frame_height,
        )
        timeres_svg = self._load_ltm_svg_plot(
            self._LTM_TIMERES,
            center=np.array([timeres_frame_center_x, -0.28, 0.0]),
            height=4.28,
            remove_text=True,
        )
        timeres_frame = self._ltm_timeres_frame(timeres_svg)
        timeres_frame = self._align_ltm_plot_frame(
            timeres_svg,
            timeres_frame,
            target_center_x=timeres_frame_center_x,
            target_top=target_frame_top,
            target_height=target_frame_height,
        )
        beh_title.move_to(np.array([beh_frame_center_x, plot_title_y, 0.0]))
        glm_title.move_to(np.array([glm_frame_center_x, plot_title_y, 0.0]))
        timeres_title.move_to(np.array([timeres_frame_center_x, plot_title_y, 0.0]))
        timeres_text = self._make_ltm_timeres_text_overlay(timeres_svg, timeres_frame)

        beh_column = Group(beh_title, beh_svg)
        glm_column = Group(glm_title, glm_svg)
        timeres_plot = VGroup(timeres_svg, timeres_text)
        timeres_column = Group(timeres_title, timeres_plot)

        anchor_groups = [beh_frame, glm_frame, timeres_frame]
        column_groups = [beh_column, glm_column, timeres_column]
        base_gap = (
            config.frame_width - sum(anchor_group.width for anchor_group in anchor_groups)
        ) / (len(anchor_groups) + 1)
        extra_shifts = [0.0, 0.0, base_gap * 0.30]
        next_left = -config.frame_width / 2 + base_gap
        for anchor_group, column_group, extra_shift in zip(
            anchor_groups, column_groups, extra_shifts
        ):
            column_group.shift(RIGHT * (next_left - anchor_group.get_left()[0] + extra_shift))
            next_left += anchor_group.width + base_gap
        midpoint_x = 0.5 * (beh_frame.get_center()[0] + timeres_frame.get_center()[0])
        glm_column.shift(RIGHT * (midpoint_x - glm_frame.get_center()[0]))

        plots = Group(*column_groups)

        takeaway = self._make_ltm_takeaway()
        takeaway.move_to(np.array([0.0, -3.28, 0.0]))

        self.add(handoff_frame)
        self.wait(0.25)
        self.play(
            FadeOut(handoff_frame),
            FadeIn(question, shift=UP * 0.06),
            run_time=0.60,
        )
        self.play(
            LaggedStart(
                FadeIn(beh_title, shift=UP * 0.05),
                FadeIn(glm_title, shift=UP * 0.05),
                FadeIn(timeres_title, shift=UP * 0.05),
                FadeIn(beh_svg, shift=RIGHT * 0.10),
                FadeIn(glm_svg, shift=RIGHT * 0.10),
                FadeIn(timeres_svg, shift=LEFT * 0.10),
                FadeIn(timeres_text, shift=LEFT * 0.08),
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )
        self.play(FadeIn(takeaway, shift=UP * 0.08), run_time=0.65)
        self.wait(2.0)


class Study2SupplementalRoiTimecoursesCombined(_Study2NumberedScene, Scene):
    """
    Compare the supplemental ROI sensory -> memory temporal time courses.

    Render:
        uv run manim scenes/study2.py Study2SupplementalRoiTimecoursesCombined -ql
        uv run manim scenes/study2.py Study2SupplementalRoiTimecoursesCombined -qh
    """

    _SUPPL_ROI_DIR = _STUDY2_ASSET_DIR / "suppl_rois"
    _ROI_SVGS = [
        ("EVC (V1-V3)", _SUPPL_ROI_DIR / "decoding_suppl_roi-v1v2v3.svg"),
        ("V1", _SUPPL_ROI_DIR / "decoding_suppl_roi-V1.svg"),
        ("V2", _SUPPL_ROI_DIR / "decoding_suppl_roi-V2.svg"),
        ("V3", _SUPPL_ROI_DIR / "decoding_suppl_roi-V3.svg"),
        ("LO1", _SUPPL_ROI_DIR / "decoding_suppl_roi-LO1.svg"),
        ("LO2", _SUPPL_ROI_DIR / "decoding_suppl_roi-LO2.svg"),
        ("IPS0 / IPS1", _SUPPL_ROI_DIR / "decoding_suppl_roi-IPS0IPS1.svg"),
        ("IPS2 / IPS3", _SUPPL_ROI_DIR / "decoding_suppl_roi-IPS2IPS3.svg"),
    ]
    _TIMERES_SOURCE_BOX = (430.0, 545.0, 748.0, 850.0)
    _PLOT_WIDTH = 2.62
    _RASTER_DENSITY = 180
    _PANEL_TITLE = r"Train Session 2 $\rightarrow$ Test Session 1"
    _ROW_X_LABEL = "Test time (s)"
    _AXES_INDEX = 3
    _POLY_GROUP_ID = "PolyCollection_1"
    _CHANCE_GROUP_ID = "line2d_11"
    _EVENT_GROUP_IDS = ("line2d_12", "line2d_13", "line2d_14", "line2d_15")
    _TRACE_GROUP_ID = "line2d_16"
    _SPINE_GROUP_IDS = ("patch_13", "patch_14", "patch_15", "patch_16")
    _AXIS_STROKE = "#262626"
    _EVENT_STROKE = "#A9A9A9"
    _CHANCE_STROKE = "#808080"
    _SIG_STROKE = "#C49A00"
    _ROI_LABEL_RIGHT_SHIFT_RATIO = 0.10
    _ROW_X_LABEL_FONT_SIZE = 17
    _ROW_X_LABEL_MAX_WIDTH_RATIO = 0.72
    _ROW_X_LABEL_SHIFT = ORIGIN
    _ROW_STACK_BUFF = 0.28
    _SKIP_AXIS_TEXTS = {
        "Test time (s)",
        "Train and test time (s)",
        "Accuracy (chance subtr)",
    }

    def _cached_svg_raster(self, svg_path: Path) -> Path:
        """Return the cached SVG raster."""
        cache_dir = Path(tempfile.gettempdir()) / "study2_suppl_roi_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        raster_path = cache_dir / f"{svg_path.stem}_d{self._RASTER_DENSITY}.png"
        if raster_path.exists() and raster_path.stat().st_mtime >= svg_path.stat().st_mtime:
            return raster_path

        magick_bin = shutil.which("magick")
        if magick_bin is None:
            raise RuntimeError("ImageMagick `magick` is required to rasterize supplemental ROI SVGs")

        subprocess.run(
            [
                magick_bin,
                "-density",
                str(self._RASTER_DENSITY),
                str(svg_path),
                str(raster_path),
            ],
            check=True,
        )
        return raster_path

    @classmethod
    def _panel_spec(cls) -> dict[str, object]:
        """Return the panel spec."""
        return {
            "title": cls._PANEL_TITLE,
            "row_x_label": cls._ROW_X_LABEL,
            "axes_index": cls._AXES_INDEX,
            "poly_group_id": cls._POLY_GROUP_ID,
            "chance_group_id": cls._CHANCE_GROUP_ID,
            "event_group_ids": cls._EVENT_GROUP_IDS,
            "trace_group_id": cls._TRACE_GROUP_ID,
            "spine_group_ids": cls._SPINE_GROUP_IDS,
        }

    def _extract_target_axes_block(self, svg_path: Path, *, axes_index: int) -> str:
        """Return the extract target axes block."""
        match = re.search(
            rf'<g id="axes_{axes_index}">(.*?)<g id="axes_{axes_index + 1}">',
            svg_path.read_text(),
            flags=re.S,
        )
        if match is None:
            raise RuntimeError(f"Could not locate axes_{axes_index} block in {svg_path}")
        return match.group(1)

    def _extract_group_path(self, axes_block: str, group_id: str) -> list[tuple[float, float]]:
        """Return the extract group path."""
        match = re.search(
            rf'<g id="{group_id}">\s*<path d="(.*?)"',
            axes_block,
            flags=re.S,
        )
        if match is None:
            raise RuntimeError(f"Could not locate {group_id} in supplemental ROI SVG")

        values = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", match.group(1))]
        if not values or len(values) % 2 != 0:
            raise RuntimeError(f"Unexpected path data for {group_id}")

        return [(values[i], values[i + 1]) for i in range(0, len(values), 2)]

    def _extract_matching_group_paths(
        self,
        axes_block: str,
        group_prefix: str,
    ) -> list[list[tuple[float, float]]]:
        """Return the extract matching group paths."""
        matches = re.finditer(
            rf'<g id="({group_prefix}\d+)">\s*<path d="(.*?)"',
            axes_block,
            flags=re.S,
        )
        paths: list[list[tuple[float, float]]] = []
        for match in matches:
            values = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", match.group(2))]
            if values and len(values) % 2 == 0:
                paths.append([(values[i], values[i + 1]) for i in range(0, len(values), 2)])
        return paths

    def _extract_polycollection_polygon(self, axes_block: str, group_id: str) -> list[tuple[float, float]]:
        """Return the extract polycollection polygon."""
        match = re.search(
            (
                rf'<g id="{group_id}">.*?<path id="([^"]+)" d="(.*?)"\s*/>.*?'
                r'<use xlink:href="#\1" x="([-0-9.]+)" y="([-0-9.]+)"'
            ),
            axes_block,
            flags=re.S,
        )
        if match is None:
            raise RuntimeError(f"Could not locate {group_id} in supplemental ROI SVG")

        values = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", match.group(2))]
        if not values or len(values) % 2 != 0:
            raise RuntimeError("Unexpected path data for PolyCollection_1")

        x_offset = float(match.group(3))
        y_offset = float(match.group(4))
        return [
            (values[i] + x_offset, values[i + 1] + y_offset)
            for i in range(0, len(values), 2)
        ]

    def _extract_text_specs(self, axes_block: str) -> list[dict[str, object]]:
        """Return the extract text specs."""
        matches = re.finditer(
            (
                r'<!--\s*(.*?)\s*-->\s*<g style="fill: #262626" '
                r'transform="translate\(([-0-9.]+) ([-0-9.]+)\)'
                r'(?: rotate\(([-0-9.]+)\))? scale\(([-0-9.]+) ([-0-9.]+)\)">'
            ),
            axes_block,
            flags=re.S,
        )
        specs: list[dict[str, object]] = []
        for match in matches:
            specs.append(
                {
                    "text": match.group(1).strip(),
                    "position": (float(match.group(2)), float(match.group(3))),
                    "rotation": float(match.group(4)) if match.group(4) else 0.0,
                }
            )
        return specs

    def _supplemental_overlay_spec(
        self,
        svg_path: Path,
        panel_spec: dict[str, object],
    ) -> dict[str, object]:
        """Return the supplemental overlay spec."""
        axes_block = self._extract_target_axes_block(
            svg_path,
            axes_index=int(panel_spec["axes_index"]),
        )
        return {
            "ci": [self._extract_polycollection_polygon(axes_block, str(panel_spec["poly_group_id"]))],
            "texts": self._extract_text_specs(axes_block),
            "chance": [self._extract_group_path(axes_block, str(panel_spec["chance_group_id"]))],
            "events": [
                self._extract_group_path(axes_block, str(group_id))
                for group_id in panel_spec["event_group_ids"]
            ],
            "trace": [self._extract_group_path(axes_block, str(panel_spec["trace_group_id"]))],
            "spines": [
                self._extract_group_path(axes_block, str(group_id))
                for group_id in panel_spec["spine_group_ids"]
            ],
            "significance": self._extract_matching_group_paths(axes_block, "LineCollection_"),
        }

    def _make_plot_canvas(self) -> Rectangle:
        """Build the plot canvas."""
        x0, y0, x1, y1 = self._TIMERES_SOURCE_BOX
        canvas = Rectangle(
            width=self._PLOT_WIDTH,
            height=self._PLOT_WIDTH * ((y1 - y0) / (x1 - x0)),
            stroke_width=0.0,
        )
        canvas.set_fill(opacity=0.0)
        canvas.set_stroke(opacity=0.0)
        return canvas

    def _source_point_to_plot(self, plot: Mobject, point: tuple[float, float]) -> np.ndarray:
        """Return the source point to plot."""
        x0, y0, x1, y1 = self._TIMERES_SOURCE_BOX
        px, py = point
        u = (px - x0) / (x1 - x0)
        v = (py - y0) / (y1 - y0)
        top_left = plot.get_corner(UL)
        return top_left + RIGHT * (u * plot.width) + DOWN * (v * plot.height)

    def _plot_polyline(
        self,
        plot: Mobject,
        source_points: list[tuple[float, float]],
        *,
        color: str,
        stroke_width: float,
    ) -> VMobject:
        """Return the plot polyline."""
        points = [self._source_point_to_plot(plot, point) for point in source_points]
        polyline = VMobject()
        polyline.set_points_as_corners(points)
        polyline.set_fill(opacity=0.0)
        polyline.set_stroke(color=color, width=stroke_width)
        return polyline

    def _plot_polygon(
        self,
        plot: Mobject,
        source_points: list[tuple[float, float]],
        *,
        color: str,
        fill_opacity: float,
    ) -> Polygon:
        """Return the plot polygon."""
        points = [self._source_point_to_plot(plot, point) for point in source_points]
        polygon = Polygon(*points, stroke_width=0.0)
        polygon.set_fill(color, opacity=fill_opacity)
        return polygon

    def _plot_line(
        self,
        plot: Mobject,
        source_points: list[tuple[float, float]],
        *,
        color: str,
        stroke_width: float,
        dashed: bool = False,
        dash_length: float = 0.08,
    ) -> VMobject:
        """Return the plot line."""
        start = self._source_point_to_plot(plot, source_points[0])
        end = self._source_point_to_plot(plot, source_points[-1])
        if dashed:
            line = DashedLine(start, end, dash_length=dash_length)
        else:
            line = Line(start, end)
        line.set_stroke(color=color, width=stroke_width)
        return line

    def _make_text_overlay(self, plot: Mobject, specs: list[dict[str, object]]) -> VGroup:
        """Build the text overlay."""
        labels = VGroup()
        for spec in specs:
            text = str(spec["text"])
            if text in self._SKIP_AXIS_TEXTS:
                continue
            font_size = 12 if re.fullmatch(r"[0-9.]+", text) else 13
            label = Tex(text, color=INK, font_size=font_size)
            label.move_to(self._source_point_to_plot(plot, spec["position"]))
            if abs(float(spec["rotation"])) > 1e-3:
                label.rotate(PI / 2)
            labels.add(label)
        return labels

    def _make_plot_group(self, svg_path: Path, panel_spec: dict[str, object]) -> Group:
        """Build the plot group."""
        spec = self._supplemental_overlay_spec(svg_path, panel_spec)
        plot = self._make_plot_canvas()
        overlay = VGroup(
            self._plot_polygon(
                plot,
                spec["ci"][0],
                color="#6E6E6E",
                fill_opacity=0.30,
            )
        )

        for source_points in spec["events"]:
            overlay.add(
                self._plot_line(
                    plot,
                    source_points,
                    color=self._EVENT_STROKE,
                    stroke_width=1.5,
                    dashed=True,
                    dash_length=0.07,
                )
            )

        overlay.add(
            self._plot_line(
                plot,
                spec["chance"][0],
                color=self._CHANCE_STROKE,
                stroke_width=1.8,
                dashed=True,
                dash_length=0.10,
            )
        )

        for source_points in spec["significance"]:
            overlay.add(
                self._plot_line(
                    plot,
                    source_points,
                    color=self._SIG_STROKE,
                    stroke_width=3.2,
                )
            )

        for source_points in spec["spines"]:
            overlay.add(
                self._plot_line(
                    plot,
                    source_points,
                    color=self._AXIS_STROKE,
                    stroke_width=1.8,
                )
            )

        overlay.add(
            self._plot_polyline(
                plot,
                spec["trace"][0],
                color=BLACK,
                stroke_width=3.4,
            )
        )
        overlay.add(self._make_text_overlay(plot, spec["texts"]))
        return Group(plot, overlay)

    def _match_plot_group_to_reference(self, plot_group: Group, reference_plot_group: Group) -> Group:
        """Position the plot group to reference."""
        target_canvas = plot_group[0]
        reference_canvas = reference_plot_group[0]
        plot_group.scale(reference_canvas.width / target_canvas.width)
        plot_group.shift(reference_canvas.get_center() - plot_group[0].get_center())
        return plot_group

    def _shift_roi_labels_right(self, cards: list[Group]) -> None:
        """Position the ROI labels right."""
        for card in cards:
            card[0].shift(RIGHT * (card[1].width * self._ROI_LABEL_RIGHT_SHIFT_RATIO))

    def _build_matched_target_plots(
        self,
        source_cards: list[Group],
        panel_spec: dict[str, object],
    ) -> list[Group]:
        """Build the matched target plots."""
        target_plots: list[Group] = []
        for (_, svg_path), source_card in zip(self._ROI_SVGS, source_cards):
            target_plot = self._make_plot_group(svg_path, panel_spec)
            self._match_plot_group_to_reference(target_plot, source_card[1])
            target_plots.append(target_plot)
        return target_plots

    def _build_plot_swap_animations(
        self,
        source_cards: list[Group],
        target_plots: list[Group],
    ) -> list[AnimationGroup]:
        """Build the plot swap animations."""
        return [
            AnimationGroup(
                FadeOut(source_card[1]),
                FadeIn(target_plot),
                lag_ratio=0.0,
            )
            for source_card, target_plot in zip(source_cards, target_plots)
        ]

    def _make_column_groups(
        self,
        top_cards: Group,
        bottom_cards: Group,
    ) -> list[Group]:
        """Build the column groups."""
        return [
            Group(top_card, bottom_card)
            for top_card, bottom_card in zip(top_cards, bottom_cards)
        ]

    def _make_roi_card(self, label: str, svg_path: Path, panel_spec: dict[str, object]) -> Group:
        """Build the ROI card."""
        plot_group = self._make_plot_group(svg_path, panel_spec)
        roi_label = Tex(label, color=INK, font_size=23)
        if roi_label.width > plot_group.width * 1.08:
            roi_label.scale_to_fit_width(plot_group.width * 1.08)
        card = Group(roi_label, plot_group).arrange(DOWN, buff=0.12)
        return card

    def _make_row_group(
        self,
        cards: list[Group],
        row_x_label: str,
        *,
        include_x_label: bool,
    ) -> tuple[Group, Group, Mobject]:
        """Build the row group."""
        row_cards = Group(*cards).arrange(RIGHT, buff=0.34, aligned_edge=UP)
        accuracy_label = Tex("Accuracy", color=INK, font_size=17).rotate(PI / 2)
        accuracy_label.next_to(row_cards, LEFT, buff=0.16)
        if include_x_label:
            test_time_label = self._make_row_x_label(row_cards, row_x_label)
            test_time_label.next_to(row_cards, DOWN, buff=0.10)
            test_time_label.shift(self._ROW_X_LABEL_SHIFT)
        else:
            test_time_label = VGroup()
        return Group(row_cards, accuracy_label, test_time_label), row_cards, test_time_label

    def _make_row_x_label(self, row_cards: Group, row_x_label: str) -> Mobject:
        """Build the row x label."""
        if "\n" in row_x_label:
            test_time_label = VGroup(
                *[
                    Tex(line, color=INK, font_size=self._ROW_X_LABEL_FONT_SIZE)
                    for line in row_x_label.split("\n")
                ]
            ).arrange(DOWN, buff=0.02, center=True)
        else:
            test_time_label = Tex(row_x_label, color=INK, font_size=self._ROW_X_LABEL_FONT_SIZE)
        if test_time_label.width > row_cards.width * self._ROW_X_LABEL_MAX_WIDTH_RATIO:
            test_time_label.scale_to_fit_width(row_cards.width * self._ROW_X_LABEL_MAX_WIDTH_RATIO)
        return test_time_label

    def _build_panel(self, panel_spec: dict[str, object]) -> dict[str, object]:
        """Build the panel."""
        title = Tex(str(panel_spec["title"]), color=INK, font_size=24).to_edge(UP, buff=0.20)
        cards = [
            self._make_roi_card(label, svg_path, panel_spec)
            for label, svg_path in self._ROI_SVGS
        ]
        top_row_group, top_row_cards, top_row_x_label = self._make_row_group(
            cards[:4],
            row_x_label=str(panel_spec["row_x_label"]),
            include_x_label=False,
        )
        bottom_row_group, bottom_row_cards, bottom_row_x_label = self._make_row_group(
            cards[4:],
            row_x_label=str(panel_spec["row_x_label"]),
            include_x_label=True,
        )
        grid = Group(top_row_group, bottom_row_group).arrange(
            DOWN,
            buff=self._ROW_STACK_BUFF,
            center=True,
        )
        grid.scale_to_fit_width(config.frame_width - 0.9)

        title_gap = 0.34
        bottom_margin = 0.26
        max_grid_height = title.get_bottom()[1] - (-config.frame_height / 2 + bottom_margin) - title_gap
        if grid.height > max_grid_height:
            grid.scale_to_fit_height(max_grid_height)
        grid.next_to(title, DOWN, buff=title_gap)
        self._shift_roi_labels_right(cards)
        return {
            "title": title,
            "grid": grid,
            "cards": cards,
            "top_row_group": top_row_group,
            "bottom_row_group": bottom_row_group,
            "top_row_cards": top_row_cards,
            "bottom_row_cards": bottom_row_cards,
            "top_row_x_label": top_row_x_label,
            "bottom_row_x_label": bottom_row_x_label,
        }

    def _play_panel_intro(self, panel: dict[str, object]) -> None:
        """Animate the panel intro."""
        column_groups = self._make_column_groups(
            panel["top_row_cards"],
            panel["bottom_row_cards"],
        )
        self.play(FadeIn(panel["title"], shift=UP * 0.06), run_time=0.45)
        self.play(
            FadeIn(panel["top_row_group"][1], shift=RIGHT * 0.04),
            FadeIn(panel["bottom_row_group"][1], shift=RIGHT * 0.04),
            FadeIn(panel["bottom_row_group"][2], shift=UP * 0.04),
            LaggedStart(
                *[FadeIn(column_group, shift=UP * 0.08) for column_group in column_groups],
                lag_ratio=0.10,
            ),
            run_time=1.05,
        )

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        panel = self._build_panel(self._panel_spec())
        self._play_panel_intro(panel)
        self.wait(2.0)


class Study2SupplementalRoiTimecoursesA(Study2SupplementalRoiTimecoursesCombined):
    """
    Alias for panel A.

    Render:
        uv run manim scenes/study2.py Study2SupplementalRoiTimecoursesA -ql
        uv run manim scenes/study2.py Study2SupplementalRoiTimecoursesA -qh
    """


class Study2SupplementalRoiTimecoursesB(Study2SupplementalRoiTimecoursesCombined):
    """
    Alias for panel B.

    Render:
        uv run manim scenes/study2.py Study2SupplementalRoiTimecoursesB -ql
        uv run manim scenes/study2.py Study2SupplementalRoiTimecoursesB -qh
    """

    _TIMERES_SOURCE_BOX = (430.0, 902.165354, 748.0, 1207.165354)
    _PANEL_TITLE = r"Train Session 1 $\rightarrow$ Test Session 1"
    _AXES_INDEX = 5
    _POLY_GROUP_ID = "PolyCollection_2"
    _CHANCE_GROUP_ID = "line2d_24"
    _EVENT_GROUP_IDS = ("line2d_25", "line2d_26", "line2d_27", "line2d_28")
    _TRACE_GROUP_ID = "line2d_29"
    _SPINE_GROUP_IDS = ("patch_23", "patch_24", "patch_25", "patch_26")

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        panel_a_scene = Study2SupplementalRoiTimecoursesA()
        panel_a = panel_a_scene._build_panel(panel_a_scene._panel_spec())
        self.add(panel_a["title"], panel_a["grid"])
        self.wait(0.25)

        title_b = Tex(self._PANEL_TITLE, color=INK, font_size=24).move_to(panel_a["title"])
        target_plots = self._build_matched_target_plots(panel_a["cards"], self._panel_spec())
        target_cards = [
            Group(source_card[0].copy(), target_plot)
            for source_card, target_plot in zip(panel_a["cards"], target_plots)
        ]
        target_columns = self._make_column_groups(
            Group(*target_cards[:4]),
            Group(*target_cards[4:]),
        )
        b_shared_labels = Group(
            panel_a["top_row_group"][1].copy(),
            panel_a["bottom_row_group"][1].copy(),
            panel_a["bottom_row_group"][2].copy(),
        )

        self.play(
            FadeOut(panel_a["title"]),
            FadeOut(panel_a["grid"]),
            run_time=0.20,
        )
        self.play(
            FadeIn(title_b),
            FadeIn(b_shared_labels),
            LaggedStart(
                *[FadeIn(column_group) for column_group in target_columns],
                lag_ratio=0.10,
            ),
            run_time=0.72,
        )
        self.wait(2.0)


class Study2SupplementalRoiTempGenMats(Study2SupplementalRoiTimecoursesCombined):
    """
    Compare temporal-generalisation matrices across ROI definitions.

    Render:
        uv run manim scenes/study2.py Study2SupplementalRoiTempGenMats -ql
        uv run manim scenes/study2.py Study2SupplementalRoiTempGenMats -qh
    """

    _ROI_SVGS = [
        (r"V1--V3", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-v1v2v3.svg"),
        ("V1", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-V1.svg"),
        ("V2", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-V2.svg"),
        ("V3", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-V3.svg"),
        ("LO1", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-LO1.svg"),
        ("LO2", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-LO2.svg"),
        ("IPS0 / IPS1", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-IPS0IPS1.svg"),
        ("IPS2 / IPS3", Study2SupplementalRoiTimecoursesCombined._SUPPL_ROI_DIR / "temp_gen_mat_roi-IPS2IPS3.svg"),
    ]
    _TEMPGEN_PLOT_HEIGHT = 2.02
    _TEMPGEN_SOURCE_PLOT_BOX = (
        316.771654,
        204.094488,
        554.88189,
        442.204724,
    )
    _TEMPGEN_SOURCE_COLORBAR_BOX = (
        566.7874,
        204.094488,
        576.31181,
        442.204724,
    )
    _TEMPGEN_SOURCE_CROP_BOX = (
        315.4,
        202.7,
        582.6,
        443.6,
    )
    _TEMPGEN_AXIS_TICKS = (0, 4, 8, 12, 16)
    _TEMPGEN_COLORBAR_TICKS = (-0.10, -0.05, 0.00, 0.05, 0.10)

    def _sanitized_tempgen_svg(self, svg_path: Path) -> Path:
        """Normalize the temporal-generalisation SVG."""
        cache_dir = Path(tempfile.gettempdir()) / "study2_tempgen_svg_sanitized"
        cache_dir.mkdir(parents=True, exist_ok=True)
        sanitized_path = cache_dir / svg_path.name
        if sanitized_path.exists() and sanitized_path.stat().st_mtime >= svg_path.stat().st_mtime:
            return sanitized_path

        tree = ET.parse(svg_path)
        root = tree.getroot()
        parent_map = {child: parent for parent in root.iter() for child in parent}
        for elem in list(root.iter()):
            if elem.tag.endswith("path") and elem.get("d") is None:
                parent = parent_map.get(elem)
                if parent is not None:
                    parent.remove(elem)
        tree.write(sanitized_path, encoding="utf-8", xml_declaration=True)
        return sanitized_path

    def _tempgen_transform_matrix(self, transform: str) -> tuple[float, float, float, float, float, float]:
        """Return the temporal-generalisation transform matrix."""
        transform = transform.strip()
        matrix_match = re.search(
            r"matrix\(\s*([-0-9.eE]+)[ ,]+([-0-9.eE]+)[ ,]+([-0-9.eE]+)[ ,]+([-0-9.eE]+)[ ,]+([-0-9.eE]+)[ ,]+([-0-9.eE]+)\s*\)",
            transform,
        )
        if matrix_match is not None:
            return tuple(float(matrix_match.group(index)) for index in range(1, 7))

        translate_match = re.search(
            r"translate\(\s*([-0-9.eE]+)(?:[ ,]+([-0-9.eE]+))?\s*\)",
            transform,
        )
        if translate_match is not None:
            return (
                1.0,
                0.0,
                0.0,
                1.0,
                float(translate_match.group(1)),
                float(translate_match.group(2) or 0.0),
            )

        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    def _tempgen_svg_context(self, svg_path: Path) -> tuple[ET.Element, tuple[float, float, float, float], tuple[float, float]]:
        """Return the temporal-generalisation SVG context."""
        root = ET.parse(self._sanitized_tempgen_svg(svg_path)).getroot()
        view_box = tuple(float(value) for value in root.get("viewBox").replace(",", " ").split())

        wrapper_offset = (0.0, 0.0)
        for elem in root.iter():
            transform = elem.get("transform")
            if transform is None:
                continue
            a, b, c, d, e, f = self._tempgen_transform_matrix(transform)
            if (
                abs(a - 1.0) < 1e-6
                and abs(b) < 1e-6
                and abs(c) < 1e-6
                and abs(d - 1.0) < 1e-6
                and e < -100
                and f < -100
            ):
                wrapper_offset = (e, f)
                break

        return root, view_box, wrapper_offset

    def _tempgen_source_point_to_raster(
        self,
        *,
        view_box: tuple[float, float, float, float],
        wrapper_offset: tuple[float, float],
        raster_size: tuple[int, int],
        point: tuple[float, float],
    ) -> tuple[float, float]:
        """Return the temporal-generalisation source point to raster."""
        view_x0, view_y0, view_w, view_h = view_box
        offset_x, offset_y = wrapper_offset
        display_x = point[0] + offset_x
        display_y = point[1] + offset_y
        raster_w, raster_h = raster_size
        return (
            (display_x - view_x0) / view_w * raster_w,
            (display_y - view_y0) / view_h * raster_h,
        )

    def _supplemental_tempgen_panel(
        self,
        svg_path: Path,
    ) -> np.ndarray:
        """Return the supplemental temporal-generalisation panel."""
        raster_path = self._cached_svg_raster(svg_path)
        _, view_box, wrapper_offset = self._tempgen_svg_context(svg_path)

        with Image.open(raster_path) as image:
            image = image.convert("RGBA")
            top_left = self._tempgen_source_point_to_raster(
                view_box=view_box,
                wrapper_offset=wrapper_offset,
                raster_size=image.size,
                point=(self._TEMPGEN_SOURCE_CROP_BOX[0], self._TEMPGEN_SOURCE_CROP_BOX[1]),
            )
            bottom_right = self._tempgen_source_point_to_raster(
                view_box=view_box,
                wrapper_offset=wrapper_offset,
                raster_size=image.size,
                point=(self._TEMPGEN_SOURCE_CROP_BOX[2], self._TEMPGEN_SOURCE_CROP_BOX[3]),
            )
            crop_box = (
                max(0, int(np.floor(min(top_left[0], bottom_right[0])))),
                max(0, int(np.floor(min(top_left[1], bottom_right[1])))),
                min(image.width, int(np.ceil(max(top_left[0], bottom_right[0])))),
                min(image.height, int(np.ceil(max(top_left[1], bottom_right[1])))),
            )
            return np.array(image.crop(crop_box))

    def _tempgen_path_polylines(
        self,
        path_d: str,
    ) -> list[list[tuple[float, float]]]:
        """Return the temporal-generalisation path polylines."""
        element = SVGPath(path_d)
        polylines: list[list[tuple[float, float]]] = []
        current: list[tuple[float, float]] = []
        for segment in element:
            segment_name = type(segment).__name__
            if segment_name == "Move":
                if len(current) >= 2:
                    polylines.append(current)
                current = [(float(segment.end.x), float(segment.end.y))]
                continue

            if not current and getattr(segment, "start", None) is not None:
                current = [(float(segment.start.x), float(segment.start.y))]

            if getattr(segment, "end", None) is not None:
                current.append((float(segment.end.x), float(segment.end.y)))

            if segment_name == "Close" and current:
                current.append(current[0])

        if len(current) >= 2:
            polylines.append(current)
        return polylines

    def _tempgen_source_point_to_plot(
        self,
        plot: ImageMobject,
        *,
        source_box: tuple[float, float, float, float],
        point: tuple[float, float],
    ) -> np.ndarray:
        """Return the temporal-generalisation source point to plot."""
        src_x0, src_y0, src_x1, src_y1 = source_box
        px, py = point
        u = (px - src_x0) / (src_x1 - src_x0)
        v = (py - src_y0) / (src_y1 - src_y0)
        top_left = plot.get_corner(UL)
        return top_left + RIGHT * (u * plot.width) + DOWN * (v * plot.height)

    def _tempgen_polyline_mobject(
        self,
        plot: ImageMobject,
        *,
        source_box: tuple[float, float, float, float],
        source_points: list[tuple[float, float]],
        color: str,
        stroke_width: float,
    ) -> VMobject:
        """Return the temporal-generalisation polyline mobject."""
        points = [
            self._tempgen_source_point_to_plot(
                plot,
                source_box=source_box,
                point=point,
            )
            for point in source_points
        ]
        polyline = VMobject()
        polyline.set_points_as_corners(points)
        polyline.set_fill(opacity=0.0)
        polyline.set_stroke(color=color, width=stroke_width)
        return polyline

    def _make_tempgen_overlay(
        self,
        plot: ImageMobject,
        *,
        source_box: tuple[float, float, float, float],
        svg_path: Path,
    ) -> VGroup:
        """Build the temporal-generalisation overlay."""
        root, _, _ = self._tempgen_svg_context(svg_path)
        overlay = VGroup()
        box_x0, box_y0, box_x1, box_y1 = source_box
        stroke_paths: list[tuple[str, list[list[tuple[float, float]]]]] = []
        for elem in root.iter():
            if not elem.tag.endswith("path"):
                continue
            path_d = elem.get("d")
            if not path_d:
                continue
            style = (elem.get("style") or "").replace(" ", "").lower()
            if "stroke:#000000" not in style and "stroke:#262626" not in style:
                continue
            polylines = self._tempgen_path_polylines(path_d)
            if not polylines:
                continue
            xs = [point[0] for polyline in polylines for point in polyline]
            ys = [point[1] for polyline in polylines for point in polyline]
            if max(xs) < box_x0 or min(xs) > box_x1 or max(ys) < box_y0 or min(ys) > box_y1:
                continue
            stroke_paths.append((style, polylines))

        for style, polylines in stroke_paths:
            is_black = "stroke:#000000" in style
            is_dashed = "stroke-dasharray" in style
            color = "#000000" if is_black else "#262626"
            if is_dashed and polylines:
                start = self._tempgen_source_point_to_plot(
                    plot,
                    source_box=source_box,
                    point=polylines[0][0],
                )
                end = self._tempgen_source_point_to_plot(
                    plot,
                    source_box=source_box,
                    point=polylines[0][-1],
                )
                overlay.add(
                    DashedLine(
                        start,
                        end,
                        dash_length=0.09,
                    ).set_stroke(color=color, width=1.4)
                )
                continue

            for polyline in polylines:
                overlay.add(
                    self._tempgen_polyline_mobject(
                        plot,
                        source_box=source_box,
                        source_points=polyline,
                        color=color,
                        stroke_width=2.0 if is_black else 1.4,
                    )
                )

        overlay.set_z_index(3)
        return overlay

    def _make_tempgen_text_overlay(self, plot: ImageMobject) -> VGroup:
        """Build the temporal-generalisation text overlay."""
        plot_left = self._tempgen_source_point_to_plot(
            plot,
            source_box=self._TEMPGEN_SOURCE_CROP_BOX,
            point=(self._TEMPGEN_SOURCE_PLOT_BOX[0], self._TEMPGEN_SOURCE_PLOT_BOX[3]),
        )
        plot_right = self._tempgen_source_point_to_plot(
            plot,
            source_box=self._TEMPGEN_SOURCE_CROP_BOX,
            point=(self._TEMPGEN_SOURCE_PLOT_BOX[2], self._TEMPGEN_SOURCE_PLOT_BOX[3]),
        )
        plot_top = self._tempgen_source_point_to_plot(
            plot,
            source_box=self._TEMPGEN_SOURCE_CROP_BOX,
            point=(self._TEMPGEN_SOURCE_PLOT_BOX[0], self._TEMPGEN_SOURCE_PLOT_BOX[1]),
        )
        colorbar_left = self._tempgen_source_point_to_plot(
            plot,
            source_box=self._TEMPGEN_SOURCE_CROP_BOX,
            point=(self._TEMPGEN_SOURCE_COLORBAR_BOX[0], self._TEMPGEN_SOURCE_COLORBAR_BOX[3]),
        )
        colorbar_right = self._tempgen_source_point_to_plot(
            plot,
            source_box=self._TEMPGEN_SOURCE_CROP_BOX,
            point=(self._TEMPGEN_SOURCE_COLORBAR_BOX[2], self._TEMPGEN_SOURCE_COLORBAR_BOX[3]),
        )
        colorbar_top = self._tempgen_source_point_to_plot(
            plot,
            source_box=self._TEMPGEN_SOURCE_CROP_BOX,
            point=(self._TEMPGEN_SOURCE_COLORBAR_BOX[0], self._TEMPGEN_SOURCE_COLORBAR_BOX[1]),
        )

        plot_left_x = float(plot_left[0])
        plot_right_x = float(plot_right[0])
        plot_bottom_y = float(plot_left[1])
        plot_top_y = float(plot_top[1])
        colorbar_left_x = float(colorbar_left[0])
        colorbar_right_x = float(colorbar_right[0])
        colorbar_bottom_y = float(colorbar_left[1])
        colorbar_top_y = float(colorbar_top[1])

        tick_font_size = 10
        cbar_font_size = 10
        tick_length = 0.05
        x_tick_y = plot_bottom_y - 0.14
        y_tick_x = plot_left_x - 0.15
        cbar_tick_x0 = colorbar_right_x + 0.01
        cbar_tick_x1 = cbar_tick_x0 + tick_length
        cbar_label_x = cbar_tick_x1 + 0.12
        cbar_title_x = cbar_label_x + 0.22

        labels = VGroup()

        x_positions = np.linspace(plot_left_x, plot_right_x, len(self._TEMPGEN_AXIS_TICKS))
        y_positions = np.linspace(plot_bottom_y, plot_top_y, len(self._TEMPGEN_AXIS_TICKS))
        cbar_positions = np.linspace(
            colorbar_bottom_y,
            colorbar_top_y,
            len(self._TEMPGEN_COLORBAR_TICKS),
        )

        for x_pos, tick in zip(x_positions, self._TEMPGEN_AXIS_TICKS):
            labels.add(
                Line(
                    np.array([x_pos, plot_bottom_y, 0.0]),
                    np.array([x_pos, plot_bottom_y + tick_length, 0.0]),
                ).set_stroke("#262626", width=1.2)
            )
            tick_label = Tex(str(tick), color=INK, font_size=tick_font_size)
            tick_label.move_to(np.array([x_pos, x_tick_y, 0.0]))
            labels.add(tick_label)

        for y_pos, tick in zip(y_positions, self._TEMPGEN_AXIS_TICKS):
            labels.add(
                Line(
                    np.array([plot_left_x, y_pos, 0.0]),
                    np.array([plot_left_x - tick_length, y_pos, 0.0]),
                ).set_stroke("#262626", width=1.2)
            )
            tick_label = Tex(str(tick), color=INK, font_size=tick_font_size)
            tick_label.move_to(np.array([y_tick_x, y_pos, 0.0]))
            labels.add(tick_label)

        for y_pos, tick in zip(cbar_positions, self._TEMPGEN_COLORBAR_TICKS):
            labels.add(
                Line(
                    np.array([cbar_tick_x0, y_pos, 0.0]),
                    np.array([cbar_tick_x1, y_pos, 0.0]),
                ).set_stroke("#262626", width=1.2)
            )
            tick_label = Tex(f"{tick:.2f}", color=INK, font_size=cbar_font_size)
            tick_label.move_to(np.array([cbar_label_x, y_pos, 0.0]))
            labels.add(tick_label)

        cbar_title = Tex("Accuracy", color=INK, font_size=12)
        cbar_title.rotate(PI / 2)
        cbar_title.move_to(
            np.array([cbar_title_x, (colorbar_top_y + colorbar_bottom_y) / 2, 0.0])
        )
        labels.add(cbar_title)

        labels.set_z_index(4)
        return labels

    def _make_tempgen_plot_group(self, svg_path: Path) -> Group:
        """Build the temporal-generalisation plot group."""
        panel_array = self._supplemental_tempgen_panel(svg_path)
        plot = ImageMobject(panel_array)
        plot.scale_to_fit_height(self._TEMPGEN_PLOT_HEIGHT)
        overlay = self._make_tempgen_overlay(
            plot,
            source_box=self._TEMPGEN_SOURCE_CROP_BOX,
            svg_path=svg_path,
        )
        labels = self._make_tempgen_text_overlay(plot)
        return Group(plot, overlay, labels)

    def _make_tempgen_roi_card(self, label: str, svg_path: Path) -> Group:
        """Build the temporal-generalisation ROI card."""
        plot_group = self._make_tempgen_plot_group(svg_path)
        roi_label = Tex(label, color=INK, font_size=23)
        if roi_label.width > plot_group.width * 1.08:
            roi_label.scale_to_fit_width(plot_group.width * 1.08)
        card = Group(roi_label, plot_group).arrange(DOWN, buff=0.12)
        roi_label.shift(LEFT * (plot_group.width * 0.07))
        return card

    def _make_tempgen_row_group(self, cards: list[Group]) -> tuple[Group, Group]:
        """Build the temporal-generalisation row group."""
        row_cards = Group(*cards).arrange(RIGHT, buff=0.34, aligned_edge=UP)
        row_y_label = Tex("Test time (s)", color=INK, font_size=21)
        row_y_label.rotate(PI / 2)
        row_y_label.next_to(row_cards, LEFT, buff=0.18)
        return Group(row_cards, row_y_label), row_cards

    def _make_tempgen_column_x_labels(
        self,
        top_row_cards: Group,
        bottom_row_cards: Group,
    ) -> VGroup:
        """Build the temporal-generalisation column x labels."""
        labels = VGroup()
        for top_card, bottom_card in zip(top_row_cards, bottom_row_cards):
            label = Tex("Train time (s)", color=INK, font_size=20)
            label.next_to(bottom_card, DOWN, buff=0.14)
            label.set_x((top_card.get_center()[0] + bottom_card.get_center()[0]) / 2)
            labels.add(label)
        return labels

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG

        title = Tex(
            r"Temporal-generalisation matrices across ROIs",
            color=INK,
            font_size=26,
        ).to_edge(UP, buff=0.22)

        cards = [self._make_tempgen_roi_card(label, svg_path) for label, svg_path in self._ROI_SVGS]
        top_row_group, top_row = self._make_tempgen_row_group(cards[:4])
        bottom_row_group, bottom_row = self._make_tempgen_row_group(cards[4:])
        row_stack = Group(top_row_group, bottom_row_group).arrange(DOWN, buff=0.48, center=True)
        column_x_labels = self._make_tempgen_column_x_labels(top_row, bottom_row)
        grid = Group(row_stack, column_x_labels)
        grid.scale_to_fit_width(config.frame_width - 0.84)

        title_gap = 0.34
        bottom_margin = 0.26
        max_grid_height = title.get_bottom()[1] - (-config.frame_height / 2 + bottom_margin) - title_gap
        if grid.height > max_grid_height:
            grid.scale_to_fit_height(max_grid_height)
        grid.next_to(title, DOWN, buff=title_gap)

        self.play(FadeIn(title, shift=UP * 0.06), run_time=0.55)
        self.play(
            LaggedStart(
                *[FadeIn(card, shift=UP * 0.08) for card in top_row],
                lag_ratio=0.10,
            ),
            LaggedStart(
                *[FadeIn(card, shift=UP * 0.08) for card in bottom_row],
                lag_ratio=0.10,
            ),
            run_time=1.05,
        )
        self.play(
            FadeIn(top_row_group[1], shift=RIGHT * 0.04),
            FadeIn(bottom_row_group[1], shift=RIGHT * 0.04),
            FadeIn(column_x_labels, shift=UP * 0.04),
            run_time=0.35,
        )
        self.wait(2.0)


# ══════════════════════════════════════════════════════════════════════════════
# Study2Searchlight
# ══════════════════════════════════════════════════════════════════════════════

_SEARCHLIGHT_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "images" / "study2"
_SEARCHLIGHT_LILAC = "#66023C"
_SEARCHLIGHT_CUT_COORDS_Z = (-12, 0, 10, 21, 32, 46, 61)
_SEARCHLIGHT_DELAY_BRAIN_PNG = _SEARCHLIGHT_ASSET_DIR / "searchlight_delay_ses01.png"
_SEARCHLIGHT_STIM_PNGS = (
    _SEARCHLIGHT_ASSET_DIR / "searchlight_stim_01.png",
    _SEARCHLIGHT_ASSET_DIR / "searchlight_stim_02.png",
    _SEARCHLIGHT_ASSET_DIR / "searchlight_stim_03.png",
)
_SEARCHLIGHT_DELAY_PNGS = (
    _SEARCHLIGHT_ASSET_DIR / "searchlight_delay_01.png",
)

_SEARCHLIGHT_MINI_S2_VALUES = np.array([0.88, 0.26, 0.74, 0.34, 0.94, 0.42, 0.68, 0.20, 0.82])
_SEARCHLIGHT_MINI_S1_VALUES = np.array([0.22, 0.84, 0.28, 0.78, 0.18, 0.90, 0.36, 0.72, 0.24])
_SEARCHLIGHT_MINI_DELAY_VALUES = np.array([0.20, 0.74, 0.34, 0.58, 0.26, 0.80, 0.42, 0.68, 0.24])

_SEARCHLIGHT_STIMULATION_SPECS = [
    {
        "path": _SEARCHLIGHT_ASSET_DIR / "spm_fwec_k-09_p-001_session02.nii",
        "image_path": _SEARCHLIGHT_STIM_PNGS[0],
        "cluster_info": r"FPR $< .001$, clusters $> 9$ voxels",
        "mini_specs": [
            {
                "values": _SEARCHLIGHT_MINI_S2_VALUES,
                "color": _D_PURP,
                "label": r"$S_2$",
                "label_direction": UP,
                "description": ("Stimulation", "Session 2"),
            },
            {
                "values": _SEARCHLIGHT_MINI_S2_VALUES,
                "color": _D_PURP,
                "label": r"$S_2$",
                "label_direction": DOWN,
                "description": ("Stimulation", "Session 2"),
            },
        ],
    },
    {
        "path": _SEARCHLIGHT_ASSET_DIR / "spm_fwec_k-27_p-001_ses02-01_encoding.nii",
        "image_path": _SEARCHLIGHT_STIM_PNGS[1],
        "cluster_info": r"FPR $< .001$, clusters $> 27$ voxels",
        "mini_specs": [
            {
                "values": _SEARCHLIGHT_MINI_S2_VALUES,
                "color": _D_PURP,
                "label": r"$S_2$",
                "label_direction": UP,
                "description": ("Stimulation", "Session 2"),
            },
            {
                "values": _SEARCHLIGHT_MINI_S1_VALUES,
                "color": _SEARCHLIGHT_LILAC,
                "label": r"$S_1$",
                "label_direction": DOWN,
                "description": ("Stimulation", "Session 1"),
            },
        ],
    },
    {
        "path": _SEARCHLIGHT_ASSET_DIR / "searchlight_spm_fwec_k-13_p-001_within-ses01_encoding.nii",
        "image_path": _SEARCHLIGHT_STIM_PNGS[2],
        "cluster_info": r"FPR $< .001$, clusters $> 13$ voxels",
        "mini_specs": [
            {
                "values": _SEARCHLIGHT_MINI_S1_VALUES,
                "color": _SEARCHLIGHT_LILAC,
                "label": r"$S_1$",
                "label_direction": UP,
                "description": ("Stimulation", "Session 1"),
            },
            {
                "values": _SEARCHLIGHT_MINI_S1_VALUES,
                "color": _SEARCHLIGHT_LILAC,
                "label": r"$S_1$",
                "label_direction": DOWN,
                "description": ("Stimulation", "Session 1"),
            },
        ],
    },
]

_SEARCHLIGHT_DELAY_SPECS = [
    {
        "path": _SEARCHLIGHT_ASSET_DIR / "spm_fwec_k-13_p-001_delay.nii",
        "image_path": _SEARCHLIGHT_DELAY_PNGS[0],
        "cluster_info": r"FPR $< .001$, clusters $> 13$ voxels",
        "mini_specs": [
            {
                "values": _SEARCHLIGHT_MINI_DELAY_VALUES,
                "color": _D_GREEN,
                "label": r"$D_1$",
                "label_direction": UP,
                "description": ("Delay", "Session 1"),
            },
            {
                "values": _SEARCHLIGHT_MINI_DELAY_VALUES,
                "color": _D_GREEN,
                "label": r"$D_1$",
                "label_direction": DOWN,
                "description": ("Delay", "Session 1"),
            },
        ],
    },
]


def _study2_build_plot_stat_map_rgba(
    map_path: str | Path,
    *,
    figure_size: tuple[float, float] = (11.6, 3.5),
    colorbar: bool = True,
    cut_coords: tuple[int, ...] = _SEARCHLIGHT_CUT_COORDS_Z,
) -> np.ndarray:
    """Build an RGBA rendering of a statistical brain map plot."""
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
            stat_map_img=str(map_path),
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


def _study2_make_small_results_matrix(
    values: np.ndarray,
    color: str,
    label: str,
    *,
    label_direction: np.ndarray = UP,
    scale_factor: float = 1.35,
) -> VGroup:
    """Build the compact matrix view used in the Study 2 results layouts."""
    rows = VGroup(*[
        _make_feature_row(
            values[row_idx * 3 : (row_idx + 1) * 3],
            color=_RESULTS_MATRIX_DIVERGING_HIGH_COLOR,
            cell_w=0.11,
            cell_h=0.11,
            gap=0.022,
            low_color=_RESULTS_MATRIX_DIVERGING_LOW_COLOR,
            mid_color=_RESULTS_MATRIX_DIVERGING_MID_COLOR,
            high_color=_RESULTS_MATRIX_DIVERGING_HIGH_COLOR,
            stroke_color=_RESULTS_MATRIX_STROKE_COLOR,
            stroke_width=0.65,
        )
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


class _Study2SearchlightSceneBase(_Study2NumberedScene, Scene):
    """Shared layout for the Study 2 searchlight scenes."""

    _TITLE_TEXT = ""
    _ROW_SPECS: list[dict] = []
    _SUPPLEMENTAL_IMAGE_PATH: Path | None = None
    _SUPPLEMENTAL_IMAGE_WIDTH: float = 5.4
    _SUPPLEMENTAL_IMAGE_BUFF: float = 0.14

    def _matrix_stack(self, mini_specs: list[dict]) -> Group:
        """Return the matrix stack."""
        matrices = Group()
        matrix_objects: list[VGroup] = []
        for spec in mini_specs:
            matrix = _study2_make_small_results_matrix(
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

    def _row_group(
        self,
        *,
        path: Path,
        cluster_info: str,
        mini_specs: list[dict],
        image_path: Path | None = None,
    ) -> Group:
        """Return the row group."""
        matrix_stack = self._matrix_stack(mini_specs)
        if image_path is None:
            plot_image = ImageMobject(
                _study2_build_plot_stat_map_rgba(
                    path,
                    figure_size=(8.6, 1.65),
                    colorbar=False,
                )
            )
        else:
            plot_image = ImageMobject(str(image_path))
        plot_image.scale_to_fit_width(9.9)
        cluster_caption = Tex(cluster_info, color=INK, font_size=18)
        plot_group = Group(plot_image, cluster_caption).arrange(DOWN, buff=0.05)
        return Group(matrix_stack, plot_group).arrange(RIGHT, buff=1.12, aligned_edge=UP)

    def _content_group(self, rows: Group) -> tuple[Group, ImageMobject | None]:
        """Return the content group."""
        if self._SUPPLEMENTAL_IMAGE_PATH is None:
            return rows, None

        supplemental = ImageMobject(str(self._SUPPLEMENTAL_IMAGE_PATH))
        supplemental.scale_to_fit_width(self._SUPPLEMENTAL_IMAGE_WIDTH)
        supplemental.next_to(rows, DOWN, buff=self._SUPPLEMENTAL_IMAGE_BUFF)
        if len(rows) == 1:
            supplemental.set_x(rows[0][1].get_center()[0])
        return Group(rows, supplemental), supplemental

    def construct(self) -> None:
        """Run the animation sequence for this scene."""
        self.camera.background_color = BG
        title = Tex(rf"\textbf{{{self._TITLE_TEXT}}}", color=INK, font_size=28).to_edge(UP, buff=0.28)

        rows = Group(*[self._row_group(**spec) for spec in self._ROW_SPECS])
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        content, supplemental = self._content_group(rows)
        max_width = config.frame_width - 0.15
        max_height = config.frame_height - 0.95
        width_scale = max_width / content.width if content.width > max_width else 1.0
        height_scale = max_height / content.height if content.height > max_height else 1.0
        content.scale(min(width_scale, height_scale))
        content.next_to(title, DOWN, buff=0.16)

        self.play(FadeIn(title, shift=UP * 0.08), run_time=0.45)
        self.play(
            LaggedStart(
                *[FadeIn(row, shift=UP * 0.10) for row in rows],
                lag_ratio=0.18,
            ),
            run_time=1.35,
        )
        if supplemental is not None:
            self.play(FadeIn(supplemental, shift=UP * 0.08), run_time=0.45)
        self.wait(1.6)


class Study2SearchlightStimulation(_Study2SearchlightSceneBase):
    """GLM-based searchlight decoding montage during stimulation."""

    _TITLE_TEXT = "GLM-based searchlight decoding during Stimulation"
    _ROW_SPECS = _SEARCHLIGHT_STIMULATION_SPECS


class Study2SearchlightDelay(_Study2SearchlightSceneBase):
    """GLM-based searchlight decoding montage during delay."""

    _TITLE_TEXT = "GLM-based searchlight decoding during Delay"
    _ROW_SPECS = _SEARCHLIGHT_DELAY_SPECS
    _SUPPLEMENTAL_IMAGE_PATH = _SEARCHLIGHT_DELAY_BRAIN_PNG


_STUDY2_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    Study2ResearchQuestions,
    Study2ExperimentalDesign,
    Study2DecodingOverviewA,
    Study2DecodingOverviewB,
    Study2DecodingOverviewC,
    Study2WithinSession2DecodingSetup,
    Study2WithinSession2DecodingResults,
    Study2CrossSessionDecodingSetup,
    Study2CrossSessionDecodingResultsA,
    Study2CrossSessionDecodingResultsB,
    Study2WithinSession1DecodingSetupA,
    Study2WithinSession1DecodingSetupB,
    Study2WithinSession1DecodingResultsA,
    Study2WithinSession1DecodingResultsB,
    Study2WithinSession1DecodingResultsC,
    Study2WithinSession1DecodingResultsD,
    Study2LTMResultsExplainer,
    Study2SupplementalRoiTimecoursesA,
    Study2SupplementalRoiTimecoursesB,
    Study2SupplementalRoiTempGenMats,
    Study2SearchlightStimulation,
    Study2SearchlightDelay,
    Study2DecodingSummary,
)
_STUDY2_SECTION_NAMES: tuple[str, ...] = (
    "study2_research_questions",
    "study2_experimental_design",
    "study2_decoding_overview_a",
    "study2_decoding_overview_b",
    "study2_decoding_overview_c",
    "study2_within_session2_decoding_setup",
    "study2_within_session2_decoding_results",
    "study2_cross_session_decoding_setup",
    "study2_cross_session_decoding_results_a",
    "study2_cross_session_decoding_results_b",
    "study2_within_session1_decoding_setup_a",
    "study2_within_session1_decoding_setup_b",
    "study2_within_session1_decoding_results_a",
    "study2_within_session1_decoding_results_b",
    "study2_within_session1_decoding_results_c",
    "study2_within_session1_decoding_results_d",
    "study2_ltm_results_explainer",
    "study2_supplemental_roi_timecourses_a",
    "study2_supplemental_roi_timecourses_b",
    "study2_supplemental_roi_temp_gen_mats",
    "study2_searchlight_stimulation",
    "study2_searchlight_delay",
    "study2_decoding_summary",
)


class Study2(
    Study2LTMResultsExplainer,
    Study2SupplementalRoiTempGenMats,
    Study2SearchlightDelay,
    Study2ResearchQuestions,
    Study2ExperimentalDesign,
):
    """
    Unified production render for Study 2.

    This master scene emits the full narrative from one continuous scene via
    ``--save_sections``.
    """

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        zip(_STUDY2_SECTION_NAMES, _STUDY2_MASTER_SECTION_ORDER)
    )

    def _legacy_scene_proxy(self, scene_cls: type[Scene]) -> Scene:
        """Return a scene-typed proxy sharing this scene's live state."""
        # Replayed legacy scene bodies mutate `self` heavily; use a typed proxy
        # so MRO-dependent helper lookups still resolve against the original class.
        proxy = scene_cls.__new__(scene_cls)
        proxy.__dict__ = self.__dict__
        return proxy

    def _reset_master_scene_state(self) -> None:
        """Reset mobjects and camera placement before replaying one legacy scene."""
        plt.close("all")
        gc.collect()
        self.clear()
        # ``Scene.clear()`` only empties ``mobjects`` / ``foreground_mobjects``.
        # The master Study 2 render replays many legacy sections through one live
        # Scene instance, so stale per-animation bookkeeping from earlier sections
        # must also be cleared before the next scene starts adding new mobjects.
        self.animations = None
        self.stop_condition = None
        self.moving_mobjects = []
        self.static_mobjects = []
        self.duration = 0.0
        self.last_t = 0.0
        if hasattr(self.renderer, "static_image"):
            self.renderer.static_image = None
        if hasattr(self.camera, "reset"):
            self.camera.reset()
        self.camera.background_color = BG
        if hasattr(self.camera, "frame_center"):
            self.camera.frame_center = ORIGIN.copy()
            _study2_clear_camera_context_cache(self.camera)
        gc.collect()

    def _hold_previous_section_frame(self) -> None:
        """Pin the previous section's last frame into the next section."""
        self.wait(1 / config.frame_rate)

    def _render_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        """Replay one existing Study 2 scene inside the master section render."""
        if carry_previous_frame and not config.save_sections:
            self._hold_previous_section_frame()
        self._reset_master_scene_state()
        self.next_section(section_name)
        scene_cls.construct(self._legacy_scene_proxy(scene_cls))

    def construct(self) -> None:
        """Render the full Study 2 narrative as one sectioned scene."""
        self._reset_master_scene_state()
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._render_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )


_HIDDEN_STUDY2_SCENES: tuple[type[Scene], ...] = (
    Study2ResearchQuestions,
    Study2ExperimentalDesign,
    Study2DecodingOverviewA,
    Study2DecodingOverviewB,
    Study2DecodingOverviewC,
    Study2DecodingSummary,
    Study2WithinSession2DecodingSetup,
    Study2WithinSession2DecodingResults,
    Study2CrossSessionDecodingSetup,
    Study2CrossSessionDecodingResultsA,
    Study2CrossSessionDecodingResultsB,
    Study2CrossSessionDecodingResultsCombined,
    _Study2WithinSession1DecodingBase,
    Study2WithinSession1DecodingSetupCombined,
    Study2WithinSession1DecodingSetupA,
    Study2WithinSession1DecodingSetupB,
    Study2WithinSession1DecodingResultsCombined,
    Study2WithinSession1DecodingResultsA,
    Study2WithinSession1DecodingResultsB,
    Study2WithinSession1DecodingResultsC,
    Study2WithinSession1DecodingResultsD,
    Study2LTMResultsExplainer,
    Study2SupplementalRoiTimecoursesCombined,
    Study2SupplementalRoiTimecoursesA,
    Study2SupplementalRoiTimecoursesB,
    Study2SupplementalRoiTempGenMats,
    _Study2SearchlightSceneBase,
    Study2SearchlightStimulation,
    Study2SearchlightDelay,
)

for _scene_cls in _HIDDEN_STUDY2_SCENES:
    _scene_cls.__module__ = "_study2_internal"
del _scene_cls
Study2.__module__ = __name__
__all__ = ["Study2"]
