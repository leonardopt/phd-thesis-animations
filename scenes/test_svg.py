from manim import *

config.background_color = WHITE

class SimpleFigure(Scene):
    def construct(self):
        fig = SVGMobject(
            "/Users/leonardo/phd-thesis-animations/assets/images/study1_stage3/behaviour_agg.svg"
        )
        fig.scale_to_fit_width(8)
        fig.center()
        fig.set_opacity(0)

        self.add(fig)
        self.play(fig.animate.set_opacity(1), run_time=2)
        self.wait(1)