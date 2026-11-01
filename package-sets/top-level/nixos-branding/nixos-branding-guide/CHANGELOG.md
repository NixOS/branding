# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-31

### Added

- Trans-colored variants of the logomark and the logo in the media kit. They
  ship in the release assets and in the npm package.
- `colors/tailwind.css` for Tailwind v4 in the npm package, next to the
  existing `tailwind.js`.

### Changed

- Use math mode for all numerical values on the linear dimensions page.
- Add new lines on the angular dimensions page so there are no orphaned words.
- Add clarity about the definition of the gradient stop points.
- Add clarity about the definition of thickness.
- Build with typix `buildTypstProject` instead of
  `buildDeterministicTypstProject` now that upstream `typst` 0.14.1 no longer
  needs a deterministic build phase; `package.nix` sets the build and install
  commands explicitly.
- Derive the artifact virtual paths in `common.nix` from the artifact scope
  names instead of listing each one by hand.
- Use `lib.nixos-branding.removeDirectoriesRecursiveAttrs` in `common.nix` to
  strip the scope attributes from the artifact sets.
- Reformat `common.nix` and the Typst source with `nix fmt`; no content changes.
- The glyph specimen on the typeface page wraps differently under Typst 0.14.1.

### Fixed

- Fixed the radius value describing the lambda on the linear dimensions page.

## [0.1.0] - 2025-06-30

### Added

- Initial release
- Typst file for creating the document.
- `package.nix` for build
- `editable.nix` for development
- `common.nix` for shared nix derivation attributes
- `README.md` has general information about the guide and contributing
- `data/` contains the version file
- `images/` contains the cake SVG file
- This `CHANGELOG.md` file
