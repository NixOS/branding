{
  artifacts,
  lib,
  symlinkJoin,
}:

let

  inherit (lib.attrsets)
    attrValues
    removeAttrs
    ;

in

symlinkJoin {
  name = "nixos-media-kit";
  paths = (
    attrValues (
      removeAttrs artifacts.media-kit [
        "callPackage"
        "newScope"
        "overrideScope"
        "packages"
        "recurseForDerivations"
      ]
    )
  );
}
