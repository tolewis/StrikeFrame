'use strict';

const { Rect, Text, SafeZone } = require('../geometry');

/**
 * StrikeFrame Critic — rule-based layout quality scoring.
 *
 * Reads the layout sidecar and scores across 5 dimensions:
 *   1. Geometry   — collisions, safe-zone violations, overflow
 *   2. Hierarchy  — focal point, size ratios, element dominance
 *   3. Readability — mobile font sizes, tap targets, line count
 *   4. Spacing    — gap enforcement, balance, crowding/dead zones
 *   5. Persuasion — CTA visibility, proof presence, clutter level
 *
 * Output: { status, overallScore, dimensions, failures, warnings, revisionTargets }
 */

// --- Dimension scorers ---

function scoreGeometry(layout) {
  const score = { name: 'geometry', value: 100, findings: [] };

  // Safe-zone violations
  // Exclude elements that intentionally sit at edges (logo corner-anchor, empty placeholders)
  const EDGE_EXEMPT = new Set(['logo', 'footer']);
  const allViolations = layout.safeZones?.violations || [];
  const hardViolations = allViolations.filter(v => v.type === 'hard' && !EDGE_EXEMPT.has(v.id));
  const softViolations = allViolations.filter(v => v.type === 'soft' && !EDGE_EXEMPT.has(v.id));
  // Also exclude placeholder elements (fontSize <= 1)
  const elements = layout.elements || [];
  const isPlaceholder = (id) => {
    const el = elements.find(e => e.id === id);
    return el && el.fontSize != null && el.fontSize <= 1;
  };
  const realHard = hardViolations.filter(v => !isPlaceholder(v.id));
  const realSoft = softViolations.filter(v => !isPlaceholder(v.id));
  if (realHard.length > 0) {
    score.value -= Math.min(40, realHard.length * 15);
    score.findings.push({
      type: 'fail',
      rule: 'safe_zone_hard',
      message: `${realHard.length} element(s) violate hard safe zones`,
      targets: realHard.map(v => v.id),
      action: 'Move elements inside safe zone boundaries'
    });
  }
  if (realSoft.length > 0) {
    score.value -= Math.min(15, realSoft.length * 5);
    score.findings.push({
      type: 'warn',
      rule: 'safe_zone_soft',
      message: `${realSoft.length} element(s) violate soft safe zones`,
      targets: realSoft.map(v => v.id)
    });
  }

  // Collisions
  const collisions = layout.collisions || [];
  if (collisions.length > 0) {
    score.value -= Math.min(30, collisions.length * 10);
    score.findings.push({
      type: 'fail',
      rule: 'element_collision',
      message: `${collisions.length} element overlap(s) detected`,
      targets: collisions.map(c => `${c.a}↔${c.b}`),
      action: 'Separate overlapping elements or adjust positions'
    });
  }

  // Occupancy — benchmark ads fill 80-95% of canvas. Sparse is the real problem.
  const occ = layout.occupancy?.occupancyRatio || 0;
  if (occ < 0.05) {
    score.value -= 15;
    score.findings.push({ type: 'warn', rule: 'canvas_sparse', message: `Canvas only ${Math.round(occ * 100)}% occupied — feels empty` });
  }
  // High occupancy is good for paid social — only penalize extreme overcrowding
  if (occ > 0.85) {
    score.value -= 5;
    score.findings.push({ type: 'info', rule: 'canvas_dense', message: `Canvas ${Math.round(occ * 100)}% occupied — verify readability` });
  }

  score.value = Math.max(0, score.value);
  return score;
}

function scoreHierarchy(layout) {
  const score = { name: 'hierarchy', value: 100, findings: [] };
  const elements = layout.elements || [];

  // Find primary elements by ID
  const headline = elements.find(e => e.id === 'headline');
  const subhead = elements.find(e => e.id === 'subhead');
  const cta = elements.find(e => e.id === 'cta');

  // Headline should be the largest text element
  if (headline && headline.fontSize) {
    const textEls = elements.filter(e => e.type === 'text' && e.fontSize && e.id !== 'headline');
    const biggerThanHeadline = textEls.filter(e => e.fontSize > headline.fontSize);
    if (biggerThanHeadline.length > 0) {
      score.value -= 20;
      score.findings.push({
        type: 'warn',
        rule: 'headline_not_dominant',
        message: `${biggerThanHeadline.map(e => e.id).join(', ')} larger than headline`,
        targets: biggerThanHeadline.map(e => e.id),
        action: 'Increase headline size or reduce competing elements'
      });
    }
  }

  // Headline/subhead ratio should be >= 1.4x
  if (headline?.fontSize && subhead?.fontSize && subhead.fontSize > 1) {
    const ratio = headline.fontSize / subhead.fontSize;
    if (ratio < 1.4) {
      score.value -= 15;
      score.findings.push({
        type: 'warn',
        rule: 'weak_hierarchy_ratio',
        message: `Headline/subhead ratio ${ratio.toFixed(1)}x (want ≥1.4x)`,
        targets: ['headline', 'subhead'],
        action: 'Increase headline size or decrease subhead size'
      });
    }
  }

  // CTA should exist and have meaningful size
  if (cta) {
    if (cta.rect.area < 5000) {
      score.value -= 15;
      score.findings.push({
        type: 'warn',
        rule: 'cta_too_small',
        message: `CTA area ${cta.rect.area}px² — may be too small to notice`,
        targets: ['cta'],
        action: 'Increase CTA button width or height'
      });
    }
  } else {
    // Not all layouts need a CTA, so mild penalty
    score.value -= 5;
    score.findings.push({ type: 'info', rule: 'no_cta', message: 'No CTA element found' });
  }

  // Check for dominant focal point — the largest element by area
  const contentEls = elements.filter(e => e.type !== 'layout' && e.rect.area > 0);
  if (contentEls.length > 2) {
    const sorted = [...contentEls].sort((a, b) => b.rect.area - a.rect.area);
    const largest = sorted[0];
    const second = sorted[1];
    if (second && largest.rect.area > 0) {
      const dominance = largest.rect.area / second.rect.area;
      if (dominance < 1.5) {
        score.value -= 10;
        score.findings.push({
          type: 'warn',
          rule: 'weak_focal_point',
          message: `Top element (${largest.id}) only ${dominance.toFixed(1)}x larger than ${second.id} — weak focal point`,
          targets: [largest.id, second.id]
        });
      }
    }
  }

  score.value = Math.max(0, score.value);
  return score;
}

function scoreReadability(layout) {
  const score = { name: 'readability', value: 100, findings: [] };
  const mobileWarnings = layout.mobileReadability || [];

  // Mobile font size warnings — skip placeholders and primitives' internal small text
  const tooSmall = mobileWarnings.filter(w => w.canvasSize && w.mobileSize);
  if (tooSmall.length > 0) {
    // Only penalize content elements with real font sizes, not placeholders or table body text
    const realSmall = tooSmall.filter(w => w.canvasSize > 16 && !w.id.includes('.row.'));
    if (realSmall.length > 0) {
      score.value -= Math.min(20, realSmall.length * 5);
      score.findings.push({
        type: 'warn',
        rule: 'mobile_text_too_small',
        message: `${realSmall.length} text element(s) too small on mobile`,
        targets: realSmall.map(w => w.id),
        action: 'Increase font size to at least 14px canvas (renders ~5px mobile)'
      });
    }
  }

  // Tap target warnings
  const tapIssues = mobileWarnings.filter(w => w.canvasHeight);
  if (tapIssues.length > 0) {
    score.value -= Math.min(20, tapIssues.length * 10);
    score.findings.push({
      type: 'warn',
      rule: 'mobile_tap_target',
      message: `${tapIssues.length} CTA(s) below Apple 44px tap target on mobile`,
      targets: tapIssues.map(w => w.id),
      action: 'Increase CTA height to at least 89px canvas (renders ~31px mobile)'
    });
  }

  // Check headline line count via layout data
  const headline = (layout.elements || []).find(e => e.id === 'headline');
  if (headline && headline.rect.height > 0 && headline.fontSize) {
    const estLines = Math.round(headline.rect.height / (headline.fontSize * 1.1));
    if (estLines > 2) {
      score.value -= 15;
      score.findings.push({
        type: 'warn',
        rule: 'headline_too_many_lines',
        message: `Headline appears to be ${estLines} lines (max 2 preferred)`,
        targets: ['headline'],
        action: 'Shorten headline copy or increase maxHeadlineChars'
      });
    }
  }

  score.value = Math.max(0, score.value);
  return score;
}

function scoreSpacing(layout) {
  const score = { name: 'spacing', value: 100, findings: [] };
  const spacingChecks = layout.spacing || [];

  for (const check of spacingChecks) {
    if (!check.pass) {
      const severity = check.min - check.gap;
      if (severity > 20) {
        score.value -= 20;
        score.findings.push({
          type: 'fail',
          rule: 'spacing_violation',
          message: `${check.pair.join('→')} gap ${check.gap}px, need ${check.min}px (${severity}px short)`,
          targets: check.pair,
          action: `Increase gap between ${check.pair[0]} and ${check.pair[1]} by ${severity}px`
        });
      } else {
        score.value -= 10;
        score.findings.push({
          type: 'warn',
          rule: 'spacing_tight',
          message: `${check.pair.join('→')} gap ${check.gap}px, want ${check.min}px`,
          targets: check.pair
        });
      }
    }
  }

  // Vertical fill — benchmark ads use 80-95% of canvas height.
  // Below 65% = dead space problem. Below 50% = layout failure.
  const bbox = layout.occupancy?.boundingBox;
  if (bbox && layout.canvas) {
    const utilization = bbox.height / layout.canvas.height;
    if (utilization < 0.50) {
      score.value -= 25;
      score.findings.push({
        type: 'fail',
        rule: 'vertical_underuse',
        message: `Content uses only ${Math.round(utilization * 100)}% of canvas height — significant dead space`,
        action: 'Expand content vertically or add supporting elements'
      });
    } else if (utilization < 0.65) {
      score.value -= 15;
      score.findings.push({
        type: 'warn',
        rule: 'vertical_underuse',
        message: `Content uses ${Math.round(utilization * 100)}% of canvas height — benchmark is 80%+`,
        action: 'Spread elements or add content to fill canvas'
      });
    }
  }

  score.value = Math.max(0, score.value);
  return score;
}

function scorePersuasion(layout) {
  const score = { name: 'persuasion', value: 100, findings: [] };
  const elements = layout.elements || [];

  // CTA visibility — should be in lower third of canvas
  const cta = elements.find(e => e.id === 'cta' || e.type === 'cta');
  if (cta && layout.canvas) {
    const ctaCenter = cta.rect.centerY;
    const lowerThird = layout.canvas.height * 0.66;
    if (ctaCenter < lowerThird) {
      score.value -= 10;
      score.findings.push({
        type: 'warn',
        rule: 'cta_position_high',
        message: `CTA center at ${Math.round(ctaCenter)}px — above lower third (${Math.round(lowerThird)}px)`,
        targets: [cta.id],
        action: 'Move CTA toward bottom third of canvas'
      });
    }
  }

  // Primitive-specific proof checks
  const proofElements = elements.filter(e => e.id.includes('proof') || e.id.includes('review') || e.id.includes('testimonial') || e.id.includes('stars'));
  const comparisonElements = elements.filter(e => e.id.includes('comparisonPanel'));
  const offerElements = elements.filter(e => e.id.includes('offerFrame'));

  // If it's a proof/testimonial layout, check that proof elements exist
  if (proofElements.length > 0) {
    const hasStars = proofElements.some(e => e.id.includes('stars'));
    const hasQuote = proofElements.some(e => e.id.includes('quote'));
    if (!hasStars && !hasQuote) {
      score.value -= 15;
      score.findings.push({
        type: 'warn',
        rule: 'proof_missing_elements',
        message: 'Proof layout without stars or quote — weak social proof',
        action: 'Add star rating or customer quote'
      });
    }
  }

  // Clutter check — too many elements reduces persuasion
  const contentCount = elements.filter(e => e.type !== 'layout').length;
  if (contentCount > 15) {
    score.value -= 10;
    score.findings.push({
      type: 'warn',
      rule: 'visual_clutter',
      message: `${contentCount} content elements — busy layout reduces impact`,
      action: 'Remove lowest-priority elements to improve focus'
    });
  }

  score.value = Math.max(0, score.value);
  return score;
}

// --- Main critic ---

/**
 * Run the critic on a layout sidecar.
 *
 * @param {object} layout - Parsed .layout.json content
 * @returns {object} Critic output
 */
function critique(layout) {
  const dimensions = [
    scoreGeometry(layout),
    scoreHierarchy(layout),
    scoreReadability(layout),
    scoreSpacing(layout),
    scorePersuasion(layout)
  ];

  const overallScore = Math.round(
    dimensions.reduce((sum, d) => sum + d.value, 0) / dimensions.length
  );

  const failures = [];
  const warnings = [];
  const revisionTargets = new Set();

  for (const dim of dimensions) {
    for (const f of dim.findings) {
      if (f.type === 'fail') failures.push(f);
      else if (f.type === 'warn') warnings.push(f);
      if (f.targets) f.targets.forEach(t => revisionTargets.add(t));
    }
  }

  let status;
  if (failures.length > 0) status = 'fail';
  else if (warnings.length > 0) status = 'warn';
  else status = 'pass';

  // Stop recommendation
  let stopRecommendation;
  if (overallScore >= 85) stopRecommendation = 'ship';
  else if (overallScore >= 65) stopRecommendation = 'iterate';
  else if (failures.length > 3) stopRecommendation = 'escalate';
  else stopRecommendation = 'iterate';

  return {
    version: '1.5.1',
    status,
    overallScore,
    dimensions: dimensions.map(d => ({ name: d.name, score: d.value, findingCount: d.findings.length })),
    failures,
    warnings,
    revisionTargets: [...revisionTargets],
    stopRecommendation,
    summary: buildSummary(overallScore, status, dimensions, failures, warnings)
  };
}

function buildSummary(score, status, dimensions, failures, warnings) {
  const weakest = [...dimensions].sort((a, b) => a.value - b.value)[0];
  const strongest = [...dimensions].sort((a, b) => b.value - a.value)[0];
  let summary = `Score: ${score}/100 (${status}).`;
  if (weakest && weakest.value < 70) summary += ` Weakest: ${weakest.name} (${weakest.value}).`;
  if (strongest) summary += ` Strongest: ${strongest.name} (${strongest.value}).`;
  if (failures.length) summary += ` ${failures.length} hard failure(s).`;
  if (warnings.length) summary += ` ${warnings.length} warning(s).`;
  return summary;
}

module.exports = { critique };
