{
  artifacts,
  lib,
  route159,
  symlinkJoin,
}:

let

  inherit (lib.attrsets)
    attrValues
    removeAttrs
    ;

in

{

  typstSource = "nixos-branding-guide.typ";

  fontPaths = [
    "${route159}/share/fonts/opentype/route159"
  ];

  virtualPaths = [
    {
      dest = "clearspace";
      src = "${symlinkJoin {
        name = "artifacts.clearspace";
        paths = (
          attrValues (
            removeAttrs artifacts.clearspace [
              "callPackage"
              "newScope"
              "overrideScope"
              "packages"
              "recurseForDerivations"
            ]
          )
        );
      }}";
    }
    {
      dest = "dimensioned";
      src = "${symlinkJoin {
        name = "artifacts.dimensioned";
        paths = (
          attrValues (
            removeAttrs artifacts.dimensioned [
              "callPackage"
              "newScope"
              "overrideScope"
              "packages"
              "recurseForDerivations"
            ]
          )
        );
      }}";
    }
    {
      dest = "internal";
      src = "${symlinkJoin {
        name = "artifacts.internal";
        paths = (
          attrValues (
            removeAttrs artifacts.internal [
              "callPackage"
              "newScope"
              "overrideScope"
              "packages"
              "recurseForDerivations"
            ]
          )
        );
      }}";
    }
    {
      dest = "media-kit";
      src = "${symlinkJoin {
        name = "artifacts.media-kit";
        paths = (
          attrValues (
            removeAttrs artifacts.media-kit [
              "callPackage"
              "newScope"
              "overrideScope"
              "packages"
              "recurseForDerivations"
            ]
          )
        );
      }}";
    }
    {
      dest = "miscellaneous";
      src = "${symlinkJoin {
        name = "artifacts.miscellaneous";
        paths = (
          attrValues (
            removeAttrs artifacts.miscellaneous [
              "callPackage"
              "newScope"
              "overrideScope"
              "packages"
              "recurseForDerivations"
            ]
          )
        );
      }}";
    }
  ];

}
