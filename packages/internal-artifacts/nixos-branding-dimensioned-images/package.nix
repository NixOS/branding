{
  nixos-lambda-dimensioned-angular,
  nixos-lambda-dimensioned-linear,
  nixos-logomark-dimensioned-gradient-annotated,
  nixos-logomark-dimensioned-gradient-background,
  nixos-logomark-dimensioned-linear,
  nixos-logotype-dimensioned,
  symlinkJoin,
}:
symlinkJoin {
  name = "nixos-branding-dimensioned-images";
  paths = [
    nixos-lambda-dimensioned-angular
    nixos-lambda-dimensioned-linear
    nixos-logomark-dimensioned-gradient-annotated
    nixos-logomark-dimensioned-gradient-background
    nixos-logomark-dimensioned-linear
    nixos-logotype-dimensioned
  ];
}
