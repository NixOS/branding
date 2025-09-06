{
  artifacts,
  lib,
  nixos-branding-guide,
  runCommandLocal,
  symlinkJoin,
}:

let

  inherit (lib.attrsets)
    attrValues
    ;

  inherit (lib.nixos-branding)
    removeDirectoriesRecursiveAttrs
    ;

  logos = symlinkJoin {
    name = "nixos-logos";
    paths = attrValues (removeDirectoriesRecursiveAttrs artifacts.media-kit);
  };
  internals = symlinkJoin {
    name = "nixos-internals";
    paths = attrValues (removeDirectoriesRecursiveAttrs artifacts.internal);
  };
  documents = symlinkJoin {
    name = "nixos-documents";
    paths = [ nixos-branding-guide ];
  };

in

runCommandLocal "deployed-assets"
  {
    inherit
      documents
      internals
      logos
      ;
  }
  ''
    mkdir -p $out/{documents,internals,logos}
    cp -r $documents/* $out/documents
    cp -r $internals/* $out/internals
    cp -r $logos/* $out/logos
  ''
