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
- The new jobs are chained behind the existing `build-the-world` so we
  never run on a broken state.
- Build caching via `/nix/store` cache so repeated runs are not
  prohibitively slow.
- Workflow setup (checkout + Nix install + cache) is extracted into a
  reusable composite action, eliminating duplication across the three
  jobs that need it.
- The check is informational about diff *content* — the workflow never
  fails the PR for artifact diffs themselves. Infrastructure errors
  (build failures, missing summary file, etc.) DO fail the check and
  produce a red status; these are bugs to fix, not signal to suppress.
- The comparison is split into two jobs so the build step (which runs
  arbitrary author-controlled Nix and Python via `nix run`) executes
  with read-only token permissions; only the subsequent comment-posting
  job carries `pull-requests: write`. This is defense in depth against
  token theft from a compromised contributor branch.

**Non-goals**

- No automatic gating, blocking, or labelling on artifact diffs (per
  the original tool design, informational only).
- No GitHub Pages preview of the HTML report. Artifact upload + PR
  comment with a download link is sufficient.
- No per-file detail in the PR comment summary — the HTML report is
  the source of truth for that.
- No support for non-`pull_request` triggers (workflow runs on pushes
  to `main` and on `workflow_dispatch` skip both `compare-artifacts-*`
  jobs, because `merge_commit_sha` is only defined on PR events).
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

Three file-level changes:

1. **New file `.github/actions/setup-nix/action.yml`** — a composite
   action that bundles the per-job setup currently duplicated across
   `format` and `build-the-world`, plus the new `/nix/store` cache for
   the new jobs.

1. **Modified `.github/workflows/check.yml`** — three existing jobs
   migrate to use the composite action; two new jobs
   (`compare-artifacts-build` and `compare-artifacts-comment`) are
   added; a workflow-level `concurrency` block cancels in-flight runs
   when a PR receives a new push.

1. **New file `.github/dependabot.yml`** — keeps action versions
   (including the SHA-pinned third-party ones) current via weekly PRs.

Job graph (simplified):

```
format ────────────────────────────────────── (success)
build-the-world ─┬──────────────────────────── (success)
                 └─→ compare-artifacts-build ─┬── (success on PR; skipped
                                              │   on push/dispatch)
                                              └─→ compare-artifacts-comment
                                                  (success on same-repo
                                                   PR; skipped on fork)
branding-guide-changelog ─────────────────── (success)
```

`format` and `branding-guide-changelog` run independently of
`build-the-world`. The `compare-artifacts-*` jobs run only on
`pull_request` events and only after `build-the-world` succeeds. On
non-PR events both `compare-artifacts-*` jobs appear in the run graph
but show as "skipped" (GitHub does not omit conditionally-skipped jobs
from the graph).

### Two-job split rationale

Splitting build from comment is a security boundary, not just
organization. The `compare-artifacts-build` job calls
`nix run .#...compare-artifacts -- ...` which executes arbitrary
author-controlled Nix expressions, Python (`nixoslogo`), and shell
inside the runner. For PRs from a fork, the workflow token is read-only
and there is no escalation risk. For PRs from a branch in the *same*
repo (a maintainer's working branch), the workflow token can in
principle carry `pull-requests: write`; if that token is in the
environment while untrusted code runs, a compromised branch could
exfiltrate it.

To eliminate that risk:

- `compare-artifacts-build` declares `permissions: contents: read` only.
  It cannot post comments. Its only outputs are the uploaded artifacts
  and a few step outputs that the next job reads.
- `compare-artifacts-comment` declares `permissions: pull-requests: write`. It runs no `nix` code, no user-controlled scripts; it only
  downloads the summary artifact, validates the JSON shape, and posts
  the sticky comment.

The two jobs communicate exclusively via:

- `outputs:` on the build job (passing `before`, `after`, and the
  artifact's URL).
- A separate `comparison_summary` uploaded artifact that the comment
  job downloads.

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

    - uses: cachix/install-nix-action@<commit-sha>          # SHA-pin: resolve to v31 tip
    - uses: nix-community/cache-nix-action@<commit-sha>     # SHA-pin: resolve to v6 tip
      with:
        primary-key: nix-${{ runner.os }}-${{ hashFiles('flake.lock') }}
        restore-prefixes-first-match: nix-${{ runner.os }}-
        gc-max-store-size-linux: 5G
        purge: true
```

Notes:

- `fetch-depth` is exposed as an input because `format` and
  `build-the-world` work with the default shallow clone, but
  `compare-artifacts-build` needs full history to resolve `base.sha`
  and the merge commit via `git worktree add --detach <ref>`.
- The `/nix/store` cache benefits all Nix-using jobs (`format`,
  `build-the-world`, `compare-artifacts-build`). Cache key includes
  the OS and the hash of `flake.lock` so a dependency update
  invalidates stale cache hits.
- `gc-max-store-size-linux: 5G` caps the saved cache size; GitHub
  enforces a 10 GB per-repo cache limit.
- `purge: true` removes older caches sharing the same key prefix so
  cache usage stays within budget.

### The workflow: `.github/workflows/check.yml`

Third-party actions are SHA-pinned (`@<commit-sha>`) rather than tag-pinned;
the implementer must resolve the SHAs against the upstream repo's
referenced tag before merging. Dependabot keeps them current. First-party
`actions/*` references stay on major tags (lower supply-chain surface;
GitHub guarantees the tag).

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
  # Includes event_name so workflow_call invocations from external
  # workflows don't share a concurrency group with PR or push runs on
  # the same ref.
  group: check-${{ github.workflow }}-${{ github.event_name }}-${{ github.event.pull_request.number || github.ref }}
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

  compare-artifacts-build:
    runs-on: ubuntu-latest
    needs: build-the-world
    if: github.event_name == 'pull_request'
    # No `pull-requests: write` here. Token theft from compromised
    # author-controlled code (run via `nix run` below) yields a
    # read-only token incapable of posting comments.
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

          # `fetch-depth: 0` already pulled base + all reachable refs.
          # Only the merge commit needs an explicit fetch because it
          # lives at `refs/pull/<N>/merge` and isn't on any branch.
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

      - uses: marocchino/sticky-pull-request-comment@<commit-sha>   # SHA-pin: resolve to v2 tip; Dependabot updates
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

  branding-guide-changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Get latest or unreleased info
        id: query-release-info
        uses: release-flow/keep-a-changelog-action@<commit-sha>   # SHA-pin: resolve to v2 tip; Dependabot updates
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

### The Dependabot config: `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    # Dependabot keeps both tag-pinned and SHA-pinned action references
    # current. PRs from Dependabot follow normal review.
```

### Key behaviors

- **`needs: build-the-world`** enforces the chain. If the world doesn't
  build, the comparison jobs are skipped and the PR doesn't get a stale
  comparison.
- **`if: github.event_name == 'pull_request'`** keeps
  `compare-artifacts-build` out of pushes to `main` and manual
  triggers — `merge_commit_sha` only exists on PR events. The comment
  job depends on the build job, so it's transitively skipped too.
- **Job-scoped `permissions:`** (not workflow-scoped). Each job
  declares the minimum it needs:
  `compare-artifacts-build` gets `contents: read` only;
  `compare-artifacts-comment` gets `pull-requests: write` only.
  Workflow-scoped `permissions: read-all` is the baseline for the
  other jobs. Note: job-scope `permissions:` **replaces** the
  workflow-scope baseline (it does not merge), so each job's block
  must list every scope it needs.
- **Comment job `if:` guard** skips on fork PRs rather than letting
  the sticky-comment step fail. The artifact uploaded by
  `compare-artifacts-build` is still available; fork contributors find
  it via the Actions run page.
- **Concurrency group** keys on `event_name`, the PR number, and the
  ref so multiple rapid pushes to a PR cancel earlier runs, while
  `workflow_call` invocations from different callers don't accidentally
  cancel each other on shared refs.
- **`set -euo pipefail` in all multi-line bash steps** — without it, a
  failing command in a pipeline or a missing file can silently produce
  empty output that gets interpolated into the comment, yielding a
  garbage but green-status PR comment.
- **`jq -e` type validation** in the comment job — before interpolating
  any summary value into the markdown body, all four count fields are
  checked to be numbers. This blocks markdown-injection attacks via
  fork-controllable JSON values.

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
- **`merge_commit_sha` async race.** GitHub computes the merge commit
  asynchronously after a `synchronize` event. There's a short window
  where the workflow fires with an outdated `merge_commit_sha` (the
  previous push's merge) — non-empty but stale. The workflow has no
  way to distinguish this from a current value; the comparison runs
  against the stale merge. In practice, `cancel-in-progress: true`
  superseded runs cover most of these, but a quiet PR that updates
  once may still get one stale report. If this becomes a recurring
  problem, the fix is to poll `pulls/{N}` until
  `mergeable_state != "unknown"` before running compare-artifacts.
  Not implemented in the first iteration.
- **Build failures (infrastructure, not diff content).** If
  `compare-artifacts` (or the underlying `nix build`) fails on either
  ref, the `compare-artifacts-build` step fails. Subsequent steps
  (artifact upload, comment job) don't run. The job shows red on the
  PR; the failure cause is in the run log. This is the "infrastructure
  error" path called out in the Goals section: it DOES fail the check.
  Note that `build-the-world` already gates this job, so the common
  case (main doesn't build) is prevented; failures here usually mean
  the PR's merge commit fails to build, which is genuinely a problem
  worth surfacing.
- **Stale sticky comment after a failed run.** Because the comment
  job is skipped when the build job fails, a previous successful
  run's sticky comment remains attached to the PR. On a subsequent
  successful run, the comment is updated in place (header-dedupe).
  Between a failed run and the next successful run, the sticky
  comment is out of date. Documented but not auto-resolved; if a
  reviewer needs current data they re-trigger the workflow.
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
1. **Exercise four scenarios on the draft PR:**
   - A push that touches no artifact-affecting code → report shows
     all zeros for changed/added/removed; sticky comment posts on the
     same-repo PR.
   - A push that intentionally modifies artifacts (e.g., a small
     `nixoslogo` tweak) → non-zero counts; the comment matches.
   - A push from a fork (synthesize via a second account if practical;
     otherwise document the limitation and accept it) → artifact still
     uploads from `compare-artifacts-build`; `compare-artifacts-comment`
     is skipped via the `if:` guard.
   - A deliberately bad `--summary` JSON (manually set up a test case
     where the build emits a string instead of integer counts, e.g.
     by patching the tool locally on a test branch) → the
     "Validate and extract summary" step exits non-zero; the comment
     job fails red rather than posting an injected comment.
1. **Confirm the existing `format` and `build-the-world` jobs still
   pass** after they're switched to the composite action.
1. **Resolve `<commit-sha>` placeholders for the SHA-pinned actions**
   before merging the implementation PR. Each placeholder is on a
   line marked `# SHA-pin: resolve to <version> tip`; the implementer
   replaces each with the current head SHA of the referenced tag. The
   Dependabot config will keep them current after merge.

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
- **Cache thrash on interleaved `flake.lock` PRs.** Two PRs that each
  bump `flake.lock` differently produce different primary keys; with
  `purge: true`, whichever finishes last evicts the other's saved
  cache. Hit rate oscillates between the two until one merges.
  Acceptable: the cost is at most one cold rebuild per affected
  branch. Mitigation if it becomes painful: tighten `purge` semantics
  to only purge older entries with the *same* primary key.
- **Sticky comment churn on chatty PRs.** The header dedupes
  comments so we never spam; updates overwrite the previous comment in
  place.
- **The `--summary` JSON format becomes a contract.** Any future
  change to the JSON keys or value types could break the workflow.
  Mitigation: the JSON shape is documented in the `--summary` spec
  amendment as exactly four integer-valued keys; CI validates types
  via `jq -e` before use; adding new fields is OK, removing or
  renaming or retyping is not.
- **`actions/upload-artifact@v4`'s `artifact-url` output is on a
  comparatively new release of that action.** If GitHub changes the
  output name, the comment link breaks. Mitigation: pin to `@v4`
  rather than `@latest`; the output is stable across v4.x.
- **`permissions: read-all` workflow ceiling cascades to
  `workflow_call` callers.** Any external workflow that calls this
  one via `workflow_call:` inherits `read-all` as the maximum
  permission set — a tightening for current callers (none in this
  repo) but worth knowing if a future caller relies on broader
  permissions. The fix would be to grant the workflow more
  permissions and rely on the per-job `permissions:` blocks for
  scoping; we keep the tighter default until a real consumer needs
  otherwise.
- **Stale tags on third-party actions.** Tags are mutable; the
  `tj-actions/changed-files` 2025 incident demonstrated this attack
  in production. Mitigation: third-party actions
  (`marocchino/sticky-pull-request-comment`,
  `release-flow/keep-a-changelog-action`, `cachix/install-nix-action`,
  `nix-community/cache-nix-action`) are pinned to commit SHAs.
  Dependabot keeps them current via reviewed PRs. First-party
  `actions/*` references stay on major tags because GitHub guarantees
  the tag itself.
- **Local composite action visibility before checkout.** A composite
  action referenced as `uses: ./.github/actions/setup-nix` must exist
  in the working tree before its first invocation. GitHub's runner
  handles this by pre-fetching the action source before evaluating the
  first step — which happens to be the `actions/checkout` inside the
  composite action itself. The pattern is supported but non-obvious;
  document here so a future maintainer doesn't try to "fix" the
  apparent chicken-and-egg by moving the checkout out of the
  composite action.
