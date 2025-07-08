inputs: final: prev: {

  lib = prev.lib.extend (
    finalLib: prevLib:
    let

      inherit (builtins)
        readDir
        ;

      inherit (finalLib.attrsets)
        attrNames
        filterAttrs
        removeAttrs
        ;

      inherit (finalLib.lists)
        filter
        ;

      inherit (finalLib.trivial)
        flip
        pathExists
        ;

    in
    {
      nixos-branding = {

        getDirectories =
          path: attrNames (filterAttrs (_: fileType: fileType == "directory") (readDir path));

        getDirectoriesAndFilter =
          path: file:
          filter (dirName: pathExists (path + "/${dirName}" + "/${file}")) (finalLib.getDirectories path);

        removeDirectoriesRecursiveAttrs = flip removeAttrs [
          "callPackage"
          "newScope"
          "overrideScope"
          "packages"
          "recurseForDerivations"
        ];

      };
    }
  );

}
