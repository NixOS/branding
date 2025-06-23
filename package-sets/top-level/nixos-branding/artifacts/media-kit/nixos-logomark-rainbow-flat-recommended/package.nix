{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-logomark"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-TcFp/n3JyPcDFZ3lXi4PaEdHGBHWD66YvX1s5RBvdts=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
