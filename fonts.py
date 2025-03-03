from pathlib import Path

import svg
from freetype import Face, Matrix, Vector

face = Face("./vegur.602/Vegur-Regular-0.602.otf")

face.set_transform(
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
    # Vector(
    #     0,
    #     400,
    # ),
)

# face.set_char_size(48 * 64)  # Sets the font size
face.set_char_size(1 * 64)  # Sets the font size
# face.set_char_size(height=150, hres=300, vres=300)  # Sets the font size
# face.set_pixel_sizes(4, 4)  # Sets the font size


face.load_char("N")  # Loads the character 'a'


def move_to(a, ctx):
    # ctx.append("M {},{}".format(a.x, a.y))
    ctx.append(svg.MoveTo(a.x, a.y))


def line_to(a, ctx):
    # ctx.append("L {},{}".format(a.x, a.y))
    ctx.append(svg.LineTo(a.x, a.y))


def conic_to(a, b, ctx):
    # ctx.append("Q {},{} {},{}".format(a.x, a.y, b.x, b.y))
    ctx.append(svg.QuadraticBezier(a.x, a.y, b.x, b.y))


def cubic_to(a, b, c, ctx):
    # ctx.append("C {},{} {},{} {},{}".format(a.x, a.y, b.x, b.y, c.x, c.y))
    ctx.append(svg.CubicBezier(a.x, a.y, b.x, b.y, c.x, c.y))


outline = face.glyph.outline
ctx = []
outline.decompose(
    ctx, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to
)

bbox = outline.get_bbox()
print((bbox.xMin, bbox.yMin, bbox.xMax, bbox.yMax))

# print(outline.contours)
# print(outline.points)
# print(outline.tags)
# print(ctx)

character = svg.SVG(
    viewBox=svg.ViewBoxSpec(
        min_x=0,
        min_y=0,
        width=400,
        height=400,
    ),
    elements=[
        svg.Rect(
            x=0,
            y=0,
            width=400,
            height=400,
            fill="#8888ee",
        ),
        svg.Path(
            d=ctx,
            transform=[
                svg.Scale(*(400 / (bbox.yMax - bbox.yMin),) * 2),
                svg.Translate(-bbox.xMin, -bbox.yMin),
            ],
        ),
    ],
)
print(character)
with open(Path("character-N.svg"), "w") as file:
    file.write(str(character))
