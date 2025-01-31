inputs:
let
  inherit (builtins)
    attrNames
    readDir
    ;

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    filterAttrs
    genAttrs
    ;
in
{
  getDirectories =
    path: attrNames (filterAttrs (_: fileType: fileType == "directory") (readDir path));

  defaultSystems = genAttrs [
    "x86_64-linux"
    "aarch64-linux"
    "x86_64-darwin"
    "aarch64-darwin"
  ];
}
