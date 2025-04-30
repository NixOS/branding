{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-gradient-dimensioned"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-8M8n6hThu2Xr3YLwwdO+M/W9cNdJgfHiVW0D+RWbB80=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-lambda-gradient-dimensioned.svg $out/
  ''
