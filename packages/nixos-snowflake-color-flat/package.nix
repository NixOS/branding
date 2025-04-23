{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-snowflake-color-flat"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-jDhlR3EKt5zAGVWbUiiMrHfCY/984eduse6OWQJQVZM=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-snowflake-color-flat.svg $out/
  ''
