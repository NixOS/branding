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

    outputHash = "sha256-7VgnX1Rl4XTq1y2FcOSZ3Q0b0zxDahk1p7OxiueBlOw=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
