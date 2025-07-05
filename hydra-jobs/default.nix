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

rec {

  nixos-branding-all = inputs.self.library.defaultSystems (
    system:
    nixos-branding.${system}
    // nixos-branding-artifacts-clearspace.${system}
    // nixos-branding-artifacts-dimensioned.${system}
    // nixos-branding-artifacts-internal.${system}
    // nixos-branding-artifacts-media-kit.${system}
    // nixos-branding-artifacts-miscellaneous.${system}
    // nixos-branding-artifacts-misuse.${system}
  );

  nixos-branding-fods = inputs.self.library.defaultSystems (
    system:
    nixos-branding-artifacts-clearspace.${system}
    // nixos-branding-artifacts-dimensioned.${system}
    // nixos-branding-artifacts-internal.${system}
    // nixos-branding-artifacts-media-kit.${system}
    // nixos-branding-artifacts-miscellaneous.${system}
    // nixos-branding-artifacts-misuse.${system}
  );

  nixos-branding = inputs.self.library.defaultSystems (
    system:
    removeAttrs (removeDirectoriesRecursiveAttrs inputs.self.legacyPackages.${system}.nixos-branding) [
      "artifact-builder"
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

  nixos-branding-artifacts-internal = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.internal
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

  nixos-branding-artifacts-misuse = inputs.self.library.defaultSystems (
    system:
    (removeDirectoriesRecursiveAttrs
      inputs.self.legacyPackages.${system}.nixos-branding.artifacts.misuse
    )
  );

}
