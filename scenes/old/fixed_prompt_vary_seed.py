"""
Alias scene for the Study 1 Step 2 clip.

This keeps the implementation in `study1_step2.py` while allowing renders to be
written under the `fixed_prompt_vary_seed` output path.

Render:
    uv run manim scenes/fixed_prompt_vary_seed.py FixedPromptVarySeed -qh
"""
from scenes.old.study1_step2 import Study1Step2


class FixedPromptVarySeed(Study1Step2):
    pass
