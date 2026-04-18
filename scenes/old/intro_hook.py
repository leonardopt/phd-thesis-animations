"""
Slide clip: Opening hook — the audience experiences visual working memory.

The image appears, disappears to white, a fixation cross holds for several
seconds (mirroring the actual experimental delay), then the question lands.

Render:
    uv run manim scenes/intro_hook.py IntroHook -qh
"""
from manim import *
from utils import stim_path


class IntroHook(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        # ── Fixation cross (standard cognitive neuroscience convention) ───────
        fix = VGroup(
            Line(UP * 0.22, DOWN * 0.22, stroke_width=2.5, color=GRAY_C),
            Line(LEFT * 0.22, RIGHT * 0.22, stroke_width=2.5, color=GRAY_C),
        ).move_to(ORIGIN)

        # ── Image ─────────────────────────────────────────────────────────────
        img = ImageMobject(stim_path("animal_fish-05"))
        img.height = 4.4
        img.move_to(ORIGIN)

        # ── Question ──────────────────────────────────────────────────────────
        question = Tex(
            r"What was your brain just doing?",
            font_size=40, color=BLACK,
        ).move_to(ORIGIN)

        # ── Animation ─────────────────────────────────────────────────────────

        # 1. Image appears — the audience looks at it
        self.play(FadeIn(img), run_time=0.6)
        self.wait(2.5)

        # 2. Gone — exactly like a working memory trial
        self.play(FadeOut(img), run_time=0.4)
        self.add(fix)          # fixation cross appears instantly (no animation)
        self.wait(0.1)

        # 3. The delay — 4 uncomfortable seconds of white
        #    The audience is now doing working memory
        self.wait(4.2)

        # 4. The question
        self.remove(fix)
        self.play(FadeIn(question), run_time=0.6)
        self.wait(4.0)
