"""Rasterised comparison of two SVG files with resvg and Pillow."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops


@dataclass(frozen=True)
class RasterResult:
    size_before: tuple[int, int]
    size_after: tuple[int, int]
    differing_pixels: int | None
    max_channel_delta: int | None


def render(svg_path: Path, png_path: Path, width: int = 1024) -> None:
    subprocess.run(
        ["resvg", "--width", str(width), str(svg_path), str(png_path)],
        check=True,
    )


def compare_raster(png_before: Path, png_after: Path) -> RasterResult:
    before = Image.open(png_before).convert("RGBA")
    after = Image.open(png_after).convert("RGBA")
    if before.size != after.size:
        return RasterResult(before.size, after.size, None, None)
    difference = ImageChops.difference(before, after)
    bands = difference.split()
    combined = bands[0]
    for band in bands[1:]:
        combined = ImageChops.lighter(combined, band)
    histogram = combined.histogram()
    differing = combined.size[0] * combined.size[1] - histogram[0]
    return RasterResult(before.size, after.size, differing, combined.getextrema()[1])
