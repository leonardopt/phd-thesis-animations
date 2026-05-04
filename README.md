# Thesis Defence Animations

Source repository for my PhD defence presentation built with [Manim](https://www.manim.community/). The project contains the scene code and curated assets used to produce videos and keynote slides. The talk was organised into an introduction, methods, two main study sections, a conclusion, and supplementary material.


## What This Repository Contains

- `scenes/`: production Manim scenes and clip wrappers
- `assets/`: tracked figures, manifests, presenter notes, and documented sync targets
- `scripts/`: deck assembly, packaging, and project tooling

Supporting project configuration lives at the repository root in `pyproject.toml`, `uv.lock`, `manim.cfg`, and `.env.example`.

## Quick Start

Use Python 3.12+ with `uv`.

```bash
uv sync
```

Copy `.env.example` to `.env` only if you need to override default local asset paths.

## Asset Model

The public repository keeps the scene source self-contained where possible, but some larger study inputs are intentionally not committed.

- Tracked in Git: scene-adjacent figures, manifests, presenter notes, and compact public assets
- Synced locally: larger study inputs restored through `scripts/sync_external_assets.py`
- Generated locally: `media/`, Keynote exports, PDFs, reports, and other disposable build products

For provenance notes and sync groups, see [assets/README.md](assets/README.md).

To populate the local-only sync targets:

```bash
uv run python scripts/sync_external_assets.py --groups small
uv run python scripts/sync_external_assets.py --all
```

Use `--groups small` for the normal portable setup. Use `--all` only when you need the larger Study 1 source assets.

## Rendering Clips

The documented render path is clip-based. Use `scenes/clips.py` to render production clips directly into the numbered `media/videos/**/sections/` folders with the expected filenames.

Quality flags:

- `-ql`: `480p15`
- `-qm`: `720p30`
- `-qh`: `1080p60`
- `-qk`: `2160p60`

Examples:

```bash
uv run manim scenes/clips.py IntroCognitiveProblemA -qh
uv run manim scenes/clips.py Study1Stage1Step2 -qh
uv run manim scenes/clips.py Study2CrossSessionDecodingSetup -qh
uv run manim scenes/clips.py ConclusionApproach -qh
uv run manim scenes/clips.py SupplementaryIntroResearchQuestion1 -qh
```

Supplementary wrappers that reuse intro or study-1 scene classes are prefixed
with `Supplementary` so each clip name resolves to exactly one output path.

The underlying production scene modules are:

- `scenes/intro.py`
- `scenes/methods.py`
- `scenes/study1.py`
- `scenes/study2.py`
- `scenes/conclusion.py`
- `scenes/supplementary.py`

## Building The Deck

After the required section clips exist locally, build the Keynote deck on macOS with Keynote installed:

```bash
osascript scripts/create_keynote_presentation.applescript
osascript scripts/create_keynote_presentation.applescript --quality-folder auto
osascript scripts/create_keynote_presentation.applescript -qh
osascript scripts/create_keynote_presentation.applescript --quality-folder 1080p60
```

The deck builder reads `assets/presentation_deck.toml` and resolves numbered section clips under `media/videos/**/sections/`. Presenter notes can live in `assets/presenter_notes.md`, using repo-relative media targets such as `## media/videos/03_study1/{{quality_dir}}/sections/000_study1_scene.mp4`.

Related local-only helper commands:

```bash
uv run python scripts/build_static_rescue_deck.py
uv run python scripts/presentation_preflight.py --presentation-file /path/to/deck.key
uv run python scripts/package_emergency_bundle.py --presentation-file /path/to/deck.key
```

## Generated Outputs

`media/` is disposable local build output and is ignored by Git. It holds rendered clips, stills, reports, fallback bundles, and Keynote exports.

Final `.key`, `.pptx`, and exported `.pdf` deliverables should be published as release artifacts, not committed into repository history.

## License Status

This repository does not yet ship a top-level open-source license while the asset-rights audit is still in progress. Treat code and non-code assets separately until that work is complete.
