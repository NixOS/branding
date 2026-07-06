{
  artifacts,
  lib,
  nixos-branding-guide,
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

# Assets attached to a GitHub release: the branding guide document plus the
# public-facing logos (artifacts.media-kit), flattened into one directory.
# This matches the pre-removal release contents (the old nixos-branding-guide
# + nixos-media-kit uploads) in a single buildable package. It deliberately
# excludes the internal logos and the browsable index.html files that
# deployed-assets adds for the Netlify web deploy.
symlinkJoin {
  name = "release-assets";
  paths = [
    nixos-branding-guide
  ]
  ++ attrValues (removeDirectoriesRecursiveAttrs artifacts.media-kit);
}
