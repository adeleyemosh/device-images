"""Idempotent jpg -> png/webp conversion for device-images."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from PIL import Image


@dataclass
class ConvertResult:
    slug: str
    converted: int = 0
    up_to_date: int = 0
    failed: int = 0
    failed_items: list[tuple[str, str]] = field(default_factory=list)


def needs_conversion(src: str, dest: str) -> bool:
    if not os.path.exists(dest):
        return True
    return os.path.getmtime(src) > os.path.getmtime(dest)


def convert_one(src_jpg: str, png_dir: str, webp_dir: str) -> tuple[bool, bool]:
    """Convert a single jpg to png/webp if the targets are missing or stale.

    Returns (converted_png, converted_webp).
    """
    base = os.path.splitext(os.path.basename(src_jpg))[0]
    png_path = os.path.join(png_dir, f"{base}.png")
    webp_path = os.path.join(webp_dir, f"{base}.webp")

    need_png = needs_conversion(src_jpg, png_path)
    need_webp = needs_conversion(src_jpg, webp_path)

    if not need_png and not need_webp:
        return False, False

    with Image.open(src_jpg) as img:
        img = img.convert("RGB")
        if need_png:
            os.makedirs(png_dir, exist_ok=True)
            img.save(png_path, "PNG")
        if need_webp:
            os.makedirs(webp_dir, exist_ok=True)
            img.save(webp_path, "WEBP", quality=85)

    return need_png, need_webp


def convert_brand(slug: str, images_root: str, verbose: bool = True) -> ConvertResult:
    jpg_dir = os.path.join(images_root, slug, "jpg")
    png_dir = os.path.join(images_root, slug, "png")
    webp_dir = os.path.join(images_root, slug, "webp")

    result = ConvertResult(slug=slug)

    if not os.path.isdir(jpg_dir):
        return result

    for fname in sorted(os.listdir(jpg_dir)):
        if not fname.lower().endswith((".jpg", ".jpeg")):
            continue
        src_jpg = os.path.join(jpg_dir, fname)
        try:
            converted_png, converted_webp = convert_one(src_jpg, png_dir, webp_dir)
            if converted_png or converted_webp:
                result.converted += 1
            else:
                result.up_to_date += 1
        except Exception as e:
            result.failed += 1
            result.failed_items.append((fname, str(e)))
            if verbose:
                print(f"[{slug}]   ! FAILED to convert {fname}: {e}")

    if verbose:
        print(
            f"[{slug}] converted={result.converted}, "
            f"up_to_date={result.up_to_date}, failed={result.failed}"
        )

    return result


def convert_all(brands: list[dict], images_root: str, verbose: bool = True) -> list[ConvertResult]:
    return [convert_brand(brand["slug"], images_root, verbose=verbose) for brand in brands]
