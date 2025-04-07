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

  inherit (lib.lists)
    filter
    ;

  inherit (lib.trivial)
    pathExists
    ;

in
rec {
  getDirectories =
    path: attrNames (filterAttrs (_: fileType: fileType == "directory") (readDir path));

  getDirectoriesAndFilter =
    path: file: filter (dirName: pathExists (path + "/${dirName}" + "/${file}")) (getDirectories path);

  defaultSystems = genAttrs [
    "x86_64-linux"
    "aarch64-linux"
    "x86_64-darwin"
    "aarch64-darwin"
  ];
}
