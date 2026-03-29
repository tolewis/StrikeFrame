'use strict';

const { Rect, Text } = require('../geometry');

/**
 * SplitReveal primitive — problem/solution two-column layout.
 *
 * Variants:
 *   - 'standard'    : Equal columns, centered divider
 *   - 'pain-heavy'  : Left column wider, emphasizes the problem
 *   - 'solution-hero' : Right column wider, solution dominates
 */

const VARIANTS = {
  'standard': {
    description: 'Equal columns, centered divider',
    dividerRatio: 0.5
  },
  'pain-heavy': {
    description: 'Left column wider, emphasizes the problem',
    dividerRatio: 0.55
  },
  'solution-hero': {
    description: 'Right column wider, solution dominates',
    dividerRatio: 0.42
  }
};

function resolve(cfg, helpers) {
  const sr = cfg.splitReveal;
  if (!sr) return null;

  const variantName = sr.variant || 'standard';
  const variant = VARIANTS[variantName] || VARIANTS.standard;
  const items = sr.items || [];

  const dividerX = sr.dividerX || Math.round(cfg.width * variant.dividerRatio);
  const startY = sr.startY || 400;
  const rowHeight = sr.rowHeight || 60;
  const textSize = sr.textSize || 24;
  const labelSize = sr.labelSize || 16;
  const font = cfg.typography?.bodyFontFamily || 'Source Sans Pro, Arial, sans-serif';
  const leftX = sr.leftX || Math.round(dividerX / 2);
  const rightX = sr.rightX || Math.round(dividerX + (cfg.width - dividerX) / 2);
  const labelY = startY - 30;

  const elements = [];

  // Labels
  const problemLabel = sr.problemLabel || 'THE PROBLEM';
  const solutionLabel = sr.solutionLabel || 'THE FIX';
  const problemWidth = Text.measureWidth(problemLabel, labelSize, font, { mode: 'upper', fontWeight: 700 });
  const solutionWidth = Text.measureWidth(solutionLabel, labelSize, font, { mode: 'upper', fontWeight: 700 });
  elements.push({ id: 'splitReveal.problemLabel', type: 'text', fontSize: labelSize, rect: Rect.create(leftX - problemWidth / 2, labelY - labelSize, problemWidth, labelSize) });
  elements.push({ id: 'splitReveal.solutionLabel', type: 'text', fontSize: labelSize, rect: Rect.create(rightX - solutionWidth / 2, labelY - labelSize, solutionWidth, labelSize) });

  // Divider
  const dividerHeight = items.length * rowHeight + 60;
  elements.push({ id: 'splitReveal.divider', type: 'layout', rect: Rect.create(dividerX - 1, labelY - 10, 2, dividerHeight) });

  // Rows
  items.forEach((item, i) => {
    const ry = startY + i * rowHeight + 20;
    const leftWidth = Text.measureWidth(item.left || '', textSize, font);
    const rightWidth = Text.measureWidth(item.right || '', textSize, font, { fontWeight: 600 });
    elements.push({ id: `splitReveal.row.${i}.left`, type: 'text', fontSize: textSize, rect: Rect.create(leftX - leftWidth / 2, ry - textSize, leftWidth, textSize) });
    elements.push({ id: `splitReveal.row.${i}.right`, type: 'text', fontSize: textSize, rect: Rect.create(rightX - rightWidth / 2, ry - textSize, rightWidth, textSize) });
  });

  return {
    variant: variantName,
    dividerX, startY, rowHeight, textSize, labelSize, font,
    leftX, rightX, labelY, items,
    problemLabel, solutionLabel,
    elements,
    warnings: [
      ...(items.length > 6 ? ['split_reveal_too_many_rows'] : []),
      ...(items.length < 2 ? ['split_reveal_too_few_rows'] : [])
    ]
  };
}

function build(cfg, helpers) {
  const sr = cfg.splitReveal;
  if (!sr) return null;

  const { escapeXml } = helpers;
  const solved = resolve(cfg, helpers);
  if (!solved) return null;

  const leftColor = sr.leftColor || 'rgba(255,255,255,0.5)';
  const rightColor = sr.rightColor || '#ffffff';
  const labelColor = sr.labelColor || 'rgba(255,255,255,0.4)';
  const accentColor = sr.accentColor || 'rgba(232,93,58,0.8)';

  let nodes = '';
  nodes += `<rect x="${solved.dividerX - 1}" y="${solved.labelY - 10}" width="2" height="${solved.items.length * solved.rowHeight + 60}" rx="1" fill="rgba(255,255,255,0.15)"/>`;
  nodes += `<text x="${solved.leftX}" y="${solved.labelY}" text-anchor="middle" fill="${labelColor}" font-size="${solved.labelSize}" font-family="${solved.font}" font-weight="700" letter-spacing="2">${escapeXml(solved.problemLabel)}</text>`;
  nodes += `<text x="${solved.rightX}" y="${solved.labelY}" text-anchor="middle" fill="${accentColor}" font-size="${solved.labelSize}" font-family="${solved.font}" font-weight="700" letter-spacing="2">${escapeXml(solved.solutionLabel)}</text>`;

  solved.items.forEach((item, i) => {
    const ry = solved.startY + i * solved.rowHeight + 20;
    nodes += `<text x="${solved.leftX}" y="${ry}" text-anchor="middle" fill="${leftColor}" font-size="${solved.textSize}" font-family="${solved.font}" font-weight="400">${escapeXml(item.left || '')}</text>`;
    nodes += `<text x="${solved.rightX}" y="${ry}" text-anchor="middle" fill="${rightColor}" font-size="${solved.textSize}" font-family="${solved.font}" font-weight="600">${escapeXml(item.right || '')}</text>`;
  });

  return {
    id: 'splitReveal',
    svg: Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`),
    imageLayers: [],
    elements: solved.elements,
    warnings: solved.warnings
  };
}

module.exports = {
  id: 'splitReveal',
  configKey: 'splitReveal',
  variants: VARIANTS,
  resolve,
  build
};
