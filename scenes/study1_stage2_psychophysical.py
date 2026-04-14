"""
Study 1, Stage 2 — Psychophysical Similarity Judgement Task.

Narrative arc:
  Scene 1 (Study1Stage2TripletTask):
    Walk through a single triplet trial: reference at top, two probes
    below.  A "participant" selects the more-similar probe.
  Scene 2 (Study1Stage2EmbeddingResult):
    Show the ordinal embedding curve that comes out of 1,113 participants'
    triplet judgements, then reveal the final reordered image strip.

Render:
    uv run manim scenes/study1_stage2_psychophysical.py Study1Stage2TripletTask -qh
    uv run manim scenes/study1_stage2_psychophysical.py Study1Stage2OrdinalEmbedding -qh
    uv run manim scenes/study1_stage2_psychophysical.py Study1Stage2EmbeddingResult -qh
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

from manim import *
from utils import env_path

# ── Palette ─────────────────────────────────────────────────────────────────────
BG    = WHITE
INK   = "#1C1C1E"
LGREY = "#D1D5DB"
MGREY = "#9CA3AF"
BLUE  = "#2563EB"
AMBER = "#D97706"

# ── Paths ────────────────────────────────────────────────────────────────────────
STIM_DIR = env_path(
    "STIMULI_REORDERED_DIR",
    Path(__file__).parent.parent / "assets" / "images" / "stimuli_reordered",
)
STAGE2_ASSET_DIR = Path(__file__).parent.parent / "assets" / "images" / "study1_stage2"


def fish_path(idx: int) -> str:
    return str(STIM_DIR / f"animal_fish-{idx:02d}.png")


def stimulus_path(prefix: str, idx: int) -> str:
    return str(STIM_DIR / f"{prefix}-{idx:02d}.png")


# Synthetic SOE embedding values for fish (monotonically decreasing, index 0 = anchor)
EMBED_Y = np.array([1.00, 0.93, 0.83, 0.70, 0.57, 0.44, 0.32, 0.20, 0.09, 0.02])


# ══════════════════════════════════════════════════════════════════════════════════
# Scene 1 — Triplet comparison task
# ══════════════════════════════════════════════════════════════════════════════════

class Study1Stage2TripletTask(Scene):
    """
    Phase 1 — introduce the task mathematically.
    Phase 2 — illustrate with fish-00 (s_i, reference), fish-02 (s_j, probe),
               fish-07 (s_k, probe) arranged in an equilateral triangle inside a box.
    """

    # ── Equilateral-triangle geometry ─────────────────────────────────────────
    _D     = 2.22    # side length  (image-centre to image-centre)
    _IMG_H = 1.18    # image height
    _CY    = -1.05   # centroid y of triangle

    def _positions(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        d, h = self._D, self._D * np.sqrt(3) / 2
        cy   = self._CY
        si = np.array([0.0,   cy + 2 * h / 3, 0.0])   # top vertex  (reference)
        sj = np.array([-d/2,  cy - h / 3,     0.0])   # bottom-left (probe j)
        sk = np.array([ d/2,  cy - h / 3,     0.0])   # bottom-right (probe k)
        return si, sj, sk

    def _make_probe(self, idx: int, pos: np.ndarray) -> tuple[ImageMobject, SurroundingRectangle]:
        img = ImageMobject(fish_path(idx)).set_height(self._IMG_H).move_to(pos)
        bdr = SurroundingRectangle(img, color=LGREY, stroke_width=1.5, buff=0.05)
        return img, bdr

    def _index_tex(self, idx: int, color: str) -> MathTex:
        return MathTex(rf"s_{{{idx + 1}}}", color=color, font_size=28)

    def _response_row(self, ref_idx: int, selected_idx: int, other_idx: int) -> VGroup:
        parts = [
            MathTex(r"(", color=INK, font_size=28),
            MathTex(str(ref_idx + 1), color=INK, font_size=28),
            MathTex(r",", color=INK, font_size=28),
            MathTex(str(selected_idx + 1), color=INK, font_size=28),
            MathTex(r",", color=INK, font_size=28),
            MathTex(str(other_idx + 1), color=INK, font_size=28),
            MathTex(r")", color=INK, font_size=28),
        ]
        return VGroup(*parts).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)

    def construct(self) -> None:
        self.camera.background_color = BG

        si_pos, sj_pos, sk_pos = self._positions()
        IMG_H = self._IMG_H
        trial_specs = [
            {"ref": 0, "left": 2, "right": 7, "selected": "left"},
            {"ref": 4, "left": 8, "right": 3, "selected": "right"},
            {"ref": 6, "left": 1, "right": 9, "selected": "left"},
            {"ref": 8, "left": 5, "right": 2, "selected": "right"},
        ]

        # ── Title + subtitle ──────────────────────────────────────────────────
        title = Tex(
            r"Psychophysical Validation",
            color=INK, font_size=38,
        ).move_to(ORIGIN)
        title_top_target = title.copy().to_edge(UP, buff=0.28)

        subtitle = Tex(
            r"Triplet similarity task \quad $N = 1{,}113$ participants",
            color=MGREY, font_size=24,
        ).next_to(title_top_target, DOWN, buff=0.10)
        question = VGroup(
            Tex(
                r"Does the model-based preselection capture",
                color=INK,
                font_size=24,
            ),
            Tex(
                r"a human-perceived perceptual continuum?",
                color=INK,
                font_size=24,
            ),
        ).arrange(DOWN, buff=0.08).next_to(subtitle, DOWN, buff=0.16)

        # ── Math block ────────────────────────────────────────────────────────
        math1 = Tex(
            r"Given a set of images $\mathcal{S} = \{s_1, s_2, \ldots, s_n\}$,",
            color=INK,
            font_size=26,
        )
        math2 = Tex(
            r"participants view triplets $(s_i,\, s_j,\, s_k)$",
            color=INK,
            font_size=26,
        )
        math3 = Tex(
            r"and select which probe is more similar",
            color=INK,
            font_size=26,
        )
        math4 = Tex(
            r"to the reference image $s_i$.",
            color=INK,
            font_size=26,
        )
        math_block = (
            VGroup(math1, math2, math3, math4)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        )

        # ── Trial layout anchors ──────────────────────────────────────────────
        lbl_h  = 0.38   # approximate label height below each image
        pad    = 0.28
        box_top    = si_pos[1] + IMG_H / 2 + pad
        box_bottom = sj_pos[1] - IMG_H / 2 - lbl_h - pad
        trial_center = np.array([0.0, (box_top + box_bottom) / 2, 0.0])
        trial_frame_side = max(self._D + IMG_H + 2 * pad, box_top - box_bottom) + 0.12
        trial_frame = Square(
            side_length=trial_frame_side,
            color=LGREY,
            stroke_width=1.5,
        ).set_fill("#F9FAFB", opacity=0.45).move_to(trial_center)
        math_block.scale_to_fit_width(3.95)
        math_block.next_to(trial_frame, LEFT, buff=0.55)
        math_block.align_to(trial_frame, UP).shift(DOWN * 0.82)
        computer_icon = (
            ImageMobject(str(STAGE2_ASSET_DIR / "computer.png"))
            .set_width(0.56)
            .move_to(trial_center + UP * (trial_frame_side / 2 + 0.42))
        )

        # ── Images ────────────────────────────────────────────────────────────
        si_img = ImageMobject(fish_path(trial_specs[0]["ref"])).set_height(IMG_H).move_to(si_pos)
        si_bdr = SurroundingRectangle(si_img, color=LGREY, stroke_width=1.5, buff=0.05)
        sj_img, sj_bdr = self._make_probe(trial_specs[0]["left"], sj_pos)
        sk_img, sk_bdr = self._make_probe(trial_specs[0]["right"], sk_pos)

        # Math labels below each image
        si_lbl = self._index_tex(trial_specs[0]["ref"], INK).next_to(si_img, DOWN, buff=0.16)
        sj_lbl = self._index_tex(trial_specs[0]["left"], INK).next_to(sj_img, DOWN, buff=0.16)
        sk_lbl = self._index_tex(trial_specs[0]["right"], INK).next_to(sk_img, DOWN, buff=0.16)
        probe_pair = Group(sj_img, sk_img)
        reference_tag = Tex(r"Reference", color=INK, font_size=24).next_to(si_img, UP, buff=0.18)
        probes_tag = Tex(r"Probes", color=INK, font_size=24).next_to(probe_pair, DOWN, buff=0.42)
        reference_focus = SurroundingRectangle(si_img, color=MGREY, stroke_width=2.1, buff=0.10)
        probes_focus = SurroundingRectangle(probe_pair, color=MGREY, stroke_width=2.1, buff=0.14)

        # ── Participant response set ──────────────────────────────────────────
        response_row_targets = VGroup(*[
            self._response_row(
                spec["ref"],
                spec["left"] if spec["selected"] == "left" else spec["right"],
                spec["right"] if spec["selected"] == "left" else spec["left"],
            )
            for spec in trial_specs
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        response_lhs = MathTex(r"\mathit{T} \; =", color=INK, font_size=30)
        response_lhs.next_to(response_row_targets, LEFT, buff=0.16).align_to(response_row_targets[0], UP)
        response_stack = VGroup(response_lhs, response_row_targets)
        response_title = Tex(
            r"Behavioural responses",
            color=INK,
            font_size=24,
        ).next_to(response_stack, UP, buff=0.28).align_to(response_stack, LEFT)
        response_panel_content = VGroup(response_title, response_lhs, response_row_targets)
        response_group = response_panel_content.move_to([4.35, -0.68, 0.0])
        response_rows = []
        for target in response_row_targets:
            row = target.copy()
            row.move_to(target.get_center()).align_to(target, LEFT)
            response_rows.append(row)
        continuation_dots = MathTex(r"\vdots", color=MGREY, font_size=30)
        continuation_dots.next_to(response_rows[-1], DOWN, buff=0.16)
        continuation_dots.move_to(
            [
                response_rows[-1].get_center()[0],
                continuation_dots.get_center()[1],
                0.0,
            ]
        )

        def emphasize_response_mapping(row: VGroup, selected_side: str) -> None:
            selected_bdr = sj_bdr if selected_side == "left" else sk_bdr
            self.play(
                AnimationGroup(
                    Indicate(si_bdr, color=BLUE, scale_factor=1.06),
                    Indicate(row.submobjects[1], color=BLUE, scale_factor=1.25),
                    lag_ratio=0.0,
                ),
                run_time=0.75,
            )
            self.wait(0.12)
            self.play(
                AnimationGroup(
                    Indicate(selected_bdr, color=AMBER, scale_factor=1.08),
                    Indicate(row.submobjects[3], color=AMBER, scale_factor=1.25),
                    lag_ratio=0.0,
                ),
                run_time=0.75,
            )
            self.wait(0.12)

        def highlight_choice(selected_side: str) -> None:
            if selected_side == "left":
                selected_img, selected_bdr, selected_lbl = sj_img, sj_bdr, sj_lbl
                other_img, other_bdr, other_lbl = sk_img, sk_bdr, sk_lbl
            else:
                selected_img, selected_bdr, selected_lbl = sk_img, sk_bdr, sk_lbl
                other_img, other_bdr, other_lbl = sj_img, sj_bdr, sj_lbl

            sel_bdr = SurroundingRectangle(selected_img, color=AMBER, stroke_width=4.2, buff=0.07)
            self.play(
                Transform(selected_bdr, sel_bdr),
                other_img.animate.set_opacity(0.28),
                other_bdr.animate.set_stroke(opacity=0.12),
                other_lbl.animate.set_opacity(0.28),
                selected_img.animate.set_opacity(1.0),
                selected_lbl.animate.set_opacity(1.0),
                run_time=0.55,
            )

        # ── Phase 1: math introduction ─────────────────────────────────────────
        self.play(Write(title), run_time=0.65)
        self.wait(0.15)
        self.play(title.animate.move_to(title_top_target), run_time=0.55)
        self.play(FadeIn(subtitle, shift=UP * 0.1), run_time=0.45)
        self.play(FadeIn(question, shift=UP * 0.12), run_time=0.60)
        self.wait(0.45)
        self.play(FadeIn(math_block, shift=UP * 0.10), run_time=0.35)
        self.wait(0.35)

        # ── Phase 2: build equilateral triangle ────────────────────────────────
        self.play(Create(trial_frame), FadeIn(computer_icon, shift=LEFT * 0.08), run_time=0.50)

        # Reference (si) appears at the top vertex
        self.play(FadeIn(si_img), Create(si_bdr), FadeIn(si_lbl), run_time=0.60)
        self.wait(0.20)

        # Probe images appear at the bottom vertices, left then right
        self.play(
            AnimationGroup(
                AnimationGroup(FadeIn(sj_img), Create(sj_bdr), FadeIn(sj_lbl)),
                AnimationGroup(FadeIn(sk_img), Create(sk_bdr), FadeIn(sk_lbl)),
                lag_ratio=0.30,
            ),
            run_time=0.80,
        )
        self.play(
            FadeIn(reference_tag, shift=UP * 0.08),
            FadeIn(probes_tag, shift=UP * 0.08),
            run_time=0.35,
        )
        self.play(
            FadeIn(reference_focus),
            run_time=0.45,
        )
        self.wait(0.25)
        self.play(
            FadeIn(probes_focus),
            run_time=0.45,
        )
        self.wait(1.00)
        self.wait(0.5)
        return


# ══════════════════════════════════════════════════════════════════════════════════
# Scene 2 — Triplet collection examples
# ══════════════════════════════════════════════════════════════════════════════════

class Study1Stage2TripletTask2(Study1Stage2TripletTask):
    """Follow-up scene: example trials and participant triplet-set construction."""

    def construct(self) -> None:
        self.camera.background_color = BG

        si_pos, sj_pos, sk_pos = self._positions()
        IMG_H = self._IMG_H
        trial_specs = [
            {"ref": 0, "left": 2, "right": 7, "selected": "left"},
            {"ref": 4, "left": 8, "right": 3, "selected": "right"},
            {"ref": 6, "left": 1, "right": 9, "selected": "left"},
            {"ref": 8, "left": 5, "right": 2, "selected": "right"},
        ]

        title = Tex(
            r"Psychophysical Validation",
            color=INK, font_size=38,
        ).to_edge(UP, buff=0.28)

        subtitle = Tex(
            r"Triplet similarity task \quad $N = 1{,}113$ participants",
            color=MGREY, font_size=24,
        ).next_to(title, DOWN, buff=0.10)
        question = VGroup(
            Tex(
                r"Does the model-based preselection capture",
                color=INK,
                font_size=24,
            ),
            Tex(
                r"a human-perceived perceptual continuum?",
                color=INK,
                font_size=24,
            ),
        ).arrange(DOWN, buff=0.08).next_to(subtitle, DOWN, buff=0.16)

        lbl_h  = 0.38
        pad    = 0.28
        box_top    = si_pos[1] + IMG_H / 2 + pad
        box_bottom = sj_pos[1] - IMG_H / 2 - lbl_h - pad
        trial_center = np.array([0.0, (box_top + box_bottom) / 2, 0.0])
        trial_frame_side = max(self._D + IMG_H + 2 * pad, box_top - box_bottom) + 0.12
        trial_frame = Square(
            side_length=trial_frame_side,
            color=LGREY,
            stroke_width=1.5,
        ).set_fill("#F9FAFB", opacity=0.45).move_to(trial_center)
        computer_icon = (
            ImageMobject(str(STAGE2_ASSET_DIR / "computer.png"))
            .set_width(0.56)
            .move_to(trial_center + UP * (trial_frame_side / 2 + 0.42))
        )
        math1 = Tex(
            r"Given a set of images $\mathcal{S} = \{s_1, s_2, \ldots, s_n\}$,",
            color=INK,
            font_size=26,
        )
        math2 = Tex(
            r"participants view triplets $(s_i,\, s_j,\, s_k)$",
            color=INK,
            font_size=26,
        )
        math3 = Tex(
            r"and select which probe is more similar",
            color=INK,
            font_size=26,
        )
        math4 = Tex(
            r"to the reference image $s_i$.",
            color=INK,
            font_size=26,
        )
        math_block = VGroup(math1, math2, math3, math4).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        math_block.scale_to_fit_width(3.95)
        math_block.next_to(trial_frame, LEFT, buff=0.55)
        math_block.align_to(trial_frame, UP).shift(DOWN * 0.82)

        si_img = ImageMobject(fish_path(trial_specs[0]["ref"])).set_height(IMG_H).move_to(si_pos)
        si_bdr = SurroundingRectangle(si_img, color=LGREY, stroke_width=1.5, buff=0.05)
        sj_img, sj_bdr = self._make_probe(trial_specs[0]["left"], sj_pos)
        sk_img, sk_bdr = self._make_probe(trial_specs[0]["right"], sk_pos)

        si_lbl = self._index_tex(trial_specs[0]["ref"], INK).next_to(si_img, DOWN, buff=0.16)
        sj_lbl = self._index_tex(trial_specs[0]["left"], INK).next_to(sj_img, DOWN, buff=0.16)
        sk_lbl = self._index_tex(trial_specs[0]["right"], INK).next_to(sk_img, DOWN, buff=0.16)
        probe_pair = Group(sj_img, sk_img)
        reference_tag = Tex(r"Reference", color=INK, font_size=24).next_to(si_img, UP, buff=0.18)
        probes_tag = Tex(r"Probes", color=INK, font_size=24).next_to(probe_pair, DOWN, buff=0.42)
        reference_focus = SurroundingRectangle(si_img, color=MGREY, stroke_width=2.1, buff=0.10)
        probes_focus = SurroundingRectangle(probe_pair, color=MGREY, stroke_width=2.1, buff=0.14)

        response_row_targets = VGroup(*[
            self._response_row(
                spec["ref"],
                spec["left"] if spec["selected"] == "left" else spec["right"],
                spec["right"] if spec["selected"] == "left" else spec["left"],
            )
            for spec in trial_specs
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        response_lhs = MathTex(r"\mathit{T} \; =", color=INK, font_size=30)
        response_lhs.next_to(response_row_targets, LEFT, buff=0.16).align_to(response_row_targets[0], UP)
        response_stack = VGroup(response_lhs, response_row_targets)
        response_title = Tex(
            r"Behavioural responses",
            color=INK,
            font_size=24,
        ).next_to(response_stack, UP, buff=0.28).align_to(response_stack, LEFT)
        response_panel_content = VGroup(response_title, response_lhs, response_row_targets)
        response_panel_content.move_to([4.35, -0.68, 0.0])
        response_rows = []
        for target in response_row_targets:
            row = target.copy()
            row.move_to(target.get_center()).align_to(target, LEFT)
            response_rows.append(row)
        continuation_dots = MathTex(r"\vdots", color=MGREY, font_size=30)
        continuation_dots.next_to(response_rows[-1], DOWN, buff=0.16)
        continuation_dots.move_to(
            [response_rows[-1].get_center()[0], continuation_dots.get_center()[1], 0.0]
        )

        def emphasize_response_mapping(row: VGroup, selected_side: str) -> None:
            selected_bdr = sj_bdr if selected_side == "left" else sk_bdr
            self.play(
                AnimationGroup(
                    Indicate(si_bdr, color=BLUE, scale_factor=1.06),
                    Indicate(row.submobjects[1], color=BLUE, scale_factor=1.25),
                    lag_ratio=0.0,
                ),
                run_time=0.75,
            )
            self.wait(0.12)
            self.play(
                AnimationGroup(
                    Indicate(selected_bdr, color=AMBER, scale_factor=1.08),
                    Indicate(row.submobjects[3], color=AMBER, scale_factor=1.25),
                    lag_ratio=0.0,
                ),
                run_time=0.75,
            )
            self.wait(0.12)

        def highlight_choice(selected_side: str) -> None:
            if selected_side == "left":
                selected_img, selected_bdr, selected_lbl = sj_img, sj_bdr, sj_lbl
                other_img, other_bdr, other_lbl = sk_img, sk_bdr, sk_lbl
            else:
                selected_img, selected_bdr, selected_lbl = sk_img, sk_bdr, sk_lbl
                other_img, other_bdr, other_lbl = sj_img, sj_bdr, sj_lbl

            sel_bdr = SurroundingRectangle(selected_img, color=AMBER, stroke_width=4.2, buff=0.07)
            self.play(
                Transform(selected_bdr, sel_bdr),
                other_img.animate.set_opacity(0.28),
                other_bdr.animate.set_stroke(opacity=0.12),
                other_lbl.animate.set_opacity(0.28),
                selected_img.animate.set_opacity(1.0),
                selected_lbl.animate.set_opacity(1.0),
                run_time=0.55,
            )

        self.add(
            title,
            subtitle,
            question,
            math_block,
            trial_frame,
            computer_icon,
            si_img,
            si_bdr,
            si_lbl,
            sj_img,
            sj_bdr,
            sj_lbl,
            sk_img,
            sk_bdr,
            sk_lbl,
            reference_tag,
            probes_tag,
            reference_focus,
            probes_focus,
        )
        self.wait(0.50)
        self.play(
            FadeOut(reference_tag, shift=UP * 0.06),
            FadeOut(probes_tag, shift=UP * 0.06),
            FadeOut(reference_focus),
            FadeOut(probes_focus),
            run_time=0.35,
        )
        self.wait(0.20)

        highlight_choice(trial_specs[0]["selected"])
        self.play(
            FadeIn(response_title, shift=UP * 0.10),
            FadeIn(response_lhs, shift=RIGHT * 0.10),
            run_time=0.65,
        )
        self.play(Write(response_rows[0]), run_time=0.45)
        emphasize_response_mapping(response_rows[0], trial_specs[0]["selected"])
        self.wait(0.45)

        for row_idx, spec in enumerate(trial_specs[1:], start=1):
            next_si_img = ImageMobject(fish_path(spec["ref"])).set_height(IMG_H).move_to(si_pos)
            next_sj_img, next_sj_bdr = self._make_probe(spec["left"], sj_pos)
            next_sk_img, next_sk_bdr = self._make_probe(spec["right"], sk_pos)
            next_si_lbl = self._index_tex(spec["ref"], INK).next_to(next_si_img, DOWN, buff=0.10)
            next_sj_lbl = self._index_tex(spec["left"], INK).next_to(next_sj_img, DOWN, buff=0.10)
            next_sk_lbl = self._index_tex(spec["right"], INK).next_to(next_sk_img, DOWN, buff=0.10)

            self.play(
                ReplacementTransform(si_img, next_si_img),
                ReplacementTransform(sj_img, next_sj_img),
                ReplacementTransform(sj_bdr, next_sj_bdr),
                ReplacementTransform(sk_img, next_sk_img),
                ReplacementTransform(sk_bdr, next_sk_bdr),
                ReplacementTransform(si_lbl, next_si_lbl),
                ReplacementTransform(sj_lbl, next_sj_lbl),
                ReplacementTransform(sk_lbl, next_sk_lbl),
                run_time=0.65,
            )
            si_img, si_lbl = next_si_img, next_si_lbl
            sj_img, sj_bdr = next_sj_img, next_sj_bdr
            sk_img, sk_bdr = next_sk_img, next_sk_bdr
            sj_lbl, sk_lbl = next_sj_lbl, next_sk_lbl

            highlight_choice(spec["selected"])
            self.play(Write(response_rows[row_idx]), run_time=0.42)
            emphasize_response_mapping(response_rows[row_idx], spec["selected"])
            self.wait(0.30)

        self.play(Write(continuation_dots), run_time=0.45)
        self.wait(1.10)


# ══════════════════════════════════════════════════════════════════════════════════
# Scene 3 — Other object-scene triplets
# ══════════════════════════════════════════════════════════════════════════════════

class Study1Stage2SimilarityJudgementsExamples(Scene):
    """Introduce additional within-category triplets for object-scene classes."""

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Recreate a compact snapshot of the previous scene ────────────────
        title_prev = Tex(
            r"Psychophysical Validation",
            color=INK, font_size=38,
        ).to_edge(UP, buff=0.28)
        subtitle_prev = Tex(
            r"Triplet similarity task \quad $N = 1{,}113$ participants",
            color=MGREY, font_size=24,
        ).next_to(title_prev, DOWN, buff=0.10)
        question_prev = VGroup(
            Tex(r"Does the model-based preselection capture", color=INK, font_size=24),
            Tex(r"a human-perceived perceptual continuum?", color=INK, font_size=24),
        ).arrange(DOWN, buff=0.08).next_to(subtitle_prev, DOWN, buff=0.16)
        math_prev = VGroup(
            Tex(r"Given a set of images $\mathcal{S} = \{s_1, s_2, \ldots, s_n\}$,", color=INK, font_size=26),
            Tex(r"participants view triplets $(s_i,\, s_j,\, s_k)$", color=INK, font_size=26),
            Tex(r"and select which probe is more similar", color=INK, font_size=26),
            Tex(r"to the reference image $s_i$.", color=INK, font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        d = 2.22
        img_h = 1.18
        cy = -1.05
        h = d * np.sqrt(3) / 2
        si_pos = np.array([0.0, cy + 2 * h / 3, 0.0])
        sj_pos = np.array([-d / 2, cy - h / 3, 0.0])
        sk_pos = np.array([d / 2, cy - h / 3, 0.0])
        lbl_h = 0.38
        pad = 0.28
        box_top = si_pos[1] + img_h / 2 + pad
        box_bottom = sj_pos[1] - img_h / 2 - lbl_h - pad
        trial_center = np.array([0.0, (box_top + box_bottom) / 2, 0.0])
        trial_frame_side = max(d + img_h + 2 * pad, box_top - box_bottom) + 0.12

        trial_frame = Square(
            side_length=trial_frame_side,
            color=LGREY,
            stroke_width=1.5,
        ).set_fill("#F9FAFB", opacity=0.45).move_to(trial_center)
        math_prev.scale_to_fit_width(3.95)
        math_prev.next_to(trial_frame, LEFT, buff=0.55)
        math_prev.align_to(trial_frame, UP).shift(DOWN * 0.82)
        computer_icon = (
            ImageMobject(str(STAGE2_ASSET_DIR / "computer.png"))
            .set_width(0.56)
            .move_to(trial_center + UP * (trial_frame_side / 2 + 0.42))
        )

        si_img = ImageMobject(fish_path(8)).set_height(img_h).move_to(si_pos)
        sj_img = ImageMobject(fish_path(5)).set_height(img_h).move_to(sj_pos)
        sk_img = ImageMobject(fish_path(2)).set_height(img_h).move_to(sk_pos)
        si_bdr = SurroundingRectangle(si_img, color=LGREY, stroke_width=1.5, buff=0.05)
        sj_bdr = SurroundingRectangle(sj_img, color=LGREY, stroke_width=1.5, buff=0.05)
        sk_bdr = SurroundingRectangle(sk_img, color=AMBER, stroke_width=4.2, buff=0.07)
        si_lbl = MathTex(r"s_{9}", color=INK, font_size=28).next_to(si_img, DOWN, buff=0.16)
        sj_lbl = MathTex(r"s_{6}", color=INK, font_size=28).next_to(sj_img, DOWN, buff=0.16).set_opacity(0.28)
        sk_lbl = MathTex(r"s_{3}", color=INK, font_size=28).next_to(sk_img, DOWN, buff=0.16)
        sj_img.set_opacity(0.28)
        sj_bdr.set_stroke(opacity=0.12)

        response_rows = VGroup(
            self._mini_response_row(1, 3, 8),
            self._mini_response_row(5, 4, 9),
            self._mini_response_row(7, 2, 10),
            self._mini_response_row(9, 3, 6),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        response_lhs = MathTex(r"\mathit{T} \; =", color=INK, font_size=30).next_to(response_rows, LEFT, buff=0.16).align_to(response_rows[0], UP)
        response_title = Tex(r"Behavioural responses", color=INK, font_size=24)
        response_stack = VGroup(response_lhs, response_rows)
        response_title.next_to(response_stack, UP, buff=0.28).align_to(response_stack, LEFT)
        continuation_dots = MathTex(r"\vdots", color=MGREY, font_size=30).next_to(response_rows[-1], DOWN, buff=0.16)
        continuation_dots.move_to([response_rows[-1].get_center()[0], continuation_dots.get_center()[1], 0.0])
        response_group = VGroup(response_title, response_lhs, response_rows, continuation_dots).move_to([4.35, -0.68, 0.0])

        previous_scene_group = Group(
            title_prev, subtitle_prev, question_prev, math_prev, trial_frame, computer_icon,
            si_img, si_bdr, si_lbl, sj_img, sj_bdr, sj_lbl, sk_img, sk_bdr, sk_lbl, response_group
        )

        # ── New title ────────────────────────────────────────────────────────
        title = Tex(
            r"Similarity judgements within object-scenes",
            color=INK, font_size=34,
        ).to_edge(UP, buff=0.30)

        # ── Four side-by-side mini triplets ─────────────────────────────────
        categories = [
            ("landscape_element_tropical_karst", "Tropical karst", (1, 4, 8)),
            ("item_sofa", "Sofa", (0, 3, 7)),
            ("vehicle_campervan", "Campervan", (2, 5, 9)),
            ("plant_pine_med", "Pine med", (1, 6, 8)),
        ]

        def mini_triplet(prefix: str, label: str, indices: tuple[int, int, int], center: np.ndarray) -> Group:
            ref_i, left_i, right_i = indices
            frame = Square(side_length=2.45, color=LGREY, stroke_width=1.3).set_fill("#F9FAFB", opacity=0.55).move_to(center)
            top = center + UP * 0.55
            bottom_y = center[1] - 0.42
            left = np.array([center[0] - 0.48, bottom_y, 0.0])
            right = np.array([center[0] + 0.48, bottom_y, 0.0])
            img_ref = ImageMobject(stimulus_path(prefix, ref_i)).set_height(0.56).move_to(top)
            img_l = ImageMobject(stimulus_path(prefix, left_i)).set_height(0.56).move_to(left)
            img_r = ImageMobject(stimulus_path(prefix, right_i)).set_height(0.56).move_to(right)
            bdr_ref = SurroundingRectangle(img_ref, color=LGREY, stroke_width=1.2, buff=0.03)
            bdr_l = SurroundingRectangle(img_l, color=LGREY, stroke_width=1.2, buff=0.03)
            bdr_r = SurroundingRectangle(img_r, color=LGREY, stroke_width=1.2, buff=0.03)
            caption = Tex(label, color=INK, font_size=18).next_to(frame, DOWN, buff=0.18)
            return Group(frame, img_ref, bdr_ref, img_l, bdr_l, img_r, bdr_r, caption)

        centers = [
            np.array([-4.65, -0.05, 0.0]),
            np.array([-1.55, -0.05, 0.0]),
            np.array([1.55, -0.05, 0.0]),
            np.array([4.65, -0.05, 0.0]),
        ]
        mini_groups = Group(*[
            mini_triplet(prefix, label, idxs, center)
            for (prefix, label, idxs), center in zip(categories, centers)
        ])

        self.add(previous_scene_group)
        self.wait(0.20)
        self.play(
            LaggedStart(
                *[
                    mob.animate.shift(DOWN * 0.10).fade(1)
                    for mob in previous_scene_group
                ],
                lag_ratio=0.03,
            ),
            run_time=0.85,
            rate_func=smooth,
        )
        self.play(Write(title), run_time=0.50)
        self.play(
            LaggedStart(*[FadeIn(group, shift=UP * 0.12, scale=0.96) for group in mini_groups], lag_ratio=0.12),
            run_time=1.10,
        )
        self.wait(1.20)

    def _mini_response_row(self, a: int, b: int, c: int) -> VGroup:
        parts = [
            MathTex(r"(", color=INK, font_size=28),
            MathTex(str(a), color=INK, font_size=28),
            MathTex(r",", color=INK, font_size=28),
            MathTex(str(b), color=INK, font_size=28),
            MathTex(r",", color=INK, font_size=28),
            MathTex(str(c), color=INK, font_size=28),
            MathTex(r")", color=INK, font_size=28),
        ]
        return VGroup(*parts).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)


# ══════════════════════════════════════════════════════════════════════════════════
# Scene 4 — Ordinal embedding: scramble → sort
# ══════════════════════════════════════════════════════════════════════════════════

class Study1Stage2OrdinalEmbedding(Scene):
    """
    Explains ordinal embedding intuitively as a sorting problem.

    Phase 1 — scrambled row of images (arbitrary order).
    Phase 2 — two example triplet constraints shown as arcs.
    Phase 3 — images animate to their perceptually correct positions.
    Phase 4 — embedding values appear; scale label replaces scramble label.
    """

    # Scrambled fish-index order for the initial display
    _SCRAMBLE = [7, 2, 5, 0, 8, 3, 9, 1, 6, 4]
    _IMG_H    = 0.84
    _Y        = 0.32                                # image-row centre y
    _XS       = np.linspace(-4.5, 4.5, 10)         # 10 evenly-spaced x slots

    # ── Helper: image + border as one moveable Group ──────────────────────────
    @staticmethod
    def _card(fish_idx: int, img_h: float, border_color=None) -> Group:
        border_color = border_color or LGREY
        img = ImageMobject(fish_path(fish_idx)).set_height(img_h)
        bdr = SurroundingRectangle(img, color=border_color, stroke_width=1.3, buff=0.04)
        return Group(img, bdr)

    # ── Helper: arc between two x-positions at image-row y ───────────────────
    @staticmethod
    def _arc(x1: float, x2: float, y: float, img_h: float,
             color: str, angle_sign: float = 1.0) -> ArcBetweenPoints:
        """Curved arc connecting two image centres, bowing upward."""
        edge_y = y + img_h / 2 + 0.05
        return ArcBetweenPoints(
            np.array([x1, edge_y, 0.0]),
            np.array([x2, edge_y, 0.0]),
            angle=angle_sign * PI / 3.5,
            color=color, stroke_width=2.2,
        )

    def construct(self) -> None:
        self.camera.background_color = BG
        xs, y, IMG_H = self._XS, self._Y, self._IMG_H
        scramble     = self._SCRAMBLE

        # ── Title ─────────────────────────────────────────────────────────────
        title = Tex(
            r"Ordinal Embedding",
            color=INK, font_size=38,
        ).to_edge(UP, buff=0.28)

        # ── Scrambled image cards ──────────────────────────────────────────────
        cards = [
            self._card(scramble[i], IMG_H).move_to([xs[i], y, 0.0])
            for i in range(10)
        ]
        target_xs = [xs[scramble[i]] for i in range(10)]

        # ── Baseline axis ──────────────────────────────────────────────────────
        axis_y = y - IMG_H / 2 - 0.18
        axis = Line([-5.1, axis_y, 0.0], [5.1, axis_y, 0.0],
                    color=LGREY, stroke_width=1.3)
        tag_before = Tex(r"Arbitrary order", color=MGREY, font_size=19).move_to(
            [0.0, y + IMG_H / 2 + 0.38, 0.0]
        )

        # ── Pipeline (bottom of screen) ────────────────────────────────────────
        # Appears progressively to track the data-flow story.
        PIPE_Y = -2.80
        pipe_task = Tex(r"Triplet task", color=INK, font_size=18)
        pipe_a1   = Tex(r"$\longrightarrow$", color=MGREY, font_size=20)
        pipe_resp = VGroup(
            Tex(r"Behavioral responses", color=INK, font_size=18),
            Tex(r"$(N \times T$ triplets$)$",  color=MGREY, font_size=14),
        ).arrange(DOWN, buff=0.05)
        pipe_a2   = Tex(r"$\longrightarrow$", color=MGREY, font_size=20)
        pipe_algo = Tex(r"Ordinal Embedding", color=BLUE, font_size=18)
        pipe_a3   = Tex(r"$\longrightarrow$", color=MGREY, font_size=20)
        pipe_scale= Tex(r"Perceptual scale",  color=INK,  font_size=18)

        pipeline = VGroup(
            pipe_task, pipe_a1, pipe_resp, pipe_a2,
            pipe_algo, pipe_a3, pipe_scale,
        ).arrange(RIGHT, buff=0.28).move_to([0.0, PIPE_Y, 0.0])

        # ── Constraint arcs (drawn at the "Behavioral responses" stage) ───────
        x_si = xs[scramble.index(0)]   # fish-00 (reference)
        x_sj = xs[scramble.index(2)]   # fish-02 (more similar)
        x_sk = xs[scramble.index(7)]   # fish-07 (less similar)

        GREEN_C = "#16A34A"
        RED_C   = "#DC2626"

        arc_close = self._arc(x_si, x_sj, y, IMG_H, GREEN_C)
        arc_far   = self._arc(x_si, x_sk, y, IMG_H, RED_C)
        lbl_close = Tex(r"$s_j$ close", color=GREEN_C, font_size=16).move_to(
            arc_close.get_center() + UP * 0.30
        )
        lbl_far = Tex(r"$s_k$ far", color=RED_C, font_size=16).move_to(
            arc_far.get_center() + UP * 0.28
        )

        # ── Embedding values (shown at the "Perceptual scale" stage) ──────────
        val_y = axis_y - 0.26
        val_labels = VGroup(*[
            Tex(f"{EMBED_Y[k]:.2f}", color=MGREY, font_size=14)
            .move_to([xs[k], val_y, 0.0])
            for k in range(10)
        ])
        tag_after = Tex(r"Perceptual scale", color=INK, font_size=19).move_to(
            [0.0, y + IMG_H / 2 + 0.38, 0.0]
        )

        # ══ Animation ══════════════════════════════════════════════════════════

        # 0. Title + scrambled images
        self.play(Write(title), run_time=0.55)
        self.play(
            LaggedStart(*[FadeIn(c, scale=1.08) for c in cards], lag_ratio=0.05),
            run_time=0.85,
        )
        self.play(Create(axis), FadeIn(tag_before), run_time=0.35)
        self.wait(0.20)

        # 1. Pipeline stage 1 — "Triplet task"
        self.play(FadeIn(pipe_task), run_time=0.35)
        self.wait(0.20)

        # 2. Pipeline stage 2 — "→ Behavioral responses" + constraint arcs
        #    The arcs show what ONE triplet response encodes geometrically.
        self.play(FadeIn(pipe_a1), FadeIn(pipe_resp), run_time=0.45)
        si_slot = scramble.index(0)
        hi_bdr = SurroundingRectangle(
            cards[si_slot][0], color=BLUE, stroke_width=2.5, buff=0.05
        )
        self.play(FadeIn(hi_bdr), run_time=0.25)
        self.play(
            Create(arc_close), FadeIn(lbl_close),
            Create(arc_far),   FadeIn(lbl_far),
            run_time=0.70,
        )
        self.wait(0.70)

        # 3. Pipeline stage 3 — "→ Ordinal Embedding" + sort animation
        self.play(
            FadeOut(arc_close, lbl_close, arc_far, lbl_far, hi_bdr),
            FadeIn(pipe_a2), FadeIn(pipe_algo),
            run_time=0.50,
        )
        self.wait(0.25)
        sort_anims = [
            cards[i].animate.move_to([target_xs[i], y, 0.0])
            for i in range(10)
        ]
        self.play(
            *sort_anims,
            FadeOut(tag_before),
            run_time=1.70,
            rate_func=smooth,
        )

        # 4. Pipeline stage 4 — "→ Perceptual scale" + values
        self.play(
            FadeIn(pipe_a3), FadeIn(pipe_scale),
            FadeIn(val_labels, shift=UP * 0.05),
            FadeIn(tag_after),
            run_time=0.50,
        )
        self.wait(1.30)


# ══════════════════════════════════════════════════════════════════════════════════
# Scene 3 — Ordinal embedding curve + final ordered image strip
# ══════════════════════════════════════════════════════════════════════════════════

class Study1Stage2EmbeddingResult(Scene):
    """
    Behavioural responses on the left, ordinal embedding algorithm underneath,
    embedding plot on the right, and final ordered image strip below.
    Styled with a cleaner, more 3Blue1Brown-like layout.
    """

    def construct(self) -> None:
        self.camera.background_color = BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Tex(
            r"From behavioural responses to perceptual embedding",
            color=INK,
            font_size=34,
        ).to_edge(UP, buff=0.28)

        # ── Left column: behavioural responses ───────────────────────────────
        responses_title = Tex(
            r"Behavioural responses",
            color=INK,
            font_size=28,
        )
        responses_main = MathTex(
            r"\mathit{T}=\{(i,j,k)\}",
            color=INK,
            font_size=36,
        )
        responses_examples = VGroup(
            MathTex(r"(1,3,8)", color=MGREY, font_size=25),
            MathTex(r"(5,4,9)", color=MGREY, font_size=25),
            MathTex(r"(7,2,10)", color=MGREY, font_size=25),
            MathTex(r"\vdots", color=MGREY, font_size=25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)

        responses_block = VGroup(
            responses_title,
            responses_main,
            responses_examples,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        responses_block.move_to([-5.0, 1.55, 0.0])

        # ── Algorithm block underneath ───────────────────────────────────────
        algo_title = Tex(
            r"Ordinal embedding algorithm",
            color=BLUE,
            font_size=27,
        )
        algo_sub = Tex(
            r"Estimate 1D stimulus positions",
            color=MGREY,
            font_size=20,
        )
        algo_block = VGroup(algo_title, algo_sub).arrange(DOWN, buff=0.10)
        algo_block.move_to([-5.0, -0.35, 0.0])

        # Smaller vertical arrow with more breathing room
        down_arrow = Arrow(
            start=responses_block.get_bottom() + DOWN * 0.06,
            end=algo_block.get_top() + UP * 0.06,
            buff=0.12,
            color=LGREY,
            stroke_width=1.8,
            tip_length=0.08,
            max_stroke_width_to_length_ratio=8,
        )

        # ── Right: embedding plot ─────────────────────────────────────────────
        # More compact and slightly higher, so the strip fits naturally below
        plot_center = np.array([2.1, 0.78, 0.0])

        axes = Axes(
            x_range=[1, 10.6, 1],
            y_range=[0, 1.05, 0.25],
            x_length=5.8,
            y_length=3.6,
            axis_config={
                "color": INK,
                "stroke_width": 1.6,
                "include_tip": False,   # cleaner, more 3b1b-like
                "tick_size": 0.06,
            },
        ).move_to(plot_center)

        plot_title = Tex(
            r"Estimated embedding",
            color=INK,
            font_size=25,
        ).next_to(axes, UP, buff=0.20)

        x_label = Tex(
            r"Image number",
            color=INK,
            font_size=22,
        ).next_to(axes.get_x_axis(), DOWN, buff=0.34)

        y_label = Tex(
            r"Embedding",
            color=INK,
            font_size=22,
        ).rotate(PI / 2).next_to(axes.get_y_axis(), LEFT, buff=0.30)

        # Larger tick labels
        x_nums = VGroup(*[
            Tex(
                str(i),
                color=INK,
                font_size=22,
            ).move_to(axes.c2p(i, 0) + DOWN * 0.24)
            for i in range(1, 11)
        ])

        # Fewer and larger y tick labels for clarity
        y_tick_values = [0.00, 0.25, 0.50, 0.75, 1.00]
        y_nums = VGroup(*[
            Tex(
                f"{v:.2f}",
                color=INK,
                font_size=20,
            ).move_to(axes.c2p(1, v) + LEFT * 0.46)
            for v in y_tick_values
        ])

        pts = [axes.c2p(i + 1, v) for i, v in enumerate(EMBED_Y)]

        curve = VMobject(
            stroke_color=BLUE,
            stroke_width=3.0,
        )
        curve.set_points_smoothly(pts)

        dots = VGroup(*[
            Dot(
                p,
                radius=0.05,
                color=BLUE,
                fill_opacity=1.0,
            )
            for p in pts
        ])

        # Put the side arrow ABOVE the x-axis, not through it
        side_arrow_y = algo_block.get_center()[1] + 0.38
        side_arrow = Arrow(
            start=np.array([algo_block.get_right()[0] + 0.18, side_arrow_y, 0.0]),
            end=np.array([axes.get_left()[0] - 0.10, side_arrow_y, 0.0]),
            buff=0.06,
            color=LGREY,
            stroke_width=1.8,
            tip_length=0.08,
            max_stroke_width_to_length_ratio=8,
        )

        # ── Ordered image strip below the plot ───────────────────────────────
        strip_xs = [axes.c2p(i + 1, 0)[0] for i in range(10)]
        strip_y = -2.08
        img_h = 0.50

        fish_imgs = Group(*[
            ImageMobject(fish_path(i))
            .set_height(img_h)
            .move_to([strip_xs[i], strip_y, 0.0])
            for i in range(10)
        ])

        fish_borders = VGroup(*[
            SurroundingRectangle(
                fish_imgs[i],
                color=LGREY,
                stroke_width=0.8,
                buff=0.02,
            )
            for i in range(10)
        ])

        connectors = VGroup(*[
            DashedLine(
                start=[strip_xs[i], axes.c2p(i + 1, 0)[1] - 0.03, 0.0],
                end=[strip_xs[i], strip_y + img_h / 2 + 0.03, 0.0],
                color=LGREY,
                stroke_width=0.7,
                dash_length=0.05,
            )
            for i in range(10)
        ])

        strip_title = Tex(
            r"Final ordered image set",
            color=INK,
            font_size=19,
        ).move_to([axes.get_center()[0], strip_y - 0.48, 0.0])

        # ── Animation ────────────────────────────────────────────────────────
        self.play(Write(title), run_time=0.75)
        self.wait(0.20)

        self.play(FadeIn(responses_block, shift=UP * 0.08), run_time=0.85)
        self.wait(0.20)

        self.play(
            Create(down_arrow),
            FadeIn(algo_block, shift=UP * 0.05),
            run_time=0.85,
        )
        self.wait(0.20)

        self.play(Create(side_arrow), run_time=0.45)
        self.play(
            FadeIn(plot_title, shift=UP * 0.05),
            Create(axes),
            FadeIn(x_label, y_label),
            FadeIn(x_nums, y_nums),
            run_time=1.20,
        )
        self.wait(0.20)

        self.play(Create(curve), run_time=1.40)
        self.play(FadeIn(dots, scale=1.10), run_time=0.45)
        self.wait(0.30)

        self.play(Create(connectors), run_time=0.60)
        self.play(
            LaggedStart(
                *[FadeIn(img, scale=1.03) for img in fish_imgs],
                lag_ratio=0.06,
            ),
            run_time=0.95,
        )
        self.play(
            FadeIn(fish_borders),
            FadeIn(strip_title, shift=UP * 0.04),
            run_time=0.25,
        )
        self.wait(1.20)