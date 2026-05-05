# Asset Rights

The source code in this repository is available under the MIT license in
`LICENSE`. Non-code assets are handled separately.

## Restricted Assets

Unless a specific file or directory states otherwise, the MIT license does not
grant reuse rights for:

- `assets/`
- generated media under `media/`
- exported `.key`, `.pptx`, `.pdf`, and video deliverables
- copied figures, stimulus examples, NIfTI overlays, presenter notes, and data
  files used to reproduce the thesis defence presentation

These files are included, when tracked, to make the presentation source
inspectable and renderable. Do not redistribute or reuse them outside this
repository without checking the original source and rights for that specific
asset.

## Publication Boundary

Copied literature screenshots and paper-derived thumbnails should not be
tracked. The public intro scenes use Manim-generated schematic cards for cited
literature examples instead of copied figures.

Large or unclear-rights inputs should stay local-only and be restored through
the sync workflow described in `assets/README.md`.

## Adding Assets

Before adding a new asset to Git:

- record its source and license or permission status
- prefer generated schematic visuals over copied paper screenshots
- keep large or restricted inputs in an ignored sync target when possible
- publish final videos, decks, and PDFs as release artifacts, not repository
  history
