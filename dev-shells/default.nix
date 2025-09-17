inputs:

let

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    mapAttrs
    ;

  inherit (inputs.self)
    checks
    legacyPackages
    ;

in

mapAttrs (system: pkgs: {

  nixos-logo-dev = pkgs.callPackage (
    {
      jura,
      mkShell,
      nixos-branding,
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

        checks.${system}.pre-commit-check.enabledPackages

      ];

      shellHook = ''
        export NIXOSLOGO_SRC=$(git rev-parse --show-toplevel)/package-sets/python-packages/nixoslogo
        export NIXOS_ANNOTATIONS_FONT_FILE="${jura}/share/fonts/truetype/jura/Jura-Regular.ttf"
        export NIXOS_COLOR_PALETTE_FILE="${nixos-branding.nixos-color-palette}/colors.toml";
        export NIXOS_LOGOTYPE_FONT_FILE="${route159}/share/fonts/opentype/route159/Route159-Regular.otf"
      ''
      + checks.${system}.pre-commit-check.shellHook;

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
        exec ${nixos-branding-guide-editable}/bin/typst-watch
      '';

    }
  ) { };

}) legacyPackages
