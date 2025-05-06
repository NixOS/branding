{
  nixos-logo-default-gradient-black-regular-horizontal-recommended,
  nixos-logomark-default-flat-recommended,
  nixos-logomark-default-gradient-recommended,
  nixos-logomark-rainbow-gradient-recommended,
  nixos-logotype-black-coloredx-recommended,
  nixos-logotype-black-regular-recommended,
  symlinkJoin,
}:
symlinkJoin {
  name = "nixos-media-kit";
  paths = [
    nixos-logo-default-gradient-black-regular-horizontal-recommended
    nixos-logomark-default-flat-recommended
    nixos-logomark-default-gradient-recommended
    nixos-logomark-rainbow-gradient-recommended
    nixos-logotype-black-coloredx-recommended
    nixos-logotype-black-regular-recommended
  ];
}
