import { useEffect, useState } from 'react';
import ScenarioTable from '../components/charts/ScenarioTable.jsx';
import BudgetSlider from '../components/hud/BudgetSlider.jsx';
import MetricCard from '../components/shared/MetricCard.jsx';
import { loadData } from '../lib/dataLoader.js';
import { buildCubeIndex, interpolateScenario } from '../lib/interp.js';
import { useScenarioStore } from '../state/scenario.js';
import { formatNaira, formatPct } from '../lib/format.js';

export default function Policy() {
  const [cube, setCube] = useState(null);
  const { budget, rule, sms_rrr, chw_rrr } = useScenarioStore();

  useEffect(() => {
    loadData('scenario_cube').then((raw) => setCube(buildCubeIndex(raw)));
  }, []);

  const live = cube ? interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr }) : null;

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <header className="mb-12">
        <h1 className="font-serif text-5xl">Policy Dashboard</h1>
        <p className="mt-3 text-muted max-w-2xl">
          Compare intervention scenarios for reducing DTP1-to-DTP3 dropout in Nigeria.
          Adjust the budget below to see how outcomes and costs shift.
        </p>
      </header>

      <section className="grid md:grid-cols-3 gap-6 mb-12">
        <MetricCard
          label="Live DTP3 completion"
          value={live ? formatPct(live.dtp3_mean, 1) : '—'}
          sublabel={live ? `CI ${formatPct(live.dtp3_ci_low, 1)}–${formatPct(live.dtp3_ci_high, 1)}` : ''}
          tone="positive"
        />
        <MetricCard
          label="Cost per child"
          value={live ? formatNaira(live.cost_per_child) : '—'}
          sublabel={`Rule: ${rule}`}
        />
        <MetricCard
          label="Concentration index"
          value={live ? live.concentration_index.toFixed(3) : '—'}
          sublabel="Wealth-related inequality"
          tone={live && live.concentration_index < 0.02 ? 'positive' : 'warning'}
        />
      </section>

      <section className="rounded-2xl border border-white/10 bg-dusk/30 p-8 mb-12">
        <h2 className="font-serif text-2xl mb-6">Adjust the budget</h2>
        <BudgetSlider />
      </section>

      <section>
        <h2 className="font-serif text-2xl mb-6">Primary scenarios</h2>
        <ScenarioTable />
      </section>
    </main>
  );
}
