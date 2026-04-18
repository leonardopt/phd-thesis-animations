from manim import *


class TitleSlide(Scene):
    """Opening title animation for thesis defence."""

    def construct(self):
        title = Text(
            "Assessing Neural Representations of\nNaturalistic Images Across\nPerception and Memory",
            font_size=36,
            line_spacing=1.4,
        ).to_edge(UP, buff=1.2)

        subtitle = Text(
            "Using Deep Generative Modelling",
            font_size=28,
            color=BLUE_C,
        ).next_to(title, DOWN, buff=0.5)

        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait(2)
