'use strict';

/**
 * Canonical rectangle model for StrikeFrame geometry system.
 *
 * Every visual element exposes its position and size through this model.
 * All coordinates are in canvas pixels, origin top-left.
 */

const ANCHORS = [
  'top-left', 'top-center', 'top-right',
  'center-left', 'center', 'center-right',
  'bottom-left', 'bottom-center', 'bottom-right'
];

/**
 * Create a rect from x, y, width, height.
 * Returns a frozen object with derived edge/center/area values.
 */
function create(x, y, width, height) {
  const left = x;
  const top = y;
  const right = x + width;
  const bottom = y + height;
  return Object.freeze({
    x, y, width, height,
    left, top, right, bottom,
    centerX: x + width / 2,
    centerY: y + height / 2,
    area: width * height
  });
}

/** Create a rect from edge coordinates. */
function fromBounds(left, top, right, bottom) {
  return create(left, top, right - left, bottom - top);
}

/** Create a rect from a plain object with x/y/width/height or left/top/right/bottom. */
function fromObject(obj) {
  if (obj.width != null && obj.height != null) {
    return create(obj.x || obj.left || 0, obj.y || obj.top || 0, obj.width, obj.height);
  }
  if (obj.right != null && obj.bottom != null) {
    return fromBounds(obj.left || 0, obj.top || 0, obj.right, obj.bottom);
  }
  return create(0, 0, 0, 0);
}

/** True if any part of a and b overlap. */
function overlaps(a, b) {
  return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
}

/** Return the intersection rect, or null if no overlap. */
function intersection(a, b) {
  if (!overlaps(a, b)) return null;
  const left = Math.max(a.left, b.left);
  const top = Math.max(a.top, b.top);
  const right = Math.min(a.right, b.right);
  const bottom = Math.min(a.bottom, b.bottom);
  return create(left, top, right - left, bottom - top);
}

/** True if outer fully contains inner. */
function contains(outer, inner) {
  return inner.left >= outer.left && inner.right <= outer.right &&
         inner.top >= outer.top && inner.bottom <= outer.bottom;
}

/**
 * True if inner is inside outer with at least `margin` px on every side.
 * This is `contains` with inset — used for safe-zone checks.
 */
function containsWithMargin(outer, inner, margin) {
  return inner.left >= outer.left + margin &&
         inner.right <= outer.right - margin &&
         inner.top >= outer.top + margin &&
         inner.bottom <= outer.bottom - margin;
}

/**
 * Directional gaps between two rects.
 * Positive = separated, negative = overlapping on that axis.
 * Returns { top, right, bottom, left } where:
 *   top = how far a.top is below b.bottom (gap above a from b)
 *   bottom = how far a.bottom is above b.top (gap below a to b)
 *   left = how far a.left is right of b.right
 *   right = how far a.right is left of b.left
 */
function gaps(a, b) {
  return {
    top: a.top - b.bottom,
    bottom: b.top - a.bottom,
    left: a.left - b.right,
    right: b.left - a.right
  };
}

/**
 * Vertical gap between two rects (assumes a is above b).
 * Positive = space between, negative = overlap.
 */
function verticalGap(above, below) {
  return below.top - above.bottom;
}

/**
 * Horizontal gap between two rects (assumes a is left of b).
 * Positive = space between, negative = overlap.
 */
function horizontalGap(leftRect, rightRect) {
  return rightRect.left - leftRect.right;
}

/**
 * Nearest-edge distance between two rects.
 * Returns 0 if overlapping, positive otherwise.
 */
function distance(a, b) {
  const dx = Math.max(0, a.left - b.right, b.left - a.right);
  const dy = Math.max(0, a.top - b.bottom, b.top - a.bottom);
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Resolve a named anchor point on a rect.
 * Returns { x, y } for the anchor position.
 */
function anchor(rect, anchorName) {
  const parts = anchorName.split('-');
  let x, y;
  if (parts.length === 1 && parts[0] === 'center') {
    return { x: rect.centerX, y: rect.centerY };
  }
  const vPart = parts[0];
  const hPart = parts[1] || 'center';
  switch (vPart) {
    case 'top': y = rect.top; break;
    case 'center': y = rect.centerY; break;
    case 'bottom': y = rect.bottom; break;
    default: y = rect.top;
  }
  switch (hPart) {
    case 'left': x = rect.left; break;
    case 'center': x = rect.centerX; break;
    case 'right': x = rect.right; break;
    default: x = rect.left;
  }
  return { x, y };
}

/** Expand a rect by `amount` pixels on all sides. */
function expand(rect, amount) {
  return create(
    rect.x - amount, rect.y - amount,
    rect.width + amount * 2, rect.height + amount * 2
  );
}

/** Contract a rect by `amount` pixels on all sides. */
function contract(rect, amount) {
  return expand(rect, -amount);
}

/** Expand with different amounts per side: { top, right, bottom, left }. */
function expandSides(rect, sides) {
  const t = sides.top || 0;
  const r = sides.right || 0;
  const b = sides.bottom || 0;
  const l = sides.left || 0;
  return create(rect.x - l, rect.y - t, rect.width + l + r, rect.height + t + b);
}

/** Ratio of inner area to outer area (0..1). */
function occupancy(inner, outer) {
  if (outer.area === 0) return 0;
  return inner.area / outer.area;
}

/** Ratio of occupied area (actual overlap) to outer area (0..1). */
function coverageRatio(inner, outer) {
  const inter = intersection(inner, outer);
  if (!inter || outer.area === 0) return 0;
  return inter.area / outer.area;
}

/**
 * Check all element rects for pairwise overlaps.
 * Returns array of { a, b, intersection } for each collision.
 */
function findCollisions(elements) {
  const collisions = [];
  for (let i = 0; i < elements.length; i++) {
    for (let j = i + 1; j < elements.length; j++) {
      const a = elements[i];
      const b = elements[j];
      const inter = intersection(a.rect, b.rect);
      if (inter && inter.area > 0) {
        collisions.push({ a: a.id, b: b.id, intersection: inter });
      }
    }
  }
  return collisions;
}

/**
 * Check which elements violate a safe zone (are not fully inside it).
 * Returns array of { id, violation } where violation describes what's outside.
 */
function findSafeZoneViolations(elements, safeZone) {
  const violations = [];
  for (const el of elements) {
    if (!contains(safeZone, el.rect)) {
      const overLeft = Math.max(0, safeZone.left - el.rect.left);
      const overTop = Math.max(0, safeZone.top - el.rect.top);
      const overRight = Math.max(0, el.rect.right - safeZone.right);
      const overBottom = Math.max(0, el.rect.bottom - safeZone.bottom);
      violations.push({
        id: el.id,
        violation: { overLeft, overTop, overRight, overBottom },
        severity: Math.max(overLeft, overTop, overRight, overBottom)
      });
    }
  }
  return violations;
}

/**
 * Compute occupancy metrics for all elements within a canvas.
 * Returns { totalOccupied, canvasArea, occupancyRatio, boundingBox }.
 */
function computeOccupancy(elements, canvas) {
  if (elements.length === 0) {
    return { totalOccupied: 0, canvasArea: canvas.area, occupancyRatio: 0, boundingBox: null };
  }
  let minLeft = Infinity, minTop = Infinity, maxRight = -Infinity, maxBottom = -Infinity;
  let totalArea = 0;
  for (const el of elements) {
    const r = el.rect;
    if (r.left < minLeft) minLeft = r.left;
    if (r.top < minTop) minTop = r.top;
    if (r.right > maxRight) maxRight = r.right;
    if (r.bottom > maxBottom) maxBottom = r.bottom;
    totalArea += r.area;
  }
  const boundingBox = fromBounds(minLeft, minTop, maxRight, maxBottom);
  return {
    totalOccupied: totalArea,
    canvasArea: canvas.area,
    occupancyRatio: canvas.area > 0 ? totalArea / canvas.area : 0,
    boundingBox,
    boundingBoxRatio: canvas.area > 0 ? boundingBox.area / canvas.area : 0
  };
}

module.exports = {
  ANCHORS,
  create,
  fromBounds,
  fromObject,
  overlaps,
  intersection,
  contains,
  containsWithMargin,
  gaps,
  verticalGap,
  horizontalGap,
  distance,
  anchor,
  expand,
  contract,
  expandSides,
  occupancy,
  coverageRatio,
  findCollisions,
  findSafeZoneViolations,
  computeOccupancy
};
