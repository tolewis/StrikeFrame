const proofHero = require('./proofHero');

const REGISTRY = {
  [proofHero.id]: proofHero
};

function getPrimitiveRegistry() {
  return REGISTRY;
}

function buildPrimitiveOutputs(cfg, helpers) {
  const outputs = [];
  for (const primitive of Object.values(REGISTRY)) {
    if (typeof primitive.build !== 'function') continue;
    const result = primitive.build(cfg, helpers);
    if (result) outputs.push(result);
  }
  return outputs;
}

module.exports = {
  getPrimitiveRegistry,
  buildPrimitiveOutputs
};
