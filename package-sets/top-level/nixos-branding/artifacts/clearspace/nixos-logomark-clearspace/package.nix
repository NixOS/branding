{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-logomark-clearspace"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-f2LSFFGeJlkrhFHNN/2drhQr7mzlQ9VMBaXPk89P3p8=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
