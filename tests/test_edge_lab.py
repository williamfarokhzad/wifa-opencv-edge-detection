import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from edge_lab import detect, make_scene, summarize

ROOT = Path(__file__).resolve().parents[1]


class EdgeTests(unittest.TestCase):
    def test_flat_image_has_no_edges(self):
        image = np.full((32, 64), 100, dtype=np.uint8)
        self.assertFalse(detect(image, 30, 60).any())

    def test_step_location_independent_of_summary(self):
        image = np.zeros((45, 71), dtype=np.uint8)
        image[:, 31:] = 140
        y, x = np.nonzero(detect(image, 60, 140))
        self.assertEqual(len(x), 45)
        self.assertTrue(np.isin(x, (30, 31)).all())
        self.assertEqual(set(y), set(range(45)))

    def test_weak_disconnected_edge_needs_own_seed(self):
        image, _ = make_scene("steps")
        loose = detect(image, 60, 120)
        strict = detect(image, 60, 220)
        self.assertTrue(loose[:, 42:46].any(axis=1).all())
        self.assertFalse(strict[:, 42:46].any())
        np.testing.assert_array_equal(loose[:, 108:112], strict[:, 108:112])

    def test_lower_threshold_preserves_connected_weak_edge(self):
        image, _ = make_scene("linked")
        kept = detect(image, 60, 220)
        cut = detect(image, 180, 220)
        self.assertTrue(kept[55:92, 78:82].any(axis=1).all())
        self.assertFalse(cut[55:92, 78:82].any())
        self.assertTrue(cut[4:24, 78:82].any(axis=1).all())

    def test_blur_reduces_noise_without_losing_synthetic_boundary(self):
        image, truth = make_scene("noise")
        raw = summarize(detect(image, 45, 95), truth)
        filtered = summarize(detect(image, 45, 95, 5), truth)
        self.assertGreater(raw["off_band_pixels"], 1000)
        self.assertLess(filtered["off_band_pixels"], raw["off_band_pixels"] // 10)
        self.assertEqual(filtered["boundary_rows"]["80"], 88)

    def test_constant_brightness_offset_preserves_edges_without_clipping(self):
        image, _ = make_scene("steps")
        np.testing.assert_array_equal(detect(image, 60, 120), detect(image + 20, 60, 120))

    def test_bad_inputs_are_rejected(self):
        good, _ = make_scene("steps")
        for args in [(good, 5, 5), (good, float("nan"), 60), (good, 1, float("inf")),
                     (good, 10, 70, 4), (good.astype(float), 10, 70),
                     (good[:, :, None], 10, 70), (good[:2], 10, 70)]:
            with self.subTest(shape=args[0].shape, values=args[1:]), self.assertRaises(ValueError):
                detect(*args)

    def test_saved_image_png_round_trip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.png"
            out = Path(tmp) / "edges.png"
            image, _ = make_scene("steps")
            self.assertTrue(cv2.imwrite(str(src), image))
            command = [sys.executable, str(ROOT / "edge_lab.py"), "--image", str(src),
                       "--low", "60", "--high", "120", "--output", str(out)]
            result = subprocess.run(command, text=True, capture_output=True, check=True)
            self.assertNotIn("boundary_rows", result.stdout)
            np.testing.assert_array_equal(cv2.imread(str(out), 0), detect(image, 60, 120))
            before = out.read_bytes()
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("File exists", result.stderr)
            self.assertEqual(out.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
