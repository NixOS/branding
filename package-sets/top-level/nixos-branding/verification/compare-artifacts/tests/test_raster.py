from pathlib import Path

from compare_artifacts.raster import RasterResult, compare_raster, render

SQUARE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect x="0" y="0" width="5" height="10" fill="black"/></svg>'
SQUARE_SHIFTED = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect x="1" y="0" width="5" height="10" fill="black"/></svg>'
TALL = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 20"><rect x="0" y="0" width="5" height="20" fill="black"/></svg>'


def write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_identical_renders_have_no_differing_pixels(tmp_path):
    a = write(tmp_path / "a.svg", SQUARE)
    render(a, tmp_path / "a.png", width=100)
    render(a, tmp_path / "b.png", width=100)
    assert compare_raster(tmp_path / "a.png", tmp_path / "b.png") == RasterResult(
        (100, 100), (100, 100), 0, 0
    )


def test_shifted_shape_counts_differing_pixels(tmp_path):
    render(write(tmp_path / "a.svg", SQUARE), tmp_path / "a.png", width=100)
    render(write(tmp_path / "b.svg", SQUARE_SHIFTED), tmp_path / "b.png", width=100)
    result = compare_raster(tmp_path / "a.png", tmp_path / "b.png")
    assert result.differing_pixels == 2000
    assert result.max_channel_delta == 255


def test_size_mismatch_is_reported(tmp_path):
    render(write(tmp_path / "a.svg", SQUARE), tmp_path / "a.png", width=100)
    render(write(tmp_path / "b.svg", TALL), tmp_path / "b.png", width=100)
    result = compare_raster(tmp_path / "a.png", tmp_path / "b.png")
    assert result.size_before == (100, 100)
    assert result.size_after == (100, 200)
    assert result.differing_pixels is None
