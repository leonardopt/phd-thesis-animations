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
import numpy as np

_SCENES_DIR = Path(__file__).resolve().parent
if str(_SCENES_DIR) not in sys.path:
    sys.path.insert(0, str(_SCENES_DIR))

import old.study1_stage3_memory as _study1_stage3_memory
import old.study1_step2_showcase as _study1_step2_showcase
from manim import (
    AnimationGroup,
    Arrow,
    Axes,
    Create,
    DashedLine,
    DashedVMobject,
    DOWN,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    LaggedStart,
    LEFT,
    MathTex,
    MoveToTarget,
    ORIGIN,
    RIGHT,
    RoundedRectangle,
    Restore,
    Scene,
    Succession,
    SurroundingRectangle,
    Tex,
    TransformFromCopy,
    TransformMatchingTex,
    UP,
    VMobject,
    ValueTracker,
    VGroup,
    Write,
    always_redraw,
    config,
    linear,
    smooth,
    there_and_back,
)

from old.study1_stage2_psychophysical import (
    Study1Stage2EmbeddingResult as _Study1Stage2EmbeddingResult,
    Study1Stage2ModelOrderToHeatmap as _Study1Stage2ModelOrderToHeatmap,
    Study1Stage2OrdinalEmbedding as _Study1Stage2OrdinalEmbedding,
    Study1Stage2SimilarityJudgementsExamples as _Study1Stage2SimilarityJudgementsExamples,
    Study1Stage2TripletTask as _Study1Stage2TripletTask,
    Study1Stage2TripletTask2 as _Study1Stage2TripletTask2,
)
from old.study1_stage3_memory import (
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
    "Study1Stage3MemoryIntroA": "18",
    "Study1Stage3MemoryIntroB": "18",
    "Study1Stage3MemoryIntroC": "18",
    "Study1Stage3MemoryIntroD": "18",
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

_STUDY1_OUTPUT_NAME_OVERRIDES: dict[str, str] = {
    "Study1Stage3MemoryIntroA": "18_Study1Stage3MemoryIntroA",
    "Study1Stage3MemoryIntroB": "18_Study1Stage3MemoryIntroB",
    "Study1Stage3MemoryIntroC": "18_Study1Stage3MemoryIntroC",
    "Study1Stage3MemoryIntroD": "18_Study1Stage3MemoryIntroD",
}


class _Study1NumberedScene:
    """Mixin: auto-prefix the output file with the narrative scene number."""

    def __init__(self, *args, **kwargs):
        scene_name = self.__class__.__name__
        output_name = _STUDY1_OUTPUT_NAME_OVERRIDES.get(scene_name)
        if output_name is None:
            number = _STUDY1_SCENE_ORDER.get(scene_name, "")
            if number:
                output_name = f"{number}_{scene_name}"
        if output_name:
            config.output_file = output_name
        super().__init__(*args, **kwargs)


def _wrap_scene(scene_cls: type[Scene]) -> type[Scene]:
    class _Wrapped(_Study1NumberedScene, scene_cls):
        pass

    _Wrapped.__name__ = scene_cls.__name__
    _Wrapped.__qualname__ = scene_cls.__name__
    _Wrapped.__module__ = __name__
    _Wrapped.__doc__ = scene_cls.__doc__
    return _Wrapped


_MEMORY_INTRO_SET_SPECS: tuple[tuple[str, str], ...] = (
    ("plant", "pine_med"),
    ("landscape_element", "lake_island"),
    ("building", "observatory"),
    ("item", "sofa"),
)

_MEMORY_INTRO_TOP_FOIL_MEAN = 0.56
_MEMORY_INTRO_TOP_TARGET_MEAN = 0.88
_MEMORY_INTRO_TOP_CRITERION_START_X = 0.75
_MEMORY_INTRO_TOP_CRITERION_LABEL_BUFF = 0.34
_MEMORY_INTRO_A_TOP_TARGET_MEAN = 0.634
_MEMORY_INTRO_A_TOP_TARGET_REPEATED_MEAN = 0.80
_MEMORY_INTRO_A_TOP_TARGET_LABEL_X = 1.10
_MEMORY_INTRO_SECOND_TARGET_MEAN = 0.80
_MEMORY_INTRO_SECOND_TARGET_REPEATED_MEAN = 1.25
_MEMORY_INTRO_SECOND_TARGET_LABEL_X = 1.39
_MEMORY_INTRO_B_CLAIM = r"Perceptual dissimilarity enhances discriminability"
_MEMORY_INTRO_C_CLAIM = r"Repeated exposure enhances memory discriminability"
_MEMORY_INTRO_TARGET_COLOR = "#5B7493"
_MEMORY_INTRO_FOIL_COLOR = "#B67A5D"
_MEMORY_INTRO_AXIS_COLOR = "#C7CDD4"
_MEMORY_INTRO_CRITERION_COLOR = "#6B7280"
_MEMORY_INTRO_REPETITION_COLOR = "#000000"
_MEMORY_INTRO_SIGNAL_SIGMA = 0.16
_MEMORY_INTRO_SIGNAL_PEAK = 0.92
_MEMORY_INTRO_SIGNAL_NARROW_SIGMA = 0.113
_MEMORY_INTRO_SIGNAL_FOIL_NARROW_SIGMA = 0.13
_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS = (1.0 / 3.0, 2.0 / 3.0, 1.0)
_MEMORY_INTRO_REPETITION_LABEL_BUFF = 0.31
_MEMORY_INTRO_REPETITION_LABEL_RIGHT_SHIFT_FACTOR = 0.20
_MEMORY_INTRO_REPETITION_LABEL_PULSE_SCALE = 1.45
_MEMORY_INTRO_REPETITION_LABEL_TRANSITION_TIME = 0.30
_MEMORY_INTRO_REPETITION_FRAME_PULSE_WIDTH = 3.2
_MEMORY_INTRO_REPETITION_STEP_RUN_TIME = 2.40
_MEMORY_INTRO_REPETITION_STEP_PAUSE = 0.20
_MEMORY_INTRO_SIGNAL_X_RANGE = [0.0, 1.63]
_MEMORY_INTRO_CONTINUUM_CARD_HEIGHT = 0.56 * 1.45


def _normal_curve_intersection_x(
    *,
    left_mean: float,
    right_mean: float,
    left_sigma: float = _MEMORY_INTRO_SIGNAL_SIGMA,
    right_sigma: float = _MEMORY_INTRO_SIGNAL_SIGMA,
    left_peak: float = _MEMORY_INTRO_SIGNAL_PEAK,
    right_peak: float = _MEMORY_INTRO_SIGNAL_PEAK,
) -> float:
    if np.isclose(left_sigma, right_sigma) and np.isclose(left_peak, right_peak):
        return 0.5 * (left_mean + right_mean)

    a = (1.0 / (2.0 * right_sigma**2)) - (1.0 / (2.0 * left_sigma**2))
    b = (left_mean / (left_sigma**2)) - (right_mean / (right_sigma**2))
    c = (
        (right_mean**2 / (2.0 * right_sigma**2))
        - (left_mean**2 / (2.0 * left_sigma**2))
        - np.log(right_peak / left_peak)
    )

    roots = np.roots([a, b, c])
    real_roots = [
        float(root.real)
        for root in roots
        if np.isclose(root.imag, 0.0) and left_mean <= root.real <= right_mean
    ]
    if not real_roots:
        return 0.5 * (left_mean + right_mean)
    midpoint = 0.5 * (left_mean + right_mean)
    return min(real_roots, key=lambda root: abs(root - midpoint))


def _validate_memory_intro_distribution_order(
    *,
    foil_mean: float,
    target_mean: float,
) -> None:
    if target_mean <= foil_mean:
        raise ValueError(
            f"Target mean must be to the right of foil mean, got target_mean={target_mean:.3f}, "
            f"foil_mean={foil_mean:.3f}"
        )


def _build_memory_intro_plot(
    *,
    center: np.ndarray,
    foil_mean: float,
    target_mean: float,
    repeated_target_mean: float,
    foil_color: str,
    target_color: str,
    target_label_x: float,
    criterion_x: float,
    criterion_label_buff: float = 0.22,
    curve_stroke_width: float,
    area_opacity: float,
) -> dict[str, object]:
    _validate_memory_intro_distribution_order(
        foil_mean=foil_mean,
        target_mean=target_mean,
    )

    axes = Axes(
        x_range=[0.0, 1.85, 0.37],
        y_range=[0.0, 1.25, 0.5],
        x_length=5.10,
        y_length=2.25,
        axis_config={
            "color": _MEMORY_INTRO_AXIS_COLOR,
            "stroke_width": 1.5,
            "include_ticks": False,
            "include_tip": True,
            "tip_width": 0.09,
            "tip_height": 0.09,
        },
    )
    axes.move_to(center)

    foil_curve = axes.plot(
        lambda x: _MEMORY_INTRO_SIGNAL_PEAK
        * np.exp(-0.5 * ((x - foil_mean) / _MEMORY_INTRO_SIGNAL_SIGMA) ** 2),
        x_range=_MEMORY_INTRO_SIGNAL_X_RANGE,
        color=foil_color,
        stroke_width=curve_stroke_width,
    )
    target_curve = axes.plot(
        lambda x: _MEMORY_INTRO_SIGNAL_PEAK
        * np.exp(-0.5 * ((x - target_mean) / _MEMORY_INTRO_SIGNAL_SIGMA) ** 2),
        x_range=_MEMORY_INTRO_SIGNAL_X_RANGE,
        color=target_color,
        stroke_width=curve_stroke_width,
    )
    foil_area = axes.get_area(
        foil_curve,
        x_range=[_MEMORY_INTRO_SIGNAL_X_RANGE[0], _MEMORY_INTRO_SIGNAL_X_RANGE[1]],
        color=foil_color,
        opacity=area_opacity,
    )
    foil_area.set_stroke(width=0.0, opacity=0.0)
    target_area = axes.get_area(
        target_curve,
        x_range=[_MEMORY_INTRO_SIGNAL_X_RANGE[0], _MEMORY_INTRO_SIGNAL_X_RANGE[1]],
        color=target_color,
        opacity=area_opacity,
    )
    target_area.set_stroke(width=0.0, opacity=0.0)

    criterion_line = DashedLine(
        axes.c2p(criterion_x, 0.0),
        axes.c2p(criterion_x, 1.12),
        dash_length=0.10,
        dashed_ratio=0.55,
        color=_MEMORY_INTRO_CRITERION_COLOR,
        stroke_width=2.0,
    )
    criterion_label = Tex(r"Criterion", color=_MEMORY_INTRO_CRITERION_COLOR, font_size=22)
    criterion_label.next_to(criterion_line, UP, buff=criterion_label_buff)

    foil_curve_label = Tex(r"Foil\\signal", color=foil_color, font_size=18)
    foil_curve_label.move_to(axes.c2p(0.16, 0.84))
    target_curve_label = Tex(r"Target signal", color=target_color, font_size=18)
    target_curve_label.move_to(axes.c2p(min(target_label_x + 0.18, 1.58), 0.84))
    memory_strength_label = Tex(r"Memory strength", color=_study1_stage3_memory.INK, font_size=22)
    memory_strength_label.next_to(axes.x_axis, DOWN, buff=0.20)
    probability_density_label = Tex(r"Probability density", color=_study1_stage3_memory.INK, font_size=18)
    probability_density_label.rotate(np.pi / 2)
    probability_density_label.next_to(axes.y_axis, LEFT, buff=0.18)

    return {
        "axes": axes,
        "foil_curve": foil_curve,
        "target_curve": target_curve,
        "foil_area": foil_area,
        "target_area": target_area,
        "foil_mean": foil_mean,
        "target_mean": target_mean,
        "repeated_target_mean": repeated_target_mean,
        "foil_color": foil_color,
        "target_color": target_color,
        "curve_stroke_width": curve_stroke_width,
        "area_opacity": area_opacity,
        "criterion_top_y": 1.12,
        "criterion_line": criterion_line,
        "criterion_label": criterion_label,
        "criterion_label_buff": criterion_label_buff,
        "foil_curve_label": foil_curve_label,
        "target_curve_label": target_curve_label,
        "memory_strength_label": memory_strength_label,
        "probability_density_label": probability_density_label,
        "group": VGroup(
            axes,
            foil_area,
            target_area,
            foil_curve,
            target_curve,
            criterion_line,
            criterion_label,
            foil_curve_label,
            target_curve_label,
            memory_strength_label,
            probability_density_label,
        ),
    }


def _build_memory_intro_claim_title(
    text: str,
    *,
    anchor: np.ndarray,
) -> Tex:
    claim = Tex(
        text,
        color=_study1_stage3_memory.INK,
        font_size=40,
    )
    max_width = config.frame_width - 1.2
    if claim.width > max_width:
        claim.scale_to_fit_width(max_width)
    claim.move_to(anchor)
    return claim


def _build_memory_intro_repeated_frame(
    *,
    target_examples: tuple[ImageMobject, ...],
) -> DashedVMobject:
    repeated_rect = SurroundingRectangle(
        Group(*target_examples),
        color=_study1_stage3_memory.MGREY,
        stroke_width=1.8,
        buff=0.12,
        corner_radius=0.08,
    )
    repeated_rect.set_fill(opacity=0.0)
    dashed_frame = DashedVMobject(
        repeated_rect,
        num_dashes=54,
        dashed_ratio=0.58,
    )
    dashed_frame.set_stroke(
        color=_study1_stage3_memory.MGREY,
        width=1.8,
        opacity=1.0,
    )
    dashed_frame.set_fill(opacity=0.0)
    dashed_frame.set_z_index(7)
    return dashed_frame


def _build_memory_intro_repetition_label(
    iteration: int,
    *,
    anchor_group: Group,
) -> Tex:
    label = Tex(
        rf"Repetition {iteration}",
        color=_MEMORY_INTRO_REPETITION_COLOR,
        font_size=22,
    )
    label.next_to(anchor_group, UP, buff=_MEMORY_INTRO_REPETITION_LABEL_BUFF)
    label.shift(
        RIGHT
        * anchor_group.width
        * _MEMORY_INTRO_REPETITION_LABEL_RIGHT_SHIFT_FACTOR
    )
    label.set_z_index(7)
    return label


def _memory_intro_signal_peak_for_sigma(sigma: float) -> float:
    return _MEMORY_INTRO_SIGNAL_PEAK * (_MEMORY_INTRO_SIGNAL_SIGMA / sigma)


def _build_memory_intro_dynamic_plot(
    plot: dict[str, object],
    *,
    repetition_tracker: ValueTracker,
) -> dict[str, object]:
    axes = plot["axes"]
    foil_color = plot["foil_color"]
    target_color = plot["target_color"]
    curve_stroke_width = max(
        mob.get_stroke_width()
        for mob in plot["target_curve"].family_members_with_points()
        + plot["foil_curve"].family_members_with_points()
    )
    area_opacity = max(
        mob.get_fill_opacity()
        for mob in plot["target_area"].family_members_with_points()
        + plot["foil_area"].family_members_with_points()
    )

    def current_foil_sigma() -> float:
        progress = repetition_tracker.get_value()
        return _MEMORY_INTRO_SIGNAL_SIGMA + (
            _MEMORY_INTRO_SIGNAL_FOIL_NARROW_SIGMA - _MEMORY_INTRO_SIGNAL_SIGMA
        ) * progress

    def current_target_sigma() -> float:
        progress = repetition_tracker.get_value()
        return _MEMORY_INTRO_SIGNAL_SIGMA + (
            _MEMORY_INTRO_SIGNAL_NARROW_SIGMA - _MEMORY_INTRO_SIGNAL_SIGMA
        ) * progress

    def current_foil_mean() -> float:
        return plot["foil_mean"]

    def current_target_mean() -> float:
        return plot["target_mean"] + (
            plot["repeated_target_mean"] - plot["target_mean"]
        ) * repetition_tracker.get_value()

    def current_criterion_x() -> float:
        foil_sigma = current_foil_sigma()
        target_sigma = current_target_sigma()
        foil_mean = current_foil_mean()
        target_mean = current_target_mean()
        _validate_memory_intro_distribution_order(
            foil_mean=foil_mean,
            target_mean=target_mean,
        )
        return _normal_curve_intersection_x(
            left_mean=foil_mean,
            right_mean=target_mean,
            left_sigma=foil_sigma,
            right_sigma=target_sigma,
            left_peak=_memory_intro_signal_peak_for_sigma(foil_sigma),
            right_peak=_memory_intro_signal_peak_for_sigma(target_sigma),
        )

    def build_curve(mean: float, sigma: float, color: str) -> VMobject:
        peak = _memory_intro_signal_peak_for_sigma(sigma)
        return axes.plot(
            lambda x: peak * np.exp(-0.5 * ((x - mean) / sigma) ** 2),
            x_range=_MEMORY_INTRO_SIGNAL_X_RANGE,
            color=color,
            stroke_width=curve_stroke_width,
        )

    def build_area(curve: VMobject, color: str) -> VMobject:
        area = axes.get_area(
            curve,
            x_range=[_MEMORY_INTRO_SIGNAL_X_RANGE[0], _MEMORY_INTRO_SIGNAL_X_RANGE[1]],
            color=color,
            opacity=area_opacity,
        )
        area.set_stroke(width=0.0, opacity=0.0)
        return area

    foil_curve = always_redraw(
        lambda: build_curve(current_foil_mean(), current_foil_sigma(), foil_color)
    )
    target_curve = always_redraw(
        lambda: build_curve(current_target_mean(), current_target_sigma(), target_color)
    )
    foil_area = always_redraw(
        lambda: build_area(build_curve(current_foil_mean(), current_foil_sigma(), foil_color), foil_color)
    )
    target_area = always_redraw(
        lambda: build_area(build_curve(current_target_mean(), current_target_sigma(), target_color), target_color)
    )
    criterion_line = DashedLine(
        axes.c2p(current_criterion_x(), 0.0),
        axes.c2p(current_criterion_x(), plot["criterion_top_y"]),
        dash_length=0.10,
        dashed_ratio=0.55,
        color=_MEMORY_INTRO_CRITERION_COLOR,
        stroke_width=2.0,
    )
    criterion_line.add_updater(
        lambda mob: mob.put_start_and_end_on(
            axes.c2p(current_criterion_x(), 0.0),
            axes.c2p(current_criterion_x(), plot["criterion_top_y"]),
        )
    )

    criterion_label = plot["criterion_label"].copy()
    criterion_label.add_updater(
        lambda mob: mob.next_to(
            criterion_line,
            UP,
            buff=plot["criterion_label_buff"] + 0.10 * repetition_tracker.get_value(),
        )
    )
    criterion_line.update()
    criterion_label.update()

    return {
        "foil_curve": foil_curve,
        "target_curve": target_curve,
        "foil_area": foil_area,
        "target_area": target_area,
        "criterion_line": criterion_line,
        "criterion_label": criterion_label,
        "group": VGroup(
            axes,
            foil_area,
            target_area,
            foil_curve,
            target_curve,
            criterion_line,
            criterion_label,
            plot["foil_curve_label"],
            plot["target_curve_label"],
            plot["memory_strength_label"],
            plot["probability_density_label"],
        ),
    }


def _build_memory_intro_core(
    *,
    top_target_mean: float = _MEMORY_INTRO_TOP_TARGET_MEAN,
    top_target_label_x: float = 1.25,
    top_criterion_x: float = _MEMORY_INTRO_TOP_CRITERION_START_X,
) -> dict[str, object]:
    title = Tex(
        r"Memory validation task",
        color=_study1_stage3_memory.INK,
        font_size=40,
    ).move_to(ORIGIN)
    title_top_target = title.copy().to_edge(UP, buff=0.28)

    question = VGroup(
        Tex(
            r"Does proximity along the perceptual continua",
            color=_study1_stage3_memory.INK,
            font_size=26,
        ),
        Tex(
            r"of our image sets predict memory performance?",
            color=_study1_stage3_memory.INK,
            font_size=26,
        ),
    ).arrange(DOWN, buff=0.10).next_to(title_top_target, DOWN, buff=0.24)

    lookup = _study1_stage3_memory.load_stimulus_lookup()
    question_bottom_y = question.get_bottom()[1]
    row_spacing = 1.05
    bottom_margin_y = -config.frame_height / 2 + 0.55
    row_block_center_y = 0.5 * (question_bottom_y + bottom_margin_y)
    row_y_positions = [
        row_block_center_y + row_spacing * offset
        for offset in (1.5, 0.5, -0.5, -1.5)
    ]
    left_column_center_x = -config.frame_width / 4
    panel_center_x = 0.0
    selected_spacing = 1.05
    selected_xs = [
        panel_center_x + selected_spacing * offset
        for offset in (-1.5, -0.5, 0.5, 1.5)
    ]

    example_side_offset = 1.55
    example_image_height = 1.95 * 1.30
    example_center = np.array([0.0, row_block_center_y, 0.0])
    example_target = ImageMobject(_study1_stage3_memory.memory_task_stimulus_path("LAN-MOU-T00.png"))
    example_target.scale_to_fit_height(example_image_height)
    example_target.move_to(example_center + LEFT * example_side_offset)
    example_target.set_z_index(5)

    example_foil = ImageMobject(_study1_stage3_memory.memory_task_stimulus_path("LAN-MOU-D01.png"))
    example_foil.scale_to_fit_height(example_image_height)
    example_foil.move_to(example_center + RIGHT * example_side_offset)
    example_foil.set_z_index(4)

    example_left_row_center = np.array([left_column_center_x, row_block_center_y, 0.0])
    example_target_left_pos = example_left_row_center + LEFT * example_side_offset
    example_foil_left_pos = example_left_row_center + RIGHT * example_side_offset

    example_target_label = Tex(r"Target", color=_MEMORY_INTRO_TARGET_COLOR, font_size=26)
    example_target_label.move_to(
        example_target_left_pos + UP * (example_image_height / 2 + 0.28)
    )
    example_target_label.set_z_index(6)
    example_foil_label = Tex(r"Foil", color=_MEMORY_INTRO_FOIL_COLOR, font_size=26)
    example_foil_label.move_to(
        example_foil_left_pos + UP * (example_image_height / 2 + 0.28)
    )
    example_foil_label.set_z_index(6)
    plot = _build_memory_intro_plot(
        center=np.array([3.48, row_block_center_y - 0.05, 0.0]),
        foil_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
        target_mean=top_target_mean,
        repeated_target_mean=_MEMORY_INTRO_A_TOP_TARGET_REPEATED_MEAN,
        foil_color=_MEMORY_INTRO_FOIL_COLOR,
        target_color=_MEMORY_INTRO_TARGET_COLOR,
        target_label_x=top_target_label_x,
        criterion_x=top_criterion_x,
        criterion_label_buff=_MEMORY_INTRO_TOP_CRITERION_LABEL_BUFF,
        curve_stroke_width=4.0,
        area_opacity=0.20,
    )

    panels = []
    for (category, obj), row_y in zip(_MEMORY_INTRO_SET_SPECS, row_y_positions):
        row = lookup[(category, obj)]
        prefix = f"{category}_{obj}"
        cards = [
            _study1_stage3_memory.stimulus_image(
                prefix,
                idx,
                _MEMORY_INTRO_CONTINUUM_CARD_HEIGHT,
                (0.0, 0.0, 0.0),
            )
            for idx in range(10)
        ]
        row_group = Group(*cards).arrange(RIGHT, buff=0.09).move_to([panel_center_x, row_y, 0.0])
        selected_indices = [
            int(row["target_position"]),
            int(row["distractor_1_position"]),
            int(row["distractor_2_position"]),
            int(row["distractor_3_position"]),
        ]
        panels.append(
            {
                "row_group": row_group,
                "cards": cards,
                "selected_indices": selected_indices,
                "row_y": row_y,
                "spec": (category, obj),
            }
        )

    return {
        "title": title,
        "title_top_target": title_top_target,
        "question": question,
        "lookup": lookup,
        "row_block_center_y": row_block_center_y,
        "row_y_positions": row_y_positions,
        "left_column_center_x": left_column_center_x,
        "example_side_offset": example_side_offset,
        "example_image_height": example_image_height,
        "example_target": example_target,
        "example_foil": example_foil,
        "example_target_left_pos": example_target_left_pos,
        "example_foil_left_pos": example_foil_left_pos,
        "example_target_label": example_target_label,
        "example_foil_label": example_foil_label,
        "selected_xs": selected_xs,
        "plot": plot,
        "panels": panels,
    }


def _set_memory_intro_a_rest_state(ctx: dict[str, object]) -> None:
    ctx["title"].move_to(ctx["title_top_target"])
    ctx["example_target"].move_to(ctx["example_target_left_pos"]).set_opacity(1.0)
    ctx["example_foil"].move_to(ctx["example_foil_left_pos"]).set_opacity(1.0)

    plot = ctx["plot"]
    plot["target_curve"].set_stroke(width=2.2, opacity=1.0)
    plot["foil_curve"].set_stroke(width=2.2, opacity=1.0)
    plot["target_area"].set_fill(opacity=0.16)
    plot["foil_area"].set_fill(opacity=0.16)
    plot["target_curve_label"].set_opacity(1.0)
    plot["foil_curve_label"].set_opacity(1.0)


def _set_memory_intro_b_end_state(
    ctx: dict[str, object],
    followup: dict[str, object],
) -> None:
    _set_memory_intro_a_rest_state(ctx)
    ctx["question"].shift(followup["subtitle_shift"])
    ctx["example_target"].move_to(followup["upper_example_target_pos"])
    ctx["example_foil"].move_to(followup["upper_example_foil_pos"])
    ctx["example_target_label"].move_to(followup["upper_target_label_pos"])
    ctx["example_foil_label"].move_to(followup["upper_foil_label_pos"])
    ctx["plot"]["group"].shift(followup["upper_plot_shift"])
    ctx["plot"]["memory_strength_label"].move_to(
        followup["second_plot"]["memory_strength_label"].get_center()
    )
    followup["second_plot"]["memory_strength_label"].set_opacity(0.0)


def _build_memory_intro_b_followup(ctx: dict[str, object]) -> dict[str, object]:
    upper_row_center_y = ctx["row_block_center_y"] + 1.20
    subtitle_shift = UP * (0.10 * (upper_row_center_y - ctx["row_block_center_y"]))
    upper_example_center = np.array([ctx["left_column_center_x"], upper_row_center_y, 0.0])
    upper_example_target_pos = upper_example_center + LEFT * ctx["example_side_offset"]
    upper_example_foil_pos = upper_example_center + RIGHT * ctx["example_side_offset"]
    upper_label_buff = 0.28
    upper_target_label_pos = upper_example_target_pos + UP * (ctx["example_image_height"] / 2 + upper_label_buff)
    upper_foil_label_pos = upper_example_foil_pos + UP * (ctx["example_image_height"] / 2 + upper_label_buff)
    upper_plot_center = np.array([3.48, upper_row_center_y - 0.05, 0.0])
    upper_plot_shift = upper_plot_center - ctx["plot"]["axes"].get_center()

    second_row_center_y = ctx["row_block_center_y"] - (1.50 * 1.10)
    second_example_center = np.array([ctx["left_column_center_x"], second_row_center_y, 0.0])
    second_example_target_pos = second_example_center + LEFT * ctx["example_side_offset"]
    second_example_foil_pos = second_example_center + RIGHT * ctx["example_side_offset"]
    second_plot_center = np.array([3.48, second_row_center_y - 0.05, 0.0])

    second_example_target = ImageMobject(_study1_stage3_memory.memory_task_stimulus_path("LAN-MOU-T00.png"))
    second_example_target.scale_to_fit_height(ctx["example_image_height"])
    second_example_target.move_to(second_example_target_pos)
    second_example_target.set_z_index(5)

    second_example_foil = ImageMobject(_study1_stage3_memory.memory_task_stimulus_path("LAN-MOU-D03.png"))
    second_example_foil.scale_to_fit_height(ctx["example_image_height"])
    second_example_foil.move_to(second_example_foil_pos)
    second_example_foil.set_z_index(4)

    second_plot = _build_memory_intro_plot(
        center=second_plot_center,
        foil_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
        target_mean=_MEMORY_INTRO_SECOND_TARGET_MEAN,
        repeated_target_mean=_MEMORY_INTRO_SECOND_TARGET_REPEATED_MEAN,
        foil_color=_MEMORY_INTRO_FOIL_COLOR,
        target_color=_MEMORY_INTRO_TARGET_COLOR,
        target_label_x=_MEMORY_INTRO_SECOND_TARGET_LABEL_X,
        criterion_x=0.5 * (
            _MEMORY_INTRO_TOP_FOIL_MEAN + _MEMORY_INTRO_SECOND_TARGET_MEAN
        ),
        curve_stroke_width=2.2,
        area_opacity=0.16,
    )

    return {
        "subtitle_shift": subtitle_shift,
        "upper_example_target_pos": upper_example_target_pos,
        "upper_example_foil_pos": upper_example_foil_pos,
        "upper_target_label_pos": upper_target_label_pos,
        "upper_foil_label_pos": upper_foil_label_pos,
        "upper_plot_shift": upper_plot_shift,
        "second_example_target": second_example_target,
        "second_example_foil": second_example_foil,
        "second_plot": second_plot,
    }


def _build_memory_intro_c_overlay(ctx: dict[str, object]) -> dict[str, object]:
    collapsed_cards = []
    source_cards = []
    continuation_marks = []
    selected_card_lookup = {}

    for panel in ctx["panels"]:
        category, obj = panel["spec"]
        for col_idx, selected_idx in enumerate(panel["selected_indices"]):
            source_card = panel["cards"][selected_idx]
            collapsed_card = source_card.copy()
            collapsed_card.move_to(np.array([ctx["selected_xs"][col_idx], panel["row_y"], 0.0]))
            collapsed_card.set_z_index(7)
            collapsed_cards.append(collapsed_card)
            source_cards.append(source_card)
            selected_card_lookup[(category, obj, col_idx)] = collapsed_card

            if obj == "sofa":
                dot = MathTex(r"\vdots", color=_study1_stage3_memory.MGREY, font_size=24).next_to(
                    collapsed_card,
                    DOWN,
                    buff=0.19,
                )
                dot.set_z_index(7)
                continuation_marks.append(dot)

    continuation_group = VGroup(*continuation_marks)
    target_cards = Group(*collapsed_cards[0::4])
    foil_cards = Group(
        *[
            collapsed_cards[idx]
            for idx in range(len(collapsed_cards))
            if idx % 4 != 0
        ]
    )

    target_rect = SurroundingRectangle(
        Group(target_cards, continuation_group[0]),
        color=_study1_stage3_memory.MGREY,
        stroke_width=1.5,
        buff=0.10,
        corner_radius=0.06,
    )
    foil_rect = SurroundingRectangle(
        Group(foil_cards, *continuation_group[1:]),
        color=_study1_stage3_memory.MGREY,
        stroke_width=1.5,
        buff=0.10,
        corner_radius=0.06,
    )
    target_label = Tex(r"Targets", color=_study1_stage3_memory.INK, font_size=24).next_to(
        target_rect,
        UP,
        buff=0.12,
    )
    foil_label = Tex(r"Foils", color=_study1_stage3_memory.INK, font_size=24).next_to(
        foil_rect,
        UP,
        buff=0.12,
    )
    arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
    dissimilar_arrow = Arrow(
        start=np.array([target_rect.get_center()[0] - 0.20, arrow_y, 0.0]),
        end=np.array([foil_rect.get_right()[0] - 0.10, arrow_y, 0.0]),
        buff=0.0,
        stroke_width=2.0,
        color=_study1_stage3_memory.MGREY,
        tip_length=0.18,
        max_stroke_width_to_length_ratio=8,
        max_tip_length_to_length_ratio=0.10,
    )
    dissimilar_text = Tex(
        r"More dissimilar",
        color=_study1_stage3_memory.MGREY,
        font_size=22,
    ).next_to(dissimilar_arrow, DOWN, buff=0.10)

    return {
        "source_cards": source_cards,
        "collapsed_cards": collapsed_cards,
        "selected_card_lookup": selected_card_lookup,
        "continuation_marks": continuation_group,
        "target_rect": target_rect,
        "foil_rect": foil_rect,
        "target_label": target_label,
        "foil_label": foil_label,
        "dissimilar_arrow": dissimilar_arrow,
        "dissimilar_text": dissimilar_text,
    }


def _build_memory_intro_c_end_state() -> dict[str, object]:
    criterion_intersection_x = _normal_curve_intersection_x(
        left_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
        right_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
    )
    ctx = _build_memory_intro_core(
        top_target_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
        top_target_label_x=_MEMORY_INTRO_A_TOP_TARGET_LABEL_X,
        top_criterion_x=criterion_intersection_x,
    )
    followup = _build_memory_intro_b_followup(ctx)
    overlay = _build_memory_intro_c_overlay(ctx)
    _set_memory_intro_b_end_state(ctx, followup)
    return {
        "ctx": ctx,
        "followup": followup,
        "overlay": overlay,
    }


class Study1Stage3MemoryIntroA(Scene):
    """Open the memory-validation task and land on the single SDT schematic."""

    def construct(self) -> None:
        self.camera.background_color = _study1_stage3_memory.BG
        criterion_intersection_x = _normal_curve_intersection_x(
            left_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
            right_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
        )
        ctx = _build_memory_intro_core(
            top_target_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
            top_target_label_x=_MEMORY_INTRO_A_TOP_TARGET_LABEL_X,
            top_criterion_x=criterion_intersection_x,
        )
        plot = ctx["plot"]

        self.play(Write(ctx["title"]), run_time=0.70)
        self.wait(0.15)
        self.play(ctx["title"].animate.move_to(ctx["title_top_target"]), run_time=0.55)
        self.play(FadeIn(ctx["question"], shift=UP * 0.12), run_time=0.60)
        self.wait(0.60)

        self.play(
            FadeIn(ctx["example_target"], scale=0.96),
            FadeIn(ctx["example_foil"], scale=0.96),
            run_time=0.70,
        )
        self.wait(2.00)
        self.play(
            ctx["example_target"].animate.move_to(np.array([0.0, ctx["row_block_center_y"], 0.0])),
            ctx["example_foil"].animate.move_to(np.array([0.0, ctx["row_block_center_y"], 0.0])),
            run_time=0.70,
        )
        self.wait(2.00)

        target_visible = True

        def swap_example(delay: float) -> None:
            nonlocal target_visible
            target_visible = not target_visible
            self.play(
                ctx["example_target"].animate.set_opacity(1.0 if target_visible else 0.0),
                run_time=0.10,
                rate_func=linear,
            )
            self.wait(delay)

        for _ in range(8):
            swap_example(0.20)
        self.wait(2.00)

        self.play(
            ctx["example_target"].animate.move_to(ctx["example_target_left_pos"]).set_opacity(1.0),
            ctx["example_foil"].animate.move_to(ctx["example_foil_left_pos"]).set_opacity(1.0),
            run_time=0.65,
            rate_func=smooth,
        )
        self.play(
            FadeIn(ctx["example_target_label"], shift=UP * 0.10),
            FadeIn(ctx["example_foil_label"], shift=UP * 0.10),
            LaggedStart(
                Create(plot["axes"]),
                FadeIn(plot["foil_area"]),
                FadeIn(plot["target_area"]),
                Create(plot["foil_curve"]),
                Create(plot["target_curve"]),
                FadeIn(plot["foil_curve_label"], shift=UP * 0.08),
                FadeIn(plot["target_curve_label"], shift=UP * 0.08),
                FadeIn(plot["memory_strength_label"], shift=UP * 0.08),
                FadeIn(plot["probability_density_label"], shift=RIGHT * 0.08),
                lag_ratio=0.12,
            ),
            run_time=1.30,
        )
        self.play(
            Create(plot["criterion_line"]),
            FadeIn(plot["criterion_label"], shift=UP * 0.08),
            run_time=0.55,
        )
        self.play(
            ctx["example_target_label"].animate.scale(1.18),
            plot["target_curve"].animate.set_stroke(width=4.8, opacity=1.0),
            plot["target_area"].animate.set_fill(opacity=0.34),
            ctx["example_foil_label"].animate.set_opacity(0.35),
            plot["foil_curve"].animate.set_stroke(opacity=0.28),
            plot["foil_area"].animate.set_fill(opacity=0.08),
            plot["target_curve_label"].animate.set_opacity(0.35),
            plot["foil_curve_label"].animate.set_opacity(0.25),
            run_time=0.80,
        )
        self.wait(0.40)
        self.play(
            ctx["example_target_label"].animate.scale(1 / 1.18),
            plot["target_curve"].animate.set_stroke(width=2.2, opacity=0.28),
            plot["target_area"].animate.set_fill(opacity=0.08),
            ctx["example_target_label"].animate.set_opacity(0.35),
            ctx["example_foil_label"].animate.set_opacity(1.0),
            plot["foil_curve"].animate.set_stroke(width=2.2, opacity=0.28),
            plot["foil_area"].animate.set_fill(opacity=0.08),
            plot["target_curve_label"].animate.set_opacity(0.25),
            plot["foil_curve_label"].animate.set_opacity(0.35),
            run_time=0.30,
        )
        self.play(
            ctx["example_foil_label"].animate.scale(1.18),
            plot["foil_curve"].animate.set_stroke(width=4.8, opacity=1.0),
            plot["foil_area"].animate.set_fill(opacity=0.34),
            run_time=0.85,
        )
        self.wait(0.40)
        self.play(
            ctx["example_foil_label"].animate.scale(1 / 1.18),
            ctx["example_target_label"].animate.set_opacity(1.0),
            plot["target_curve"].animate.set_stroke(width=2.2, opacity=1.0),
            plot["target_area"].animate.set_fill(opacity=0.16),
            ctx["example_foil_label"].animate.set_opacity(1.0),
            plot["foil_curve"].animate.set_stroke(width=2.2, opacity=1.0),
            plot["foil_area"].animate.set_fill(opacity=0.16),
            plot["target_curve_label"].animate.set_opacity(1.0),
            plot["foil_curve_label"].animate.set_opacity(1.0),
            run_time=0.85,
        )
        self.wait(1.00)


class Study1Stage3MemoryIntroB(Scene):
    """Continue from intro A by stacking a second SDT example underneath."""

    def construct(self) -> None:
        self.camera.background_color = _study1_stage3_memory.BG
        criterion_intersection_x = _normal_curve_intersection_x(
            left_mean=_MEMORY_INTRO_TOP_FOIL_MEAN,
            right_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
        )
        ctx = _build_memory_intro_core(
            top_target_mean=_MEMORY_INTRO_A_TOP_TARGET_MEAN,
            top_target_label_x=_MEMORY_INTRO_A_TOP_TARGET_LABEL_X,
            top_criterion_x=criterion_intersection_x,
        )
        followup = _build_memory_intro_b_followup(ctx)
        _set_memory_intro_a_rest_state(ctx)

        self.add(
            ctx["title"],
            ctx["question"],
            ctx["example_target"],
            ctx["example_foil"],
            ctx["example_target_label"],
            ctx["example_foil_label"],
            ctx["plot"]["group"],
        )

        claim_title = _build_memory_intro_claim_title(
            _MEMORY_INTRO_B_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )

        self.wait(0.40)
        self.play(
            FadeOut(ctx["title"], shift=UP * 0.06),
            FadeOut(ctx["question"], shift=UP * 0.06),
            FadeIn(claim_title, shift=UP * 0.06),
            run_time=0.65,
        )
        self.play(
            ctx["example_target"].animate.move_to(followup["upper_example_target_pos"]),
            ctx["example_foil"].animate.move_to(followup["upper_example_foil_pos"]),
            ctx["example_target_label"].animate.move_to(followup["upper_target_label_pos"]),
            ctx["example_foil_label"].animate.move_to(followup["upper_foil_label_pos"]),
            ctx["plot"]["group"].animate.shift(followup["upper_plot_shift"]),
            run_time=1.05,
            rate_func=smooth,
        )
        self.wait(0.25)
        self.play(
            FadeIn(followup["second_example_target"], scale=0.96),
            FadeIn(followup["second_example_foil"], scale=0.96),
            run_time=0.70,
        )
        self.wait(0.25)
        self.play(
            LaggedStart(
                Create(followup["second_plot"]["axes"]),
                FadeIn(followup["second_plot"]["foil_area"]),
                FadeIn(followup["second_plot"]["target_area"]),
                Create(followup["second_plot"]["foil_curve"]),
                Create(followup["second_plot"]["target_curve"]),
                Create(followup["second_plot"]["criterion_line"]),
                FadeIn(followup["second_plot"]["criterion_label"], shift=UP * 0.08),
                FadeIn(followup["second_plot"]["foil_curve_label"], shift=UP * 0.08),
                FadeIn(followup["second_plot"]["target_curve_label"], shift=UP * 0.08),
                FadeIn(followup["second_plot"]["probability_density_label"], shift=RIGHT * 0.08),
                lag_ratio=0.10,
            ),
            ctx["plot"]["memory_strength_label"].animate.move_to(
                followup["second_plot"]["memory_strength_label"].get_center()
            ),
            run_time=1.35,
        )
        self.wait(1.10)


class Study1Stage3MemoryIntroC(Scene):
    """Hold on the two-example SDT layout from the end of intro B."""

    def construct(self) -> None:
        self.camera.background_color = _study1_stage3_memory.BG
        end_state = _build_memory_intro_c_end_state()
        ctx = end_state["ctx"]
        followup = end_state["followup"]
        repetition_tracker = ValueTracker(0.0)
        top_plot = _build_memory_intro_dynamic_plot(
            ctx["plot"],
            repetition_tracker=repetition_tracker,
        )
        second_plot = _build_memory_intro_dynamic_plot(
            followup["second_plot"],
            repetition_tracker=repetition_tracker,
        )
        dissimilarity_claim = _build_memory_intro_claim_title(
            _MEMORY_INTRO_B_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )
        repetition_claim = _build_memory_intro_claim_title(
            _MEMORY_INTRO_C_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )
        repeated_frame = _build_memory_intro_repeated_frame(
            target_examples=(ctx["example_target"], followup["second_example_target"]),
        )
        repetition_label_anchor = Group(ctx["plot"]["axes"], followup["second_plot"]["axes"])
        repetition_index_tracker = ValueTracker(1.0)
        repetition_label_pulse_tracker = ValueTracker(0.0)
        repetition_label_opacity_tracker = ValueTracker(0.0)
        repetition_label = always_redraw(
            lambda: _build_memory_intro_repetition_label(
                max(1, int(round(repetition_index_tracker.get_value()))),
                anchor_group=repetition_label_anchor,
            )
            .scale(
                1.0
                + (_MEMORY_INTRO_REPETITION_LABEL_PULSE_SCALE - 1.0)
                * repetition_label_pulse_tracker.get_value()
            )
            .set_opacity(repetition_label_opacity_tracker.get_value())
        )

        self.add(
            dissimilarity_claim,
            ctx["example_target"],
            ctx["example_foil"],
            ctx["example_target_label"],
            ctx["example_foil_label"],
            top_plot["group"],
            followup["second_example_target"],
            followup["second_example_foil"],
            second_plot["group"],
            repetition_label,
        )
        self.wait(0.40)
        self.play(
            FadeOut(dissimilarity_claim, shift=UP * 0.06),
            FadeIn(repetition_claim, shift=UP * 0.06),
            run_time=0.60,
        )
        self.wait(2.00)
        self.play(
            Create(repeated_frame),
            run_time=0.60,
        )
        self.wait(0.20)
        for pulse_idx, next_stage in enumerate(_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS):
            repetition_index_tracker.set_value(float(pulse_idx + 1))
            step_animations = [repetition_tracker.animate.set_value(next_stage)]
            step_animations.append(
                repeated_frame.animate(rate_func=there_and_back).set_stroke(
                    width=_MEMORY_INTRO_REPETITION_FRAME_PULSE_WIDTH
                )
            )
            step_animations.append(
                repetition_label_pulse_tracker.animate(rate_func=there_and_back).set_value(1.0)
            )
            if pulse_idx == 0:
                step_animations.append(repetition_label_opacity_tracker.animate.set_value(1.0))
            self.play(
                *step_animations,
                run_time=_MEMORY_INTRO_REPETITION_STEP_RUN_TIME,
            )
            repetition_label_pulse_tracker.set_value(0.0)
            if pulse_idx < len(_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS) - 1:
                self.wait(_MEMORY_INTRO_REPETITION_STEP_PAUSE)
        self.wait(0.40)


class Study1Stage3MemoryIntroD(Scene):
    """Overlay the full continua and collapse them to targets versus foils."""

    def construct(self) -> None:
        self.camera.background_color = _study1_stage3_memory.BG
        end_state = _build_memory_intro_c_end_state()
        ctx = end_state["ctx"]
        followup = end_state["followup"]
        overlay = end_state["overlay"]
        repetition_tracker = ValueTracker(1.0)
        top_plot = _build_memory_intro_dynamic_plot(
            ctx["plot"],
            repetition_tracker=repetition_tracker,
        )
        second_plot = _build_memory_intro_dynamic_plot(
            followup["second_plot"],
            repetition_tracker=repetition_tracker,
        )
        repetition_claim = _build_memory_intro_claim_title(
            _MEMORY_INTRO_C_CLAIM,
            anchor=ctx["title_top_target"].get_center(),
        )
        repeated_frame = _build_memory_intro_repeated_frame(
            target_examples=(ctx["example_target"], followup["second_example_target"]),
        )
        repetition_label_anchor = Group(ctx["plot"]["axes"], followup["second_plot"]["axes"])
        repetition_label = _build_memory_intro_repetition_label(
            len(_MEMORY_INTRO_REPEATED_EXPOSURE_STEPS),
            anchor_group=repetition_label_anchor,
        )

        self.add(
            repetition_claim,
            ctx["example_target"],
            ctx["example_foil"],
            ctx["example_target_label"],
            ctx["example_foil_label"],
            top_plot["group"],
            followup["second_example_target"],
            followup["second_example_foil"],
            second_plot["group"],
            repeated_frame,
            repetition_label,
        )

        self.wait(0.25)
        self.play(
            FadeOut(repetition_claim, shift=UP * 0.06),
            FadeOut(repeated_frame, shift=LEFT * 0.04),
            FadeOut(repetition_label, shift=UP * 0.04),
            FadeIn(ctx["title"], shift=UP * 0.06),
            FadeIn(ctx["question"], shift=UP * 0.06),
            run_time=0.65,
        )
        self.wait(0.20)
        self.play(
            LaggedStart(
                *[FadeIn(panel["row_group"], shift=UP * 0.08) for panel in ctx["panels"]],
                lag_ratio=0.08,
            ),
            FadeOut(ctx["example_target"], shift=UP * 0.04),
            FadeOut(ctx["example_foil"], shift=UP * 0.04),
            FadeOut(ctx["example_target_label"], shift=UP * 0.04),
            FadeOut(ctx["example_foil_label"], shift=UP * 0.04),
            FadeOut(top_plot["group"], shift=UP * 0.04),
            FadeOut(followup["second_example_target"], shift=DOWN * 0.04),
            FadeOut(followup["second_example_foil"], shift=DOWN * 0.04),
            FadeOut(second_plot["group"], shift=DOWN * 0.04),
            run_time=1.10,
        )
        self.wait(0.20)
        self.play(
            AnimationGroup(
                *[FadeOut(panel["row_group"]) for panel in ctx["panels"]],
                lag_ratio=0.0,
            ),
            LaggedStart(
                *[
                    TransformFromCopy(source_card.copy(), collapsed_card)
                    for source_card, collapsed_card in zip(overlay["source_cards"], overlay["collapsed_cards"])
                ],
                lag_ratio=0.06,
            ),
            run_time=1.80,
        )
        self.play(
            FadeIn(overlay["continuation_marks"]),
            Create(overlay["target_rect"]),
            Create(overlay["foil_rect"]),
            FadeIn(overlay["target_label"], shift=UP * 0.08),
            FadeIn(overlay["foil_label"], shift=UP * 0.08),
            Create(overlay["dissimilar_arrow"]),
            FadeIn(overlay["dissimilar_text"], shift=UP * 0.08),
            run_time=1.10,
        )
        self.wait(1.20)


class Study1Stage3MemoryExpDesignA(Scene):
    """Show the delayed match-to-sample design, continuing directly from IntroD."""

    def construct(self) -> None:
        self.camera.background_color = _study1_stage3_memory.BG
        end_state = _build_memory_intro_c_end_state()
        ctx = end_state["ctx"]
        overlay = end_state["overlay"]

        collapsed_cards = overlay["collapsed_cards"]
        continuation_marks = overlay["continuation_marks"]
        target_rect = overlay["target_rect"]
        foil_rect = overlay["foil_rect"]
        target_label = overlay["target_label"]
        foil_label = overlay["foil_label"]
        dissimilar_arrow = overlay["dissimilar_arrow"]
        dissimilar_text = overlay["dissimilar_text"]
        selected_card_lookup = overlay["selected_card_lookup"]
        lake_target_card = selected_card_lookup[("landscape_element", "lake_island", 0)]
        lake_d3_card = selected_card_lookup[("landscape_element", "lake_island", 3)]

        self.add(
            ctx["title"],
            ctx["question"],
            *collapsed_cards,
            continuation_marks,
            target_rect,
            foil_rect,
            target_label,
            foil_label,
            dissimilar_arrow,
            dissimilar_text,
        )

        left_panel = Group(
            *collapsed_cards,
            continuation_marks,
            target_rect,
            foil_rect,
            target_label,
            foil_label,
            dissimilar_arrow,
            dissimilar_text,
        )

        left_panel_target = left_panel.copy()
        left_panel_target.scale(0.80)
        left_half_center_x = -config.frame_width / 4
        left_panel_shift = np.array([left_half_center_x - left_panel_target.get_center()[0], 0.0, 0.0])
        self.wait(0.40)
        self.play(
            left_panel.animate.scale(0.80).shift(left_panel_shift),
            run_time=0.65,
            rate_func=smooth,
        )
        self.wait(0.20)

        frame_side = 1.75
        right_margin_x = config.frame_width / 2 - 0.35
        stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
        stage_center_y = 0.5 * (ctx["row_y_positions"][1] + ctx["row_y_positions"][2])
        right_center = np.array([stage_center_x, stage_center_y, 0.0])

        lake_prefix = "landscape_element_lake_island"
        lake_row = ctx["lookup"][("landscape_element", "lake_island")]
        target_idx = int(lake_row["target_position"])
        probe1_idx = int(lake_row["distractor_3_position"])
        probe2_idx = target_idx

        def stage_content(
            kind: str,
            center: np.ndarray,
            large: bool,
        ) -> Group:
            image_height = 0.95 if large else 0.44
            fixation_height = 0.18 if large else 0.06

            if kind == "target":
                img = _study1_stage3_memory.stimulus_image(lake_prefix, target_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = _study1_stage3_memory.fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind == "probe1":
                img = _study1_stage3_memory.stimulus_image(lake_prefix, probe1_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = _study1_stage3_memory.fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind == "probe2":
                img = _study1_stage3_memory.stimulus_image(lake_prefix, probe2_idx, image_height, center)
                img.set_z_index(8 if large else 6)
                fix = _study1_stage3_memory.fixation_on(img, height=fixation_height)
                return Group(img, fix)

            if kind in {"delay", "buffer", "iti"}:
                fix = _study1_stage3_memory.fixation_on(center, height=fixation_height)
                return Group(fix)

            response_size = 18 if large else 8
            response_buff = 0.14 if large else 0.04
            fix = _study1_stage3_memory.fixation_on(center, height=fixation_height)
            left_text = Tex(
                r"TWO",
                color=_study1_stage3_memory.INK,
                font_size=response_size,
            ).next_to(fix, LEFT, buff=response_buff)
            right_text = Tex(
                r"ONE",
                color=_study1_stage3_memory.INK,
                font_size=response_size,
            ).next_to(fix, RIGHT, buff=response_buff)
            arrow_length = 0.40 if large else 0.20
            arrow = Arrow(
                start=left_text.get_center() + RIGHT * (arrow_length / 2),
                end=left_text.get_center() + LEFT * (arrow_length / 2),
                color=_study1_stage3_memory.INK,
                stroke_width=10 if large else 4,
                buff=0,
                tip_length=0.3 if large else 0.10,
            )
            arrow.next_to(left_text, DOWN, buff=0.06 if large else 0.035)
            fix.set_z_index(8 if large else 6)
            left_text.set_z_index(8 if large else 6)
            right_text.set_z_index(8 if large else 6)
            arrow.set_z_index(8 if large else 6)
            return Group(left_text, fix, right_text, arrow)

        stage_specs = [
            ("2s", "Target", "target"),
            ("8s", "Delay", "delay"),
            ("1s", "Probe 1", "probe1"),
            ("0.5s", "Buffer", "buffer"),
            ("1s", "Probe 2", "probe2"),
            ("2s", "Response", "response"),
            ("(M=4s)", "ITI", "iti"),
        ]

        stage_frame = RoundedRectangle(
            corner_radius=0.12,
            width=frame_side,
            height=frame_side,
            stroke_color=_study1_stage3_memory.MGREY,
            stroke_width=1.6,
        ).move_to(right_center)
        stage_frame.set_fill(_study1_stage3_memory.BG, opacity=1.0)
        stage_duration = Tex(stage_specs[0][0], color=_study1_stage3_memory.INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
        stage_label = Tex(stage_specs[0][1], color=_study1_stage3_memory.INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)

        strip_side = 0.82
        strip_gap = 0.10
        strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
        quadrant_bottom_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1])
        strip_vertical_offset = 0.16
        strip_start_y = quadrant_bottom_y + strip_side / 2 - strip_vertical_offset
        strip_final_y = right_center[1] - 0.12 - strip_vertical_offset
        strip_start_centers = [
            np.array(
                [
                    right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                    strip_start_y,
                    0.0,
                ]
            )
            for i in range(len(stage_specs))
        ]
        strip_final_centers = [
            np.array(
                [
                    right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                    strip_final_y,
                    0.0,
                ]
            )
            for i in range(len(stage_specs))
        ]

        parked_cards = []
        for (_, _, kind), center in zip(stage_specs, strip_start_centers):
            parked_frame = RoundedRectangle(
                corner_radius=0.08,
                width=strip_side,
                height=strip_side,
                stroke_color=_study1_stage3_memory.MGREY,
                stroke_width=1.2,
            ).move_to(center)
            parked_frame.set_fill(_study1_stage3_memory.BG, opacity=1.0)
            parked_content = stage_content(kind, center, large=False)
            parked_group = Group(parked_frame, parked_content)
            parked_group.set_z_index(6)
            parked_cards.append(parked_group)

        strip_arrow_start_x = strip_start_centers[0][0] - strip_side / 2
        strip_arrow_y = ValueTracker(strip_start_y - strip_side / 2 - 0.18)
        strip_arrow_progress_x = ValueTracker(strip_arrow_start_x + 0.04)
        progress_arrow = always_redraw(
            lambda: Arrow(
                start=np.array([strip_arrow_start_x, strip_arrow_y.get_value(), 0.0]),
                end=np.array(
                    [
                        max(strip_arrow_progress_x.get_value(), strip_arrow_start_x + 0.04),
                        strip_arrow_y.get_value(),
                        0.0,
                    ]
                ),
                color=_study1_stage3_memory.LGREY,
                stroke_width=1.3,
                buff=0.0,
                tip_length=0.14,
            )
        )

        target_copy = lake_target_card.copy()
        target_copy.move_to(lake_target_card.get_center())
        target_copy.set_z_index(8)
        target_copy.generate_target()
        target_copy.target.scale_to_fit_height(0.95)
        target_copy.target.move_to(right_center)
        target_fixation = _study1_stage3_memory.fixation_on(right_center, height=0.18)
        active_content = Group(target_copy, target_fixation)

        self.play(
            Create(stage_frame),
            MoveToTarget(target_copy),
            FadeIn(target_fixation),
            FadeIn(stage_duration),
            FadeIn(stage_label),
            run_time=0.80,
        )
        self.add(progress_arrow)
        self.wait(0.20)

        hold_before_park = 1
        park_run_time = 0.4
        hold_after_park = 0.08

        for idx, (_, _, kind) in enumerate(stage_specs):
            self.wait(hold_before_park)

            self.play(
                TransformFromCopy(Group(stage_frame, active_content), parked_cards[idx]),
                strip_arrow_progress_x.animate.set_value(parked_cards[idx].get_right()[0]),
                run_time=park_run_time,
            )

            self.wait(hold_after_park)

            if idx == len(stage_specs) - 1:
                continue

            next_duration = Tex(stage_specs[idx + 1][0], color=_study1_stage3_memory.INK, font_size=24).next_to(stage_frame, UP, buff=0.16)
            next_label = Tex(stage_specs[idx + 1][1], color=_study1_stage3_memory.INK, font_size=24).next_to(stage_frame, DOWN, buff=0.18)
            next_kind = stage_specs[idx + 1][2]
            step_run_time = 0.5

            if next_kind in {"probe1", "probe2"}:
                source_card = lake_d3_card if next_kind == "probe1" else lake_target_card
                highlight_rect = SurroundingRectangle(
                    source_card,
                    color="#F63924",
                    stroke_width=2.5,
                    buff=0.06,
                    corner_radius=0.05,
                )
                highlight_rect.set_z_index(9)
                self.play(FadeIn(highlight_rect), run_time=0.25)
                self.wait(0.10)
                probe_copy = source_card.copy()
                probe_copy.move_to(source_card.get_center())
                probe_copy.set_z_index(8)
                probe_copy.generate_target()
                probe_copy.target.scale_to_fit_height(0.95)
                probe_copy.target.move_to(right_center)
                probe_fix = _study1_stage3_memory.fixation_on(right_center, height=0.18)
                next_content = Group(probe_copy, probe_fix)
                self.play(
                    FadeOut(active_content, shift=DOWN * 0.06),
                    FadeOut(highlight_rect),
                    MoveToTarget(probe_copy),
                    FadeIn(probe_fix),
                    FadeOut(stage_duration),
                    FadeIn(next_duration),
                    FadeOut(stage_label),
                    FadeIn(next_label),
                    run_time=0.90,
                )
            else:
                next_content = stage_content(next_kind, right_center, large=True)
                self.play(
                    FadeOut(active_content, shift=DOWN * 0.06),
                    FadeIn(next_content, shift=UP * 0.06),
                    FadeOut(stage_duration),
                    FadeIn(next_duration),
                    FadeOut(stage_label),
                    FadeIn(next_label),
                    run_time=step_run_time,
                )
            active_content = next_content
            stage_duration = next_duration
            stage_label = next_label
            self.wait(0.30 if next_kind == "delay" else 0.18)

        final_arrow_y = min(strip_final_y - (strip_side * 1.12) / 2 - 0.20, right_center[1] - 1.15)
        promotion_anims = [
            parked.animate.move_to(target_center)
            for parked, target_center in zip(parked_cards, strip_final_centers)
        ]
        self.play(
            FadeOut(active_content, shift=UP * 0.06),
            FadeOut(stage_frame, shift=UP * 0.06),
            FadeOut(stage_duration, shift=UP * 0.06),
            FadeOut(stage_label, shift=UP * 0.06),
            strip_arrow_y.animate.set_value(final_arrow_y),
            *promotion_anims,
            run_time=0.85,
        )

        final_duration_labels = VGroup(
            *[
                Tex(duration, color=_study1_stage3_memory.INK, font_size=16).next_to(card, UP, buff=0.10)
                for (duration, _, _), card in zip(stage_specs, parked_cards)
            ]
        )
        final_stage_labels = VGroup(
            *[
                Tex(label, color=_study1_stage3_memory.INK, font_size=16).next_to(card, DOWN, buff=0.10)
                for (_, label, _), card in zip(stage_specs, parked_cards)
            ]
        )
        time_label = MathTex("t", color=_study1_stage3_memory.INK, font_size=24).next_to(progress_arrow, RIGHT, buff=0.10)

        self.play(
            LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_duration_labels], lag_ratio=0.05),
            LaggedStart(*[FadeIn(label, shift=UP * 0.05) for label in final_stage_labels], lag_ratio=0.05),
            FadeIn(time_label, shift=RIGHT * 0.05),
            run_time=1.00,
        )
        self.wait(1.00)


def _build_memory_exp_design_a_end_state() -> dict[str, object]:
    end_state = _build_memory_intro_c_end_state()
    ctx = end_state["ctx"]
    overlay = end_state["overlay"]

    left_column_center_x = ctx["left_column_center_x"]
    selected_spacing = ctx["selected_xs"][1] - ctx["selected_xs"][0]
    left_selected_xs = [
        left_column_center_x + selected_spacing * offset
        for offset in (-1.5, -0.5, 0.5, 1.5)
    ]

    for idx, collapsed_card in enumerate(overlay["collapsed_cards"]):
        row_idx, col_idx = divmod(idx, 4)
        collapsed_card.move_to(np.array([left_selected_xs[col_idx], ctx["row_y_positions"][row_idx], 0.0]))

    for row_idx, dot in enumerate(overlay["continuation_marks"]):
        target_card = overlay["collapsed_cards"][12 + row_idx]
        dot.next_to(target_card, DOWN, buff=0.19)

    target_cards = Group(*[overlay["collapsed_cards"][idx] for idx in range(0, 16, 4)])
    foil_cards = Group(
        *[
            overlay["collapsed_cards"][idx]
            for idx in range(16)
            if idx % 4 != 0
        ]
    )
    continuation_marks = overlay["continuation_marks"]
    target_rect = SurroundingRectangle(
        Group(target_cards, continuation_marks[0]),
        color=_study1_stage3_memory.MGREY,
        stroke_width=1.5,
        buff=0.10,
        corner_radius=0.06,
    )
    foil_rect = SurroundingRectangle(
        Group(foil_cards, *continuation_marks[1:]),
        color=_study1_stage3_memory.MGREY,
        stroke_width=1.5,
        buff=0.10,
        corner_radius=0.06,
    )
    target_label = Tex(r"Targets", color=_study1_stage3_memory.INK, font_size=24).next_to(
        target_rect, UP, buff=0.12
    )
    foil_label = Tex(r"Foils", color=_study1_stage3_memory.INK, font_size=24).next_to(
        foil_rect, UP, buff=0.12
    )
    arrow_y = min(target_rect.get_bottom()[1], foil_rect.get_bottom()[1]) - 0.34
    dissimilar_arrow = Arrow(
        start=np.array([target_rect.get_center()[0] - 0.20, arrow_y, 0.0]),
        end=np.array([foil_rect.get_right()[0] - 0.10, arrow_y, 0.0]),
        buff=0.0,
        stroke_width=2.0,
        color=_study1_stage3_memory.MGREY,
        tip_length=0.18,
        max_stroke_width_to_length_ratio=8,
        max_tip_length_to_length_ratio=0.10,
    )
    dissimilar_text = Tex(
        r"More dissimilar",
        color=_study1_stage3_memory.MGREY,
        font_size=22,
    ).next_to(dissimilar_arrow, DOWN, buff=0.10)

    frame_side = 1.75
    right_margin_x = config.frame_width / 2 - 0.35
    stage_center_x = 0.5 * (foil_rect.get_right()[0] + right_margin_x)
    stage_center_y = 0.5 * (ctx["row_y_positions"][1] + ctx["row_y_positions"][2])
    right_center = np.array([stage_center_x, stage_center_y, 0.0])

    lake_prefix = "landscape_element_lake_island"
    lake_row = ctx["lookup"][("landscape_element", "lake_island")]
    target_idx = int(lake_row["target_position"])
    probe1_idx = int(lake_row["distractor_3_position"])
    probe2_idx = target_idx

    def stage_content(kind: str, center: np.ndarray, large: bool) -> Group:
        image_height = 0.95 if large else 0.44
        fixation_height = 0.18 if large else 0.06
        if kind == "target":
            img = _study1_stage3_memory.stimulus_image(lake_prefix, target_idx, image_height, center)
            img.set_z_index(8 if large else 6)
            return Group(img, _study1_stage3_memory.fixation_on(img, height=fixation_height))
        if kind == "probe1":
            img = _study1_stage3_memory.stimulus_image(lake_prefix, probe1_idx, image_height, center)
            img.set_z_index(8 if large else 6)
            return Group(img, _study1_stage3_memory.fixation_on(img, height=fixation_height))
        if kind == "probe2":
            img = _study1_stage3_memory.stimulus_image(lake_prefix, probe2_idx, image_height, center)
            img.set_z_index(8 if large else 6)
            return Group(img, _study1_stage3_memory.fixation_on(img, height=fixation_height))
        if kind in {"delay", "buffer", "iti"}:
            return Group(_study1_stage3_memory.fixation_on(center, height=fixation_height))
        response_size = 18 if large else 8
        response_buff = 0.14 if large else 0.04
        fix = _study1_stage3_memory.fixation_on(center, height=fixation_height)
        left_text = Tex(r"TWO", color=_study1_stage3_memory.INK, font_size=response_size).next_to(
            fix, LEFT, buff=response_buff
        )
        right_text = Tex(r"ONE", color=_study1_stage3_memory.INK, font_size=response_size).next_to(
            fix, RIGHT, buff=response_buff
        )
        arrow_len = 0.40 if large else 0.20
        arr = Arrow(
            start=left_text.get_center() + RIGHT * (arrow_len / 2),
            end=left_text.get_center() + LEFT * (arrow_len / 2),
            color=_study1_stage3_memory.INK,
            stroke_width=10 if large else 4,
            buff=0,
            tip_length=0.3 if large else 0.10,
        )
        arr.next_to(left_text, DOWN, buff=0.06 if large else 0.035)
        for mob in (fix, left_text, right_text, arr):
            mob.set_z_index(8 if large else 6)
        return Group(left_text, fix, right_text, arr)

    stage_specs = [
        ("2s", "Target", "target"),
        ("8s", "Delay", "delay"),
        ("1s", "Probe 1", "probe1"),
        ("0.5s", "Buffer", "buffer"),
        ("1s", "Probe 2", "probe2"),
        ("2s", "Response", "response"),
        ("(M=4s)", "ITI", "iti"),
    ]

    strip_side = 0.82
    strip_gap = 0.10
    strip_total_width = len(stage_specs) * strip_side + (len(stage_specs) - 1) * strip_gap
    strip_vertical_offset = 0.16
    strip_final_y = right_center[1] - 0.12 - strip_vertical_offset
    strip_final_centers = [
        np.array(
            [
                right_center[0] - strip_total_width / 2 + strip_side / 2 + i * (strip_side + strip_gap),
                strip_final_y,
                0.0,
            ]
        )
        for i in range(len(stage_specs))
    ]

    parked_cards = []
    for (_, _, kind), center in zip(stage_specs, strip_final_centers):
        parked_frame = RoundedRectangle(
            corner_radius=0.08,
            width=strip_side,
            height=strip_side,
            stroke_color=_study1_stage3_memory.MGREY,
            stroke_width=1.2,
        ).move_to(center)
        parked_frame.set_fill(_study1_stage3_memory.BG, opacity=1.0)
        parked_content = stage_content(kind, center, large=False)
        parked_group = Group(parked_frame, parked_content)
        parked_group.set_z_index(6)
        parked_cards.append(parked_group)

    final_duration_labels = VGroup(
        *[
            Tex(dur, color=_study1_stage3_memory.INK, font_size=16).next_to(card, UP, buff=0.10)
            for (dur, _, _), card in zip(stage_specs, parked_cards)
        ]
    )
    final_stage_labels = VGroup(
        *[
            Tex(lbl, color=_study1_stage3_memory.INK, font_size=16).next_to(card, DOWN, buff=0.10)
            for (_, lbl, _), card in zip(stage_specs, parked_cards)
        ]
    )
    final_arrow_y = min(strip_final_y - (strip_side * 1.12) / 2 - 0.20, right_center[1] - 1.15)
    strip_arrow_start_x = right_center[0] - strip_total_width / 2
    progress_arrow = Arrow(
        start=np.array([strip_arrow_start_x, final_arrow_y, 0.0]),
        end=np.array([right_center[0] + strip_total_width / 2, final_arrow_y, 0.0]),
        color=_study1_stage3_memory.LGREY,
        stroke_width=1.3,
        buff=0.0,
        tip_length=0.14,
    )
    time_label = MathTex("t", color=_study1_stage3_memory.INK, font_size=24).next_to(
        progress_arrow, RIGHT, buff=0.10
    )

    left_panel = Group(
        *overlay["collapsed_cards"],
        continuation_marks,
        target_rect,
        foil_rect,
        target_label,
        foil_label,
        dissimilar_arrow,
        dissimilar_text,
    )
    left_panel.scale(0.80)

    return {
        "title": ctx["title"],
        "question": ctx["question"],
        "collapsed_cards": overlay["collapsed_cards"],
        "continuation_marks": continuation_marks,
        "target_rect": target_rect,
        "foil_rect": foil_rect,
        "target_label": target_label,
        "foil_label": foil_label,
        "dissimilar_arrow": dissimilar_arrow,
        "dissimilar_text": dissimilar_text,
        "parked_cards": parked_cards,
        "final_duration_labels": final_duration_labels,
        "final_stage_labels": final_stage_labels,
        "progress_arrow": progress_arrow,
        "time_label": time_label,
    }


class Study1Stage3MemoryExpDesignB(Scene):
    """Difficulty labels, N=240, and block structure — sequel to ExpDesignA."""

    def construct(self) -> None:
        self.camera.background_color = _study1_stage3_memory.BG
        state = _build_memory_exp_design_a_end_state()

        self.add(
            state["title"],
            state["question"],
            *state["collapsed_cards"],
            *state["continuation_marks"],
            state["target_rect"],
            state["foil_rect"],
            state["target_label"],
            state["foil_label"],
            state["dissimilar_arrow"],
            state["dissimilar_text"],
            *state["parked_cards"],
            state["final_duration_labels"],
            state["final_stage_labels"],
            state["progress_arrow"],
            state["time_label"],
        )

        self.play(
            state["dissimilar_arrow"].animate.shift(DOWN * 0.38),
            state["dissimilar_text"].animate.shift(DOWN * 0.38),
            FadeOut(state["foil_rect"]),
            run_time=0.65,
        )

        foil_cols = [
            Group(
                *[state["collapsed_cards"][4 * row_idx + col_idx] for row_idx in range(4)],
                state["continuation_marks"][col_idx],
            )
            for col_idx in (1, 2, 3)
        ]
        for diff_label, color, col_group in [
            ("Hard", "#C94040", foil_cols[0]),
            ("Medium", "#C87137", foil_cols[1]),
            ("Easy", "#3A7EC8", foil_cols[2]),
        ]:
            col_rect = SurroundingRectangle(
                col_group,
                color=color,
                stroke_width=1.8,
                buff=0.08,
                corner_radius=0.06,
            )
            lbl = Tex(diff_label, color=color, font_size=22).next_to(col_group, DOWN, buff=0.18)
            self.play(Create(col_rect), FadeIn(lbl, shift=UP * 0.08), run_time=0.55)
            self.wait(0.35)

        self.wait(0.30)

        stats_block = VGroup(
            Tex(r"$N = 240$", color=_study1_stage3_memory.INK, font_size=22),
            Tex(
                r"6 blocks $\cdot$ half repeated, half new targets per block",
                color=_study1_stage3_memory.MGREY,
                font_size=20,
            ),
        ).arrange(DOWN, buff=0.12)
        timeline_bottom = min(
            state["final_stage_labels"].get_bottom()[1],
            state["time_label"].get_bottom()[1],
            state["progress_arrow"].get_bottom()[1],
        )
        stats_block.align_to(state["final_stage_labels"], LEFT)
        stats_block.set_y(timeline_bottom - stats_block.get_height() / 2 - 0.32)

        self.play(
            LaggedStart(
                FadeIn(stats_block[0], shift=UP * 0.08),
                FadeIn(stats_block[1], shift=UP * 0.08),
                lag_ratio=0.35,
            ),
            run_time=0.80,
        )
        self.wait(1.00)


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
    Study1Stage3MemoryIntroA,
    Study1Stage3MemoryIntroB,
    Study1Stage3MemoryIntroC,
    Study1Stage3MemoryIntroD,
    Study1Stage3MemoryExpDesignA,
    Study1Stage3MemoryExpDesignB,
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
