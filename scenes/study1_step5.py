"""
Study 1, Step 5 — LPIPS-guided selection of interpolation steps.

Render:
    uv run manim scenes/study1_step5.py Study1Step5 -qh
    uv run manim scenes/study1_step5.py Study1Step5Intro -qh
    uv run manim scenes/study1_step5.py Study1Step5Selection -qh
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image as PILImage

from manim import *
from scenes.utils import env_path

# ── Palette ─────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
BLUE  = "#2563EB"   # anchor colour
ORNG  = "#EA580C"   # selected steps colour

# ── Paths ────────────────────────────────────────────────────────────────────────
_INTERP_DIR = env_path("FISH_INTERPOLATIONS_DIR", Path(__file__).parent.parent / "assets" / "images" / "fish_interpolations")

_LPIPS_CSV = env_path("SIMILARITY_INTERPOLATIONS_FISH_CSV")

ANCHOR_NAME = "ANI-FIS-interpol-000.png"

# Interpolation steps selected for the stimulus set (stimulus_set_info table).
SELECTED_INDICES: list[int] = [0, 1, 12, 21, 31, 38, 42, 63, 91, 199]


# ── Data & pixel loading ─────────────────────────────────────────────────────────

def load_lpips_to_anchor(csv_path: Path, anchor_name: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(csv_path, index_col=0)
    df.index.name = None
    names  = df.index.tolist()
    scores = df[anchor_name].to_numpy()
    return names, scores


def load_pixels(images_dir: Path, image_names: list[str], sz: int = 256) -> np.ndarray:
    """Load all interpolation frames as (N, sz, sz, 4) uint8 arrays."""
    N      = len(image_names)
    pixels = np.empty((N, sz, sz, 4), dtype=np.uint8)
    for i, name in enumerate(image_names):
        pixels[i] = np.asarray(
            PILImage.open(str(images_dir / name))
            .convert("RGBA")
            .resize((sz, sz), PILImage.LANCZOS)
        )
    return pixels


# ── Visual helpers ───────────────────────────────────────────────────────────────

def build_deck(
    images_dir: Path,
    image_names: list[str],
    n_visible: int,
    selected_indices: list[int],
    thumb_h: float      = 0.55,
    rotation_deg: float = -10.0,   # clockwise → top tilts right
    step_x: float       = 0.38,    # horizontal advance per card
    step_y: float       = 0.020,   # vertical rise per card (depth perspective)
    depth_scale: float  = 0.998,   # per-card scale reduction
) -> Group:
    """
    Fan-deck of tilted thumbnails with simulated perspective depth.
    Left = front of deck (highest z_index, full opacity).
    Right = back of deck (lower z_index, reduced scale and opacity).
    Each thumb Group carries .img_idx and .border.
    Selected borders are revealed in Phase 5; all borders start LGREY.
    """
    total   = len(image_names)
    sample  = np.linspace(0, total - 1, n_visible).round().astype(int).tolist()
    visible = sorted(set(sample + selected_indices))
    n       = len(visible)

    thumbs = Group()
    for rank, img_idx in enumerate(visible):
        img = ImageMobject(str(images_dir / image_names[img_idx]))
        img.height = thumb_h
        img.rotate(rotation_deg * DEGREES)

        border = SurroundingRectangle(img, color=LGREY, buff=0.025, stroke_width=1.0)
        border.rotate(rotation_deg * DEGREES)

        scale   = depth_scale ** rank
        y_off   = rank * step_y
        opacity = 1.0 - 0.28 * rank / max(n - 1, 1)

        thumb = Group(img, border)
        thumb.scale(scale)
        thumb.move_to([rank * step_x, y_off, 0.0])
        thumb.set_opacity(opacity)
        thumb.set_z_index(n - rank)      # front card on top
        thumb.img_idx = img_idx
        thumb.border  = border
        thumbs.add(thumb)

    thumbs.move_to(ORIGIN)
    return thumbs


def find_thumb(deck: Group, img_idx: int) -> Group:
    """Return deck thumbnail whose .img_idx is closest to img_idx."""
    return min(deck, key=lambda t: abs(t.img_idx - img_idx))


def build_anchor_panel(
    images_dir: Path, anchor_name: str, img_h: float = 1.55
) -> Group:
    img    = ImageMobject(str(images_dir / anchor_name))
    img.height = img_h
    border = SurroundingRectangle(img, color=BLUE, stroke_width=2.5, buff=0.04)
    label  = Tex(r"\textbf{Anchor}", color=BLUE, font_size=22)
    panel  = Group(label, Group(img, border)).arrange(DOWN, buff=0.12)
    panel.anchor_img = img
    return panel


def build_lpips_graph(
    lpips_scores: np.ndarray,
    selected_indices: list[int],
    width: float  = 9.0,
    height: float = 1.80,
) -> dict:
    n     = len(lpips_scores)
    y_min = float(lpips_scores.min())
    y_max = float(lpips_scores.max())
    y_pad = 0.05 * (y_max - y_min)

    plot_axes = Axes(
        x_range=[0, n - 1, 50],
        y_range=[y_min - y_pad, y_max + y_pad, 0.1],
        x_length=width,
        y_length=height,
        axis_config={
            "color": INK,
            "stroke_width": 1.8,
            "include_tip": False,
            "font_size": 16,
        },
    )
    x_lbl = Tex(r"Interpolation index", color=MGREY, font_size=14).next_to(
        plot_axes.x_axis, DOWN, buff=0.16
    )
    y_lbl = (
        Tex(r"LPIPS", color=MGREY, font_size=14)
        .rotate(90 * DEGREES)
        .next_to(plot_axes.y_axis, LEFT, buff=0.14)
    )
    axes_group = VGroup(plot_axes, x_lbl, y_lbl)

    # Full curve — all 200 data points
    curve = VMobject(color=INK, stroke_width=1.8)
    curve.set_points_as_corners(
        [plot_axes.c2p(i, float(lpips_scores[i])) for i in range(n)]
    )

    sel_dots = VGroup(*[
        Dot(plot_axes.c2p(i, float(lpips_scores[i])), radius=0.058, color=ORNG)
        for i in selected_indices
    ])
    sel_guides = VGroup(*[
        DashedLine(
            plot_axes.c2p(i, y_min - y_pad),
            plot_axes.c2p(i, float(lpips_scores[i])),
            color=ORNG, stroke_width=1.4, dash_length=0.05,
        )
        for i in selected_indices
    ])

    group = VGroup(axes_group, curve, sel_guides, sel_dots)
    return {
        "group":      group,
        "axes":       axes_group,
        "plot_axes":  plot_axes,
        "x_lbl":      x_lbl,
        "y_lbl":      y_lbl,
        "curve":      curve,
        "sel_dots":   sel_dots,
        "sel_guides": sel_guides,
        # sel_curve is built in build_common_state after group is positioned
    }


# ══════════════════════════════════════════════════════════════════════════════════
# Base class
# ══════════════════════════════════════════════════════════════════════════════════

class _Study1Step5Base(Scene):

    def build_common_state(self) -> dict:
        self.camera.background_color = BG

        # ── Layout constants ──────────────────────────────────────────────────
        # Phase 1 — big animated preview
        P1_IMG_H    = 2.40
        P1_ANCHOR_X = -2.80
        P1_INTERP_X =  2.80
        P1_IMG_Y    =  0.20

        # Phase 2+ — deck layout
        ANCHOR_X         = -5.50
        STRIP_Y          =  1.80
        STRIP_ANCHOR_GAP =  0.50
        GRAPH_Y          = -1.00
        GRAPH_H          =  1.80
        THUMB_H          =  0.55
        ROT_DEG          = -10.0
        STEP_X           =  0.38
        STEP_Y           =  0.020
        DEPTH_SCALE      =  0.998
        N_VISIBLE        =  20

        # ── 1. Data ───────────────────────────────────────────────────────────
        image_names, lpips_scores = load_lpips_to_anchor(_LPIPS_CSV, ANCHOR_NAME)
        selected_indices          = SELECTED_INDICES
        pixels                    = load_pixels(_INTERP_DIR, image_names, sz=256)
        N                         = len(pixels)

        # ── 2. Title ──────────────────────────────────────────────────────────
        title = Tex(
            r"Selecting Interpolation Steps",
            color=INK, font_size=36,
        ).to_edge(UP, buff=0.36)

        # ── 3. Phase 1 objects ────────────────────────────────────────────────
        anchor_big = ImageMobject(pixels[0]).set_height(P1_IMG_H).move_to(
            [P1_ANCHOR_X, P1_IMG_Y, 0.0]
        )
        anchor_big_border = SurroundingRectangle(
            anchor_big, color=BLUE, stroke_width=2.5, buff=0.05
        )
        anchor_big_lbl = Tex(r"\textbf{Anchor}", color=BLUE, font_size=22).next_to(
            anchor_big, UP, buff=0.16
        )

        alpha_tracker  = ValueTracker(0.0)
        interp_preview = ImageMobject(pixels[0]).set_height(P1_IMG_H).move_to(
            [P1_INTERP_X, P1_IMG_Y, 0.0]
        )
        interp_border = SurroundingRectangle(
            interp_preview, color=LGREY, stroke_width=1.5, buff=0.05
        )
        interp_lbl = Tex(
            r"200 interpolation steps", color=MGREY, font_size=20,
        ).next_to(interp_preview, UP, buff=0.16)

        # ── 4. Anchor panel ───────────────────────────────────────────────────
        anchor_panel = build_anchor_panel(_INTERP_DIR, ANCHOR_NAME)
        anchor_panel.move_to([ANCHOR_X, STRIP_Y, 0.0])

        # ── 5. Deck ───────────────────────────────────────────────────────────
        deck = build_deck(
            _INTERP_DIR, image_names, N_VISIBLE, selected_indices,
            thumb_h=THUMB_H, rotation_deg=ROT_DEG,
            step_x=STEP_X, step_y=STEP_Y, depth_scale=DEPTH_SCALE,
        )
        deck_left = anchor_panel.get_right()[0] + STRIP_ANCHOR_GAP
        deck.move_to([deck_left + deck.width / 2, STRIP_Y, 0.0])

        deck_label = Tex(
            r"200 interpolation steps", color=MGREY, font_size=16,
        ).next_to(deck, UP, buff=0.15)

        # ── 6. LPIPS graph (width matches deck) ───────────────────────────────
        graph = build_lpips_graph(
            lpips_scores, selected_indices,
            width=deck.width, height=GRAPH_H,
        )
        graph["group"].move_to([deck.get_center()[0], GRAPH_Y, 0.0])

        # Selected-only curve built after group is positioned so c2p is correct
        sel_curve = VMobject(color=ORNG, stroke_width=2.4)
        sel_curve.set_points_as_corners(
            [graph["plot_axes"].c2p(i, float(lpips_scores[i])) for i in selected_indices]
        )
        graph["sel_curve"] = sel_curve

        graph_title = Tex(
            r"LPIPS to anchor", color=MGREY, font_size=16,
        ).next_to(graph["group"], UP, buff=0.15)

        # ── 7. Selector arrow ─────────────────────────────────────────────────
        sel_arrow = Arrow(
            UP * 0.32, DOWN * 0.02,
            color=ORNG, stroke_width=4.5, buff=0,
            max_tip_length_to_length_ratio=0.38,
            tip_length=0.16,
        )
        sel_arrow.move_to(deck[0].get_top() + UP * 0.24)

        # ── 8. Tracking dot ───────────────────────────────────────────────────
        tracking_dot = Dot(
            graph["plot_axes"].c2p(deck[0].img_idx, float(lpips_scores[deck[0].img_idx])),
            radius=0.055, color=BLUE,
        )

        return {
            "image_names":      image_names,
            "lpips_scores":     lpips_scores,
            "selected_indices": selected_indices,
            "pixels":           pixels,
            "N":                N,
            "title":            title,
            # Phase 1
            "alpha_tracker":    alpha_tracker,
            "anchor_big":       anchor_big,
            "anchor_big_border": anchor_big_border,
            "anchor_big_lbl":   anchor_big_lbl,
            "interp_preview":   interp_preview,
            "interp_border":    interp_border,
            "interp_lbl":       interp_lbl,
            # Phase 2+
            "anchor_panel":     anchor_panel,
            "deck":             deck,
            "deck_label":       deck_label,
            "graph":            graph,
            "graph_title":      graph_title,
            "sel_arrow":        sel_arrow,
            "tracking_dot":     tracking_dot,
        }

    # ── Phase 1: animated anchor + interpolation sequence ────────────────────
    def play_intro(self, st: dict) -> None:
        pixels = st["pixels"]
        N      = st["N"]
        pos    = st["interp_preview"].get_center().copy()
        h      = st["interp_preview"].height

        self.play(
            Write(st["title"]),
            FadeIn(st["anchor_big"], st["anchor_big_border"], st["anchor_big_lbl"]),
            run_time=0.7,
        )
        self.play(
            FadeIn(st["interp_preview"], st["interp_border"], st["interp_lbl"]),
            run_time=0.5,
        )
        # Attach updater after FadeIn so opacity animation is unaffected
        st["interp_preview"].add_updater(lambda mob: mob.become(
            ImageMobject(pixels[int(np.clip(st["alpha_tracker"].get_value() * (N - 1), 0, N - 1))])
            .set_height(h)
            .move_to(pos)
        ))
        self.play(
            st["alpha_tracker"].animate.set_value(1.0),
            run_time=3.0,
            rate_func=linear,
        )
        self.wait(0.4)

    # ── Phase 2: transition to deck layout ────────────────────────────────────
    def play_transition(self, st: dict) -> None:
        st["interp_preview"].clear_updaters()
        self.play(
            FadeOut(
                st["anchor_big"], st["anchor_big_border"], st["anchor_big_lbl"],
                st["interp_preview"], st["interp_border"], st["interp_lbl"],
            ),
            run_time=0.5,
        )
        self.play(
            FadeIn(st["anchor_panel"], shift=RIGHT * 0.12),
            LaggedStart(
                *[FadeIn(t, shift=DOWN * 0.06) for t in st["deck"]],
                lag_ratio=0.04,
                run_time=1.8,
            ),
            FadeIn(st["deck_label"], shift=DOWN * 0.05),
        )
        self.wait(0.4)

    # ── Phase 3: LPIPS graph reveal ───────────────────────────────────────────
    def play_graph(self, st: dict) -> None:
        g = st["graph"]
        self.play(
            Create(g["plot_axes"]),
            FadeIn(st["graph_title"], shift=DOWN * 0.05),
            run_time=0.8,
        )
        self.play(
            Create(g["curve"]),
            FadeIn(g["x_lbl"]),
            FadeIn(g["y_lbl"]),
            run_time=1.5,
        )
        self.wait(0.4)

    # ── Phase 4: synchronised scan ────────────────────────────────────────────
    def play_scan(self, st: dict) -> None:
        deck_list = list(st["deck"])
        n         = len(deck_list)
        lpips     = st["lpips_scores"]
        axes      = st["graph"]["plot_axes"]

        def upd_arrow(mob, alpha: float) -> None:
            i = min(int(alpha * n), n - 1)
            mob.move_to(deck_list[i].get_top() + UP * 0.24)

        def upd_dot(mob, alpha: float) -> None:
            i = min(int(alpha * n), n - 1)
            mob.move_to(axes.c2p(deck_list[i].img_idx, float(lpips[deck_list[i].img_idx])))

        self.play(FadeIn(st["sel_arrow"]), FadeIn(st["tracking_dot"]))
        self.play(
            UpdateFromAlphaFunc(st["sel_arrow"],    upd_arrow),
            UpdateFromAlphaFunc(st["tracking_dot"], upd_dot),
            run_time=3.5,
            rate_func=linear,
        )
        self.wait(0.3)

    # ── Phase 5: reveal selected steps ───────────────────────────────────────
    def play_selection(self, st: dict) -> None:
        deck             = st["deck"]
        selected_indices = st["selected_indices"]

        selected_thumbs = [find_thumb(deck, i) for i in selected_indices]
        other_thumbs    = [t for t in deck if t not in selected_thumbs]

        # Bring selected to front before animating
        for t in selected_thumbs:
            t.set_z_index(len(deck) + 2)

        self.play(
            *[t.animate.set_opacity(1.0) for t in selected_thumbs],
            *[t.border.animate.set_stroke(color=ORNG, width=2.5) for t in selected_thumbs],
            *[t.animate.set_opacity(0.30) for t in other_thumbs],
            FadeOut(st["sel_arrow"]),
            FadeOut(st["tracking_dot"]),
            FadeIn(st["graph"]["sel_dots"]),
            FadeIn(st["graph"]["sel_guides"]),
            run_time=0.9,
        )
        self.wait(0.4)

    # ── Phase 6: simplify graph to selected-only line ─────────────────────────
    def play_simplify_graph(self, st: dict) -> None:
        g = st["graph"]
        self.play(
            Transform(g["curve"], g["sel_curve"]),
            run_time=0.9,
        )
        self.wait(0.3)

    # ── Static add (for partial renders) ─────────────────────────────────────
    def add_static(self, st: dict) -> None:
        self.add(
            st["title"],
            st["anchor_panel"],
            st["deck"],
            st["deck_label"],
        )


# ══════════════════════════════════════════════════════════════════════════════════
# Scenes
# ══════════════════════════════════════════════════════════════════════════════════

class Study1Step5Intro(_Study1Step5Base):
    """Phases 1–2: animated intro and deck reveal only."""
    def construct(self) -> None:
        state = self.build_common_state()
        self.play_intro(state)
        self.play_transition(state)
        self.wait(0.8)


class Study1Step5Selection(_Study1Step5Base):
    """Phases 3–6: graph, scan, selection, graph simplification (deck pre-loaded)."""
    def construct(self) -> None:
        state = self.build_common_state()
        self.add_static(state)
        self.play_graph(state)
        self.play_scan(state)
        self.play_selection(state)
        self.play_simplify_graph(state)
        self.wait(1.0)


class Study1Step5(_Study1Step5Base):
    """Full scene — all six phases."""
    def construct(self) -> None:
        state = self.build_common_state()
        self.play_intro(state)
        self.play_transition(state)
        self.play_graph(state)
        self.play_scan(state)
        self.play_selection(state)
        self.play_simplify_graph(state)
        self.wait(1.5)
