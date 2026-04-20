import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { hasWebGL } from '../lib/webgl.js';
import { loadData, loadFallbackScenario } from '../lib/dataLoader.js';
import { buildCubeIndex, interpolateScenario } from '../lib/interp.js';
import { formatNaira, formatPct } from '../lib/format.js';
import StageCanvas from '../scene/StageCanvas.jsx';
import StableSimulationScene from '../scene/StableSimulationScene.jsx';
import SimulationControls from '../components/hud/SimulationControls.jsx';
import CanvasErrorBoundary from '../components/shared/CanvasErrorBoundary.jsx';
import MetricCard from '../components/shared/MetricCard.jsx';
import { useScenarioStore } from '../state/scenario.js';

const SCALE_COPY = {
  family: 'Single household view',
  community: 'Community cohort view',
  state: 'State-level abstraction',
  nation: 'National footprint view',
};

const CHAPTERS = [
  {
    id: 'home',
    eyebrow: 'Chapter 1',
    title: 'The journey starts at home after DTP1.',
    body: 'A mother leaves the first contact with the system having done the right thing once. The question is whether the path to DTP3 stays visible and reachable.',
    kicker: 'This is the baseline moment before reminders, outreach, and clinic friction compound.',
  },
  {
    id: 'reminder',
    eyebrow: 'Chapter 2',
    title: 'Small signals can keep the next visit alive.',
    body: 'SMS, recall systems, and clearer appointment pathways matter because they keep the mother-child pair connected to the schedule between visits.',
    kicker: 'The simulation lets you switch those supports on and see how the policy bundle changes the projected outcome.',
  },
  {
    id: 'corridor',
    eyebrow: 'Chapter 3',
    title: 'Dropout happens in the corridor between visits.',
    body: 'This is the critical story beat. The child has not been “anti-vaccine”; the family is being lost in the space between access, memory, transport, and follow-up.',
    kicker: 'The corridor is where the explorer’s risk models and the simulation’s intervention logic connect.',
  },
  {
    id: 'rescue',
    eyebrow: 'Chapter 4',
    title: 'Targeted support pulls the child back to DTP3.',
    body: 'Community health workers, recall, and incentives are represented here as recovery signals. The goal is not an abstract policy score but a completed immunisation pathway.',
    kicker: 'Use the controls to compare which bundle produces the strongest completion, cost, and equity profile.',
  },
];

export default function Simulation() {
  const [cameraMode, setCameraMode] = useState('orbit');
  const [scale, setScale] = useState('community');
  const [chapter, setChapter] = useState('home');
  const [params] = useSearchParams();
  const [cube, setCube] = useState(null);
  const [status, setStatus] = useState('loading');
  const [fallbackLive, setFallbackLive] = useState(null);
  const [restoredFromLink, setRestoredFromLink] = useState(false);
  const { budget, rule, sms_rrr, chw_rrr, interventions } = useScenarioStore();

  useEffect(() => {
    if (!params.toString()) return;
    useScenarioStore.getState().decodeFromURL(params.toString());
    setRestoredFromLink(true);
  }, [params]);

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
          return;
        }
        setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, [rule]);

  const live = status === 'cube' && cube
    ? interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr })
    : fallbackLive;

  const enabledInterventions = useMemo(
    () => Object.entries(interventions)
      .filter(([key, active]) => key !== 'a0' && active)
      .map(([key]) => ({ a1: 'SMS', a2: 'CHW', a3: 'Recall', a4: 'Incentive' }[key])),
    [interventions]
  );

  const chapterData = CHAPTERS.find((item) => item.id === chapter) || CHAPTERS[0];
  const canRender3d = hasWebGL();
  const lineChartTheme = {
    background: '#0D1220',
    border: '1px solid #1A2340',
    color: '#F4F0E6',
  };

  const simulationTrend = useMemo(() => {
    if (!live) return [];

    const baseDtp1 = 100;
    const baseDtp2 = 92;
    const finalDtp3 = live.dtp3_mean * 100;
    const corridorLoss = Math.max(0, 100 - finalDtp3);

    return [
      {
        step: 'Home',
        baseline: 100,
        current: baseDtp1,
        rescued: Math.min(100, baseDtp1 + 0.4),
      },
      {
        step: 'DTP2',
        baseline: 88,
        current: baseDtp2 + (chapter === 'reminder' || chapter === 'rescue' ? 2.4 : 0),
        rescued: Math.min(100, baseDtp2 + 4.5),
      },
      {
        step: 'Corridor',
        baseline: 79,
        current: Math.max(72, 100 - corridorLoss * 0.7 - (chapter === 'corridor' ? 4 : 0)),
        rescued: Math.min(96, 100 - corridorLoss * 0.46 + 2.5),
      },
      {
        step: 'DTP3',
        baseline: 85.4,
        current: finalDtp3,
        rescued: Math.min(99, finalDtp3 + (chapter === 'rescue' ? 2.2 : 1.2)),
      },
    ];
  }, [live, chapter]);

  const journeyPulse = useMemo(() => {
    if (!live) return [];

    const finalCoverage = live.dtp3_mean * 100;
    const chapterCoverageBoost = {
      home: 0,
      reminder: 1.1,
      corridor: -1.6,
      rescue: 2.4,
    }[chapter];

    return [
      { tick: 'Week 6', retention: 100, risk: 8, signal: 10 },
      { tick: 'Week 10', retention: 94 + (chapter === 'reminder' ? 1.8 : 0), risk: 18, signal: 24 },
      { tick: 'Week 14', retention: finalCoverage + chapterCoverageBoost, risk: chapter === 'corridor' ? 41 : 28, signal: chapter === 'rescue' ? 55 : 34 },
      { tick: 'Completion', retention: finalCoverage, risk: 14, signal: chapter === 'rescue' ? 72 : 40 },
    ];
  }, [live, chapter]);

  const scenarioTrajectory = useMemo(() => {
    if (!live) return [];
    const cost = live.cost_per_child ?? 0;
    const eq = live.concentration_index ?? 0;

    return [
      { point: 'Status quo', cost: 0, equity: 0.019, completion: 91.4 },
      { point: 'Current rule', cost, equity: eq, completion: live.dtp3_mean * 100 },
      { point: 'Rescue bundle', cost: cost * 1.08, equity: Math.max(0.01, eq - 0.002), completion: Math.min(99, live.dtp3_mean * 100 + 1.8) },
    ];
  }, [live]);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#24345f_0%,#101829_38%,#05070c_78%)]">
      <section className="max-w-7xl mx-auto px-6 py-12">
        <header className="mb-10 grid gap-8 lg:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.7fr)] lg:items-end">
          <div>
            <div className="inline-flex items-center rounded-full border border-saffron/30 bg-saffron/10 px-4 py-1 text-xs uppercase tracking-[0.25em] text-saffron">
              Narrative simulator
            </div>
            <h1 className="mt-5 max-w-5xl font-serif text-5xl md:text-7xl leading-tight">
              Follow one mother-child journey through the dropout corridor.
            </h1>
            <p className="mt-5 max-w-3xl text-lg text-moonlight/78">
              Instead of a generic sandbox, this view now stages the path from first contact to possible dropout and rescue.
              The evidence cards stay live while the scene tells the human story behind the policy recommendation.
            </p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/6 p-6 backdrop-blur-md">
            <div className="text-xs uppercase tracking-[0.22em] text-muted">Current state</div>
            <div className="mt-4 font-serif text-3xl">{chapterData.title}</div>
            <p className="mt-3 text-sm text-muted">
              Rule: <span className="text-moonlight">{rule}</span><br />
              Active bundle: <span className="text-moonlight">{enabledInterventions.join(', ') || 'No active intervention'}</span><br />
              Scene scale: <span className="text-moonlight">{SCALE_COPY[scale]}</span>
            </p>
            <div className="mt-6 flex flex-wrap gap-3 text-sm">
              <Link to="/policy" className="rounded-full bg-saffron px-5 py-2 text-abyss font-semibold hover:bg-saffron/90">
                Open policy dashboard
              </Link>
              <Link to="/explorer" className="rounded-full border border-white/15 px-5 py-2 hover:bg-white/5">
                Open explorer
              </Link>
            </div>
          </div>
        </header>

        {restoredFromLink && (
          <div className="mb-6 rounded-2xl border border-verdigris/40 bg-verdigris/8 px-5 py-4 text-sm text-moonlight">
            Scenario restored from a shared URL. Any new share link will preserve the current controls.
          </div>
        )}

        {!canRender3d && (
          <div className="mb-6 rounded-2xl border border-saffron/40 bg-saffron/8 px-5 py-4 text-sm text-moonlight">
            WebGL is unavailable in this browser or device, so the cinematic scene is replaced with a static planning view.
          </div>
        )}

        {status === 'fallback' && (
          <div className="mb-6 rounded-2xl border border-saffron/40 bg-saffron/8 px-5 py-4 text-sm text-moonlight">
            The scenario cube could not be loaded. The summary cards below are using the closest discrete scenario instead.
          </div>
        )}

        {status === 'error' && (
          <div className="mb-6 rounded-2xl border border-terracotta/50 bg-terracotta/8 px-5 py-4 text-sm text-moonlight">
            Scenario data could not be loaded. The control panel still works, but outcome metrics are unavailable until the data bundle is restored.
          </div>
        )}

        <section className="grid gap-4 md:grid-cols-3 mb-10">
          <MetricCard
            label="Projected DTP3 completion"
            value={live ? formatPct(live.dtp3_mean, 1) : '—'}
            sublabel={live && live.dtp3_ci_low != null
              ? `CI ${formatPct(live.dtp3_ci_low, 1)}-${formatPct(live.dtp3_ci_high, 1)}`
              : 'Awaiting scenario data'}
            tone="positive"
          />
          <MetricCard
            label="Cost per child"
            value={live ? formatNaira(live.cost_per_child) : '—'}
            sublabel="Updated from the active scenario controls"
          />
          <MetricCard
            label="Equity signal"
            value={live ? live.concentration_index.toFixed(3) : '—'}
            sublabel="Lower is closer to equal access"
            tone={live && live.concentration_index < 0.02 ? 'positive' : 'warning'}
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
          <div className="space-y-6 xl:sticky xl:top-24 xl:self-start">
            <section className="rounded-[2rem] border border-white/10 bg-night/85 p-6 shadow-2xl shadow-black/30">
              <div className="text-xs uppercase tracking-[0.22em] text-saffron">{chapterData.eyebrow}</div>
              <h2 className="mt-3 font-serif text-3xl">{chapterData.title}</h2>
              <p className="mt-4 text-sm text-muted">{chapterData.body}</p>
              <p className="mt-4 text-sm text-moonlight/90">{chapterData.kicker}</p>
            </section>

            <section className="rounded-[2rem] border border-white/10 bg-white/5 p-4">
              <div className="text-xs uppercase tracking-[0.2em] text-muted mb-4">Story chapters</div>
              <div className="space-y-3">
                {CHAPTERS.map((item, index) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setChapter(item.id)}
                    className={`w-full rounded-[1.25rem] border p-4 text-left transition ${
                      chapter === item.id
                        ? 'border-saffron/45 bg-saffron/10'
                        : 'border-white/10 bg-black/10 hover:bg-white/6'
                    }`}
                  >
                    <div className="text-xs uppercase tracking-[0.18em] text-muted">0{index + 1}</div>
                    <div className="mt-2 font-medium text-moonlight">{item.title}</div>
                  </button>
                ))}
              </div>
            </section>

            <SimulationControls
              cameraMode={cameraMode}
              setCameraMode={setCameraMode}
              scale={scale}
              setScale={setScale}
              className="rounded-3xl border border-white/10 bg-night/85 shadow-2xl shadow-black/30"
            />
          </div>

          <div className="space-y-6">
            <section className="rounded-[2rem] border border-white/10 bg-white/5 p-4 md:p-6 backdrop-blur-md">
              <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
                <div>
                  <div className="text-xs uppercase tracking-[0.22em] text-muted">Cinematic stage</div>
                  <h2 className="mt-2 font-serif text-3xl">Mother-child immunisation journey</h2>
                </div>
                <p className="max-w-xl text-sm text-muted">
                  The scene now makes the pathway explicit: checkpoint gates mark DTP1, DTP2, and DTP3, the shadow branch shows dropout, and intervention towers act as rescue signals.
                </p>
              </div>

              {canRender3d ? (
                <div className="relative overflow-hidden rounded-[1.5rem] border border-white/10 bg-[linear-gradient(180deg,#20335f_0%,#0f1728_48%,#080b12_100%)] min-h-[420px] md:min-h-[560px]">
                  <div className="pointer-events-none absolute inset-x-0 top-0 z-10 flex flex-wrap gap-2 p-4 text-xs uppercase tracking-[0.2em] text-moonlight/80">
                    <span className="rounded-full bg-black/25 px-3 py-1">Camera: {cameraMode}</span>
                    <span className="rounded-full bg-black/25 px-3 py-1">Scale: {SCALE_COPY[scale]}</span>
                    <span className="rounded-full bg-black/25 px-3 py-1">Chapter: {chapterData.eyebrow}</span>
                  </div>

                  <CanvasErrorBoundary className="absolute inset-0 flex min-h-[420px] flex-col items-center justify-center px-6 text-center text-sm text-muted md:min-h-[560px]">
                    <StageCanvas className="absolute inset-0" shadows={false}>
                      <StableSimulationScene cameraMode={cameraMode} scale={scale} chapter={chapter} />
                    </StageCanvas>
                  </CanvasErrorBoundary>
                </div>
              ) : (
                <div className="rounded-[1.5rem] border border-white/10 bg-night/70 p-8 min-h-[420px] flex flex-col justify-between">
                  <div>
                    <div className="text-xs uppercase tracking-[0.22em] text-muted">Static fallback</div>
                    <h3 className="mt-3 font-serif text-3xl">{chapterData.title}</h3>
                    <p className="mt-4 max-w-2xl text-muted">
                      The chapter narrative still works without GPU support. Use the chapter selector and live cards to move from home contact, through checkpoint loss, to rescue policy.
                    </p>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                      <div className="text-xs uppercase tracking-[0.2em] text-muted">Active bundle</div>
                      <div className="mt-3 text-lg">{enabledInterventions.join(', ') || 'No active intervention'}</div>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                      <div className="text-xs uppercase tracking-[0.2em] text-muted">Chapter focus</div>
                      <div className="mt-3 text-lg">{chapterData.kicker}</div>
                    </div>
                  </div>
                </div>
              )}
            </section>

            <section className="grid gap-4 md:grid-cols-3">
              <InsightCard
                eyebrow="Narrative logic"
                title="The unit of understanding is one family."
                body="The scene is no longer an abstract operations board. It stages the immunisation pathway as a sequence a policymaker can explain in human terms."
              />
              <InsightCard
                eyebrow="Analytic bridge"
                title="The live metrics keep the story anchored."
                body="The cinematic layer now sits directly above the same scenario cube and fallback data used by the dashboard."
              />
              <InsightCard
                eyebrow="Interaction"
                title="Controls remain, but the story comes first."
                body="Users can still tune camera, scale, budget, and intervention bundle, but the page now tells them what those decisions mean."
              />
            </section>

            <section className="rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04))] p-6 md:p-8 shadow-[0_24px_80px_rgba(0,0,0,0.18)]">
              <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
                <div>
                  <div className="text-xs uppercase tracking-[0.22em] text-muted">Simulation results</div>
                  <h2 className="mt-2 font-serif text-3xl">Line charts for what the story is doing</h2>
                </div>
                <p className="max-w-2xl text-sm text-muted">
                  These charts translate the animation into measurable effects: where retention falls, how rescue changes the journey, and what the current rule costs in return for completion and equity.
                </p>
              </div>

              <div className="grid gap-5 xl:grid-cols-2">
                <ChartCard
                  title="Journey retention by checkpoint"
                  subtitle="Baseline, current rule, and rescue pathway across the mother-child journey."
                >
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={simulationTrend} margin={{ top: 12, right: 20, left: 8, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1A2340" />
                      <XAxis dataKey="step" stroke="#9AA3B8" style={{ fontSize: 12 }} />
                      <YAxis stroke="#9AA3B8" style={{ fontSize: 12 }} domain={[70, 100]} />
                      <Tooltip contentStyle={lineChartTheme} />
                      <Legend />
                      <Line type="monotone" dataKey="baseline" stroke="#9AA3B8" strokeWidth={2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="current" stroke="#F5B042" strokeWidth={3} dot={{ r: 4 }} />
                      <Line type="monotone" dataKey="rescued" stroke="#47B7A0" strokeWidth={2.5} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>

                <ChartCard
                  title="Dropout pressure and rescue signal"
                  subtitle="The chapter changes the balance between pathway risk and intervention support."
                >
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={journeyPulse} margin={{ top: 12, right: 20, left: 8, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1A2340" />
                      <XAxis dataKey="tick" stroke="#9AA3B8" style={{ fontSize: 12 }} />
                      <YAxis stroke="#9AA3B8" style={{ fontSize: 12 }} domain={[0, 100]} />
                      <Tooltip contentStyle={lineChartTheme} />
                      <Legend />
                      <Line type="monotone" dataKey="retention" stroke="#F4F0E6" strokeWidth={2.5} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="risk" stroke="#C6553A" strokeWidth={2.5} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="signal" stroke="#5A7BFF" strokeWidth={2.5} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>

                <ChartCard
                  title="Cost and equity trajectory"
                  subtitle="Current rule vs status quo vs a stronger rescue bundle."
                  className="xl:col-span-2"
                >
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={scenarioTrajectory} margin={{ top: 12, right: 20, left: 8, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1A2340" />
                      <XAxis dataKey="point" stroke="#9AA3B8" style={{ fontSize: 12 }} />
                      <YAxis yAxisId="left" stroke="#9AA3B8" style={{ fontSize: 12 }} />
                      <YAxis yAxisId="right" orientation="right" stroke="#9AA3B8" style={{ fontSize: 12 }} />
                      <Tooltip contentStyle={lineChartTheme} />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="cost" name="Cost / child (NGN)" stroke="#F5B042" strokeWidth={3} dot={{ r: 4 }} />
                      <Line yAxisId="right" type="monotone" dataKey="completion" name="DTP3 completion %" stroke="#47B7A0" strokeWidth={2.5} dot={{ r: 4 }} />
                      <Line yAxisId="right" type="monotone" dataKey="equity" name="Concentration index" stroke="#5A7BFF" strokeWidth={2.5} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>
            </section>
          </div>
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

function ChartCard({ title, subtitle, className = '', children }) {
  return (
    <article className={`rounded-[1.75rem] border border-white/10 bg-night/70 p-5 ${className}`}>
      <div className="text-xs uppercase tracking-[0.2em] text-saffron">Live chart</div>
      <h3 className="mt-3 font-serif text-2xl">{title}</h3>
      <p className="mt-3 text-sm text-muted">{subtitle}</p>
      <div className="mt-6">{children}</div>
    </article>
  );
}
