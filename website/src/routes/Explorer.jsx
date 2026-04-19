import { Link } from 'react-router-dom';
import { useEffect, useMemo, useState } from 'react';
import TabNav from '../components/explorer/TabNav.jsx';
import Cascade from '../components/explorer/tabs/Cascade.jsx';
import PredictionModels from '../components/explorer/tabs/PredictionModels.jsx';
import Shap from '../components/explorer/tabs/Shap.jsx';
import RL from '../components/explorer/tabs/RL.jsx';
import Microsim from '../components/explorer/tabs/Microsim.jsx';
import Equity from '../components/explorer/tabs/Equity.jsx';
import Validation from '../components/explorer/tabs/Validation.jsx';
import Downloads from '../components/explorer/tabs/Downloads.jsx';
import MetricCard from '../components/shared/MetricCard.jsx';
import { loadData } from '../lib/dataLoader.js';
import { formatNaira, formatPct } from '../lib/format.js';

const TAB_MAP = {
  cascade: Cascade,
  models: PredictionModels,
  shap: Shap,
  rl: RL,
  microsim: Microsim,
  equity: Equity,
  validation: Validation,
  downloads: Downloads,
};

const TAB_COPY = {
  cascade: {
    eyebrow: 'Stage 0',
    title: 'Where the cascade fractures',
    body: 'Zone-level retention shows that the problem is systemic but not uniform. This is the entry point for the whole analytical story.',
  },
  models: {
    eyebrow: 'Stage 1',
    title: 'Which children are most at risk',
    body: 'Transition-specific prediction models surface where dropout risk concentrates and how reliable that ranking is.',
  },
  shap: {
    eyebrow: 'Stage 1',
    title: 'Why the models behave that way',
    body: 'Andersen-domain SHAP summaries make the risk story legible rather than leaving it trapped inside model coefficients.',
  },
  rl: {
    eyebrow: 'Stage 2',
    title: 'How policy selection was learned',
    body: 'Offline RL was used to compare intervention policies under observed trajectories without unsafe live experimentation.',
  },
  microsim: {
    eyebrow: 'Stage 3',
    title: 'What scenario wins under uncertainty',
    body: 'Bootstrapped microsimulation translates intervention logic into coverage, cost, and equity outcomes.',
  },
  equity: {
    eyebrow: 'Cross-cutting',
    title: 'Whether gains are shared fairly',
    body: 'Equity indicators test whether better average performance still leaves the poorest children behind.',
  },
  validation: {
    eyebrow: 'Cross-cutting',
    title: 'Where caution is still needed',
    body: 'Validation highlights the calibration gap and the subgroups where interpretation should stay comparative rather than absolute.',
  },
  downloads: {
    eyebrow: 'Open science',
    title: 'Take the artefacts with you',
    body: 'All public JSON artefacts used by the site are downloadable directly from the Explorer.',
  },
};

const PIPELINE = [
  { id: 'cascade', stage: 'Stage 0', title: 'Descriptive cascade', metricLabel: 'Worst zone dropout' },
  { id: 'models', stage: 'Stage 1', title: 'Risk prediction', metricLabel: 'Best AUC-ROC' },
  { id: 'rl', stage: 'Stage 2', title: 'Offline policy learning', metricLabel: 'Policy winner' },
  { id: 'microsim', stage: 'Stage 3', title: 'Microsimulation', metricLabel: 'Best scenario' },
];

export default function Explorer() {
  const [active, setActive] = useState('cascade');
  const [cascadeRows, setCascadeRows] = useState([]);
  const [shapData, setShapData] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [validation, setValidation] = useState(null);
  const Active = TAB_MAP[active];

  useEffect(() => {
    loadData('cascade').then(setCascadeRows);
    loadData('shap_summary').then(setShapData);
    loadData('scenarios').then(setScenarios);
    loadData('validation').then(setValidation);
  }, []);

  const headline = useMemo(() => {
    const highestDropout = cascadeRows.length
      ? [...cascadeRows].sort((a, b) => b.who_dropout - a.who_dropout)[0]
      : null;
    const bestScenario = scenarios.length
      ? [...scenarios].sort((a, b) => (b.dtp3_mean - b.cost_per_child_mean / 100000) - (a.dtp3_mean - a.cost_per_child_mean / 100000))[0]
      : null;
    const bestAuc = shapData
      ? Math.max(
        shapData.t1?.metrics?.auc_roc || 0,
        shapData.t2?.metrics?.auc_roc || 0
      )
      : null;
    const flaggedStrata = validation
      ? Object.values(validation.subgroups || {}).reduce((sum, rows) => sum + rows.filter((row) => row.flagged).length, 0)
      : null;

    return { highestDropout, bestScenario, bestAuc, flaggedStrata };
  }, [cascadeRows, scenarios, shapData, validation]);

  const pipelineMetrics = useMemo(() => {
    const highestDropout = headline.highestDropout
      ? `${headline.highestDropout.zone} · ${formatPct(headline.highestDropout.who_dropout / 100, 1)}`
      : '—';
    const bestAuc = headline.bestAuc ? headline.bestAuc.toFixed(3) : '—';
    const bestScenario = headline.bestScenario
      ? headline.bestScenario.id.replace(/^S\d+:\s*/, '')
      : '—';

    return {
      cascade: highestDropout,
      models: bestAuc,
      rl: 'IQL selected',
      microsim: bestScenario,
    };
  }, [headline]);

  return (
    <main className="min-h-screen">
      <section className="max-w-7xl mx-auto px-6 py-12">
        <header className="mb-10 grid gap-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)] lg:items-end">
          <div>
            <div className="inline-flex items-center rounded-full border border-verdigris/30 bg-verdigris/10 px-4 py-1 text-xs uppercase tracking-[0.25em] text-verdigris">
              Research explorer
            </div>
            <h1 className="mt-5 max-w-5xl font-serif text-5xl md:text-7xl leading-tight">
              Follow the full analysis pipeline, then drop into the evidence layer you need.
            </h1>
            <p className="mt-5 max-w-3xl text-lg text-moonlight/78">
              This is now an overview-first explorer: headline findings up front,
              drill-down tabs beneath, and direct links back to the dashboard and
              simulation when you want to move from evidence to decisions.
            </p>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/6 p-6 backdrop-blur-md">
            <div className="text-xs uppercase tracking-[0.22em] text-muted">Current panel</div>
            <div className="mt-4 font-serif text-3xl">{TAB_COPY[active].title}</div>
            <p className="mt-3 text-sm text-muted">
              {TAB_COPY[active].body}
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link to="/policy" className="rounded-full border border-white/15 px-5 py-2 text-sm hover:bg-white/5">
                Open dashboard
              </Link>
              <Link to="/simulation" className="rounded-full bg-saffron px-5 py-2 text-sm font-semibold text-abyss hover:bg-saffron/90">
                Open simulator
              </Link>
            </div>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4 mb-10">
          <MetricCard
            label="Highest zone dropout"
            value={headline.highestDropout ? formatPct(headline.highestDropout.who_dropout / 100, 1) : '—'}
            sublabel={headline.highestDropout ? headline.highestDropout.zone : 'Loading cascade data'}
            tone="warning"
          />
          <MetricCard
            label="Best model AUC-ROC"
            value={headline.bestAuc ? headline.bestAuc.toFixed(3) : '—'}
            sublabel="Transition-specific XGBoost performance"
            tone="positive"
          />
          <MetricCard
            label="Best scenario"
            value={headline.bestScenario ? formatPct(headline.bestScenario.dtp3_mean, 1) : '—'}
            sublabel={headline.bestScenario ? `${headline.bestScenario.id} · ${formatNaira(headline.bestScenario.cost_per_child_mean)} per child` : 'Loading scenarios'}
          />
          <MetricCard
            label="Flagged strata"
            value={headline.flaggedStrata != null ? `${headline.flaggedStrata}` : '—'}
            sublabel="Validation subgroups with calibration concern"
            tone="negative"
          />
        </section>

        <section className="mb-10 rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04))] p-6 md:p-8 shadow-[0_26px_90px_rgba(0,0,0,0.2)]">
          <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.22em] text-muted">Pipeline map</div>
              <h2 className="mt-2 font-serif text-3xl">From descriptive burden to policy recommendation</h2>
            </div>
            <p className="max-w-2xl text-sm text-muted">
              The sample site’s strongest pattern was overview-first navigation. Here, the stages are tied directly to this project’s actual outputs and jump you into the matching tab.
            </p>
          </div>

          <div className="grid gap-4 lg:grid-cols-4">
            {PIPELINE.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setActive(item.id)}
                className={`rounded-[1.5rem] border p-5 text-left transition ${
                  active === item.id
                    ? 'border-saffron/50 bg-saffron/10'
                    : 'border-white/10 bg-white/5 hover:bg-white/8'
                }`}
              >
                <div className="text-xs uppercase tracking-[0.2em] text-saffron">{item.stage}</div>
                <div className="mt-3 font-serif text-2xl">{item.title}</div>
                <div className="mt-4 text-xs uppercase tracking-[0.18em] text-muted">{item.metricLabel}</div>
                <div className="mt-2 text-sm text-moonlight">{pipelineMetrics[item.id]}</div>
              </button>
            ))}
          </div>
        </section>

        <section className="grid gap-5 lg:grid-cols-3 mb-10">
          <InsightCard
            eyebrow="Main finding"
            title="Dropout is a corridor, not a single miss."
            body="The explorer now frames each tab as one piece of the same chain: burden, risk stratification, policy learning, scenario evaluation, and validation."
          />
          <InsightCard
            eyebrow="Policy translation"
            title="Risk-targeted and RL-informed views sit next to raw evidence."
            body="The user no longer has to jump between abstract methods pages and scenario tables to understand how the recommendation was produced."
          />
          <InsightCard
            eyebrow="Open science"
            title="Downloads remain one click away."
            body="The evidence layer stays inspectable and exportable, but the route now leads with interpretation before raw artefacts."
          />
        </section>

        <TabNav active={active} onChange={setActive} />

        <section
          role="tabpanel"
          id={`tabpanel-${active}`}
          aria-labelledby={`tab-${active}`}
          tabIndex={0}
          className="rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04))] p-6 md:p-8 shadow-[0_26px_90px_rgba(0,0,0,0.2)]"
        >
          <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-saffron">{TAB_COPY[active].eyebrow}</div>
              <h2 className="mt-2 font-serif text-3xl">{TAB_COPY[active].title}</h2>
            </div>
            <p className="max-w-2xl text-sm text-muted">{TAB_COPY[active].body}</p>
          </div>
          <Active />
        </section>
      </section>
    </main>
  );
}

function InsightCard({ eyebrow, title, body }) {
  return (
    <article className="rounded-[1.75rem] border border-white/10 bg-white/5 p-6">
      <div className="text-xs uppercase tracking-[0.2em] text-verdigris">{eyebrow}</div>
      <h3 className="mt-3 font-serif text-2xl">{title}</h3>
      <p className="mt-4 text-sm text-muted">{body}</p>
    </article>
  );
}
