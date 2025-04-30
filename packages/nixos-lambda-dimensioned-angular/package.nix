{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-dimensioned-angular"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-rGl12pX+0eOIPd9jIudGq/HUeWu9GJN/sJeUSTIuVLo=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-lambda-dimensioned-angular.svg $out/
  ''
