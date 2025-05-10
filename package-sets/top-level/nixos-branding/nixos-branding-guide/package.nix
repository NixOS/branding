{
  artifacts,
  lib,
  route159,
  symlinkJoin,
  typix-lib,
}:

let

  inherit (lib.attrsets)
    attrValues
    removeAttrs
    ;

  inherit (lib.fileset)
    unions
    toSource
    ;

  inherit (typix-lib)
    buildTypstProject
    ;

in

buildTypstProject {

  src = toSource {
    root = ./.;
    fileset = unions [ ./main.typ ];
  };

  typstSource = "main.typ";

  fontPaths = [
    "${route159}/share/fonts/opentype/route159"
  ];

  virtualPaths = [
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
