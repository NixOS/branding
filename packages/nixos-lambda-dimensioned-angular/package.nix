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

    outputHash = "sha256-VzxhRyVCEzVC92LoHiocQb/fedQypOqMVl7Zkx8JXJk=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-lambda-dimensioned-angular.svg $out/
  ''
