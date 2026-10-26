{
  lib,
  nodePackages,
  stdenvNoCC,
}:
let

  # inherits

  inherit (builtins)
    attrNames
    baseNameOf
    foldl'
    toString
    ;

  inherit (lib.attrsets)
    attrValues
    getAttr
    listToAttrs
    mapAttrs
    mapAttrs'
    nameValuePair
    mapAttrsToList
    ;

  inherit (lib.lists)
    concatMap
    head
    map
    toList
    ;

  inherit (lib.strings)
    concatMapStringsSep
    concatStringsSep
    match
    replaceStrings
    toJSON
    toLower
    ;

  inherit (lib.trivial)
    flip
    importTOML
    pipe
    ;

  # reshaping

  /**
    Converts oklch values to a Tailwind string.

    # Examples
    :::{.example}
    ## `oklchToTailwind` usage example

    ```nix
    oklchToTailwind [0.55 0.11 264]
    => "oklch(0.550000 0.110000 264)"
    ```

    :::
  */
  oklchToTailwind = value: "oklch(${toString value})";

  /**
    Gets the lightness value from a string.

    # Examples
    :::{.example}
    ## `getLightnessValue` usage example

    ```nix
    getLightnessValue "L95"
    => "95"
    ```

    :::
  */
  getLightnessValue = flip pipe [
    (match "[[:alpha:]]([[:digit:]]+)")
    head
  ];

  /**
    Convert a sequence of space-delimited words to kebab case. Will try to coerce
    non-string types to string.

    # Type

    ```
    toKebab :: String | [String] -> String
    ```

    # Examples
    :::{.example}
    ## `toKebab` usage example

    ```nix
    toKebab [ "1" "2" "3" ]
    => "1-2-3"
    toKebab [ 1 2 3 ]
    => "1-2-3"
    toKebab [ "1 2 3" ]
    => "1-2-3"
    ```

    :::
  */
  toKebab = flip pipe [
    toList
    (map toString)
    (concatStringsSep " ")
    (replaceStrings [ " " ] [ "-" ])
    toLower
  ];

  /**
    Converts the tints of a color to a Tailwind CSS string.

    The color optionally has an attribute `tints`. Each tint attribute
    contained should have a name of the form `XY+` where `X` is an alpha
    character and `Y` is one or more digits. The alpha character will be
    removed and the color values will be inserted into a string.

    # Type

    mapTintsToTailwind :: Attrset -> Attrset

    # Examples
    :::{.example}
    ## `mapTintsToTailwind` usage example

    ```nix
    mapTintsToTailwind {
      name = "Italian Violet";
      tints = {
        L15 = [ 0.15 0.03 288 ];
        L55 = [ 0.55 0.11 288 ];
        L95 = [ 0.95 0.02 288 ];
      };
      value = [ 0.75 0.12 288 ];
    }
    => {
      "15" = "oklch(0.150000 0.030000 288)";
      "55" = "oklch(0.550000 0.110000 288)";
      "95" = "oklch(0.950000 0.020000 288)";
    }

    mapTintsToTailwind {
      name = "NixOS Dark Blue";
      value = [ 0.55 0.12 264 ];
    }
    => { }
    ```

    :::
  */
  mapTintsToTailwind =
    member:
    mapAttrs' (
      shadeName: shadeValue: nameValuePair (getLightnessValue shadeName) (oklchToTailwind shadeValue)
    ) member.tints or { };

  /**
    Convert a color to a name value pair that is compatible with Tailwind CSS.

    # Inputs

    `groupName`

    : 1\. Name of the parent color group

    `member`

    : 2\. The color

    # Type

    mapColorToTailwind ::
      String ->
      { name :: String; tints :: Maybe Attrset; value :: [Number]; } ->
      { name :: String; value :: { DEFAULT :: String; Maybe XX :: String}; }

    # Examples
    :::{.example}
    ## `mapColorToTailwind` usage example

    ```nix
    mapColorToTailwind "accent" {
      name = "Italian Violet";
      tints = {
        L15 = [ 0.15 0.03 288 ];
        L55 = [ 0.55 0.11 288 ];
        L95 = [ 0.95 0.02 288 ];
      };
      value = [ 0.75 0.12 288 ];
    }
    => {
      "name": "accent-italian-violet",
      "value": {
        "15": "oklch(0.150000 0.030000 288)",
        "55": "oklch(0.550000 0.110000 288)",
        "95": "oklch(0.950000 0.020000 288)",
        "DEFAULT": "oklch(0.750000 0.120000 288)"
      }
    }

    mapColorToTailwind "rainbow" {
      "name": "red",
      "value": [ 0.51, 0.208963, 29.2339 ]
    }
    => {
      "name": "rainbow-red",
      "value": {
        "DEFAULT": "oklch(0.510000 0.208963 29.233900)"
      }
    }
    ```

    :::
  */
  mapColorToTailwindV3 =
    groupName: member:
    nameValuePair
      (toKebab [
        groupName
        member.name
      ])
      (
        {
          DEFAULT = oklchToTailwind member.value;
        }
        // (mapTintsToTailwind member)
      );

  /**
    Convert a palette group to a structure suitable for Tailwind.

    Examples
    :::{.example}
    ## `mapPaletteGroup` usage example

    ```nix
    mapPaletteGroup {
      "primary": [
        {
          "name": "Black",
          "tints": {
            "L15": [ 0.15, 0, 0 ],
            "L55": [ 0.55, 0, 0 ],
            "L95": [ 0.95, 0, 0 ]
          },
          "value": [ 0, 0, 0 ]
        },
        {
          "name": "White",
          "tints": {
            "L15": [ 0.15, 0, 0 ],
            "L55": [ 0.55, 0, 0 ],
            "L95": [ 0.95, 0, 0 ]
          },
          "value": [ 1, 0, 0 ]
        }
      ]
    }
    => {
      "primary": {
        "primary-black": {
          "15": "oklch(0.150000 0 0)",
          "55": "oklch(0.550000 0 0)",
          "95": "oklch(0.950000 0 0)",
          "DEFAULT": "oklch(0 0 0)"
        },
        "primary-white": {
          "15": "oklch(0.150000 0 0)",
          "55": "oklch(0.550000 0 0)",
          "95": "oklch(0.950000 0 0)",
          "DEFAULT": "oklch(1 0 0)"
        }
      }
    }
    ```

    :::
  */
  mapPaletteGroup = mapAttrs (
    groupName: groupValue: listToAttrs (map (mapColorToTailwindV3 groupName) groupValue)
  );

  /**
    Convert multiple palette groups to structures suitable for Tailwind.
  */
  mapPaletteGroups =
    colors:
    concatMap (
      flip pipe [
        (flip getAttr colors)
        mapPaletteGroup
        attrValues
      ]
    );

  /**
    Convert the palette to a structure suitable for Tailwind.
  */
  mapPaletteV3 =
    colors: groups:
    let
      data = foldl' (acc: elem: acc // elem) { } (mapPaletteGroups colors groups);
    in
    "export default ${toJSON data}";

  /**
    Convert the palette to a `@theme` block for Tailwind CSS v4.

    The `DEFAULT` shade of each color becomes a `--color-<name>` custom
    property and every other shade a `--color-<name>-<shade>` custom
    property, matching the Tailwind CSS v4 color variable convention. The
    result is meant to be imported into a stylesheet that imports
    `tailwindcss`.

    # Type

    mapPaletteV4 :: Attrset -> [String] -> String

    # Examples
    :::{.example}
    ## `mapPaletteV4` usage example

    ```nix
    mapPaletteV4 {
      logos = [
        {
          name = "red";
          value = [ 0.51 0.21 29 ];
        }
      ];
    } [ "logos" ]
    => ''
      @theme {
        --color-logos-red: oklch(0.51 0.21 29);
      }
    ''
    ```

    :::
  */
  mapPaletteV4 =
    colors: groups:
    let
      data = foldl' (acc: elem: acc // elem) { } (mapPaletteGroups colors groups);
      declarations = concatMap (
        groupName:
        mapAttrsToList (
          shadeName: shadeValue:
          nameValuePair (
            if shadeName == "DEFAULT" then "--color-${groupName}" else "--color-${groupName}-${shadeName}"
          ) shadeValue
        ) data.${groupName}
      ) (attrNames data);
    in
    ''
      @theme {
        ${concatMapStringsSep "\n" (d: "  ${d.name}: ${d.value};") declarations}
      }
    '';

  # sources

  colorsPath = ../nixos-color-palette;
  colorsFile = colorsPath + "/colors.toml";
  colorsData = importTOML colorsFile;

  tailwindContentV3 = mapPaletteV3 colorsData [
    "logos"
    "palette"
  ];

  tailwindContentV4 = mapPaletteV4 colorsData [
    "logos"
    "palette"
  ];
in

stdenvNoCC.mkDerivation {

  pname = baseNameOf ./.;
  version = colorsData.version;

  src = "";

  runLocal = true;
  dontUnpack = true;
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  installPhase = ''
    mkdir $out

    cat > $out/tailwind.js <<EOF
    ${tailwindContentV3}
    EOF

    cat > $out/tailwind.css <<EOF
    ${tailwindContentV4}
    EOF

    ${nodePackages.prettier}/bin/prettier --write $out/tailwind.js --write $out/tailwind.css
  '';

}
