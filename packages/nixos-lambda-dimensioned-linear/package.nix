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

    outputHash = "sha256-PO5WI3/VQcJbEHLicrPORc0/Cfrx/7RD4JHZaAxRjFo=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-lambda-dimensioned-linear.svg $out/
  ''
