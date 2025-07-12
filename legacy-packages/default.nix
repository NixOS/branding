inputs:

let

  inherit (inputs.self)
    library
    overlays
    ;

in

library.defaultSystems (
  system:
  import inputs.nixpkgs {
    inherit system;
    overlays = [ overlays.everything ];
  }
)
