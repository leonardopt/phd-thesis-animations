# Asset Policy

This repository uses three asset categories:

- tracked public source assets that are part of the published repo
- synced local assets that are required for some scenes but intentionally not tracked
- generated local outputs and intermediate specs that are ignored by Git

## Tracked In Git

Tracked assets in this repository are limited to items that are small enough and central enough to the public source tree to justify keeping them in Git:

- hand-authored presentation figures and slide assets under `assets/images/` and `assets/slides/`
- small copied reference files needed by the public scene source
- compact binary inputs that live scenes still reference directly, such as the retained Study 2 NIfTI overlays and `assets/images/fish_video.mp4`
- public manifests and presenter-note inputs such as `assets/presentation_deck.toml`, `assets/presentation_frame_overrides.toml`, and `assets/presenter_notes.md`

The pre-publication cleanup removed generated outputs, native-slide spec dumps, and the oversized tracked files that were not part of the live source boundary.

## Synced Locally, Not Tracked

These asset groups are populated through `scripts/sync_external_assets.py` and are intentionally left out of Git history:

- `small`
  - Study 1 fish anchor image
  - Study 1 LPIPS CSVs
  - Study 1 stimulus-task showcase subset
  - Study 1 memory-task example images and `stimuli_info.csv`
  - Study 2 task/training stimulus subset
- `study1-exemplars`
  - exemplar image folders used by Study 1 Step 2, Step 3, and showcase scenes
- `study1-interpolations`
  - fish interpolation frames used by Study 1 Step 4 and Step 5
- `study1-reordered`
  - reordered stimulus strips used by Study 1 Stage 2 and Stage 3

## Generated Locally, Ignored

The following paths are generated locally and should never be committed:

- `media/`
- `assets/native_specs/`
- `assets/presentation_hybrid_deck.toml`
- `assets/hybrid_wtext_deck.toml`
- `assets/presentation_hybrid_native_deck.toml`
- `assets/presentation_hybrid_text_deck.toml`
- exported `.key`, `.pptx`, and fallback `.pdf` deliverables at the repository root

Final presentation exports belong in GitHub Releases or another artifact store, not in Git history.

## Source Repos Expected By The Sync Script

- `~/similarity-judgment-task-analysis`
- `~/stable-visual-memory-design`
- `~/sd-wltm-fmri-experiment`
- `~/visual-memory-task-analysis`

If your local paths differ, either edit the sync script or point the runtime to custom locations through `.env`.

## Redistribution Status

This repository does not yet apply one blanket license to all non-code assets. Before reusing tracked figures or copied reference material outside this repository, verify the origin and redistribution rights for that specific asset. If an asset later turns out to be unsuitable for public redistribution, it should move from the tracked set into the sync-only workflow.
