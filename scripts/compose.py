#!/usr/bin/env python3
"""Compose an Illustrated Memory page from generated and original images.

The original image is never regenerated or recolored. It is only resized
proportionally for placement on the final canvas.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

try:
    import yaml
except ImportError:  # pragma: no cover - handled by load_config
    yaml = None


DEFAULT_CONFIG: dict[str, Any] = {
    "canvas": {"width": 1536, "height": 2048},
    "background": {"base_rgb": [241, 231, 205]},
    "illustration": {
        "width_ratio": 0.72,
        "max_height_ratio": 0.66,
        "top_ratio": 0.06,
        "rough_edge_px": 18,
        "feather_px": 7,
    },
    "original": {
        "width_ratio": 0.28,
        "right_margin_ratio": 0.045,
        "bottom_margin_ratio": 0.05,
        "overlap_ratio": 0.055,
        "border_ratio": 0.005,
        "border_rgb": [246, 241, 226],
    },
    "caption": {
        "x_ratio": 0.08,
        "y_ratio": 0.78,
        "font_size_ratio": 0.034,
        "fill_rgb": [104, 127, 78],
        "line_spacing_ratio": 0.009,
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "config" / "style.yaml"
    if not path.exists():
        return DEFAULT_CONFIG
    if yaml is None:
        raise RuntimeError("PyYAML is required when using a YAML config file.")
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    return deep_merge(DEFAULT_CONFIG, loaded)


def fit_width(img: Image.Image, width: int) -> Image.Image:
    scale = width / img.width
    height = max(1, round(img.height * scale))
    return img.resize((width, height), Image.Resampling.LANCZOS)


def paper_texture(size: tuple[int, int], base: tuple[int, int, int], seed: int = 17) -> Image.Image:
    random.seed(seed)
    width, height = size
    img = Image.new("RGB", size, base)
    px = img.load()

    for y in range(height):
        for x in range(width):
            noise = random.gauss(0, 3.0)
            px[x, y] = (
                max(0, min(255, int(base[0] + noise + 0.6))),
                max(0, min(255, int(base[1] + noise))),
                max(0, min(255, int(base[2] + noise - 0.4))),
            )

    small = Image.new("L", (max(8, width // 60), max(8, height // 60)), 128)
    draw = ImageDraw.Draw(small)
    for _ in range(180):
        x = random.randrange(small.width)
        y = random.randrange(small.height)
        radius = random.randint(1, 4)
        value = random.randint(116, 140)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=value)
    variation = small.resize(size, Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(18))
    variation_rgb = Image.merge("RGB", (variation, variation, variation))
    return ImageChops.soft_light(img, variation_rgb)


def rough_mask(size: tuple[int, int], rough_px: int, feather_px: int, seed: int = 23) -> Image.Image:
    random.seed(seed)
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    step = max(8, rough_px // 2)

    left = []
    right = []
    for y in range(0, height + step, step):
        yy = min(height - 1, y)
        left.append((max(0, rough_px + random.randint(-rough_px, rough_px)), yy))
        right.append((min(width - 1, width - rough_px + random.randint(-rough_px, rough_px)), yy))

    top = []
    bottom = []
    for x in range(0, width + step, step):
        xx = min(width - 1, x)
        top.append((xx, max(0, rough_px + random.randint(-rough_px, rough_px))))
        bottom.append((xx, min(height - 1, height - rough_px + random.randint(-rough_px, rough_px))))

    polygon = top + list(reversed(right)) + list(reversed(bottom)) + left
    draw.polygon(polygon, fill=255)

    for _ in range(max(30, (width + height) // 40)):
        side = random.choice(["t", "b", "l", "r"])
        if side in ("t", "b"):
            x = random.randrange(width)
            y = random.randrange(0, max(1, rough_px * 2)) if side == "t" else random.randrange(max(0, height - rough_px * 2), height)
        else:
            y = random.randrange(height)
            x = random.randrange(0, max(1, rough_px * 2)) if side == "l" else random.randrange(max(0, width - rough_px * 2), width)
        radius = random.randint(2, max(3, rough_px // 2))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=random.randint(0, 80))

    if feather_px > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(feather_px))
    return mask


def resolve_font(path: str | None, size: int) -> ImageFont.ImageFont:
    if path:
        font_path = Path(path)
        if not font_path.exists():
            raise FileNotFoundError(f"Font not found: {font_path}")
        return ImageFont.truetype(str(font_path), size=size)

    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def rgb(value: list[int]) -> tuple[int, int, int]:
    return (int(value[0]), int(value[1]), int(value[2]))


def compose(
    illustration_path: Path,
    original_path: Path,
    caption: str,
    output_path: Path,
    font_path: str | None = None,
    config_path: Path | None = None,
    width: int | None = None,
    height: int | None = None,
) -> Path:
    config = load_config(config_path)
    canvas_cfg = config["canvas"]
    illustration_cfg = config["illustration"]
    original_cfg = config["original"]
    caption_cfg = config["caption"]

    canvas_width = width or int(canvas_cfg["width"])
    canvas_height = height or int(canvas_cfg["height"])
    canvas = paper_texture((canvas_width, canvas_height), rgb(config["background"]["base_rgb"]))

    illustration = Image.open(illustration_path).convert("RGB")
    original = Image.open(original_path).convert("RGB")

    illustration = fit_width(illustration, round(canvas_width * float(illustration_cfg["width_ratio"])))
    max_illustration_height = round(canvas_height * float(illustration_cfg["max_height_ratio"]))
    if illustration.height > max_illustration_height:
        scale = max_illustration_height / illustration.height
        illustration = illustration.resize((round(illustration.width * scale), max_illustration_height), Image.Resampling.LANCZOS)

    illustration_x = (canvas_width - illustration.width) // 2
    illustration_y = round(canvas_height * float(illustration_cfg["top_ratio"]))
    mask = rough_mask(
        illustration.size,
        rough_px=max(14, int(illustration_cfg["rough_edge_px"])),
        feather_px=max(3, int(illustration_cfg["feather_px"])),
    )
    canvas.paste(illustration.convert("RGBA"), (illustration_x, illustration_y), mask)

    original = fit_width(original, round(canvas_width * float(original_cfg["width_ratio"])))
    border = max(5, round(canvas_width * float(original_cfg["border_ratio"])))
    framed = Image.new("RGB", (original.width + border * 2, original.height + border * 2), rgb(original_cfg["border_rgb"]))
    framed.paste(original, (border, border))

    original_x = canvas_width - framed.width - round(canvas_width * float(original_cfg["right_margin_ratio"]))
    overlap = round(canvas_width * float(original_cfg["overlap_ratio"]))
    original_y = min(
        canvas_height - framed.height - round(canvas_height * float(original_cfg["bottom_margin_ratio"])),
        illustration_y + illustration.height - overlap,
    )
    canvas.paste(framed, (original_x, original_y))

    draw = ImageDraw.Draw(canvas)
    font = resolve_font(font_path, max(34, round(canvas_width * float(caption_cfg["font_size_ratio"]))))
    caption_x = round(canvas_width * float(caption_cfg["x_ratio"]))
    caption_y = min(round(canvas_height * float(caption_cfg["y_ratio"])), illustration_y + illustration.height + round(canvas_height * 0.025))
    caption_max_width = max(250, original_x - caption_x - round(canvas_width * 0.035))
    lines = wrap_text(draw, caption.strip(), font, caption_max_width)
    line_spacing = max(10, round(canvas_width * float(caption_cfg["line_spacing_ratio"])))

    y = caption_y
    for line in lines:
        draw.text((caption_x, y), line, font=font, fill=rgb(caption_cfg["fill_rgb"]))
        bbox = draw.textbbox((caption_x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=95)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--illustration", required=True, type=Path)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--caption", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--font", default=None, help="Path to a handwriting TTF/OTF such as Handlee, Kalam, or Caveat")
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    args = parser.parse_args()

    output = compose(
        illustration_path=args.illustration,
        original_path=args.original,
        caption=args.caption,
        output_path=args.output,
        font_path=args.font,
        config_path=args.config,
        width=args.width,
        height=args.height,
    )
    print(output)


if __name__ == "__main__":
    main()
