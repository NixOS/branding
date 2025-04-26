inputs:
inputs.self.library.defaultSystems (
  system:
  let
    pkgs = inputs.self.legacyPackages.${system};
  in
  (inputs.treefmt-nix.lib.evalModule pkgs (
    { ... }:
    {
      config = {
        enableDefaultExcludes = true;
        projectRootFile = "flake.nix";
        programs = {
          mdformat.enable = true;
          mdsh.enable = true;
          nixfmt.enable = true;
          ruff-check.enable = true;
          ruff-format.enable = true;
          shellcheck.enable = true;
        };
        settings.global.excludes = [
          "**/pyproject.toml"
          "*.gitignore"
          "*.zip"
          ".git-blame-ignore-revs"
        ];
      };
    }
  ))
)
