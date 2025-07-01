inputs:

let

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib)
    nixosSystem
    ;

  inherit (lib.attrsets)
    filterAttrs
    mapAttrs
    ;

in

mapAttrs (
  configurationDir: _:
  nixosSystem {
    modules = [
      ./${configurationDir}/configuration.nix
    ];
  }
) (filterAttrs (_: fileType: fileType == "directory") (builtins.readDir ./.))
