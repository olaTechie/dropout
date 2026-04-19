import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';
import { formatPct } from '../../../lib/format.js';

export default function Validation() {
  const [data, setData] = useState(null);
  useEffect(() => { loadData('validation').then(setData); }, []);
  if (!data) return <div className="text-muted">Loading…</div>;

  const internal = data.internal || {};
  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Validation</h2>
      <div className={`rounded-2xl border p-6 mb-8 ${internal.passed ? 'border-verdigris/40 bg-verdigris/5' : 'border-terracotta/40 bg-terracotta/5'}`}>
        <div className="font-mono text-xs uppercase text-muted">Internal calibration</div>
        <div className="mt-2 font-serif text-3xl">
          Predicted {internal.predicted !== undefined ? formatPct(internal.predicted, 1) : '—'} · Observed {internal.observed !== undefined ? formatPct(internal.observed, 1) : '—'}
        </div>
        <div className="mt-2 text-sm">
          Absolute error: <span className="tabular-nums">{internal.absolute_error?.toFixed(4)}</span> (tolerance {internal.tolerance})
        </div>
        <div className="mt-1 text-sm font-semibold">{internal.passed ? 'PASS' : 'FAIL — known limitation'}</div>
        {!internal.passed && (
          <p className="mt-3 text-sm text-muted">
            The microsim over-predicts S0 DTP3 completion by ~5.6 percentage points. Absolute rates in the dashboard should be interpreted as relative comparisons rather than absolute predictions. See the manuscript's Discussion section.
          </p>
        )}
      </div>

      <h3 className="font-serif text-2xl mb-4">Subgroup calibration</h3>
      <div className="grid md:grid-cols-2 gap-4">
        {Object.entries(data.subgroups || {}).map(([name, rows]) => {
          const flagged = rows.filter((r) => r.flagged).length;
          return (
            <div key={name} className="rounded-2xl border border-white/10 bg-dusk/30 p-4">
              <div className="font-mono text-xs uppercase text-muted">{name}</div>
              <div className="mt-2 text-lg">{flagged} / {rows.length} strata flagged</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
