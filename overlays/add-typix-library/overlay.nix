inputs:
let

  # inherits

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.fixedPoints)
    composeManyExtensions
    ;

in

composeManyExtensions [

  (final: prev: {
    typix-lib = inputs.typix.lib.${final.stdenv.hostPlatform.system};
  })

]
