'use strict';

/**
 * Primitive registry for StrikeFrame.
 *
 * Each primitive exports:
 *   id       — unique name (e.g. 'proofHero', 'comparisonPanel')
 *   configKey — the config key that activates this primitive (e.g. 'proofHero', 'comparisonTable')
 *   variants — optional map of named variant modes
 *   resolve  — compute geometry and validate (cfg, helpers) → solved state
 *   build    — generate SVG + image layers (cfg, helpers) → { svg, imageLayers, elements, warnings }
 *
 * Lifecycle: detect → resolve → build → export geometry
 */

const proofHero = require('./proofHero');
const comparisonPanel = require('./comparisonPanel');
const offerFrame = require('./offerFrame');
const benefitStack = require('./benefitStack');
const testimonial = require('./testimonial');
const splitReveal = require('./splitReveal');
const authorityBar = require('./authorityBar');

const REGISTRY = {};

function register(primitive) {
  if (!primitive.id) throw new Error('Primitive must have an id');
  REGISTRY[primitive.id] = primitive;
}

register(proofHero);
register(comparisonPanel);
register(offerFrame);
register(benefitStack);
register(testimonial);
register(splitReveal);
register(authorityBar);

function getPrimitiveRegistry() {
  return { ...REGISTRY };
}

/**
 * Detect which primitives should activate for a given config.
 * Returns array of primitive objects that match.
 */
function detectPrimitives(cfg) {
  const active = [];
  for (const primitive of Object.values(REGISTRY)) {
    const key = primitive.configKey || primitive.id;
    if (cfg[key]) active.push(primitive);
  }
  return active;
}

/**
 * Build all active primitives for a config.
 * Runs the full lifecycle: detect → resolve → build → collect outputs.
 *
 * Returns array of { id, svg, imageLayers, elements, warnings, solved }.
 */
function buildPrimitiveOutputs(cfg, helpers) {
  const outputs = [];
  const active = detectPrimitives(cfg);
  for (const primitive of active) {
    if (typeof primitive.build !== 'function') continue;
    const result = primitive.build(cfg, helpers);
    if (result) {
      result.id = result.id || primitive.id;
      outputs.push(result);
    }
  }
  return outputs;
}

/**
 * Resolve all active primitives without building.
 * Useful for geometry-only analysis.
 */
function resolvePrimitives(cfg, helpers) {
  const results = [];
  const active = detectPrimitives(cfg);
  for (const primitive of active) {
    if (typeof primitive.resolve !== 'function') continue;
    const solved = primitive.resolve(cfg, helpers);
    if (solved) results.push({ id: primitive.id, solved });
  }
  return results;
}

module.exports = {
  register,
  getPrimitiveRegistry,
  detectPrimitives,
  buildPrimitiveOutputs,
  resolvePrimitives
};
