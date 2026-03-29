'use strict';

const { Rect, Text } = require('../geometry');

/**
 * BenefitStack primitive — vertical list of icon + benefit pairs.
 *
 * Variants:
 *   - 'standard'   : Evenly spaced rows, left-aligned
 *   - 'compact'    : Tighter spacing, smaller icons, more items visible
 *   - 'card'       : Each benefit in a subtle card/pill background
 */

const VARIANTS = {
  'standard': {
    description: 'Evenly spaced rows, left-aligned',
    spacingScale: 1.0,
    iconScale: 1.0,
    textScale: 1.0
  },
  'compact': {
    description: 'Tighter spacing, smaller icons',
    spacingScale: 0.75,
    iconScale: 0.85,
    textScale: 0.9
  },
  'card': {
    description: 'Each benefit in a subtle card background',
    spacingScale: 1.15,
    iconScale: 1.0,
    textScale: 1.0,
    showCards: true
  }
};

function resolve(cfg, helpers) {
  const bs = cfg.benefitStack;
  if (!bs || !bs.items || !bs.items.length) return null;

  const variantName = bs.variant || 'standard';
  const variant = VARIANTS[variantName] || VARIANTS.standard;

  const startX = bs.startX || cfg.layout?.leftX || 80;
  const startY = bs.startY || 580;
  const spacing = Math.round((bs.spacing || 90) * variant.spacingScale);
  const iconSize = Math.round((bs.iconSize || 36) * variant.iconScale);
  const textSize = Math.round((bs.textSize || 28) * variant.textScale);
  const textMaxChars = bs.textMaxChars || 32;
  const textFont = bs.fontFamily || cfg.typography?.bodyFontFamily || 'Source Sans Pro, Arial, sans-serif';
  const textX = startX + iconSize + 16;

  const elements = [];
  const { wrapText } = helpers;

  bs.items.forEach((item, i) => {
    const iy = startY + i * spacing;
    const lines = wrapText(item.label || '', textMaxChars);
    const lineStep = Math.round(textSize * 1.2);
    const textWidth = Math.max(...lines.map(l => Text.measureWidth(l, textSize, textFont, { fontWeight: 600 })));
    const textHeight = lines.length * lineStep;

    elements.push({ id: `benefitStack.icon.${i}`, type: 'layout', rect: Rect.create(startX, iy - Math.round(iconSize / 2), iconSize, iconSize) });
    elements.push({ id: `benefitStack.text.${i}`, type: 'text', fontSize: textSize, rect: Rect.create(textX, iy - textSize, textWidth, textHeight) });
  });

  const totalHeight = (bs.items.length - 1) * spacing + textSize;
  elements.push({ id: 'benefitStack.bounds', type: 'layout', rect: Rect.create(startX, startY - Math.round((bs.iconSize || 36) / 2), cfg.width - startX * 2, totalHeight + iconSize) });

  return {
    variant: variantName,
    startX, startY, spacing, iconSize, textSize, textMaxChars, textFont, textX,
    elements,
    warnings: [
      ...(bs.items.length > 5 ? ['benefit_stack_too_many_items'] : [])
    ]
  };
}

function build(cfg, helpers) {
  const bs = cfg.benefitStack;
  if (!bs || !bs.items || !bs.items.length) return null;

  const { escapeXml, wrapText } = helpers;
  const solved = resolve(cfg, helpers);
  if (!solved) return null;

  // Import icon builder from render.js context — passed via helpers
  const buildIconGlyphSvg = helpers.buildIconGlyphSvg;

  const iconColor = bs.iconColor || '#63b3ed';
  const textColor = bs.textColor || '#ffffff';

  const nodes = bs.items.map((item, i) => {
    const iy = solved.startY + i * solved.spacing;
    const iconCenterY = iy - Math.round(solved.iconSize / 2);
    let icon = '';
    if (buildIconGlyphSvg) {
      icon = buildIconGlyphSvg(item.icon || 'check', solved.startX, iconCenterY, solved.iconSize, item.color || iconColor);
    }
    const lines = wrapText(item.label || '', solved.textMaxChars);
    const lineStep = Math.round(solved.textSize * 1.2);
    const tspans = lines.map((line, li) => `<tspan x="${solved.textX}" dy="${li === 0 ? 0 : lineStep}">${escapeXml(line)}</tspan>`).join('');
    return `${icon}<text x="${solved.textX}" y="${iy}" fill="${textColor}" font-size="${solved.textSize}" font-family="${solved.textFont}" font-weight="600">${tspans}</text>`;
  }).join('\n');

  return {
    id: 'benefitStack',
    svg: Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`),
    imageLayers: [],
    elements: solved.elements,
    warnings: solved.warnings
  };
}

module.exports = {
  id: 'benefitStack',
  configKey: 'benefitStack',
  variants: VARIANTS,
  resolve,
  build
};
