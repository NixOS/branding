# compare-artifacts CI integration — Design

## Background

The `compare-artifacts` tool (see
`docs/superpowers/specs/2026-06-03-compare-artifacts-design.md`) produces
an HTML report showing how branding artifacts differ between two git
refs. Today it is only invokable locally. This design wires it into the
GitHub Actions workflow so that every pull request to `main` gets an
artifact-comparison report attached, helping reviewers see exactly how
the merged state of `main` would change.

## Goals and non-goals

**Goals**

- Every PR to `main` automatically gets a fresh `comparison_report.html`
  attached as a downloadable workflow artifact.
- A sticky PR comment summarizes the counts
  (`X changed · Y added · Z removed · U unchanged`) and links to the
  artifact.
- The comparison is the "post-merge delta": `pull_request.base.sha`
  (current `main` tip when the workflow fires) vs
  `pull_request.merge_commit_sha` (GitHub's auto-generated merge of the
  PR into `main`). Falls back to `head.sha` for unmergeable PRs.
- The new job is chained behind the existing `build-the-world` so we
  never run on a broken state.
- Build caching via `/nix/store` cache so repeated runs are not
  prohibitively slow.
- Workflow setup (checkout + Nix install + cache) is extracted into a
  reusable composite action, eliminating duplication across the three
  jobs that need it.
- The check is informational — it never fails the PR for artifact
  diffs.

**Non-goals**

- No automatic gating, blocking, or labelling on artifact diffs (per
  the original tool design, informational only).
- No GitHub Pages preview of the HTML report. Artifact upload + PR
  comment with a download link is sufficient.
- No per-file detail in the PR comment summary — the HTML report is
  the source of truth for that.
- No support for non-`pull_request` triggers (workflow runs on pushes
  to `main` and on `workflow_dispatch` skip the compare-artifacts job
  entirely, because `merge_commit_sha` is only defined on PR events).
- No special handling for the sticky comment from forks — fork PRs
  receive the uploaded artifact but no PR comment (a GitHub-imposed
  limitation, see "Edge cases").

## Prerequisites

This design depends on one change to the `compare-artifacts` tool that
does not yet exist:

- **`--summary PATH` flag** writing a sidecar JSON file with the four
  count keys (`changed`, `added`, `removed`, `unchanged`). The CI job
  uses the JSON to render the sticky comment without parsing HTML.

The CI work cannot ship until the `--summary` flag does. The expected
sequence is:

1. Amend the compare-artifacts spec to add `--summary`.
1. Plan and implement the flag (small TDD cycle).
1. Implement this CI integration.

## Architecture

Two file-level changes:

1. **New file `.github/actions/setup-nix/action.yml`** — a composite
   action that bundles the per-job setup currently duplicated across
   `format` and `build-the-world`, plus the new `/nix/store` cache for
   `compare-artifacts`.

1. **Modified `.github/workflows/check.yml`** — three existing jobs
   migrate to use the composite action; one new job
   (`compare-artifacts`) is added; a workflow-level `concurrency` block
   cancels in-flight runs when a PR receives a new push.

Job graph (simplified):

```
format ────────────────────────────────────── (success)
build-the-world ─┬──────────────────────────── (success)
                 └─→ compare-artifacts ─────── (success on PR; skipped
                                                on push)
branding-guide-changelog ─────────────────── (success)
```

`format` and `branding-guide-changelog` run independently of
`build-the-world`. `compare-artifacts` runs only on `pull_request`
events and only after `build-the-world` succeeds.

### The composite action: `.github/actions/setup-nix/action.yml`

```yaml
name: 'Setup Nix'
description: |
  Checks out the repository, installs Nix, and restores the /nix/store
  cache. Used by every job in check.yml that needs to run nix commands.

inputs:
  fetch-depth:
    description: |
      Git history depth. Default 1 (just the checkout commit). The
      compare-artifacts job overrides to 0 because it needs to resolve
      arbitrary refs (base.sha and merge_commit_sha) via
      `git worktree add`.
    required: false
    default: '1'

runs:
  using: 'composite'
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: ${{ inputs.fetch-depth }}

    - uses: cachix/install-nix-action@v31

    - uses: nix-community/cache-nix-action@v6
      with:
        primary-key: nix-${{ runner.os }}-${{ hashFiles('flake.lock') }}
        restore-prefixes-first-match: nix-${{ runner.os }}-
        gc-max-store-size-linux: 5G
        purge: true
```

Notes:

- `fetch-depth` is exposed as an input because `format` and
  `build-the-world` work with the default shallow clone, but
  `compare-artifacts` needs full history to resolve `base.sha` and the
  merge commit via `git worktree add --detach <ref>`.
- The `/nix/store` cache benefits all three Nix-using jobs, not just
  `compare-artifacts`. Cache key includes the OS and the hash of
  `flake.lock` so a dependency update invalidates stale cache hits.
- `gc-max-store-size-linux: 5G` caps the saved cache size; GitHub
  enforces a 10 GB per-repo cache limit.
- `purge: true` removes older caches sharing the same key prefix so
  cache usage stays within budget.

### The workflow: `.github/workflows/check.yml`

```yaml
name: Check
run-name: ${{ github.actor }} is running checks

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main
  workflow_call:
  workflow_dispatch:

concurrency:
  group: check-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

permissions: read-all

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/setup-nix
      - run: nix flake check --print-build-logs

  build-the-world:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/setup-nix
      - run: nix run .#nixos-branding.verification.verify-nixos-branding-all --print-build-logs

  compare-artifacts:
    runs-on: ubuntu-latest
    needs: build-the-world
    if: github.event_name == 'pull_request'
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: ./.github/actions/setup-nix
        with:
          fetch-depth: 0

      - name: Resolve refs
        id: refs
        shell: bash
        run: |
          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          MERGE_SHA="${{ github.event.pull_request.merge_commit_sha }}"
          HEAD_SHA="${{ github.event.pull_request.head.sha }}"

          git fetch origin "$BASE_SHA" --quiet

          if [ -n "$MERGE_SHA" ]; then
            git fetch origin "$MERGE_SHA" --quiet || true
            AFTER_SHA="$MERGE_SHA"
          else
            echo "::warning::PR has no merge commit (likely unmergeable); using head.sha"
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

      - name: Extract summary
        id: summary
        shell: bash
        run: |
          SUMMARY=$(jq -r '"\(.changed) changed · \(.added) added · \(.removed) removed · \(.unchanged) unchanged"' \
                    comparison_summary.json)
          echo "summary=$SUMMARY" >> "$GITHUB_OUTPUT"

      - id: artifact
        uses: actions/upload-artifact@v4
        with:
          name: comparison_report
          path: comparison_report.html
          if-no-files-found: error

      - uses: marocchino/sticky-pull-request-comment@v2
        if: github.event.pull_request.head.repo.full_name == github.repository
        with:
          header: compare-artifacts
          message: |
            ## Artifact comparison

            **${{ steps.summary.outputs.summary }}**

            [Download report](${{ steps.artifact.outputs.artifact-url }}) — HTML file; open in a browser.

            <details>
            <summary>Compared</summary>

            - Base: `${{ steps.refs.outputs.before }}` (current `main` tip when this ran)
            - After: `${{ steps.refs.outputs.after }}` (merge commit; falls back to PR head if unmergeable)

            </details>

  branding-guide-changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Get latest or unreleased info
        id: query-release-info
        uses: release-flow/keep-a-changelog-action@v2
        with:
          command: query
          version: latest-or-unreleased
          changelog: ./package-sets/top-level/nixos-branding/nixos-branding-guide/CHANGELOG.md

      - name: Display release info
        run: |
          echo "Version: ${{ steps.query-release-info.outputs.version }}"
          echo "Date: ${{ steps.query-release-info.outputs.release-date }}"
          cat <<'EOF'
          "${{ steps.query-release-info.outputs.release-notes }}"
          EOF
```

### Key behaviors

- **`needs: build-the-world`** enforces the chain. If the world doesn't
  build, the comparison job is skipped and the PR doesn't get a stale
  comparison.
- **`if: github.event_name == 'pull_request'`** keeps the job out of
  pushes to `main` and manual triggers — `merge_commit_sha` only exists
  on PR events.
- **`permissions: pull-requests: write`** is scoped to the
  `compare-artifacts` job, not the workflow. Other jobs keep
  `read-all`.
- **Sticky comment `if:` guard** skips the comment step on fork PRs
  rather than letting it fail. The artifact upload still succeeds; the
  fork's contributors find the report via the Actions run page.
- **Concurrency group** keys on the PR number (or branch ref for non-PR
  events) so multiple rapid pushes to a PR cancel earlier in-flight
  runs.

## Edge cases

- **Fork PRs.** GitHub gives `pull_request`-triggered workflows from
  forks a read-only `GITHUB_TOKEN`, so the sticky-comment step can't
  post. Detected via
  `github.event.pull_request.head.repo.full_name == github.repository`;
  comment step is skipped on forks. Artifact upload still works. We do
  not switch to `pull_request_target` because that event runs in the
  trusted context against untrusted code — too much security risk for
  the marginal UX gain.
- **Unmergeable PRs.** `merge_commit_sha` is empty when GitHub cannot
  auto-merge (conflicts, draft state, etc.). The workflow emits a
  `::warning::` and falls back to `head.sha`. The PR comment notes
  which ref was used.
- **Build failures.** If `compare-artifacts` (or the underlying
  `nix build`) fails on either ref, the workflow step fails. Artifact
  upload is skipped because the prior step errored. The job shows red
  on the PR; the failure cause is in the run log. Note that
  `build-the-world` already gates this job, so the common case (main
  doesn't build) is prevented; failures here usually mean the PR's
  merge commit fails to build.
- **`compare-artifacts` succeeds but produces an empty diff
  (`0 changed · 0 added · 0 removed`).** Normal case for most PRs. The
  comment posts with the zero counts. The report is still uploaded so
  reviewers can confirm the lack of changes.
- **First-run with a cold cache.** Both `base.sha` and the merge
  commit build from scratch. Slow (multiple minutes) but only happens
  once per `flake.lock` change.
- **Cache restore failures.** `cache-nix-action` falls back to building
  from a cold store. The job still succeeds.

## Testing strategy

Workflow changes are hard to test outside of a real GitHub run because
the Actions runner is the only execution environment. The plan:

1. **Implement the `--summary` flag first.** Unit-test the JSON output
   locally and from inside `nix build`'s `pytestCheckHook` sandbox.
1. **Open a draft PR with the workflow change against `main`.** The
   workflow runs on that PR; iterate by pushing additional commits
   until the artifact upload, summary parsing, and sticky comment all
   behave correctly.
1. **Exercise three scenarios on the draft PR:**
   - A push that touches no artifact-affecting code → report shows
     all zeros for changed/added/removed; sticky comment posts.
   - A push that intentionally modifies artifacts (e.g., a small
     `nixoslogo` tweak) → non-zero counts; the comment matches.
   - A push from a fork (synthesize via a second account if practical;
     otherwise document the limitation and accept it) → artifact still
     uploads; sticky-comment step is skipped via the `if:` guard.
1. **Confirm the existing `format` and `build-the-world` jobs still
   pass** after they're switched to the composite action.

## Rollout sequence

1. Amend the compare-artifacts spec at
   `docs/superpowers/specs/2026-06-03-compare-artifacts-design.md` to
   add the `--summary` flag.
1. Plan and implement `--summary` (small TDD cycle: promote `counts()`
   to public in `collect.py` with a test, add `--summary` parsing +
   JSON write in `cli.py`, update README).
1. Plan and implement the workflow changes from this spec.
1. Open a draft PR against `main`. Iterate through the three test
   scenarios.
1. Promote the PR out of draft once verified.

## Risks and mitigations

- **GitHub Actions cache exhaustion.** Each `flake.lock` bump
  invalidates the cache; old caches are purged via `purge: true`.
  Worst case: a cold cache takes several minutes to rebuild the
  artifact world.
- **Sticky comment churn on chatty PRs.** The header dedupes
  comments so we never spam; updates overwrite the previous comment in
  place.
- **The `--summary` JSON format becomes a contract.** Any future
  change to the JSON keys could break the workflow. Mitigation:
  the JSON shape is documented in the `--summary` spec amendment; CI
  expects exactly the four current keys; adding new fields is OK,
  removing or renaming is not.
- **`actions/upload-artifact@v4`'s `artifact-url` output is on a
  comparatively new release of that action.** If GitHub changes the
  output name, the comment link breaks. Mitigation: pin to `@v4`
  rather than `@latest`; the output is stable across v4.x.
