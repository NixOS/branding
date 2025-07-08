inputs:
inputs.nixpkgs.lib.attrsets.mapAttrs (
  system: pkgs:
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
          typstyle.enable = true;
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
) inputs.self.legacyPackages
