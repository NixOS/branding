inputs:

let

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    attrNames
    attrValues
    getAttrFromPath
    listToAttrs
    mapAttrsToList
    mergeAttrsList
    recursiveUpdate
    removeAttrs
    ;

  inherit (lib.lists)
    map
    foldl'
    ;

  inherit (lib.strings)
    concatStringsSep
    ;

  inherit (lib.trivial)
    pipe
    ;

  inherit (inputs.self)
    legacyPackages
    library
    ;

  inherit (library)
    defaultSystems
    removeDirectoriesRecursiveAttrs
    ;

  /*
    Generates individual hydraJobs for each category of branding artifact.

    It would be easier to access all the artifacts by directory and map over
    the list of names but that is a little clunky and not as stable as
    attribute paths. Unfortunately this means having to access through system
    first which makes the logic more difficult to parse.

    Get a map from systems to the list of artifacts. Map over list and
    generate a name-value pair where the name is the jobset name and the value
    is an attribute set where system maps to an attribute set of derivations.
    Because the map is per system, we can use `listToAttrs` without worrying
    about an attribute path getting clobbered. However, at the top level, we
    need to merge all the lists together with `recursiveUpdate`.
  */
  nixosBrandingArtifacts =
    let
      artifactsPath = [
        "nixos-branding"
        "artifacts"
      ];
      system2artifacts = defaultSystems (
        system:
        pipe legacyPackages.${system} [
          (getAttrFromPath artifactsPath)
          removeDirectoriesRecursiveAttrs
          attrNames
        ]
      );
    in
    foldl' recursiveUpdate { } (
      mapAttrsToList (
        system: artifacts:
        listToAttrs (
          map (
            artifactType:
            let
              artifactTypePath = artifactsPath ++ [ artifactType ];
            in
            {
              name = concatStringsSep "-" artifactTypePath;
              value = {
                ${system} = pipe legacyPackages.${system} [
                  (getAttrFromPath artifactTypePath)
                  removeDirectoriesRecursiveAttrs
                ];
              };
            }
          ) artifacts
        )
      ) system2artifacts
    );

in

rec {

  # All the NixOS branding
  nixos-branding-all = defaultSystems (
    system: nixos-branding.${system} // nixos-branding-fods.${system}
  );

  # All the NixOS branding that are fixed-output derivations
  nixos-branding-fods = defaultSystems (
    system: mergeAttrsList (map (attrs: attrs.${system}) (attrValues nixosBrandingArtifacts))
  );

  # All the NixOS branding that are not fixed-output derivations
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
