#!/usr/bin/env bash

# Pretty-print an SVG into a diff-friendly TEXT view (to STDOUT)
# Usage: svg_pretty path/to/file.svg [path/to/svg-diff-view.xsl] [indent]
svg_pretty() {
  local in="$1"
  local xsl="${2:-svg-diff-view.xsl}"
  local indent="${3:-2}"
  local real
  real="$(realpath -e "$in")" || {
    echo "not found: $in" >&2
    return 1
  }

  xsltproc --stringparam indent "$indent" \
    "$xsl" \
    <(xmlstarlet c14n "$real")
}

# Side-by-side diff of two SVGs using your svg_pretty (no temp files)
# Usage: svg_diff a.svg b.svg [xsl_path] [indent]
svg_diff() {
  local a="$1" b="$2"
  local xsl="${3:-svg-diff-view.xsl}"
  local indent="${4:-2}"

  local left
  local right
  left="$(mktemp "/tmp/left.XXXX.svg")"
  right="$(mktemp "/tmp/right.XXXX.svg")"

  svg_pretty "$a" "$xsl" "$indent" >"$left"
  svg_pretty "$b" "$xsl" "$indent" >"$right"

  git --no-pager \
    diff \
    --no-index \
    --no-ext-diff \
    --color=always \
    --unified=999999 \
    --diff-algorithm=histogram \
    --minimal \
    "$left" "$right" |
    delta \
      --side-by-side \
      --paging=never \
      --file-modified-label "modified: $(basename -- "$a") --->"
}

# Example direct call (uncomment to use like a script):
# svg_pretty "$1"  # or: svg_diff "$1" "$2"
# svg_pretty "$1"
svg_diff "$1" "$2"
