{
  description = "nix-derivation-parser";

  inputs = {
    flake-compat.flake = false;
    flake-compat.url = "github:edolstra/flake-compat";
    gitignore.inputs.nixpkgs.follows = "nixpkgs";
    gitignore.url = "github:hercules-ci/gitignore.nix";
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    pre-commit-hooks.inputs.flake-compat.follows = "flake-compat";
    pre-commit-hooks.inputs.gitignore.follows = "gitignore";
    pre-commit-hooks.inputs.nixpkgs.follows = "nixpkgs";
    pre-commit-hooks.url = "github:cachix/git-hooks.nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    typix.url = "github:loqusion/typix";
    typix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs: {
    checks = import ./checks inputs;
    devShells = import ./dev-shells inputs;
    formatter = import ./formatter inputs;
    formatterModule = import ./formatter-module inputs;
    hydraJobs = import ./hydra-jobs inputs;
    legacyPackages = import ./legacy-packages inputs;
    library = import ./library inputs;
    overlays = import ./overlays inputs;
    packages = import ./packages inputs;
  };
}
