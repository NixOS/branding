inputs:
let

  # inherits

  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.fixedPoints)
    composeManyExtensions
    ;

in

composeManyExtensions [

  (final: prev: {
    typix-lib = inputs.typix.lib.${final.stdenv.hostPlatform.system};
  })

  (
    final: prev:

    {
      typix-lib = prev.typix-lib.overrideScope (
        finalScope: prevScope: {

          # TODO @djacu remove this once upstream qpdf reaches version 12
          qpdf = final.qpdf;

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
                      --linearize \
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
