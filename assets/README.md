# Asset Policy

This repository uses three asset categories:

- tracked restricted source assets that are part of the published repo
- synced local assets that are required for some scenes but intentionally not tracked
- generated local outputs and intermediate specs that are ignored by Git

## Tracked In Git

Tracked assets in this repository are limited to items that are small enough and central enough to the public source tree to justify keeping them in Git. They are not covered by the MIT code license unless a file or directory explicitly says otherwise.

- hand-authored presentation figures and slide assets under `assets/images/` and `assets/slides/`
- normalized shared image assets under `assets/images/shared/`, anatomy assets under `assets/images/anatomy/`, and Study 1 assets under `assets/images/study1/stage1/`, `assets/images/study1/stage2/`, and `assets/images/study1/stage3/`
- compact binary inputs that live scenes still reference directly, such as the retained Study 2 NIfTI overlays and `assets/videos/fish_video.mp4`
- public-source manifests and presenter-note inputs such as `assets/presentation_deck.toml`, `assets/presentation_frame_overrides.toml`, and `assets/presenter_notes.md`

The pre-publication cleanup removed generated outputs, copied literature/reference screenshots, and oversized tracked files that were not part of the live source boundary. Intro literature examples now render from generated Manim schematic cards rather than copied paper figures.

## Sync Groups

These asset groups are populated through `scripts/sync_external_assets.py`:

- `small`
  - refreshes compact restricted assets that are tracked in Git
  - Study 1 fish anchor image
  - Study 1 LPIPS CSVs
  - Study 1 stimulus-task showcase subset
  - Study 1 memory-task example images and `stimuli_info.csv`
  - Study 2 task/training stimulus subset
- `study1-exemplars`
  - local-only, ignored by Git
  - exemplar image folders used by Study 1 Step 2, Step 3, and showcase scenes
- `study1-interpolations`
  - local-only, ignored by Git
  - fish interpolation frames used by Study 1 Step 4 and Step 5
- `study1-reordered`
  - local-only, ignored by Git
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

This repository does not apply one blanket open license to non-code assets. Before reusing tracked figures, stimuli, videos, data, or presenter notes outside this repository, verify the origin and redistribution rights for that specific asset. See the top-level `ASSET_RIGHTS.md`.

Copied paper or dataset screenshots should not be added to the tracked tree; prefer generated schematic cards in scene code or the sync-only workflow for local-only material.
