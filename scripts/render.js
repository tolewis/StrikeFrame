const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const projectRoot = path.resolve(__dirname, '..');
const argPath = process.argv[2] || 'configs/sample-banner.json';
const configPath = path.isAbsolute(argPath) ? argPath : path.join(projectRoot, argPath);

const PRESETS = {
  'landscape-banner': { width: 1600, height: 900 },
  'social-square': { width: 1080, height: 1080 },
  'social-portrait': { width: 1080, height: 1350 },
  'linkedin-landscape': { width: 1200, height: 627 }
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

function normalizeConfig(raw) {
  const preset = PRESETS[raw.preset || 'landscape-banner'];
  if (!preset) throw new Error(`Unknown preset: ${raw.preset}`);
  const chosenPreset = raw.preset || 'landscape-banner';
  const cfg = {
    preset: chosenPreset,
    template: raw.template || 'banner',
    width: raw.width || preset.width,
    height: raw.height || preset.height,
    output: path.isAbsolute(raw.output || '') ? raw.output : path.join(projectRoot, raw.output || 'output/render.jpg'),
    backgroundPath: raw.backgroundPath,
    productPath: raw.productPath || null,
    overlay: Object.assign({ leftOpacity: 0.78, midOpacity: 0.42, rightOpacity: 0.18, vignetteBottom: 0.30, leftColor: '5,14,24', midColor: '5,14,24', rightColor: '5,14,24' }, raw.overlay || {}),
    text: Object.assign({ headline: 'Headline goes here', subhead: 'Subhead goes here', cta: 'LEARN MORE', footer: 'STRIKEFRAME' }, raw.text || {}),
    theme: Object.assign({
      headlineColor: '#ffffff', subheadColor: '#e8eef2', footerColor: '#d6dde2', ctaTextColor: '#ffffff',
      ctaFill: 'rgba(255,255,255,0.16)', ctaStroke: 'rgba(255,255,255,0.28)', gradientStart: '#0b2a40', gradientEnd: '#1f6b8f',
      badgeFill: 'rgba(255,255,255,0.16)', badgeStroke: 'rgba(255,255,255,0.24)', badgeTextColor: '#ffffff',
      productCircleFill: 'rgba(255,255,255,0.94)', productShadowColor: '0,0,0', textPanelFill: 'rgba(255,255,255,0.08)', textPanelStroke: 'rgba(255,255,255,0.16)'
    }, raw.theme || {}),
    typography: Object.assign({
      headlineFontFamily: 'Montserrat, Arial, sans-serif', bodyFontFamily: 'Source Sans Pro, Arial, sans-serif',
      headlineWeight: 700, subheadWeight: 400, ctaWeight: 700, footerWeight: 600,
      headlineSize: presetDefault(chosenPreset, 66, chosenPreset === 'linkedin-landscape' ? 58 : 78),
      subheadSize: presetDefault(chosenPreset, 30, chosenPreset === 'linkedin-landscape' ? 28 : 32),
      ctaSize: 24, footerSize: presetDefault(chosenPreset, 18, chosenPreset === 'linkedin-landscape' ? 18 : 21),
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
      ctaWidth: chosenPreset === 'linkedin-landscape' ? 300 : 274, ctaHeight: 58, ctaRectX: 96,
      ctaRectY: chosenPreset === 'social-portrait' ? 612 : (chosenPreset === 'linkedin-landscape' ? 428 : 522),
      ctaGroup: null,
      panelX: 80, panelY: chosenPreset === 'social-portrait' ? 110 : 90,
      panelWidth: chosenPreset === 'social-portrait' ? 840 : (chosenPreset === 'linkedin-landscape' ? 700 : 760),
      panelHeight: chosenPreset === 'social-portrait' ? 760 : (chosenPreset === 'linkedin-landscape' ? 390 : 600)
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
    productImage: raw.productImage || null,
    shapes: Array.isArray(raw.shapes) ? raw.shapes : [],
    textLayers: Array.isArray(raw.textLayers) ? raw.textLayers : [],
    statBlocks: Array.isArray(raw.statBlocks) ? raw.statBlocks : [],
    dividers: Array.isArray(raw.dividers) ? raw.dividers : []
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
    const estHeadlineW = Math.round(Math.max(1, ...headlineLines.map(l => l.length)) * cfg.typography.headlineSize * 0.58);
    const estSubheadW = Math.round(Math.max(1, ...subheadLines.map(l => l.length)) * cfg.typography.subheadSize * 0.58);
    const maxTextRight = cfg.layout.leftX + Math.max(estHeadlineW, estSubheadW, cfg.layout.ctaWidth);
    const requiredWidth = maxTextRight - cfg.layout.panelX + panelPad;
    const maxPanelWidth = cfg.width - cfg.layout.panelX - 40;
    if (requiredWidth > cfg.layout.panelWidth) cfg.layout.panelWidth = Math.min(requiredWidth, maxPanelWidth);
    const estimatedPanelBottom = cfg.layout.ctaRectY + cfg.layout.ctaHeight + 40;
    const requiredHeight = estimatedPanelBottom - cfg.layout.panelY;
    if (requiredHeight > cfg.layout.panelHeight) cfg.layout.panelHeight = requiredHeight;
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
  const panel = layout.personality === 'split-card'
    ? `<rect x="${layout.panelX}" y="${layout.panelY}" width="${layout.panelWidth}" height="${layout.panelHeight}" rx="36" fill="${theme.textPanelFill}" stroke="${theme.textPanelStroke}" />`
    : '';
  const headlineTspans = headlineLines.map((line, i) => `<tspan x="${headlineX}" dy="${i === 0 ? 0 : headlineStep}">${escapeXml(line)}</tspan>`).join('');
  const subheadTspans = subheadLines.map((line, i) => `<tspan x="${subheadX}" dy="${i === 0 ? 0 : subheadStep}">${escapeXml(line)}</tspan>`).join('');
  return Buffer.from(`
    <svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
      ${panel}
      <rect x="${cta.rectX}" y="${cta.rectY}" width="${layout.ctaWidth}" height="${layout.ctaHeight}" rx="29" fill="${theme.ctaFill}" stroke="${theme.ctaStroke}" />
      <text x="${headlineX}" y="${layout.headlineY}" text-anchor="${headlineAnchor}" fill="${theme.headlineColor}" font-size="${typography.headlineSize}" font-family="${typography.headlineFontFamily}" font-weight="${typography.headlineWeight}">${headlineTspans}</text>
      <text x="${subheadX}" y="${layout.subheadY}" text-anchor="${headlineAnchor}" fill="${theme.subheadColor}" font-size="${typography.subheadSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.subheadWeight}">${subheadTspans}</text>
      <text x="${cta.textX}" y="${cta.textY}" dy="0.35em" text-anchor="${cta.textAnchor}" fill="${theme.ctaTextColor}" font-size="${typography.ctaSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.ctaWeight}">${escapeXml(text.cta).replace(/★+/g, m => `<tspan fill="#FFD700">${m}</tspan>`)}</text>
      <text x="${footerX}" y="${layout.footerY}" text-anchor="${headlineAnchor}" fill="${theme.footerColor}" font-size="${typography.footerSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.footerWeight}" letter-spacing="${typography.footerTracking}">${escapeXml(text.footer)}</text>
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


function estimateTextBlock({ lines, fontSize, lineStep, x, y, align = 'left', maxChars = 24 }) {
  const maxLen = Math.max(1, ...lines.map((l) => l.length));
  const estWidth = Math.round(maxLen * fontSize * 0.58);
  const estHeight = Math.round(fontSize + ((Math.max(lines.length, 1) - 1) * lineStep));
  let left = x;
  if (align === 'center') left = Math.round(x - estWidth / 2);
  if (align === 'right') left = Math.round(x - estWidth);
  const top = Math.round(y - fontSize * 0.82);
  return { left, top, width: estWidth, height: estHeight, right: left + estWidth, bottom: top + estHeight, lines: lines.length, maxChars };
}

function boxInside(inner, outer, pad = 0) {
  return inner.left >= outer.left + pad && inner.top >= outer.top + pad && inner.right <= outer.right - pad && inner.bottom <= outer.bottom - pad;
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
  const headlineBox = estimateTextBlock({ lines: headlineLines, fontSize: cfg.typography.headlineSize, lineStep: headlineStep, x: textX, y: cfg.layout.headlineY, align: anchor, maxChars: cfg.layout.maxHeadlineChars });
  const subheadBox = estimateTextBlock({ lines: subheadLines, fontSize: cfg.typography.subheadSize, lineStep: subheadStep, x: textX, y: cfg.layout.subheadY, align: anchor, maxChars: cfg.layout.maxSubheadChars });
  const footerBox = estimateTextBlock({ lines: [cfg.text.footer], fontSize: cfg.typography.footerSize, lineStep: cfg.typography.footerSize, x: textX, y: cfg.layout.footerY, align: anchor, maxChars: 60 });
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

async function buildRectProductLayer(cfg) {
  const pi = cfg.productImage;
  if (!pi || !pi.path || !fileExists(pi.path)) return null;
  const w = pi.width || 400;
  const h = pi.height || 400;
  const pad = pi.padding || 20;
  const productBuf = await sharp(pi.path)
    .resize({ width: w - pad * 2, height: h - pad * 2, fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 1 } })
    .png()
    .toBuffer();
  const prodMeta = await sharp(productBuf).metadata();
  return sharp({
    create: { width: w, height: h, channels: 4, background: { r: 255, g: 255, b: 255, alpha: 1 } }
  })
    .composite([{
      input: productBuf,
      left: Math.round((w - prodMeta.width) / 2),
      top: Math.round((h - prodMeta.height) / 2)
    }])
    .png()
    .toBuffer();
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
  composites.push({ input: buildPrimaryTextSvg(cfg) });
  const textLayers = buildTextLayersSvg(cfg); if (textLayers) composites.push({ input: textLayers });
  const statBlocksSvg = buildStatBlocksSvg(cfg); if (statBlocksSvg) composites.push({ input: statBlocksSvg });
  const compositeSvg = buildCompositeSvg(cfg); if (compositeSvg) composites.push({ input: compositeSvg });
  const productLayer = await buildProductLayer(cfg);
  if (productLayer) composites.push({ input: productLayer, left: cfg.productComposite.circleX, top: cfg.productComposite.circleY });
  const base = (cfg.backgroundPath && fileExists(cfg.backgroundPath))
    ? sharp(cfg.backgroundPath).resize(cfg.width, cfg.height, { fit: 'cover', position: 'center' }).modulate({ brightness: 0.82, saturation: 1.05 })
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
  return { output: cfg.output, width: meta.width, height: meta.height, preset: cfg.preset, template: cfg.template, personality: cfg.layout.personality, reviewStatus: review.status, reviewPath };
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
