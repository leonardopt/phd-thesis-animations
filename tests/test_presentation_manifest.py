from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "presentation_manifest.py"
SPEC = importlib.util.spec_from_file_location("presentation_manifest", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
presentation_manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(presentation_manifest)


def _slide_media_references(slide: dict) -> list[str]:
    values: list[str] = []
    for key in ("path", "glob"):
        value = slide.get(key)
        if value:
            values.append(value)
    for key in ("paths", "globs"):
        values.extend(slide.get(key, []))
    return values


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
        with tempfile.TemporaryDirectory() as tmp_dir:
            invalid_video = Path(tmp_dir) / "study2.mp4"
            invalid_video.write_bytes(b"")
            with self.assertRaisesRegex(
                SystemExit,
                "deck videos must point at numbered section clips under a /sections/ directory",
            ):
                presentation_manifest.validate_media_slide(
                    "video",
                    {"path": str(invalid_video)},
                    REPO_ROOT,
                    "480p15",
                )

    def test_current_manifest_video_slides_all_use_sections(self) -> None:
        manifest = presentation_manifest.load_manifest(
            REPO_ROOT / "assets" / "presentation_deck.toml"
        )
        for slide in manifest["slide"]:
            if slide.get("type") not in {"video", "video_sequence"}:
                continue
            for reference in _slide_media_references(slide):
                self.assertIn("/sections/", reference, reference)
                self.assertTrue(reference.endswith(".mp4"), reference)
                self.assertNotIn("_autocreated.mp4", reference, reference)

    def test_auto_quality_mode_uses_existing_mixed_section_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            intro_path = (
                project_root
                / "media"
                / "videos"
                / "01_intro"
                / "1080p60"
                / "sections"
                / "000_intro.mp4"
            )
            study1_path = (
                project_root
                / "media"
                / "videos"
                / "03_study1"
                / "480p15"
                / "sections"
                / "000_study1.mp4"
            )
            intro_path.parent.mkdir(parents=True, exist_ok=True)
            study1_path.parent.mkdir(parents=True, exist_ok=True)
            intro_path.write_bytes(b"intro")
            study1_path.write_bytes(b"study1")

            manifest_path = project_root / "deck.toml"
            manifest_path.write_text(
                """
[[slide]]
type = "video_sequence"
glob = "media/videos/01_intro/1080p60/sections/*.mp4"

[[slide]]
type = "video_sequence"
glob = "media/videos/03_study1/480p15/sections/*.mp4"
""".strip(),
                encoding="utf-8",
            )

            manifest = presentation_manifest.load_manifest(manifest_path)
            expanded = presentation_manifest.expand_slides(
                manifest["slide"],
                project_root,
                "auto",
            )

        video_paths = [slide["path"] for slide in expanded if slide["type"] == "video"]
        self.assertIn(str(intro_path.resolve()), video_paths)
        self.assertIn(str(study1_path.resolve()), video_paths)

    def test_explicit_quality_override_rewrites_mixed_manifest_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            high_path = (
                project_root
                / "media"
                / "videos"
                / "01_intro"
                / "1080p60"
                / "sections"
                / "001_intro.mp4"
            )
            qk_path = (
                project_root
                / "media"
                / "videos"
                / "01_intro"
                / "2160p60"
                / "sections"
                / "001_intro.mp4"
            )
            high_path.parent.mkdir(parents=True, exist_ok=True)
            qk_path.parent.mkdir(parents=True, exist_ok=True)
            high_path.write_bytes(b"high")
            qk_path.write_bytes(b"qk")

            resolved = presentation_manifest.resolve_media_path(
                "media/videos/01_intro/1080p60/sections/001_intro.mp4",
                project_root,
                "2160p60",
                "video",
            )

        self.assertEqual(resolved, qk_path.resolve())

    def test_study1_memory_intro_clips_live_only_in_supplementary(self) -> None:
        manifest = presentation_manifest.load_manifest(
            REPO_ROOT / "assets" / "presentation_deck.toml"
        )
        slides = manifest["slide"]

        study2_index = next(
            index
            for index, slide in enumerate(slides)
            if slide["type"] == "section" and slide["title"].endswith("Study 2")
        )
        acknowledgments_index = next(
            index
            for index, slide in enumerate(slides)
            if slide["type"] == "text" and slide["title"] == "Acknowledgments"
        )
        supplementary_index = next(
            index
            for index, slide in enumerate(slides)
            if slide["type"] == "section" and slide["title"].endswith("Supplementary Slides")
        )
        study1_memory_results_slide = next(
            slide
            for slide in slides
            if slide.get("type") == "video_sequence"
            and slide.get("paths")
            and any(
                path.endswith("017_study1_stage3_memory_exp_design.mp4")
                for path in slide["paths"]
            )
        )
        supplementary_slide = next(
            slide
            for slide in slides
            if slide.get("type") == "video_sequence"
            and slide.get("paths")
            and any("/06_supplementary/" in path for path in slide["paths"])
        )
        study1_memory_results = [
            Path(path).stem for path in study1_memory_results_slide["paths"]
        ]
        supplementary_stems = [
            Path(path).stem for path in supplementary_slide["paths"]
        ]
        supplementary_intro_stems = {
            stem for stem in supplementary_stems if "study1_stage3_memory_intro" in stem
        }
        nonsupplementary_intro_stems = {
            Path(path).stem
            for slide in slides
            if slide is not supplementary_slide
            for path in _slide_media_references(slide)
            if "study1_stage3_memory_intro" in Path(path).stem
        }

        self.assertEqual(
            supplementary_intro_stems,
            {
                "003_study1_stage3_memory_intro_a",
                "004_study1_stage3_memory_intro_b",
                "005_study1_stage3_memory_intro_c",
                "006_study1_stage3_memory_intro_d",
                "007_study1_stage3_memory_intro_e",
            },
        )
        self.assertLess(study2_index, acknowledgments_index)
        self.assertLess(acknowledgments_index, supplementary_index)
        self.assertEqual(
            study1_memory_results,
            [
                "017_study1_stage3_memory_exp_design",
                "018_study1_stage3_memory_repetition_explainer",
                "019_study1_stage3_memory_exp_results",
            ],
        )
        self.assertTrue(
            all("/06_supplementary/" in path for path in supplementary_slide["paths"])
        )
        self.assertEqual(nonsupplementary_intro_stems, set())


if __name__ == "__main__":
    unittest.main()
