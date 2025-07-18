import atexit
import logging
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import fontforge
import svg

from nixoslogo.core import (
    DEFAULT_LOGOTYPE_SPACINGS,
    DEFAULT_ROUTE159_TRANSFORMS,
    NIXOS_DARK_BLUE,
    NIXOS_LIGHT_BLUE,
    BaseRenderable,
    ClearSpace,
    LogotypeStyle,
    get_nixos_logotype_font_file,
)
from nixoslogo.logging_config import setup_logging

logger = logging.getLogger(__name__)


class FontLoader:
    def __init__(
        self,
        get_font_file: Callable[[], Path] = get_nixos_logotype_font_file,
        transforms_map: dict[str, Any] = DEFAULT_ROUTE159_TRANSFORMS,
        capHeight: int | None = None,
        scale_glyph: bool = True,
        offset_glyph: bool = True,
    ):
        self.get_font_file = get_font_file
        self.transforms_map = transforms_map
        self.capHeight = capHeight
        self.scale_glyph = scale_glyph
        self.offset_glyph = offset_glyph

        self._open_font_file()
        self._setup_glyphs()

    def _open_font_file(self):
        source_path = self.get_font_file()
        logger.debug(f"Original font file: {source_path}")
        self._tempdir = Path(tempfile.mkdtemp(prefix="fontforge_"))
        logger.debug(f"Temporary directory created: {self._tempdir}")
        self._font_path = self._tempdir / source_path.name
        shutil.copy2(source_path, self._font_path)
        logger.debug(f"Font file copied: {self._font_path}")

        self.font = fontforge.open(str(self._font_path))
        logger.debug(f"Font file loaded: {self._font_path}")
        self._cleaned_up = False

        # Register the cleanup function to be called when the Python process exits
        atexit.register(self._cleanup_once)

    def _setup_glyphs(self):
        self._set_ref_size()

        for character, transforms in self.transforms_map.items():
            if self.scale_glyph:
                self._scale_glyph(character, transforms)
            if self.offset_glyph:
                self._offset_glyph(character, transforms)

    def _set_ref_size(self):
        """
        Conditionally update the font size.

        The glyphs can be scaled by updating the `em` attribute.
        `capHeight` goes to zero because we are flipping glyphs so that is stored off for later use.
        """
        if self.capHeight is None:
            self.scale = 1
            self.capHeight = int(self.font.capHeight)
        else:
            self.scale = self.capHeight / self.font.capHeight
            self.font.em = round(self.font.em * self.scale)

    def _scale_glyph(self, character, transforms):
        """Scale a glyph; primarily used for vertically flipping."""
        self.font[character].transform(
            (
                transforms["scale_x"],
                0,
                0,
                transforms["scale_y"],
                0,
                0,
            )
        )

    def _offset_glyph(self, character, transforms):
        """Offset a glyph; primarily used to remove the left side bearing."""
        self.font[character].transform(
            (
                1,
                0,
                0,
                1,
                -self.font[character].left_side_bearing,
                0,
            )
        )

    def cleanup(self):
        """Manual cleanup method."""
        logger.debug(f"Manual cleanup for font file: {self._font_path}")
        self._cleanup_once()

    def _cleanup_once(self):
        """Ensure cleanup happens only once."""
        if self._cleaned_up:
            return
        self._cleaned_up = True
        try:
            # Close the font file if it's open
            self.font.close()
            logger.debug(f"Font file closed: {self._font_path}")
        except Exception as e:
            logger.error(f"Error closing font file: {self._font_path}, {e}")
        # Remove the temporary directory and its contents
        try:
            shutil.rmtree(self._tempdir, ignore_errors=True)
            logger.debug(f"Temporary directory removed: {self._tempdir}")
        except Exception as e:
            logger.error(f"Error removing temporary directory: {self._tempdir}, {e}")

    def __del__(self):
        """Fallback cleanup in case it's not done manually."""
        self._cleanup_once()


class Glyph(BaseRenderable):
    def __init__(
        self,
        character: str | None,
        loader: FontLoader | None = None,
        color: str = "black",
        style: LogotypeStyle = LogotypeStyle.REGULAR,
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        **kwargs,
    ):
        self.character = character
        self.loader = loader
        self.color = color
        self.style = style
        self.clear_space = clear_space

        self._init_loader()
        self.font = self.loader.font
        self.glyph = self.font[self.character]
        self.layer = self.glyph.foreground.dup()

        super().__init__(**kwargs)

    def _init_loader(self):
        if self.loader is None:
            self.loader = FontLoader()

    def get_path(self, layer):
        path = []
        for contour in layer:
            first_iteration = True
            points = list(contour)

            # If last point is a control point
            if not points[-1].on_curve:
                points.append(points[0])

            while points:
                # First iteration of a contour should always be a move.
                if first_iteration:
                    point = points.pop(0)
                    element = svg.MoveTo(point.x, point.y)
                    path.append(element)
                    first_iteration = False
                    continue

                if points[0].on_curve:
                    # If the next point is on curve, it is a straight line from the previous point.
                    point = points.pop(0)
                    element = svg.LineTo(point.x, point.y)
                    path.append(element)
                    continue
                if not points[0].on_curve and points[1].on_curve:
                    # If the next point is off curve and the following point is on curve,
                    # it is a quadratic Bézier curve. So take the next 2 points.
                    points_bezier = [
                        elem
                        for pair in (
                            (point.x, point.y)
                            for point in (points.pop(0) for _ in range(2))
                        )
                        for elem in pair
                    ]
                    element = svg.QuadraticBezier(*points_bezier)
                    path.append(element)
                else:
                    # If the next two points are off curve, it is a cubic Bézier curve.
                    # So take the next 3 points.
                    points_bezier = [
                        elem
                        for pair in (
                            (point.x, point.y)
                            for point in (points.pop(0) for _ in range(3))
                        )
                        for elem in pair
                    ]
                    element = svg.CubicBezier(*points_bezier)
                    path.append(element)

        return path

    @property
    def elements_bounding_box(self):
        return self.layer.boundingBox()

    def _get_clearspace(self):
        match self.clear_space:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return self.loader.capHeight / 2
            case ClearSpace.RECOMMENDED:
                return self.loader.capHeight
            case _:
                raise Exception("Unknown ClearSpace")

    def make_svg_element(self):
        match self.style:
            case LogotypeStyle.REGULAR:
                return svg.Path(
                    d=self.get_path(self.layer),
                    fill=self.color,
                )
            case LogotypeStyle.LAMBDAPRIME:
                if self.character == "x":
                    upper = [self.layer[0][:2] + self.layer[0][10:]]
                    lower = [self.layer[0][2:10]]
                    return [
                        svg.Path(
                            d=self.get_path(upper),
                            fill=NIXOS_LIGHT_BLUE.convert("srgb").to_string(hex=True),
                        ),
                        svg.Path(
                            d=self.get_path(lower),
                            fill=NIXOS_DARK_BLUE.convert("srgb").to_string(hex=True),
                        ),
                    ]
                else:
                    return svg.Path(
                        d=self.get_path(self.layer),
                        fill=self.color,
                    )
            case _:
                raise Exception("Unknown LogotypeStyle")

    def make_svg_elements(self):
        return (self.make_svg_element(),)

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                "nixos",
                "glyph",
                self.character,
                self.color,
                self.style.name.lower(),
                self.clear_space.name.lower(),
            ]
            + list(extras)
        )


class Logotype(BaseRenderable):
    def __init__(
        self,
        characters: str = "NixOS",
        loader: FontLoader | None = None,
        color: str = "black",
        style: LogotypeStyle = LogotypeStyle.REGULAR,
        spacings: tuple[int] = DEFAULT_LOGOTYPE_SPACINGS,
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        **kwargs,
    ):
        self.loader = loader
        self.characters = characters
        self.loader = loader
        self.color = color
        self.style = style
        self.spacings = spacings
        self.clear_space = clear_space

        self._init_loader()
        self._load_glyphs()
        self.cap_height = self.glyphs[0].loader.capHeight
        self.scale = self.glyphs[0].loader.scale
        self._set_spacings()

        super().__init__(**kwargs)

    def _init_loader(self):
        if self.loader is None:
            self.loader = FontLoader()

    def _load_glyphs(self):
        self.glyphs = tuple(
            Glyph(
                loader=self.loader,
                character=character,
                color=self.color,
                style=self.style,
            )
            for character in self.characters
        )

    def _set_spacings(self):
        x_offset = 0
        for character, spacing in zip(self.glyphs, self.spacings):
            x_offset += spacing * self.scale
            character.layer.transform((1, 0, 0, 1, x_offset, 0))
            x_offset += character.elements_width

    def _get_clearspace(self):
        match self.clear_space:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return self.cap_height / 2
            case ClearSpace.RECOMMENDED:
                return self.cap_height
            case _:
                raise Exception("Unknown ClearSpace")

    @property
    def elements_bounding_box(self):
        characters_box = tuple(
            f(elem)
            for f, elem in zip(
                (min, min, max, max),
                list(zip(*(elem.elements_bounding_box for elem in self.glyphs))),
            )
        )
        with_lead_spacing = (characters_box[0] - self.spacings[0],) + characters_box[1:]
        return with_lead_spacing

    def make_svg_elements(self):
        return tuple(elem.make_svg_element() for elem in self.glyphs)

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                self.characters.lower(),
                "logotype",
                self.color,
                self.style.name.lower(),
                self.clear_space.name.lower(),
            ]
            + list(extras)
        )


if __name__ == "__main__":
    setup_logging(level=logging.DEBUG)
    loader = FontLoader()

    character = Glyph(loader=loader, character="x", background_color="#dddddd")
    character.write_svg(filename=character.make_filename(extras=("test",)))

    logotype = Logotype(loader=loader, background_color="#dddddd")
    logotype.write_svg(filename=logotype.make_filename(extras=("test",)))

    loader.cleanup()
