inputs:

let

  inherit (inputs.self)
    library
    formatterModule
    ;

in

library.defaultSystems (system: formatterModule.${system}.config.build.wrapper)
