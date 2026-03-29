'use strict';

const { Rect, Text } = require('../geometry');

/**
 * OfferFrame primitive — price-led promotional layout.
 *
 * Variants:
 *   - 'standard'    : Vertical stack: original → sale price → badge → offer text
 *   - 'hero-price'  : Oversized sale price, compact supporting elements
 *   - 'badge-first' : Savings badge above price for urgency-first layouts
 */

const VARIANTS = {
  'standard': {
    description: 'Vertical stack: original → sale price → badge → offer text',
    priceScale: 1.0,
    badgePosition: 'below',
    spacing: { origToSale: 12, saleToBadge: 30, badgeToOffer: 50 }
  },
  'hero-price': {
    description: 'Oversized sale price, compact supporting elements',
    priceScale: 1.35,
    badgePosition: 'below',
    spacing: { origToSale: 16, saleToBadge: 36, badgeToOffer: 44 }
  },
  'badge-first': {
    description: 'Savings badge above price for urgency-first',
    priceScale: 1.0,
    badgePosition: 'above',
    spacing: { origToSale: 12, saleToBadge: 30, badgeToOffer: 40 }
  }
};

function resolve(cfg, helpers) {
  const of = cfg.offerFrame;
  if (!of) return null;

  const variantName = of.variant || 'standard';
  const variant = VARIANTS[variantName] || VARIANTS.standard;

  const isCentered = (cfg.layout?.personality === 'centered-hero' || cfg.layout?.align === 'center');
  const font = cfg.typography?.headlineFontFamily || 'Montserrat, Arial, sans-serif';
  const bodyFont = cfg.typography?.bodyFontFamily || 'Source Sans Pro, Arial, sans-serif';

  const baseX = isCentered ? Math.round(cfg.width / 2) : (of.priceX || cfg.layout?.leftX || 80);
  const priceY = of.priceY || 600;
  const salePriceSize = Math.round((of.salePriceSize || 72) * variant.priceScale);
  const origPriceSize = of.originalPriceSize || 28;

  const elements = [];

  // Original price
  if (of.originalPrice) {
    const origY = priceY - salePriceSize - variant.spacing.origToSale;
    const origWidth = Text.measureWidth(of.originalPrice, origPriceSize, font, { mode: 'narrow' });
    const origLeft = isCentered ? Math.round(baseX - origWidth / 2) : baseX;
    elements.push({ id: 'offerFrame.originalPrice', type: 'text', fontSize: origPriceSize, rect: Rect.create(origLeft, origY - origPriceSize, origWidth, origPriceSize) });
  }

  // Sale price
  const saleWidth = Text.measureWidth(of.salePrice || '', salePriceSize, font, { mode: 'narrow', fontWeight: 800 });
  const saleLeft = isCentered ? Math.round(baseX - saleWidth / 2) : baseX;
  elements.push({ id: 'offerFrame.salePrice', type: 'text', fontSize: salePriceSize, rect: Rect.create(saleLeft, priceY - salePriceSize, saleWidth, salePriceSize) });

  // Savings badge
  if (of.savings) {
    const badgeWidth = Math.round(of.savings.length * 14 + 32);
    const badgeX = isCentered ? Math.round(baseX - badgeWidth / 2) : baseX;
    const badgeY = priceY + variant.spacing.saleToBadge;
    elements.push({ id: 'offerFrame.badge', type: 'badge', rect: Rect.create(badgeX, badgeY, badgeWidth, 32) });
  }

  // Offer text
  if (of.offerText) {
    const offerY = priceY + (of.savings ? variant.spacing.saleToBadge + 32 + 18 : variant.spacing.badgeToOffer);
    const offerWidth = Text.measureWidth(of.offerText, 20, bodyFont);
    const offerLeft = isCentered ? Math.round(baseX - offerWidth / 2) : baseX;
    elements.push({ id: 'offerFrame.offerText', type: 'text', fontSize: 20, rect: Rect.create(offerLeft, offerY - 20, offerWidth, 20) });
  }

  return { variant: variantName, elements, warnings: [] };
}

function build(cfg, helpers) {
  const of = cfg.offerFrame;
  if (!of) return null;

  const { escapeXml } = helpers;
  const solved = resolve(cfg, helpers);
  if (!solved) return null;

  const variant = VARIANTS[solved.variant] || VARIANTS.standard;
  const isCentered = (cfg.layout?.personality === 'centered-hero' || cfg.layout?.align === 'center');
  const font = cfg.typography?.headlineFontFamily || 'Montserrat, Arial, sans-serif';
  const bodyFont = cfg.typography?.bodyFontFamily || 'Source Sans Pro, Arial, sans-serif';
  const baseX = isCentered ? Math.round(cfg.width / 2) : (of.priceX || cfg.layout?.leftX || 80);
  const anchor = isCentered ? 'middle' : 'start';
  const priceY = of.priceY || 600;
  const salePriceSize = Math.round((of.salePriceSize || 72) * variant.priceScale);
  const origPriceSize = of.originalPriceSize || 28;

  let nodes = '';

  if (of.originalPrice) {
    const origY = priceY - salePriceSize - variant.spacing.origToSale;
    const origTextWidth = Text.measureWidth(of.originalPrice, origPriceSize, font, { mode: 'narrow' });
    const origTextX = isCentered ? Math.round(baseX - origTextWidth / 2) : baseX;
    nodes += `<text x="${baseX}" y="${origY}" text-anchor="${anchor}" fill="rgba(255,255,255,0.45)" font-size="${origPriceSize}" font-family="${font}" font-weight="400">${escapeXml(of.originalPrice)}</text>`;
    nodes += `<rect x="${origTextX - 4}" y="${origY - Math.round(origPriceSize * 0.35)}" width="${origTextWidth + 8}" height="2" fill="rgba(255,255,255,0.6)"/>`;
  }

  nodes += `<text x="${baseX}" y="${priceY}" text-anchor="${anchor}" fill="#ffffff" font-size="${salePriceSize}" font-family="${font}" font-weight="800">${escapeXml(of.salePrice || '')}</text>`;

  if (of.savings) {
    const savingsY = priceY + variant.spacing.saleToBadge;
    const badgeWidth = Math.round(of.savings.length * 14 + 32);
    const badgeX = isCentered ? Math.round(baseX - badgeWidth / 2) : baseX;
    nodes += `<rect x="${badgeX}" y="${savingsY}" width="${badgeWidth}" height="32" rx="16" fill="rgba(40,180,80,0.9)"/>`;
    nodes += `<text x="${badgeX + Math.round(badgeWidth / 2)}" y="${savingsY + 16}" dy="0.35em" text-anchor="middle" fill="#ffffff" font-size="14" font-family="${font}" font-weight="700">${escapeXml(of.savings)}</text>`;
  }

  if (of.offerText) {
    const offerY = priceY + (of.savings ? variant.spacing.saleToBadge + 32 + 18 : variant.spacing.badgeToOffer);
    nodes += `<text x="${baseX}" y="${offerY}" text-anchor="${anchor}" fill="rgba(255,255,255,0.6)" font-size="20" font-family="${bodyFont}" font-weight="500">${escapeXml(of.offerText)}</text>`;
  }

  return {
    id: 'offerFrame',
    svg: Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`),
    imageLayers: [],
    elements: solved.elements,
    warnings: solved.warnings
  };
}

module.exports = {
  id: 'offerFrame',
  configKey: 'offerFrame',
  variants: VARIANTS,
  resolve,
  build
};
