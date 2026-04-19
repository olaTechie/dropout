export default function Methods() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-12 text-moonlight">
      <header className="mb-10">
        <h1 className="font-serif text-5xl">Methods</h1>
        <p className="mt-3 text-muted">
          A summary of the analytic pipeline behind every figure on this site.
          For full statistical detail, see the manuscript and supplementary
          materials at the GitHub repository.
        </p>
      </header>

      <section className="space-y-6 leading-relaxed">
        <div>
          <h2 className="font-serif text-2xl mb-2">Data</h2>
          <p className="text-muted">
            Nigeria Demographic and Health Survey 2024 (Children's Recode,
            NGKR8BFL). Analytic cohort: 3,194 children aged 12–23 months with
            card-confirmed DTP1 receipt (h3 ∈ {'{'}1, 2, 3{'}'}). Survey design
            applied throughout: weights v005/1,000,000, strata v022, PSU v021.
          </p>
        </div>

        <div>
          <h2 className="font-serif text-2xl mb-2">Outcomes</h2>
          <ul className="list-disc list-inside text-muted space-y-1">
            <li><strong>T1 dropout</strong>: DTP1 received, DTP2 not received.</li>
            <li><strong>T2 dropout</strong>: DTP2 received, DTP3 not received.</li>
            <li><strong>WHO cascade dropout</strong>: (DTP1 − DTP3) ÷ DTP1 × 100.</li>
          </ul>
        </div>

        <div>
          <h2 className="font-serif text-2xl mb-2">Prediction (TRIPOD-AI)</h2>
          <p className="text-muted">
            Two transition-specific XGBoost classifiers (T1, T2). Nested
            5-fold cluster-robust cross-validation; isotonic recalibration;
            performance reported as AUROC, AUPRC, Brier, ECE with 95 %
            bootstrap CI. SHAP for feature attribution. Reported per
            TRIPOD-AI (Collins et al. 2024 BMJ).
          </p>
        </div>

        <div>
          <h2 className="font-serif text-2xl mb-2">Sequential intervention (offline RL)</h2>
          <p className="text-muted">
            Markov Decision Process formulation with five actions
            (a₀ none, a₁ SMS, a₂ CHW visit, a₃ facility recall, a₄
            conditional incentive). Behaviour policy inferred from DHS
            proxies because interventions are not directly recorded.
            Policies learned with Fitted Q Iteration (FQI), Conservative
            Q-Learning (CQL), and Implicit Q-Learning (IQL); off-policy
            evaluation via Importance Sampling, Weighted IS, and
            Doubly-Robust estimators. Reported per the seven Gottesman
            et al. (2019) RL-in-health guidelines.
          </p>
        </div>

        <div>
          <h2 className="font-serif text-2xl mb-2">Cost-effectiveness (CHEERS 2022)</h2>
          <p className="text-muted">
            Six scenarios (status quo, uniform SMS, uniform CHW,
            risk-targeted, RL-optimised, bandit-allocated) simulated
            on bootstrap child-level replicates with 1,000-iteration
            probabilistic sensitivity analysis. Outcomes: DTP3 coverage,
            cost per child (2026 NGN), incremental cost-effectiveness
            ratio vs status quo, cost-effectiveness acceptability curves,
            tornado one-way sensitivity, and equity (concentration index,
            wealth-quintile gap, slope index).
          </p>
        </div>

        <div>
          <h2 className="font-serif text-2xl mb-2">Reproducibility</h2>
          <p className="text-muted">
            All analytic code, derived artefacts, and the manuscript itself
            are openly released under MIT at{' '}
            <a
              href="https://github.com/olatechie/dropout"
              className="text-saffron hover:underline"
              target="_blank"
              rel="noreferrer"
            >
              github.com/olatechie/dropout
            </a>.
          </p>
        </div>
      </section>
    </main>
  );
}
