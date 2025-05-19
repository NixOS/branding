{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-logomark-misuse-mirror"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-RkmJpLm7vrNYb+dvgSalbKGOvMNhRde5E7qd15cMPo8=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
