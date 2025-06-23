{
  python3,
  route159,
  runCommandLocal,
}:
runCommandLocal "nixos-logo"
  {
    script = ./script.py;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    env.NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";

    outputHash = "sha256-t9fzJYP+s22ayKPXb3tuu6g9CD4kVQ9cP5bFRs9Ofb4=";
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";
  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
