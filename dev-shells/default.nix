inputs:
inputs.self.library.defaultSystems (
  system:
  let
    pkgs = inputs.self.legacyPackages.${system};
  in
  {
    default = pkgs.mkShell {
      packages = [ ] ++ inputs.self.checks.${system}.pre-commit-check.enabledPackages;

      inherit (inputs.self.checks.${system}.pre-commit-check) shellHook;
    };
  }
)
