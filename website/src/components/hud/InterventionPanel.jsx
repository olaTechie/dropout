import { useScenarioStore } from '../../state/scenario.js';

// Static class strings — Tailwind v4 JIT only emits classes it can see verbatim
// in source, so dynamic `border-${color}` interpolation does NOT work.
const INTERVENTIONS = [
  {
    key: 'a1', label: 'SMS reminder', cost: 50,
    activeClass: 'border-saffron bg-saffron/10',
  },
  {
    key: 'a2', label: 'CHW visit', cost: 500,
    activeClass: 'border-verdigris bg-verdigris/10',
  },
  {
    key: 'a3', label: 'Facility recall', cost: 1500,
    activeClass: 'border-iris bg-iris/10',
  },
  {
    key: 'a4', label: 'Incentive', cost: 800,
    activeClass: 'border-terracotta bg-terracotta/10',
  },
];

export default function InterventionPanel() {
  const interventions = useScenarioStore((s) => s.interventions);
  const toggle = useScenarioStore((s) => s.toggleIntervention);

  return (
    <div className="fixed left-6 top-1/2 -translate-y-1/2 z-20 rounded-2xl border border-white/10 bg-abyss/70 backdrop-blur-md p-4 w-64">
      <h3 className="font-serif text-lg mb-3">Interventions</h3>
      <ul className="space-y-2">
        {INTERVENTIONS.map((iv) => {
          const active = interventions[iv.key];
          return (
            <li key={iv.key}>
              <button
                type="button"
                aria-pressed={active}
                onClick={() => toggle(iv.key)}
                className={`w-full text-left rounded-xl border p-3 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-saffron/60 ${
                  active ? iv.activeClass : 'border-white/10 bg-dusk/30 hover:border-white/30'
                }`}
              >
                <div className="flex items-baseline justify-between">
                  <span className="text-sm">{iv.label}</span>
                  <span className="text-xs font-mono text-muted">₦{iv.cost}</span>
                </div>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
