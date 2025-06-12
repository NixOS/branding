import math

import svg
from svg._types import Number

from nixoslogo.annotations import Annotations
from nixoslogo.core import ClearSpace
from nixoslogo.geometry import Point, Points
from nixoslogo.layout import Canvas
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Lambda, Logomark
from nixoslogo.logotype import Logotype


class DimensionedLambda(Lambda):
    def __init__(
        self,
        annotations: Annotations,
        clear_space: ClearSpace = ClearSpace.NONE,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.annotations = annotations
        self.clear_space = clear_space

    def _init_canvas(self):
        if self.canvas is None:
            self.canvas = Canvas(
                min_x=-2 * self.radius,
                min_y=-2 * self.radius,
                width=4 * self.radius,
                height=4 * self.radius,
            )

    def make_diagonal_line(self, radius: Number) -> list[Number]:
        hexagon_points = self.make_hexagon_points(radius)
        return Points([hexagon_points[1], hexagon_points[4]])

    def make_lambda_construction_lines(self):
        return (
            svg.Circle(
                cx=0,
                cy=0,
                r=self.radius,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                fill=self.annotations.construction_lines.fill,
            ),
            svg.Polygon(
                points=self.make_hexagon_points(radius=self.radius).to_list(),
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                fill=self.annotations.construction_lines.fill,
            ),
        )

    def make_lambda_main_diagonal(self):
        return (
            svg.Polyline(
                points=self.make_diagonal_line(radius=self.radius).to_list(),
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                fill=self.annotations.construction_lines.fill,
            ),
        )

    def make_lambda_off_diagonal(self):
        lambda_points_gap = self.make_named_lambda_points()
        return (
            svg.Line(
                x1=Point((0, 0)).x,
                y1=Point((0, 0)).y,
                x2=lambda_points_gap["rear_foot"].x,
                y2=lambda_points_gap["rear_foot"].y,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
        )

    def make_lambda_polygons(self):
        lambda_points_no_gap = self.make_lambda_points(gap=0)
        lambda_points_gap = self.make_lambda_points()
        return (
            svg.Polygon(
                points=lambda_points_no_gap.to_list(),
                stroke=self.annotations.object_lines.stroke,
                stroke_width=self.annotations.object_lines.stroke_width,
                fill=self.annotations.object_lines.fill,
                stroke_dasharray=4,
            ),
            svg.Polygon(
                points=lambda_points_gap.to_list(),
                stroke=self.annotations.object_lines.stroke,
                stroke_width=self.annotations.object_lines.stroke_width,
                fill=self.annotations.object_lines.fill,
            ),
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                "nixos",
                "lambda",
                "dimensioned",
            ]
            + list(extras)
        )


class DimensionedLambdaLinear(DimensionedLambda):
    def make_lambda_linear_dimensions(self):
        hexagon_points = self.make_hexagon_points(radius=self.radius)
        lambda_points_no_gap = self.make_lambda_points(gap=0)
        lambda_points_gap = self.make_named_lambda_points()

        dim_main_diagonal = self.annotations.dimension_lines.make_dimension_line(
            point1=hexagon_points[1],
            point2=hexagon_points[4],
            flip=False,
            side="right",
            offset=1 / 2,
            reference=2 * self.radius,
        )

        dim_gap_diagonal = self.annotations.dimension_lines.make_dimension_line(
            point1=(
                lambda_points_gap["forward_tip"] + lambda_points_gap["forward_heel"]
            )
            / 2,
            point2=(lambda_points_gap["upper_notch"] + lambda_points_gap["upper_apex"])
            / 2,
            flip=False,
            side="right",
            offset=15 / 32,
            reference=2 * self.radius,
        )
        dim_gap_long_edge = self.annotations.dimension_lines.make_dimension_line(
            point1=lambda_points_gap["upper_apex"],
            point2=lambda_points_gap["forward_tip"],
            flip=True,
            side="right",
            offset=7 / 16,
            reference=2 * self.radius,
        )
        dim_gap_left_top = self.annotations.dimension_lines.make_dimension_line(
            point1=lambda_points_gap["midpoint_join"],
            point2=lambda_points_gap["upper_notch"],
            flip=False,
            side="right",
            offset=1 / 8,
            reference=2 * self.radius,
        )

        # fmt: off
        options = [
            {"side": "right", "flip": True,  "offset": 1 / 4},
            {"side": "right", "flip": True,  "offset": 15 / 32},
            {"side": "left",  "flip": True,  "offset": 1 / 4},
            {"side": "right", "flip": False, "offset": 1 / 4},
            {"side": "right", "flip": False, "offset": 1 / 4},
            {"side": "left",  "flip": True,  "offset": 1 / 2},
            {"side": "left",  "flip": True,  "offset": 1 / 2},
            {"side": "left",  "flip": False, "offset": 1 / 8},
            {"side": "left",  "flip": True,  "offset": 1 / 4},
        ]
        # fmt: on

        return (
            dim_main_diagonal,
            dim_gap_diagonal,
            dim_gap_long_edge,
            dim_gap_left_top,
        ) + tuple(
            self.annotations.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap[(index + 0) % 9],
                point2=lambda_points_no_gap[(index + 1) % 9],
                reference=2 * self.radius,
                **opts,
            )
            for index, opts in enumerate(options)
        )

    def make_svg_elements(self):
        return (
            self.canvas.make_axis_lines()
            + self.annotations.dimension_lines.make_dimension_arrow_defs()
            + self.make_lambda_construction_lines()
            + self.make_lambda_main_diagonal()
            + self.make_lambda_off_diagonal()
            + self.make_lambda_polygons()
            + self.make_lambda_linear_dimensions()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                super().make_filename(),
                "linear",
            ]
            + list(extras)
        )


class DimensionedLambdaAngular(DimensionedLambda):
    def make_lambda_angular_dimensions(self):
        lambda_points_no_gap = self.make_lambda_points()
        # fmt: off
        options = [
            {"flip": True,  "large": False, "side": "right", "ratio": 1 / 2, "text": "A"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "A"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 3 / 8, "text": "B"},
            {"flip": False, "large": False, "side": "right", "ratio": 1 / 2, "text": "A"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": False, "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 3 / 8, "text": "B"},
        ]
        # fmt: on

        return tuple(
            self.annotations.dimension_lines.make_dimension_angle(
                point1=lambda_points_no_gap[(index + 0) % 9],
                point2=lambda_points_no_gap[(index + 2) % 9],
                reference=lambda_points_no_gap[(index + 1) % 9],
                **opts,
            )
            for index, opts in enumerate(options)
        )

    def make_svg_elements(self) -> svg.SVG:
        return (
            self.canvas.make_axis_lines()
            + self.annotations.dimension_lines.make_dimension_arrow_defs()
            + self.make_lambda_construction_lines()
            + self.make_lambda_polygons()
            + self.make_lambda_angular_dimensions()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                super().make_filename(),
                "angular",
            ]
            + list(extras)
        )


class DimensionedLambdaAnnotatedVertices(DimensionedLambda):
    def make_dotted_lambda_vertices(self):
        return tuple(
            svg.Circle(
                cx=point.x,
                cy=point.y,
                r=self.radius / 96,
                fill=self.annotations.construction_lines.stroke,
            )
            for point in self.make_lambda_points()
        )

    def make_named_lambda_vertices(self):
        named_points = self.make_named_lambda_points()
        translations = [
            lambda elem: [
                svg.Translate(
                    -elem.elements_width - elem.elements_height / 2,
                    +elem.elements_height / 4,
                )
            ],
            lambda elem: [
                svg.Translate(
                    +elem.elements_height / 2,
                    +elem.elements_height / 4,
                )
            ],
            lambda elem: [
                svg.Translate(
                    +elem.elements_height / 4,
                    +elem.elements_height / 4,
                )
            ],
            lambda elem: [
                svg.Translate(
                    -elem.elements_width / 4,
                    +elem.elements_height * 5 / 4,
                )
            ],
            lambda elem: [
                svg.Translate(
                    -elem.elements_width - elem.elements_height / 2,
                    +elem.elements_height / 2,
                )
            ],
            lambda elem: [
                svg.Translate(
                    -elem.elements_width / 4,
                    +elem.elements_height * 5 / 4,
                )
            ],
            lambda elem: [
                svg.Translate(
                    -elem.elements_width - elem.elements_height / 4,
                    +elem.elements_height * 5 / 4,
                )
            ],
            lambda elem: [
                svg.Translate(
                    -elem.elements_width - elem.elements_height / 2,
                    +elem.elements_height / 4,
                )
            ],
            lambda elem: [
                svg.Translate(
                    -elem.elements_width - elem.elements_height * 3 / 4,
                    -elem.elements_height / 4,
                )
            ],
        ]
        named_annotations = {
            name: (
                point,
                self.annotations.make_annotation(text=(f"{name}").replace("_", " ")),
                translation,
            )
            for (name, point), translation in zip(named_points.items(), translations)
        }
        return tuple(
            svg.G(
                transform=[
                    svg.Translate(point.x, point.y),
                ]
                + translation(annotation),
                elements=annotation.make_svg_elements(),
            )
            for point, annotation, translation in named_annotations.values()
        )

    def make_svg_elements(self) -> svg.SVG:
        return (
            self.canvas.make_axis_lines()
            + self.make_lambda_construction_lines()
            + self.make_lambda_main_diagonal()
            + self.make_lambda_off_diagonal()
            + self.make_lambda_polygons()
            + self.make_dotted_lambda_vertices()
            + self.make_named_lambda_vertices()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                super().make_filename(),
                "annotated",
                "vertices",
            ]
            + list(extras)
        )


class DimensionedLambdaAnnotatedParameters(DimensionedLambda):
    def make_parametric_annotations(self):
        hexagon_points = self.make_hexagon_points(radius=self.radius)
        lambda_points_no_gap = self.make_named_lambda_points(gap=0)
        lambda_points_gap = self.make_named_lambda_points()

        radius = self.annotations.dimension_lines.make_dimension_line(
            point1=Point((0, 0)),
            point2=hexagon_points[5],
            flip=False,
            side="left",
            offset=0,
            text="radius",
        )

        thickness_points = [
            Point((0, 0)),
            Point((self.radius * self.thickness, 0)),
            Point(
                (
                    self.radius * self.thickness * math.cos(math.radians(60)),
                    self.radius * self.thickness * math.sin(math.radians(60)),
                )
            ),
            Point(lambda_points_gap["joint_crotch"]),
            (lambda_points_gap["midpoint_join"] + lambda_points_gap["joint_crotch"])
            / 2,
            Point(lambda_points_gap["midpoint_join"]),
        ]
        thickness_annotation = self.annotations.make_annotation(text="thickness")
        thickness = tuple(
            self.annotations.dimension_lines.make_dimension_line(
                point1=thickness_points[(index + 0) % len(thickness_points)],
                point2=thickness_points[(index + 1) % len(thickness_points)],
                flip=False,
                side="left",
                offset=0,
                text="",
            )
            for index in range(len(thickness_points))
        ) + (
            svg.G(
                transform=[
                    svg.Translate(*thickness_points[3]),
                    svg.Translate(
                        -thickness_annotation.elements_width
                        - thickness_annotation.elements_height / 2,
                        +thickness_annotation.elements_height / 2,
                    ),
                ],
                elements=thickness_annotation.make_svg_elements(),
            ),
        )

        gap = self.annotations.dimension_lines.make_dimension_line_outer(
            point1=(lambda_points_gap["upper_notch"] + lambda_points_gap["upper_apex"])
            / 2,
            point2=(
                lambda_points_no_gap["upper_notch"] + lambda_points_no_gap["upper_apex"]
            )
            / 2,
            flip=True,
            side="left",
            offset=0,
            text="gap",
            text_offset=True,
        )

        return radius + thickness + gap

    def make_svg_elements(self) -> svg.SVG:
        return (
            self.canvas.make_axis_lines()
            + self.annotations.dimension_lines.make_dimension_arrow_defs()
            + self.make_lambda_construction_lines()
            + self.make_lambda_main_diagonal()
            + self.make_lambda_off_diagonal()
            + self.make_lambda_polygons()
            + self.make_parametric_annotations()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                super().make_filename(),
                "annotated",
                "parameters",
            ]
            + list(extras)
        )


class DimensionedLogomark(Logomark):
    def __init__(
        self,
        annotations: Annotations,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.annotations = annotations

    def _init_canvas(self):
        if self.canvas is None:
            self.canvas = Canvas(
                min_x=-4 * self.ilambda.radius,
                min_y=-4 * self.ilambda.radius,
                width=8 * self.ilambda.radius,
                height=8 * self.ilambda.radius,
            )

    def make_flake_construction_lines(self):
        return (
            svg.Circle(
                cx=0,
                cy=0,
                r=self.ilambda.radius * 2.25,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                fill=self.annotations.construction_lines.fill,
            ),
            svg.Polygon(
                points=self.ilambda.make_hexagon_points(
                    radius=self.ilambda.radius * 2.25
                ).to_list(),
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                fill=self.annotations.construction_lines.fill,
            ),
            svg.Polyline(
                points=self.ilambda.make_diagonal_line(
                    radius=self.ilambda.radius * 2.25
                ).to_list(),
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                fill=self.annotations.construction_lines.fill,
            ),
        )

    def make_flake_linear_dimensions(self):
        flake_points = self.make_flake_points()
        hexagon_points = self.ilambda.make_hexagon_points(radius=self.ilambda.radius)

        lin_inner_hex_long_length = (
            self.annotations.dimension_lines.make_dimension_line(
                point1=hexagon_points[1],
                point2=hexagon_points[4],
                flip=False,
                side="right",
                offset=1 / 8,
                reference=2 * self.ilambda.radius,
            )
        )

        lin_flake_long_length = self.annotations.dimension_lines.make_dimension_line(
            point1=flake_points[2][6],
            point2=flake_points[5][6],
            flip=True,
            side="right",
            offset=1 / 2,
            reference=2 * self.ilambda.radius,
        )

        return (
            lin_inner_hex_long_length,
            lin_flake_long_length,
        )

    def make_flake_polygons_for_dimensions(self):
        flake_points = self.make_flake_points()

        return tuple(
            svg.Polygon(
                points=lambda_points.to_list(),
                stroke=self.ilambda.annotations.object_lines.stroke,
                stroke_width=self.ilambda.annotations.object_lines.stroke_width,
                fill=self.ilambda.annotations.object_lines.fill,
            )
            for lambda_points in flake_points
        )

    def make_svg_elements(self):
        return (
            self.make_flake_polygons_for_dimensions()
            + self.canvas.make_axis_lines()
            + self.annotations.dimension_lines.make_dimension_arrow_defs()
            + self.ilambda.make_lambda_construction_lines()
            + self.make_flake_construction_lines()
            + self.make_flake_linear_dimensions()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                "nixos",
                "logomark",
                "dimensioned",
                "linear",
            ]
            + list(extras)
        )


class DimensionedLogomarkGradient(Logomark):
    def __init__(
        self,
        annotations: Annotations,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.annotations = annotations

    def _init_canvas(self):
        if self.canvas is None:
            self.canvas = Canvas(
                min_x=-2 * self.ilambda.radius,
                min_y=-2 * self.ilambda.radius,
                width=4 * self.ilambda.radius,
                height=4 * self.ilambda.radius,
            )

    def make_dimensioned_gradient_lines(self):
        gradient_end_points = self.make_gradient_end_points()
        point_start = Point((gradient_end_points["x1"], gradient_end_points["y1"]))
        point_stop = Point((gradient_end_points["x2"], gradient_end_points["y2"]))
        point_vector = point_stop - point_start
        stop_points = [
            point_start + offset / 100 * point_vector
            for offset in self._gradient_stop_offsets
        ]

        text_annotations = [
            self.annotations.make_annotation(text=f"{offset}%")
            for offset in self._gradient_stop_offsets
        ]

        return tuple(
            [
                svg.Line(
                    **gradient_end_points,
                    stroke=self.annotations.construction_lines.stroke,
                    stroke_width=self.annotations.construction_lines.stroke_width,
                    stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                ),
            ]
            + [
                svg.Circle(
                    cx=stop_point.x,
                    cy=stop_point.y,
                    r=2 * self.annotations.construction_lines.stroke_width,
                    fill=self.annotations.construction_lines.stroke,
                )
                for stop_point in stop_points
            ]
            + [
                svg.G(
                    transform=[
                        svg.Translate(stop_point.x, stop_point.y),
                        svg.Translate(
                            text_annotation.elements_height / 4,
                            -text_annotation.elements_height / 4,
                        ),
                    ],
                    elements=text_annotation.make_svg_elements(),
                )
                for stop_point, text_annotation in zip(stop_points, text_annotations)
            ]
        )

    def make_svg_elements(self):
        return (
            self.canvas.make_axis_lines()
            + self.annotations.dimension_lines.make_dimension_arrow_defs()
            + self.ilambda.make_lambda_construction_lines()
            + self.ilambda.make_lambda_polygons()
            + self.make_dimensioned_gradient_lines()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                "nixos",
                "logomark",
                "dimensioned",
                "gradient",
            ]
            + list(extras)
        )


class DimensionedLogomarkGradientAnnotated(DimensionedLogomarkGradient):
    def make_gradient_annotations(self):
        gradient_end_points = self.make_gradient_end_points()
        point_start = Point((gradient_end_points["x1"], gradient_end_points["y1"]))
        point_stop = Point((gradient_end_points["x2"], gradient_end_points["y2"]))

        lambda_points_no_gap = self.ilambda.make_named_lambda_points(gap=0)
        return (
            self.annotations.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap["upper_notch"],
                point2=point_start,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.ilambda.radius,
                text="V",
            ),
            self.annotations.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap["upper_apex"],
                point2=point_start,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.ilambda.radius,
                text="H",
            ),
            self.annotations.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap["joint_crotch"],
                point2=point_stop,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.ilambda.radius,
                text="H",
            ),
        )

    def make_svg_elements(self):
        return super().make_svg_elements() + self.make_gradient_annotations()

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                super().make_filename(),
                "annotated",
            ]
            + list(extras)
        )


class DimensionedLogomarkGradientBackground(DimensionedLogomarkGradient):
    def make_svg_elements(self):
        return (
            self.make_flake_gradients_defs()
            + self.canvas.make_svg_background(fill=f"url(#{self.css_color_names[0]})")
            + super().make_svg_elements()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                super().make_filename(),
                "background",
            ]
            + list(extras)
        )


class DimensionedLogotype(Logotype):
    def __init__(
        self,
        annotations: Annotations,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.annotations = annotations

    def svg_bounding_box(self):
        bbox = self.elements_bounding_box

        return (
            svg.Rect(
                x=bbox[0],
                y=bbox[1],
                width=self.elements_width,
                height=self.elements_height,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
                fill="transparent",
            ),
            self.annotations.dimension_lines.make_dimension_line(
                point1=Point((self.elements_x_max, self.elements_y_min)),
                point2=Point((self.elements_x_min, self.elements_y_min)),
                flip=False,
                side="right",
                offset=1 / 16,
                reference=self.cap_height,
                fractional=False,
            ),
            self.annotations.dimension_lines.make_dimension_line(
                point1=Point((self.elements_x_max, self.elements_y_max)),
                point2=Point((self.elements_x_max, self.elements_y_min)),
                flip=False,
                side="right",
                offset=1 / 4,
                reference=self.cap_height,
                fractional=False,
            ),
        )

    def dimension_cap_height(self):
        point1 = Point((self.glyphs[0].elements_x_min, self.glyphs[0].elements_y_min))
        point2 = Point((self.glyphs[0].elements_x_min, self.glyphs[0].elements_y_max))
        return (
            self.annotations.dimension_lines.make_dimension_line(
                point1=point1,
                point2=point2,
                flip=False,
                side="right",
                offset=1 / 4,
                reference=self.cap_height,
            ),
        )

    def dimension_spacings(self):
        points = [
            (
                Point((self.glyphs[index + 0].elements_x_max, self.elements_y_min)),
                Point((self.glyphs[index + 1].elements_x_min, self.elements_y_min)),
            )
            for index in range(4)
        ]
        offsets = [
            self.cap_height / (point1 - point2).length() for point1, point2 in points
        ]
        sides = ["left", "right", "right", "right"]
        return tuple(
            self.annotations.dimension_lines.make_dimension_line(
                point1=point1,
                point2=point2,
                flip=False,
                side=side,
                offset=offset,
                reference=self.cap_height,
                text_offset=True,
                fractional=False,
            )
            for (point1, point2), offset, side in zip(points, offsets, sides)
        )

    def make_svg_elements(self):
        return (
            self.svg_bounding_box()
            + self.dimension_cap_height()
            + self.dimension_spacings()
            + super().make_svg_elements()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                "nixos",
                "logotype",
                "dimensioned",
            ]
            + list(extras)
        )


class DimensionedLogo(NixosLogo):
    def __init__(
        self,
        annotations: Annotations,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.annotations = annotations

    def dimension_cap_height(self):
        return (
            svg.Line(
                x1=self.canvas.min_x,
                y1=-self.logotype_cap_height / 2,
                x2=self.canvas.max_x,
                y2=-self.logotype_cap_height / 2,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Line(
                x1=self.canvas.min_x,
                y1=self.logotype_cap_height / 2,
                x2=self.canvas.max_x,
                y2=self.logotype_cap_height / 2,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
        )

    def dimension_bearing(self):
        return (
            self.annotations.dimension_lines.make_dimension_line(
                point1=Point((self.logomark.circumradius, 0)),
                point2=Point(
                    (
                        self.logomark.circumradius
                        + self.logotype.scale * self.logotype_spacings[0],
                        0,
                    )
                ),
                offset=2.5,
                reference=self.logotype_cap_height,
                text_offset=True,
                fractional=False,
            ),
        )

    def make_svg_elements(self):
        return (
            self.dimension_cap_height()
            + self.dimension_bearing()
            + super().make_svg_elements()
        )

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return "-".join(
            [
                "nixos",
                "logo",
                "dimensioned",
            ]
            + list(extras)
        )


if __name__ == "__main__":
    from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS
    from nixoslogo.logotype import FontLoader

    annotations = Annotations.small()
    annotations.construction_lines.stroke = "black"
    annotations.construction_lines.stroke_dasharray = 16

    loader = FontLoader(capHeight=512)

    artifact = DimensionedLogotype(
        loader=loader,
        spacings=DEFAULT_LOGOTYPE_SPACINGS,
        clear_space=ClearSpace.MINIMAL,
        annotations=annotations,
        background_color="#dddddd",
    )
    artifact.write_svg(filename=artifact.make_filename(extras=("test",)))

    annotations = Annotations.large()
    annotations.construction_lines.stroke = "black"
    artifact = DimensionedLogo(
        clear_space=ClearSpace.MINIMAL,
        annotations=annotations,
        background_color="#dddddd",
    )
    artifact.write_svg(filename=artifact.make_filename(extras=("test",)))
