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
    shapes: Array.isArray(raw.shapes) ? raw.shapes : [],
    textLayers: Array.isArray(raw.textLayers) ? raw.textLayers : []
  };
  if (cfg.review.enforcePanelFit && cfg.layout.personality === 'split-card') {
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

function buildPrimaryTextSvg(cfg) {
  const { width, text, layout, theme, typography } = cfg;
  const headlineLines = wrapText(text.headline, layout.maxHeadlineChars);
  const subheadLines = wrapText(text.subhead, layout.maxSubheadChars);
  const headlineStep = cfg.preset === 'social-portrait' ? 82 : (cfg.preset === 'linkedin-landscape' ? 68 : 88);
  const subheadStep = cfg.preset === 'linkedin-landscape' ? 34 : 40;
  const isCentered = layout.personality === 'centered-hero' || layout.align === 'center';
  const headlineAnchor = isCentered ? 'middle' : 'start';
  const headlineX = isCentered ? Math.round(width / 2) : layout.leftX;
  const subheadX = headlineX;
  const footerX = headlineX;
  const ctaRectX = isCentered ? Math.round((width - layout.ctaWidth) / 2) : layout.ctaRectX;
  const ctaTextX = isCentered ? Math.round(width / 2) : layout.ctaX;
  const ctaAnchor = isCentered ? 'middle' : 'start';
  const panel = layout.personality === 'split-card'
    ? `<rect x="${layout.panelX}" y="${layout.panelY}" width="${layout.panelWidth}" height="${layout.panelHeight}" rx="36" fill="${theme.textPanelFill}" stroke="${theme.textPanelStroke}" />`
    : '';
  const headlineTspans = headlineLines.map((line, i) => `<tspan x="${headlineX}" dy="${i === 0 ? 0 : headlineStep}">${escapeXml(line)}</tspan>`).join('');
  const subheadTspans = subheadLines.map((line, i) => `<tspan x="${subheadX}" dy="${i === 0 ? 0 : subheadStep}">${escapeXml(line)}</tspan>`).join('');
  return Buffer.from(`
    <svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
      ${panel}
      <rect x="${ctaRectX}" y="${layout.ctaRectY}" width="${layout.ctaWidth}" height="${layout.ctaHeight}" rx="29" fill="${theme.ctaFill}" stroke="${theme.ctaStroke}" />
      <text x="${headlineX}" y="${layout.headlineY}" text-anchor="${headlineAnchor}" fill="${theme.headlineColor}" font-size="${typography.headlineSize}" font-family="${typography.headlineFontFamily}" font-weight="${typography.headlineWeight}">${headlineTspans}</text>
      <text x="${subheadX}" y="${layout.subheadY}" text-anchor="${headlineAnchor}" fill="${theme.subheadColor}" font-size="${typography.subheadSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.subheadWeight}">${subheadTspans}</text>
      <text x="${ctaTextX}" y="${layout.ctaY}" text-anchor="${ctaAnchor}" fill="${theme.ctaTextColor}" font-size="${typography.ctaSize}" font-family="${typography.bodyFontFamily}" font-weight="${typography.ctaWeight}">${escapeXml(text.cta)}</text>
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
    return `${shadow}<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${t.color || '#ffffff'}" font-size="${t.fontSize || 28}" font-family="${t.fontFamily || cfg.typography.bodyFontFamily}" font-weight="${t.fontWeight || 600}">${tspans}</text>`;
  }).join('\n');
  return Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">${nodes}</svg>`);
}

function buildCompositeSvg(cfg) {
  const { productComposite, theme, typography } = cfg;
  if (!productComposite.enabled) return null;
  const d = productComposite.circleDiameter;
  return Buffer.from(`
    <svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${productComposite.circleX + d / 2}" cy="${productComposite.circleY + d / 2 + 20}" r="${d / 2}" fill="rgba(${theme.productShadowColor},${productComposite.shadowOpacity})" />
      <circle cx="${productComposite.circleX + d / 2}" cy="${productComposite.circleY + d / 2}" r="${d / 2}" fill="${theme.productCircleFill}" />
      <rect x="${productComposite.badgeX}" y="${productComposite.badgeY}" width="170" height="42" rx="21" fill="${theme.badgeFill}" stroke="${theme.badgeStroke}" />
      <text x="${productComposite.badgeX + 24}" y="${productComposite.badgeY + 28}" fill="${theme.badgeTextColor}" font-size="20" font-family="${typography.bodyFontFamily}" font-weight="700">${escapeXml(productComposite.badgeText)}</text>
    </svg>`);
}

async function buildProductLayer(cfg) {
  if (!cfg.productComposite.enabled || !cfg.productPath || !fileExists(cfg.productPath)) return null;
  return sharp(cfg.productPath).resize({ width: cfg.productComposite.productWidth, fit: 'inside' }).png().toBuffer();
}

async function renderOne(rawConfig) {
  const cfg = normalizeConfig(rawConfig);
  ensureDir(cfg.output);
  const composites = [{ input: buildOverlaySvg(cfg) }];
  const shapes = buildShapesSvg(cfg); if (shapes) composites.push({ input: shapes });
  composites.push({ input: buildPrimaryTextSvg(cfg) });
  const textLayers = buildTextLayersSvg(cfg); if (textLayers) composites.push({ input: textLayers });
  const compositeSvg = buildCompositeSvg(cfg); if (compositeSvg) composites.push({ input: compositeSvg });
  const productLayer = await buildProductLayer(cfg);
  if (productLayer) composites.push({ input: productLayer, left: cfg.productComposite.circleX + cfg.productComposite.productOffsetX, top: cfg.productComposite.circleY + cfg.productComposite.productOffsetY });
  const base = (cfg.backgroundPath && fileExists(cfg.backgroundPath))
    ? sharp(cfg.backgroundPath).resize(cfg.width, cfg.height, { fit: 'cover', position: 'center' }).modulate({ brightness: 0.82, saturation: 1.05 })
    : sharp({ create: { width: cfg.width, height: cfg.height, channels: 3, background: { r: 11, g: 42, b: 64 } } }).composite([{ input: Buffer.from(`<svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="${cfg.theme.gradientStart}"/><stop offset="100%" stop-color="${cfg.theme.gradientEnd}"/></linearGradient></defs><rect width="100%" height="100%" fill="url(#g)"/></svg>`) }]);
  await base.composite(composites).jpeg({ quality: 90 }).toFile(cfg.output);
  const meta = await sharp(cfg.output).metadata();
  return { output: cfg.output, width: meta.width, height: meta.height, preset: cfg.preset, template: cfg.template, personality: cfg.layout.personality };
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
