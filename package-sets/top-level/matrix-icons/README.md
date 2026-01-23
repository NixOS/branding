# NixOS Matrix Room Icons

This directory contains the builder scripts and the sources that generate the icons for NixOS-managed Matrix rooms.

## Creating a New Room Icon

1. Create a new subdirectory inside the `rooms/` directory with your room's alias in the [nixos.org](https://matrix.to/#/#community:nixos.org) space.

- For example, if your new room can be reached with the `#haskell:nixos.org` address, you would name the subdirectory `haskell`.

2. Inside your new subdirectory, create a file named `icon.json`. This file determines how your icon will be generated from the default templates.

- See the "`icon.json` Syntax" section below for more information on the valid fields for the `icon.json` file.

3. Build your new icon with `nix build .#matrix-icons.your-room-name`. Following the same example above, you would build the `#haskell:nixos.org` room icon with `nix build .#matrix-icons.haskell`.

- You can also build all room icons at once using `nix build .#matrix-icons`.

## `icon.json` Syntax

<!-- TODO: @sigmasquadron: How to best expose the full schema for `icon.json`? It would be great if there was some magic hidden file that code editors picked up automatically or something. -->

## Custom Assets

<!-- TODO: @sigmasquadron: Explain how to add .svg images to be embedded in the room icon. -->

## Examples

<!-- TODO: @sigmasquadron: Add a table with examples. -->
