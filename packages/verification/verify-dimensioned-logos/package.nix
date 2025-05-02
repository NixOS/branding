{
  nix-eval-jobs,
  stdenv,
  writeShellApplication,
}:
writeShellApplication {

  name = "verify-dimensioned-logos";

  runtimeInputs = [
    nix-eval-jobs
  ];

  text = ''
    nix-eval-jobs \
      --flake .#hydraJobs.dimensioned-logos.${stdenv.hostPlatform.system} \
      --constituents \
      | \
      jq \
      -cr \
      '.constituents + [.drvPath] | .[] | select(.!=null) + "^*"' \
      | \
      nom \
      build \
      --keep-going \
      --no-link \
      --print-out-paths \
      --stdin \
      "$@"
  '';

}
