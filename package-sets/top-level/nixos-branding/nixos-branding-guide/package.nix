{
  artifacts,
  jura,
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
      fileset = unions [ ./nixos-branding-guide.typ ];
    };

  }
  // (import ./common.nix {
    inherit
      artifacts
      jura
      lib
      route159
      symlinkJoin
      ;
  })
)
