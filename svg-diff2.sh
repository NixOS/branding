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

  if command -v delta >/dev/null 2>&1; then
    git --no-pager diff --no-index --no-ext-diff --color=always \
      -U999999 \
      --diff-algorithm=histogram --minimal \
      <(svg_pretty "$a" "$xsl" "$indent") \
      <(svg_pretty "$b" "$xsl" "$indent") |
      delta --side-by-side --paging=never
  else
    git --no-pager diff --no-index --no-ext-diff --color=always \
      -U999999 \
      --diff-algorithm=histogram --minimal \
      <(svg_pretty "$a" "$xsl" "$indent") \
      <(svg_pretty "$b" "$xsl" "$indent")
  fi

  # diff -u \
  #   <(svg_pretty "$a" "$xsl" "$indent") \
  #   <(svg_pretty "$b" "$xsl" "$indent") |
  #   delta --paging=never --side-by-side
}

# Example direct call (uncomment to use like a script):
# svg_pretty "$1"  # or: svg_diff "$1" "$2"
# svg_pretty "$1"
svg_diff "$1" "$2"
