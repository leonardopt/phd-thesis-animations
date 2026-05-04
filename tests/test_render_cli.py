from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.render import cli, config, helpers


class RenderHelpersTests(unittest.TestCase):
    def test_normalize_quality_aliases(self) -> None:
        self.assertEqual(helpers.normalize_quality_dir("-ql"), "480p15")
        self.assertEqual(helpers.normalize_quality_dir("qm"), "720p30")
        self.assertEqual(helpers.normalize_quality_dir("high"), "1080p60")
        self.assertEqual(helpers.normalize_quality_dir("2160p60"), "2160p60")

    def test_section_registry_matches_expected_output_dirs(self) -> None:
        self.assertEqual(
            config.ORDERED_SECTION_KEYS,
            ("intro", "methods", "study1", "study2", "conclusion", "supplementary"),
        )
        self.assertEqual(config.SECTION_CONFIGS["study1"].output_dir, "03_study1")
        self.assertTrue(config.SECTION_CONFIGS["study1"].disable_caching)
        self.assertTrue(config.SECTION_CONFIGS["study2"].disable_caching)
        self.assertFalse(config.SECTION_CONFIGS["intro"].disable_caching)

    def test_clear_stale_section_clips_targets_selected_quality_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            videos_root = Path(tmp_dir)
            clips_dir = videos_root / "03_study1" / "1080p60" / "sections"
            nested_dir = clips_dir / "nested"
            nested_dir.mkdir(parents=True)
            stale_clip = clips_dir / "000_old.mp4"
            stale_probe = nested_dir / "probe.txt"
            keep_file = videos_root / "03_study1" / "1080p60" / "study1.mp4"
            stale_clip.write_text("clip", encoding="utf-8")
            stale_probe.write_text("probe", encoding="utf-8")
            keep_file.parent.mkdir(parents=True, exist_ok=True)
            keep_file.write_text("keep", encoding="utf-8")

            returned_dir = helpers.clear_stale_section_clips(videos_root, "03_study1", "1080p60")

            self.assertEqual(returned_dir, clips_dir)
            self.assertFalse(stale_clip.exists())
            self.assertFalse(stale_probe.exists())
            self.assertTrue(keep_file.exists())

    def test_collect_concat_inputs_preserves_section_order_then_clip_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            videos_root = Path(tmp_dir)
            intro_dir = videos_root / "01_intro" / "1080p60" / "sections"
            methods_dir = videos_root / "02_methods" / "1080p60" / "sections"
            intro_dir.mkdir(parents=True)
            methods_dir.mkdir(parents=True)

            intro_b = intro_dir / "001_intro_b.mp4"
            intro_a = intro_dir / "000_intro_a.mp4"
            methods_a = methods_dir / "000_methods_a.mp4"
            skipped = methods_dir / "001_methods_autocreated.mp4"
            for path in (intro_b, intro_a, methods_a, skipped):
                path.write_text(path.name, encoding="utf-8")

            ordered = helpers.collect_concat_inputs(
                videos_root,
                "1080p60",
                ("01_intro", "02_methods"),
            )

            self.assertEqual(
                ordered,
                [intro_a.resolve(), intro_b.resolve(), methods_a.resolve()],
            )


class RenderCliTests(unittest.TestCase):
    def test_help_exits_cleanly(self) -> None:
        with self.assertRaises(SystemExit) as exc:
            cli.main(["--help"])
        self.assertEqual(exc.exception.code, 0)

    def test_section_command_dispatches_to_named_renderer(self) -> None:
        with mock.patch.object(cli, "render_named_section") as render_named_section:
            exit_code = cli.main(["section", "intro", "-qh"])

        self.assertEqual(exit_code, 0)
        render_named_section.assert_called_once_with("intro", "-qh")

    def test_all_command_dispatches_to_batch_renderer(self) -> None:
        with mock.patch.object(cli, "render_all_sections") as render_all_sections:
            exit_code = cli.main(["all", "-qm"])

        self.assertEqual(exit_code, 0)
        render_all_sections.assert_called_once_with("-qm")

    def test_single_video_command_dispatches_with_output_path(self) -> None:
        output_path = Path("media/videos/custom.mp4")
        with mock.patch.object(cli, "render_single_video") as render_single_video:
            exit_code = cli.main(["single-video", "-qh", "--output", str(output_path)])

        self.assertEqual(exit_code, 0)
        render_single_video.assert_called_once_with("-qh", output_path)

    def test_invalid_section_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as exc:
            cli.main(["section", "not-a-section"])
        self.assertEqual(exc.exception.code, 2)

    def test_invalid_quality_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as exc:
            cli.main(["all", "-qx"])
        self.assertIn("Unsupported quality", str(exc.exception))
