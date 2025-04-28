{
  all-developed-imagery,
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
    "${route159}/share/fonts/opentype"
  ];

  virtualPaths = [
    {
      dest = "images";
      src = "${all-developed-imagery}";
    }
  ];

}
