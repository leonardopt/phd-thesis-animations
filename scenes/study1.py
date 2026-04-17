"""
Study 1 — consolidated, numbered entrypoint.

Render from this file to keep all Study 1 outputs in the same
`media/videos/study1/...` folder with `NN_ClassName` filenames.

Main narrative sequence:
    01 Study1Step1a
    02 Study1Step1b
    03 Study1Step2
    04 Study1Step2Showcase
    05 Study1Step3Part1
    06 Study1Step3Part2
    07 Study1Step4Setup
    08 Study1Step4Interpolation
    09 Study1Step5Handoff
    10 Study1Step5Deck
    11 Study1Step5LPIPS
    12 Study1StimulusSetShowcase
    13 Study1Stage2TripletTask
    14 Study1Stage2TripletTask2
    15 Study1Stage2SimilarityJudgementsExamples
    16 Study1Stage2EmbeddingResult
    17 Study1Stage2ModelOrderToHeatmap
    18 Study1Stage3MemoryIntro
    19 Study1Stage3MemoryExpDesignA
    20 Study1Stage3MemoryExpDesignB
    21 Study1Stage3MemoryExpResults

Supplemental / alternate scenes are also re-exported and numbered after the
main sequence.

Render examples:
    uv run manim scenes/study1.py Study1Step1a -qh
    uv run manim scenes/study1.py Study1Step5LPIPS -qh
    uv run manim scenes/study1.py Study1Stage2TripletTask -qh
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCENES_DIR = Path(__file__).resolve().parent
if str(_SCENES_DIR) not in sys.path:
    sys.path.insert(0, str(_SCENES_DIR))

import old.study1_step2_showcase as _study1_step2_showcase
from manim import Scene, config

from old.study1_stage2_psychophysical import (
    Study1Stage2EmbeddingResult as _Study1Stage2EmbeddingResult,
    Study1Stage2ModelOrderToHeatmap as _Study1Stage2ModelOrderToHeatmap,
    Study1Stage2OrdinalEmbedding as _Study1Stage2OrdinalEmbedding,
    Study1Stage2SimilarityJudgementsExamples as _Study1Stage2SimilarityJudgementsExamples,
    Study1Stage2TripletTask as _Study1Stage2TripletTask,
    Study1Stage2TripletTask2 as _Study1Stage2TripletTask2,
)
from old.study1_stage3_memory import (
    Study1Stage3MemoryExpDesignA as _Study1Stage3MemoryExpDesignA,
    Study1Stage3MemoryExpDesignB as _Study1Stage3MemoryExpDesignB,
    Study1Stage3MemoryExpResults as _Study1Stage3MemoryExpResults,
    Study1Stage3MemoryIntro as _Study1Stage3MemoryIntro,
)
from old.study1_step1 import Study1Step1a as _Study1Step1a
from old.study1_step1 import Study1Step1b as _Study1Step1b
from old.study1_step2 import Study1Step2 as _Study1Step2
from old.study1_step2_showcase import Study1Step2Showcase as _Study1Step2Showcase
from old.study1_step3 import Study1Step3 as _Study1Step3
from old.study1_step3 import Study1Step3Part1 as _Study1Step3Part1
from old.study1_step3 import Study1Step3Part2 as _Study1Step3Part2
from old.study1_step4 import Study1Step4 as _Study1Step4
from old.study1_step4 import Study1Step4Detailed as _Study1Step4Detailed
from old.study1_step4 import Study1Step4Interpolation as _Study1Step4Interpolation
from old.study1_step4 import Study1Step4Setup as _Study1Step4Setup
from old.study1_step5 import Study1Step5Deck as _Study1Step5Deck
from old.study1_step5 import Study1Step5Handoff as _Study1Step5Handoff
from old.study1_step5 import Study1Step5LPIPS as _Study1Step5LPIPS
from old.study1_stimulus_setshowcase import (
    Study1StimulusSetShowcase as _Study1StimulusSetShowcase,
)

# Narrative order for numbered outputs.
_STUDY1_SCENE_ORDER: dict[str, str] = {
    "Study1Step1a": "01",
    "Study1Step1b": "02",
    "Study1Step2": "03",
    "Study1Step2Showcase": "04",
    "Study1Step3Part1": "05",
    "Study1Step3Part2": "06",
    "Study1Step4Setup": "07",
    "Study1Step4Interpolation": "08",
    "Study1Step5Handoff": "09",
    "Study1Step5Deck": "10",
    "Study1Step5LPIPS": "11",
    "Study1StimulusSetShowcase": "12",
    "Study1Stage2TripletTask": "13",
    "Study1Stage2TripletTask2": "14",
    "Study1Stage2SimilarityJudgementsExamples": "15",
    "Study1Stage2EmbeddingResult": "16",
    "Study1Stage2ModelOrderToHeatmap": "17",
    "Study1Stage3MemoryIntro": "18",
    "Study1Stage3MemoryExpDesignA": "19",
    "Study1Stage3MemoryExpDesignB": "20",
    "Study1Stage3MemoryExpResults": "21",
    "Study1Step3": "22",
    "Study1Step4Detailed": "23",
    "Study1Step4": "24",
    "Study1Stage2OrdinalEmbedding": "25",
    "Showcase_sequoia": "26",
    "Showcase_lake_island": "27",
    "Showcase_observatory": "28",
    "Showcase_campervan": "29",
    "Showcase_sofa": "30",
}


class _Study1NumberedScene:
    """Mixin: auto-prefix the output file with the narrative scene number."""

    def __init__(self, *args, **kwargs):
        number = _STUDY1_SCENE_ORDER.get(self.__class__.__name__, "")
        if number:
            config.output_file = f"{number}_{self.__class__.__name__}"
        super().__init__(*args, **kwargs)


def _wrap_scene(scene_cls: type[Scene]) -> type[Scene]:
    class _Wrapped(_Study1NumberedScene, scene_cls):
        pass

    _Wrapped.__name__ = scene_cls.__name__
    _Wrapped.__qualname__ = scene_cls.__name__
    _Wrapped.__module__ = __name__
    _Wrapped.__doc__ = scene_cls.__doc__
    return _Wrapped


_PUBLIC_SCENES: tuple[type[Scene], ...] = (
    _Study1Step1a,
    _Study1Step1b,
    _Study1Step2,
    _Study1Step2Showcase,
    _Study1Step3Part1,
    _Study1Step3Part2,
    _Study1Step4Setup,
    _Study1Step4Interpolation,
    _Study1Step5Handoff,
    _Study1Step5Deck,
    _Study1Step5LPIPS,
    _Study1StimulusSetShowcase,
    _Study1Stage2TripletTask,
    _Study1Stage2TripletTask2,
    _Study1Stage2SimilarityJudgementsExamples,
    _Study1Stage2EmbeddingResult,
    _Study1Stage2ModelOrderToHeatmap,
    _Study1Stage3MemoryIntro,
    _Study1Stage3MemoryExpDesignA,
    _Study1Stage3MemoryExpDesignB,
    _Study1Stage3MemoryExpResults,
    _Study1Step3,
    _Study1Step4Detailed,
    _Study1Step4,
    _Study1Stage2OrdinalEmbedding,
)

for _scene_cls in _PUBLIC_SCENES:
    globals()[_scene_cls.__name__] = _wrap_scene(_scene_cls)

for _name in dir(_study1_step2_showcase):
    if not _name.startswith("Showcase_"):
        continue

    _scene_cls = getattr(_study1_step2_showcase, _name)
    if isinstance(_scene_cls, type) and issubclass(_scene_cls, Scene):
        globals()[_name] = _wrap_scene(_scene_cls)


__all__ = list(_STUDY1_SCENE_ORDER)
