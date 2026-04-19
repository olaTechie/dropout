import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';

export default function PredictionModels() {
  const [data, setData] = useState(null);
  useEffect(() => { loadData('shap_summary').then(setData); }, []);
  if (!data) return <div className="text-muted">Loading…</div>;

  const rows = Object.entries(data).map(([model, d]) => ({ model, ...d }));

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Transition-specific prediction models</h2>
      <p className="text-muted max-w-3xl mb-8">
        Three XGBoost models predict dropout at each cascade transition. Isotonic recalibration applied post-hoc. DeLong test compares against logistic regression baseline.
      </p>
      <div className="grid md:grid-cols-3 gap-6">
        {rows.map((r) => (
          <div key={r.model} className="rounded-2xl border border-white/10 bg-dusk/30 p-6">
            <div className="font-mono text-xs text-muted uppercase">{r.model}</div>
            <div className="mt-2 font-serif text-3xl">{r.metrics?.auc_roc ? r.metrics.auc_roc.toFixed(3) : '—'}</div>
            <div className="text-sm text-muted mt-1">AUC-ROC</div>
            <dl className="mt-4 text-sm space-y-1">
              <div className="flex justify-between"><dt className="text-muted">AUC-PR</dt><dd className="tabular-nums">{r.metrics?.auc_pr?.toFixed(3) ?? '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-muted">Prevalence</dt><dd className="tabular-nums">{r.prevalence ? (r.prevalence * 100).toFixed(1) + '%' : '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-muted">N</dt><dd className="tabular-nums">{r.n ?? '—'}</dd></div>
              <div className="flex justify-between"><dt className="text-muted">DeLong p</dt><dd className="tabular-nums">{r.delong?.p ? r.delong.p.toExponential(1) : '—'}</dd></div>
            </dl>
          </div>
        ))}
      </div>
    </div>
  );
}
