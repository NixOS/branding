# compare-artifacts: show unchanged, rename states, fix badge CSS — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Three coupled changes to `compare-artifacts`: (1) flip the default
to show unchanged files (with `--hide-unchanged` to opt out), (2) rename two
of the four state strings so the badge letter matches the word's first
letter (`changed → modified`, `removed → deleted`), (3) fix the `.badge`
CSS so multi-character text doesn't overflow the colored background.
Also: per-subdir "(M of N)" count format, summary anchor links, version
bump, and `--full` help-text warning.

**Architecture:** All work lands on the current `compare-artifacts-ci-integration`
branch and merges to `main` in one PR with the existing tool implementation
and CI integration work. The state rename and the CI workflow's `jq` update
must land in the same commit (intermediate-commit-broken-CI requirement).
Other changes can ship in separate commits.

**Tech Stack:** Python 3.13 stdlib only (no new deps), embedded CSS in
Python string, GitHub Actions workflow YAML. Tests via pytest's existing
suite; no new tests.

**Spec:** `docs/superpowers/specs/2026-06-04-compare-artifacts-show-unchanged-design.md`.

______________________________________________________________________

## Working directory and conventions

All paths in this plan are relative to the repo root
`/home/djacu/dev/nixos/branding/`.

**Branch:** Already on `compare-artifacts-ci-integration`. Verify with
`git branch --show-current` before starting; if not, `git checkout compare-artifacts-ci-integration` first. No new branch is created in
this plan.

**Commit convention:** Match existing repo style — `<scope>: <imperative>`.
Use `compare-artifacts:` for Python changes, `ci:` for workflow changes,
`docs:` for spec amendments.

**No `Co-Authored-By` trailer** on any commit. Per repo saved preference.

**Pre-commit hook (`treefmt`)** runs on every commit. Python is formatted
by `ruff`; YAML/TOML are untouched; markdown by `mdformat`. If treefmt
reformats a file, re-stage and re-commit (do NOT amend).

**GPG signing** is enabled. If `git commit` fails with a GPG timeout,
STOP and ask the user to unlock the key. Do NOT bypass signing with
`-c commit.gpgsign=false`.

## File map

| Path | Action | Tasks |
|---|---|---|
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/collect.py` | modify | 2 |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py` | modify | 2, 3 |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py` | modify | 1, 2, 3, 4, 5 |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/test_collect.py` | modify | 2 |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/pyproject.toml` | modify | 7 |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md` | modify | 8 |
| `.github/workflows/check.yml` | modify | 2, 6 |
| `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md` | modify | 9 |
| `docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md` | modify | 10 |

______________________________________________________________________

## Task 1: Badge CSS sizing fix + U badge color rule

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py`

### Step 1: Locate the `.badge` rule in the STYLES constant

```bash
grep -n "^\.badge {" /home/djacu/dev/nixos/branding/package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py
```

Expected: one match, near line 68 of `report.py`. The next few lines
show:

```css
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
```

- [ ] **Step 2: Replace the `.badge` rule with the content-aware version**

In `report.py`, change `width: 1.2em;` to two new lines `min-width: 1.2em;` and
`padding: 0 0.4em;`. The block becomes:

```css
.badge {
    display: inline-block;
    min-width: 1.2em;
    padding: 0 0.4em;
    text-align: center;
    font-weight: 700;
    border-radius: 3px;
    margin-right: 0.4em;
    font-size: 0.85em;
    color: white;
}
```

- [ ] **Step 3: Add the `.badge-U` rule immediately after `.badge-D`**

The result:

```css
.badge-A { background: #28a745; }
.badge-M { background: #f0a500; }
.badge-D { background: #d73a49; }
.badge-U { background: #666; }
```

- [ ] **Step 4: Verify Nix build still passes**

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes; tests run.

- [ ] **Step 5: Smoke-test the badge appearance**

The U badge isn't used by the rendered HTML until Task 3. For now,
just confirm A/M/D still render correctly. Render a synthetic report:

```bash
cd /home/djacu/dev/nixos/branding/package-sets/top-level/nixos-branding/verification/compare-artifacts
nix shell nixpkgs#python313 --command python -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path
from compare_artifacts.collect import DiffSpec
from compare_artifacts.report import render_report
specs = [
    DiffSpec(before=['<svg>'], after=['<svg>'], path=Path('a.svg'), state='unchanged'),
    DiffSpec(before=['<svg id=\"x\">'], after=['<svg id=\"y\">'], path=Path('b.svg'), state='changed'),
    DiffSpec(before=[], after=['<svg>'], path=Path('c.svg'), state='added'),
    DiffSpec(before=['<svg>'], after=[], path=Path('d.svg'), state='removed'),
]
Path('/tmp/badge-test.html').write_text(render_report(specs, context=3, full=False, ref_a='a', ref_b='b', attr='x'))
print('wrote /tmp/badge-test.html')
"
```

Note: this uses the OLD state names (`changed`, `removed`) because
Task 2 hasn't renamed yet. The point is to confirm the badge sizing
works for the multi-word headers.

Open `/tmp/badge-test.html` in a browser. Expected:

- Sidebar shows single-letter badges (M, A, D) with a slightly wider
  colored pill (padding around the letter).

- Each `<h2>` shows the full state word INSIDE the colored badge box
  (e.g., "changed" fully visible on yellow background, "added" on
  green, "removed" on red). Words no longer overflow into the page
  background.

- [ ] **Step 6: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py
git commit -m "compare-artifacts: fix badge CSS overflow; add U badge color"
```

______________________________________________________________________

## Task 2: State rename + CI workflow `jq` update (ATOMIC)

This task is the largest single commit in the plan. The rename of
state strings cascades through `collect.py`, `report.py`, `cli.py`,
the tests, and the CI workflow's `jq` queries. **All of these must
land in the same commit** — otherwise intermediate commits emit new
JSON keys but the CI workflow queries old keys, breaking CI on
those SHAs.

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/collect.py`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/test_collect.py`
- Modify: `.github/workflows/check.yml`

### Step 1: Update `compare_artifacts/collect.py`

Locate `DiffSpec` (around line 22). Change the `state` Literal:

```python
# Before
@dataclass
class DiffSpec:
    before: list[str]
    after: list[str]
    path: Path  # relative to the build output root
    state: Literal["added", "removed", "changed", "unchanged"]
```

```python
# After
@dataclass
class DiffSpec:
    before: list[str]
    after: list[str]
    path: Path  # relative to the build output root
    state: Literal["added", "deleted", "modified", "unchanged"]
```

In `collect_files` (around line 54 onwards), update the two state
assignments:

```python
# Find this case:
            case (True, True):
                before = path_to_parsed(before_root, path)
                after = path_to_parsed(after_root, path)
                state = "unchanged" if before == after else "changed"
            case (True, False):
                before = path_to_parsed(before_root, path)
                after = []
                state = "removed"
```

Change to:

```python
            case (True, True):
                before = path_to_parsed(before_root, path)
                after = path_to_parsed(after_root, path)
                state = "unchanged" if before == after else "modified"
            case (True, False):
                before = path_to_parsed(before_root, path)
                after = []
                state = "deleted"
```

(The `case (False, True)` branch already uses `state = "added"`; leave
it unchanged.)

Locate `counts()` (around line 77). Update the docstring and dict:

```python
# Before
def counts(specs: list[DiffSpec]) -> dict[str, int]:
    """Return the count of specs in each of the four states.

    Always returns a dict with exactly four keys (`changed`, `added`,
    `removed`, `unchanged`) with integer values. Used by `report.py`
    for the on-page summary and by `cli.py`'s `--summary` flag for the
    JSON sidecar that CI consumes.
    """
    result = {"changed": 0, "added": 0, "removed": 0, "unchanged": 0}
    for spec in specs:
        result[spec.state] += 1
    return result
```

```python
# After
def counts(specs: list[DiffSpec]) -> dict[str, int]:
    """Return the count of specs in each of the four states.

    Always returns a dict with exactly four keys (`modified`, `added`,
    `deleted`, `unchanged`) with integer values. Used by `report.py`
    for the on-page summary and by `cli.py`'s `--summary` flag for the
    JSON sidecar that CI consumes.
    """
    result = {"modified": 0, "added": 0, "deleted": 0, "unchanged": 0}
    for spec in specs:
        result[spec.state] += 1
    return result
```

### Step 2: Update `compare_artifacts/report.py`

Locate `_STATE_TO_BADGE` (around line 187). Update:

```python
# Before
_STATE_TO_BADGE = {
    "added": "A",
    "changed": "M",
    "removed": "D",
}
```

```python
# After
_STATE_TO_BADGE = {
    "added": "A",
    "modified": "M",
    "deleted": "D",
    "unchanged": "U",
}
```

(Added "unchanged": "U" too — required for Task 3's render_diff_section
to pick up the U badge.)

Locate `render_summary` (around line 196). Update the f-string to use
new dict keys and display words:

```python
# Before
def render_summary(specs: list[DiffSpec], ref_a: str, ref_b: str, attr: str) -> str:
    counts_ = counts(specs)
    return (
        '<header class="summary">'
        f"<p><strong>{counts_['changed']} changed</strong> · "
        f"{counts_['added']} added · "
        f"{counts_['removed']} removed · "
        f"{counts_['unchanged']} unchanged (hidden)</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )
```

```python
# After
def render_summary(specs: list[DiffSpec], ref_a: str, ref_b: str, attr: str) -> str:
    counts_ = counts(specs)
    return (
        '<header class="summary">'
        f"<p><strong>{counts_['modified']} modified</strong> · "
        f"{counts_['added']} added · "
        f"{counts_['deleted']} deleted · "
        f"{counts_['unchanged']} unchanged (hidden)</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )
```

(The `(hidden)` becomes conditional in Task 3; leave it hardcoded here
for now since unchanged is still being hidden by default until Task 3.)

Locate `render_sidebar` (around line 226). Find the sidebar summary
text and update the keys + words:

```python
# Before (inside render_sidebar, look for the sidebar-summary section)
    out = ['<aside class="sidebar">']
    out.append(
        '<section class="sidebar-summary">'
        f"{counts_['changed']} changed · "
        f"{counts_['added']} added · "
        f"{counts_['removed']} removed · "
        f"{counts_['unchanged']} unchanged"
        '<br /><label for="dark-toggle" class="dark-button"></label>'
        "</section>"
    )
```

```python
# After
    out = ['<aside class="sidebar">']
    out.append(
        '<section class="sidebar-summary">'
        f"{counts_['modified']} modified · "
        f"{counts_['added']} added · "
        f"{counts_['deleted']} deleted · "
        f"{counts_['unchanged']} unchanged"
        '<br /><label for="dark-toggle" class="dark-button"></label>'
        "</section>"
    )
```

Locate the module docstring at the top of `report.py` (lines 1–13).
Find the line "color-coded state badges (A/M/D)" and update to
"color-coded state badges (A/M/D/U)".

### Step 3: Update `compare_artifacts/cli.py`

Locate the `--summary` argparse argument (around line 50–57). Update
its help text:

```python
# Before
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="If set, write a JSON file at this path with the counts "
             "(changed/added/removed/unchanged). The HTML output is "
             "unchanged whether or not this flag is passed.",
    )
```

```python
# After
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="If set, write a JSON file at this path with the counts "
             "(modified/added/deleted/unchanged). The HTML output is "
             "unchanged whether or not this flag is passed.",
    )
```

### Step 4: Update `tests/test_collect.py`

The file has several assertions that reference the old state strings.
Find each and update.

Locate `test_changed` (around line 43):

```python
# Before
    def test_changed(self, tmp_path):
        ...
        assert specs[0].state == "changed"
```

```python
# After
    def test_changed(self, tmp_path):
        ...
        assert specs[0].state == "modified"
```

(Keep the test method name `test_changed` — the test name describes
behavior, not state. Optionally rename to `test_modified` for
consistency. RECOMMENDATION: leave names as-is to keep the diff small.)

Locate `test_removed` (around line 66):

```python
# Before
        # Regression: the original code wrote "remove" here.
        assert specs[0].state == "removed"
```

```python
# After
        # Regression: the original code wrote "remove" here.
        assert specs[0].state == "deleted"
```

Locate `test_subdirectory_paths_preserved` (around line 90):

```python
# Before
        assert specs[0].state == "changed"
```

```python
# After
        assert specs[0].state == "modified"
```

Locate `test_empty_list` (around line 104):

```python
# Before
    def test_empty_list(self):
        # All four keys must be present even when empty.
        assert counts([]) == {
            "changed": 0,
            "added": 0,
            "removed": 0,
            "unchanged": 0,
        }
```

```python
# After
    def test_empty_list(self):
        # All four keys must be present even when empty.
        assert counts([]) == {
            "modified": 0,
            "added": 0,
            "deleted": 0,
            "unchanged": 0,
        }
```

Locate `test_one_of_each` (around line 126):

```python
# Before
        assert counts(specs) == {
            "changed": 1,
            "added": 1,
            "removed": 1,
            "unchanged": 1,
        }
```

```python
# After
        assert counts(specs) == {
            "modified": 1,
            "added": 1,
            "deleted": 1,
            "unchanged": 1,
        }
```

Locate `test_all_keys_always_present` (around line 136):

```python
# Before
    def test_all_keys_always_present(self):
        # Even if some states have zero entries, all four keys exist.
        result = counts([])
        assert set(result.keys()) == {"changed", "added", "removed", "unchanged"}
```

```python
# After
    def test_all_keys_always_present(self):
        # Even if some states have zero entries, all four keys exist.
        result = counts([])
        assert set(result.keys()) == {"modified", "added", "deleted", "unchanged"}
```

### Step 5: Update `.github/workflows/check.yml`

Locate the `compare-artifacts-comment` job's `Validate and extract summary` step. The current `jq` commands reference the old keys:

```yaml
# Before
          jq -e 'all(.changed, .added, .removed, .unchanged; type == "number")' \
             comparison_summary.json > /dev/null
          SUMMARY=$(jq -r '"\(.changed) changed · \(.added) added · \(.removed) removed · \(.unchanged) unchanged"' \
                    comparison_summary.json)
```

Replace with:

```yaml
# After
          jq -e 'all(.modified, .added, .deleted, .unchanged; type == "number")' \
             comparison_summary.json > /dev/null
          SUMMARY=$(jq -r '"\(.modified) modified · \(.added) added · \(.deleted) deleted · \(.unchanged) unchanged"' \
                    comparison_summary.json)
```

### Step 6: Run pytest to confirm all tests pass

```bash
cd /home/djacu/dev/nixos/branding/package-sets/top-level/nixos-branding/verification/compare-artifacts
nix shell nixpkgs#python313Packages.pytest --command pytest tests/ -v
```

Expected: all tests pass (44 from parse + 12 from collect = 56 items).

### Step 7: Run the full Nix build

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes; tests run in the sandbox.

### Step 8: Smoke-test the renamed output

```bash
./result/bin/compare-artifacts main main \
    --output /tmp/rename-test.html \
    --summary /tmp/rename-test.json
cat /tmp/rename-test.json
```

Expected output (96 artifacts identical on main vs main):

```
{"modified": 0, "added": 0, "deleted": 0, "unchanged": 96}
```

(Note the new key names.)

### Step 9: Verify YAML parses

```bash
nix shell nixpkgs#yamllint --command yamllint .github/workflows/check.yml
```

Expected: only pre-existing style warnings; no parse errors.

- [ ] **Step 10: Commit (ATOMIC)**

```bash
git add \
    package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/collect.py \
    package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py \
    package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py \
    package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/test_collect.py \
    .github/workflows/check.yml
git commit -m "compare-artifacts: rename states (changed→modified, removed→deleted)"
```

(Single atomic commit covering all 5 files. If this commit is split
into multiple commits, intermediate CIs break.)

______________________________________________________________________

## Task 3: `--hide-unchanged` flag + `--full` help warning

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py`

### Step 1: Add `--hide-unchanged` and update `--full` help in `cli.py`

Locate `_build_parser()` in `cli.py`. Find the `--full` argument:

```python
# Before
    diff_mode.add_argument(
        "--full",
        action="store_true",
        help="Show full file diffs (no context trimming).",
    )
```

```python
# After
    diff_mode.add_argument(
        "--full",
        action="store_true",
        help="Show full file diffs (no context trimming). WARNING: "
             "combined with the show-all default (no --hide-unchanged), "
             "the rendered HTML can grow to many MB for repos with "
             "hundreds of large artifacts. Local dev use only; the CI "
             "workflow does not pass --full.",
    )
```

Find the `--keep` argument (it's after `--context` in the file):

```python
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep temp worktrees after the run.",
    )
```

Immediately BEFORE the `--keep` argument, insert a new `--hide-unchanged`
argument:

```python
    parser.add_argument(
        "--hide-unchanged",
        action="store_true",
        help="Exclude unchanged files from the sidebar and body. "
             "Summary counts include them but the report is otherwise "
             "terse. Default: unchanged files are shown.",
    )
```

### Step 2: Pass `hide_unchanged` to `render_report` in `cli.py::main`

Locate the call to `render_report` in `main()` (around line 91–100):

```python
# Before
            html_out = render_report(
                specs,
                context=args.context,
                full=args.full,
                ref_a=args.ref_a,
                ref_b=args.ref_b,
                attr=args.attr,
            )
```

```python
# After
            html_out = render_report(
                specs,
                context=args.context,
                full=args.full,
                ref_a=args.ref_a,
                ref_b=args.ref_b,
                attr=args.attr,
                hide_unchanged=args.hide_unchanged,
            )
```

### Step 3: Update `_visible` signature in `report.py`

Locate `_visible` (around line 192):

```python
# Before
def _visible(specs: list[DiffSpec]) -> list[DiffSpec]:
    return [s for s in specs if s.state != "unchanged"]
```

```python
# After
def _visible(specs: list[DiffSpec], hide_unchanged: bool) -> list[DiffSpec]:
    if hide_unchanged:
        return [s for s in specs if s.state != "unchanged"]
    return list(specs)
```

### Step 4: Plumb `hide_unchanged` through `render_sidebar` and `render_report`

Locate `render_sidebar` (around line 226):

```python
# Before
def render_sidebar(specs: list[DiffSpec]) -> str:
    counts_ = counts(specs)
    visible = _visible(specs)
    ...
```

```python
# After
def render_sidebar(specs: list[DiffSpec], hide_unchanged: bool) -> str:
    counts_ = counts(specs)
    visible = _visible(specs, hide_unchanged)
    ...
```

Locate `render_report` (around line 297):

```python
# Before
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
    ...
```

```python
# After
def render_report(
    specs: list[DiffSpec],
    *,
    context: int,
    full: bool,
    ref_a: str,
    ref_b: str,
    attr: str,
    hide_unchanged: bool,
) -> str:
    visible = _visible(specs, hide_unchanged)
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
    sidebar = render_sidebar(specs, hide_unchanged)
    summary = render_summary(specs, ref_a, ref_b, attr, hide_unchanged=hide_unchanged)
    ...
```

(`render_summary` gets its `hide_unchanged` kwarg in the next step.)

### Step 5: Make `(hidden)` conditional in `render_summary`

Locate `render_summary`. Update its signature and conditional logic:

```python
# Before
def render_summary(specs: list[DiffSpec], ref_a: str, ref_b: str, attr: str) -> str:
    counts_ = counts(specs)
    return (
        '<header class="summary">'
        f"<p><strong>{counts_['modified']} modified</strong> · "
        f"{counts_['added']} added · "
        f"{counts_['deleted']} deleted · "
        f"{counts_['unchanged']} unchanged (hidden)</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )
```

```python
# After
def render_summary(
    specs: list[DiffSpec],
    ref_a: str,
    ref_b: str,
    attr: str,
    *,
    hide_unchanged: bool,
) -> str:
    counts_ = counts(specs)
    hidden_suffix = " (hidden)" if hide_unchanged else ""
    return (
        '<header class="summary">'
        f"<p><strong>{counts_['modified']} modified</strong> · "
        f"{counts_['added']} added · "
        f"{counts_['deleted']} deleted · "
        f"{counts_['unchanged']} unchanged{hidden_suffix}</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )
```

### Step 6: Verify Nix build and tests pass

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes; tests run.

### Step 7: Smoke-test both modes

```bash
# Default (show all)
./result/bin/compare-artifacts main main --output /tmp/show-all.html
# With --hide-unchanged
./result/bin/compare-artifacts main main --output /tmp/hide-unchanged.html --hide-unchanged
ls -la /tmp/show-all.html /tmp/hide-unchanged.html
```

Expected: `show-all.html` is larger (96 sections) than `hide-unchanged.html`
(0 sections since all 96 are unchanged here).

Open both in a browser. Verify:

- `show-all.html`: sidebar has 96 entries, all with U badges (gray).
  Summary header says "0 modified · 0 added · 0 deleted · 96 unchanged"
  WITHOUT "(hidden)".

- `hide-unchanged.html`: sidebar is empty (no entries since all are
  unchanged). Summary says "0 modified · 0 added · 0 deleted · 96
  unchanged (hidden)".

- [ ] **Step 8: Commit**

```bash
git add \
    package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py \
    package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py
git commit -m "compare-artifacts: add --hide-unchanged flag; show all by default"
```

______________________________________________________________________

## Task 4: Per-subdir count format `(M of N)`

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py`

### Step 1: Update the per-subdir count display in `render_sidebar`

Locate the inside of `render_sidebar`'s loop over `groups.items()`
(around line 245 area). The current code:

```python
# Before
    out.append("<nav>")
    for subdir, entries in groups.items():
        out.append(
            f"<h3>{html.escape(subdir)} "
            f'<span class="count">({len(entries)})</span></h3>'
        )
        out.append("<ul>")
        ...
```

Change to:

```python
# After
    out.append("<nav>")
    for subdir, entries in groups.items():
        total = len(entries)
        non_unchanged = sum(1 for _, s in entries if s.state != "unchanged")
        if non_unchanged == total:
            count_str = f"({total})"
        else:
            count_str = f"({non_unchanged} of {total})"
        out.append(
            f"<h3>{html.escape(subdir)} "
            f'<span class="count">{count_str}</span></h3>'
        )
        out.append("<ul>")
        ...
```

The `entries` variable is a list of `(index, spec)` tuples (per
`_group_by_subdir`'s return type), so `s.state` is accessed via tuple
unpacking in the generator.

### Step 2: Verify Nix build

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes.

### Step 3: Smoke-test the count format

```bash
./result/bin/compare-artifacts main main --output /tmp/count-test.html
```

Open `/tmp/count-test.html`. Expected: each subdirectory header
shows `(0 of N)` where N is the count of SVGs in that subdir (since
all are unchanged on main-vs-main). Format like:

```
clearspace (0 of 3)
dimensioned (0 of 9)
internal (0 of 64)
...
```

Then run with `--hide-unchanged`:

```bash
./result/bin/compare-artifacts main main --output /tmp/count-test-hidden.html --hide-unchanged
```

Expected: sidebar is empty (no subdir headers since all entries are
filtered out). If there were diffs, each subdir would show `(N)`
(without "of") because M == N when unchanged is excluded.

- [ ] **Step 4: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py
git commit -m "compare-artifacts: per-subdir count shows (M of N) when N > M"
```

______________________________________________________________________

## Task 5: Summary header anchor links

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py`

### Step 1: Add a `_summary_link` helper

In `report.py`, near the top (after imports, before `STYLES`), add a
new private helper:

```python
def _summary_link(
    first_idx_by_state: dict[str, int],
    state: str,
    count: int,
    strong: bool = False,
) -> str:
    """Render a summary count fragment, wrapped in an anchor link if
    the state has at least one visible occurrence."""
    text = f"{count} {state}"
    if strong:
        text = f"<strong>{text}</strong>"
    if count == 0 or state not in first_idx_by_state:
        return text
    return f'<a href="#diff-{first_idx_by_state[state]}">{text}</a>'
```

### Step 2: Compute the first-index map in `render_report` and pass it to `render_summary`

Locate `render_report`. Change:

```python
# Before
def render_report(
    specs: list[DiffSpec],
    *,
    context: int,
    full: bool,
    ref_a: str,
    ref_b: str,
    attr: str,
    hide_unchanged: bool,
) -> str:
    visible = _visible(specs, hide_unchanged)
    sections = "".join(
        ...
        for index, spec in enumerate(visible)
    )
    sidebar = render_sidebar(specs, hide_unchanged)
    summary = render_summary(specs, ref_a, ref_b, attr, hide_unchanged=hide_unchanged)
    ...
```

```python
# After
def render_report(
    specs: list[DiffSpec],
    *,
    context: int,
    full: bool,
    ref_a: str,
    ref_b: str,
    attr: str,
    hide_unchanged: bool,
) -> str:
    visible = _visible(specs, hide_unchanged)
    first_idx_by_state: dict[str, int] = {}
    for i, s in enumerate(visible):
        if s.state not in first_idx_by_state:
            first_idx_by_state[s.state] = i
    sections = "".join(
        ...
        for index, spec in enumerate(visible)
    )
    sidebar = render_sidebar(specs, hide_unchanged)
    summary = render_summary(
        specs,
        ref_a,
        ref_b,
        attr,
        hide_unchanged=hide_unchanged,
        first_idx_by_state=first_idx_by_state,
    )
    ...
```

### Step 3: Update `render_summary` to use the helper

Locate `render_summary`. Update signature and body:

```python
# Before
def render_summary(
    specs: list[DiffSpec],
    ref_a: str,
    ref_b: str,
    attr: str,
    *,
    hide_unchanged: bool,
) -> str:
    counts_ = counts(specs)
    hidden_suffix = " (hidden)" if hide_unchanged else ""
    return (
        '<header class="summary">'
        f"<p><strong>{counts_['modified']} modified</strong> · "
        f"{counts_['added']} added · "
        f"{counts_['deleted']} deleted · "
        f"{counts_['unchanged']} unchanged{hidden_suffix}</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )
```

```python
# After
def render_summary(
    specs: list[DiffSpec],
    ref_a: str,
    ref_b: str,
    attr: str,
    *,
    hide_unchanged: bool,
    first_idx_by_state: dict[str, int],
) -> str:
    counts_ = counts(specs)
    hidden_suffix = " (hidden)" if hide_unchanged else ""
    return (
        '<header class="summary">'
        f"<p>{_summary_link(first_idx_by_state, 'modified', counts_['modified'], strong=True)} · "
        f"{_summary_link(first_idx_by_state, 'added', counts_['added'])} · "
        f"{_summary_link(first_idx_by_state, 'deleted', counts_['deleted'])} · "
        f"{_summary_link(first_idx_by_state, 'unchanged', counts_['unchanged'])}{hidden_suffix}</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )
```

### Step 4: Verify Nix build

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes.

### Step 5: Smoke-test the anchor links

```bash
./result/bin/compare-artifacts main main --output /tmp/anchor-test.html
```

Open `/tmp/anchor-test.html`. In the main-area summary header,
expected:

- `0 modified` (no anchor — count is 0)
- `0 added` (no anchor)
- `0 deleted` (no anchor)
- `96 unchanged` should be an `<a href="#diff-0">96 unchanged</a>`
  link. Clicking it should scroll to the first `<section id="diff-0">`
  in the body.

Test the click: verify the link works.

- [ ] **Step 6: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py
git commit -m "compare-artifacts: link summary counts to first section of each state"
```

______________________________________________________________________

## Task 6: CI workflow `--context 3` pin

**Files:**

- Modify: `.github/workflows/check.yml`

### Step 1: Add `--context 3` to the Compare artifacts step

Locate the `compare-artifacts-build` job. Find the `Compare artifacts`
step:

```yaml
# Before
      - name: Compare artifacts
        run: |
          nix run .#nixos-branding.verification.compare-artifacts -- \
            "${{ steps.refs.outputs.before }}" \
            "${{ steps.refs.outputs.after }}" \
            --output comparison_report.html \
            --summary comparison_summary.json
```

```yaml
# After
      - name: Compare artifacts
        run: |
          nix run .#nixos-branding.verification.compare-artifacts -- \
            "${{ steps.refs.outputs.before }}" \
            "${{ steps.refs.outputs.after }}" \
            --output comparison_report.html \
            --summary comparison_summary.json \
            --context 3
```

(The default is already 3, but pinning it explicitly decouples CI from
future tool defaults.)

### Step 2: Verify YAML parses

```bash
nix shell nixpkgs#yamllint --command yamllint .github/workflows/check.yml
```

Expected: only pre-existing style warnings.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/check.yml
git commit -m "ci: pin compare-artifacts --context 3 in CI report"
```

______________________________________________________________________

## Task 7: `pyproject.toml` version bump

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/pyproject.toml`

### Step 1: Bump version from 0.1.0 to 0.2.0

In `pyproject.toml`, find:

```toml
version = "0.1.0"
```

Change to:

```toml
version = "0.2.0"
```

### Step 2: Verify Nix build still passes

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes; the new version propagates through
`importTOML ./pyproject.toml` in `package.nix`.

- [ ] **Step 3: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/pyproject.toml
git commit -m "compare-artifacts: bump version to 0.2.0"
```

______________________________________________________________________

## Task 8: Update README

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md`

### Step 1: Update the Usage code block

Locate the Usage section's code block:

```bash
# Before
nix run .#nixos-branding.verification.compare-artifacts -- \
    <ref-a> <ref-b> [--attr ATTR] [--output PATH] [--summary PATH] \
                    [--full | --context N] [--keep]
```

Replace with:

```bash
# After
nix run .#nixos-branding.verification.compare-artifacts -- \
    <ref-a> <ref-b> [--attr ATTR] [--output PATH] [--summary PATH] \
                    [--full | --context N] [--hide-unchanged] [--keep]
```

### Step 2: Update the `--summary output` JSON example

Locate the JSON block in the `## --summary output` section:

```json
# Before
{
  "changed": 5,
  "added": 1,
  "removed": 0,
  "unchanged": 21
}
```

Replace with:

```json
# After
{
  "modified": 5,
  "added": 1,
  "deleted": 0,
  "unchanged": 21
}
```

### Step 3: Add a new paragraph after the Usage section's numbered list, before "## Examples"

Find the line "Renders an HTML report at `comparison_report.html` (or
`--output`) with a sticky sidebar grouped by subdirectory and per-file
diff tables (context-only by default, full diffs with `--full`)." This
ends the Usage section's pipeline list.

Right after the closing `1.` of that list and before the next `##`
heading, add:

```markdown
By default the report includes every artifact, with unchanged files
shown in gray. Pass `--hide-unchanged` for a terser report focused on
the changed/added/deleted entries only.
```

- [ ] **Step 4: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md
git commit -m "compare-artifacts: README docs --hide-unchanged and renamed JSON keys"
```

______________________________________________________________________

## Task 9: Update compare-artifacts spec

**Files:**

- Modify: `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md`

### Step 1: Update DiffSpec Literal in the Module responsibilities section

Locate the `DiffSpec` dataclass code block (around line 242–248):

```python
# Before
@dataclass
class DiffSpec:
    before: list[str]
    after: list[str]
    path: Path  # relative to the build output root
    state: Literal["added", "removed", "changed", "unchanged"]
```

```python
# After
@dataclass
class DiffSpec:
    before: list[str]
    after: list[str]
    path: Path  # relative to the build output root
    state: Literal["added", "deleted", "modified", "unchanged"]
```

### Step 2: Update the `--summary` JSON example

Locate the JSON example in the spec (around line 187–192):

```json
# Before
{"changed": 5, "added": 1, "removed": 0, "unchanged": 21}
```

```json
# After
{"modified": 5, "added": 1, "deleted": 0, "unchanged": 21}
```

### Step 3: Update the CLI synopsis to add `[--hide-unchanged]`

Locate the CLI synopsis code block. The current form has lines:

```
[--full | --context N]
[--keep]
```

Add `[--hide-unchanged]` between them:

```
[--full | --context N]
[--hide-unchanged]
[--keep]
```

### Step 4: Update the Options block to add `--hide-unchanged`

In the Options block, after the `--context` line and before the
`--keep` line, insert:

```
  --hide-unchanged       Exclude unchanged files from the sidebar
                         and body. Summary counts include them but
                         the report is otherwise terse. Default:
                         unchanged files are shown.
```

### Step 5: Update ASCII diagrams in the HTML report structure section

Locate the ASCII diagram showing sidebar layout (around line 401–420).
Anywhere it references the old words "changed" or "removed", update
to "modified" / "deleted". Common spots:

- `M  logo.svg` → still `M` (letter); but in the labels/legend
  showing state words: change "changed" → "modified" and "removed" →
  "deleted".
- The summary line `X changed · Y added · Z removed` → `X modified · Y added · Z deleted`.
- The example `<h2>` text: change "changed" → "modified" in any
  example badge text.

Use `grep -n "changed\|removed" docs/superpowers/specs/2026-06-03-compare-artifacts-design.md`
to find all sites. Update each occurrence in the body (NOT in the
ASCII diagrams' single-letter `M` / `D` references, which stay).

### Step 6: Update the Conventions bullet about subdir suppression

Locate the bullet that says (around line 466):

```markdown
- **Sidebar groups** are subdirectory names from the relative paths.
  Subdirs with zero changed/added/removed entries do not appear.
```

Update to reflect the new default (show all):

```markdown
- **Sidebar groups** are subdirectory names from the relative paths.
  Every subdir with at least one visible entry appears. With
  `--hide-unchanged`, subdirs with zero modified/added/deleted entries
  are filtered out.
```

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/specs/2026-06-03-compare-artifacts-design.md
git commit -m "docs: update compare-artifacts spec for state rename and --hide-unchanged"
```

______________________________________________________________________

## Task 10: Update CI integration spec

**Files:**

- Modify: `docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md`

### Step 1: Update `jq` queries in the workflow YAML excerpt

Locate the `compare-artifacts-comment` job's YAML excerpt in the
spec. Find the two `jq` lines:

```yaml
# Before
jq -e 'all(.changed, .added, .removed, .unchanged; type == "number")' \
   comparison_summary.json > /dev/null
SUMMARY=$(jq -r '"\(.changed) changed · \(.added) added · \(.removed) removed · \(.unchanged) unchanged"' \
          comparison_summary.json)
```

```yaml
# After
jq -e 'all(.modified, .added, .deleted, .unchanged; type == "number")' \
   comparison_summary.json > /dev/null
SUMMARY=$(jq -r '"\(.modified) modified · \(.added) added · \(.deleted) deleted · \(.unchanged) unchanged"' \
          comparison_summary.json)
```

### Step 2: Update the `Compare artifacts` step to show `--context 3`

Locate the `Compare artifacts` step's YAML excerpt. Update to include
the `--context 3` flag:

```yaml
# Before
- name: Compare artifacts
  run: |
    nix run .#nixos-branding.verification.compare-artifacts -- \
      "${{ steps.refs.outputs.before }}" \
      "${{ steps.refs.outputs.after }}" \
      --output comparison_report.html \
      --summary comparison_summary.json
```

```yaml
# After
- name: Compare artifacts
  run: |
    nix run .#nixos-branding.verification.compare-artifacts -- \
      "${{ steps.refs.outputs.before }}" \
      "${{ steps.refs.outputs.after }}" \
      --output comparison_report.html \
      --summary comparison_summary.json \
      --context 3
```

### Step 3: Search the spec for other references to the old keys

```bash
grep -n "changed\|removed" docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md | grep -v "^[0-9]*:[a-zA-Z #][^[:alnum:]]*-" | head -40
```

Review the matches. Common spots:

- Comment-body example text inside the sticky-comment YAML
- Edge-cases section mentions of "changed" state
- The "Two-job split rationale" section may reference state words

Update each occurrence to use `modified` / `deleted`. Skip context
where "changed" means "modified by another process" (verb usage, not
state-name usage).

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md
git commit -m "docs: update CI integration spec for renamed JSON keys"
```

______________________________________________________________________

## End-to-end verification

After all 10 tasks complete:

- [ ] **Step 1: Run the full test suite**

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes; all 56 tests pass in the sandbox.

- [ ] **Step 2: Run end-to-end with two real refs**

Pick two refs that produce different artifacts (the CI integration
spec mentions `9c6d172^` vs `main` produces no diffs; pick refs that
DO diff if you want to exercise the full path):

```bash
./result/bin/compare-artifacts <ref-a> <ref-b> \
    --output /tmp/final-test.html \
    --summary /tmp/final-test.json
cat /tmp/final-test.json
```

Expected: JSON has the new keys (`modified`, `added`, `deleted`,
`unchanged`).

Open `/tmp/final-test.html` in a browser. Verify:

- **Badges:** Sidebar has single-letter A/M/D/U badges with proper
  padding (no overflow). Section headers have full state words
  ("modified", "added", "deleted", "unchanged") in colored pills
  with text fully visible on the colored background.
- **Default behavior:** Sidebar shows every artifact (including
  unchanged ones). Unchanged entries have gray `U` badges.
- **Subdir counts:** Format is `(M of N)` when modified+added+deleted
  count < total, otherwise `(N)`.
- **Summary anchor links:** Each non-zero count in the main-area
  summary header is a clickable link that jumps to the first section
  of that state.
- **Summary text:** Shows "X modified · Y added · Z deleted · U
  unchanged" (no "(hidden)" qualifier).
- **`--hide-unchanged`:** Re-run with `--hide-unchanged`. Sidebar
  shrinks to only modified/added/deleted entries. Subdir counts
  collapse to `(N)`. Summary text shows "(hidden)" qualifier.
- **`--full`:** Re-run with `--full` (alone, no `--hide-unchanged`).
  Expect a multi-MB HTML file. Warning lives in help text but isn't
  programmatically blocked.

No commit at this stage — verification only.

______________________________________________________________________

## Commit summary

After all 10 tasks, your branch should have 10 new commits on top of
where you started:

1. `compare-artifacts: fix badge CSS overflow; add U badge color`
1. `compare-artifacts: rename states (changed→modified, removed→deleted)` (atomic)
1. `compare-artifacts: add --hide-unchanged flag; show all by default`
1. `compare-artifacts: per-subdir count shows (M of N) when N > M`
1. `compare-artifacts: link summary counts to first section of each state`
1. `ci: pin compare-artifacts --context 3 in CI report`
1. `compare-artifacts: bump version to 0.2.0`
1. `compare-artifacts: README docs --hide-unchanged and renamed JSON keys`
1. `docs: update compare-artifacts spec for state rename and --hide-unchanged`
1. `docs: update CI integration spec for renamed JSON keys`

All commits should be signed (`git log --pretty=format:'%G?' --no-merges` shows all `G`).

The branch (`compare-artifacts-ci-integration`) is now ready to push
and open a PR against `main`, bundling the original compare-artifacts
implementation, the CI integration work, and these three feature
changes.
