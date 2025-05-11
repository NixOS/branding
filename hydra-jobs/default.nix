inputs:

let

  inherit (inputs.self.library)
    removeDirectoriesRecursiveAttrs
    ;

in

{

  nixos-branding-artifacts-dimensioned = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.dimensioned
    )
  );

  nixos-branding-artifacts-media-kit = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.media-kit
    )
  );

}
