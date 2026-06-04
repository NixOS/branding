# compare-artifacts

Diff nixos-branding artifacts between two git refs.

## Usage

```bash
nix run .#nixos-branding.verification.compare-artifacts -- \
    <ref-a> <ref-b> [--attr ATTR] [--output PATH] [--full | --context N] [--keep]
```

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
