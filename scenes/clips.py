"""
Standalone per-clip wrappers for development and iteration.

Usage:
    uv run manim scenes/clips.py IntroCognitiveProblemA -ql
    uv run manim scenes/clips.py Study1Clip01 -ql
    uv run manim scenes/clips.py Study2Clip07 -ql
"""
from __future__ import annotations

# ── Introduction ──────────────────────────────────────────────────────────────

from intro import _IntroductionFlow, BG as _INTRO_BG


class IntroCognitiveProblemA(_IntroductionFlow):
    def construct(self) -> None:
        self._play_intro_a_core()


class IntroCognitiveProblemB(_IntroductionFlow):
    def construct(self) -> None:
        self.camera.background_color = _INTRO_BG
        self._play_intro_b_core()


class IntroCognitiveProblemC(_IntroductionFlow):
    def construct(self) -> None:
        self.camera.background_color = _INTRO_BG
        b_state = self._build_intro_b_layout()
        self.add(*b_state["final_group"])
        self._transition_b_to_c(b_state)


class IntroClassicalView(_IntroductionFlow):
    def construct(self) -> None:
        self._play_intro_d_core()


class IntroSensoryRecruitment(_IntroductionFlow):
    def construct(self) -> None:
        self._play_intro_e_core()


class IntroResearchQuestions(_IntroductionFlow):
    def construct(self) -> None:
        self._play_intro_f_core()


# ── Study 1 ───────────────────────────────────────────────────────────────────

from study1 import (
    Study1Stage1Step1a,
    Study1Stage1Step1b,
    Study1Stage1Step2,
    Study1Stage1Step2Showcase,
    Study1Stage1Step3,
    Study1Stage1Step4,
    Study1Stage1Step5,
    Study1StimulusSetShowcase,
    Study1Stage2TripletTask,
    Study1Stage2TripletTask2,
    Study1Stage2SimilarityJudgementsExamples,
    Study1Stage2EmbeddingResult,
    Study1Stage2ModelOrderToHeatmap,
    Study1Stage3MemoryIntroA,
    Study1Stage3MemoryIntroB,
    Study1Stage3MemoryIntroC,
    Study1Stage3MemoryIntroD,
    Study1Stage3MemoryExpDesign,
    Study1Stage3MemoryExpResults,
)


class Study1Clip01(Study1Stage1Step1a): pass
class Study1Clip02(Study1Stage1Step1b): pass
class Study1Clip03(Study1Stage1Step2): pass
class Study1Clip04(Study1Stage1Step2Showcase): pass
class Study1Clip05(Study1Stage1Step3): pass
class Study1Clip07(Study1Stage1Step4): pass
class Study1Clip09(Study1Stage1Step5): pass
class Study1Clip12(Study1StimulusSetShowcase): pass
class Study1Clip13(Study1Stage2TripletTask): pass
class Study1Clip14(Study1Stage2TripletTask2): pass
class Study1Clip15(Study1Stage2SimilarityJudgementsExamples): pass
class Study1Clip16(Study1Stage2EmbeddingResult): pass
class Study1Clip17(Study1Stage2ModelOrderToHeatmap): pass
class Study1Clip18(Study1Stage3MemoryIntroA): pass
class Study1Clip19(Study1Stage3MemoryIntroB): pass
class Study1Clip20(Study1Stage3MemoryIntroC): pass
class Study1Clip21(Study1Stage3MemoryIntroD): pass
class Study1Clip22(Study1Stage3MemoryExpDesign): pass
class Study1Clip23(Study1Stage3MemoryExpResults): pass


# ── Study 2 ───────────────────────────────────────────────────────────────────

from study2 import (
    Study2ResearchQuestions,
    Study2ExperimentalDesign,
    Study2DecodingOverviewA,
    Study2DecodingOverviewB,
    Study2DecodingOverviewC,
    Study2WithinSession2DecodingSetup,
    Study2WithinSession2DecodingResults,
    Study2CrossSessionDecodingSetup,
    Study2CrossSessionDecodingResultsA,
    Study2CrossSessionDecodingResultsB,
    Study2WithinSession1DecodingSetupA,
    Study2WithinSession1DecodingSetupB,
    Study2WithinSession1DecodingResultsA,
    Study2WithinSession1DecodingResultsB,
    Study2WithinSession1DecodingResultsC,
    Study2WithinSession1DecodingResultsD,
    Study2LTMResultsExplainer,
    Study2SupplementalRoiTimecoursesA,
    Study2SupplementalRoiTimecoursesB,
    Study2SupplementalRoiTempGenMats,
    Study2SearchlightStimulation,
    Study2SearchlightDelay,
    Study2DecodingSummary,
)


class Study2Clip00(Study2ResearchQuestions): pass
class Study2Clip01(Study2ExperimentalDesign): pass
class Study2Clip02(Study2DecodingOverviewA): pass
class Study2Clip03(Study2DecodingOverviewB): pass
class Study2Clip04(Study2DecodingOverviewC): pass
class Study2Clip05(Study2WithinSession2DecodingSetup): pass
class Study2Clip06(Study2WithinSession2DecodingResults): pass
class Study2Clip07(Study2CrossSessionDecodingSetup): pass
class Study2Clip08(Study2CrossSessionDecodingResultsA): pass
class Study2Clip09(Study2CrossSessionDecodingResultsB): pass
class Study2Clip10(Study2WithinSession1DecodingSetupA): pass
class Study2Clip11(Study2WithinSession1DecodingSetupB): pass
class Study2Clip12(Study2WithinSession1DecodingResultsA): pass
class Study2Clip13(Study2WithinSession1DecodingResultsB): pass
class Study2Clip14(Study2WithinSession1DecodingResultsC): pass
class Study2Clip15(Study2WithinSession1DecodingResultsD): pass
class Study2Clip16(Study2LTMResultsExplainer): pass
class Study2Clip17(Study2SupplementalRoiTimecoursesA): pass
class Study2Clip18(Study2SupplementalRoiTimecoursesB): pass
class Study2Clip19(Study2SupplementalRoiTempGenMats): pass
class Study2Clip20(Study2SearchlightStimulation): pass
class Study2Clip21(Study2SearchlightDelay): pass
class Study2Clip22(Study2DecodingSummary): pass
