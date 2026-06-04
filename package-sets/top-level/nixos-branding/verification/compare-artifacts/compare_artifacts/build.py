"""Parallel `nix build` invocation.

`build_attr` runs `nix build --no-link --print-out-paths .#<attr>` in a
given worktree and captures the printed store path. `build_pair` runs
two `build_attr` calls concurrently via `ThreadPoolExecutor`.

stdout is piped (to capture the store path); stderr is inherited (so
nix's progress output streams to the user's terminal). Two concurrent
builds means stderr from both interleaves — functional, visually messy.
"""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def build_attr(worktree_path: Path, attr: str) -> Path:
    """Run `nix build` for `attr` inside `worktree_path` and return the store path."""
    result = subprocess.run(
        ["nix", "build", "--no-link", "--print-out-paths", f".#{attr}"],
        cwd=worktree_path,
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def build_pair(wt_a: Path, wt_b: Path, attr: str) -> tuple[Path, Path]:
    """Build `attr` on both worktrees concurrently. Returns (path_a, path_b)."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_a = pool.submit(build_attr, wt_a, attr)
        fut_b = pool.submit(build_attr, wt_b, attr)
        return fut_a.result(), fut_b.result()
