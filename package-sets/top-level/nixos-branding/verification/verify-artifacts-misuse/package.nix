{
  jq,
  nix,
  nix-eval-jobs,
  nix-output-monitor,
  stdenv,
  writeShellApplication,
}:
writeShellApplication {

  name = "verify-artifacts-misuse";

  runtimeInputs = [
    jq
    nix
    nix-eval-jobs
    nix-output-monitor
  ];

  text = ''
    nix-eval-jobs \
      --flake .#hydraJobs.nixos-branding-artifacts-misuse.${stdenv.hostPlatform.system} \
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
