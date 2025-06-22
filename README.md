# NixOS Branding

This repository contains the official branding assets, guidelines, and design resources for the NixOS project.

## Purpose

The goal of this repository is to provide a unified and well-documented brand identity for NixOS.
It includes assets such as:

- The NixOS Branding Guide
- The NixOS logo and its variants
- Color palettes (OKLCH-based)
- Typography specifications

These materials help ensure consistency across websites, presentations, print materials, merchandise, and social media.

## Structure

This repository uses `packagesFromDirectoryRecursive` and has a file structure that takes complements its usage.

```
package-sets/
├── python-packages
│   └── nixoslogo  # code for generating logo variants
└── top-level
    ├── jura  # vendored copy of the Jura font
    ├── nixos-branding
    │   ├── artifacts  # Generated artifacts used in the branding guide and media-kit
    │   ├── nixos-branding-guide  # NixOS Branding Guide
    │   ├── nixos-color-palette  # NixOS color palette
    │   ├── nixos-media-kit  # NixOS media-kit
    │   └── verification  # Scripts use to verify that everything builds
    └── route159  # vendored copy of the Route 159 font
```

This maps to a `nixos-branding` scope under the top-level package set.

```
nixos-branding
├── artifacts
│   ├── all-artifacts
│   ├── clearspace
│   ├── dimensioned
│   ├── internal
│   ├── media-kit
│   ├── miscellaneous
│   └── misuse
├── nixos-media-kit
├── nixos-branding-guide
├── nixos-color-palette
└── verification
```

For example, to build the NixOS Branding Guide, run `nix build .#nixos-branding.nixos-branding-guide`.

## Contributing

We welcome contributions to improve and expand the NixOS branding system — whether you're refining logo assets, expanding the color palette, improving documentation, or proposing new use cases.

Because this repository involves visual identity, contributions are reviewed not only for technical correctness, but also for design consistency, accessibility, and alignment with the NixOS brand.

### Ways to Contribute

- Fix typos or improve the clarity of documentation
- Propose improvements to the branding guide
- Suggest additional assets (e.g. layout templates, printable logos)
- Add accessibility information or metadata
- Create or refine usage examples (correct and incorrect)

### Design-sensitive Contributions

For visual or structural changes (logos, color definitions, font treatments, layout guidelines), please:

1. Open a GitHub issue or discussion thread first to explain your idea.
1. Include visuals or mockups to illustrate your proposal.
1. Be prepared for collaborative iteration — visual identity is a shared responsibility.

Changes that impact the core brand elements (e.g., logo geometry, primary palette, typeface) will be reviewed by the Brand and Design Steward in coordination with the NixOS Marketing Team.

## Development

There are two major development efforts in this repository: the Python package `nixoslogo` and the NixOS Branding Guide.
Each of these has devShell suited for development.

### `nixoslogo`

The NixOS logos and other assets used in the NixOS Branding Guide are generated using Python.

To start developing, run `nix develop .#nixos-logo-dev`.
You can find the source code as mentioned in the [Structure](#structure) section.
Many of the modules have been instrumented to generate test images if called with `python` directly; use these to your benefit.

### NixOS Branding Guide

The NixOS Branding Guide is created using [Typst](https://github.com/typst/typst) and [Typix](https://github.com/loqusion/typix).

To start developing, run `nix develop .#nixos-branding-guide-dev`.
This will vendor files into the source directory where the Typst document lives.
It will also start a script that compiles the project and watches for changes.
Compilation will generate a PDF in the source directory; open it with a PDF viewer to watch your progress.

### Verification

All of the logo artifacts generated from `nixoslogo` are [fixed-output derivations][fods].
This allows us to update the source code of `nixoslogo` with confidence.
Before getting started, it is advised to run the following command.

```
nix run .\#nixos-branding.verification.verify-nixos-branding-fods
```

This will build all the fixed-output derivations.
As you are developing, you can run the following command to check that your changes to the source code have not changed the artifacts.

```
nix run .\#nixos-branding.verification.verify-nixos-branding-fods -- --rebuild
```

Sometimes we _do_ want to change the artifacts, but updating the hashes for all fixed-output derivations can be cumbersome.
The following command will attempt to build all the artifacts and update the hashes when it finds a mismatch.

```
nix run .\#nixos-branding.verification.update-nixos-branding-fods
```

There is also a command to build the other elements under the `nixos-branding` scope in addition to the fixed-output derivation artifacts.
It was created because some versions of Typst are not deterministic and this was put in place to verify that the NixOS Branding Guide builds reproducibly.
It can also be used with the `--rebuild` flag.

```
nix run .\#nixos-branding.verification.verify-nixos-branding-all
```

## Contact

For questions, feedback, or to request approval for brand use, reach out to the [NixOS Marketing Team](https://nixos.org/community/teams/marketing/).

[fods]: https://nix.dev/manual/nix/latest/glossary.html?highlight=fixed-output#gloss-fixed-output-derivation
