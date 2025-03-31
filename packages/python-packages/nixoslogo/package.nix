{
  buildPythonPackage,
  coloraide,
  fontforge,
  jsonpickle,
  poetry-core,
  svg-py,
}:

buildPythonPackage {

  pname = "nixoslogo";
  version = "0.1.0";

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
