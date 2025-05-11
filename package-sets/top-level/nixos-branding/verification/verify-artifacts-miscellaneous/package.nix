{
  jq,
  nix,
  nix-eval-jobs,
  nix-output-monitor,
  stdenv,
  writeShellApplication,
}:
writeShellApplication {

  name = "verify-artifacts-miscellaneous";

  runtimeInputs = [
    jq
    nix
    nix-eval-jobs
    nix-output-monitor
  ];

  text = ''
    nix-eval-jobs \
      --flake .#hydraJobs.nixos-branding-artifacts-miscellaneous.${stdenv.hostPlatform.system} \
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
