{
  jq,
  jura,
  lib,
  matrix-icons,
  nixos-branding,
  efficient-compression-tool,
  route159,
  symlinkJoin,
  typix-lib,

  singleIcon ? null,
}:

let
  inherit (builtins)
    readDir
    ;
  inherit (lib.asserts)
    assertOneOf
    ;
  inherit (lib.attrsets)
    attrNames
    attrValues
    genAttrs
    removeAttrs
    ;
  inherit (lib.fileset)
    toSource
    unions
    ;
  inherit (typix-lib)
    buildDeterministicTypstProject
    ;

  typstSource = "main.typ";
  listOfRooms = attrNames (readDir ./rooms);
in

assert assertOneOf "The selected room icon" singleIcon ([ null ] ++ listOfRooms);

buildDeterministicTypstProject {
  pname = "matrix-icons";
  version = "0.1.0";

  src = toSource {
    root = ./.;
    fileset = unions [ ./main.typ ];
  };

  nativeBuildInputs = [
    jq
    efficient-compression-tool
  ];

  inherit typstSource;

  fontPaths = [
    "${jura}/share/fonts/truetype/jura"
    "${route159}/share/fonts/opentype/route159"
  ];

  virtualPaths = [
    {
      dest = "icons";
      src = "${symlinkJoin {
        name = "helper-icons";
        paths = (
          attrValues (
            removeAttrs nixos-branding.artifacts.media-kit [
              "callPackage"
              "newScope"
              "overrideScope"
              "packages"
              "recurseForDerivations"
            ]
          )
        );
        postBuild = ''
          find ${./rooms} -type f -name "*.svg" -exec cp {} $out \;
        '';
      }}";
    }
  ];

  buildPhaseTypstCommand = ''
    find ${./rooms} -type f -name icon.json -print0 | xargs -0 jq -n 'reduce inputs as $item ({}; . + { (input_filename | split("/")[4]): $item })' >> final.json
    typst compile \
      --format png \
      --input singleIcon=${if (isNull singleIcon) then "null" else singleIcon} \
      ${typstSource} "{p}.png"
  '';

  installPhaseCommand = ''
    mkdir $out
    ${
      if (isNull singleIcon) then
        ''
          paste \
            <(jq -r 'keys[]' final.json) \
            <(find . -maxdepth 1 -type f -name '*.png' -printf '%f\n') \
          | while IFS=$'\t' read key png; do
            mv -- "$png" "$out/$key.png"
          done
        ''
      else
        "mv 1.png $out/${singleIcon}.png"
    }
    ect -9 -keep --strip --strict $out
  '';

  passthru = genAttrs listOfRooms (name: matrix-icons.override { singleIcon = name; });
}
