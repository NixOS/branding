{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logo"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";

    outputHash = "sha256-URR6uEodYh7fmClN5QQBR16kKu+uPzaeOBJny09jb1c=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
