import hashlib
import math
from typing import cast

import jsonpickle

from nixoslogo.geometry import Point


def stable_hash(thing: object) -> str:
    dump = cast(str, jsonpickle.encode(thing))
    return hashlib.md5(dump.encode("utf-8")).digest().hex()


def arc_sagitta(point1: Point, point2: Point, radius: float, large: bool, sweep: bool):
    chord_midpoint = ((point1 + point2) / 2).to_vector()
    chord = point2 - point1
    unit_chord = chord.normalize()
    chord_normal = unit_chord.normal()
    chord_length = chord.length()

    sagitta = radius - math.sqrt(radius**2 - chord_length**2 / 4)

    arc_center = (
        chord_midpoint
        + (sagitta - radius)
        * (-1 if large else +1)
        * (+1 if sweep else -1)
        * chord_normal
    )
    arc_midpoint = arc_center + radius * (+1 if sweep else -1) * chord_normal
    arc_midpoint_vector = (arc_midpoint - arc_center).normalize()
    return (arc_midpoint, arc_midpoint_vector)
