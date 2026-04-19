import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import ScenarioTable from '../components/charts/ScenarioTable.jsx';
import BudgetSlider from '../components/hud/BudgetSlider.jsx';
import MetricCard from '../components/shared/MetricCard.jsx';
import { loadData, loadFallbackScenario } from '../lib/dataLoader.js';
import { buildCubeIndex, interpolateScenario } from '../lib/interp.js';
import { useScenarioStore } from '../state/scenario.js';
import { formatNaira, formatPct } from '../lib/format.js';

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
    <main className="min-h-screen">
      <section className="max-w-7xl mx-auto px-6 py-12">
        <header className="mb-10 grid gap-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)] lg:items-end">
          <div>
            <div className="inline-flex items-center rounded-full border border-saffron/30 bg-saffron/10 px-4 py-1 text-xs uppercase tracking-[0.25em] text-saffron">
              Policy dashboard
            </div>
            <h1 className="mt-5 max-w-4xl font-serif text-5xl md:text-7xl leading-tight">
              Compare what different intervention rules buy you.
            </h1>
            <p className="mt-5 max-w-3xl text-lg text-moonlight/78">
              Shift budget and targeting assumptions, then inspect completion, cost,
              and equity together instead of reading each result in isolation.
            </p>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/6 p-6 backdrop-blur-md">
            <div className="text-xs uppercase tracking-[0.22em] text-muted">Current decision frame</div>
            <div className="mt-4 font-serif text-3xl">{rule}</div>
            <p className="mt-3 text-sm text-muted">
              Pair this page with the redesigned simulator for scenario snapshots,
              or open the Explorer for the underlying research outputs.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link to="/simulation" className="rounded-full bg-saffron px-5 py-2 text-sm font-semibold text-abyss hover:bg-saffron/90">
                Open simulator
              </Link>
              <Link to="/explorer" className="rounded-full border border-white/15 px-5 py-2 text-sm hover:bg-white/5">
                Open explorer
              </Link>
            </div>
          </div>
        </header>

        {status === 'loading' && (
          <p role="status" aria-live="polite" className="mb-6 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-sm text-muted">
            Loading scenario cube…
          </p>
        )}
        {status === 'fallback' && (
          <div role="status" aria-live="polite" className="mb-6 rounded-2xl border border-saffron/40 bg-saffron/8 p-4 text-sm">
            Live interpolation is unavailable. Showing the closest discrete scenario instead, so the budget slider is illustrative only in this state.
          </div>
        )}
        {status === 'error' && (
          <div role="alert" className="mb-6 rounded-2xl border border-terracotta/50 bg-terracotta/8 p-4 text-sm">
            Could not load scenario data. Headline metrics are unavailable. Open the Explorer for the underlying outputs while the bundle is restored.
          </div>
        )}

        <section className="grid gap-4 md:grid-cols-3 mb-10">
          <MetricCard
            label="Live DTP3 completion"
            value={live ? formatPct(live.dtp3_mean, 1) : '—'}
            sublabel={live && live.dtp3_ci_low != null
              ? `CI ${formatPct(live.dtp3_ci_low, 1)}–${formatPct(live.dtp3_ci_high, 1)}`
              : 'Awaiting scenario data'}
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

        <section className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_360px]">
          <div className="rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04))] p-6 md:p-8 shadow-[0_28px_90px_rgba(0,0,0,0.22)]">
            <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <div className="text-xs uppercase tracking-[0.22em] text-muted">Scenario library</div>
                <h2 className="mt-2 font-serif text-3xl">Primary intervention scenarios</h2>
              </div>
              <p className="max-w-xl text-sm text-muted">
                Use the table as the evidence backbone, then treat the cards above as the live summary of the currently selected rule and budget.
              </p>
            </div>
            <ScenarioTable />
          </div>

          <div className="space-y-6">
            <section className="rounded-[2rem] border border-white/10 bg-night/80 p-6 backdrop-blur-md shadow-[0_24px_80px_rgba(0,0,0,0.2)]">
              <div className="text-xs uppercase tracking-[0.22em] text-muted">Budget control</div>
              <h2 className="mt-2 font-serif text-3xl">Adjust the spend envelope</h2>
              <p className="mt-3 text-sm text-muted">
                Tune the working budget here and watch the live metrics respond when the interpolation cube is available.
              </p>
              <div className="mt-6">
                <BudgetSlider />
              </div>
            </section>

            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-1">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
                <div className="text-xs uppercase tracking-[0.2em] text-muted">What this page does well</div>
                <p className="mt-4 text-sm text-muted">
                  It compresses cost, effect, and equity into one decision surface, which is what the manuscript outputs need in product form.
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
                <div className="text-xs uppercase tracking-[0.2em] text-muted">Best next click</div>
                <p className="mt-4 text-sm text-muted">
                  Move to the simulator when you want a presentable scenario walkthrough, or the Explorer when you want the raw research artefacts.
                </p>
              </div>
            </section>
          </div>
        </section>
      </section>
    </main>
  );
}
