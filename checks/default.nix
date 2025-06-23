inputs:
inputs.self.library.defaultSystems (system: {

  inherit (inputs.self.legacyPackages.${system}.nixos-branding)
    nixos-branding-guide
    nixos-logo-all-variants
    nixos-media-kit
    ;

  formatting = inputs.self.formatterModule.${system}.config.build.check inputs.self;

  pre-commit-check = inputs.pre-commit-hooks.lib.${system}.run {
    src = inputs.self;
    hooks = {
      treefmt.enable = true;
      treefmt.packageOverrides.treefmt = inputs.self.formatter.${system};
    };
  };

})
