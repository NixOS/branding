inputs:
let

  # inherits

  inherit (builtins)
    attrValues
    ;

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    genAttrs
    listToAttrs
    ;

  inherit (lib.fixedPoints)
    composeManyExtensions
    ;

  inherit (lib.lists)
    map
    ;

  inherit (inputs.self.library)
    getDirectories
    getDirectoriesAndFilter
    ;

  # overlays

  localOverlays = genAttrs (getDirectories ../overlays) (
    dir: import ../overlays/${dir}/overlay.nix inputs
  );

  externalPackages =
    let
      parent = "../packages/external-artifacts";
    in
    (listToAttrs (
      map (dir: {
        name = "${dir}-editable";
        value = final: prev: {
          "${dir}-editable" = final.callPackage ./${parent}/${dir}/editable.nix { };
        };
      }) (getDirectoriesAndFilter ./${parent} "editable.nix")
    ))
    // genAttrs (getDirectories ./${parent}) (
      dir: final: prev: {
        "${dir}" = final.callPackage ./${parent}/${dir}/package.nix { };
      }
    );

  internalPackages =
    let
      parent = "../packages/internal-artifacts";
    in
    (listToAttrs (
      map (dir: {
        name = "${dir}-editable";
        value = final: prev: {
          "${dir}-editable" = final.callPackage ./${parent}/${dir}/editable.nix { };
        };
      }) (getDirectoriesAndFilter ./${parent} "editable.nix")
    ))
    // genAttrs (getDirectories ./${parent}) (
      dir: final: prev: {
        "${dir}" = final.callPackage ./${parent}/${dir}/package.nix { };
      }
    );

  localFontPackages = genAttrs (getDirectories ../packages/fonts) (
    dir: final: prev: {
      "${dir}" = final.callPackage ../packages/fonts/${dir}/package.nix { };
    }
  );

  pythonExtensions = genAttrs (getDirectories ../packages/python-packages) (
    dir: final: prev: {
      pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
        (python-final: python-prev: {
          "${dir}" = python-final.callPackage ../packages/python-packages/${dir}/package.nix { };
        })
      ];
    }
  );

  pythonEditable = listToAttrs (
    map (dir: {
      name = "${dir}-editable";
      value = final: prev: {
        pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
          (python-final: python-prev: {
            "${dir}-editable" = python-final.callPackage ../packages/python-packages/${dir}/editable.nix { };
          })
        ];
      };
    }) (getDirectoriesAndFilter ../packages/python-packages "editable.nix")
  );

  verificationPackages = genAttrs (getDirectories ../packages/verification) (
    dir: final: prev: {
      "${dir}" = final.callPackage ../packages/verification/${dir}/package.nix { };
    }
  );

  default = composeManyExtensions (
    (attrValues localOverlays)
    ++ (attrValues externalPackages)
    ++ (attrValues internalPackages)
    ++ (attrValues localFontPackages)
    ++ (attrValues pythonExtensions)
    ++ (attrValues pythonEditable)
    ++ (attrValues verificationPackages)
  );
  fonts = composeManyExtensions (attrValues localFontPackages);
  python-extensions = composeManyExtensions (attrValues pythonExtensions);

in
localOverlays
// {
  inherit
    default
    fonts
    python-extensions
    ;
}
