{
  artifacts,
  jura,
  lib,
  nixos-color-palette,
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
    buildTypstProject
    ;

  pname = "nixos-branding-guide";

in

buildTypstProject (
  {

    inherit pname;
    version = trim (readFile ./data/version);

    src = toSource {
      root = ./.;
      fileset = unions [ ./${pname}.typ ];
    };

    buildPhaseTypstCommand = "typst compile --format pdf ${pname}.typ";

    installPhaseCommand = ''
      mkdir $out
      cp ${pname}.pdf $out/
    '';

  }
  // (import ./common.nix {
    inherit
      artifacts
      jura
      lib
      nixos-color-palette
      route159
      symlinkJoin
      ;
  })
)
