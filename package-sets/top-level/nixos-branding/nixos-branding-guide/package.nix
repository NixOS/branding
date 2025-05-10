{
  lib,
  nixos-branding,
  route159,
  symlinkJoin,
  typix-lib,
}:

let

  inherit (lib.attrsets)
    attrValues
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
        paths = (attrValues nixos-branding.artifacts.dimensioned);
      }}";
    }
    {
      dest = "miscellaneous";
      src = "${symlinkJoin {
        name = "artifacts.miscellaneous";
        paths = (attrValues nixos-branding.artifacts.miscellaneous);
      }}";
    }
  ];

}
