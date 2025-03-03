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

    logoDev = pkgs.mkShell {
      packages = [
        (pkgs.python3.withPackages (
          ps: with ps; [
            coloraide
            freetype-py
            svg-py
          ]
        ))
      ];
    };
  }
)
