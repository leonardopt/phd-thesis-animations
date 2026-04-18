#!/usr/bin/env python3
"""Sync external source assets into repo-local publication paths."""

from __future__ import annotations

import argparse
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()


@dataclass(frozen=True)
class SyncItem:
    group: str
    kind: str
    source: Path
    dest: Path
    patterns: tuple[str, ...] = ()


ITEMS: tuple[SyncItem, ...] = (
    # Small, high-value local copies.
    SyncItem(
        "small",
        "file",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "anchor_images" / "anchor-animal-fish.png",
        REPO_ROOT / "assets" / "images" / "study1" / "anchor_images" / "anchor-animal-fish.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "dataset_info" / "similarity_scores_anchors" / "lpips-squeeze-mat-animal-fish.csv",
        REPO_ROOT / "assets" / "data" / "study1" / "lpips-squeeze-mat-animal-fish.csv",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "dataset_info" / "similarity_scores_interpolations" / "lpips-squeeze-mat-interpols-animal-fish.csv",
        REPO_ROOT / "assets" / "data" / "study1" / "lpips-squeeze-mat-interpols-animal-fish.csv",
    ),
    SyncItem(
        "small",
        "glob",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "stimuli_task",
        REPO_ROOT / "assets" / "images" / "study1" / "stimuli_task",
        (
            "LAN-TRP-*.png",
            "PLA-PIE-*.png",
            "BUI-OBS-*.png",
            "ITE-SOF-*.png",
            "VEH-PAS-*.png",
        ),
    ),
    SyncItem(
        "small",
        "file",
        HOME / "stable-visual-memory-design" / "stimuli_task" / "LAN-MOU-T00.png",
        REPO_ROOT / "assets" / "images" / "study1" / "memory_task" / "LAN-MOU-T00.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "stable-visual-memory-design" / "stimuli_task" / "LAN-MOU-D01.png",
        REPO_ROOT / "assets" / "images" / "study1" / "memory_task" / "LAN-MOU-D01.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "stable-visual-memory-design" / "stimuli_task" / "LAN-MOU-D03.png",
        REPO_ROOT / "assets" / "images" / "study1" / "memory_task" / "LAN-MOU-D03.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "stable-visual-memory-design" / "stimuli_task" / "stimuli_info.csv",
        REPO_ROOT / "assets" / "data" / "study1" / "stimuli_info.csv",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "visual-memory-task-analysis" / "figures" / "manim" / "p2_manim.svg",
        REPO_ROOT / "assets" / "images" / "references" / "p2_manim.svg",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "visual-memory-task-analysis" / "figures" / "manim" / "p3_manim.svg",
        REPO_ROOT / "assets" / "images" / "references" / "p3_manim.svg",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "LAN-LAK-T00.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "LAN-LAK-T00.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "LAN-LAK-D01.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "LAN-LAK-D01.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "LAN-LAK-D02.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "LAN-LAK-D02.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "PLA-PIN-T00.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "PLA-PIN-T00.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "BUI-OBS-T00.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "BUI-OBS-T00.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "ANI-CAT-T00.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "ANI-CAT-T00.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "ITE-VAS-T00.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "ITE-VAS-T00.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_task" / "PLA-BRI-T00.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_task" / "PLA-BRI-T00.png",
    ),
    SyncItem(
        "small",
        "file",
        HOME / "sd-wltm-fmri-experiment" / "images" / "stimuli_training" / "ITE-SOF-T00.png",
        REPO_ROOT / "assets" / "images" / "study2" / "stimuli_training" / "ITE-SOF-T00.png",
    ),
    # Heavy Study 1 assets kept as a sync workflow rather than committed defaults.
    SyncItem(
        "study1-exemplars",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "exemplar_images" / "animal" / "fish",
        REPO_ROOT / "assets" / "images" / "study1" / "exemplar_images" / "animal" / "fish",
    ),
    SyncItem(
        "study1-exemplars",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "exemplar_images" / "plant" / "sequoia",
        REPO_ROOT / "assets" / "images" / "study1" / "exemplar_images" / "plant" / "sequoia",
    ),
    SyncItem(
        "study1-exemplars",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "exemplar_images" / "landscape_element" / "lake_island",
        REPO_ROOT / "assets" / "images" / "study1" / "exemplar_images" / "landscape_element" / "lake_island",
    ),
    SyncItem(
        "study1-exemplars",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "exemplar_images" / "building" / "observatory",
        REPO_ROOT / "assets" / "images" / "study1" / "exemplar_images" / "building" / "observatory",
    ),
    SyncItem(
        "study1-exemplars",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "exemplar_images" / "vehicle" / "campervan",
        REPO_ROOT / "assets" / "images" / "study1" / "exemplar_images" / "vehicle" / "campervan",
    ),
    SyncItem(
        "study1-exemplars",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "exemplar_images" / "item" / "sofa",
        REPO_ROOT / "assets" / "images" / "study1" / "exemplar_images" / "item" / "sofa",
    ),
    SyncItem(
        "study1-interpolations",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "fish_interpolations",
        REPO_ROOT / "assets" / "images" / "study1" / "fish_interpolations",
    ),
    SyncItem(
        "study1-reordered",
        "tree",
        HOME / "similarity-judgment-task-analysis" / "data" / "assets" / "images" / "stimuli_reordered",
        REPO_ROOT / "assets" / "images" / "stimuli_reordered",
    ),
)


GROUPS = tuple(sorted({item.group for item in ITEMS}))


def copy_file(source: Path, dest: Path) -> bool:
    if not source.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return True


def copy_tree(source: Path, dest: Path) -> bool:
    if not source.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, dirs_exist_ok=True)
    return True


def copy_globs(source_dir: Path, dest_dir: Path, patterns: tuple[str, ...]) -> bool:
    if not source_dir.exists():
        return False
    copied_any = False
    dest_dir.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        for source in sorted(source_dir.glob(pattern)):
            if source.is_file():
                shutil.copy2(source, dest_dir / source.name)
                copied_any = True
    return copied_any


def sync_groups(groups: list[str]) -> int:
    status = defaultdict(int)

    for item in ITEMS:
        if item.group not in groups:
            continue

        if item.kind == "file":
            copied = copy_file(item.source, item.dest)
        elif item.kind == "tree":
            copied = copy_tree(item.source, item.dest)
        elif item.kind == "glob":
            copied = copy_globs(item.source, item.dest, item.patterns)
        else:
            raise ValueError(f"Unsupported sync item kind: {item.kind}")

        if copied:
            status["copied"] += 1
            print(f"[copied] {item.group}: {item.source} -> {item.dest}")
        else:
            status["missing"] += 1
            print(f"[missing] {item.group}: {item.source}")

    print()
    print(f"Finished asset sync. copied={status['copied']} missing={status['missing']}")
    return 0 if status["missing"] == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--groups",
        nargs="+",
        choices=GROUPS,
        default=["small"],
        help="Asset groups to sync. Defaults to 'small'.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Sync every defined group.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    groups = list(GROUPS) if args.all else args.groups
    return sync_groups(groups)


if __name__ == "__main__":
    raise SystemExit(main())
