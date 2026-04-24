from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "presentation_hybrid_deck.py"
SPEC = importlib.util.spec_from_file_location("presentation_hybrid_deck", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
presentation_hybrid_deck = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = presentation_hybrid_deck
SPEC.loader.exec_module(presentation_hybrid_deck)


class PresentationHybridDeckTests(unittest.TestCase):
    def test_parse_report_extracts_hybrid_decisions(self) -> None:
        report_text = textwrap.dedent(
            """
            | Clip | Duration | Current animation | Decision | Why |
            | --- | --- | --- | --- | --- |
            | `000_intro_cognitive_problem` | 12.0s | Sequential reveal | Yes -> Keynote build | The build matters but can be recreated natively. |
            | `001_intro_hook` | 4.5s | Static frame hold | Yes -> Static still | No timing information is lost. |
            | `002_intro_interpolation` | 7.2s | Continuous interpolation | No -> Embedded video | The motion itself carries the explanation. |
            """
        ).strip()

        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "audit.md"
            report_path.write_text(report_text, encoding="utf-8")

            decisions = presentation_hybrid_deck.parse_report(report_path)

        self.assertEqual(
            decisions["000_intro_cognitive_problem"].disposition,
            presentation_hybrid_deck.HybridDisposition.KEYNOTE_BUILD,
        )
        self.assertEqual(
            decisions["001_intro_hook"].disposition,
            presentation_hybrid_deck.HybridDisposition.STATIC_STILL,
        )
        self.assertEqual(
            decisions["002_intro_interpolation"].disposition,
            presentation_hybrid_deck.HybridDisposition.EMBEDDED_VIDEO,
        )

    def test_parse_report_extracts_simple_config_decisions(self) -> None:
        report_text = textwrap.dedent(
            """
            # Video Disposition Config

            Variant: `strict_static_only`

            | clip | decision |
            | --- | --- |
            | `000_intro_cognitive_problem` | `video` |
            | `001_intro_classical_view` | `static` |
            | `999_omitted_clip` | `omit` |
            """
        ).strip()

        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "audit.md"
            report_path.write_text(report_text, encoding="utf-8")

            decisions = presentation_hybrid_deck.parse_report(report_path)

        self.assertEqual(
            decisions["000_intro_cognitive_problem"].disposition,
            presentation_hybrid_deck.HybridDisposition.EMBEDDED_VIDEO,
        )
        self.assertEqual(
            decisions["001_intro_classical_view"].disposition,
            presentation_hybrid_deck.HybridDisposition.STATIC_STILL,
        )
        self.assertEqual(
            decisions["999_omitted_clip"].disposition,
            presentation_hybrid_deck.HybridDisposition.OMIT,
        )

    def test_build_hybrid_slide_records_rewrites_video_slides(self) -> None:
        static_video_path = (
            REPO_ROOT / "media" / "videos" / "01_intro" / "1080p60" / "sections" / "001_static.mp4"
        )
        keynote_video_path = (
            REPO_ROOT / "media" / "videos" / "01_intro" / "1080p60" / "sections" / "002_keynote.mp4"
        )
        embedded_video_path = (
            REPO_ROOT / "media" / "videos" / "01_intro" / "1080p60" / "sections" / "003_embedded.mp4"
        )
        static_still_path = REPO_ROOT / "media" / "hybrid_stills" / "01_intro" / "001_static.png"
        keynote_still_path = REPO_ROOT / "media" / "hybrid_stills" / "01_intro" / "002_keynote.png"

        expanded_slides = [
            {
                "type": "title",
                "path": "",
                "title": "Deck title",
                "subtitle": "",
                "body": "",
                "notes": "",
            },
            {
                "type": "video",
                "path": str(static_video_path),
                "title": "",
                "subtitle": "",
                "body": "",
                "notes": "",
            },
            {
                "type": "video",
                "path": str(keynote_video_path),
                "title": "",
                "subtitle": "",
                "body": "",
                "notes": "Original presenter notes",
            },
            {
                "type": "video",
                "path": str(embedded_video_path),
                "title": "",
                "subtitle": "",
                "body": "",
                "notes": "",
            },
        ]
        decisions = {
            "001_static": presentation_hybrid_deck.AuditDecision(
                stem="001_static",
                disposition=presentation_hybrid_deck.HybridDisposition.STATIC_STILL,
                duration_text="1.0s",
                animation_summary="Static frame hold",
                why="No motion is needed.",
            ),
            "002_keynote": presentation_hybrid_deck.AuditDecision(
                stem="002_keynote",
                disposition=presentation_hybrid_deck.HybridDisposition.KEYNOTE_BUILD,
                duration_text="2.0s",
                animation_summary="Bullet reveal",
                why="Better as a native build.",
            ),
            "003_embedded": presentation_hybrid_deck.AuditDecision(
                stem="003_embedded",
                disposition=presentation_hybrid_deck.HybridDisposition.EMBEDDED_VIDEO,
                duration_text="3.0s",
                animation_summary="Continuous motion",
                why="Needs the original animation.",
            ),
        }
        extracted_stills = {
            static_video_path.resolve(): static_still_path.resolve(),
            keynote_video_path.resolve(): keynote_still_path.resolve(),
        }

        hybrid_slides, used_stems = presentation_hybrid_deck.build_hybrid_slide_records(
            expanded_slides,
            decisions,
            extracted_stills,
        )

        self.assertEqual(hybrid_slides[0]["type"], "title")
        self.assertEqual(hybrid_slides[1]["type"], "image")
        self.assertEqual(
            hybrid_slides[1]["path"],
            "media/hybrid_stills/01_intro/001_static.png",
        )
        self.assertEqual(hybrid_slides[2]["type"], "image")
        self.assertIn(
            presentation_hybrid_deck.HYBRID_BUILD_NOTE,
            hybrid_slides[2]["notes"],
        )
        self.assertIn("Original presenter notes", hybrid_slides[2]["notes"])
        self.assertEqual(hybrid_slides[3]["type"], "video")
        self.assertEqual(
            hybrid_slides[3]["path"],
            "media/videos/01_intro/1080p60/sections/003_embedded.mp4",
        )
        self.assertEqual(
            used_stems,
            {"001_static", "002_keynote", "003_embedded"},
        )

    def test_build_hybrid_slide_records_omits_marked_video_slides(self) -> None:
        omitted_video_path = (
            REPO_ROOT / "media" / "videos" / "04_study2" / "1080p60" / "sections" / "000_omitted_clip.mp4"
        )
        kept_video_path = (
            REPO_ROOT / "media" / "videos" / "04_study2" / "1080p60" / "sections" / "001_kept_clip.mp4"
        )

        expanded_slides = [
            {
                "type": "video",
                "path": str(omitted_video_path),
                "title": "",
                "subtitle": "",
                "body": "",
                "notes": "",
            },
            {
                "type": "video",
                "path": str(kept_video_path),
                "title": "",
                "subtitle": "",
                "body": "",
                "notes": "",
            },
        ]
        decisions = {
            "000_omitted_clip": presentation_hybrid_deck.AuditDecision(
                stem="000_omitted_clip",
                disposition=presentation_hybrid_deck.HybridDisposition.OMIT,
                duration_text="",
                animation_summary="",
                why="",
            ),
            "001_kept_clip": presentation_hybrid_deck.AuditDecision(
                stem="001_kept_clip",
                disposition=presentation_hybrid_deck.HybridDisposition.EMBEDDED_VIDEO,
                duration_text="",
                animation_summary="",
                why="",
            ),
        }

        hybrid_slides, used_stems = presentation_hybrid_deck.build_hybrid_slide_records(
            expanded_slides,
            decisions,
            extracted_stills={},
        )

        self.assertEqual(len(hybrid_slides), 1)
        self.assertEqual(hybrid_slides[0]["type"], "video")
        self.assertEqual(
            hybrid_slides[0]["path"],
            "media/videos/04_study2/1080p60/sections/001_kept_clip.mp4",
        )
        self.assertEqual(
            used_stems,
            {"000_omitted_clip", "001_kept_clip"},
        )

    def test_serialize_hybrid_manifest_keeps_note_blocks_readable(self) -> None:
        manifest_text = presentation_hybrid_deck.serialize_hybrid_manifest(
            deck={
                "output_dir": "media/keynote",
                "slide_width": 1920,
                "slide_height": 1080,
            },
            slides=[
                {
                    "type": "image",
                    "path": "media/hybrid_stills/example.png",
                    "title": "",
                    "subtitle": "",
                    "body": "",
                    "notes": "Line one\nLine two",
                }
            ],
            deck_base_name="presentation_hybrid_test",
        )

        self.assertIn('deck_base_name = "presentation_hybrid_test"', manifest_text)
        self.assertIn('path = "media/hybrid_stills/example.png"', manifest_text)
        self.assertIn('notes = """\nLine one\nLine two\n"""', manifest_text)

    def test_render_everything_qk_forces_4k_quality_folder(self) -> None:
        self.assertEqual(
            presentation_hybrid_deck.resolve_effective_quality_folder(
                "auto",
                render_everything_qk=True,
            ),
            "2160p60",
        )
        self.assertEqual(
            presentation_hybrid_deck.resolve_effective_quality_folder(
                "qk",
                render_everything_qk=True,
            ),
            "2160p60",
        )
        with self.assertRaisesRegex(ValueError, "conflicts with --quality-folder"):
            presentation_hybrid_deck.resolve_effective_quality_folder(
                "1080p60",
                render_everything_qk=True,
            )


if __name__ == "__main__":
    unittest.main()
