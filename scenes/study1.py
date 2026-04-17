"""
Study 1 — all scenes consolidated.

Includes:
  - Study1Pipeline
  - Study1Step1a, Study1Step1b
  - Study1Step2, Study1Step2Showcase, Showcase_*
  - Study1Step3, Study1Step3Part1, Study1Step3Part2
  - Study1Step4Detailed, Study1Step4Setup, Study1Step4Interpolation, Study1Step4
  - Study1Step5Handoff, Study1Step5Deck, Study1Step5LPIPS
  - Study1StimulusSetShowcase
  - Study1Stage2TripletTask, Study1Stage2TripletTask2
  - Study1Stage2SimilarityJudgementsExamples
  - Study1Stage2OrdinalEmbedding, Study1Stage2EmbeddingResult
  - Study1Stage2ModelOrderToHeatmap
  - Study1Stage3MemoryIntro, Study1Stage3MemoryExpDesignA
  - Study1Stage3MemoryExpDesignB, Study1Stage3MemoryExpResults

Render examples:
    uv run manim scenes/study1.py Study1Pipeline -qh
    uv run manim scenes/study1.py Study1Step1a -qh
    uv run manim scenes/study1.py Study1Step2 -qh
    uv run manim scenes/study1.py Study1StimulusSetShowcase -qh
    uv run manim scenes/study1.py Study1Stage2TripletTask -qh
    uv run manim scenes/study1.py Study1Stage3MemoryIntro -qh
"""
from __future__ import annotations

import csv
import numpy as np
import pandas as pd
import matplotlib.cm as _mcm
import hashlib
import shutil
import subprocess
import tempfile
import re
from pathlib import Path
from PIL import Image as PILImage

from manim import *
from utils import env_path
