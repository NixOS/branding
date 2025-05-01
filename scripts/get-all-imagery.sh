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

# external

IMAGERY=(
  "nixos-logomark-default-flat-recommended"
  "nixos-logomark-default-gradient-recommended"
  "nixos-logomark-rainbow-gradient-recommended"
  "nixos-logotype-black-coloredx-recommended"
  "nixos-logotype-black-regular-recommended"
)

for IMAGE in "${IMAGERY[@]}"; do
  python ../packages/external-artifacts/"$IMAGE"/script.py
done

for IMAGE in "${IMAGERY[@]}"; do
  nix build ..#"${IMAGE}" --option warn-dirty false
  nix build ..#"${IMAGE}" --option warn-dirty false --rebuild
  if cmp -s "${IMAGE}.svg" "./result/${IMAGE}.svg"; then
    echo "SAME ${IMAGE}"
  else
    echo "NOT SAME ${IMAGE}"
  fi
done

# internal

IMAGERY=(
  "nixos-lambda-dimensioned-angular"
  "nixos-lambda-dimensioned-linear"
  "nixos-lambda-gradient-background"
  "nixos-lambda-gradient-dimensioned"
  "nixos-logotype-black-dimensioned"
  "nixos-snowflake-dimensioned-linear"
)

for IMAGE in "${IMAGERY[@]}"; do
  python ../packages/internal-artifacts/"$IMAGE"/script.py
done

for IMAGE in "${IMAGERY[@]}"; do
  nix build ..#"${IMAGE}" --option warn-dirty false
  nix build ..#"${IMAGE}" --option warn-dirty false --rebuild
  if cmp -s "${IMAGE}.svg" "./result/${IMAGE}.svg"; then
    echo "SAME ${IMAGE}"
  else
    echo "NOT SAME ${IMAGE}"
  fi
done
