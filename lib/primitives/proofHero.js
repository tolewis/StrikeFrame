function estimateTextWidth(text, fontSize) {
  return Math.round(String(text || '').length * fontSize * 0.58);
}

function rect(x, y, width, height) {
  return {
    x, y, width, height,
    left: x, top: y, right: x + width, bottom: y + height,
    centerX: x + width / 2, centerY: y + height / 2, area: width * height
  };
}

function resolveQuoteLayout(quote, p, helpers, canvasWidth) {
  const { wrapText } = helpers;
  const fontSize = p.quoteSize || 64;
  const maxLines = p.maxQuoteLines || 3;
  const minChars = p.minQuoteMaxChars || 14;
  const maxCharsCap = p.maxQuoteMaxChars || 28;
  const quoteX = p.quoteX || 108;
  const maxWidth = p.maxQuoteWidth || Math.round(canvasWidth * 0.72);

  let bestChars = p.quoteMaxChars || minChars;
  let lines = wrapText(quote, bestChars);

  for (let chars = bestChars; chars <= maxCharsCap; chars += 1) {
    const candidate = wrapText(quote, chars);
    const candidateWidth = Math.max(...candidate.map(line => estimateTextWidth(line, fontSize)));
    if (candidate.length <= maxLines && candidateWidth <= maxWidth) {
      bestChars = chars;
      lines = candidate;
      break;
    }
    if (candidateWidth <= maxWidth) {
      bestChars = chars;
      lines = candidate;
    } else {
      break;
    }
  }

  const quoteLineHeight = p.quoteLineHeight || Math.round(fontSize * 1.08);
  const quoteWidth = Math.min(maxWidth, Math.max(...lines.map(line => estimateTextWidth(line, fontSize))));
  const quoteHeight = lines.length * quoteLineHeight;
  const quoteY = p.quoteY || 110;
  return { quoteX, quoteY, lines, quoteWidth, quoteHeight, quoteLineHeight, quoteMaxChars: bestChars, quoteTop: quoteY - fontSize };
}

function resolveProofHero(cfg, helpers) {
  const p = cfg.proofHero || {};
  const quote = p.quote || p.content?.quote || '';
  const reviewPath = p.reviewPath || p.assets?.reviewPath || null;
  const productPath = p.productPath || p.assets?.productPath || null;
  const ctaText = p.cta?.text || p.content?.cta || null;

  const quoteLayout = resolveQuoteLayout(quote, p, helpers, cfg.width);
  const starsSize = p.starsSize || 90;
  const starsX = p.starsX || quoteLayout.quoteX + 130;
  const starsY = p.starsY || (quoteLayout.quoteTop + quoteLayout.quoteHeight + 72);

  const reviewX = p.reviewX || 118;
  const reviewY = p.reviewY || (starsY + 62);
  const reviewWidth = p.reviewWidth || Math.round(cfg.width * 0.66);
  const reviewHeight = p.reviewHeight || 210;

  const cta = ctaText ? {
    text: ctaText,
    x: p.cta?.x || 110,
    y: p.cta?.y || (cfg.height - 162),
    width: p.cta?.width || 420,
    height: p.cta?.height || 74,
    radius: p.cta?.radius || 12,
    fill: p.cta?.fill || '#FFFFFF',
    textColor: p.cta?.textColor || '#111111',
    fontSize: p.cta?.fontSize || 24,
    fontWeight: p.cta?.fontWeight || 800,
    fontFamily: p.cta?.fontFamily || 'Montserrat, Arial, sans-serif'
  } : null;

  const product = productPath ? {
    path: productPath,
    x: p.productX || (reviewX + reviewWidth - 120),
    y: p.productY || (reviewY + reviewHeight + 18),
    width: p.productWidth || 250,
    height: p.productHeight || 228,
    padding: 0,
    background: p.productBackground || { r: 255, g: 255, b: 255, alpha: 1 },
    fit: p.productFit || 'cover',
    radius: p.productRadius || 16,
    shadow: p.productShadow || { y: 12, color: 'rgba(0,0,0,0.18)' }
  } : null;

  const review = reviewPath ? {
    path: reviewPath,
    x: reviewX,
    y: reviewY,
    width: reviewWidth,
    height: reviewHeight,
    padding: 0,
    background: p.reviewBackground || { r: 255, g: 255, b: 255, alpha: 1 },
    fit: p.reviewFit || 'contain',
    radius: p.reviewRadius || 18,
    stroke: p.reviewStroke || 'rgba(255,255,255,0.10)',
    strokeWidth: p.reviewStrokeWidth || 2,
    shadow: p.reviewShadow || { y: 10, color: 'rgba(0,0,0,0.22)' }
  } : null;

  const elements = [
    { id: 'proofHero.quote', type: 'text', rect: rect(quoteLayout.quoteX, quoteLayout.quoteTop, quoteLayout.quoteWidth, quoteLayout.quoteHeight) },
    { id: 'proofHero.stars', type: 'text', rect: rect(starsX, starsY - starsSize, Math.round(starsSize * 4.2), Math.round(starsSize * 1.2)) }
  ];
  if (review) elements.push({ id: 'proofHero.review', type: 'image', rect: rect(review.x, review.y, review.width, review.height) });
  if (product) elements.push({ id: 'proofHero.product', type: 'image', rect: rect(product.x, product.y, product.width, product.height) });
  if (cta) elements.push({ id: 'proofHero.cta', type: 'cta', rect: rect(cta.x, cta.y, cta.width, cta.height) });

  return {
    quote,
    quoteLayout,
    starsX,
    starsY,
    starsSize,
    cta,
    review,
    product,
    elements,
    warnings: [
      ...(quoteLayout.lines.length > (p.maxQuoteLines || 3) ? ['quote_exceeds_line_target'] : [])
    ]
  };
}

function buildProofHero(cfg, helpers) {
  if (!cfg.proofHero) return null;
  const { escapeXml } = helpers;
  const solved = resolveProofHero(cfg, helpers);
  const p = cfg.proofHero;
  const quoteTspans = solved.quoteLayout.lines
    .map((line, i) => `<tspan x="${solved.quoteLayout.quoteX}" dy="${i === 0 ? 0 : solved.quoteLayout.quoteLineHeight}">${escapeXml(line)}</tspan>`)
    .join('');
  const quoteMark = p.quoteMark !== false
    ? `<text x="${p.quoteMarkX || solved.quoteLayout.quoteX - 34}" y="${p.quoteMarkY || solved.quoteLayout.quoteY - 22}" fill="${p.quoteMarkColor || '#ffffff'}" font-size="${p.quoteMarkSize || 104}" font-family="Georgia, serif" font-weight="700">“</text>`
    : '';
  const closingQuote = p.quoteMark !== false
    ? `<text x="${p.quoteCloseX || (solved.quoteLayout.quoteX + solved.quoteLayout.quoteWidth + 10)}" y="${p.quoteCloseY || (solved.quoteLayout.quoteTop + solved.quoteLayout.quoteHeight - 4)}" fill="${p.quoteMarkColor || '#ffffff'}" font-size="${p.quoteMarkSize || 104}" font-family="Georgia, serif" font-weight="700">”</text>`
    : '';
  const starsNode = `<text x="${solved.starsX}" y="${solved.starsY}" fill="${p.starsColor || '#F4B63D'}" font-size="${solved.starsSize}" font-family="Arial, sans-serif" font-weight="700">${escapeXml(p.starsText || '★★★★★')}</text>`;
  const eyebrow = p.eyebrow
    ? `<text x="${p.eyebrowX || solved.quoteLayout.quoteX}" y="${p.eyebrowY || 48}" fill="${p.eyebrowColor || 'rgba(255,255,255,0.72)'}" font-size="${p.eyebrowSize || 18}" font-family="${p.eyebrowFontFamily || 'Montserrat, Arial, sans-serif'}" font-weight="${p.eyebrowWeight || 700}" letter-spacing="${p.eyebrowTracking || 2}">${escapeXml(p.eyebrow)}</text>`
    : '';
  const cta = solved.cta ? `
    <rect x="${solved.cta.x}" y="${solved.cta.y}" width="${solved.cta.width}" height="${solved.cta.height}" rx="${solved.cta.radius}" fill="${solved.cta.fill}" />
    <text x="${solved.cta.x + Math.round(solved.cta.width / 2)}" y="${solved.cta.y + Math.round(solved.cta.height / 2) + 10}" text-anchor="middle" fill="${solved.cta.textColor}" font-size="${solved.cta.fontSize}" font-family="${solved.cta.fontFamily}" font-weight="${solved.cta.fontWeight}">${escapeXml(solved.cta.text)}</text>` : '';
  const svg = Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${eyebrow}${quoteMark}<text x="${solved.quoteLayout.quoteX}" y="${solved.quoteLayout.quoteY}" fill="${p.quoteColor || '#ffffff'}" font-size="${p.quoteSize || 64}" font-family="${p.quoteFontFamily || 'Georgia, Times New Roman, serif'}" font-weight="${p.quoteWeight || 700}" ${p.quoteStyle ? `font-style="${p.quoteStyle}"` : ''}>${quoteTspans}</text>${closingQuote}${starsNode}${cta}</svg>`);
  const imageLayers = [solved.review, solved.product].filter(Boolean);
  return { id: 'proofHero', svg, imageLayers, elements: solved.elements, warnings: solved.warnings };
}

module.exports = {
  id: 'proofHero',
  build: buildProofHero,
  resolve: resolveProofHero
};
