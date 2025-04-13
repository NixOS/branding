{
  lib,
  stdenvNoCC,
  unzip,
}:

stdenvNoCC.mkDerivation (finalAttrs: {
  pname = "route159";
  version = "${finalAttrs.majorVersion}.${finalAttrs.minorVersion}";
  majorVersion = "1";
  minorVersion = "10";

  src = ./route159_110.zip;

  nativeBuildInputs = [ unzip ];

  unpackPhase = ''
    unzip $src
  '';

  installPhase = ''
    runHook preInstall

    install -D -m444 -t $out/share/fonts/opentype *.otf

    runHook postInstall
  '';

  meta = with lib; {
    homepage = "http://dotcolon.net/fonts/route159/";
    description = "Weighted sans serif font";
    platforms = platforms.all;
    license = licenses.ofl;
  };
})
