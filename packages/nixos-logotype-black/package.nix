{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logotype-black"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/Route159-Regular.otf";

    outputHash = "sha256-O/bXnzpb6MlQ8E2FVEg97GlGCszmzUEbG+fRwKuP1Vg=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-logotype-black.svg $out/
  ''
