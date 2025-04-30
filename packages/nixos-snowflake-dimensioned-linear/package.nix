{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-snowflake-dimensioned-linear"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-h3KboPp7K0hTzqFIBvpieDcK62PYz0b8W4iteR1JrPA=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-snowflake-dimensioned-linear.svg $out/
  ''
