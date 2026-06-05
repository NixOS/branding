# `compare-artifacts` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `svg-multiline.py` with a tested Python package
(`compare-artifacts`) that takes two git refs, builds the chosen Nix attr
on detached-HEAD worktrees in parallel, and renders an HTML report with a
sticky sidebar, summary counts, and per-file diff tables.

**Architecture:** Python package under
`package-sets/top-level/nixos-branding/verification/compare-artifacts/`,
packaged with `python3Packages.buildPythonApplication`. Six modules:
`cli` (entry point + arg parsing + signal install), `worktree` (context
manager for `git worktree add --detach` + cleanup), `build` (parallel
`nix build` via `ThreadPoolExecutor`), `collect` (SVG file pairing +
state classification + `DiffSpec`), `parse` (pure SVG-to-lines), `report`
(HTML render around `difflib.HtmlDiff.make_table`). Tests cover `parse`
and `collect` only; the orchestration modules are exercised at runtime
via `nix run`.

**Tech Stack:** Python 3.13 (stdlib only — `argparse`, `subprocess`,
`difflib`, `xml.etree.ElementTree`, `concurrent.futures`, `tempfile`,
`shutil`, `signal`, `dataclasses`, `pathlib`, `re`, `math`, `itertools`,
`html`, `typing`), pytest for tests, Nix via `buildPythonApplication`
with `poetry-core` build backend and `pytestCheckHook`.

**Spec:** `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md`.

______________________________________________________________________

## Working directory

All paths in this plan are relative to the repo root
`/home/djacu/dev/nixos/branding/`. The package being built lives at:

```
package-sets/top-level/nixos-branding/verification/compare-artifacts/
```

Refer to this as `<pkg>/` below; spell out the full path in `git add`,
`Read`, `Edit`, `Write` calls.

## File map

| Path | Purpose |
|------|---------|
| `<pkg>/package.nix` | Nix derivation (`python3Packages.buildPythonApplication`) |
| `<pkg>/pyproject.toml` | Project metadata + console_scripts entry |
| `<pkg>/README.md` | Short usage doc |
| `<pkg>/compare_artifacts/__init__.py` | Package marker (empty) |
| `<pkg>/compare_artifacts/__main__.py` | `python -m compare_artifacts` entry |
| `<pkg>/compare_artifacts/cli.py` | argparse, signal install, orchestration |
| `<pkg>/compare_artifacts/worktree.py` | `Worktree` context manager, `Interrupted` exception |
| `<pkg>/compare_artifacts/build.py` | `build_attr` and `build_pair` |
| `<pkg>/compare_artifacts/collect.py` | `DiffSpec`, `path_to_parsed`, `collect_files` |
| `<pkg>/compare_artifacts/parse.py` | Pure SVG → list[str] parsers |
| `<pkg>/compare_artifacts/report.py` | `render_report` + helpers |
| `<pkg>/tests/__init__.py` | (empty) |
| `<pkg>/tests/test_parse.py` | Unit tests for `parse.py` |
| `<pkg>/tests/test_collect.py` | Unit tests for `collect.py` |
| `<pkg>/tests/fixtures/.gitkeep` | Keeps the dir tracked even when empty |
| `svg-multiline.py` | **Deleted at the end** (replaced by this package) |

## Dev environment

Tests run during `nix build` via `pytestCheckHook`. For quick TDD cycles
outside of `nix build`, run pytest directly from the package directory:

```bash
cd package-sets/top-level/nixos-branding/verification/compare-artifacts
nix shell nixpkgs#python313Packages.pytest --command pytest tests/ -v
```

For the full Nix build (which also runs tests):

```bash
nix build .#nixos-branding.verification.compare-artifacts
```

## Commit convention

Match existing repo style: `<scope>: <imperative description>`.
Use `compare-artifacts:` as the scope. Examples in this plan use this
prefix. **Do not add a `Co-Authored-By` trailer.** The pre-commit hook
runs `treefmt` (ruff for Python, nixfmt for Nix, mdformat for
markdown) — if a commit fails because files were reformatted, re-stage
the modified files and re-commit.

______________________________________________________________________

## Phase 1: Scaffolding

### Task 1: Create directory layout and stub Python modules

**Files:**

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/__init__.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/__main__.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/worktree.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/build.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/collect.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/parse.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/__init__.py`

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/fixtures/.gitkeep`

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts
mkdir -p package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/fixtures
```

- [ ] **Step 2: Write `compare_artifacts/__init__.py`** (empty file)

(Just `touch` it — pure package marker.)

- [ ] **Step 3: Write `compare_artifacts/__main__.py`**

```python
from compare_artifacts.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write `compare_artifacts/cli.py`** (stub `main()` so the binary exists)

```python
def main() -> None:
    """Real implementation arrives in later tasks; this stub keeps the
    pyproject console_script wired up so `nix build` produces a binary."""
    print("compare-artifacts: not implemented yet")
```

- [ ] **Step 5: Write empty stub modules**

Each file gets only a one-line module docstring so it imports cleanly:

`compare_artifacts/worktree.py`:

```python
"""Git worktree lifecycle. Populated by a later task."""
```

`compare_artifacts/build.py`:

```python
"""Parallel `nix build` invocation. Populated by a later task."""
```

`compare_artifacts/collect.py`:

```python
"""File pairing and `DiffSpec`. Populated by a later task."""
```

`compare_artifacts/parse.py`:

```python
"""Pure SVG → list[str] parsers. Populated by a later task."""
```

`compare_artifacts/report.py`:

```python
"""HTML report rendering. Populated by a later task."""
```

- [ ] **Step 6: Write `tests/__init__.py`** (empty file — `touch`)

- [ ] **Step 7: Write `tests/fixtures/.gitkeep`** (empty file — keeps the dir in git)

- [ ] **Step 8: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: scaffold Python package layout"
```

______________________________________________________________________

### Task 2: Add `pyproject.toml`

**Files:**

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/pyproject.toml`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "compare-artifacts"
version = "0.1.0"
description = "Diff nixos-branding artifacts between two git refs"
requires-python = ">=3.13"

[project.scripts]
compare-artifacts = "compare_artifacts.cli:main"

[tool.poetry]
packages = [{ include = "compare_artifacts" }]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

Note: `requires-python = ">=3.13"` because `Path.rglob(recurse_symlinks=...)`
(used in `collect.py`) was added in 3.13. The spec wrote `>=3.11` but the
code requires 3.13.

- [ ] **Step 2: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/pyproject.toml
git commit -m "compare-artifacts: add pyproject.toml"
```

______________________________________________________________________

### Task 3: Add `package.nix` (without test hook yet)

**Files:**

- Create: `package-sets/top-level/nixos-branding/verification/compare-artifacts/package.nix`

The `pytestCheckHook` is omitted in this task because no tests exist
yet — pytest would error on no-tests-collected. The hook will be added
back together with the first real test in Task 5.

- [ ] **Step 1: Write `package.nix`**

```nix
{
  git,
  lib,
  makeWrapper,
  nix,
  python3Packages,
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

  nativeBuildInputs = [ makeWrapper ];

  pythonImportsCheck = [ "compare_artifacts" ];

  # Ensure `git` and `nix` are on PATH at runtime.
  makeWrapperArgs = [
    "--prefix" "PATH" ":" (lib.makeBinPath [ git nix ])
  ];
}
```

- [ ] **Step 2: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/package.nix
git commit -m "compare-artifacts: add Nix package"
```

______________________________________________________________________

### Task 4: Verify scaffolding builds and runs

- [ ] **Step 1: Run `nix build`**

```bash
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build succeeds, creates a `result` symlink.

- [ ] **Step 2: Run the CLI**

```bash
./result/bin/compare-artifacts
```

Expected output:

```
compare-artifacts: not implemented yet
```

- [ ] **Step 3: Run via `nix run`**

```bash
nix run .#nixos-branding.verification.compare-artifacts
```

Expected: same output as Step 2.

If any step fails, debug (likely a missing module, typo in `pyproject.toml`,
or wrong attribute path) before continuing.

No commit (verification only).

______________________________________________________________________

## Phase 2: `parse.py` with TDD

Each task below implements one function from `parse.py`. The order is
forced by dependencies: helpers first, then composite parsers, then the
recursive `parse_node`. All tests live in `tests/test_parse.py`. New test
cases get appended; previously-passing tests must keep passing.

The plan tasks lift the function bodies almost verbatim from the existing
`svg-multiline.py`. Two existing bugs are preserved during these tasks
because they live in `collect.py`, not `parse.py`; they're fixed in
Phase 3.

### Task 5: `pad_min` (and the INDENT constants)

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py` (currently doesn't exist — create it)

- Modify: `<pkg>/package.nix` (enable `pytestCheckHook` for the first time)

- [ ] **Step 1: Write the failing tests**

Create `<pkg>/tests/test_parse.py`:

```python
import pytest

from compare_artifacts.parse import pad_min


class TestPadMin:
    def test_empty_sequence_returns_minimum(self):
        # Regression: log10(0) used to crash.
        assert pad_min([]) == 4

    @pytest.mark.parametrize(
        "length,expected",
        [
            (1, 4),  # min wins
            (9999, 4),  # log10(9999) ~ 4
            (10000, 5),  # crosses the boundary
            (99999, 5),
            (100000, 6),
        ],
    )
    def test_length_drives_padding_above_min(self, length, expected):
        assert pad_min([0] * length) == expected

    def test_custom_minimum(self):
        assert pad_min([], min=2) == 2
        assert pad_min([0] * 1000, min=2) == 4  # length wins
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd package-sets/top-level/nixos-branding/verification/compare-artifacts
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: ImportError / failure because `pad_min` and the INDENT
constants don't exist yet.

- [ ] **Step 3: Write the implementation in `<pkg>/compare_artifacts/parse.py`**

Replace the docstring stub with:

```python
"""Pure SVG → list[str] parsers."""

import math
from collections.abc import Sequence

INDENTAMOUNT = 2
INDENTCHAR = " "
INDENT = INDENTAMOUNT * INDENTCHAR


def pad_min(seq: Sequence, min: int = 4) -> int:
    """Return enough width to label `len(seq)` items, never less than `min`.

    Used by the parsers that produce indexed labels like `[0001] M 10 20`.
    """
    if len(seq) == 0:
        return min
    return max(min, math.ceil(math.log10(len(seq))))
```

- [ ] **Step 4: Enable `pytestCheckHook` in `package.nix`**

Edit `<pkg>/package.nix` to add the check hook:

```nix
{
  git,
  lib,
  makeWrapper,
  nix,
  python3Packages,
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

  nativeBuildInputs = [ makeWrapper ];
  nativeCheckInputs = [ python3Packages.pytestCheckHook ];

  pythonImportsCheck = [ "compare_artifacts" ];

  makeWrapperArgs = [
    "--prefix" "PATH" ":" (lib.makeBinPath [ git nix ])
  ];
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 6: Verify the full Nix build still works**

```bash
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes, tests run in the sandbox.

- [ ] **Step 7: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add pad_min parser helper with tests"
```

______________________________________________________________________

### Task 6: `no_name_space`

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import no_name_space


class TestNoNameSpace:
    def test_bare_tag(self):
        assert no_name_space("svg") == "svg"

    def test_namespaced_tag(self):
        assert no_name_space("{http://www.w3.org/2000/svg}svg") == "svg"

    def test_empty_string(self):
        assert no_name_space("") == ""
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 3 new tests fail with ImportError or AttributeError.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

```python
def no_name_space(tag: str) -> str:
    """Strip an XML namespace prefix from a tag name.

    `{http://www.w3.org/2000/svg}svg` → `svg`.
    """
    _, _, only_tag = tag.rpartition("}")
    return only_tag
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 10 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add no_name_space parser helper"
```

______________________________________________________________________

### Task 7: `parse_misc`

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import parse_misc


class TestParseMisc:
    def test_basic_round_trip(self):
        assert parse_misc("  ", "fill", "#abcdef") == "  @fill: #abcdef"

    def test_no_indent(self):
        assert parse_misc("", "id", "foo") == "@id: foo"

    def test_empty_value(self):
        assert parse_misc("", "class", "") == "@class: "
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 3 new tests fail (parse_misc not defined).

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

```python
def parse_misc(indent: str, name: str, value: str) -> str:
    """Render a generic XML attribute as `@name: value`."""
    return f"{indent}@{name}: {value}"
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 13 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add parse_misc parser"
```

______________________________________________________________________

### Task 8: `parse_viewbox`

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import parse_viewbox


class TestParseViewbox:
    def test_four_values(self):
        result = parse_viewbox("", "viewBox", "0 0 100 100")
        assert result == [
            "@viewBox:",
            "  [0000] 0",
            "  [0001] 0",
            "  [0002] 100",
            "  [0003] 100",
        ]

    def test_with_indent(self):
        result = parse_viewbox("  ", "viewBox", "0 0 10 20")
        # parse_viewbox adds INDENT (two spaces) to indent for the value lines.
        assert result[0] == "  @viewBox:"
        assert result[1] == "    [0000] 0"
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 2 new tests fail.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

```python
def parse_viewbox(indent: str, name: str, value: str) -> list[str]:
    """Render a `viewBox="x y w h"` attribute as one indexed line per value."""
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    parts = value.split()
    pad = pad_min(parts)
    for index, elem in enumerate(parts):
        parsed.append(f"{indent}[{index:0{pad}d}] {elem}")
    return parsed
```

Note: This rewrites the existing `svg-multiline.py:parse_viewbox` to split
once and reuse the list, avoiding the double `value.split()` of the
original (functionally identical; cleaner).

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 15 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add parse_viewbox parser"
```

______________________________________________________________________

### Task 9: `parse_d`

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import parse_d


class TestParseD:
    def test_empty_value(self):
        # pad_min returns 4 for empty sequences; header is still emitted.
        assert parse_d("", "d", "") == ["@d:"]

    def test_single_command(self):
        # M 10 20
        assert parse_d("", "d", "M 10 20") == [
            "@d:",
            "  [0000] M 10 20",
        ]

    def test_multi_command(self):
        assert parse_d("", "d", "M 10 20 L 30 40 z") == [
            "@d:",
            "  [0000] M 10 20",
            "  [0001] L 30 40",
            "  [0002] z ",
        ]

    def test_whitespace_handling(self):
        # Letters split the string; surrounding whitespace is preserved on the
        # tail half, then stripped via `elem[1].strip()` in the formatter.
        assert parse_d("", "d", "M10 20L30 40") == [
            "@d:",
            "  [0000] M 10 20",
            "  [0001] L 30 40",
        ]

    def test_with_indent(self):
        result = parse_d("  ", "d", "M 1 2")
        assert result[0] == "  @d:"
        assert result[1] == "    [0000] M 1 2"
```

The trailing-space `"z "` in the multi-command test is intentional —
`parse_d` pairs a letter with the following chunk via `batched`. The
last `"z"` has no following number sequence; the call to `batched`
groups it with empty-ish content, and `.strip()` on the trailing half
yields an empty string. The exact output captures current behavior.

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 5 new tests fail.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

Add the imports needed at the top of the file:

```python
import re
from itertools import batched
```

(Place these next to the existing `import math` etc., to keep imports
grouped.)

Add at the bottom of `parse.py`:

```python
def parse_d(indent: str, name: str, value: str) -> list[str]:
    """Render an SVG path `d="..."` attribute as one indexed line per command.

    The path string is split on alphabetic command letters (M, L, C, ...),
    each letter is paired with the following number sequence, and each
    pair is rendered as `[NNNN] X 1 2 3 ...`.
    """
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    parts = re.split(r"([a-zA-Z]+)", value)
    parts = list(filter(None, parts))
    pairs = list(batched(parts, 2))
    pad = pad_min(pairs)
    for index, elem in enumerate(pairs):
        # batched may yield 1-tuples on a trailing letter; guard with a fallback.
        if len(elem) == 2:
            parsed.append(f"{indent}[{index:0{pad}d}] {elem[0]} {elem[1].strip()}")
        else:
            parsed.append(f"{indent}[{index:0{pad}d}] {elem[0]} ")
    return parsed
```

Note: the original `svg-multiline.py:parse_d` would raise `IndexError`
on a 1-tuple from `batched`. The implementation here is robust to
trailing single letters (the `z`-only test case above). This matches
existing behavior of the original input set but is safer.

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 20 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add parse_d parser"
```

______________________________________________________________________

### Task 10: `parse_points`

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import parse_points


class TestParsePoints:
    def test_empty_value(self):
        assert parse_points("", "points", "") == ["@points:"]

    def test_single_pair(self):
        assert parse_points("", "points", "10 20") == [
            "@points:",
            "  [0000] (10, 20)",
        ]

    def test_multi_pair(self):
        assert parse_points("", "points", "0 0 100 0 50 86") == [
            "@points:",
            "  [0000] (0, 0)",
            "  [0001] (100, 0)",
            "  [0002] (50, 86)",
        ]

    def test_padding_widens_for_large_lists(self):
        value = " ".join(["1 2"] * 12000)  # 12000 pairs
        result = parse_points("", "points", value)
        # 12000 pairs → log10 ~ 5 → pad 5
        assert result[1].startswith("  [00000] ")
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 4 new tests fail.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

```python
def parse_points(indent: str, name: str, value: str) -> list[str]:
    """Render a `points="x1 y1 x2 y2 ..."` attribute as one indexed pair per line."""
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    pairs = list(batched(value.split(), 2))
    pad = pad_min(pairs)
    for index, elem in enumerate(pairs):
        parsed.append(f"{indent}[{index:0{pad}d}] ({elem[0]}, {elem[1]})")
    return parsed
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 24 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add parse_points parser"
```

______________________________________________________________________

### Task 11: `split_transforms`

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import split_transforms


class TestSplitTransforms:
    def test_single(self):
        assert split_transforms("translate(10, 20)") == ["translate(10, 20)"]

    def test_chained(self):
        assert split_transforms("translate(10, 20) rotate(45) scale(2)") == [
            "translate(10, 20)",
            "rotate(45)",
            "scale(2)",
        ]

    def test_no_whitespace_between(self):
        assert split_transforms("translate(10,20)rotate(45)") == [
            "translate(10,20)",
            "rotate(45)",
        ]

    def test_whitespace_inside_parens(self):
        assert split_transforms("translate( 1 , 2 )") == ["translate( 1 , 2 )"]

    def test_empty(self):
        assert split_transforms("") == []
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 5 new tests fail.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

```python
def split_transforms(transform_str: str) -> list[str]:
    """Split an SVG `transform` attribute into individual function calls."""
    # `[a-zA-Z]+\([^)]*\)` matches:
    #   - [a-zA-Z]+   the function name (translate, rotate, ...)
    #   - \([^)]*\)   everything inside the parentheses
    pattern = r"[a-zA-Z]+\([^)]*\)"
    return re.findall(pattern, transform_str)
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 29 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add split_transforms helper"
```

______________________________________________________________________

### Task 12: `parse_transform`

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import parse_transform


class TestParseTransform:
    def test_single(self):
        assert parse_transform("", "transform", "translate(10, 20)") == [
            "@transform:",
            "  translate(10, 20)",
        ]

    def test_chained(self):
        assert parse_transform("", "transform", "translate(1, 2) rotate(45)") == [
            "@transform:",
            "  translate(1, 2)",
            "  rotate(45)",
        ]

    def test_with_indent(self):
        result = parse_transform("    ", "transform", "rotate(0)")
        assert result == [
            "    @transform:",
            "      rotate(0)",
        ]
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 3 new tests fail.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

```python
def parse_transform(indent: str, name: str, value: str) -> list[str]:
    """Render a `transform="..."` attribute as one function call per line."""
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    for part in split_transforms(value):
        parsed.append(f"{indent}{part}")
    return parsed
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 32 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add parse_transform parser"
```

______________________________________________________________________

### Task 13: `parse_attributes`

`parse_attributes` is the dispatcher: it iterates a node's attributes
and dispatches each one to the correct specialised parser. It mutates
the `parsed` list rather than returning a new one (matches the existing
`svg-multiline.py` style).

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
import xml.etree.ElementTree as ET

from compare_artifacts.parse import parse_attributes


class TestParseAttributes:
    def test_misc_attribute(self):
        node = ET.fromstring('<svg id="foo" />')
        parsed: list[str] = []
        parse_attributes(node, parsed, indent="")
        assert parsed == ["  @id: foo"]

    def test_viewbox_attribute(self):
        node = ET.fromstring('<svg viewBox="0 0 100 100" />')
        parsed: list[str] = []
        parse_attributes(node, parsed, indent="")
        assert parsed == [
            "  @viewBox:",
            "    [0000] 0",
            "    [0001] 0",
            "    [0002] 100",
            "    [0003] 100",
        ]

    def test_d_attribute(self):
        node = ET.fromstring('<path d="M 0 0 L 1 1" />')
        parsed: list[str] = []
        parse_attributes(node, parsed, indent="")
        assert parsed == [
            "  @d:",
            "    [0000] M 0 0",
            "    [0001] L 1 1",
        ]

    def test_transform_attribute(self):
        node = ET.fromstring('<g transform="rotate(45)" />')
        parsed: list[str] = []
        parse_attributes(node, parsed, indent="")
        assert parsed == [
            "  @transform:",
            "    rotate(45)",
        ]

    def test_points_attribute(self):
        node = ET.fromstring('<polygon points="0 0 1 1" />')
        parsed: list[str] = []
        parse_attributes(node, parsed, indent="")
        assert parsed == [
            "  @points:",
            "    [0000] (0, 0)",
            "    [0001] (1, 1)",
        ]
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 5 new tests fail.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

Add a typing import next to the others:

```python
from xml.etree.ElementTree import Element
```

Then add at the bottom of `parse.py`:

```python
def parse_attributes(node: Element, parsed: list[str], indent: str) -> None:
    """Dispatch each attribute on `node` to the appropriate parser.

    Mutates `parsed` in place by appending one or more lines per attribute.
    The dispatching is intentionally hard-coded: each named SVG attribute
    has a render that produces more readable output than `parse_misc`.
    """
    indent += INDENT
    for name, value in node.attrib.items():
        match name:
            case "d":
                parsed.extend(parse_d(indent, name, value))
            case "points":
                parsed.extend(parse_points(indent, name, value))
            case "transform":
                parsed.extend(parse_transform(indent, name, value))
            case "viewBox":
                parsed.extend(parse_viewbox(indent, name, value))
            case _:
                parsed.append(parse_misc(indent, name, value))
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 37 tests pass.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add parse_attributes dispatcher"
```

______________________________________________________________________

### Task 14: `parse_node` (recursive)

`parse_node` is the top-level entry point. It produces the full line
representation of an `<svg>` element and all of its descendants. Each
element gets a `depth` tag (`@0/0/2/1`-style) so the diff algorithm can
distinguish sibling tags that share a name.

**Files:**

- Modify: `<pkg>/compare_artifacts/parse.py`

- Modify: `<pkg>/tests/test_parse.py`

- [ ] **Step 1: Add the failing tests** at the bottom of `tests/test_parse.py`:

```python
from compare_artifacts.parse import parse_node


class TestParseNode:
    def test_minimal_element(self):
        node = ET.fromstring("<svg />")
        assert parse_node(node, []) == [
            "<svg @0>",
            "</svg @0>",
        ]

    def test_with_attribute(self):
        node = ET.fromstring('<svg id="root" />')
        assert parse_node(node, []) == [
            "<svg @0>",
            "  @id: root",
            "</svg @0>",
        ]

    def test_nested_children(self):
        node = ET.fromstring("<svg><g /><g /></svg>")
        assert parse_node(node, []) == [
            "<svg @0>",
            "  <g @0/0>",
            "  </g @0/0>",
            "  <g @0/1>",
            "  </g @0/1>",
            "</svg @0>",
        ]

    def test_depth_disambiguates_siblings(self):
        # Two <g> siblings get distinct depth tags so the differ doesn't
        # confuse them.
        node = ET.fromstring("<svg><g id=\"a\" /><g id=\"b\" /></svg>")
        lines = parse_node(node, [])
        assert "  <g @0/0>" in lines
        assert "  <g @0/1>" in lines

    def test_namespaced_tag_is_stripped(self):
        # `{ns}tag` becomes `tag` thanks to no_name_space.
        node = ET.fromstring(
            '<svg xmlns="http://www.w3.org/2000/svg"><g /></svg>'
        )
        lines = parse_node(node, [])
        assert lines[0] == "<svg @0>"
        assert "  <g @0/0>" in lines
```

- [ ] **Step 2: Run to verify failure**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: 5 new tests fail.

- [ ] **Step 3: Add the implementation** at the bottom of `parse.py`:

```python
def parse_node(
    node: Element,
    parsed: list[str],
    indent: str = "",
    depth: str = "@0",
) -> list[str]:
    """Recursively render an XML element as a list of lines.

    `depth` is a per-node tag (`@0`, `@0/1`, `@0/1/3`, ...) appended to the
    open/close lines so the diff algorithm can tell apart sibling elements
    that share a name.
    """
    parsed.append(f"{indent}<{no_name_space(node.tag)} {depth}>")
    parse_attributes(node, parsed, indent=indent)
    for index, child in enumerate(node.findall("*")):
        parse_node(
            child,
            parsed,
            indent=indent + INDENT,
            depth=depth + f"/{index}",
        )
    parsed.append(f"{indent}</{no_name_space(node.tag)} {depth}>")
    return parsed
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_parse.py -v
```

Expected: all 42 tests pass.

- [ ] **Step 5: Verify the full Nix build (with all tests in the sandbox)**

```bash
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: the build runs pytest and all tests pass.

- [ ] **Step 6: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add parse_node recursive parser"
```

______________________________________________________________________

## Phase 3: `collect.py` with TDD

### Task 15: `DiffSpec` and the I/O helpers

This task adds the `DiffSpec` dataclass, the `path_to_parsed` bridge
between filesystem and the pure parser, and the `glob_path_no_parent`
helper. These are tested indirectly via `collect_files` in Task 16, so
no separate test classes are added here.

**Files:**

- Modify: `<pkg>/compare_artifacts/collect.py`

- [ ] **Step 1: Write `<pkg>/compare_artifacts/collect.py`**

Replace the docstring stub with:

```python
"""File pairing and DiffSpec.

This module owns the single I/O boundary into the SVG parser:
`path_to_parsed` reads an SVG file from disk and hands its parsed root
to `compare_artifacts.parse.parse_node`. Everything else in `parse.py`
stays pure.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from compare_artifacts.parse import parse_node


@dataclass
class DiffSpec:
    before: list[str]
    after: list[str]
    path: Path  # relative to the build output root
    state: Literal["added", "removed", "changed", "unchanged"]


def path_to_parsed(root: Path, rel: Path) -> list[str]:
    """Read the SVG at `root / rel` and return its parsed line representation."""
    return parse_node(ET.fromstring((root / rel).read_text()), [])


def glob_path_no_parent(root: Path, glob: str) -> set[Path]:
    """Return all relative paths under `root` matching `glob`.

    Symlinks are followed so build outputs that link into the Nix store
    are walked transparently.
    """
    return {
        rpath.relative_to(root)
        for rpath in root.rglob(glob, recurse_symlinks=True)
    }
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
nix shell nixpkgs#python313 --command python -c \
  "import sys; sys.path.insert(0, '.'); from compare_artifacts.collect import DiffSpec, path_to_parsed, glob_path_no_parent; print('ok')"
```

Expected output: `ok`. (Run from inside the package directory.)

- [ ] **Step 3: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add DiffSpec and I/O helpers in collect.py"
```

______________________________________________________________________

### Task 16: `collect_files` with full state-classification tests

This is where the two bugs in `svg-multiline.py:collect_files` get
fixed: the `(True, False)` branch uses `state = "removed"` (not
`"remove"`), and the `(False, True)` branch parses from `after_root`
(not `before_root`).

**Files:**

- Modify: `<pkg>/compare_artifacts/collect.py`

- Create: `<pkg>/tests/test_collect.py`

- [ ] **Step 1: Write `<pkg>/tests/test_collect.py`** (the full file)

```python
from pathlib import Path

import pytest

from compare_artifacts.collect import DiffSpec, collect_files


# Tiny SVG fragments. The content has to differ visibly between A and B
# for the parser to produce different line outputs.
SVG_A = '<svg id="a"><g /></svg>'
SVG_B = '<svg id="b"><g /></svg>'


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestCollectFiles:
    def test_empty_trees(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        before.mkdir()
        after.mkdir()
        assert collect_files(before, after) == []

    def test_unchanged(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "logo.svg", SVG_A)
        write(after / "logo.svg", SVG_A)
        specs = collect_files(before, after)
        assert len(specs) == 1
        assert specs[0].state == "unchanged"
        assert specs[0].path == Path("logo.svg")

    def test_changed(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "logo.svg", SVG_A)
        write(after / "logo.svg", SVG_B)
        specs = collect_files(before, after)
        assert len(specs) == 1
        assert specs[0].state == "changed"
        assert specs[0].before != specs[0].after

    def test_added(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        before.mkdir()
        write(after / "new.svg", SVG_A)
        specs = collect_files(before, after)
        assert len(specs) == 1
        assert specs[0].state == "added"
        assert specs[0].before == []
        # Regression: the original code mistakenly parsed from before_root here.
        assert specs[0].after != []

    def test_removed(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "gone.svg", SVG_A)
        after.mkdir()
        specs = collect_files(before, after)
        assert len(specs) == 1
        # Regression: the original code wrote "remove" here.
        assert specs[0].state == "removed"
        assert specs[0].before != []
        assert specs[0].after == []

    def test_sorted_by_path(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        for name in ["z.svg", "a.svg", "m.svg"]:
            write(before / name, SVG_A)
            write(after / name, SVG_A)
        specs = collect_files(before, after)
        assert [s.path for s in specs] == [
            Path("a.svg"),
            Path("m.svg"),
            Path("z.svg"),
        ]

    def test_subdirectory_paths_preserved(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "clearspace" / "logo.svg", SVG_A)
        write(after / "clearspace" / "logo.svg", SVG_B)
        specs = collect_files(before, after)
        assert specs[0].path == Path("clearspace") / "logo.svg"
        assert specs[0].state == "changed"

    def test_returns_diffspec_instances(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        write(before / "logo.svg", SVG_A)
        write(after / "logo.svg", SVG_A)
        specs = collect_files(before, after)
        assert isinstance(specs[0], DiffSpec)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_collect.py -v
```

Expected: `ImportError` for `collect_files` (it doesn't exist yet).

- [ ] **Step 3: Add `collect_files` to `<pkg>/compare_artifacts/collect.py`**

Append at the bottom of `collect.py`:

```python
def collect_files(before_root: Path, after_root: Path) -> list[DiffSpec]:
    """Pair SVG files between two artifact trees and classify each pair.

    Returns one `DiffSpec` per file appearing in either tree, sorted by
    relative path. Includes `unchanged` specs so callers can show summary
    counts; filtering them out is the caller's responsibility.
    """
    before_files = glob_path_no_parent(before_root, "*.svg")
    after_files = glob_path_no_parent(after_root, "*.svg")
    all_files = sorted(before_files | after_files)
    diff_specs: list[DiffSpec] = []

    for path in all_files:
        match (path in before_files, path in after_files):
            case (True, True):
                before = path_to_parsed(before_root, path)
                after = path_to_parsed(after_root, path)
                state = "unchanged" if before == after else "changed"
            case (True, False):
                before = path_to_parsed(before_root, path)
                after = []
                state = "removed"
            case (False, True):
                before = []
                after = path_to_parsed(after_root, path)
                state = "added"
            case _:
                # Cannot happen — `all_files` is the union, so each path
                # is in at least one of the sets.
                raise AssertionError(f"unreachable: {path}")

        diff_specs.append(DiffSpec(before=before, after=after, path=path, state=state))

    return diff_specs
```

- [ ] **Step 4: Run tests to verify pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_collect.py -v
```

Expected: all 8 tests pass.

- [ ] **Step 5: Verify the full Nix build**

```bash
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: the build runs `test_parse.py` (42 tests) and
`test_collect.py` (8 tests) and all pass.

- [ ] **Step 6: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add collect_files with state classification"
```

______________________________________________________________________

## Phase 4: Orchestration modules (no unit tests)

These modules touch the filesystem, run subprocesses, install signal
handlers, or render HTML. They are exercised end-to-end in Phase 5 (via
`nix run` against real refs), not via unit tests.

### Task 17: `worktree.py` — Worktree context manager + Interrupted exception

**Files:**

- Modify: `<pkg>/compare_artifacts/worktree.py`

- [ ] **Step 1: Write `<pkg>/compare_artifacts/worktree.py`**

Replace the docstring stub with:

```python
"""Git worktree lifecycle.

The `Worktree` context manager creates a temporary detached-HEAD worktree
at `__enter__`, yields its path, and decides at `__exit__` whether to
remove it. The decision depends on what caused the `with`-block to exit
(see the spec's exit-time decision matrix):

  - Success or KeyboardInterrupt (SIGINT) → remove unless `--keep` is set.
  - Interrupted (SIGTERM / SIGHUP) → keep regardless of `--keep`.
  - Any other exception → keep regardless of `--keep`.

`Interrupted` inherits from `BaseException` so that `except Exception`
clauses (including those inside `ThreadPoolExecutor` worker threads)
don't swallow it.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from types import TracebackType


class Interrupted(BaseException):
    """Raised by signal handlers for SIGTERM / SIGHUP."""


class Worktree:
    """Create a temporary detached-HEAD worktree at `ref`."""

    def __init__(self, ref: str, *, keep: bool = False) -> None:
        self._ref = ref
        self._keep = keep
        self._path: Path | None = None

    def __enter__(self) -> Path:
        tmp = tempfile.mkdtemp(prefix="compare-artifacts-")
        try:
            subprocess.run(
                ["git", "worktree", "add", "--detach", tmp, self._ref],
                check=True,
            )
        except BaseException:
            # `git worktree add` failed or was interrupted; clean up the
            # empty tmp dir before re-raising.
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        self._path = Path(tmp)
        return self._path

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if self._path is None:
            # `__enter__` failed; nothing to clean.
            return False

        path = self._path

        # Clean-up branch: success OR SIGINT (KeyboardInterrupt). Both
        # are "normal" exits; nothing is still writing to the worktree.
        is_clean_exit = exc_type is None or issubclass(exc_type, KeyboardInterrupt)

        if is_clean_exit and not self._keep:
            try:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(path)],
                    check=True,
                )
            except subprocess.CalledProcessError:
                # A cleanup hiccup never masks the original exit cause.
                print(f"worktree kept at {path} (cleanup failed)")
        else:
            # `--keep`, SIGTERM/SIGHUP, or any other exception → keep.
            print(f"worktree kept at {path}")

        return False  # never swallow the exception
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
nix shell nixpkgs#python313 --command python -c \
  "import sys; sys.path.insert(0, '.'); from compare_artifacts.worktree import Worktree, Interrupted; print('ok')"
```

Expected: `ok`.

- [ ] **Step 3: Smoke-test the context manager against the real repo**

(Optional but very useful: catches obvious bugs before integration.)

From the repo root:

```bash
nix shell nixpkgs#python313 --command python -c "
import sys; sys.path.insert(0, 'package-sets/top-level/nixos-branding/verification/compare-artifacts')
from compare_artifacts.worktree import Worktree
with Worktree('main') as p:
    print('created at', p)
    assert p.exists() and (p / 'flake.nix').exists()
print('after exit')
"
```

Expected: prints the temp path (under `/tmp`), then `worktree kept at .../` (because the context manager doesn't remove on this path) or
removes it (if it doesn't see an exception). The exact output depends
on the success path — in success mode, the printed path is from the
removal log. You should see:

```
created at /tmp/compare-artifacts-XXXXXX
after exit
```

with no `worktree kept` line (because success + not-`--keep` runs the
removal silently). If you see the `worktree kept` line, the cleanup
failed — investigate.

- [ ] **Step 4: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add Worktree context manager"
```

______________________________________________________________________

### Task 18: `build.py` — parallel `nix build`

**Files:**

- Modify: `<pkg>/compare_artifacts/build.py`

- [ ] **Step 1: Write `<pkg>/compare_artifacts/build.py`**

Replace the docstring stub with:

```python
"""Parallel `nix build` invocation.

`build_attr` runs `nix build --no-link --print-out-paths .#<attr>` in a
given worktree and captures the printed store path. `build_pair` runs
two `build_attr` calls concurrently via `ThreadPoolExecutor`.

stdout is piped (to capture the store path); stderr is inherited (so
nix's progress output streams to the user's terminal). Two concurrent
builds means stderr from both interleaves — functional, visually messy.
"""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def build_attr(worktree_path: Path, attr: str) -> Path:
    """Run `nix build` for `attr` inside `worktree_path` and return the store path."""
    result = subprocess.run(
        ["nix", "build", "--no-link", "--print-out-paths", f".#{attr}"],
        cwd=worktree_path,
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def build_pair(wt_a: Path, wt_b: Path, attr: str) -> tuple[Path, Path]:
    """Build `attr` on both worktrees concurrently. Returns (path_a, path_b)."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_a = pool.submit(build_attr, wt_a, attr)
        fut_b = pool.submit(build_attr, wt_b, attr)
        return fut_a.result(), fut_b.result()
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
nix shell nixpkgs#python313 --command python -c \
  "import sys; sys.path.insert(0, '.'); from compare_artifacts.build import build_attr, build_pair; print('ok')"
```

(From inside the package dir.) Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add build_attr and build_pair"
```

______________________________________________________________________

### Task 19: `report.py` — HTML rendering

`report.py` is the biggest file outside `parse.py`. It builds:

1. The CSS string (constant), including dark-mode rules gated on
   `body:has(.dark-toggle:checked) ...`.
1. The summary header (4 counts).
1. The sticky sidebar, grouped by top-level subdirectory, with a CSS-only
   dark-mode toggle button at the top.
1. One `<section>` per non-unchanged file, each containing
   `difflib.HtmlDiff().make_table(...)`.
1. The full page shell wrapping the above. A hidden checkbox at the top
   of `<body>` is the dark-mode state holder; the visible label inside
   the sidebar is `for=`-linked to it. No JavaScript.

There are no unit tests for HTML output (golden-file tests are brittle).
Visual inspection in Phase 5 serves the same purpose.

**Files:**

- Modify: `<pkg>/compare_artifacts/report.py`

- [ ] **Step 1: Write `<pkg>/compare_artifacts/report.py`**

Replace the docstring stub with:

```python
"""HTML report rendering.

`render_report` produces a self-contained HTML document with:

  - A sticky sidebar grouped by top-level subdirectory, with color-coded
    state badges (A/M/D).
  - A summary header in the main area showing counts and ref / attr
    metadata.
  - One `<section>` per non-unchanged file, containing
    `difflib.HtmlDiff().make_table(...)` output.

CSS is embedded; the report has no external assets.
"""

import difflib
import html
from collections import defaultdict
from pathlib import Path

from compare_artifacts.collect import DiffSpec


STYLES = """
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    align-items: flex-start;
}
aside.sidebar {
    width: 280px;
    flex-shrink: 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid #ddd;
    padding: 1em;
    box-sizing: border-box;
    font-size: 0.9em;
    background: #fafafa;
}
aside.sidebar h3 {
    margin: 1em 0 0.3em;
    font-size: 0.95em;
    color: #333;
}
aside.sidebar ul {
    list-style: none;
    padding: 0;
    margin: 0;
}
aside.sidebar li {
    padding: 0.15em 0;
}
aside.sidebar a {
    text-decoration: none;
    color: #0366d6;
}
aside.sidebar .sidebar-summary {
    padding: 0.5em 0;
    border-bottom: 1px solid #ddd;
    font-weight: 600;
}
.count {
    color: #888;
    font-weight: normal;
}
.badge {
    display: inline-block;
    width: 1.2em;
    text-align: center;
    font-weight: 700;
    border-radius: 3px;
    margin-right: 0.4em;
    font-size: 0.85em;
    color: white;
}
.badge-A { background: #28a745; }
.badge-M { background: #f0a500; }
.badge-D { background: #d73a49; }
main {
    flex-grow: 1;
    padding: 1em 2em;
    overflow-x: auto;
}
header.summary {
    margin-bottom: 2em;
    padding-bottom: 1em;
    border-bottom: 1px solid #ddd;
}
section {
    margin-bottom: 2em;
}
section h2 {
    font-family: Menlo, Consolas, monospace;
    font-size: 1.1em;
}
table.diff {
    font-family: Menlo, Consolas, Monaco, Liberation Mono, Lucida Console, monospace;
    border: medium;
    width: 100%;
}
.diff_header { background-color: #e0e0e0; }
td.diff_header { text-align: right; }
.diff_next { background-color: #c0c0c0; }
.diff_add { background-color: #aaffaa; }
.diff_chg { background-color: #ffff77; }
.diff_sub { background-color: #ffaaaa; }

/* Dark-mode toggle (CSS-only): the checkbox is hidden; the label is
   the visible button. `body:has(.dark-toggle:checked)` flips colors. */
input.dark-toggle {
    position: absolute;
    opacity: 0;
    pointer-events: none;
}
label.dark-button {
    display: inline-block;
    cursor: pointer;
    padding: 0.3em 0.6em;
    margin-top: 0.5em;
    background: #eee;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.85em;
    user-select: none;
}
label.dark-button:hover { background: #ddd; }
label.dark-button::before { content: "Dark mode"; }
body:has(.dark-toggle:checked) label.dark-button::before {
    content: "Light mode";
}

/* Dark theme — only applied when the checkbox is checked. */
body:has(.dark-toggle:checked) {
    background: #1a1a1a;
    color: #e0e0e0;
}
body:has(.dark-toggle:checked) aside.sidebar {
    background: #222;
    border-right-color: #444;
}
body:has(.dark-toggle:checked) aside.sidebar h3 { color: #ddd; }
body:has(.dark-toggle:checked) aside.sidebar a { color: #58a6ff; }
body:has(.dark-toggle:checked) aside.sidebar .sidebar-summary {
    border-bottom-color: #444;
}
body:has(.dark-toggle:checked) label.dark-button {
    background: #333;
    border-color: #555;
    color: #e0e0e0;
}
body:has(.dark-toggle:checked) label.dark-button:hover { background: #444; }
body:has(.dark-toggle:checked) header.summary {
    border-bottom-color: #444;
}
body:has(.dark-toggle:checked) code {
    background: #333;
    padding: 0.1em 0.3em;
    border-radius: 2px;
}
body:has(.dark-toggle:checked) .diff_header {
    background-color: #2a2a2a;
    color: #c0c0c0;
}
body:has(.dark-toggle:checked) .diff_next {
    background-color: #333;
    color: #ddd;
}
body:has(.dark-toggle:checked) .diff_add {
    background-color: #1f4f1f;
    color: #aaffaa;
}
body:has(.dark-toggle:checked) .diff_chg {
    background-color: #4f4f1f;
    color: #ffff77;
}
body:has(.dark-toggle:checked) .diff_sub {
    background-color: #4f1f1f;
    color: #ffaaaa;
}
"""


_STATE_TO_BADGE = {
    "added": "A",
    "changed": "M",
    "removed": "D",
}


def _counts(specs: list[DiffSpec]) -> dict[str, int]:
    counts = {"added": 0, "changed": 0, "removed": 0, "unchanged": 0}
    for spec in specs:
        counts[spec.state] += 1
    return counts


def _visible(specs: list[DiffSpec]) -> list[DiffSpec]:
    return [s for s in specs if s.state != "unchanged"]


def render_summary(specs: list[DiffSpec], ref_a: str, ref_b: str, attr: str) -> str:
    counts = _counts(specs)
    return (
        '<header class="summary">'
        f"<p><strong>{counts['changed']} changed</strong> · "
        f"{counts['added']} added · "
        f"{counts['removed']} removed · "
        f"{counts['unchanged']} unchanged (hidden)</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )


def _group_by_subdir(visible: list[DiffSpec]) -> dict[str, list[tuple[int, DiffSpec]]]:
    """Group visible specs by their top-level subdirectory, preserving order.

    Each (index, spec) tuple carries the spec's position in the visible
    list — used as the section ID (`diff-N`).
    """
    groups: dict[str, list[tuple[int, DiffSpec]]] = defaultdict(list)
    for index, spec in enumerate(visible):
        parts = spec.path.parts
        # If the file sits at the root (no subdir), group it under "(root)".
        subdir = parts[0] if len(parts) > 1 else "(root)"
        groups[subdir].append((index, spec))
    return groups


def render_sidebar(specs: list[DiffSpec]) -> str:
    counts = _counts(specs)
    visible = _visible(specs)
    groups = _group_by_subdir(visible)

    out = ['<aside class="sidebar">']
    out.append(
        '<section class="sidebar-summary">'
        f"{counts['changed']} changed · "
        f"{counts['added']} added · "
        f"{counts['removed']} removed · "
        f"{counts['unchanged']} unchanged"
        '<br /><label for="dark-toggle" class="dark-button"></label>'
        "</section>"
    )
    out.append("<nav>")
    for subdir, entries in groups.items():
        out.append(
            f"<h3>{html.escape(subdir)} "
            f'<span class="count">({len(entries)})</span></h3>'
        )
        out.append("<ul>")
        for index, spec in entries:
            badge = _STATE_TO_BADGE[spec.state]
            # Show the path relative to the subdir for less visual noise.
            label = spec.path.name if subdir == "(root)" else str(
                spec.path.relative_to(subdir)
            )
            out.append(
                f'<li><a href="#diff-{index}">'
                f'<span class="badge badge-{badge}">{badge}</span>'
                f"{html.escape(label)}</a></li>"
            )
        out.append("</ul>")
    out.append("</nav>")
    out.append("</aside>")
    return "".join(out)


def render_diff_section(
    index: int,
    spec: DiffSpec,
    *,
    context: int,
    full: bool,
    ref_a: str,
    ref_b: str,
) -> str:
    badge = _STATE_TO_BADGE[spec.state]
    table = difflib.HtmlDiff().make_table(
        spec.before,
        spec.after,
        fromdesc=f"{spec.path} ({ref_a})",
        todesc=f"{spec.path} ({ref_b})",
        context=not full,
        numlines=context,
    )
    return (
        f'<section id="diff-{index}">'
        f"<h2>{html.escape(str(spec.path))} "
        f'<span class="badge badge-{badge}">{spec.state}</span></h2>'
        f"{table}"
        "</section>"
    )


def render_report(
    specs: list[DiffSpec],
    *,
    context: int,
    full: bool,
    ref_a: str,
    ref_b: str,
    attr: str,
) -> str:
    visible = _visible(specs)
    sections = "".join(
        render_diff_section(
            index,
            spec,
            context=context,
            full=full,
            ref_a=ref_a,
            ref_b=ref_b,
        )
        for index, spec in enumerate(visible)
    )
    sidebar = render_sidebar(specs)
    summary = render_summary(specs, ref_a, ref_b, attr)
    title = f"compare-artifacts: {html.escape(ref_a)} ↔ {html.escape(ref_b)}"
    return (
        "<!DOCTYPE html><html><head>"
        '<meta charset="utf-8" />'
        f"<title>{title}</title>"
        f"<style>{STYLES}</style>"
        "</head><body>"
        # The hidden checkbox is the dark-mode state holder. Its `id`
        # matches the `for=` on the visible label inside the sidebar.
        '<input type="checkbox" id="dark-toggle" class="dark-toggle" />'
        f"{sidebar}"
        "<main>"
        f"{summary}"
        f"{sections}"
        "</main>"
        "</body></html>"
    )
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
nix shell nixpkgs#python313 --command python -c \
  "import sys; sys.path.insert(0, '.'); from compare_artifacts.report import render_report; print('ok')"
```

(From inside the package dir.) Expected: `ok`.

- [ ] **Step 3: Smoke-test rendering with synthetic specs**

```bash
nix shell nixpkgs#python313 --command python -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path
from compare_artifacts.collect import DiffSpec
from compare_artifacts.report import render_report
specs = [
    DiffSpec(before=['<svg @0>'], after=['<svg @0>'], path=Path('clearspace/logo.svg'), state='unchanged'),
    DiffSpec(before=['<svg @0>', '  @id: a'], after=['<svg @0>', '  @id: b'], path=Path('clearspace/mark.svg'), state='changed'),
    DiffSpec(before=[], after=['<svg @0>'], path=Path('new/icon.svg'), state='added'),
]
html_out = render_report(specs, context=3, full=False, ref_a='abc', ref_b='def', attr='nixos-branding.all-artifacts')
Path('/tmp/test-report.html').write_text(html_out)
print('wrote /tmp/test-report.html')
"
```

Expected: writes a file. Open it in a browser:

```bash
xdg-open /tmp/test-report.html  # or just inspect with `head -100 /tmp/test-report.html`
```

Verify visually:

- Sidebar has two subdir headers (clearspace, new), correct badges (M
  for `clearspace/mark.svg`, A for `new/icon.svg`).

- Summary shows `1 changed · 1 added · 0 removed · 1 unchanged (hidden)`.

- The `clearspace/logo.svg` (unchanged) is **not** listed in either
  sidebar or body.

- A "Dark mode" button sits inside the sidebar's summary section.
  Click it → page colors flip (dark background, lighter text); button
  text changes to "Light mode". Click again → light theme restored.
  No JavaScript involved.

- [ ] **Step 4: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add HTML report rendering"
```

______________________________________________________________________

### Task 20: `cli.py` — argument parsing and orchestration

This task replaces the stub `main()` from Task 1 with the full
implementation: argparse, signal install, the nested `with Worktree(...)`
block, build+collect+render pipeline, error handling.

**Files:**

- Modify: `<pkg>/compare_artifacts/cli.py`

- [ ] **Step 1: Write `<pkg>/compare_artifacts/cli.py`**

Replace the existing stub with:

```python
"""compare-artifacts CLI entry point.

Wires together worktree creation, parallel nix builds, file collection,
and HTML rendering. Installs SIGTERM/SIGHUP handlers that raise the
`Interrupted` exception so the worktree context managers can react.
"""

import argparse
import signal
import subprocess
import sys
from pathlib import Path

from compare_artifacts.build import build_pair
from compare_artifacts.collect import collect_files
from compare_artifacts.report import render_report
from compare_artifacts.worktree import Interrupted, Worktree


def _raise_interrupted(signum, frame):
    raise Interrupted(signum)


def _non_negative_int(value: str) -> int:
    n = int(value)
    if n < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return n


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compare-artifacts",
        description="Diff nixos-branding artifacts between two git refs.",
    )
    parser.add_argument("ref_a", help="First git ref (branch, tag, or SHA).")
    parser.add_argument("ref_b", help="Second git ref.")
    parser.add_argument(
        "--attr",
        default="nixos-branding.all-artifacts",
        help="Flake attribute to build on each worktree.",
    )
    parser.add_argument(
        "--output",
        default="comparison_report.html",
        type=Path,
        help="Output HTML path (default: ./comparison_report.html).",
    )
    diff_mode = parser.add_mutually_exclusive_group()
    diff_mode.add_argument(
        "--full",
        action="store_true",
        help="Show full file diffs (no context trimming).",
    )
    diff_mode.add_argument(
        "--context",
        type=_non_negative_int,
        default=3,
        help="Lines of unchanged context around changes (default: 3).",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep temp worktrees after the run.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()

    signal.signal(signal.SIGTERM, _raise_interrupted)
    signal.signal(signal.SIGHUP, _raise_interrupted)
    # SIGINT raises KeyboardInterrupt by default.

    try:
        with (
            Worktree(args.ref_a, keep=args.keep) as wt_a,
            Worktree(args.ref_b, keep=args.keep) as wt_b,
        ):
            path_a, path_b = build_pair(wt_a, wt_b, args.attr)
            specs = collect_files(path_a, path_b)
            html_out = render_report(
                specs,
                context=args.context,
                full=args.full,
                ref_a=args.ref_a,
                ref_b=args.ref_b,
                attr=args.attr,
            )
            args.output.write_text(html_out)
    except subprocess.CalledProcessError as e:
        # Distinguish git-worktree-add failure from nix-build failure by
        # the command vector recorded on the exception.
        cmd = e.cmd or []
        if cmd[:3] == ["git", "worktree", "add"]:
            ref = cmd[-1]
            print(
                f"Could not create worktree for {ref}: see git output above",
                file=sys.stderr,
            )
        elif cmd[:2] == ["nix", "build"]:
            # We don't know which ref's build it was; both were attempted.
            print(
                f"nix build of {args.attr} failed. See output above.",
                file=sys.stderr,
            )
        else:
            # Some other subprocess; rethrow with full traceback.
            raise
        return 1
    except (OSError, PermissionError) as e:
        print(f"Could not write report to {args.output}: {e}", file=sys.stderr)
        return 1

    print(f"Report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
nix shell nixpkgs#python313 --command python -c \
  "import sys; sys.path.insert(0, '.'); from compare_artifacts.cli import main; print('ok')"
```

(From inside the package dir.) Expected: `ok`.

- [ ] **Step 3: Smoke-test `--help`**

Rebuild and run:

```bash
nix build .#nixos-branding.verification.compare-artifacts
./result/bin/compare-artifacts --help
```

Expected output: argparse help text listing both positionals and all
options.

- [ ] **Step 4: Smoke-test arg validation**

```bash
./result/bin/compare-artifacts --full --context 5 main main 2>&1 | head -5
```

Expected: exit code 2; argparse error about mutually exclusive
arguments.

```bash
./result/bin/compare-artifacts --context -1 main main 2>&1 | head -5
```

Expected: exit code 2; "must be >= 0" error.

- [ ] **Step 5: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: implement CLI orchestration"
```

______________________________________________________________________

### Task 21: Add a short `README.md`

**Files:**

- Create: `<pkg>/README.md`

- [ ] **Step 1: Write `<pkg>/README.md`**

````markdown
# compare-artifacts

Diff nixos-branding artifacts between two git refs.

## Usage

```bash
nix run .#nixos-branding.verification.compare-artifacts -- \
    <ref-a> <ref-b> [--attr ATTR] [--output PATH] [--full | --context N] [--keep]
````

The tool:

1. Creates two temporary detached-HEAD worktrees, one per ref.
1. Runs `nix build --no-link --print-out-paths .#<attr>` on each
   worktree in parallel (default attr: `nixos-branding.all-artifacts`).
1. Globs `*.svg` from both build outputs, pairs files by relative path,
   classifies each as added / removed / changed / unchanged.
1. Renders an HTML report at `comparison_report.html` (or `--output`)
   with a sticky sidebar grouped by subdirectory and per-file diff
   tables (context-only by default, full diffs with `--full`).

## Examples

```bash
# Compare two branches.
nix run .#nixos-branding.verification.compare-artifacts -- main feature-branch

# Compare just one subset of artifacts.
nix run .#nixos-branding.verification.compare-artifacts -- \
    main feature-branch --attr nixos-branding.artifacts.clearspace

# Show full diffs and keep the temp worktrees afterwards.
nix run .#nixos-branding.verification.compare-artifacts -- \
    main feature-branch --full --keep
```

## Exit codes

- `0` — report generated successfully (regardless of whether diffs were found).
- `1` — runtime failure (invalid ref, nix build failed, IO error).
- `2` — argument error.

## Worktree lifecycle

The tool creates worktrees with `git worktree add --detach`, so the
temporary checkouts never collide with your existing branches. By
default they are removed on success or SIGINT (Ctrl-C from a terminal),
and **kept** on SIGTERM, SIGHUP, or any internal failure so you can
inspect them. The path is printed in either case. Pass `--keep` to
always retain them.

````

- [ ] **Step 2: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add README"
````

______________________________________________________________________

## Phase 5: End-to-end verification

### Task 22: Run the tool against two real refs and inspect the report

This task exercises the orchestration that no unit test covers. It is
verification only — no code or commits.

- [ ] **Step 1: Pick two refs that differ**

Use the current branch and `main`:

```bash
git log --oneline -5
git log --oneline main -5
```

Note both refs.

- [ ] **Step 2: Build the tool**

```bash
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: succeeds, tests pass during the build.

- [ ] **Step 3: Run end-to-end (default attr)**

```bash
./result/bin/compare-artifacts main djacu/svg-multiline --output /tmp/compare.html
```

Expected:

- nix progress output streams to stderr (possibly interleaved between
  the two parallel builds).

- Final line: `Report written to /tmp/compare.html`.

- Exit code: `0` (`echo $?`).

- [ ] **Step 4: Inspect the report**

```bash
xdg-open /tmp/compare.html  # or open in a browser of choice
```

Verify visually:

- Sticky sidebar on the left with subdir groups
  (clearspace, dimensioned, etc.).

- Summary header at top with the changed/added/removed/unchanged counts.

- Each link in the sidebar jumps to the corresponding diff table.

- Unchanged files appear in the summary count but **not** as sidebar
  entries or sections.

- Diff tables show context-only diffs by default.

- [ ] **Step 5: Run with `--full` and confirm full diffs render**

```bash
./result/bin/compare-artifacts main djacu/svg-multiline --output /tmp/compare-full.html --full
```

Verify: the diff tables now show every line of each file (not just
context around changes).

- [ ] **Step 6: Run with `--attr` for a single subset**

```bash
./result/bin/compare-artifacts main djacu/svg-multiline \
    --attr nixos-branding.artifacts.clearspace \
    --output /tmp/compare-clearspace.html
```

Verify: the report only includes clearspace artifacts; the summary
counts reflect that smaller scope.

- [ ] **Step 7: Run with an invalid ref to verify the error path**

```bash
./result/bin/compare-artifacts main no-such-ref-xyz --output /tmp/should-not-exist.html
echo "exit code: $?"
```

Expected:

- One-line error message about the invalid ref.

- Exit code `1`.

- The output file is **not** created.

- The first worktree (for `main`) may still be on disk; the tool prints
  its path. Run `git worktree list` to confirm. Clean it up:
  `git worktree remove --force <path>`.

- [ ] **Step 8: Run with `--keep` and verify worktrees persist**

```bash
./result/bin/compare-artifacts main djacu/svg-multiline --output /tmp/compare.html --keep
git worktree list
```

Verify: two extra worktrees show in the list with detached HEADs.
Clean them up afterwards:

```bash
git worktree list | grep compare-artifacts- | awk '{print $1}' | xargs -n1 git worktree remove --force
```

If any verification fails, fix the issue in the code and re-run.

______________________________________________________________________

## Phase 6: Cleanup

### Task 23: Delete `svg-multiline.py` and stale build symlinks

**Files:**

- Delete: `svg-multiline.py`
- Delete (if present): `result`, `result-bin`, `result-rerounded`,
  `result-rerounded2`, `result-rounded`, `result-unrounded`,
  `comparison_report.html`

The old script is fully replaced by the new package. The build
symlinks at the repo root are leftovers from the old workflow.

- [ ] **Step 1: Delete the script**

```bash
git rm svg-multiline.py
```

- [ ] **Step 2: Remove stale build-output symlinks and the old report (these
  were never tracked but pollute the working directory)**

```bash
rm -f result result-bin result-rerounded result-rerounded2 \
      result-rounded result-unrounded comparison_report.html
```

- [ ] **Step 3: Verify the working tree is clean**

```bash
git status
```

Expected: shows `deleted: svg-multiline.py` staged. No untracked
`result*` files.

- [ ] **Step 4: Commit**

```bash
git commit -m "svg-multiline: remove standalone script (replaced by compare-artifacts)"
```

- [ ] **Step 5: Final verification — full build still works**

```bash
nix build .#nixos-branding.verification.compare-artifacts
./result/bin/compare-artifacts --help
```

Expected: builds, prints help.
