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

    nixoslogo-dev = pkgs.callPackage (
      {
        mkShell,
        poetry,
        python3,
        route159,
      }:
      mkShell {

        packages = [
          poetry
          (python3.withPackages (ps: [
            ps.nixoslogo-editable
            ps.fontforge
          ]))
        ];

        shellHook = ''
          export NIXOSLOGO_SRC=$(git rev-parse --show-toplevel)/packages/python-packages/nixoslogo

          cp "${route159}/share/fonts/opentype/Route159-Regular.otf" $(git rev-parse --show-toplevel)
        '';

      }
    ) { };
  }
)
