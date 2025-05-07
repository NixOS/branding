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

    outputHash = "sha256-2eLzAHCvhqP5+c/zIoSeuLzCpSQv7TtbNu6lPGwZ0Ro=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
