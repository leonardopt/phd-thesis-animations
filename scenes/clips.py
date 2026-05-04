"""
Standalone clip wrappers for development and iteration.

Most clips are exported under their original production scene name. Shared
supplementary clips use ``Supplementary...`` names so each public wrapper maps
to exactly one output path.

Usage:
    uv run manim scenes/clips.py IntroCognitiveProblemA -ql
    uv run manim scenes/clips.py Study1Stage1Step2 -ql
    uv run manim scenes/clips.py Study2CrossSessionDecodingSetup -ql
    uv run manim scenes/clips.py ConclusionApproach -ql
    uv run manim scenes/clips.py SupplementaryIntroResearchQuestion1 -ql
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class ClipSpec:
    """Render-routing spec for one public clip wrapper."""
    export_name: str
    scene_cls: type[Scene]
    video_dir: str
    output_name: str


def _section_pairs(
    section_names: tuple[str, ...],
    scene_classes: tuple[type[Scene], ...],
) -> tuple[tuple[str, type[Scene]], ...]:
    """Zip one chapter's section names to its scene classes in presentation order."""
    return tuple(zip(section_names, scene_classes, strict=True))


def _chapter_specs(
    chapter_key: str,
    section_scenes: Iterable[tuple[str, type[Scene]]],
    *,
    export_names: dict[str, str] | None = None,
) -> tuple[ClipSpec, ...]:
    """Build clip specs for one chapter."""
    output_dir = section_output_dir(chapter_key)
    video_dir = f"{{media_dir}}/videos/{output_dir}/{{quality}}/sections"
    specs: list[ClipSpec] = []
    for index, (section_name, scene_cls) in enumerate(section_scenes):
        export_name = scene_cls.__name__
        if export_names is not None:
            export_name = export_names.get(export_name, export_name)
        specs.append(
            ClipSpec(
                export_name=export_name,
                scene_cls=scene_cls,
                video_dir=video_dir,
                output_name=f"{index:03}_{section_name}",
            )
        )
    return tuple(specs)


def _make_clip_init(spec: ClipSpec):
    """Create the wrapper __init__ that routes renders into the correct clip path."""
    original_init = spec.scene_cls.__init__

    def __init__(self, *args, **kwargs):
        config.video_dir = spec.video_dir
        config.output_file = spec.output_name
        config.partial_movie_dir = f"{{video_dir}}/partial_movie_files/{spec.output_name}"
        original_init(self, *args, **kwargs)

    return __init__


def _make_clip_wrapper(spec: ClipSpec) -> type[Scene]:
    """Create one public clip wrapper class from a production scene."""
    return type(
        spec.export_name,
        (spec.scene_cls,),
        {
            "__doc__": spec.scene_cls.__doc__,
            "__init__": _make_clip_init(spec),
            "__module__": __name__,
            "__qualname__": spec.export_name,
        },
    )


def _register_clip(spec: ClipSpec, exports: dict[str, type[Scene]]) -> None:
    """Register one clip wrapper and fail fast on duplicate public names."""
    if spec.export_name in exports:
        raise ValueError(f"Duplicate clip export name: {spec.export_name}")
    exports[spec.export_name] = _make_clip_wrapper(spec)


def _register_alias(alias_name: str, target_name: str, exports: dict[str, type[Scene]]) -> None:
    """Expose a short alias class that subclasses an existing clip wrapper."""
    if alias_name in exports:
        raise ValueError(f"Duplicate clip export name: {alias_name}")
    try:
        target = exports[target_name]
    except KeyError as exc:
        raise ValueError(f"Unknown clip alias target: {target_name}") from exc
    exports[alias_name] = type(
        alias_name,
        (target,),
        {
            "__doc__": target.__doc__,
            "__module__": __name__,
            "__qualname__": alias_name,
        },
    )


_SUPPLEMENTARY_EXPORT_NAMES: dict[str, str] = {
    # Supplementary reuses intro and study1 scene classes directly, so give the
    # clip wrappers chapter-specific names instead of clobbering the originals.
    "IntroResearchQuestion1": "SupplementaryIntroResearchQuestion1",
    "IntroResearchQuestion2": "SupplementaryIntroResearchQuestion2",
    "IntroResearchQuestion3": "SupplementaryIntroResearchQuestion3",
    "Study1Stage3MemoryIntroA": "SupplementaryStudy1Stage3MemoryIntroA",
    "Study1Stage3MemoryIntroB": "SupplementaryStudy1Stage3MemoryIntroB",
    "Study1Stage3MemoryIntroC": "SupplementaryStudy1Stage3MemoryIntroC",
    "Study1Stage3MemoryIntroD": "SupplementaryStudy1Stage3MemoryIntroD",
    "Study1Stage3MemoryIntroE": "SupplementaryStudy1Stage3MemoryIntroE",
}
_ALIASES: tuple[tuple[str, str], ...] = (
    ("CognitiveProblemA", "IntroCognitiveProblemA"),
    ("SensMemRepresentationsA", "IntroSensoryMemoryRepresentationA"),
    ("SensMemRepresentationsB", "IntroSensoryMemoryRepresentationB"),
    ("ClassicalView", "IntroClassicalView"),
    ("SensoryRecruitment", "IntroSensoryRecruitment"),
    ("ResearchQuestion1", "IntroResearchQuestion1"),
    ("ResearchQuestion2", "IntroResearchQuestion2"),
    ("ResearchQuestion3", "IntroResearchQuestion3"),
)
_CLIP_SPECS: tuple[ClipSpec, ...] = (
    *_chapter_specs("intro", _INTRO_SECTION_SCENES),
    *_chapter_specs("methods", _section_pairs(_METHODS_SECTION_NAMES, _METHODS_MASTER_SECTION_ORDER)),
    *_chapter_specs("study1", _section_pairs(_STUDY1_SECTION_NAMES, _STUDY1_MASTER_SECTION_ORDER)),
    *_chapter_specs("study2", _section_pairs(_STUDY2_SECTION_NAMES, _STUDY2_MASTER_SECTION_ORDER)),
    *_chapter_specs("conclusion", _section_pairs(_CONCLUSION_SECTION_NAMES, _CONCLUSION_MASTER_SECTION_ORDER)),
    *_chapter_specs(
        "supplementary",
        _section_pairs(_SUPPLEMENTARY_SECTION_NAMES, _SUPPLEMENTARY_MASTER_SECTION_ORDER),
        export_names=_SUPPLEMENTARY_EXPORT_NAMES,
    ),
)
_CLIP_EXPORTS: dict[str, type[Scene]] = {}

for _clip_spec in _CLIP_SPECS:
    _register_clip(_clip_spec, _CLIP_EXPORTS)
for _alias_name, _target_name in _ALIASES:
    _register_alias(_alias_name, _target_name, _CLIP_EXPORTS)

globals().update(_CLIP_EXPORTS)
__all__ = list(_CLIP_EXPORTS)

del _alias_name, _target_name, _clip_spec
