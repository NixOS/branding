{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-dimensioned-angular"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-MjGS0GJhJ5u2AijXIXmlqji1BGljsR5pq0T0aoUilyc=";
    outputHashAlgo = "sha256";
    outputHashMode = "flat";
  }
  ''
    python $script
    cp nixos-lambda-dimensioned-angular.svg $out
  ''
