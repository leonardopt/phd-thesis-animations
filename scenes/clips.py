"""
Standalone per-clip wrappers for development and iteration.

Each scene class from the production files is re-exported here under its
original name.  Rendering it writes directly into the chapter's sections
folder with the production filename, so the result can be used in-place.

Usage:
    uv run manim scenes/clips.py IntroCognitiveProblemA -ql
    uv run manim scenes/clips.py Study1Stage1Step2 -ql
    uv run manim scenes/clips.py Study2CrossSessionDecodingSetup -ql
    uv run manim scenes/clips.py ConclusionResults -ql
"""
from __future__ import annotations

import re
from pathlib import Path
import sys

_SCENES_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCENES_DIR.parent / "scripts"
for _d in (_SCENES_DIR, _SCRIPTS_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from manim import Scene, config
from utils import section_output_dir

from intro import _INTRO_SECTION_SCENES
from methods import _METHODS_MASTER_SECTION_ORDER, _METHODS_SECTION_NAMES
from study1 import _STUDY1_MASTER_SECTION_ORDER, _STUDY1_SECTION_NAMES
from study2 import _STUDY2_MASTER_SECTION_ORDER, _STUDY2_SECTION_NAMES
from conclusion import _CONCLUSION_MASTER_SECTION_ORDER, _CONCLUSION_SECTION_NAMES
from supplementary import _SUPPLEMENTARY_MASTER_SECTION_ORDER, _SUPPLEMENTARY_SECTION_NAMES

__all__: list[str] = []


def _register(chapter_key: str, pairs: list[tuple[type[Scene], str]]) -> None:
    output_dir = section_output_dir(chapter_key)
    for index, (scene_cls, section_name) in enumerate(pairs):
        output_name = f"{index:03}_{section_name}"

        def _make_init(cls: type, vdir: str, ofile: str):
            orig = cls.__init__
            def __init__(self, *args, **kwargs):
                config.video_dir = vdir
                config.output_file = ofile
                config.partial_movie_dir = f"{{video_dir}}/partial_movie_files/{ofile}"
                orig(self, *args, **kwargs)
            return __init__

        wrapper = type(
            scene_cls.__name__,
            (scene_cls,),
            {
                "__init__": _make_init(
                    scene_cls,
                    f"{{media_dir}}/videos/{output_dir}/{{quality}}/sections",
                    output_name,
                ),
                "__module__": __name__,
            },
        )
        globals()[scene_cls.__name__] = wrapper
        __all__.append(scene_cls.__name__)


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _alias(alias_name: str, target_name: str) -> None:
    target = globals()[target_name]
    globals()[alias_name] = type(
        alias_name,
        (target,),
        {
            "__module__": __name__,
        },
    )
    __all__.append(alias_name)


_register("intro",       [(cls, name) for name, cls in _INTRO_SECTION_SCENES])
_register("methods",     list(zip(_METHODS_MASTER_SECTION_ORDER, _METHODS_SECTION_NAMES, strict=True)))
_register("study1",      list(zip(_STUDY1_MASTER_SECTION_ORDER, _STUDY1_SECTION_NAMES, strict=True)))
_register("study2",      list(zip(_STUDY2_MASTER_SECTION_ORDER, _STUDY2_SECTION_NAMES, strict=True)))
_register("conclusion",  list(zip(_CONCLUSION_MASTER_SECTION_ORDER, _CONCLUSION_SECTION_NAMES, strict=True)))
_register("supplementary", list(zip(_SUPPLEMENTARY_MASTER_SECTION_ORDER, _SUPPLEMENTARY_SECTION_NAMES, strict=True)))

for _alias_name, _target_name in (
    ("CognitiveProblemA", "IntroCognitiveProblemA"),
    ("SensMemRepresentationsA", "IntroSensoryMemoryRepresentationA"),
    ("SensMemRepresentationsB", "IntroSensoryMemoryRepresentationB"),
    ("ClassicalView", "IntroClassicalView"),
    ("SensoryRecruitment", "IntroSensoryRecruitment"),
    ("ResearchQuestion1", "IntroResearchQuestion1"),
    ("ResearchQuestion2", "IntroResearchQuestion2"),
    ("ResearchQuestion3", "IntroResearchQuestion3"),
):
    _alias(_alias_name, _target_name)
del _alias_name, _target_name
