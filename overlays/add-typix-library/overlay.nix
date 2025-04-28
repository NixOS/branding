inputs: final: prev: {
  typix-lib = inputs.typix.lib.${final.stdenv.hostPlatform.system};
}
