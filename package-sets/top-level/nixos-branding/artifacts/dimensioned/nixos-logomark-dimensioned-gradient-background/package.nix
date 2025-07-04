{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-logomark-dimensioned-gradient-background"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-jxG4QIUitGYr05B24/BAi2nz4mxSrq2zLwV3fr5NcmQ=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
