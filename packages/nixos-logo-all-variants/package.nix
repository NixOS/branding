{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logo-all-variants"
  {

    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/Route159-Regular.otf";

  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
