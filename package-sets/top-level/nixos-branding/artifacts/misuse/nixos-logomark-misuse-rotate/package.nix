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

    outputHash = "sha256-GvolEpXZkQjX9X48hisQINzvrcDGROHN1Lyg5eGqYck=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
