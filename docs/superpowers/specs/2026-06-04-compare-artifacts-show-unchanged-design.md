# compare-artifacts: show unchanged files, rename states, fix badge CSS — Design

## Background

The `compare-artifacts` HTML report currently filters `unchanged` files
out of the sidebar and body to keep the report focused on diffs. While
implementing the CI integration, two issues surfaced with that design:

1. **No way to inspect unchanged files.** When reviewing a PR's
   artifact comparison, contributors sometimes want to confirm which
   artifacts were *not* affected by a change — that information is
   present in the summary count but not in the sidebar or body. Today
   they have to look at the artifact tree separately.

1. **Section-header badges are visually broken in light mode.** The
   `.badge` CSS rule was designed for single-letter sidebar entries
   (`A`, `M`, `D`): it sets `width: 1.2em` with white text. The same
   `.badge` class is reused on the per-section `<h2>` to render the
   full state word ("changed", "added", "removed"). The text overflows
   the colored 1.2em-wide background; in light mode the overflowing
   white text sits on the white page background and is invisible
   (only "ch", "ad", "re" of each word is readable). In dark mode the
   page background contrasts with the white overflow, so the bug isn't
   visible.

1. **State name / single-letter inconsistency.** The codebase uses
   git's familiar single-letter state codes (`M`, `A`, `D`) but with
   non-git words: `M = changed`, `A = added`, `D = removed`. The
   first letter of the word doesn't match the badge letter for the
   "modified" and "deleted" cases.

This design addresses all three in one branch.

## Goals and non-goals

**Goals**

- Show unchanged files in the report by default; provide
  `--hide-unchanged` to opt back into the current concise behavior.
- Display unchanged entries with a gray `U` badge in the sidebar and
  in `<h2>` section headers, alongside the existing A/M/D badges.
- Fix `.badge` CSS so multi-character text doesn't overflow the
  colored background; preserve the look of single-letter sidebar
  badges.
- Rename two of the four state strings so the badge letter matches
  the first letter of the word: `changed` → `modified`,
  `removed` → `deleted`. `added` and `unchanged` are unchanged.

**Non-goals**

- No new finer-grained state-filter controls (e.g., "show only
  added/removed"). The single `--hide-unchanged` boolean is enough
  for the current need; finer controls can be added later if a
  concrete use case emerges.
- No automatic re-pagination, lazy-loading, or other report-size
  mitigations. Showing all artifacts will make the report larger;
  contributors who want terse output use `--hide-unchanged`.
- No change to the underlying diff content of any file — only the
  visibility and labeling of each state.
- No new tests for `render_*` HTML output — golden-file tests for
  HTML are brittle and were ruled out by the original design.

## CLI surface

Add one new flag to the existing CLI:

```
compare-artifacts <ref-a> <ref-b> [--attr ATTR]
                                  [--output PATH]
                                  [--summary PATH]
                                  [--full | --context N]
                                  [--hide-unchanged]
                                  [--keep]

Options:
  ...
  --full                 Show full file diffs (no context trimming).
                         Mutually exclusive with --context. WARNING:
                         combined with the show-all default (no
                         --hide-unchanged), the rendered HTML can grow
                         to many MB for repos with hundreds of large
                         artifacts. Local dev use only; the CI
                         workflow does not pass --full.
  ...
  --hide-unchanged       Exclude unchanged files from the sidebar
                         and body. Summary counts include them but
                         the report is otherwise terse. Default:
                         unchanged files are shown.
  ...
```

The default behavior is now to show all four states. Passing
`--hide-unchanged` restores the previous filtering behavior (unchanged
entries excluded from sidebar and body; summary text appends
"(hidden)").

The `--full` flag's help text gains the explicit warning above so
local users know combining it with the show-all default produces a
much larger HTML output.

## State rename

`DiffSpec.state` literal changes:

```python
# Before
state: Literal["added", "removed", "changed", "unchanged"]

# After
state: Literal["added", "deleted", "modified", "unchanged"]
```

Affected by this rename (complete list — must update every site below
or runtime KeyError / stale display strings will result):

- **`collect.py::collect_files`**: the `(True, False)` branch sets
  `state = "deleted"` (was `"removed"`); the unchanged-vs-different
  fork sets `state = "modified"` (was `"changed"`).
- **`collect.py::counts()`** dict literal: keys become `modified, added, deleted, unchanged`. The literal order is `{"modified": 0, "added": 0, "deleted": 0, "unchanged": 0}` purely as developer intent — Python
  dict equality and the only consumers (the f-strings below and
  `json.dumps`) are order-independent, so no test pins the order. The
  literal order does affect `json.dumps` output order (cosmetic).
- **`collect.py::counts()`** docstring: replace `` `changed`, `added`, `removed`, `unchanged` `` with `` `modified`, `added`, `deleted`, `unchanged` ``.
- **`cli.py::_build_parser`**: the `--summary` flag's help text mentions
  the keys; update from
  `"(changed/added/removed/unchanged)"` to
  `"(modified/added/deleted/unchanged)"`.
- **`tests/test_collect.py`**: every `spec.state == "removed"` becomes
  `"deleted"`; every `spec.state == "changed"` becomes `"modified"`.
  The specific sites are: `test_changed` (line ~43), `test_removed`
  (line ~66), `test_subdirectory_paths_preserved` (line ~90). The
  `TestCounts` expected dicts (lines ~104–108 for `test_empty_list`
  and ~126–131 for `test_one_of_each`) update to the renamed keys.
  The `test_all_keys_always_present` expected set updates to
  `{"modified", "added", "deleted", "unchanged"}`.
- **`report.py::_STATE_TO_BADGE`**: keys become
  `{"added": "A", "modified": "M", "deleted": "D", "unchanged": "U"}`.
- **`report.py::render_summary`** dict-key indices in the f-string:
  every `counts_["changed"]` becomes `counts_["modified"]`; every
  `counts_["removed"]` becomes `counts_["deleted"]`. The displayed
  word in the text also changes (e.g., `"X changed"` → `"X modified"`).
  Final formats:
  - default (unchanged shown):
    `**X modified** · Y added · Z deleted · U unchanged`
  - with `--hide-unchanged`:
    `**X modified** · Y added · Z deleted · U unchanged (hidden)`
- **`report.py::render_sidebar`** sidebar summary line: same dict-key
  and displayed-word changes as `render_summary`. Final format:
  `X modified · Y added · Z deleted · U unchanged` (no "(hidden)" — it's
  only added in the main-area summary).
- **`report.py::render_diff_section`** continues to interpolate
  `spec.state` verbatim into the badge content; the rename means the
  badge text becomes "modified" / "added" / "deleted" / "unchanged"
  (no code change beyond the lookup table).
- **`report.py` module docstring**: the line "color-coded state badges
  (A/M/D)" updates to "color-coded state badges (A/M/D/U)".
- **`cli.py::main`** continues to call `json.dumps(counts(specs))` for
  the `--summary` write; the JSON keys automatically reflect the
  renamed states.

### `--summary` JSON shape

The JSON contract changes from:

```json
{"changed": 5, "added": 1, "removed": 0, "unchanged": 21}
```

to:

```json
{"modified": 5, "added": 1, "deleted": 0, "unchanged": 21}
```

Same four-key structure with integer values; only the keys for
"modified" and "deleted" rename. This is a breaking change for any
consumer that hard-codes the old keys. The only current consumer is
the CI workflow on this same branch, updated as part of the same PR
(see "CI workflow update" below).

The compare-artifacts spec amendment that documented `--summary`
updates its JSON example to the new keys.

## Badge CSS bug fix

Replace the existing `.badge` rule's fixed width with content-aware
sizing:

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

- Single-letter sidebar badges (`A`, `M`, `D`, `U`) still center
  inside the 1.2em minimum width and gain a small horizontal padding
  (subtle visual improvement; consistent with the multi-character
  case).
- Multi-word section-header badges ("modified", "added", "deleted",
  "unchanged") expand to fit their content. The colored background
  covers the entire word; white text reads correctly on both light
  and dark themes.

Add the new `U` rule alongside the existing A/M/D rules:

```css
.badge-A { background: #28a745; }
.badge-M { background: #f0a500; }
.badge-D { background: #d73a49; }
.badge-U { background: #666; }
```

`#666` was chosen for WCAG AA compliance:

| Contrast check | Light (`#666` on `#fff`) | Dark (`#666` on `#1a1a1a`) |
|---|---|---|
| White text on badge bg | 5.74:1 ✓ AA normal text | 5.74:1 ✓ AA normal text |
| Badge bg vs page bg | 5.74:1 ✓ AA non-text | 3.69:1 ✓ AA non-text (≥3:1) |

`#888` (originally proposed) failed AA in light mode (2.85:1 background
contrast and 3.54:1 text contrast against white). `#666` passes both
checks in both themes with a single rule — no dark-mode override.

## Show-unchanged feature

### Filter signature

`_visible` gains a `hide_unchanged: bool` parameter:

```python
def _visible(specs: list[DiffSpec], hide_unchanged: bool) -> list[DiffSpec]:
    if hide_unchanged:
        return [s for s in specs if s.state != "unchanged"]
    return list(specs)
```

### Plumbing

The flag flows from CLI through `render_report` to `_visible`:

- `cli.py::main` passes `hide_unchanged=args.hide_unchanged` to
  `render_report`.
- `render_report` and `render_sidebar` gain a `hide_unchanged: bool`
  kwarg and forward it to `_visible`.
- `render_summary` gains both the `hide_unchanged: bool` kwarg AND
  access to the visible spec list (so it can compute first-occurrence
  indices for the summary anchor links). The cleanest signature
  change: `render_summary(specs, visible, ref_a, ref_b, attr, hide_unchanged)` where `specs` is used for the four counts (which
  include unchanged regardless of visibility) and `visible` is used
  for the anchor-link computation. Both lists are already computed
  in `render_report`, so the call becomes a straightforward arg pass.

### Sidebar appearance

- Unchanged entries appear in the same subdirectory groups as A/M/D
  entries, alphabetically interleaved by relative path. No special
  separator or ordering.
- Each unchanged entry has a gray `U` badge prefix.
- **Per-subdir count format changes** from `(N)` (just total visible)
  to `(M of N)` — where `M` is the count of non-unchanged entries
  (added + modified + deleted) and `N` is the total visible entries
  in that subdir. Example: `clearspace (2 of 27)`. This restores the
  "things to look at" signal that the bare visible count loses when
  unchanged is included.
  - Implementation: `_group_by_subdir` already returns groups of
    `(index, spec)` tuples. The per-subdir count display becomes
    `f"({sum(1 for _, s in entries if s.state != 'unchanged')} of {len(entries)})"`.
  - When `--hide-unchanged` is passed, `M` always equals `N` (no
    unchanged in the visible list), so the format collapses to `(N of N)`.
    To keep the display useful in that case, use `(N)` when `M == N`
    and `(M of N)` only when they differ.

### Section body

- Unchanged entries get the same `<section>` structure as A/M/D
  entries: an `<h2>` with the path and the U-state badge, followed by
  the `difflib.HtmlDiff().make_table(...)` output.
- The existing `--full` flag controls verbosity uniformly:
  - Without `--full` (default `--context 3`): the diff table for an
    unchanged file has an empty body (no diff lines to render) but
    still contains the table skeleton (headers, column groups). The
    section appears as the `<h2>` plus a small empty table —
    minimal but not literally zero markup.
  - With `--full`: the diff table shows the entire file content. For
    ~96 SVG artifacts each ~500 lines, this can produce 10–20 MB of
    HTML. Recommended for local inspection only; the CI workflow
    does not pass `--full`.

### Sidebar summary line

The compact sidebar summary continues to show the four raw counts
without the "(hidden)" qualifier. The detailed "(hidden)" disclosure
only appears in the main-area summary header where there's more
horizontal space for the wording.

### Summary anchor links

Each non-zero count in the main-area summary header becomes a link to
the first section with that state. So given the rendered text:

```
**X modified** · Y added · Z deleted · U unchanged
```

each of the four counts wraps in `<a href="#diff-N">…</a>` where `N`
is the index (in the visible list) of the first spec with that state.
Counts of 0 stay as plain text (no anchor). Implementation:
`render_summary` receives the `specs` list, computes a state →
first-index map (`first_idx_by_state = {state: i for i, s in enumerate(visible) if s.state == state}` — but only the first
occurrence per state), then renders each count's HTML as either a
plain `<strong>` (count is 0 or no occurrence) or as an `<a>` to the
target section. This is a cheap addition that significantly improves
navigation in a 96-entry sidebar.

## CI workflow update

The CI workflow added in the prior CI integration spec (also on this
branch) has a `compare-artifacts-build` and a `compare-artifacts-comment`
job. Both need updates.

### `compare-artifacts-build`: pin `--context 3`

The `Compare artifacts` step's `nix run` invocation gains an explicit
`--context 3` flag so the CI report size stays bounded regardless of
future changes to the tool's default. The job does NOT pass
`--hide-unchanged` — the new show-all default carries through to CI as
agreed during brainstorming:

```diff
- name: Compare artifacts
  run: |
    nix run .#nixos-branding.verification.compare-artifacts -- \
      "${{ steps.refs.outputs.before }}" \
      "${{ steps.refs.outputs.after }}" \
      --output comparison_report.html \
-     --summary comparison_summary.json
+     --summary comparison_summary.json \
+     --context 3
```

### `compare-artifacts-comment`: rename JSON keys

Two lines in the `Validate and extract summary` step change to match
the renamed JSON contract:

```diff
- jq -e 'all(.changed, .added, .removed, .unchanged; type == "number")' \
+ jq -e 'all(.modified, .added, .deleted, .unchanged; type == "number")' \
    comparison_summary.json > /dev/null
- SUMMARY=$(jq -r '"\(.changed) changed · \(.added) added · \(.removed) removed · \(.unchanged) unchanged"' \
+ SUMMARY=$(jq -r '"\(.modified) modified · \(.added) added · \(.deleted) deleted · \(.unchanged) unchanged"' \
    comparison_summary.json)
```

### Commit atomicity requirement

The Python state rename (data layer) and the CI workflow's `jq` query
update **MUST land in the same commit**, otherwise the intermediate
commit produces a tool that emits the new JSON keys but a CI workflow
that queries the old keys → CI fails on that SHA. The plan that
executes this design must keep these two changes together. The
`--context 3` pin and `--full` help-text warning are independent of the
rename and may land in separate commits.

## Version bump

`pyproject.toml` bumps from `0.1.0` to `0.2.0`. Justification: the
`--summary` JSON key rename is a breaking change to the documented
JSON contract. The version bump is a small semver signal that
consumers should re-check their integration. The bump is the only
change in `pyproject.toml`.

## Spec / README updates

The following docs need updates to reflect the renamed states, the
new flag, and the badge color:

- `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md`:
  - State `Literal` updates (in the "Module responsibilities" section
    where `DiffSpec` is shown).
  - `--summary` JSON example updates to new keys.
  - `--hide-unchanged` flag added to the CLI synopsis and Options
    block (in the "CLI surface" section).
  - **ASCII diagrams** in the "HTML report structure" section
    contain the old words ("changed", "removed") — update to
    "modified" / "deleted".
  - The "Conventions" bullet about "Subdirs with zero
    changed/added/removed entries do not appear" updates to either
    "modified/added/deleted" or rewrites for the new show-all
    default (subdirs with zero non-unchanged entries no longer have
    special suppression — every subdir with at least one visible
    entry appears).
- `docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md` —
  references to JSON keys (the `jq` snippets in the workflow YAML
  excerpt and the comment-body example) update to the new keys.
- `package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md` —
  `--summary` example JSON in the `## --summary output` section uses
  the new keys; usage synopsis adds `[--hide-unchanged]`; description
  paragraph mentions the new default (unchanged shown).

Older plan documents (`docs/superpowers/plans/2026-06-04-compare-artifacts.md`,
`docs/superpowers/plans/2026-06-04-compare-artifacts-ci-integration.md`)
are historical execution artifacts — they are NOT updated. Future
plans should reference the post-rename spec.

## Tests

Updated assertions in existing tests; no new tests. The complete list
of test sites to update (mirrors the "Affected by this rename" list in
the "State rename" section):

- `tests/test_collect.py::TestCollectFiles::test_changed` —
  `assert specs[0].state == "changed"` → `"modified"`.
- `TestCollectFiles::test_removed` —
  `assert specs[0].state == "removed"` → `"deleted"`.
- `TestCollectFiles::test_subdirectory_paths_preserved` —
  `assert specs[0].state == "changed"` → `"modified"`.
- `TestCounts::test_empty_list` expected dict updates to
  `{"changed": 0, "added": 0, "removed": 0, "unchanged": 0}` →
  `{"modified": 0, "added": 0, "deleted": 0, "unchanged": 0}`.
- `TestCounts::test_one_of_each` expected dict updates to
  `{"modified": 1, "added": 1, "deleted": 1, "unchanged": 1}`.
- `TestCounts::test_all_keys_always_present` updates the expected set
  to `{"modified", "added", "deleted", "unchanged"}`.
- All other tests are unaffected.

No tests for the `_visible` filter, the `--hide-unchanged` flag, the
new per-subdir `(M of N)` count format, the summary anchor links, or
the badge CSS. These are exercised via the existing manual `nix run`
smoke test path (build the tool, run against two refs, open the HTML
in a browser).

## Branch and merge strategy

All work lands on the current branch
`compare-artifacts-ci-integration`. No new branch; no rebase. The
commits in this feature add to the existing chain, ending with the
CI workflow `jq` update. The entire branch (original compare-artifacts
implementation + CI integration + this feature) merges to `main` in
one PR.

## Risks and mitigations

- **JSON contract breakage for hypothetical external consumers.** The
  `--summary` JSON keys change from `changed/removed` to
  `modified/deleted`. The only known consumer is the CI workflow on
  this same branch, updated atomically. Mitigation: bumped
  `pyproject.toml` version from `0.1.0` to `0.2.0` to signal the
  break; the compare-artifacts spec amendment documents the new keys
  with the stability note that future renames are breaking.
- **Report-size growth.** Showing all artifacts by default makes the
  generated HTML noticeably larger (every artifact becomes a sidebar
  entry and a `<section>`). Without `--full`, each unchanged section
  is an `<h2>` + an empty difflib table skeleton, so growth is
  bounded to roughly N × 100 bytes (N = artifact count). For the
  current ~96-artifact branding repo, that's ~10 KB more —
  negligible. With `--full`, unchanged sections expand to full file
  content, producing 10–20 MB of HTML for typical inputs; the
  `--full` help text now carries an explicit warning, and the CI
  workflow does not pass `--full`.
- **CI report size pinned via `--context 3`.** The CI workflow
  explicitly passes `--context 3` so future changes to the tool's
  default `--context` value don't change CI report size unexpectedly.
- **Sidebar visual clutter.** With many unchanged files in a single
  subdir (the common case), the sidebar grows. Three mitigations
  inside this design: (1) the gray `U` badge visually de-emphasizes
  unchanged entries; (2) the per-subdir count format `(M of N)`
  preserves the at-a-glance "how many things to look at" signal;
  (3) the summary header's counts become anchor links to the first
  matching section so a 96-entry sidebar isn't required for
  navigation. Future enhancements (per-state collapsing, etc.) are
  explicitly out of scope.
- **Section-ID `diff-N` stability.** Section IDs are computed from
  position in the visible list. With `--hide-unchanged` toggled, the
  same file gets a different `diff-N`. Anchor links shared between
  runs with different visibility settings won't resolve to the same
  content. Low impact for a CI artifact (each run's report is
  self-contained); not addressed in this design. If link stability
  becomes a real problem, a future amendment could base IDs on a
  hash of the relative path instead.
