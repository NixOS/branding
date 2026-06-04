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

## State rename

`DiffSpec.state` literal changes:

```python
# Before
state: Literal["added", "removed", "changed", "unchanged"]

# After
state: Literal["added", "deleted", "modified", "unchanged"]
```

Affected by this rename:

- **`collect.py`**: the `(True, False)` branch sets `state = "deleted"`
  (was `"removed"`); the unchanged-vs-different fork sets
  `state = "modified"` (was `"changed"`).
- **`collect.py::counts()`**: dict keys become
  `{"added", "modified", "deleted", "unchanged"}`. The order in the
  dict literal also updates to `{"modified": 0, "added": 0, "deleted": 0, "unchanged": 0}`
  (we keep "modified" first because it's the most common state for
  a typical PR; the test that pins this ordering updates accordingly).
- **`tests/test_collect.py`**: assertions checking
  `spec.state == "removed"` become `"deleted"`; same for `"changed"` → `"modified"`. `TestCounts` test cases update their expected dicts.
- **`report.py::_STATE_TO_BADGE`**: keys become
  `{"added": "A", "modified": "M", "deleted": "D", "unchanged": "U"}`.
- **`report.py::render_summary`** text:
  - default: `**X modified** · Y added · Z deleted · U unchanged`
  - with `--hide-unchanged`: `**X modified** · Y added · Z deleted · U unchanged (hidden)`
- **`report.py::render_diff_section`** continues to interpolate
  `spec.state` verbatim into the badge content; no code change here
  beyond the lookup table.
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
.badge-U { background: #888; }
```

No dark-mode override for `.badge-U` — `#888` reads adequately on both
the light (white) and dark (`#1a1a1a`) backgrounds, matching the
existing A/M/D treatment (which also has no dark-mode overrides).

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
- `render_summary` gains the same kwarg and uses it to decide whether
  to append "(hidden)" to the unchanged count.

### Sidebar appearance

- Unchanged entries appear in the same subdirectory groups as A/M/D
  entries, alphabetically interleaved by relative path. No special
  separator or ordering.
- Each unchanged entry has a gray `U` badge prefix.
- Per-subdir count in the sidebar reflects the count of *visible*
  entries; this number grows when unchanged is included.

### Section body

- Unchanged entries get the same `<section>` structure as A/M/D
  entries: an `<h2>` with the path and the U-state badge, followed by
  the `difflib.HtmlDiff().make_table(...)` output.
- The existing `--full` flag controls verbosity uniformly:
  - Without `--full` (default `--context 3`): the diff table for an
    unchanged file is essentially empty (no diff to surround with
    context). Section appears as just the `<h2>` header.
  - With `--full`: the diff table shows the entire file content.

### Sidebar summary line

The compact sidebar summary continues to show the four raw counts
without the "(hidden)" qualifier. The detailed "(hidden)" disclosure
only appears in the main-area summary header where there's more
horizontal space for the wording.

## CI workflow update

The CI workflow added in the prior CI integration spec (also on this
branch) has a `compare-artifacts-comment` job that consumes the
`--summary` JSON via `jq`. Two lines change:

```diff
- jq -e 'all(.changed, .added, .removed, .unchanged; type == "number")' \
+ jq -e 'all(.modified, .added, .deleted, .unchanged; type == "number")' \
    comparison_summary.json > /dev/null
- SUMMARY=$(jq -r '"\(.changed) changed · \(.added) added · \(.removed) removed · \(.unchanged) unchanged"' \
+ SUMMARY=$(jq -r '"\(.modified) modified · \(.added) added · \(.deleted) deleted · \(.unchanged) unchanged"' \
    comparison_summary.json)
```

This update lands as part of the same set of commits as the tool
changes; the final PR's diff stays internally consistent.

## Spec / README updates

The following docs need updates to reflect the renamed states and the
new flag:

- `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md` —
  state literal, `--summary` JSON example, `--hide-unchanged` flag
  documentation, CLI synopsis includes `[--hide-unchanged]`.
- `docs/superpowers/specs/2026-06-04-compare-artifacts-ci-integration-design.md` —
  references to JSON keys (e.g., the `jq` snippets in the workflow
  YAML) update to the new keys.
- `package-sets/top-level/nixos-branding/verification/compare-artifacts/README.md` —
  `--summary` example JSON in the `## --summary output` section uses
  the new keys; usage synopsis adds `[--hide-unchanged]`.

## Tests

Updated assertions in existing tests; no new tests:

- `tests/test_collect.py::TestCollectFiles::test_removed` updates
  `assert specs[0].state == "deleted"` (was `"removed"`).
- `TestCollectFiles::test_changed` updates `assert specs[0].state == "modified"`
  (was `"changed"`).
- `TestCounts::test_one_of_each` expected dict updates to
  `{"modified": 1, "added": 1, "deleted": 1, "unchanged": 1}`.
- `TestCounts::test_all_keys_always_present` updates the expected set
  to `{"modified", "added", "deleted", "unchanged"}`.
- All other tests are unaffected.

No tests for the `_visible` filter, the `--hide-unchanged` flag, or
the badge CSS. The first two are one-line conditionals; the third is
CSS text. All three are exercised via the existing manual `nix run`
smoke test path (build the tool, run against two refs, open the HTML).

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
  this same branch, updated atomically. If any other consumer exists
  (none known), they break and must update. Mitigation: the
  compare-artifacts spec amendment explicitly documents the new keys
  with a stability note that future renames are breaking; PRs that
  add new consumers should reference the spec.
- **Report-size growth.** Showing all artifacts by default makes the
  generated HTML noticeably larger (every artifact becomes a sidebar
  entry and a `<section>`). Without `--full`, each unchanged section
  is a short `<h2>` + a near-empty diff table, so growth is bounded
  to roughly N × 100 bytes (N = artifact count). For the current
  ~96-artifact branding repo, that's ~10 KB more — negligible.
  With `--full`, unchanged sections expand to full file content,
  which can be a few hundred KB per file; CI users who want a small
  artifact should not combine `--full` with the new default.
- **Sidebar visual clutter.** With many unchanged files in a single
  subdir (the common case), the sidebar grows. The gray `U` badge
  visually de-emphasizes them so the eye still tracks A/M/D first;
  acceptable for first iteration. Future enhancements (per-state
  collapsing, etc.) are explicitly out of scope.
