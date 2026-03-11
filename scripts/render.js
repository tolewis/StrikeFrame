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
  try {
    fs.accessSync(filePath, fs.constants.R_OK);
    return true;
  } catch {
    return false;
  }
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function escapeXml(value = '') {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function wrapText(text, maxChars) {
  const words = String(text || '').split(/\s+/).filter(Boolean);
  const lines = [];
  let current = '';
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) lines.push(current);
  return lines;
}

function normalizeConfig(raw) {
  const preset = PRESETS[raw.preset || 'landscape-banner'];
  if (!preset) throw new Error(`Unknown preset: ${raw.preset}`);
  return {
    preset: raw.preset || 'landscape-banner',
    template: raw.template || 'banner',
    width: raw.width || preset.width,
    height: raw.height || preset.height,
    output: path.isAbsolute(raw.output) ? raw.output : path.join(projectRoot, raw.output || 'output/render.jpg'),
    backgroundPath: raw.backgroundPath,
    productPath: raw.productPath || null,
    overlay: Object.assign({ leftOpacity: 0.78, midOpacity: 0.42, rightOpacity: 0.18, vignetteBottom: 0.30, leftColor: '5,14,24', midColor: '5,14,24', rightColor: '5,14,24' }, raw.overlay || {}),
    text: Object.assign({
      headline: 'Headline goes here',
      subhead: 'Subhead goes here',
      cta: 'LEARN MORE',
      footer: 'MEDIA RENDERER MVP'
    }, raw.text || {}),
    theme: Object.assign({
      headlineColor: '#ffffff',
      subheadColor: '#e8eef2',
      footerColor: '#d6dde2',
      ctaTextColor: '#ffffff',
      ctaFill: 'rgba(255,255,255,0.16)',
      ctaStroke: 'rgba(255,255,255,0.28)',
      gradientStart: '#0b2a40',
      gradientEnd: '#1f6b8f',
      badgeFill: 'rgba(255,255,255,0.16)',
      badgeStroke: 'rgba(255,255,255,0.24)',
      badgeTextColor: '#ffffff',
      productCircleFill: 'rgba(255,255,255,0.94)',
      productShadowColor: '0,0,0'
    }, raw.theme || {}),
    layout: Object.assign({
      leftX: 120,
      headlineY: raw.preset === 'social-portrait' ? 180 : 168,
      subheadY: raw.preset === 'social-portrait' ? 470 : 392,
      ctaX: 132,
      ctaY: raw.preset === 'social-portrait' ? 650 : 560,
      footerY: raw.preset === 'social-portrait' ? preset.height - 84 : preset.height - 88,
      maxHeadlineChars: raw.preset === 'social-portrait' ? 18 : 22,
      maxSubheadChars: raw.preset === 'social-portrait' ? 28 : 42,
      ctaWidth: 274,
      ctaHeight: 58,
      ctaRectX: 96,
      ctaRectY: raw.preset === 'social-portrait' ? 612 : 522
    }, raw.layout || {}),
    productComposite: Object.assign({
      enabled: raw.template === 'product-composite',
      circleDiameter: raw.preset === 'social-portrait' ? 360 : 300,
      circleX: raw.preset === 'social-portrait' ? preset.width - 420 : preset.width - 380,
      circleY: raw.preset === 'social-portrait' ? 260 : 180,
      shadowOpacity: 0.16,
      productWidth: raw.preset === 'social-portrait' ? 260 : 230,
      productOffsetX: 35,
      productOffsetY: 35,
      badgeText: 'PRODUCT',
      badgeX: raw.preset === 'social-portrait' ? preset.width - 360 : preset.width - 330,
      badgeY: raw.preset === 'social-portrait' ? 180 : 120
    }, raw.productComposite || {})
  };
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

function buildTextSvg(cfg) {
  const { width, height, text, layout, theme } = cfg;
  const headlineLines = wrapText(text.headline, layout.maxHeadlineChars);
  const subheadLines = wrapText(text.subhead, layout.maxSubheadChars);
  const headlineStep = cfg.preset === 'social-portrait' ? 82 : 88;
  const subheadStep = 40;
  const headlineFont = cfg.preset === 'social-portrait' ? 66 : 78;
  const subheadFont = cfg.preset === 'social-portrait' ? 30 : 32;
  const footerFont = cfg.preset === 'social-portrait' ? 18 : 21;
  const headlineTspans = headlineLines.map((line, i) => `<tspan x="${layout.leftX}" dy="${i === 0 ? 0 : headlineStep}">${escapeXml(line)}</tspan>`).join('');
  const subheadTspans = subheadLines.map((line, i) => `<tspan x="${layout.leftX}" dy="${i === 0 ? 0 : subheadStep}">${escapeXml(line)}</tspan>`).join('');
  return Buffer.from(`
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect x="${layout.ctaRectX}" y="${layout.ctaRectY}" width="${layout.ctaWidth}" height="${layout.ctaHeight}" rx="29" fill="${theme.ctaFill}" stroke="${theme.ctaStroke}" />
      <text x="${layout.leftX}" y="${layout.headlineY}" fill="${theme.headlineColor}" font-size="${headlineFont}" font-family="Arial, Helvetica, sans-serif" font-weight="700">${headlineTspans}</text>
      <text x="${layout.leftX}" y="${layout.subheadY}" fill="${theme.subheadColor}" font-size="${subheadFont}" font-family="Arial, Helvetica, sans-serif" font-weight="400">${subheadTspans}</text>
      <text x="${layout.ctaX}" y="${layout.ctaY}" fill="${theme.ctaTextColor}" font-size="24" font-family="Arial, Helvetica, sans-serif" font-weight="700">${escapeXml(text.cta)}</text>
      <text x="${layout.leftX}" y="${layout.footerY}" fill="${theme.footerColor}" font-size="${footerFont}" font-family="Arial, Helvetica, sans-serif" letter-spacing="3">${escapeXml(text.footer)}</text>
    </svg>`);
}

function buildCompositeSvg(cfg) {
  const { width, height, productComposite, theme } = cfg;
  if (!productComposite.enabled) return null;
  const d = productComposite.circleDiameter;
  return Buffer.from(`
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${productComposite.circleX + d / 2}" cy="${productComposite.circleY + d / 2 + 20}" r="${d / 2}" fill="rgba(${theme.productShadowColor},${productComposite.shadowOpacity})" />
      <circle cx="${productComposite.circleX + d / 2}" cy="${productComposite.circleY + d / 2}" r="${d / 2}" fill="${theme.productCircleFill}" />
      <rect x="${productComposite.badgeX}" y="${productComposite.badgeY}" width="170" height="42" rx="21" fill="${theme.badgeFill}" stroke="${theme.badgeStroke}" />
      <text x="${productComposite.badgeX + 24}" y="${productComposite.badgeY + 28}" fill="${theme.badgeTextColor}" font-size="20" font-family="Arial, Helvetica, sans-serif" font-weight="700">${escapeXml(productComposite.badgeText)}</text>
    </svg>`);
}

async function buildProductLayer(cfg) {
  if (!cfg.productComposite.enabled || !cfg.productPath || !fileExists(cfg.productPath)) return null;
  return sharp(cfg.productPath)
    .resize({ width: cfg.productComposite.productWidth, fit: 'inside' })
    .png()
    .toBuffer();
}

async function main() {
  if (!fileExists(configPath)) throw new Error(`Config not found: ${configPath}`);
  const raw = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const cfg = normalizeConfig(raw);
  ensureDir(cfg.output);

  const composites = [
    { input: buildOverlaySvg(cfg) },
    { input: buildTextSvg(cfg) }
  ];

  const compositeSvg = buildCompositeSvg(cfg);
  if (compositeSvg) composites.splice(1, 0, { input: compositeSvg });

  const productLayer = await buildProductLayer(cfg);
  if (productLayer) {
    composites.push({
      input: productLayer,
      left: cfg.productComposite.circleX + cfg.productComposite.productOffsetX,
      top: cfg.productComposite.circleY + cfg.productComposite.productOffsetY
    });
  }

  const base = (cfg.backgroundPath && fileExists(cfg.backgroundPath))
    ? sharp(cfg.backgroundPath).resize(cfg.width, cfg.height, { fit: 'cover', position: 'center' }).modulate({ brightness: 0.82, saturation: 1.05 })
    : sharp({
        create: {
          width: cfg.width,
          height: cfg.height,
          channels: 3,
          background: { r: 11, g: 42, b: 64 }
        }
      }).composite([{ input: Buffer.from(`
        <svg width="${cfg.width}" height="${cfg.height}" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="${cfg.theme.gradientStart}"/>
              <stop offset="100%" stop-color="${cfg.theme.gradientEnd}"/>
            </linearGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#g)"/>
        </svg>`)}]);

  await base
    .composite(composites)
    .jpeg({ quality: 90 })
    .toFile(cfg.output);

  const meta = await sharp(cfg.output).metadata();
  console.log(JSON.stringify({ output: cfg.output, width: meta.width, height: meta.height, preset: cfg.preset, template: cfg.template }, null, 2));
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
