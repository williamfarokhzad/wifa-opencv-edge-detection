"""Small Canny experiments for saved or synthetic grayscale images."""
import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np


def make_scene(name):
    """Generate an 8-bit frame and the expected x coordinates of vertical edges."""
    h, w = 96, 160
    image = np.full((h, w), 45, dtype=np.uint8)
    if name == "steps":
        image[:, 44:] = 80
        image[:, 110:] = 180
        return image, (44, 110)
    if name == "linked":
        # At x=80 the upper section seeds a weaker, connected lower section.
        right = np.rint(np.interp(np.arange(h), [0, 24, 47, 95],
                                   [155, 155, 80, 80])).astype(np.uint8)
        image[:, 80:] = right[:, None]
        return image, (80,)
    if name == "noise":
        image[:, 80:] = 130
        rng = np.random.default_rng(42)
        return np.clip(image.astype(np.int16) + rng.integers(-26, 27, image.shape),
                       0, 255).astype(np.uint8), (80,)
    raise ValueError(f"unknown scene: {name}")


def detect(image, low, high, blur=0):
    if not isinstance(image, np.ndarray) or image.ndim != 2 or image.dtype != np.uint8 or min(image.shape) < 3:
        raise ValueError("expected a grayscale uint8 image at least 3 x 3 pixels")
    if not math.isfinite(low) or not math.isfinite(high) or not 0 <= low < high:
        raise ValueError("thresholds must be finite and satisfy 0 <= low < high")
    if blur not in (0, 3, 5, 7):
        raise ValueError("blur must be 0, 3, 5 or 7")
    prepared = cv2.GaussianBlur(image, (blur, blur), 0) if blur else image
    return cv2.Canny(prepared, low, high, apertureSize=3, L2gradient=True)


def summarize(edges, truth_x=()):
    mask = edges != 0
    result = {"edge_pixels": int(mask.sum()), "size": [edges.shape[1], edges.shape[0]]}
    if truth_x:
        # Tolerate a one-pixel boundary shift and exclude top and bottom rows.
        rows = mask[4:-4]
        bands = [rows[:, x-2:x+2] for x in truth_x]
        selected = np.zeros(rows.shape[1], dtype=bool)
        for x in truth_x:
            selected[x-2:x+2] = True
        result["boundary_rows"] = {str(x): int(b.any(axis=1).sum())
                                   for x, b in zip(truth_x, bands)}
        result["rows_measured"] = int(rows.shape[0])
        result["off_band_pixels"] = int(rows[:, ~selected].sum())
        if truth_x == (80,):
            result["bottom_boundary_rows"] = int(mask[55:92, 78:82].any(axis=1).sum())
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--scene", choices=("steps", "linked", "noise"))
    inputs.add_argument("--image", type=Path, help="saved image to read as grayscale")
    parser.add_argument("--low", type=float, required=True)
    parser.add_argument("--high", type=float, required=True)
    parser.add_argument("--blur", type=int, choices=(0, 3, 5, 7), default=0)
    parser.add_argument("--output", type=Path, help="new PNG file for the edge map")
    args = parser.parse_args(argv)
    try:
        if args.scene:
            image, truth = make_scene(args.scene)
        else:
            if not args.image.is_file():
                raise ValueError(f"image file not found: {args.image}")
            image = cv2.imread(str(args.image), cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError(f"OpenCV could not decode: {args.image}")
            truth = ()
        edges = detect(image, args.low, args.high, args.blur)
        if args.output:
            if args.output.suffix.lower() != ".png":
                raise ValueError("output must have a .png suffix")
            ok, buffer = cv2.imencode(".png", edges)
            if not ok:
                raise ValueError("could not encode PNG")
            with args.output.open("xb") as handle:
                handle.write(buffer.tobytes())
    except (ValueError, OSError, cv2.error) as err:
        parser.error(str(err))
    print(json.dumps(summarize(edges, truth), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
