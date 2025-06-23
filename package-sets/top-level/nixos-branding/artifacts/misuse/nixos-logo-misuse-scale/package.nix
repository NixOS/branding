{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logo-misuse-scale"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";

    outputHash = "sha256-RfKqEqtFJDk13V69EL+7mRcWbF35oHfbLQWDtjrQPEM=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
