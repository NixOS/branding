{
  git,
  lib,
  makeWrapper,
  nix,
  python3Packages,
}:

let
  inherit (lib.trivial) importTOML;
  pyproject = importTOML ./pyproject.toml;
in
python3Packages.buildPythonApplication {
  inherit (pyproject.project) name version;
  pyproject = true;
  src = ./.;

  build-system = [ python3Packages.poetry-core ];

  nativeBuildInputs = [ makeWrapper ];

  pythonImportsCheck = [ "compare_artifacts" ];

  # Ensure `git` and `nix` are on PATH at runtime.
  makeWrapperArgs = [
    "--prefix"
    "PATH"
    ":"
    (lib.makeBinPath [
      git
      nix
    ])
  ];
}
