{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logo-misuse-crop"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";

    outputHash = "sha256-lWWWXX8dMxbd1yQ5g3GAaa+ae8eg9xZ7vjHWIiZq0n4=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
