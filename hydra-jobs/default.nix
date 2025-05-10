inputs:

let

  inherit (inputs.self.library)
    removeDirectoriesRecursiveAttrs
    ;

in

{

  media-kit = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.media-kit
    )
  );

  dimensioned-logos = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.dimensioned
    )
  );

}
