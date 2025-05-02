{
  jura,
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logotype-black-dimensioned"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";
    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";

    outputHash = "sha256-awCOlj73NHC3qcfsUo2Y2gwIHHk5Romrz7isSOgnCj4=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
