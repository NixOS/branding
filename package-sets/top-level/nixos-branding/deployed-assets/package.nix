{
  artifacts,
  lib,
  nixos-branding-guide,
  runCommandLocal,
  symlinkJoin,
  tree,
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

    buildInputs = [ tree ];
  }
  ''
    mkdir -p $out/{documents,internals,logos}
    cp -r $documents/* $out/documents
    cp -r $internals/* $out/internals
    cp -r $logos/* $out/logos

    cd $out
    find . -type d -print0 | while IFS= read -r -d "" dir; do
      (
        cd "$dir" || exit
        tree . \
          -H "" \
          -L 1 \
          --noreport \
          --houtro "" \
          --dirsfirst \
          --charset utf-8 \
          -I "index.html" \
          -T "NixOS Branding" \
          --ignore-case \
          --timefmt "%d-%b-%Y %H:%M" \
          -s \
          -D \
          -o index.html
      )
    done
  ''
