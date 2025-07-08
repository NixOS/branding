{
  artifacts,
  lib,
  symlinkJoin,
}:

let

  inherit (lib.attrsets)
    attrValues
    ;

  inherit (lib.nixos-branding)
    removeDirectoriesRecursiveAttrs
    ;

in

symlinkJoin {
  name = "nixos-media-kit";
  paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.media-kit));
}
