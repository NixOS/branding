inputs:

let

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    attrValues
    getAttrFromPath
    listToAttrs
    mergeAttrsList
    removeAttrs
    ;

  inherit (lib.lists)
    map
    ;

  inherit (lib.strings)
    concatStringsSep
    ;

  inherit (inputs.self)
    legacyPackages
    ;

  inherit (inputs.self.library)
    defaultSystems
    getDirectories
    removeDirectoriesRecursiveAttrs
    ;

  nixosBrandingArtifacts = listToAttrs (
    map (
      attrName:
      let
        attrPath = [
          "nixos-branding"
          "artifacts"
          attrName
        ];
      in
      {
        name = concatStringsSep "-" attrPath;
        value = defaultSystems (
          system: removeDirectoriesRecursiveAttrs (getAttrFromPath attrPath legacyPackages.${system})
        );
      }
    ) (getDirectories ../package-sets/top-level/nixos-branding/artifacts)
  );

in

rec {

  nixos-branding-all = defaultSystems (
    system: nixos-branding.${system} // nixos-branding-fods.${system}
  );

  nixos-branding-fods = defaultSystems (
    system: mergeAttrsList (lib.map (attrs: attrs.${system}) (attrValues nixosBrandingArtifacts))
  );

  nixos-branding = defaultSystems (
    system:
    removeAttrs (removeDirectoriesRecursiveAttrs legacyPackages.${system}.nixos-branding) [
      "artifact-builder"
      "artifacts"
      "verification"
      "nixos-branding-guide-editable"
    ]
  );

}
// nixosBrandingArtifacts
