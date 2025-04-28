{
  all-developed-imagery,
  lib,
  route159,
  typix-lib,
}:

let

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
    "${route159}/share/fonts/opentype"
  ];

  virtualPaths = [
    {
      dest = "images";
      src = "${all-developed-imagery}";
    }
  ];

}
