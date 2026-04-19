const METHOD_SECTIONS = [
  {
    title: 'Data',
    body: `Nigeria Demographic and Health Survey 2024 (Children's Recode, NGKR8BFL). Analytic cohort: 3,194 children aged 12–23 months with card-confirmed DTP1 receipt (h3 ∈ {1, 2, 3}). Survey design applied throughout: weights v005/1,000,000, strata v022, PSU v021.`,
  },
  {
    title: 'Outcomes',
    body: `Three primary outcome frames were tracked: T1 dropout (DTP1 received, DTP2 not received), T2 dropout (DTP2 received, DTP3 not received), and WHO cascade dropout ((DTP1 − DTP3) ÷ DTP1 × 100).`,
  },
  {
    title: 'Prediction',
    body: `Two transition-specific XGBoost classifiers (T1 and T2) were trained with nested 5-fold cluster-robust cross-validation and isotonic recalibration. Performance was reported as AUROC, AUPRC, Brier, and ECE with 95% bootstrap intervals. Feature attribution used SHAP, and reporting followed TRIPOD-AI guidance.`,
  },
  {
    title: 'Sequential intervention',
    body: `The decision problem was framed as a Markov Decision Process with five actions: no action, SMS, CHW visit, facility recall, and conditional incentive. Because interventions are not directly recorded in DHS, the behaviour policy was approximated using proxies. Policies were learned with FQI, CQL, and IQL, then evaluated with Importance Sampling, Weighted IS, and Doubly Robust estimators.`,
  },
  {
    title: 'Cost-effectiveness',
    body: `Six scenarios were simulated on bootstrap child-level replicates with 1,000-iteration probabilistic sensitivity analysis. Reported outcomes included DTP3 coverage, cost per child (2026 NGN), ICER versus status quo, acceptability curves, tornado sensitivity, and equity indicators including concentration index, wealth-quintile gap, and slope index.`,
  },
  {
    title: 'Reproducibility',
    body: `All analytic code, derived artefacts, and manuscript materials are openly released under MIT in the project repository.`,
  },
];

export default function Methods() {
  return (
    <main className="min-h-screen">
      <section className="max-w-5xl mx-auto px-6 py-12 text-moonlight">
        <header className="mb-10 grid gap-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(300px,0.85fr)] lg:items-end">
          <div>
            <div className="inline-flex items-center rounded-full border border-saffron/30 bg-saffron/10 px-4 py-1 text-xs uppercase tracking-[0.25em] text-saffron">
              Methods
            </div>
            <h1 className="mt-5 font-serif text-5xl md:text-7xl leading-tight">
              The analytic pipeline behind every chart and scenario.
            </h1>
            <p className="mt-5 max-w-3xl text-lg text-moonlight/78">
              This page keeps the methodological summary compact enough for web reading
              while preserving the structure of the full research workflow.
            </p>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/6 p-6 backdrop-blur-md">
            <div className="text-xs uppercase tracking-[0.22em] text-muted">Repository</div>
            <p className="mt-4 text-sm text-muted">
              For manuscript files, code, and supplementary outputs, use the public project repository.
            </p>
            <a
              href="https://github.com/olatechie/dropout"
              className="mt-6 inline-flex rounded-full bg-saffron px-5 py-2 text-sm font-semibold text-abyss hover:bg-saffron/90"
              target="_blank"
              rel="noreferrer"
            >
              Open GitHub repository
            </a>
          </div>
        </header>

        <section className="grid gap-5 md:grid-cols-2">
          {METHOD_SECTIONS.map((section) => (
            <article
              key={section.title}
              className="rounded-[1.75rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] p-6 leading-relaxed shadow-[0_20px_70px_rgba(0,0,0,0.14)]"
            >
              <div className="text-xs uppercase tracking-[0.2em] text-saffron">{section.title}</div>
              <p className="mt-4 text-sm text-muted">{section.body}</p>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}
