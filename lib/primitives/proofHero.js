function buildProofHeroSvg(cfg, helpers) {
  if (!cfg.proofHero) return null;
  const { wrapText, escapeXml } = helpers;
  const p = cfg.proofHero;
  const quote = p.quote || '';
  const quoteLines = wrapText(quote, p.quoteMaxChars || 16);
  const quoteStep = p.quoteLineHeight || Math.round((p.quoteSize || 64) * 1.08);
  const quoteTspans = quoteLines
    .map((line, i) => `<tspan x="${p.quoteX || 120}" dy="${i === 0 ? 0 : quoteStep}">${escapeXml(line)}</tspan>`)
    .join('');
  const quoteMark = p.quoteMark !== false
    ? `<text x="${p.quoteMarkX || (p.quoteX || 120) - 22}" y="${p.quoteMarkY || (p.quoteY || 110) - 14}" fill="${p.quoteMarkColor || '#ffffff'}" font-size="${p.quoteMarkSize || 92}" font-family="Georgia, serif" font-weight="700">“</text>`
    : '';
  const stars = p.starsText || '★★★★★';
  const starsNode = `<text x="${p.starsX || 260}" y="${p.starsY || 320}" fill="${p.starsColor || '#F4B63D'}" font-size="${p.starsSize || 80}" font-family="Arial, sans-serif" font-weight="700">${escapeXml(stars)}</text>`;
  const eyebrow = p.eyebrow
    ? `<text x="${p.eyebrowX || (p.quoteX || 120)}" y="${p.eyebrowY || 48}" fill="${p.eyebrowColor || 'rgba(255,255,255,0.72)'}" font-size="${p.eyebrowSize || 18}" font-family="${p.eyebrowFontFamily || 'Montserrat, Arial, sans-serif'}" font-weight="${p.eyebrowWeight || 700}" letter-spacing="${p.eyebrowTracking || 2}">${escapeXml(p.eyebrow)}</text>`
    : '';
  const cta = p.cta && p.cta.text ? `
    <rect x="${p.cta.x}" y="${p.cta.y}" width="${p.cta.width}" height="${p.cta.height}" rx="${p.cta.radius || 12}" fill="${p.cta.fill || '#ffffff'}" />
    <text x="${p.cta.x + Math.round(p.cta.width / 2)}" y="${p.cta.y + Math.round(p.cta.height / 2) + (p.cta.textDy || 10)}" text-anchor="middle" fill="${p.cta.textColor || '#141414'}" font-size="${p.cta.fontSize || 28}" font-family="${p.cta.fontFamily || 'Montserrat, Arial, sans-serif'}" font-weight="${p.cta.fontWeight || 800}">${escapeXml(p.cta.text)}</text>` : '';
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${eyebrow}${quoteMark}<text x="${p.quoteX || 120}" y="${p.quoteY || 110}" fill="${p.quoteColor || '#ffffff'}" font-size="${p.quoteSize || 64}" font-family="${p.quoteFontFamily || 'Georgia, Times New Roman, serif'}" font-weight="${p.quoteWeight || 700}" ${p.quoteStyle ? `font-style="${p.quoteStyle}"` : ''}>${quoteTspans}</text>${starsNode}${cta}</svg>`);
}

module.exports = {
  id: 'proofHero',
  buildSvg: buildProofHeroSvg
};
