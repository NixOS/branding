{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
  hatchling,
}:

buildPythonPackage rec {
  pname = "coloraide";
  version = "4.5.1";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "facelessuser";
    repo = "coloraide";
    rev = version;
    hash = "sha256-/jhVYJE3zxnSTPTFWB4CWw3TPq1qyte+hN7hcgzbbkE=";
  };

  build-system = [
    hatchling
  ];

  pythonImportsCheck = [
    "coloraide"
  ];

  meta = {
    description = "A library to aid in using colors";
    homepage = "https://github.com/facelessuser/coloraide";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ djacu ];
  };
}
