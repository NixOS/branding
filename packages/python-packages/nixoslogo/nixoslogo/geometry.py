import math
from collections.abc import Sequence
from typing import Self

from svg._types import Number


def cosd(angle) -> float:
    return math.cos(math.radians(angle))


def sind(angle) -> float:
    return math.sin(math.radians(angle))


class Point(Sequence):
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return f"{self.x, self.y}"

    def __repr__(self):
        return f"Point{self.value}"

    def __neg__(self):
        return Point(tuple(-elem for elem in self))

    def __add__(self, other: Self | "Vector") -> Self:
        if isinstance(other, Point):
            return Point((self.x + other.x, self.y + other.y))
        elif isinstance(other, Vector):
            return Point((self.x + other[0], self.y + other[1]))
        else:
            raise Exception(f"Not sure how to add {type(other)} to Point.")

    def __sub__(self, other: Self | "Vector") -> Self:
        if isinstance(other, Point):
            return Vector((self.x - other.x, self.y - other.y))
        elif isinstance(other, Vector):
            return Point((self.x - other[0], self.y - other[1]))
        else:
            raise Exception(f"Not sure how to add {type(other)} to Point.")

    def __truediv__(self, other: Number) -> Self:
        return Point(tuple(elem / other for elem in self))

    @property
    def x(self):
        """The x property."""
        return self.value[0]

    @property
    def y(self):
        """The y property."""
        return self.value[1]

    def distance(self, other: Self) -> float:
        return (self - other).length()

    def normal(self, reference: Self):
        normal = Vector(
            (
                +(self.y - reference.y),
                -(self.x - reference.x),
            )
        )
        return normal.normalize()

    def rotate(self, angle: Number):
        rotation_matrix = Matrix(
            (
                Vector(
                    (cosd(angle), sind(-angle)),
                ),
                Vector(
                    (sind(angle), cosd(angle)),
                ),
            )
        )
        return Point(rotation_matrix @ self)

    def to_vector(self) -> "Vector":
        return Vector(self.value)


class Points(Sequence):
    def __init__(self, value: list[Point]):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return f"Points{self.value}"

    def __str__(self):
        return "[" + ", ".join(str(elem) for elem in self.value) + "]"

    def to_list(self):
        nested = [(elem.x, elem.y) for elem in self]
        return [elem for point in nested for elem in point]


class Vector(Sequence):
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return f"Vector{self.value}"

    def __str__(self):
        return f"{self.value}"

    def __add__(self, other: Self) -> Self:
        return Vector(tuple(s + o for s, o in zip(self, other)))

    def __neg__(self):
        return Vector(tuple(-elem for elem in self))

    def __sub__(self, other: Self) -> Self:
        return self + (-other)

    def __mul__(self, other: Self) -> Self:
        return Vector(tuple(s * o for s, o in zip(self, other)))

    def __rmul__(self, other: Number) -> Self:
        return Vector(tuple(other * elem for elem in self))

    def __matmul__(self, other: Self | Point) -> Self:
        if isinstance(other, Point | Vector):
            return [s * o for s, o in zip(self, other)]
        else:
            raise Exception(f"Not sure how to add {type(other)} to Point.")

    def __truediv__(self, other: Number) -> Self:
        return Vector(tuple(elem / other for elem in self))

    def _modulus_squared(self) -> Number:
        return self.dot(self)

    def length(self) -> float:
        return math.sqrt(self._modulus_squared())

    def dot(self, other: Self) -> float:
        return sum((self * other))

    def normalize(self) -> Self:
        return self / self.length()

    def normal(self) -> Self:
        return Vector((self[1], -self[0])).normalize()

    def angle_from(self, other: Self) -> float:
        return math.acos(self.dot(other) / (self.length() * other.length()))

    def to_point(self) -> Point:
        return Point(self.value)


class Matrix(Sequence):
    def __init__(self, value: Sequence[Vector]):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value) * len(self.value[0])

    def __str__(self):
        return "(" + ",\n ".join(str(elem) for elem in self.value) + ")"

    def transpose(self) -> Self:
        return Matrix(tuple(zip(*self)))

    def __matmul__(self, other: Point | Vector) -> Self:
        if isinstance(other, Point | Vector):
            return [sum(row @ other) for row in self]
        else:
            raise Exception(
                f"Not sure how to matrix multiply {type(self)} and {type(other)}."
            )
