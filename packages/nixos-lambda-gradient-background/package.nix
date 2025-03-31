{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-gradient-background"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-EwcfnpSVi920TTbuRkPbAXGxM6eIUMIbAXklzoAAFDI=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-lambda-gradient-background.svg $out/
  ''
