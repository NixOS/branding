inputs:

{

  media-kit = inputs.self.library.defaultSystems (
    system: inputs.self.legacyPackages.${system}.nixos-branding.artifacts.media-kit
  );

  dimensioned-logos = inputs.self.library.defaultSystems (
    system: inputs.self.legacyPackages.${system}.nixos-branding.artifacts.dimensioned
  );

}
