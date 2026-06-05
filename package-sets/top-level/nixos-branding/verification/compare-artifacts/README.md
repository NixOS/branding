# compare-artifacts

Diff nixos-branding artifacts between two git refs.

## Usage

```bash
nix run .#nixos-branding.verification.compare-artifacts -- \
    <ref-a> <ref-b> [--attr ATTR] [--output PATH] [--summary PATH] \
                    [--full | --context N] [--hide-unchanged] [--keep]
```

The tool:

1. Creates two temporary detached-HEAD worktrees, one per ref.
1. Runs `nix build --no-link --print-out-paths .#<attr>` on each
   worktree in parallel (default attr: `nixos-branding.all-artifacts`).
1. Globs `*.svg` from both build outputs, pairs files by relative path,
   classifies each as added / deleted / modified / unchanged.
1. Renders an HTML report at `comparison_report.html` (or `--output`)
   with a sticky sidebar grouped by subdirectory and per-file diff
   tables (context-only by default, full diffs with `--full`).

By default the report includes every artifact, with unchanged files
shown in gray. Pass `--hide-unchanged` for a terser report focused on
the modified/added/deleted entries only.

## `--summary` output

When `--summary PATH` is passed, the tool also writes a small JSON
file at PATH alongside the HTML report. The JSON contains exactly
four integer count keys:

```json
{
  "modified": 5,
  "added": 1,
  "deleted": 0,
  "unchanged": 21
}
```

The HTML output (`--output`) is unchanged whether or not `--summary`
is passed. The JSON is for consumers that need machine-readable counts
without parsing the HTML (notably the CI workflow that posts a sticky
PR comment).

The shape is stable: adding new keys is OK; removing or renaming
existing keys, or changing their types, is a breaking change.

## Examples

```bash
# Compare two branches.
nix run .#nixos-branding.verification.compare-artifacts -- main feature-branch

# Compare a different artifact bundle.
nix run .#nixos-branding.verification.compare-artifacts -- \
    main feature-branch --attr nixos-branding.deployed-assets

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
