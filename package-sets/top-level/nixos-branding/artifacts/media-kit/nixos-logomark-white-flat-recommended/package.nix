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

    outputHash = "sha256-8+v1++CCdBrZuCrPirF6LbqiEJtkOvhfx5BQn8AUvO0=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
