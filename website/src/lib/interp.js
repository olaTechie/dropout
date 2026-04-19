/**
 * Build an index keyed by rule, then a 3D grid over (budget, sms_rrr, chw_rrr).
 */
export function buildCubeIndex(cube) {
  const { grid, points } = cube;
  const byRule = {};
  for (const rule of grid.rules) {
    byRule[rule] = {};
    for (const b of grid.budgets) {
      byRule[rule][b] = {};
      for (const s of grid.sms_rrr) {
        byRule[rule][b][s] = {};
        for (const c of grid.chw_rrr) {
          byRule[rule][b][s][c] = null;
        }
      }
    }
  }
  for (const p of points) {
    if (byRule[p.rule]?.[p.budget]?.[p.sms_rrr]?.[p.chw_rrr] !== undefined) {
      byRule[p.rule][p.budget][p.sms_rrr][p.chw_rrr] = p;
    }
  }
  return { grid, byRule };
}

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function findBracket(sorted, v) {
  const clamped = clamp(v, sorted[0], sorted[sorted.length - 1]);
  for (let i = 0; i < sorted.length - 1; i++) {
    if (clamped >= sorted[i] && clamped <= sorted[i + 1]) {
      const t = (clamped - sorted[i]) / (sorted[i + 1] - sorted[i]);
      return [sorted[i], sorted[i + 1], t];
    }
  }
  return [sorted[0], sorted[0], 0];
}

const FIELDS = [
  'dtp3_mean', 'dtp3_ci_low', 'dtp3_ci_high',
  'cost_per_child', 'concentration_index', 'wealth_gap',
];

/**
 * Trilinear interpolation over (budget, sms_rrr, chw_rrr) within a targeting rule.
 */
export function interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr }) {
  const { grid, byRule } = cube;
  if (!byRule[rule]) {
    throw new Error(`Unknown targeting rule: ${rule}`);
  }

  const [b0, b1, tb] = findBracket(grid.budgets, budget);
  const [s0, s1, ts] = findBracket(grid.sms_rrr, sms_rrr);
  const [c0, c1, tc] = findBracket(grid.chw_rrr, chw_rrr);

  const corners = [];
  for (const b of [b0, b1]) {
    for (const s of [s0, s1]) {
      for (const c of [c0, c1]) {
        const p = byRule[rule][b]?.[s]?.[c];
        if (!p) throw new Error(`Missing grid point: ${rule} b=${b} s=${s} c=${c}`);
        corners.push(p);
      }
    }
  }

  // Corner order: (b0,s0,c0)(b0,s0,c1)(b0,s1,c0)(b0,s1,c1)(b1,s0,c0)(b1,s0,c1)(b1,s1,c0)(b1,s1,c1)
  const lerp = (a, b, t) => a * (1 - t) + b * t;

  const out = {};
  for (const field of FIELDS) {
    const v = corners.map((p) => p[field] ?? 0);
    const cxy00 = lerp(v[0], v[4], tb);
    const cxy01 = lerp(v[1], v[5], tb);
    const cxy10 = lerp(v[2], v[6], tb);
    const cxy11 = lerp(v[3], v[7], tb);
    const cy0 = lerp(cxy00, cxy10, ts);
    const cy1 = lerp(cxy01, cxy11, ts);
    out[field] = lerp(cy0, cy1, tc);
  }
  out.budget = budget;
  out.rule = rule;
  out.sms_rrr = sms_rrr;
  out.chw_rrr = chw_rrr;
  return out;
}
