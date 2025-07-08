{
  artifacts,
  lib,
  linkFarm,
  symlinkJoin,
}:

let

  inherit (lib.attrsets)
    attrValues
    mapAttrs
    ;

  inherit (lib.nixos-branding)
    removeDirectoriesRecursiveAttrs
    ;

  individualLinkFarms = mapAttrs (
    name: value:
    symlinkJoin {
      inherit name;
      paths = (attrValues (removeDirectoriesRecursiveAttrs value));
    }
  ) (removeDirectoriesRecursiveAttrs artifacts);

in
linkFarm "nixos-branding-all-artifacts" individualLinkFarms
