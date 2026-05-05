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

Tracked literature screenshots and paper-derived thumbnails are restricted
assets. They are included only to reproduce the existing defence presentation;
the MIT code license does not grant reuse rights for them.

New copied paper or dataset screenshots should not be added to the tracked tree
without recording their source and redistribution status. Prefer generated
schematic visuals in scene code or the sync-only workflow for local-only
material.

Large or unclear-rights inputs should stay local-only and be restored through
the sync workflow described in `assets/README.md`.

## Adding Assets

Before adding a new asset to Git:

- record its source and license or permission status
- prefer generated schematic visuals over copied paper screenshots
- keep large or restricted inputs in an ignored sync target when possible
- publish final videos, decks, and PDFs as release artifacts, not repository
  history
