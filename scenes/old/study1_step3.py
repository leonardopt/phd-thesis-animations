"""
Study 1, Step 3 — select anchor and guide.

Narrative arc:
  1. Start from the exemplar cloud for one fixed prompt
  2. Compute LPIPS-based scores for exemplar pairs
  3. Populate a lower-triangular similarity matrix progressively
  4. Use a custom selection algorithm to return anchor and guide

Render:
    uv run manim scenes/study1_step3.py Study1Step3 -qh
    uv run manim scenes/study1_step3.py Study1Step3Part1 -qh
    uv run manim scenes/study1_step3.py Study1Step3Part2 -qh
"""
from __future__ import annotations

import csv
import numpy as np
from pathlib import Path
from PIL import Image as PILImage

from manim import *
from utils import REPO_ROOT, env_path

# ── Palette ────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
GREY  = "#6B7280"
LGREY = "#D1D5DB"

C_ANCHOR = "#2563EB"
C_GUIDE  = "#DC2626"
C_ACCENT = "#D97706"
C_MATRIX = "#3F7F7A"
C_FLOW   = "#C58A2A"

# ── Image sources ──────────────────────────────────────────────────────────────
IMG_DIR = env_path(
    "EXEMPLAR_FISH_DIR",
    REPO_ROOT / "assets" / "images" / "study1" / "exemplar_images" / "animal" / "fish",
)
ANCHOR_NAME = "ANI-FIS-3873620486.png"
GUIDE_NAME = "ANI-FIS-4212442282.png"
SIMILARITY_CSV_PATH = env_path(
    "SIMILARITY_ANCHORS_FISH_CSV",
    REPO_ROOT / "assets" / "data" / "study1" / "lpips-squeeze-mat-animal-fish.csv",
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def cloud_positions(n: int, cx: float, cy: float):
    """
    Same deterministic ring layout used in Study1Step2.
    """
    rings = [
        (0.00,  1, 0.00),
        (0.65,  6, 0.00),
        (1.30, 12, 0.26),
        (1.95, 18, 0.00),
        (2.60, 23, 0.14),
    ]
    out, total = [], 0
    for r, n_def, off in rings:
        cnt = min(n_def, n - total)
        if cnt <= 0:
            break
        for k in range(cnt):
            ang = 2 * np.pi * k / max(cnt, 1) + off
            out.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))
        total += cnt
    return out


def choose_demo_pairs(
    cloud_pts: list[tuple[float, float]],
    cx: float,
    cy: float,
    selected_pair: tuple[int, int],
    excluded_indices: set[int],
    count: int = 8,
) -> list[tuple[int, int]]:
    """
    Pick demo pairs from different cloud regions so the LPIPS examples feel
    visually varied, while keeping pair spacing moderate, readable, and away
    from the matrix edges.
    """
    target_offsets = [
        (-1.10, 0.70),
        (-0.10, 1.55),
        (1.75, 1.00),
        (1.45, -0.90),
        (0.10, -1.85),
        (-1.15, -0.75),
        (-1.00, 0.15),
        (0.95, 0.45),
    ]
    n = len(cloud_pts)
    edge_margin = max(8, n // 7)
    distance_target = 1.95

    candidates: list[tuple[tuple[int, int], np.ndarray, float]] = []
    for i in range(n):
        if i in excluded_indices:
            continue
        for j in range(i):
            if j in excluded_indices:
                continue
            pair = tuple(sorted((i, j)))
            if pair == selected_pair:
                continue
            if j < edge_margin or i > n - 1 - edge_margin:
                continue

            (x1, y1), (x2, y2) = cloud_pts[i], cloud_pts[j]
            dist = float(np.hypot(x1 - x2, y1 - y2))
            if not 1.45 <= dist <= 2.20:
                continue

            midpoint = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
            candidates.append((pair, midpoint, dist))

    chosen: list[tuple[int, int]] = []
    used_indices = set(excluded_indices)
    for dx, dy in target_offsets:
        target = np.array([cx + dx, cy + dy])
        best_pair = None
        best_score = None
        for pair, midpoint, dist in candidates:
            i, j = pair
            if pair in chosen or i in used_indices or j in used_indices:
                continue

            score = np.linalg.norm(midpoint - target) + 0.45 * abs(dist - distance_target)
            if best_score is None or score < best_score:
                best_score = score
                best_pair = pair

        if best_pair is not None:
            chosen.append(best_pair)
            used_indices.update(best_pair)
        if len(chosen) == count:
            break

    if len(chosen) < count:
        remaining = sorted(candidates, key=lambda item: abs(item[2] - distance_target))
        for pair, _, _ in remaining:
            i, j = pair
            if pair in chosen or i in used_indices or j in used_indices:
                continue
            chosen.append(pair)
            used_indices.update(pair)
            if len(chosen) == count:
                break

    return chosen


def load_pixels(sz: int = 320) -> tuple[list[np.ndarray], list[Path]]:
    files = sorted(IMG_DIR.glob("ANI-FIS-*.png"))
    pixels = [
        np.asarray(
            PILImage.open(fp).convert("RGBA").resize((sz, sz), PILImage.LANCZOS)
        )
        for fp in files
    ]
    return pixels, files


def load_pixel(path: Path, sz: int = 320) -> np.ndarray:
    return np.asarray(
        PILImage.open(path).convert("RGBA").resize((sz, sz), PILImage.LANCZOS)
    )


def load_similarity_matrix() -> tuple[np.ndarray, list[str]]:
    with SIMILARITY_CSV_PATH.open(newline="") as f:
        rows = list(csv.reader(f))

    ordered_names = rows[0][1:]
    row_names = [row[0] for row in rows[1:]]
    if row_names != ordered_names:
        raise ValueError("Similarity CSV row/column ordering mismatch")

    scores = np.asarray(
        [[float(value) for value in row[1:]] for row in rows[1:]],
        dtype=np.float32,
    )
    return scores, ordered_names


def score_heatmap_rgba(
    scores: np.ndarray,
    row_start: int = 0,
    row_end: int | None = None,
) -> np.ndarray:
    n = scores.shape[0]
    if row_end is None:
        row_end = n

    vmax = max(float(scores.max()), 1e-6)
    norm = np.clip(scores / vmax, 0.0, 1.0)

    low = np.array([242, 247, 246, 255], dtype=np.float32)
    mid = np.array([181, 208, 204, 255], dtype=np.float32)
    high = np.array([63, 127, 122, 255], dtype=np.float32)

    colored = (
        ((1 - norm) ** 2)[..., None] * low
        + (2 * (1 - norm) * norm)[..., None] * mid
        + (norm ** 2)[..., None] * high
    ).astype(np.uint8)

    rgba = np.zeros((n, n, 4), dtype=np.uint8)
    row_mask = np.zeros(n, dtype=bool)
    row_mask[row_start:row_end] = True
    lower_mask = np.tril(np.ones((n, n), dtype=bool), k=-1)
    keep_mask = lower_mask & row_mask[:, None]
    rgba[keep_mask] = colored[keep_mask]

    diag_idx = np.arange(n)
    diag_mask = row_mask
    rgba[diag_idx[diag_mask], diag_idx[diag_mask]] = np.array(
        [248, 248, 250, 255], dtype=np.uint8
    )
    return rgba


def thumb(pixel: np.ndarray, h: float, border_color: str = LGREY, sw: float = 1.8) -> Group:
    img = ImageMobject(pixel).set_height(h)
    border = SurroundingRectangle(img, color=border_color, stroke_width=sw, buff=0.03)
    return Group(img, border)


class _Study1Step3Base(Scene):
    segment = "full"

    def construct(self) -> None:
        self.camera.background_color = BG

        pixels, files = load_pixels()
        scores_csv, ordered_names = load_similarity_matrix()
        csv_index_by_name = {name: i for i, name in enumerate(ordered_names)}
        perm = [csv_index_by_name[fp.name] for fp in files]
        scores = scores_csv[np.ix_(perm, perm)]
        n = len(pixels)
        file_index_by_name = {fp.name: i for i, fp in enumerate(files)}
        anchor_idx = file_index_by_name[ANCHOR_NAME]
        guide_idx = file_index_by_name[GUIDE_NAME]
        anchor_pixel = pixels[anchor_idx]
        guide_pixel = pixels[guide_idx]
        selected_pair = tuple(sorted((anchor_idx, guide_idx)))

        # ── Layout ───────────────────────────────────────────────────────────
        IMG_CLOUD_H = 0.45
        CLOUD_CX, CLOUD_CY = -4.15, -0.10
        MATRIX_SIDE = 4.10
        MATRIX_C = np.array([1.05, -0.28, 0.0])

        cloud_pts = cloud_positions(n, cx=CLOUD_CX, cy=CLOUD_CY)
        demo_pairs = choose_demo_pairs(
            cloud_pts,
            cx=CLOUD_CX,
            cy=CLOUD_CY,
            selected_pair=selected_pair,
            excluded_indices={anchor_idx, guide_idx},
            count=8,
        )
        cloud_imgs = [
            ImageMobject(pixels[i]).set_height(IMG_CLOUD_H).move_to(RIGHT * x + UP * y)
            for i, (x, y) in enumerate(cloud_pts)
        ]

        cloud_title = Tex(
            r"\textbf{60 exemplars} — \textit{fish}",
            color=INK, font_size=24,
        ).move_to(RIGHT * CLOUD_CX + UP * 3.20)

        matrix_title = VGroup(
            Tex(r"Neural network-based perceptual similarity", color=INK, font_size=20),
            Tex(r"\textbf{LPIPS} (Zhang et al., 2018)", color=INK, font_size=20),
        ).arrange(DOWN, buff=0.05).move_to(RIGHT * MATRIX_C[0] + UP * 3.15)

        half = MATRIX_SIDE / 2
        mat_ul = MATRIX_C + np.array([-half, half, 0.0])
        mat_dl = MATRIX_C + np.array([-half, -half, 0.0])
        mat_ur = MATRIX_C + np.array([half, half, 0.0])
        mat_dr = MATRIX_C + np.array([half, -half, 0.0])
        tri_bg = Polygon(mat_ul, mat_dl, mat_dr, stroke_width=0).set_fill("#FAFAFB", opacity=1.0)
        tri_frame = Polygon(mat_ul, mat_dl, mat_dr, color=LGREY, stroke_width=1.5)
        diag_line = Line(mat_ul, mat_dr, color=LGREY, stroke_width=1.0)
        axis_x = Tex(r"\textit{exemplar }j", color=GREY, font_size=14).next_to(tri_frame, DOWN, buff=0.15)
        axis_y = Tex(r"\textit{exemplar }i", color=GREY, font_size=14).rotate(PI / 2).next_to(tri_frame, LEFT, buff=0.15)
        tri_bg.set_z_index(0)
        tri_frame.set_z_index(2)
        diag_line.set_z_index(2)
        matrix_title.set_z_index(3)
        axis_x.set_z_index(3)
        axis_y.set_z_index(3)

        band_edges = np.linspace(0, n, 7, dtype=int)
        band_imgs = []
        for start, end in zip(band_edges[:-1], band_edges[1:]):
            band = ImageMobject(score_heatmap_rgba(scores, start, end)).set_height(MATRIX_SIDE).move_to(MATRIX_C)
            band.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
            band.set_z_index(1)
            band_imgs.append(band)

        cell = MATRIX_SIDE / n

        def cell_center(i: int, j: int) -> np.ndarray:
            i, j = max(i, j), min(i, j)
            left = MATRIX_C[0] - MATRIX_SIDE / 2
            top = MATRIX_C[1] + MATRIX_SIDE / 2
            return np.array([
                left + (j + 0.5) * cell,
                top - (i + 0.5) * cell,
                0.0,
            ])

        def pair_cell(i: int, j: int, color: str = C_ACCENT) -> Square:
            box = Square(
                side_length=max(cell * 2.2, 0.07),
                stroke_color=color,
                stroke_width=2.2,
            ).set_fill(color, opacity=0.14)
            box.move_to(cell_center(i, j))
            return box

        def score_label(i: int, j: int) -> Tex:
            score = float(scores[i, j])
            return Tex(
                rf"\textit{{score}} = {score:.3f}",
                color=C_MATRIX,
                font_size=18,
            )

        # Pairwise LPIPS demo card
        pair_title = Tex(r"\textbf{Example pairwise similarity}", color=INK, font_size=20)
        pair_l = thumb(pixels[demo_pairs[0][0]], h=0.90)
        pair_r = thumb(pixels[demo_pairs[0][1]], h=0.90)
        pair_formula = MathTex(r"\mathrm{LPIPS}(x_i,x_j)", color=C_MATRIX, font_size=24)
        pair_imgs = Group(pair_l, pair_r).arrange(RIGHT, buff=0.24)
        pair_score = score_label(*demo_pairs[0])
        pair_title.set_z_index(6)
        pair_formula.set_z_index(6)
        pair_imgs.set_z_index(6)
        pair_score.set_z_index(6)
        pair_card = Group(pair_title, pair_formula, pair_imgs, pair_score).arrange(DOWN, buff=0.12)
        pair_card.move_to(RIGHT * 5.25 + UP * 2.15)
        pair_card.set_z_index(5)

        repeat_note = Tex(
            r"\textit{repeat for all exemplar pairs}",
            color=GREY, font_size=16,
        ).next_to(pair_card, DOWN, buff=0.16)
        repeat_note.set_z_index(5)

        pair_arrow = Arrow(
            pair_card.get_left() + LEFT * 0.04 + DOWN * 0.10,
            cell_center(*demo_pairs[0]) + RIGHT * 0.10,
            buff=0.08,
            color=C_FLOW,
            stroke_width=2.0,
            tip_length=0.18,
            max_stroke_width_to_length_ratio=20,
        )
        pair_arrow.set_z_index(4)
        current_cell = pair_cell(*demo_pairs[0], color=C_FLOW)
        current_cell.set_z_index(4)

        def cloud_pair_box(idx: int) -> SurroundingRectangle:
            return SurroundingRectangle(
                cloud_imgs[idx],
                color=C_FLOW,
                stroke_width=2.4,
                buff=0.04,
            ).set_fill(C_FLOW, opacity=0.06)

        current_cloud_left = cloud_pair_box(demo_pairs[0][0])
        current_cloud_right = cloud_pair_box(demo_pairs[0][1])
        current_cloud_left.set_z_index(4)
        current_cloud_right.set_z_index(4)

        # Selection stage
        algo_title = Tex(r"\textbf{Custom selection algorithm}", color=INK, font_size=18)
        algo_body = VGroup(
            Tex(r"Batch-representative", color=GREY, font_size=15),
            Tex(r"Similar to each other", color=GREY, font_size=15),
            Tex(r"Returns \textit{anchor} and \textit{guide}", color=GREY, font_size=15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        algo_content = VGroup(algo_title, algo_body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        algo_box = RoundedRectangle(
            width=algo_content.width + 0.42,
            height=algo_content.height + 0.36,
            corner_radius=0.12,
            stroke_color=LGREY,
            stroke_width=1.4,
        ).set_fill(WHITE, opacity=0.96)
        algo_content.move_to(algo_box.get_center())
        algo_panel = Group(algo_box, algo_content).move_to(RIGHT * 5.25 + UP * 1.15)
        algo_panel.set_z_index(5)

        output_title = Tex(r"\textbf{Selected pair}", color=INK, font_size=20)
        anchor_card = thumb(anchor_pixel, h=1.02, border_color=C_ANCHOR, sw=2.4)
        guide_card = thumb(guide_pixel, h=1.02, border_color=C_GUIDE, sw=2.4)
        anchor_label = Tex(r"\textit{anchor}", color=C_ANCHOR, font_size=22)
        guide_label = Tex(r"\textit{guide}", color=C_GUIDE, font_size=22)
        anchor_panel = Group(anchor_label, anchor_card).arrange(DOWN, buff=0.12)
        guide_panel = Group(guide_label, guide_card).arrange(DOWN, buff=0.12)
        output_group = Group(anchor_panel, guide_panel).arrange(DOWN, buff=0.42)
        output_block = Group(output_title, output_group).arrange(DOWN, buff=0.18)
        output_block.move_to(RIGHT * 5.10 + DOWN * 1.65)
        output_block.set_z_index(5)

        cloud_anchor_box = SurroundingRectangle(cloud_imgs[anchor_idx], color=C_ANCHOR, stroke_width=2.5, buff=0.04)
        cloud_guide_box = SurroundingRectangle(cloud_imgs[guide_idx], color=C_GUIDE, stroke_width=2.5, buff=0.04)
        selected_cell = pair_cell(*selected_pair, color=C_ACCENT)
        selected_row = max(anchor_idx, guide_idx)
        selected_col = min(anchor_idx, guide_idx)
        row_color = C_ANCHOR if selected_row == anchor_idx else C_GUIDE
        col_color = C_ANCHOR if selected_col == anchor_idx else C_GUIDE

        def row_band(row_idx: int, color: str) -> Rectangle:
            width = (row_idx + 1) * cell
            left = MATRIX_C[0] - MATRIX_SIDE / 2
            top = MATRIX_C[1] + MATRIX_SIDE / 2
            band = Rectangle(
                width=width,
                height=cell * 0.96,
                stroke_color=color,
                stroke_width=2.6,
            ).set_fill(color, opacity=0.10)
            band.move_to(np.array([
                left + width / 2,
                top - (row_idx + 0.5) * cell,
                0.0,
            ]))
            return band

        def col_band(col_idx: int, color: str) -> Rectangle:
            height = (n - col_idx) * cell
            left = MATRIX_C[0] - MATRIX_SIDE / 2
            top = MATRIX_C[1] + MATRIX_SIDE / 2
            band = Rectangle(
                width=cell * 0.96,
                height=height,
                stroke_color=color,
                stroke_width=2.6,
            ).set_fill(color, opacity=0.10)
            band.move_to(np.array([
                left + (col_idx + 0.5) * cell,
                top - col_idx * cell - height / 2,
                0.0,
            ]))
            return band

        selected_row_band = row_band(selected_row, row_color)
        selected_col_band = col_band(selected_col, col_color)
        anchor_source_band = selected_row_band if selected_row == anchor_idx else selected_col_band
        guide_source_band = selected_row_band if selected_row == guide_idx else selected_col_band
        search_path = [
            (8, 1),
            (18, 4),
            (30, 11),
            (41, 20),
            (50, 31),
            selected_pair,
        ]
        search_cell = pair_cell(*search_path[0], color=YELLOW)
        cloud_anchor_box.set_z_index(4)
        cloud_guide_box.set_z_index(4)
        selected_cell.set_z_index(4)
        search_cell.set_z_index(4)
        selected_row_band.set_z_index(3)
        selected_col_band.set_z_index(3)

        def make_algo_scan_arrow() -> CurvedArrow:
            arrow = CurvedArrow(
                algo_panel.get_left() + LEFT * 0.08 + DOWN * 0.04,
                search_cell.get_center() + RIGHT * (cell * 0.95),
                angle=32 * DEGREES,
                color=C_FLOW,
                stroke_width=2.4,
                tip_length=0.18,
            )
            arrow.set_z_index(4)
            return arrow

        algo_scan_arrow = always_redraw(make_algo_scan_arrow)

        # ── Animation ────────────────────────────────────────────────────────
        def play_intro_and_matrix(keep_example_visible: bool = False) -> None:
            nonlocal pair_score

            self.play(
                Write(cloud_title),
                LaggedStart(*[FadeIn(m, shift=UP * 0.03) for m in cloud_imgs], lag_ratio=0.010),
                run_time=1.45,
            )
            self.wait(0.45)

            self.play(
                FadeIn(tri_bg),
                Create(tri_frame),
                Create(diag_line),
                run_time=0.65,
            )
            self.play(Write(matrix_title), run_time=0.55)
            self.wait(1.15)
            self.play(FadeIn(axis_x, axis_y), run_time=0.40)

            first_left = cloud_imgs[demo_pairs[0][0]]
            first_right = cloud_imgs[demo_pairs[0][1]]
            self.play(
                FadeIn(pair_title, pair_formula, pair_score, shift=DOWN * 0.04),
                TransformFromCopy(first_left, pair_l[0]),
                FadeIn(pair_l[1]),
                TransformFromCopy(first_right, pair_r[0]),
                FadeIn(pair_r[1]),
                FadeIn(current_cloud_left, current_cloud_right),
                Create(pair_arrow),
                FadeIn(current_cell),
                run_time=1.05,
            )
            self.wait(0.45)

            for next_pair in demo_pairs[1:]:
                new_left = thumb(pixels[next_pair[0]], h=0.90)
                new_right = thumb(pixels[next_pair[1]], h=0.90)
                new_left.move_to(pair_l.get_center())
                new_right.move_to(pair_r.get_center())
                new_score = score_label(*next_pair).move_to(pair_score.get_center())
                new_arrow = Arrow(
                    pair_card.get_left() + LEFT * 0.04 + DOWN * 0.10,
                    cell_center(*next_pair) + RIGHT * 0.10,
                    buff=0.08,
                    color=C_FLOW,
                    stroke_width=2.0,
                    tip_length=0.18,
                    max_stroke_width_to_length_ratio=20,
                )
                new_cell = pair_cell(*next_pair, color=C_FLOW)
                new_cloud_left = cloud_pair_box(next_pair[0]).set_z_index(4)
                new_cloud_right = cloud_pair_box(next_pair[1]).set_z_index(4)
                self.play(
                    Transform(pair_l, new_left),
                    Transform(pair_r, new_right),
                    FadeTransform(pair_score, new_score),
                    Transform(pair_arrow, new_arrow),
                    Transform(current_cell, new_cell),
                    Transform(current_cloud_left, new_cloud_left),
                    Transform(current_cloud_right, new_cloud_right),
                    run_time=0.65,
                )
                pair_score = new_score
                self.wait(0.14)

            self.play(Write(repeat_note), run_time=0.45)
            self.wait(0.45)
            fill_anims = [
                LaggedStart(
                    *[FadeIn(band, shift=UP * 0.02) for band in band_imgs],
                    lag_ratio=0.14,
                )
            ]
            if not keep_example_visible:
                fill_anims.extend([
                    FadeOut(current_cloud_left, current_cloud_right),
                    FadeOut(pair_arrow, current_cell),
                ])
            self.play(*fill_anims, run_time=2.20)
            self.wait(0.45)
            if not keep_example_visible:
                self.play(FadeOut(pair_card, pair_score, repeat_note), run_time=0.45)
                self.wait(0.25)

        def play_selection_sequence() -> None:
            self.play(
                FadeIn(algo_panel, shift=UP * 0.04),
                run_time=0.95,
            )
            self.wait(0.45)
            self.play(
                FadeIn(search_cell),
                FadeIn(algo_scan_arrow),
                run_time=0.45,
            )
            self.wait(0.20)
            for pair in search_path[1:]:
                self.play(
                    Transform(search_cell, pair_cell(*pair, color=YELLOW).set_z_index(4)),
                    run_time=0.34,
                )
            self.play(
                Transform(search_cell, selected_cell),
                FadeOut(algo_scan_arrow),
                run_time=0.45,
            )
            self.wait(0.35)
            self.play(
                AnimationGroup(
                    GrowFromCenter(selected_row_band),
                    GrowFromCenter(selected_col_band),
                    lag_ratio=0.18,
                ),
                FadeIn(cloud_anchor_box, cloud_guide_box),
                run_time=0.90,
            )
            self.wait(0.35)
            self.play(
                FadeIn(output_title, shift=DOWN * 0.04),
                GrowFromPoint(anchor_card, anchor_source_band.get_center()),
                GrowFromPoint(guide_card, guide_source_band.get_center()),
                FadeIn(anchor_label, target_position=anchor_source_band.get_center()),
                FadeIn(guide_label, target_position=guide_source_band.get_center()),
                run_time=1.10,
            )
            self.wait(1.45)

        def build_part1_final_frame() -> dict[str, Mobject]:
            final_pair = demo_pairs[-1]

            pair_title_final = pair_title.copy().set_z_index(6)
            pair_formula_final = pair_formula.copy().set_z_index(6)
            pair_l_final = thumb(pixels[final_pair[0]], h=0.90)
            pair_r_final = thumb(pixels[final_pair[1]], h=0.90)
            pair_imgs_final = Group(pair_l_final, pair_r_final).arrange(RIGHT, buff=0.24)
            pair_imgs_final.set_z_index(6)
            pair_score_final = score_label(*final_pair).set_z_index(6)
            pair_card_final = Group(
                pair_title_final,
                pair_formula_final,
                pair_imgs_final,
                pair_score_final,
            ).arrange(DOWN, buff=0.12)
            pair_card_final.move_to(pair_card.get_center())
            pair_card_final.set_z_index(5)

            repeat_note_final = repeat_note.copy()
            repeat_note_final.next_to(pair_card_final, DOWN, buff=0.16)
            repeat_note_final.set_z_index(5)

            pair_arrow_final = Arrow(
                pair_card_final.get_left() + LEFT * 0.04 + DOWN * 0.10,
                cell_center(*final_pair) + RIGHT * 0.10,
                buff=0.08,
                color=C_FLOW,
                stroke_width=2.0,
                tip_length=0.18,
                max_stroke_width_to_length_ratio=20,
            )
            pair_arrow_final.set_z_index(4)

            current_cell_final = pair_cell(*final_pair, color=C_FLOW)
            current_cell_final.set_z_index(4)

            current_cloud_left_final = cloud_pair_box(final_pair[0]).set_z_index(4)
            current_cloud_right_final = cloud_pair_box(final_pair[1]).set_z_index(4)

            return {
                "pair_card": pair_card_final,
                "repeat_note": repeat_note_final,
                "pair_arrow": pair_arrow_final,
                "current_cell": current_cell_final,
                "current_cloud_left": current_cloud_left_final,
                "current_cloud_right": current_cloud_right_final,
            }

        if self.segment == "selection":
            part1_final_frame = build_part1_final_frame()
            self.add(
                cloud_title,
                *cloud_imgs,
                tri_bg,
                tri_frame,
                diag_line,
                matrix_title,
                axis_x,
                axis_y,
                *band_imgs,
                part1_final_frame["pair_card"],
                part1_final_frame["repeat_note"],
                part1_final_frame["pair_arrow"],
                part1_final_frame["current_cell"],
                part1_final_frame["current_cloud_left"],
                part1_final_frame["current_cloud_right"],
            )
            self.wait(0.55)
            self.play(
                FadeOut(part1_final_frame["current_cloud_left"], part1_final_frame["current_cloud_right"]),
                FadeOut(part1_final_frame["pair_arrow"], part1_final_frame["current_cell"]),
                FadeOut(part1_final_frame["pair_card"], part1_final_frame["repeat_note"]),
                run_time=0.45,
            )
            self.wait(0.25)
            play_selection_sequence()
            return

        play_intro_and_matrix(keep_example_visible=self.segment == "matrix")
        if self.segment == "matrix":
            self.wait(1.35)
            return

        play_selection_sequence()


class Study1Step3(_Study1Step3Base):
    segment = "full"


class Study1Step3Part1(_Study1Step3Base):
    segment = "matrix"


class Study1Step3Part2(_Study1Step3Base):
    segment = "selection"
