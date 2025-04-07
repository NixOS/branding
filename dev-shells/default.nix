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
        pkgs.poetry
        (pkgs.python3.withPackages (
          ps: with ps; [
            coloraide
            fontforge
            freetype-py
            jsonpickle
            svg-py
          ]
        ))
      ];
    };

    nixoslogo-dev = pkgs.mkShell {
      packages = [ (pkgs.python3.withPackages (ps: [ ps.nixoslogo-editable ])) ];
      shellHook = ''
        export NIXOSLOGO_SRC=$(git rev-parse --show-toplevel)/packages/python-packages/nixoslogo
      '';
    };
  }
)
