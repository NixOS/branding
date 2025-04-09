#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo 'No Python available. Try using the logo devShell.'
  exit 1
fi

if ! python -c "import nixoslogo"; then
  echo 'Python package "nixoslogo" not found. Try using the logo devShell.'
  exit 1
fi

IMAGERY=(
  "nixos-lambda-dimensioned-angular"
  "nixos-lambda-dimensioned-linear"
  "nixos-lambda-gradient-background"
  "nixos-lambda-gradient-dimensioned"
  "nixos-snowflake-color-flat"
  "nixos-snowflake-color-gradient"
  "nixos-snowflake-dimensioned-linear"
  "nixos-snowflake-rainbow-gradient"
)

for IMAGE in "${IMAGERY[@]}"; do
  python ../packages/"$IMAGE"/script.py
done

nix build .#all-developed-imagery

for IMAGE in "${IMAGERY[@]}"; do
  if cmp -s "${IMAGE}.svg" "./result/${IMAGE}.svg"; then
    echo "SAME ${IMAGE}"
  else
    echo "NOT SAME ${IMAGE}"
  fi
done
