{
  nixos-branding-dimensioned-images,
  nixos-lambda-outline,
  route159,
  typix-lib,
}:

let

  inherit (typix-lib)
    watchTypstProject
    ;

in

watchTypstProject {

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
