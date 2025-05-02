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

    outputHash = "sha256-AwKqSL7SJkR0XTQjGbZIE3NK840AA2U/nRsmotexZGI=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
