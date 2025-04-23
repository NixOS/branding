from dataclasses import dataclass
from enum import Enum, auto

import svg


class ClearSpace(Enum):
    NONE = auto()
    MINIMAL = auto()
    RECOMMENDED = auto()


@dataclass(kw_only=True)
class Canvas:
    min_x: int
    min_y: int
    width: int
    height: int

    def make_view_box(self):
        return svg.ViewBoxSpec(
            min_x=self.min_x,
            min_y=self.min_y,
            width=self.width,
            height=self.height,
        )

    def make_svg_background(self, fill="#8888ee"):
        return (
            svg.Rect(
                x=self.min_x,
                y=self.min_y,
                width=self.width,
                height=self.height,
                fill=fill,
            ),
        )

    def make_axis_lines(self, color: str = "black"):
        return (
            svg.Line(
                x1=self.min_x,
                x2=self.min_x + self.width,
                y1=0,
                y2=0,
                stroke=color,
            ),
            svg.Line(
                x1=0,
                x2=0,
                y1=self.min_y,
                y2=self.min_y + self.height,
                stroke=color,
            ),
        )
