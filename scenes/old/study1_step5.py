"""
Study 1, Step 5 — LPIPS-guided selection of interpolation steps.

Render:
    uv run manim scenes/study1_step5.py Study1Step5Handoff -qh
    uv run manim scenes/study1_step5.py Study1Step5Deck -qh
    uv run manim scenes/study1_step5.py Study1Step5LPIPS -qh
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image as PILImage

from manim import *
from utils import REPO_ROOT, env_path

# ── Palette ─────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
BLUE  = "#2563EB"   # anchor colour
ORNG  = "#EA580C"   # selected steps colour

# ── Paths ────────────────────────────────────────────────────────────────────────
_INTERP_DIR = env_path(
    "FISH_INTERPOLATIONS_DIR",
    REPO_ROOT / "assets" / "images" / "study1" / "fish_interpolations",
)
_LPIPS_CSV = env_path(
    "SIMILARITY_INTERPOLATIONS_FISH_CSV",
    REPO_ROOT / "assets" / "data" / "study1" / "lpips-squeeze-mat-interpols-animal-fish.csv",
)

ANCHOR_NAME = "ANI-FIS-interpol-000.png"

SELECTED_INDICES: list[int] = [0, 1, 12, 21, 31, 38, 42, 63, 91, 199]

# ── Step-4 helpers (handoff transition) ─────────────────────────────────────────
_C_Z1  = "#DC2626"
_C_ZA  = "#D97706"
_C_ARC = "#93C5FD"


def _slerp(u: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
    cos_t = float(np.clip(np.dot(u, v), -1.0, 1.0))
    theta = np.arccos(cos_t)
    if abs(np.sin(theta)) < 1e-8:
        return (1.0 - t) * u + t * v
    return (np.sin((1.0 - t) * theta) * u + np.sin(t * theta) * v) / np.sin(theta)


def _vec3(start, end, color, sw: float = 3.5, tl: float = 0.18) -> Arrow:
    return Arrow(
        np.asarray(start, dtype=float),
        np.asarray(end,   dtype=float),
        color=color, stroke_width=sw, tip_length=tl, buff=0,
        max_stroke_width_to_length_ratio=100,
    )


# ── Data & pixel loading ─────────────────────────────────────────────────────────

def load_lpips_to_anchor(csv_path: Path, anchor_name: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(csv_path, index_col=0)
    df.index.name = None
    names  = df.index.tolist()
    scores = df[anchor_name].to_numpy()
    return names, scores


def load_pixels(images_dir: Path, image_names: list[str], sz: int = 256) -> np.ndarray:
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
    rotation_deg: float = 0.0,
    step_x: float       = 0.38,
    step_y: float       = 0.020,
    depth_scale: float  = 0.998,
) -> Group:
    total   = len(image_names)
    sample  = np.linspace(0, total - 1, n_visible).round().astype(int).tolist()
    endpoint_indices = {0, total - 1}
    selected_set = set(selected_indices)
    visible = sorted(
        (set(sample) | {i for i in selected_indices if i not in endpoint_indices})
        - endpoint_indices
    )
    n       = len(visible)

    placeholder_rank = None
    candidate_ranks = [
        rank for rank, img_idx in enumerate(visible)
        if img_idx not in selected_set
    ]
    if candidate_ranks:
        center = (n - 1) / 2
        placeholder_rank = min(candidate_ranks, key=lambda rank: abs(rank - center))

    thumbs = Group()
    for rank, img_idx in enumerate(visible):
        if rank == placeholder_rank:
            continue

        mob = ImageMobject(str(images_dir / image_names[img_idx]))
        mob.height = thumb_h
        mob.is_placeholder = False
        mob.img_idx = img_idx

        mob.move_to([rank * step_x, rank * step_y, 0.0])
        mob.set_opacity(1.0)
        mob.set_z_index(n - rank)
        thumbs.add(mob)

    thumbs.move_to(ORIGIN)
    return thumbs, placeholder_rank


def find_thumb(deck: Group, img_idx: int) -> Group:
    candidates = [t for t in deck if not getattr(t, "is_placeholder", False)]
    return min(candidates, key=lambda t: abs(t.img_idx - img_idx))


def row_layout_for_mobs(
    mobs: list[Mobject],
    target_h: float,
    buff: float,
    max_width: float,
    y: float = 0.0,
) -> tuple[float, float, list[np.ndarray]]:
    raw_widths = [
        mob.width * (target_h / max(mob.height, 1e-6))
        for mob in mobs
    ]
    total_w = sum(raw_widths) + buff * max(len(mobs) - 1, 0)
    scale = min(1.0, max_width / max(total_w, 1e-6))
    final_h = target_h * scale
    final_buff = buff * scale
    final_widths = [w * scale for w in raw_widths]

    positions: list[np.ndarray] = []
    cursor = -(sum(final_widths) + final_buff * max(len(mobs) - 1, 0)) / 2
    for width in final_widths:
        positions.append(np.array([cursor + width / 2, y, 0.0]))
        cursor += width + final_buff

    return final_h, final_buff, positions


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


def build_placeholder_card(card_h: float) -> Mobject:
    box = Square(side_length=card_h)
    box.set_stroke(opacity=0)
    box.set_fill(opacity=0)

    dots = Text("...", color=INK, font_size=30)
    dots.move_to(box.get_center())

    mob = Group(box, dots)
    mob.is_placeholder = True
    return mob


# ══════════════════════════════════════════════════════════════════════════════════
# Base class
# ══════════════════════════════════════════════════════════════════════════════════

class _Study1Step5Base(ThreeDScene):

    def build_common_state(self) -> dict:
        self.camera.background_color = BG
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)

        # ── Layout constants ──────────────────────────────────────────────────
        # Scenes 1 & 2 — anchor / guide side-by-side
        P1_IMG_H    = 2.40
        P1_ANCHOR_X = -2.80
        P1_INTERP_X =  2.80
        P1_IMG_Y    =  0.20

        # Scene 3 — deck layout
        ANCHOR_X         = -5.50
        STRIP_Y          =  1.80
        STRIP_ANCHOR_GAP =  0.50
        THUMB_H          =  0.55
        ROT_DEG          =  0.0
        STEP_X           =  0.030
        STEP_Y           =  0.0
        DEPTH_SCALE      =  1.0
        N_VISIBLE        =  12

        # ── 1. Data ───────────────────────────────────────────────────────────
        image_names, lpips_scores = load_lpips_to_anchor(_LPIPS_CSV, ANCHOR_NAME)
        selected_indices          = SELECTED_INDICES
        pixels                    = load_pixels(_INTERP_DIR, image_names, sz=256)
        N                         = len(pixels)

        # ── 2. Title (Scene 3) ────────────────────────────────────────────────
        title = Tex(
            r"Selecting Interpolation Steps",
            color=INK, font_size=36,
        ).to_edge(UP, buff=0.36)

        # ── 3. Anchor / guide — borderless, used by Scenes 1 & 2 ─────────────
        anchor_simple = ImageMobject(pixels[0]).set_height(P1_IMG_H).move_to(
            [P1_ANCHOR_X, P1_IMG_Y, 0.0]
        )
        guide_simple = ImageMobject(pixels[-1]).set_height(P1_IMG_H).move_to(
            [P1_INTERP_X, P1_IMG_Y, 0.0]
        )
        anchor_grp = Group(anchor_simple)
        guide_grp  = Group(guide_simple)
        anchor_simple.set_z_index(100)
        guide_simple.set_z_index(100)

        # ── 4. Anchor panel (Scene 3) ─────────────────────────────────────────
        anchor_panel = build_anchor_panel(_INTERP_DIR, ANCHOR_NAME)
        anchor_panel.move_to([ANCHOR_X, STRIP_Y, 0.0])

        # ── 5. Deck ───────────────────────────────────────────────────────────
        deck, placeholder_rank = build_deck(
            _INTERP_DIR, image_names, N_VISIBLE, selected_indices,
            thumb_h=THUMB_H, rotation_deg=ROT_DEG,
            step_x=STEP_X, step_y=STEP_Y, depth_scale=DEPTH_SCALE,
        )
        deck_left = anchor_panel.get_right()[0] + STRIP_ANCHOR_GAP
        deck.move_to([deck_left + deck.width / 2, STRIP_Y, 0.0])

        deck_label = Tex(
            r"200 interpolation steps", color=MGREY, font_size=16,
        ).next_to(deck, UP, buff=0.15)

        deck_count_label = Tex(r"200 interpolated images", color=INK, font_size=24)

        return {
            "image_names":       image_names,
            "lpips_scores":      lpips_scores,
            "selected_indices":  selected_indices,
            "pixels":            pixels,
            "N":                 N,
            # Scenes 1 & 2
            "anchor_simple":     anchor_simple,
            "guide_simple":      guide_simple,
            "anchor_grp":        anchor_grp,
            "guide_grp":         guide_grp,
            # Scene 3
            "anchor_panel":      anchor_panel,
            "deck":              deck,
            "placeholder_rank":  placeholder_rank,
            "deck_label":        deck_label,
            "deck_count_label":  deck_count_label,
        }

    def _deck_final_layout(self, st: dict) -> dict:
        anchor_grp = st["anchor_grp"]
        guide_grp = st["guide_grp"]
        deck = st["deck"]
        placeholder_rank = st["placeholder_rank"]

        anchor_target = np.array([-4.9, 2.15, 0.0])
        guide_target  = np.array([ 4.9, 2.15, 0.0])
        deck_target_y = 2.28
        target_h = anchor_grp[0].height * 0.24

        edge_gap = 0.18
        inner_left  = anchor_target[0] + (target_h / 2) + edge_gap
        inner_right = guide_target[0]  - (target_h / 2) - edge_gap
        available_w = inner_right - inner_left

        card_w = target_h
        total_slots = len(deck) + (1 if placeholder_rank is not None else 0)
        step_x = max(0.0, (available_w - card_w) / max(total_slots - 1, 1))
        start_x = inner_left + card_w / 2
        slot_centers = []
        slot_scales = []
        slot_opacities = []
        for idx in range(total_slots):
            t = idx / max(total_slots - 1, 1)
            x = start_x + idx * step_x
            y = deck_target_y + 0.58 * np.sin(np.pi * t)
            recede = np.sin(np.pi * t)
            slot_centers.append(np.array([x, y, 0.0]))
            slot_scales.append(1.0 - 0.22 * recede)
            slot_opacities.append(1.0 - 0.20 * recede)

        final_centers = []
        final_scales = []
        final_opacities = []
        placeholder_center = None
        placeholder_scale = None
        for idx in range(total_slots):
            if placeholder_rank is not None and idx == placeholder_rank:
                placeholder_center = slot_centers[idx]
                placeholder_scale = slot_scales[idx]
                continue
            final_centers.append(slot_centers[idx])
            final_scales.append(slot_scales[idx])
            final_opacities.append(slot_opacities[idx])

        return {
            "anchor_target": anchor_target,
            "guide_target": guide_target,
            "target_h": target_h,
            "edge_gap": edge_gap,
            "final_centers": final_centers,
            "final_scales": final_scales,
            "final_opacities": final_opacities,
            "placeholder_center": placeholder_center,
            "placeholder_scale": placeholder_scale,
        }

    def _apply_deck_card_layout(self, deck: Group, layout: dict) -> None:
        center = (len(deck) - 1) / 2
        for idx, card in enumerate(deck):
            card.set_height(layout["target_h"])
            card.move_to(layout["final_centers"][idx])
            card.scale(layout["final_scales"][idx])
            card.set_opacity(layout["final_opacities"][idx])
            card.set_z_index(10 + abs(idx - center))

    def setup_deck_final_state(self, st: dict) -> None:
        layout = self._deck_final_layout(st)
        deck = st["deck"]
        anchor_grp = st["anchor_grp"]
        guide_grp = st["guide_grp"]
        placeholder_rank = st["placeholder_rank"]

        anchor_grp.scale(0.5)
        anchor_grp.move_to(layout["anchor_target"])
        guide_grp.scale(0.5)
        guide_grp.move_to(layout["guide_target"])
        anchor_grp[0].set_z_index(100)
        guide_grp[0].set_z_index(100)

        self._apply_deck_card_layout(deck, layout)

        placeholder = None
        if placeholder_rank is not None:
            placeholder = build_placeholder_card(layout["target_h"])
            placeholder.set_height(layout["target_h"])
            placeholder.move_to(layout["placeholder_center"])
            placeholder.scale(layout["placeholder_scale"])
            placeholder.set_opacity(1.0)
            placeholder.set_z_index(20)
        st["_placeholder"] = placeholder

        deck_count_label = st["deck_count_label"]
        deck_count_label.to_edge(UP, buff=0.2)
        if placeholder is not None:
            self.add(anchor_grp, guide_grp, deck, placeholder)
        else:
            self.add(anchor_grp, guide_grp, deck)
        self.add_fixed_in_frame_mobjects(deck_count_label)

    # ── Phase 0: step-4 handoff ───────────────────────────────────────────────
    def play_step4_handoff(self, st: dict) -> None:
        """
        Replicate step-4's final state (α=1 SLERP), then:
          A — fade out all 3-D decorations and borders;
          B — rotate camera to flat 2-D view;
          C — float anchor and guide (borderless) to P1 positions, labels appear.
        """
        pixels = st["pixels"]

        # ── Step-4 geometry ───────────────────────────────────────────────────
        R      = 2.85
        z0_dir = np.array([0.0, 1.0, 1.0]); z0_dir /= np.linalg.norm(z0_dir)
        z1_dir = np.array([1.0, 1.0, 0.0]); z1_dir /= np.linalg.norm(z1_dir)
        tip0, tip1 = R * z0_dir, R * z1_dir

        # ── XY ground grid ────────────────────────────────────────────────────
        STEP, L_XY, L_Z = 0.5, 4.8, 3.95
        GRID_R = L_XY * 0.9
        grid_lines = VGroup(*[
            seg
            for k in np.arange(-GRID_R, GRID_R + STEP * 0.5, STEP)
            for seg in (
                Line(np.array([k, -GRID_R, 0.0]), np.array([k,  GRID_R, 0.0]),
                     color=LGREY, stroke_width=0.9),
                Line(np.array([-GRID_R, k, 0.0]), np.array([ GRID_R, k, 0.0]),
                     color=LGREY, stroke_width=0.9),
            )
        ])

        # ── Coordinate axes ───────────────────────────────────────────────────
        ax_x = _vec3(ORIGIN, [L_XY, 0, 0], MGREY, sw=2.4, tl=0.24)
        ax_y = _vec3(ORIGIN, [0, L_XY, 0], MGREY, sw=2.4, tl=0.24)
        ax_z = _vec3(ORIGIN, [0, 0, L_Z], MGREY, sw=2.4, tl=0.24)
        lab_ax = MathTex(r"x", color=MGREY, font_size=30).move_to([L_XY + 0.32, 0.0, 0.0])
        lab_ay = MathTex(r"y", color=MGREY, font_size=30).move_to([0.0, L_XY + 0.32, 0.0])
        lab_az = MathTex(r"z", color=MGREY, font_size=30).move_to([0.18, 0.18, L_Z - 0.08])

        # ── Data vectors (α=1 → z_α coincides with z₁) ───────────────────────
        vec_z0 = _vec3(ORIGIN, tip0, BLUE, sw=4.2, tl=0.28)
        vec_z1 = _vec3(ORIGIN, tip1, _C_Z1, sw=4.2, tl=0.28)
        arc_3d = ParametricFunction(
            lambda t: R * _slerp(z0_dir, z1_dir, t),
            t_range=[0.0, 1.0, 0.005],
            color=_C_ARC, stroke_width=4,
        )
        tip_a  = R * _slerp(z0_dir, z1_dir, 1.0)
        vec_za = _vec3(ORIGIN, tip_a, _C_ZA, sw=4.2, tl=0.28)
        lab_za = MathTex(r"\mathbf{z}_\alpha", color=_C_ZA, font_size=36).move_to(
            tip_a * 1.30
        )

        # ── Thumbnails ────────────────────────────────────────────────────────
        THUMB_H = 0.95
        thumb0  = ImageMobject(pixels[0]).set_height(THUMB_H)
        thumb0.move_to(tip0 + z0_dir * 0.92)
        border0 = SurroundingRectangle(thumb0, color=BLUE, stroke_width=2.5, buff=0.03)

        t1_offset = np.array([THUMB_H / 2 + 0.05, THUMB_H / 2, 0.16])
        thumb1  = ImageMobject(pixels[-1]).set_height(THUMB_H)
        thumb1.move_to(tip1 + t1_offset)
        border1 = SurroundingRectangle(thumb1, color=_C_Z1, stroke_width=2.5, buff=0.03)

        lab_z0 = Tex(r"\text{anchor}", color=BLUE, font_size=30).set_z_index(10)
        lab_z0.move_to(thumb0.get_center() + np.array([0.0, 0.0, THUMB_H / 2 + 0.26]))
        lab_z1 = Tex(r"\text{guide}", color=_C_Z1, font_size=30).set_z_index(10)
        lab_z1.move_to(thumb1.get_center() + np.array([0.0, 0.0, -(THUMB_H / 2 + 0.28)]))

        img_follow        = ImageMobject(pixels[-1]).set_height(THUMB_H).move_to(
            thumb1.get_center()
        )
        img_follow_border = SurroundingRectangle(
            img_follow, color=_C_ZA, stroke_width=2.5, buff=0.03
        )

        # ── Prompt box (fixed-in-frame) ───────────────────────────────────────
        _prompt_lines = (
            r"``award-winning marine photo",
            r"of a colorful fish in a coral reef,",
            r"centered in the scene,",
            r"vibrant underwater scene,",
            r"high detail''",
        )
        scene_title = Tex(
            r"\textit{Noise latent space} ($\mathbb{R}^n$)", color=INK, font_size=24,
        ).to_corner(UL, buff=0.45).shift(RIGHT * 1.8)
        prompt_bg = (
            RoundedRectangle(corner_radius=0.12, width=3.1, height=2.55,
                             stroke_color=LGREY, stroke_width=1.5)
            .set_fill(WHITE, opacity=0.95)
            .to_corner(UR, buff=0.22)
        )
        p_title = Tex(r"\textbf{Prompt}", color=INK, font_size=21)
        p_lines = VGroup(*[
            Tex(line, color=BLACK, font_size=17) for line in _prompt_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        VGroup(p_title, p_lines).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(
            prompt_bg.get_center()
        )

        # ── Set camera and add scene statically ───────────────────────────────
        self.set_camera_orientation(
            phi=62 * DEGREES,
            theta=-42 * DEGREES,
            frame_center=np.array([0.35, 0.2, 0.0]),
        )
        self.add(grid_lines, ax_x, ax_y, ax_z, vec_z0, vec_z1, arc_3d, vec_za)
        self.add_fixed_orientation_mobjects(
            lab_ax, lab_ay, lab_az,
            thumb0, border0, lab_z0,
            thumb1, border1, lab_z1,
            img_follow, img_follow_border, lab_za,
        )
        self.add_fixed_in_frame_mobjects(scene_title, prompt_bg, p_title, p_lines)
        self.wait(0.6)

        # ── Phase A: fade out everything except the two thumbnails ────────────
        self.play(
            FadeOut(
                grid_lines, ax_x, ax_y, ax_z,
                lab_ax, lab_ay, lab_az,
                vec_z0, vec_z1, arc_3d, vec_za, lab_za,
                border0, border1,
                img_follow, img_follow_border,
                lab_z0, lab_z1,
                scene_title, prompt_bg, p_title, p_lines,
            ),
            run_time=1.0,
        )

        # ── Phase B/C: flatten to 2-D while the images settle into place ──────
        P1_IMG_H    = 2.40
        P1_ANCHOR_X = -2.80
        P1_INTERP_X =  2.80
        P1_IMG_Y    =  0.20

        for mob in (thumb0, thumb1):
            mob.clear_updaters()

        self.move_camera(
            phi=0 * DEGREES,
            theta=-90 * DEGREES,
            frame_center=ORIGIN,
            added_anims=[
                thumb0.animate.set_height(P1_IMG_H).move_to([P1_ANCHOR_X, P1_IMG_Y, 0.0]),
                thumb1.animate.set_height(P1_IMG_H).move_to([P1_INTERP_X, P1_IMG_Y, 0.0]),
            ],
            run_time=1.2,
        )
        self.wait(0.6)

    # ── Phase 1: deck fans between anchor and guide ───────────────────────────
    def play_deck_between(self, st: dict) -> None:
        """
        Start from the handoff end-state, shrink anchor/guide into the top
        corners, and unfold the interpolation deck between them.
        """
        deck = st["deck"]
        anchor_grp = st["anchor_grp"]
        guide_grp = st["guide_grp"]
        placeholder_rank = st["placeholder_rank"]
        placeholder = None
        layout = self._deck_final_layout(st)
        anchor_grp[0].set_z_index(100)
        guide_grp[0].set_z_index(100)
        if placeholder_rank is not None:
            placeholder = build_placeholder_card(layout["target_h"])

        collapse_center = np.array([0.0, 0.95, 0.0])
        for card in deck:
            card.set_height(layout["target_h"])
            card.move_to(collapse_center)
            card.set_opacity(0)
        center = (len(deck) - 1) / 2
        for idx, card in enumerate(deck):
            card.set_z_index(10 + abs(idx - center))

        deck_unfold = AnimationGroup(*[
            card.animate.move_to(layout["final_centers"][idx]).scale(layout["final_scales"][idx]).set_opacity(
                0.0 if getattr(card, "is_placeholder", False) else layout["final_opacities"][idx]
            )
            for idx, card in enumerate(deck)
        ])

        self.play(
            anchor_grp.animate.scale(0.5).move_to(layout["anchor_target"]),
            guide_grp.animate.scale(0.5).move_to(layout["guide_target"]),
            deck_unfold,
            run_time=1.6,
        )
        self._apply_deck_card_layout(deck, layout)
        deck_count_label = st["deck_count_label"]
        deck_count_label.to_edge(UP, buff=0.2)
        self.add_fixed_in_frame_mobjects(deck_count_label)
        if placeholder is not None and placeholder_rank is not None:
            placeholder.set_height(layout["target_h"])
            placeholder.move_to(layout["placeholder_center"])
            placeholder.scale(layout["placeholder_scale"])
            placeholder.set_opacity(1.0)
            placeholder.set_z_index(20)
            self.add(placeholder)
            self.play(Write(deck_count_label), FadeIn(placeholder), run_time=0.4)
        else:
            self.play(Write(deck_count_label), run_time=0.4)
        self.wait(0.8)

    # ── Phase 2: LPIPS formula ────────────────────────────────────────────────
    def play_lpips_formula(self, st: dict) -> None:
        formula = MathTex(
            r"\mathrm{LPIPS}(\mathrm{anchor},\, x_n)",
            color=INK, font_size=34,
        ).move_to([0.0, 0.0, 0.0])
        arrow = Arrow(
            start=[0.0, 1.6, 0.0],
            end=formula.get_top() + UP * 0.12,
            color=INK, stroke_width=2.5, tip_length=0.18, buff=0.0,
        )
        self.play(GrowArrow(arrow), Write(formula), run_time=0.8)
        self.wait(0.5)
        st["_lpips_formula"] = formula
        st["_lpips_arrow"]   = arrow

    # ── Phase 3: model-based preselection ─────────────────────────────────────
    def play_preselection(self, st: dict) -> None:
        deck             = st["deck"]
        selected_indices = st["selected_indices"]

        endpoint_indices = {0, st["N"] - 1}

        selected_thumbs = [
            find_thumb(deck, i)
            for i in selected_indices
            if i not in endpoint_indices
        ]

        other_thumbs = [
            t for t in deck
            if (t not in selected_thumbs) and (t.img_idx not in endpoint_indices)
        ]

        title = Tex(r"\textbf{Model-based preselection}", color=INK, font_size=30)
        title.to_edge(UP, buff=0.36)

        selected_boxes = VGroup(*[
            SurroundingRectangle(t, color=ORNG, stroke_width=2.5, buff=0.02).set_z_index(
                t.z_index + 0.1
            )
            for t in selected_thumbs
        ])

        placeholder = st.get("_placeholder")

        fade_targets = [st["_lpips_arrow"], st["_lpips_formula"], st["deck_count_label"]]
        if placeholder is not None:
            fade_targets.append(placeholder)

        self.play(
            FadeOut(*fade_targets),
            Write(title),
            *[t.animate.set_opacity(1.0) for t in selected_thumbs],
            *[t.animate.set_opacity(0.12) for t in other_thumbs],
            run_time=0.8,
        )
        self.play(FadeIn(selected_boxes), run_time=0.4)
        st["_selected_boxes"] = selected_boxes
        self.wait(1.0)

    # ── Phase 4: bring selection + anchor + guide to front in a grid ──────────
    def play_final_reveal(self, st: dict) -> None:
        deck             = st["deck"]
        selected_indices = st["selected_indices"]
        anchor_grp       = st["anchor_grp"]
        guide_grp        = st["guide_grp"]
        endpoint_indices = {0, st["N"] - 1}

        selected_thumbs = [
            find_thumb(deck, i)
            for i in selected_indices
            if i not in endpoint_indices
        ]
        other_thumbs    = [t for t in deck if t not in selected_thumbs]
        anchor_grp.set_z_index(len(deck) + 20)
        guide_grp.set_z_index(len(deck) + 20)

        IMG_H   = 1.30
        BUFF    = 0.12

        # Final row: [anchor, selected interpolations, guide]
        row = [anchor_grp] + selected_thumbs + [guide_grp]
        final_h, _, pos = row_layout_for_mobs(
            row,
            target_h=IMG_H,
            buff=BUFF,
            max_width=config.frame_width - 0.8,
            y=0.0,
        )

        # Keep the row ordered left-to-right as anchor, selected interpolations,
        # guide, with all elements moving into their new positions together.
        row_anims = [
            mob.animate.set_height(final_h).move_to(p)
            for mob, p in zip(row, pos)
        ]

        self.play(
            FadeOut(*other_thumbs, st["_selected_boxes"]),
            run_time=0.4,
        )
        self.play(*row_anims, run_time=1.2)
        self.wait(1.0)

# ══════════════════════════════════════════════════════════════════════════════════
# Scenes
# ══════════════════════════════════════════════════════════════════════════════════

class Study1Step5Handoff(_Study1Step5Base):
    """Scene 1 — step-4 3-D ending → anchor and guide settle on screen."""
    def construct(self) -> None:
        state = self.build_common_state()
        self.play_step4_handoff(state)
        self.wait(0.5)


class Study1Step5Deck(_Study1Step5Base):
    """Scene 2 — deck of cards fans between anchor and guide."""
    def construct(self) -> None:
        state = self.build_common_state()
        self.add(state["anchor_grp"], state["guide_grp"])
        self.play_deck_between(state)
        self.wait(0.5)


class Study1Step5LPIPS(_Study1Step5Base):
    """Scene 3 — LPIPS formula, then model-based preselection of 10 images."""
    def construct(self) -> None:
        state = self.build_common_state()
        self.setup_deck_final_state(state)
        self.play_lpips_formula(state)
        self.play_preselection(state)
        self.play_final_reveal(state)
        self.wait(1.0)
