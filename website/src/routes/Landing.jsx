import { Link } from 'react-router-dom';

const DESTINATIONS = [
  {
    to: '/story',
    eyebrow: 'Narrative',
    title: 'Start with the evidence story',
    body: 'A cinematic walkthrough of where children are lost between DTP1 and DTP3, and why the bottlenecks differ across Nigeria.',
  },
  {
    to: '/policy',
    eyebrow: 'Decisions',
    title: 'Compare intervention scenarios',
    body: 'Open the policy dashboard to inspect cost, projected completion, and equity tradeoffs under different rules and budgets.',
  },
  {
    to: '/simulation',
    eyebrow: 'Sandbox',
    title: 'Use the redesigned simulator',
    body: 'Adjust interventions, shift the camera, and generate working share links without relying on a fragile full-screen scene.',
  },
];

export default function Landing() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#253763_0%,#121b2d_40%,#05070c_78%)]">
      <section className="max-w-7xl mx-auto px-6 py-16 md:py-24">
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)] lg:items-end">
          <div>
            <div className="inline-flex items-center rounded-full border border-saffron/30 bg-saffron/10 px-4 py-1 text-xs uppercase tracking-[0.25em] text-saffron">
              Vaccination dropout in Nigeria
            </div>
            <h1 className="mt-6 max-w-5xl font-serif text-6xl md:text-8xl leading-[0.95]">
              Catching the fall before DTP3 is missed.
            </h1>
            <p className="mt-6 max-w-3xl text-lg md:text-xl text-moonlight/78">
              A research website for understanding where the immunization cascade breaks,
              which children are most at risk of dropout, and which interventions deliver
              the strongest improvement under real budget constraints.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                to="/simulation"
                className="inline-flex items-center gap-2 rounded-full bg-saffron px-8 py-4 font-semibold text-abyss hover:bg-saffron/90 transition"
              >
                Open simulator
              </Link>
              <Link
                to="/story"
                className="inline-flex items-center gap-2 rounded-full border border-white/15 px-8 py-4 hover:bg-white/5 transition"
              >
                Begin the story
              </Link>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/6 p-6 backdrop-blur-md">
            <div className="text-xs uppercase tracking-[0.22em] text-muted">Why this site matters</div>
            <div className="mt-5 grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              <Stat label="Analytic cohort" value="3,194" note="Children aged 12-23 months with card-confirmed DTP1" />
              <Stat label="Intervention actions" value="5" note="From no action to incentive support" />
              <Stat label="Policy views" value="3" note="Story, dashboard, and simulation modes" />
            </div>
          </div>
        </div>

        <section className="mt-14 grid gap-5 lg:grid-cols-3">
          {DESTINATIONS.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="group rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] p-6 transition hover:-translate-y-1 hover:border-saffron/35 hover:bg-white/8"
            >
              <div className="text-xs uppercase tracking-[0.2em] text-saffron">{item.eyebrow}</div>
              <h2 className="mt-4 font-serif text-3xl leading-tight">{item.title}</h2>
              <p className="mt-4 text-sm text-muted">{item.body}</p>
              <div className="mt-8 text-sm text-moonlight group-hover:text-saffron">Open section →</div>
            </Link>
          ))}
        </section>
      </section>
    </main>
  );
}

function Stat({ label, value, note }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-muted">{label}</div>
      <div className="mt-2 font-serif text-3xl">{value}</div>
      <div className="mt-2 text-sm text-muted">{note}</div>
    </div>
  );
}
