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

    outputHash = "sha256-cLQP54BfpoQsjGGtFgFPbMVz8o1KsQMj3yFjzpNCzxg=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
