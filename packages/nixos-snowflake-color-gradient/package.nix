{
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-snowflake-color-gradient"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = "sha256-OYvqH/1esMy2NyCuhdw7WC+JwTL91C6/B10asoqFvgs=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp nixos-snowflake-color-gradient.svg $out/
  ''
