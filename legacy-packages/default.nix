inputs:
inputs.self.library.defaultSystems (
  system:
  import inputs.nixpkgs {
    inherit system;
    overlays = [ inputs.self.overlays.default ];
  }
)
