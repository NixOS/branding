{
  lib,
  stdenvNoCC,
  unzip,
}:

stdenvNoCC.mkDerivation (finalAttrs: {
  pname = "jura";
  version = "latest";

  src = ./Jura.zip;

  nativeBuildInputs = [ unzip ];

  unpackPhase = ''
    unzip $src
  '';

  installPhase = ''
    runHook preInstall

    install -D -m444 -t $out/share/fonts/truetype/${finalAttrs.pname} static/*.ttf

    runHook postInstall
  '';

  meta = with lib; {
    homepage = "https://fonts.google.com/specimen/Jura";
    description = "A family of sans-serif fonts in the Eurostile vein";
    platforms = platforms.all;
    license = licenses.ofl;
  };
})
