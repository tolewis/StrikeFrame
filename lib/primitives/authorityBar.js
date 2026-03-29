'use strict';

const { Rect, Text } = require('../geometry');

/**
 * AuthorityBar primitive — horizontal credibility/verification strip.
 *
 * Variants:
 *   - 'standard' : Centered text bar, subtle background
 *   - 'bold'     : Higher contrast, larger text, stronger background
 */

const VARIANTS = {
  'standard': {
    description: 'Centered text bar, subtle background',
    textScale: 1.0,
    barOpacity: 0.06
  },
  'bold': {
    description: 'Higher contrast, larger text, stronger background',
    textScale: 1.2,
    barOpacity: 0.12
  }
};

function resolve(cfg, helpers) {
  const ab = cfg.authorityBar;
  if (!ab) return null;

  const pubs = ab.publications || [];
  if (!pubs.length) return null;

  const variantName = ab.variant || 'standard';
  const variant = VARIANTS[variantName] || VARIANTS.standard;

  const barY = ab.barY || Math.round(cfg.height * 0.75);
  const barHeight = ab.barHeight || 40;
  const textSize = Math.round((ab.textSize || 14) * variant.textScale);
  const font = cfg.typography?.bodyFontFamily || 'Source Sans Pro, Arial, sans-serif';
  const joined = pubs.join('  \u2022  ').toUpperCase();
  const textWidth = Text.measureWidth(joined, textSize, font, { mode: 'upper', fontWeight: 600 });
  const centerX = Math.round(cfg.width / 2);

  const elements = [
    { id: 'authorityBar.bar', type: 'layout', rect: Rect.create(0, barY, cfg.width, barHeight) },
    { id: 'authorityBar.text', type: 'text', fontSize: textSize, rect: Rect.create(centerX - textWidth / 2, barY + (barHeight - textSize) / 2, textWidth, textSize) }
  ];

  return {
    variant: variantName,
    barY, barHeight, textSize, font,
    joined, centerX, barOpacity: variant.barOpacity,
    elements,
    warnings: []
  };
}

function build(cfg, helpers) {
  const ab = cfg.authorityBar;
  if (!ab) return null;

  const { escapeXml } = helpers;
  const solved = resolve(cfg, helpers);
  if (!solved) return null;

  const textColor = ab.textColor || 'rgba(255,255,255,0.5)';
  const barFill = ab.barFill || `rgba(255,255,255,${solved.barOpacity})`;

  let nodes = '';
  nodes += `<rect x="0" y="${solved.barY}" width="${cfg.width}" height="${solved.barHeight}" fill="${barFill}"/>`;
  nodes += `<text x="${solved.centerX}" y="${solved.barY + Math.round(solved.barHeight / 2)}" dy="0.35em" text-anchor="middle" fill="${textColor}" font-size="${solved.textSize}" font-family="${solved.font}" font-weight="600" letter-spacing="2">${escapeXml(solved.joined)}</text>`;

  return {
    id: 'authorityBar',
    svg: Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`),
    imageLayers: [],
    elements: solved.elements,
    warnings: solved.warnings
  };
}

module.exports = {
  id: 'authorityBar',
  configKey: 'authorityBar',
  variants: VARIANTS,
  resolve,
  build
};
