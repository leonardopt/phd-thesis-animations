# Publication Review

Status: blocker-first public GitHub cleanup completed with restricted assets.

## Go/No-Go Checklist

- [x] Source code has a top-level MIT license.
- [x] Non-code assets are excluded from the MIT grant in `ASSET_RIGHTS.md`.
- [x] Generated outputs and local render products remain ignored.
- [x] Copied intro literature screenshots were removed from the tracked tree.
- [x] Intro literature visuals now render as generated Manim schematics.
- [x] Manim starts without the color-configuration warning from `manim.cfg`.
- [x] Full deck validation is documented as a release-artifact check because it
  depends on local rendered media under `media/`.

## Known Local Dependencies

- Python 3.12+ and `uv`
- System Manim dependencies, including a LaTeX installation for `Tex`
- `ffmpeg` and `ffprobe` for video reports, backup PDFs, and preflight checks
- macOS with Keynote for `scripts/create_keynote_presentation.applescript`
- Optional external source repositories configured through `.env` for the
  sync-only asset groups

## Release Artifact Checks

Before publishing a release with rendered outputs, render the required section
clips and run:

```bash
uv run python scripts/presentation_manifest.py --manifest assets/presentation_deck.toml --project-root . --quality-dir auto
uv run python scripts/presentation_preflight.py --presentation-file /path/to/deck.key
```

The manifest/preflight checks are not expected to pass in a fresh source clone
until the referenced videos under `media/videos/**/sections/` have been
rendered or restored locally.
