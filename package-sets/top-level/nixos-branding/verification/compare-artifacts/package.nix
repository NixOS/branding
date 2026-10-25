{
  git,
  lib,
  makeWrapper,
  nix,
  python3Packages,
  resvg,
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

  dependencies = [ python3Packages.pillow ];

  nativeBuildInputs = [ makeWrapper ];
  nativeCheckInputs = [
    python3Packages.pytestCheckHook
    resvg
  ];

  pythonImportsCheck = [ "compare_artifacts" ];

  # Ensure `git`, `nix` and `resvg` are on PATH at runtime.
  makeWrapperArgs = [
    "--prefix"
    "PATH"
    ":"
    (lib.makeBinPath [
      git
      nix
      resvg
    ])
  ];
}
