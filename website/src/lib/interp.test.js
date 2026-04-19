import { describe, it, expect } from 'vitest';
import { buildCubeIndex, interpolateScenario } from './interp.js';

const fixture = {
  grid: {
    budgets: [250_000_000, 500_000_000],
    rules: ['uniform_sms', 'top30_risk'],
    sms_rrr: [0.05, 0.15],
    chw_rrr: [0.15, 0.25],
  },
  points: [
    // uniform_sms corners
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15, dtp3_mean: 0.80, cost_per_child: 100 },
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.25, dtp3_mean: 0.81, cost_per_child: 100 },
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.15, dtp3_mean: 0.84, cost_per_child: 100 },
    { budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.25, dtp3_mean: 0.85, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15, dtp3_mean: 0.82, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.25, dtp3_mean: 0.83, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.15, dtp3_mean: 0.86, cost_per_child: 100 },
    { budget: 500_000_000, rule: 'uniform_sms', sms_rrr: 0.15, chw_rrr: 0.25, dtp3_mean: 0.87, cost_per_child: 100 },
  ],
};

describe('interp', () => {
  const cube = buildCubeIndex(fixture);

  it('exact grid point returns stored value', () => {
    const r = interpolateScenario(cube, {
      budget: 250_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15,
    });
    expect(r.dtp3_mean).toBeCloseTo(0.80, 4);
  });

  it('midpoint interpolates linearly', () => {
    const r = interpolateScenario(cube, {
      budget: 375_000_000, rule: 'uniform_sms', sms_rrr: 0.10, chw_rrr: 0.20,
    });
    // Mean of 8 corners: (0.80+0.81+0.84+0.85+0.82+0.83+0.86+0.87) / 8 = 0.835
    expect(r.dtp3_mean).toBeCloseTo(0.835, 3);
  });

  it('clamps out-of-range budget to nearest edge', () => {
    const r = interpolateScenario(cube, {
      budget: 100_000_000, rule: 'uniform_sms', sms_rrr: 0.05, chw_rrr: 0.15,
    });
    expect(r.dtp3_mean).toBeCloseTo(0.80, 4);
  });

  it('throws for unknown rule', () => {
    expect(() =>
      interpolateScenario(cube, {
        budget: 250_000_000, rule: 'unknown', sms_rrr: 0.05, chw_rrr: 0.15,
      })
    ).toThrow(/unknown/i);
  });
});
