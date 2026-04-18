# Asset Provenance

This repository mixes three asset types:

- tracked presentation assets created for this repo
- tracked small reference files copied in from sibling analysis repos
- large sync targets populated locally via `scripts/sync_external_assets.py`

## Sync Groups

- `small`
  - Study 1 fish anchor image
  - Study 1 LPIPS CSVs
  - Study 1 stimulus-task showcase subset
  - Study 1 memory-task example images and `stimuli_info.csv`
  - Study 2 task/training stimulus subset
  - `test_svg.py` reference SVGs
- `study1-exemplars`
  - exemplar image folders used by Study 1 Step 2, Step 3, and showcase scenes
- `study1-interpolations`
  - fish interpolation frames used by Study 1 Step 4 and Step 5
- `study1-reordered`
  - reordered stimulus strips used by Study 1 Stage 2 and Stage 3

## Source Repos Expected By The Sync Script

- `~/similarity-judgment-task-analysis`
- `~/stable-visual-memory-design`
- `~/sd-wltm-fmri-experiment`
- `~/visual-memory-task-analysis`

If your local paths differ, either edit the script or point the runtime to custom locations through `.env`.
