{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-snowflake-dimensioned-linear"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-snfh5XqnROCxKFETR81842SPi16sS5RNZ+Xgrjq+HSA=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-snowflake-dimensioned-linear.svg $out/
  ''

