Intro cognitive-problem assets
==============================

This folder is optional. The intro scenes render without any local media, but if
you want to swap in a concrete clip later, use this layout:

- `frames/`: extracted still frames for the main scene sequence
- `probes/`: optional comparison images shown after the interruption
- `repeat/`: optional repeated or prior-exposure images for the LTM slide
- `scene.mp4`: optional source video reference for your own bookkeeping

The scene code reads these paths by default:

- `assets/images/intro/frames`
- `assets/images/intro/probes`
- `assets/images/intro/repeat`
- `assets/images/intro/scene.mp4`

You can override them locally through `.env`:

- `INTRO_FRAME_DIR`
- `INTRO_PROBE_DIR`
- `INTRO_REPEAT_DIR`
- `INTRO_VIDEO_PATH`

Notes:

- The current infrastructure uses extracted frames for rendering.
- If `scene.mp4` exists but no frames are available, the slides show a labeled
  placeholder instead of trying to play raw video.
- Image formats supported by the loader are `png`, `jpg`, `jpeg`, and `webp`.
- Paper screenshots and literature thumbnails are intentionally not tracked in
  this folder. The public intro scenes use generated Manim schematic cards for
  cited literature examples.
