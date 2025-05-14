{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logotype"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";

    outputHash = "sha256-GVitgDPcjizf0nqG4JQoPdhUZrkGuTJEvEC30k7ta8g=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
