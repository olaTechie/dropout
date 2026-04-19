import { useScenarioStore } from '../../state/scenario.js';
import BudgetSlider from './BudgetSlider.jsx';

export default function SimulationControls({ cameraMode, setCameraMode, scale, setScale }) {
  const { interventions, toggleIntervention, rule, setRule } = useScenarioStore();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-80 z-20 bg-abyss/80 backdrop-blur-lg border-r border-white/10 p-6 overflow-y-auto">
      <h2 className="font-serif text-2xl mb-6">Simulation</h2>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Camera</legend>
        <div className="flex gap-2">
          {['orbit', 'flythrough', 'top'].map((m) => (
            <button key={m} onClick={() => setCameraMode(m)} className={`px-3 py-1 text-xs rounded-full border ${cameraMode === m ? 'border-saffron text-saffron' : 'border-white/10 text-muted'}`}>
              {m}
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Scale</legend>
        <select value={scale} onChange={(e) => setScale(e.target.value)} className="w-full bg-dusk border border-white/10 rounded-xl p-2">
          <option value="family">Family (1)</option>
          <option value="community">Community (100)</option>
          <option value="state">State (10k)</option>
          <option value="nation">Nation (3M particles)</option>
        </select>
      </fieldset>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Interventions</legend>
        <div className="space-y-2">
          {['a1', 'a2', 'a3', 'a4'].map((k) => (
            <label key={k} className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={interventions[k]} onChange={() => toggleIntervention(k)} className="accent-saffron" />
              <span>{{ a1: 'SMS', a2: 'CHW', a3: 'Recall', a4: 'Incentive' }[k]}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset className="mb-6">
        <legend className="text-xs uppercase tracking-wider text-muted mb-2">Targeting rule</legend>
        <select value={rule} onChange={(e) => setRule(e.target.value)} className="w-full bg-dusk border border-white/10 rounded-xl p-2">
          <option value="uniform_sms">Uniform SMS</option>
          <option value="uniform_chw">Uniform CHW</option>
          <option value="top30_risk">Top-30% risk</option>
          <option value="top10_incentive">Top-10% + incentive</option>
          <option value="rl_optimised">RL-optimised</option>
        </select>
      </fieldset>

      <div className="mb-6"><BudgetSlider /></div>

      <button
        onClick={() => {
          const { encodeToURL } = useScenarioStore.getState();
          const url = `${window.location.origin}${window.location.pathname}?${encodeToURL()}`;
          navigator.clipboard.writeText(url);
        }}
        className="w-full py-2 border border-white/10 rounded-xl text-sm hover:border-saffron/40"
      >
        Copy snapshot URL
      </button>
    </aside>
  );
}
