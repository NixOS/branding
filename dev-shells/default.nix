inputs:
inputs.self.library.defaultSystems (
  system:
  let
    pkgs = inputs.self.legacyPackages.${system};
  in
  {

    nixos-logo-dev = pkgs.callPackage (
      {
        jura,
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

        buildInputs = [

          inputs.self.checks.${system}.pre-commit-check.enabledPackages

        ];

        shellHook =
          ''
            export NIXOSLOGO_SRC=$(git rev-parse --show-toplevel)/package-sets/python-packages/nixoslogo
            export NIXOS_LOGOTYPE_FONT_FILE="${route159}/share/fonts/opentype/route159/Route159-Regular.otf"
            export NIXOS_ANNOTATIONS_FONT_FILE="${jura}/share/fonts/truetype/jura/Jura-Regular.ttf"
          ''
          + inputs.self.checks.${system}.pre-commit-check.shellHook;

      }
    ) { };

    nixos-branding-guide-dev = pkgs.nixos-branding.callPackage (
      {
        mkShell,
        nixos-branding-guide-editable,
      }:
      mkShell {

        shellHook = ''
          cd $(git rev-parse --show-toplevel)/package-sets/top-level/nixos-branding/nixos-branding-guide
          ${nixos-branding-guide-editable}/bin/typst-watch
        '';

      }
    ) { };

  }
)
