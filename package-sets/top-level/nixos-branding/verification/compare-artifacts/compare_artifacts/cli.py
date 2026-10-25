"""compare-artifacts CLI entry point.

Wires together worktree creation, parallel nix builds, file collection,
and HTML rendering. Installs SIGTERM/SIGHUP handlers that raise the
`Interrupted` exception so the worktree context managers can react.
"""

import argparse
import json
import signal
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

from compare_artifacts.build import build_pair
from compare_artifacts.collect import collect_files, counts
from compare_artifacts.numeric import compare_numeric
from compare_artifacts.raster import compare_raster, render
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
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="If set, write a JSON file at this path with the counts "
        "(modified/added/deleted/unchanged). The HTML output is "
        "unchanged whether or not this flag is passed.",
    )
    parser.add_argument(
        "--numeric",
        action="store_true",
        help="For each modified file, align number-masked lines and report "
        "the maximum numeric delta over aligned lines plus the count of "
        "unaligned lines. Written under 'numeric' in the summary JSON.",
    )
    parser.add_argument(
        "--raster",
        action="store_true",
        help="For each modified file, render both versions with resvg at "
        "1024 px wide and report differing pixels. Written under 'raster' "
        "in the summary JSON.",
    )
    diff_mode = parser.add_mutually_exclusive_group()
    diff_mode.add_argument(
        "--full",
        action="store_true",
        help="Show full file diffs (no context trimming). WARNING: "
        "combined with the show-all default (no --hide-unchanged), "
        "the rendered HTML can grow to many MB for repos with "
        "hundreds of large artifacts. Local dev use only; the CI "
        "workflow does not pass --full.",
    )
    diff_mode.add_argument(
        "--context",
        type=_non_negative_int,
        default=3,
        help="Lines of unchanged context around changes (default: 3).",
    )
    parser.add_argument(
        "--hide-unchanged",
        action="store_true",
        help="Exclude unchanged files from the sidebar and body. "
        "Summary counts include them but the report is otherwise "
        "terse. Default: unchanged files are shown.",
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
                hide_unchanged=args.hide_unchanged,
            )
            args.output.write_text(html_out)
            summary: dict[str, object] = dict(counts(specs))
            modified = [spec for spec in specs if spec.state == "modified"]
            if args.numeric:
                numeric = {
                    str(spec.path): asdict(compare_numeric(spec.before, spec.after))
                    for spec in modified
                }
                summary["numeric"] = numeric
                for path, result in numeric.items():
                    print(
                        f"numeric {path}: matched={result['matched']} "
                        f"unmatched={result['unmatched_before']}/{result['unmatched_after']} "
                        f"changed={result['changed']}/{result['compared']} "
                        f"max_delta={result['max_delta']:.6g}"
                    )
            if args.raster:
                raster: dict[str, dict[str, object]] = {}
                with tempfile.TemporaryDirectory() as tmp:
                    for index, spec in enumerate(modified):
                        png_a = Path(tmp) / f"{index}-a.png"
                        png_b = Path(tmp) / f"{index}-b.png"
                        render(path_a / spec.path, png_a)
                        render(path_b / spec.path, png_b)
                        raster[str(spec.path)] = asdict(compare_raster(png_a, png_b))
                summary["raster"] = raster
                for path, result in raster.items():
                    print(
                        f"raster {path}: differing_pixels={result['differing_pixels']} "
                        f"max_channel_delta={result['max_channel_delta']}"
                    )
            if args.summary is not None:
                args.summary.write_text(json.dumps(summary))
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
