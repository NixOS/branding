{
  lib,
  nixos-branding,
  symlinkJoin,
}:

let

  inherit (lib.attrsets)
    attrValues
    ;

in

symlinkJoin {
  name = "nixos-media-kit";
  paths = (attrValues nixos-branding.artifacts.media-kit);
}
