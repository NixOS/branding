{ lib, stdenvNoCC }:

let

  inherit (lib.fileset)
    unions
    toSource
    ;

  inherit (lib.trivial)
    importTOML
    ;

in

stdenvNoCC.mkDerivation {

  pname = "nixos-color-palette";
  version = (importTOML ./colors.toml).version;

  src = toSource {
    root = ./.;
    fileset = unions [
      ./colors.toml
    ];
  };

  runLocal = true;
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  installPhase = ''
    mkdir $out
    cp $src/* $out
  '';

}
