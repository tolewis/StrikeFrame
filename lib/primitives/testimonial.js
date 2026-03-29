'use strict';

const { Rect, Text } = require('../geometry');

/**
 * Testimonial primitive — quote card with stars and attribution.
 *
 * Variants:
 *   - 'standard'     : Quote → stars → name/role, vertical stack
 *   - 'quote-hero'   : Oversized quote, compact attribution
 *   - 'attribution-forward' : Name/role emphasized alongside quote
 */

const VARIANTS = {
  'standard': {
    description: 'Quote → stars → name/role, vertical stack',
    quoteScale: 1.0,
    nameScale: 1.0,
    gapScale: 1.0
  },
  'quote-hero': {
    description: 'Oversized quote, compact attribution',
    quoteScale: 1.25,
    nameScale: 0.85,
    gapScale: 0.8
  },
  'attribution-forward': {
    description: 'Name/role emphasized alongside quote',
    quoteScale: 0.9,
    nameScale: 1.15,
    gapScale: 1.1
  }
};

function resolve(cfg, helpers) {
  const t = cfg.testimonial;
  if (!t) return null;

  const variantName = t.variant || 'standard';
  const variant = VARIANTS[variantName] || VARIANTS.standard;
  const { wrapText } = helpers;

  const quoteSize = Math.round((t.quoteSize || 36) * variant.quoteScale);
  const nameSize = Math.round((t.nameSize || 22) * variant.nameScale);
  const starSize = t.starSize || 32;
  const maxChars = t.quoteMaxChars || 28;
  const quoteFont = t.fontFamily || cfg.typography?.bodyFontFamily || 'Source Sans Pro, Arial, sans-serif';
  const headFont = cfg.typography?.headlineFontFamily || 'Montserrat, Arial, sans-serif';

  const isCentered = (cfg.layout?.personality === 'centered-hero' || cfg.layout?.align === 'center');
  const baseX = isCentered ? Math.round(cfg.width / 2) : (cfg.layout?.leftX || 80);
  const quoteMarkY = t.startY || 300;
  const quoteTextY = quoteMarkY + 80;
  const quoteLineStep = Math.round(quoteSize * 1.35);
  const lines = wrapText(t.quote || '', maxChars);
  const quoteBlockHeight = (lines.length - 1) * quoteLineStep + quoteSize;
  const starsY = quoteTextY + quoteBlockHeight + Math.round(40 * variant.gapScale);
  const nameY = starsY + starSize + Math.round(24 * variant.gapScale);
  const roleY = nameY + nameSize + 8;

  const elements = [];

  // Quote mark
  elements.push({ id: 'testimonial.quoteMark', type: 'text', fontSize: 120, rect: Rect.create(baseX - 40, quoteMarkY - 100, 80, 120) });

  // Quote text
  const quoteWidth = Math.max(...lines.map(l => Text.measureWidth(l, quoteSize, quoteFont)));
  const quoteLeft = isCentered ? Math.round(baseX - quoteWidth / 2) : baseX;
  elements.push({ id: 'testimonial.quote', type: 'text', fontSize: quoteSize, rect: Rect.create(quoteLeft, quoteTextY - quoteSize, quoteWidth, quoteBlockHeight) });

  // Stars
  const starsTotalWidth = 5 * (starSize + Math.round(starSize * 0.25)) - Math.round(starSize * 0.25);
  const starsX = isCentered ? Math.round(baseX - starsTotalWidth / 2) : baseX;
  elements.push({ id: 'testimonial.stars', type: 'text', fontSize: starSize, rect: Rect.create(starsX, starsY, starsTotalWidth, starSize) });

  // Name
  const nameWidth = Text.measureWidth(t.name || '', nameSize, headFont, { fontWeight: 700 });
  const nameLeft = isCentered ? Math.round(baseX - nameWidth / 2) : baseX;
  elements.push({ id: 'testimonial.name', type: 'text', fontSize: nameSize, rect: Rect.create(nameLeft, nameY - nameSize, nameWidth, nameSize) });

  // Role
  const roleSize = Math.round(nameSize * 0.82);
  const roleWidth = Text.measureWidth(t.role || '', roleSize, cfg.typography?.bodyFontFamily);
  const roleLeft = isCentered ? Math.round(baseX - roleWidth / 2) : baseX;
  elements.push({ id: 'testimonial.role', type: 'text', fontSize: roleSize, rect: Rect.create(roleLeft, roleY - roleSize, roleWidth, roleSize) });

  return {
    variant: variantName,
    quoteSize, nameSize, starSize, maxChars, lines,
    quoteFont, headFont, isCentered, baseX,
    quoteMarkY, quoteTextY, quoteLineStep, quoteBlockHeight,
    starsY, starsX, starsTotalWidth,
    nameY, roleY,
    elements,
    warnings: [
      ...(lines.length > 4 ? ['testimonial_quote_too_long'] : [])
    ]
  };
}

function build(cfg, helpers) {
  const t = cfg.testimonial;
  if (!t) return null;

  const { escapeXml, wrapText } = helpers;
  const solved = resolve(cfg, helpers);
  if (!solved) return null;

  const quoteColor = t.quoteColor || '#ffffff';
  const attributionColor = t.attributionColor || 'rgba(255,255,255,0.7)';
  const anchor = solved.isCentered ? 'middle' : 'start';
  const bodyFont = cfg.typography?.bodyFontFamily || 'Source Sans Pro, Arial, sans-serif';

  const tspans = solved.lines.map((line, i) => `<tspan x="${solved.baseX}" dy="${i === 0 ? 0 : solved.quoteLineStep}">${escapeXml(line)}</tspan>`).join('');

  // Build star rating
  const buildStarRatingSvg = helpers.buildStarRatingSvg;
  const starsSvg = buildStarRatingSvg ? buildStarRatingSvg(solved.starsX, solved.starsY, t.stars || 5, solved.starSize, cfg) : '';
  const quoteMarkX = solved.isCentered ? Math.round(solved.baseX - 20) : solved.baseX;

  const svg = Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
    <text x="${quoteMarkX}" y="${solved.quoteMarkY}" fill="${t.quoteMarkColor || 'rgba(232,93,58,0.8)'}" font-size="120" font-family="Georgia, serif" font-weight="700">\u201C</text>
    <text x="${solved.baseX}" y="${solved.quoteTextY}" text-anchor="${anchor}" fill="${quoteColor}" font-size="${solved.quoteSize}" font-family="${solved.quoteFont}" font-weight="500" font-style="italic">${tspans}</text>
    ${starsSvg}
    <text x="${solved.baseX}" y="${solved.nameY}" text-anchor="${anchor}" fill="${quoteColor}" font-size="${solved.nameSize}" font-family="${solved.headFont}" font-weight="700">${escapeXml(t.name || '')}</text>
    <text x="${solved.baseX}" y="${solved.roleY}" text-anchor="${anchor}" fill="${attributionColor}" font-size="${Math.round(solved.nameSize * 0.82)}" font-family="${bodyFont}" font-weight="400">${escapeXml(t.role || '')}</text>
  </svg>`);

  return {
    id: 'testimonial',
    svg,
    imageLayers: [],
    elements: solved.elements,
    warnings: solved.warnings
  };
}

module.exports = {
  id: 'testimonial',
  configKey: 'testimonial',
  variants: VARIANTS,
  resolve,
  build
};
