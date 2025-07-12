inputs:

let

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    mapAttrs
    ;

  inherit (inputs)
    pre-commit-hooks
    self
    ;

  inherit (inputs.self)
    formatter
    formatterModule
    legacyPackages
    ;

in

mapAttrs (system: pkgs: {

  formatting = formatterModule.${system}.config.build.check self;

  pre-commit-check = pre-commit-hooks.lib.${system}.run {
    src = self;
    hooks = {
      treefmt.enable = true;
      treefmt.packageOverrides.treefmt = formatter.${system};
    };
  };

}) legacyPackages
