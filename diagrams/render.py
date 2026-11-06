"""Regenerate original lesson WebPs from the exact simulated edge arrays."""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from edge_lab import detect, make_scene

HERE = Path(__file__).resolve().parent
FONTS = Path(os.environ.get("EDGE_LAB_FONTS", "/usr/share/fonts/truetype/dejavu"))


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


def render(name, heading, cards):
    canvas = Image.new("RGB", (720, 575), "#0a1822")
    draw = ImageDraw.Draw(canvas)
    draw.text((36, 25), heading, font=font(32, True), fill="#edf6ff")
    for index, (array, title, note, result) in enumerate(cards):
        y = 82 + index * 154
        draw.rounded_rectangle((28, y, 692, y + 140), 14, fill="#122837", outline="#2a4c5f", width=2)
        canvas.paste(Image.fromarray(array).convert("RGB").resize((192, 115), Image.Resampling.NEAREST), (42, y + 12))
        draw.text((255, y + 18), title, font=font(24, True), fill="#edf6ff")
        draw.text((255, y + 59), note, font=font(23), fill="#b6d0e1")
        draw.text((255, y + 94), result, font=font(24, True), fill="#77e1bc")
    canvas.save(HERE / (name + ".webp"), "WEBP", quality=87, method=6)


def main():
    linked, _ = make_scene("linked")
    noisy, _ = make_scene("noise")
    render("canny-hysteresis", "A strong edge can carry a weak one", [
        (linked, "Synthetic input", "Dark left half", "Right fades toward bottom"),
        (detect(linked, 60, 220), "Low 60 · High 220", "Weak portion stays linked", "37 of 37 lower rows"),
        (detect(linked, 180, 220), "Low 180 · High 220", "Weak portion is cut off", "0 of 37 lower rows"),
    ])
    render("canny-noise", "Blur the noise, then count the cost", [
        (noisy, "Synthetic input", "Seeded pixel noise", "One vertical boundary"),
        (detect(noisy, 45, 95), "No blur", "Low 45 · High 95", "4,797 off-band pixels"),
        (detect(noisy, 45, 95, 5), "5 × 5 Gaussian blur", "Same two thresholds", "0 off-band pixels"),
    ])


if __name__ == "__main__":
    main()
