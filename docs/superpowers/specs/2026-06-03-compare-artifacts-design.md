# `compare-artifacts` — Design

## Background

The repository builds branding artifacts (SVGs) via Nix derivations such as
`nixos-branding.all-artifacts`. To audit how artifacts change across branches
or commits, contributors today run `nix build` twice with different out-links
and feed two hardcoded paths into the standalone `svg-multiline.py` script,
which produces a single HTML report comparing the two trees.

This design replaces that script with `compare-artifacts`, a proper Python
package that:

- Accepts two git refs and a nix attribute on the command line.
- Creates two temporary git worktrees (using detached HEADs so it never
  interferes with existing branch checkouts).
- Builds the requested attribute on each worktree in parallel.
- Globs the resulting trees for SVGs, classifies each file as
  added / removed / changed / unchanged, and renders an HTML report with
  a sticky sidebar index, summary counts, and per-file diff tables.
- Cleans up its worktrees afterward (with debug-friendly fallbacks).
- Is invokable both locally and from CI via `nix run`.

## Goals and non-goals

**Goals**

- Single command takes two refs and produces a self-contained HTML report.
- Default attribute is `nixos-branding.all-artifacts`, overridable via
  `--attr`, so any other artifact collection (e.g.
  `nixos-branding.artifacts.clearspace`) can be compared.
- Two `nix build` invocations run concurrently to minimize wall-clock time.
- Worktrees never collide with the user's existing checkouts or branches.
- Report has navigation (sticky sidebar grouped by subdirectory), summary
  stats at the top, color-coded state badges, and only shows files that
  changed/added/removed (unchanged files are filtered).
- Diff display defaults to context-only (3 surrounding lines); a `--full`
  flag shows the entire file diff.
- Internal failures and signal-driven exits (SIGTERM / SIGHUP) keep the
  worktrees on disk for debugging. Clean success and SIGINT (Ctrl-C
  from a terminal, which signals the whole process group and lets nix
  die naturally) respect `--keep`.
- SVG-parsing logic is unit-tested under `nix build` via `pytestCheckHook`.

**Non-goals**

- No interactive (JS) controls in the generated HTML; CLI flags decide
  what the report contains.
- No support for comparing the working tree against a ref. Both inputs are
  refs that git can resolve.
- No support for non-SVG artifacts (PDFs, PNGs, fonts, etc.). The branding
  artifacts are currently SVG-only and the tool name and globbing reflect
  that.
- No automatic browser open after generation; the tool prints the output
  path and exits.
- No allowlist / "expected diff" mechanism. The exit code does not
  distinguish "diff found" from "no diff."

## Package placement and CLI

### Filesystem layout

```
package-sets/top-level/nixos-branding/verification/compare-artifacts/
├── package.nix              # python3Packages.buildPythonApplication (see Nix package details)
├── pyproject.toml           # project metadata; console_scripts entry point
├── README.md                # short usage doc
├── compare_artifacts/       # importable Python package
│   ├── __init__.py
│   ├── __main__.py          # enables `python -m compare_artifacts`
│   ├── cli.py
│   ├── worktree.py
│   ├── build.py
│   ├── collect.py
│   ├── parse.py
│   └── report.py
└── tests/
    ├── __init__.py
    ├── test_parse.py
    ├── test_collect.py
    └── fixtures/            # tiny hand-crafted SVGs
```

Surfaces in the Nix package set as
`nixos-branding.verification.compare-artifacts`. Invoked as
`nix run .#nixos-branding.verification.compare-artifacts -- <args>`.
`packagesFromDirectoryRecursive` in `overlays/default.nix:43-49`
discovers the directory automatically — no extra wiring needed.

### Nix package details

`package-sets/top-level/` is called from the top-level `pkgs` scope, so
`package.nix` must request `python3Packages` (and `lib`, `git`, `nix`)
as inputs and call `python3Packages.buildPythonApplication` —
`buildPythonApplication` is not in scope at the top level. (Compare
with `nixoslogo/package.nix`, which takes `buildPythonPackage` directly
because it sits in `package-sets/python-packages/` where the python
overlay puts the python build helpers in scope.)

Shape of `package.nix`:

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

  # Ensure `git` and `nix` are on PATH at runtime — the tool shells
  # out to both. Without this wrapper, the tool only works if the
  # user happens to have them on their own PATH.
  makeWrapperArgs = [
    "--prefix" "PATH" ":" (lib.makeBinPath [ git nix ])
  ];
}
```

`pyproject.toml` matches the repo's convention (`poetry-core` build
backend, matching `nixoslogo`), declares the package version, and
exposes the CLI via `[project.scripts]`:

```toml
[project]
name = "compare-artifacts"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
compare-artifacts = "compare_artifacts.cli:main"

[tool.poetry]
packages = [{ include = "compare_artifacts" }]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

Notes:

- `pytestCheckHook` auto-discovers `tests/` at the source root.
  Fixtures under `tests/fixtures/` are picked up because pytest follows
  conftest/rootdir conventions without extra config.
- `buildPythonApplication` (vs `buildPythonPackage`) is the right choice
  for a CLI: it strips Python-version cross-deps from the closure and
  doesn't surface in `python3Packages`. The CLI ends up as a regular
  derivation with `bin/compare-artifacts`.
- The tool cannot be exercised inside the `pytestCheckHook` sandbox
  (no nix daemon, no git history). Only the pure parsing / collection
  modules run under tests; the worktree and build modules are exercised
  at runtime via `nix run`. This matches the testing strategy in the
  "Testing" section.

### CLI surface

```
compare-artifacts <ref-a> <ref-b> [--attr ATTR]
                                  [--output PATH]
                                  [--full | --context N]
                                  [--keep]

Positional:
  ref-a                  First git ref (branch, tag, or SHA).
  ref-b                  Second git ref.

Options:
  --attr ATTR            Flake attribute to build on each worktree.
                         Default: nixos-branding.all-artifacts
  --output PATH          Output HTML path.
                         Default: ./comparison_report.html
  --full                 Show full file diffs (no context trimming).
                         Mutually exclusive with --context.
  --context N            Lines of unchanged context around changes.
                         Default: 3. Must be >= 0.
  --keep                 Keep temp worktrees after the run.
  -h, --help             Show help.

Exit codes:
  0   Report generated successfully (regardless of whether diffs were found).
  1   Runtime failure (invalid ref, nix build failed, IO error, etc.).
  2   Argument error (argparse).
```

`--full` and `--context N` are enforced as mutually exclusive via
`add_mutually_exclusive_group`. The `--attr` value is passed unmodified to
`nix build .#<attr>`; anything `nix build` accepts is valid.

## Architecture

### Module responsibilities

- **`cli.py`** — `main()`. Parses args, installs signal handlers, opens two
  `Worktree` context managers, calls `build_pair` for parallel builds,
  passes the resulting paths to `collect_files`, hands the specs to
  `render_report`, writes the output, prints the path. Catches expected
  failures (see Error handling) and maps them to user-facing messages and
  exit code 1.

- **`worktree.py`** — `Worktree(ref, *, keep=False)` context manager.
  `__enter__` runs `tempfile.mkdtemp(prefix="compare-artifacts-")`, then
  `git worktree add --detach <tmp> <ref>`. If `git worktree add` raises,
  `__enter__` removes the tmp dir via `shutil.rmtree(tmp, ignore_errors=True)`
  before re-raising (otherwise the empty tmp dir leaks). On success it
  yields `Path(tmp)`. `__exit__` decides whether to remove the worktree
  based on the exit cause (see Lifecycle below) and always returns
  `False` so the original exception (if any) propagates. If
  `git worktree remove --force` itself raises during cleanup, `__exit__`
  catches the error, prints the kept path, and continues — a cleanup
  failure never replaces the original exception. Also defines the
  `Interrupted(BaseException)` exception used by SIGTERM / SIGHUP
  handlers (inherits from `BaseException` so it survives `except Exception`
  in worker threads).

- **`build.py`** — `build_attr(worktree_path: Path, attr: str) -> Path`
  runs `nix build --no-link --print-out-paths .#<attr>` in the worktree
  via `subprocess.run(..., cwd=worktree_path, stdout=subprocess.PIPE, text=True, check=True)`. **stdout is piped** so we can capture the
  printed store path; **stderr is inherited** so nix's progress output
  streams to the user's terminal. Returns the captured path as
  `Path(result.stdout.strip())`. `build_pair(wt_a, wt_b, attr) -> tuple[Path, Path]` runs two `build_attr` calls concurrently via
  `concurrent.futures.ThreadPoolExecutor(max_workers=2)`.

- **`collect.py`** — owns the `DiffSpec` dataclass:

  ```python
  @dataclass
  class DiffSpec:
      before: list[str]
      after: list[str]
      path: Path  # relative to the build output root
      state: Literal["added", "removed", "changed", "unchanged"]
  ```

  Also owns the small filesystem→parse bridge
  `path_to_parsed(root: Path, rel: Path) -> list[str]` (reads the SVG
  text and calls `parse.parse_node` on its root element). This is the
  single I/O boundary into parsing, kept in `collect.py` so `parse.py`
  stays pure. `collect_files(before_root: Path, after_root: Path) -> list[DiffSpec]` globs `*.svg` recursively under each root (following
  symlinks), builds the sorted union of relative paths, and produces
  one `DiffSpec` per path classified as `added`, `removed`, `changed`,
  or `unchanged`. Returns all specs including `unchanged` so the
  renderer can count them for the summary; the renderer filters them
  out of sidebar and body.

- **`parse.py`** — pure functions only. Migrates the existing parsers
  (`parse_node`, `parse_attributes`, `parse_d`, `parse_points`,
  `parse_transform`, `parse_viewbox`, `parse_misc`, `no_name_space`,
  `pad_min`, `split_transforms`) and the `INDENT*` constants. No I/O,
  no globals beyond constants. The filesystem-touching `path_to_parsed`
  helper lives in `collect.py`, not here.

- **`report.py`** — `render_report(specs, *, context: int, full: bool, ref_a: str, ref_b: str, attr: str) -> str`. Helpers: `render_summary`,
  `render_sidebar`, `render_diff_section`, plus a module-level `STYLES`
  string with the embedded CSS. Uses `difflib.HtmlDiff().make_table(...)`
  for the actual diff tables. The `fromdesc` / `todesc` arguments use
  the ref names: `f"{spec.path} ({ref_a})"` and `f"{spec.path} ({ref_b})"`
  so each table is self-describing.

### Orchestration

The body of `cli.main()`:

```python
signal.signal(signal.SIGTERM, _raise_interrupted)
signal.signal(signal.SIGHUP,  _raise_interrupted)
# SIGINT raises KeyboardInterrupt by default.

with Worktree(ref_a, keep=keep) as wt_a, Worktree(ref_b, keep=keep) as wt_b:
    path_a, path_b = build_pair(wt_a, wt_b, attr)
    specs = collect_files(path_a, path_b)
    html = render_report(
        specs,
        context=context,
        full=full,
        ref_a=ref_a,
        ref_b=ref_b,
        attr=attr,
    )
    Path(output).write_text(html)

print(f"Report written to {output}")
```

### Data flow

1. **Parse args.** argparse validates `--context N >= 0` and the
   `--full` / `--context` mutual exclusion before any side effects.
1. **Install signal handlers** for SIGTERM and SIGHUP that raise the
   custom `Interrupted(BaseException)` exception.
1. **Open two worktrees sequentially** (just git plumbing — fast).
   Each runs `git worktree add --detach <tmp> <ref>`. The `--detach`
   flag means git checks out the commit `<ref>` resolves to without
   reserving any branch name, so the temp worktrees cannot collide
   with the user's existing branch checkouts (including `main`).
1. **Run two `nix build` calls in parallel** via
   `ThreadPoolExecutor(max_workers=2)`. Each `nix build` runs with
   `cwd=<worktree>` and uses `--no-link --print-out-paths` to print
   the store path on stdout. **stdout is piped** (so the store path
   can be captured); **stderr is inherited** (so nix's progress
   output streams to the user's terminal). Two concurrent builds
   means stderr from both will interleave on the user's terminal —
   functional, just visually messy if nix is drawing a progress bar.
1. **`collect_files(path_a, path_b)`** rglobs `*.svg` under each root,
   builds two `set[Path]` of relative paths, iterates the sorted union:
   - Both sides present → parse both; if equal, state is `unchanged`,
     else `changed`.
   - Only in `path_a` → `removed`; parsed before, empty after.
   - Only in `path_b` → `added`; empty before, parsed after.
1. **`render_report`** computes counts from the full spec list, then
   filters out `unchanged` for both sidebar and body. Renders one
   `<section>` per remaining spec, each containing an `<h2>` and the
   `difflib.HtmlDiff().make_table(...)` output (with
   `context=not full` and `numlines=context`).
1. **Write the HTML** to `--output` and print the path.
1. **`Worktree.__exit__`** for each worktree (in LIFO order) decides
   whether to remove based on the exit cause (see Lifecycle).

### Worktree lifecycle

Worktrees use detached HEAD specifically so they cannot interfere with
the user's branch checkouts. No temporary branches are created and no
branch cleanup is needed.

Exit-time decision matrix:

| Exit cause | Worktree action |
|---------------------------------------|----------------------------------------|
| Success | Remove (unless `--keep`) |
| `KeyboardInterrupt` (SIGINT / Ctrl-C from terminal) | Remove (unless `--keep`) |
| `Interrupted` (SIGTERM / SIGHUP) | **Keep regardless of `--keep`** |
| Any other exception | **Keep regardless of `--keep`** |

Rationale:

- **Success** and **SIGINT** are the "normal" exit paths. SIGINT from a
  terminal goes to the whole process group, so `nix build` dies
  naturally and the worker thread sees a `CalledProcessError` shortly
  after the main thread raises `KeyboardInterrupt`. Cleanup can safely
  remove the worktree because nothing is still writing to it.
- **SIGTERM / SIGHUP** keep the worktrees. The reason is concurrency:
  Python only delivers signals to the main thread, but the `nix build`
  subprocesses are blocked-on inside worker threads. When the main
  thread's signal handler raises `Interrupted` and we exit the `with`
  block, the worker threads (and the nix processes they're waiting on)
  may still be running. Removing the worktree at that point races with
  active writes from nix. Safer to keep, print the path, and let the
  user clean up once nix has finished or been killed manually.
- **Other exceptions** (build errors, parser crashes, IO errors) keep
  the worktrees so contributors can `cd` in and reproduce.

The kept paths are always printed on stdout. Removal uses
`git worktree remove --force <path>` so a half-finished build with a
busy file doesn't block cleanup. If the `--force` removal itself fails,
`__exit__` catches the error, prints the kept path, and continues — a
cleanup hiccup never masks the original exit cause.

The race where SIGINT kills the child `nix build` process and the
resulting `CalledProcessError` reaches `__exit__` before our
`KeyboardInterrupt` propagates is deliberately not handled. In that
case the worktrees are kept (an "other exception" branch), and the
user runs `git worktree remove` once. Adding race-handling
infrastructure (process-group tracking, Popen registry, signal
forwarding) is not worth the complexity for this edge case.

### HTML report structure

Layout:

```
┌────────────────────────────┬──────────────────────────────────────────────┐
│ Sticky sidebar (~280px)    │ Main content                                 │
│                            │                                              │
│ Summary stats              │ Summary header                               │
│ ────────────               │ X changed · Y added · Z removed              │
│ X changed                  │ U unchanged (hidden)                         │
│ Y added                    │ ref-a: <sha>   ref-b: <sha>                  │
│ Z removed                  │ attr: nixos-branding.all-artifacts           │
│ U unchanged                │                                              │
│                            │ <section> per non-unchanged file:            │
│ clearspace (2)             │   <h2>relative/path.svg [state]</h2>         │
│  M logo.svg                │   <difflib.HtmlDiff table>                   │
│  M logomark.svg            │                                              │
│                            │                                              │
│ dimensioned (3)            │                                              │
│  M lambda-angular.svg      │                                              │
│  A lambda-new.svg          │                                              │
│  M logo-dim.svg            │                                              │
└────────────────────────────┴──────────────────────────────────────────────┘
```

HTML skeleton (simplified):

```html
<html>
  <head>
    <meta charset="utf-8" />
    <title>compare-artifacts: <ref-a> ↔ <ref-b></title>
    <style>/* embedded CSS: flex layout, sidebar position: sticky,
              difflib styles, badge colors */</style>
  </head>
  <body>
    <aside class="sidebar">
      <section class="sidebar-summary">
        X changed · Y added · Z removed · U unchanged
      </section>
      <nav>
        <h3>clearspace <span class="count">(2)</span></h3>
        <ul>
          <li><a href="#diff-0">
              <span class="badge badge-M">M</span> logo.svg</a></li>
          ...
        </ul>
        <h3>dimensioned <span class="count">(3)</span></h3>
        <ul>...</ul>
      </nav>
    </aside>
    <main>
      <header class="summary">
        <p><strong>X changed</strong> · Y added · Z removed ·
           U unchanged (hidden)</p>
        <p>ref-a: <code>...</code>   ref-b: <code>...</code></p>
        <p>attr: <code>...</code></p>
      </header>
      <section id="diff-0">
        <h2>clearspace/logo.svg <span class="badge badge-M">changed</span></h2>
        <!-- difflib.HtmlDiff().make_table(...) output -->
      </section>
      ...
    </main>
  </body>
</html>
```

Conventions:

- **Sidebar groups** are subdirectory names from the relative paths.
  Subdirs with zero changed/added/removed entries do not appear.
- **Per-subdir counts** show non-unchanged entries only (matches what
  is actually listed under each).
- **Badges** mirror git status short codes: `A` (green) for added,
  `M` (yellow) for changed, `D` (red) for removed.
- **Section IDs** use the file's position in the rendered list:
  `diff-0`, `diff-1`, ..., `diff-N`. This trivially avoids any
  slugification edge cases (path collisions like `a/b.svg` vs `a-b.svg`,
  characters that need URL-encoding, case sensitivity). The human
  identifier — the relative path — is visible in the sidebar link text
  and in the section's `<h2>`.
- **CSS** is embedded in `<style>` (no external assets). Sidebar
  uses `position: sticky; top: 0; height: 100vh; overflow-y: auto;`.
- **Summary header** appears in both the sidebar (compact) and the
  top of the main area (with ref / attr metadata).

## Testing

Unit tests run during `nix build` via `pytestCheckHook`.

**Tested (hermetic, no git/nix dependency):**

- `parse.py` — one test class per parser:

  - `parse_d` — empty value, single command, multi-command, whitespace
    handling, index-padding boundaries (1, 9, 10, 99, 100).
  - `parse_points` — empty, single pair, multi-pair, padding boundaries.
  - `parse_transform` — single transform, chained transforms, whitespace
    inside parens.
  - `parse_viewbox` — four-value strings, padding behavior.
  - `parse_misc` — round-trip name/value as `@name: value`.
  - `parse_node` — minimal element, nested children with `depth` tags
    disambiguating duplicate sibling tags, namespaced tag stripping.
  - `pad_min` — empty sequence (regression test for the zero-length
    fix already in `svg-multiline.py`), short sequences, large sequences.
  - `no_name_space` — bare tag and namespaced tag.

- `collect.py` — `collect_files` against fixture trees built in
  `tmp_path`:

  - empty/empty → empty list
  - same file, same content → `unchanged`
  - same file, different content → `changed`
  - file only in `before` → `removed`
  - file only in `after` → `added`
  - returned list is sorted by path

**Not unit-tested** (covered by manual / integration use):

- `worktree.py` — requires a real git repo.
- `build.py` — requires nix; slow.
- `cli.py` — glue layer.
- `report.py` — HTML golden-file tests are brittle and noisy. Visual
  inspection serves the same purpose.

Fixtures under `tests/fixtures/` are small hand-crafted SVGs covering
the parser dimensions above. Tests use `pathlib` and pytest's
`tmp_path` for directory-tree construction rather than checking real
build outputs into the test data.

## Error handling

`cli.main()` wraps the orchestration in a top-level try/except. Three
expected failure modes produce a one-line user-facing message and exit
code 1:

- `CalledProcessError` from `git worktree add` — almost always "unknown
  ref" or "ref not fetched." Message:
  `Could not create worktree for <ref>: <git stderr last line>`.
- `CalledProcessError` from `nix build` — message:
  `nix build of <attr> failed on <ref>. See output above.` (nix output
  is on the terminal because the subprocess inherits stdio.)
- `OSError` / `PermissionError` writing the output file — message:
  `Could not write report to <output>: <reason>`.

Anything else (programming bugs, parser crashes on malformed SVG, etc.)
propagates with full traceback. Internal failures keep the worktrees
on disk per the lifecycle decision matrix.

### Argument validation

- `--context N` requires `N >= 0` (argparse `type=int` plus a custom
  validator).
- `--full` and `--context N` are mutually exclusive.
- Ref positionals are not validated up front; git is the source of
  truth. `compare-artifacts main main` runs and produces an empty
  diff report.

### Edge cases

- **Two refs that resolve to the same commit** — works; produces an
  empty diff.
- **Ambiguous SHA prefix** — git fails on `worktree add`, surfaced via
  the `CalledProcessError` handler.
- **`nix build` succeeds but produces no SVGs** — `collect_files`
  returns an empty list; the report renders with all-zero counts and an
  empty sidebar/body. User can tell from the report.
- **Deep symlink trees in build output** — `rglob` with
  `recurse_symlinks=True` (already in the current script) handles them.
- **Malformed SVG** — `xml.etree.ElementTree.ParseError` propagates
  with traceback; worktrees kept.

## Migration

The existing `svg-multiline.py` at the repo root is removed once
`compare-artifacts` lands. Two bugs in the current script that are
fixed during the rewrite:

- `collect_files` assigns `state = "remove"` for files only in the
  before tree; the `DiffSpec.state` literal is `"removed"`.
- The `added` case calls `path_to_parsed(before_root, path)` instead
  of `path_to_parsed(after_root, path)`, so newly-added files are
  parsed from the wrong tree (and would fail to read if not also
  present in `before_root`).
