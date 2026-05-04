"""
Slide clip: Reverse diffusion process — noise is guided into a new image.
Intended as a standalone MP4/MOV inserted into a PowerPoint slide.

Render:
    uv run manim scenes/sdxl_reverse.py SDXLReverseProcess -qh
    uv run manim scenes/sdxl_reverse.py SDXLReverseProcess -qh --transparent
"""
import shutil

from manim import *
from utils import noise_sequence, stim_path

# ── Layout ────────────────────────────────────────────────────────────────────
N = 5
IMG_H = 1.9
SPACING = 2.75
XS = [SPACING * (i - (N - 1) / 2) for i in range(N)]
IMG_Y = 0.0             # slightly lower to leave room for prompt above

# Same seed as forward so the pure-noise frame is identical
ALPHAS_REV = [1.0, 0.75, 0.5, 0.25, 0.0]
STEP_LABELS = [
    r"pure noise",
    r"$t = 3$",
    r"$t = 2$",
    r"$t = 1$",
    r"generated image",
]

# Text prompt that produced this stimulus
PROMPT = r"\textit{``a fish swimming in the ocean''}"


class SDXLReverseProcess(Scene):
    """Reverse diffusion: starting from noise, guided by a text prompt → stimulus image."""

    def construct(self):
        # Use ANI-FIS-02 as the "generated" output (a different fish from forward)
        paths, tmpdir = noise_sequence(stim_path("animal_fish-02"), ALPHAS_REV)

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

            # ── Prompt box (above first image) ────────────────────────────────
            prompt_txt = Tex(PROMPT, font_size=20, color=YELLOW)
            prompt_box = SurroundingRectangle(
                prompt_txt, color=YELLOW, buff=0.18, corner_radius=0.12, stroke_width=1.5
            )
            prompt_grp = VGroup(prompt_box, prompt_txt)
            prompt_grp.next_to(images[0], UP, buff=0.35)

            prompt_arrow = Arrow(
                prompt_grp.get_bottom() + DOWN * 0.05,
                images[0].get_top() + UP * 0.05,
                buff=0.05, stroke_width=1.5, color=YELLOW,
                max_tip_length_to_length_ratio=0.25,
            )

            # ── Arrows + denoise labels ───────────────────────────────────────
            arrows, denoise_tags = [], []
            for i in range(N - 1):
                a = Arrow(
                    images[i].get_right() + RIGHT * 0.05,
                    images[i + 1].get_left() + LEFT * 0.05,
                    buff=0.05, stroke_width=2,
                    max_tip_length_to_length_ratio=0.3,
                    color=GRAY_B,
                )
                tag = Tex(r"$-$ noise", font_size=17, color=GREEN_C)
                tag.next_to(a, UP, buff=0.1)
                arrows.append(a)
                denoise_tags.append(tag)

            # ── Animation ────────────────────────────────────────────────────
            # Prompt appears, then arrow down to first image, then denoise L→R
            self.play(FadeIn(prompt_grp), run_time=0.4)
            self.play(Create(prompt_arrow), run_time=0.4)
            self.play(FadeIn(images[0]), FadeIn(labels[0]), run_time=0.4)

            for i in range(N - 1):
                self.play(
                    Create(arrows[i]),
                    FadeIn(denoise_tags[i]),
                    FadeIn(images[i + 1]),
                    FadeIn(labels[i + 1]),
                    run_time=0.65,
                )

            # Highlight the final generated image
            highlight = SurroundingRectangle(
                images[-1], color=YELLOW, buff=0.08, stroke_width=2.5, corner_radius=0.05
            )
            self.play(Create(highlight), run_time=0.5)
            self.wait(2.0)

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
