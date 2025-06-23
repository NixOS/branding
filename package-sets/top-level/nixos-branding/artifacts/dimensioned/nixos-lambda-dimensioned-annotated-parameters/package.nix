{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-dimensioned-annotated-parameters"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-l+FhSHMKZIOwe1xw0gccMBJ5SQD3VT10zgSRssZZ40k=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
