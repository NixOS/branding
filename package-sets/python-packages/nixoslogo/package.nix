{
  buildPythonPackage,
  coloraide,
  fontforge,
  jsonpickle,
  lib,
  lxml,
  poetry-core,
  svg-py,
  svgpathtools,
}:

let

  inherit (lib.trivial)
    importTOML
    ;

  pyproject = importTOML ./pyproject.toml;

in

buildPythonPackage {

  inherit (pyproject.project) name version;

  pyproject = true;

  src = ./.;

  build-system = [
    poetry-core
  ];

  dependencies = [
    coloraide
    fontforge
    jsonpickle
    lxml
    svg-py
    svgpathtools
  ];

}
