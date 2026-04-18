"""
Slide clip: Forward diffusion process — image degrades into noise.
Intended as a standalone MP4/MOV inserted into a PowerPoint slide.

Render:
    uv run manim scenes/sdxl_forward.py SDXLForwardProcess -qh
    uv run manim scenes/sdxl_forward.py SDXLForwardProcess -qh --transparent
"""
import shutil

from manim import *
from utils import noise_sequence, stim_path

# ── Layout ────────────────────────────────────────────────────────────────────
N = 5
IMG_H = 1.9
SPACING = 2.75           # centre-to-centre
XS = [SPACING * (i - (N - 1) / 2) for i in range(N)]
IMG_Y = 0.35             # vertical centre of image row

ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0]
STEP_LABELS = [
    r"original",
    r"$t = 1$",
    r"$t = 2$",
    r"$t = 3$",
    r"pure noise",
]


class SDXLForwardProcess(Scene):
    """Forward diffusion: a fish image progressively degrades into noise."""

    def construct(self):
        paths, tmpdir = noise_sequence(stim_path("animal_fish-05"), ALPHAS)

        try:
            # ── Images ───────────────────────────────────────────────────────
            images = []
            for path, x in zip(paths, XS):
                img = ImageMobject(path)
                img.height = IMG_H
                img.move_to(RIGHT * x + UP * IMG_Y)
                images.append(img)

            # ── Labels ───────────────────────────────────────────────────────
            labels = []
            for img, txt in zip(images, STEP_LABELS):
                lbl = Tex(txt, font_size=22)
                lbl.next_to(img, DOWN, buff=0.22)
                labels.append(lbl)

            # ── Arrows + noise labels ─────────────────────────────────────────
            arrows, noise_tags = [], []
            for i in range(N - 1):
                a = Arrow(
                    images[i].get_right() + RIGHT * 0.05,
                    images[i + 1].get_left() + LEFT * 0.05,
                    buff=0.05, stroke_width=2,
                    max_tip_length_to_length_ratio=0.3,
                    color=GRAY_B,
                )
                tag = Tex(r"$+$ noise", font_size=17, color=ORANGE)
                tag.next_to(a, UP, buff=0.1)
                arrows.append(a)
                noise_tags.append(tag)

            # ── Animation: left → right ────────────────────────────────────────
            self.play(FadeIn(images[0]), FadeIn(labels[0]), run_time=0.4)
            for i in range(N - 1):
                self.play(
                    Create(arrows[i]),
                    FadeIn(noise_tags[i]),
                    FadeIn(images[i + 1]),
                    FadeIn(labels[i + 1]),
                    run_time=0.65,
                )

            self.wait(2.0)

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
