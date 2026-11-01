{
  jura,
  nixos-color-palette,
  python3,
  route159,
  runCommandLocal,
  testers,
}:
let
  pythonEnv = python3.withPackages (ps: [ ps.nixoslogo ]);
in
testers.invalidateFetcherByDrvHash (
  {
    name,
    outputHash,
    script,
  }:
  runCommandLocal name
    {
      inherit script;

      nativeBuildInputs = [
        pythonEnv
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
      ${pythonEnv}/bin/python $script
      mkdir $out
      cp *.svg $out/
    ''
)
