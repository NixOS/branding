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

    outputHash = "sha256-NMUPemzi4Wt9HYff0hu3BJKRcRk7WkIeLdcymgLYvag=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
