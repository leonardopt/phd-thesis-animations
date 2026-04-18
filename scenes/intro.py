"""
Introduction — consolidated, numbered entrypoint.

Render from this file to keep all introduction outputs in the same
`media/videos/introduction/...` folder with `NN_ClassName` filenames.

This entrypoint is intentionally empty for now. When intro scenes are ready,
import them here, assign their narrative order in `_INTRODUCTION_SCENE_ORDER`,
and add them to `_PUBLIC_SCENES`.
"""
from __future__ import annotations

from manim import Scene, config

# Narrative order for numbered outputs.
_INTRODUCTION_SCENE_ORDER: dict[str, str] = {}


class _IntroductionNumberedScene:
    """Mixin: auto-prefix the output file with the narrative scene number."""

    def __init__(self, *args, **kwargs):
        number = _INTRODUCTION_SCENE_ORDER.get(self.__class__.__name__, "")
        if number:
            config.output_file = f"{number}_{self.__class__.__name__}"
        super().__init__(*args, **kwargs)


def _wrap_scene(scene_cls: type[Scene]) -> type[Scene]:
    class _Wrapped(_IntroductionNumberedScene, scene_cls):
        pass

    _Wrapped.__name__ = scene_cls.__name__
    _Wrapped.__qualname__ = scene_cls.__name__
    _Wrapped.__module__ = __name__
    _Wrapped.__doc__ = scene_cls.__doc__
    return _Wrapped


_PUBLIC_SCENES: tuple[type[Scene], ...] = ()

for _scene_cls in _PUBLIC_SCENES:
    globals()[_scene_cls.__name__] = _wrap_scene(_scene_cls)


__all__ = list(_INTRODUCTION_SCENE_ORDER)
