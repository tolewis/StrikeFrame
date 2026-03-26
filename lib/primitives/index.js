const proofHero = require('./proofHero');

const REGISTRY = {
  [proofHero.id]: proofHero
};

function getPrimitiveRegistry() {
  return REGISTRY;
}

function buildPrimitiveSvgs(cfg, helpers) {
  const outputs = [];
  for (const primitive of Object.values(REGISTRY)) {
    const svg = primitive.buildSvg(cfg, helpers);
    if (svg) outputs.push({ id: primitive.id, input: svg });
  }
  return outputs;
}

module.exports = {
  getPrimitiveRegistry,
  buildPrimitiveSvgs
};
