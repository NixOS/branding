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
    removeAttrs
    ;

  inherit (lib.nixos-branding)
    removeDirectoriesRecursiveAttrs
    ;

  cleanedArtifacts = removeAttrs (removeDirectoriesRecursiveAttrs artifacts) [ "all-artifacts" ];

  individualLinkFarms = mapAttrs (
    name: value:
    symlinkJoin {
      inherit name;
      paths = (attrValues (removeDirectoriesRecursiveAttrs value));
    }
  ) cleanedArtifacts;

in
linkFarm "nixos-branding-artifacts" individualLinkFarms
