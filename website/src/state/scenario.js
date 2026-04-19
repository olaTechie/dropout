import { create } from 'zustand';

export const useScenarioStore = create((set, get) => ({
  budget: 500_000_000,
  rule: 'top30_risk',
  sms_rrr: 0.10,
  chw_rrr: 0.20,
  interventions: { a0: true, a1: true, a2: true, a3: false, a4: false },

  setBudget: (v) => set({ budget: v }),
  setRule: (v) => set({ rule: v }),
  setSmsRrr: (v) => set({ sms_rrr: v }),
  setChwRrr: (v) => set({ chw_rrr: v }),
  toggleIntervention: (key) =>
    set((s) => ({ interventions: { ...s.interventions, [key]: !s.interventions[key] } })),
  reset: () =>
    set({
      budget: 500_000_000,
      rule: 'top30_risk',
      sms_rrr: 0.10,
      chw_rrr: 0.20,
      interventions: { a0: true, a1: true, a2: true, a3: false, a4: false },
    }),

  encodeToURL: () => {
    const { budget, rule, sms_rrr, chw_rrr, interventions } = get();
    const params = new URLSearchParams({
      budget: `${budget / 1e6}M`,
      rule,
      sms: sms_rrr.toFixed(2),
      chw: chw_rrr.toFixed(2),
      ivs: Object.keys(interventions).filter((k) => interventions[k]).join(','),
    });
    return params.toString();
  },

  decodeFromURL: (searchString) => {
    const params = new URLSearchParams(searchString);
    const updates = {};
    const b = params.get('budget');
    if (b) updates.budget = parseInt(b, 10) * 1e6;
    const rule = params.get('rule');
    if (rule) updates.rule = rule;
    const sms = params.get('sms');
    if (sms) updates.sms_rrr = parseFloat(sms);
    const chw = params.get('chw');
    if (chw) updates.chw_rrr = parseFloat(chw);
    const ivs = params.get('ivs');
    if (ivs) {
      updates.interventions = { a0: false, a1: false, a2: false, a3: false, a4: false };
      ivs.split(',').forEach((k) => { updates.interventions[k] = true; });
    }
    set(updates);
  },
}));
