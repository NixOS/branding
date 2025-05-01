{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-gradient-background"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-RI+Y5gMmHEoy1LDbCwie12lFmewvJbj31rhVPK8SJ04=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-lambda-gradient-background.svg $out/
  ''
