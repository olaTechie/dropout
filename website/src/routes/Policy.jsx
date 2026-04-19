import { useEffect, useState } from 'react';
import ScenarioTable from '../components/charts/ScenarioTable.jsx';
import BudgetSlider from '../components/hud/BudgetSlider.jsx';
import MetricCard from '../components/shared/MetricCard.jsx';
import { loadData, loadFallbackScenario } from '../lib/dataLoader.js';
import { buildCubeIndex, interpolateScenario } from '../lib/interp.js';
import { useScenarioStore } from '../state/scenario.js';
import { formatNaira, formatPct } from '../lib/format.js';

// Three loading states: 'loading' (cube fetch in flight), 'cube' (live
// interpolation available), 'fallback' (cube failed, using closest discrete
// scenario from scenarios.json), 'error' (both failed).
export default function Policy() {
  const [cube, setCube] = useState(null);
  const [status, setStatus] = useState('loading');
  const [fallbackLive, setFallbackLive] = useState(null);
  const { budget, rule, sms_rrr, chw_rrr } = useScenarioStore();

  useEffect(() => {
    let cancelled = false;
    loadData('scenario_cube')
      .then((raw) => {
        if (cancelled) return;
        setCube(buildCubeIndex(raw));
        setStatus('cube');
      })
      .catch(async () => {
        if (cancelled) return;
        const fb = await loadFallbackScenario(rule);
        if (cancelled) return;
        if (fb) {
          setFallbackLive(fb);
          setStatus('fallback');
        } else {
          setStatus('error');
        }
      });
    return () => { cancelled = true; };
  }, [rule]);

  const live = status === 'cube' && cube
    ? interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr })
    : fallbackLive;

  return (
    <main className="max-w-7xl mx-auto px-6 py-12">
      <header className="mb-12">
        <h1 className="font-serif text-5xl">Policy Dashboard</h1>
        <p className="mt-3 text-muted max-w-2xl">
          Compare intervention scenarios for reducing DTP1-to-DTP3 dropout in Nigeria.
          Adjust the budget below to see how outcomes and costs shift.
        </p>
      </header>

      {status === 'loading' && (
        <p role="status" aria-live="polite" className="mb-6 text-sm text-muted">
          Loading scenario cube…
        </p>
      )}
      {status === 'fallback' && (
        <div role="status" aria-live="polite" className="mb-6 rounded-xl border border-saffron/40 bg-saffron/5 p-4 text-sm">
          Live interpolation is unavailable (scenario cube failed to load).
          Showing the closest discrete scenario instead — the budget slider has
          no effect in this fallback view. Try refreshing the page to retry.
        </div>
      )}
      {status === 'error' && (
        <div role="alert" className="mb-6 rounded-xl border border-terracotta/50 bg-terracotta/5 p-4 text-sm">
          Could not load scenario data. Headline metrics are unavailable.
          Refresh to retry, or open the Explorer for the underlying CSVs.
        </div>
      )}

      <section className="grid md:grid-cols-3 gap-6 mb-12">
        <MetricCard
          label="Live DTP3 completion"
          value={live ? formatPct(live.dtp3_mean, 1) : '—'}
          sublabel={live && live.dtp3_ci_low != null
            ? `CI ${formatPct(live.dtp3_ci_low, 1)}–${formatPct(live.dtp3_ci_high, 1)}`
            : ''}
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
