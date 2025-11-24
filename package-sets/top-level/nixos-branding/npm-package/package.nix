{
  all-artifacts,
  lib,
  nixos-color-palette,
  nodePackages,
  stdenvNoCC,
}:

let

  inherit (builtins)
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
    readFile
    replaceStrings
    substring
    toJSON
    toLower
    trim
    ;

  inherit (lib.trivial)
    importTOML
    ;

  npmPackageMetadata = {
    name = "@nixos/branding";
    version = trim (readFile ./../nixos-branding-guide/data/version);
    description = "Branding assets for the NixOS project.";
    main = "index.js";
    repository = {
      type = "git";
      url = "https://github.com/NixOS/branding.git";
    };
    author = "NixOS Marketing Team";
    license = "CC-BY-4.0";
    bugs = {
      url = "https://github.com/NixOS/branding/issues";
    };
    homepage = "https://nixos.org";
    publishConfig = {
      registry = "https://registry.npmjs.org";
    };
    keywords = [
      "nixos"
      "branding"
      "assets"
    ];
    files = [
      "colors/"
      "artifacts/"
      "package.json"
    ];
  };

  toKebapCase = x: toLower (replaceStrings [ " " ] [ "-" ] x);

  arrToOklch = arr: "oklch(${concatMapStringsSep " " toString arr})";

  colorsFile = importTOML ../nixos-color-palette/colors.toml;

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
    (attrValues (mapPalettes colorsFile.logos)) ++ (attrValues (mapPalettes colorsFile.palette))
  );

in

stdenvNoCC.mkDerivation {
  pname = "npm-package";
  version = trim (readFile ./../nixos-branding-guide/data/version);

  src = ./.;

  runLocal = true;
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  installPhase = ''
    mkdir -p $out/colors
    cat > $out/package.json <<EOF
    ${toJSON npmPackageMetadata}
    EOF
    ${nodePackages.prettier}/bin/prettier --write $out/package.json

    mkdir -p $out/artifacts
    cp -RL -r ${all-artifacts}/* $out/artifacts/

    cat > $out/colors/tailwind.js <<EOF
    export default ${toJSON colors}
    EOF
    ${nodePackages.prettier}/bin/prettier --write $out/colors/tailwind.js

    cat > $out/.npmrc <<EOF
    //npm.pkg.github.com/:_authToken=$\{NODE_AUTH_TOKEN\}
    registry=https://npm.pkg.github.com/
    EOF
  '';
}
