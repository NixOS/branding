{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-dimensioned-angular"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-bKwUdEq0RDft5O8hEJTznPPppIK7xwUhx4FWCe8aXvg=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
