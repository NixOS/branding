# nixoslogo architecture refactor

Status: design approved in discussion on 2026-10-11; written spec revised
after two review passes against the code, the second adversarial with
implementation attempts on scratch copies; awaiting owner review.
Scope: `package-sets/python-packages/nixoslogo/` and the 96 artifact scripts
under `package-sets/top-level/nixos-branding/artifacts/`.

## 1. Goals and decisions

Three goals, as stated by the owner:

1. Use composition instead of inheritance where inheritance is demonstrably
   wrong.
1. Fix how glyphs are imported, transformed and used.
1. Support fonts of other sizes and weights, other wordmarks, and typefaces
   not packaged today. Mixed fonts inside one word are supported by the
   glyph model (each glyph is built from its own font and scaled by that
   font's cap height) but not exposed on any constructor until a design
   needs it.

Decisions already made:

- Shipped SVG bytes may change. Structural equivalence is verified with
  `compare-artifacts`, numeric drift is bounded and reported, and the 96
  fixed-output hashes are regenerated in the commits that change bytes.
- fontTools replaces fontforge for reading fonts. HarfBuzz (via `uharfbuzz`)
  selects and positions glyphs for wordmarks. Both are in the flake's nixpkgs
  (fonttools 4.60.1, uharfbuzz 0.51.1).
- Bounding boxes and left side bearings are the tight ink extents of the
  outline. Today's bearings already are (fontforge recomputes them from the
  splines); today's boxes are control-point boxes. Control points overhang
  the ink on 60 Route159 and 516 Jura glyphs. One of them is the wordmark's
  "i": its dot's closing curve has control points at y=723 against a tight
  extremum of 721.5. No artifact reads the i's vertical extent (the logotype
  union is set by O and S at 754, and spacing consumes widths only), so the
  logo artifacts are unaffected; annotation label boxes move by sub-unit
  amounts in the step that changes annotation bytes anyway.
- `Annotations` and its line groups become frozen dataclasses: fields cannot
  be rebound after construction, and presets take a typed override
  dictionary instead. (`stroke_dasharray` stays a `list` because svg-py's
  annotation requires one.)
- `NixosLogo` is composed from a `Logomark` and a `Logotype` instance.
- uharfbuzz ships no type information, and basedpyright reports every use
  of its names as an error, not as Unknown. The package ships a local stub,
  `typings/uharfbuzz/__init__.pyi`, declaring the seven names used, and
  `pyproject.toml` gains `[tool.basedpyright] stubPath = "typings"`. The
  gate runs basedpyright with `-p package-sets/python-packages/nixoslogo`.
  Verified: 7 errors without the stub, 0 with it.
- A pytest suite is added, run in the devshell and in the package's check
  phase.

## 2. Problems this fixes

Verified live during the design work. Each is referenced by number below.

| # | Problem | Where |
|---|---|---|
| P1 | `BaseRenderable.__init__` calls the virtual `_make_canvas()` before subclasses that assign after `super().__init__` have set their attributes. Latent today: the `Dimensioned*` overrides read only `radius`, so nothing unset is reached. | `core.py:198`, `dimensioned.py:36` |
| P2 | Every constructor takes `**kwargs` and drops what it does not recognise. `FontConfig.stroke_dasharray` is forwarded into `TextAnnotations` by every preset and survives only because of this. | all renderables, `annotations.py:131` |
| P3 | `Logomark.ilambda` defaults to one `Lambda()` shared by every instance. | `logomark.py:180` |
| P4 | Scaling rewrites the fontforge font's em size, which rounds every coordinate to an integer. The logo asks for cap height 1330.215 and gets 1331-tall glyphs positioned as if 1330.215. Layer transforms store float32. | `logotype.py:72`, shipped SVGs |
| P5 | `fontforge.open` returns one shared object per path. The tempdir copy exists to defeat that; closing invalidates other handles. | `logotype.py:49` |
| P6 | Flip, mirror and bearing strip mutate the shared font. The bearing strip corrupts advance widths (Route159 Regular `i`: 264 to 440). | `logotype.py:86` |
| P7 | Glyph lookup by raw character fails for anything not in `CHARACTER_GLYPHNAME_MAP`; `make_dimension_angle(text=None)` crashes on the degree sign. Fontforge's foreground layer also drops composite glyphs (337 in Jura). | `logotype.py:157`, `annotations.py:441` |
| P8 | `Logotype.elements_bounding_box` subtracts the lead spacing unscaled while `_set_spacings` applied it scaled: with cap-height scaling the box starts at x=159.5 instead of 0 (it subtracts 200 while the first glyph was offset by 200 times 1.7976). | `logotype.py:340` |
| P9 | `Logotype._set_spacings` zips without `strict`, so a six-letter wordmark leaves its tail glyphs at x=0. | `logotype.py:315` |
| P10 | `NixosLogo(loader=...)` positions the logotype with the lambda-derived cap height while the glyphs carry the loader's. The only size hook produces a wrong logo. | `logo.py:56` |
| P11 | `DimensionedLogomark` only works with a `DimensionedLambda`, because the lambda's construction-line drawing is a method on the subclass. | `dimensioned.py:481` |
| P12 | `LogoClearspace` takes a class and instantiates it twice to get two canvases. | `clearspace.py:30` |
| P13 | `LogoScale` and `LogoColorsWithLambdaPrime` are subclasses whose only content is a changed default (`clear_space`, `logotype_style`, or a `_default_cap_height` override returning the lambda radius) and a filename. | `misuse.py:135`, `misuse.py:164` |
| P14 | Five identical `_get_clearspace` match blocks differ only in the unit. | five classes |
| P15 | The defaults are Route159 and NixOS specific: the env-var partial, the transform map that mirrors every "i", and `NixosLogo`'s broken size hook. A standalone `Logotype` can reach another weight or size only by hand-building a `FontLoader`. | `core.py:100`, `logotype.py:34`, `logo.py:30` |

## 3. Structure

### 3.1 Base classes

In `core.py`:

```python
Box = tuple[float, float, float, float]   # min_x, min_y, max_x, max_y

class Shape(ABC):
    @property
    @abstractmethod
    def elements_bounding_box(self) -> Box: ...
    @abstractmethod
    def make_svg_elements(self) -> list[svg.Element]: ...
    # elements_x_min, elements_y_min, elements_x_max, elements_y_max,
    # elements_width, elements_height: moved verbatim from BaseRenderable

@dataclass(kw_only=True)
class BaseRenderable(Shape, ABC):
    clear_space: ClearSpace = ClearSpace.RECOMMENDED
    background_color: str | None = None

    @property
    @abstractmethod
    def clearspace_unit(self) -> float: ...
    @abstractmethod
    def make_filename(self, extras: tuple[str, ...] = ()) -> str: ...

    def make_canvas(self, clear_space: ClearSpace) -> Canvas:
        # today's _make_canvas body, with clear_space.distance(self.clearspace_unit)
    @property
    def canvas(self) -> Canvas:
        return self.make_canvas(self.clear_space)
    # make_svg, make_svg_background, write_svg, canvas_bounding_box unchanged
```

`Shape` is what parents and the clearspace diagram consume. `BaseRenderable`
adds the document behaviour. A frozen dataclass can subclass `Shape`; it
cannot subclass `BaseRenderable` (frozen cannot inherit from non-frozen).

The `canvas=` constructor parameter is removed. No code in the package or the
96 scripts passes it. The four `_make_canvas` overrides (`dimensioned.py:41, 494, 612`, `misuse.py:378`) become `make_canvas(self, clear_space)` overrides
that accept and ignore the parameter, so the signature matches the base.
Fixes P1: nothing is computed during construction.

```python
class ClearSpace(Enum):
    NONE = auto()
    MINIMAL = auto()
    RECOMMENDED = auto()

    def distance(self, unit: float) -> float:
        match self:
            case ClearSpace.NONE:
                return 0            # unchanged from today's match blocks
            case ClearSpace.MINIMAL:
                return unit / 2
            case ClearSpace.RECOMMENDED:
                return unit
```

Fixes P14. `clearspace_unit` per class, each the value its match block uses
today: `Logotype` its cap height, `Lambda` and `Logomark` their
`elements_y_max`, `NixosLogo` its logomark's `elements_height`,
`LogoClearspace` delegates to its logo. `Glyph.clearspace_unit` is
`self.loader.capHeight` until step 9 and `TextAnnotations.clearspace_unit`
is `0` (today's stub) until step 8; after those steps neither is a
`BaseRenderable`.

### 3.2 Dataclasses

Every `BaseRenderable` subclass becomes `@dataclass(kw_only=True)`. Fields are
the constructor parameters. Derived state is `field(init=False)` assigned in
`__post_init__`. Mutable defaults use `default_factory`. Class-level
constants are `ClassVar`. Overriding methods and properties carry
`@override` as they do today.

Fixes P2 (an unknown keyword raises `TypeError`) and P3
(`ilambda: Lambda = field(default_factory=Lambda)`).

**Parameters that are both input and derived state.** Today several
constructors take an optional parameter and store a resolved value under
the same name. A dataclass field typed `X | None` is read as `X | None`
everywhere outside `__post_init__`, which is a basedpyright error at every
later read. The resolution per class:

- `Glyph.loader` and `Logotype.loader`: `loader: FontLoader = field(default_factory=FontLoader)`
  (until step 9 removes the loader).
- `NixosLogo.loader`: the parameter is removed now (no script or package
  caller passes it); `loader: FontLoader = field(init=False)` is built in
  `__post_init__`.
- `NixosLogo.logotype_cap_height: float | None = None` stays an input.
  `__post_init__` resolves it locally, passes it to the loader, and every
  later read uses `self.logotype.cap_height`, which carries the same value.
- `NixosLogo.logotype_transform: svg.Translate | None = None` stays an
  input, read through a `transform` property that returns it or today's
  `_default_transform` arithmetic.

**Classes with `__post_init__`** after the dataclass step: `Logomark`
(colour names), `NixosLogo` (children and loader), `Glyph` (fontforge
objects), `Logotype` and `TextAnnotations` (glyph runs). A subclass
`__post_init__` calls `super().__post_init__()` only when the parent has
one. After step 10 `NixosLogo` has no derived state and no `__post_init__`.

A subclass that wants a different default redeclares the field, with its
annotation: `DimensionedLambda` declares
`clear_space: ClearSpace = ClearSpace.NONE`; at the dataclass step all five
misuse classes declare `ClearSpace.MINIMAL`, and `LogoColorsWithLambdaPrime`
also redeclares `logotype_style: LogotypeStyle = LogotypeStyle.LAMBDAPRIME`
(both until step 5 deletes it). An unannotated class attribute is not a
field: the parent default silently wins, basedpyright only warns, and only
the artifact hash would catch it. The dead pre-`super()` assignments in
`misuse.py` are deleted.

Pitfalls to honour in implementation: every subclass needs its own
`@dataclass(kw_only=True)` decorator or its annotations stop being fields;
`eq=True` (the default) makes instances unhashable, and nothing in the
package hashes a renderable; `Logomark._gradient_stop_offsets` becomes
`GRADIENT_STOP_OFFSETS: ClassVar[tuple[int, int, int]] = (0, 25, 100)` and
all five readers follow (`logomark.py:314, 318, 322`, `dimensioned.py:626, 631`); `Glyph`'s derived fontforge attributes (`font`, `glyph`, `layer`) are
annotated with the `fontforge` classes until step 9 removes them.

### 3.3 Composition changes

**Lambda overlay drawing becomes functions.** In `dimensioned.py`:

| Function | Signature | Reads |
|---|---|---|
| `make_lambda_construction_lines` | `(ilambda: Lambda, lines: LineGroup)` | `annotations.construction_lines` |
| `make_lambda_main_diagonal` | `(ilambda: Lambda, lines: LineGroup)` | `annotations.construction_lines` |
| `make_lambda_off_diagonal` | `(ilambda: Lambda, lines: LineGroup)` | `annotations.construction_lines` |
| `make_lambda_polygons` | `(ilambda: Lambda, lines: LineGroup)` | `annotations.object_lines`; keeps its literal `stroke_dasharray=[4]` on the no-gap polygon |
| `diagonal_line` | `(radius: float) -> Points` | nothing; called with `radius` and with `radius * 2.25` |

`make_hexagon_points` never reads `self` and becomes `hexagon_points(radius)`
in `logomark.py`. `DimensionedLogomark` and `DimensionedLogomarkGradient`
read line styles from their own `annotations`, and their class-level
`ilambda: DimensionedLambda` annotation is deleted, so they accept any
`Lambda`. This must land before the dataclass step: once `Logomark.ilambda`
is a dataclass field, redeclaring it with a narrower type is a basedpyright
error (mutable fields are invariant) and not redeclaring it leaves the
subclass method calls unresolved. Fixes P11. Bodies move verbatim; element
order is unchanged.

**`DimensionedLogotype.dimension_spacings`** derives its gap list from
`itertools.pairwise(self.glyphs)` and its sides from
`["left"] + ["right"] * (len(gaps) - 1)` instead of `range(4)` and a
four-entry list. Identical for five glyphs, which give four gaps.

**`LogoClearspace` takes an instance.**

```python
@dataclass(kw_only=True)
class LogoClearspace(BaseRenderable):
    logo: BaseRenderable
    logo_name: str
    space_object: Shape
    annotations: Annotations
```

The two rectangles come from `logo.make_canvas(ClearSpace.RECOMMENDED)` and
`logo.make_canvas(ClearSpace.MINIMAL)`; the elements from
`logo.make_svg_elements()`. The elements never depended on clear space, only
the canvas did, so one instance suffices. Fixes P12.

**`LogoScale` and `LogoColorsWithLambdaPrime` are deleted.** Their scripts
call `NixosLogo` with the arguments the subclasses supplied and pass the old
filename to `write_svg`:

```python
NixosLogo(clear_space=ClearSpace.MINIMAL, logotype_cap_height=512).write_svg("nixos-logo-misuse-scale")
NixosLogo(clear_space=ClearSpace.MINIMAL, logotype_style=LogotypeStyle.LAMBDAPRIME).write_svg("nixos-logo-misuse-lambdaprime")
```

(After step 10 the cap height and style live on the `Logotype` child.) The
critique pass verified canonicalised output equality. The three geometric
misuse classes stay. Fixes P13.

**`NixosLogo` is composed.** In `logo.py`:

```python
def logotype_cap_height(ilambda: Lambda) -> float:
    return ilambda.radius * (1 + ilambda.thickness * 2) * math.sqrt(3)

@dataclass(kw_only=True)
class NixosLogo(BaseRenderable):
    logomark: Logomark = field(default_factory=Logomark)
    logotype: Logotype
    logo_layout: LogoLayout = LogoLayout.HORIZONTAL
    logotype_transform: svg.Translate | None = None
```

`transform` is a property: the given translate, else today's
`_default_transform` arithmetic using `self.logotype.cap_height`.
`make_filename` reads every component from the children:
`logotype.characters`, `logomark.colors_name`, `logomark.color_style`,
`logotype.color`, `logotype.style`, `logo_layout`, `clear_space`. The
critique pass verified that a logo built this way has identical elements,
bounding box and name to the flattened form. Fixes P10 structurally: there is
no second cap height. `close()` is deleted; no script calls it.

`DimensionedLogo` reads `self.logotype.cap_height`, and its bearing dimension
ends at `Point((self.logomark.circumradius + self.logotype.glyphs[0].elements_x_min, 0))`.
After step 9 the first glyph's minimum x is exactly `spacings[0] * scale`;
today's value differs from that product by 5e-6 because of float32 layer
storage, which is why step 10's byte identity is measured against step 9's
output. `LogoCrop` keeps its `make_canvas` override.

### 3.4 Annotations

```python
@dataclass(frozen=True, kw_only=True)
class LineGroup:
    name: str
    stroke: str
    stroke_width: int
    stroke_dasharray: list[Number]
    fill: str = "transparent"

@dataclass(frozen=True, kw_only=True)
class DimensionLines(LineGroup):
    font: Font = field(repr=False)
    cap_height: float
    color: str

    def make_annotation(self, text: str) -> TextAnnotations: ...
    # make_dimension_line, make_dimension_line_outer, make_dimension_angle,
    # make_dimension_arrow_defs: unchanged bodies, text built via make_annotation

class LineGroupOverrides(TypedDict, total=False):
    stroke: str
    stroke_width: int
    stroke_dasharray: list[Number]
    fill: str

class DimensionLinesOverrides(LineGroupOverrides, total=False):
    font: Font
    cap_height: float
    color: str

class AnnotationsOverrides(TypedDict, total=False):
    object_lines: LineGroupOverrides
    construction_lines: LineGroupOverrides
    dimension_lines: DimensionLinesOverrides

@dataclass(frozen=True, kw_only=True)
class Annotations:
    object_lines: LineGroup
    construction_lines: LineGroup
    dimension_lines: DimensionLines

    def make_annotation(self, text: str) -> TextAnnotations:
        return self.dimension_lines.make_annotation(text)

    @classmethod
    def sized(cls, multiplier: int, overrides: AnnotationsOverrides | None = None) -> "Annotations":
        base = cls(
            object_lines=LineGroup(name="object", stroke="green",
                                   stroke_width=4 * multiplier, stroke_dasharray=[4 * multiplier]),
            construction_lines=LineGroup(name="construction", stroke="blue",
                                         stroke_width=2 * multiplier, stroke_dasharray=[4 * multiplier]),
            dimension_lines=DimensionLines(name="dimension", stroke="red",
                                           stroke_width=1 * multiplier, stroke_dasharray=[4 * multiplier],
                                           font=annotations_font(), cap_height=24 * multiplier, color="black"),
        )
        if overrides is None:
            return base
        return replace(
            base,
            object_lines=replace(base.object_lines, **overrides.get("object_lines", {})),
            construction_lines=replace(base.construction_lines, **overrides.get("construction_lines", {})),
            dimension_lines=replace(base.dimension_lines, **overrides.get("dimension_lines", {})),
        )

    @classmethod
    def small(cls, overrides: AnnotationsOverrides | None = None) -> "Annotations":
        return cls.sized(1, overrides)
    @classmethod
    def medium(cls, overrides: AnnotationsOverrides | None = None) -> "Annotations":
        return cls.sized(2, overrides)
    @classmethod
    def large(cls, overrides: AnnotationsOverrides | None = None) -> "Annotations":
        return cls.sized(4, overrides)
```

`sized(1)`, `sized(2)` and `sized(4)` reproduce today's `small`, `medium` and
`large` literals exactly (stroke widths 4/2/1, 8/4/2, 16/8/4; dash arrays
`[4]`, `[8]`, `[16]`; cap heights 24, 48, 96). The multiplier is an `int` so
the products stay ints. Overrides are absolute values applied after sizing.
A different Jura weight is `{"dimension_lines": {"font": load_font(path)}}`.

basedpyright checks an override literal against the TypedDicts wherever it
runs (the package gate and the editor): a misspelled key or wrong value type
is a `reportArgumentType` error at the call site. Two limits: the literal
must be written inline or in a variable annotated `AnnotationsOverrides`
(an unannotated variable is inferred as `dict[str, ...]` and rejected), and
`dataclasses.replace` itself is unchecked, so the TypedDict field lists are
edited in lockstep with the dataclasses and a drift is caught only by the
runtime `TypeError`. The presets must carry the annotation shown; an
unannotated `overrides` parameter would turn the check into warnings only.

`LineConfig`, `FontConfig`, `ObjectLines` and `ConstructionLines` are deleted
(`FontConfig.scale` was `None` in every preset; `stroke_dasharray` was never
read). The six scripts (eight assignments) that assign
`construction_lines.stroke`, `construction_lines.stroke_dasharray` or
`object_lines.stroke` after construction pass overrides instead:

```python
annotations = Annotations.large(overrides={"construction_lines": {"stroke": "grey"}})
```

Two of them need two keys: `nixos-logomark-dimensioned-gradient-background`
overrides `object_lines` and `construction_lines`;
`nixos-logotype-dimensioned` overrides `stroke` and `stroke_dasharray` under
`construction_lines`.

## 4. Font and glyph pipeline

### 4.1 `font.py`

The only module that imports fontTools or uharfbuzz.

```python
Point = tuple[float, float]
Segment = tuple[Literal["M", "L", "Q", "C"], tuple[Point, ...]]
#   ("M", (p,))  ("L", (p,))  ("Q", (control, p))  ("C", (control1, control2, p))
Contour = tuple[Segment, ...]      # first segment is always "M"
Outline = tuple[Contour, ...]

@dataclass(frozen=True)
class FontGlyph:
    name: str
    outline: Outline                   # font units, y up
    advance: float                     # hmtx advance width
    left_side_bearing: float           # tight ink minimum x; 0.0 for an empty glyph
    bounds: Box | None                 # tight ink bounds; None for an empty glyph

@dataclass(frozen=True)
class ShapedGlyph:
    name: str
    x_advance: float                   # after GPOS positioning
    x_offset: float
    y_offset: float

@dataclass(frozen=True)
class Font:
    path: Path
    name: str                          # the file stem
    em: int
    cap_height: float
    glyphs: Mapping[str, FontGlyph] = field(repr=False)   # every glyph, by glyph name
    cmap: Mapping[int, str] = field(repr=False)           # code point to glyph name
    hb_face: hb.Face = field(repr=False, compare=False)
    hb_font: hb.Font = field(repr=False, compare=False)

    def glyph_for(self, character: str) -> FontGlyph:
        return self.glyphs[self.cmap[ord(character)]]       # KeyError if unencoded

    def shape(self, text: str, features: Mapping[str, bool]) -> tuple[ShapedGlyph, ...]: ...

def load_font(path: Path) -> Font: ...
def logotype_font() -> Font: return load_font(get_nixos_logotype_font_file())
def annotations_font() -> Font: return load_font(get_nixos_annotation_font_file())

def transform(outline: Outline, sx: float, sy: float, dx: float, dy: float) -> Outline: ...
def transform_box(box: Box, sx: float, sy: float, dx: float, dy: float) -> Box: ...
def path_data(outline: Outline) -> list[svg.PathData]: ...
```

`Font` equality compares path, metrics, glyphs and cmap; the HarfBuzz objects
have identity equality and are excluded. `repr=False` on the glyph table
and on every `font` field that holds a `Font` keeps reprs and assertion
messages from printing the whole outline table. Frozen dataclasses with
mapping or list fields are not hashable; nothing hashes them.

`load_font` opens the file with `fontTools.ttLib.TTFont`, iterates
`getGlyphOrder()`, and draws every glyph into a `DecomposingRecordingPen`
built with the glyph set, so composite glyphs are flattened first. The
recording is then replayed into the outline pen, wrapped in
`ReverseContourPen(outputImpliedClosingLine=False)` when the font has a
`CFF ` table. Decomposing before reversing matters because the reverse pen
forwards components to the inner pen unreversed (fontTools'
`_PassThruComponentsMixin`); Route159 has no components, so no shipped glyph
depends on it. The reversal reproduces the command stream the current
pipeline emits for every Route159 glyph (346 of 346 compared), because
fontforge reverses CFF contour direction on import; TrueType outlines
already match without it (all 771 non-composite Jura glyphs compared).
Bounds come from `BoundsPen` (tight ink extents), and `left_side_bearing` is
that box's minimum x, which is what fontforge's `left_side_bearing` reports
today. Advance comes from `hmtx`. Every number is cast to `float` on load,
including bounds, advance and bearing, so that viewBoxes print as `0.0` and
not `0`. `em` is `head.unitsPerEm`. `cap_height` is the top of the bounds of
`glyphs[cmap[ord("H")]]`, which is what fontforge reported (Route159 740,
Jura 1289; the OS/2 table says 1266 for Jura and must not be used). The
font file is read once and nothing is kept open except the HarfBuzz
objects. Measured: 346 glyphs in 57 ms for Route159, 1108 in 166 ms for
Jura.

`shape` is the only HarfBuzz call site. It fills a buffer with the text,
sets `direction="ltr"`, `script="Latn"` and `language="dflt"` explicitly
(the OpenType default language system; never guessed from the process
locale, because Jura carries Turkish and other locale substitutions for
"i"), shapes with the given features, and returns one `ShapedGlyph` per
output glyph with the glyph name from the font's glyph order. Units are
font units. An unencoded character shapes to `.notdef`, whose outline is
rendered; no error is raised. Verified with both fonts: "Nixflake" yields
the `fl` ligature unless `liga` is off; "e" plus combining acute yields
`eacute`; Route159's `cpsp` returns x offsets; Jura's `zero` and `smcp`
select alternate glyphs.

`transform` maps every point of every segment to `(sx * x + dx, sy * y + dy)`
and adds `+ 0.0` to each coordinate so a flipped zero is `0.0`, not `-0.0`.
`transform_box` maps both corners and returns
`(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))`, so a negative scale
re-sorts the box. `path_data` emits the first segment of each contour as
`svg.MoveTo` to its end point, then `LineTo`, `QuadraticBezier` or
`CubicBezier`. No `ClosePath` is emitted; today's output has none and fill
closes implicitly.

### 4.2 `Glyph`

```python
@dataclass(frozen=True)
class Glyph(Shape):
    name: str                          # glyph name
    outline: Outline                   # final SVG-space geometry, y down, placed
    bounds: Box                        # final
    color: str
    style: LogotypeStyle

    @property
    def elements_bounding_box(self) -> Box:
        return self.bounds
    def make_svg_element(self) -> svg.Element | list[svg.Element]: ...
    def make_svg_elements(self) -> list[svg.Element]:
        return flatten_svg_elements(self.make_svg_element())   # today's logotype.py:258-260
```

An empty glyph (a space) has bounds `(x, 0, x, 0)` at its placed origin x on
the baseline. Today an empty fontforge layer reports `(0, 0, 0, 0)`
regardless of placement. Both points lie on the ink box boundary of every
shipped label (x=0 is the first glyph's stripped left edge and y=0 the
baseline), so unions are unchanged.

`make_svg_element` is today's: one `svg.Path` for `REGULAR`; for
`LAMBDAPRIME` and glyph name `x`, two paths from contour 0 split by
`LAMBDAPRIME_X_LOWER = slice(2, 10)` in `core.py`: the lower path is
`contour[LAMBDAPRIME_X_LOWER]`, the upper path is
`contour[:LAMBDAPRIME_X_LOWER.start] + contour[LAMBDAPRIME_X_LOWER.stop:]`
in that order (the other order renders identically but moves bytes), upper
filled `NIXOS_LIGHT_BLUE`, lower `NIXOS_DARK_BLUE`. Because the first
segment of a sub-contour is emitted as `MoveTo`, slicing segments gives the
same paths as slicing points did. The slice is Route159 contour data; it
holds for all 12 Route159 faces (one contour of 12 segments, one `M` and
eleven `L`, in the same order) and is meaningless for any other family.

A `Glyph` is built once at its final position and never mutated. Fixes P6.

### 4.3 `Logotype`

```python
@dataclass(kw_only=True)
class Logotype(BaseRenderable):
    characters: str
    font: Font = field(default_factory=logotype_font, repr=False)
    cap_height: float
    color: str = "black"
    style: LogotypeStyle = LogotypeStyle.REGULAR
    spacings: tuple[float, ...] | None = None     # None: shaped positioning
    features: Mapping[str, bool] = field(default_factory=dict[str, bool])
    mirrored: frozenset[str] = frozenset()        # glyph names
    glyphs: tuple[Glyph, ...] = field(init=False)

    @property
    def scale(self) -> float:
        return self.cap_height / self.font.cap_height
    @property
    def clearspace_unit(self) -> float:
        return self.cap_height
```

`cap_height` and `characters` are required. The 12 native-size artifacts
pass `cap_height=font.cap_height`, which gives scale exactly 1.0.

Glyph selection is the same in both modes: `self.font.shape(characters, features)`. Shaping "NixOS" in Route159 selects `N i x O S`, the glyphs the
current pipeline uses, so the NixOS wordmark is unaffected by the change of
selection path. The `mirrored` set and the `LAMBDAPRIME` glyph-name check
apply to the names `shape` returns, after any substitution: an "i" absorbed
into an `fi` ligature or renamed to `i.sc` by small caps is not matched.

**Manual mode** (`spacings` given). One entry per shaped glyph,
`zip(shaped, spacings, strict=True)`, so a mismatch raises `ValueError`
(fixes P9). Per glyph, in this order:

1. `transform(outline, sx=-1 if name in mirrored else 1, sy=-1, dx=0, dy=0)`
   (flip to y down, optional mirror), and `transform_box` of the glyph's
   bounds the same way;
1. `transform(..., dx=-min_x)` where `min_x` is the first element of that
   transformed box (for an empty glyph, 0): strip the bearing by the
   outline's own minimum x, as the fontforge bearing strip did;
1. `transform(..., sx=scale, sy=scale)`;
1. `transform(..., dx=x_offset)` where `x_offset` accumulates
   `spacing * scale` before the glyph and the glyph's bounds width (today's
   `elements_width`, not its advance) after it.

Today the scale step comes first, as the em rescale, with integer rounding;
the new order scales after the bearing strip. The two differ only in float
rounding, and the step-9 expected deltas were measured with the new order.
From step 9 on the order is pinned because reordering would move bytes.
At scale 1.0 every step is exact, which is why the 12 native-size artifacts
stay byte-identical and serve as the acceptance test for the port.

`elements_bounding_box` is the union of glyph boxes with `min_x` reduced by
`spacings[0] * scale`. Fixes P8.

**Shaped mode** (`spacings` is `None`). Bearings are kept. Per glyph:
flip; then, if mirrored, reflect within the font glyph's own advance
(`x' = FontGlyph.advance - x`); then
`transform(sx=scale, sy=scale, dx=(pen + x_offset) * scale, dy=-y_offset * scale)`,
with `pen` accumulating `ShapedGlyph.x_advance` (the kerned advance).
`elements_bounding_box` is the union of glyph boxes.

The mirrored "i" and the manual spacings are NixOS wordmark data. The
constants `DEFAULT_LOGOTYPE_SPACINGS`, `DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING`
and a new `DEFAULT_LOGOTYPE_MIRRORED = frozenset({"i"})` live in `core.py`
and scripts pass them explicitly.

### 4.4 `TextAnnotations`

```python
@dataclass(kw_only=True)
class TextAnnotations(Shape):
    characters: str
    font: Font = field(repr=False)
    cap_height: float
    color: str = "black"
    glyphs: tuple[Glyph, ...] = field(init=False)

    @property
    def elements_bounding_box(self) -> Box: ...      # union of glyph boxes
    def make_svg_elements(self) -> list[svg.Element]: ...
```

Not frozen, because the placed glyphs are derived state assigned in
`__post_init__`; `Glyph` itself stays frozen. Annotation text is tooling,
not a brand asset, and stays on plain advances through the cmap: no shaping,
no kerning. Per character, with `scale = cap_height / font.cap_height` and
`pen` starting at `-font.glyph_for(characters[0]).left_side_bearing`:
`transform(outline, sx=1, sy=-1, dx=pen, dy=0)` then
`transform(..., sx=scale, sy=scale)`; `pen += advance`. Translate in font
units, then scale: today's order. One `svg.Path` per character including
empty ones, as today. The degree sign resolves through the cmap, so
`make_dimension_angle(text=None)` renders. Fixes P7.

### 4.5 Deleted

`FontLoader` and its tempdir, `atexit`, `__del__`, `cleanup`,
`_cleanup_once`; `CHARACTER_GLYPHNAME_MAP`, `DEFAULT_CHARACTER_TRANSFORMS`,
`DEFAULT_CHARACTER_SET`, `DEFAULT_ROUTE159_TRANSFORMS`,
`DEFAULT_JURA_TRANSFORMS` and the `string` import in `core.py`;
`TextAnnotations._map_characters`; `NixosLogo.close`. Fixes P4, P5, P15.

The `__main__` preview blocks in `logotype.py`, `logomark.py`, `logo.py`,
`annotations.py`, `dimensioned.py`, `artifacts/clearspace.py` and
`artifacts/misuse.py` are not artifacts, but they are inside the basedpyright
and ruff gates. Each migration step rewrites the blocks that reference what
it changes. `annotations.py`'s block, which exercised `FontLoader` and wrote
one `TextAnnotations` preview, is deleted in step 8; that preview is dropped
deliberately.

### 4.6 Data flow

Font file (store path from `NIXOS_LOGOTYPE_FONT_FILE` or
`NIXOS_ANNOTATIONS_FONT_FILE`, or any path a script names) to
`load_font` to a frozen `Font`. Logotype: `Font.shape` to glyph names and
positions, `FontGlyph` outlines through the pinned transform sequence to
`Glyph` values, `path_data` to `svg.Path` elements, `Logotype.make_svg_elements`,
then either `BaseRenderable.make_svg` with the lazy canvas or
`NixosLogo.make_svg_elements` wrapping them in `svg.G(transform=[...])`.
Annotations: `Annotations.sized` to `DimensionLines.font`, `TextAnnotations`
through the cmap and advance layout, to the dimension methods and the
dimensioned and clearspace diagrams. Every coordinate after `load_font` is a
Python float from float64 arithmetic.

### 4.7 Errors

No defensive code at internal boundaries. In `TextAnnotations`, an unencoded
character is a `KeyError` from the cmap. In `Logotype`, HarfBuzz substitutes
`.notdef` and it is rendered. Spacing count mismatch: `ValueError` from
`zip`. Unknown constructor keyword: `TypeError` from the dataclass. Missing
font file: fontTools' own error. A font without an "H" glyph: `KeyError`
from `load_font`.

### 4.8 Dependencies and typing

`pyproject.toml` adds `fonttools` (step 8) and `uharfbuzz` (step 9), and
`poetry.lock` is regenerated in the same commits. `package.nix` drops
`fontforge` and adds the two packages; `editable.nix`, where `fontforge` is
already commented out, adds the two packages. The `nixos-logo-dev` shell
drops `ps.fontforge`. `types-lxml` stays.

fontTools ships no `py.typed`; `TTFont.__getitem__`, `getGlyphSet`,
`getBestCmap` and `BoundsPen.bounds` are partially Unknown under
basedpyright, and `font.py` casts at those calls. uharfbuzz has no type
information at all: every one of its names is an attribute-access error.
Step 9 adds `typings/uharfbuzz/__init__.pyi` under the package directory,
declaring `Blob`, `Face`, `Font`, `Buffer`, `GlyphInfo`, `GlyphPosition` and
`shape` with the signatures `font.py` uses, and
`[tool.basedpyright] stubPath = "typings"` in `pyproject.toml`, which the
editor picks up as well. Nothing outside `font.py` sees either library.
Expected effect on the current 288 warnings: the ~171 from `**kwargs` and
the ~75 from fontforge go; a handful remain inside `font.py`.

## 5. Migration

Every step is one commit, independently mergeable, with the artifact build
green. Verification per step is in section 6. Script counts refer to files
under `artifacts/`. Each step also rewrites the `__main__` blocks that
reference what it changes (section 4.5).

### Phase 1: byte-identical structure

1. **`Shape`, `ClearSpace.distance`, lazy canvas.** `Shape` split out;
   `clearspace_unit` on every class including `Glyph` (`loader.capHeight`)
   and `TextAnnotations` (`0`); `make_canvas(clear_space)` and the `canvas`
   property; `canvas=` parameter removed; the four `_make_canvas` overrides
   renamed and given the parameter. Because the `canvas` property reads
   `self.clear_space`, `BaseRenderable.__init__` gains
   `clear_space: ClearSpace = ClearSpace.RECOMMENDED` and stores it, and
   every subclass that takes `clear_space` today passes it through as
   `super().__init__(clear_space=clear_space, **kwargs)` and stops assigning
   it itself. Read literally without that forwarding, the base default
   overwrites every subclass value and all 52 minimal and no-clear-space
   artifacts come out as recommended. `NixosLogo` keeps its early
   `self.clear_space` assignment as well, because `_init_snowflake` reads it
   before `super().__init__`. `DimensionedLambda`'s post-`super()`
   assignment keeps working only because the canvas is now lazy. No script
   changes.
1. **Dimensioned.** Section 3.3: overlay functions, `diagonal_line`,
   `hexagon_points`, plain-`Lambda` logomark diagrams, glyph-count-derived
   spacing dimensions. The three logomark diagram scripts drop their
   `DimensionedLambda` construction. Before the dataclass step for the
   reason given in 3.3.
1. **Dataclasses.** Every `BaseRenderable` subclass converted per section
   3.2, `loader` kept on `Glyph` and `Logotype`, dead pre-`super()`
   assignments removed. `stroke_dasharray` is removed from `FontConfig` and
   from the three preset literals in this step, not step 4: every
   `TextAnnotations(**font_config)` call forwards it today and it only
   survives through the `**kwargs` hole this step closes; left in place,
   all 12 annotation artifacts would fail to build. No script changes.
1. **Annotations.** Section 3.4, with `DimensionLines` holding
   `font_loader: FontLoader` until step 8. Six scripts (eight assignments)
   switch from attribute assignment to `overrides`.
1. **Misuse presets deleted.** Two scripts call `NixosLogo` directly with
   the arguments shown in section 3.3.
1. **`LogoClearspace` takes an instance.** Three scripts pass instances;
   `nixos-logotype-clearspace` passes `logo=Logotype()` with today's
   defaults.
1. **Verification tooling.** `compare-artifacts` gains a numeric mode and a
   raster mode, with `resvg` as a runtime input and both results written
   into the summary JSON. The numeric mode parses both trees with
   `parse_node`, masks numbers, aligns the masked elements of each file with
   `difflib`, reports unmatched elements on either side, and reports the
   maximum absolute delta over the numbers of matched elements only. The
   pairing rule matters: positional pairing over a file with one extra
   element reports a meaningless delta in the thousands. The raster mode
   renders both trees with `resvg` at 1024 px wide and reports per-file
   pixel differences. No package changes; needed before step 8 can be
   judged.

### Phase 2: pipeline, two hash bumps

8. **`font.py` and annotations.** `font.py` without `shape` and without the
   HarfBuzz fields; `TextAnnotations` becomes the `Shape` of 4.4 on
   outlines; `DimensionLines.font: Font`; presets load `annotations_font()`;
   `annotations.py`'s `__main__` deleted; `fonttools` added and `poetry.lock`
   regenerated. `Logotype` still uses `FontLoader`. Expected: 12 artifacts
   change, the 9 dimensioned and 3 clearspace ones, every element matched,
   numbers only: Jura glyph digits move from float32 to float64 (under
   0.001 units), and label boxes change from control-point to tight
   extents, which moves label translations by sub-unit amounts (measured on
   a reviewer's probe: 0.32 units for a label starting with "1" at cap
   height 24, 0.56 units for the "RECOMMENDED" label's placement). The
   exact maximum is measured by the step-7 tooling and recorded in the
   commit message. No script changes.

1. **Shaping, `Logotype`, `Glyph`, fontforge removed.** `Font.shape`, the
   HarfBuzz fields, `uharfbuzz`, the stub and `stubPath` of 4.8
   (`poetry.lock` regenerated); `Glyph` and `Logotype` per sections 4.2 and
   4.3; `LAMBDAPRIME_X_LOWER` and `DEFAULT_LOGOTYPE_MIRRORED` in `core.py`;
   `NixosLogo` (still flattened) builds
   `Logotype(characters=self.logotype_characters, font=logotype_font(), cap_height=<resolved cap height>, color=..., style=..., spacings=self.logotype_spacings, mirrored=DEFAULT_LOGOTYPE_MIRRORED)`;
   everything in 4.5 deleted; `fontforge` removed from Nix and the
   devshell; the pytest suite of section 7 added with the check phase.
   Scripts, 14 in total:

   - the 12 standalone logotype scripts become
     `font = logotype_font()` then `Logotype(characters="NixOS", font=font, cap_height=font.cap_height, color=..., style=..., spacings=DEFAULT_LOGOTYPE_SPACINGS, mirrored=DEFAULT_LOGOTYPE_MIRRORED, clear_space=...)`;
   - `nixos-logotype-dimensioned` passes `characters="NixOS", cap_height=512, spacings=DEFAULT_LOGOTYPE_SPACINGS, mirrored=DEFAULT_LOGOTYPE_MIRRORED` instead of a loader;
   - `nixos-logotype-clearspace` builds `logo=Logotype(characters="NixOS", font=font, cap_height=font.cap_height, spacings=DEFAULT_LOGOTYPE_SPACINGS, mirrored=DEFAULT_LOGOTYPE_MIRRORED)` and
     `space_object=Logotype(characters="N", font=font, cap_height=font.cap_height, spacings=(0,))`.

   Expected against step 8: 48 artifacts change, the 42 media-kit and
   internal logos, misuse crop, scale and lambdaprime,
   `nixos-logo-dimensioned`, `nixos-logo-clearspace` and
   `nixos-logotype-dimensioned`. Against `main`: 57 (three of the 48 were
   already in step 8's 12). Numeric only, max 1.41 units at default cap
   height, 2.19 for the cap-512 misuse-scale logo and for the cap-512
   `nixos-logotype-dimensioned` glyphs; the logotype's cap height becomes
   exact (N spans plus and minus 665.1075 instead of -665.89 to +665.11).
   One artifact changes structure: on `nixos-logotype-dimensioned` the
   labels 3.36 and 1.039 become 3.357 and 1.038, because today's labels
   measure the rounded glyphs. The longer label adds one glyph path, and
   because labels are centred on their own width, the two label groups'
   translations move by about 9.5 units (half the added digit's advance at
   cap height 24). The numeric mode reports those label paths and groups as
   unmatched or changed elements; they are excluded from the delta bound.
   The 12 native-size logotype artifacts and all 27 lambda and logomark
   artifacts must be byte-identical; they are the acceptance test for the
   port.

These expectations were first measured on a prototype that used the same
float64 arithmetic and operation order over fontforge-extracted outlines,
then reproduced by a fontTools and HarfBuzz implementation of section 4
written during the adversarial review: 12 of 12 native-size logotype
artifacts byte-identical, `nixos-logotype-clearspace` byte-identical, the
default logo at a maximum delta of 1.4078, misuse-scale at 2.1947, and the
two label changes as predicted. A different count, a structural difference
beyond those labels, or a delta above the stated bounds stops the step.

### Phase 3: byte-identical composition

10. **`NixosLogo(logomark=, logotype=)`.** Section 3.3; `logotype_cap_height`
    in `logo.py`. Scripts: the 42 logo scripts, misuse crop, scale and
    lambdaprime, `nixos-logo-dimensioned` and `nixos-logo-clearspace` build
    the two children explicitly. Placed after the pipeline so the 42 scripts
    are rewritten once, in their final form. All 96 artifacts unchanged
    against step 9.

A media-kit script after step 10:

```python
from nixoslogo.logo import NixosLogo, logotype_cap_height

logomark = Logomark(colors=LogomarkColors.RAINBOW, color_style=ColorStyle.GRADIENT)
logotype = Logotype(
    characters="NixOS",
    cap_height=logotype_cap_height(logomark.ilambda),
    color="white",
    style=LogotypeStyle.REGULAR,
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
    mirrored=DEFAULT_LOGOTYPE_MIRRORED,
)
NixosLogo(
    logomark=logomark,
    logotype=logotype,
    logo_layout=LogoLayout.VERTICAL,
    clear_space=ClearSpace.MINIMAL,
).write_svg()
```

### Evidence from the review

Steps 1 and 3 (then numbered 1 and 2) were implemented on a scratch copy by
a reviewer and all 96 scripts run against it: 96 of 96 byte-identical after
each step, ruff clean. The same attempt found the two gaps now fixed above:
the `clear_space` forwarding in step 1, and the dataclass field conflicts
that moved the dimensioned step ahead of the dataclass step and added the
input-versus-derived rule in 3.2. With those, basedpyright on the step-3
copy is expected at 0 errors; the attempt measured 16 errors, all from the
two gaps.

### Optional follow-ups, not part of this plan

- **Dead `<path>` in `make_dimension_line`.** Delete the unstyled path and
  the `point1_text`, `point2_text` and `text_offset_scale` that feed only it
  (`annotations.py:189-191, 280-285`). Six dimensioned artifacts lose those
  elements and nothing else. Separate hash bump.
- **Import-time logging.** `nixoslogo/__init__.py` reconfigures the root
  logger with `force=True` on import. Removing that call and the slash
  replacement in `write_svg` affects no artifact, but neither serves the
  three goals.

## 6. Verification

For every step: `nix build .#hydraJobs.nixos-branding.x86_64-linux.all-artifacts`
green; basedpyright at 0 errors on the package, run as
`basedpyright -p package-sets/python-packages/nixoslogo --pythonpath "$PY"`
from the devshell so the project's `pyproject.toml` (and from step 9 its
`stubPath`) applies; `nix run nixpkgs#ruff -- check` clean;
`nix fmt -- --fail-on-change` clean (the flag goes to treefmt after the
separator; `nix fmt --fail-on-change` is rejected by nix). Compare against
`main`, never against `HEAD` on a clean tree.

The comparison tool builds two committed refs in separate worktrees:

```
nix run .#nixos-branding.verification.compare-artifacts -- main <commit> --summary summary.json
```

Both refs must be commits; the working tree is not consulted.

Byte-identical steps (1 to 7, 10): the build succeeds without touching any
`outputHash`, which is the proof; the comparison against `main` (step 10:
against step 9) reports 96 unchanged.

Hash-bump steps (8, 9):

1. Regenerate with
   `nix run .#legacyPackages.x86_64-linux.nixos-branding.verification.update-nixos-branding-fods`
   and delete its `error.log`.
1. The comparison against `main` reports exactly the expected modified count
   (12 after step 8, 57 after step 9).
1. The step-7 numeric mode reports every element matched for every artifact
   except the label paths and label groups in `nixos-logotype-dimensioned`
   after step 9, and maximum deltas within the bounds in section 5.
1. The step-7 raster mode reports per-file pixel differences for the
   owner's review. resvg renders the gradient, filter and marker artifacts
   correctly (checked on four representative files).
1. The owner reviews the branding guide build and the compare-artifacts
   report.

Downstream packages: at the end of each phase,
`compare-artifacts main <commit> --attr nixos-branding.<pkg>` for
`npm-package`, `deployed-assets` and `release-assets`. Expected: unchanged
after phases 1 and 3; after phase 2 only the files derived from the 57
changed artifacts, every non-SVG file byte-identical.

## 7. Tests

The package has none. The suite lands with step 9 under
`package-sets/python-packages/nixoslogo/tests/`, runs in the devshell with
`pytest`, and runs in the package's check phase: `package.nix` adds
`pytestCheckHook` to `nativeCheckInputs`, takes `jura`, `route159` and
`nixos-branding` as arguments, and sets `NIXOS_LOGOTYPE_FONT_FILE`,
`NIXOS_ANNOTATIONS_FONT_FILE` and
`NIXOS_COLOR_PALETTE_FILE=${nixos-branding.nixos-color-palette}/colors.toml`
(the palette is inside the `nixos-branding` scope, not top level, and
`core.py` reads it at import). Coverage:

- `load_font`: cap heights 740 and 1289, `em` 1000 and 2000, the "x" glyph
  of Route159 has one contour of 12 segments (one `M`, eleven `L`), the
  degree sign and space resolve through the cmap, Jura's "ñ" has two
  contours.
- `path_data` on a flipped integer outline contains no `-0.0`.
- `Logotype` at `cap_height=font.cap_height` has `scale == 1.0` and
  integer-valued outline coordinates (bounds may be fractional: the "i"
  dot's tight top is 721.5).
- `Logotype` with five spacings and "Nixpkgs" raises `ValueError`; with
  seven it lays out seven glyphs left to right.
- Shaped "Nixflake" yields seven glyphs including `fl`; with
  `features={"liga": False}` eight. Shaped "NixOS" in Jura yields `i`, not
  `i.loclTRK`, regardless of the process locale.
- Mirrored "i": the glyph's outline is the reflection of the unmirrored one
  within the font glyph's advance.
- `LAMBDAPRIME` on "x" yields two paths.
- `make_dimension_angle(text=None)` returns elements.
- `Annotations.sized(2)` equals `Annotations.medium()` (`Font` equality
  excludes the HarfBuzz objects); an override replaces only the named field.

## 8. Not changed

- The 1e-13 noise from computing hexagon vertices through radians (74
  artifacts). A separate exact-constant change if ever wanted.
- Gradient stop colours leaving the sRGB gamut under coloraide's default
  mapping.
- `geometry.py`: `__matmul__` duplicating `__mul__`, `list[float]` returns,
  non-strict zips.
- `DimensionedLogotype` and `DimensionedLogo` draw the NixOS wordmark's
  specific dimensions; only the glyph count is generalised.
- Annotation text stays unshaped and unkerned.
- `background_color` and `make_filename` stay on `BaseRenderable`.
- No font cache: each default factory loads the env font anew.
