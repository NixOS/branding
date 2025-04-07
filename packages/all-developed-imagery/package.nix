{
  nixos-lambda-dimensioned-angular,
  nixos-lambda-dimensioned-linear,
  nixos-lambda-gradient-background,
  nixos-lambda-gradient-dimensioned,
  nixos-snowflake-color-flat,
  nixos-snowflake-color-gradient,
  nixos-snowflake-dimensioned-linear,
  nixos-snowflake-rainbow-gradient,
  symlinkJoin,
}:
symlinkJoin {
  name = "all-developed-imagery";
  paths = [
    nixos-lambda-dimensioned-angular
    nixos-lambda-dimensioned-linear
    nixos-lambda-gradient-background
    nixos-lambda-gradient-dimensioned
    nixos-snowflake-color-flat
    nixos-snowflake-color-gradient
    nixos-snowflake-dimensioned-linear
    nixos-snowflake-rainbow-gradient
  ];
}
