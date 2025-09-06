{
  lib,
  stdenvNoCC,
  nixos-color-palette,
  all-artifacts,
  pkgs,
}:

let
  npmPckageMetadata = {
    name = "@NixOS/branding";
    version = "0.0.1";
    description = "Branding assets for the NixOS organization";
    main = "index.js";
    repository = {
      type = "git";
      url = "https://github.com/NixOS/branding.git";
    };
    author = "The NixOS Community";
    license = "ISC";
    bugs = {
      url = "https://github.com/NixOS/branding/issues";
    };
    homepage = "https://nixos.org";
    publishConfig = {
      registry = "https://npm.pkg.github.com/";
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

  toKebapCase = x: lib.strings.toLower (lib.strings.replaceStrings [ " " ] [ "-" ] x);

  arrToOklch =
    arr:
    "oklch(${toString (builtins.elemAt arr 0)}, ${toString (builtins.elemAt arr 1)}, ${toString (builtins.elemAt arr 2)})";

  colorsFile = lib.trivial.importTOML "${nixos-color-palette}/colors.toml";

  colorsFlattened =
    colorsFile.logos.default
    ++ colorsFile.logos.rainbow
    ++ colorsFile.palette.accent
    ++ colorsFile.palette.secondary;

  colors = builtins.listToAttrs (
    builtins.map (
      color:
      let
        mappedTints = builtins.mapAttrs (
          shadeName: shadeValue: toString (arrToOklch shadeValue)
        ) color.tints or { };
      in
      {
        name = toString (toKebapCase color.name);
        value = {
          DEFAULT = toString (arrToOklch color.value);
        }
        // mappedTints;
      }
    ) colorsFlattened
  );

in

stdenvNoCC.mkDerivation {
  pname = "npm-package";
  version = "0.0.1";

  src = ./.;

  runLocal = true;
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  installPhase = ''
    mkdir -p $out/colors
    cat > $out/package.json <<EOF
    ${builtins.toJSON npmPckageMetadata}
    EOF
    ${pkgs.nodePackages.prettier}/bin/prettier --write $out/package.json

    mkdir -p $out/artifacts
    cp -RL -r ${all-artifacts}/* $out/artifacts/

    cat > $out/colors/tailwind.js <<EOF
    export default ${builtins.toJSON colors}
    EOF
    ${pkgs.nodePackages.prettier}/bin/prettier --write $out/colors/tailwind.js

    cat > $out/.npmrc <<EOF
    //npm.pkg.github.com/:_authToken=$\{NODE_AUTH_TOKEN\}
    registry=https://npm.pkg.github.com/
    EOF
  '';
}
