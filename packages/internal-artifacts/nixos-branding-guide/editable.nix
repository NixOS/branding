{
  nixos-branding-dimensioned-images,
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
      dest = "dimensioned-images";
      src = "${nixos-branding-dimensioned-images}";
    }
  ];

}
