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
    attrNames
    attrValues
    ;

  inherit (lib.lists)
    map
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

  virtualPaths =
    [
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
    ]
    ++ (map (artifact: {
      dest = artifact;
      src = "${symlinkJoin {
        name = "artifacts.${artifact}";
        paths = (attrValues (removeDirectoriesRecursiveAttrs artifacts.${artifact}));
      }}";
    }) (attrNames (removeDirectoriesRecursiveAttrs artifacts)));

}
