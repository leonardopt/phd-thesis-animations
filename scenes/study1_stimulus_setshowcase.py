"""
Study 1 — stimulus set showcase.

Shows a small set of ordered strips from the task stimulus set.

Render:
    uv run manim scenes/study1_stimulus_setshowcase.py Study1StimulusSetShowcase -qh
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

from manim import *

from utils import env_path

BG    = WHITE
INK   = "#1C1C1E"

STIMULI_TASK_DIR = env_path(
    "STIMULI_TASK_DIR",
    env_path("EXEMPLAR_IMAGES_DIR").parent / "stimuli_task",
)

SHOWCASE_TARGETS = [
    ("Tropical Karst", "LAN-TRP"),
    ("Pine Mediterranean", "PLA-PIE"),
    ("Observatory", "BUI-OBS"),
    ("Sofa", "ITE-SOF"),
    ("Passenger train", "VEH-PAS"),
]


def resolve_strip_paths(display_name: str, image_code: str) -> list[Path]:
    paths = [
        STIMULI_TASK_DIR / f"{image_code}-{idx:02d}.png"
        for idx in range(10)
    ]
    missing = [fp.name for fp in paths if not fp.exists()]
    if missing:
        raise FileNotFoundError(
            f"Could not resolve the full 10-image set for '{display_name}' "
            f"with code '{image_code}' from {STIMULI_TASK_DIR}. Missing: {missing}"
        )
    return paths


def build_row(image_paths: list[Path]) -> dict[str, Mobject]:
    thumbs = Group(*[
        ImageMobject(str(image_path))
        for image_path in image_paths
    ])
    for thumb in thumbs:
        thumb.height = 0.94

    thumbs.arrange(RIGHT, buff=0.035)
    return {
        "thumbs": thumbs,
    }


class Study1StimulusSetShowcase(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        title = Tex(
            r"\textbf{Model-based preselected sets of 10 images for each object-scene}",
            color=INK,
            font_size=24,
        )
        title.to_edge(UP, buff=0.18)

        row_specs = [
            build_row(resolve_strip_paths(display_name, image_code))
            for display_name, image_code in SHOWCASE_TARGETS
        ]
        anchor_mobs = Group()

        thumb_w = row_specs[0]["thumbs"][0].width
        thumb_h = row_specs[0]["thumbs"][0].height
        thumb_gap = 0.035
        row_gap = 0.05
        row_width = 10 * thumb_w + 9 * thumb_gap
        row_height = thumb_h
        x_left = -row_width / 2 + thumb_w / 2
        row_ys = np.linspace(
            (len(row_specs) - 1) * (row_height + row_gap) / 2,
            -(len(row_specs) - 1) * (row_height + row_gap) / 2,
            len(row_specs),
        )

        rows_target = Group(*[
            spec["thumbs"]
            for spec in row_specs
        ])
        rows_target.move_to(DOWN * 0.36)
        available_width = config.frame_width - 0.06
        available_height = config.frame_height - 0.52
        if rows_target.width > available_width:
            rows_target.scale_to_fit_width(available_width)
        if rows_target.height > available_height:
            rows_target.scale_to_fit_height(available_height)

        thumb_w = row_specs[0]["thumbs"][0].width
        thumb_h = row_specs[0]["thumbs"][0].height
        row_width = 10 * thumb_w + 9 * thumb_gap
        row_height = thumb_h
        x_left = -row_width / 2 + thumb_w / 2
        row_ys = np.linspace(
            (len(row_specs) - 1) * (row_height + row_gap) / 2,
            -(len(row_specs) - 1) * (row_height + row_gap) / 2,
            len(row_specs),
        ) + np.array([-0.36] * len(row_specs))

        unfold_tracks = []

        for row_idx, spec in enumerate(row_specs):
            thumbs = spec["thumbs"]
            anchor = thumbs[0]
            start_center = np.array([0.0, row_ys[row_idx], 0.0])
            final_centers = [
                np.array([x_left + thumb_idx * (thumb_w + thumb_gap), row_ys[row_idx], 0.0])
                for thumb_idx in range(len(thumbs))
            ]

            anchor_mobs.add(anchor)
            anchor.move_to(start_center)
            anchor.set_z_index(3)

            for thumb_idx, thumb in enumerate(thumbs):
                if thumb_idx == 0:
                    continue
                thumb.move_to(start_center)
                thumb.set_opacity(0)
                thumb.set_z_index(2)

            thumb_animations = [
                anchor.animate.move_to(final_centers[0]),
            ]
            for thumb_idx, thumb in enumerate(thumbs[1:], start=1):
                thumb_animations.append(
                    Succession(
                        Wait(0.05 * thumb_idx),
                        thumb.animate.move_to(final_centers[thumb_idx]).set_opacity(1),
                    )
                )

            unfold_tracks.append(
                AnimationGroup(
                    *thumb_animations,
                    lag_ratio=0,
                )
            )

        self.play(FadeIn(title, shift=DOWN * 0.04), run_time=0.35)
        self.play(FadeIn(anchor_mobs, scale=0.9), run_time=0.4)
        self.wait(0.35)
        self.play(
            AnimationGroup(*unfold_tracks, lag_ratio=0.08, rate_func=smooth),
            run_time=2.6,
        )
        self.wait(1.4)
