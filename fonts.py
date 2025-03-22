from pathlib import Path

import freetype
import svg
from freetype import Face, Matrix, Vector

# face = Face("./vegur.602/Vegur-Regular-0.602.otf")
#
# face.set_transform(
#     Matrix(
#         1 * 0x10000,
#         0 * 0x10000,
#         0 * 0x10000,
#         -1 * 0x10000,
#     ),
#     Vector(
#         0,
#         0,
#     ),
#     # Vector(
#     #     0,
#     #     400,
#     # ),
# )
#
# # face.set_char_size(48 * 64)  # Sets the font size
# face.set_char_size(8 * 64)  # Sets the font size
# # face.set_char_size(height=150, hres=300, vres=300)  # Sets the font size
# # face.set_pixel_sizes(4, 4)  # Sets the font size
#
#
# face.load_char("N")  # Loads the character 'a'
#
#
# def move_to(a, ctx):
#     # ctx.append("M {},{}".format(a.x, a.y))
#     ctx.append(svg.MoveTo(a.x, a.y))
#
#
# def line_to(a, ctx):
#     # ctx.append("L {},{}".format(a.x, a.y))
#     ctx.append(svg.LineTo(a.x, a.y))
#
#
# def conic_to(a, b, ctx):
#     # ctx.append("Q {},{} {},{}".format(a.x, a.y, b.x, b.y))
#     ctx.append(svg.QuadraticBezier(a.x, a.y, b.x, b.y))
#
#
# def cubic_to(a, b, c, ctx):
#     # ctx.append("C {},{} {},{} {},{}".format(a.x, a.y, b.x, b.y, c.x, c.y))
#     ctx.append(svg.CubicBezier(a.x, a.y, b.x, b.y, c.x, c.y))
#
#
# outline = face.glyph.outline
# ctx = []
# outline.decompose(
#     ctx, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to
# )
#
# bbox = outline.get_bbox()
# print((bbox.xMin, bbox.yMin, bbox.xMax, bbox.yMax))
#
# # print(outline.contours)
# # print(outline.points)
# # print(outline.tags)
# # print(ctx)
#
# character = svg.SVG(
#     viewBox=svg.ViewBoxSpec(
#         min_x=-400,
#         min_y=-400,
#         width=800,
#         height=800,
#     ),
#     elements=[
#         svg.Rect(
#             x=0,
#             y=-400,
#             width=400,
#             height=400,
#             fill="#8888ee",
#         ),
#         svg.Path(
#             d=ctx,
#             transform=[
#                 svg.Scale(*(400 / (bbox.yMax - bbox.yMin),) * 2),
#                 svg.Translate(-bbox.xMin, -bbox.yMin * 0),
#             ],
#         ),
#     ],
# )
# print(character)
# with open(Path("character-N.svg"), "w") as file:
#     file.write(str(character))


class Character:
    def __init__(
        self,
        character,
        size=400,
        scale=None,
        font="./vegur.602/Vegur-Regular-0.602.otf",
        # font="./vegur_0701/Vegur-Regular.otf",
    ):
        self.size = size
        self._scale = scale
        self._setup_face(character=character, font=font)
        self._decompose_path()

    def _setup_face(self, character, font):
        self._face = Face(font)
        self._face.set_transform(
            Matrix(
                1 * 0x10000,
                0 * 0x10000,
                0 * 0x10000,
                -1 * 0x10000,
            ),
            Vector(
                0,
                0,
            ),
        )
        self._face.set_char_size(4 * 64)  # has the correct aspect ratio at 8 points
        self._face.load_char(
            character,
            freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_BITMAP,
        )
        self._outline = self._face.glyph.outline

    def _decompose_path(self):
        ctx = []

        def move_to(a, ctx):
            ctx.append(svg.MoveTo(a.x, a.y))

        def line_to(a, ctx):
            ctx.append(svg.LineTo(a.x, a.y))

        def conic_to(a, b, ctx):
            ctx.append(svg.QuadraticBezier(a.x, a.y, b.x, b.y))

        def cubic_to(a, b, c, ctx):
            ctx.append(svg.CubicBezier(a.x, a.y, b.x, b.y, c.x, c.y))

        self._outline.decompose(
            ctx, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to
        )
        self._path = ctx

    @property
    def bbox(self):
        return self._outline.get_bbox()

    @property
    def scale(self):
        if self._scale is not None:
            return self._scale
        return self.size / (self.bbox.yMax - self.bbox.yMin)

    @property
    def svg_width(self):
        return self.scale * (self.bbox.xMax - self.bbox.xMin)

    def make_svg(self):
        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=-self.size,
                min_y=-self.size,
                width=self.size * 2,
                height=self.size * 2,
            ),
            elements=[
                svg.Rect(  # TODO: delete
                    x=0,
                    y=-self.size,
                    width=self.size,
                    height=self.size,
                    fill="#8888ee",
                ),
                svg.Path(
                    d=self._path,
                    transform=[
                        svg.Scale(*(self.scale,) * 2),
                        svg.Translate(0 * -self.bbox.xMin, 0),
                    ],
                ),
                svg.Circle(
                    cx=self.bbox.xMin,
                    cy=self.bbox.yMin,
                    r=1,
                ),
                svg.Circle(
                    cx=self.bbox.xMax,
                    cy=self.bbox.yMax,
                    r=1,
                ),
            ],
        )


character = Character("N", scale=1)
# print(character.scale)
print(character.bbox.yMax - character.bbox.yMin)

# character = Character("O", scale=1)
# # print(character.scale)
# print(character.bbox.yMax - character.bbox.yMin)
#
# character = Character("O", scale=1)
# # print(character.scale)
# print(character.bbox.yMax - character.bbox.yMin)
# print(character.bbox.yMin)
# print(character.bbox.yMax)

with open(Path("character-N.svg"), "w") as file:
    file.write(str(character.make_svg()))
