"""Git worktree lifecycle.

The `Worktree` context manager creates a temporary detached-HEAD worktree
at `__enter__`, yields its path, and decides at `__exit__` whether to
remove it. The decision depends on what caused the `with`-block to exit
(see the spec's exit-time decision matrix):

  - Success or KeyboardInterrupt (SIGINT) → remove unless `--keep` is set.
  - Interrupted (SIGTERM / SIGHUP) → keep regardless of `--keep`.
  - Any other exception → keep regardless of `--keep`.

`Interrupted` inherits from `BaseException` so that `except Exception`
clauses (including those inside `ThreadPoolExecutor` worker threads)
don't swallow it.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from types import TracebackType


class Interrupted(BaseException):
    """Raised by signal handlers for SIGTERM / SIGHUP."""


class Worktree:
    """Create a temporary detached-HEAD worktree at `ref`."""

    def __init__(self, ref: str, *, keep: bool = False) -> None:
        self._ref = ref
        self._keep = keep
        self._path: Path | None = None

    def __enter__(self) -> Path:
        tmp = tempfile.mkdtemp(prefix="compare-artifacts-")
        try:
            subprocess.run(
                ["git", "worktree", "add", "--detach", tmp, self._ref],
                check=True,
            )
        except BaseException:
            # `git worktree add` failed or was interrupted; clean up the
            # empty tmp dir before re-raising.
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        self._path = Path(tmp)
        return self._path

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if self._path is None:
            # `__enter__` failed; nothing to clean.
            return False

        path = self._path

        # Clean-up branch: success OR SIGINT (KeyboardInterrupt). Both
        # are "normal" exits; nothing is still writing to the worktree.
        is_clean_exit = exc_type is None or issubclass(exc_type, KeyboardInterrupt)

        if is_clean_exit and not self._keep:
            try:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(path)],
                    check=True,
                )
            except subprocess.CalledProcessError:
                # A cleanup hiccup never masks the original exit cause.
                print(f"worktree kept at {path} (cleanup failed)")
        else:
            # `--keep`, SIGTERM/SIGHUP, or any other exception → keep.
            print(f"worktree kept at {path}")

        return False  # never swallow the exception
