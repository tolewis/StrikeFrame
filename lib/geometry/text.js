'use strict';

const Rect = require('./rect');

/**
 * Text measurement for StrikeFrame geometry system.
 *
 * Uses per-font average character width ratios derived from published
 * font metrics. These are not pixel-perfect (that requires actual font
 * file parsing via opentype.js), but they are significantly better than
 * the blanket 0.58 ratio used previously.
 *
 * Width ratios represent the average character width as a fraction of
 * font size (em). Measured from real font files using typical ad copy
 * character distributions (uppercase-heavy headlines, mixed-case body).
 */

// Average character width as fraction of fontSize.
// Measured per font family for typical ad copy character distributions.
// Uppercase-heavy text (headlines, CTAs) uses different ratios than mixed-case.
const FONT_METRICS = {
  // Montserrat — geometric sans, wide characters
  'montserrat': {
    upper: 0.68,    // ALL CAPS headlines, CTAs
    mixed: 0.58,    // Mixed case body text
    narrow: 0.52,   // Numerals and punctuation
    lineHeight: 1.2, // Default line height ratio
    capHeight: 0.72, // Cap height as fraction of fontSize
    ascender: 0.93,
    descender: 0.25
  },
  // Source Sans Pro — humanist sans, slightly narrower
  'source sans pro': {
    upper: 0.62,
    mixed: 0.53,
    narrow: 0.48,
    lineHeight: 1.2,
    capHeight: 0.66,
    ascender: 0.93,
    descender: 0.29
  },
  'source sans 3': {  // Source Sans Pro renamed in newer versions
    upper: 0.62,
    mixed: 0.53,
    narrow: 0.48,
    lineHeight: 1.2,
    capHeight: 0.66,
    ascender: 0.93,
    descender: 0.29
  },
  // Georgia — serif, moderate width, wider serifs
  'georgia': {
    upper: 0.64,
    mixed: 0.55,
    narrow: 0.50,
    lineHeight: 1.2,
    capHeight: 0.68,
    ascender: 0.91,
    descender: 0.24
  },
  // Arial — fallback sans
  'arial': {
    upper: 0.63,
    mixed: 0.55,
    narrow: 0.49,
    lineHeight: 1.15,
    capHeight: 0.72,
    ascender: 0.91,
    descender: 0.21
  },
  // Times New Roman — fallback serif
  'times new roman': {
    upper: 0.60,
    mixed: 0.50,
    narrow: 0.45,
    lineHeight: 1.15,
    capHeight: 0.66,
    ascender: 0.89,
    descender: 0.22
  },
  // Default fallback
  '_default': {
    upper: 0.62,
    mixed: 0.55,
    narrow: 0.48,
    lineHeight: 1.2,
    capHeight: 0.70,
    ascender: 0.92,
    descender: 0.24
  }
};

// Special character widths relative to fontSize (these are consistent across fonts)
const SPECIAL_WIDTHS = {
  '\u2605': 1.0,   // ★ star
  '\u2713': 0.7,   // ✓ checkmark
  '\u2717': 0.7,   // ✗ cross mark
  '\u2022': 0.4,   // bullet
  '\u2014': 0.8,   // em dash
  '\u2013': 0.5,   // en dash
  ' ': 0.27         // space
};

/**
 * Resolve font metrics for a font-family CSS string.
 * Handles comma-separated fallback stacks like "Montserrat, Arial, sans-serif".
 */
function getFontMetrics(fontFamily) {
  if (!fontFamily) return FONT_METRICS['_default'];
  const primary = fontFamily.split(',')[0].trim().replace(/['"]/g, '').toLowerCase();
  return FONT_METRICS[primary] || FONT_METRICS['_default'];
}

/**
 * Classify text for width ratio selection.
 * Returns 'upper', 'mixed', or 'narrow'.
 */
function classifyText(text) {
  if (!text || text.length === 0) return 'mixed';
  let upperCount = 0;
  let digitPunctCount = 0;
  let alphaCount = 0;
  for (const ch of text) {
    if (ch >= 'A' && ch <= 'Z') { upperCount++; alphaCount++; }
    else if (ch >= 'a' && ch <= 'z') { alphaCount++; }
    else if ((ch >= '0' && ch <= '9') || ch === '$' || ch === '.' || ch === ',' || ch === '%') { digitPunctCount++; }
  }
  if (alphaCount > 0 && upperCount / alphaCount > 0.7) return 'upper';
  if (digitPunctCount > alphaCount) return 'narrow';
  return 'mixed';
}

/**
 * Measure the width of a text string in pixels.
 *
 * @param {string} text - The text to measure
 * @param {number} fontSize - Font size in pixels
 * @param {string} [fontFamily] - CSS font-family string
 * @param {object} [opts] - Options
 * @param {string} [opts.mode] - Force 'upper', 'mixed', or 'narrow' classification
 * @param {number} [opts.letterSpacing] - Additional letter spacing in pixels
 * @param {number} [opts.fontWeight] - Font weight (bold text is ~5% wider)
 * @returns {number} Estimated width in pixels
 */
function measureWidth(text, fontSize, fontFamily, opts = {}) {
  if (!text || text.length === 0) return 0;
  const metrics = getFontMetrics(fontFamily);
  const mode = opts.mode || classifyText(text);
  const baseRatio = metrics[mode] || metrics.mixed;

  let width = 0;
  for (const ch of text) {
    if (SPECIAL_WIDTHS[ch] != null) {
      width += SPECIAL_WIDTHS[ch] * fontSize;
    } else {
      width += baseRatio * fontSize;
    }
  }

  // Bold text is slightly wider (~3-5% for weights >= 700)
  if (opts.fontWeight && opts.fontWeight >= 700) {
    width *= 1.04;
  }

  // Letter spacing adds per-character
  if (opts.letterSpacing) {
    width += opts.letterSpacing * text.length;
  }

  return Math.round(width);
}

/**
 * Measure a text block: multiple lines with wrapping.
 *
 * @param {object} params
 * @param {string[]} params.lines - Pre-wrapped text lines
 * @param {number} params.fontSize - Font size in pixels
 * @param {string} [params.fontFamily] - CSS font-family
 * @param {number} [params.lineHeight] - Line height in pixels (overrides font default)
 * @param {number} params.x - X position of text origin
 * @param {number} params.y - Y position of text baseline (first line)
 * @param {string} [params.align] - 'left', 'center', or 'right'
 * @param {number} [params.fontWeight] - Font weight
 * @param {number} [params.letterSpacing] - Letter spacing
 * @returns {object} { rect, lines, lineRects, maxLineWidth, totalHeight, baseline }
 */
function measureBlock(params) {
  const {
    lines, fontSize, fontFamily, x, y,
    align = 'left', fontWeight, letterSpacing
  } = params;
  const metrics = getFontMetrics(fontFamily);
  const lineHeightPx = params.lineHeight || Math.round(fontSize * metrics.lineHeight);
  const measureOpts = { fontWeight, letterSpacing };

  // Measure each line
  const lineWidths = lines.map(line => measureWidth(line, fontSize, fontFamily, measureOpts));
  const maxLineWidth = Math.max(0, ...lineWidths);

  // Total height: first line cap + remaining lines at lineHeight
  const firstLineTop = Math.round(fontSize * metrics.capHeight);
  const totalHeight = lines.length <= 1
    ? firstLineTop
    : firstLineTop + (lines.length - 1) * lineHeightPx;

  // Compute block position based on alignment
  const blockTop = Math.round(y - firstLineTop);
  let blockLeft;
  switch (align) {
    case 'center': blockLeft = Math.round(x - maxLineWidth / 2); break;
    case 'right': blockLeft = Math.round(x - maxLineWidth); break;
    default: blockLeft = x;
  }

  const rect = Rect.create(blockLeft, blockTop, maxLineWidth, totalHeight);

  // Per-line rects
  const lineRects = lines.map((line, i) => {
    const w = lineWidths[i];
    const lineY = blockTop + (i === 0 ? 0 : firstLineTop + (i - 1) * lineHeightPx + (lineHeightPx - firstLineTop));
    let lineX;
    switch (align) {
      case 'center': lineX = Math.round(x - w / 2); break;
      case 'right': lineX = Math.round(x - w); break;
      default: lineX = x;
    }
    return {
      text: line,
      rect: Rect.create(lineX, lineY, w, i === 0 ? firstLineTop : lineHeightPx),
      width: w
    };
  });

  return {
    rect,
    lines,
    lineRects,
    maxLineWidth,
    totalHeight,
    lineCount: lines.length,
    fontSize,
    lineHeight: lineHeightPx,
    fontFamily: fontFamily || '_default',
    baseline: y
  };
}

/**
 * Quick single-line width estimate (drop-in replacement for the old 0.58 approach).
 * Use this when you just need a width number, not full block geometry.
 */
function quickWidth(text, fontSize, fontFamily) {
  return measureWidth(text, fontSize, fontFamily);
}

/**
 * Estimate how many characters fit in a given pixel width.
 */
function charsForWidth(targetWidth, fontSize, fontFamily, mode) {
  const metrics = getFontMetrics(fontFamily);
  const ratio = metrics[mode || 'mixed'];
  const charWidth = ratio * fontSize;
  return Math.floor(targetWidth / charWidth);
}

module.exports = {
  FONT_METRICS,
  getFontMetrics,
  classifyText,
  measureWidth,
  measureBlock,
  quickWidth,
  charsForWidth
};
