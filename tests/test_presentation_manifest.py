from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "presentation_manifest.py"
SPEC = importlib.util.spec_from_file_location("presentation_manifest", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
presentation_manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(presentation_manifest)


class PresentationManifestAliasTests(unittest.TestCase):
    def test_old_camel_case_presenter_note_targets_match_current_sectioned_stems(self) -> None:
        old_target = "media/videos/04_study2/{{quality_dir}}/03c_Study2DecodingOverviewC.mp4"
        current_path = (
            REPO_ROOT
            / "media"
            / "videos"
            / "04_study2"
            / "480p15"
            / "sections"
            / "004_study2_decoding_overview_c.mp4"
        )

        note_aliases = presentation_manifest.presenter_note_aliases(
            old_target,
            REPO_ROOT,
            "480p15",
        )
        media_aliases = presentation_manifest.media_path_aliases(
            current_path,
            REPO_ROOT,
            "480p15",
        )

        self.assertTrue(note_aliases & media_aliases)

    def test_canonical_media_stem_normalizes_old_and_current_names(self) -> None:
        self.assertEqual(
            presentation_manifest.canonical_media_stem("01_Study1Stage1Step1a"),
            "study_1_stage_1_step_1a",
        )
        self.assertEqual(
            presentation_manifest.canonical_media_stem("000_study1_stage1_step1a"),
            "study_1_stage_1_step_1a",
        )

    def test_validate_media_slide_rejects_non_section_video_path(self) -> None:
        with self.assertRaisesRegex(
            SystemExit,
            "deck videos must point at numbered section clips under a /sections/ directory",
        ):
            presentation_manifest.validate_media_slide(
                "video",
                {"path": "media/videos/04_study2/480p15/study2.mp4"},
                REPO_ROOT,
                "480p15",
            )

    def test_current_manifest_video_slides_all_use_sections(self) -> None:
        manifest = presentation_manifest.load_manifest(
            REPO_ROOT / "assets" / "presentation_deck.toml"
        )
        expanded = presentation_manifest.expand_slides(
            manifest["slide"],
            REPO_ROOT,
            "480p15",
        )

        for slide in expanded:
            if slide["type"] != "video":
                continue
            self.assertTrue(
                presentation_manifest.is_numbered_section_video_path(Path(slide["path"])),
                slide["path"],
            )


if __name__ == "__main__":
    unittest.main()
