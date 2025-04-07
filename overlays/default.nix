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
    elem
    filter
    map
    ;

  inherit (inputs.self.library)
    getDirectories
    getDirectoriesAndFilter
    ;

  # helpers

  removedDirectories = filter (
    x:
    !elem x [
      "python-packages" # this is a package set
    ]
  );

  # overlays

  allLocalOverlays = genAttrs (getDirectories ../overlays) (
    dir: import ../overlays/${dir}/overlay.nix inputs
  );

  allLocalPackages = genAttrs (removedDirectories (getDirectories ../packages)) (
    dir: final: prev: {
      "${dir}" = final.callPackage ../packages/${dir}/package.nix { };
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

  default = composeManyExtensions (
    (attrValues allLocalOverlays)
    ++ (attrValues allLocalPackages)
    ++ (attrValues pythonExtensions)
    ++ (attrValues pythonEditable)
  );

in
allLocalOverlays // allLocalPackages // pythonExtensions // pythonEditable // { inherit default; }
