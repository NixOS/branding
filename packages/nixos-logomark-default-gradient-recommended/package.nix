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

    outputHash = "sha256-O/WYV6hFjlf7vErrQfqKTAX1tz+4buxh4zZvYtnuYeA=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
