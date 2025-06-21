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

  inherit (lib.strings)
    readFile
    trim
    ;

  inherit (typix-lib)
    buildDeterministicTypstProject
    ;

in

buildDeterministicTypstProject (
  {

    pname = "nixos-branding-guide";
    version = trim (readFile ./data/version);

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
