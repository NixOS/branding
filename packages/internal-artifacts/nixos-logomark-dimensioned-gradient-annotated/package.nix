{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-logomark-dimensioned-gradient-annotated"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-8xIAlGOhmbf1h8CMKWUELnSDbhJ3rCTJW0kd9cjmLqU=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
