{
  buildPythonPackage,
  coloraide,
  fontforge,
  jsonpickle,
  lib,
  poetry-core,
  svg-py,
}:

let

  inherit (lib.trivial)
    importTOML
    ;

  pyproject = importTOML ./pyproject.toml;

in

buildPythonPackage {

  pname = pyproject.project.name;
  version = pyproject.project.version;

  pyproject = true;

  src = ./.;

  build-system = [
    poetry-core
  ];

  dependencies = [
    coloraide
    fontforge
    jsonpickle
    svg-py
  ];

}
