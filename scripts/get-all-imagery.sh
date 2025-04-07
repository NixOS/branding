#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

python ../packages/nixos-lambda-dimensioned-angular/script.py
python ../packages/nixos-lambda-dimensioned-linear/script.py
python ../packages/nixos-lambda-gradient-background/script.py
python ../packages/nixos-lambda-gradient-dimensioned/script.py
python ../packages/nixos-snowflake-color-flat/script.py
python ../packages/nixos-snowflake-color-gradient/script.py
python ../packages/nixos-snowflake-dimensioned-linear/script.py
python ../packages/nixos-snowflake-rainbow-gradient/script.py
