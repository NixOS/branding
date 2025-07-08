inputs:
inputs.nixpkgs.lib.attrsets.mapAttrs (system: pkgs: {

  formatting = inputs.self.formatterModule.${system}.config.build.check inputs.self;

  pre-commit-check = inputs.pre-commit-hooks.lib.${system}.run {
    src = inputs.self;
    hooks = {
      treefmt.enable = true;
      treefmt.packageOverrides.treefmt = inputs.self.formatter.${system};
    };
  };

}) inputs.self.legacyPackages
