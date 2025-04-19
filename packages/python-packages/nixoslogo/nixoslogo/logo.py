import math
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import svg

from nixoslogo.colors import ColorStyle
from nixoslogo.logotype import (
    DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    Character,
    Characters,
    FontLoader,
)
from nixoslogo.snowflake import Lambda, SnowFlake
from nixoslogo.svghelpers import ImageParameters


class ClearSpace(Enum):
    NONE = auto()
    MINIMAL = auto()
    RECOMMENDED = auto()


@dataclass(kw_only=True)
class NixosLogo:
    radius: int = 512
    thickness: float = 1 / 4
    gap: float = 1 / 32
    color_style: ColorStyle = ColorStyle.GRADIENT
    capHeight: float | None = None
    characters: str = "NixOS"
    character_spacings: tuple[int] = DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING
    characters_transform: svg.Translate | None = None
    image_parameters: ImageParameters | None = None
    clear_space: ClearSpace = ClearSpace.RECOMMENDED

    def __post_init__(self):
        self._init_snowflake()
        self._init_capHeight()
        self._init_logotype()
        self._init_image_parameters()

    def _init_snowflake(self):
        self.ilambda = Lambda(
            radius=self.radius,
            thickness=self.thickness,
            gap=self.gap,
        )
        self.snowflake = SnowFlake(
            ilambda=self.ilambda,
            color_style=self.color_style,
        )

    def _init_capHeight(self):
        if self.capHeight is None:
            self.capHeight = self.radius * (1 + self.thickness * 2) * math.sqrt(3)

    def _init_logotype(self):
        self.loader = FontLoader(capHeight=self.capHeight)
        self.logotype = Characters(
            characters=[
                Character(character=letter, loader=self.loader)
                for letter in self.characters
            ],
            spacings=self.character_spacings,
        )

        if self.characters_transform is None:
            self.characters_transform = svg.Translate(
                9 / 4 * self.radius, self.capHeight / 2
            )

    @property
    def bounding_box(self):
        logomark_box = self.snowflake.bounding_box
        logotype_box = self.logotype.boundingBox
        logotype_box_translated = (
            logotype_box[0] + self.characters_transform.x,
            logotype_box[1] + self.characters_transform.y,
            logotype_box[2] + self.characters_transform.x,
            logotype_box[3] + self.characters_transform.y,
        )
        return [
            predicate(elem)
            for predicate, elem in zip(
                (min, min, max, max),
                list(zip(*(logomark_box, logotype_box_translated))),
            )
        ]

    def _init_image_parameters(self):
        if self.image_parameters is None:
            min_x, min_y, max_x, max_y = self.bounding_box

            clear_space = self._get_clearspace()
            min_x -= clear_space
            min_y -= clear_space
            max_x += clear_space
            max_y += clear_space

            width = max_x - min_x
            height = max_y - min_y

            self.image_parameters = ImageParameters(
                min_x=min_x,
                min_y=min_y,
                width=width,
                height=height,
            )

    def _get_clearspace(self):
        match self.clear_space:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return self.snowflake.radius * math.sqrt(3) / 4
            case ClearSpace.RECOMMENDED:
                return self.snowflake.radius * math.sqrt(3) / 2
            case _:
                raise Exception("Unknown ClearSpace")

    def make_svg_elements(self):
        return (
            self.snowflake.get_svg_elements(),
            svg.G(
                transform=[self.characters_transform],
                elements=(self.logotype.make_svg_elements()),
            ),
        )

    def make_svg(self):
        return svg.SVG(
            viewBox=self.image_parameters.make_view_box(),
            elements=self.make_svg_elements(),
        )

    def write_svg(self):
        with open(Path("test-logo.svg"), "w") as file:
            file.write(str(self.make_svg()))
