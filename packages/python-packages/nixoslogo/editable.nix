{
  coloraide,
  # fontforge,
  jsonpickle,
  lib,
  mkPythonEditablePackage,
  lxml,
  poetry-core,
  svg-py,
}:

let

  inherit (lib.trivial)
    importTOML
    ;

  pyproject = importTOML ./pyproject.toml;

in

mkPythonEditablePackage {

  pname = pyproject.project.name;
  version = pyproject.project.version;

  root = "$NIXOSLOGO_SRC";

  build-system = [
    poetry-core
  ];

  dependencies = [
    coloraide
    # fontforge
    jsonpickle
    lxml
    svg-py
  ];

}
