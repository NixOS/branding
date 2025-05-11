{
  artifacts,
  lib,
  route159,
  symlinkJoin,
  typix-lib,
}:

let

  inherit (lib.fileset)
    unions
    toSource
    ;

  inherit (typix-lib)
    buildDeterministicTypstProject
    ;

in

buildDeterministicTypstProject (
  {

    pname = "nixos-branding-guide";
    version = "0.1.0";

    src = toSource {
      root = ./.;
      fileset = unions [ ./main.typ ];
    };

  }
  // (import ./common.nix {
    inherit
      artifacts
      lib
      route159
      symlinkJoin
      ;
  })
)
