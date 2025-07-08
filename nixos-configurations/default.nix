inputs:

let

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib)
    nixosSystem
    ;

  inherit (lib.attrsets)
    genAttrs
    ;

  inherit (inputs.self.library)
    getDirectories
    ;

in

genAttrs (getDirectories ./.) (
  configurationDir:
  nixosSystem {
    modules = [
      ./${configurationDir}/configuration.nix
    ];
  }
)
