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

  inherit (lib.filesystem)
    packagesFromDirectoryRecursive
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

  toplevelOverlays =
    final: prev:
    packagesFromDirectoryRecursive {
      inherit (final)
        callPackage
        newScope
        ;
      directory = ../package-sets/top-level;
    };

  pythonPackagesOverlays = final: prev: {
    pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
      (
        python-final: python-prev:
        packagesFromDirectoryRecursive {
          inherit (python-final)
            callPackage
            newScope
            ;
          directory = ../package-sets/python-packages;
        }
      )
    ];
  };

  pythonPackagesEditable = listToAttrs (
    map (dir: {
      name = "${dir}-editable";
      value = final: prev: {
        pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
          (python-final: python-prev: {
            "${dir}-editable" =
              python-final.callPackage ../package-sets/python-packages/${dir}/editable.nix
                { };
          })
        ];
      };
    }) (getDirectoriesAndFilter ../package-sets/python-packages "editable.nix")
  );

  nixosBrandingGuideEditable = final: prev: {
    nixos-branding-guide-editable =
      final.callPackage ../package-sets/top-level/nixos-branding/nixos-branding-guide/editable.nix
        { };
  };

  default = composeManyExtensions (
    (attrValues localOverlays)
    ++ [
      toplevelOverlays
      pythonPackagesOverlays
    ]
  );
  editable = composeManyExtensions (
    (attrValues pythonPackagesEditable)
    ++ [
      nixosBrandingGuideEditable
    ]
  );

  everything = composeManyExtensions [
    default
    editable
  ];

in
localOverlays
// {
  inherit
    default
    editable
    everything
    ;
}
