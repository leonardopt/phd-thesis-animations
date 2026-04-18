# Thesis Defence Animations

Manim scenes and supporting assets for the thesis defence talk.

## What Is In Here

- `scenes/study1.py`: consolidated Study 1 entrypoint
- `scenes/study2.py`: consolidated Study 2 entrypoint
- `scenes/intro.py`: consolidated introduction entrypoint
- `scenes/old/`: legacy source modules still imported by the consolidated entrypoints
- `assets/`: tracked figures plus repo-local sync targets for external source assets
- `render_study1.sh`, `render_study2.sh`, `render_all.sh`: narrative-order render helpers

Generated Manim output stays under `media/` and is ignored from git.

## Requirements

- Python 3.12+
- `uv`
- a working LaTeX installation for Manim text rendering

## Setup

Install the environment:

```bash
uv sync
```

Sync the small repo-local asset copies used by the portable defaults:

```bash
uv run python scripts/sync_external_assets.py --groups small
```

For full Study 1 reproducibility from sibling local repos, sync the heavier asset groups as well:

```bash
uv run python scripts/sync_external_assets.py --all
```

If you want to override any asset locations, copy `.env.example` to `.env` and edit the paths there. The defaults in `.env.example` assume repo-local copies under `assets/`.

## Rendering

Common quality flags:

- `-ql`: low quality, writes videos to `480p15/`
- `-qm`: medium quality, writes videos to `720p30/`
- `-qh`: high quality, writes videos to `1080p60/`
- `-qk`: 4K quality, writes videos to `2160p60/`

Render all Study 1 scenes in narrative order:

```bash
./render_study1.sh -qh
```

Runs the consolidated Study 1 deck sequence and writes outputs under `media/videos/study1/<quality>/`.

Render all Study 2 scenes in narrative order:

```bash
./render_study2.sh -qh
```

Runs the consolidated Study 2 deck sequence and writes outputs under `media/videos/study2/<quality>/`.

Render every top-level render script with one quality setting:

```bash
./render_all.sh -qh
```

Runs the full talk sequence across all top-level render helpers with one shared quality flag.

Render a single scene directly:

```bash
uv run manim scenes/study1.py Study1Step1a -qh
uv run manim scenes/study2.py Study2ExperimentalDesign -qh
uv run manim scenes/intro.py -a -qh
```

Use this when you only want to rerender one scene or one file.

## Presentation Build

The Keynote deck is driven by [assets/presentation_deck.toml](/Users/leonardo/phd-thesis-animations/assets/presentation_deck.toml). Add `title`, `section`, `text`, `image`, `pdf`, `video`, or `video_sequence` entries there to control slide order.

Build a Keynote deck from the manifest:

```bash
osascript /Users/leonardo/phd-thesis-animations/scripts/create_keynote_presentation.applescript
```

By default this uses the `480p15/` video folders.

Build the same deck against a different render quality:

```bash
osascript /Users/leonardo/phd-thesis-animations/scripts/create_keynote_presentation.applescript -ql
osascript /Users/leonardo/phd-thesis-animations/scripts/create_keynote_presentation.applescript -qh
osascript /Users/leonardo/phd-thesis-animations/scripts/create_keynote_presentation.applescript --quality-folder 1080p60
```

`-ql`, `-qm`, `-qh`, and `-qk` map to the standard Manim output folders. The deck build will fail cleanly if the corresponding video folder does not exist yet.

## Renumbering

Use a script, not ad-hoc find/replace and not an AI-only instruction note. The numbered source of truth lives in `scenes/study1.py` and `scenes/study2.py`, while `media/` outputs and reports are derived artifacts.

Dry-run a renumber after removing one scene from the numbered sequence:

```bash
python3 scripts/renumber_scene_order.py study1 --remove-class Study1Stage3MemoryExpDesignA
```

Write the renumbered mapping back to the scene file:

```bash
python3 scripts/renumber_scene_order.py study1 --remove-class Study1Stage3MemoryExpDesignA --apply
```

Then rerender the affected study and rebuild any backup PDFs or bundles that depend on the old filenames.

`assets/presentation_frame_overrides.toml` supports scene-class keys such as `["Study1Step2Showcase"]`, which survive renumbering better than numbered video stems.

## Asset Notes

- Small cross-repo reference files are copied into tracked repo-local locations by `scripts/sync_external_assets.py --groups small`.
- Large Study 1 source assets such as `assets/images/stimuli_reordered`, `assets/images/study1/exemplar_images`, and `assets/images/study1/fish_interpolations` are treated as sync targets rather than committed defaults.
- Historical Stage 2 and Stage 3 figure assets live under `assets/images/study1_stage2` and `assets/images/study1_stage3`.

## Repository Hygiene

- `media/` is generated output and cache material.
- `scenes/old/__pycache__/` is ignored, but the Python source files in `scenes/old/` are part of the project.
- `.env` is optional and ignored.
