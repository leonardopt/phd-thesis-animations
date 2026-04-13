"""Shared utilities for phd-thesis-animations scenes."""
import os
import tempfile
import shutil
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent


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
