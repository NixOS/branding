{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-dimensioned-linear"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-CSosXo75VpVUVHh2vslrIC7avyxsuP7Z4dRsyM0W5sM=";
    outputHashAlgo = "sha256";
    outputHashMode = "flat";
  }
  ''
    python $script
    cp nixos-lambda-dimensioned-linear.svg $out
  ''
