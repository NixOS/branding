{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-snowflake-color-gradient"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-bnzRw6ed/w65rTUtMHZZxTr0fgPCXoadwM8MkBIsYjs=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-snowflake-color-gradient.svg $out/
  ''
