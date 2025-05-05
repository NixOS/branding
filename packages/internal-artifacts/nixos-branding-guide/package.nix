{
  lib,
  nixos-branding-dimensioned-images,
  nixos-lambda-outline,
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
    "${route159}/share/fonts/opentype/route159"
  ];

  virtualPaths = [
    {
      dest = "background-images";
      src = "${nixos-lambda-outline}";
    }
    {
      dest = "dimensioned-images";
      src = "${nixos-branding-dimensioned-images}";
    }
  ];

}
