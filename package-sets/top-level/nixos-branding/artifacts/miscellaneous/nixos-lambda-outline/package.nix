{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-/cDuzBtFWKSuXbFOhtcQZayYtzg1bL8fnegPfvm2ZDg=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
