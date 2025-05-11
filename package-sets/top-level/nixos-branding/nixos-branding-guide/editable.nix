{
  artifacts,
  lib,
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
      lib
      route159
      symlinkJoin
      ;
  }
)
