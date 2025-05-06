{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-dimensioned-annotated-vertices"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-EeuZr3XEEsLYE8ZTPtfxzlkxI+1575p4Nw0UIzQH3s0=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
