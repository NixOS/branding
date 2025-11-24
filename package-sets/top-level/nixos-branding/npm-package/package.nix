{
  all-artifacts,
  lib,
  nixos-color-palette-tailwind,
  nodePackages,
  stdenvNoCC,
}:

let

  inherit (lib.strings)
    readFile
    toJSON
    trim
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

in

stdenvNoCC.mkDerivation {

  pname = baseNameOf ./.;
  version = trim (readFile ./../nixos-branding-guide/data/version);

  src = "";

  runLocal = true;
  dontUnpack = true;
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  installPhase = ''
    mkdir -p $out/{colors,artifacts}

    cat > $out/package.json <<EOF
    ${toJSON npmPackageMetadata}
    EOF
    ${nodePackages.prettier}/bin/prettier --write $out/package.json

    cp -RL -r ${all-artifacts}/* $out/artifacts/
    cp ${nixos-color-palette-tailwind}/tailwind.js $out/colors/tailwind.js
  '';
}
