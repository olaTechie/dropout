import { describe, it, expect, beforeEach } from 'vitest';
import { useScenarioStore } from './scenario.js';

describe('scenario store', () => {
  beforeEach(() => {
    useScenarioStore.setState({
      budget: 500_000_000,
      rule: 'top30_risk',
      sms_rrr: 0.10,
      chw_rrr: 0.20,
      interventions: { a0: true, a1: true, a2: true, a3: false, a4: false },
    });
  });

  it('has sensible defaults', () => {
    const s = useScenarioStore.getState();
    expect(s.budget).toBe(500_000_000);
    expect(s.rule).toBe('top30_risk');
  });

  it('setBudget updates budget', () => {
    useScenarioStore.getState().setBudget(750_000_000);
    expect(useScenarioStore.getState().budget).toBe(750_000_000);
  });

  it('toggleIntervention flips boolean', () => {
    useScenarioStore.getState().toggleIntervention('a3');
    expect(useScenarioStore.getState().interventions.a3).toBe(true);
    useScenarioStore.getState().toggleIntervention('a3');
    expect(useScenarioStore.getState().interventions.a3).toBe(false);
  });

  it('encodeToURL serializes state', () => {
    const s = useScenarioStore.getState();
    const url = s.encodeToURL();
    expect(url).toContain('budget=500');
    expect(url).toContain('rule=top30_risk');
  });
});
