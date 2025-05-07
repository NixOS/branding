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

    outputHash = "sha256-7J7ti9EWUjhOO7RgEP+eFYYfRGO62/F2k8VKr+HPv3Y=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
