from __future__ import annotations

import unittest

import numpy as np

import scenes.study1 as study1


class Study1HelperCharacterizationTests(unittest.TestCase):
    def test_cloud_positions_match_current_layout(self) -> None:
        expected = np.array(
            [
                [1.25, -0.5],
                [1.9, -0.5],
                [1.5750000000000002, 0.06291651245988505],
                [0.925, 0.06291651245988517],
                [0.6, -0.49999999999999994],
                [0.9249999999999997, -1.062916512459885],
                [1.5750000000000002, -1.0629165124598852],
            ],
            dtype=np.float64,
        )
        for func in (
            study1._s1_step2_cloud_positions,
            study1._s1_step2_showcase_cloud_positions,
            study1._s1_step3_cloud_positions,
        ):
            with self.subTest(func=func.__name__):
                np.testing.assert_array_equal(
                    np.asarray(func(7, 1.25, -0.5)),
                    expected,
                )
                np.testing.assert_array_equal(
                    np.asarray(func(0, 1.25, -0.5)),
                    np.empty((0,), dtype=np.float64),
                )

    def test_noise_magma_matches_current_pixels(self) -> None:
        expected = np.array(
            [
                [[15, 11, 44, 255], [74, 16, 121, 255], [253, 161, 110, 255], [215, 69, 107, 255]],
                [[18, 13, 51, 255], [153, 45, 127, 255], [172, 51, 123, 255], [40, 17, 89, 255]],
                [[250, 128, 94, 255], [24, 15, 63, 255], [137, 40, 129, 255], [189, 57, 119, 255]],
                [[153, 45, 127, 255], [217, 70, 106, 255], [250, 128, 94, 255], [252, 232, 170, 255]],
            ],
            dtype=np.uint8,
        )
        for func in (
            study1._s1_step2_noise_magma,
            study1._s1_step2_showcase_noise_magma,
        ):
            with self.subTest(func=func.__name__):
                actual = func(3, 4)
                self.assertEqual(actual.dtype, np.uint8)
                self.assertEqual(actual.shape, (4, 4, 4))
                np.testing.assert_array_equal(actual, expected)

    def test_slerp_variants_match_each_other_and_edge_case(self) -> None:
        u = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        v = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        expected = np.array([0.9238795325112867, 0.3826834323650898, 0.0])

        step4 = study1._s1_step4_slerp(u, v, 0.25)
        step5 = study1._s1_step5__slerp(u, v, 0.25)
        np.testing.assert_allclose(step4, expected, rtol=0.0, atol=1e-12)
        np.testing.assert_allclose(step5, expected, rtol=0.0, atol=1e-12)
        np.testing.assert_array_equal(step4, step5)

        same = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        np.testing.assert_array_equal(
            study1._s1_step4_slerp(same, same, 0.25),
            study1._s1_step5__slerp(same, same, 0.25),
        )
        np.testing.assert_array_equal(
            study1._s1_step4_slerp(same, same, 0.25),
            same,
        )

    def test_vec3_variants_preserve_arrow_geometry_and_style(self) -> None:
        kwargs = dict(start=[0, 0, 0], end=[1, 2, 3], color="#123456", sw=2.5, tl=0.33)
        step4 = study1._s1_step4_vec3(**kwargs)
        step5 = study1._s1_step5__vec3(**kwargs)

        self.assertIsInstance(step4, study1.Arrow)
        self.assertIsInstance(step5, study1.Arrow)
        np.testing.assert_allclose(step4.get_start(), np.array([0.0, 0.0, 0.0]), rtol=0.0, atol=1e-15)
        np.testing.assert_allclose(step4.get_end(), np.array([1.0, 2.0, 3.0]), rtol=0.0, atol=1e-15)
        np.testing.assert_allclose(step5.get_start(), np.array([0.0, 0.0, 0.0]), rtol=0.0, atol=1e-15)
        np.testing.assert_allclose(step5.get_end(), np.array([1.0, 2.0, 3.0]), rtol=0.0, atol=1e-15)
        self.assertEqual(step4.get_stroke_width(), 2.5)
        self.assertEqual(step5.get_stroke_width(), 2.5)
        self.assertEqual(step4.tip_length, 0.33)
        self.assertEqual(step5.tip_length, 0.33)
        self.assertEqual(step4.max_stroke_width_to_length_ratio, 100)
        self.assertEqual(step5.max_stroke_width_to_length_ratio, 100)
        self.assertEqual(step4.get_color().to_hex().upper(), "#123456")
        self.assertEqual(step5.get_color().to_hex().upper(), "#123456")


if __name__ == "__main__":
    unittest.main()
