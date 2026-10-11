import math
from collections.abc import Sequence
from typing import overload, override

from svg._types import Number


def cosd(angle: float) -> float:
    return math.cos(math.radians(angle))


def sind(angle: float) -> float:
    return math.sin(math.radians(angle))


class Point(Sequence[float]):
    def __init__(self, value: Sequence[float]):
        self.value: Sequence[float] = value
        super().__init__()

    @overload
    def __getitem__(self, index: int) -> float: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[float]: ...

    @override
    def __getitem__(self, index: int | slice) -> "float | Sequence[float]":
        return self.value[index]

    @override
    def __len__(self):
        return len(self.value)

    @override
    def __str__(self):
        return f"{self.x, self.y}"

    @override
    def __repr__(self):
        return f"Point{self.value}"

    def __neg__(self):
        return Point(tuple(-elem for elem in self))

    def __add__(self, other: "Point | Vector") -> "Point":
        if isinstance(other, Point):
            return Point((self.x + other.x, self.y + other.y))
        if isinstance(other, Vector):
            return Point((self.x + other[0], self.y + other[1]))
        return NotImplemented

    @overload
    def __sub__(self, other: "Point") -> "Vector": ...

    @overload
    def __sub__(self, other: "Vector") -> "Point": ...

    def __sub__(self, other: "Point | Vector") -> "Point | Vector":
        if isinstance(other, Point):
            return Vector((self.x - other.x, self.y - other.y))
        if isinstance(other, Vector):
            return Point((self.x - other[0], self.y - other[1]))
        return NotImplemented

    def __truediv__(self, other: float) -> "Point":
        return Point(tuple(elem / other for elem in self))

    @property
    def x(self):
        """The x property."""
        return self.value[0]

    @property
    def y(self):
        """The y property."""
        return self.value[1]

    def distance(self, other: "Point") -> float:
        return (self - other).length()

    def normal(self, reference: "Point") -> "Vector":
        normal = Vector(
            (
                +(self.y - reference.y),
                -(self.x - reference.x),
            )
        )
        return normal.normalize()

    def rotate(self, angle: float) -> "Point":
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


class Points(Sequence[Point]):
    def __init__(self, value: list[Point]):
        self.value: list[Point] = value
        super().__init__()

    @overload
    def __getitem__(self, index: int) -> Point: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Point]: ...

    @override
    def __getitem__(self, index: int | slice) -> "Point | Sequence[Point]":
        return self.value[index]

    @override
    def __len__(self):
        return len(self.value)

    @override
    def __repr__(self):
        return f"Points{self.value}"

    @override
    def __str__(self):
        return "[" + ", ".join(str(elem) for elem in self.value) + "]"

    def to_list(self) -> list[Number]:
        nested = [(elem.x, elem.y) for elem in self]
        flat: list[Number] = [elem for point in nested for elem in point]
        return flat


class Vector(Sequence[float]):
    def __init__(self, value: Sequence[float]):
        self.value: Sequence[float] = value
        super().__init__()

    @overload
    def __getitem__(self, index: int) -> float: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[float]: ...

    @override
    def __getitem__(self, index: int | slice) -> "float | Sequence[float]":
        return self.value[index]

    @override
    def __len__(self):
        return len(self.value)

    @override
    def __repr__(self):
        return f"Vector{self.value}"

    @override
    def __str__(self):
        return f"{self.value}"

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(tuple(s + o for s, o in zip(self, other)))

    def __neg__(self):
        return Vector(tuple(-elem for elem in self))

    def __sub__(self, other: "Vector") -> "Vector":
        return self + (-other)

    def __mul__(self, other: "Vector") -> "Vector":
        return Vector(tuple(s * o for s, o in zip(self, other)))

    def __rmul__(self, other: float) -> "Vector":
        return Vector(tuple(other * elem for elem in self))

    def __matmul__(self, other: "Point | Vector") -> list[float]:
        if not isinstance(other, Point | Vector):
            return NotImplemented
        return [s * o for s, o in zip(self, other)]

    def __truediv__(self, other: float) -> "Vector":
        return Vector(tuple(elem / other for elem in self))

    def _modulus_squared(self) -> float:
        return self.dot(self)

    def length(self) -> float:
        return math.sqrt(self._modulus_squared())

    def dot(self, other: "Vector") -> float:
        return sum(self * other)

    def normalize(self) -> "Vector":
        return self / self.length()

    def normal(self) -> "Vector":
        return Vector((self[1], -self[0])).normalize()

    def angle_from(self, other: "Vector") -> float:
        return math.acos(self.dot(other) / (self.length() * other.length()))

    def to_point(self) -> Point:
        return Point(self.value)


class Matrix(Sequence[Vector]):
    def __init__(self, value: Sequence[Vector]):
        self.value: Sequence[Vector] = value
        super().__init__()

    @overload
    def __getitem__(self, index: int) -> Vector: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Vector]: ...

    @override
    def __getitem__(self, index: int | slice) -> "Vector | Sequence[Vector]":
        return self.value[index]

    @override
    def __len__(self):
        return len(self.value) * len(self.value[0])

    @override
    def __str__(self):
        return "(" + ",\n ".join(str(elem) for elem in self.value) + ")"

    def transpose(self) -> "Matrix":
        return Matrix(tuple(Vector(row) for row in zip(*self)))

    def __matmul__(self, other: Point | Vector) -> list[float]:
        if not isinstance(other, Point | Vector):
            return NotImplemented
        return [sum(row @ other) for row in self]
