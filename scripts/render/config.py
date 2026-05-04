from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.utils import section_output_dir


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENES_DIR = REPO_ROOT / "scenes"


@dataclass(frozen=True)
class SectionConfig:
    key: str
    scene_file: Path
    scene_class: str
    output_dir: str
    status_line: str
    disable_caching: bool = False


SECTION_CONFIGS: dict[str, SectionConfig] = {
    "intro": SectionConfig(
        key="intro",
        scene_file=SCENES_DIR / "intro.py",
        scene_class="Introduction",
        output_dir=section_output_dir("intro"),
        status_line="Introduction -> intro (sectioned)",
    ),
    "methods": SectionConfig(
        key="methods",
        scene_file=SCENES_DIR / "methods.py",
        scene_class="Methods",
        output_dir=section_output_dir("methods"),
        status_line="Methods -> methods (sectioned)",
    ),
    "study1": SectionConfig(
        key="study1",
        scene_file=SCENES_DIR / "study1.py",
        scene_class="Study1",
        output_dir=section_output_dir("study1"),
        status_line="Study1 -> study1 (sectioned, cache disabled)",
        disable_caching=True,
    ),
    "study2": SectionConfig(
        key="study2",
        scene_file=SCENES_DIR / "study2.py",
        scene_class="Study2",
        output_dir=section_output_dir("study2"),
        status_line="Study2 -> study2 (sectioned, no cache)",
        disable_caching=True,
    ),
    "conclusion": SectionConfig(
        key="conclusion",
        scene_file=SCENES_DIR / "conclusion.py",
        scene_class="Conclusion",
        output_dir=section_output_dir("conclusion"),
        status_line="Conclusion -> conclusion (sectioned)",
    ),
    "supplementary": SectionConfig(
        key="supplementary",
        scene_file=SCENES_DIR / "supplementary.py",
        scene_class="Supplementary",
        output_dir=section_output_dir("supplementary"),
        status_line="Supplementary -> supplementary (sectioned)",
    ),
}

ORDERED_SECTION_KEYS: tuple[str, ...] = tuple(SECTION_CONFIGS)
ORDERED_SECTIONS: tuple[SectionConfig, ...] = tuple(
    SECTION_CONFIGS[section_key] for section_key in ORDERED_SECTION_KEYS
)
