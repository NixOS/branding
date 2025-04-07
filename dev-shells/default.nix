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

    nixoslogo-dev =
      let
        myPython = pkgs.python3.override {
          self = myPython;
          packageOverrides = pyfinal: pyprev: {
            nixoslogo-editable = pyfinal.callPackage ../packages/python-packages/nixoslogo/editable.nix { };
          };
        };

        pythonEnv = myPython.withPackages (ps: [ ps.nixoslogo-editable ]);
      in
      pkgs.mkShell {
        packages = [ pythonEnv ];
        shellHook = ''
          export NIXOSLOGO_SRC=$PWD/packages/python-packages/nixoslogo
        '';
      };
  }
)
