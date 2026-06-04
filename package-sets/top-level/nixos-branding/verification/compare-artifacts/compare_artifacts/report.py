"""HTML report rendering.

`render_report` produces a self-contained HTML document with:

  - A sticky sidebar grouped by top-level subdirectory, with color-coded
    state badges (A/M/D).
  - A summary header in the main area showing counts and ref / attr
    metadata.
  - One `<section>` per non-unchanged file, containing
    `difflib.HtmlDiff().make_table(...)` output.

CSS is embedded; the report has no external assets.
"""

import difflib
import html
from collections import defaultdict

from compare_artifacts.collect import DiffSpec, counts


STYLES = """
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    align-items: flex-start;
}
aside.sidebar {
    width: 280px;
    flex-shrink: 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid #ddd;
    padding: 1em;
    box-sizing: border-box;
    font-size: 0.9em;
    background: #fafafa;
}
aside.sidebar h3 {
    margin: 1em 0 0.3em;
    font-size: 0.95em;
    color: #333;
}
aside.sidebar ul {
    list-style: none;
    padding: 0;
    margin: 0;
}
aside.sidebar li {
    padding: 0.15em 0;
}
aside.sidebar a {
    text-decoration: none;
    color: #0366d6;
}
aside.sidebar .sidebar-summary {
    padding: 0.5em 0;
    border-bottom: 1px solid #ddd;
    font-weight: 600;
}
.count {
    color: #888;
    font-weight: normal;
}
.badge {
    display: inline-block;
    width: 1.2em;
    text-align: center;
    font-weight: 700;
    border-radius: 3px;
    margin-right: 0.4em;
    font-size: 0.85em;
    color: white;
}
.badge-A { background: #28a745; }
.badge-M { background: #f0a500; }
.badge-D { background: #d73a49; }
main {
    flex-grow: 1;
    padding: 1em 2em;
    overflow-x: auto;
}
header.summary {
    margin-bottom: 2em;
    padding-bottom: 1em;
    border-bottom: 1px solid #ddd;
}
section {
    margin-bottom: 2em;
}
section h2 {
    font-family: Menlo, Consolas, monospace;
    font-size: 1.1em;
}
table.diff {
    font-family: Menlo, Consolas, Monaco, Liberation Mono, Lucida Console, monospace;
    border: medium;
    width: 100%;
}
.diff_header { background-color: #e0e0e0; }
td.diff_header { text-align: right; }
.diff_next { background-color: #c0c0c0; }
.diff_add { background-color: #aaffaa; }
.diff_chg { background-color: #ffff77; }
.diff_sub { background-color: #ffaaaa; }

/* Dark-mode toggle (CSS-only): the checkbox is hidden; the label is
   the visible button. `body:has(.dark-toggle:checked)` flips colors. */
input.dark-toggle {
    position: absolute;
    opacity: 0;
    pointer-events: none;
}
label.dark-button {
    display: inline-block;
    cursor: pointer;
    padding: 0.3em 0.6em;
    margin-top: 0.5em;
    background: #eee;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.85em;
    user-select: none;
}
label.dark-button:hover { background: #ddd; }
label.dark-button::before { content: "Dark mode"; }
body:has(.dark-toggle:checked) label.dark-button::before {
    content: "Light mode";
}

/* Dark theme — only applied when the checkbox is checked. */
body:has(.dark-toggle:checked) {
    background: #1a1a1a;
    color: #e0e0e0;
}
body:has(.dark-toggle:checked) aside.sidebar {
    background: #222;
    border-right-color: #444;
}
body:has(.dark-toggle:checked) aside.sidebar h3 { color: #ddd; }
body:has(.dark-toggle:checked) aside.sidebar a { color: #58a6ff; }
body:has(.dark-toggle:checked) aside.sidebar .sidebar-summary {
    border-bottom-color: #444;
}
body:has(.dark-toggle:checked) label.dark-button {
    background: #333;
    border-color: #555;
    color: #e0e0e0;
}
body:has(.dark-toggle:checked) label.dark-button:hover { background: #444; }
body:has(.dark-toggle:checked) header.summary {
    border-bottom-color: #444;
}
body:has(.dark-toggle:checked) code {
    background: #333;
    padding: 0.1em 0.3em;
    border-radius: 2px;
}
body:has(.dark-toggle:checked) .diff_header {
    background-color: #2a2a2a;
    color: #c0c0c0;
}
body:has(.dark-toggle:checked) .diff_next {
    background-color: #333;
    color: #ddd;
}
body:has(.dark-toggle:checked) .diff_add {
    background-color: #1f4f1f;
    color: #aaffaa;
}
body:has(.dark-toggle:checked) .diff_chg {
    background-color: #4f4f1f;
    color: #ffff77;
}
body:has(.dark-toggle:checked) .diff_sub {
    background-color: #4f1f1f;
    color: #ffaaaa;
}
"""


_STATE_TO_BADGE = {
    "added": "A",
    "changed": "M",
    "removed": "D",
}


def _visible(specs: list[DiffSpec]) -> list[DiffSpec]:
    return [s for s in specs if s.state != "unchanged"]


def render_summary(specs: list[DiffSpec], ref_a: str, ref_b: str, attr: str) -> str:
    counts_ = counts(specs)
    return (
        '<header class="summary">'
        f"<p><strong>{counts_['changed']} changed</strong> · "
        f"{counts_['added']} added · "
        f"{counts_['removed']} removed · "
        f"{counts_['unchanged']} unchanged (hidden)</p>"
        f"<p>ref-a: <code>{html.escape(ref_a)}</code> &nbsp; "
        f"ref-b: <code>{html.escape(ref_b)}</code></p>"
        f"<p>attr: <code>{html.escape(attr)}</code></p>"
        "</header>"
    )


def _group_by_subdir(visible: list[DiffSpec]) -> dict[str, list[tuple[int, DiffSpec]]]:
    """Group visible specs by their top-level subdirectory, preserving order.

    Each (index, spec) tuple carries the spec's position in the visible
    list — used as the section ID (`diff-N`).
    """
    groups: dict[str, list[tuple[int, DiffSpec]]] = defaultdict(list)
    for index, spec in enumerate(visible):
        parts = spec.path.parts
        # If the file sits at the root (no subdir), group it under "(root)".
        subdir = parts[0] if len(parts) > 1 else "(root)"
        groups[subdir].append((index, spec))
    return groups


def render_sidebar(specs: list[DiffSpec]) -> str:
    counts_ = counts(specs)
    visible = _visible(specs)
    groups = _group_by_subdir(visible)

    out = ['<aside class="sidebar">']
    out.append(
        '<section class="sidebar-summary">'
        f"{counts_['changed']} changed · "
        f"{counts_['added']} added · "
        f"{counts_['removed']} removed · "
        f"{counts_['unchanged']} unchanged"
        '<br /><label for="dark-toggle" class="dark-button"></label>'
        "</section>"
    )
    out.append("<nav>")
    for subdir, entries in groups.items():
        out.append(
            f"<h3>{html.escape(subdir)} "
            f'<span class="count">({len(entries)})</span></h3>'
        )
        out.append("<ul>")
        for index, spec in entries:
            badge = _STATE_TO_BADGE[spec.state]
            # Show the path relative to the subdir for less visual noise.
            label = (
                spec.path.name
                if subdir == "(root)"
                else str(spec.path.relative_to(subdir))
            )
            out.append(
                f'<li><a href="#diff-{index}">'
                f'<span class="badge badge-{badge}">{badge}</span>'
                f"{html.escape(label)}</a></li>"
            )
        out.append("</ul>")
    out.append("</nav>")
    out.append("</aside>")
    return "".join(out)


def render_diff_section(
    index: int,
    spec: DiffSpec,
    *,
    context: int,
    full: bool,
    ref_a: str,
    ref_b: str,
) -> str:
    badge = _STATE_TO_BADGE[spec.state]
    table = difflib.HtmlDiff().make_table(
        spec.before,
        spec.after,
        fromdesc=f"{spec.path} ({ref_a})",
        todesc=f"{spec.path} ({ref_b})",
        context=not full,
        numlines=context,
    )
    return (
        f'<section id="diff-{index}">'
        f"<h2>{html.escape(str(spec.path))} "
        f'<span class="badge badge-{badge}">{spec.state}</span></h2>'
        f"{table}"
        "</section>"
    )


def render_report(
    specs: list[DiffSpec],
    *,
    context: int,
    full: bool,
    ref_a: str,
    ref_b: str,
    attr: str,
) -> str:
    visible = _visible(specs)
    sections = "".join(
        render_diff_section(
            index,
            spec,
            context=context,
            full=full,
            ref_a=ref_a,
            ref_b=ref_b,
        )
        for index, spec in enumerate(visible)
    )
    sidebar = render_sidebar(specs)
    summary = render_summary(specs, ref_a, ref_b, attr)
    title = f"compare-artifacts: {html.escape(ref_a)} ↔ {html.escape(ref_b)}"
    return (
        "<!DOCTYPE html><html><head>"
        '<meta charset="utf-8" />'
        f"<title>{title}</title>"
        f"<style>{STYLES}</style>"
        "</head><body>"
        # The hidden checkbox is the dark-mode state holder. Its `id`
        # matches the `for=` on the visible label inside the sidebar.
        '<input type="checkbox" id="dark-toggle" class="dark-toggle" />'
        f"{sidebar}"
        "<main>"
        f"{summary}"
        f"{sections}"
        "</main>"
        "</body></html>"
    )
