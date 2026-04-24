"""
Supplementary - sectioned production render.

Render from this file to keep supplementary outputs in the same
`media/videos/06_supplementary/...` folder.

Production render:
    uv run manim scenes/supplementary.py Supplementary -ql --save_sections
"""
from __future__ import annotations

from pathlib import Path
import sys

from manim import *

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _import_dir in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_import_dir) not in sys.path:
        sys.path.insert(0, str(_import_dir))

from intro import (
    IntroResearchQuestion1,
    IntroResearchQuestion2,
    IntroResearchQuestion3,
)
from utils import section_output_dir, simplify_manim_section_video_names
from study1 import (
    Study1Stage3MemoryIntroA,
    Study1Stage3MemoryIntroB,
    Study1Stage3MemoryIntroC,
    Study1Stage3MemoryIntroD,
    Study1Stage3MemoryIntroE,
)


_SECTION_OUTPUT_DIR = section_output_dir("supplementary")
config.video_dir = f"{{media_dir}}/videos/{_SECTION_OUTPUT_DIR}/{{quality}}"
config.images_dir = f"{{media_dir}}/images/{_SECTION_OUTPUT_DIR}"
config.output_file = "supplementary"
simplify_manim_section_video_names(
    lambda _output_name, index, name, ext: f"{index:03}_{name}{ext}"
)


def _ensure_supplementary_output_dirs(output_name: str | None = None) -> None:
    """Create the supplementary render directories before Manim writes frames."""
    video_dir = Path(config.get_dir("video_dir"))
    images_dir = Path(config.get_dir("images_dir"))
    video_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    if output_name:
        (video_dir / "partial_movie_files" / output_name).mkdir(parents=True, exist_ok=True)


_SUPPLEMENTARY_MASTER_SECTION_ORDER: tuple[type[Scene], ...] = (
    IntroResearchQuestion1,
    IntroResearchQuestion2,
    IntroResearchQuestion3,
    Study1Stage3MemoryIntroA,
    Study1Stage3MemoryIntroB,
    Study1Stage3MemoryIntroC,
    Study1Stage3MemoryIntroD,
    Study1Stage3MemoryIntroE,
)
_SUPPLEMENTARY_SECTION_NAMES: tuple[str, ...] = (
    "intro_research_question_1",
    "intro_research_question_2",
    "intro_research_question_3",
    "study1_stage3_memory_intro_a",
    "study1_stage3_memory_intro_b",
    "study1_stage3_memory_intro_c",
    "study1_stage3_memory_intro_d",
    "study1_stage3_memory_intro_e",
)


class Supplementary(Scene):
    """Render the supplementary deck block as one sectioned scene."""

    _SECTION_SCENES: tuple[tuple[str, type[Scene]], ...] = tuple(
        zip(_SUPPLEMENTARY_SECTION_NAMES, _SUPPLEMENTARY_MASTER_SECTION_ORDER)
    )

    def _reset_scene_state(self, *, clear_scene: bool = True) -> None:
        """Reset camera placement so imported scene bodies replay cleanly."""
        if clear_scene:
            self.clear()
        self.camera.background_color = WHITE
        if hasattr(self.camera, "fixed_orientation_mobjects"):
            self.camera.fixed_orientation_mobjects.clear()
        if hasattr(self.camera, "fixed_in_frame_mobjects"):
            self.camera.fixed_in_frame_mobjects.clear()
        if hasattr(self.camera, "frame_center"):
            self.camera.frame_center = ORIGIN.copy()
        if hasattr(self.camera, "_frame_center"):
            self.camera._frame_center.move_to(ORIGIN)
        if hasattr(self, "set_camera_orientation"):
            self.set_camera_orientation(
                phi=0 * DEGREES,
                theta=-90 * DEGREES,
                gamma=0 * DEGREES,
                zoom=1,
                frame_center=ORIGIN,
            )

    def _hold_previous_section_frame(self) -> None:
        """Match the normal deck behavior by holding the prior frame briefly."""
        self.wait(1 / config.frame_rate)

    def _render_section(
        self,
        section_name: str,
        scene_cls: type[Scene],
        *,
        carry_previous_frame: bool,
    ) -> None:
        """Replay one imported section scene inside this chapter."""
        self.next_section(section_name)
        if carry_previous_frame:
            self._hold_previous_section_frame()
        self._reset_scene_state(clear_scene=True)
        scene_cls.construct(self)

    def construct(self) -> None:
        """Render the supplementary narrative as one sectioned scene."""
        _ensure_supplementary_output_dirs(str(getattr(config, "output_file", self.__class__.__name__)))
        self._reset_scene_state(clear_scene=True)
        for idx, (section_name, scene_cls) in enumerate(self._SECTION_SCENES):
            self._render_section(
                section_name,
                scene_cls,
                carry_previous_frame=idx > 0,
            )


__all__ = ["Supplementary"]
