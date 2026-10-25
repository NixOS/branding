# nixoslogo Refactor Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the `nixoslogo` package (lazy canvas, one clear-space rule, keyword-only dataclasses, composition where inheritance was wrong, immutable annotation presets) and extend `compare-artifacts` with numeric and raster modes, with every one of the 96 shipped SVG artifacts byte-identical after every task.

**Architecture:** Seven commits on `djacu/architecture-refactor`, each independently mergeable. The oracle is the artifact build: the 96 fixed-output derivations pin the SVG bytes, so a byte change fails the build. A local harness runs the 96 scripts in seconds for fast feedback before the build. The comparison tool's own tests cover the one behaviour the artifacts cannot observe. The package gains no tests in this phase.

**Tech Stack:** Python 3.12+ dataclasses and TypedDict, svg-py, fontforge (still, in this phase), basedpyright, ruff, treefmt via `nix fmt`, Nix flake builds; Pillow and resvg for the comparison tool.

**Spec:** `docs/superpowers/specs/2026-10-11-nixoslogo-architecture-refactor-design.md` (sections 3, 5 steps 1 to 7, and 6). Phases 2 and 3 get their own plans once this one has landed.

## Global Constraints

- Branch: `djacu/architecture-refactor`. Never commit on `main`.
- Every task must leave all 96 artifacts byte-identical: the harness reports `identical=96`, and `nix build .#hydraJobs.nixos-branding.x86_64-linux.all-artifacts` succeeds without any `outputHash` change.
- Every task must pass: basedpyright at 0 errors on `package-sets/python-packages/nixoslogo/nixoslogo`; `nix run --inputs-from . nixpkgs#ruff -- check package-sets/python-packages/nixoslogo` clean; `nix fmt -- --fail-on-change` clean (run `nix fmt` first to format; the flag must come after the `--` separator). The `--inputs-from .` pins ruff to the flake's nixpkgs (0.14.7, the version treefmt runs); the registry's newer ruff adds rules such as B008 that the pinned one does not have, and the gate is defined by the pinned one.
- Some code blocks in this plan run past 88 columns. `nix fmt` wraps them, and the wrapped form is what gets committed; the pre-commit hook will reject the first commit attempt whenever that happens, which is why every commit step says to re-add and retry.
- Every commit: plain engineer voice, no thank-you lines, no bolded lead-ins, no em dashes, and the trailer `Assisted-by: Claude Code (claude-fable-5-1)` as the last line. The repo's pre-commit hook runs treefmt; if it reformats a file the commit aborts, so `git add` the file again and repeat the same `git commit`.
- `requires-python = ">=3.12"`; `typing.override` on every overriding method and property, as today.
- Fonts and the colour palette arrive through `NIXOS_LOGOTYPE_FONT_FILE`, `NIXOS_ANNOTATIONS_FONT_FILE` and `NIXOS_COLOR_PALETTE_FILE`, which the devshell sets. Run every Python command through `nix develop .#nixos-logo-dev --command ...` from the repo root.
- Do not touch `geometry.py`, `colors.py`, `helpers.py`, `layout.py`, the hexagon trigonometry, the gradient colours, `background_color`, `make_filename`, or the `__init__.py` logging call. No docstrings, no renames beyond those listed, no new abstractions.
- Scripts under `package-sets/top-level/nixos-branding/artifacts/` are edited only where a task lists them.

## Review Focus

The 96 artifacts are the test suite for this phase: every clear-space value, every preset, every override a script uses, the cap-height-512 logo and all three clearspace diagrams are among them, and a byte change fails the build. The five failure modes most likely to bite, and what catches each:

1. A subclass stops forwarding `clear_space` to the base, so every `NONE` and `MINIMAL` renderable comes out `RECOMMENDED`. The first implementation attempt of Task 1 did exactly this. Caught by the harness: 52 artifacts change filename and canvas.
1. An unannotated default redeclaration (`clear_space = ClearSpace.MINIMAL` without the type) is not a dataclass field, so the base default silently wins. Caught by the five misuse artifacts' canvases.
1. An override applied to the wrong group, or clobbering a sibling field, changes a stroke colour or width. Caught by the twelve annotation artifacts.
1. `dimension_spacings` generalised wrongly. Its only caller is the five-glyph `nixos-logotype-dimensioned` artifact, which pins the five-glyph case; no other length is shipped or tested, and the spec lists this class as NixOS-wordmark specific.
1. The numeric comparison treats an inserted element as a huge positional delta, or measures the parser's own depth tags. Not observable in any artifact; pinned by the comparison-tool tests in Task 7.

______________________________________________________________________

### Task 0: Fast harness

**Files:**

- Create (outside the repo, not committed): `/tmp/nixoslogo-harness/run-artifacts.sh`

**Interfaces:**

- Produces: `run-artifacts.sh`, which every later task runs. No commit: this phase adds nothing to the package that the artifacts cannot check, so there is no pytest suite and the devshell is unchanged. The spec's Phase 2 adds pytest with the font pipeline tests.

- [ ] **Step 1: Create the harness**

Create `/tmp/nixoslogo-harness/run-artifacts.sh`:

```bash
#!/usr/bin/env bash
# Run all 96 artifact scripts against the working tree and compare each
# output with the artifact built from main. Run inside the devshell:
#   nix develop .#nixos-logo-dev --command bash /tmp/nixoslogo-harness/run-artifacts.sh
set -euo pipefail
repo=$(git rev-parse --show-toplevel)
baseline=${BASELINE:-$(nix build "git+file://$repo?ref=main#hydraJobs.nixos-branding.x86_64-linux.all-artifacts" --no-link --print-out-paths | tail -1)}
out=$(mktemp -d)
identical=0
different=0
report=()
for script in "$repo"/package-sets/top-level/nixos-branding/artifacts/*/*/script.py; do
  name=$(basename "$(dirname "$script")")
  category=$(basename "$(dirname "$(dirname "$script")")")
  dir="$out/$name"
  mkdir -p "$dir"
  if ! (cd "$dir" && python "$script" >"$dir/log" 2>&1); then
    different=$((different + 1))
    report+=("CRASH $category/$name (see $dir/log)")
    continue
  fi
  # Seven scripts write a file named by make_filename rather than by their
  # directory (the coloredx logotypes write ...-lambdaprime-..., the lambda
  # background writes nixos-lambda-R512-T1_4-G0-none), so compare whatever
  # the script produced under that same basename in the baseline.
  produced=("$dir"/*.svg)
  if [ "${#produced[@]}" -ne 1 ] || [ ! -e "${produced[0]}" ]; then
    different=$((different + 1))
    report+=("NOSVG $category/$name")
    continue
  fi
  if cmp -s "${produced[0]}" "$baseline/$category/$(basename "${produced[0]}")"; then
    identical=$((identical + 1))
  else
    different=$((different + 1))
    report+=("DIFF  $category/$(basename "${produced[0]}")")
  fi
done
echo "identical=$identical different=$different baseline=$baseline"
printf '%s\n' "${report[@]}"
```

- [ ] **Step 2: Run the harness on the unmodified tree**

Run: `nix develop .#nixos-logo-dev --command bash /tmp/nixoslogo-harness/run-artifacts.sh`
Expected: `identical=96 different=0` and no report lines. If a script crashes, the devshell environment is wrong; fix that before continuing.

### Task 1: `Shape`, `ClearSpace.distance`, lazy canvas

**Files:**

- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/core.py:17-27` (types), `:158-162` (ClearSpace), `:187-282` (base class)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/logotype.py:140-160, 221-229, 277-300, 320-328`
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/logomark.py:27-42, 63-71, 177-200, 227-235`
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/logo.py:40-73, 135-143`
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/annotations.py:99-101`
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/dimensioned.py:29-47, 492-499, 610-617`
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/artifacts/clearspace.py:39-41`
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/artifacts/misuse.py:117-132`

**Interfaces:**

- Produces: `core.Box`, `core.Shape` (abstract `elements_bounding_box: Box`, `make_svg_elements()`, the six `elements_*` properties), `ClearSpace.distance(unit: float) -> float`, `BaseRenderable.__init__(clear_space=..., background_color=..., **kwargs)`, `BaseRenderable.clearspace_unit` (abstract property), `BaseRenderable.make_canvas(clear_space: ClearSpace) -> Canvas`, `BaseRenderable.canvas` (property). `_get_clearspace`, `_make_canvas` and the `canvas=` parameter no longer exist.

- [ ] **Step 1: Add `Box` and `ClearSpace.distance` in `core.py`**

Under `# === Types ===`, after the `PaletteColor` class and before `SvgElements`, add:

```python
Box = tuple[float, float, float, float]
```

Replace the `ClearSpace` enum with:

```python
class ClearSpace(Enum):
    NONE = auto()
    MINIMAL = auto()
    RECOMMENDED = auto()

    def distance(self, unit: float) -> float:
        match self:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return unit / 2
            case ClearSpace.RECOMMENDED:
                return unit
```

- [ ] **Step 2: Split `Shape` out of `BaseRenderable` in `core.py`**

Replace everything from `# === Base Classes ===` to the end of the file with:

```python
# === Base Classes ===


class Shape(ABC):
    @property
    @abstractmethod
    def elements_bounding_box(self) -> Box: ...

    @abstractmethod
    def make_svg_elements(self) -> list[svg.Element]: ...

    @property
    def elements_x_min(self):
        return self.elements_bounding_box[0]

    @property
    def elements_y_min(self):
        return self.elements_bounding_box[1]

    @property
    def elements_x_max(self):
        return self.elements_bounding_box[2]

    @property
    def elements_y_max(self):
        return self.elements_bounding_box[3]

    @property
    def elements_width(self):
        return self.elements_x_max - self.elements_x_min

    @property
    def elements_height(self):
        return self.elements_y_max - self.elements_y_min


class BaseRenderable(Shape, ABC):
    def __init__(
        self,
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        background_color: str | None = None,
        **kwargs: object,
    ):
        self.clear_space: ClearSpace = clear_space
        self.background_color: str | None = background_color

    @property
    @abstractmethod
    def clearspace_unit(self) -> float: ...

    @abstractmethod
    def make_filename(self, extras: tuple[str, ...] = ()) -> str: ...

    def make_canvas(self, clear_space: ClearSpace) -> Canvas:
        min_x, min_y, max_x, max_y = self.elements_bounding_box
        distance = clear_space.distance(self.clearspace_unit)

        min_x -= distance
        min_y -= distance
        max_x += distance
        max_y += distance

        return Canvas(
            min_x=min_x,
            min_y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
        )

    @property
    def canvas(self) -> Canvas:
        return self.make_canvas(self.clear_space)

    @property
    def canvas_bounding_box(self):
        return (
            self.canvas.min_x,
            self.canvas.min_y,
            self.canvas.min_x + self.canvas.width,
            self.canvas.min_y + self.canvas.height,
        )

    def make_svg_background(self) -> list[svg.Element]:
        return (
            []
            if self.background_color is None
            else flatten_svg_elements(
                self.canvas.make_svg_background(fill=self.background_color)
            )
        )

    def make_svg(self):
        return svg.SVG(
            viewBox=self.canvas.make_view_box(),
            elements=self.make_svg_background() + self.make_svg_elements(),
        )

    def write_svg(self, filename: str | None = None):
        if filename is None:
            filename = self.make_filename()
        filename = filename.replace("/", "_")
        with open(Path(filename + ".svg"), "w", encoding="utf-8") as file:
            etree.canonicalize(str(self.make_svg()), out=file)
```

`make_svg_background`, `make_svg` and `write_svg` are byte-for-byte today's bodies; only their position moved.

- [ ] **Step 3: Forward `clear_space` and replace the clear-space blocks in `logotype.py`**

In `Glyph.__init__`, delete the line `self.clear_space: ClearSpace = clear_space` and change the `super().__init__(**kwargs)` call to:

```python
        super().__init__(clear_space=clear_space, **kwargs)
```

Replace `Glyph._get_clearspace` (the `match self.clear_space` block) with:

```python
    @property
    @override
    def clearspace_unit(self) -> float:
        return self.loader.capHeight
```

In `Logotype.__init__`, delete `self.clear_space: ClearSpace = clear_space` and change the `super().__init__(**kwargs)` call to `super().__init__(clear_space=clear_space, **kwargs)`. Replace `Logotype._get_clearspace` with:

```python
    @property
    @override
    def clearspace_unit(self) -> float:
        return self.cap_height
```

- [ ] **Step 4: The same in `logomark.py`**

In `Lambda.__init__`, delete `self.clear_space: ClearSpace = clear_space` and forward: `super().__init__(clear_space=clear_space, **kwargs)`. Replace `Lambda._get_clearspace` with:

```python
    @property
    @override
    def clearspace_unit(self) -> float:
        return self.elements_y_max
```

In `Logomark.__init__`, delete `self.clear_space: ClearSpace = clear_space` and forward the same way. Replace `Logomark._get_clearspace` with the identical `clearspace_unit` property returning `self.elements_y_max`.

- [ ] **Step 5: `logo.py`: forward but keep the early assignment**

`NixosLogo.__init__` reads `self.clear_space` inside `_init_snowflake()` before calling `super().__init__`, so keep the line `self.clear_space: ClearSpace = clear_space` where it is and change the final call to:

```python
        super().__init__(clear_space=clear_space, **kwargs)
```

Replace `NixosLogo._get_clearspace` with:

```python
    @property
    @override
    def clearspace_unit(self) -> float:
        return self.logomark.elements_height
```

- [ ] **Step 6: `annotations.py`, `dimensioned.py`, `clearspace.py`, `misuse.py`**

In `annotations.py`, replace `TextAnnotations._get_clearspace` (which returns 0) with:

```python
    @property
    @override
    def clearspace_unit(self) -> float:
        return 0
```

In `dimensioned.py`, `DimensionedLambda.__init__` becomes:

```python
    def __init__(
        self,
        annotations: Annotations,
        clear_space: ClearSpace = ClearSpace.NONE,
        **kwargs,
    ):
        super().__init__(clear_space=clear_space, **kwargs)
        self.annotations: Annotations = annotations
```

The three `_make_canvas` overrides in `dimensioned.py` (on `DimensionedLambda`, `DimensionedLogomark`, `DimensionedLogomarkGradient`) change their signature only:

```python
    @override
    def make_canvas(self, clear_space: ClearSpace) -> Canvas:
```

with their bodies unchanged.

In `artifacts/clearspace.py`, replace `LogoClearspace._get_clearspace` with:

```python
    @property
    @override
    def clearspace_unit(self) -> float:
        return self.recommended.clearspace_unit
```

In `artifacts/misuse.py`, `LogoCrop._make_canvas` becomes:

```python
    @override
    def make_canvas(self, clear_space: ClearSpace) -> Canvas:
        min_x, min_y, max_x, max_y = self.elements_bounding_box
        distance = clear_space.distance(self.clearspace_unit)

        min_x += distance
        min_y -= distance
        max_x -= distance
        max_y += distance

        return Canvas(
            min_x=min_x,
            min_y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
        )
```

- [ ] **Step 7: Harness and gates**

Run: `nix develop .#nixos-logo-dev --command bash /tmp/nixoslogo-harness/run-artifacts.sh`
Expected: `identical=96 different=0`. A DIFF on any `-none` or `-minimal` artifact means a subclass is not forwarding `clear_space`.

Run: `nix develop .#nixos-logo-dev --command bash -c 'PY=$(which python); nix run nixpkgs#basedpyright -- --pythonpath "$PY" package-sets/python-packages/nixoslogo/nixoslogo | tail -1'`
Expected: `0 errors, ...`.

Run: `nix run --inputs-from . nixpkgs#ruff -- check package-sets/python-packages/nixoslogo && nix fmt && nix fmt -- --fail-on-change`
Expected: ruff `All checks passed!`, treefmt clean.

Run: `nix build .#hydraJobs.nixos-branding.x86_64-linux.all-artifacts --no-link`
Expected: success with no hash mismatch errors.

- [ ] **Step 8: Commit**

```bash
git add package-sets/python-packages/nixoslogo
git commit -F - <<'EOF'
nixoslogo: compute the canvas lazily and share one clear space rule

BaseRenderable no longer calls the virtual _make_canvas during
construction; canvas is a property over make_canvas(clear_space), so
the order of attribute assignments in subclasses stops mattering. The
five identical _get_clearspace match blocks become ClearSpace.distance
with a clearspace_unit per class. Shape holds the geometry surface that
parents consume; BaseRenderable adds the document behaviour. Subclasses
forward clear_space to the base instead of assigning it themselves.

All 96 artifacts are byte-identical.

Assisted-by: Claude Code (claude-fable-5-1)
EOF
```

______________________________________________________________________

### Task 2: Lambda overlay drawing as functions

**Files:**

- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/logomark.py` (`Lambda.make_hexagon_points`, `Lambda.make_lambda_points`)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/dimensioned.py` (module functions; `DimensionedLambda*`, `DimensionedLogomark`, `DimensionedLogomarkGradient`, `DimensionedLogotype.dimension_spacings`)
- Modify: `package-sets/top-level/nixos-branding/artifacts/dimensioned/nixos-logomark-dimensioned-linear/script.py`
- Modify: `package-sets/top-level/nixos-branding/artifacts/dimensioned/nixos-logomark-dimensioned-gradient-annotated/script.py`
- Modify: `package-sets/top-level/nixos-branding/artifacts/dimensioned/nixos-logomark-dimensioned-gradient-background/script.py`

**Interfaces:**

- Consumes: `Lambda`, `Points`, `LineGroup` (today's dataclass in `annotations.py`).

- Produces: `logomark.hexagon_points(radius: float) -> Points`; in `dimensioned.py`: `diagonal_line(radius: float) -> Points`, `make_lambda_construction_lines(ilambda: Lambda, lines: LineGroup) -> tuple[svg.Element, ...]`, `make_lambda_main_diagonal(...)`, `make_lambda_off_diagonal(...)`, `make_lambda_polygons(...)` with the same signature. `DimensionedLogomark` and `DimensionedLogomarkGradient` no longer take `ilambda` explicitly; it reaches `Logomark` through `**kwargs` and defaults to `Lambda()`.

- [ ] **Step 1: `hexagon_points` in `logomark.py`**

Add after the `GradientEndPoints` TypedDict and before `class Lambda`:

```python
def hexagon_points(radius: float) -> Points:
    angles = [math.radians(angle) for angle in range(0, 360, 60)]
    return Points(
        [
            Point(
                (
                    radius * math.cos(angle),
                    radius * math.sin(angle),
                )
            )
            for angle in angles
        ]
    )
```

Delete `Lambda.make_hexagon_points`. In `Lambda.make_lambda_points`, change `hexagon_points = self.make_hexagon_points(radius)` to `hexagon = hexagon_points(radius)` and the three following reads (`hexagon_points[2]`, `[4]`, `[5]`) to `hexagon[2]`, `hexagon[4]`, `hexagon[5]`, so the local does not shadow the function.

- [ ] **Step 2: Module functions in `dimensioned.py`**

Change the imports at the top of `dimensioned.py` to:

```python
import itertools
import math
from collections.abc import Callable
from typing import TypedDict, override

import svg

from nixoslogo.annotations import Annotations, LineGroup, TextAnnotations
from nixoslogo.core import ClearSpace, flatten_svg_elements
from nixoslogo.geometry import Point, Points
from nixoslogo.layout import Canvas
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Lambda, Logomark, hexagon_points
from nixoslogo.logotype import Logotype
```

Add, after the two `*Options` TypedDicts and before `class DimensionedLambda`:

```python
def diagonal_line(radius: float) -> Points:
    points = hexagon_points(radius)
    return Points([points[1], points[4]])


def make_lambda_construction_lines(
    ilambda: Lambda, lines: LineGroup
) -> tuple[svg.Element, ...]:
    return (
        svg.Circle(
            cx=0,
            cy=0,
            r=ilambda.radius,
            stroke=lines.stroke,
            stroke_width=lines.stroke_width,
            stroke_dasharray=lines.stroke_dasharray,
            fill=lines.fill,
        ),
        svg.Polygon(
            points=hexagon_points(radius=ilambda.radius).to_list(),
            stroke=lines.stroke,
            stroke_width=lines.stroke_width,
            stroke_dasharray=lines.stroke_dasharray,
            fill=lines.fill,
        ),
    )


def make_lambda_main_diagonal(
    ilambda: Lambda, lines: LineGroup
) -> tuple[svg.Element, ...]:
    return (
        svg.Polyline(
            points=diagonal_line(radius=ilambda.radius).to_list(),
            stroke=lines.stroke,
            stroke_width=lines.stroke_width,
            stroke_dasharray=lines.stroke_dasharray,
            fill=lines.fill,
        ),
    )


def make_lambda_off_diagonal(
    ilambda: Lambda, lines: LineGroup
) -> tuple[svg.Element, ...]:
    lambda_points_gap = ilambda.make_named_lambda_points()
    return (
        svg.Line(
            x1=Point((0, 0)).x,
            y1=Point((0, 0)).y,
            x2=lambda_points_gap["rear_foot"].x,
            y2=lambda_points_gap["rear_foot"].y,
            stroke=lines.stroke,
            stroke_width=lines.stroke_width,
            stroke_dasharray=lines.stroke_dasharray,
        ),
    )


def make_lambda_polygons(ilambda: Lambda, lines: LineGroup) -> tuple[svg.Element, ...]:
    lambda_points_no_gap = ilambda.make_lambda_points(gap=0)
    lambda_points_gap = ilambda.make_lambda_points()
    return (
        svg.Polygon(
            points=lambda_points_no_gap.to_list(),
            stroke=lines.stroke,
            stroke_width=lines.stroke_width,
            fill=lines.fill,
            stroke_dasharray=[4],
        ),
        svg.Polygon(
            points=lambda_points_gap.to_list(),
            stroke=lines.stroke,
            stroke_width=lines.stroke_width,
            fill=lines.fill,
        ),
    )
```

These are the bodies of today's `DimensionedLambda.make_diagonal_line`, `make_lambda_construction_lines`, `make_lambda_main_diagonal`, `make_lambda_off_diagonal` and `make_lambda_polygons` with `self` replaced by `ilambda` and `self.annotations.<group>` by `lines`. Delete those five methods from `DimensionedLambda`.

- [ ] **Step 3: Update the call sites in the `DimensionedLambda*` classes**

Everywhere in `DimensionedLambdaLinear`, `DimensionedLambdaAngular`, `DimensionedLambdaAnnotatedVertices` and `DimensionedLambdaAnnotatedParameters`:

| Old | New |
|---|---|
| `hexagon_points = self.make_hexagon_points(radius=self.radius)` (in `make_lambda_linear_dimensions` and `make_parametric_annotations`) | `hexagon = hexagon_points(radius=self.radius)`, and the reads `hexagon_points[1]`, `hexagon_points[4]`, `hexagon_points[5]` that follow become `hexagon[1]`, `hexagon[4]`, `hexagon[5]` |
| `self.make_lambda_construction_lines()` | `make_lambda_construction_lines(self, self.annotations.construction_lines)` |
| `self.make_lambda_main_diagonal()` | `make_lambda_main_diagonal(self, self.annotations.construction_lines)` |
| `self.make_lambda_off_diagonal()` | `make_lambda_off_diagonal(self, self.annotations.construction_lines)` |
| `self.make_lambda_polygons()` | `make_lambda_polygons(self, self.annotations.object_lines)` |

Keep the order of the arguments to `flatten_svg_elements` exactly as it is in each `make_svg_elements`. The local must be renamed where the result is assigned: `hexagon_points = hexagon_points(...)` makes the name local to the whole method and raises `UnboundLocalError` on the call.

- [ ] **Step 4: `DimensionedLogomark` and `DimensionedLogomarkGradient` take any `Lambda`**

In both classes delete the class-level annotation `ilambda: DimensionedLambda` and change `__init__` to:

```python
    def __init__(
        self,
        annotations: Annotations,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.annotations: Annotations = annotations
```

In `DimensionedLogomark`:

| Old | New |
|---|---|
| `self.ilambda.make_hexagon_points(radius=self.ilambda.radius * 2.25)` (formatted over three lines in the source) | `hexagon_points(radius=self.ilambda.radius * 2.25)` |
| `self.ilambda.make_diagonal_line(radius=self.ilambda.radius * 2.25)` (three lines in the source) | `diagonal_line(radius=self.ilambda.radius * 2.25)` |
| `hexagon_points = self.ilambda.make_hexagon_points(radius=self.ilambda.radius)` (in `make_flake_linear_dimensions`) | `hexagon = hexagon_points(radius=self.ilambda.radius)`, and the reads `hexagon_points[1]`, `hexagon_points[4]` become `hexagon[1]`, `hexagon[4]` |
| `self.ilambda.annotations.object_lines.stroke` (and `.stroke_width`, `.fill`) | `self.annotations.object_lines.stroke` (etc.) |
| `self.ilambda.make_lambda_construction_lines()` | `make_lambda_construction_lines(self.ilambda, self.annotations.construction_lines)` |

In `DimensionedLogomarkGradient.make_svg_elements`:

| Old | New |
|---|---|
| `self.ilambda.make_lambda_construction_lines()` | `make_lambda_construction_lines(self.ilambda, self.annotations.construction_lines)` |
| `self.ilambda.make_lambda_polygons()` | `make_lambda_polygons(self.ilambda, self.annotations.object_lines)` |

- [ ] **Step 5: Generalise `DimensionedLogotype.dimension_spacings`**

Replace the method with:

```python
    def dimension_spacings(self):
        gaps = [
            (
                Point((left.elements_x_max, self.elements_y_min)),
                Point((right.elements_x_min, self.elements_y_min)),
            )
            for left, right in itertools.pairwise(self.glyphs)
        ]
        offsets = [
            self.cap_height / (point1 - point2).length() for point1, point2 in gaps
        ]
        sides = ["left"] + ["right"] * (len(gaps) - 1)
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
            for (point1, point2), offset, side in zip(gaps, offsets, sides, strict=True)
        )
```

- [ ] **Step 6: The three logomark diagram scripts**

`dimensioned/nixos-logomark-dimensioned-linear/script.py`:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomark

annotations = Annotations.medium()

logomark = DimensionedLogomark(
    color_style=ColorStyle.FLAT,
    annotations=annotations,
)
logomark.write_svg()
```

`dimensioned/nixos-logomark-dimensioned-gradient-annotated/script.py`:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomarkGradientAnnotated

annotations = Annotations.small()

logomark = DimensionedLogomarkGradientAnnotated(
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
```

`dimensioned/nixos-logomark-dimensioned-gradient-background/script.py`:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomarkGradientBackground

# TODO @djacu see if this can be better
annotations = Annotations.small()
annotations.object_lines.stroke = "white"
annotations.construction_lines.stroke = "black"

logomark = DimensionedLogomarkGradientBackground(
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
```

The dropped `DimensionedLambda(annotations=annotations)` had default radius, thickness and gap, so the `Lambda()` default inside `Logomark` draws the same geometry.

- [ ] **Step 7: Harness and gates**

Run the harness, basedpyright, ruff, `nix fmt`, and the artifact build exactly as in Task 1 Step 7. Expected: `identical=96`, 0 errors, clean, clean, build succeeds. A crash on `nixos-lambda-dimensioned-linear`, `nixos-lambda-dimensioned-annotated-parameters` or `nixos-logomark-dimensioned-linear` means one of the three `hexagon` renames in Steps 3 and 4 was missed.

- [ ] **Step 8: Commit**

```bash
git add package-sets/python-packages/nixoslogo package-sets/top-level/nixos-branding/artifacts/dimensioned
git commit -F - <<'EOF'
nixoslogo: draw lambda construction lines with functions

The construction lines, diagonals and outline polygons of the lambda
diagrams were methods on DimensionedLambda, which forced the logomark
diagrams to require a DimensionedLambda and to read line styles through
it. They are module functions taking a Lambda and a LineGroup now, and
the logomark diagrams take any Lambda and read their own annotations.
make_hexagon_points never read self and is hexagon_points. The logotype
spacing dimensions derive their count from the glyphs.

All 96 artifacts are byte-identical.

Assisted-by: Claude Code (claude-fable-5-1)
EOF
```

______________________________________________________________________

### Task 3: Keyword-only dataclasses

**Files:**

- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/core.py` (`BaseRenderable`)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/logomark.py` (`Lambda`, `Logomark`)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/logotype.py` (`Glyph`, `Logotype`)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/logo.py` (`NixosLogo`)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/annotations.py` (`TextAnnotations`, `FontConfig`, the three presets)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/dimensioned.py` (all eleven classes)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/artifacts/misuse.py` (five classes)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/artifacts/clearspace.py` (`LogoClearspace`)

**Interfaces:**

- Consumes: Task 1's `BaseRenderable` surface; Task 2's `DimensionedLogomark` without an explicit `ilambda`.

- Produces: every renderable constructed by keyword only; `Logomark.GRADIENT_STOP_OFFSETS` (class constant, replaces `_gradient_stop_offsets`); `Logomark.colors_name`, `colors_value`, `css_color_names` and `Logotype.cap_height`, `scale` become properties with the same values; `NixosLogo.transform` (property, replaces reads of `logotype_transform`); `NixosLogo` no longer accepts `loader`; `NixosLogo.logotype.cap_height` replaces reads of `logotype_cap_height` outside `__post_init__`.

- [ ] **Step 1: `BaseRenderable` in `core.py`**

Add `from dataclasses import dataclass` to the imports. Replace the `BaseRenderable.__init__` with fields:

```python
@dataclass(kw_only=True)
class BaseRenderable(Shape, ABC):
    clear_space: ClearSpace = ClearSpace.RECOMMENDED
    background_color: str | None = None

    @property
    @abstractmethod
    def clearspace_unit(self) -> float: ...
```

The rest of the class is unchanged.

- [ ] **Step 2: `Lambda` and `Logomark` in `logomark.py`**

Add `from dataclasses import dataclass, field` and `ClassVar` to the typing import. Replace `Lambda.__init__` with fields:

```python
@dataclass(kw_only=True)
class Lambda(BaseRenderable):
    radius: int = 512
    thickness: float = 1 / 4
    gap: float = 1 / 32
    color: str = "black"
```

Replace `Logomark.__init__` with:

```python
@dataclass(kw_only=True)
class Logomark(BaseRenderable):
    ilambda: Lambda = field(default_factory=Lambda)
    color_style: ColorStyle = ColorStyle.GRADIENT
    colors: LogomarkColors | tuple[Color, ...] = LogomarkColors.DEFAULT

    GRADIENT_STOP_OFFSETS: ClassVar[tuple[int, int, int]] = (0, 25, 100)

    @property
    def colors_name(self) -> str:
        return self.colors.name if isinstance(self.colors, LogomarkColors) else "custom"

    @property
    def colors_value(self) -> tuple[Color, ...]:
        return self.colors.value if isinstance(self.colors, LogomarkColors) else self.colors

    @property
    def css_color_names(self) -> tuple[str, ...]:
        return self._make_css_color_names()
```

The three were assigned once in `__init__`; as properties they are pure functions of `colors` and `color_style`, cannot go stale, and `Logomark` needs no `__post_init__`, so its subclasses have nothing to chain. The values are the same expressions, so output is unchanged.

Replace the three reads of `self._gradient_stop_offsets[...]` in `make_flake_gradients_defs` with `self.GRADIENT_STOP_OFFSETS[...]`, and the two reads in `DimensionedLogomarkGradient.make_dimensioned_gradient_lines` (`dimensioned.py`) the same way. Remove `ClearSpace` from the `nixoslogo.core` import in `logomark.py`: the deleted `__init__` signatures were its last uses, and ruff reports the import as unused otherwise.

- [ ] **Step 3: `Glyph` and `Logotype` in `logotype.py`**

Add `from dataclasses import dataclass, field`. Replace `Glyph.__init__` with:

```python
@dataclass(kw_only=True)
class Glyph(BaseRenderable):
    character: str
    loader: FontLoader = field(default_factory=FontLoader)
    color: str = "black"
    style: LogotypeStyle = LogotypeStyle.REGULAR

    def __post_init__(self) -> None:
        self.font = self.loader.font
        self.glyph = self.font[self.character]
        self.layer = self.glyph.foreground.dup()
```

`font`, `glyph` and `layer` stay plain attributes (fontforge has no stubs; they are inferred exactly as today).

Replace `Logotype.__init__` with:

```python
@dataclass(kw_only=True)
class Logotype(BaseRenderable):
    characters: str = "NixOS"
    loader: FontLoader = field(default_factory=FontLoader)
    color: str = "black"
    style: LogotypeStyle = LogotypeStyle.REGULAR
    spacings: tuple[int, ...] = DEFAULT_LOGOTYPE_SPACINGS
    glyphs: tuple[Glyph, ...] = field(init=False)

    @property
    def cap_height(self) -> float:
        return self.loader.capHeight

    @property
    def scale(self) -> float:
        return self.loader.scale

    def __post_init__(self) -> None:
        self._load_glyphs()
        self._set_spacings()
```

`cap_height` and `scale` were copies of the loader's values, read through `glyphs[0].loader`, which is the same object as `self.loader`; as properties they read it directly. `glyphs` stays a field because `_load_glyphs` and `_set_spacings` transform fontforge layers and must run exactly once. In `_load_glyphs`, remove the `self.glyphs: tuple[Glyph, ...] =` annotation (the field is declared on the class now): `self.glyphs = tuple(...)`. Remove `ClearSpace` from the `nixoslogo.core` import in `logotype.py`; nothing in the module names it any more.

- [ ] **Step 4: `TextAnnotations` and `FontConfig` in `annotations.py`**

Add `from dataclasses import dataclass, field` (the module already imports `dataclass`). Replace `TextAnnotations.__init__` with:

```python
@dataclass(kw_only=True)
class TextAnnotations(BaseRenderable):
    characters: str
    loader: FontLoader
    color: str = "black"
    scale: float | None = None
    cap_height: float | None = None
    glyphs: tuple[Glyph, ...] = field(init=False)
    original_cap_height: float = field(init=False)

    def __post_init__(self) -> None:
        self._load_glyphs()
        self.original_cap_height = self.loader.capHeight
        self._set_spacings()
        self._scale_glyphs()
```

`original_scale` is gone: today it is assigned and never read. In `_load_glyphs`, drop the `self.glyphs: tuple[Glyph, ...] =` annotation.

Remove `stroke_dasharray` from `FontConfig`:

```python
class FontConfig(TypedDict):
    scale: float | None
    cap_height: float
    color: str
```

and delete the `"stroke_dasharray": [...]` line from the `font_config` literal of each of `small`, `medium` and `large`. Those entries were forwarded into `TextAnnotations(**self.font_config)` and swallowed by `**kwargs`; with the dataclass they would raise `TypeError` at every dimension label.

- [ ] **Step 5: `NixosLogo` in `logo.py`**

Add `from dataclasses import dataclass, field`. Replace `NixosLogo.__init__` with:

```python
@dataclass(kw_only=True)
class NixosLogo(BaseRenderable):
    lambda_radius: int = 512
    lambda_thickness: float = 1 / 4
    lambda_gap: float = 1 / 32
    logo_layout: LogoLayout = LogoLayout.HORIZONTAL
    logomark_colors: LogomarkColors | tuple[Color, ...] = LogomarkColors.DEFAULT
    logomark_color_style: ColorStyle = ColorStyle.GRADIENT
    logotype_cap_height: float | None = None
    logotype_color: str = "black"
    logotype_style: LogotypeStyle = LogotypeStyle.REGULAR
    logotype_spacings: tuple[int, ...] = DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING
    logotype_characters: str = "NixOS"
    logotype_transform: svg.Translate | None = None
    ilambda: Lambda = field(init=False)
    logomark: Logomark = field(init=False)
    loader: FontLoader = field(init=False)
    logotype: Logotype = field(init=False)

    def __post_init__(self) -> None:
        self._init_snowflake()
        cap_height = (
            self.logotype_cap_height
            if self.logotype_cap_height is not None
            else self._default_cap_height()
        )
        self.loader = FontLoader(capHeight=cap_height)
        self._init_logotype()

    @property
    def transform(self) -> svg.Translate:
        return (
            self.logotype_transform
            if self.logotype_transform is not None
            else self._default_transform()
        )
```

The `loader` constructor parameter is gone: no script or package caller passes it, and it was the mispositioning hook. In `_init_snowflake` and `_init_logotype`, drop the `self.ilambda: Lambda =`, `self.logomark: Logomark =` and `self.logotype: Logotype =` annotations (fields are declared on the class). In `_default_transform`, replace both reads of `self.logotype_cap_height` with `self.logotype.cap_height`. In `elements_bounding_box`, replace `self.logotype_transform.x` and `self.logotype_transform.y` with `self.transform.x` and `self.transform.y`. In `make_svg_elements`, replace `transform=[self.logotype_transform]` with `transform=[self.transform]`.

`self.logotype.cap_height` is the loader's `capHeight`, which `_ref_size` returns as the requested value unchanged, so positions are byte-identical. Remove `ClearSpace` from the `nixoslogo.core` import in `logo.py`; the deleted signature and the deleted `self.clear_space` assignment were its last uses.

- [ ] **Step 6: `dimensioned.py`**

Every class gets `@dataclass(kw_only=True)`. The ones with constructors become:

```python
@dataclass(kw_only=True)
class DimensionedLambda(Lambda):
    annotations: Annotations
    clear_space: ClearSpace = ClearSpace.NONE
```

```python
@dataclass(kw_only=True)
class DimensionedLogomark(Logomark):
    annotations: Annotations
```

```python
@dataclass(kw_only=True)
class DimensionedLogomarkGradient(Logomark):
    annotations: Annotations
```

```python
@dataclass(kw_only=True)
class DimensionedLogotype(Logotype):
    annotations: Annotations
```

```python
@dataclass(kw_only=True)
class DimensionedLogo(NixosLogo):
    annotations: Annotations
```

Delete their `__init__` methods. `DimensionedLambdaLinear`, `DimensionedLambdaAngular`, `DimensionedLambdaAnnotatedVertices`, `DimensionedLambdaAnnotatedParameters`, `DimensionedLogomarkGradientAnnotated` and `DimensionedLogomarkGradientBackground` get the decorator with no fields. In `DimensionedLogo`, replace every `self.logotype_cap_height` with `self.logotype.cap_height` (five reads in `dimension_cap_height` and `dimension_bearing`). Add `from dataclasses import dataclass` to the imports.

- [ ] **Step 7: `misuse.py` and `clearspace.py`**

In `artifacts/misuse.py`, add `from dataclasses import dataclass` and replace each `__init__` with field redeclarations:

```python
@dataclass(kw_only=True)
class LogomarkRotate(Logomark):
    clear_space: ClearSpace = ClearSpace.MINIMAL
```

```python
@dataclass(kw_only=True)
class LogomarkMirror(Logomark):
    clear_space: ClearSpace = ClearSpace.MINIMAL
```

```python
@dataclass(kw_only=True)
class LogoCrop(NixosLogo):
    clear_space: ClearSpace = ClearSpace.MINIMAL
```

```python
@dataclass(kw_only=True)
class LogoScale(NixosLogo):
    clear_space: ClearSpace = ClearSpace.MINIMAL
```

```python
@dataclass(kw_only=True)
class LogoColorsWithLambdaPrime(NixosLogo):
    clear_space: ClearSpace = ClearSpace.MINIMAL
    logotype_style: LogotypeStyle = LogotypeStyle.LAMBDAPRIME
```

Each keeps its other methods (`make_filename`, overrides) unchanged. Both redeclarations must carry their annotation; an unannotated `clear_space = ClearSpace.MINIMAL` is not a field and the base default would win.

In `artifacts/clearspace.py`, add `from dataclasses import dataclass, field` and replace `LogoClearspace.__init__` with:

```python
@dataclass(kw_only=True)
class LogoClearspace(BaseRenderable):
    logo: type[BaseRenderable]
    logo_name: str
    space_object: BaseRenderable
    annotations: Annotations
    recommended: BaseRenderable = field(init=False)
    minimal: BaseRenderable = field(init=False)

    def __post_init__(self) -> None:
        self.recommended = self.logo(clear_space=ClearSpace.RECOMMENDED)
        self.minimal = self.logo(clear_space=ClearSpace.MINIMAL)
```

- [ ] **Step 8: Harness and gates**

Run the harness, basedpyright, ruff, `nix fmt`, and the artifact build exactly as in Task 1 Step 7. Expected: `identical=96`, 0 errors, clean, clean, build succeeds. basedpyright errors here almost always mean a field typed `X | None` is read outside `__post_init__`; resolve by reading the derived value (`self.logotype.cap_height`, `self.transform`), never by `assert`.

- [ ] **Step 9: Commit**

```bash
git add package-sets/python-packages/nixoslogo
git commit -F - <<'EOF'
nixoslogo: make every renderable a keyword-only dataclass

Fields are the constructor parameters; values that are pure functions
of them are properties, and the glyph runs that must be built once are
set in __post_init__. An unknown keyword raises TypeError instead of
disappearing into **kwargs, every Logomark gets its own Lambda, and
subclasses redeclare the defaults they change. NixosLogo loses the
loader parameter that positioned the logotype with the wrong cap
height and reads the cap height back from the logotype it built.
FontConfig loses stroke_dasharray, which only ever survived because
the **kwargs hole swallowed it.

All 96 artifacts are byte-identical.

Assisted-by: Claude Code (claude-fable-5-1)
EOF
```

______________________________________________________________________

### Task 4: Frozen annotations with typed overrides

**Files:**

- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/annotations.py` (`LineConfig`, `FontConfig`, `LineGroup`, `ObjectLines`, `ConstructionLines`, `DimensionLines`, `Annotations`)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/dimensioned.py` (`__main__` block)
- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/artifacts/clearspace.py` (`__main__` block)
- Modify: six scripts under `package-sets/top-level/nixos-branding/artifacts/` listed in Step 4

**Interfaces:**

- Consumes: `TextAnnotations(characters=, loader=, cap_height=, color=)` from Task 3.

- Produces: frozen `LineGroup(name=, stroke=, stroke_width=, stroke_dasharray=, fill=)`; frozen `DimensionLines(LineGroup)` with `font_loader: FontLoader`, `cap_height: float`, `color: str`, `make_annotation(text) -> TextAnnotations`; `LineGroupOverrides`, `DimensionLinesOverrides`, `AnnotationsOverrides` TypedDicts; frozen `Annotations(object_lines=, construction_lines=, dimension_lines=)` with `sized(multiplier: int, overrides=None)`, `small/medium/large(overrides=None)`, `make_annotation(text)`. `LineConfig`, `FontConfig`, `ObjectLines`, `ConstructionLines` and `Annotations.__init__`'s config dicts no longer exist.

- [ ] **Step 1: Replace the line-group section of `annotations.py`**

Replace everything from `class LineConfig(TypedDict):` through the end of `class DimensionLines(LineGroup):`'s `__init__` (keep its four `make_dimension_*` methods) with:

```python
@dataclass(frozen=True, kw_only=True)
class LineGroup:
    name: str
    stroke: str
    stroke_width: int
    stroke_dasharray: list[Number]
    fill: str = "transparent"


class LineGroupOverrides(TypedDict, total=False):
    stroke: str
    stroke_width: int
    stroke_dasharray: list[Number]
    fill: str


class DimensionLinesOverrides(LineGroupOverrides, total=False):
    font_loader: FontLoader
    cap_height: float
    color: str


class AnnotationsOverrides(TypedDict, total=False):
    object_lines: LineGroupOverrides
    construction_lines: LineGroupOverrides
    dimension_lines: DimensionLinesOverrides


@dataclass(frozen=True, kw_only=True)
class DimensionLines(LineGroup):
    font_loader: FontLoader
    cap_height: float
    color: str

    def make_annotation(self, text: str) -> TextAnnotations:
        return TextAnnotations(
            characters=text,
            loader=self.font_loader,
            cap_height=self.cap_height,
            color=self.color,
        )
```

Inside `make_dimension_line`, `make_dimension_line_outer` and `make_dimension_angle`, replace each

```python
            text_annotation = TextAnnotations(
                characters=str(label),
                loader=self.font_loader,
                **self.font_config,
            )
```

with `text_annotation = self.make_annotation(str(label))` (and `str(text)` in `make_dimension_angle`). The presets always passed `scale=None`, which is `TextAnnotations`'s default, so the layout is unchanged.

`make_annotation` is now the only caller that reaches `TextAnnotations` with a size, and it passes `cap_height`, so the `scale` input is unreachable. Delete the `scale: float | None = None` field from `TextAnnotations` and reduce `_scale_glyphs` to its surviving branch:

```python
    def _scale_glyphs(self):
        if self.cap_height is None:
            return
        scale = self.original_cap_height / self.cap_height
        for glyph in self.glyphs:
            glyph.layer.transform((1 / scale, 0, 0, 1 / scale, 0, 0))
```

Nothing outside the class read `TextAnnotations.scale` (the `.scale` reads in `dimensioned.py` are on `Logotype`), and every preset sets `cap_height`, so the executed path is the same.

- [ ] **Step 2: Replace `Annotations`**

Replace the `Annotations` class (its `__init__`, `make_annotation`, `small`, `medium`, `large`) with:

```python
@dataclass(frozen=True, kw_only=True)
class Annotations:
    object_lines: LineGroup
    construction_lines: LineGroup
    dimension_lines: DimensionLines

    def make_annotation(self, text: str) -> TextAnnotations:
        return self.dimension_lines.make_annotation(text)

    @classmethod
    def sized(
        cls, multiplier: int, overrides: AnnotationsOverrides | None = None
    ) -> Self:
        base = cls(
            object_lines=LineGroup(
                name="object",
                stroke="green",
                stroke_width=4 * multiplier,
                stroke_dasharray=[4 * multiplier],
            ),
            construction_lines=LineGroup(
                name="construction",
                stroke="blue",
                stroke_width=2 * multiplier,
                stroke_dasharray=[4 * multiplier],
            ),
            dimension_lines=DimensionLines(
                name="dimension",
                stroke="red",
                stroke_width=1 * multiplier,
                stroke_dasharray=[4 * multiplier],
                font_loader=FontLoader(
                    get_font_file=get_nixos_annotation_font_file,
                    transforms_map=DEFAULT_JURA_TRANSFORMS,
                    offset_glyph=False,
                ),
                cap_height=24 * multiplier,
                color="black",
            ),
        )
        if overrides is None:
            return base
        return replace(
            base,
            object_lines=replace(base.object_lines, **overrides.get("object_lines", {})),
            construction_lines=replace(
                base.construction_lines, **overrides.get("construction_lines", {})
            ),
            dimension_lines=replace(
                base.dimension_lines, **overrides.get("dimension_lines", {})
            ),
        )

    @classmethod
    def small(cls, overrides: AnnotationsOverrides | None = None) -> Self:
        return cls.sized(1, overrides)

    @classmethod
    def medium(cls, overrides: AnnotationsOverrides | None = None) -> Self:
        return cls.sized(2, overrides)

    @classmethod
    def large(cls, overrides: AnnotationsOverrides | None = None) -> Self:
        return cls.sized(4, overrides)
```

Imports: add `replace` to the `dataclasses` import and `Self` to the `typing` import; remove `Callable`, `Path` and `NotRequired` if ruff reports them unused.

The old literals were stroke widths 4/2/1, 8/4/2, 16/8/4, dash arrays `[4]`, `[8]`, `[16]` and cap heights 24, 48, 96; `4 * m`, `2 * m`, `1 * m`, `[4 * m]`, `24 * m` with `m` in 1, 2, 4 reproduce them as the same ints.

- [ ] **Step 3: `__main__` blocks**

In `dimensioned.py`'s `__main__`, replace

```python
    annotations = Annotations.small()
    annotations.construction_lines.stroke = "black"
    annotations.construction_lines.stroke_dasharray = [16]
```

with

```python
    annotations = Annotations.small(
        overrides={"construction_lines": {"stroke": "black", "stroke_dasharray": [16]}}
    )
```

and

```python
    annotations = Annotations.large()
    annotations.construction_lines.stroke = "black"
```

with `annotations = Annotations.large(overrides={"construction_lines": {"stroke": "black"}})`.

In `artifacts/clearspace.py`'s `__main__`, replace each `annotations = Annotations.medium()` followed by `annotations.construction_lines.stroke = "grey"` with `annotations = Annotations.medium(overrides={"construction_lines": {"stroke": "grey"}})`, and the `large()` pair the same way.

- [ ] **Step 4: The six scripts**

`clearspace/nixos-logo-clearspace/script.py`: replace the two lines `annotations = Annotations.large()` and `annotations.construction_lines.stroke = "grey"` with

```python
annotations = Annotations.large(overrides={"construction_lines": {"stroke": "grey"}})
```

`clearspace/nixos-logomark-clearspace/script.py` and `clearspace/nixos-logotype-clearspace/script.py`: the same with `Annotations.medium(...)`.

`dimensioned/nixos-logo-dimensioned/script.py` becomes:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.core import ClearSpace
from nixoslogo.dimensioned import DimensionedLogo

annotations = Annotations.large(overrides={"construction_lines": {"stroke": "black"}})

logo = DimensionedLogo(
    clear_space=ClearSpace.MINIMAL,
    annotations=annotations,
)
logo.write_svg()
```

`dimensioned/nixos-logotype-dimensioned/script.py` becomes:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS, ClearSpace
from nixoslogo.dimensioned import DimensionedLogotype
from nixoslogo.logotype import FontLoader

annotations = Annotations.small(
    overrides={"construction_lines": {"stroke": "black", "stroke_dasharray": [16]}}
)

loader = FontLoader(capHeight=512)

logotype = DimensionedLogotype(
    loader=loader,
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
    clear_space=ClearSpace.MINIMAL,
    annotations=annotations,
)
logotype.write_svg()
```

`dimensioned/nixos-logomark-dimensioned-gradient-background/script.py` becomes:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomarkGradientBackground

annotations = Annotations.small(
    overrides={
        "object_lines": {"stroke": "white"},
        "construction_lines": {"stroke": "black"},
    }
)

logomark = DimensionedLogomarkGradientBackground(
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
```

The `# TODO @djacu see if this can be better` comments go; the override is the better way.

- [ ] **Step 5: Harness and gates**

Run the harness, basedpyright, ruff, `nix fmt`, and the artifact build exactly as in Task 1 Step 7. Expected: `identical=96`, 0 errors, clean, clean, build succeeds.

- [ ] **Step 6: Commit**

```bash
git add package-sets/python-packages/nixoslogo package-sets/top-level/nixos-branding/artifacts
git commit -F - <<'EOF'
nixoslogo: freeze the annotation presets and take typed overrides

LineGroup, DimensionLines and Annotations are frozen dataclasses. The
three presets are one constructor, sized(multiplier), that reproduces
their literals, and it takes a typed override dictionary in place of
the attribute assignments six scripts made after construction. The
LineConfig and FontConfig TypedDicts and the empty ObjectLines and
ConstructionLines subclasses are gone.

All 96 artifacts are byte-identical.

Assisted-by: Claude Code (claude-fable-5-1)
EOF
```

______________________________________________________________________

### Task 5: Delete the two preset misuse classes

**Files:**

- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/artifacts/misuse.py` (`LogoScale`, `LogoColorsWithLambdaPrime`, `__main__`)
- Modify: `package-sets/top-level/nixos-branding/artifacts/misuse/nixos-logo-misuse-scale/script.py`
- Modify: `package-sets/top-level/nixos-branding/artifacts/misuse/nixos-logo-misuse-lambdaprime/script.py`

**Interfaces:**

- Consumes: `NixosLogo(clear_space=, logotype_cap_height=, logotype_style=)` and `write_svg(filename)` from Task 3.

- Produces: nothing new; `LogoScale` and `LogoColorsWithLambdaPrime` no longer exist.

- [ ] **Step 1: Delete the classes and their preview entries**

In `artifacts/misuse.py`, delete `class LogoScale(NixosLogo)` and `class LogoColorsWithLambdaPrime(NixosLogo)` entirely, and in the `__main__` block delete the four lines that construct and write `LogoScale(...)` and `LogoColorsWithLambdaPrime(...)`. If ruff then reports `LogotypeStyle` as unused, remove it from the `nixoslogo.core` import.

- [ ] **Step 2: The two scripts**

`misuse/nixos-logo-misuse-scale/script.py`:

```python
from nixoslogo.core import ClearSpace
from nixoslogo.logo import NixosLogo

logo = NixosLogo(clear_space=ClearSpace.MINIMAL, logotype_cap_height=512)
logo.write_svg("nixos-logo-misuse-scale")
```

`misuse/nixos-logo-misuse-lambdaprime/script.py`:

```python
from nixoslogo.core import ClearSpace, LogotypeStyle
from nixoslogo.logo import NixosLogo

logo = NixosLogo(clear_space=ClearSpace.MINIMAL, logotype_style=LogotypeStyle.LAMBDAPRIME)
logo.write_svg("nixos-logo-misuse-lambdaprime")
```

`LogoScale` overrode `_default_cap_height` to return the lambda radius, 512; `logotype_cap_height=512` is the same int. The explicit filenames keep the output names the fixed-output derivations expect.

- [ ] **Step 3: Harness and gates**

Run the harness, basedpyright, ruff, `nix fmt`, and the artifact build exactly as in Task 1 Step 7. Expected: `identical=96`, 0 errors, clean, clean, build succeeds.

- [ ] **Step 4: Commit**

```bash
git add package-sets/python-packages/nixoslogo package-sets/top-level/nixos-branding/artifacts/misuse
git commit -F - <<'EOF'
nixoslogo: drop the two misuse classes that only set defaults

LogoScale and LogoColorsWithLambdaPrime changed a default and a
filename and nothing else. Their scripts call NixosLogo with those
arguments and pass the filename to write_svg.

All 96 artifacts are byte-identical.

Assisted-by: Claude Code (claude-fable-5-1)
EOF
```

______________________________________________________________________

### Task 6: `LogoClearspace` takes an instance

**Files:**

- Modify: `package-sets/python-packages/nixoslogo/nixoslogo/artifacts/clearspace.py`
- Modify: `package-sets/top-level/nixos-branding/artifacts/clearspace/nixos-logo-clearspace/script.py`
- Modify: `package-sets/top-level/nixos-branding/artifacts/clearspace/nixos-logomark-clearspace/script.py`
- Modify: `package-sets/top-level/nixos-branding/artifacts/clearspace/nixos-logotype-clearspace/script.py`

**Interfaces:**

- Consumes: `BaseRenderable.make_canvas(clear_space)` from Task 1; `Shape` from Task 1.

- Produces: `LogoClearspace(logo: BaseRenderable, logo_name: str, space_object: Shape, annotations: Annotations)`. The `recommended` and `minimal` attributes no longer exist.

- [ ] **Step 1: Rewrite the class head**

Replace the dataclass head of `LogoClearspace` with:

```python
@dataclass(kw_only=True)
class LogoClearspace(BaseRenderable):
    logo: BaseRenderable
    logo_name: str
    space_object: Shape
    annotations: Annotations
```

and delete `__post_init__`. Add `Shape` to the `nixoslogo.core` import; drop `field` from the dataclasses import if unused.

- [ ] **Step 2: Replace the reads**

| Old | New |
|---|---|
| `self.recommended.elements_bounding_box` | `self.logo.elements_bounding_box` |
| `self.recommended.clearspace_unit` | `self.logo.clearspace_unit` |
| `self.recommended.make_svg_elements()` | `self.logo.make_svg_elements()` |
| `self.recommended.elements_x_min` (and `_x_max`, `_y_min`, `_y_max`, in `make_space_object_elements` and `make_grid_lines`) | `self.logo.elements_x_min` (etc.) |
| `self.recommended.canvas.min_x` (and `.min_y`, `.width`, `.height`, in `make_clearspace_lines`) | `recommended.min_x` (etc.) |
| `self.minimal.canvas.min_x` (and `.min_y`, `.width`, `.height`) | `minimal.min_x` (etc.) |
| `def make_space_object_element(self, space: BaseRenderable, ...)` | `def make_space_object_element(self, space: Shape, ...)` (it is called with `self.space_object`, now a `Shape`, and only calls `space.make_svg_elements()`) |

At the top of `make_clearspace_lines`, before the two annotations, add:

```python
        recommended = self.logo.make_canvas(ClearSpace.RECOMMENDED)
        minimal = self.logo.make_canvas(ClearSpace.MINIMAL)
```

The elements of a renderable never depended on its clear space, only its canvas did, so one instance produces the same drawing.

- [ ] **Step 3: The three scripts and the preview block**

`clearspace/nixos-logo-clearspace/script.py`:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Logomark

annotations = Annotations.large(overrides={"construction_lines": {"stroke": "grey"}})
ilc = LogoClearspace(
    logo=NixosLogo(),
    logo_name="logo",
    space_object=Logomark(),
    annotations=annotations,
)
ilc.write_svg()
```

`clearspace/nixos-logomark-clearspace/script.py`:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logomark import Lambda, Logomark

annotations = Annotations.medium(overrides={"construction_lines": {"stroke": "grey"}})
ilc = LogoClearspace(
    logo=Logomark(),
    logo_name="logomark",
    space_object=Lambda(gap=0),
    annotations=annotations,
)
ilc.write_svg()
```

`clearspace/nixos-logotype-clearspace/script.py`:

```python
from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logotype import Glyph, Logotype

annotations = Annotations.medium(overrides={"construction_lines": {"stroke": "grey"}})
ilc = LogoClearspace(
    logo=Logotype(),
    logo_name="logotype",
    space_object=Glyph(character="N"),
    annotations=annotations,
)
ilc.write_svg()
```

In the `__main__` block of `clearspace.py`, change the three `logo=Logomark,`, `logo=Logotype,` and `logo=NixosLogo,` arguments to `logo=Logomark(),`, `logo=Logotype(),` and `logo=NixosLogo(),`.

- [ ] **Step 4: Harness and gates**

Run the harness, basedpyright, ruff, `nix fmt`, and the artifact build exactly as in Task 1 Step 7. Expected: `identical=96`, 0 errors, clean, clean, build succeeds.

- [ ] **Step 5: Commit**

```bash
git add package-sets/python-packages/nixoslogo package-sets/top-level/nixos-branding/artifacts/clearspace
git commit -F - <<'EOF'
nixoslogo: give the clearspace diagram a logo instance

LogoClearspace took a class and instantiated it twice to obtain two
canvases that differ by one number. It takes an instance and derives
both rectangles from make_canvas, so the three scripts build the logo
themselves and the font is loaded once per diagram.

All 96 artifacts are byte-identical.

Assisted-by: Claude Code (claude-fable-5-1)
EOF
```

______________________________________________________________________

### Task 7: Numeric and raster modes for `compare-artifacts`

**Files:**

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/numeric.py`
- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/raster.py`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/package.nix`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/pyproject.toml`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md`
- Test: `package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/test_numeric.py`, `tests/test_raster.py`

**Interfaces:**

- Consumes: `compare_artifacts.collect.DiffSpec` (`before`, `after` line lists, `path`, `state`) and `parse.parse_node` output lines.

- Produces: `numeric.compare_numeric(before: list[str], after: list[str]) -> NumericResult(matched, unmatched_before, unmatched_after, compared, changed, max_delta)`; `raster.render(svg_path, png_path, width=1024)`, `raster.compare_raster(png_before, png_after) -> RasterResult(size_before, size_after, differing_pixels, max_channel_delta)`; CLI flags `--numeric` and `--raster` that add `numeric` and `raster` objects to the `--summary` JSON, keyed by relative path, for modified files only.

- [ ] **Step 1: Write the failing numeric tests**

Create `tests/test_numeric.py` under the compare-artifacts directory:

```python
from compare_artifacts.numeric import NumericResult, compare_numeric


def test_shifted_depth_tags_are_not_deltas():
    before = ["<g @0>", "  <rect @0/0>", "    @x: 5", "</g @0>"]
    after = [
        "<g @0>",
        "  <circle @0/0>",
        "    @r: 1",
        "  <rect @0/1>",
        "    @x: 5",
        "</g @0>",
    ]
    result = compare_numeric(before, after)
    assert result.unmatched_after == 2
    assert result.compared == 1  # the rect's x; the renumbered depth tag is not a number
    assert result.changed == 0
    assert result.max_delta == 0.0


def test_numeric_drift_is_measured_on_matched_lines():
    before = ["<path @0/1>", "  @d:", "    [0000] M 100.0 200.0"]
    after = ["<path @0/1>", "  @d:", "    [0000] M 100.5 199.0"]
    assert compare_numeric(before, after) == NumericResult(3, 0, 0, 2, 2, 1.0)


def test_inserted_element_is_unmatched_not_a_huge_delta():
    before = ["<g @0>", "  <path @0/0>", "    @d: M 1 1", "</g @0>"]
    after = ["<g @0>", "  <path @0/0>", "    @d: M 1 1", "  <path @0/1>", "    @d: M 900 900", "</g @0>"]
    result = compare_numeric(before, after)
    assert result.unmatched_before == 0
    assert result.unmatched_after == 2
    assert result.compared == 2  # the matched path's M 1 1
    assert result.changed == 0
    assert result.max_delta == 0.0
```

- [ ] **Step 2: Run them to verify they fail**

Every test command in this task runs from the package directory in a shell that has pytest, Pillow and resvg (the devshell python has none of the three):

```bash
cd package-sets/top-level/nixos-branding/verification/compare-artifacts
nix shell --impure --expr 'let pkgs = (builtins.getFlake "git+file://'"$(git rev-parse --show-toplevel)"'").inputs.nixpkgs.legacyPackages.x86_64-linux; in { python = pkgs.python3.withPackages (ps: [ ps.pytest ps.pillow ]); inherit (pkgs) resvg; }' python resvg --command pytest tests/test_numeric.py -q
```

Expected: FAIL at import with `ModuleNotFoundError: No module named 'compare_artifacts.numeric'`.

- [ ] **Step 3: Write `numeric.py`**

```python
"""Element-aligned numeric comparison of two parsed SVG line lists.

Lines come from `parse.parse_node`. Numbers are masked, the masked lines
are aligned with difflib, and deltas are measured only between lines that
align. Lines that do not align are counted, not measured: positional
pairing over a file with one inserted element would otherwise report a
meaningless delta.

Alignment is by masked text, so an inserted element whose masked lines
equal an existing element's is paired with it and its numbers are
measured. This is a drift detector for numerically changed files, not a
structural diff; a large delta is a prompt to look at the HTML report.
"""

import difflib
import re
from dataclasses import dataclass

NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
# parse_node's own tokens: the depth tag "@0/1/3>" on open and close lines and
# the index label "[0001]". They are masked so shifted siblings still align,
# but they are not measured: an inserted sibling renumbers every later one.
STRUCTURE = re.compile(r"@\d+(?:/\d+)*>|\[\d+\]")


def mask(line: str) -> str:
    return NUMBER.sub("#", line)


def numbers(line: str) -> list[float]:
    return [float(match) for match in NUMBER.findall(STRUCTURE.sub("", line))]


@dataclass(frozen=True)
class NumericResult:
    matched: int
    unmatched_before: int
    unmatched_after: int
    compared: int  # numbers compared on matched lines
    changed: int  # of those, how many differ
    max_delta: float


def compare_numeric(before: list[str], after: list[str]) -> NumericResult:
    matcher = difflib.SequenceMatcher(
        a=[mask(line) for line in before],
        b=[mask(line) for line in after],
        autojunk=False,
    )
    matched = 0
    unmatched_before = 0
    unmatched_after = 0
    compared = 0
    changed = 0
    max_delta = 0.0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            unmatched_before += i2 - i1
            unmatched_after += j2 - j1
            continue
        for line_before, line_after in zip(before[i1:i2], after[j1:j2], strict=True):
            for x, y in zip(numbers(line_before), numbers(line_after), strict=True):
                compared += 1
                if x != y:
                    changed += 1
                    max_delta = max(max_delta, abs(x - y))
            matched += 1
    return NumericResult(
        matched, unmatched_before, unmatched_after, compared, changed, max_delta
    )
```

- [ ] **Step 4: Run the numeric tests**

Run the same command as Step 2. Expected: 3 passed.

- [ ] **Step 5: Write the failing raster tests**

Create `tests/test_raster.py`:

```python
import shutil
from pathlib import Path

import pytest

from compare_artifacts.raster import RasterResult, compare_raster, render

SQUARE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect x="0" y="0" width="5" height="10" fill="black"/></svg>'
SQUARE_SHIFTED = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect x="1" y="0" width="5" height="10" fill="black"/></svg>'
TALL = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 20"><rect x="0" y="0" width="5" height="20" fill="black"/></svg>'

needs_resvg = pytest.mark.skipif(
    shutil.which("resvg") is None, reason="resvg not on PATH"
)


def write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


@needs_resvg
def test_identical_renders_have_no_differing_pixels(tmp_path):
    a = write(tmp_path / "a.svg", SQUARE)
    render(a, tmp_path / "a.png", width=100)
    render(a, tmp_path / "b.png", width=100)
    assert compare_raster(tmp_path / "a.png", tmp_path / "b.png") == RasterResult(
        (100, 100), (100, 100), 0, 0
    )


@needs_resvg
def test_shifted_shape_counts_differing_pixels(tmp_path):
    render(write(tmp_path / "a.svg", SQUARE), tmp_path / "a.png", width=100)
    render(write(tmp_path / "b.svg", SQUARE_SHIFTED), tmp_path / "b.png", width=100)
    result = compare_raster(tmp_path / "a.png", tmp_path / "b.png")
    assert result.differing_pixels == 2000
    assert result.max_channel_delta == 255


@needs_resvg
def test_size_mismatch_is_reported(tmp_path):
    render(write(tmp_path / "a.svg", SQUARE), tmp_path / "a.png", width=100)
    render(write(tmp_path / "b.svg", TALL), tmp_path / "b.png", width=100)
    result = compare_raster(tmp_path / "a.png", tmp_path / "b.png")
    assert result.size_before == (100, 100)
    assert result.size_after == (100, 200)
    assert result.differing_pixels is None
```

A 1-unit shift of a 5-by-10 rectangle in a 10-unit viewBox at 100 px wide moves 10 px by 100 px of black on each side: 2000 pixels.

- [ ] **Step 6: Run them to verify they fail**

Run the Step 2 command with `tests/test_raster.py` in place of `tests/test_numeric.py`.
Expected: FAIL at import with `ModuleNotFoundError: No module named 'compare_artifacts.raster'`.

- [ ] **Step 7: Write `raster.py`**

```python
"""Rasterised comparison of two SVG files with resvg and Pillow."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops


@dataclass(frozen=True)
class RasterResult:
    size_before: tuple[int, int]
    size_after: tuple[int, int]
    differing_pixels: int | None
    max_channel_delta: int | None


def render(svg_path: Path, png_path: Path, width: int = 1024) -> None:
    subprocess.run(
        ["resvg", "--width", str(width), str(svg_path), str(png_path)],
        check=True,
    )


def compare_raster(png_before: Path, png_after: Path) -> RasterResult:
    before = Image.open(png_before).convert("RGBA")
    after = Image.open(png_after).convert("RGBA")
    if before.size != after.size:
        return RasterResult(before.size, after.size, None, None)
    difference = ImageChops.difference(before, after)
    bands = difference.split()
    combined = bands[0]
    for band in bands[1:]:
        combined = ImageChops.lighter(combined, band)
    histogram = combined.histogram()
    differing = combined.size[0] * combined.size[1] - histogram[0]
    return RasterResult(before.size, after.size, differing, combined.getextrema()[1])
```

- [ ] **Step 8: Run the raster tests**

Run the command from Step 6. Expected: 3 passed.

- [ ] **Step 9: Wire the CLI**

In `cli.py`, add the imports:

```python
import tempfile
from dataclasses import asdict

from compare_artifacts.numeric import compare_numeric
from compare_artifacts.raster import compare_raster, render
```

Add two arguments to `_build_parser`, after `--summary`:

```python
    parser.add_argument(
        "--numeric",
        action="store_true",
        help="For each modified file, align number-masked lines and report "
        "the maximum numeric delta over aligned lines plus the count of "
        "unaligned lines. Written under 'numeric' in the summary JSON.",
    )
    parser.add_argument(
        "--raster",
        action="store_true",
        help="For each modified file, render both versions with resvg at "
        "1024 px wide and report differing pixels. Written under 'raster' "
        "in the summary JSON.",
    )
```

Replace the summary block in `main`:

```python
            if args.summary is not None:
                args.summary.write_text(json.dumps(counts(specs)))
```

with:

```python
            summary: dict[str, object] = dict(counts(specs))
            modified = [spec for spec in specs if spec.state == "modified"]
            if args.numeric:
                numeric = {
                    str(spec.path): asdict(compare_numeric(spec.before, spec.after))
                    for spec in modified
                }
                summary["numeric"] = numeric
                for path, result in numeric.items():
                    print(
                        f"numeric {path}: matched={result['matched']} "
                        f"unmatched={result['unmatched_before']}/{result['unmatched_after']} "
                        f"changed={result['changed']}/{result['compared']} "
                        f"max_delta={result['max_delta']:.6g}"
                    )
            if args.raster:
                raster: dict[str, dict[str, object]] = {}
                with tempfile.TemporaryDirectory() as tmp:
                    for index, spec in enumerate(modified):
                        png_a = Path(tmp) / f"{index}-a.png"
                        png_b = Path(tmp) / f"{index}-b.png"
                        render(path_a / spec.path, png_a)
                        render(path_b / spec.path, png_b)
                        raster[str(spec.path)] = asdict(compare_raster(png_a, png_b))
                summary["raster"] = raster
                for path, result in raster.items():
                    print(
                        f"raster {path}: differing_pixels={result['differing_pixels']} "
                        f"max_channel_delta={result['max_channel_delta']}"
                    )
            if args.summary is not None:
                args.summary.write_text(json.dumps(summary))
```

Without `--numeric` or `--raster` the summary JSON keeps exactly its four integer keys, which is what the CI consumer reads.

- [ ] **Step 10: Packaging**

`pyproject.toml`: add under `[project]`:

```toml
dependencies = ["pillow (>=12,<13)"]
```

`package.nix`: take `resvg` as an argument and wire it in:

```nix
{
  git,
  lib,
  makeWrapper,
  nix,
  python3Packages,
  resvg,
}:

let
  inherit (lib.trivial) importTOML;
  pyproject = importTOML ./pyproject.toml;
in
python3Packages.buildPythonApplication {
  inherit (pyproject.project) name version;
  pyproject = true;
  src = ./.;

  build-system = [ python3Packages.poetry-core ];

  dependencies = [ python3Packages.pillow ];

  nativeBuildInputs = [ makeWrapper ];
  nativeCheckInputs = [
    python3Packages.pytestCheckHook
    resvg
  ];

  pythonImportsCheck = [ "compare_artifacts" ];

  # Ensure `git`, `nix` and `resvg` are on PATH at runtime.
  makeWrapperArgs = [
    "--prefix"
    "PATH"
    ":"
    (lib.makeBinPath [
      git
      nix
      resvg
    ])
  ];
}
```

`README.md`: add to the usage line `[--numeric] [--raster]`, change the sentence "The JSON contains exactly four integer count keys:" under `--summary output` to "By default the JSON contains exactly four integer count keys:", and add a paragraph after the JSON example:

```
With `--numeric` the JSON gains a `numeric` object keyed by relative
path, for modified files only: `matched`, `unmatched_before`,
`unmatched_after` (line counts after aligning number-masked lines) and
`compared` and `changed` (numbers on the matched lines, and how many of
them differ) and `max_delta` over them. Breadth and size together tell a
whole-file drift (most numbers changed a little) from a single moved
coordinate. Alignment is by number-masked text,
so a numerically different file with the same structure is measured
exactly, while an inserted element that masks identically to an existing
one is paired with it; treat a surprising `max_delta` as a prompt to read
the HTML diff. With `--raster` it gains a `raster`
object with `size_before`, `size_after`, `differing_pixels` and
`max_channel_delta` from resvg renders at 1024 px wide; the two pixel
fields are null when the sizes differ.
```

- [ ] **Step 11: Build the package, which runs its tests**

Run: `nix build .#legacyPackages.x86_64-linux.nixos-branding.verification.compare-artifacts --no-link -L 2>&1 | tail -5`
Expected: the pytest run inside the build reports all tests passed, and the build succeeds.

- [ ] **Step 12: Format and commit**

Run: `nix fmt && nix fmt -- --fail-on-change`
Expected: clean.

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts
git commit -F - <<'EOF'
compare-artifacts: add numeric and raster comparison modes

--numeric aligns the number-masked lines of each modified artifact and
reports the maximum delta over aligned lines and the count of lines
that did not align. The parser's own depth tags and index labels are
masked for alignment but excluded from measurement, so an inserted
sibling renumbering later ones is counted, not measured. --raster renders both
versions with resvg and reports differing pixels. Both are written
into the summary JSON only when requested; the four count keys are
unchanged otherwise.

Assisted-by: Claude Code (claude-fable-5-1)
EOF
```

- [ ] **Step 13: Smoke test against main**

Run: `nix run .#nixos-branding.verification.compare-artifacts -- main HEAD --numeric --raster --summary /tmp/nixoslogo-harness/summary.json && cat /tmp/nixoslogo-harness/summary.json`
Expected: `{"modified": 0, "added": 0, "deleted": 0, "unchanged": 96, "numeric": {}, "raster": {}}`. Phase 1 is byte-identical, so both objects are empty; the point is that the tool runs end to end on two real refs.

______________________________________________________________________

## Self-review

**Spec coverage.** Section 3.1 (Task 1), 3.2 (Task 3), 3.3 overlay functions and `dimension_spacings` (Task 2), `LogoClearspace` (Task 6), misuse presets (Task 5), `NixosLogo` composition (Phase 3 plan), 3.4 (Task 4), section 5 steps 1 to 7 (Tasks 1 to 7 in that order), section 6 gates (every task's gate step). Sections 4, steps 8 to 10 and section 7's full suite belong to the Phase 2 and 3 plans.

**Placeholders.** None: every edit shows its code, every test its body, every command its expected output.

**Type consistency.** `clearspace_unit` is a property returning `float` everywhere; `make_canvas(self, clear_space: ClearSpace) -> Canvas` on the base and all four overrides; `LineGroup` fields are `name, stroke, stroke_width, stroke_dasharray, fill` in Task 2's tests, Task 4's class and the overrides TypedDict; `NixosLogo.transform` is used by `logo.py` and nothing else in this phase; `Annotations.sized` and the three presets return `Self`, since they build through `cls`; `geometry.py` keeps concrete names because its operators return fixed classes.

**Review Focus.** Items 1 to 4 are pinned by named artifacts through the harness and build every task runs; item 5 by Task 7's tests. No test duplicates what the build already fails on.
