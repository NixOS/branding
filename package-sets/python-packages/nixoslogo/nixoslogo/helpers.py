import dataclasses
import hashlib
import math
from typing import Any, cast

import jsonpickle

from nixoslogo.geometry import Point


def stable_hash(thing: object) -> str:
    dump = cast(str, jsonpickle.encode(thing))
    return hashlib.md5(dump.encode("utf-8")).hexdigest()


SVG_NUMBER_DECIMALS = 6

# Decimals kept when serializing SVG numbers. Transcendental math (sin, cos,
# atan2, acos) in the standard library rounds differently between platforms,
# so unquantized values would make fixed-output derivations produce different
# hashes on different systems. The grid is coarse enough that such Ulp noise
# cannot move a value across the quantization boundary, so the serialized
# bytes stay identical everywhere.
SVG_NUMBER_QUANTUM = 10**-SVG_NUMBER_DECIMALS

# Insurance gap at the rounding boundary, in units of the quantization grid.
# Platform math noise (about 1e-13 on values up to 1e4) is four orders of
# magnitude below this gap, so both platforms apply the same boundary side.
SVG_NUMBER_BOUNDARY_GAP = 1e-3


def quantize_number(value: float) -> float:
    """Return the value snapped to the SVG number grid from one side.

    The floor-based rounding never jumps across the grid boundary from Ulp
    noise, and values exactly at a boundary are always mapped down, so both
    platforms serialize the same decimal for the same theoretical value.
    """

    if not math.isfinite(value):
        return value

    scaled = value / SVG_NUMBER_QUANTUM
    floor_point = math.floor(scaled + 0.5 - SVG_NUMBER_BOUNDARY_GAP)
    return round(floor_point * SVG_NUMBER_QUANTUM, SVG_NUMBER_DECIMALS)


def quantize_numbers(value: Any) -> Any:
    """Quantize every float serialized into an SVG."""

    if isinstance(value, float):
        return quantize_number(value)

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        changes = {
            field.name: quantize_numbers(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
        return dataclasses.replace(value, **changes)

    if type(value) is list:
        return [quantize_numbers(item) for item in value]

    if type(value) is tuple:
        return tuple(quantize_numbers(item) for item in value)

    return value


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
