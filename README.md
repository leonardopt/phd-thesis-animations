# Thesis Defence Animations

Source repository for my PhD defence presentation built with [Manim](https://www.manim.community/). The project contains the scene code and curated, restricted assets used to produce videos and Keynote slides. The talk was organised into an introduction, methods, two main study sections, a conclusion, and supplementary material.

## Preview

### Study 1 Stage 1 Step 2

[![Study 1 Stage 1 Step 2 preview](assets/images/readme_preview_study1_stage1_step2.gif)](media/videos/03_study1/1080p60/sections/002_study1_stage1_step2.mp4)

### Study 1 Stage 1 Step 4 Interpolation

[![Study 1 Stage 1 Step 4 interpolation preview](assets/images/readme_preview_study1_interpolation.gif)](media/videos/03_study1/1080p60/sections/006_007_study1_stage1_step4_setup_interpolation.mp4)

### Study 2 Within-Session 1 Decoding Results

[![Study 2 within-session 1 decoding results A-B preview](assets/images/readme_preview_study2_within_session1_results_ab.gif)](media/videos/04_study2/1080p60/sections/013_014_study2_within_session1_decoding_results_ab.mp4)

## Quick Start

Use Python 3.12+ with `uv` and the usual Manim system dependencies, including LaTeX and `ffmpeg`.

```bash
uv sync
```

## Rendering Videos

Render one production clip:

```bash
uv run manim scenes/clips.py Study1Stage1Step2 -qh
```

Render all production clips at 1080p60:

```bash
uv run manim scenes/clips.py $(uv run python -c "import scenes.clips as c; print(' '.join(s.export_name for s in c._CLIP_SPECS))") -qh
```

Quality flags:

- `-ql`: `480p15`
- `-qm`: `720p30`
- `-qh`: `1080p60`
- `-qk`: `2160p60`

Final 1080p renders are tracked under `media/videos/**/1080p60/sections/`. Manim partial movie files and other local build outputs remain ignored.

## Project Layout

- `scenes/`: Manim scene code and production clip wrappers
- `assets/`: figures, small videos, manifests, presenter notes, and asset documentation
- `scripts/`: rendering support, deck assembly, preflight checks, and packaging helpers

The clip entrypoint is `scenes/clips.py`. The main scene modules are `intro.py`, `methods.py`, `study1.py`, `study2.py`, `conclusion.py`, and `supplementary.py`.

## Assets And Outputs

Some larger study inputs are restored locally instead of committed. See [assets/README.md](assets/README.md) for sync details and [ASSET_RIGHTS.md](ASSET_RIGHTS.md) before reusing non-code assets.

Keynote, PowerPoint, PDF, and emergency bundle outputs should be published as release artifacts rather than committed. Public-release checks live in [PUBLICATION_REVIEW.md](PUBLICATION_REVIEW.md).

## License

Source code is licensed under the MIT license in [LICENSE](LICENSE).

Non-code assets are not covered by the MIT license unless explicitly stated.
See [ASSET_RIGHTS.md](ASSET_RIGHTS.md) before reusing figures, stimuli, data,
videos, presenter notes, or generated presentation exports.
