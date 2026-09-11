#!/usr/bin/env python3
"""Deterministically compose an Illustrated Memory page.

The source original image is never regenerated or recolored. It is only resized
proportionally for placement on the final canvas.
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from typing import Optional

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


def fit_width(img: Image.Image, width: int) -> Image.Image:
    scale = width / img.width
    height = max(1, round(img.height * scale))
    return img.resize((width, height), Image.Resampling.LANCZOS)


def paper_texture(size: tuple[int, int], base=(241, 231, 205), seed=17) -> Image.Image:
    """Create texture-only cream paper: subtle grain/fibers, no decorations."""
    random.seed(seed)
    w, h = size
    img = Image.new("RGB", size, base)
    px = img.load()

    # Fine monochrome-ish paper grain.
    for y in range(h):
        for x in range(w):
            n = random.gauss(0, 3.0)
            # very slight warm variation
            px[x, y] = (
                max(0, min(255, int(base[0] + n + 0.6))),
                max(0, min(255, int(base[1] + n))),
                max(0, min(255, int(base[2] + n - 0.4))),
            )

    # Extremely faint blurred tonal variation; still texture, not pattern.
    small = Image.new("L", (max(8, w // 60), max(8, h // 60)), 128)
    sdraw = ImageDraw.Draw(small)
    for _ in range(180):
        x = random.randrange(small.width)
        y = random.randrange(small.height)
        r = random.randint(1, 4)
        v = random.randint(116, 140)
        sdraw.ellipse((x-r, y-r, x+r, y+r), fill=v)
    variation = small.resize(size, Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(18))
    variation_rgb = Image.merge("RGB", (variation, variation, variation))
    img = ImageChops.soft_light(img, variation_rgb)
    return img


def rough_mask(size: tuple[int, int], rough_px=18, feather_px=7, seed=23) -> Image.Image:
    """Organic mask that creates dry-brush / irregular painted edges."""
    random.seed(seed)
    w, h = size
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)

    step = max(8, rough_px // 2)
    left = []
    right = []
    for y in range(0, h + step, step):
        yy = min(h - 1, y)
        left.append((max(0, rough_px + random.randint(-rough_px, rough_px)), yy))
        right.append((min(w - 1, w - rough_px + random.randint(-rough_px, rough_px)), yy))

    top = []
    bottom = []
    for x in range(0, w + step, step):
        xx = min(w - 1, x)
        top.append((xx, max(0, rough_px + random.randint(-rough_px, rough_px))))
        bottom.append((xx, min(h - 1, h - rough_px + random.randint(-rough_px, rough_px))))

    poly = top + list(reversed(right)) + list(reversed(bottom)) + left
    d.polygon(poly, fill=255)

    # Random tiny unpainted bites close to edges to mimic broken pigment.
    for _ in range(max(30, (w + h) // 40)):
        side = random.choice(["t", "b", "l", "r"])
        if side in ("t", "b"):
            x = random.randrange(w)
            y = random.randrange(0, max(1, rough_px * 2)) if side == "t" else random.randrange(max(0, h - rough_px * 2), h)
        else:
            y = random.randrange(h)
            x = random.randrange(0, max(1, rough_px * 2)) if side == "l" else random.randrange(max(0, w - rough_px * 2), w)
        r = random.randint(2, max(3, rough_px // 2))
        d.ellipse((x-r, y-r, x+r, y+r), fill=random.randint(0, 80))

    if feather_px > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(feather_px))
    return mask


def paste_with_mask(canvas: Image.Image, img: Image.Image, xy: tuple[int, int], mask: Optional[Image.Image] = None):
    if mask is None:
        canvas.paste(img, xy)
    else:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        canvas.paste(img, xy, mask)


def resolve_font(path: Optional[str], size: int) -> ImageFont.FreeTypeFont:
    if path:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Font not found: {p}")
        return ImageFont.truetype(str(p), size=size)

    # Portable fallbacks. For the intended look, pass an actual handwriting font.
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--illustration", required=True)
    ap.add_argument("--original", required=True)
    ap.add_argument("--caption", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--font", default=None, help="Path to a handwriting TTF/OTF (Handlee/Kalam/Caveat recommended)")
    ap.add_argument("--width", type=int, default=1536)
    ap.add_argument("--height", type=int, default=2048)
    args = ap.parse_args()

    W, H = args.width, args.height
    canvas = paper_texture((W, H))

    illustration = Image.open(args.illustration).convert("RGB")
    original = Image.open(args.original).convert("RGB")

    ill_w = round(W * 0.72)
    illustration = fit_width(illustration, ill_w)
    # If too tall, scale down to preserve caption space.
    max_ill_h = round(H * 0.66)
    if illustration.height > max_ill_h:
        scale = max_ill_h / illustration.height
        illustration = illustration.resize((round(illustration.width * scale), max_ill_h), Image.Resampling.LANCZOS)
    ill_x = (W - illustration.width) // 2
    ill_y = round(H * 0.06)

    mask = rough_mask(illustration.size, rough_px=max(14, W // 90), feather_px=max(3, W // 240))
    paste_with_mask(canvas, illustration, (ill_x, ill_y), mask)

    # Original photo: exact pixels aside from proportional resizing for layout.
    orig_w = round(W * 0.28)
    original = fit_width(original, orig_w)
    border = max(5, round(W * 0.005))
    framed = Image.new("RGB", (original.width + border * 2, original.height + border * 2), (246, 241, 226))
    framed.paste(original, (border, border))

    orig_x = W - framed.width - round(W * 0.045)
    overlap = round(W * 0.055)
    orig_y = min(H - framed.height - round(H * 0.05), ill_y + illustration.height - overlap)
    canvas.paste(framed, (orig_x, orig_y))

    # Caption area below illustration, left of original.
    draw = ImageDraw.Draw(canvas)
    font = resolve_font(args.font, max(34, round(W * 0.034)))
    cap_x = round(W * 0.08)
    cap_y = min(round(H * 0.78), ill_y + illustration.height + round(H * 0.025))
    cap_max_w = max(250, orig_x - cap_x - round(W * 0.035))
    lines = wrap_text(draw, args.caption.strip(), font, cap_max_w)
    fill = (104, 127, 78)
    spacing = max(10, round(W * 0.009))
    y = cap_y
    for line in lines:
        draw.text((cap_x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((cap_x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + spacing

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=95)
    print(out)


if __name__ == "__main__":
    main()
