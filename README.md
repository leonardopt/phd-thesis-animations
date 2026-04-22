# Thesis Defence Animations

This repository contains the Manim scenes, presentation assets, and build helpers used to produce animated material for my PhD defence talk. It includes the tooling needed to assemble a presentation deck, generate static fallbacks, and package backups for live delivery.

The project is organized around my thesis chapters, with a set of scripts that turn rendered clips into presentation-ready artifacts. The result is a reproducible workflow from scene source to numbered videos, Keynote decks, backup PDFs, and emergency bundles.

At a glance:

- Render the Study 1 and Study 2 animation sequences in numbered narrative order.
- Build a Keynote deck from a manifest instead of placing videos by hand.
- Generate static rescue PDFs, frame screeners, and emergency presentation bundles.
- Keep local asset sync and scene numbering reproducible across rerenders.

## Overview

The core of the repository is a set of Manim entrypoints: `scenes/study1.py`, `scenes/study2.py`, and `scenes/intro.py`. `study1.py` and `study2.py` define the numbered public scene sequences used for rendering; `intro.py` is a scaffold for future introduction scenes. Together they provide the stable public rendering interface for the two study pipelines and the surrounding presentation tooling.

Downstream scripts assume that rendered clips follow a consistent numbered naming scheme and live under numbered section folders such as `media/videos/01_intro/<quality>/`, `media/videos/02_methods/<quality>/`, `media/videos/03_study1/<quality>/`, `media/videos/04_study2/<quality>/`, and `media/videos/05_conclusion/<quality>/`. That convention is then reused by the presentation builder, backup generators, preflight checks, and bundle-packaging helpers. Assets follow a similar model: some are tracked directly in the repo, while larger study inputs are synced locally into expected locations under `assets/`.

## Repository Structure

| Area | Purpose | Key Paths |
|---|---|---|
| Scene source | Public scene entrypoints and shared scene code | `scenes/study1.py`, `scenes/study2.py`, `scenes/intro.py`, `scenes/utils.py` |
| Assets | Tracked presentation figures, repo-local sync targets, and presentation manifests | `assets/`, `assets/presentation_deck.toml`, `assets/presentation_frame_overrides.toml` |
| Tooling | Render helpers, deck assembly, backup generation, preflight, packaging, renumbering | `render_01_intro.sh`, `render_02_methods.sh`, `render_03_study1.sh`, `render_04_study2.sh`, `render_05_conclusion.sh`, `render_all.sh`, `render_single_video.sh`, `scripts/` |
| Generated outputs | Rendered videos, stills, PDFs, reports, and Keynote exports | `media/videos/`, `media/images/`, `media/pdfs/`, `media/reports/`, `media/keynote/` |

Supporting configuration lives at the repository root in `pyproject.toml`, `uv.lock`, `manim.cfg`, and `.env.example`.

## Core Workflows

The main workflows in this repository are:

- Environment setup: install the Python environment and ensure the local machine has the runtime dependencies required by Manim and, optionally, Keynote.
- Asset sync: populate the repo-local asset locations that the scenes expect, either with the small tracked/copied groups or with the larger study-specific sync targets as needed.
- Rendering: render Study 1, Study 2, or every top-level render helper, or rerender a single scene during iteration.
- Presentation build: assemble a Keynote deck from `assets/presentation_deck.toml`, using the numbered rendered videos as slide media.
- Backup and recovery: generate static rescue decks, screeners, preflight reports, and transport bundles for live presentation fallback.

The next section gives the main operator path for each of those workflows.

## Running the Project

### Prerequisites

Use this repository with Python 3.12+, `uv`, and a working LaTeX installation for Manim text rendering. Building a Keynote deck also requires macOS with Keynote installed.

### Environment Setup

Use this once on a fresh checkout to create the local Python environment and install pinned dependencies.

```bash
uv sync
```

### Asset Sync

Use the small sync group for the normal portable setup. Use `--all` only when you need the larger Study 1 asset sets that are intentionally not committed into the repository.

```bash
uv run python scripts/sync_external_assets.py --groups small
uv run python scripts/sync_external_assets.py --all
```

### Quality Flags

Use the same Manim quality flags across the render helpers and the Keynote builder:

- `-ql`: low quality, outputs to `480p15/`
- `-qm`: medium quality, outputs to `720p30/`
- `-qh`: high quality, outputs to `1080p60/`
- `-qk`: 4K quality, outputs to `2160p60/`

### Render Sequences

Use these when you want the numbered study sequences rather than one-off scene renders.

```bash
./render_01_intro.sh -qh
./render_02_methods.sh -qh
./render_03_study1.sh -qh
./render_04_study2.sh -qh
./render_05_conclusion.sh -qh
./render_all.sh -qh
```

`render_all.sh` runs every top-level `render_*.sh` helper in the repository. If you specifically want one concatenated presentation video after rendering both studies, use:

```bash
./render_single_video.sh -qh
```

### Render a Single Scene

Use direct `manim` commands during development when you only want to rerender one scene instead of a full numbered sequence.

```bash
uv run manim scenes/study1.py Study1Stage1Step1a -qh
uv run manim scenes/study2.py Study2ExperimentalDesign -qh
```

`scenes/intro.py` exists as the public introduction entrypoint, but it currently has no exported scenes.

### Build the Presentation

Use the Keynote builder when the rendered videos are ready and you want a deck assembled from the manifest in `assets/presentation_deck.toml`.

```bash
osascript scripts/create_keynote_presentation.applescript
osascript scripts/create_keynote_presentation.applescript -qh
osascript scripts/create_keynote_presentation.applescript --quality-folder 1080p60
```

Presenter notes for media slides can live in `assets/presenter_notes.md`. The
builder reads that file through `presenter_notes_path` in the deck manifest and
matches each `## media-target` section onto the corresponding rendered slide.
Use a repo-relative templated path such as
`## media/videos/03_study1/{{quality_dir}}/01_Study1Scene.mp4` when you want the
same notes to work across qualities.

### Optional Backup and Recovery Commands

Use these when you want a static fallback deck, a readiness check, or a portable presentation bundle.

```bash
uv run python scripts/build_static_rescue_deck.py
uv run python scripts/presentation_preflight.py --presentation-file /path/to/deck.key
uv run python scripts/package_emergency_bundle.py --presentation-file /path/to/deck.key
```

## Outputs and Conventions

Rendered videos are written as numbered section clips under paths such as `media/videos/03_study1/<quality>/sections/000_*.mp4`. The presentation builder, fallback PDF scripts, and backup tooling read only those numbered section clips and ignore stray files outside that convention. Other generated artifacts are grouped alongside them in matching numbered directories under `media/images/`, plus `media/pdfs/`, `media/reports/`, and `media/keynote/`.

The numbered output convention is intentional. The unified render scenes emit section clips into filenames such as `sections/000_section_name.mp4`, and the presentation and backup tooling assumes that convention rather than trying to infer order from ad hoc filenames.

The Keynote builder is manifest-driven. `assets/presentation_deck.toml` defines the slide sequence and can mix text slides, static image/PDF slides, and video sequences sourced from the numbered render outputs. Deck-level presenter notes for media slides can be authored separately in `assets/presenter_notes.md` instead of being embedded into the TOML slide definitions.

The detailed current rendered order lives in [media/reports/presentation_video_order.md](media/reports/presentation_video_order.md). It is kept out of the main README on purpose so the landing page stays focused on structure and workflow rather than current build state.

## Additional Tools

- `scripts/export_last_frames_pdf.py`: build a last-frame backup PDF from rendered videos.
- `scripts/export_frame_screener_pdf.py`: build screener PDFs from stable frames rather than arbitrary timestamps.
- `scripts/presentation_preflight.py`: check that required videos and backup artifacts exist and can be opened.
- `scripts/package_emergency_bundle.py`: assemble a portable bundle containing videos, backup PDFs, and reports.
- `scripts/renumber_scene_order.py`: update numbered study ordering when scenes are removed or compacted.
- `assets/presentation_frame_overrides.toml`: store manual frame-pick overrides for static rescue deck generation.

## Reproducibility and Assets

This repository uses a mixed asset model. Small reference files and presentation assets are tracked directly in `assets/`, while larger study-specific inputs are expected to be synced locally into repo-local directories. That keeps the public repository usable without silently depending on machine-specific absolute paths while still avoiding large committed binary datasets where they are not appropriate.

Asset provenance, sync groups, and expected sibling source repositories are documented in [assets/README.md](assets/README.md). Start there if you need to understand where a local asset set comes from or why a particular folder is a sync target instead of a committed source directory.

Runtime defaults point to repo-local asset paths. If your local setup differs, copy `.env.example` to `.env` and override the relevant directories there. Generated output under `media/` should be treated as disposable build output: rerender or regenerate it rather than editing it by hand.
