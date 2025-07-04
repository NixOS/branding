{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
  setuptools,
  wheel,
  numpy,
  scipy,
  svgwrite,
}:

buildPythonPackage {
  pname = "svgpathtools";
  version = "1.7.1";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "mathandy";
    repo = "svgpathtools";
    rev = "9ec59bb946544b14806af57f785ad84ed8d05119";
    hash = "sha256-SzYssDJ+uGb5zXZ16XaMCvIPF8BKJ4VVI/gUghz1IyA=";
  };

  build-system = [
    setuptools
    wheel
  ];

  dependencies = [
    numpy
    scipy
    svgwrite
  ];

  pythonImportsCheck = [
    "svgpathtools"
  ];

  meta = {
    description = "A collection of tools for manipulating and analyzing SVG Path objects and Bezier curves";
    homepage = "https://github.com/mathandy/svgpathtools";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ djacu ];
  };
}
