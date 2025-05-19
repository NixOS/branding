{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-logomark-misuse-rotate"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-5dP0GyZWRRCaqCI1XsR8cs/h+9llhkq35xvM3ZTr33c=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
