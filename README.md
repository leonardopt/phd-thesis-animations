# Thesis Defence Animations

This repository contains the Manim scenes used for the presentation of my thesis defence.

The animations cover the main visual components of the talk, including:

- stimulus-set design for Study 1
- prompt-based exemplar generation
- LPIPS-based anchor and guide selection
- 3D SLERP interpolation in latent space
- supporting SDXL process diagrams, title slides, and hook animations

## Tech Stack

- Python 3.12+
- [Manim Community](https://www.manim.community/)
- `uv` for dependency and environment management
- a working LaTeX installation for text rendering

## Project Structure

- `scenes/`: main Manim scene files
- `assets/`: local image assets used by the scenes
- `.env.example`: template for required local dataset paths
- `media/`: generated Manim outputs and caches, ignored from git

## Setup

Install dependencies:

```bash
uv sync
```

Create a local environment file:

```bash
cp .env.example .env
```

Then edit `.env` so the path variables point to your local dataset and asset folders.

## Rendering Scenes

General form:

```bash
uv run manim scenes/<scene_file>.py <SceneClass> -ql
```

Examples:

```bash
uv run manim scenes/study1_step1.py Study1Step1a -ql
uv run manim scenes/study1_step3.py Study1Step3Part1 -qh
uv run manim scenes/study1_step4.py Study1Step4 -qh
```

## Notes

- local machine-specific configuration lives in `.env`, which is ignored from version control
- generated outputs under `media/` are ignored
- archival material under `scenes/old/` is not part of the active scene set
