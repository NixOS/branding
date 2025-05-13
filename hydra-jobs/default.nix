inputs:

let

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    removeAttrs
    ;

  inherit (inputs.self.library)
    removeDirectoriesRecursiveAttrs
    ;

in

{

  nixos-branding = inputs.self.library.defaultSystems (
    system:
    removeAttrs (removeDirectoriesRecursiveAttrs inputs.self.legacyPackages.${system}.nixos-branding) [
      "artifacts"
      "verification"
      "nixos-branding-guide-editable"
    ]
  );

  nixos-branding-artifacts-clearspace = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.clearspace
    )
  );

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

  nixos-branding-artifacts-miscellaneous = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.miscellaneous
    )
  );

}
