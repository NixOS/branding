inputs:
let

  # inherits

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.fixedPoints)
    composeManyExtensions
    ;

  inherit (lib.strings)
    versionOlder
    ;

  inherit (lib.trivial)
    warnIf
    ;

in

composeManyExtensions [

  (final: prev: {
    typix-lib = inputs.typix.lib.${final.stdenv.hostPlatform.system};
  })

  (
    final: prev:

    {
      typix-lib =
        let
          versionThreshold = "0.13.1";
          currentTypstVersion = final.typst.version;
        in
        prev.typix-lib.overrideScope (
          finalScope: prevScope:
          warnIf (versionOlder versionThreshold currentTypstVersion)
            ''
              The current version of typst is ${currentTypstVersion} which is older than version ${versionThreshold}.
              This overlay was created because typst version ${versionThreshold} did not deterministically create PDF files.
              Specifically, certain color data in SVG files were not being embedded in the SVG file deterministically.
              Try removing this overlay and see if the NixOS Branding Guide can be built and then re-built deterministically.
              If it can, remove this overlay. If not, bump the version threshold.
            ''
            {

              qpdf = warnIf (versionOlder "12" prev.qpdf.version) ''
                Upstream qpdf has reached version 12. This override and the associated derivation definition can be removed.
              '' final.qpdf;

              buildDeterministicTypstProject = finalScope.callPackage (
                {
                  lib,
                  mkTypstDerivation,
                  ocamlPackages,
                  qpdf,
                  typstOptsFromArgs,
                }:
                args@{
                  typstCompileCommand ? "typst compile",
                  typstSource ? "main.typ",
                  ...
                }:
                let

                  inherit (lib.attrsets)
                    removeAttrs
                    ;

                  inherit (lib.strings)
                    escapeShellArg
                    removeSuffix
                    ;

                  typstOptsString = args.typstOptsString or (typstOptsFromArgs args);

                  cleanedArgs = removeAttrs args [
                    "typstCompileCommand"
                    "typstOpts"
                    "typstOptsString"
                    "typstOutput"
                    "typstSource"
                  ];

                  outfileName = "${removeSuffix ".typ" typstSource}";

                  nativeBuildInputs = (args.nativeBuildInputs or [ ]) ++ [
                    ocamlPackages.cpdf
                    qpdf
                  ];

                in
                mkTypstDerivation (
                  cleanedArgs
                  // {
                    inherit
                      nativeBuildInputs
                      ;

                    buildPhaseTypstCommand =
                      args.buildPhaseTypstCommand or ''
                        ${typstCompileCommand} \
                          ${typstOptsString} \
                          ${escapeShellArg typstSource} \
                          ${outfileName}-compile.pdf

                        # need to remove the trailer ID so it can be recreated deterministically
                        cpdf \
                          -i ${outfileName}-compile.pdf \
                          -remove-id \
                          -o ${outfileName}-no-meta.pdf

                        qpdf \
                          ${outfileName}-no-meta.pdf \
                          --remove-metadata \
                          --deterministic-id \
                          ${outfileName}.pdf

                        mkdir $out
                        cp ${outfileName}.pdf $out/
                      '';
                  }
                )
              ) { };

            }
        );
    })

]
