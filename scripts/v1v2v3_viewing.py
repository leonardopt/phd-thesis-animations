from __future__ import annotations

from pathlib import Path

from manim import *


config.background_color = WHITE
config.output_file = "v1v2v3_viewing"

ROOT = Path(__file__).resolve().parents[1]
V1V2V3_PATH = ROOT / "assets" / "images" / "anatomy" / "v1v2v3.png"

BLUE = "#2563EB"


class V1V2V3Viewing(Scene):
    """Probe composition for adding an explicit 'viewing' cue to the V1-V3 brain image."""

    def _brain_target_point(self, brain: ImageMobject, x_norm: float, y_norm: float) -> np.ndarray:
        """Map normalized image coordinates to the positioned brain image."""
        return (
            brain.get_center()
            + RIGHT * (0.5 * x_norm * brain.width)
            + UP * (0.5 * y_norm * brain.height)
        )

    def construct(self) -> None:
        brain = ImageMobject(str(V1V2V3_PATH)).scale_to_fit_height(4.75).move_to(np.array([1.7, -0.08, 0.0]))

        cone_apex = self._brain_target_point(brain, x_norm=-0.98, y_norm=-0.02)
        cone_left_x = cone_apex[0] - 4.75
        source_top = np.array([cone_left_x, 0.62, 0.0])
        source_bottom = np.array([cone_left_x, -0.66, 0.0])

        view_cone = Polygon(
            source_top,
            source_bottom,
            cone_apex,
            stroke_width=0.0,
        ).set_fill(BLUE, opacity=0.07)

        top_ray = Line(
            source_top,
            cone_apex,
            color=BLUE,
            stroke_width=1.6,
        ).set_stroke(opacity=0.28)
        bottom_ray = Line(
            source_bottom,
            cone_apex,
            color=BLUE,
            stroke_width=1.6,
        ).set_stroke(opacity=0.28)

        self.add(brain, view_cone, top_ray, bottom_ray)
        self.wait(1)
