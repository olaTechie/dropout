import { useScenarioStore } from '../../state/scenario.js';

const INTERVENTIONS = [
  { key: 'a1', label: 'SMS reminder', cost: 50, color: 'saffron' },
  { key: 'a2', label: 'CHW visit', cost: 500, color: 'verdigris' },
  { key: 'a3', label: 'Facility recall', cost: 1500, color: 'iris' },
  { key: 'a4', label: 'Incentive', cost: 800, color: 'terracotta' },
];

export default function InterventionPanel() {
  const interventions = useScenarioStore((s) => s.interventions);
  const toggle = useScenarioStore((s) => s.toggleIntervention);

  return (
    <div className="fixed left-6 top-1/2 -translate-y-1/2 z-20 rounded-2xl border border-white/10 bg-abyss/70 backdrop-blur-md p-4 w-64">
      <h3 className="font-serif text-lg mb-3">Interventions</h3>
      <ul className="space-y-2">
        {INTERVENTIONS.map((iv) => (
          <li key={iv.key}>
            <button
              onClick={() => toggle(iv.key)}
              className={`w-full text-left rounded-xl border p-3 transition ${
                interventions[iv.key]
                  ? `border-${iv.color} bg-${iv.color}/10`
                  : 'border-white/10 bg-dusk/30 hover:border-white/30'
              }`}
            >
              <div className="flex items-baseline justify-between">
                <span className="text-sm">{iv.label}</span>
                <span className="text-xs font-mono text-muted">₦{iv.cost}</span>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
