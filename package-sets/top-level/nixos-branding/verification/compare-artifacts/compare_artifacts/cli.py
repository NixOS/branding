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
