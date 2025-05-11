{
  jq,
  nix,
  nix-eval-jobs,
  nix-output-monitor,
  stdenv,
  writeShellApplication,
}:
writeShellApplication {

  name = "verify-artifacts-media-kit";

  runtimeInputs = [
    jq
    nix
    nix-eval-jobs
    nix-output-monitor
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
      nom \
      build \
      --keep-going \
      --no-link \
      --print-out-paths \
      --stdin \
      "$@"
  '';

}
