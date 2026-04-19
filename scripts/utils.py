"""Shared utilities for phd-thesis-animations scenes."""
import os
import tempfile
import shutil
from functools import lru_cache
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
SECTION_OUTPUT_DIRS: dict[str, str] = {
    "intro": "01_intro",
    "methods": "02_methods",
    "study1": "03_study1",
    "study2": "04_study2",
    "conclusion": "05_conclusion",
}
SECTION_DISPLAY_NAMES: dict[str, str] = {
    "intro": "Intro",
    "methods": "Methods",
    "study1": "Study 1",
    "study2": "Study 2",
    "conclusion": "Conclusion",
}
_SECTION_KEYS_BY_OUTPUT_DIR = {value: key for key, value in SECTION_OUTPUT_DIRS.items()}


@lru_cache(maxsize=1)
def _load_env_file() -> dict[str, str]:
    env_path = REPO_ROOT / ".env"
    data: dict[str, str] = {}
    if not env_path.exists():
        return data

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        data[key] = value
    return data


def env_value(name: str, default: str | None = None) -> str:
    if name in os.environ:
        return os.environ[name]
    data = _load_env_file()
    if name in data:
        return data[name]
    if default is not None:
        return default
    raise KeyError(f"Missing environment variable: {name}")


def env_path(name: str, default: str | Path | None = None) -> Path:
    raw_default = None if default is None else str(default)
    raw = env_value(name, raw_default)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def section_output_dir(section_name: str) -> str:
    """Return the canonical numbered output directory for one presentation section."""
    return SECTION_OUTPUT_DIRS.get(section_name, section_name)


def section_key_from_output_dir(output_dir_name: str) -> str:
    """Return the logical section key for a numbered output directory name."""
    return _SECTION_KEYS_BY_OUTPUT_DIR.get(output_dir_name, output_dir_name)


def section_display_name(section_name: str) -> str:
    """Return a human-friendly section label from either a key or output directory."""
    section_key = section_key_from_output_dir(section_name)
    return SECTION_DISPLAY_NAMES.get(section_key, section_key.replace("_", " ").title())


def simplify_manim_section_video_names(
    namer: Callable[[str, int, str, str], str] | None = None,
) -> None:
    """Patch Manim so section videos use a project-defined filename convention.

    Manim 0.20.1 hardcodes section filenames as
    ``<SceneName>_<index>_<section_name>.mp4``. For production renders we keep the
    section name in the JSON index and simplify the actual video filenames.
    """
    from manim import config
    from manim.scene.scene_file_writer import SceneFileWriter
    from manim.scene.section import Section
    from manim.utils.file_ops import write_to_movie

    if getattr(SceneFileWriter.next_section, "_phd_simple_section_names", False):
        return

    if namer is None:
        namer = lambda output_name, index, name, ext: f"{output_name}_{index:04}{ext}"

    def _next_section_simple_name(self, name: str, type_: str, skip_animations: bool) -> None:
        self.finish_last_section()

        section_video: str | None = None
        if (
            not config.dry_run
            and write_to_movie()
            and config.save_sections
            and not skip_animations
        ):
            section_video = namer(
                str(self.output_name),
                len(self.sections),
                name,
                config.movie_file_extension,
            )

        self.sections.append(Section(type_, section_video, name, skip_animations))

    _next_section_simple_name._phd_simple_section_names = True
    SceneFileWriter.next_section = _next_section_simple_name


STIM_DIR = env_path("STIMULI_REORDERED_DIR", REPO_ROOT / "assets" / "images" / "stimuli_reordered")


def stim_path(name: str) -> str:
    """Return absolute path to a stimulus image, e.g. stim_path('animal_fish-05')."""
    return os.path.join(STIM_DIR, f"{name}.png")


def noise_sequence(src_path: str, alphas: list[float], size: int = 512, seed: int = 42):
    """
    Generate a sequence of images blending the source image with random noise.

    alpha = 0.0 → original image
    alpha = 1.0 → pure random noise

    Returns (list_of_file_paths, tmpdir).
    Caller is responsible for calling shutil.rmtree(tmpdir) when done.
    """
    rng = np.random.default_rng(seed)
    img = Image.open(src_path).convert("RGB").resize((size, size), Image.LANCZOS)
    base = np.array(img, dtype=np.float32) / 255.0

    # Pre-generate one fixed noise frame so forward & reverse share the same noise image
    fixed_noise = rng.random(base.shape).astype(np.float32)

    tmpdir = tempfile.mkdtemp(prefix="manim_sdxl_")
    paths = []
    for k, alpha in enumerate(alphas):
        if alpha <= 0.0:
            out = base.copy()
        elif alpha >= 1.0:
            out = fixed_noise.copy()
        else:
            out = np.clip((1.0 - alpha) * base + alpha * fixed_noise, 0.0, 1.0)
        path = os.path.join(tmpdir, f"frame_{k:02d}.png")
        Image.fromarray((out * 255).astype(np.uint8)).save(path)
        paths.append(path)

    return paths, tmpdir
