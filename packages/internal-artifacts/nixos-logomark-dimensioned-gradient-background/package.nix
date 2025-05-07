{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-logomark-dimensioned-gradient-background"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-dB2MMhFELavNuuXIB0d2JRdX73BaakCRXjjgvwQkalo=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
