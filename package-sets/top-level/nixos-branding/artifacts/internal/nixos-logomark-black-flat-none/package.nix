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

    outputHash = "sha256-KkR80D3qMK1Szso8istPP86GfsD/NE9z3Eopsib08X4=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
