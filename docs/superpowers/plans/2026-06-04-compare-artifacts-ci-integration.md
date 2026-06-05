# compare-artifacts CI Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire `compare-artifacts` into the GitHub Actions workflow so every
PR to `main` gets an HTML report attached and a sticky PR comment with
the diff counts. As a hard prerequisite, add a `--summary PATH` flag to
the tool that emits the counts as a sidecar JSON file (the CI job uses
that JSON, never the HTML, to avoid markdown-injection risk).

**Architecture:** Two-job split in CI for defense-in-depth — a
`compare-artifacts-build` job (read-only token) runs `nix run` on
author-controlled code and uploads artifacts; a separate
`compare-artifacts-comment` job (`pull-requests: write`, no `nix run`)
downloads the summary JSON, validates the value types with `jq -e`, and
posts the sticky comment. Common setup (checkout, Nix install, store
cache) extracted into a composite action that all Nix-using jobs share.
Third-party actions pinned to commit SHAs with a Dependabot config to
keep them current.

**Tech Stack:** GitHub Actions workflow YAML; one composite action;
`actions/checkout@v4`, `actions/upload-artifact@v4`,
`actions/download-artifact@v4` (first-party, tag-pinned);
`cachix/install-nix-action`, `nix-community/cache-nix-action`,
`marocchino/sticky-pull-request-comment`, `release-flow/keep-a-changelog-action`
(third-party, SHA-pinned). Python 3.13 stdlib `json` for the new
`--summary` flag.

**Spec:** `docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md`.

______________________________________________________________________

## Working directory and conventions

All paths in this plan are relative to the repo root
`/home/djacu/dev/nixos/branding/`.

**Commit convention:** Match existing repo style — `<scope>: <imperative>`.
Use `compare-artifacts:` for Python changes, `ci:` for workflow/action
changes, `docs:` for spec amendments. Examples in this plan use these
scopes.

**No `Co-Authored-By` trailer** on any commit. The repo's saved
preference (and the engineer's instruction) is to omit AI attribution.

**Pre-commit hook (`treefmt`)** runs on every commit. If it reformats a
file, re-stage the modified file and re-commit (do not amend). Python is
formatted by `ruff`; Nix by `nixfmt`; markdown by `mdformat`; YAML and
TOML are untouched. `pyproject.toml` is explicitly excluded.

**Feature branch:** Create a single feature branch off `main`
(e.g., `compare-artifacts-ci-integration`) for the entire plan and
push commits to it as you go. The draft PR opened in Phase 5 lives on
this branch.

______________________________________________________________________

## File map

| Path | Action | Phase | Purpose |
|------|--------|-------|---------|
| `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md` | modify | 1 | Amend CLI surface to add `--summary` |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/collect.py` | modify | 1 | Add public `counts(specs)` |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/report.py` | modify | 1 | Replace private `_counts` with import from `collect` |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py` | modify | 1 | Add `--summary` argparse arg + JSON write |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/test_collect.py` | modify | 1 | New `TestCounts` class |
| `package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md` | modify | 1 | Document `--summary` flag |
| `.github/actions/setup-nix/action.yml` | create | 2 | Composite action for shared setup |
| `.github/workflows/check.yml` | modify | 2, 3, 4 | Migrate jobs; add new jobs |
| `.github/dependabot.yml` | create | 3 | Auto-update action versions |

______________________________________________________________________

## Phase 1: Add `--summary` flag to compare-artifacts

This phase is a small amendment to the existing `compare-artifacts` tool.
It must complete before any of Phase 2+ has anything useful to consume.

### Task 1: Amend compare-artifacts spec with `--summary` documentation

**Files:**

- Modify: `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md`

The CI spec already references `--summary` as a prerequisite, but the
canonical tool spec does not yet describe it. Amend the tool spec so the
two documents agree.

- [ ] **Step 1: Add `--summary PATH` to the CLI surface section**

Open `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md`.

In the "CLI surface" section, find the help-text block (around the
`--full` / `--context` lines). Replace the section's options block with:

```
Options:
  --attr ATTR            Flake attribute to build on each worktree.
                         Default: nixos-branding.all-artifacts
  --output PATH          Output HTML path.
                         Default: ./comparison_report.html
  --summary PATH         If set, write a JSON file at PATH with the
                         counts: {"changed": N, "added": N,
                         "removed": N, "unchanged": N}. All values
                         are integers. CI uses this so the report's
                         HTML doesn't have to be parsed.
  --full                 Show full file diffs (no context trimming).
                         Mutually exclusive with --context.
  --context N            Lines of unchanged context around changes.
                         Default: 3. Must be >= 0.
  --keep                 Keep temp worktrees after the run.
  -h, --help             Show help.
```

- [ ] **Step 2: Add a paragraph immediately below the options block**

```markdown
The `--summary` JSON file is emitted alongside the HTML output (not
instead of) and contains exactly the four count keys with integer
values. The shape is stable: adding new keys is OK, removing or
renaming keys or changing their type is a breaking change for
consumers (notably the CI workflow).
```

- [ ] **Step 3: Commit**

```bash
git checkout -b compare-artifacts-ci-integration
git add docs/superpowers/specs/2026-06-03-compare-artifacts-design.md
git commit -m "docs: amend compare-artifacts spec with --summary flag"
```

______________________________________________________________________

### Task 2: Add public `counts()` to `collect.py` with tests (TDD)

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/collect.py`
- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/tests/test_collect.py`

`report.py` currently has a private `_counts(specs)` helper. The CLI's
`--summary` write needs the same function, so we promote it to a public
`counts(specs)` in `collect.py` (where `DiffSpec` already lives) and
update `report.py` to import it.

- [ ] **Step 1: Add failing tests at the bottom of `tests/test_collect.py`**

Append:

```python
from compare_artifacts.collect import counts


class TestCounts:
    def test_empty_list(self):
        # All four keys must be present even when empty.
        assert counts([]) == {
            "changed": 0,
            "added": 0,
            "removed": 0,
            "unchanged": 0,
        }

    def test_one_of_each(self, tmp_path):
        before = tmp_path / "before"
        after = tmp_path / "after"
        # Same path on both sides, same content → unchanged.
        write(before / "u.svg", SVG_A)
        write(after / "u.svg", SVG_A)
        # Same path, different content → changed.
        write(before / "c.svg", SVG_A)
        write(after / "c.svg", SVG_B)
        # Only in before → removed.
        write(before / "r.svg", SVG_A)
        # Only in after → added.
        write(after / "a.svg", SVG_A)

        specs = collect_files(before, after)
        assert counts(specs) == {
            "changed": 1,
            "added": 1,
            "removed": 1,
            "unchanged": 1,
        }

    def test_all_keys_always_present(self):
        # Even if some states have zero entries, all four keys exist.
        result = counts([])
        assert set(result.keys()) == {"changed", "added", "removed", "unchanged"}

    def test_values_are_int(self):
        # The CI's jq type-validation requires integer values, not bool/float.
        result = counts([])
        for value in result.values():
            assert isinstance(value, int)
            assert not isinstance(value, bool)  # bool is a subclass of int
```

- [ ] **Step 2: Run the tests to verify failure**

```bash
cd package-sets/top-level/nixos-branding/verification/compare-artifacts
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_collect.py -v
```

Expected: 4 new tests fail with `ImportError` (counts not defined).

- [ ] **Step 3: Add `counts()` to `compare_artifacts/collect.py`**

Append at the bottom of `collect.py`:

```python
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

- [ ] **Step 4: Run the tests to verify they pass**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/test_collect.py -v
```

Expected: all `test_collect.py` tests pass (including the original 8 +
the 4 new ones).

- [ ] **Step 5: Update `compare_artifacts/report.py` to use the public function**

In `compare_artifacts/report.py`, find the existing private `_counts`
helper:

```python
def _counts(specs: list[DiffSpec]) -> dict[str, int]:
    counts = {"added": 0, "changed": 0, "removed": 0, "unchanged": 0}
    for spec in specs:
        counts[spec.state] += 1
    return counts
```

Delete that function entirely. At the existing import block at the top
of the file, find:

```python
from compare_artifacts.collect import DiffSpec
```

Replace with:

```python
from compare_artifacts.collect import DiffSpec, counts
```

Then in the file, find every call site of `_counts(` and rename to
`counts(`. There are exactly two call sites: in `render_summary` and
in `render_sidebar`. Both lines look like `counts = _counts(specs)`
and become `counts_ = counts(specs)` — the local variable shadowed the
function name, which is fine to fix here:

In `render_summary`, change:

```python
def render_summary(specs: list[DiffSpec], ref_a: str, ref_b: str, attr: str) -> str:
    counts = _counts(specs)
    return (
        '<header class="summary">'
        f"<p><strong>{counts['changed']} changed</strong> · "
        ...
```

to:

```python
def render_summary(specs: list[DiffSpec], ref_a: str, ref_b: str, attr: str) -> str:
    counts_ = counts(specs)
    return (
        '<header class="summary">'
        f"<p><strong>{counts_['changed']} changed</strong> · "
        ...
```

Same pattern in `render_sidebar`: rename the local variable from
`counts` to `counts_` to avoid shadowing the imported function. Update
all references in those two functions accordingly. Do NOT change any
function-call signatures or any HTML output strings.

- [ ] **Step 6: Run the full test suite to confirm nothing broke**

```bash
nix shell nixpkgs#python313Packages.pytest --command pytest tests/ -v
```

Expected: all tests pass (parse + collect, including the new
`TestCounts`).

- [ ] **Step 7: Verify the full Nix build still passes**

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build succeeds; tests run in the sandbox.

- [ ] **Step 8: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: promote counts() to public in collect.py"
```

______________________________________________________________________

### Task 3: Add `--summary` flag to `cli.py`

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/compare_artifacts/cli.py`

- [ ] **Step 1: Add `import json` to the imports at the top of `cli.py`**

Find:

```python
import argparse
import signal
import subprocess
import sys
from pathlib import Path
```

Replace with:

```python
import argparse
import json
import signal
import subprocess
import sys
from pathlib import Path
```

- [ ] **Step 2: Add the `counts` import alongside the existing collect import**

Find:

```python
from compare_artifacts.collect import collect_files
```

Replace with:

```python
from compare_artifacts.collect import collect_files, counts
```

- [ ] **Step 3: Add the `--summary` argument to argparse**

In `_build_parser()`, find the existing `--output` argument:

```python
    parser.add_argument(
        "--output",
        default="comparison_report.html",
        type=Path,
        help="Output HTML path (default: ./comparison_report.html).",
    )
```

Immediately after it, add:

```python
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="If set, write a JSON file at this path with the counts "
             "(changed/added/removed/unchanged). The HTML output is "
             "unchanged whether or not this flag is passed.",
    )
```

- [ ] **Step 4: Write the JSON summary file in `main()` after the HTML write**

In `main()`, find the line that writes the HTML:

```python
            args.output.write_text(html_out)
```

Immediately after it (still inside the `with` block, before any close-
paren of the `try:`), add:

```python
            if args.summary is not None:
                args.summary.write_text(json.dumps(counts(specs)))
```

- [ ] **Step 5: Verify the module imports cleanly**

```bash
cd package-sets/top-level/nixos-branding/verification/compare-artifacts
nix shell nixpkgs#python313 --command python -c \
  "import sys; sys.path.insert(0, '.'); from compare_artifacts.cli import main, _build_parser; print('ok')"
```

Expected: `ok`.

- [ ] **Step 6: Verify the argparse setup includes `--summary`**

```bash
nix shell nixpkgs#python313 --command python -c \
  "import sys; sys.path.insert(0, '.'); from compare_artifacts.cli import _build_parser; p = _build_parser(); p.parse_args(['--help'])"
```

Expected: argparse help text including a line with `--summary` and the
description from Step 3.

- [ ] **Step 7: End-to-end smoke test**

From the repo root, rebuild the package and run it against `main` twice
(no diff expected, but the JSON should still be produced):

```bash
cd /home/djacu/dev/nixos/branding
nix build .#nixos-branding.verification.compare-artifacts
./result/bin/compare-artifacts main main \
    --output /tmp/test-report.html \
    --summary /tmp/test-summary.json
cat /tmp/test-summary.json
```

Expected output (assuming `main` produces N artifacts identical to
itself):

```
{"changed": 0, "added": 0, "removed": 0, "unchanged": N}
```

where `N` is the actual count of `.svg` files under the
`all-artifacts` build output (likely ~96).

Verify all four keys are present and all values are integers (not
strings, not floats):

```bash
nix shell nixpkgs#jq --command jq -e \
  'all(.changed, .added, .removed, .unchanged; type == "number")' \
  /tmp/test-summary.json
```

Expected: prints `true` and exits 0.

- [ ] **Step 8: Verify the full Nix build still passes**

```bash
nix build .#nixos-branding.verification.compare-artifacts
```

Expected: build passes.

- [ ] **Step 9: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/
git commit -m "compare-artifacts: add --summary flag for sidecar JSON"
```

______________________________________________________________________

### Task 4: Document `--summary` in the package README

**Files:**

- Modify: `package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md`

- [ ] **Step 1: Update the usage section to mention `--summary`**

Open
`package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md`.

Find the "Usage" section's code block:

```bash
nix run .#nixos-branding.verification.compare-artifacts -- \
    <ref-a> <ref-b> [--attr ATTR] [--output PATH] [--full | --context N] [--keep]
```

Replace with:

```bash
nix run .#nixos-branding.verification.compare-artifacts -- \
    <ref-a> <ref-b> [--attr ATTR] [--output PATH] [--summary PATH] \
                    [--full | --context N] [--keep]
```

- [ ] **Step 2: Add a new section after "Usage" documenting `--summary`**

Insert a new H2 section directly after the Usage section (and before
"Examples"):

````markdown
## `--summary` output

When `--summary PATH` is passed, the tool also writes a small JSON
file at PATH alongside the HTML report. The JSON contains exactly
four integer count keys:

```json
{
  "changed": 5,
  "added": 1,
  "removed": 0,
  "unchanged": 21
}
````

The HTML output (`--output`) is unchanged whether or not `--summary`
is passed. The JSON is for consumers that need machine-readable counts
without parsing the HTML (notably the CI workflow that posts a sticky
PR comment).

The shape is stable: adding new keys is OK; removing or renaming
existing keys, or changing their types, is a breaking change.

````

- [ ] **Step 3: Commit**

```bash
git add package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md
git commit -m "compare-artifacts: document --summary flag in README"
````

______________________________________________________________________

## Phase 2: Composite action and existing-job migration

### Task 5: Resolve SHA pins for third-party actions

**Files:** No file changes in this task; output is a set of SHAs the
later tasks substitute into YAML.

Each third-party action used in the workflow needs a commit SHA
corresponding to the desired version tag. Use `gh api` to look these
up.

- [ ] **Step 1: Look up `cachix/install-nix-action` v31's head SHA**

```bash
gh api repos/cachix/install-nix-action/git/refs/tags/v31 --jq '.object.sha'
```

Expected: a 40-character hex string. Note it down as
`SHA_CACHIX_INSTALL`.

- [ ] **Step 2: Look up `nix-community/cache-nix-action` v6's head SHA**

```bash
gh api repos/nix-community/cache-nix-action/git/refs/tags/v6 --jq '.object.sha'
```

Expected: a 40-character hex string. Note it as `SHA_CACHE_NIX`.

- [ ] **Step 3: Look up `marocchino/sticky-pull-request-comment` v2's head SHA**

```bash
gh api repos/marocchino/sticky-pull-request-comment/git/refs/tags/v2 --jq '.object.sha'
```

Expected: a 40-character hex string. Note it as `SHA_STICKY_COMMENT`.

- [ ] **Step 4: Look up `release-flow/keep-a-changelog-action` v2's head SHA**

```bash
gh api repos/release-flow/keep-a-changelog-action/git/refs/tags/v2 --jq '.object.sha'
```

Expected: a 40-character hex string. Note it as `SHA_CHANGELOG`.

- [ ] **Step 5: Record the SHAs**

Keep the four SHA values in a notes file or in the next tasks'
working memory. Each will be substituted into the YAML in Tasks 6, 8,
and 11.

No commit in this task — research only.

______________________________________________________________________

### Task 6: Create the composite action

**Files:**

- Create: `.github/actions/setup-nix/action.yml`

- [ ] **Step 1: Make the directory**

```bash
mkdir -p .github/actions/setup-nix
```

- [ ] **Step 2: Write `.github/actions/setup-nix/action.yml`**

Substitute the SHAs from Task 5 for the `<SHA_CACHIX_INSTALL>` and
`<SHA_CACHE_NIX>` placeholders.

```yaml
name: 'Setup Nix'
description: |
  Checks out the repository, installs Nix, and restores the /nix/store
  cache. Used by every job in check.yml that needs to run nix commands.

inputs:
  fetch-depth:
    description: |
      Git history depth. Default 1 (just the checkout commit). The
      compare-artifacts-build job overrides to 0 because it needs to
      resolve arbitrary refs (base.sha and merge_commit_sha) via
      `git worktree add`.
    required: false
    default: '1'

runs:
  using: 'composite'
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: ${{ inputs.fetch-depth }}

    - uses: cachix/install-nix-action@<SHA_CACHIX_INSTALL>          # was v31
    - uses: nix-community/cache-nix-action@<SHA_CACHE_NIX>          # was v6
      with:
        primary-key: nix-${{ runner.os }}-${{ hashFiles('flake.lock') }}
        restore-prefixes-first-match: nix-${{ runner.os }}-
        gc-max-store-size-linux: 5G
        purge: true
```

- [ ] **Step 3: Commit**

```bash
git add .github/actions/setup-nix/action.yml
git commit -m "ci: add setup-nix composite action"
```

______________________________________________________________________

### Task 7: Migrate `format` and `build-the-world` jobs to the composite action

**Files:**

- Modify: `.github/workflows/check.yml`

- [ ] **Step 1: Read the current workflow file to confirm the starting state**

```bash
cat .github/workflows/check.yml
```

Expected: a file with `format`, `build-the-world`, and
`branding-guide-changelog` jobs. The first two each have
`actions/checkout@v4` + `cachix/install-nix-action@v31` steps that we
will replace with the composite action.

- [ ] **Step 2: Replace the `format` job's steps**

Find:

```yaml
  format:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Install Nix
        uses: cachix/install-nix-action@v31
      - name: Check formatting
        run: nix flake check --print-build-logs
```

Replace with:

```yaml
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/setup-nix
      - run: nix flake check --print-build-logs
```

- [ ] **Step 3: Replace the `build-the-world` job's steps**

Find:

```yaml
  build-the-world:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Install Nix
        uses: cachix/install-nix-action@v31
      - name: Build all branding assets
        run: nix run .\#nixos-branding.verification.verify-nixos-branding-all --print-build-logs
```

Replace with:

```yaml
  build-the-world:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/setup-nix
      - run: nix run .#nixos-branding.verification.verify-nixos-branding-all --print-build-logs
```

(Note: the unescaped `#` in `nix run .#...` is now safe because we're
inside `run:` block, not shell escape — same as before, just cleaner.)

- [ ] **Step 4: Leave `branding-guide-changelog` unchanged**

The third job does not install Nix and does not need migration.

- [ ] **Step 5: Verify the YAML still parses**

```bash
nix shell nixpkgs#yamllint --command yamllint .github/workflows/check.yml || true
```

(yamllint may warn about line length or style; that's fine. We just
want to confirm it's not a parse error.)

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/check.yml
git commit -m "ci: migrate format and build-the-world to setup-nix action"
```

______________________________________________________________________

## Phase 3: Workflow-level infrastructure and Dependabot

### Task 8: Add workflow-level concurrency, permissions, and pin existing third-party action

**Files:**

- Modify: `.github/workflows/check.yml`

- [ ] **Step 1: Add the `concurrency:` and `permissions:` blocks after the `on:` block**

In `.github/workflows/check.yml`, find the `on:` block (currently around
lines 4-12). Immediately after it (before `jobs:`), insert:

```yaml
concurrency:
  # Includes event_name so workflow_call invocations from external
  # workflows don't share a concurrency group with PR or push runs on
  # the same ref. Includes the PR number for PR events, and falls back
  # to the ref for push/dispatch events.
  group: check-${{ github.workflow }}-${{ github.event_name }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

permissions: read-all
```

- [ ] **Step 2: SHA-pin `release-flow/keep-a-changelog-action`**

In the `branding-guide-changelog` job, find:

```yaml
        uses: release-flow/keep-a-changelog-action@v2
```

Replace `v2` with the SHA you noted as `SHA_CHANGELOG` in Task 5,
keeping the version as a trailing comment:

```yaml
        uses: release-flow/keep-a-changelog-action@<SHA_CHANGELOG>     # was v2
```

- [ ] **Step 3: Verify the YAML still parses**

```bash
nix shell nixpkgs#yamllint --command yamllint .github/workflows/check.yml || true
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/check.yml
git commit -m "ci: add concurrency, workflow-level permissions, SHA-pin changelog action"
```

______________________________________________________________________

### Task 9: Add the Dependabot config

**Files:**

- Create: `.github/dependabot.yml`

- [ ] **Step 1: Write the file**

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    # Dependabot updates both tag-pinned and SHA-pinned action
    # references. PRs from Dependabot follow normal review.
```

- [ ] **Step 2: Commit**

```bash
git add .github/dependabot.yml
git commit -m "ci: add Dependabot config for github-actions ecosystem"
```

______________________________________________________________________

## Phase 4: Add the two new compare-artifacts jobs

### Task 10: Add the `compare-artifacts-build` job

**Files:**

- Modify: `.github/workflows/check.yml`

- [ ] **Step 1: Insert the new job after `build-the-world`**

In `.github/workflows/check.yml`, find the `build-the-world:` job
definition. Immediately after its closing (after the `run:` line; before
the `branding-guide-changelog:` job), insert:

```yaml

  compare-artifacts-build:
    runs-on: ubuntu-latest
    needs: build-the-world
    if: github.event_name == 'pull_request'
    # No `pull-requests: write` here. Token theft from compromised
    # author-controlled code (run via `nix run` below) yields a
    # read-only token incapable of posting comments. The comment job
    # downstream (compare-artifacts-comment) carries the write token.
    permissions:
      contents: read
    outputs:
      before: ${{ steps.refs.outputs.before }}
      after: ${{ steps.refs.outputs.after }}
      report-url: ${{ steps.artifact_report.outputs.artifact-url }}
    steps:
      - uses: ./.github/actions/setup-nix
        with:
          fetch-depth: 0

      - name: Resolve refs
        id: refs
        shell: bash
        run: |
          set -euo pipefail
          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          MERGE_SHA="${{ github.event.pull_request.merge_commit_sha }}"
          HEAD_SHA="${{ github.event.pull_request.head.sha }}"

          # fetch-depth: 0 already pulled base + all reachable refs.
          # Only the merge commit needs an explicit fetch because it
          # lives at refs/pull/<N>/merge and isn't on any branch.
          if [ -n "$MERGE_SHA" ]; then
            git fetch origin "$MERGE_SHA" --quiet || true
            AFTER_SHA="$MERGE_SHA"
          else
            echo "::warning::PR has no merge commit (likely unmergeable, or GitHub still computing mergeability); using head.sha"
            AFTER_SHA="$HEAD_SHA"
          fi

          echo "before=$BASE_SHA" >> "$GITHUB_OUTPUT"
          echo "after=$AFTER_SHA" >> "$GITHUB_OUTPUT"

      - name: Compare artifacts
        run: |
          nix run .#nixos-branding.verification.compare-artifacts -- \
            "${{ steps.refs.outputs.before }}" \
            "${{ steps.refs.outputs.after }}" \
            --output comparison_report.html \
            --summary comparison_summary.json

      - id: artifact_report
        uses: actions/upload-artifact@v4
        with:
          name: comparison_report
          path: comparison_report.html
          if-no-files-found: error

      - uses: actions/upload-artifact@v4
        with:
          name: comparison_summary
          path: comparison_summary.json
          if-no-files-found: error
```

- [ ] **Step 2: Verify the YAML still parses**

```bash
nix shell nixpkgs#yamllint --command yamllint .github/workflows/check.yml || true
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/check.yml
git commit -m "ci: add compare-artifacts-build job"
```

______________________________________________________________________

### Task 11: Add the `compare-artifacts-comment` job

**Files:**

- Modify: `.github/workflows/check.yml`

- [ ] **Step 1: Insert the new job after `compare-artifacts-build`**

Find the end of the `compare-artifacts-build` job (the last
`actions/upload-artifact@v4` step). Immediately after it (still before
`branding-guide-changelog:`), insert:

Substitute the SHA you noted as `SHA_STICKY_COMMENT` for the placeholder.

```yaml

  compare-artifacts-comment:
    runs-on: ubuntu-latest
    needs: compare-artifacts-build
    # Skip on fork PRs (read-only token can't post). Also implicitly
    # only runs on pull_request events because compare-artifacts-build
    # itself is gated to those.
    if: github.event.pull_request.head.repo.full_name == github.repository
    permissions:
      pull-requests: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: comparison_summary

      - name: Validate and extract summary
        id: summary
        shell: bash
        run: |
          set -euo pipefail
          # Type-validate the JSON before interpolating into markdown.
          # The summary is fork-controllable in same-repo branch PRs
          # (it's produced by author code via `nix run`), so an
          # unvalidated string interpolation would allow markdown
          # injection (links, mentions, HTML).
          jq -e 'all(.changed, .added, .removed, .unchanged; type == "number")' \
             comparison_summary.json > /dev/null
          SUMMARY=$(jq -r '"\(.changed) changed · \(.added) added · \(.removed) removed · \(.unchanged) unchanged"' \
                    comparison_summary.json)
          echo "summary=$SUMMARY" >> "$GITHUB_OUTPUT"

      - uses: marocchino/sticky-pull-request-comment@<SHA_STICKY_COMMENT>   # was v2
        with:
          header: compare-artifacts
          message: |
            ## Artifact comparison

            **${{ steps.summary.outputs.summary }}**

            [Download report](${{ needs.compare-artifacts-build.outputs.report-url }}) — HTML file; open in a browser.

            <details>
            <summary>Compared</summary>

            - Base: `${{ needs.compare-artifacts-build.outputs.before }}` (current `main` tip when this ran)
            - After: `${{ needs.compare-artifacts-build.outputs.after }}` (merge commit; falls back to PR head if unmergeable)

            </details>
```

- [ ] **Step 2: Verify the YAML still parses**

```bash
nix shell nixpkgs#yamllint --command yamllint .github/workflows/check.yml || true
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/check.yml
git commit -m "ci: add compare-artifacts-comment job"
```

______________________________________________________________________

## Phase 5: End-to-end verification on a draft PR

GitHub Actions workflows can only be exercised on real GitHub runs, so
the rest of the plan is "push and observe."

### Task 12: Push the branch and open a draft PR

- [ ] **Step 1: Push the feature branch**

```bash
cd /home/djacu/dev/nixos/branding
git push -u origin compare-artifacts-ci-integration
```

Expected: branch published; remote URL printed.

- [ ] **Step 2: Open a draft PR against `main`**

```bash
gh pr create --draft \
  --title "ci: add compare-artifacts to PR checks" \
  --body "$(cat <<'EOF'
## Summary

Wires `compare-artifacts` into the GitHub Actions workflow so every PR
to main gets an HTML report attached and a sticky comment with the
diff counts.

Implements two phases of work in one PR for review-time atomicity:

1. New `--summary` flag on `compare-artifacts` that emits the counts
   as a sidecar JSON file (so CI doesn't have to parse the HTML).
2. Two new jobs in `.github/workflows/check.yml`:
   - `compare-artifacts-build` — runs the tool, uploads the report
     and summary as artifacts. Read-only token.
   - `compare-artifacts-comment` — downloads the summary, validates
     the JSON shape, posts a sticky comment with a link to the
     report. `pull-requests: write` token.
3. Shared setup extracted into `.github/actions/setup-nix` composite
   action. Third-party actions SHA-pinned; Dependabot config added to
   keep them current.

## Test plan

- [ ] Scenario 1 (no-op): this PR itself, before any deliberate
      artifact changes. Expect `0 changed · 0 added · 0 removed`.
- [ ] Scenario 2: push a commit that intentionally modifies
      artifacts. Expect non-zero counts; comment updates.
- [ ] Scenario 3: deliberately bad `--summary` JSON (test via a
      throw-away patch). Expect comment job to fail red.
- [ ] Scenario 4: a fork PR. Expect artifact upload to succeed and
      comment job to be skipped via the `if:` guard.

Specs:
- `docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md`
- `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md` (amended)
EOF
)"
```

Expected: PR URL printed; PR status is "Draft."

______________________________________________________________________

### Task 13: Verify scenario 1 — no-op PR

- [ ] **Step 1: Wait for the workflow to complete**

Open the Actions tab for the PR and wait until all jobs finish. The
first run on a cold cache will take several minutes per nix-using job.

```bash
gh pr checks --watch
```

Expected: `format`, `build-the-world`, `compare-artifacts-build`, and
`compare-artifacts-comment` all green. `branding-guide-changelog` may
be green or skipped depending on whether the changelog has unreleased
entries.

- [ ] **Step 2: Verify the sticky comment posted**

Open the PR in the browser, or:

```bash
gh pr view --comments
```

Expected: a comment from `github-actions[bot]` with header
"Artifact comparison" and body showing
`**0 changed · 0 added · 0 removed · N unchanged**` (where N is the
total number of `.svg` artifacts, typically ~96).

- [ ] **Step 3: Verify the artifact uploaded**

Click "Artifacts" on the workflow run page, or:

```bash
gh run list --workflow=check.yml --limit 1
# Then use the run ID:
gh run view <run-id> --log
```

Expected: an artifact named `comparison_report` is listed; downloading
it produces a single `.html` file viewable in a browser.

- [ ] **Step 4: Verify the link in the sticky comment works**

Click the "Download report" link in the PR comment. Expected: GitHub's
artifact download page for the same run.

- [ ] **Step 5: Verify cache restored on the second push** (next task)

No action here; documented for context.

No commit in this task — verification only.

______________________________________________________________________

### Task 14: Verify scenario 2 — artifact-changing commit

- [ ] **Step 1: Pick a low-risk artifact change**

A small change to a `nixoslogo` Python file that affects rendering
output is suitable. For example, edit
`package-sets/python-packages/nixoslogo/nixoslogo/colors.py` and tweak
one color literal by a single hex digit (something visible but
inconsequential):

(Concrete change — open the file, find any line defining a color
constant that flows into rendered SVGs, and change one of its hex
digits. The exact line depends on the current state of that file at
plan-execution time. The key constraint: the change must propagate to
at least one rendered SVG artifact, so the diff has non-zero counts.)

If no obvious target presents itself, alternative:

```bash
echo "# trivial whitespace change" >> \
    package-sets/python-packages/nixoslogo/nixoslogo/colors.py
```

A docstring-level whitespace tweak likely won't change artifacts. The
goal is a non-zero diff, so prefer the color-literal approach.

- [ ] **Step 2: Commit and push**

```bash
git add package-sets/python-packages/nixoslogo/nixoslogo/colors.py
git commit -m "test: deliberate artifact-changing commit for CI verification"
git push
```

- [ ] **Step 3: Wait for the workflow to finish**

```bash
gh pr checks --watch
```

Expected: green across the board.

- [ ] **Step 4: Verify the sticky comment updated**

```bash
gh pr view --comments
```

Expected: one sticky comment (header-dedupe means the previous
comment is updated in place, not duplicated). The counts now show
non-zero values for `changed` (and possibly others, depending on
which SVGs the colors.py change affects).

- [ ] **Step 5: Download the report and confirm the diff content matches**

Click the artifact link; open the HTML locally. Expected: the report
shows the actual diff tables for the changed SVGs.

No commit cleanup yet — keep the test commit; we revert it in Task 17.

______________________________________________________________________

### Task 15: Verify scenario 3 — bad-JSON injection rejection

- [ ] **Step 1: Stash the previous test commit and create an injection-test commit**

The goal is to push a commit where `--summary`'s JSON has a non-integer
value, then verify the comment job fails (rather than posting).

A clean way to do this without modifying the tool itself: write a tiny
shell wrapper script that overrides `compare-artifacts` for one CI run.
This is fragile and you can skip if you'd prefer; if you do, **skip
ahead to Task 16** and document Scenario 3 as deferred.

If you proceed: in the workflow YAML's `compare-artifacts-build` job,
replace the `Compare artifacts` step's `run:` body with this temporary
content:

```yaml
      - name: Compare artifacts
        run: |
          nix run .#nixos-branding.verification.compare-artifacts -- \
            "${{ steps.refs.outputs.before }}" \
            "${{ steps.refs.outputs.after }}" \
            --output comparison_report.html \
            --summary comparison_summary.json
          # TEST: override summary with a malicious string value
          echo '{"changed": "0](http://evil/)[link", "added": 0, "removed": 0, "unchanged": 0}' \
            > comparison_summary.json
```

```bash
git add .github/workflows/check.yml
git commit -m "test: TEMPORARY summary-injection probe; revert before merging"
git push
```

- [ ] **Step 2: Wait for the workflow**

```bash
gh pr checks --watch
```

Expected: `compare-artifacts-build` succeeds (it just uploaded the bad
JSON). `compare-artifacts-comment` FAILS at the "Validate and extract
summary" step because `jq -e` rejects the string value.

- [ ] **Step 3: Verify the comment was NOT updated with injected content**

```bash
gh pr view --comments
```

Expected: the sticky comment remains as it was from Task 14 (or
earlier) — no markdown injection. The injection attempt is visible in
the workflow run log but did not reach the comment body.

- [ ] **Step 4: Revert the temporary test commit**

```bash
git revert HEAD --no-edit
git push
```

This pushes a clean revert; the next workflow run uses the normal,
non-malicious summary again.

No long-term commits in this task — the test commit and its revert
both stay in history, but neither change persists in the final tree.

______________________________________________________________________

### Task 16: Verify scenario 4 — fork PR (deferred)

Synthesizing a fork-originated PR requires a second GitHub account,
which most engineers don't have set up. Two acceptable approaches:

- [ ] **Step 1a: Defer with documentation**

If a second account isn't available, accept this as a deferred
verification. The behavior is documented in the spec; the `if:` guard
on `compare-artifacts-comment` (`github.event.pull_request.head.repo.full_name == github.repository`)
is a well-known GitHub Actions pattern; the worst case is that the
sticky comment doesn't post on fork PRs — the artifact upload still
works. No action required; proceed to Task 17.

OR

- [ ] **Step 1b: Synthesize a fork PR**

1. From a personal GitHub account that does NOT have write access to
   the repo (or use an account that doesn't), fork the repo.
1. Push a no-op change to a branch on the fork.
1. Open a PR from the fork's branch into the upstream's main.
1. Confirm: `compare-artifacts-build` runs (the action runs on fork
   PRs by default). `compare-artifacts-comment` is SKIPPED (the `if:`
   guard fails). The artifact is still uploaded to the run.

Either way, no commits in this task.

______________________________________________________________________

### Task 17: Clean up test commits and promote PR

- [ ] **Step 1: Drop the test commits from the branch**

The test commit from Task 14 (the deliberate artifact change) must not
ship. The injection test from Task 15 was already reverted, leaving
both the test and the revert in history; they cancel out content-wise
but clutter the log.

Cleanest approach: interactive rebase to drop them.

```bash
# List recent commits to identify which to drop.
git log --oneline -10
```

Expected: the commits to drop are the artifact-changing test commit
(Task 14), the injection-test commit (Task 15), and the revert of the
injection-test commit (Task 15 step 4). If you used `git revert`, the
revert and original are next to each other; both can be dropped.

Use `git rebase -i origin/main` to drop them. **Do NOT use `-i` with
this tool's automated execution since it requires interactive input;
instead, drop them with `git reset --soft <hash>` followed by selective
re-commits, OR use `git rebase --onto`:**

Identify the parent of the first test commit (the one before Task 14's
commit) as `<parent-sha>`. Then:

```bash
git rebase --onto <parent-sha> HEAD~<N> HEAD
```

where `<N>` is the count of test commits to drop (likely 3 if injection
test + revert + artifact-changing change are all present).

A simpler alternative if the test commits are at the tip with no
non-test commits after them: `git reset --hard <parent-sha>` (which
discards them entirely) followed by `git push --force-with-lease`.

- [ ] **Step 2: Force-push the cleaned branch**

```bash
git push --force-with-lease
```

Use `--force-with-lease` (not `--force`) so the push fails safely if
the remote has commits we don't have locally.

- [ ] **Step 3: Wait for the workflow on the cleaned branch**

```bash
gh pr checks --watch
```

Expected: all green; the sticky comment shows zero counts again.

- [ ] **Step 4: Promote the PR out of draft**

```bash
gh pr ready
```

Expected: PR is now ready for review.

- [ ] **Step 5: Final commit / state check**

```bash
git log --oneline origin/main..HEAD
```

Expected: a clean, linear sequence of commits matching the phases of
this plan, with no `test:` commits remaining.

______________________________________________________________________

## Failure-mode checklist (for the engineer's reference)

If anything goes wrong during Phase 5 verification, consult the spec's
"Edge cases" and "Risks" sections at
`docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md`.

The most likely failure modes:

- **`<commit-sha>` placeholder slipped through.** A SHA placeholder
  was left in a YAML file. `nix run` or `gh workflow run` will report
  an unresolved action. Fix: search the YAML for `<` and `>` characters.
- **`jq -e` rejects integer-typed JSON.** Should not happen if the
  `counts()` function correctly returns Python ints (which serialize
  to JSON numbers). If it does, check that no `bool` values are
  leaking (Python's `True`/`False` JSON-serialize as `true`/`false`,
  which `jq` types as boolean, not number).
- **Cache restore is slow on first run.** Expected. After the first
  successful run, the cache is populated; subsequent runs use it.
- **`merge_commit_sha` empty.** Either the PR is unmergeable
  (conflicts) or GitHub is still computing mergeability. The fallback
  to `head.sha` is automatic and prints a `::warning::` in the run log.
