{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-snowflake-rainbow-gradient"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-32quLnw8dYPmWDLb9avqUlqZkeKxcHW/FIvKpG4Runk=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-snowflake-rainbow-gradient.svg $out/
  ''
