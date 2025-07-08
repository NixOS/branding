{
  artifacts,
  jura,
  lib,
  nixos-color-palette,
  route159,
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

{

  typstSource = "nixos-branding-guide.typ";

  fontPaths = [
    "${route159}/share/fonts/opentype/route159"
    "${jura}/share/fonts/truetype/jura"
  ];

  virtualPaths = [
    {
      dest = "data";
      src = ./data;
    }
    {
      dest = "images";
      src = ./images;
    }
    {
      dest = "colors";
      src = nixos-color-palette;
    }
    {
      dest = "clearspace";
      src = "${symlinkJoin {
        name = "artifacts.clearspace";
        paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.clearspace));
      }}";
    }
    {
      dest = "dimensioned";
      src = "${symlinkJoin {
        name = "artifacts.dimensioned";
        paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.dimensioned));
      }}";
    }
    {
      dest = "internal";
      src = "${symlinkJoin {
        name = "artifacts.internal";
        paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.internal));
      }}";
    }
    {
      dest = "media-kit";
      src = "${symlinkJoin {
        name = "artifacts.media-kit";
        paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.media-kit));
      }}";
    }
    {
      dest = "miscellaneous";
      src = "${symlinkJoin {
        name = "artifacts.miscellaneous";
        paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.miscellaneous));
      }}";
    }
    {
      dest = "misuse";
      src = "${symlinkJoin {
        name = "artifacts.misuse";
        paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.misuse));
      }}";
    }
  ];

}
