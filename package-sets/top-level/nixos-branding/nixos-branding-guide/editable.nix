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

  inherit (typix-lib)
    watchTypstProject
    ;

in

watchTypstProject (
  import ./common.nix {
    inherit
      artifacts
      jura
      lib
      nixos-color-palette
      route159
      symlinkJoin
      ;
  }
)
