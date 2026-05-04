# Thesis Defence Animations

This repository contains the Manim scene source, tracked presentation assets, and build helpers used to produce animated material for a PhD defence talk. It is published as a source-first repository: scene code, manifests, and curated small assets live here, while rendered videos, Keynote decks, PDFs, reports, and other build products are generated locally and kept out of Git.

## Supported Workflows

- Fresh source checkout and test run
- Optional local asset sync for larger study inputs
- Optional local clip rendering and macOS/Keynote deck assembly

## Repository Layout

| Area | Purpose |
|---|---|
| `scenes/` | Public Manim entrypoints and shared scene logic |
| `archive/` | Archived scene experiments kept out of the active source path |
| `assets/` | Tracked presentation figures, slide manifests, and documented sync targets |
| `docs/` | Planning notes and repo-local project documents that are not part of the public API |
| `scripts/` | Deck assembly, probes, packaging, and audit tooling |
| `tests/` | Source-only tests that do not require tracked render outputs |
| `media/` | Local-only generated output such as renders, reports, and deck exports |

Supporting configuration lives at the repository root in `pyproject.toml`, `uv.lock`, `manim.cfg`, and `.env.example`.

## 1. Fresh Checkout And Tests

Use Python 3.12+ with `uv`. Rendering also requires the native dependencies that Manim expects on your platform, and Keynote deck assembly additionally requires macOS with Keynote installed.

```bash
uv sync --group dev
uv run python -m pytest -q
```

Copy `.env.example` to `.env` only if you need to override the default repo-local asset paths.

## 2. Local Asset Sync (Optional)

The public repository keeps only the small tracked assets needed for the core scene source. Larger study inputs are synced locally when needed.

```bash
uv run python scripts/sync_external_assets.py --groups small
uv run python scripts/sync_external_assets.py --all
```

Use `--groups small` for the normal portable setup. Use `--all` only when you need the larger Study 1 sync targets that are intentionally not committed here.

Asset categories, provenance notes, and expected sibling repositories are documented in [assets/README.md](assets/README.md).

## 3. Clip Rendering And Deck Build (Optional)

### Quality flags

- `-ql`: low quality, outputs to `480p15/`
- `-qm`: medium quality, outputs to `720p30/`
- `-qh`: high quality, outputs to `1080p60/`
- `-qk`: 4K quality, outputs to `2160p60/`

### Render numbered section clips

```bash
uv run manim scenes/clips.py IntroCognitiveProblemA -qh
uv run manim scenes/clips.py Study1Stage1Step2 -qh
uv run manim scenes/clips.py Study2CrossSessionDecodingSetup -qh
uv run manim scenes/clips.py ConclusionResults -qh
```

`scenes/clips.py` re-exports the production clips and writes them directly into the numbered `media/videos/**/sections/` folders with the production filenames, so the rendered MP4 can be dropped into the deck workflow without any rename step.

The active production scene modules remain `scenes/intro.py`, `scenes/methods.py`, `scenes/study1.py`, `scenes/study2.py`, `scenes/conclusion.py`, and `scenes/supplementary.py`. Archived prototypes live under `archive/scenes/`.

### Build the Keynote deck

Use the Keynote builder after the required section clips exist locally:

```bash
osascript scripts/create_keynote_presentation.applescript
osascript scripts/create_keynote_presentation.applescript --quality-folder auto
osascript scripts/create_keynote_presentation.applescript -qh
osascript scripts/create_keynote_presentation.applescript --quality-folder 1080p60
```

The deck builder reads `assets/presentation_deck.toml` and resolves only numbered section clips under `media/videos/**/sections/`. Presenter notes can live in `assets/presenter_notes.md`, using repo-relative media targets such as `## media/videos/03_study1/{{quality_dir}}/sections/000_study1_scene.mp4`.

### Optional fallback and packaging commands

```bash
uv run python scripts/build_static_rescue_deck.py
uv run python scripts/presentation_preflight.py --presentation-file /path/to/deck.key
uv run python scripts/package_emergency_bundle.py --presentation-file /path/to/deck.key
```

## Generated Outputs

- `media/` is disposable local build output. It holds renders, stills, reports, fallback bundles, and Keynote exports and is intentionally ignored by Git.
- `assets/native_specs/` and the hybrid deck manifest variants are generated local intermediates for native-slide experiments and are also ignored by Git.
- Final `.key`, `.pptx`, and exported `.pdf` deliverables should be published as GitHub Release assets, not committed into repository history.

## Asset Provenance And License Status

Asset provenance, sync groups, and redistribution notes live in [assets/README.md](assets/README.md). The repository does not yet ship a top-level open-source license while the asset-rights audit is still in progress, so treat code and non-code assets separately until that audit is complete.
