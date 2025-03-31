{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-gradient-dimensioned"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-4CbAJrVnOnlUm3J8uY9LOPxeAsVXhYXvphZfClk5/rk=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-lambda-gradient-dimensioned.svg $out/
  ''
