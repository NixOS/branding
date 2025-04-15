{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logotype-black-modified-x"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/Route159-Regular.otf";

    outputHash = "sha256-5xBILHMJlcWmg0x65xYkK+SJhB/JytTVVcecAn8hybY=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-logotype-black-modified-x.svg $out/
  ''
