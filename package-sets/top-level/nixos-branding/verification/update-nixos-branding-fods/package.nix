{
  gnugrep,
  gnused,
  jq,
  nix,
  nix-eval-jobs,
  nix-output-monitor,
  stdenv,
  writeShellApplication,
}:
writeShellApplication {

  name = "verify-nixos-branding";

  runtimeInputs = [
    gnugrep
    gnused
    jq
    nix
    nix-eval-jobs
    nix-output-monitor
  ];

  bashOptions = [
    "nounset"
    "pipefail"
  ];

  text = ''
    nix-eval-jobs \
      --flake .#hydraJobs.nixos-branding-artifacts-media-kit.${stdenv.hostPlatform.system} \
      --constituents \
      | \
      jq \
      -cr \
      '.constituents + [.drvPath] | .[] | select(.!=null) + "^*"' \
      | \
      nix \
      build \
      --keep-going \
      --no-link \
      --print-out-paths \
      --stdin \
      --rebuild \
      2>error.log

    if [[ -s error.log ]]; then
      echo "Error log is found not empty."
      specified=""
      while IFS= read -r line; do
        # Match specified line
        if [[ "$line" =~ specified:[[:space:]]*(sha256-[a-zA-Z0-9+/=]+) ]]; then
          specified="''${BASH_REMATCH[1]}"
          continue
        fi

        # Match got line, only if a specified value was just seen
        if [[ -n "$specified" && "$line" =~ got:[[:space:]]*(sha256-[a-zA-Z0-9+/=]+) ]]; then
          got="''${BASH_REMATCH[1]}"

          # Search and replace
          file=$(grep -rl "$specified" --exclude=error.log .)
          if [[ -n "$file" ]]; then
            echo "Replacing $specified with $got in:"
            echo "$file"
            sed -i "s|$specified|$got|g" "$file"
          else
            echo "No file found containing: $specified"
          fi

          # Reset for next pair
          specified=""
        fi
      done <error.log
    fi
  '';

}
