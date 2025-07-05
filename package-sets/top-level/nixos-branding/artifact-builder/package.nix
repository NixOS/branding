# artifact-builder
{
  jura,
  nixos-color-palette,
  python3,
  route159,
  runCommandLocal,
}:
# artifact
{
  name,
  outputHash,
  script,
}:
runCommandLocal name
  {
    inherit script;

    nativeBuildInputs = [
      (python3.withPackages (ps: [ ps.nixoslogo ]))
    ];

    outputHash = outputHash;
    outputHashAlgo = "sha256";
    outputHashMode = "recursive";

    env = {
      NIXOS_ANNOTATIONS_FONT_FILE = "${jura}/share/fonts/truetype/jura/Jura-Regular.ttf";
      NIXOS_COLOR_PALETTE_FILE = "${nixos-color-palette}/colors.toml";
      NIXOS_LOGOTYPE_FONT_FILE = "${route159}/share/fonts/opentype/route159/Route159-Regular.otf";
    };

  }
  ''
    python $script
    mkdir $out
    cp *.svg $out/
  ''
