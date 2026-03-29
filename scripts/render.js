const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const { buildPrimitiveOutputs, getPrimitiveRegistry } = require('../lib/primitives');
const { Rect, Text, SafeZone } = require('../lib/geometry');

const projectRoot = path.resolve(__dirname, '..');
const argPath = process.argv[2] || 'configs/sample-banner.json';
const configPath = path.isAbsolute(argPath) ? argPath : path.join(projectRoot, argPath);

const PRESETS = {
  'landscape-banner': { width: 1600, height: 900 },
  'social-square': { width: 1080, height: 1080 },
  'social-portrait': { width: 1080, height: 1350 },
  'linkedin-landscape': { width: 1200, height: 627 },
  'google-landscape': { width: 1200, height: 628 },
  'google-portrait': { width: 960, height: 1200 }
};

function fileExists(filePath) {
  try { fs.accessSync(filePath, fs.constants.R_OK); return true; } catch { return false; }
}
function ensureDir(filePath) { fs.mkdirSync(path.dirname(filePath), { recursive: true }); }
function escapeXml(value = '') {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}
function wrapText(text, maxChars) {
  const words = String(text || '').split(/\s+/).filter(Boolean);
  const lines = []; let current = '';
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars && current) { lines.push(current); current = word; }
    else current = next;
  }
  if (current) lines.push(current);
  return lines;
}
function presetDefault(preset, portraitValue, defaultValue) { return preset === 'social-portrait' ? portraitValue : defaultValue; }

const LOGO_MODE_DEFAULTS = {
  'white-card-landscape': {
    path: '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/camera-strikeframe/tier1-ready/logo-landscape-1200x300-v2.png',
    width: 250,
    height: 66,
    padding: 8,
    background: { r: 255, g: 255, b: 255, alpha: 1 }
  },
  'transparent-full': {
    path: '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/brand-lifestyle/tier1-ready/TackleRoom 1.1.png',
    width: 220,
    height: 88,
    padding: 0,
    background: { r: 255, g: 255, b: 255, alpha: 0 }
  },
  'compact-square': {
    path: '/home/tlewis/Dropbox/Tim/TackleRoom/Creative/camera-strikeframe/tier1-ready/logo-square-1200x1200-v2.png',
    width: 132,
    height: 132,
    padding: 8,
    background: { r: 255, g: 255, b: 255, alpha: 1 }
  }
};

// --- Icon glyph SVG paths (simple 24x24 viewBox paths) ---
const ICON_PATHS = {
  shield: 'M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z',
  check: 'M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z',
  wave: 'M2 12c1.5-2 3-3 4.5-1s3 1 4.5-1 3-3 4.5-1 3 1 4.5-1M2 17c1.5-2 3-3 4.5-1s3 1 4.5-1 3-3 4.5-1 3 1 4.5-1M2 7c1.5-2 3-3 4.5-1s3 1 4.5-1 3-3 4.5-1 3 1 4.5-1',
  anchor: 'M12 2a3 3 0 00-3 3c0 1.3.84 2.4 2 2.82V11H8v2h3v6.95A8 8 0 014 12H2a10 10 0 0010 10 10 10 0 0010-10h-2a8 8 0 01-7 7.95V13h3v-2h-3V7.82A3 3 0 0015 5a3 3 0 00-3-3zm0 2a1 1 0 110 2 1 1 0 010-2z',
  gear: 'M19.14 12.94c.04-.3.06-.61.06-.94s-.02-.64-.07-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.49.49 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.48.48 0 00-.48-.41h-3.84a.48.48 0 00-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.49.49 0 00-.59.22L2.74 8.87a.48.48 0 00.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.26.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6A3.6 3.6 0 1115.6 12 3.6 3.6 0 0112 15.6z',
  arrow: 'M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8-8-8z',
  target: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm0-6a2 2 0 100 4 2 2 0 000-4z',
  fish: 'M12 20l-2-2c-3-3-8-6-8-10a4 4 0 018 0 4 4 0 018 0c0 4-5 7-8 10l1 1zM18 6a6 6 0 00-6 6c2.5-2.5 6-5 6-6z'
};

function buildIconGlyphSvg(type, x, y, size, color) {
  const pathData = ICON_PATHS[type] || ICON_PATHS.check;
  const scale = size / 24;
  const isStroke = (type === 'wave');
  const fill = isStroke ? 'none' : color;
  const stroke = isStroke ? `stroke="${color}" stroke-width="2" stroke-linecap="round"` : '';
  return `<g transform="translate(${x},${y}) scale(${scale})"><path d="${pathData}" fill="${fill}" ${stroke}/></g>`;
}

function resolveLogoLayer(cfg) {
  if (!cfg.logoMode) return null;
  const mode = LOGO_MODE_DEFAULTS[cfg.logoMode];
  if (!mode) return null;
  const marginX = (cfg.logo && cfg.logo.x != null) ? cfg.logo.x : 60;
  const marginY = (cfg.logo && cfg.logo.y != null) ? cfg.logo.y : 40;
  const placement = (cfg.logo && cfg.logo.placement) || 'default';
  const corner = (cfg.logo && cfg.logo.corner) || 'top-left';
  return Object.assign({}, mode, cfg.logo || {}, { x: marginX, y: marginY, fit: (cfg.logo && cfg.logo.fit) || 'contain', placement, corner });
}

async function buildCornerAnchorLogo(cfg, logoResolved) {
  if (!logoResolved || logoResolved.placement !== 'corner-anchor') return null;
  const logoW = logoResolved.width || 250;
  const logoH = logoResolved.height || 66;
  const clearSpace = logoResolved.clearSpace || Math.round(logoH * 0.2);
  const corner = logoResolved.corner || 'top-left';

  // Consistent padding on all four sides per logo guidelines.
  const pad = clearSpace;
  const bgColor = logoResolved.background || { r: 255, g: 255, b: 255, alpha: 1 };
  const radius = logoResolved.panelRadius || 0;

  // Trim internal whitespace from logo source before resizing so the panel
  // fits the actual visible content, not the file's baked-in padding.
  const trimmedBuf = await sharp(logoResolved.path).trim().ensureAlpha().png().toBuffer();
  const logoBuf = await sharp(trimmedBuf)
    .resize({ width: logoW, height: logoH, fit: 'inside', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .ensureAlpha()
    .png()
    .toBuffer();
  const logoMeta = await sharp(logoBuf).metadata();

  // Panel dimensions: equal padding on all four sides, built from ACTUAL rendered logo size
  const actualLogoW = logoMeta.width;
  const actualLogoH = logoMeta.height;
  const panelW = pad + actualLogoW + pad;
  const panelH = pad + actualLogoH + pad;
  let panelX = 0, panelY = 0;
  let logoX = 0, logoY = 0;

  if (corner === 'top-left') {
    panelX = 0; panelY = 0;
    logoX = pad;
    logoY = pad;
  } else if (corner === 'top-right') {
    panelX = cfg.width - panelW; panelY = 0;
    logoX = panelX + pad;
    logoY = pad;
  } else if (corner === 'bottom-left') {
    panelX = 0; panelY = cfg.height - panelH;
    logoX = pad;
    logoY = panelY + pad;
  } else if (corner === 'bottom-right') {
    panelX = cfg.width - panelW; panelY = cfg.height - panelH;
    logoX = panelX + pad;
    logoY = panelY + pad;
  }

  const r = radius || Math.round(Math.min(panelW, panelH) * 0.08);

  // SVG panel with one rounded inner corner only
  let panelPath;
  if (corner === 'top-left') {
    panelPath = `M0,0 H${panelW} V${panelH - r} Q${panelW},${panelH} ${panelW - r},${panelH} H0 Z`;
  } else if (corner === 'top-right') {
    panelPath = `M0,0 H${panelW} V${panelH} H${r} Q0,${panelH} 0,${panelH - r} V0 Z`;
  } else if (corner === 'bottom-left') {
    panelPath = `M0,0 V${panelH} H${panelW} V${r} Q${panelW},0 ${panelW - r},0 H0 Z`;
  } else {
    panelPath = `M${r},0 H${panelW} V${panelH} H0 V0 Q0,0 ${r},0 Z`;
  }

  const panelSvg = Buffer.from(`<svg width="${panelW}" height="${panelH}" xmlns="http://www.w3.org/2000/svg"><path d="${panelPath}" fill="rgba(${bgColor.r || 255},${bgColor.g || 255},${bgColor.b || 255},${bgColor.alpha != null ? bgColor.alpha : 1})"/></svg>`);

  return {
    panelBuf: panelSvg,
    panelX, panelY, panelW, panelH,
    logoBuf, logoX, logoY,
    logoW: logoMeta.width, logoH: logoMeta.height
  };
}

function buildBadgesSvg(cfg) {
  if (!cfg.badges || !cfg.badges.length) return null;
  const nodes = cfg.badges.map((b) => {
    const fontSize = b.fontSize || 16;
    const text = String(b.text || '').trim();
    const textLen = text.length;
    const padX = b.paddingX || 24;
    const width = b.width || Math.max(100, Math.round(textLen * fontSize * 0.62 + padX * 2));
    const height = b.height || 36;
    const rx = b.radius || Math.round(height / 2);
    const fill = b.fill || 'rgba(232,93,58,0.92)';
    const textColor = b.textColor || '#ffffff';
    const fontFamily = b.fontFamily || 'Montserrat, Arial, sans-serif';
    const fontWeight = b.fontWeight || 700;
    const textX = (b.x || 0) + Math.round(width / 2);
    const textY = (b.y || 0) + Math.round(height / 2);
    return `<rect x="${b.x || 0}" y="${b.y || 0}" width="${width}" height="${height}" rx="${rx}" fill="${fill}"/>` +
      `<text x="${textX}" y="${textY}" dy="0.35em" text-anchor="middle" fill="${textColor}" font-size="${fontSize}" font-family="${fontFamily}" font-weight="${fontWeight}">${escapeXml(text)}</text>`;
  }).join('\n');
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildStarRatingSvg(x, y, stars, size, cfg) {
  const gap = Math.round(size * 0.25);
  const total = 5;
  const nodes = [];
  for (let i = 0; i < total; i++) {
    const sx = x + i * (size + gap);
    const color = i < stars ? '#FFD700' : 'rgba(255,255,255,0.2)';
    nodes.push(`<text x="${sx}" y="${y}" fill="${color}" font-size="${size}" font-family="Arial">★</text>`);
  }
  return nodes.join('\n');
}

function buildBenefitStackSvg(cfg) {
  if (!cfg.benefitStack || !cfg.benefitStack.items || !cfg.benefitStack.items.length) return null;
  const bs = cfg.benefitStack;
  const startX = bs.startX || cfg.layout.leftX || 80;
  const startY = bs.startY || 580;
  const spacing = bs.spacing || 90;
  const iconSize = bs.iconSize || 36;
  const textSize = bs.textSize || 28;
  const iconColor = bs.iconColor || '#63b3ed';
  const textColor = bs.textColor || '#ffffff';
  const textMaxChars = bs.textMaxChars || 32;
  const textFont = bs.fontFamily || cfg.typography.bodyFontFamily;

  const nodes = bs.items.map((item, i) => {
    const iy = startY + i * spacing;
    const iconCenterY = iy - Math.round(iconSize / 2);
    const icon = buildIconGlyphSvg(item.icon || 'check', startX, iconCenterY, iconSize, item.color || iconColor);
    const textX = startX + iconSize + 16;
    const lines = wrapText(item.label || '', textMaxChars);
    const lineStep = Math.round(textSize * 1.2);
    const tspans = lines.map((line, li) => `<tspan x="${textX}" dy="${li === 0 ? 0 : lineStep}">${escapeXml(line)}</tspan>`).join('');
    return `${icon}<text x="${textX}" y="${iy}" fill="${textColor}" font-size="${textSize}" font-family="${textFont}" font-weight="600">${tspans}</text>`;
  }).join('\n');

  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildTestimonialSvg(cfg) {
  if (!cfg.testimonial) return null;
  const t = cfg.testimonial;
  const quoteSize = t.quoteSize || 36;
  const nameSize = t.nameSize || 22;
  const starSize = t.starSize || 32;
  const quoteColor = t.quoteColor || '#ffffff';
  const attributionColor = t.attributionColor || 'rgba(255,255,255,0.7)';
  const maxChars = t.quoteMaxChars || 28;
  const quoteFont = t.fontFamily || cfg.typography.bodyFontFamily;
  const isCentered = (cfg.layout.personality === 'centered-hero' || cfg.layout.align === 'center');
  const anchor = isCentered ? 'middle' : 'start';
  const baseX = isCentered ? Math.round(cfg.width / 2) : (cfg.layout.leftX || 80);
  const quoteMarkY = t.startY || 300;
  const quoteTextY = quoteMarkY + 80;
  const quoteLineStep = Math.round(quoteSize * 1.35);
  const lines = wrapText(t.quote || '', maxChars);
  const tspans = lines.map((line, i) => `<tspan x="${baseX}" dy="${i === 0 ? 0 : quoteLineStep}">${escapeXml(line)}</tspan>`).join('');
  const quoteBlockHeight = (lines.length - 1) * quoteLineStep + quoteSize;
  const starsY = quoteTextY + quoteBlockHeight + 40;
  const starsTotalWidth = 5 * (starSize + Math.round(starSize * 0.25)) - Math.round(starSize * 0.25);
  const starsX = isCentered ? Math.round(baseX - starsTotalWidth / 2) : baseX;
  const starsSvg = buildStarRatingSvg(starsX, starsY, t.stars || 5, starSize, cfg);
  const nameY = starsY + starSize + 24;
  const roleY = nameY + nameSize + 8;
  const quoteMarkX = isCentered ? Math.round(baseX - 20) : baseX;

  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
    <text x="${quoteMarkX}" y="${quoteMarkY}" fill="${t.quoteMarkColor || 'rgba(232,93,58,0.8)'}" font-size="120" font-family="Georgia, serif" font-weight="700">\u201C</text>
    <text x="${baseX}" y="${quoteTextY}" text-anchor="${anchor}" fill="${quoteColor}" font-size="${quoteSize}" font-family="${quoteFont}" font-weight="500" font-style="italic">${tspans}</text>
    ${starsSvg}
    <text x="${baseX}" y="${nameY}" text-anchor="${anchor}" fill="${quoteColor}" font-size="${nameSize}" font-family="${cfg.typography.headlineFontFamily}" font-weight="700">${escapeXml(t.name || '')}</text>
    <text x="${baseX}" y="${roleY}" text-anchor="${anchor}" fill="${attributionColor}" font-size="${Math.round(nameSize * 0.82)}" font-family="${cfg.typography.bodyFontFamily}" font-weight="400">${escapeXml(t.role || '')}</text>
  </svg>`);
}

function buildSplitRevealSvg(cfg) {
  if (!cfg.splitReveal) return null;
  const sr = cfg.splitReveal;
  const dividerX = sr.dividerX || Math.round(cfg.width / 2);
  const startY = sr.startY || 400;
  const rowHeight = sr.rowHeight || 60;
  const textSize = sr.textSize || 24;
  const labelSize = sr.labelSize || 16;
  const leftColor = sr.leftColor || 'rgba(255,255,255,0.5)';
  const rightColor = sr.rightColor || '#ffffff';
  const labelColor = sr.labelColor || 'rgba(255,255,255,0.4)';
  const accentColor = sr.accentColor || 'rgba(232,93,58,0.8)';
  const font = cfg.typography.bodyFontFamily;
  const leftX = sr.leftX || Math.round(dividerX / 2);
  const rightX = sr.rightX || Math.round(dividerX + (cfg.width - dividerX) / 2);
  const labelY = startY - 30;

  let nodes = '';
  // Divider line
  nodes += `<rect x="${dividerX - 1}" y="${labelY - 10}" width="2" height="${(sr.items || []).length * rowHeight + 60}" rx="1" fill="rgba(255,255,255,0.15)"/>`;
  // Labels
  nodes += `<text x="${leftX}" y="${labelY}" text-anchor="middle" fill="${labelColor}" font-size="${labelSize}" font-family="${font}" font-weight="700" letter-spacing="2">${escapeXml(sr.problemLabel || 'THE PROBLEM')}</text>`;
  nodes += `<text x="${rightX}" y="${labelY}" text-anchor="middle" fill="${accentColor}" font-size="${labelSize}" font-family="${font}" font-weight="700" letter-spacing="2">${escapeXml(sr.solutionLabel || 'THE FIX')}</text>`;
  // Rows
  (sr.items || []).forEach((item, i) => {
    const ry = startY + i * rowHeight + 20;
    nodes += `<text x="${leftX}" y="${ry}" text-anchor="middle" fill="${leftColor}" font-size="${textSize}" font-family="${font}" font-weight="400">${escapeXml(item.left || '')}</text>`;
    nodes += `<text x="${rightX}" y="${ry}" text-anchor="middle" fill="${rightColor}" font-size="${textSize}" font-family="${font}" font-weight="600">${escapeXml(item.right || '')}</text>`;
  });

  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildOfferFrameSvg(cfg) {
  if (!cfg.offerFrame) return null;
  const of = cfg.offerFrame;
  const isCentered = (cfg.layout.personality === 'centered-hero' || cfg.layout.align === 'center');
  const baseX = isCentered ? Math.round(cfg.width / 2) : (of.priceX || cfg.layout.leftX || 80);
  const anchor = isCentered ? 'middle' : 'start';
  const priceY = of.priceY || 600;
  const salePriceSize = of.salePriceSize || 72;
  const origPriceSize = of.originalPriceSize || 28;
  const font = cfg.typography.headlineFontFamily;

  let nodes = '';
  // Original price with strikethrough
  if (of.originalPrice) {
    const origY = priceY - salePriceSize - 12;
    const origTextWidth = Text.measureWidth(of.originalPrice, origPriceSize, font, { mode: 'narrow' });
    const origTextX = isCentered ? Math.round(baseX - origTextWidth / 2) : baseX;
    nodes += `<text x="${baseX}" y="${origY}" text-anchor="${anchor}" fill="rgba(255,255,255,0.45)" font-size="${origPriceSize}" font-family="${font}" font-weight="400">${escapeXml(of.originalPrice)}</text>`;
    nodes += `<rect x="${origTextX - 4}" y="${origY - Math.round(origPriceSize * 0.35)}" width="${origTextWidth + 8}" height="2" fill="rgba(255,255,255,0.6)"/>`;
  }
  // Sale price
  nodes += `<text x="${baseX}" y="${priceY}" text-anchor="${anchor}" fill="#ffffff" font-size="${salePriceSize}" font-family="${font}" font-weight="800">${escapeXml(of.salePrice || '')}</text>`;
  // Savings badge
  if (of.savings) {
    const savingsY = priceY + 30;
    const badgeWidth = Math.round(of.savings.length * 14 + 32);
    const badgeX = isCentered ? Math.round(baseX - badgeWidth / 2) : baseX;
    nodes += `<rect x="${badgeX}" y="${savingsY}" width="${badgeWidth}" height="32" rx="16" fill="rgba(40,180,80,0.9)"/>`;
    nodes += `<text x="${badgeX + Math.round(badgeWidth / 2)}" y="${savingsY + 16}" dy="0.35em" text-anchor="middle" fill="#ffffff" font-size="14" font-family="${font}" font-weight="700">${escapeXml(of.savings)}</text>`;
  }
  // Offer text
  if (of.offerText) {
    const offerY = priceY + (of.savings ? 80 : 40);
    nodes += `<text x="${baseX}" y="${offerY}" text-anchor="${anchor}" fill="rgba(255,255,255,0.6)" font-size="20" font-family="${cfg.typography.bodyFontFamily}" font-weight="500">${escapeXml(of.offerText)}</text>`;
  }

  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildComparisonTableSvg(cfg) {
  if (!cfg.comparisonTable) return null;
  const ct = cfg.comparisonTable;
  const startX = ct.startX || 60;
  const startY = ct.startY || 350;
  const colWidth = ct.colWidth || Math.round((cfg.width - startX * 2 - 40) / 2);
  const rowHeight = ct.rowHeight || 60;
  const headerSize = ct.headerSize || 24;
  const bodySize = ct.bodySize || 20;
  const font = cfg.typography.bodyFontFamily;
  const headFont = cfg.typography.headlineFontFamily;
  const highlightCol = ct.highlightCol || 'right';
  const leftCenter = startX + Math.round(colWidth / 2);
  const rightCenter = startX + colWidth + 40 + Math.round(colWidth / 2);
  const dividerX = startX + colWidth + 19;
  const rows = ct.rows || [];
  const headerY = startY;
  const rowStartY = startY + 50;

  let nodes = '';
  // Highlight column background
  if (highlightCol === 'right') {
    nodes += `<rect x="${startX + colWidth + 20}" y="${startY - 20}" width="${colWidth + 20}" height="${rows.length * rowHeight + 80}" rx="16" fill="rgba(232,93,58,0.08)" stroke="rgba(232,93,58,0.2)" stroke-width="1"/>`;
  } else {
    nodes += `<rect x="${startX - 10}" y="${startY - 20}" width="${colWidth + 20}" height="${rows.length * rowHeight + 80}" rx="16" fill="rgba(232,93,58,0.08)" stroke="rgba(232,93,58,0.2)" stroke-width="1"/>`;
  }
  // Column headers
  const leftHeaderColor = ct.leftHeaderColor || ct.leftTextColor || 'rgba(255,255,255,0.5)';
  const leftBodyColor = ct.leftTextColor || 'rgba(255,255,255,0.5)';
  nodes += `<text x="${leftCenter}" y="${headerY}" text-anchor="middle" fill="${leftHeaderColor}" font-size="${headerSize}" font-family="${headFont}" font-weight="700" letter-spacing="1">${escapeXml((ct.leftHeader || 'STATUS QUO').toUpperCase())}</text>`;
  nodes += `<text x="${rightCenter}" y="${headerY}" text-anchor="middle" fill="rgba(232,93,58,0.92)" font-size="${headerSize}" font-family="${headFont}" font-weight="700" letter-spacing="1">${escapeXml((ct.rightHeader || 'TACKLEROOM').toUpperCase())}</text>`;
  // Divider
  const dividerColor = ct.dividerColor || 'rgba(255,255,255,0.25)';
  const dividerWidth = ct.dividerWidth || 3;
  nodes += `<rect x="${dividerX}" y="${startY - 10}" width="${dividerWidth}" height="${rows.length * rowHeight + 60}" rx="1" fill="${dividerColor}"/>`;
  // Icon sizing
  const iconSize = ct.iconSize || Math.round(bodySize * 1.6);
  const iconGap = ct.iconGap || Math.round(iconSize * 0.5);
  const badColor = ct.badColor || '#e05050';
  const goodColor = ct.goodColor || '#4ade80';
  const textLeftX = startX + iconSize + iconGap;
  const textRightX = startX + colWidth + 40 + iconSize + iconGap;

  // Rows
  rows.forEach((row, i) => {
    const ry = rowStartY + i * rowHeight + 30;
    // Row separator line
    if (i > 0) {
      nodes += `<rect x="${startX}" y="${ry - Math.round(rowHeight / 2) - 5}" width="${colWidth * 2 + 40}" height="1" fill="rgba(255,255,255,0.06)"/>`;
    }
    // Strip leading icon characters from text
    const leftText = (row.left || '').replace(/^[✗✕✖×xX]\s*/u, '').replace(/^\s*/, '');
    const rightText = (row.right || '').replace(/^[✓✔✅]\s*/u, '').replace(/^\s*/, '');

    // Left column: red X icon + text
    const leftIconY = ry - Math.round(iconSize * 0.35);
    nodes += `<text x="${startX + Math.round(iconSize / 2)}" y="${ry}" text-anchor="middle" fill="${badColor}" font-size="${iconSize}" font-family="${headFont}" font-weight="900">✗</text>`;
    nodes += `<text x="${textLeftX}" y="${ry}" text-anchor="start" fill="${leftBodyColor}" font-size="${bodySize}" font-family="${font}" font-weight="400">${escapeXml(leftText)}</text>`;

    // Right column: green check icon + text
    nodes += `<text x="${startX + colWidth + 40 + Math.round(iconSize / 2)}" y="${ry}" text-anchor="middle" fill="${goodColor}" font-size="${iconSize}" font-family="${headFont}" font-weight="900">✓</text>`;
    nodes += `<text x="${textRightX}" y="${ry}" text-anchor="start" fill="#ffffff" font-size="${bodySize}" font-family="${font}" font-weight="600">${escapeXml(rightText)}</text>`;
  });

  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildAuthorityBarSvg(cfg) {
  if (!cfg.authorityBar) return null;
  const ab = cfg.authorityBar;
  const pubs = ab.publications || [];
  if (!pubs.length) return null;
  const barY = ab.barY || Math.round(cfg.height * 0.75);
  const barHeight = ab.barHeight || 40;
  const textSize = ab.textSize || 14;
  const textColor = ab.textColor || 'rgba(255,255,255,0.5)';
  const barFill = ab.barFill || 'rgba(255,255,255,0.06)';
  const font = cfg.typography.bodyFontFamily;
  const joined = pubs.join('  \u2022  ');
  const centerX = Math.round(cfg.width / 2);

  let nodes = '';
  nodes += `<rect x="0" y="${barY}" width="${cfg.width}" height="${barHeight}" fill="${barFill}"/>`;
  nodes += `<text x="${centerX}" y="${barY + Math.round(barHeight / 2)}" dy="0.35em" text-anchor="middle" fill="${textColor}" font-size="${textSize}" font-family="${font}" font-weight="600" letter-spacing="2">${escapeXml(joined.toUpperCase())}</text>`;

  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

async function removeWhiteBackground(inputBuffer) {
  const { data, info } = await sharp(inputBuffer).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const { width, height, channels } = info;
  const pixels = Buffer.from(data);
  const total = width * height;
  const minCh = (k) => { const i = k * channels; return Math.min(pixels[i], pixels[i + 1], pixels[i + 2]); };
  // Analyze edge pixels to pick strategy
  const edgeBri = [];
  for (let x = 0; x < width; x++) {
    for (const y of [0, 1, height - 1, height - 2]) edgeBri.push(minCh(y * width + x));
  }
  for (let y = 2; y < height - 2; y++) {
    for (const x of [0, 1, width - 1, width - 2]) edgeBri.push(minCh(y * width + x));
  }
  edgeBri.sort((a, b) => a - b);
  const p50 = edgeBri[Math.floor(edgeBri.length * 0.5)];
  if (p50 >= 245) {
    // Clean white background — flood fill from edges
    const threshold = 240;
    const visited = new Uint8Array(total);
    const queue = new Int32Array(total);
    let head = 0, tail = 0;
    const isWhite = (k) => minCh(k) >= threshold;
    const seed = (x, y) => {
      const k = y * width + x;
      if (!visited[k] && isWhite(k)) { visited[k] = 1; queue[tail++] = k; }
    };
    for (let x = 0; x < width; x++) { seed(x, 0); seed(x, height - 1); }
    for (let y = 1; y < height - 1; y++) { seed(0, y); seed(width - 1, y); }
    while (head < tail) {
      const k = queue[head++];
      pixels[k * channels + 3] = 0;
      const cx = k % width, cy = (k - cx) / width;
      if (cx > 0) seed(cx - 1, cy);
      if (cx < width - 1) seed(cx + 1, cy);
      if (cy > 0) seed(cx, cy - 1);
      if (cy < height - 1) seed(cx, cy + 1);
    }
  } else {
    // Gradient/gray background — soft brightness mask
    const threshold = Math.max(p50 - 5, 200);
    const feather = 30;
    for (let k = 0; k < total; k++) {
      const b = minCh(k);
      if (b >= threshold) {
        pixels[k * channels + 3] = 0;
      } else if (b >= threshold - feather) {
        pixels[k * channels + 3] = Math.round(255 * (threshold - b) / feather);
      }
    }
  }
  return sharp(pixels, { raw: { width, height, channels } }).png().toBuffer();
}

// Map Google presets to layout-equivalent presets for default calculations
const PRESET_LAYOUT_ALIAS = {
  'google-landscape': 'linkedin-landscape',
  'google-portrait': 'social-portrait'
};

function normalizeConfig(raw) {
  const preset = PRESETS[raw.preset || 'landscape-banner'];
  if (!preset) throw new Error(`Unknown preset: ${raw.preset}`);
  // Use alias for layout defaults so Google presets inherit correct positioning
  const chosenPreset = PRESET_LAYOUT_ALIAS[raw.preset] || raw.preset || 'landscape-banner';
  const cfg = {
    preset: chosenPreset,
    template: raw.template || 'banner',
    width: raw.width || preset.width,
    height: raw.height || preset.height,
    output: path.isAbsolute(raw.output || '') ? raw.output : path.join(projectRoot, raw.output || 'output/render.jpg'),
    backgroundPath: raw.backgroundPath,
    backgroundPosition: raw.backgroundPosition || null,
    productPath: raw.productPath || null,
    overlay: Object.assign({ leftOpacity: 0.78, midOpacity: 0.32, rightOpacity: 0.08, vignetteBottom: 0.28, leftColor: '8,12,21', midColor: '12,20,35', rightColor: '18,32,52' }, raw.overlay || {}),
    text: Object.assign({ headline: 'Headline goes here', subhead: 'Subhead goes here', cta: 'LEARN MORE', footer: 'STRIKEFRAME' }, raw.text || {}),
    theme: Object.assign({
      headlineColor: '#ffffff', subheadColor: '#c8d8e8', footerColor: '#8fa8c0', ctaTextColor: '#ffffff',
      ctaFill: 'rgba(255,255,255,0.28)', ctaStroke: 'rgba(255,255,255,0.50)', gradientStart: '#0b2a40', gradientEnd: '#1f6b8f',
      badgeFill: 'rgba(255,255,255,0.16)', badgeStroke: 'rgba(255,255,255,0.24)', badgeTextColor: '#ffffff',
      productCircleFill: 'rgba(255,255,255,0.94)', productShadowColor: '0,0,0', textPanelFill: 'rgba(255,255,255,0.08)', textPanelStroke: 'rgba(255,255,255,0.16)'
    }, raw.theme || {}),
    typography: Object.assign({
      headlineFontFamily: 'Montserrat, Arial, sans-serif', bodyFontFamily: 'Source Sans Pro, Arial, sans-serif',
      headlineWeight: 700, subheadWeight: 400, ctaWeight: 700, footerWeight: 600,
      headlineSize: presetDefault(chosenPreset, 66, chosenPreset === 'linkedin-landscape' ? 58 : 78),
      subheadSize: presetDefault(chosenPreset, 30, chosenPreset === 'linkedin-landscape' ? 28 : 32),
      ctaSize: 28, footerSize: presetDefault(chosenPreset, 18, chosenPreset === 'linkedin-landscape' ? 18 : 21),
      subheadLineHeight: null,
      footerTracking: 3
    }, raw.typography || {}),
    layout: Object.assign({
      personality: 'editorial-left', align: 'left', leftX: 120,
      headlineY: chosenPreset === 'social-portrait' ? 180 : (chosenPreset === 'linkedin-landscape' ? 140 : 168),
      subheadY: chosenPreset === 'social-portrait' ? 470 : (chosenPreset === 'linkedin-landscape' ? 320 : 392),
      ctaX: 132, ctaY: chosenPreset === 'social-portrait' ? 650 : (chosenPreset === 'linkedin-landscape' ? 466 : 560),
      footerY: chosenPreset === 'social-portrait' ? preset.height - 84 : (chosenPreset === 'linkedin-landscape' ? 565 : preset.height - 88),
      maxHeadlineChars: chosenPreset === 'social-portrait' ? 18 : (chosenPreset === 'linkedin-landscape' ? 24 : 22),
      maxSubheadChars: chosenPreset === 'social-portrait' ? 28 : (chosenPreset === 'linkedin-landscape' ? 46 : 42),
      ctaWidth: chosenPreset === 'linkedin-landscape' ? 300 : 274, ctaHeight: 64, ctaRectX: 96,
      ctaRectY: chosenPreset === 'social-portrait' ? 612 : (chosenPreset === 'linkedin-landscape' ? 428 : 522),
      ctaGroup: null,
      panelX: 80, panelY: chosenPreset === 'social-portrait' ? 110 : 90,
      panelWidth: chosenPreset === 'social-portrait' ? 840 : (chosenPreset === 'linkedin-landscape' ? 700 : 760),
      panelHeight: chosenPreset === 'social-portrait' ? 760 : (chosenPreset === 'linkedin-landscape' ? 390 : 600),
      minHeadlineCtaGap: 40
    }, raw.layout || {}),
    productComposite: Object.assign({
      enabled: raw.template === 'product-composite', circleDiameter: chosenPreset === 'social-portrait' ? 360 : 300,
      circleX: chosenPreset === 'social-portrait' ? preset.width - 420 : preset.width - 380,
      circleY: chosenPreset === 'social-portrait' ? 260 : 180, shadowOpacity: 0.16,
      productWidth: chosenPreset === 'social-portrait' ? 260 : 230, productOffsetX: 35, productOffsetY: 35,
      badgeText: 'PRODUCT', badgeX: chosenPreset === 'social-portrait' ? preset.width - 360 : preset.width - 330,
      badgeY: chosenPreset === 'social-portrait' ? 180 : 120
    }, raw.productComposite || {}),
    review: Object.assign({ enforcePanelFit: true }, raw.review || {}),
    designIntent: raw.designIntent || null,
    constraintPolicy: raw.constraintPolicy || null,
    productImage: raw.productImage || null,
    logoPath: raw.logoPath || null,
    logoMode: raw.logoMode || null,
    logo: Object.assign({
      enabled: !!raw.logoPath,
      width: 120,
      height: 120,
      x: null,
      y: null,
      opacity: 0.85
    }, raw.logo || {}),
    imageLayers: Array.isArray(raw.imageLayers) ? raw.imageLayers : [],
    shapes: Array.isArray(raw.shapes) ? raw.shapes : [],
    textLayers: Array.isArray(raw.textLayers) ? raw.textLayers : [],
    statBlocks: Array.isArray(raw.statBlocks) ? raw.statBlocks : [],
    dividers: Array.isArray(raw.dividers) ? raw.dividers : [],
    // New template-specific config keys
    benefitStack: raw.benefitStack || null,
    testimonial: raw.testimonial || null,
    splitReveal: raw.splitReveal || null,
    offerFrame: raw.offerFrame || null,
    comparisonTable: raw.comparisonTable || null,
    authorityBar: raw.authorityBar || null,
    proofHero: raw.proofHero || null,
    badges: Array.isArray(raw.badges) ? raw.badges : null
  };
  if (cfg.review.enforcePanelFit && cfg.layout.personality === 'split-card') {
    const panelPad = 40;
    const panelLeft = cfg.layout.panelX + panelPad;
    const panelTop = cfg.layout.panelY + panelPad;
    const estHeadlineTop = cfg.layout.headlineY - Math.round(cfg.typography.headlineSize * 0.82);
    if (estHeadlineTop < panelTop) cfg.layout.headlineY += (panelTop - estHeadlineTop);
    if (cfg.layout.ctaRectX < panelLeft) {
      const shift = panelLeft - cfg.layout.ctaRectX;
      cfg.layout.ctaRectX += shift;
      cfg.layout.ctaX += shift;
    }
    if (cfg.layout.leftX < panelLeft) cfg.layout.leftX = panelLeft;
    const headlineLines = wrapText(cfg.text.headline, cfg.layout.maxHeadlineChars);
    const subheadLines = wrapText(cfg.text.subhead, cfg.layout.maxSubheadChars);
    const estHeadlineW = Math.max(...headlineLines.map(l => Text.measureWidth(l, cfg.typography.headlineSize, cfg.typography.headlineFontFamily, { fontWeight: cfg.typography.headlineWeight })));
    const estSubheadW = Math.max(...subheadLines.map(l => Text.measureWidth(l, cfg.typography.subheadSize, cfg.typography.bodyFontFamily)));
    const maxTextRight = cfg.layout.leftX + Math.max(estHeadlineW, estSubheadW, cfg.layout.ctaWidth);
    const requiredWidth = maxTextRight - cfg.layout.panelX + panelPad;
    const maxPanelWidth = cfg.width - cfg.layout.panelX - 40;
    if (requiredWidth > cfg.layout.panelWidth) cfg.layout.panelWidth = Math.min(requiredWidth, maxPanelWidth);
    const estimatedPanelBottom = cfg.layout.ctaRectY + cfg.layout.ctaHeight + 40;
    const requiredHeight = estimatedPanelBottom - cfg.layout.panelY;
    if (requiredHeight > cfg.layout.panelHeight) cfg.layout.panelHeight = requiredHeight;
  }

  // --- minHeadlineCtaGap enforcement ---
  // Compute estimated headline box (same approach as estimateTextBlock)
  {
    const minGap = cfg.layout.minHeadlineCtaGap;
    const headlineLines = wrapText(cfg.text.headline, cfg.layout.maxHeadlineChars);
    const headlineStep = preset.height >= 1350 ? 82 : (chosenPreset === 'linkedin-landscape' ? 68 : 88);
    const isCentered = cfg.layout.personality === 'centered-hero' || cfg.layout.align === 'center';
    const textX = isCentered ? Math.round(cfg.width / 2) : cfg.layout.leftX;
    const headlineEstHeight = Math.round(cfg.typography.headlineSize + ((Math.max(headlineLines.length, 1) - 1) * headlineStep));
    const headlineTop = Math.round(cfg.layout.headlineY - cfg.typography.headlineSize * 0.82);
    const headlineBottom = headlineTop + headlineEstHeight;

    const gap = cfg.layout.ctaRectY - headlineBottom;
    if (gap < minGap) {
      const deficit = minGap - gap;
      // Try pushing CTA down first
      const safeZoneBottom = cfg.height - 40 - cfg.layout.ctaHeight;
      const newCtaRectY = cfg.layout.ctaRectY + deficit;
      if (newCtaRectY <= safeZoneBottom) {
        cfg.layout.ctaRectY = newCtaRectY;
        cfg.layout.ctaY = newCtaRectY + Math.round(cfg.layout.ctaHeight / 2);
      } else {
        // CTA would go below safe zone — push headlineY UP instead
        cfg.layout.headlineY -= deficit;
      }
    }
  }

  return cfg;
}

function buildOverlaySvg(cfg) {
  const { width, height, overlay } = cfg;
  return Buffer.from(`
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="rgba(${overlay.leftColor},${overlay.leftOpacity})"/>
          <stop offset="58%" stop-color="rgba(${overlay.midColor},${overlay.midOpacity})"/>
          <stop offset="100%" stop-color="rgba(${overlay.rightColor},${overlay.rightOpacity})"/>
        </linearGradient>
        <linearGradient id="vignette" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(0,0,0,0.08)"/>
          <stop offset="100%" stop-color="rgba(0,0,0,${overlay.vignetteBottom})"/>
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#bg)"/>
      <rect width="100%" height="100%" fill="url(#vignette)"/>
    </svg>`);
}

function getPrimaryRegion(cfg) {
  return cfg.layout.personality === 'split-card'
    ? { left: cfg.layout.panelX, top: cfg.layout.panelY, right: cfg.layout.panelX + cfg.layout.panelWidth, bottom: cfg.layout.panelY + cfg.layout.panelHeight }
    : { left: 0, top: 0, right: cfg.width, bottom: cfg.height };
}

function getCtaGeometry(cfg) {
  const isCentered = cfg.layout.personality === 'centered-hero' || cfg.layout.align === 'center';
  const group = cfg.layout.ctaGroup;
  if (group) {
    const region = group.relativeTo === 'canvas' ? { left: 0, top: 0, right: cfg.width, bottom: cfg.height } : getPrimaryRegion(cfg);
    const padX = group.offsetX || 0;
    const padY = group.offsetY || 0;
    let rectX = region.left + padX;
    if (group.anchorX === 'center') rectX = Math.round((region.left + region.right - cfg.layout.ctaWidth) / 2) + padX;
    if (group.anchorX === 'right') rectX = region.right - cfg.layout.ctaWidth - padX;
    let rectY = region.top + padY;
    if (group.anchorY === 'middle') rectY = Math.round((region.top + region.bottom - cfg.layout.ctaHeight) / 2) + padY;
    if (group.anchorY === 'bottom') rectY = region.bottom - cfg.layout.ctaHeight - padY;
    const textX = rectX + (group.textAlign === 'center' || isCentered ? Math.round(cfg.layout.ctaWidth / 2) : (group.textInsetX || 24));
    const textY = rectY + Math.round(cfg.layout.ctaHeight / 2) + (group.textOffsetY || 0);
    return {
      rectX,
      rectY,
      textX,
      textY,
      textAnchor: (group.textAlign === 'center' || isCentered) ? 'middle' : ((group.textAlign === 'right') ? 'end' : 'start')
    };
  }
  const rectX = isCentered ? Math.round((cfg.width - cfg.layout.ctaWidth) / 2) : cfg.layout.ctaRectX;
  return {
    rectX,
    rectY: cfg.layout.ctaRectY,
    textX: rectX + Math.round(cfg.layout.ctaWidth / 2),
    textY: cfg.layout.ctaRectY + Math.round(cfg.layout.ctaHeight / 2),
    textAnchor: 'middle'
  };
}

function buildPrimaryTextSvg(cfg) {
  const { width, text, layout, theme, typography } = cfg;
  const headlineLines = wrapText(text.headline, layout.maxHeadlineChars);
  const subheadLines = wrapText(text.subhead, layout.maxSubheadChars);
  const headlineStep = cfg.preset === 'social-portrait' ? 82 : (cfg.preset === 'linkedin-landscape' ? 68 : 88);
  const subheadStep = cfg.typography.subheadLineHeight || (cfg.preset === 'linkedin-landscape' ? 34 : Math.round(cfg.typography.subheadSize * 1.22));
  const isCentered = layout.personality === 'centered-hero' || layout.align === 'center';
  const headlineAnchor = isCentered ? 'middle' : 'start';
  const headlineX = isCentered ? Math.round(width / 2) : layout.leftX;
  const subheadX = headlineX;
  const footerX = headlineX;
  const cta = getCtaGeometry(cfg);
  const panelEnabled = theme.textPanelFill && theme.textPanelFill !== 'none';
  let panel = '';
  if (layout.personality === 'split-card' && panelEnabled) {
    panel = `<rect x="${layout.panelX}" y="${layout.panelY}" width="${layout.panelWidth}" height="${layout.panelHeight}" rx="36" fill="${theme.textPanelFill}" stroke="${theme.textPanelStroke || 'none'}" />`;
  } else if (panelEnabled && layout.panelWidth && layout.panelHeight) {
    // Centered panel for centered-hero or editorial-left with explicit panel dimensions
    const panelX = layout.panelX != null ? layout.panelX : Math.round((cfg.width - layout.panelWidth) / 2);
    const panelY = layout.panelY != null ? layout.panelY : Math.round(layout.headlineY - 60);
    panel = `<rect x="${panelX}" y="${panelY}" width="${layout.panelWidth}" height="${layout.panelHeight}" rx="36" fill="${theme.textPanelFill}" stroke="${theme.textPanelStroke || 'none'}" />`;
  }
  const headlineTspans = headlineLines.map((line, i) => `<tspan x="${headlineX}" dy="${i === 0 ? 0 : headlineStep}">${escapeXml(line)}</tspan>`).join('');
  const subheadTspans = subheadLines.map((line, i) => `<tspan x="${subheadX}" dy="${i === 0 ? 0 : subheadStep}">${escapeXml(line)}</tspan>`).join('');
  return Buffer.from(`
    <svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
      ${panel}
      <rect x="${cta.rectX}" y="${cta.rectY}" width="${layout.ctaWidth}" height="${layout.ctaHeight}" rx="${layout.ctaRadius || 29}" fill="${theme.ctaFill}" stroke="${theme.ctaStroke}" />
      <text x="${headlineX}" y="${layout.headlineY}" text-anchor="${headlineAnchor}" fill="${theme.headlineColor}" font-size="${typography.headlineSize}" font-family="${typography.headlineFontFamily}" font-weight="${typography.headlineWeight}">${headlineTspans}</text>
      <text x="${subheadX}" y="${layout.subheadY}" text-anchor="${headlineAnchor}" fill="${theme.subheadColor}" font-size="${typography.subheadSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.subheadWeight}">${subheadTspans}</text>
      <text x="${cta.textX}" y="${cta.textY}" dy="0.35em" text-anchor="${cta.textAnchor}" fill="${theme.ctaTextColor}" font-size="${typography.ctaSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.ctaWeight}">${escapeXml(text.cta).replace(/★+/g, m => `<tspan fill="#FFD700">${m}</tspan>`)}</text>
      ${cfg.logo && cfg.logo.enabled ? '' : `<text x="${footerX}" y="${layout.footerY}" text-anchor="${headlineAnchor}" fill="${theme.footerColor}" font-size="${typography.footerSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.footerWeight}" letter-spacing="${typography.footerTracking}">${escapeXml(text.footer)}</text>`}
    </svg>`);
}

function buildShapesSvg(cfg) {
  if (!cfg.shapes.length) return null;
  const items = cfg.shapes.map((s) => {
    const fill = s.fill || 'rgba(255,255,255,0.15)';
    const stroke = s.stroke || 'none';
    const strokeWidth = s.strokeWidth || 0;
    const opacity = s.opacity == null ? 1 : s.opacity;
    if (s.type === 'ellipse') {
      const rx = (s.width || 100) / 2; const ry = (s.height || s.width || 100) / 2;
      return `<ellipse cx="${(s.x || 0) + rx}" cy="${(s.y || 0) + ry}" rx="${rx}" ry="${ry}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}" opacity="${opacity}" />`;
    }
    if (s.type === 'rectangle') {
      return `<rect x="${s.x || 0}" y="${s.y || 0}" width="${s.width || 100}" height="${s.height || 100}" rx="${s.radius || 0}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}" opacity="${opacity}" />`;
    }
    return '';
  }).join('\n');
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${items}</svg>`);
}

function buildTextLayersSvg(cfg) {
  if (!cfg.textLayers.length) return null;
  const nodes = cfg.textLayers.map((t) => {
    const maxChars = t.maxChars || 26;
    const lines = wrapText(t.content || '', maxChars);
    const step = t.lineHeight || Math.round((t.fontSize || 28) * 1.15);
    const anchor = t.align === 'center' ? 'middle' : (t.align === 'right' ? 'end' : 'start');
    const x = t.x || 0;
    const y = t.y || 0;
    const tspans = lines.map((line, i) => `<tspan x="${x}" dy="${i === 0 ? 0 : step}">${escapeXml(line)}</tspan>`).join('');
    const shadow = t.shadow ? `<text x="${x + (t.shadow.dx || 2)}" y="${y + (t.shadow.dy || 2)}" text-anchor="${anchor}" fill="${t.shadow.color || 'rgba(0,0,0,0.35)'}" font-size="${t.fontSize || 28}" font-family="${t.fontFamily || cfg.typography.bodyFontFamily}" font-weight="${t.fontWeight || 600}">${tspans}</text>` : '';
    return `${shadow}<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${t.color || '#ffffff'}" font-size="${t.fontSize || 28}" font-family="${t.fontFamily || cfg.typography.bodyFontFamily}" font-weight="${t.fontWeight || 600}">${tspans}</text>`.replace(/✓/g, '<tspan fill="#4CAF50" font-weight="800">✓</tspan>');
  }).join('\n');
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildProofHeroSvg(cfg) {
  if (!cfg.proofHero) return null;
  const p = cfg.proofHero;
  const quote = p.quote || '';
  const quoteLines = wrapText(quote, p.quoteMaxChars || 16);
  const quoteStep = p.quoteLineHeight || Math.round((p.quoteSize || 64) * 1.08);
  const quoteTspans = quoteLines.map((line, i) => `<tspan x="${p.quoteX || 120}" dy="${i === 0 ? 0 : quoteStep}">${escapeXml(line)}</tspan>`).join('');
  const quoteMark = p.quoteMark !== false
    ? `<text x="${p.quoteMarkX || (p.quoteX || 120) - 22}" y="${p.quoteMarkY || (p.quoteY || 110) - 14}" fill="${p.quoteMarkColor || '#ffffff'}" font-size="${p.quoteMarkSize || 92}" font-family="Georgia, serif" font-weight="700">“</text>`
    : '';
  const stars = p.starsText || '★★★★★';
  const starsNode = `<text x="${p.starsX || 260}" y="${p.starsY || 320}" fill="${p.starsColor || '#F4B63D'}" font-size="${p.starsSize || 80}" font-family="Arial, sans-serif" font-weight="700">${escapeXml(stars)}</text>`;
  const eyebrow = p.eyebrow ? `<text x="${p.eyebrowX || (p.quoteX || 120)}" y="${p.eyebrowY || 48}" fill="${p.eyebrowColor || 'rgba(255,255,255,0.72)'}" font-size="${p.eyebrowSize || 18}" font-family="${p.eyebrowFontFamily || 'Montserrat, Arial, sans-serif'}" font-weight="${p.eyebrowWeight || 700}" letter-spacing="${p.eyebrowTracking || 2}">${escapeXml(p.eyebrow)}</text>` : '';
  const cta = p.cta && p.cta.text ? `
    <rect x="${p.cta.x}" y="${p.cta.y}" width="${p.cta.width}" height="${p.cta.height}" rx="${p.cta.radius || 12}" fill="${p.cta.fill || '#ffffff'}" />
    <text x="${p.cta.x + Math.round(p.cta.width / 2)}" y="${p.cta.y + Math.round(p.cta.height / 2) + (p.cta.textDy || 10)}" text-anchor="middle" fill="${p.cta.textColor || '#141414'}" font-size="${p.cta.fontSize || 28}" font-family="${p.cta.fontFamily || 'Montserrat, Arial, sans-serif'}" font-weight="${p.cta.fontWeight || 800}">${escapeXml(p.cta.text)}</text>` : '';
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${eyebrow}${quoteMark}<text x="${p.quoteX || 120}" y="${p.quoteY || 110}" fill="${p.quoteColor || '#ffffff'}" font-size="${p.quoteSize || 64}" font-family="${p.quoteFontFamily || 'Georgia, Times New Roman, serif'}" font-weight="${p.quoteWeight || 700}" ${p.quoteStyle ? `font-style="${p.quoteStyle}"` : ''}>${quoteTspans}</text>${starsNode}${cta}</svg>`);
}

function rectFromXYWH(x, y, width, height) {
  return Rect.create(x, y, width, height);
}

function estimateProofHeroGeometry(cfg) {
  if (!cfg.proofHero) return [];
  const p = cfg.proofHero;
  const quoteLines = wrapText(p.quote || '', p.quoteMaxChars || 16);
  const quoteStep = p.quoteLineHeight || Math.round((p.quoteSize || 64) * 1.08);
  const quoteFontFamily = p.quoteFontFamily || 'Georgia, Times New Roman, serif';
  const quoteWidth = Math.max(...quoteLines.map(line => Text.measureWidth(line, p.quoteSize || 64, quoteFontFamily, { fontWeight: p.quoteWeight || 700 })));
  const quoteHeight = Math.max(1, quoteLines.length) * quoteStep;
  const starsText = p.starsText || '★★★★★';
  const starsWidth = Text.measureWidth(starsText, p.starsSize || 80, 'Arial, sans-serif');
  const elements = [
    { id: 'proofHero.quote', type: 'text', fontSize: p.quoteSize || 64, rect: rectFromXYWH(p.quoteX || 120, (p.quoteY || 110) - (p.quoteSize || 64), Math.round(quoteWidth), Math.round(quoteHeight)) },
    { id: 'proofHero.stars', type: 'text', fontSize: p.starsSize || 80, rect: rectFromXYWH(p.starsX || 260, (p.starsY || 320) - (p.starsSize || 80), Math.round(starsWidth), Math.round((p.starsSize || 80) * 1.2)) }
  ];
  if (p.cta && p.cta.text) elements.push({ id: 'proofHero.cta', type: 'cta', fontSize: p.cta.fontSize || 28, rect: rectFromXYWH(p.cta.x, p.cta.y, p.cta.width, p.cta.height) });
  return elements;
}

function buildLayoutSidecar(cfg, primitiveElements = [], resolvedImageLayers = []) {
  const canvas = Rect.create(0, 0, cfg.width, cfg.height);
  const elements = [];

  // --- Collect all elements with geometry ---

  // Image layers
  const allImageLayers = [...(Array.isArray(cfg.imageLayers) ? cfg.imageLayers : []), ...resolvedImageLayers];
  allImageLayers.forEach((img, i) => {
    elements.push({ id: `imageLayer.${i + 1}`, type: 'image', source: img.path || null, rect: Rect.create(img.x || 0, img.y || 0, img.width || 0, img.height || 0) });
  });

  // Primitive elements (from proofHero etc.)
  elements.push(...primitiveElements);

  // Text layers
  if (Array.isArray(cfg.textLayers)) {
    cfg.textLayers.forEach((t, i) => {
      const lines = wrapText(t.content || '', t.maxChars || 26);
      const fontSize = t.fontSize || 28;
      const fontFamily = t.fontFamily || cfg.typography.bodyFontFamily;
      const step = t.lineHeight || Math.round(fontSize * 1.15);
      const width = Math.max(...lines.map(line => Text.measureWidth(line, fontSize, fontFamily)));
      const height = Math.max(1, lines.length) * step;
      elements.push({ id: `textLayer.${i + 1}`, type: 'text', fontSize, rect: Rect.create(t.x || 0, (t.y || 0) - fontSize, Math.round(width), Math.round(height)) });
    });
  }

  // Primary text elements (headline, subhead, CTA, footer)
  const isCenteredLayout = cfg.layout.personality === 'centered-hero' || cfg.layout.align === 'center';
  const textAlign = isCenteredLayout ? 'center' : 'left';
  const textX = isCenteredLayout ? Math.round(cfg.width / 2) : cfg.layout.leftX;

  const headlineLines = wrapText(cfg.text.headline, cfg.layout.maxHeadlineChars);
  const headlineStep = cfg.height >= 1350 ? 82 : (cfg.preset === 'linkedin-landscape' ? 68 : 88);
  const headlineBlock = estimateTextBlock({
    lines: headlineLines, fontSize: cfg.typography.headlineSize, lineStep: headlineStep,
    x: textX, y: cfg.layout.headlineY, align: textAlign,
    fontFamily: cfg.typography.headlineFontFamily, fontWeight: cfg.typography.headlineWeight
  });
  elements.push({ id: 'headline', type: 'text', fontSize: cfg.typography.headlineSize, rect: Rect.fromObject(headlineBlock) });

  const subheadLines = wrapText(cfg.text.subhead, cfg.layout.maxSubheadChars);
  const subheadStep = cfg.typography.subheadLineHeight || (cfg.preset === 'linkedin-landscape' ? 34 : Math.round(cfg.typography.subheadSize * 1.22));
  const subheadBlock = estimateTextBlock({
    lines: subheadLines, fontSize: cfg.typography.subheadSize, lineStep: subheadStep,
    x: textX, y: cfg.layout.subheadY, align: textAlign,
    fontFamily: cfg.typography.bodyFontFamily
  });
  elements.push({ id: 'subhead', type: 'text', fontSize: cfg.typography.subheadSize, rect: Rect.fromObject(subheadBlock) });

  const ctaGeom = getCtaGeometry(cfg);
  const ctaRect = Rect.create(ctaGeom.rectX, ctaGeom.rectY, cfg.layout.ctaWidth, cfg.layout.ctaHeight);
  elements.push({ id: 'cta', type: 'cta', fontSize: cfg.typography.ctaSize, rect: ctaRect });

  const footerBlock = estimateTextBlock({
    lines: [cfg.text.footer], fontSize: cfg.typography.footerSize, lineStep: cfg.typography.footerSize,
    x: textX, y: cfg.layout.footerY, align: textAlign,
    fontFamily: cfg.typography.bodyFontFamily, fontWeight: cfg.typography.footerWeight
  });
  elements.push({ id: 'footer', type: 'text', fontSize: cfg.typography.footerSize, rect: Rect.fromObject(footerBlock) });

  // Badge elements
  if (Array.isArray(cfg.badges)) {
    cfg.badges.forEach((b, i) => {
      const bw = b.width || Text.measureWidth(b.text || '', b.fontSize || 16, 'Montserrat') + 24;
      const bh = b.height || (b.fontSize || 16) + 16;
      elements.push({ id: `badge.${i + 1}`, type: 'badge', rect: Rect.create(b.x || 0, b.y || 0, bw, bh) });
    });
  }

  // Logo element (corner-anchor or legacy)
  const logoResolved = resolveLogoLayer(cfg);
  if (logoResolved) {
    elements.push({ id: 'logo', type: 'logo', rect: Rect.create(logoResolved.x || 0, logoResolved.y || 0, logoResolved.width || 0, logoResolved.height || 0) });
  }

  // --- Primary layout gap analysis ---
  const headlineTop = headlineBlock.top;
  const headlineBottom = headlineBlock.bottom;
  const ctaTop = ctaGeom.rectY;
  const ctaBottom = ctaTop + cfg.layout.ctaHeight;
  const minGap = cfg.layout.minHeadlineCtaGap != null ? cfg.layout.minHeadlineCtaGap : 40;
  const actualGap = ctaTop - headlineBottom;

  // --- Safe-zone analysis ---
  const zones = SafeZone.getSafeZones(cfg.width, cfg.height, cfg.preset);
  const safeZoneCheck = SafeZone.checkAll(elements, zones);
  const mobileWarnings = SafeZone.mobileReadabilityCheck(elements, cfg.width);

  // --- Collision detection ---
  const collisions = Rect.findCollisions(elements);

  // --- Occupancy metrics ---
  const occupancyMetrics = Rect.computeOccupancy(elements, canvas);

  // --- Spacing analysis ---
  const spacingChecks = [];
  // Headline → subhead gap
  const hlSubGap = Rect.verticalGap(Rect.fromObject(headlineBlock), Rect.fromObject(subheadBlock));
  spacingChecks.push({ pair: ['headline', 'subhead'], gap: hlSubGap, min: 24, pass: hlSubGap >= 24 });
  // Subhead → CTA gap
  const subCtaGap = Rect.verticalGap(Rect.fromObject(subheadBlock), ctaRect);
  spacingChecks.push({ pair: ['subhead', 'cta'], gap: subCtaGap, min: 24, pass: subCtaGap >= 24 });
  // CTA → footer gap
  const ctaFooterGap = Rect.verticalGap(ctaRect, Rect.fromObject(footerBlock));
  spacingChecks.push({ pair: ['cta', 'footer'], gap: ctaFooterGap, min: 20, pass: ctaFooterGap >= 20 });
  // Headline → CTA gap (the big constraint)
  spacingChecks.push({ pair: ['headline', 'cta'], gap: actualGap, min: minGap, pass: actualGap >= minGap });

  return {
    version: '1.5.1',
    canvas,
    preset: cfg.preset,
    personality: cfg.layout.personality,
    designIntent: cfg.designIntent || null,
    constraintPolicy: cfg.constraintPolicy || null,
    primitiveIds: cfg.proofHero ? ['proofHero'] : [],
    primaryLayout: {
      headlineY: cfg.layout.headlineY,
      headlineTop,
      headlineBottom,
      ctaRectY: cfg.layout.ctaRectY,
      ctaTop,
      ctaBottom,
      headlineCtaGap: actualGap,
      minHeadlineCtaGap: minGap,
      gapEnforced: actualGap >= minGap
    },
    elements,
    safeZones: {
      canvasSafe: zones.canvasSafe,
      textSafe: zones.textSafe,
      ctaSafe: zones.ctaSafe,
      check: safeZoneCheck.summary,
      violations: safeZoneCheck.violations
    },
    collisions,
    spacing: spacingChecks,
    occupancy: occupancyMetrics,
    mobileReadability: mobileWarnings,
    warnings: [
      ...safeZoneCheck.violations.filter(v => v.type === 'hard').map(v => `${v.id} violates ${v.zone} safe zone by ${v.severity}px`),
      ...collisions.map(c => `${c.a} overlaps ${c.b} (${c.intersection.width}x${c.intersection.height}px)`),
      ...spacingChecks.filter(s => !s.pass).map(s => `${s.pair.join('→')} gap ${s.gap}px < min ${s.min}px`),
      ...mobileWarnings.map(w => w.message)
    ]
  };
}

function buildStatBlocksSvg(cfg) {
  if (!cfg.statBlocks || !cfg.statBlocks.length) return null;
  const nodes = cfg.statBlocks.map((s) => {
    const x = s.x || 0;
    const y = s.y || 0;
    const valueSize = s.valueSize || 72;
    const labelSize = s.labelSize || 18;
    const valueColor = s.valueColor || '#ffffff';
    const labelColor = s.labelColor || 'rgba(255,255,255,0.6)';
    const valueWeight = s.valueWeight || 800;
    const labelWeight = s.labelWeight || 500;
    const valueFontFamily = s.valueFontFamily || cfg.typography.headlineFontFamily;
    const labelFontFamily = s.labelFontFamily || cfg.typography.bodyFontFamily;
    const anchor = s.align === 'center' ? 'middle' : (s.align === 'right' ? 'end' : 'start');
    const labelGap = s.labelGap || 8;
    const labelY = y + valueSize + labelGap;
    const labelTracking = s.labelTracking || 2;

    // Optional accent line above the value
    const accent = s.accent ? `<rect x="${s.accent.align === 'center' ? x - (s.accent.width || 40) / 2 : x}" y="${y - (s.accent.gap || 16) - (s.accent.height || 3)}" width="${s.accent.width || 40}" height="${s.accent.height || 3}" rx="${(s.accent.height || 3) / 2}" fill="${s.accent.color || 'rgba(255,255,255,0.3)'}"/>` : '';

    // Optional background pill/card behind the stat
    const bg = s.background ? `<rect x="${s.background.x || x - 20}" y="${s.background.y || y - 20}" width="${s.background.width || 200}" height="${s.background.height || valueSize + labelSize + labelGap + 40}" rx="${s.background.radius || 16}" fill="${s.background.fill || 'rgba(255,255,255,0.06)'}" stroke="${s.background.stroke || 'rgba(255,255,255,0.1)'}" stroke-width="${s.background.strokeWidth || 1}"/>` : '';

    return `${bg}${accent}<text x="${x}" y="${y + valueSize * 0.82}" text-anchor="${anchor}" fill="${valueColor}" font-size="${valueSize}" font-family="${valueFontFamily}" font-weight="${valueWeight}">${escapeXml(s.value)}</text><text x="${x}" y="${labelY + labelSize * 0.82}" text-anchor="${anchor}" fill="${labelColor}" font-size="${labelSize}" font-family="${labelFontFamily}" font-weight="${labelWeight}" letter-spacing="${labelTracking}">${escapeXml((s.label || '').toUpperCase())}</text>`;
  }).join('\n');
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildDividersSvg(cfg) {
  if (!cfg.dividers || !cfg.dividers.length) return null;
  const nodes = cfg.dividers.map((d) => {
    if (d.type === 'vertical') {
      return `<rect x="${d.x || 0}" y="${d.y || 0}" width="${d.width || 1}" height="${d.height || 100}" rx="${(d.width || 1) / 2}" fill="${d.color || 'rgba(255,255,255,0.12)'}"/>`;
    }
    return `<rect x="${d.x || 0}" y="${d.y || 0}" width="${d.width || 100}" height="${d.height || 1}" rx="${(d.height || 1) / 2}" fill="${d.color || 'rgba(255,255,255,0.12)'}"/>`;
  }).join('\n');
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildCompositeSvg(cfg) {
  const { productComposite, theme, typography } = cfg;
  if (!productComposite.enabled) return null;
  const d = productComposite.circleDiameter;
  const shadowFill = String(theme.productShadowColor).startsWith('rgb')
    ? theme.productShadowColor
    : `rgba(${theme.productShadowColor},${productComposite.shadowOpacity})`;
  const badgeLabel = escapeXml(productComposite.badgeText);
  const badgeWidth = Math.max(170, Math.round(badgeLabel.length * 11 + 48));
  const badgeTextX = productComposite.badgeX + Math.round(badgeWidth / 2);
  return Buffer.from(`
    <svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${productComposite.circleX + d / 2}" cy="${productComposite.circleY + d / 2 + 20}" r="${d / 2}" fill="${shadowFill}" />
      <circle cx="${productComposite.circleX + d / 2}" cy="${productComposite.circleY + d / 2}" r="${d / 2}" fill="${theme.productCircleFill}" />
      <rect x="${productComposite.badgeX}" y="${productComposite.badgeY}" width="${badgeWidth}" height="42" rx="21" fill="${theme.badgeFill}" stroke="${theme.badgeStroke}" />
      <text x="${badgeTextX}" y="${productComposite.badgeY + 28}" text-anchor="middle" fill="${theme.badgeTextColor}" font-size="20" font-family="${typography.bodyFontFamily}" font-weight="700">${badgeLabel}</text>
    </svg>`);
}

async function buildProductLayer(cfg) {
  if (!cfg.productComposite.enabled || !cfg.productPath || !fileExists(cfg.productPath)) return null;
  const d = cfg.productComposite.circleDiameter;
  const r = d / 2;
  const inset = 20;
  const fitSize = d - inset * 2;
  let productBuf = await sharp(cfg.productPath)
    .resize({ width: fitSize, height: fitSize, fit: 'inside', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toBuffer();
  productBuf = await removeWhiteBackground(productBuf);
  const prodMeta = await sharp(productBuf).metadata();
  const centered = await sharp({
    create: { width: d, height: d, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } }
  })
    .composite([{
      input: productBuf,
      left: Math.round((d - prodMeta.width) / 2),
      top: Math.round((d - prodMeta.height) / 2)
    }])
    .png()
    .toBuffer();
  const circleMask = Buffer.from(
    `<svg width="${d}" height="${d}" xmlns="http://www.w3.org/2000/svg"><circle cx="${r}" cy="${r}" r="${r}" fill="white"/></svg>`
  );
  const maskBuf = await sharp(circleMask).resize(d, d).png().toBuffer();
  return sharp(centered)
    .composite([{ input: maskBuf, blend: 'dest-in' }])
    .png()
    .toBuffer();
}


function estimateTextBlock({ lines, fontSize, lineStep, x, y, align = 'left', maxChars = 24, fontFamily, fontWeight }) {
  const block = Text.measureBlock({
    lines, fontSize, fontFamily,
    lineHeight: lineStep,
    x, y, align, fontWeight
  });
  // Return backward-compatible shape with extra geometry data
  return {
    left: block.rect.left, top: block.rect.top,
    width: block.rect.width, height: block.rect.height,
    right: block.rect.right, bottom: block.rect.bottom,
    lines: lines.length, maxChars,
    _measured: true,
    _lineRects: block.lineRects,
    _maxLineWidth: block.maxLineWidth
  };
}

function boxInside(inner, outer, pad = 0) {
  return Rect.containsWithMargin(Rect.fromObject(outer), Rect.fromObject(inner), pad);
}

function boxCenter(box) {
  return { x: (box.left + box.right) / 2, y: (box.top + box.bottom) / 2 };
}

function runCompositionChecks(cfg, { headlineBox, subheadBox, ctaRect, footerBox, canvas }) {
  const checks = [];
  const warnings = [];
  const scores = {};
  const w = cfg.width;
  const h = cfg.height;
  const thirdX = w / 3;
  const thirdY = h / 3;

  // 1. Rule of thirds — headline vertical alignment
  // Best: headline center Y near top-third line (h/3) within 15% tolerance
  const headlineCenter = boxCenter(headlineBox);
  const headlineThirdDist = Math.abs(headlineCenter.y - thirdY) / h;
  const headlineThirdScore = Math.max(0, Math.round((1 - headlineThirdDist / 0.25) * 100));
  scores.headlineThirdsAlignment = headlineThirdScore;
  checks.push({ name: 'thirds-headline-vertical', pass: headlineThirdScore >= 40, value: headlineThirdScore, note: `Headline center ${Math.round(headlineCenter.y)}px vs top-third ${Math.round(thirdY)}px` });
  if (headlineThirdScore < 40) warnings.push('Headline is far from the rule-of-thirds grid line.');

  // 2. Vertical reading order
  const ctaCenterY = (ctaRect.top + ctaRect.bottom) / 2;
  const footerCenterY = (footerBox.top + footerBox.bottom) / 2;
  const orderCorrect = headlineCenter.y < subheadBox.top && (ctaCenterY <= 0 || subheadBox.bottom < ctaCenterY) && (footerCenterY <= 0 || footerCenterY > headlineCenter.y);
  scores.readingOrder = orderCorrect ? 100 : 0;
  checks.push({ name: 'reading-order', pass: orderCorrect, value: orderCorrect ? 100 : 0 });
  if (!orderCorrect) warnings.push('Elements break natural top-to-bottom reading order.');

  // 3. Edge margins — no key text within 60px of canvas edge
  const minMargin = 60;
  const allBoxes = [headlineBox, subheadBox];
  if (ctaRect.left >= 0) allBoxes.push(ctaRect);
  let marginOk = true;
  for (const box of allBoxes) {
    if (box.left < minMargin || box.top < minMargin || (w - box.right) < minMargin) { marginOk = false; break; }
  }
  scores.edgeMargins = marginOk ? 100 : 30;
  checks.push({ name: 'edge-margins', pass: marginOk, value: marginOk ? 100 : 30 });
  if (!marginOk) warnings.push('Key text is within 60px of the canvas edge — tight margins reduce perceived quality.');

  // 4. Visual hierarchy — headline must be larger than subhead
  const hlSize = cfg.typography.headlineSize || 42;
  const shSize = cfg.typography.subheadSize || 22;
  const hierarchyRatio = hlSize / Math.max(shSize, 1);
  const hierarchyOk = hierarchyRatio >= 1.4;
  scores.visualHierarchy = hierarchyOk ? 100 : Math.round(hierarchyRatio / 1.4 * 100);
  checks.push({ name: 'visual-hierarchy', pass: hierarchyOk, value: Math.round(hierarchyRatio * 100) / 100, note: `headline ${hlSize}px / subhead ${shSize}px = ${Math.round(hierarchyRatio * 100) / 100}x (want ≥1.4x)` });
  if (!hierarchyOk) warnings.push(`Headline-to-subhead size ratio is only ${Math.round(hierarchyRatio * 100) / 100}x — weak visual hierarchy.`);

  // 5. Canvas utilization — content shouldn't be crammed into < 40% or sprawled > 90% of height
  const contentTop = headlineBox.top;
  const contentBottom = Math.max(subheadBox.bottom, ctaRect.bottom > 0 ? ctaRect.bottom : 0, footerBox.bottom);
  const utilization = (contentBottom - contentTop) / h;
  const utilizationOk = utilization >= 0.35 && utilization <= 0.92;
  scores.canvasUtilization = utilizationOk ? 100 : 50;
  checks.push({ name: 'canvas-utilization', pass: utilizationOk, value: Math.round(utilization * 100), note: `Content spans ${Math.round(utilization * 100)}% of canvas height` });
  if (!utilizationOk) warnings.push(`Content uses ${Math.round(utilization * 100)}% of canvas height — ${utilization < 0.35 ? 'feels empty' : 'feels crammed'}.`);

  // 8. Margin balance — all text elements should have consistent left margins
  const leftMargins = [headlineBox.left, subheadBox.left, ctaRect.left].filter(v => v > 0);
  const rightMargins = [w - headlineBox.right, w - subheadBox.right, w - ctaRect.right].filter(v => v > 0);
  const maxLeftDiff = Math.max(...leftMargins) - Math.min(...leftMargins);
  const maxRightDiff = Math.max(...rightMargins) - Math.min(...rightMargins);
  // For left-aligned layouts (editorial-left, split-card), only check left margins — right side intentionally shows photo
  const isLeftAligned = cfg.layout.personality === 'editorial-left' || cfg.layout.personality === 'split-card';
  const marginBalanced = isLeftAligned ? (maxLeftDiff <= 60) : (maxLeftDiff <= 60 && maxRightDiff <= 60);
  scores.marginBalance = marginBalanced ? 100 : 40;
  checks.push({ name: 'margin-balance', pass: marginBalanced, value: { leftDiff: maxLeftDiff, rightDiff: maxRightDiff }, note: `Max left margin variance ${maxLeftDiff}px, right ${maxRightDiff}px (want ≤60px)` });
  if (!marginBalanced) warnings.push(`Text elements have unbalanced margins (left diff: ${maxLeftDiff}px, right diff: ${maxRightDiff}px). Constrain elements to consistent width.`);

  // 9. Panel overflow — text must fit within split-card panel bounds
  if (cfg.layout.personality === 'split-card' && cfg.layout.panelWidth) {
    const panelRight = (cfg.layout.panelX || 0) + cfg.layout.panelWidth;
    const panelBottom = (cfg.layout.panelY || 0) + cfg.layout.panelHeight;
    const headlineOverflow = headlineBox.right > panelRight;
    const subheadOverflow = subheadBox.right > panelRight;
    const ctaOverflow = ctaRect.right > panelRight;
    const vertOverflow = ctaRect.bottom > panelBottom;
    const anyOverflow = headlineOverflow || subheadOverflow || ctaOverflow || vertOverflow;
    scores.panelOverflow = anyOverflow ? 0 : 100;
    checks.push({ name: 'panel-overflow', pass: !anyOverflow, value: {
      panelRight, headlineRight: headlineBox.right, subheadRight: subheadBox.right,
      ctaRight: ctaRect.right, ctaBottom: ctaRect.bottom, panelBottom
    }, note: anyOverflow ? 'Text overflows panel — reduce font size or maxChars' : 'All text inside panel' });
    if (headlineOverflow) { warnings.push(`Headline overflows panel by ${headlineBox.right - panelRight}px — reduce headlineSize or maxHeadlineChars.`); failures.push('headline-overflow'); }
    if (subheadOverflow) { warnings.push(`Subhead overflows panel by ${subheadBox.right - panelRight}px — reduce subheadSize or maxSubheadChars.`); failures.push('subhead-overflow'); }
    if (ctaOverflow) { warnings.push(`CTA overflows panel by ${ctaRect.right - panelRight}px — reduce ctaWidth.`); failures.push('cta-overflow'); }
    if (vertOverflow) { warnings.push(`CTA extends below panel by ${ctaRect.bottom - panelBottom}px — adjust vertical positions.`); failures.push('vertical-overflow'); }
  }

  // Composite score (average of all sub-scores)
  const scoreValues = Object.values(scores);
  scores.overall = Math.round(scoreValues.reduce((a, b) => a + b, 0) / scoreValues.length);

  return { checks, warnings, scores };
}

function runReview(cfg, meta) {
  const checks = [];
  const warnings = [];
  const failures = [];
  const canvas = { left: 0, top: 0, right: cfg.width, bottom: cfg.height };
  const isCentered = cfg.layout.personality === 'centered-hero' || cfg.layout.align === 'center';
  const primaryRegion = getPrimaryRegion(cfg);

  const headlineLines = wrapText(cfg.text.headline, cfg.layout.maxHeadlineChars);
  const subheadLines = wrapText(cfg.text.subhead, cfg.layout.maxSubheadChars);
  const headlineStep = cfg.preset === 'social-portrait' ? 82 : (cfg.preset === 'linkedin-landscape' ? 68 : 88);
  const subheadStep = cfg.typography.subheadLineHeight || (cfg.preset === 'linkedin-landscape' ? 34 : Math.round(cfg.typography.subheadSize * 1.22));
  const anchor = isCentered ? 'center' : 'left';
  const textX = isCentered ? Math.round(cfg.width / 2) : cfg.layout.leftX;
  const headlineBox = estimateTextBlock({ lines: headlineLines, fontSize: cfg.typography.headlineSize, lineStep: headlineStep, x: textX, y: cfg.layout.headlineY, align: anchor, maxChars: cfg.layout.maxHeadlineChars, fontFamily: cfg.typography.headlineFontFamily, fontWeight: cfg.typography.headlineWeight });
  const subheadBox = estimateTextBlock({ lines: subheadLines, fontSize: cfg.typography.subheadSize, lineStep: subheadStep, x: textX, y: cfg.layout.subheadY, align: anchor, maxChars: cfg.layout.maxSubheadChars, fontFamily: cfg.typography.bodyFontFamily });
  const footerBox = estimateTextBlock({ lines: [cfg.text.footer], fontSize: cfg.typography.footerSize, lineStep: cfg.typography.footerSize, x: textX, y: cfg.layout.footerY, align: anchor, maxChars: 60, fontFamily: cfg.typography.bodyFontFamily, fontWeight: cfg.typography.footerWeight });
  const ctaGeom = getCtaGeometry(cfg);
  const ctaRect = { left: ctaGeom.rectX, top: ctaGeom.rectY, right: ctaGeom.rectX + cfg.layout.ctaWidth, bottom: ctaGeom.rectY + cfg.layout.ctaHeight };

  const headlineInside = boxInside(headlineBox, primaryRegion, 18);
  checks.push({ name: 'headline-inside-primary-region', pass: headlineInside, box: headlineBox });
  if (!headlineInside) failures.push('Headline exceeds the intended primary region.');

  const subheadInside = boxInside(subheadBox, primaryRegion, 18);
  checks.push({ name: 'subhead-inside-primary-region', pass: subheadInside, box: subheadBox });
  if (!subheadInside) failures.push('Subhead exceeds the intended primary region.');

  const ctaInside = boxInside(ctaRect, primaryRegion, 18);
  checks.push({ name: 'cta-inside-primary-region', pass: ctaInside, box: ctaRect });
  if (!ctaInside) failures.push('CTA box exceeds the intended primary region.');

  const verticalGap1 = subheadBox.top - headlineBox.bottom;
  const verticalGap2 = ctaRect.top - subheadBox.bottom;
  const verticalGap3 = footerBox.top - ctaRect.bottom;
  checks.push({ name: 'headline-to-subhead-gap', pass: verticalGap1 >= 24, value: verticalGap1 });
  if (verticalGap1 < 24) warnings.push('Headline/subhead spacing is too tight.');
  checks.push({ name: 'subhead-to-cta-gap', pass: verticalGap2 >= 24, value: verticalGap2 });
  if (verticalGap2 < 24) warnings.push('Subhead/CTA spacing is too tight.');
  checks.push({ name: 'cta-to-footer-gap', pass: verticalGap3 >= 20, value: verticalGap3 });
  if (verticalGap3 < 20) warnings.push('CTA/footer spacing is too tight.');

  // --- headline-to-CTA gap check (minHeadlineCtaGap) ---
  const minHeadlineCtaGap = cfg.layout.minHeadlineCtaGap != null ? cfg.layout.minHeadlineCtaGap : 40;
  const headlineCtaGap = ctaRect.top - headlineBox.bottom;
  checks.push({ name: 'headline-to-cta-gap', pass: headlineCtaGap >= minHeadlineCtaGap, value: headlineCtaGap, note: `Gap between headline bottom and CTA top: ${headlineCtaGap}px (min ${minHeadlineCtaGap}px)` });
  if (headlineCtaGap < minHeadlineCtaGap) warnings.push(`Headline sits too close to CTA — gap is ${headlineCtaGap}px, minimum is ${minHeadlineCtaGap}px. Layout was auto-adjusted.`);

  if (cfg.layout.personality === 'split-card') {
    const panelPaddingLeft = headlineBox.left - primaryRegion.left;
    const panelPaddingRight = primaryRegion.right - headlineBox.right;
    checks.push({ name: 'panel-left-padding', pass: panelPaddingLeft >= 36, value: panelPaddingLeft });
    checks.push({ name: 'panel-right-padding', pass: panelPaddingRight >= 36, value: panelPaddingRight });
    if (panelPaddingLeft < 36 || panelPaddingRight < 36) warnings.push('Text padding inside panel is too tight.');
  }

  for (const [i, layer] of cfg.textLayers.entries()) {
    const lines = wrapText(layer.content || '', layer.maxChars || 26);
    const box = estimateTextBlock({ lines, fontSize: layer.fontSize || 28, lineStep: layer.lineHeight || Math.round((layer.fontSize || 28) * 1.15), x: layer.x || 0, y: layer.y || 0, align: layer.align || 'left' });
    const insideCanvas = boxInside(box, canvas, 12);
    checks.push({ name: `text-layer-${i + 1}-inside-canvas`, pass: insideCanvas, box });
    if (!insideCanvas) failures.push(`Text layer ${i + 1} exceeds the canvas.`);
  }

  // --- Composition checks (marketing design frameworks) ---
  const composition = runCompositionChecks(cfg, { headlineBox, subheadBox, ctaRect, footerBox, canvas });
  checks.push(...composition.checks);
  warnings.push(...composition.warnings);

  const status = failures.length ? 'fail' : (warnings.length ? 'warn' : 'pass');
  return { status, checks, warnings, failures, composition: composition.scores, regions: { canvas, primaryRegion }, output: cfg.output, dimensions: { width: meta.width, height: meta.height } };
}

async function buildFramedImageLayer(img) {
  if (!img || !img.path || !fileExists(img.path)) return null;
  const w = img.width || 400;
  const h = img.height || 400;
  const pad = img.padding || 20;
  const background = img.background || { r: 255, g: 255, b: 255, alpha: 1 };
  const fit = img.fit || 'contain';
  const radius = img.radius || 0;
  const stroke = img.stroke || null;
  const strokeWidth = img.strokeWidth || 0;
  const shadow = img.shadow || null;
  let resizedBuf = await sharp(img.path)
    .resize({ width: w - pad * 2, height: h - pad * 2, fit, background: { r: 255, g: 255, b: 255, alpha: 1 } })
    .png()
    .toBuffer();
  const meta = await sharp(resizedBuf).metadata();
  if (radius > 0) {
    const innerRadius = Math.max(0, radius - pad);
    const mask = Buffer.from(`<svg width="${meta.width}" height="${meta.height}" xmlns="http://www.w3.org/2000/svg"><rect width="${meta.width}" height="${meta.height}" rx="${innerRadius}" ry="${innerRadius}" fill="#fff"/></svg>`);
    resizedBuf = await sharp(resizedBuf).composite([{ input: mask, blend: 'dest-in' }]).png().toBuffer();
  }
  const layers = [];
  if (shadow) {
    const shadowSvg = Buffer.from(`<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg"><rect x="${shadow.x || 0}" y="${shadow.y || 10}" width="${w - (shadow.insetX || 0)}" height="${h - (shadow.insetY || 0)}" rx="${radius}" fill="${shadow.color || 'rgba(0,0,0,0.18)'}"/></svg>`);
    layers.push({ input: shadowSvg, left: 0, top: 0 });
  }
  layers.push({ input: resizedBuf, left: Math.round((w - meta.width) / 2), top: Math.round((h - meta.height) / 2) });
  if (stroke && strokeWidth > 0) {
    const strokeSvg = Buffer.from(`<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg"><rect x="${Math.round(strokeWidth/2)}" y="${Math.round(strokeWidth/2)}" width="${w - strokeWidth}" height="${h - strokeWidth}" rx="${Math.max(0, radius - Math.round(strokeWidth/2))}" fill="none" stroke="${stroke}" stroke-width="${strokeWidth}"/></svg>`);
    layers.push({ input: strokeSvg, left: 0, top: 0 });
  }
  return sharp({ create: { width: w, height: h, channels: 4, background } }).composite(layers).png().toBuffer();
}

async function buildRectProductLayer(cfg) {
  return buildFramedImageLayer(cfg.productImage);
}

async function renderOne(rawConfig) {
  const cfg = normalizeConfig(rawConfig);
  ensureDir(cfg.output);
  const composites = [{ input: buildOverlaySvg(cfg) }];
  const shapes = buildShapesSvg(cfg); if (shapes) composites.push({ input: shapes });
  const dividers = buildDividersSvg(cfg); if (dividers) composites.push({ input: dividers });
  // Rectangular product image (for explainer cards)
  const rectProduct = await buildRectProductLayer(cfg);
  if (rectProduct) composites.push({ input: rectProduct, left: cfg.productImage.x || 0, top: cfg.productImage.y || 0 });
  const derivedLogoLayer = resolveLogoLayer(cfg);
  if (derivedLogoLayer && derivedLogoLayer.placement !== 'corner-anchor') {
    const layer = await buildFramedImageLayer(derivedLogoLayer);
    if (layer) composites.push({ input: layer, left: derivedLogoLayer.x || 0, top: derivedLogoLayer.y || 0 });
  }
  const primitiveOutputs = buildPrimitiveOutputs(cfg, { wrapText, escapeXml, registry: getPrimitiveRegistry() });
  const resolvedPrimitiveImageLayers = [];
  const primitiveElements = [];
  const activePrimitiveIds = new Set();
  for (const primitiveOutput of primitiveOutputs) {
    if (primitiveOutput.id) activePrimitiveIds.add(primitiveOutput.id);
    if (primitiveOutput.svg) composites.push({ input: primitiveOutput.svg });
    if (Array.isArray(primitiveOutput.imageLayers)) resolvedPrimitiveImageLayers.push(...primitiveOutput.imageLayers);
    if (Array.isArray(primitiveOutput.elements)) primitiveElements.push(...primitiveOutput.elements);
  }
  if (Array.isArray(cfg.imageLayers)) {
    for (const img of cfg.imageLayers) {
      const layer = await buildFramedImageLayer(img);
      if (layer) composites.push({ input: layer, left: img.x || 0, top: img.y || 0 });
    }
  }
  for (const img of resolvedPrimitiveImageLayers) {
    const layer = await buildFramedImageLayer(img);
    if (layer) composites.push({ input: layer, left: img.x || 0, top: img.y || 0 });
  }
  composites.push({ input: buildPrimaryTextSvg(cfg) });
  const textLayers = buildTextLayersSvg(cfg); if (textLayers) composites.push({ input: textLayers });
  const statBlocksSvg = buildStatBlocksSvg(cfg); if (statBlocksSvg) composites.push({ input: statBlocksSvg });
  // New template layers
  const benefitStackSvg = buildBenefitStackSvg(cfg); if (benefitStackSvg) composites.push({ input: benefitStackSvg });
  const testimonialSvg = buildTestimonialSvg(cfg); if (testimonialSvg) composites.push({ input: testimonialSvg });
  const splitRevealSvg = buildSplitRevealSvg(cfg); if (splitRevealSvg) composites.push({ input: splitRevealSvg });
  const offerFrameSvg = buildOfferFrameSvg(cfg); if (offerFrameSvg) composites.push({ input: offerFrameSvg });
  // Skip inline builder when primitive handles it
  if (!activePrimitiveIds.has('comparisonPanel')) {
    const comparisonTableSvg = buildComparisonTableSvg(cfg); if (comparisonTableSvg) composites.push({ input: comparisonTableSvg });
  }
  const authorityBarSvg = buildAuthorityBarSvg(cfg); if (authorityBarSvg) composites.push({ input: authorityBarSvg });
  const badgesSvg = buildBadgesSvg(cfg); if (badgesSvg) composites.push({ input: badgesSvg });
  const compositeSvg = buildCompositeSvg(cfg); if (compositeSvg) composites.push({ input: compositeSvg });
  const productLayer = await buildProductLayer(cfg);
  if (productLayer) composites.push({ input: productLayer, left: cfg.productComposite.circleX, top: cfg.productComposite.circleY });
  // Corner-anchor logo layer (new logo guidelines)
  const logoResolved = resolveLogoLayer(cfg);
  const cornerAnchor = await buildCornerAnchorLogo(cfg, logoResolved);
  if (cornerAnchor) {
    composites.push({ input: cornerAnchor.panelBuf, left: cornerAnchor.panelX, top: cornerAnchor.panelY });
    composites.push({ input: cornerAnchor.logoBuf, left: cornerAnchor.logoX, top: cornerAnchor.logoY });
  }
  // Legacy logo layer — replaces footer text when logoPath is set
  if (!cornerAnchor && cfg.logo.enabled && cfg.logoPath && fileExists(cfg.logoPath)) {
    const logoW = cfg.logo.width || 120;
    const logoH = cfg.logo.height || 120;
    const logoBuf = await sharp(cfg.logoPath)
      .resize({ width: logoW, height: logoH, fit: 'inside', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .ensureAlpha()
      .png()
      .toBuffer();
    const logoMeta = await sharp(logoBuf).metadata();
    const isCentered = cfg.layout.personality === 'centered-hero' || cfg.layout.align === 'center';
    const logoX = cfg.logo.x != null ? cfg.logo.x : (isCentered ? Math.round((cfg.width - logoMeta.width) / 2) : cfg.layout.leftX);
    const logoY = cfg.logo.y != null ? cfg.logo.y : Math.round(cfg.layout.footerY - logoMeta.height / 2);
    // White outer glow — blur logo alpha, recolor white, composite under logo
    // This follows the logo shape (not a rectangle) like Nike/Apple on dark heroes
    const glowRadius = cfg.logo.glowRadius || 12;
    const glowOpacity = cfg.logo.glowOpacity || 0.7;
    const glowBuf = await sharp(logoBuf)
      .extractChannel(3)  // alpha channel only
      .toColourspace('b-w')
      .linear(glowOpacity * 2.5, 0)  // brighten
      .blur(glowRadius)
      .toBuffer();
    // Create white glow from the blurred alpha
    const glowW = logoMeta.width;
    const glowH = logoMeta.height;
    const glowLayer = await sharp({
      create: { width: glowW, height: glowH, channels: 4, background: { r: 255, g: 255, b: 255, alpha: 0 } }
    })
      .composite([{ input: glowBuf, blend: 'dest-in' }])
      .png()
      .toBuffer();
    // Extend glow buffer to match canvas and position it
    const glowPad = glowRadius * 2;
    const extendedGlow = await sharp({
      create: { width: cfg.width, height: cfg.height, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } }
    })
      .composite([{ input: glowLayer, left: logoX, top: logoY }])
      .blur(glowRadius)
      .png()
      .toBuffer();
    composites.push({ input: extendedGlow });
    composites.push({ input: logoBuf, left: logoX, top: logoY });
  }
  const base = (cfg.backgroundPath && fileExists(cfg.backgroundPath))
    ? sharp(cfg.backgroundPath).resize(cfg.width, cfg.height, { fit: 'cover', position: cfg.backgroundPosition || 'center' }).modulate({ brightness: 0.82, saturation: 1.05 })
    : sharp({ create: { width: cfg.width, height: cfg.height, channels: 3, background: { r: 11, g: 42, b: 64 } } }).composite([{ input: Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="${cfg.theme.gradientStart}"/><stop offset="100%" stop-color="${cfg.theme.gradientEnd}"/></linearGradient></defs><rect width="100%" height="100%" fill="url(#g)"/></svg>`) }]);
  const ext = path.extname(cfg.output).toLowerCase();
  let pipeline = base.composite(composites);
  if (ext === '.png') pipeline = pipeline.png({ compressionLevel: 9 });
  else if (ext === '.webp') pipeline = pipeline.webp({ quality: 92 });
  else pipeline = pipeline.jpeg({ quality: 90 });
  await pipeline.toFile(cfg.output);
  const meta = await sharp(cfg.output).metadata();
  const review = runReview(cfg, meta);
  const reviewPath = cfg.output.replace(/\.[^.]+$/, '') + '.review.json';
  fs.writeFileSync(reviewPath, JSON.stringify(review, null, 2));
  const layout = buildLayoutSidecar(cfg, primitiveElements, resolvedPrimitiveImageLayers);
  const layoutPath = cfg.output.replace(/\.[^.]+$/, '') + '.layout.json';
  fs.writeFileSync(layoutPath, JSON.stringify(layout, null, 2));
  return { output: cfg.output, width: meta.width, height: meta.height, preset: cfg.preset, template: cfg.template, personality: cfg.layout.personality, reviewStatus: review.status, reviewPath, layoutPath };
}

async function main() {
  if (!fileExists(configPath)) throw new Error(`Config not found: ${configPath}`);
  const raw = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  if (Array.isArray(raw.renders)) {
    const results = [];
    for (const item of raw.renders) results.push(await renderOne(Object.assign({}, raw.defaults || {}, item)));
    console.log(JSON.stringify(results, null, 2));
    return;
  }
  const result = await renderOne(raw);
  console.log(JSON.stringify(result, null, 2));
}
main().catch((err) => { console.error(err.message); process.exit(1); });
