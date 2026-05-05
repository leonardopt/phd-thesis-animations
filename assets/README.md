# Asset Policy

This repository uses three asset categories:

- tracked public source assets that are part of the published repo
- synced local assets that are required for some scenes but intentionally not tracked
- generated local outputs and intermediate specs that are ignored by Git

## Tracked In Git

Tracked assets in this repository are limited to items that are small enough and central enough to the public source tree to justify keeping them in Git:

- hand-authored presentation figures and slide assets under `assets/images/` and `assets/slides/`
- normalized shared image assets under `assets/images/shared/`, anatomy assets under `assets/images/anatomy/`, and Study 1 stage figures under `assets/images/study1/stage*/`
- compact binary inputs that live scenes still reference directly, such as the retained Study 2 NIfTI overlays and `assets/videos/fish_video.mp4`
- public manifests and presenter-note inputs such as `assets/presentation_deck.toml`, `assets/presentation_frame_overrides.toml`, and `assets/presenter_notes.md`

The pre-publication cleanup removed generated outputs, copied reference-image screenshots that were not required for rendering, and oversized tracked files that were not part of the live source boundary.

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
- exported `.key`, `.pptx`, and fallback `.pdf` deliverables at the repository root

Final presentation exports belong in GitHub Releases or another artifact store, not in Git history.

## Source Repos Expected By The Sync Script

By default, `scripts/sync_external_assets.py` looks for source repositories under the user's home directory:

- `~/similarity-judgment-task-analysis`
- `~/stable-visual-memory-design`
- `~/sd-wltm-fmri-experiment`
- `~/visual-memory-task-analysis`

If your local paths differ, set these variables in `.env`:

- `SIMILARITY_JUDGMENT_TASK_ANALYSIS_ROOT`
- `STABLE_VISUAL_MEMORY_DESIGN_ROOT`
- `SD_WLTM_FMRI_EXPERIMENT_ROOT`
- `VISUAL_MEMORY_TASK_ANALYSIS_ROOT`

## Redistribution Status

This repository does not yet apply one blanket license to all non-code assets. Before reusing tracked figures or copied reference material outside this repository, verify the origin and redistribution rights for that specific asset. Copied paper or dataset screenshots should not be added to the tracked tree; prefer generated schematic cards in scene code or the sync-only workflow for local-only material.
