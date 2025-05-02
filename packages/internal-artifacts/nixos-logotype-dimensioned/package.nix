{
  jura,
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logotype-dimensioned"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";
    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";

    outputHash = "sha256-qvrPhs9kROI+fH3zx9wCuicPbFCzImtNzr3uLvIF51g=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
