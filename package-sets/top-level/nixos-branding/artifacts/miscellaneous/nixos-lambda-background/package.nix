{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-background"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-C0/jGIbmVr+/0P2zwOart741jCDTf/8sBva5cVy0P3c=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
