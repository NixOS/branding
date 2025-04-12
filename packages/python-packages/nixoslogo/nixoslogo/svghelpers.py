from dataclasses import dataclass

import svg


@dataclass(kw_only=True)
class ImageParameters:
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

    def make_svg_background(self, color="#8888ee"):  # TODO: delete
        return [
            svg.Rect(
                x=self.min_x,
                y=self.min_y,
                width=self.width,
                height=self.height,
                fill=color,
            ),
        ]
