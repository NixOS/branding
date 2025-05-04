{
  jura,
  python3,
  runCommandLocal,
}:
runCommandLocal "nixos-lambda-dimensioned-annotated-parameters"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";

    outputHash = "sha256-OkLjgghWV68jtQk9XGyhm6cn6n3bSlYLs8CKicpwz/g=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
