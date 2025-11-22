{
  lib,
  nodePackages,
  stdenvNoCC,
}:
let

  # inherits

  inherit (builtins)
    baseNameOf
    foldl'
    toString
    ;

  inherit (lib.attrsets)
    attrValues
    listToAttrs
    mapAttrs
    mapAttrs'
    nameValuePair
    ;

  inherit (lib.lists)
    map
    ;

  inherit (lib.strings)
    concatMapStringsSep
    replaceStrings
    substring
    toJSON
    toLower
    ;

  inherit (lib.trivial)
    importTOML
    ;

  # reshaping

  toKebapCase = x: toLower (replaceStrings [ " " ] [ "-" ] x);

  arrToOklch = arr: "oklch(${concatMapStringsSep " " toString arr})";

  mapPalettes = mapAttrs (
    paletteGroupName: paletteGroupValue:
    listToAttrs (
      map (
        member:
        let
          mappedTints = mapAttrs' (
            shadeName: shadeValue: nameValuePair (substring 1 2 shadeName) (arrToOklch shadeValue)
          ) member.tints or { };
        in
        nameValuePair (toKebapCase "${paletteGroupName} ${member.name}") (
          {
            DEFAULT = arrToOklch member.value;
          }
          // mappedTints
        )
      ) paletteGroupValue
    )

  );

  colors = foldl' (acc: elem: acc // elem) { } (
    (attrValues (mapPalettes colorsData.logos)) ++ (attrValues (mapPalettes colorsData.palette))
  );

  # sources

  colorsPath = ../nixos-color-palette;
  colorsFile = colorsPath + "/colors.toml";
  colorsData = importTOML colorsFile;

in

stdenvNoCC.mkDerivation {

  pname = baseNameOf ./.;
  version = colorsData.version;

  src = "";

  runLocal = true;
  dontUnpack = true;
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  installPhase = ''
    mkdir $out

    cat > $out/tailwind.js <<EOF
    export default ${toJSON colors}
    EOF
    ${nodePackages.prettier}/bin/prettier --write $out/tailwind.js
  '';

}
