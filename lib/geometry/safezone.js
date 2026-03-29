'use strict';

const Rect = require('./rect');

/**
 * Safe-zone model for StrikeFrame geometry system.
 *
 * Safe zones define the regions where content should live to avoid
 * being cut off by platform UI, device bezels, or visual margin issues.
 *
 * Three zone types:
 *   1. Canvas safe zone — inset from canvas edges (platform crop/UI safety)
 *   2. Text safe zone — tighter inset where text must stay readable
 *   3. CTA safe zone — where CTA buttons must sit to be tappable
 */

/**
 * Default safe-zone insets per preset.
 * Values are {top, right, bottom, left} in pixels.
 *
 * These are conservative defaults based on:
 * - Meta/Instagram: 14px title bar, 250px bottom gradient on stories/reels
 * - LinkedIn: minimal crop, but feeds get tight margins on mobile
 * - Google Display: varies widely, 40px is safe minimum
 */
const PRESET_SAFE_ZONES = {
  'social-square': {       // 1080x1080
    canvas:  { top: 40, right: 40, bottom: 40, left: 40 },
    text:    { top: 60, right: 60, bottom: 80, left: 60 },
    cta:     { top: 200, right: 60, bottom: 40, left: 60 }
  },
  'social-portrait': {     // 1080x1350
    canvas:  { top: 40, right: 40, bottom: 40, left: 40 },
    text:    { top: 60, right: 60, bottom: 100, left: 60 },
    cta:     { top: 300, right: 60, bottom: 40, left: 60 }
  },
  'landscape-banner': {    // 1600x900
    canvas:  { top: 40, right: 40, bottom: 40, left: 40 },
    text:    { top: 60, right: 80, bottom: 80, left: 80 },
    cta:     { top: 200, right: 80, bottom: 40, left: 80 }
  },
  'linkedin-landscape': {  // 1200x627
    canvas:  { top: 30, right: 30, bottom: 30, left: 30 },
    text:    { top: 40, right: 50, bottom: 60, left: 50 },
    cta:     { top: 150, right: 50, bottom: 30, left: 50 }
  },
  'google-landscape': {    // 1200x628
    canvas:  { top: 30, right: 30, bottom: 30, left: 30 },
    text:    { top: 40, right: 50, bottom: 60, left: 50 },
    cta:     { top: 150, right: 50, bottom: 30, left: 50 }
  },
  'google-portrait': {     // 960x1200
    canvas:  { top: 40, right: 40, bottom: 40, left: 40 },
    text:    { top: 60, right: 60, bottom: 80, left: 60 },
    cta:     { top: 250, right: 60, bottom: 40, left: 60 }
  }
};

// Fallback for unknown presets
const DEFAULT_SAFE_ZONE = {
  canvas:  { top: 40, right: 40, bottom: 40, left: 40 },
  text:    { top: 60, right: 60, bottom: 80, left: 60 },
  cta:     { top: 200, right: 60, bottom: 40, left: 60 }
};

/**
 * Get safe-zone rects for a canvas.
 *
 * @param {number} width - Canvas width
 * @param {number} height - Canvas height
 * @param {string} [preset] - Preset name for preset-specific insets
 * @param {object} [overrides] - Custom insets { canvas, text, cta }
 * @returns {object} { canvas, text, cta } — each a Rect
 */
function getSafeZones(width, height, preset, overrides) {
  const base = PRESET_SAFE_ZONES[preset] || DEFAULT_SAFE_ZONE;
  const canvas = Rect.create(0, 0, width, height);

  function insetRect(insets) {
    const merged = { ...insets, ...(overrides && overrides[name]) };
    return Rect.create(
      merged.left,
      merged.top,
      width - merged.left - merged.right,
      height - merged.top - merged.bottom
    );
  }

  return {
    canvas,
    canvasSafe: Rect.create(
      base.canvas.left,
      base.canvas.top,
      width - base.canvas.left - base.canvas.right,
      height - base.canvas.top - base.canvas.bottom
    ),
    textSafe: Rect.create(
      base.text.left,
      base.text.top,
      width - base.text.left - base.text.right,
      height - base.text.top - base.text.bottom
    ),
    ctaSafe: Rect.create(
      base.cta.left,
      base.cta.top,
      width - base.cta.left - base.cta.right,
      height - base.cta.top - base.cta.bottom
    )
  };
}

/**
 * Run all safe-zone checks on a set of elements.
 *
 * @param {Array} elements - Array of { id, type, rect } objects
 * @param {object} zones - Output of getSafeZones()
 * @returns {object} { violations, summary }
 */
function checkAll(elements, zones) {
  const violations = [];

  for (const el of elements) {
    // Everything should be inside canvas safe zone
    if (!Rect.contains(zones.canvasSafe, el.rect)) {
      const overLeft = Math.max(0, zones.canvasSafe.left - el.rect.left);
      const overTop = Math.max(0, zones.canvasSafe.top - el.rect.top);
      const overRight = Math.max(0, el.rect.right - zones.canvasSafe.right);
      const overBottom = Math.max(0, el.rect.bottom - zones.canvasSafe.bottom);
      violations.push({
        id: el.id,
        zone: 'canvas',
        type: 'hard',
        overflow: { overLeft, overTop, overRight, overBottom },
        severity: Math.max(overLeft, overTop, overRight, overBottom)
      });
    }

    // Text elements should be inside text safe zone
    if (el.type === 'text' && !Rect.contains(zones.textSafe, el.rect)) {
      const overLeft = Math.max(0, zones.textSafe.left - el.rect.left);
      const overTop = Math.max(0, zones.textSafe.top - el.rect.top);
      const overRight = Math.max(0, el.rect.right - zones.textSafe.right);
      const overBottom = Math.max(0, el.rect.bottom - zones.textSafe.bottom);
      violations.push({
        id: el.id,
        zone: 'text',
        type: 'soft',
        overflow: { overLeft, overTop, overRight, overBottom },
        severity: Math.max(overLeft, overTop, overRight, overBottom)
      });
    }

    // CTA elements should be inside CTA safe zone
    if (el.type === 'cta' && !Rect.contains(zones.ctaSafe, el.rect)) {
      const overLeft = Math.max(0, zones.ctaSafe.left - el.rect.left);
      const overTop = Math.max(0, zones.ctaSafe.top - el.rect.top);
      const overRight = Math.max(0, el.rect.right - zones.ctaSafe.right);
      const overBottom = Math.max(0, el.rect.bottom - zones.ctaSafe.bottom);
      violations.push({
        id: el.id,
        zone: 'cta',
        type: 'hard',
        overflow: { overLeft, overTop, overRight, overBottom },
        severity: Math.max(overLeft, overTop, overRight, overBottom)
      });
    }
  }

  const hardViolations = violations.filter(v => v.type === 'hard');
  const softViolations = violations.filter(v => v.type === 'soft');

  return {
    violations,
    summary: {
      total: violations.length,
      hard: hardViolations.length,
      soft: softViolations.length,
      pass: hardViolations.length === 0,
      worstSeverity: violations.length > 0 ? Math.max(...violations.map(v => v.severity)) : 0
    }
  };
}

/**
 * Mobile readability check.
 * Simulates rendering on a 375px-wide phone screen.
 * Returns warnings for text that would be too small to read.
 */
function mobileReadabilityCheck(elements, canvasWidth, minMobileFontSize = 11) {
  const scale = 375 / canvasWidth;
  const warnings = [];
  for (const el of elements) {
    if (el.type === 'text' && el.fontSize) {
      const mobileSize = Math.round(el.fontSize * scale * 10) / 10;
      if (mobileSize < minMobileFontSize) {
        warnings.push({
          id: el.id,
          canvasSize: el.fontSize,
          mobileSize,
          minRequired: minMobileFontSize,
          message: `${el.id} renders at ${mobileSize}px on mobile (min ${minMobileFontSize}px)`
        });
      }
    }
    // CTA tap target check — Apple minimum is 44px
    if (el.type === 'cta') {
      const mobileHeight = Math.round(el.rect.height * scale);
      if (mobileHeight < 44) {
        warnings.push({
          id: el.id,
          canvasHeight: el.rect.height,
          mobileHeight,
          minRequired: 44,
          message: `${el.id} tap target is ${mobileHeight}px on mobile (Apple minimum 44px)`
        });
      }
    }
  }
  return warnings;
}

module.exports = {
  PRESET_SAFE_ZONES,
  getSafeZones,
  checkAll,
  mobileReadabilityCheck
};
