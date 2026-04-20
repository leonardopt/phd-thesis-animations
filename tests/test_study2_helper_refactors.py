from __future__ import annotations

import unittest

import numpy as np
from manim import ManimColor

import scenes.study2 as study2


class Study2HelperCharacterizationTests(unittest.TestCase):
    def test_overview_identity_color_matches_current_mapping_and_error(self) -> None:
        self.assertEqual(study2._overview_identity_color(study2.LAKE), "#4F78A8")
        self.assertEqual(study2._overview_identity_color(study2.SOFA), "#2E8B94")
        with self.assertRaisesRegex(
            KeyError,
            "^'No overview identity color registered for missing\\.png'$",
        ):
            study2._overview_identity_color("missing.png")

    def test_identity_color_helpers_match_current_mappings_and_error(self) -> None:
        self.assertEqual(study2._identity_color(study2.LAKE), "#2563EB")
        self.assertEqual(study2._identity_color(study2.SOFA), "#D97706")
        self.assertEqual(
            study2._identity_colors([study2.LAKE, study2.SOFA, study2.CAT]),
            ["#2563EB", "#D97706", "#DC2626"],
        )
        with self.assertRaisesRegex(
            KeyError,
            "^'No identity color registered for missing\\.png'$",
        ):
            study2._identity_color("missing.png")

    def test_vector_layout_matches_current_positions(self) -> None:
        scene = study2.Study2DecodingOverviewA.__new__(study2.Study2DecodingOverviewA)
        actual = np.asarray(scene._vector_layout(1.75, 5))
        expected = np.array(
            [
                [1.75, 1.2, 0.0],
                [1.75, 0.6, 0.0],
                [1.75, 0.0, 0.0],
                [1.75, -0.5999999999999999, 0.0],
                [1.75, -1.2, 0.0],
            ],
            dtype=np.float64,
        )
        np.testing.assert_array_equal(actual, expected)

    def test_glm_svg_hex_matches_current_normalization(self) -> None:
        scene = study2.Study2CrossSessionDecodingResultsCombined.__new__(
            study2.Study2CrossSessionDecodingResultsCombined
        )
        self.assertIsNone(scene._glm_svg_hex(None))
        self.assertEqual(scene._glm_svg_hex("#262626"), "#262626")
        self.assertEqual(
            scene._glm_svg_hex(ManimColor("#7b51a0")),
            "#7B51A0",
        )

    def test_synced_source_pulse_matches_current_profile(self) -> None:
        self.assertEqual(study2._study2_synced_source_pulse(0.0), 0.0)
        self.assertEqual(study2._study2_synced_source_pulse(0.12), 0.0)
        self.assertAlmostEqual(
            study2._study2_synced_source_pulse(0.56),
            1.0,
            places=15,
        )
        self.assertEqual(study2._study2_synced_source_pulse(1.0), 0.0)


if __name__ == "__main__":
    unittest.main()
