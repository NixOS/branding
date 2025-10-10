import hashlib
from math import floor, log10, sqrt

import jsonpickle


def stable_hash(thing):
    dump = jsonpickle.encode(thing)
    return hashlib.md5(dump.encode("utf-8")).digest().hex()


def arc_sagitta(point1, point2, radius, large, sweep):
    chord_midpoint = ((point1 + point2) / 2).to_vector()
    chord = point2 - point1
    unit_chord = chord.normalize()
    chord_normal = unit_chord.normal()
    chord_length = chord.length()

    sagitta = radius - sqrt(radius**2 - chord_length**2 / 4)

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


def round_to_sigfig(x: int | float, s: int = 12):
    if x == 0:
        return 0
    else:
        return round(x, s - 1 - int(floor(log10(abs(x)))))
