"""Replay all comparisons. Run from the project root: python -m examples.compare."""
import json

from edge_lab import detect, make_scene, summarize

CASES = (
    ("steps", 60, 120, 0),
    ("steps", 60, 220, 0),
    ("linked", 60, 220, 0),
    ("linked", 180, 220, 0),
    ("noise", 45, 95, 0),
    ("noise", 45, 95, 5),
)

if __name__ == "__main__":
    for scene, low, high, blur in CASES:
        image, truth = make_scene(scene)
        summary = summarize(detect(image, low, high, blur), truth)
        print(json.dumps(dict(scene=scene, low=low, high=high, blur=blur, **summary), sort_keys=True))
