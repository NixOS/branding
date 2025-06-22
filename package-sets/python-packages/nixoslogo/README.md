# nixoslogo

`nixoslogo` is a Python project that programmatically generates all official NixOS logo variants and supporting SVG assets used in the NixOS Branding Guide.

This tool ensures that all logo outputs are built from source using consistent geometry, spacing, and color logic — making the branding system reproducible, auditable, and easy to maintain.

## Features

- Generates the complete set of NixOS logo variants, including:
  - Default logomark
  - Logotype variants (e.g. λ′ / lambda prime)
  - Pride flag variant
  - Monochrome versions
- Outputs structural diagrams:
  - Geometry overlays
  - Dimensions and alignment guides
  - Clear space references
- Produces misuse illustrations:
  - Distortion examples
  - Improper cropping
  - Improper spacing
- Supports internal-use assets:
  - Versions without clear space

All outputs are generated as clean, standards-compliant SVG files suitable for web, print, and documentation pipelines.

## Design Philosophy

`nixoslogo` reflects the values of the NixOS project: declarative, reproducible, and precise.
By generating all branding assets from code, we reduce ambiguity and ensure consistency across all uses of the NixOS visual identity.

## Contributing

Contributions are welcome.
If you're proposing a new logo variant, refining SVG output, or improving internal tooling, please open an issue or pull request.
Design-sensitive contributions will be reviewed by the **Brand and Design Steward** in collaboration with the **NixOS Marketing Team**.
